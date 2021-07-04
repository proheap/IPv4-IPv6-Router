from src.helpers.parsing_helper import parseFrame

class LLDP():
    def __init__(self):
        self.lldpTable = []

    def printLLDPTable(self):
        print(f'Device ID\tLocal int\tHoldtime\tCapability\tPort ID')
        for entry in self.lldpTable:
            entry.print()

    # def sendPacket(self):

    def receivePacket(self, interface):
        while True:
            frame = interface.sock.recv(1000)
            self.lldpTable.append(parseFrame(frame, interface.label))
    