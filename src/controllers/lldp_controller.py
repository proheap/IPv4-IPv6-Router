import time

from src.helpers.parsing_helper import parseLLDPFrame
from src.models.eth_model import ETH_frame
from src.models.lldp_model import LLDP_PACKET_FREQUENCY, TLV_chassis, TLV_port, TLV_ttl, TLV_end, LLDP_PACKET_FREQUENCY

class LLDP():
    def __init__(self):
        self.lldpTable = []

    def addEntryToLLDPTable(self, entryLLDP):
        for entry in self.lldpTable:
            if entry.deviceID == entryLLDP.mac:
                return False
        self.lldpTable.append(entryLLDP)
        return True

    def getLLDPTable(self):
        return self.lldpTable

    def printLLDPTable(self):
        print(f'Device ID\t\tLocal int\tHoldtime\tCapability\tPort ID')
        for entry in self.lldpTable:
            entry.print()

    def sendPacket(self, interface):
        while True:
            frameLLDP = ETH_frame(interface.mac)
            frameLLDP.addPayload(TLV_chassis(interface.mac))
            frameLLDP.addPayload(TLV_port(interface.name))
            frameLLDP.addPayload(TLV_ttl())
            frameLLDP.addPayload(TLV_end())
            interface.sock.send(frameLLDP.getBytes())
            print(f'LLDP was sent on {interface.name}')
            time.sleep(LLDP_PACKET_FREQUENCY)

    def receivePacket(self, interface):
        print(f'Receiving on {interface.name}:')
        while True:
            frameLLDP = interface.sock.recv(1000)
            entryLLDP = parseLLDPFrame(frameLLDP, interface.name)
            if entryLLDP is not None:
                self.addEntryToLLDPTable(entryLLDP)