#!/usr/bin/env python3
#
# umap.py
#
from serial import Serial, PARITY_NONE
import time
from Facedancer import *
from MAXUSBApp import *
from USBMassStorage import *
from USBHub import *
from USBIphone import *
from USBAudio import *
from USBKeyboard import *
from USBPrinter import *
from USBImage import *
from USBCDC import *
from USBVendorSpecific import *
from USBSmartcard import *
from optparse import OptionParser
from optparse import OptionGroup
from collections import namedtuple, defaultdict
import codecs
import urllib.request
from testcases import *
from device_class_data import *
import sys
import platform

current_version = "1.01"
current_platform = platform.system()

print ("\n---------------------------------------")
print (" _   _ _ __ ___   __ _ _ __")   
print ("| | | | '_ ` _ \ / _` | '_ \\")  
print ("| |_| | | | | | | (_| | |_) |") 
print (" \__,_|_| |_| |_|\__,_| .__/")  
print ("                      |_|  ")
print ("\nThe USB host assessment tool")
print ("Andy Davis, NCC Group 2013")
print ("Version:", current_version)
print ("\nBased on Facedancer by Travis Goodspeed\n")
print ("For help type: umap.py -h")
print ("---------------------------------------\n")

parser = OptionParser(usage="%prog ", version=current_version)
group = OptionGroup(parser, "Experimental Options")

parser.add_option("-P", dest="serial", help="Facedancer serial port **Mandatory option** (SERIAL=/dev/ttyX or just 1 for COM1)")
parser.add_option("-L", action="store_true", dest="listclasses", default=False, help="List device classes supported by umap")
parser.add_option("-i", action="store_true", dest="identify", default=False, help="identify all supported device classes on connected host")
parser.add_option("-c", dest="cls", help="identify if a specific class on the connected host is supported (CLS=class:subclass:proto)")
parser.add_option("-O", action="store_true", dest="osid", default=False, help="Operating system identification")
parser.add_option("-e", dest="device", help="emulate a specific device (DEVICE=class:subclass:proto)")
parser.add_option("-v", dest="vid", help="specify Vendor ID (hex format e.g. 1a2b)")
parser.add_option("-p", dest="pid", help="specify Product ID (hex format e.g. 1a2b)")
parser.add_option("-r", dest="rev", help="specify product Revision (hex format e.g. 1a2b)")
parser.add_option("-f", dest="fuzzc", help="fuzz a specific class (FUZZC=class:subclass:proto:E/C/A[:start fuzzcase])")
parser.add_option("-s", dest="fuzzs", help="send a single fuzz testcase (FUZZS=class:subclass:proto:E/C:Testcase)")
parser.add_option("-d", dest="dly", help="delay between enumeration attempts (seconds): Default=1")
parser.add_option("-l", dest="log", help="log to a file")
parser.add_option("-R", dest="ref", help="Reference the VID/PID database (REF=VID:PID)")
parser.add_option("-u", action="store_true", dest="updatedb", default=False, help="update the VID/PID database (Internet connectivity required)")

group.add_option("-A", dest="apple", help="emulate an Apple iPhone device (APPLE=VID:PID:REV)")
group.add_option("-b", dest="vendor", help="brute-force vendor driver support (VENDOR=VID:PID)")

parser.add_option_group(group)

(options, args) = parser.parse_args()

device_vid = 0x1111
device_pid = 0x2222
device_rev = 0x3333

if not options.serial:
    print ("Error: Facedancer serial port not supplied\n")
    sys.exit()
else:
    tmp_serial = options.serial

    if current_platform == "Windows":
        try:
            serial0 = int(tmp_serial)-1
        except:
            print ("Error: Invalid serial port specification")
            sys.exit()

    else:
        serial0 = tmp_serial

def connectserial():

    try:
        sp = Serial(serial0, 115200, parity=PARITY_NONE, timeout=2)
        return sp
    except:
        print ("\nError: Check serial port is connected to Facedancer board\n")
        sys.exit(0)

