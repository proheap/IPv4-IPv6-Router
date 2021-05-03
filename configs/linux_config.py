LINUX = {
    "INTERFACE_SRC_MAC": "08:00:27:c4:0e:aa",
    "INTERFACE_PORT_NAME": "eth1",
    "ETH_P_ALL": 0x0003,        # Every packet
    "SIOCGIFFLAGS": 0x8913,     # `G` for Get socket flags
    "SIOCSIFFLAGS": 0x8914,     # `S` for Set socket flags
    "IFF_PROMISC": 0x0100       # Enter Promiscuous mode
}