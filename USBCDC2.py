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
            0x00 : self.handle_send_encapsulated_command,
            0x01 : self.handle_get_encapsulated_response,
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

    def handle_send_encapsulated_command(self, req):
        self.maxusb_app.send_on_endpoint(0, b'')

    def handle_get_encapsulated_response(self, req):
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

        bmCapabilities = 0x00
        bDataInterface = 0x01

        cs_config2 = [
            0x01,           # Call Management Functional Descriptor
            bmCapabilities,
            bDataInterface
        ]

        bmCapabilities = 0x00

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
                0xff
            ),
            USBCSInterface (
                maxusb_app,
                cs_config2,
                2,
                2,
                0xff
            ),
            USBCSInterface (
                maxusb_app,
                cs_config3,
                2,
                2,
                0xff
            ),
            USBCSInterface (
                maxusb_app,
                cs_config4,
                2,
                2,
                0xff
            )

        ]


        cs_interfaces1 = []




        cs_config5 = [
            0x00,           # Header Functional Descriptor
            0x1001,         # bcdCDC
        ]


        bControlInterface = 0
        bSubordinateInterface0 = 1

        cs_config6 = [
            0x06,       # Union Functional Descriptor
            bControlInterface,
            bSubordinateInterface0
        ]





#        iMACAddress = self.get_string_id("020406080a0c")
        iMACAddress = 0
        bmEthernetStatistics = 0x00000000
        wMaxSegmentSize = 0xea05
        wNumberMCFilters = 0x0000
        bNumberPowerFilters = 0x00

        cs_config7 = [
            0x0f,       # Ethernet Networking Functional Descriptor
            iMACAddress,
            bmEthernetStatistics,
            wMaxSegmentSize,
            wNumberMCFilters,
            bNumberPowerFilters            
        ]

        cs_interfaces2 = [
            USBCSInterface (
                maxusb_app,
                cs_config5,
                2,
                6,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config6,
                2,
                6,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config7,
                2,
                6,
                0
            )

        ]

        cs_interfaces3 = []






        endpoints0 = [
            USBEndpoint(
                maxusb_app,
                3,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0800,         # max packet size
                0x09,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]


        endpoints1 = [
            USBEndpoint(
                maxusb_app,
                3,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                1,           # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]


        endpoints2 = [
            USBEndpoint(
                maxusb_app,
                3,           # 2 endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x1000,         # max packet size
                0x09,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]


        endpoints3 = [
            USBEndpoint(
                maxusb_app,
                3,           # 1 endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
                0x00,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                1,           # endpoint address
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0002,         # max packet size
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

        elif self.int_num == 2:
                endpoints = endpoints2
                cs_interfaces = cs_interfaces2

        elif self.int_num == 3:
                endpoints = endpoints3
                cs_interfaces = cs_interfaces3


        if self.int_num == 2:   #Ugly hack
            self.int_num = 0

        if self.int_num == 3:
            self.int_num = 1




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


    def handle_data_available(self):
        #print(self.name, "handling", len(data), "bytes of data")
        return



class USBCDCDevice(USBDevice):
    name = "USB CDC device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):

        interface0 = USBCDCInterface(0, maxusb_app, 0x02, 0x02, 0xff,verbose=verbose)
        interface1 = USBCDCInterface(1, maxusb_app, 0x0a, 0x00, 0x00,verbose=verbose)
        interface2 = USBCDCInterface(2, maxusb_app, 0x02, 0x06, 0x00,verbose=verbose)
        interface3 = USBCDCInterface(3, maxusb_app, 0x0a, 0x00, 0x00,verbose=verbose)

        if vid == 0x1111:
            vid = 0x1390
        if pid == 0x2222:
            pid = 0x5454
        if rev == 0x3333:
            rev = 0x0327


        config = [
            USBConfiguration(
                maxusb_app,
                2,                          # index
                "CDC Ethernet Control Module (ECM)",             # string desc
                [ interface0, interface1 ]  # interfaces
            ),
            USBConfiguration(
                maxusb_app,
                1,                          # index
                "Emulated CDC - ACM",             # string desc
                [ interface2, interface3 ]  # interfaces
            )
        ]



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
                "TOMTOM B.V.",               # manufacturer string
                "TomTom",              # product string
                "TA6380K10346",               # serial number string
                config,
                verbose=verbose
        )