sp = connectserial()

if options.log:
    logfilepath = options.log
    fplog = open(logfilepath, mode='a')
    fplog.write ("---------------------------------------\n")
    fplog.write ("umap - the USB host assessment tool\n")
    fplog.write ("Andy Davis, NCC Group 2013\n")
    write_string = "Version:" + current_version + "\n"
    fplog.write (write_string)
    fplog.write ("\nBased on Facedancer by Travis Goodspeed\n")
    fplog.write ("---------------------------------------\n")


if options.updatedb:
    print ("Downloading latest VID/PID database...")
    try:
        urllib.request.urlretrieve("http://www.linux-usb.org/usb.ids", "usb.ids")
        print ("Finished")
    except:
        print ("Error: Unable to contact server")

if options.vid:
    try:
        device_vid = int(options.vid,16)
        if device_vid > 65535:
            print ("Error: Invalid VID")
        else:
            print_output = "VID = %04x" % device_vid
            print (print_output)
            if options.log:
                fplog.write (print_output + "\n")
    except:
        print ("Error: Invalid VID")

if options.pid:
    try:
        device_pid = int(options.pid,16)
        if device_pid > 65535:
            print ("Error: Invalid PID")
        else:
            print_output = "PID = %04x" % device_pid
            print (print_output)
            if options.log:
                fplog.write (print_output + "\n")
    except:
        print ("Error: Invalid PID")

if options.rev:
    try:
        device_rev = int(options.rev,16)
        if device_rev > 65535:
            print ("Error: Invalid REV")
        else:
            print_output = "REV = %04x" % device_rev
            print (print_output)
            if options.log:
                fplog.write (print_output + "\n")
    except:
        print ("Error: Invalid REV")

if options.ref:
    vidpid = options.ref.split(':')
    if len(vidpid) != 2:
        print ("Error: VID/PID invalid")
    else:
        lookup_vid = vidpid[0]
        lookup_pid = vidpid[1]

        print ("Looking up VID=",lookup_vid, "/ PID=", lookup_pid)

        Vendor = namedtuple("Vendor", ['name', 'devices'])
        vendors = dict()

        with codecs.open("usb.ids", "r", "latin-1") as f:
            for line in f:
                if not line.strip():
                    continue
                line = line.rstrip()
                if line.startswith("#"):
                    continue
                if line.startswith("# List of known device classes, subclasses and protocols"): 
                    break
                if not line.startswith("\t"):
                    current_vendor, name = line.split(None, 1)
                    vendors[current_vendor] = Vendor(name=name, devices=dict())
                if line.startswith("\t"):
                    device_id, desc = line.lstrip().split(None, 1)
                    vendors[current_vendor].devices[device_id] = desc
        try:       
            print(vendors[lookup_vid].name, end=" ") 
        except:
            print ("\nVID could not be located")
        try:
            print(vendors[lookup_vid].devices[lookup_pid])
        except:
            print ("\nPID could not be located\n")

if options.dly:
    enumeration_delay = options.dly

    try:
        print ("Enumeration delay set to:", int(enumeration_delay))
        if options.log:
            write_string = "Enumeration delay set to:" + int( enumeration_delay) + "\n"
            fplog.write (write_string)

    except ValueError:
        print("Error: Enumeration delay is not an integer")
    
else:
    enumeration_delay = 1     

def optionerror():
    print ("Error: Invalid option\n")
    return


def execute_fuzz_testcase (device_class, device_subclass, device_proto, current_testcase, serialnum):
    
