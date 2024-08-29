#!/usr/bin/env python3

# sfc 2024-08-29

import os
import sys
import re

class DhcpdLeasesParser:
    def __init__(self, filename='dhcpd.leases'):
        self.filename = filename
        self.leases = []

    def parse(self):
        with open(self.filename, 'r') as file:
            lease = {}
            for line in file:
                line = line.strip()

                if line.startswith('lease'):
                    lease = {}
                    lease['ip_address'] = line.split()[1]
                elif line.startswith('starts'):
                    lease['starts'] = self._parse_date_time(line)
                elif line.startswith('ends'):
                    lease['ends'] = self._parse_date_time(line)
                elif line.startswith('hardware ethernet'):
                    lease['mac_address'] = line.split()[2].strip(';')
                elif line.startswith('client-hostname'):
                    lease['client_hostname'] = line.split()[1].strip('";')
                elif line.startswith('binding state'):
                    lease['binding_state'] = line.split()[2].strip(';')
                elif line == '}':
                    self.leases.append(lease)

    def _parse_date_time(self, line):
        # Example line: "starts 2 2021/04/29 18:06:39;"
        parts = line.split()
        return f"{parts[1]} {parts[2]} {parts[3].strip(';')}"

    def get_leases(self):
        return self.leases

def main():
    # Determine the filename to parse
    filename = 'dhcpd.leases'
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' does not exist.")
        sys.exit(1)

    # Parse the leases file
    parser = DhcpdLeasesParser(filename)
    parser.parse()

    # Output the parsed leases (or perform linting checks)
    leases = parser.get_leases()

    # Example check: Ensure no leases are in the 'free' state
    for lease in leases:
        if lease.get('binding_state') == 'free':
            print(f"Warning: Lease for {lease['ip_address']} is in 'free' state.")

if __name__ == '__main__':
    main()
