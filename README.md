# Vodafone Technical Assessment

A multi-task technical assessment covering **Network Automation, Network Monitoring, Web Application Development, AI Integration, and Infrastructure Automation**.

This repository contains four independent tasks implemented as separate projects. Each task focuses on a specific technical area and includes its own source code, configuration files, documentation, and supporting artifacts.

# 📁 Repository Structure

```
vodafone-task/
│
├── AI_Prompt_Web_App_OpenRouter/
│
├── Ansible_Simple_SSH_Lab/
│
├── network syslog analytics/
│
└── network_audit_portal/
```

Each directory is an independent task and contains its own detailed README and implementation.

---

## 📋 Tasks Overview

| Task       | Project                  | Main Technologies         | Focus                                |
| ---------- | ------------------------ | ------------------------- | ------------------------------------ |
| **Task 1** | Network Syslog Analytics | Python, SQLite, CSV       | Log parsing & network risk detection |
| **Task 2** | Network Audit Portal     | Python, Flask, SQLite     | Network configuration auditing       |
| **Task 3** | AI Prompt Web App        | Python, Flask, OpenRouter | AI-powered prompt processing         |
| **Task 4** | Ansible Basics Lab       | Ansible, Docker, SSH      | Infrastructure automation            |

---

# 1. Network Syslog Analytics

### Overview

A Python-based network monitoring and analytics tool that processes router syslog files, normalizes network events, detects operational risks, stores the results in SQLite, and generates CSV reports.

### Key Features

* Parse router syslog files.
* Normalize raw network events.
* Extract:

  * Timestamp
  * Device
  * Severity
  * Event category
  * Interface
  * BGP neighbor
  * Source IP
  * CPU threshold
* Detect operational and security risks.
* Store normalized events in SQLite.
* Generate CSV reports.
* Filter events by:

  * Date
  * Device
  * Severity
  * Category
  * Risk level

### Risk Detection

The system detects several network conditions:

* **Interface Flapping**
* **BGP Instability**
* **High CPU Utilization**
* **SNMP Authentication Failures**
* **Thermal Alarms**
* **Security-related events**

CPU spikes above 80% are detected, while values at or above 95% are treated as critical. Interface flapping and BGP instability are evaluated using time-based rules.

### Architecture

```text
Raw Syslog Files
       │
       ▼
    Parser
       │
       ▼
 Event Model
       │
       ├──────────────► Risk Detector
       │                      │
       ▼                      ▼
    SQLite              Risk Analysis
       │
       ▼
 CSV Reports
```

### Project Structure

```text
network syslog analytics/
├── logs/
├── screenshots/
├── app.py
├── cli.py
├── parser.py
├── models.py
├── detectors.py
├── database.py
├── reporter.py
├── events.csv
├── risk_report.csv
├── network_events.db
├── NOTES.md
├── README.md
└── requirements.txt.
```

[View Task 1](./network%20syslog%20analytics/)

---

# 2. Network Audit Portal

### Overview

A Flask-based web application for auditing network configuration files from different vendors.

The portal allows network configuration and log files to be uploaded, parsed, validated, analyzed, and presented through a web dashboard.

### Supported Network Vendors

* Cisco
* Huawei
* Juniper

### Key Features

* Upload multiple configuration files.
* Process `.log` files.
* Extract network information including:

  * Hostname
  * Interfaces
  * IP addresses and subnets
  * Routing protocols
  * BGP neighbors
  * OSPF areas
  * ACL/security information
  * Loopback0
* Validate network configurations.
* Detect:

  * Missing Loopback0
  * Subnet overlaps
  * OSPF area inconsistencies
  * High-risk events
* Store data in SQLite.
* Dashboard with network analytics.
* Device-level drill-down.
* Search and filtering.
* CSV report export.

### Validation Workflow

```text
Configuration Files
        │
        ▼
     Upload
        │
        ▼
     Parsers
        │
        ▼
 Extract Network Data
        │
        ▼
    Validation
        │
   ┌────┼─────────────┐
   ▼    ▼             ▼
Loopback  Subnet    OSPF
Validation Overlap  Validation
        │
        ▼
    SQLite DB
        │
        ▼
    Dashboard
        │
        ▼
    CSV Export
```

### Dashboard

The dashboard provides:

* Configuration validation results.
* BGP vs OSPF visualization.
* Interfaces per device.
* Recent high-risk events.
* Search and filtering.
* Device drill-down.

### Project Structure

```text
network_audit_portal/
├── Screenshots/
├── exports/
├── parsers/
├── sample_configs/
├── static/
├── templates/
├── uploads/
├── validation/
├── app.py
├── database.py
├── exporter.py
├── models.py
├── schema.sql
├── .env.example
├── .gitignore
├── NOTES.md
├── README.md
└── requirements.txt
```

[View Task 2](./network_audit_portal/)

---

# 3. AI Prompt Web App — OpenRouter

### Overview

