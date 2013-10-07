# USBConfiguration.py
#
# Contains class definition for USBConfiguration.

class USBConfiguration:
    def __init__(self, maxusb_app, configuration_index, configuration_string, interfaces):
        self.maxusb_app = maxusb_app
        self.configuration_index        = configuration_index
        self.configuration_string       = configuration_string
        self.configuration_string_index = 0
        self.interfaces                 = interfaces

        self.attributes = 0xe0
        self.max_power = 0x32

        self.device = None

        for i in self.interfaces:
            i.set_configuration(self)

    def set_device(self, device):
        self.device = device

    def set_configuration_string_index(self, i):
        self.configuration_string_index = i

    def get_descriptor(self):
        interface_descriptors = bytearray()
        for i in self.interfaces:
            interface_descriptors += i.get_descriptor()

        if self.maxusb_app.testcase[1] == "conf_bLength":
            bLength = self.maxusb_app.testcase[2]
        else:
            bLength = 9

        if self.maxusb_app.testcase[1] == "conf_bDescriptorType":
            bDescriptorType = self.maxusb_app.testcase[2]
        else:
            bDescriptorType = 2

        if self.maxusb_app.testcase[1] == "conf_wTotalLength":
            wTotalLength = self.maxusb_app.testcase[2]
        else:
            wTotalLength = len(interface_descriptors) + 9

        if self.maxusb_app.testcase[1] == "conf_bNumInterfaces":
            bNumInterfaces = self.maxusb_app.testcase[2]
        else:
            bNumInterfaces = len(self.interfaces)



        d = bytes([
                bLength,          # length of descriptor in bytes
                bDescriptorType,          # descriptor type 2 == configuration
                wTotalLength & 0xff,
                (wTotalLength >> 8) & 0xff,
                bNumInterfaces,
                self.configuration_index,
                self.configuration_string_index,
                self.attributes,
                self.max_power
        ])

        return d + interface_descriptors

