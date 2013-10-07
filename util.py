# util.py
#
# Random helpful functions.

import struct

def bytes_as_hex(b, delim=" "):
    return delim.join(["%02x" % x for x in b])

def change_byte_order(data):
    return (bytes(reversed(data)))

def int_to_bytestring(i):
    return struct.pack('B',int(i))
       
