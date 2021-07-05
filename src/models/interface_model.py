class Interface(object):
    def __init__(self, name, mac, ipv4=None, ipv6=None, sock=0):
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.name = name
        self.mac = mac
        self.sock = sock

    def print(self):
        if self.ipv6 is None:
            if self.ipv4 is None:
                print(f'-/-\t\t\t-\t\t\t\t[{self.name}: {self.mac}]')
            else:
                print(f'{self.ipv4.with_prefixlen}\t-\t\t[{self.name}: {self.mac}]')
        else:
            if self.ipv4 is None:
                print(f'-/-\t\t\t{self.ipv6.ip}\t\t[{self.name}: {self.mac}]')
            else:
                print(f'{self.ipv4.with_prefixlen}\t{self.ipv6.ip}\t[{self.name}: {self.mac}]')
        