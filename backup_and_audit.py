from datetime import date
from pathlib import Path
from netmiko import ConnectHandler

# Lab device details (matches docker-compose.yml)
router_connection = {
    "device_type": "linux",
    "host": "127.0.0.1",
    "port": 2222,
    "username": "root",
    "password": "labpass123",
}

# Each check: (description, text that must appear in the config)
compliance_checks = [
    ("Hostname is set to router1", "hostname router1"),
    ("Logging to syslog is configured", "log syslog"),
    ("Banner is configured", "banner motd"),
]

def backup_config(connection, device_name):
    """Pull the running config and save it with today's date."""
    running_config = connection.send_command('vtysh -c "show running-config"')
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"{device_name}_{date.today()}.txt"
    backup_file.write_text(running_config)
    print(f"Backup saved: {backup_file}")
    return running_config

def run_compliance_checks(running_config):
    """Print PASS/FAIL for each required config line."""
    print("\nCompliance report")
    for description, required_text in compliance_checks:
        status = "PASS" if required_text in running_config else "FAIL"
        print(f"  [{status}] {description}")

if __name__ == "__main__":
    with ConnectHandler(**router_connection) as connection:
        config_text = backup_config(connection, "router1")
        run_compliance_checks(config_text)
