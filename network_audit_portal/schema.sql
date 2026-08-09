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