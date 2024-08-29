#!/usr/bin/env python3

import sys
import os
import re
import time
import argparse
import shutil

def backup_file(original_file):
    timestamp = time.strftime('%Y%m%d%H%M%S')
    backup_filename = f"{original_file}-{timestamp}"
    try:
        shutil.copy2(original_file, backup_filename)
        return backup_filename
    except OSError as e:
        print(f"Error: Could not create backup file '{backup_filename}': {e}")
        sys.exit(1)

def prune_leases(input_file, mac_addresses):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    new_lines = []
    skip_lease = False
    current_lease = []
    removed_lease_count = 0

    for line in lines:
        if line.startswith('lease'):
            skip_lease = False
            current_lease = []

        current_lease.append(line)

        if line.strip().startswith('hardware ethernet'):
            lease_mac = line.split()[2].strip(';')
            if lease_mac in mac_addresses:
                skip_lease = True

        if line.strip() == '}':
            if skip_lease:
                removed_lease_count += 1
            else:
                new_lines.extend(current_lease)
            current_lease = []  # Reset after processing each lease block

    return new_lines, removed_lease_count

def main():
    parser = argparse.ArgumentParser(description="Prune DHCP leases by MAC address.")
    parser.add_argument('-i', '--input', help="Input dhcpd.leases file path", default='dhcpd.leases')
    parser.add_argument('mac_addresses', nargs='*', help="List of MAC addresses to prune")

    args = parser.parse_args()

    # If no MAC addresses are provided, read from stdin
    if not args.mac_addresses:
        args.mac_addresses = [line.strip() for line in sys.stdin]

    if not os.path.exists(args.input):
        print(f"Error: The file '{args.input}' does not exist.")
        sys.exit(1)

    # Backup the original file
    backup_filename = backup_file(args.input)

    # Prune leases based on MAC addresses and get the count of removed leases
    pruned_leases, removed_lease_count = prune_leases(args.input, args.mac_addresses)

    # Write the new leases to the original file
    with open(args.input, 'w') as file:
        file.writelines(pruned_leases)

    print(f"Successfully pruned {removed_lease_count} lease(s). Original file backed up as '{backup_filename}'.")

if __name__ == '__main__':
    main()
