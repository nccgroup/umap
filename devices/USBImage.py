# USBImage.py 
#
# Contains class definitions to implement a USB image device.

from mmap import mmap
import os

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBClass import *

from util import *

class USBImageClass(USBClass):
    name = "USB image class"

    def setup_request_handlers(self):
        self.request_handlers = {
            0x66 : self.handle_device_reset_request,
        }

    def handle_device_reset_request(self, req):
        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')



class USBImageInterface(USBInterface):
    name = "USB image interface"

    def __init__(self, int_num, maxusb_app, thumb_image, partial_image, usbclass, sub, proto, verbose=0):
        self.thumb_image = thumb_image
        self.partial_image = partial_image
        self.maxusb_app = maxusb_app
        self.int_num = int_num
        descriptors = { }

        endpoints = [
            USBEndpoint(
                maxusb_app,
                1,          # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x4000,      # max packet size
                0x00,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x82,          # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x4000,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
                #None        # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x83,          # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0800,      # max packet size
                0x10,          # polling interval, see USB 2.0 spec Table 9-13
                #None        # handler function
                self.handle_data_available    # handler function

            )


        ]


        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                self.int_num,          # interface number
                0,          # alternate setting
                usbclass,          # interface class
                sub,          # subclass
                proto,       # protocol
                0,          # string index
                verbose,
                endpoints,
                descriptors
        )

        self.device_class = USBImageClass()
        self.device_class.set_interface(self)


    def create_send_ok (self, transaction_id):

        if self.verbose > 0:
            print(self.name, "sent Image:OK")


        container_type = b'\x00\x03' # Response block
        response_code = b'\x20\x01'  # "OK"
        container_length = b'\x00\x00\x00\x0c' # always this length

        response = change_byte_order(container_length) + \
                   change_byte_order(container_type) + \
                   change_byte_order(response_code) + \
                   change_byte_order(transaction_id)

        return response

    def handle_data_available(self, data):
        if self.verbose > 0:
            print(self.name, "handling", len(data), "bytes of Image class data")

        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True

        container = ContainerRequestWrapper(data)
        opcode = container.operation_code[1] << 8 | container.operation_code[0] 
        container_type = container.container_type[1] << 8 | \
                        container.container_type[0] 
        
        #print ("DEBUG: container type:", container_type) 


        if self.maxusb_app.testcase[1] == "DeviceInfo_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "StorageIDArray_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "StorageInfo_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "ObjectHandles_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "ObjectInfo_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "ThumbData_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        elif self.maxusb_app.testcase[1] == "PartialData_TransactionID":
            transaction_id = change_byte_order(self.maxusb_app.testcase[2])
        else:
            transaction_id = bytes ([container.transaction_id[3], \
                                     container.transaction_id[2], \
                                     container.transaction_id[1], \
                                     container.transaction_id[0]]) 

        status = 0              # default to success
        response = None         # with no response data
        response2 = None

        if self.maxusb_app.server_running == True:
            try:
                self.maxusb_app.netserver_from_endpoint_sd.send(data)
            except:
                print ("Error: No network client connected")
            while True:
                if len(self.maxusb_app.reply_buffer) > 0:
                    self.maxusb_app.send_on_endpoint(2, self.maxusb_app.reply_buffer)
                    self.maxusb_app.reply_buffer = ""
                    break



        elif opcode == 0x1002:      # OpenSession
            if self.verbose > 0:
                print(self.name, "got OpenSession")

            response = self.create_send_ok(transaction_id)




        elif opcode == 0x1016:      # SetDevicePropValue
            if self.verbose > 0:
                print(self.name, "got SetDevicePropValue")

            if container_type == 2: #Data block
                response = self.create_send_ok(transaction_id)



        elif opcode == 0x100a:      # GetThumb
            if self.verbose > 0:
                print(self.name, "got GetThumb")
            thumb_data = (self.thumb_image.read_data())

            if self.maxusb_app.testcase[1] == "ThumbData_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block
            if self.maxusb_app.testcase[1] == "ThumbData_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x0a' # GetThumb
                thumbnail_data_object = thumb_data

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) 

            x = 0
            while x < len(thumbnail_data_object):
                response += bytes([thumbnail_data_object[x]])
                x+=1

            container_length = len(response) + 4


            if self.maxusb_app.testcase[1] == "ThumbData_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)



        elif opcode == 0x101b:      # GetPartialObject
            if self.verbose > 0:
                print(self.name, "got GetPartialObject")


