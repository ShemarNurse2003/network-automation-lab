# Network Automation Lab

A Python script that logs into routers over SSH, backs up each running config, and checks it against a short compliance baseline. I built it to practice a task network teams do all the time: config backups plus audit checks.

## What it does

- Reads the list of devices and the login details from `inventory.yml`
- Connects to each FRRouting router (running in Docker) with Netmiko
- Saves each running config to `backups/<device>_<date>.txt`
- Prints PASS/FAIL for each compliance check
- If a router is down or the login fails, it prints one clear line and moves on to the next device

## Sample output

```
router1
  Backup saved: backups/router1_2026-11-12.txt
  [PASS] Hostname matches device name
  [PASS] Logging to syslog is configured
  [PASS] Password encryption is enabled

router2
  unreachable. Check the device is up and the port is right.
```

## How the script evolved

- **Version 1:** one hardcoded router. Log in, run `show running-config`, save the backup, print PASS/FAIL.
- **Version 2:** added error handling. A wrong password raises an authentication error (the device answered, the login was rejected). A wrong port or stopped container raises a timeout (nothing answered). Both now print a short message instead of a traceback.
- **Version 3:** replaced a check that could never pass. FRR 8.4 doesn't show banners in the running config, so the banner check failed no matter what I configured. I confirmed that by grepping the live config, then swapped in a `service password-encryption` check.
- **Version 4:** moved devices and credentials into `inventory.yml` and wrapped each router's work in an `audit_device()` function. The hostname check fills in each device's own name, so every router is checked against itself.

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

Wait about 10 seconds for SSH to start. Then configure each router so the checks can pass, using `router1` first and `router2` second:

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
| `docker-compose.yml` | Starts router1 (port 2222) and router2 (port 2223) |
| `start.sh` | Starts SSH, then FRR |
| `inventory.yml` | Devices and lab login details |
| `backup_and_audit.py` | Backup and compliance script |

## Lessons learned

- Auth failure means the device was reached but the login was rejected. A timeout means it was unreachable. They are different problems with different fixes.
- A compliance check has to match what the device really prints. Check it against real output before trusting it.
- Keeping devices in a data file instead of the code makes the script reusable.

## Roadmap

- CSV compliance report with pandas
- Pass-rate chart per device
- Config changes pushed with Jinja2 templates

## Lab credentials

The password in `inventory.yml` (`labpass123`) is for local throwaway containers only. Never commit real device credentials.