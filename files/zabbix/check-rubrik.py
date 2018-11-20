#!/usr/bin/python

try:
    import rubrik_cdm
except:
    print("ERROR - python 'rubrik_cdm' module is missing")

import json
import urllib3
import argparse
import os
import sys
urllib3.disable_warnings()

def discovery(ctx):
    d = {"data":[]}
    # Node Discovery
    node_names = ctx.cluster_node_name()
    for node in node_names:
        zbx_item = { "{#NODEID}": node }
        d["data"].append(zbx_item)
    return json.dumps(d, indent=4, sort_keys=True)




def nodeStatus(ctx,id):
    # Return BrickID if a brick is not Status == 'OK'
    data = ctx.get('internal', '/node/{}'.format(id))
    disks = []
    # Disk status
    for ssd in data['ssd']:
        if ssd['status'] != 'ACTIVE':
            disks.append(ssd['id'])
    for hdd in data['hdd']:
        if hdd['status'] != 'ACTIVE':
            disks.append(hdd['id'])
    if data['status'] != 'OK' or len(disks) > 0:
        return 'Overall Status: {} Disk with bad state: {}'.format(data['status'], ','.join(disks))
    return data['status']
    

def main():

    parser = argparse.ArgumentParser(description='Rubrik Node status')
    parser.add_argument('--host', dest='hostname', required=True, help='hostname')
    parser.add_argument('-u', dest='username', required=True, help='username')
    parser.add_argument('-p', dest='password', required=True, help='password')
    parser.add_argument('-n', dest='node', required=False, help='node')
    parser.add_argument('-d', dest='discover', required=False, default=False, help='discover nodes')
    args = parser.parse_args()

    rubrik = rubrik_cdm.Connect(node_ip=args.hostname, username=args.username, password=args.password, enable_logging=False)

    if args.discover:
        print(discovery(rubrik))
        sys.exit(0)


    if args.node:
        data = nodeStatus(rubrik,args.node)
        print(data)



if __name__ == '__main__':
    main()

