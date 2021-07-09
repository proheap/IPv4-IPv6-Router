from ipaddress import IPv4Network

# LLDP Capability codes
LLDP_CAP_OTHER          = '0001'
LLDP_CAP_REPEATER       = '0002'
LLDP_CAP_BRIDGE         = '0004'
LLDP_CAP_AP             = '0008'
LLDP_CAP_ROUTER         = '0010'
LLDP_CAP_TELEPHONE      = '0020'
LLDP_CAP_CABLE          = '0040'
LLDP_CAP_STATION        = '0080'

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

def capabilityFromBytes(bytesCAP):
    capability = bytesCAP.hex()
    enabledCAP = capability[2:]
    if enabledCAP == LLDP_CAP_OTHER:
        stringCAP = "O"
    elif enabledCAP == LLDP_CAP_REPEATER:
        stringCAP = "P"
    elif enabledCAP == LLDP_CAP_BRIDGE:
        stringCAP = "B"
    elif enabledCAP == LLDP_CAP_AP:
        stringCAP = "W"
    elif enabledCAP == LLDP_CAP_ROUTER:
        stringCAP = "R"
    elif enabledCAP == LLDP_CAP_TELEPHONE:
        stringCAP = "T"
    elif enabledCAP == LLDP_CAP_CABLE:
        stringCAP = "C"
    elif enabledCAP == LLDP_CAP_STATION:
        stringCAP = "S"
    else:
        stringCAP = "-"
    return stringCAP