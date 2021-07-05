import struct

from src.helpers.conversion_helper import macToBytes

# MAC SIZE
MAC_SIZE                = 6

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
# LLDP TLV Chassis Subtype:
LLDP_TLV_CHASSIS_SUB_MAC= 0x04
# LLDP TLV Port Subtype:
LLDP_TLV_PORT_SUB_INT   = 0x05
# LLDP Timers:
LLDP_HOLD_TIME          = 120
LLDP_PACKET_FREQUENCY   = 30
# LLDP TTL:
LLDP_TLV_TTL_VALUE      = 120
LLDP_TLV_TTL_LEN        = 2

class LLDP_TLV(object):
    def __init__(self, tlvType):
        self.tlvType = tlvType
        self.tlvLength = 0

    def getBytes(self):
        tl = 0
        tl |= (self.tlvType << LLDP_TLV_LEN_BIT_LEN)
        tl |= self.tlvLength
        return struct.pack('!H', tl)

class TLV_chassis(LLDP_TLV):
    def __init__(self, srcMAC):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_CHASSISID)
        self.tlvLength = 1 + MAC_SIZE
        self.tlvSubtype = LLDP_TLV_CHASSIS_SUB_MAC
        self.tlvChassisID = srcMAC
    
    def getBytes(self):
        return LLDP_TLV.getBytes(self) + struct.pack('!B', self.tlvSubtype) + macToBytes(self.tlvChassisID)
    
    def print(self):
        print(f'    TLV Chassis: Chassis ID: {self.tlvChassisID}')

class TLV_port(LLDP_TLV):
    def __init__(self, portName):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_PORTID)
        self.tlvLength = 1
        self.tlvSubtype = LLDP_TLV_PORT_SUB_INT
        self.tlvPortID = portName
    
    def getBytes(self):
        bytesPortID = self.tlvPortID.encode()
        self.tlvLength += len(bytesPortID)
        return LLDP_TLV.getBytes(self) + struct.pack('!B', self.tlvSubtype) + bytesPortID
    
    def print(self):
        print(f'    TLV Port: Port ID: {self.tlvPortID}')

class TLV_ttl(LLDP_TLV):
    def __init__(self, ttl=LLDP_TLV_TTL_VALUE):
        LLDP_TLV.__init__(self, LLDP_TLV_TYPE_TTL)
        self.tlvLength = LLDP_TLV_TTL_LEN
        self.tlvTTL = ttl
    
    def getBytes(self):
        return LLDP_TLV.getBytes(self) + struct.pack('!H', self.tlvTTL)

class TLV_end(LLDP_TLV):
    def __init__(self):
        super().__init__(LLDP_TLV_TYPE_PDUEND)

class LLDP_entry(object):
    def __init__(self, deviceID, localInt, portID, capability="-", holdtime=120):
        self.deviceID = deviceID
        self.localInt = localInt
        self.holdtime = holdtime
        self.capability = capability
        self.portID = portID

    def getJSON(self):
        jsonLLDPEntry = dict()
        jsonLLDPEntry['deviceID'] = self.deviceID
        jsonLLDPEntry['localInt'] = self.localInt
        jsonLLDPEntry['holdtime'] = self.holdtime
        jsonLLDPEntry['capability'] = self.capability
        jsonLLDPEntry['portID'] = self.portID
        return jsonLLDPEntry

    def print(self):
        print(f'{self.deviceID}\t{self.localInt}\t{self.holdtime}\t\t{self.capability}\t{self.portID}')