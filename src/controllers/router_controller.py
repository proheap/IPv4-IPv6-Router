import socket
import ipaddress
import threading
from pyroute2 import IPRoute
from pyroute2.netlink.exceptions import NetlinkError

from src.helpers.conversion_helper import maskToPrefix
from src.helpers.promiscuous_helper import setPromiscuousMode
from src.controllers.lldp_controller import LLDP
from src.models.interface_model import Interface

# Linux values
ETH_P_ALL               = 0x0003

class Router():
    def __init__(self):
        self.iproute = IPRoute()

        self.activeSockets = []
        self.interfaces = []
        self.addInterfaces()

        self.enableLLDP = False

    def addInterfaces(self):
            # Adding interfaces to list using module pyroute2
            addresses = ()
            addresses = self.iproute.get_addr(family=2)

            print("Added interfaces:")
            for address in addresses:
                ip = address.get_attrs('IFA_ADDRESS')[0]
                prefix = address['prefixlen']
                intLabel = address.get_attrs('IFA_LABEL')[0]
                link = self.iproute.get_links(ifname=intLabel)
                mac = [x[1]
				    for x in link["attrs"] if x[0] == "IFLA_ADDRESS"][0]
                print(f'{ip}/{prefix} [{intLabel}: {mac}]')
                self.interfaces.append(Interface(ipaddress.IPv4Interface(f'{ip}/{prefix}'), intLabel, mac))

    def createSocket(self, interface):
        intLabel = interface.label
        # Create socket on interface
        for sock in self.activeSockets:
            if sock.getsockname() == (intLabel, 0):
                print (f'Socket {intLabel} was already open!')
                return False
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))

        # Bind to the port
        sock.bind((intLabel, 0))

        # Append socket to active socket list
        self.activeSockets.append(sock)
        interface.sock = sock
        print (f'{intLabel} -> SOCKET ADDED')
        return True

    def closeSocket(self, interface):
        intLabel = interface.label
        # Closing socket with 'ip' on 'port'
        for sock in self.activeSockets:
            if sock.getsockname() == (intLabel, 0):
                sock.close()
                self.activeSockets.remove(sock)
                interface.sock = 0
                print (f'{intLabel} -> SOCKET CLOSED')
                return True
        print (f'Socket {intLabel} wasn`t open!')
        return False

    def findSocket(self, ip, port):
        for sock in self.activeSockets:
            if sock.getsockname() == (ip, port):
                return True
        return False

    def addRoute(self, ip, mask, nextHop, metric):
		# Adding route to linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in range(len(self.interfaces)):
            int_network = self.interfaces[i].ip.network
            if ipaddress.IPv4Address(nextHop) in int_network:
                interface = self.interfaces[i].ip
                assignedInt = True
            if ipaddress.IPv4Network(f'{ip}/{prefix}') == int_network:
                return False
        if assignedInt == True:
            try:
                self.iproute.route("add",
                                    dst=ip,
                                    mask=prefix,
                                    gateway=str(interface.ip),
                                    metrics={"mtu": metric})
                print(f'{ip}/{prefix} {str(interface.ip)} -> ROUTE ADDED')
                return True
            except NetlinkError as error:
                if error.code == 17:
                    print(f'IP Address {ip} already exists.')
                else:
                    raise error
        else:
            return False
        return True

    def deleteRoute(self, ip, mask, nextHop):
        # Deleting route from linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in range(len(self.interfaces)):
            int_network = self.interfaces[i].ip.network
            if ipaddress.IPv4Address(nextHop) in int_network:
                interface = self.interfaces[i].ip
                assignedInt = True
                break

        if assignedInt == True:
            try:
                self.iproute.route("delete",
                                    dst=ip,
                                    mask=prefix,
                                    gateway=str(interface.ip))
                print(f'{ip}/{prefix} {str(interface.ip)} -> ROUTE REMOVED')
                return True
            except NetlinkError as error:
                if error.code == 3:
                    print(f'IP Address {ip} doesn`t exists.')
                else:
                    raise error
        return False

    def startLLDP(self):
        self.enableLLDP = True
        # Creating LLDP class for LLDP protocol
        lldp = LLDP(self.activeSockets)
        # Creating sockets for every interface
        for interface in self.interfaces:
            self.createSocket(interface)
            # Set promiscuous mode
            setPromiscuousMode(interface)
            # Recieving LLDP packets
            tRecv = threading.Thread(target=lldp.receivePacket, args=(interface,))
            tRecv.start()
        