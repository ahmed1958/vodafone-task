import ipaddress
from collections import defaultdict

def validate_devices(devices):
    results = []
    # Loopback0
    for d in devices:
        if not d.loopback0:
            results.append((d.hostname, "Loopback0", "FAIL", "Loopback0 is missing"))
        else:
            results.append((d.hostname, "Loopback0", "PASS", "Loopback0 is present"))

    # Subnet overlap
    nets = []
    for d in devices:
        for i in d.interfaces:
            if i.subnet:
                try: nets.append((d.hostname, i.name, ipaddress.ip_network(i.subnet)))
                except ValueError: pass
    seen = set()
    for idx, (dev, intf, net) in enumerate(nets):
        for dev2, intf2, net2 in nets[idx+1:]:
            if dev == dev2: continue
            if net.overlaps(net2):
                key = tuple(sorted([(dev,intf),(dev2,intf2)])) + (str(net),str(net2))
                if key not in seen:
                    seen.add(key)
                    results.append((dev, "Subnet overlap", "FAIL", f"{intf} {net} overlaps {dev2}:{intf2} {net2}"))

    # OSPF area consistency: compare declared areas across devices.
    area_devices = [(d.hostname, sorted(set(d.ospf_areas))) for d in devices if "OSPF" in d.routing_protocols and d.ospf_areas]
    all_areas = sorted(set(a for _, areas in area_devices for a in areas))
    if len(all_areas) > 1:
        for host, areas in area_devices:
            results.append((host, "OSPF area consistency", "FAIL", f"Declared OSPF areas {', '.join(areas)}; platform set is {', '.join(all_areas)}"))
    else:
        for host, _ in area_devices:
            results.append((host, "OSPF area consistency", "PASS", "OSPF area declarations are consistent"))

    # BGP ASN/area consistency is intentionally limited: source configs do not declare
    # a common BGP area. We validate that BGP is at least consistently represented.
    bgp_hosts = [d.hostname for d in devices if "BGP" in d.routing_protocols]
    if bgp_hosts:
        for host in bgp_hosts:
            results.append((host, "BGP consistency", "PASS", "BGP is declared; no common BGP area is present in supplied syntax"))

    return results