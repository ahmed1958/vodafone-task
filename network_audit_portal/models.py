from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Interface:
    name: str
    ip_address: Optional[str] = None
    subnet: Optional[str] = None
    description: Optional[str] = None
    loopback: bool = False

@dataclass
class Device:
    hostname: str
    vendor: str
    interfaces: list[Interface] = field(default_factory=list)
    routing_protocols: list[str] = field(default_factory=list)
    bgp_neighbors: list[str] = field(default_factory=list)
    ospf_areas: list[str] = field(default_factory=list)
    acl_rules: list[str] = field(default_factory=list)
    loopback0: bool = False
    loopback_ip: Optional[str] = None
    router_id: Optional[str] = None

@dataclass
class LogEvent:
    timestamp: str
    device: str
    severity: str
    message: str
    category: str
    risk_level: str = "None"