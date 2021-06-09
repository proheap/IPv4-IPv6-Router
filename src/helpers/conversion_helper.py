from ipaddress import IPv4Network

def macToBytes(mac):
    return bytes.fromhex(mac.replace(':', ''))

def macFromBytes(bytesMAC):
    ret = bytesMAC.hex()
    mac = ""
    for i in range(0, 6):
        mac += ret[0+(2*i):2+(2*i)]+ ":"
    return mac[0:-1]

def maskToPrefix(mask):
    return IPv4Network(f'0.0.0.0/{mask}').prefixlen