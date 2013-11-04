# USBVendorSpecific.py
#

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBVendor import *


class USBVendorVendor(USBVendor):
    name = "USB vendor"

    def setup_request_handlers(self):
        self.request_handlers = {
             0 : self.handle_reset_request
        }

    def handle_reset_request(self, req):
        if self.verbose > 0:
            print(self.name, "received reset request")

        self.device.maxusb_app.send_on_endpoint(0, b'')



class USBVendorClass(USBClass):
    name = "USB Vendor class"

    def __init__(self, maxusb_app):

        self.maxusb_app = maxusb_app
        self.setup_request_handlers()

    def setup_request_handlers(self):
        self.request_handlers = {
            0x01 : self.handle_get_report
        }

    def handle_get_report(self, req):
        response = b''
        self.maxusb_app.send_on_endpoint(0, response)




class USBVendorInterface(USBInterface):
    name = "USB Vendor interface"

    def __init__(self, maxusb_app, verbose=0):

        self.maxusb_app = maxusb_app

        descriptors = { }


        endpoint = [
            USBEndpoint(
                maxusb_app,
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                8,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                1,          # endpoint number
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
            ),
            USBEndpoint(
                maxusb_app,
                2,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,         # polling interval, see USB 2.0 spec Table 9-13
                None    # handler function
            )
        ]



        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                maxusb_app,
                0,          # interface number
                0,          # alternate setting
                0xff,       # 3 interface class
                0xff,          # 0 subclass
                0xff,          # 0 protocol
                0,          # string index
                verbose,
                endpoint,
                descriptors
        )

        self.device_class = USBVendorClass(maxusb_app)


    def handle_data_available(self,data):
        return        


    def handle_buffer_available(self):
        return



class USBVendorDevice(USBDevice):
    name = "USB Vendor device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):


        interface = USBVendorInterface(maxusb_app, verbose=verbose)

        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Vendor device",    # string desc
                [ interface ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0xff,                   # 0 device class
		        0xff,                   # device subclass
                0xff,                   # protocol release number
                64,                     # max packet size for endpoint 0
		        vid,                    # vendor id
                pid,                    # product id
		        rev,                    # device revision
                "Vendor",              # manufacturer string
                "Product",   # product string
                "00000000",    # serial number string
                [ config ],
                verbose=verbose
        )

        self.device_vendor = USBVendorVendor()
        self.device_vendor.set_device(self)