#    sp = connectserial()
    mode = 3

    if device_class == 8:
        mode = 4    # Hack to get the Mass storage device to stop for each fuzz case

    fd = Facedancer(sp, verbose=0)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, current_testcase, verbose=0)
    if device_class == 1:
        d = USBAudioDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 2:
        d = USBCDCDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 3:
        d = USBKeyboardDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 6:
        d = USBImageDevice(u, device_vid, device_pid, device_rev, device_class, device_subclass, device_proto, "ncc_group_logo.jpg", verbose=0)
    elif device_class == 7:
        d = USBPrinterDevice(u, device_vid, device_pid, device_rev, device_class, device_subclass, device_proto, verbose=0)
    elif device_class == 8:
        try:
            d = USBMassStorageDevice(u, device_vid, device_pid, device_rev, device_class, device_subclass, device_proto, "stick.img", verbose=0)
        except:
            print ("Error: stick.img not found - please create a disk image using dd")

    elif device_class == 9:
        d = USBHubDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 10:
        d = USBCDCDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 11:
        d = USBSmartcardDevice(u, device_vid, device_pid, device_rev, verbose=0)
    elif device_class == 14:
        d = USBImageDevice(u, device_vid, device_pid, device_rev, 0xe, 1, 0, "ncc_group_logo.jpg", verbose=0)   #HACK

    try:
        d.connect()
    except:
        pass
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()

    time.sleep(int(enumeration_delay))


