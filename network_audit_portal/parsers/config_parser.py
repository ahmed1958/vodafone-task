import ipaddress
import re
from pathlib import Path
from models import Device, Interface

class ConfigParser:
    """Parse the three config styles represented by the supplied sample files."""

    def parse_file(self, path: str | Path) -> Device:
        path = Path(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        vendor = self._vendor(text)
        if vendor == "Cisco":
            return self._cisco(text)
        if vendor == "Huawei":
            return self._huawei(text)
        return self._juniper(text)

    @staticmethod
    def _vendor(text):
        if re.search(r"^\s*hostname\s+", text, re.M) or "router ospf" in text:
            return "Cisco"
        if re.search(r"^\s*sysname\s+", text, re.M) or re.search(r"^\s*bgp\s+\d+", text, re.M):
            return "Huawei"
        return "Juniper"

    @staticmethod
    def _mask_to_prefix(mask):
        try:
            return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
        except ValueError:
            return None

    @classmethod
    def _subnet(cls, ip, mask):
        try:
            prefix = mask if isinstance(mask, int) else cls._mask_to_prefix(mask)
            if prefix is None:
                return None
            return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))
        except ValueError:
            return None

    @staticmethod
    def _add_routing(device, protocol):
        if protocol not in device.routing_protocols:
            device.routing_protocols.append(protocol)

    def _cisco(self, text):
        hostname = re.search(r"^hostname\s+(\S+)", text, re.M).group(1)
        d = Device(hostname, "Cisco")
        current = None
        for line in text.splitlines():
            s = line.strip()
            m = re.match(r"interface\s+(\S+)", s)
            if m:
                name = m.group(1)
                current = Interface(name, loopback=name.lower() == "loopback0")
                d.interfaces.append(current)
                if current.loopback:
                    d.loopback0 = True
                continue
            if current:
                m = re.match(r"ip address\s+(\S+)\s+(\S+)", s)
                if m:
                    current.ip_address = m.group(1)
                    current.subnet = self._subnet(*m.groups())
                    if current.loopback:
                        d.loopback_ip = current.ip_address
                m = re.match(r"description\s+(.+)", s)
                if m:
                    current.description = m.group(1)
            m = re.match(r"router ospf\s+\S+", s)
            if m:
                self._add_routing(d, "OSPF")
            m = re.match(r"network\s+\S+\s+\S+\s+area\s+(\S+)", s)
            if m:
                d.ospf_areas.append(m.group(1))
            m = re.match(r"router bgp\s+(\S+)", s)
            if m:
                self._add_routing(d, "BGP")
            m = re.match(r"neighbor\s+(\S+)\s+remote-as\s+\S+", s)
            if m:
                d.bgp_neighbors.append(m.group(1))
            m = re.match(r"bgp router-id\s+(\S+)", s)
            if m:
                d.router_id = m.group(1)
            m = re.match(r"(?:access-list\s+(\S+)|ip access-list extended\s+(\S+))", s)
            if m:
                d.acl_rules.append(next(x for x in m.groups() if x))
        return d

    def _huawei(self, text):
        hostname = re.search(r"^sysname\s+(\S+)", text, re.M).group(1)
        d = Device(hostname, "Huawei")
        current = None
        for line in text.splitlines():
            s = line.strip()
            m = re.match(r"interface\s+(\S+)", s)
            if m:
                name = m.group(1)
                current = Interface(name, loopback=name.lower() == "loopback0")
                d.interfaces.append(current)
                if current.loopback:
                    d.loopback0 = True
                continue
            if current:
                m = re.match(r"ip address\s+(\S+)\s+(\S+)", s)
                if m:
                    current.ip_address = m.group(1)
                    current.subnet = self._subnet(*m.groups())
                    if current.loopback:
                        d.loopback_ip = current.ip_address
                m = re.match(r"description\s+(.+)", s)
                if m:
                    current.description = m.group(1)
            m = re.match(r"ospf\s+\S+", s)
            if m:
                self._add_routing(d, "OSPF")
            m = re.match(r"area\s+(\S+)", s)
            if m:
                d.ospf_areas.append(m.group(1))
            m = re.match(r"bgp\s+(\S+)", s)
            if m:
                self._add_routing(d, "BGP")
            m = re.match(r"peer\s+(\S+)\s+as-number\s+\S+", s)
            if m:
                d.bgp_neighbors.append(m.group(1))
            m = re.match(r"router-id\s+(\S+)", s)
            if m:
                d.router_id = m.group(1)
            m = re.match(r"acl number\s+(\S+)", s)
            if m:
                d.acl_rules.append(m.group(1))
        return d

    def _juniper(self, text):
        host = re.search(r"host-name\s+(\S+);", text)
        d = Device(host.group(1), "Juniper")
        # Interfaces are parsed from the supplied Junos hierarchy.
        for m in re.finditer(
            r"(?m)^\s{4}(\S+) \{\s*.*?family inet \{\s*address ([0-9.]+)/(\d+);",
            text, re.S
        ):
            name, ip, prefix = m.groups()
            intf = Interface(name, ip, self._subnet(ip, int(prefix)),
                             loopback=name.lower() == "lo0",)
            d.interfaces.append(intf)
            if intf.loopback:
                d.loopback0 = True
                d.loopback_ip = ip
        if re.search(r"\bospf\s*\{", text):
            self._add_routing(d, "OSPF")
        for m in re.finditer(r"area\s+([0-9.]+)\s*\{", text):
            d.ospf_areas.append(m.group(1))
        if re.search(r"\bbgp\s*\{", text):
            self._add_routing(d, "BGP")
        for m in re.finditer(r"\bneighbor\s+([0-9.]+);", text):
            d.bgp_neighbors.append(m.group(1))
        for m in re.finditer(r"policy-statement\s+(\S+)\s*\{", text):
            d.acl_rules.append(m.group(1))
        for m in re.finditer(r"filter\s+(\S+)\s*\{", text):
            d.acl_rules.append(m.group(1))
        m = re.search(r"local-address\s+([0-9.]+);", text)
        if m:
            d.router_id = m.group(1)
        return d