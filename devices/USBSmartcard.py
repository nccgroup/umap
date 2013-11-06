# USBSmartcard.py
#
# Contains class definitions to implement a USB Smartcard.

# This devbice doesn't work properly yet!!!!!

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *

class USBSmartcardClass(USBClass):
    name = "USB Smartcard class"

    def __init__(self, maxusb_app):

        self.maxusb_app = maxusb_app
        self.setup_request_handlers()


    def setup_request_handlers(self):
        self.request_handlers = {
            0x02 : self.handle_get_clock_frequencies
        }

    def handle_get_clock_frequencies(self, req):
        response = b'\x67\x32\x00\x00\xCE\x64\x00\x00\x9D\xC9\x00\x00\x3A\x93\x01\x00\x74\x26\x03\x00\xE7\x4C\x06\x00\xCE\x99\x0C\x00\xD7\x5C\x02\x00\x11\xF0\x03\x00\x34\x43\x00\x00\x69\x86\x00\x00\xD1\x0C\x01\x00\xA2\x19\x02\x00\x45\x33\x04\x00\x8A\x66\x08\x00\x0B\xA0\x02\x00\x73\x30\x00\x00\xE6\x60\x00\x00\xCC\xC1\x00\x00\x99\x83\x01\x00\x32\x07\x03\x00\x63\x0E\x06\x00\xB3\x22\x01\x00\x7F\xE4\x01\x00\x06\x50\x01\x00\x36\x97\x00\x00\x04\xFC\x00\x00\x53\x28\x00\x00\xA5\x50\x00\x00\x4A\xA1\x00\x00\x95\x42\x01\x00\x29\x85\x02\x00\xF8\x78\x00\x00\x3E\x49\x00\x00\x7C\x92\x00\x00\xF8\x24\x01\x00\xF0\x49\x02\x00\xE0\x93\x04\x00\xC0\x27\x09\x00\x74\xB7\x01\x00\x6C\xDC\x02\x00\xD4\x30\x00\x00\xA8\x61\x00\x00\x50\xC3\x00\x00\xA0\x86\x01\x00\x40\x0D\x03\x00\x80\x1A\x06\x00\x48\xE8\x01\x00\xBA\xDB\x00\x00\x36\x6E\x01\x00\x24\xF4\x00\x00\xDD\x6D\x00\x00\x1B\xB7\x00\x00'

        self.maxusb_app.send_on_endpoint(0, response)



