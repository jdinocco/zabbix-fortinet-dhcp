# Zabbix Template Firewall Fortinet DHCP

Zabbix template for monitoring the DHCP pools utilization.

## Zabbix Data

### Items

- DHCP Raw [External check]: Get raw json data for the pools utilization
- DHCP Pool {#POOL} ({#NET}) Lease [Discovered/Dependent Item]: Get data from "DCHP Raw" and filter by vlan (pool) using JSONPath
- DHCP Pool {#POOL} ({#NET}) Utilzation [Discovered/Calculated]: Get pool utilization using "DHCP Pool {#POOL} ({#NET}) Lease" and total host available ({#TOTAL}) from the discover

### Triggers

- DHCP Pool ({#POOL}) UTILIZATION >80% on {HOST.NAME} [Severity: Average]
- DHCP Pool ({#POOL}) UTILIZATION >90% on {HOST.NAME} [Severity High]

## Features

- Using Python in Discovery for parsing the pool name, from address and netmask of the interface vlan get the network and total available hosts
- Using JSONPath for Raw data extraction

## Requirements

- Python >= 3.8
- Zabbix >= 5.0

## Installation

- Clone the repo

- Install the python libraries

```bash
pip install -r requirements.txt
```

- Copy file "**fortinet-dhcp-py**" to your server or proxy externalscript folder (usually on /usr/lib/zabbix/externalscripts/)

```bash
cp -p fortinet-dhcp-py /usr/lib/zabbix/externalscripts/
chmod +x fortinet-dhcp.py
```

- Run a smoke test, you need to pass as argument the "action", host ipaddress, cli-user, cli-user-password (this is necessary for make sure that you have all dependencies)

```bash
./fortinet-dhcp.py discover 10.20.30.40 testmonitoring M0n1t0r1ngP4$$
{"data":[{"{#NET}":"10.14.136.32/28","{#TOTAL}":"13","{#POOL}":"vlan10"},{"{#NET}":"10.14.200.0/234","{#TOTAL}":"253","{#POOL}":"vlan20"}]}
```

```bash
./fortinet-dhcp.py lease 10.20.30.40 testmonitoring M0n1t0r1ngP4$$
{"vlan10": 2, "vlan20": 60}
```

- Import the template on Zabbix Server and enjoy! ;)

## Known Issues

- The smoke test it is necessary to do it before importing and assigning the template to a host, otherwise you will probably have errors when executing the Python script.
- The pool usage item may throw errors or change to the unsupported state when it is assigned to a host for the first time, this is because it may not yet have all the parameters to perform the calculation. After a few minutes it should normalize.
