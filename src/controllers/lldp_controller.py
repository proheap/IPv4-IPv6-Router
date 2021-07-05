import time

from src.helpers.parsing_helper import parseFrame
from src.models.eth_model import ETH_frame
from src.models.lldp_model import LLDP_PACKET_FREQUENCY, TLV_chassis, TLV_port, TLV_ttl, TLV_end, LLDP_TLV_TTL, LLDP_PACKET_FREQUENCY

class LLDP():
    def __init__(self):
        self.lldpTable = []

    def getLLDPTable(self):
        return self.lldpTable

    def printLLDPTable(self):
        print(f'Device ID\tLocal int\tHoldtime\tCapability\tPort ID')
        for entry in self.lldpTable:
            entry.print()

    def sendPacket(self, interface):
        frame = ETH_frame(interface.mac)
        frame.addPayload(TLV_chassis(interface.mac))
        frame.addPayload(TLV_port(interface.label))
        frame.addPayload(TLV_ttl(LLDP_TLV_TTL))
        frame.addPayload(TLV_end())
        while True:
            interface.sock.send(frame.getBytes())
            time.sleep(LLDP_PACKET_FREQUENCY)


    def receivePacket(self, interface):
        while True:
            frame = interface.sock.recv(1000)
            self.lldpTable.append(parseFrame(frame, interface.label))
    