def connect_as_image (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBImageDevice(u, vid, pid, rev, 6, 1, 1, "ncc_group_logo.jpg", verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_cdc (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBCDCDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_iphone (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBIphoneDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_audio (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBAudioDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_printer (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBPrinterDevice(u, vid, pid, rev, 7, 1, 2, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_keyboard (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBKeyboardDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_smartcard (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBSmartcardDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_vendor (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBVendorDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()



def connect_as_hub (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    d = USBHubDevice(u, vid, pid, rev, verbose=ver2)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()


def connect_as_mass_storage (vid, pid, rev, mode):
    if mode == 1:
        ver1 = 0
        ver2 = 0
    else:
        ver1 = 1
        ver2 = 4
#    sp = connectserial()
    fake_testcase = ["dummy","",0] 
    fd = Facedancer(sp, verbose=ver1)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, mode, fake_testcase, verbose=ver1)
    try:
        d = USBMassStorageDevice(u, vid, pid, rev, 8, 6, 80, "stick.img", verbose=ver2)
        d.connect()
        try:
            d.run()
        except KeyboardInterrupt:
            d.disconnect()
            if options.log:
                fplog.close()

    except:
        print ("Error: stick.img not found - please create a disk image using dd")




def identify_classes (single_device):

    if single_device:
        supported_devices_id = single_device
    else:
        supported_devices_id = supported_devices
        
    class_count = 0


    while class_count < len(supported_devices_id):
        list_classes([supported_devices_id[class_count]])

        logfp = 0
        if options.log:
            logfp = fplog
        mode = 1 # identity mode

        if supported_devices_id[class_count][0] == 1:
            connect_as_audio (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 2:
            connect_as_cdc (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 3:
            connect_as_keyboard (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 6:
            connect_as_image (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 7:
            connect_as_printer (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 8:
            connect_as_mass_storage (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 9:
            connect_as_hub (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 10:
            connect_as_cdc (device_vid, device_pid, device_rev, 1)
        elif supported_devices_id[class_count][0] == 11:
            connect_as_smartcard (device_vid, device_pid, device_rev, 1)

        sys.stdout.flush()

        print ("")
        time.sleep(int(enumeration_delay)) 
        class_count += 1



def list_classes (devices_list):
    x = 0
    while x < len(devices_list):
        print ("%02x:%02x:%02x - " % (devices_list[x][0], devices_list[x][1], devices_list[x][2]), end="")

        class_name = 0
        while class_name < len (device_class_list):
            if (devices_list[x][0] == device_class_list[class_name][1]):
                print (device_class_list[class_name][0],": ",end="")
            class_name += 1

        subclass_name = 0
        while subclass_name < len (device_subclass_list):
            if (devices_list[x][0] == device_subclass_list[subclass_name][0]) and (devices_list[x][1] == device_subclass_list[subclass_name][2]):
                print (device_subclass_list[subclass_name][1],": ",end="")
            subclass_name += 1

        protocol_name = 0
        while protocol_name < len (device_protocol_list):
            if (devices_list[x][0] == device_protocol_list[protocol_name][0]) and (devices_list[x][2] == device_protocol_list[protocol_name][2]):
                print (device_protocol_list[protocol_name][1])
            protocol_name += 1

        x+=1


if options.listclasses:
    print ("XX:YY:ZZ - XX = Class : YY = Subclass : ZZ = Protocol")
    list_classes(supported_devices)

if options.identify:
    devtmp = []
    identify_classes(devtmp)

if options.fuzzs:
    error = 0
    devsubproto = options.fuzzs.split(':')

    if len(devsubproto) != 5:
        print ("Error: Device class specification invalid - too many parameters\n")
        sys.exit()

    try:
        usbclass = int(devsubproto[0],16)
        usbsubclass = int(devsubproto[1],16)
        usbproto = int(devsubproto[2],16)
        fuzztype = devsubproto[3]
        fuzztestcase = int(devsubproto[4])
    except:
        print ("Error: Device class specification invalid\n")
        sys.exit()

    if fuzztype == "E" and error != 1:
        print ("Fuzzing:")
        devicetmp = [[usbclass,usbsubclass,usbproto]]
        identify_classes(devicetmp)
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        print (timestamp, end="")
        print (" Enumeration phase: %04d -" % fuzztestcase, testcases_class_independent[fuzztestcase][0])
        execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_class_independent[fuzztestcase],serial0)

    elif fuzztype == "C" and error != 1:
        print ("Fuzzing:")
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        print (timestamp, end="")

        devicetmp = [[usbclass,usbsubclass,usbproto]]
        identify_classes(devicetmp)
        print (" Class-specific data...")
        if usbclass == 1:   #Audio
            print (" Audio class: %04d -" % fuzztestcase, testcases_audio_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_audio_class[fuzztestcase],serial0)
        elif usbclass == 3:   #HID
            print (" HID class: %04d -" % fuzztestcase, testcases_hid_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_hid_class[fuzztestcase],serial0)
        elif usbclass == 6:   #Image
            print (" Image class: %04d -" % fuzztestcase, testcases_image_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_image_class[fuzztestcase],serial0)
        elif usbclass == 7:    #Printer
            print (" Printer class: %04d -" % fuzztestcase, testcases_printer_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_printer_class[fuzztestcase],serial0)
        elif usbclass == 8:    #Mass Storage
            print (" Mass Storage class: %04d -" % fuzztestcase, testcases_mass_storage_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_mass_storage_class[fuzztestcase],serial0)
        elif usbclass == 9:    #Hub
            print (" Hub class: %04d -" % fuzztestcase, testcases_hub_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_hub_class[fuzztestcase],serial0)
        elif usbclass == 11:    #Printer
            print (" Smartcard class: %04d -" % fuzztestcase, testcases_smartcard_class[fuzztestcase][0])
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_smartcard_class[fuzztestcase],serial0)
        else:
            print ("\n***Class fuzzing not yet implemented for this device***\n")
        
    else:
        optionerror()

if options.fuzzc:
    start_fuzzcase = 0
    devsubproto = options.fuzzc.split(':')
    if len(devsubproto) > 5:
        print ("Error: Device class specification invalid - too many parameters\n")
        sys.exit()

    try:
        usbclass = int(devsubproto[0],16)
        usbsubclass = int(devsubproto[1],16)
        usbproto = int(devsubproto[2],16)
        fuzztype = devsubproto[3]
        try:
            if devsubproto[4]:
                start_fuzzcase = int(devsubproto[4])
        except:
            pass
    except:
        print ("Error: Device class specification invalid\n")
        sys.exit()

    if fuzztype == "E" or fuzztype == "A": 

        print ("Fuzzing:")
        if options.log:
            fplog.write ("Fuzzing:\n")
        devicetmp = [[usbclass,usbsubclass,usbproto]]
        identify_classes(devicetmp)
        print ("Enumeration phase...")
        if options.log:
            fplog.write ("Enumeration phase...\n")

        current_serial_port = 0
        x = 0
        if start_fuzzcase:
            if start_fuzzcase < len (testcases_class_independent):
                x = start_fuzzcase
            else:
                print ("Error: Invalid fuzzcase - starting from zero")
                if options.log:
                    fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
        else:
            x = 0
        while (x < len (testcases_class_independent)):
            timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print (timestamp, end="")
            print_output = " Enumeration phase: %04d - %s" % (x, testcases_class_independent[x][0])
            print (print_output)

            if options.log:
                fplog.write (timestamp)
                fplog.write (print_output)
                
            execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_class_independent[x],serial0)
            x+=1

    if fuzztype == "C" or fuzztype == "A":

        print ("Fuzzing:")
        if options.log:
            fplog.write ("Fuzzing:\n")
        devicetmp = [[usbclass,usbsubclass,usbproto]]
        identify_classes(devicetmp)
        print ("Class-specific data...")
        if options.log:
            fplog.write ("Class-specific data...\n")
        if usbclass == 3:   #HID

            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_hid_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_hid_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " HID class: %04d - %s" % (x, testcases_hid_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_hid_class[x],serial0)
                x+=1

        elif usbclass == 6:   #Image
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_image_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_image_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Image class: %04d - %s" % (x, testcases_image_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_image_class[x],serial0)
                x+=1

        elif usbclass == 7:   #Printer
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_printer_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_printer_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Printer class: %04d - %s" % (x, testcases_printer_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_printer_class[x],serial0)
                x+=1

        elif usbclass == 1:   #Audio
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_audio_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_audio_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Audio class: %04d - %s" % (x, testcases_audio_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_audio_class[x],serial0)
                x+=1

        elif usbclass == 8:   #Mass Storage
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_mass_storage_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_mass_storage_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Mass Storage class: %04d - %s" % (x, testcases_mass_storage_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_mass_storage_class[x],serial0)
                x+=1

        elif usbclass == 9:   #Hub
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_hub_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_hub_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Hub class: %04d - %s" % (x, testcases_hub_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_hub_class[x],serial0)
                x+=1

        elif usbclass == 11:   #Smartcard
            x = 0
            if start_fuzzcase:
                if start_fuzzcase < len (testcases_smartcard_class):
                    x = start_fuzzcase
                else:
                    print ("Error: Invalid fuzzcase - starting from zero")
                    if options.log:
                        fplog.write ("Error: Invalid fuzzcase - starting from zero\n")
            else:
                x = 0
            while (x < len (testcases_smartcard_class)):
                timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print (timestamp, end="")
                print_output = " Smartcard class: %04d - %s" % (x, testcases_smartcard_class[x][0])
                print (print_output)

                if options.log:
                    fplog.write (timestamp)
                    fplog.write (print_output)

                execute_fuzz_testcase (usbclass,usbsubclass,usbproto,testcases_smartcard_class[x],serial0)
                x+=1

        else:
            print ("\nError: Class fuzzing not yet implemented for this device\n")


    if fuzztype != "C" and fuzztype != "E" and fuzztype != "A":
        optionerror()

if options.vendor:
    vidpid = options.vendor.split(':')
    vid = int(vidpid[0],16)
    pid = int(vidpid[1],16)
    rev = device_rev

    print ("Emulating vendor-specific device:", vidpid[0], vidpid[1])
    connect_as_vendor (vid, pid, rev, 1)

if options.apple:
    vidpidrev = options.apple.split(':')
    vid = int(vidpidrev[0],16)
    pid = int(vidpidrev[1],16)
    rev = int(vidpidrev[2],16)
    print ("Emulating iPhone device:", vidpidrev[0], vidpidrev[1], vidpidrev[2])
    connect_as_iphone (vid, pid, rev, 3)

if options.cls:
    devsubproto = options.cls.split(':')
    if len(devsubproto) != 3:
        print ("Error: Device class specification invalid\n")
    else:
        try:
            dev = int(devsubproto[0],16)
            sub = int(devsubproto[1],16)
            proto = int(devsubproto[2],16)
            devicetmp = [[dev,sub,proto]]
            identify_classes(devicetmp)
        except:
            print ("Error: Device class specification invalid\n")

if options.device:
    devsubproto = options.device.split(':')
    if len(devsubproto) != 3:
        print ("Error: Device class specification invalid\n")
        sys.exit()

    try:
        dev = int(devsubproto[0],16)
        sub = int(devsubproto[1],16)
        proto = int(devsubproto[2],16)
        devicetmp = [[dev,sub,proto]]
    except:
        print ("Error: Device class specification invalid\n")
        sys.exit()


    print ("Emulating ",end="")

    list_classes(devicetmp)

    if dev == 1:
        connect_as_audio (device_vid, device_pid, device_rev, 3)
    elif dev == 2:
        connect_as_cdc (device_vid, device_pid, device_rev, 3)
    elif dev == 3:
        connect_as_keyboard (device_vid, device_pid, device_rev, 3)
    elif dev == 6:
        connect_as_image (device_vid, device_pid, device_rev, 2)   
    elif dev == 7:
        connect_as_printer (device_vid, device_pid, device_rev, 3)
    elif dev == 8:
        connect_as_mass_storage (device_vid, device_pid, device_rev, 3)
    elif dev == 9:
        connect_as_hub (device_vid, device_pid, device_rev, 3)
    elif dev == 10:
        connect_as_cdc (device_vid, device_pid, device_rev, 0)
    elif dev == 11:
        connect_as_smartcard (device_vid, device_pid, device_rev, 3)
    else:
        print ("Error: Device not supported\n")

if options.osid:

    print ("Fingerprinting the connected host - please wait...")

    try:
        print (vid)
    except:
        vid = 0x1111

    try:
        print (pid)
    except:
        pid = 0x2222

    try:
        print (rev)
    except:
        rev = 0x3333

#    sp = connectserial()
    fake_testcase = ["dummy","",0]
    fd = Facedancer(sp, verbose=0)
    logfp = 0
    if options.log:
        logfp = fplog
    u = MAXUSBApp(fd, logfp, 3, fake_testcase, verbose=0)
    d = USBPrinterDevice(u, vid, pid, rev, 7, 1, 2, verbose=0)
    d.connect()
    try:
        d.run()
    except KeyboardInterrupt:
        d.disconnect()
        if options.log:
            fplog.close()

    matching1 = [s for s in u.fingerprint if "GetDes:1:0" in s]
    matching2 = [s for s in u.fingerprint if "GetDes:2:0" in s]

    if len(matching1) == 2 and len(matching2) == 2 and len(u.fingerprint) == 5:
        print ("\nOS Matches: Sony Playstation 3\n")
        sys.exit()

    if any("SetFea" in s for s in u.fingerprint):
        print ("\nOS Matches: Apple iPad/iPhone\n")
        sys.exit()
    
    matching = [s for s in u.fingerprint if "SetInt" in s]
    if len(matching) == 2:
        print ("\nOS Matches: Ubuntu Linux\n")
        sys.exit()

    if any("GetDes:3:4" in s for s in u.fingerprint):
        print ("\nOS Matches: Chrome OS\n")
        sys.exit()

    matching = [s for s in u.fingerprint if "GetDes:3:3" in s]
    if len(matching) == 2:
        print ("\nOS Matches: Microsoft Windows 8\n")
        sys.exit()

    print ("\nUnknown OS - Fingerprint:")
    print (u.fingerprint) 


if options.log:
    fplog.close()


