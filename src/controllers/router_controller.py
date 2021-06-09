import socket
import struct
import threading
import ipaddress
from pyroute2 import IPRoute, NetlinkError

from src.helpers.conversion_helper import maskToPrefix

class Router():
    def __init__(self):
        self.iproute = IPRoute()

        self.activeSockets = []
        self.interfaces = []
        self.addInterfaces()

    def addInterfaces(self):
            # Adding interfaces to list using module pyroute2
            addresses = ()
            addresses = self.iproute.get_addr(family=2)

            print("Added interfaces:")
            for address in addresses:
                ip = [x[1]
                    for x in address["attrs"] if x[0] == "IFA_ADDRESS"][0]
                prefix = address["prefixlen"]
                int_name = [x[1]
                    for x in address["attrs"] if x[0] == "IFA_LABEL"][0]
                print(f'{ip}/{prefix} [{int_name}]')

                self.interfaces.append(ipaddress.IPv4Interface(f'{ip}/{prefix}'))

    def createSocket(self, ip, port):
        # Create socket with 'ip' on 'port'
        for sock in self.activeSockets:
            if sock.getsockname() == (ip, port):
                print (f'Socket {ip}:{port} was already open!')
                return False
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)

        # Bind to the port
        sock.bind((ip, port))

        # Append socket to active socket list
        self.activeSockets.append(sock)
        print (f'{self.activeSockets[-1].getsockname()[0]}:{self.activeSockets[-1].getsockname()[1]} -> SOCKET ADDED')
        return True

    def closeSocket(self, ip, port):
        # Closing socket with 'ip' on 'port'
        for sock in self.activeSockets:
            if sock.getsockname() == (ip, port):
                sock.close()
                self.activeSockets.remove(sock)
                print (f'{ip}:{port} -> SOCKET CLOSED')
                return True
        print (f'Socket {ip}:{port} wasn`t open!')
        return False

    def findSocket(self, ip, port):
        for sock in self.activeSockets:
            if sock.getsockname() == (ip, port):
                return True
        return False

    def addRoute(self, ip, mask, nextHop):
		# Adding route to linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in range(len(self.interfaces)):
            int_network = self.interfaces[i].network
            if ipaddress.IPv4Address(nextHop) in int_network:
                interface = self.interfaces[i]
                assignedInt = True
            if ipaddress.IPv4Network(f'{ip}/{prefix}') == int_network:
                return False
        if assignedInt == True:
            try:
                self.iproute.route("add",
                                    dst=ip,
                                    mask=prefix,
                                    gateway=str(interface.ip),
                                    metrics={"mtu": 1400,
                                            "hoplimit": 16})
                print(f'{ip}/{prefix} {str(interface.ip)} -> ROUTE ADDED')
                return True
            except NetlinkError as e:
                if e.code == 17:
                    print(f'IP Address {ip} already exists.')
                else:
                    raise e
        else:
            return False
        return True

    def removeRoute(self, ip, mask, nextHop):
        # Removing route from linux routing table
        prefix = maskToPrefix(mask)
        assignedInt = False

        for i in range(len(self.interfaces)):
            int_network = self.interfaces[i].network
            if ipaddress.IPv4Address(nextHop) in int_network:
                interface = self.interfaces[i]
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
            except NetlinkError as e:
                if e.code == 3:
                    print(f'IP Address {ip} doesn`t exists.')
                else:
                    raise e
        return False
