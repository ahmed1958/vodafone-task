import sqlite3
from pathlib import Path

from models import Event


class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def initialize(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                event_category TEXT NOT NULL,
                interface TEXT,
                bgp_neighbor TEXT,
                source_ip TEXT,
                numeric_threshold REAL
            );

            CREATE TABLE IF NOT EXISTS risk_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT NOT NULL,
                event TEXT NOT NULL,
                event_detail TEXT NOT NULL,
                count INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                recommendation TEXT NOT NULL
            );
        """)
        conn.close()

    def save(self, events: list[Event], risks: list[dict]):
        self.initialize()
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM risk_summary")

        conn.executemany("""
            INSERT INTO events
            (timestamp, device, severity, message, event_category, interface,
             bgp_neighbor, source_ip, numeric_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (e.timestamp, e.device, e.severity, e.message, e.event_category,
             e.interface, e.bgp_neighbor, e.source_ip, e.numeric_threshold)
            for e in events
        ])

        conn.executemany("""
            INSERT INTO risk_summary
            (device, event, event_detail, count, first_seen, last_seen,
             risk_level, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r["Device"], r["Event"], r["Event_Detail"], r["Count"],
             r["First_Seen"], r["Last_Seen"], r["Risk_Level"], r["Recommendation"])
            for r in risks
        ])
        conn.commit()
        conn.close()
