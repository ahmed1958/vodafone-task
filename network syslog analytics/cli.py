import argparse

from detectors import RiskDetector
from models import Event


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Network Syslog Analytics Tool")
        self.parser.add_argument("--logs", default="logs")
        self.parser.add_argument("--output", default=".")
        self.parser.add_argument("--date")
        self.parser.add_argument("--device")
        self.parser.add_argument("--severity")
        self.parser.add_argument(
            "--category",
            choices=["Interface", "BGP", "CPU", "Thermal", "SNMP/Security", "Other"]
        )
        self.parser.add_argument(
            "--risk",
            choices=["Low", "Medium", "High", "Critical"]
        )
        self.parser.add_argument("--show", action="store_true")

    def parse_args(self):
        return self.parser.parse_args()

    @staticmethod
    def filter_events(events: list[Event], args) -> list[Event]:
        result = events

        if args.date:
            result = [e for e in result if e.timestamp.startswith(args.date)]
        if args.device:
            result = [e for e in result if e.device.lower() == args.device.lower()]
        if args.severity:
            result = [e for e in result if e.severity.lower() == args.severity.lower()]
        if args.category:
            result = [e for e in result if e.event_category.lower() == args.category.lower()]

        return result

    @staticmethod
    def risk_level_for_event(event: Event, risks: list[dict]) -> str:
        matches = []
        for r in risks:
            if r["Device"] != event.device:
                continue
            if event.event_category == "Interface" and r["Event"] == "Interface Flap":
                matches.append(r["Risk_Level"])
            elif event.event_category == "BGP" and r["Event"] == "BGP Instability":
                matches.append(r["Risk_Level"])
            elif event.event_category == "CPU" and r["Event"] == "CPU Spike":
                if event.numeric_threshold and event.numeric_threshold > 80:
                    matches.append(r["Risk_Level"])
            elif event.event_category == "SNMP/Security" and r["Event"] == "SNMP Authentication Failure":
                matches.append(r["Risk_Level"])
            elif event.event_category == "Thermal" and r["Event"] == "Thermal Alarm":
                matches.append(r["Risk_Level"])

        order = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        return max(matches, key=lambda x: order[x], default="None")

    def print_events(self, events: list[Event], risks: list[dict]):
        print(f"\nMatched events: {len(events)}")
        print("-" * 110)
        print(f"{'Timestamp':19} {'Device':6} {'Severity':8} {'Category':15} {'Risk':8} Message")
        print("-" * 110)

        for e in events:
            risk = self.risk_level_for_event(e, risks)
            print(
                f"{e.timestamp:19} {e.device:6} {e.severity:8} "
                f"{e.event_category:15} {risk:8} {e.message}"
            )