#            return
#            partial_data = (self.partial_image.read_data())

#            if self.maxusb_app.testcase[1] == "PartialObject_ContainerType":
#                container_type = change_byte_order(self.maxusb_app.testcase[2])
#            else:
#                container_type = b'\x00\x02' # Data block
#            if self.maxusb_app.testcase[1] == "PartialObject_OperationCode":
#                operation_code = change_byte_order(self.maxusb_app.testcase[2])
#            else:
#                operation_code = b'\x10\x1b' # GetPartialObject
#                data_object = partial_data
#
#            response = change_byte_order(container_type) + \
#                       change_byte_order(operation_code) + \
#                       change_byte_order(transaction_id)
#
#            x = 0
#            while x < len(data_object):
#                response += bytes([data_object[x]])
#                x+=1
#
#            container_length = len(response) + 4
#
#
#            if self.maxusb_app.testcase[1] == "PartialObject_ContainerLength":
#                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
#            else:
#                container_length_bytes = bytes([
#                (container_length      ) & 0xff,
#                (container_length >>  8) & 0xff,
#                (container_length >> 16) & 0xff,
#                (container_length >> 24) & 0xff])

#            response = container_length_bytes + response
#            response2 = self.create_send_ok(transaction_id)






        elif opcode == 0x1001:      # GetDeviceInfo
            if self.verbose > 0:
                print(self.name, "got GetDeviceInfo")

            if self.maxusb_app.testcase[1] == "DeviceInfo_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block
            
            if self.maxusb_app.testcase[1] == "DeviceInfo_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x01' # GetDeviceInfo
            #transaction ID
            if self.maxusb_app.testcase[1] == "DeviceInfo_StandardVersion":
                standard_version = change_byte_order(self.maxusb_app.testcase[2])
            else:
                standard_version = b'\x00\x64' # version 1.0
            if self.maxusb_app.testcase[1] == "DeviceInfo_VendorExtensionID":
                vendor_extension_id = change_byte_order(self.maxusb_app.testcase[2])
            else:
                vendor_extension_id = b'\x00\x00\x00\x06' # Microsoft Corporation
            if self.maxusb_app.testcase[1] == "DeviceInfo_VendorExtensionVersion":
                vendor_extension_version = change_byte_order(self.maxusb_app.testcase[2])
            else:
                vendor_extension_version = b'\x00\x64' # version 1.0
            if self.maxusb_app.testcase[1] == "DeviceInfo_VendorExtensionDesc":
                vendor_extension_desc = change_byte_order(self.maxusb_app.testcase[2])
            else:
                vendor_extension_desc = b'\x00'
            if self.maxusb_app.testcase[1] == "DeviceInfo_FunctionalMode":
                functional_mode = change_byte_order(self.maxusb_app.testcase[2])
            else:
                functional_mode = b'\x00\x00' # standard mode
           
            if self.maxusb_app.testcase[1] == "DeviceInfo_OperationsSupportedArraySize":
                operations_supported_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operations_supported_array_size = b'\x00\x00\x00\x10' # 16 operations supported
       
            if self.maxusb_app.testcase[1] == "DeviceInfo_OperationSupported":
                op1_supported = change_byte_order(self.maxusb_app.testcase[2])
            else:
                op1_supported = b'\x10\x01' # GetDeviceInfo
            op2_supported = b'\x10\x02' # OpenSession
            op3_supported = b'\x10\x03' # CloseSession
            op4_supported = b'\x10\x04' # GetStorageIDs
            op5_supported = b'\x10\x05' # GetStorageInfo
            op6_supported = b'\x10\x06' # GetNumObjects
            op7_supported = b'\x10\x07' # GetObjectHandles
            op8_supported = b'\x10\x08' # GetObjectInfo
            op9_supported = b'\x10\x09' # GetObject
            op10_supported = b'\x10\x0a' # GetThumb
            op11_supported = b'\x10\x0c' # SendObjectInfo
            op12_supported = b'\x10\x0d' # SendObject
            op13_supported = b'\x10\x14' # GetDevicePropDesc
            op14_supported = b'\x10\x15' # GetDevicePropValue
            op15_supported = b'\x10\x16' # SetDevicePropValue
            op16_supported = b'\x10\x1b' # GetPartialObject
 
            if self.maxusb_app.testcase[1] == "DeviceInfo_EventsSupportedArraySize":
                events_supported_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                events_supported_array_size = b'\x00\x00\x00\x04' # 4 events supported

            if self.maxusb_app.testcase[1] == "DeviceInfo_EventSupported":
                ev1_supported = change_byte_order(self.maxusb_app.testcase[2])
            else:
                ev1_supported = b'\x40\x04' # StoredAdded
            ev2_supported = b'\x40\x05' # StoreRemoved
            ev3_supported = b'\x40\x08' # DeviceInfoChanged
            ev4_supported = b'\x40\x09' # RequestObjectTransfer

            if self.maxusb_app.testcase[1] == "DeviceInfo_DevicePropertiesSupportedArraySize":
                device_properties_supported_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                device_properties_supported_array_size = b'\x00\x00\x00\x02' # 2 properties supported

            if self.maxusb_app.testcase[1] == "DeviceInfo_DevicePropertySupported":
                dp1_supported = change_byte_order(self.maxusb_app.testcase[2])
            else:
                dp1_supported = b'\xd4\x06' # Unknown property 
            dp2_supported = b'\xd4\x07' # Unknown property

            if self.maxusb_app.testcase[1] == "DeviceInfo_CaptureFormatsSupportedArraySize":
                capture_formats_supported_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                capture_formats_supported_array_size = b'\x00\x00\x00\x00' # 0 formats supported

            if self.maxusb_app.testcase[1] == "DeviceInfo_ImageFormatsSupportedArraySize":
                image_formats_supported_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                image_formats_supported_array_size = b'\x00\x00\x00\x06' # 6 formats supported

            if self.maxusb_app.testcase[1] == "DeviceInfo_ImageFormatSupported":
                if1_supported = change_byte_order(self.maxusb_app.testcase[2])
            else:
                if1_supported = b'\x30\x01' # Association (Folder)
            if2_supported = b'\x30\x02' # Script
            if3_supported = b'\x30\x06' # DPOF
            if4_supported = b'\x30\x0d' # Unknown image format
            if5_supported = b'\x38\x01' # EXIF/JPEG
            if6_supported = b'\x38\x0d' # TIFF

            manufacturer = b'P\x00a\x00n\x00a\x00s\x00o\x00n\x00i\x00c\x00\x00\x00'
            manufacturer_length = len(manufacturer) / 2
            model = b'D\x00M\x00C\x00-\x00F\x00S\x007\x00\x00\x00'
            model_length = len(model) /2
            device_version = b'1\x00.\x000\x00\x00\x00'
            device_version_length = len(device_version) /2
            serial_number = b'0\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x000\x001\x00X\x000\x002\x000\x009\x000\x003\x000\x007\x005\x004\x00\x00\x00\x00\x00'
            serial_number_length = len(serial_number) /2

            device_version_length_bytes = int_to_bytestring(device_version_length)
            serial_number_length_bytes = int_to_bytestring(serial_number_length)

            if self.maxusb_app.testcase[1] == "DeviceInfo_Manufacturer":
                manufacturer = change_byte_order(self.maxusb_app.testcase[2])
                manufacturer_length_bytes = b''
            else:
                manufacturer_length_bytes = int_to_bytestring(manufacturer_length)

            if self.maxusb_app.testcase[1] == "DeviceInfo_Model":
                model = change_byte_order(self.maxusb_app.testcase[2])
                model_length_bytes = b''
            else:
                model_length_bytes = int_to_bytestring(model_length)

            if self.maxusb_app.testcase[1] == "DeviceInfo_DeviceVersion":
                device_version = change_byte_order(self.maxusb_app.testcase[2])
                device_version_length_bytes = b''
            else:
                device_version_length_bytes = int_to_bytestring(device_version_length)

            if self.maxusb_app.testcase[1] == "DeviceInfo_SerialNumber":
                serial_number = change_byte_order(self.maxusb_app.testcase[2])
                serial_number_length_bytes = b''
            else:
                serial_number_length_bytes = int_to_bytestring(serial_number_length)

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) + \
                       change_byte_order(standard_version) + \
                       change_byte_order(vendor_extension_id) + \
                       change_byte_order(vendor_extension_version) + \
                       change_byte_order(vendor_extension_desc) + \
                       change_byte_order(functional_mode) + \
                       change_byte_order(operations_supported_array_size) + \
                       change_byte_order(op1_supported) + \
                       change_byte_order(op2_supported) + \
                       change_byte_order(op3_supported) + \
                       change_byte_order(op4_supported) + \
                       change_byte_order(op5_supported) + \
                       change_byte_order(op6_supported) + \
                       change_byte_order(op7_supported) + \
                       change_byte_order(op8_supported) + \
                       change_byte_order(op9_supported) + \
                       change_byte_order(op10_supported) + \
                       change_byte_order(op11_supported) + \
                       change_byte_order(op12_supported) + \
                       change_byte_order(op13_supported) + \
                       change_byte_order(op14_supported) + \
                       change_byte_order(op15_supported) + \
                       change_byte_order(op16_supported) + \
                       change_byte_order(events_supported_array_size) + \
                       change_byte_order(ev1_supported) + \
                       change_byte_order(ev2_supported) + \
                       change_byte_order(ev3_supported) + \
                       change_byte_order(ev4_supported) + \
                       change_byte_order(device_properties_supported_array_size) + \
                       change_byte_order(dp1_supported) + \
                       change_byte_order(dp2_supported) + \
                       change_byte_order(capture_formats_supported_array_size) + \
                       change_byte_order(image_formats_supported_array_size) + \
                       change_byte_order(if1_supported) + \
                       change_byte_order(if2_supported) + \
                       change_byte_order(if3_supported) + \
                       change_byte_order(if4_supported) + \
                       change_byte_order(if5_supported) + \
                       change_byte_order(if6_supported) + \
                       manufacturer_length_bytes + \
                       manufacturer + \
                       model_length_bytes + \
                       model + \
                       device_version_length_bytes + \
                       device_version + \
                       serial_number_length_bytes + \
                       serial_number

            

            if self.maxusb_app.testcase[1] == "DeviceInfo_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length = len(response) + 4
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)


        elif opcode == 0x1003:      # CloseSession
            if self.verbose > 0:
                print(self.name, "got CloseSession")

            response = self.create_send_ok(transaction_id)


        elif opcode == 0x1004:      # GetSTorageIDs
            if self.verbose > 0:
                print(self.name, "got GetStorageIDs")


            if self.maxusb_app.testcase[1] == "StorageIDArray_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block

            if self.maxusb_app.testcase[1] == "StorageIDArray_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x04' # GetStorageID

            if self.maxusb_app.testcase[1] == "StorageIDArray_StorageIDsArraySize":
                storage_id_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                storage_id_array_size = b'\x00\x00\x00\x01' # 1 storage ID


            if self.maxusb_app.testcase[1] == "StorageIDArray_StorageID":
                storage_id = change_byte_order(self.maxusb_app.testcase[2])
            else:
                storage_id = b'\x00\x01\x00\x01' # Phys: 0x0001 Log: 0x0001

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) + \
                       change_byte_order(storage_id_array_size) + \
                       change_byte_order(storage_id)

            container_length = len(response) + 4


            if self.maxusb_app.testcase[1] == "StorageIDArray_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)




        elif opcode == 0x1007:      # GetObjectHandles
            if self.verbose > 0:
                print(self.name, "got GetObjectHandles")


            if self.maxusb_app.testcase[1] == "ObjectHandles_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block

            if self.maxusb_app.testcase[1] == "ObjectHandles_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x07' # GetObjectHandles

            if self.maxusb_app.testcase[1] == "ObjectHandles_ObjectHandleArraySize":
                object_handle_array_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                object_handle_array_size = b'\x00\x00\x00\x01' # 1 array size
            if self.maxusb_app.testcase[1] == "ObjectHandles_ObjectHandle":
                object_handle = change_byte_order(self.maxusb_app.testcase[2])
            else:
                object_handle = b'\x42\x19\x42\xca' # Object handle

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) + \
                       change_byte_order(object_handle_array_size) + \
                       change_byte_order(object_handle) 

            container_length = len(response) + 4

            if self.maxusb_app.testcase[1] == "ObjectHandles_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)


        elif opcode == 0x1008:      # GetObjectInfo
            if self.verbose > 0:
                print(self.name, "got GetObjectInfo")


            if self.maxusb_app.testcase[1] == "ObjectInfo_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block
            if self.maxusb_app.testcase[1] == "ObjectInfo_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x08' # GetObjectInfo
            if self.maxusb_app.testcase[1] == "ObjectInfo_StorageID":
                storage_id = change_byte_order(self.maxusb_app.testcase[2])
            else:
                storage_id = b'\x00\x01\x00\x01' # Phy: 0x0001 Log: 0x0001
            if self.maxusb_app.testcase[1] == "ObjectInfo_ObjectFormat":
                object_format = change_byte_order(self.maxusb_app.testcase[2])
            else:
                object_format = b'\x38\x01' # EXIF/JPEG
            if self.maxusb_app.testcase[1] == "ObjectInfo_ProtectionStatus":
                protection_status = change_byte_order(self.maxusb_app.testcase[2])
            else:
                protection_status = b'\x00\x00' # no protection
            if self.maxusb_app.testcase[1] == "ObjectInfo_ObjectCompressedSize":
                object_compressed_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                object_compressed_size = b'\x00\x31\xd6\x58' # 3266136
            if self.maxusb_app.testcase[1] == "ObjectInfo_ThumbFormat":
                thumb_format = change_byte_order(self.maxusb_app.testcase[2])
            else:
                thumb_format = b'\x38\x08' # JFIF
            if self.maxusb_app.testcase[1] == "ObjectInfo_ThumbCompressedSize":
                thumb_compressed_size = change_byte_order(self.maxusb_app.testcase[2])
            else:
                thumb_compressed_size = b'\x00\x00\x0d\xcd' # 3533
            if self.maxusb_app.testcase[1] == "ObjectInfo_ThumbPixelWidth":
                thumb_pixel_width = change_byte_order(self.maxusb_app.testcase[2])
            else:
                thumb_pixel_width = b'\x00\x00\x00\xa0' # 160
            if self.maxusb_app.testcase[1] == "ObjectInfo_ThumbPixelHeight":
                thumb_pixel_height = change_byte_order(self.maxusb_app.testcase[2])
            else:
                thumb_pixel_height = b'\x00\x00\x00\x78' # 120
            if self.maxusb_app.testcase[1] == "ObjectInfo_ImagePixelWidth":
                image_pixel_width = change_byte_order(self.maxusb_app.testcase[2])
            else:
                image_pixel_width = b'\x00\x00\x0e\x40' # 3648
            if self.maxusb_app.testcase[1] == "ObjectInfo_ImagePixelHeight":
                image_pixel_height = change_byte_order(self.maxusb_app.testcase[2])
            else:
                image_pixel_height = b'\x00\x00\x0a\xb0' # 2736
            if self.maxusb_app.testcase[1] == "ObjectInfo_ImagePixelDepth":
                image_pixel_depth = change_byte_order(self.maxusb_app.testcase[2])
            else:
                image_pixel_depth = b'\x00\x00\x00\x18' # 24
            if self.maxusb_app.testcase[1] == "ObjectInfo_ParentObject":
                parent_object = change_byte_order(self.maxusb_app.testcase[2])
            else:
                parent_object = b'\x00\x00\x00\x00' # Object handle = 0
            if self.maxusb_app.testcase[1] == "ObjectInfo_AssociationType":
                association_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                association_type = b'\x00\x00' # undefined
            if self.maxusb_app.testcase[1] == "ObjectInfo_AssociationDesc":
                association_desc = change_byte_order(self.maxusb_app.testcase[2])
            else:
                association_desc = b'\x00\x00\x00\x00' # undefined
            if self.maxusb_app.testcase[1] == "ObjectInfo_SequenceNumber":
                sequence_number = change_byte_order(self.maxusb_app.testcase[2])
            else:
                sequence_number = b'\x00\x00\x00\x00' # 0
            if self.maxusb_app.testcase[1] == "ObjectInfo_Filename":
                filename = change_byte_order(self.maxusb_app.testcase[2])
            else:
                filename = b'\x0D\x50\x00\x31\x00\x30\x00\x31\x00\x30\x00\x37\x00\x34\x00\x39\x00\x2E\x00\x4A\x00\x50\x00\x47\x00\x00\x00' # P1010749.JPG
            if self.maxusb_app.testcase[1] == "ObjectInfo_CaptureDate":
                capture_date = change_byte_order(self.maxusb_app.testcase[2])
            else:
                capture_date = b'\x10\x32\x00\x30\x00\x31\x00\x33\x00\x30\x00\x37\x00\x32\x00\x33\x00\x54\x00\x31\x00\x31\x00\x30\x00\x35\x00\x30\x00\x36\x00\x00\x00' # 20130723T110506
            if self.maxusb_app.testcase[1] == "ObjectInfo_ModificationDate":
                modification_date = change_byte_order(self.maxusb_app.testcase[2])
            else:
                modification_date = b'\x10\x32\x00\x30\x00\x31\x00\x33\x00\x30\x00\x37\x00\x32\x00\x33\x00\x54\x00\x31\x00\x31\x00\x30\x00\x35\x00\x30\x00\x36\x00\x00\x00' # 20130723T110506

            if self.maxusb_app.testcase[1] == "ObjectInfo_Keywords":
                keywords = change_byte_order(self.maxusb_app.testcase[2])
            else:
                keywords = b'\x00' # none

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) + \
                       change_byte_order(storage_id) + \
                       change_byte_order(object_format) + \
                       change_byte_order(protection_status) + \
                       change_byte_order(object_compressed_size) + \
                       change_byte_order(thumb_format) + \
                       change_byte_order(thumb_compressed_size) + \
                       change_byte_order(thumb_pixel_width) + \
                       change_byte_order(thumb_pixel_height) + \
                       change_byte_order(image_pixel_width) + \
                       change_byte_order(image_pixel_height) + \
                       change_byte_order(image_pixel_depth) + \
                       change_byte_order(parent_object) + \
                       change_byte_order(association_type) + \
                       change_byte_order(association_desc) + \
                       change_byte_order(sequence_number) + \
                       filename + \
                       capture_date + \
                       modification_date + \
                       keywords 

            container_length = len(response) + 4

            if self.maxusb_app.testcase[1] == "ObjectInfo_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)




        elif opcode == 0x1005:      # GetSTorageInfo
            if self.verbose > 0:
                print(self.name, "got GetStorageInfo")

            if self.maxusb_app.testcase[1] == "StorageInfo_ContainerType":
                container_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_type = b'\x00\x02' # Data block
            if self.maxusb_app.testcase[1] == "StorageInfo_OperationCode":
                operation_code = change_byte_order(self.maxusb_app.testcase[2])
            else:
                operation_code = b'\x10\x05' # GetStorageInfo

            if self.maxusb_app.testcase[1] == "StorageInfo_StorageType":
                storage_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                storage_type = b'\x00\x04' # Removable RAM
            if self.maxusb_app.testcase[1] == "StorageInfo_FilesystemType":
                filesystem_type = change_byte_order(self.maxusb_app.testcase[2])
            else:
                filesystem_type = b'\x00\x03' # DCF (Design rule for Camera File system)

            if self.maxusb_app.testcase[1] == "StorageInfo_AccessCapability":
                access_capability = change_byte_order(self.maxusb_app.testcase[2])
            else:
                access_capability = b'\x00\x00' # Read-write

            if self.maxusb_app.testcase[1] == "StorageInfo_MaxCapacity":
                max_capacity = change_byte_order(self.maxusb_app.testcase[2])
            else:
                max_capacity = b'\x00\x00\x00\x00\x78\x18\x00\x00' # 2014838784 bytes

            if self.maxusb_app.testcase[1] == "StorageInfo_FreeSpaceInBytes":
                free_space_in_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                free_space_in_bytes = b'\x00\x00\x00\x00\x77\xda\x80\x00' # 2010808320 bytes


            if self.maxusb_app.testcase[1] == "StorageInfo_FreeSpaceInImages":
                free_space_in_images = change_byte_order(self.maxusb_app.testcase[2])
            else:
                free_space_in_images = b'\x00\x00\x00\x00' # 0 bytes

            if self.maxusb_app.testcase[1] == "StorageInfo_StorageDescription":
                storage_description = change_byte_order(self.maxusb_app.testcase[2])
            else:
                storage_description = b'\x00'

            if self.maxusb_app.testcase[1] == "StorageInfo_VolumeLabel":
                volume_label = change_byte_order(self.maxusb_app.testcase[2])
            else:
                volume_label = b'\x00' 

            response = change_byte_order(container_type) + \
                       change_byte_order(operation_code) + \
                       change_byte_order(transaction_id) + \
                       change_byte_order(storage_type) + \
                       change_byte_order(filesystem_type) + \
                       change_byte_order(access_capability) + \
                       change_byte_order(max_capacity) + \
                       change_byte_order(free_space_in_bytes) + \
                       change_byte_order(free_space_in_images) + \
                       change_byte_order(storage_description) + \
                       change_byte_order(volume_label)

            container_length = len(response) + 4

            if self.maxusb_app.testcase[1] == "StorageInfo_ContainerLength":
                container_length_bytes = change_byte_order(self.maxusb_app.testcase[2])
            else:
                container_length_bytes = bytes([
                (container_length      ) & 0xff,
                (container_length >>  8) & 0xff,
                (container_length >> 16) & 0xff,
                (container_length >> 24) & 0xff])

            response = container_length_bytes + response
            response2 = self.create_send_ok(transaction_id)


        if response and self.maxusb_app.server_running == False:
            if self.verbose > 2:
                print(self.name, "responding with", len(response), "bytes:",
                        bytes_as_hex(response))

            self.configuration.device.maxusb_app.send_on_endpoint(2, response)


        if response2 and self.maxusb_app.server_running == False:
            if self.verbose > 2:
                print(self.name, "responding with", len(response2), "bytes:",
                        bytes_as_hex(response2))

            self.configuration.device.maxusb_app.send_on_endpoint(2, response2)






