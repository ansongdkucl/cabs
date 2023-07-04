import csv
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command

# Initialize Nornir with the host file
nr = InitNornir(config_file='/home/ansongdk/scripts/inventory/config.yaml')
#nr = InitNornir(config_file='/home/ansongdk/scripts/vlans/config.yaml')

# Define the MAC addresses you want to check
mac_addresses = ["2829.86", "00c0.b7"]

# List to store the hosts that do not match the pattern
non_matching_hosts = []

def check_mac(task):
    # Retrieve the hostname and IP address of the current host
    hostname = task.host.hostname
    ip = task.host.hostname

    # Retrieve the Building, Cab, and SNMP location information from the inventory
    building = task.host.get("building", "N/A")
    cab = task.host.get("cab", "N/A")

    # Execute the "show snmp location" command on the current host
    cmd = "show snmp location"
    result = task.run(task=netmiko_send_command, command_string=cmd, enable=True)

    # Extract the SNMP location from the command output
    snmp_location = result[0].result.strip()

    # Execute the "show mac address-table" command on the current host
    cmd = "show mac address-table"
    result = task.run(task=netmiko_send_command, command_string=cmd, enable=True)

    # Check if any MAC address matches the specified patterns
    mac_address_table = result[0].result
    mac_found = False
    for entry in mac_address_table.splitlines():
        if "Gi" not in entry and "Fa" not in entry:
            continue  # Skip trunk ports
        for mac_address in mac_addresses:
            if mac_address in entry:
                mac_found = True
                # Extract the interface and MAC address from the entry
                parts = entry.split()
                interface = parts[1]
                mac = parts[2]
                break
        if mac_found:
            break

    # Save the result
    if not mac_found:
        non_matching_hosts.append((hostname, building, cab, snmp_location))

    # Print the host and interface information where a match is found
    if mac_found:
        print(f"MAC address matching the pattern found on {hostname} ({ip})")
        print(f"Building: {building}")
        print(f"Cab: {cab}")
        print(f"SNMP Location: {snmp_location}")
        print(f"Interface: {interface}")
        print(f"MAC Address: {mac}")
        print("-" * 30)

# Run the task on all hosts
result = nr.run(task=check_mac)

# Print the non-matching hosts to the screen
print("Hosts without matching MAC address pattern:")
for host in non_matching_hosts:
    print(host)

# Save the non-matching hosts to the CSV report
with open("report.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Hostname", "Building", "Cab", "SNMP Location"])
    for host in non_matching_hosts:
        writer.writerow(host)
