# USBMassStorage.py 
#
# Contains class definitions to implement a USB mass storage device.

from mmap import mmap
import os

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBClass import *

from util import *

class USBMassStorageClass(USBClass):
    name = "USB mass storage class"

    def setup_request_handlers(self):
        self.request_handlers = {
            0xFF : self.handle_bulk_only_mass_storage_reset_request,
            0xFE : self.handle_get_max_lun_request
         
        }

    def handle_bulk_only_mass_storage_reset_request(self, req):
        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_get_max_lun_request(self, req):
        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'\x00')


class USBMassStorageInterface(USBInterface):
    name = "USB mass storage interface"

    def __init__(self, maxusb_app, disk_image, usbclass, sub, proto, verbose=0):
        self.disk_image = disk_image
        self.maxusb_app = maxusb_app
        descriptors = { }

        endpoints = [
            USBEndpoint(
                maxusb_app,
                1,          # endpoint number
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                None        # handler function
            )
        ]

        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                0,          # interface number
                0,          # alternate setting
                usbclass,          # 8 interface class: Mass Storage
                sub,          # 6 subclass: SCSI transparent command set
                proto,       # 0x50 protocol: bulk-only (BBB) transport
                0,          # string index
                verbose,
                endpoints,
                descriptors
        )

        self.device_class = USBMassStorageClass()
        self.device_class.set_interface(self)

        self.is_write_in_progress = False
        self.write_cbw = None
        self.write_base_lba = 0
        self.write_length = 0
        self.write_data = b''

    def handle_data_available(self, data):

        if self.verbose > 0:
            print(self.name, "handling", len(data), "bytes of SCSI data")

        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True

        cbw = CommandBlockWrapper(data)
        opcode = cbw.cb[0]
        status = 0              # default to success
        response = None         # with no response data

        if self.maxusb_app.server_running == True:
            try:
                self.maxusb_app.netserver_from_endpoint_sd.send(data)
            except:
                print ("Error: No network client connected")

            while True:
                if len(self.maxusb_app.reply_buffer) > 0:
                    self.maxusb_app.send_on_endpoint(3, self.maxusb_app.reply_buffer)
                    self.maxusb_app.reply_buffer = ""
                    break

        elif self.is_write_in_progress:
            if self.verbose > 0:
                print(self.name, "got", len(data), "bytes of SCSI write data")

            self.write_data += data

            if len(self.write_data) < self.write_length:
                # more yet to read, don't send the CSW
                return

            self.disk_image.put_sector_data(self.write_base_lba, self.write_data)
            cbw = self.write_cbw

            self.is_write_in_progress = False
            self.write_data = b''

        elif opcode == 0x00:      # Test Unit Ready: just return OK status
            if self.verbose > 0:
                print(self.name, "got SCSI Test Unit Ready")

        elif opcode == 0x03:    # Request Sense
            if self.verbose > 0:
                print(self.name, "got SCSI Request Sense, data",
                        bytes_as_hex(cbw.cb[1:]))

            response_code = b'\x70'
            valid = b'\x00'
            filemark = b'\x06'
            information = b'\x00\x00\x00\x00'
            command_info = b'\x00\x00\x00\x00'
            additional_sense_code = b'\x3a'
            additional_sens_code_qualifier = b'\x00'
            field_replacement_unti_code = b'\x00'
            sense_key_specific = b'\x00\x00\x00'

            part1 = response_code + \
                    valid + \
                    filemark + \
                    information

            part2 = command_info + \
                    additional_sense_code + \
                    additional_sens_code_qualifier + \
                    field_replacement_unti_code + \
                    sense_key_specific

            length = bytes([len(part2)])
            response = part1 + length + part2


        elif opcode == 0x12:    # Inquiry
            if self.verbose > 0:
                print(self.name, "got SCSI Inquiry, data",
                        bytes_as_hex(cbw.cb[1:]))

            if self.maxusb_app.testcase[1] == "inquiry_peripheral":
                peripheral = self.maxusb_app.testcase[2]
            else:
                peripheral = b'\x00'    # SBC
            if self.maxusb_app.testcase[1] == "inquiry_RMB":
                RMB = self.maxusb_app.testcase[2]
            else:
                RMB = b'\x80'           # Removable
            if self.maxusb_app.testcase[1] == "inquiry_version":
                version = self.maxusb_app.testcase[2]
            else:
                version = b'\x00'
            if self.maxusb_app.testcase[1] == "response_data_format":
                response_data_format = self.maxusb_app.testcase[2]
            else:
                response_data_format = b'\x01'
            if self.maxusb_app.testcase[1] == "config1":
                config1 = self.maxusb_app.testcase[2]
            else:
                config1 = b'\x00'
            if self.maxusb_app.testcase[1] == "config2":
                config2 = self.maxusb_app.testcase[2]
            else:
                config2 = b'\x00'
            if self.maxusb_app.testcase[1] == "config3":
                config3 = self.maxusb_app.testcase[2]
            else:
                config3 = b'\x00'
            if self.maxusb_app.testcase[1] == "vendor_id":
                vendor_id = self.maxusb_app.testcase[2]
            else:
                vendor_id = b'PNY     '
            if self.maxusb_app.testcase[1] == "product_id":
                product_id = self.maxusb_app.testcase[2]
            else:
                product_id = b'USB 2.0 FD      '
            if self.maxusb_app.testcase[1] == "product_revision_level":
                product_revision_level = self.maxusb_app.testcase[2]
            else:
                product_revision_level = b'8.02'

            part1 = peripheral + \
                    RMB + \
                    version + \
                    response_data_format

            part2 = config1 + \
                    config2 + \
                    config3 + \
                    vendor_id + \
                    product_id + \
                    product_revision_level

            length = bytes([len(part2)])
            response = part1 + length + part2


        elif opcode == 0x1a or opcode == 0x5a:    # Mode Sense (6 or 10)
            page = cbw.cb[2] & 0x3f

            if self.verbose > 0:
                print(self.name, "got SCSI Mode Sense, page code 0x%02x" % page)

            if page == 0x1c:

                if self.maxusb_app.testcase[1] == "mode_sense_medium_type":
                    medium_type = self.maxusb_app.testcase[2]
                else:
                    medium_type = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_device_specific_param":
                    device_specific_param = self.maxusb_app.testcase[2]
                else:
                    device_specific_param = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_block_descriptor_len":
                    block_descriptor_len = self.maxusb_app.testcase[2]
                else:
                    block_descriptor_len = b'\x00'
                mode_page_1c = b'\x1c\x06\x00\x05\x00\x00\x00\x00'
            
                body =  medium_type + \
                        device_specific_param + \
                        block_descriptor_len + \
                        mode_page_1c 

                if self.maxusb_app.testcase[1] == "mode_sense_length":
                    length = self.maxusb_app.testcase[2]
                else:
                    length = bytes([len(body)]) 
                response = length + body

            if page == 0x3f:
                if self.maxusb_app.testcase[1] == "mode_sense_length":
                    length = self.maxusb_app.testcase[2]
                else:
                    length = b'\x45'
                if self.maxusb_app.testcase[1] == "mode_sense_medium_type":
                    medium_type = self.maxusb_app.testcase[2]
                else:
                    medium_type = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_device_specific_param":
                    device_specific_param = self.maxusb_app.testcase[2]
                else:
                    device_specific_param = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_block_descriptor_len":
                    block_descriptor_len = self.maxusb_app.testcase[2]
                else:
                    block_descriptor_len = b'\x08'
                mode_page = b'\x00\x00\x00\x00'

                response =  length + \
                            medium_type + \
                            device_specific_param + \
                            block_descriptor_len + \
                            mode_page

            else:
                if self.maxusb_app.testcase[1] == "mode_sense_length":
                    length = self.maxusb_app.testcase[2]
                else:
                    length = b'\x07'
                if self.maxusb_app.testcase[1] == "mode_sense_medium_type":
                    medium_type = self.maxusb_app.testcase[2]
                else:
                    medium_type = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_device_specific_param":
                    device_specific_param = self.maxusb_app.testcase[2]
                else:
                    device_specific_param = b'\x00'
                if self.maxusb_app.testcase[1] == "mode_sense_block_descriptor_len":
                    block_descriptor_len = self.maxusb_app.testcase[2]
                else:
                    block_descriptor_len = b'\x00'
                mode_page = b'\x00\x00\x00\x00'

                response =  length + \
                            medium_type + \
                            device_specific_param + \
                            block_descriptor_len + \
                            mode_page


        elif opcode == 0x1e:    # Prevent/Allow Removal: feign success
            if self.verbose > 0:
                print(self.name, "got SCSI Prevent/Allow Removal")

        #elif opcode == 0x1a or opcode == 0x5a:      # Mode Sense (6 or 10)
            # TODO

        elif opcode == 0x23:    # Read Format Capacity
            if self.verbose > 0:
                print(self.name, "got SCSI Read Format Capacity")

            if self.maxusb_app.testcase[1] == "read_format_capacity_capacity_list_length":
                capacity_list_length = self.maxusb_app.testcase[2]
            else:
                capacity_list_length = b'\x00\x00\x00\x08'
            if self.maxusb_app.testcase[1] == "read_format_capacity_number_of_blocks":
                number_of_blocks = self.maxusb_app.testcase[2]
            else:
                number_of_blocks = b'\x00\x00\x10\x00'
            if self.maxusb_app.testcase[1] == "read_format_capacity_descriptor_type":
                descriptor_type = self.maxusb_app.testcase[2]
            else:
                descriptor_type = b'\x00'
            if self.maxusb_app.testcase[1] == "read_format_capacity_block_length":
                block_length = self.maxusb_app.testcase[2]
            else:
                block_length = b'\x00\x02\x00'

            response =  capacity_list_length + \
                        number_of_blocks + \
                        descriptor_type + \
                        block_length


        elif opcode == 0x25:    # Read Capacity
            if self.verbose > 0:
                print(self.name, "got SCSI Read Capacity, data",
                        bytes_as_hex(cbw.cb[1:]))

            lastlba = self.disk_image.get_sector_count()

            if self.maxusb_app.testcase[1] == "read_capacity_logical_block_address":
                logical_block_address = self.maxusb_app.testcase[2]
            else:
                logical_block_address = bytes([
                    (lastlba >> 24) & 0xff,
                    (lastlba >> 16) & 0xff,
                    (lastlba >>  8) & 0xff,
                    (lastlba      ) & 0xff,
                ])


            if self.maxusb_app.testcase[1] == "read_capacity_length":
                length = self.maxusb_app.testcase[2]
            else:
                length = b'\x00\x00\x02\x00'
            response =  logical_block_address + \
                        length

        elif opcode == 0x28:    # Read (10)

            if self.maxusb_app.mode == 4:
                self.maxusb_app.stop = True


            base_lba = cbw.cb[2] << 24 \
                     | cbw.cb[3] << 16 \
                     | cbw.cb[4] << 8 \
                     | cbw.cb[5]

            num_blocks = cbw.cb[7] << 8 \
                       | cbw.cb[8]

            if self.verbose > 0:
                print(self.name, "got SCSI Read (10), lba", base_lba, "+",
                        num_blocks, "block(s)")
                        

            # Note that here we send the data directly rather than putting
            # something in 'response' and letting the end of the switch send
            for block_num in range(num_blocks):
                data = self.disk_image.get_sector_data(base_lba + block_num)
                self.configuration.device.maxusb_app.send_on_endpoint(3, data)

        elif opcode == 0x2a:    # Write (10)
            if self.verbose > 0:
                print(self.name, "got SCSI Write (10), data",
                        bytes_as_hex(cbw.cb[1:]))

            base_lba = cbw.cb[1] << 24 \
                     | cbw.cb[2] << 16 \
                     | cbw.cb[3] <<  8 \
                     | cbw.cb[4]

            num_blocks = cbw.cb[7] << 8 \
                       | cbw.cb[8]

            if self.verbose > 0:
                print(self.name, "got SCSI Write (10), lba", base_lba, "+",
                        num_blocks, "block(s)")

            # save for later
            self.write_cbw = cbw
            self.write_base_lba = base_lba
            self.write_length = num_blocks * self.disk_image.block_size
            self.is_write_in_progress = True

            # because we need to snarf up the data from wire before we reply
            # with the CSW
            return

        elif opcode == 0x35:    # Synchronize Cache (10): blindly OK
            if self.verbose > 0:
                print(self.name, "got Synchronize Cache (10)")

        else:
            if self.verbose > 0:
                print(self.name, "received unsupported SCSI opcode 0x%x" % opcode)
            status = 0x02   # command failed
            if cbw.data_transfer_length > 0:
                response = bytes([0] * cbw.data_transfer_length)

        if response and self.maxusb_app.server_running == False:
            if self.verbose > 2:
                print(self.name, "responding with", len(response), "bytes:",
                        bytes_as_hex(response))

            self.configuration.device.maxusb_app.send_on_endpoint(3, response)


        csw = bytes([
            ord('U'), ord('S'), ord('B'), ord('S'),
            cbw.tag[0], cbw.tag[1], cbw.tag[2], cbw.tag[3],
            0x00, 0x00, 0x00, 0x00,
            status
        ])

        if self.verbose > 3:
            print(self.name, "responding with status =", status)

