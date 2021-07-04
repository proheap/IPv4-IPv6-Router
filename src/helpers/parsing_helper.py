import struct

from src.helpers.conversion_helper import macFromBytes
from src.models.lldp_model import *
from src.models.eth_model import ETH_frame

def parseFrame(frame, interface):
    ethType, = struct.unpack('!H', frame[12:14])
    if ethType != LLDP_PROTO_ID:
        return None
    parsedFrame = ETH_frame(macFromBytes(frame[6:12]))

    frameLength = len(frame)
    lldp = frame[14:frameLength]

    while True:
        tl, = struct.unpack('!H', lldp[0:2])
        tlvType = tl >> LLDP_TLV_LEN_BIT_LEN
        tlvLen = (tl & LLDP_TLV_LEN_MASK)
        if tlvType == LLDP_TLV_TYPE_PDUEND:
            break
        elif tlvType == LLDP_TLV_TYPE_CHASSISID:
            chasisID = macFromBytes(lldp[3:9])
            lldp = lldp[9:]
        elif tlvType == LLDP_TLV_TYPE_PORTID:
            portID = lldp[3:2 + tlvLen].decode()
            lldp = lldp[2 + tlvLen:] 
        elif tlvType == LLDP_TLV_TYPE_CAP:  
            capability = lldp[3:2 + tlvLen].decode()
            lldp = lldp[2 + tlvLen:] 
        else:
            lldp = lldp[2 + tlvLen:] 
    return LLDP_entry(chasisID, interface, portID)