class USBSmartcardInterface(USBInterface):
    name = "USB Smartcard interface"

    def __init__(self, maxusb_app, verbose=0):


        self.maxusb_app = maxusb_app

        if self.maxusb_app.testcase[1] == "icc_bLength":
            bLength = self.maxusb_app.testcase[2]
        else:
            bLength = b'\x36'

        if self.maxusb_app.testcase[1] == "icc_bDescriptorType":
            bDescriptorType = self.maxusb_app.testcase[2]
        else:
            bDescriptorType = b'\x21'   # USB-ICC
        bcdCCID = b'\x10\x01'
        if self.maxusb_app.testcase[1] == "icc_bMaxSlotIndex":
            bMaxSlotIndex = self.maxusb_app.testcase[2]
        else:
            bMaxSlotIndex = b'\x00' # index of highest available slot
        if self.maxusb_app.testcase[1] == "icc_bVoltageSupport":
            bVoltageSupport = self.maxusb_app.testcase[2]
        else:
            bVoltageSupport = b'\x07'
        if self.maxusb_app.testcase[1] == "icc_dwProtocols":
            dwProtocols = self.maxusb_app.testcase[2]
        else:
            dwProtocols = b'\x03\x00\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwDefaultClock":
            dwDefaultClock = self.maxusb_app.testcase[2]
        else:
            dwDefaultClock = b'\xA6\x0E\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwMaximumClock":
            dwMaximumClock = self.maxusb_app.testcase[2]
        else:
            dwMaximumClock = b'\x4C\x1D\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_bNumClockSupported":
            bNumClockSupported = self.maxusb_app.testcase[2]
        else:
            bNumClockSupported = b'\x00'
        if self.maxusb_app.testcase[1] == "icc_dwDataRate":
            dwDataRate = self.maxusb_app.testcase[2]
        else:
            dwDataRate = b'\x60\x27\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwMaxDataRate":
            dwMaxDataRate = self.maxusb_app.testcase[2]
        else:
            dwMaxDataRate = b'\xB4\xC4\x04\x00'
        if self.maxusb_app.testcase[1] == "icc_bNumDataRatesSupported":
            bNumDataRatesSupported = self.maxusb_app.testcase[2]
        else:
            bNumDataRatesSupported = b'\x00'
        if self.maxusb_app.testcase[1] == "icc_dwMaxIFSD":
            dwMaxIFSD = self.maxusb_app.testcase[2]
        else:
            dwMaxIFSD = b'\xFE\x00\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwSynchProtocols":
            dwSynchProtocols = self.maxusb_app.testcase[2]
        else:
            dwSynchProtocols =  b'\x00\x00\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwMechanical":
            dwMechanical = self.maxusb_app.testcase[2]
        else:
            dwMechanical = b'\x00\x00\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_dwFeatures":
            dwFeatures = self.maxusb_app.testcase[2]
        else:
            dwFeatures = b'\x30\x00\x01\x00'
        if self.maxusb_app.testcase[1] == "icc_dwMaxCCIDMessageLength":
            dwMaxCCIDMessageLength = self.maxusb_app.testcase[2]
        else:
            dwMaxCCIDMessageLength = b'\x0F\x01\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_bClassGetResponse":
            bClassGetResponse = self.maxusb_app.testcase[2]
        else:
            bClassGetResponse = b'\x00'
        if self.maxusb_app.testcase[1] == "icc_bClassEnvelope":
            bClassEnvelope = self.maxusb_app.testcase[2]
        else:
            bClassEnvelope = b'\x00'
        if self.maxusb_app.testcase[1] == "icc_wLcdLayout":
            wLcdLayout = self.maxusb_app.testcase[2]
        else:
            wLcdLayout = b'\x00\x00'
        if self.maxusb_app.testcase[1] == "icc_bPinSupport":
            bPinSupport = self.maxusb_app.testcase[2]
        else:
            bPinSupport = b'\x00'
        if self.maxusb_app.testcase[1] == "icc_bMaxCCIDBusySlots":
            bMaxCCIDBusySlots = self.maxusb_app.testcase[2]
        else:
            bMaxCCIDBusySlots = b'\x01'

        self.icc_descriptor =    bLength + \
                            bDescriptorType + \
                            bcdCCID + \
                            bMaxSlotIndex + \
                            bVoltageSupport + \
                            dwProtocols + \
                            dwDefaultClock + \
                            dwMaximumClock + \
                            bNumClockSupported + \
                            dwDataRate + \
                            dwMaxDataRate + \
                            bNumDataRatesSupported + \
                            dwMaxIFSD + \
                            dwSynchProtocols + \
                            dwMechanical + \
                            dwFeatures + \
                            dwMaxCCIDMessageLength + \
                            bClassGetResponse + \
                            bClassEnvelope + \
                            wLcdLayout + \
                            bPinSupport + \
                            bMaxCCIDBusySlots

        descriptors = { 
                USB.desc_type_hid    : self.icc_descriptor  # 33 is the same descriptor type code as HID
        }


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
                0x0b,       # 3 interface class
                0,          # 0 subclass
                0,          # 0 protocol
                0,          # string index
                verbose,
                endpoint,
                descriptors
        )

        self.device_class = USBSmartcardClass(maxusb_app)
        self.trigger = False
        self.initial_data = b'\x50\x03'


    def handle_data_available(self,data):


        if self.maxusb_app.mode == 1:
            print (" **SUPPORTED**",end="")
            if self.maxusb_app.fplog:
                self.maxusb_app.fplog.write (" **SUPPORTED**\n")
            self.maxusb_app.stop = True

#        print ("Received:",data)
        command = ord(data[:1])
#        print ("command=%02x" % command)
        bSeq = data[6:7]
#        print ("seq=",ord(bSeq))
        bReserved = ord(data[7:8])
