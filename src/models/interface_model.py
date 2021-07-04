class Interface(object):
    def __init__(self, ip, label, mac, sock=0):
        self.ip = ip
        self.label = label
        self.mac = mac
        self.sock = sock
