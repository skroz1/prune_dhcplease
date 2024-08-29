#!/usr/bin/env python3

import sys
import os
import re
import time
import argparse
import shutil
from datetime import datetime

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

def purge_leases(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    new_lines = []
    current_lease = []
    leases_by_mac = {}
    removed_lease_count = 0
    now = datetime.utcnow()

    for line in lines:
        if line.startswith('lease'):
            if current_lease:
                mac = extract_mac_address(current_lease)
                ends = extract_end_date(current_lease)
                if mac and ends and ends < now:
                    # Remove expired leases
                    removed_lease_count += 1
                elif mac:
                    # Save non-expired lease to dictionary
                    if mac not in leases_by_mac:
                        leases_by_mac[mac] = []
                    leases_by_mac[mac].append(current_lease)
                else:
                    new_lines.extend(current_lease)
            current_lease = []
        
        current_lease.append(line)

        if line.strip() == '}':
            mac = extract_mac_address(current_lease)
            ends = extract_end_date(current_lease)
            if mac and ends and ends < now:
                # Remove expired leases
                removed_lease_count += 1
            elif mac:
                if mac not in leases_by_mac:
                    leases_by_mac[mac] = []
                leases_by_mac[mac].append(current_lease)
            else:
                new_lines.extend(current_lease)
            current_lease = []

    # Process leases by MAC
    for mac, leases in leases_by_mac.items():
        if len(leases) > 1:
            # Sort by start date, keeping the most recent
            leases.sort(key=lambda l: extract_start_date(l), reverse=True)
            new_lines.extend(leases[0])
            removed_lease_count += len(leases) - 1
        elif len(leases) == 1:
            new_lines.extend(leases[0])

    return new_lines, removed_lease_count

def extract_mac_address(lease):
    for line in lease:
        if line.strip().startswith('hardware ethernet'):
            return line.split()[2].strip(';')
    return None

def extract_start_date(lease):
    for line in lease:
        if line.strip().startswith('starts'):
            parts = line.split()
            date_time_str = f"{parts[2]} {parts[3].strip(';')}"  # Remove the trailing semicolon
            return datetime.strptime(date_time_str, "%Y/%m/%d %H:%M:%S")
    return None

def extract_end_date(lease):
    for line in lease:
        if line.strip().startswith('ends'):
            parts = line.split()
            date_time_str = f"{parts[2]} {parts[3].strip(';')}"  # Remove the trailing semicolon
            return datetime.strptime(date_time_str, "%Y/%m/%d %H:%M:%S")
    return None

def main():
    parser = argparse.ArgumentParser(description="Prune or purge DHCP leases.")
    parser.add_argument('-i', '--input', help="Input dhcpd.leases file path", default='dhcpd.leases')
    parser.add_argument('-p', '--purge', action='store_true', help="Purge expired leases and duplicates")
    parser.add_argument('mac_addresses', nargs='*', help="List of MAC addresses to prune")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: The file '{args.input}' does not exist.")
        sys.exit(1)

    # Backup the original file
    backup_filename = backup_file(args.input)

    if args.purge:
        # Purge expired and duplicate leases
        pruned_leases, removed_lease_count = purge_leases(args.input)
    else:
        # Prune leases based on MAC addresses
        if not args.mac_addresses:
            args.mac_addresses = [line.strip() for line in sys.stdin]
        pruned_leases, removed_lease_count = prune_leases(args.input, args.mac_addresses)

    # Write the pruned or purged leases to the original file
    with open(args.input, 'w') as file:
        file.writelines(pruned_leases)

    print(f"Successfully removed {removed_lease_count} lease(s). Original file backed up as '{backup_filename}'.")

if __name__ == '__main__':
    main()
