# USBAudio.py
#
# Contains class definitions to implement a USB Audio device.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBCSInterface import *
from USBEndpoint import *
from USBCSEndpoint import *


class USBAudioClass(USBClass):
    name = "USB Audio class"

    def __init__(self, maxusb_app):

        self.maxusb_app = maxusb_app
        self.setup_request_handlers()


    def setup_request_handlers(self):
        self.request_handlers = {
            0x0a : self.handle_set_idle,
            0x83 : self.handle_get_max,
            0x82 : self.handle_get_min,
            0x84 : self.handle_get_res,
            0x81 : self.handle_get_cur,
            0x04 : self.handle_set_res,
            0x01 : self.handle_set_cur
        }

    def handle_get_max(self, req):
        response = b'\xf0\xff'
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_get_min(self, req):
        response = b'\xa0\xe0'
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_get_res(self, req):
        response = b'\x30\x00'
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_get_cur(self, req):
        response = b''
#        response = b'\x80\xfd'
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_set_res(self, req):
        response = b''
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_set_cur(self, req):
        response = b''
        self.maxusb_app.send_on_endpoint(0, response)
        self.supported()

    def handle_set_idle(self, req):
        self.maxusb_app.send_on_endpoint(0, b'')
        self.supported()

    def supported(self):
        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True


class USBAudioInterface(USBInterface):
    name = "USB audio interface"

    hid_descriptor = b'\x09\x21\x10\x01\x00\x01\x22\x2b\x00'
    report_descriptor = b'\x05\x0C\x09\x01\xA1\x01\x15\x00\x25\x01\x09\xE9\x09\xEA\x75\x01\x95\x02\x81\x02\x09\xE2\x09\x00\x81\x06\x05\x0B\x09\x20\x95\x01\x81\x42\x05\x0C\x09\x00\x95\x03\x81\x02\x26\xFF\x00\x09\x00\x75\x08\x95\x03\x81\x02\x09\x00\x95\x04\x91\x02\xC0'


    def __init__(self, int_num, maxusb_app, usbclass, sub, proto, verbose=0):

        self.maxusb_app = maxusb_app
        self.int_num = int_num

        descriptors = { 
                USB.desc_type_hid    : self.hid_descriptor,
                USB.desc_type_report : self.report_descriptor
        }

        if self.maxusb_app.testcase[1] == "CSInterface1_wTotalLength":
            wTotalLength = self.maxusb_app.testcase[2]
        else:
            wTotalLength = 0x0047
        if self.maxusb_app.testcase[1] == "CSInterface1_bInCollection":
            bInCollection = self.maxusb_app.testcase[2]
        else:
            bInCollection = 0x02
        if self.maxusb_app.testcase[1] == "CSInterface1_baInterfaceNr1":
            baInterfaceNr1 = self.maxusb_app.testcase[2]
        else:
            baInterfaceNr1 = 0x01
        if self.maxusb_app.testcase[1] == "CSInterface1_baInterfaceNr2":
            baInterfaceNr2 = self.maxusb_app.testcase[2]
        else:
            baInterfaceNr2 = 0x02

        cs_config1 = [
            0x01,           # HEADER
            0x0001,         # bcdADC
            wTotalLength,   # wTotalLength
            bInCollection,  # bInCollection
            baInterfaceNr1, # baInterfaceNr1
            baInterfaceNr2  # baInterfaceNr2
        ]

        if self.maxusb_app.testcase[1] == "CSInterface2_bTerminalID":
            bTerminalID = self.maxusb_app.testcase[2]
        else:
            bTerminalID = 0x01
        if self.maxusb_app.testcase[1] == "CSInterface2_wTerminalType":
            wTerminalType = self.maxusb_app.testcase[2]
        else:
            wTerminalType = 0x0101
        if self.maxusb_app.testcase[1] == "CSInterface2_bAssocTerminal":
            bAssocTerminal = self.maxusb_app.testcase[2]
        else:
            bAssocTerminal = 0x0
        if self.maxusb_app.testcase[1] == "CSInterface2_bNrChannel":
            bNrChannel = self.maxusb_app.testcase[2]
        else:
            bNrChannel = 0x02
        if self.maxusb_app.testcase[1] == "CSInterface2_wChannelConfig":
            wChannelConfig = self.maxusb_app.testcase[2]
        else:
            wChannelConfig = 0x0002

        cs_config2 = [
            0x02,           # INPUT_TERMINAL
            bTerminalID,    # bTerminalID
            wTerminalType,  # wTerminalType
            bAssocTerminal, # bAssocTerminal    
            bNrChannel,     # bNrChannel
            wChannelConfig, # wChannelConfig
            0,          # iChannelNames
            0           # iTerminal
        ]

        cs_config3 = [
            0x02,       # INPUT_TERMINAL
            0x02,       # bTerminalID
            0x0201,     # wTerminalType
            0,          # bAssocTerminal
            0x01,       # bNrChannel
            0x0001,     # wChannelConfig
            0,          # iChannelNames
            0           # iTerminal
        ]

        if self.maxusb_app.testcase[1] == "CSInterface4_bSourceID":
            bSourceID = self.maxusb_app.testcase[2]
        else:
            bSourceID = 0x09

        cs_config4 = [
            0x03,       # OUTPUT_TERMINAL
            0x06,       # bTerminalID
            0x0301,     # wTerminalType
            0,          # bAssocTerminal
            bSourceID,  # bSourceID
            0           # iTerminal
        ]

        cs_config5 = [
            0x03,       # OUTPUT_TERMINAL
            0x07,       # bTerminalID
            0x0101,     # wTerminalType
            0,          # bAssocTerminal
            0x0a,       # bSourceID
            0           # iTerminal
        ]

        if self.maxusb_app.testcase[1] == "CSInterface6_bUnitID":
            bUnitID = self.maxusb_app.testcase[2]
        else:
            bUnitID = 0x09
        if self.maxusb_app.testcase[1] == "CSInterface6_bSourceID":
            bSourceID = self.maxusb_app.testcase[2]
        else:
            bSourceID = 0x01
        if self.maxusb_app.testcase[1] == "CSInterface6_bControlSize":
            bControlSize = self.maxusb_app.testcase[2]
        else:
            bControlSize = 0x01
        if self.maxusb_app.testcase[1] == "CSInterface6_bmaControls0":
            bmaControls0 = self.maxusb_app.testcase[2]
        else:
            bmaControls0 = 0x01
        if self.maxusb_app.testcase[1] == "CSInterface6_bmaControls1":
            bmaControls1 = self.maxusb_app.testcase[2]
        else:
            bmaControls1 = 0x02
        if self.maxusb_app.testcase[1] == "CSInterface6_bmaControls2":
            bmaControls2 = self.maxusb_app.testcase[2]
        else:
            bmaControls2 = 0x02

        cs_config6 = [
            0x06,           # FEATURE_UNIT
            bUnitID,        # bUnitID
            bSourceID,      # bSourceID
            bControlSize,   # bControlSize
            bmaControls0,   # bmaControls0
            bmaControls1,   # bmaControls1
            bmaControls2,   # bmaControls2
            0               # iFeature
        ]

        cs_config7 = [
            0x06,       # FEATURE_UNIT
            0x0a,       # bUnitID
            0x02,       # bSourceID
            0x01,       # bControlSize
            0x43,       # bmaControls0
            0x00,       # bmaControls1
            0x00,       # bmaControls2
            0           # iFeature
        ]

        cs_interfaces0 = [
            USBCSInterface (
                maxusb_app,
                cs_config1,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config2,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config3,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config4,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config5,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config6,
                1,
                1,
                0
            ),
            USBCSInterface (
                maxusb_app,
                cs_config7,
                1,
                1,
                0
            )

        ]

