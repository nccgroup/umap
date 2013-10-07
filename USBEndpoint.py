# USBEndpoint.py
#
# Contains class definition for USBEndpoint.

class USBEndpoint:
    direction_out               = 0x00
    direction_in                = 0x01

    transfer_type_control       = 0x00
    transfer_type_isochronous   = 0x01
    transfer_type_bulk          = 0x02
    transfer_type_interrupt     = 0x03

    sync_type_none              = 0x00
    sync_type_async             = 0x01
    sync_type_adaptive          = 0x02
    sync_type_synchronous       = 0x03

    usage_type_data             = 0x00
    usage_type_feedback         = 0x01
    usage_type_implicit_feedback = 0x02

    def __init__(self, maxusb_app, number, direction, transfer_type, sync_type,
            usage_type, max_packet_size, interval, handler):

        self.maxusb_app         = maxusb_app
        self.number             = number
        self.direction          = direction
        self.transfer_type      = transfer_type
        self.sync_type          = sync_type
        self.usage_type         = usage_type
        self.max_packet_size    = max_packet_size
        self.interval           = interval
        self.handler            = handler

        self.interface          = None

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
        address = (self.number & 0x0f) | (self.direction << 7) 
        attributes = (self.transfer_type & 0x03) \
                   | ((self.sync_type & 0x03) << 2) \
                   | ((self.usage_type & 0x03) << 4)

        if self.maxusb_app.testcase[1] == "end_bLength":
            bLength = self.maxusb_app.testcase[2]
        else:
            bLength = 7

        if self.maxusb_app.testcase[1] == "end_bDescriptorType":
            bDescriptorType = self.maxusb_app.testcase[2]
        else:
            bDescriptorType = 5

        if self.maxusb_app.testcase[1] == "end_bEndpointAddress":
            bEndpointAddress = self.maxusb_app.testcase[2]
        else:
            bEndpointAddress = address

        if self.maxusb_app.testcase[1] == "end_wMaxPacketSize":
            wMaxPacketSize = self.maxusb_app.testcase[2]
        else:
            wMaxPacketSize = self.max_packet_size

        d = bytearray([
                bLength,          # length of descriptor in bytes
                bDescriptorType,          # descriptor type 5 == endpoint
                bEndpointAddress,
                attributes,
                (wMaxPacketSize >> 8) & 0xff,
                wMaxPacketSize & 0xff,
                self.interval
        ])

        return d

