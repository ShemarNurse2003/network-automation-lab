from datetime import date, datetime
import pandas as pd
from pathlib import Path

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

INVENTORY_FILE = "inventory.yml"

# Each check: (description, text that must appear in the config)
compliance_checks = [
    ("Hostname matches device name", "hostname {name}"),
    ("Logging to syslog is configured", "log syslog"),
    ("Password encryption is enabled", "service password-encryption"),
]

def load_inventory(path):
    """Read devices and credentials from the YAML inventory."""
    with open(path) as inventory_file:
        return yaml.safe_load(inventory_file)

def backup_config(connection, device_name):
    """Pull the running config and save it with today's date."""
    running_config = connection.send_command('vtysh -c "show running-config"')
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"{device_name}_{date.today()}.txt"
    backup_file.write_text(running_config)
    print(f"  Backup saved: {backup_file}")
    return running_config

def run_compliance_checks(running_config, device_name, report_rows):
    """Print PASS/FAIL for each check and record it for the CSV report."""
    for description, required_text in compliance_checks:
        required_text = required_text.format(name=device_name)
        status = "PASS" if required_text in running_config else "FAIL"
        print(f"  [{status}] {description}")
        report_rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device_name,
            "check": description,
            "status": status,
        })

def audit_device(device, credentials, report_rows):
    """Connect to one device, back it up, and run the checks."""
    print(f"\n{device['name']}")
    connection_details = {
        "device_type": "linux",
        "host": device["host"],
        "port": device["port"],
        "username": credentials["username"],
        "password": credentials["password"],
    }
    try:
        with ConnectHandler(**connection_details) as connection:
            config_text = backup_config(connection, device["name"])
            run_compliance_checks(config_text, device["name"], report_rows)
    except NetmikoAuthenticationException:
        print("  login failed. Check username and password.")
        report_rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device["name"], "check": "Connection", "status": "LOGIN FAILED",
        })
    except NetmikoTimeoutException:
        print("  unreachable. Check the device is up and the port is right.")
        report_rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device["name"], "check": "Connection", "status": "UNREACHABLE",
        })
        
def save_report(report_rows):
    """Write all results to a dated CSV file with pandas."""
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"compliance_{date.today()}.csv"
    report_dataframe = pd.DataFrame(report_rows)
    report_dataframe.to_csv(report_file, index=False)
    pass_rate = (report_dataframe["status"] == "PASS").mean() * 100
    print(f"\nReport saved: {report_file} ({pass_rate:.0f}% of checks passed)")


if __name__ == "__main__":
    inventory = load_inventory(INVENTORY_FILE)
    report_rows = []
    for device in inventory["devices"]:
        audit_device(device, inventory["credentials"], report_rows)
    save_report(report_rows)