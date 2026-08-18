from __future__ import annotations

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


BENIGN_CLASS = "Benign"
ATTACK_FAMILIES = (
    "DDoS",
    "DoS",
    "Mirai",
    "Recon",
    "Spoofing",
    "Web",
    "BruteForce",
    "Malware",
)
FINE_TO_FAMILY = {
    "Benign": "Benign",
    "Backdoor_Malware": "Malware",
    "BrowserHijacking": "Web",
    "CommandInjection": "Web",
    "DDoS-ACK_Fragmentation": "DDoS",
    "DDoS-HTTP_Flood": "DDoS",
    "DDoS-ICMP_Flood": "DDoS",
    "DDoS-ICMP_Fragmentation": "DDoS",
    "DDoS-PSHACK_FLOOD": "DDoS",
    "DDoS-RSTFINFLOOD": "DDoS",
    "DDoS-SYN_Flood": "DDoS",
    "DDoS-SlowLoris": "DDoS",
    "DDoS-SynonymousIP_Flood": "DDoS",
    "DDoS-TCP_Flood": "DDoS",
    "DDoS-UDP_Flood": "DDoS",
    "DDoS-UDP_Fragmentation": "DDoS",
    "DNS_Spoofing": "Spoofing",
    "DictionaryBruteForce": "BruteForce",
    "DoS-HTTP_Flood": "DoS",
    "DoS-SYN_Flood": "DoS",
    "DoS-TCP_Flood": "DoS",
    "DoS-UDP_Flood": "DoS",
    "MITM-ArpSpoofing": "Spoofing",
    "Mirai-greeth_flood": "Mirai",
    "Mirai-greip_flood": "Mirai",
    "Mirai-udpplain": "Mirai",
    "Recon-HostDiscovery": "Recon",
    "Recon-OSScan": "Recon",
    "Recon-PingSweep": "Recon",
    "Recon-PortScan": "Recon",
    "SqlInjection": "Web",
    "VulnerabilityScan": "Recon",
    "XSS": "Web",
}