#        if self.maxusb_app.server_running == False:
        self.configuration.device.maxusb_app.send_on_endpoint(3, csw)


class DiskImage:
    def __init__(self, filename, block_size):
        self.filename = filename
        self.block_size = block_size

        statinfo = os.stat(self.filename)
        self.size = statinfo.st_size

        self.file = open(self.filename, 'r+b')
        self.image = mmap(self.file.fileno(), 0)

    def close(self):
        self.image.flush()
        self.image.close()

    def get_sector_count(self):
        return int(self.size / self.block_size) - 1

    def get_sector_data(self, address):
        block_start = address * self.block_size
        block_end   = (address + 1) * self.block_size   # slices are NON-inclusive

        return self.image[block_start:block_end]

    def put_sector_data(self, address, data):
        block_start = address * self.block_size
        block_end   = (address + 1) * self.block_size   # slices are NON-inclusive

        self.image[block_start:block_end] = data[:self.block_size]
        self.image.flush()


class CommandBlockWrapper:
    def __init__(self, bytestring):
        self.signature              = bytestring[0:4]
        self.tag                    = bytestring[4:8]
        self.data_transfer_length   = bytestring[8] \
                                    | bytestring[9] << 8 \
                                    | bytestring[10] << 16 \
                                    | bytestring[11] << 24
        self.flags                  = int(bytestring[12])
        self.lun                    = int(bytestring[13] & 0x0f)
        self.cb_length              = int(bytestring[14] & 0x1f)
        #self.cb                     = bytestring[15:15+self.cb_length]
        self.cb                     = bytestring[15:]

    def __str__(self):
        s  = "sig: " + bytes_as_hex(self.signature) + "\n"
        s += "tag: " + bytes_as_hex(self.tag) + "\n"
        s += "data transfer len: " + str(self.data_transfer_length) + "\n"
        s += "flags: " + str(self.flags) + "\n"
        s += "lun: " + str(self.lun) + "\n"
        s += "command block len: " + str(self.cb_length) + "\n"
        s += "command block: " + bytes_as_hex(self.cb) + "\n"

        return s


class USBMassStorageDevice(USBDevice):
    name = "USB mass storage device"

    def __init__(self, maxusb_app, vid, pid, rev, int_class, int_sub, int_proto, disk_image_filename, verbose=0):
        self.disk_image = DiskImage(disk_image_filename, 512)

        interface = USBMassStorageInterface(maxusb_app, self.disk_image, int_class, int_sub, int_proto, verbose=verbose)

        if vid == 0x1111:
            vid = 0x154b
        if pid == 0x2222:
            pid = 0x6545
        if rev == 0x3333:
            rev = 0x0200

        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "MassStorage config",                       # string desc
                [ interface ]                               # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                vid,                    # vendor id
                pid,                    # product id
                rev,                    # device revision
                "PNY",                  # manufacturer string
                "USB 2.0 FD",           # product string
                "4731020ef1914da9",     # serial number string
                [ config ],
                verbose=verbose
        )

    def disconnect(self):
        self.disk_image.close()
        USBDevice.disconnect(self)

