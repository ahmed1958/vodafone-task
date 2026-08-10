from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


# TIMESTAMP_RE = re.compile(
#     r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
#     r"(?P<device>\S+)\s+(?P<severity>\S+)\s+(?P<message>.+)$"
# )
# INTERFACE_RE = re.compile(r"Interface\s+(?P<interface>\S+)")
# BGP_RE = re.compile(r"BGP neighbor\s+(?P<neighbor>\d{1,3}(?:\.\d{1,3}){3})")
# SOURCE_IP_RE = re.compile(r"from\s+(?P<source_ip>\d{1,3}(?:\.\d{1,3}){3})")


@dataclass
class Event:
    timestamp: str
    device: str
    severity: str #(Info,Warning,error)
    message: str
    event_category: str #Interface,BGP....
    interface: Optional[str] = None 
    bgp_neighbor: Optional[str] = None
    source_ip: Optional[str] = None #snmp
    numeric_threshold: Optional[float] = None #cpu

    @property
    def datetime(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)


# def classify(message: str) -> str:
#     text = message.lower()
#     if "interface" in text:
#         return "Interface"
#     if "bgp neighbor" in text:
#         return "BGP"
#     if "cpu utilization" in text:
#         return "CPU"
#     if "temperature" in text or "thermal" in text:
#         return "Thermal"
#     if "snmp authentication" in text:
#         return "SNMP/Security"
#     return "Other"


# def parse_line(line: str) -> Optional[Event]:
#     match = TIMESTAMP_RE.match(line.strip())
#     if not match:
#         return None
#     #convert data to dict
#     data = match.groupdict()
#     message = data["message"]
#     category = classify(message)

#     interface = None
#     bgp_neighbor = None
#     source_ip = None
#     numeric_threshold = None

#     m = INTERFACE_RE.search(message)
#     if m:
#         interface = m.group("interface")

#     m = BGP_RE.search(message)
#     if m:
#         bgp_neighbor = m.group("neighbor")

#     m = SOURCE_IP_RE.search(message)
#     if m:
#         source_ip = m.group("source_ip")

#     if category == "CPU":
#         m = re.search(r"(\d+(?:\.\d+)?)\s*%", message)
#         if m:
#             numeric_threshold = float(m.group(1))

#     return Event(
#         timestamp=data["timestamp"],
#         device=data["device"],
#         severity=data["severity"],
#         message=message,
#         event_category=category,
#         interface=interface,
#         bgp_neighbor=bgp_neighbor,
#         source_ip=source_ip,
#         numeric_threshold=numeric_threshold,
#     )

