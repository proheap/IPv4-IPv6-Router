import struct

from src.models.lldp_model import LLDP_DST_MAC, LLDP_PROTO_ID
from src.helpers.conversion_helper import macToBytes

class ETH_frame(object):
    def __init__(self, srcMAC):
        self.dstMAC = LLDP_DST_MAC
        self.srcMAC = srcMAC
        self.ethType = LLDP_PROTO_ID
        self.payload = list()

    def addPayload(self, payload):
        self.payload.append(payload)

    def getBytes(self):
        frame = macToBytes(self.dstMAC) + macToBytes(self.srcMAC) + struct.pack('!H', self.ethType)
        for tlv in self.payload:
            frame += tlv.getBytes()
        return frame
    def print(self):
        print(f'DstMAC: {self.dstMAC}, SrcMAC: {self.srcMAC}, EthType: 0x{self.ethType:02x}')
        for tlv in self.payload:
            tlv.print()