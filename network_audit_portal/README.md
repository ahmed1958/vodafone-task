# Network Audit Portal — Task 2

Independent Flask implementation for the Multi-Service Flask Platform for Network Audit, Analytics & File Distribution assessment.

## Features

* Upload multiple Cisco, Huawei, Juniper configuration files and `.log` files.
* Extract hostname, interfaces, IPs/subnets, routing protocols, BGP neighbors, OSPF areas, ACL/security names, and Loopback0.
* Validate Loopback0 presence, subnet overlap, OSPF area consistency, and expose high-risk logs.
* SQLite persistence.
* Dashboard with validation table, BGP vs OSPF chart, interfaces/device chart, and recent high-risk events.
* Search/filter by hostname, protocol, validation status, and risk.
* Device drill-down.
* CSV export.
* Configuration through `.env`.

## Requirements

* Python 3
* `python3-venv`
* pip

On Ubuntu/Debian, if virtual environments are not available:

```bash
sudo apt update
sudo apt install python3-venv
```

## Setup

Clone the repository and enter the Task 2 directory:

```bash
cd task2-network-audit
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Review the values in `.env`, then start the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Environment Variables

The application uses a `.env` file for configurable values instead of hardcoding configuration in the source code.

Create `.env` from the provided example:

```bash
cp .env.example .env
```

The `.env` file contains the following configuration:

```env
SECRET_KEY=change-this-secret-key
DATABASE_URL=sqlite:///network_audit.db
UPLOAD_FOLDER=uploads
EXPORT_FOLDER=exports
```

### `SECRET_KEY`

Used by Flask for application security and session-related functionality.

For local development, you can use any random value:

```env
SECRET_KEY=change-this-secret-key
```

For a real deployment, use a strong randomly generated secret and **do not commit it to Git**.

### `DATABASE_URL`

Defines the database used by the application.

The default configuration uses SQLite:

```env
DATABASE_URL=sqlite:///network_audit.db
```

The project is designed to use SQLite for the assessment and does not require an external database server.

### `UPLOAD_FOLDER`

Defines where uploaded configuration and log files are stored:

```env
UPLOAD_FOLDER=uploads
```

The application reads uploaded configuration files and `.log` files from this location when processing the data.

### `EXPORT_FOLDER`

Defines where generated CSV reports are stored:

```env
EXPORT_FOLDER=exports
```

Generated validation/risk reports are written to this directory.

## Sample configuration data

The `sample_configs/` directory contains the seven supplied assessment configuration files. Upload them from `/upload` to populate the dashboard.

The supplied samples demonstrate deliberate validation cases. For example, R6 is explicitly described as missing Loopback0, overlapping with R2/R3, and having an OSPF area mismatch. R7 is described as having a duplicate router-id/loopback IP and an overlapping R4-R5 subnet.

## Log assumptions

Task 2 uses the same normalized log format as Task 1:

```text
YYYY-MM-DD HH:MM:SS DEVICE SEVERITY MESSAGE
```

Only `.log` files are ingested from the upload directory.

## Configuration assumptions

* Cisco uses `hostname`, `interface`, `router ospf`, `router bgp`, `neighbor ... remote-as`, and ACL syntax.
* Huawei uses `sysname`, `interface`, `ospf`, `bgp`, `peer ... as-number`, and `acl number`.
* Juniper uses the supplied brace-based `system/interfaces/protocols/policy-options/firewall` syntax.
* `LoopBack0` on Cisco/Huawei and `lo0` on Juniper are treated as the Loopback0 concept.
* The supplied configs do not define a common BGP "area"; therefore BGP validation is limited to visibility/declared protocol rather than inventing an area rule.
* OSPF area consistency is checked from explicitly declared areas.
* Subnet overlap uses IPv4 network overlap semantics.
* The source files themselves contain problem descriptions; the parser treats them as configuration text and does not rely on those comments to generate validation results.

## Routes

* `/upload` — upload and parse files.
* `/dashboard` — audit summary and filters.
* `/device/<hostname>` — device drill-down.
* `/export` — validation CSV.
* `/ingest` — reprocess currently uploaded files.

## Project Structure

```text
task2-network-audit/
├── app.py
├── database.py
├── models.py
├── exporter.py
├── schema.sql
├── requirements.txt
├── .env.example
├── parsers/
│   ├── config_parser.py
│   └── log_parser.py
├── validation/
│   └── validator.py
├── templates/
├── static/
├── sample_configs/
├── uploads/
└── exports/
```
