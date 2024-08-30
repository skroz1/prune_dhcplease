# ISC DHCPD Lease Management Scripts

lint and prune/purge dhcpd.leases files for ISC DHCPD (tested against version 3.0)

## Scripts

### 1. `dhcpdlint.py`

**Description:**  
Simple linting tool for DHCP lease files.  Currently checks for leases that are in the `free` state and validates the file structure only.  This script is not yet ready to be trusted.

**Usage:**

```bash
./dhcpdlint.py [optional path to dhcpd.leases]
```

- By default check the `dhcpd.leases` file in the current working directory.

### 2. `prune_dhcpleases.py`

**Description:**  
Originally built to remove leases given one or more MAC addresses, this script can also purge expired or duplicate leases.  This functinoality has VERY limited testing and the output should be tested thoroughly before use.  

**Usage:**

```bash
./prune_dhcpleases.py [-i dhcpd.leases] [-p] [MAC addresses]
```

- `-i`: Specify the input `dhcpd.leases` file path (defaults to `dhcpd.leases` in the current directory).
- `-p`/`--purge`: Purge expired leases and remove duplicates (based on the most recent start date).
- `[MAC addresses]`: A list of MAC addresses to prune. If not provided, MAC addresses can be read from STDIN.


## Requirements

- Python 3.9

## License

This project is licensed under the MIT License.