#        cs_config8 = [
#            0x01,       # AS_GENERAL
#            0x01,       # bTerminalLink
#            0x01,       # bDelay
#            0x0001      # wFormatTag
#        ]

#        cs_config9 = [
#            0x02,       # FORMAT_TYPE
#            0x01,       # bFormatType
#            0x02,       # bNrChannels
#            0x02,       # bSubframeSize
#            0x10,       # bBitResolution
#            0x02,       # SamFreqType
#            0x80bb00,    # tSamFreq1
#            0x44ac00    # tSamFreq2
#        ]

        cs_interfaces1 = []
        cs_interfaces2 = []
        cs_interfaces3 = []

#        ep_cs_config1 = [
#            0x01,       # EP_GENERAL
#            0x01,       # Endpoint number
#            0x01,       # bmAttributes
#            0x01,       # bLockDelayUnits
#            0x0001,     # wLockeDelay
#        ]

        endpoints0 = [
            USBEndpoint(
                maxusb_app,
                1,           # endpoint address
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                0x0400,         # max packet size
                0x02,           # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            )
        ]

        if self.int_num == 3:
                endpoints = endpoints0
        else:
                endpoints = []

        if self.int_num == 0:
                cs_interfaces = cs_interfaces0
        if self.int_num == 1:
                cs_interfaces = cs_interfaces1
        if self.int_num == 2:
                cs_interfaces = cs_interfaces2
        if self.int_num == 3:
                cs_interfaces = cs_interfaces3




#        if self.int_num == 1:
#                endpoints = endpoints1


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

        self.device_class = USBAudioClass(maxusb_app)
        self.device_class.set_interface(self)


    def handle_data_available(self, data):
        if self.verbose > 0:
            print(self.name, "handling", len(data), "bytes of audio data")
    



class USBAudioDevice(USBDevice):
    name = "USB audio device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):

        int_class = 1
        int_subclass = 1
        int_proto = 0
        interface0 = USBAudioInterface(0, maxusb_app, 0x01, 0x01, 0x00,verbose=verbose)
        interface1 = USBAudioInterface(1, maxusb_app, 0x01, 0x02, 0x00,verbose=verbose)
        interface2 = USBAudioInterface(2, maxusb_app, 0x01, 0x02, 0x00,verbose=verbose)
        interface3 = USBAudioInterface(3, maxusb_app, 0x03, 0x00, 0x00,verbose=verbose)

        if vid == 0x1111:
            vid = 0x041e
        if pid == 0x2222:
            pid = 0x0402
        if rev == 0x3333:
            rev = 0x0100

        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Emulated Audio",    # string desc
                [ interface0, interface1, interface2, interface3 ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # 0 device class
		        0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
		        vid,                 # vendor id
                pid,                 # product id
		        rev,                 # device revision
                "Creative Technology Ltd.",                # manufacturer string
                "Creative HS-720 Headset",   # product string
                "",             # serial number string
                [ config ],
                verbose=verbose
        )

