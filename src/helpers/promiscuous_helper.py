import ctypes
import fcntl

SIOCGIFFLAGS            = 0x8913    # `G` for Get socket flags
SIOCSIFFLAGS            = 0x8914    # `S` for Set socket flags
IFF_PROMISC             = 0x0100    # Enter Promiscuous mode

class ifreq(ctypes.Structure):
    _fields_ = [("ifr_ifrn", ctypes.c_char * 16),
                ("ifr_flags", ctypes.c_short)]

def setPromiscuousMode(interface):
    ifr = ifreq()
    ifr.ifr_ifrn = interface.name.encode()
    fcntl.ioctl(interface.sock.fileno(), SIOCGIFFLAGS, ifr)
    ifr.ifr_flags |= IFF_PROMISC
    fcntl.ioctl(interface.sock.fileno(), SIOCSIFFLAGS, ifr)