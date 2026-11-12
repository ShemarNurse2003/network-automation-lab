from datetime import date
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

def run_compliance_checks(running_config, device_name):
    """Print PASS/FAIL for each required config line."""
    for description, required_text in compliance_checks:
        required_text = required_text.format(name=device_name)
        status = "PASS" if required_text in running_config else "FAIL"
        print(f"  [{status}] {description}")

def audit_device(device, credentials):
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
            run_compliance_checks(config_text, device["name"])
    except NetmikoAuthenticationException:
        print("  login failed. Check username and password.")
    except NetmikoTimeoutException:
        print("  unreachable. Check the device is up and the port is right.")

if __name__ == "__main__":
    inventory = load_inventory(INVENTORY_FILE)
    for device in inventory["devices"]:
        audit_device(device, inventory["credentials"])