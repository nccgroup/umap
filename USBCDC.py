# USBCDC.py
#
# Contains class definitions to implement a USB CDC device.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBCSInterface import *
from USBEndpoint import *
from USBCSEndpoint import *


class USBCDCClass(USBClass):
    name = "USB CDC class"

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



class USBCDCInterface(USBInterface):
    name = "USB CDC interface"

    def __init__(self, int_num, maxusb_app, usbclass, sub, proto, verbose=0):

        self.maxusb_app = maxusb_app
        self.int_num = int_num

        descriptors = { }

        cs_config1 = [
            0x00,           # Header Functional Descriptor
            0x1001,         # bcdCDC
        ]

        bmCapabilities = 0x03
        bDataInterface = 0x01

        cs_config2 = [
            0x01,           # Call Management Functional Descriptor
            bmCapabilities,
            bDataInterface
        ]

        bmCapabilities = 0x06

        cs_config3 = [
            0x02,           # Abstract Control Management Functional Descriptor
            bmCapabilities
        ]

        bControlInterface = 0
        bSubordinateInterface0 = 1

        cs_config4 = [
            0x06,       # Union Functional Descriptor
            bControlInterface,
            bSubordinateInterface0
        ]

        cs_interfaces0 = [
            USBCSInterface (
                maxusb_app,
                cs_config1,
                2,
                2,
                1
            ),
            USBCSInterface (
                maxusb_app,
                cs_config2,
                2,
                2,
                1
            ),
            USBCSInterface (
                maxusb_app,
                cs_config3,
                2,
                2,
                1
            ),
            USBCSInterface (
                maxusb_app,
                cs_config4,
                2,
                2,
                1
            )

        ]


        cs_interfaces1 = []

        endpoints0 = [
            USBEndpoint(
                maxusb_app,
                0x83,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x2000,         # max packet size
                0xff,           # polling interval, see USB 2.0 spec Table 9-13
                #self.handle_data_available    # handler function
                None
            )
        ]


        endpoints1 = [
            USBEndpoint(
                maxusb_app,
                0x81,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x2000,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                #self.handle_data_available    # handler function
                None
            ),
            USBEndpoint(
                maxusb_app,
                0x02,           # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x2000,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]

        if self.int_num == 0:
                endpoints = endpoints0
                cs_interfaces = cs_interfaces0

        elif self.int_num == 1:
                endpoints = endpoints1
                cs_interfaces = cs_interfaces1




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
                descriptors,
                cs_interfaces
        )

        self.device_class = USBCDCClass(maxusb_app)
        self.device_class.set_interface(self)


    def handle_data_available(self, data):
        if self.verbose > 0:
            print(self.name, "handling", len(data), "bytes of audio data")
    



class USBCDCDevice(USBDevice):
    name = "USB CDC device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):

        int_class = 2
        int_subclass = 0
        int_proto = 0
        interface0 = USBCDCInterface(0, maxusb_app, 0x02, 0x02, 0x01,verbose=verbose)
        interface1 = USBCDCInterface(1, maxusb_app, 0x0a, 0x00, 0x00,verbose=verbose)

        if vid == 0x1111:
            vid = 0x2548
        if pid == 0x2222:
            pid = 0x1001
        if rev == 0x3333:
            rev = 0x1000


        config = USBConfiguration(
                maxusb_app,
                1,                          # index
                "Emulated CDC",             # string desc
                [ interface0, interface1 ]  # interfaces
        )


        USBDevice.__init__(
                self,
                maxusb_app,
                2,                      # 0 device class
		        0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
		        vid,                 # vendor id
                pid,                 # product id
		        rev,                 # device revision
                "Vendor",               # manufacturer string
                "Product",              # product string
                "Serial",               # serial number string
                [ config ],
                verbose=verbose
        )

