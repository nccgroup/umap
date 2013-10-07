# USBHub.py
#
# Contains class definitions to implement a USB hub.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *

class USBHubClass(USBClass):
    name = "USB hub class"

    def __init__(self, maxusb_app):

        self.maxusb_app = maxusb_app
        self.setup_request_handlers()

    def setup_request_handlers(self):
        self.request_handlers = {
            0x00 : self.handle_get_hub_status_request,
            0x03 : self.handle_set_port_feature_request

        }

    def handle_get_hub_status_request(self, req):
        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True
        else:

            response = b'\x61\x61\x61\x61'
            self.maxusb_app.send_on_endpoint(0, response)
            self.maxusb_app.stop = True

        
    def handle_set_port_feature_request(self, req):
#        print ("DEBUG: Set port feature request")
        response = b''
        self.maxusb_app.send_on_endpoint(0, response)



class USBHubInterface(USBInterface):
    name = "USB hub interface"

    def __init__(self, maxusb_app, verbose=0):
        self.maxusb_app = maxusb_app


        if self.maxusb_app.testcase[1] == "hub_bLength":
            bLength = self.maxusb_app.testcase[2]
        else:
            bLength = 9
        if self.maxusb_app.testcase[1] == "hub_bDescriptorType":
            bDescriptorType = self.maxusb_app.testcase[2]
        else:
            bDescriptorType = 0x29
        if self.maxusb_app.testcase[1] == "hub_bNbrPorts":
            bNbrPorts = self.maxusb_app.testcase[2]
        else:
            bNbrPorts = 4
        if self.maxusb_app.testcase[1] == "hub_wHubCharacteristics":
            wHubCharacteristics = self.maxusb_app.testcase[2]
        else:
            wHubCharacteristics = 0xe000
        if self.maxusb_app.testcase[1] == "hub_bPwrOn2PwrGood":
            bPwrOn2PwrGood = self.maxusb_app.testcase[2]
        else:
            bPwrOn2PwrGood = 0x32
        if self.maxusb_app.testcase[1] == "hub_bHubContrCurrent":
            bHubContrCurrent = self.maxusb_app.testcase[2]
        else:
            bHubContrCurrent = 0x64
        if self.maxusb_app.testcase[1] == "hub_DeviceRemovable":
            DeviceRemovable = self.maxusb_app.testcase[2]
        else:
            DeviceRemovable = 0
        if self.maxusb_app.testcase[1] == "hub_PortPwrCtrlMask":
            PortPwrCtrlMask = self.maxusb_app.testcase[2]
        else:
            PortPwrCtrlMask = 0xff

        hub_descriptor = bytes([
                bLength,                        # length of descriptor in bytes
                bDescriptorType,                # descriptor type 0x29 == hub
                bNbrPorts,                      # number of physical ports
                wHubCharacteristics & 0xff ,    # hub characteristics
                (wHubCharacteristics >> 8) & 0xff,
                bPwrOn2PwrGood,                 # time from power on til power good
                bHubContrCurrent,               # max current required by hub controller
                DeviceRemovable,
                PortPwrCtrlMask
        ])



        descriptors = { 
                USB.desc_type_hub    : hub_descriptor
        }

        endpoint = USBEndpoint(
                maxusb_app,
                0x81,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0x0c,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
        )

        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                0,          # interface number
                0,          # alternate setting
                9,          # 3 interface class
                0,          # 0 subclass
                0,          # 0 protocol
                0,          # string index
                verbose,
                [ endpoint ],
                descriptors
        )

        self.device_class = USBHubClass(maxusb_app)
        self.device_class.set_interface(self)


    def handle_buffer_available(self):

#        print ("DEBUG: handle_buffer_available")
        return


class USBHubDevice(USBDevice):
    name = "USB hub device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):


        interface = USBHubInterface(maxusb_app, verbose=verbose)

        if vid == 0x1111:
            vid = 0x05e3
        if pid == 0x2222:
            pid = 0x0608
        if rev == 0x3333:
            rev = 0x7764


        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Emulated Hub",    # string desc
                [ interface ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                9,                      # 0 device class
		        0,                      # device subclass
                1,                      # protocol release number
                64,                     # max packet size for endpoint 0
		        vid,                    # vendor id
                pid,                    # product id
		        rev,                    # device revision
                "Genesys Logic, Inc",   # manufacturer string
                "USB2.0 Hub",           # product string
                "1234",                 # serial number string
                [ config ],
                verbose=verbose
        )


