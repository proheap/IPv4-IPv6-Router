class Interface(object):
    def __init__(self, ip, name, mac, sock=0):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.sock = sock
