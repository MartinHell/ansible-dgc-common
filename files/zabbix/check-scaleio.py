#!/usr/bin/python
import json
import siolib
import argparse


def discovery(scaleio):
    d = {"data":[]}
    data = json.loads(scaleio._get('/api/types/Sds/instances').text)
    for sds in data:
        zbx_item = { "{#NODEID}": sds['id'], "{#NODENAME}": sds['name'] }
        d["data"].append(zbx_item)
    return json.dumps(d, indent=4, sort_keys=True)

# device monitoring
def nodeStatus(scaleio,sds_id):
    # check node status dont continue if the overall status is not normal
    data = json.loads(scaleio._get('/api/instances/Sds::' + str(sds_id)).text)
    if data['sdsState'] != 'Normal':
        return 'name: {} , state: {}'.format(data['name'], data['sdsState'])
    # Check device status
    failed_disks = []
    devices = json.loads(scaleio._get('/api/instances/Sds::' + str(sds_id) + '/relationships/Device').text)
    for dev in devices:
        if dev['deviceState'] != 'Normal':
            failed_disks.append('devicename: {}, state: {}'.format(dev['deviceCurrentPathName'], dev['deviceState']))
    if len(failed_disks) > 0:
        return ','.join(failed_disks)
    else:
        return 'OK'



def main():

    parser = argparse.ArgumentParser(description='ScaleIO/VxFlex Node status')
    parser.add_argument('--host', dest='hostname', required=True, help='hostname')
    parser.add_argument('-u', dest='username', required=True, help='username')
    parser.add_argument('-p', dest='password', required=True, help='password')
    parser.add_argument('-n', dest='node', required=False, help='node')
    parser.add_argument('-d', dest='discover', required=False, default=False, help='discover nodes')
    args = parser.parse_args()

    scaleio = siolib.ScaleIO(rest_server_ip=args.hostname,
                              rest_server_port=443,
                              rest_server_username=args.username,
                              rest_server_password=args.password,
                              verify_server_certificate=False,
                              server_certificate_path=''
                              )


    if args.discover:
        print(discovery(scaleio))


    if args.node:
        data = nodeStatus(scaleio,args.node)
        print(data)



if __name__ == '__main__':
    main()