class ThumbImage:
    def __init__(self, filename):
        self.filename = filename

        self.file = open(self.filename, 'r+b')
        self.image = mmap(self.file.fileno(), 0)

    def close(self):
        self.image.flush()
        self.image.close()

    def read_data(self):
        return self.image



class ContainerRequestWrapper:
    def __init__(self, bytestring):
        self.container_length       = bytestring[0:4]
        self.container_type         = bytestring[4:6]
        self.operation_code         = bytestring[6:8]
        self.transaction_id         = bytestring[8:12]
        self.parameter1             = bytestring[12:16]



class USBImageDevice(USBDevice):
    name = "USB image device"

    def __init__(self, maxusb_app, vid, pid, rev, int_class, int_sub, int_proto, thumb_image_filename, verbose=0):
        self.thumb_image = ThumbImage("ncc_group_logo.jpg")
        self.partial_image = ThumbImage("ncc_group_logo.bin")

        interface1 = USBImageInterface(0, maxusb_app, self.thumb_image, self.partial_image, int_class, int_sub, int_proto, verbose=verbose)


        if vid == 0x1111:
            vid = 0x04da
        if pid == 0x2222:
            pid = 0x2374
        if rev == 0x3333:
            rev = 0x0010


        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Image",                       # string desc
                [ interface1 ]                               # interfaces
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
                "Panasonic",            # manufacturer string
                "DMC-FS7",              # product string
                "0000000000000000001X0209030754",         # serial number string
                [ config ],
                verbose=verbose
        )

    def disconnect(self):
        self.disk_image.close()
        USBDevice.disconnect(self)

