import re
from datetime import datetime, timedelta
from collections import defaultdict
from models import LogEvent

LINE_RE = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(?P<device>\S+)\s+(?P<severity>\S+)\s+(?P<message>.+)$")

def classify(message):
    t = message.lower()
    if "interface" in t: return "Interface"
    if "bgp neighbor" in t: return "BGP"
    if "cpu utilization" in t: return "CPU"
    if "temperature" in t or "thermal" in t: return "Thermal"
    if "snmp authentication" in t: return "SNMP/Security"
    return "Other"

def parse_line(line):
    m = LINE_RE.match(line.strip())
    if not m: return None
    return LogEvent(m.group("timestamp"), m.group("device"), m.group("severity"), m.group("message"), classify(m.group("message")))

def parse_logs(folder):
    events = []
    for p in sorted(folder.glob("*.log")):
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            e = parse_line(line)
            if e: events.append(e)
    return sorted(events, key=lambda x: x.timestamp)

def detect_risks(events):
    """Task-1-compatible risk rules kept local to Task 2."""
    for e in events:
        t = e.message.lower()
        if e.category == "CPU":
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", e.message)
            if m and float(m.group(1)) >= 95: e.risk_level = "Critical"
            elif m and float(m.group(1)) > 80: e.risk_level = "Medium"
        elif e.category == "SNMP/Security":
            e.risk_level = "High"
    by_device = defaultdict(list)
    for e in events:
        by_device[e.device].append(e)
    for device, items in by_device.items():
        cpu = [e for e in items if e.category == "CPU" and "exceeded" in e.message.lower()]
        for i, e in enumerate(cpu):
            window = [x for x in cpu if abs(datetime.fromisoformat(x.timestamp)-datetime.fromisoformat(e.timestamp)) <= timedelta(hours=1)]
            if len(window) > 2 and e.risk_level != "Critical":
                e.risk_level = "High"
        snmp = defaultdict(list)
        for e in items:
            if e.category == "SNMP/Security":
                m = re.search(r"from\s+([0-9.]+)", e.message, re.I)
                if m: snmp[m.group(1)].append(e)
        for group in snmp.values():
            if len(group) > 1:
                for e in group: e.risk_level = "High"
    return events