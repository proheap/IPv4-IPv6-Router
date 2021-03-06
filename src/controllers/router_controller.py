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
        self.lldp = None

    def addInterfaces(self):
            # Adding interfaces to list using module pyroute2
            links = ()
            links = self.iproute.get_links(family=socket.AF_INET)

            print("Added interfaces:")
            for link in links:
                mac = link.get_attrs('IFLA_ADDRESS')[0]
                ifName = link.get_attrs('IFLA_IFNAME')[0]
                index = link['index']
                
                # IPv4
                address = self.iproute.get_addr(index=index, family=socket.AF_INET)
                if address:
                    address = address[0]
                    ip = [x[1]
                        for x in address['attrs'] if x[0] == 'IFA_ADDRESS'][0]
                    prefix = address['prefixlen']
                    ipv4 = ipaddress.IPv4Interface(f'{ip}/{prefix}')
                else:
                    ipv4 = None
                # IPv6
                address = self.iproute.get_addr(index=index, family=socket.AF_INET6)
                if address:
                    address = address[0]
                    ip = [x[1]
                        for x in address['attrs'] if x[0] == 'IFA_ADDRESS'][0]
                    ipv6 = ipaddress.IPv6Interface(ip)
                else:
                    ipv6 = None
                # Creating interface models
                if ifName != "lo":
                    interface = Interface(ifName, mac, ipv4, ipv6)
                    interface.print()
                    self.interfaces.append(interface)

    def createSocket(self, interface):
        intLabel = interface.name
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
        intLabel = interface.name
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

    def addIPv4Route(self, ip, mask, nextHop, metric):
		# Adding route to linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in self.interfaces:
            if i.ipv4 is not None:
                int_network = i.ipv4.network
                if ipaddress.IPv4Address(nextHop) in int_network:
                    interface = i.ipv4
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

    def deleteIPv4Route(self, ip, mask, nextHop):
        # Deleting route from linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in self.interfaces:
            int_network = i.ipv4.network
            if ipaddress.IPv4Address(nextHop) in int_network:
                interface = i.ipv4
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
    
    def addIPv6Route(self, ip, prefix, nextHop, metric):
		# Adding route to linux routing table
        assignedInt = False

        for i in self.interfaces:
            if i.ipv6 is not None:
                int_network = i.ipv6.network
                if ipaddress.IPv6Address(nextHop) in int_network:
                    interface = i
                    intIndex = self.iproute.link_lookup(ifname=interface.name)
                    assignedInt = True
                if ipaddress.IPv6Network(f'{ip}/{prefix}') == int_network:
                    return False
        if assignedInt == True:
            try:
                self.iproute.route("add",
                                    dst=ip,
                                    mask=prefix,
                                    oif=intIndex,
                                    metrics={"mtu": metric})
                print(f'{ip}/{prefix} {interface.name} -> ROUTE ADDED')
                return True
            except NetlinkError as error:
                if error.code == 17:
                    print(f'IP Address {ip} already exists.')
                else:
                    raise error
        else:
            return False
        return True
    
    def deleteIPv6Route(self, ip, prefix, nextHop):
        # Deleting route from linux routing table
        assignedInt = False

        for i in self.interfaces:
            int_network = i.ipv6.network
            if ipaddress.IPv6Address(nextHop) in int_network:
                interface = i
                intIndex = self.iproute.link_lookup(ifname=interface.name)
                assignedInt = True
                break

        if assignedInt == True:
            try:
                self.iproute.route("delete",
                                    dst=ip,
                                    mask=prefix,
                                    oif=intIndex)
                print(f'{ip}/{prefix} {interface.name} -> ROUTE REMOVED')
                return True
            except NetlinkError as error:
                if error.code == 3:
                    print(f'IP Address {ip} doesn`t exists.')
                else:
                    raise error
        return False

    def runLLDP(self):
        if self.enableLLDP == False:
            self.enableLLDP = True
            # Creating LLDP class for LLDP protocol
            self.lldp = LLDP()
            # Creating sockets for every interface
            for interface in self.interfaces:
                self.createSocket(interface)
                # Set promiscuous mode
                setPromiscuousMode(interface)
                # Recieving LLDP packets
                tRecv = threading.Thread(target=self.lldp.receivePacket, args=(interface,))
                tRecv.start()
                # Sending LLDP packets
                tSend = threading.Thread(target=self.lldp.sendPacket, args=(interface,))
                tSend.start()
        return True
    
    def getLLDPTable(self):
        if self.enableLLDP == True:
            self.lldp.printLLDPTable()
            return self.lldp.getLLDPTable()
        else:
            return None
