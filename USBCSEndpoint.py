# USBCSEndpoint.py
#
# Contains class definition for USBCSEndpoint.

class USBCSEndpoint:

    def __init__(self, maxusb_app, cs_config):

        self.maxusb_app         = maxusb_app
        self.cs_config = cs_config
        self.number = self.cs_config[1]

        self.interface = None
        self.device_class = None

        self.request_handlers   = {
                1 : self.handle_clear_feature_request
        }

    def handle_clear_feature_request(self, req):
        if self.maxusb_app.mode != 2:
            #print("received CLEAR_FEATURE request for endpoint", self.number,
            #        "with value", req.value)
            self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def set_interface(self, interface):
        self.interface = interface

    # see Table 9-13 of USB 2.0 spec (pdf page 297)
    def get_descriptor(self):
        if self.cs_config[0] == 0x01:  # EP_GENERAL
            bLength = 7
            bDescriptorType = 37 # CS_ENDPOINT
            bDescriptorSubtype = 0x01 # EP_GENERAL
            bmAttributes = self.cs_config[2]
            bLockDelayUnits = self.cs_config[3]
            wLockDelay = self.cs_config[4]


        d = bytearray([
                bLength,          # length of descriptor in bytes
                bDescriptorType,          # descriptor type 5 == endpoint
                bDescriptorSubtype,
                bmAttributes,
                bLockDelayUnits,
                wLockDelay & 0xff,
                (wLockDelay >> 8) & 0xff,

        ])

        return d

