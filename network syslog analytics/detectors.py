from __future__ import annotations

import re
from collections import defaultdict
from datetime import timedelta

from models import Event


class RiskDetector:
    def detect_all(self, events: list[Event]) -> list[dict]:
        risks = []
        risks.extend(self.interface_flaps(events))
        risks.extend(self.bgp_instability(events))
        risks.extend(self.cpu_risks(events))
        risks.extend(self.snmp_risks(events))
        risks.extend(self.thermal_risks(events))
        return sorted(risks, key=lambda r: (r["First_Seen"], r["Device"], r["Event"]))

    @staticmethod
    def _risk_row(device, event, detail, count, first_seen, last_seen, level, recommendation):
        return {
            "Device": device,
            "Event": event,
            "Event_Detail": detail,
            "Count": count,
            "First_Seen": first_seen,
            "Last_Seen": last_seen,
            "Risk_Level": level,
            "Recommendation": recommendation,
        }

    def interface_flaps(self, events):
        groups = defaultdict(list)
        for e in events:
            if e.event_category == "Interface":
                groups[(e.device, e.interface)].append(e)

        risks = []
        for (device, interface), items in groups.items():
            items.sort(key=lambda e: e.datetime)
            flaps = []
            pending_down = None

            for e in items:
                msg = e.message.lower()
                if "changed state to down" in msg:
                    pending_down = e
                elif "changed state to up" in msg and pending_down:
                    delta = e.datetime - pending_down.datetime
                    if delta <= timedelta(minutes=5):
                        flaps.append((pending_down, e, delta))
                    pending_down = None

            if not flaps:
                continue

            repeated = []
            for down, up, delta in flaps:
                count = sum(
                    1 for other_down, _, _ in flaps
                    if abs(other_down.datetime - down.datetime) <= timedelta(hours=1)
                )
                if count >= 2:
                    repeated.append((down, up, delta, count))

            if repeated:
                first = min((x[0] for x in repeated), key=lambda e: e.datetime)
                last = max((x[1] for x in repeated), key=lambda e: e.datetime)
                level = "Medium"
                detail = f"{interface}: {len(flaps)} flap(s), repeated >=2 within one hour"
                recommendation = "Investigate interface errors, cabling/optics, and link stability."
            else:
                first = flaps[0][0]
                last = flaps[-1][1]
                level = "Low"
                detail = f"{interface}: {len(flaps)} flap(s) detected"
                recommendation = "Monitor the interface and inspect error counters if flaps recur."

            risks.append(self._risk_row(
                device, "Interface Flap", detail, len(flaps),
                first.timestamp, last.timestamp, level, recommendation
            ))
        return risks

    def bgp_instability(self, events):
        groups = defaultdict(list)
        for e in events:
            if e.event_category == "BGP":
                groups[(e.device, e.bgp_neighbor)].append(e)

        risks = []
        for (device, neighbor), items in groups.items():
            items.sort(key=lambda e: e.datetime)
            downs = [e for e in items if "went down" in e.message.lower()]
            established = [e for e in items if "established" in e.message.lower()]
            pairs = []

            for down in downs:
                previous = [e for e in established if e.datetime <= down.datetime]
                if previous:
                    est = max(previous, key=lambda e: e.datetime)
                    delta = down.datetime - est.datetime
                    if delta <= timedelta(minutes=10):
                        pairs.append((est, down, delta))

            if pairs:
                first, last = pairs[0][0], pairs[-1][1]
                risks.append(self._risk_row(
                    device, "BGP Instability",
                    f"Neighbor {neighbor} established then went down within 10 minutes",
                    len(pairs), first.timestamp, last.timestamp, "High",
                    "Check BGP peer reachability, timers, route-policy changes, and link stability."
                ))

        by_day = defaultdict(list)
        for e in events:
            if e.event_category == "BGP" and "went down" in e.message.lower():
                by_day[(e.device, e.datetime.date())].append(e)

        for (device, day), downs in by_day.items():
            if len(downs) > 2:
                risks.append(self._risk_row(
                    device, "BGP Instability",
                    f"{len(downs)} BGP down events on {day.isoformat()}",
                    len(downs), downs[0].timestamp, downs[-1].timestamp, "High",
                    "Review BGP logs and peer stability; investigate repeated session resets."
                ))
        return risks

    def cpu_risks(self, events):
        spikes = [
            e for e in events
            if e.event_category == "CPU"
            and "exceeded" in e.message.lower()
            and e.numeric_threshold is not None
            and e.numeric_threshold > 80
        ]
        risks = []

        for e in spikes:
            if e.numeric_threshold >= 95:
                risks.append(self._risk_row(
                    e.device, "CPU Spike",
                    f"CPU utilization reached {e.numeric_threshold:g}%",
                    1, e.timestamp, e.timestamp, "Critical",
                    "Investigate CPU-consuming processes immediately and check capacity/traffic anomalies."
                ))

        by_device = defaultdict(list)
        for e in spikes:
            by_device[e.device].append(e)

        for device, items in by_device.items():
            items.sort(key=lambda e: e.datetime)
            for anchor in items:
                window = [e for e in items if abs(e.datetime - anchor.datetime) <= timedelta(hours=1)]
                if len(window) > 2:
                    risks.append(self._risk_row(
                        device, "CPU Spike",
                        f"{len(window)} CPU spikes >80% within one hour",
                        len(window), window[0].timestamp, window[-1].timestamp, "High",
                        "Investigate sustained CPU pressure and identify top CPU-consuming processes."
                    ))
                    break
        return risks

    def snmp_risks(self, events):
        groups = defaultdict(list)
        for e in events:
            if e.event_category == "SNMP/Security" and e.source_ip:
                groups[(e.device, e.source_ip)].append(e)

        risks = []
        for (device, source_ip), items in groups.items():
            items.sort(key=lambda e: e.datetime)
            if len(items) > 1:
                risks.append(self._risk_row(
                    device, "SNMP Authentication Failure",
                    f"Repeated authentication failures from {source_ip}",
                    len(items), items[0].timestamp, items[-1].timestamp, "High",
                    "Verify SNMP credentials/ACLs and investigate the source IP for unauthorized access attempts."
                ))
        return risks

    def thermal_risks(self, events):
        groups = defaultdict(list)
        for e in events:
            if e.event_category == "Thermal":
                sensor = re.search(r"sensor\s+(\d+)", e.message, re.I)
                key = (e.device, sensor.group(1) if sensor else "unknown")
                groups[key].append(e)

        risks = []
        for (device, sensor), items in groups.items():
            items.sort(key=lambda e: e.datetime)
            recoveries = []
            exceeded = None

            for e in items:
                msg = e.message.lower()
                if "exceeded threshold" in msg:
                    exceeded = e
                elif "returned to normal" in msg and exceeded:
                    recoveries.append((exceeded, e, e.datetime - exceeded.datetime))
                    exceeded = None

            if recoveries:
                avg_seconds = sum(x[2].total_seconds() for x in recoveries) / len(recoveries)
                risks.append(self._risk_row(
                    device, "Thermal Alarm",
                    f"Sensor {sensor}: {len(recoveries)} alarm(s), average recovery {avg_seconds:.1f}s",
                    len(recoveries), recoveries[0][0].timestamp, recoveries[-1][1].timestamp,
                    "Medium",
                    "Check cooling, airflow, fan/temperature sensor health, and environmental conditions."
                ))
        return risks
