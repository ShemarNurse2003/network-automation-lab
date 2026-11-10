# Network Automation Lab

Python script that logs into a router over SSH, backs up its running config, and checks it against a compliance baseline. Built to mirror a routine network-team task: config backups plus audit checks.

## What it does

- Connects to an FRRouting router in a Docker container using Netmiko
- Saves the running config to `backups/<device>_<date>.txt`
- Runs PASS/FAIL checks against the config
- Handles login failures and unreachable devices with clear one-line messages

## Sample output

```
Backup saved: backups/router1_2026-11-10.txt

Compliance report
  [PASS] Hostname is set to router1
  [PASS] Logging to syslog is configured
  [PASS] Password encryption is enabled
```

## Requirements

- macOS or Linux
- Docker Desktop
- Python 3.9+

## Setup

```bash
git clone https://github.com/ShemarNurse2003/network-automation-lab.git
cd network-automation-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d --build
```

Wait about 10 seconds for SSH to start, then configure the router so the checks pass:

```bash
docker exec -it router1 vtysh
```

```
configure terminal
log syslog
service password-encryption
end
write memory
exit
```

## Run

```bash
python backup_and_audit.py
```

## Project files

| File | Purpose |
|------|---------|
| `Dockerfile` | FRR router image with SSH added |
| `docker-compose.yml` | Starts router1 on port 2222 |
| `start.sh` | Starts SSH, then FRR |
| `backup_and_audit.py` | Backup and compliance script |

## Lessons learned

- Auth failure means the device was reached but credentials were rejected. Timeout means it was unreachable.
- A compliance check must match what the device really prints. My first banner check could never pass because FRR 8.4 doesn't show banners in the running config.

## Roadmap

- Multiple routers from a YAML inventory
- CSV compliance report with pandas
- Config changes pushed with Jinja2 templates

## Lab credentials

Lab-only credentials (`labpass123`) for a local container. Never reuse them on real devices.