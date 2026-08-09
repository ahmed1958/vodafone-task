import csv
from pathlib import Path

from models import Event


class Reporter:
    EVENT_FIELDS = [
        "Timestamp", "Device", "Severity", "Message", "Event_Category",
        "Interface", "BGP_Neighbor", "Source_IP", "Numeric_Threshold"
    ]

    RISK_FIELDS = [
        "Device", "Event", "Event_Detail", "Count",
        "First_Seen", "Last_Seen", "Risk_Level", "Recommendation"
    ]

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, events: list[Event], risks: list[dict]):
        self._export_events(events)
        self._export_risks(risks)

    def _export_events(self, events):
        with (self.output_dir / "events.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.EVENT_FIELDS)
            writer.writeheader()
            for e in events:
                writer.writerow({
                    "Timestamp": e.timestamp,
                    "Device": e.device,
                    "Severity": e.severity,
                    "Message": e.message,
                    "Event_Category": e.event_category,
                    "Interface": e.interface or "",
                    "BGP_Neighbor": e.bgp_neighbor or "",
                    "Source_IP": e.source_ip or "",
                    "Numeric_Threshold": "" if e.numeric_threshold is None else e.numeric_threshold,
                })

    def _export_risks(self, risks):
        with (self.output_dir / "risk_report.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.RISK_FIELDS)
            writer.writeheader()
            writer.writerows(risks)
