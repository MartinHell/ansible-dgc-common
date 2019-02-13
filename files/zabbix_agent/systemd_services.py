#!/usr/bin/env python

import argparse
import os
import subprocess
import re
import json

def Discovery(*kv):
    d = {"data":[]}

    if len(kv[0]) > 0:
      white = kv[0]
    else:
      white = ['sshd', 'ntp', 'syslog', 'zabbix', 'docker']

    cmd = [ 'systemctl', 'list-unit-files', '--type', 'service', '--state', 'enabled,generated']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, err =  proc.communicate()

    services = re.findall(".*.service", output)
    whitelist = re.compile('|'.join([re.escape(word) for word in white]))
    filtered_list = [word for word in services if whitelist.search(word)]

    for service in filtered_list:
        zbx_item = { "{#SERVICE}": service }
        d["data"].append(zbx_item)

    return json.dumps(d, indent=4, sort_keys=True)


def CheckService(service):
    cmd = [ 'systemctl', 'status', '--quiet', service ]
    try:
        output = subprocess.check_output(cmd)
        return 1
    except subprocess.CalledProcessError as e:
        return 0


def main():
    parser = argparse.ArgumentParser(description='Systemd monitoring')
    parser.add_argument(
        '-d',
        '--discovery',
        dest='discovery',
        action='store_true',
        default=False,
        help="Discovery")
    parser.add_argument(
        '-l',
        '--servicelist',
        dest='list',
        default=[],
        help="Comma separated list of services to discover")
    parser.add_argument(
        '-s',
        '--service',
        dest='service',
        default=None,
        help="Service to be checked")

    args = parser.parse_args()

    discover_list = []
    if len(args.list) > 0:
        discover_list = args.list.split(',')
    if args.discovery:
        print(Discovery(discover_list))
        return
    if args.service:
        print(CheckService(args.service))



if __name__ == '__main__':
    main()

