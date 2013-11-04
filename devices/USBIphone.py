# USBIphone.py
#
# Contains class definitions to implement a USB iPhone device.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBCSInterface import *
from USBEndpoint import *
from USBCSEndpoint import *
from USBVendor import *

class USBIphoneVendor(USBVendor):
    name = "USB iPhone vendor"

    def setup_request_handlers(self):
        self.request_handlers = {
             0x40 : self.handle_40_request,
             0x45 : self.handle_45_request

        }

    def handle_40_request(self, req):
        if self.verbose > 0:
            print(self.name, "received reset request")

        self.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_45_request(self, req):
        if self.verbose > 0:
            print(self.name, "received reset request")

        self.device.maxusb_app.send_on_endpoint(0, b'\x03')




class USBIphoneClass(USBClass):
    name = "USB iPhone class"

    def __init__(self, maxusb_app):

        self.maxusb_app = maxusb_app
        self.setup_request_handlers()

    def setup_request_handlers(self):
        self.request_handlers = {
            0x22 : self.handle_set_control_line_state,
            0x20 : self.handle_set_line_coding
        }

    def handle_set_control_line_state(self, req):
        self.maxusb_app.send_on_endpoint(0, b'')
        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True

    def handle_set_line_coding(self, req):
        self.maxusb_app.send_on_endpoint(0, b'')



class USBIphoneInterface(USBInterface):
    name = "USB iPhone interface"

    def __init__(self, int_num, maxusb_app, usbclass, sub, proto, verbose=0):

        self.maxusb_app = maxusb_app
        self.int_num = int_num

        descriptors = { }

        endpoints0 = [
            USBEndpoint(
                maxusb_app,
                0x02,           # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x0a,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x81,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x0a,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x83,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x4000,         # max packet size
                0x0a,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )

        ]


        endpoints1 = [
            USBEndpoint(
                maxusb_app,
                0x04,           # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                0x85,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]


        endpoints2 = []


        if self.int_num == 0:
                endpoints = endpoints0

        elif self.int_num == 1:
                endpoints = endpoints1

        elif self.int_num == 2:
                endpoints = endpoints2




        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                self.int_num,          # interface number
                0,          # alternate setting
                usbclass,          # 3 interface class
                sub,          # 0 subclass
                proto,          # 0 protocol
                0,          # string index
                verbose,
                endpoints,
                descriptors
        )

        self.device_class = USBIphoneClass(maxusb_app)
        self.device_class.set_interface(self)


    def handle_data_available(self, data):
        if self.verbose > 0:
            print(self.name, "handling", len(data), "bytes of audio data")
    



class USBIphoneDevice(USBDevice):
    name = "USB iPhone device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):

        int_class = 0
        int_subclass = 0
        int_proto = 0
        interface0 = USBIphoneInterface(0, maxusb_app, 0x06, 0x01, 0x01,verbose=verbose)
        interface1 = USBIphoneInterface(1, maxusb_app, 0xff, 0xfe, 0x02,verbose=verbose)
        interface2 = USBIphoneInterface(2, maxusb_app, 0xff, 0xfd, 0x01,verbose=verbose)


        config = [
            USBConfiguration(                
                maxusb_app,
                1,                          # index
                "iPhone",             # string desc
                [ interface0, interface1, interface2 ]  # interfaces
            ),
            USBConfiguration(
                maxusb_app,
                2,                          # index
                "iPhone",             # string desc
                [ interface0, interface1, interface2 ]  # interfaces
            ),
            USBConfiguration(
                maxusb_app,
                3,                          # index
                "iPhone",             # string desc
                [ interface0, interface1, interface2 ]  # interfaces
            ),
            USBConfiguration(
                maxusb_app,
                4,                          # index
                "iPhone",             # string desc
                [ interface0, interface1, interface2 ]  # interfaces
            )

        ]


        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # 0 device class
		        0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
		        0x05ac,                 # vendor id
                0x1297,                 # product id
		        0x0310,                 # device revision
                "Apple",                # manufacturer string
                "iPhone",               # product string
                "a9f579a7e04281fbf77fe04d06b5cc083e6eb5a3",               # serial number string
                config,
                verbose=verbose
        )
        self.device_vendor = USBIphoneVendor()
        self.device_vendor.set_device(self)



