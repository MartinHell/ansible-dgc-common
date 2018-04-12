#!/usr/bin/python2.7
# vim: ai ts=4 sts=4 et sw=4 ft=python
 
from __future__ import print_function
 
import sys
import re
import argparse
import ssl
import atexit
import pyVmomi
from pyVim.connect import SmartConnect, Disconnect
from collections import Counter
 
DEBUG = False
 
def get_args():
    global DEBUG
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', required=True, action='store', help='vCenter host')
    parser.add_argument('-U', '--user', required=True, action='store', help='vCenter username')
    parser.add_argument('-P', '--password', required=True, action='store', help='vCenter password')
    parser.add_argument('-t', '--alarmcolor', required=True, action='store', help='Alarm color to look for (red, yellow, any)')
    parser.add_argument('-p', '--port', type=int, default=443, action='store', help='vCenter port (optional)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug logging (optional)')
    args = parser.parse_args()
    if not re.search(r'^(red|yellow|any)$', args.alarmcolor):
        print('[error] -t/--alarmcolor was incorrectly defined')
        #parser.print_help()
        sys.exit(1)
    if args.debug:
        DEBUG = True
    return args
 
def connect(args):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    ctx.verify_mode = ssl.CERT_NONE
    try:
        si = SmartConnect(
            host = args.host,
            user = args.user,
            pwd  = args.password,
            port = args.port,
            sslContext = ctx)
    except Exception as e:
        print('[error] Connection to vCenter failed')
        sys.exit(1)
    DEBUG and print('Successfully logged on!')
    atexit.register(Disconnect, si)
    return si
 
def search(service_instance, vim_type, root=None):
    if not service_instance or not vim_type:
        return False
    if not root:
        root = service_instance.RetrieveServiceContent().rootFolder
    container = service_instance.content.viewManager.CreateContainerView(root, vim_type, True)
    view = container.view
    container.Destroy()
    return view
 
def print_alarms(counter):
    alarm_count = 0
    output = ''
    # Sum up all alarms
    for k,v in counter.items():
        alarm_count += v
        output += ' {}; '.format(k)
 
    print(str(alarm_count) + output)
 
def main():
    red_alarms = Counter()
    yellow_alarms = Counter()
 
    args = get_args()
    si = connect(args)
    results = search(si, [pyVmomi.vim.Datacenter])
    for datacenter in results:
        DEBUG and print('Scanning datacenter {}'.format(datacenter.name))
        alarms = datacenter.triggeredAlarmState
        for alarm in alarms:
            # Skip acked alarms
            if alarm.acknowledged == True:
                continue
            DEBUG and print(alarm)
            DEBUG and print(alarm.alarm.info)
            if alarm.overallStatus == 'red':
                red_alarms[datacenter.name + ':' + alarm.alarm.info.name] += 1
            elif alarm.overallStatus == 'yellow':
               yellow_alarms[datacenter.name + ':' + alarm.alarm.info.name] += 1
 
    if args.alarmcolor == 'any':
        # Combines red_alarms and yellow_alarms into red_alarms.
        DEBUG and print('yellow_alarms _before_ merge: {}'.format(yellow_alarms))
        DEBUG and print('red_alarms _before_ merge: {}'.format(red_alarms))
        DEBUG and print('all alarms _after_ merge: {}'.format(red_alarms + yellow_alarms))
        print_alarms(red_alarms + yellow_alarms)
    elif args.alarmcolor == 'red':
        print_alarms(red_alarms)
    elif args.alarmcolor == 'yellow':
        print_alarms(yellow_alarms)
 
if __name__ == "__main__":
    main()
