# USBPrinter.py 
#
# Contains class definitions to implement a USB printer device.

from mmap import mmap
import os

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBClass import *

from util import *

class USBPrinterClass(USBClass):
    name = "USB printer class"

    def __init__(self, maxusb_app):
     
        self.maxusb_app = maxusb_app
        self.setup_request_handlers()

    def setup_request_handlers(self):
        self.request_handlers = {
            0x00 : self.handle_get_device_ID_request,
        }


    def handle_get_device_ID_request(self, req):

        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True

        if self.maxusb_app.testcase[1] == "Device_ID_Key1":
            device_id_key1 = self.maxusb_app.testcase[2]
        else:
            device_id_key1 = b"MFG"
        if self.maxusb_app.testcase[1] == "Device_ID_Value1":
            device_id_value1 = self.maxusb_app.testcase[2]
        else:
            device_id_value1 = b"Hewlett-Packard"
        if self.maxusb_app.testcase[1] == "Device_ID_Key2":
            device_id_key2 = self.maxusb_app.testcase[2]
        else:
            device_id_key2 = b"CMD"
        if self.maxusb_app.testcase[1] == "Device_ID_Value2":
            device_id_value2 = self.maxusb_app.testcase[2]
        else:
            device_id_value2 = b"PJL,PML,PCLXL,POSTSCRIPT,PCL"
        if self.maxusb_app.testcase[1] == "Device_ID_Key3":
            device_id_key3 = self.maxusb_app.testcase[2]
        else:
            device_id_key3 = b"MDL"
        if self.maxusb_app.testcase[1] == "Device_ID_Value3":
            device_id_value3 = self.maxusb_app.testcase[2]
        else:
            device_id_value3 = b"HP Color LaserJet CP1515n"
        if self.maxusb_app.testcase[1] == "Device_ID_Key4":
            device_id_key4 = self.maxusb_app.testcase[2]
        else:
            device_id_key4 = b"CLS"
        if self.maxusb_app.testcase[1] == "Device_ID_Value4":
            device_id_value4 = self.maxusb_app.testcase[2]
        else:
            device_id_value4 = b"PRINTER"
        if self.maxusb_app.testcase[1] == "Device_ID_Key5":
            device_id_key5 = self.maxusb_app.testcase[2]
        else:
            device_id_key5 = b"DES"
        if self.maxusb_app.testcase[1] == "Device_ID_Value5":
            device_id_value5 = self.maxusb_app.testcase[2]
        else:
            device_id_value5 = b"Hewlett-Packard Color LaserJet CP1515n"
        if self.maxusb_app.testcase[1] == "Device_ID_Key6":
            device_id_key6 = self.maxusb_app.testcase[2]
        else:
            device_id_key6 = b"MEM"
        if self.maxusb_app.testcase[1] == "Device_ID_Value6":
            device_id_value6 = self.maxusb_app.testcase[2]
        else:
            device_id_value6 = b"MEM=55MB"
        if self.maxusb_app.testcase[1] == "Device_ID_Key7":
            device_id_key7 = self.maxusb_app.testcase[2]
        else:
            device_id_key7 = b"COMMENT"
        if self.maxusb_app.testcase[1] == "Device_ID_Value7":
            device_id_value7 = self.maxusb_app.testcase[2]
        else:
            device_id_value7 = b"RES=600x8"


        device_id_length = b"\x00\xAB" # 171 bytes
        device_id_elements  =  device_id_key1 + b":" + device_id_value1 + b";"
        device_id_elements  += device_id_key2 + b":" + device_id_value2 + b";"
        device_id_elements  += device_id_key3 + b":" + device_id_value3 + b";"
        device_id_elements  += device_id_key4 + b":" + device_id_value4 + b";"
        device_id_elements  += device_id_key5 + b":" + device_id_value5 + b";"
        device_id_elements  += device_id_key6 + b":" + device_id_value6 + b";"
        device_id_elements  += device_id_key7 + b":" + device_id_value7 + b";"

        length = len(device_id_elements) + 2
        device_id_length = bytes([
        (length >> 8) & 0xff,
        (length)      & 0xff])

        device_id_response = device_id_length + device_id_elements

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, device_id_response)


class USBPrinterInterface(USBInterface):
    name = "USB printer interface"

    def __init__(self, int_num, maxusb_app, usbclass, sub, proto, verbose=0):
        self.maxusb_app = maxusb_app
        self.int_num = int_num
        descriptors = { }

        endpoints0 = [
            USBEndpoint(
                maxusb_app,
                1,          # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0xff,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x81,          # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                None        # handler function
            )
        ]

        endpoints1 = [
            USBEndpoint(
                maxusb_app,
                0x0b,          # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0xff,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x8b,          # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                None        # handler function
            )
        ]


        if self.int_num == 0:
                endpoints = endpoints0

        if self.int_num == 1:
                endpoints = endpoints1


        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                self.int_num,          # interface number
                0,          # alternate setting
                usbclass,     # interface class
                sub,          # subclass
                proto,       # protocol
                0,          # string index
                verbose,
                endpoints,
                descriptors
        )

        self.device_class = USBPrinterClass(maxusb_app)
        self.device_class.set_interface(self)

        self.is_write_in_progress = False
        self.write_cbw = None
        self.write_base_lba = 0
        self.write_length = 0
        self.write_data = b''

    def handle_data_available(self):

        print ("DEBUG: Here!!")
#        if self.verbose > 0:
#            print(self.name, "handling", len(data), "bytes of printer data")

class USBPrinterDevice(USBDevice):
    name = "USB printer device"

    def __init__(self, maxusb_app, vid, pid, rev, int_class, int_sub, int_proto, verbose=0):

        interface1 = USBPrinterInterface(0, maxusb_app, int_class, int_sub, int_proto, verbose=verbose)

        int_class = 0xff
        int_subclass = 1
        int_proto = 1

        interface2 = USBPrinterInterface(1, maxusb_app, int_class, int_sub, int_proto, verbose=verbose)

        if vid == 0x1111:
            vid = 0x03f0
        if pid == 0x2222:
            pid = 0x4417
        if rev == 0x3333:
            rev = 0x0100

        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Printer",                       # string desc
                [ interface1, interface2 ]                               # interfaces
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
                "Hewlett-Packard",      # manufacturer string
                "HP Color LaserJet CP1515n",               # product string
                "00CNC2618971",         # serial number string
                [ config ],
                verbose=verbose
        )

    def disconnect(self):
        USBDevice.disconnect(self)