#        print ("bReserved=",bReserved) 

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


        elif command == 0x61: # PC_to_RDR_SetParameters

            if self.maxusb_app.testcase[1] == "SetParameters_bMessageType":
                bMessageType = self.maxusb_app.testcase[2]
            else:
                bMessageType = b'\x82'  # RDR_to_PC_Parameters
            if self.maxusb_app.testcase[1] == "SetParameters_dwLength":
                dwLength = self.maxusb_app.testcase[2]
            else:
                dwLength = b'\x05\x00\x00\x00' # Message-specific data length
            if self.maxusb_app.testcase[1] == "SetParameters_bSlot":
                bSlot = self.maxusb_app.testcase[2]
            else:
                bSlot = b'\x00' # fixed for legacy reasons
            if self.maxusb_app.testcase[1] == "SetParameters_bStatus":
                bStatus = self.maxusb_app.testcase[2]
            else:
                bStatus = b'\x00' # reserved
            if self.maxusb_app.testcase[1] == "SetParameters_bError":
                bError = self.maxusb_app.testcase[2]
            else:
                bError = b'\x80'
            if self.maxusb_app.testcase[1] == "SetParameters_bProtocolNum":
                bProtocolNum = self.maxusb_app.testcase[2]
            else:
                bProtocolNum = b'\x00'

            abProtocolDataStructure = b'\x11\x00\x00\x0a\x00'
            
            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        bStatus + \
                        bError + \
                        bProtocolNum + \
                        abProtocolDataStructure      

 
        elif command == 0x62: # PC_to_RDR_IccPowerOn

            if bReserved == 2:

                if self.maxusb_app.testcase[1] == "IccPowerOn_bMessageType":
                    bMessageType = self.maxusb_app.testcase[2]
                else:
                    bMessageType = b'\x80'  # RDR_to_PC_DataBlock
                if self.maxusb_app.testcase[1] == "IccPowerOn_dwLength":
                    dwLength = self.maxusb_app.testcase[2]
                else:
                    dwLength = b'\x12\x00\x00\x00' # Message-specific data length
                if self.maxusb_app.testcase[1] == "IccPowerOn_bSlot":
                    bSlot = self.maxusb_app.testcase[2]
                else:
                    bSlot = b'\x00' # fixed for legacy reasons
                if self.maxusb_app.testcase[1] == "IccPowerOn_bStatus":
                    bStatus = self.maxusb_app.testcase[2]
                else:
                    bStatus = b'\x00'
                if self.maxusb_app.testcase[1] == "IccPowerOn_bError":
                    bError = self.maxusb_app.testcase[2]
                else:
                    bError = b'\x80'
                if self.maxusb_app.testcase[1] == "IccPowerOn_bChainParameter":
                    bChainParameter = self.maxusb_app.testcase[2]
                else:
                    bChainParameter = b'\x00'
                abData = b'\x3b\x6e\x00\x00\x80\x31\x80\x66\xb0\x84\x12\x01\x6e\x01\x83\x00\x90\x00'
                response =  bMessageType + \
                            dwLength + \
                            bSlot + \
                            bSeq + \
                            bStatus + \
                            bError + \
                            bChainParameter + \
                            abData

            else:
                if self.maxusb_app.testcase[1] == "IccPowerOn_bMessageType":
                    bMessageType = self.maxusb_app.testcase[2]
                else:
                    bMessageType = b'\x80'  # RDR_to_PC_DataBlock
                if self.maxusb_app.testcase[1] == "IccPowerOn_dwLength":
                    dwLength = self.maxusb_app.testcase[2]
                else:
                    dwLength = b'\x00\x00\x00\x00' # Message-specific data length
                if self.maxusb_app.testcase[1] == "IccPowerOn_bSlot":
                    bSlot = self.maxusb_app.testcase[2]
                else:
                    bSlot = b'\x00' # fixed for legacy reasons
                if self.maxusb_app.testcase[1] == "IccPowerOn_bStatus":
                    bStatus = self.maxusb_app.testcase[2]
                else:
                    bStatus = b'\x40'
                if self.maxusb_app.testcase[1] == "IccPowerOn_bError":
                    bError = self.maxusb_app.testcase[2]
                else:
                    bError = b'\xfe'
                if self.maxusb_app.testcase[1] == "IccPowerOn_bChainParameter":
                    bChainParameter = self.maxusb_app.testcase[2]
                else:
                    bChainParameter = b'\x00'

                response =  bMessageType + \
                            dwLength + \
                            bSlot + \
                            bSeq + \
                            bStatus + \
                            bError + \
                            bChainParameter



        elif command == 0x63: # PC_to_RDR_IccPowerOff

            if self.maxusb_app.testcase[1] == "IccPowerOff_bMessageType":
                bMessageType = self.maxusb_app.testcase[2]
            else:
                bMessageType = b'\x81'  # PC_to_RDR_IccPowerOff
            if self.maxusb_app.testcase[1] == "IccPowerOff_dwLength":
                dwLength = self.maxusb_app.testcase[2]
            else:
                dwLength = b'\x00\x00\x00\x00' # Message-specific data length
            if self.maxusb_app.testcase[1] == "IccPowerOff_bSlot":
                bSlot = self.maxusb_app.testcase[2]
            else:
                bSlot = b'\x00' # fixed for legacy reasons
            if self.maxusb_app.testcase[1] == "IccPowerOff_abRFU":
                abRFU = self.maxusb_app.testcase[2]            
            else:
                abRFU = b'\x01' # reserved

            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        abRFU


        elif command == 0x65: # PC_to_RDR_GetSlotStatus


            bMessageType = b'\x81'  # RDR_to_PC_SlotStatus
            dwLength = b'\x00\x00\x00\x00' # Message-specific data length
            bSlot = b'\x00'
            bStatus = b'\x01'
            bError = b'\x00'
            bClockStatus = b'\x00' # reserved

            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        bStatus + \
                        bError + \
                        bClockStatus




                    

        elif command == 0x6b: # PC_to_RDR_Escape

           
            bMessageType = b'\x83'  # RDR_to_PC_Escape
            dwLength = b'\x00\x00\x00\x00' # Message-specific data length
            bSlot = b'\x00'
            bStatus = b'\x41'
            bError = b'\x0a'
            bRFU = b'\x00' # reserved

            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        bStatus + \
                        bError + \
                        bRFU


        elif command == 0x6f: # PC_to_RDR_XfrBlock message

            if self.maxusb_app.testcase[1] == "XfrBlock_bMessageType":
                bMessageType = self.maxusb_app.testcase[2]
            else:
                bMessageType = b'\x80'  # RDR_to_PC_DataBlock
            if self.maxusb_app.testcase[1] == "XfrBlock_dwLength":
                dwLength = self.maxusb_app.testcase[2]
            else:
                dwLength = b'\x02\x00\x00\x00' # Message-specific data length
            if self.maxusb_app.testcase[1] == "XfrBlock_bSlot":
                bSlot = self.maxusb_app.testcase[2]
            else:
                bSlot = b'\x00' # fixed for legacy reasons
            if self.maxusb_app.testcase[1] == "XfrBlock_bStatus":
                bStatus = self.maxusb_app.testcase[2]
            else:
                bStatus = b'\x00' # reserved
            if self.maxusb_app.testcase[1] == "XfrBlock_bError":
                bError = self.maxusb_app.testcase[2]
            else:
                bError = b'\x80'
            if self.maxusb_app.testcase[1] == "XfrBlock_bChainParameter":
                bChainParameter = self.maxusb_app.testcase[2]
            else:
                bChainParameter = b'\x00'
            abData = b'\x6a\x82' 

            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        bStatus + \
                        bError + \
                        bChainParameter + \
                        abData

        elif command == 0x73: # PC_to_RDR_SetDataRateAndClockFrequency

            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_bMessageType":
                bMessageType = self.maxusb_app.testcase[2]
            else:
                bMessageType = b'\x84'  # RDR_to_PC_DataRateAndClockFrequency
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_dwLength":
                dwLength = self.maxusb_app.testcase[2]
            else:
                dwLength = b'\x08\x00\x00\x00' # Message-specific data length
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_bSlot":
                bSlot = self.maxusb_app.testcase[2]
            else:
                bSlot = b'\x00' # fixed for legacy reasons
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_bStatus":
                bStatus = self.maxusb_app.testcase[2]
            else:
                bStatus = b'\x00' # reserved
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_bError":
                bError = self.maxusb_app.testcase[2]
            else:
                bError = b'\x80'
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_bRFU":
                bRFU = self.maxusb_app.testcase[2]
            else:
                bRFU = b'\x80'
            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_dwClockFrequency":
                dwClockFrequency = self.maxusb_app.testcase[2]
            else:
                dwClockFrequency = b'\xA6\x0E\x00\x00'

            if self.maxusb_app.testcase[1] == "SetDataRateAndClockFrequency_dwDataRate":
                dwDataRate = self.maxusb_app.testcase[2]
            else:
                dwDataRate = b'\x60\x27\x00\x00' 

            response =  bMessageType + \
                        dwLength + \
                        bSlot + \
                        bSeq + \
                        bStatus + \
                        bError + \
                        bRFU + \
                        dwClockFrequency + \
                        dwDataRate

        else:
            print ("Received Smartcard command not understood") 
            response = b''

        if self.maxusb_app.server_running == False:
            self.configuration.device.maxusb_app.send_on_endpoint(2, response)


    def handle_buffer_available(self):

        if self.trigger == False:
            self.configuration.device.maxusb_app.send_on_endpoint(3, self.initial_data)
            self.trigger = True



class USBSmartcardDevice(USBDevice):
    name = "USB Smartcard device"

    def __init__(self, maxusb_app, vid, pid, rev, verbose=0):



        interface = USBSmartcardInterface(maxusb_app, verbose=verbose)


        if vid == 0x1111:
            vid = 0x0bda
        if pid == 0x2222:
            pid = 0x0165
        if rev == 0x3333:
            rev = 0x6123

        config = USBConfiguration(
                maxusb_app,
                1,                                          # index
                "Emulated Smartcard",    # string desc
                [ interface ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # 0 device class
		        0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
		        vid,                    # vendor id
                pid,                    # product id
		        rev,                    # device revision
                "Generic",              # manufacturer string
                "Smart Card Reader Interface",   # product string
                "20070818000000000",    # serial number string
                [ config ],
                verbose=verbose
        )

