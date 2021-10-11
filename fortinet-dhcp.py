#!/usr/bin/env python3

from netmiko import ConnectHandler
from ttp import ttp
import sys
import json
import ipaddress
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from collections import Counter

action = sys.argv[1]
host = sys.argv[2]
user = sys.argv[3]
passwd = sys.argv[4]


def run():
    if action == 'discover':
        dhcp_discover()

    elif action == 'lease':
        dhcp_lease()

    else:
        exit


def dhcp_discover(host=host, user=user, passwd=passwd):
    fortigate = {
        'device_type': 'fortinet',
        'host': host,
        'username': user,
        'password': passwd,
        'fast_cli': True
    }
    conn = ConnectHandler(**fortigate)

    output = conn.send_command("show system dhcp server")

    ttp_template = """
        set default-gateway {{ net }}
        set netmask {{ netmask }}
        set interface "{{ vlan }}"
        """
    parser = ttp(data=output, template=ttp_template)
    parser.parse()

    results = parser.result(format='json')[0]
    format = results.lstrip("[").rstrip("]")

    data = json.loads(format)

    var = ''

    for line in data:
        net = ipaddress.ip_network(
            line['net'] + '/' + line['netmask'], strict=False)
        total = ipaddress.ip_network(net, strict=False).num_addresses

        final = ("{\"{#NET}\":\"" + str(net) + "\"," + "\"{#TOTAL}\":\"" +
                 str(total - 3) + "\"," + "\"{#POOL}\":\"" + line['vlan'] + "\"},")
        for item in final:
            var += item
    var = var.rstrip(",")
    print('{\"data\":[' + var + ']}')


def dhcp_lease(host=host, user=user, passwd=passwd):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    fortigate_host = host
    fortigate_user = user
    fortigate_pass = passwd

    login_url = 'https://%s/logincheck' % fortigate_host
    login_payload = {'username': fortigate_user,
                     'secretkey': fortigate_pass}

    r = requests.post(login_url, data=login_payload, verify=False)
    cookiejar = r.cookies

    r = requests.get('https://%s/api/v2/monitor/system/dhcp/' %
                     fortigate_host, cookies=cookiejar, verify=False)

    pretty_json = json.loads(r.text)
    payload = json.dumps(pretty_json, indent=2)
    # print(payload)

    c = Counter([k['interface']
                for k in pretty_json['results'] if k.get('interface')])

    print(json.dumps(c))


run()
