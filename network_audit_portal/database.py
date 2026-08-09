import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
 id INTEGER PRIMARY KEY, hostname TEXT UNIQUE, vendor TEXT, loopback0 INTEGER, loopback_ip TEXT, router_id TEXT
);
CREATE TABLE IF NOT EXISTS interfaces (
 id INTEGER PRIMARY KEY, device_id INTEGER, name TEXT, ip_address TEXT, subnet TEXT, description TEXT, loopback INTEGER
);
CREATE TABLE IF NOT EXISTS routing_protocols (
 id INTEGER PRIMARY KEY, device_id INTEGER, protocol TEXT, area TEXT
);
CREATE TABLE IF NOT EXISTS bgp_neighbors (
 id INTEGER PRIMARY KEY, device_id INTEGER, neighbor TEXT
);
CREATE TABLE IF NOT EXISTS acl_rules (
 id INTEGER PRIMARY KEY, device_id INTEGER, rule_name TEXT
);
CREATE TABLE IF NOT EXISTS log_events (
 id INTEGER PRIMARY KEY, timestamp TEXT, device TEXT, severity TEXT, message TEXT, category TEXT, risk_level TEXT
);
CREATE TABLE IF NOT EXISTS validation_results (
 id INTEGER PRIMARY KEY, device TEXT, rule_name TEXT, status TEXT, details TEXT
);
"""

class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def initialize(self):
        with self.connect() as c: c.executescript(SCHEMA)

    def replace_all(self, devices, events, validations):
        self.initialize()
        with self.connect() as c:
            for table in ["interfaces","routing_protocols","bgp_neighbors","acl_rules","devices","log_events","validation_results"]:
                c.execute(f"DELETE FROM {table}")
            for d in devices:
                cur=c.execute("INSERT INTO devices(hostname,vendor,loopback0,loopback_ip,router_id) VALUES(?,?,?,?,?)",(d.hostname,d.vendor,int(d.loopback0),d.loopback_ip,d.router_id))
                did=cur.lastrowid
                for i in d.interfaces:
                    c.execute("INSERT INTO interfaces(device_id,name,ip_address,subnet,description,loopback) VALUES(?,?,?,?,?,?)",(did,i.name,i.ip_address,i.subnet,i.description,int(i.loopback)))
                for p in d.routing_protocols:
                    areas=d.ospf_areas if p=="OSPF" else [None]
                    for area in areas or [None]:
                        c.execute("INSERT INTO routing_protocols(device_id,protocol,area) VALUES(?,?,?)",(did,p,area))
                for n in d.bgp_neighbors: c.execute("INSERT INTO bgp_neighbors(device_id,neighbor) VALUES(?,?)",(did,n))
                for r in d.acl_rules: c.execute("INSERT INTO acl_rules(device_id,rule_name) VALUES(?,?)",(did,r))
            for e in events:
                c.execute("INSERT INTO log_events(timestamp,device,severity,message,category,risk_level) VALUES(?,?,?,?,?,?)",(e.timestamp,e.device,e.severity,e.message,e.category,e.risk_level))
            for host,rule,status,details in validations:
                c.execute("INSERT INTO validation_results(device,rule_name,status,details) VALUES(?,?,?,?)",(host,rule,status,details))

    def dashboard_data(self, filters=None):
        with self.connect() as c:
            devices=c.execute("SELECT * FROM devices ORDER BY hostname").fetchall()
            validations=c.execute("SELECT * FROM validation_results ORDER BY id DESC").fetchall()
            events=c.execute("SELECT * FROM log_events WHERE risk_level IN ('High','Critical') ORDER BY timestamp DESC LIMIT 20").fetchall()
            counts=c.execute("SELECT d.hostname, COUNT(i.id) count FROM devices d LEFT JOIN interfaces i ON i.device_id=d.id GROUP BY d.id ORDER BY d.hostname").fetchall()
            protocols=c.execute("SELECT protocol, COUNT(DISTINCT device_id) count FROM routing_protocols GROUP BY protocol").fetchall()
        return devices, validations, events, counts, protocols

    def device(self, hostname):
        with self.connect() as c:
            d=c.execute("SELECT * FROM devices WHERE hostname=?", (hostname,)).fetchone()
            if not d: return None
            did=d["id"]
            interfaces=c.execute("SELECT * FROM interfaces WHERE device_id=?", (did,)).fetchall()
            protocols=c.execute("SELECT * FROM routing_protocols WHERE device_id=?", (did,)).fetchall()
            neighbors=c.execute("SELECT * FROM bgp_neighbors WHERE device_id=?", (did,)).fetchall()
            acls=c.execute("SELECT * FROM acl_rules WHERE device_id=?", (did,)).fetchall()
            validations=c.execute("SELECT * FROM validation_results WHERE device=?", (hostname,)).fetchall()
            events=c.execute("SELECT * FROM log_events WHERE device=? ORDER BY timestamp DESC LIMIT 50",(hostname,)).fetchall()
            return d,interfaces,protocols,neighbors,acls,validations,events