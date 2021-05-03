# LLDP Ethernet Protocol:
LLDP = {
    "DST_MAC": "01:80:c2:00:00:0e", # LLDP Destination MAC
    "PROTO_ID": 0x88cc,             # LLDP Protocol ID
    "HOLD_TIME": 120,               # LLDP Timers
    "PACKET_FREQUENCY_TIMER": 30
}

LLDP_TLV = {
    "LEN_MASK ": 0x01ff,            # LLDP Protocol BitFiddling Mask
    "TYPE_BIT_LEN ": 7,             # LLDP Lengths
    "LEN_BIT_LEN": 9,
    "TYPE_PDUEND": 0x00,            # LLDP TLV Types
    "TYPE_CHASSISID": 0x01,
    "TYPE_PORTID": 0x02,
    "TYPE_TTL": 0x03
}