A lightweight Flask web application that allows users to submit AI prompts, select a prompt template, send the request to an AI provider, display the generated response, and maintain a searchable prompt history.

The application is designed with a configurable provider architecture and supports **OpenRouter as the primary AI provider**.

### Key Features

* Flask web application.
* Prompt submission interface.
* Prompt templates:

  * General
  * Explain
  * Summarize
  * Interview Answer
* OpenRouter integration.
* Gemini integration.
* OpenAI integration.
* Automatic provider fallback.
* Deterministic local mock mode.
* SQLite prompt history.
* History search.
* Input validation.
* Prompt length limits.
* Provider timeout handling.
* Automated tests using pytest.
* Environment-based API key management.

### AI Provider Architecture

```text
             User Prompt
                  │
                  ▼
             Flask App
                  │
                  ▼
          Prompt Validation
                  │
                  ▼
          Provider Selection
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   OpenRouter   Gemini     OpenAI
       │          │          │
       └──────────┼──────────┘
                  │
                  ▼
             AI Response
                  │
          ┌───────┴───────┐
          ▼               ▼
       Browser         SQLite
                      History
```

### Supported Provider Modes

```text
openrouter
gemini
openai
auto
mock
```

The default OpenRouter model is configurable through:

```env
OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

OpenRouter uses an OpenAI-compatible API, allowing the project to use the Python OpenAI SDK with OpenRouter's API endpoint.

### Mock Mode

The project includes a deterministic mock mode so the application can be tested without an API key or network connection.

```env
AI_PROVIDER=mock
```

This makes the project easier to review and test without requiring external credentials.

### Project Structure

```text
AI_Prompt_Web_App_OpenRouter/
├── screenshots/
├── services/
├── static/
├── templates/
├── tests/
├── app.py
├── prompt_history.db
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

[View Task 3](./AI_Prompt_Web_App_OpenRouter/)

---

# 4. Ansible Basics Lab

### Overview

A Docker-based infrastructure automation lab demonstrating basic **Ansible**, **SSH**, and **Linux system administration** concepts.

The environment contains one Ansible control machine and two Ubuntu-based target machines.

### Lab Architecture

```text
                 Docker Network
                       │
                       ▼
              ┌─────────────────┐
              │ Ansible Control │
              │    Container    │
              └────────┬────────┘
                       │
                 SSH / Ansible
                 ┌─────┴─────┐
                 ▼           ▼
          ┌───────────┐ ┌───────────┐
          │  Agent 1  │ │  Agent 2  │
          │  Ubuntu   │ │  Ubuntu   │
          └───────────┘ └───────────┘
```

### Containers

* `ansible-control` — Ansible control machine.
* `ansible-agent1` — Ubuntu target.
* `ansible-agent2` — Ubuntu target.

### Main Tasks

The Ansible playbook:

1. Gathers system facts.
2. Displays the hostname.
3. Displays the OS family.
4. Displays the IP address.
5. Displays system uptime.
6. Installs `curl`.
7. Creates `/tmp/ansible_lab`.
8. Copies a README file.
9. Checks whether the `sshd` process is running.
10. Demonstrates Ansible idempotence by running the playbook twice.

### Project Structure

```text
Ansible_Simple_SSH_Lab/
├── agent/
│   ├── Dockerfile
│   └── entrypoint.sh
├── control/
│   └── Dockerfile
├── lab/
│   ├── ansible.cfg
│   ├── inventory.ini
│   ├── basic_setup.yml
│   └── README.md
├── screenshots/
├── docker-compose.yml
├── .gitignore
└── README.md
```

[View Task 4](./Ansible_Simple_SSH_Lab/)

---

# 🛠️ Technologies Used

### Programming & Web

* Python
* Flask
* SQLite
* HTML
* CSS
* JavaScript

### AI

* OpenRouter
* OpenAI-compatible API
* Prompt Engineering
* Deterministic Mock Mode

### Networking

* Syslog
* Network Configuration Parsing
* BGP
* OSPF
* SNMP
* ACL/Security Analysis
* Network Risk Detection

### Automation & DevOps

* Ansible
* Docker
* Docker Compose
* SSH
* Linux

### Data & Reporting

* SQLite
* CSV
* Network Event Analytics
* Configuration Validation

---

# 📚 Task Documentation

Detailed documentation is available inside each task:

* [Task 1 — Network Syslog Analytics](./network%20syslog%20analytics/README.md)
* [Task 2 — Network Audit Portal](./network_audit_portal/README.md)
* [Task 3 — AI Prompt Web App](./AI_Prompt_Web_App_OpenRouter/README.md)
* [Task 4 — Ansible Basics Lab](./Ansible_Simple_SSH_Lab/README.md)

---

# 👤 Author

**Ahmed**

GitHub: [@ahmed1958](https://github.com/ahmed1958)

---

# 📄 License

This repository was created for technical assessment and demonstration purposes.
