#!/usr/bin/env python3

from cli import CLI
from database import Database
from detectors import RiskDetector
from parser import SyslogParser
from reporter import Reporter


def main():
    cli = CLI()
    args = cli.parse_args()

    events = SyslogParser(args.logs).parse()
    risks = RiskDetector().detect_all(events)

    Reporter(args.output).export(events, risks)
    Database(f"{args.output}/network_events.db").save(events, risks)

    filtered = cli.filter_events(events, args)

    if args.risk:
        filtered = [
            e for e in filtered
            if cli.risk_level_for_event(e, risks).lower() == args.risk.lower()
        ]

    file_count = len(list(__import__("pathlib").Path(args.logs).glob("*.log"))) +                  len(list(__import__("pathlib").Path(args.logs).glob("*.txt")))

    print(f"Parsed {len(events)} events from {file_count} log files.")
    print(f"Detected {len(risks)} summarized risk records.")

    if args.show or any([args.date, args.device, args.severity, args.category, args.risk]):
        cli.print_events(filtered, risks)
    else:
        print("Use --show or filters such as --device R1 --category CPU to inspect events.")


if __name__ == "__main__":
    main()
