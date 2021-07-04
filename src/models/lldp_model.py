import struct

from src.helpers.conversion_helper import macToBytes

## LLDP Ethernet Protocol:
# LLDP destination MAC:
LLDP_DST_MAC            = "01:80:c2:00:00:0e"
# LLDP Protocol ID:
LLDP_PROTO_ID           = 0x88cc
# LLDP Protocol BitFiddling Mask:
LLDP_TLV_TYPE_MASK      = 0xfe00
LLDP_TLV_LEN_MASK       = 0x01ff
# LLDP Length:
LLDP_TLV_TYPE_BIT_LEN   = 7
LLDP_TLV_LEN_BIT_LEN    = 9
# LLDP TLV Type:
LLDP_TLV_TYPE_PDUEND    = 0x00
LLDP_TLV_TYPE_CHASSISID = 0x01
LLDP_TLV_TYPE_PORTID    = 0x02
LLDP_TLV_TYPE_TTL       = 0x03
LLDP_TLV_TYPE_CAP       = 0x07
# LLDP Timers:
LLDP_HOLD_TIME          = 120
LLDP_PACKET_FREQUENCY   = 30

class LLDP_TLV(object):
    def __init__(self, tlvType):
        self.tlvType = tlvType
        self.tlvLength = 0

    def getBytes(self):
        tl = 0
        tl |= (self.tlvType << LLDP_TLV_LEN_BIT_LEN)
        tl |= self.tlvLength
        return  struct.pack('!H', tl)

class TLV_chassis(LLDP_TLV):
    def __init__(self, srcMAC):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_CHASSISID)
        self.tlvLength = 1 + 6
        self.tlvSubtype = 4
        self.tlvChassisID = srcMAC
    
    def getBytes(self):
        return LLDP_TLV.getBytes(self) + struct.pack('!B', self.tlvSubtype) + macToBytes(self.tlvChassisID)
    
    def print(self):
        print(f'    TLV Chassis: Chassis ID: {self.tlvChassisID}')

class TLV_port(LLDP_TLV):
    def __init__(self, portName):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_PORTID)
        self.tlvLength = 1
        self.tlvSubtype = 5
        self.tlvPortID = portName
    
    def getBytes(self):
        bytesPortID = self.tlvPortID.encode()
        self.tlvLength += len(bytesPortID)
        return LLDP_TLV.getBytes(self) + struct.pack('!B', self.tlvSubtype) + bytesPortID
    
    def print(self):
        print(f'    TLV Port: Port ID: {self.tlvPortID}')

class TLV_ttl(LLDP_TLV):
    def __init__(self, ttl):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_TTL)
        self.tlvLength = 2
        self.tlvTTL = ttl
    
    def getBytes(self):
        return LLDP_TLV.getBytes(self) + struct.pack('!H', self.tlvTTL)

class TLV_end(LLDP_TLV):
    def __init__(self):
        super().__init__(LLDP_TLV_TYPE_PDUEND)

class LLDP_entry(object):
    def __init__(self, deviceID, localInt, portID, holdtime=120, capability="-"):
        self.deviceID = deviceID
        self.localInt = localInt
        self.holdtime = holdtime
        self.capability = capability
        self.portID = portID

    def print(self):
        print(f'{self.deviceID}\t{self.localInt}\t{self.holdtime}\t{self.capability}\t{self.portID}')