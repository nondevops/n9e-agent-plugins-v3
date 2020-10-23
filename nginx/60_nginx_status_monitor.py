#!/usr/bin/env python
# -*- coding: utf-8 -*

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

from subprocess import Popen, PIPE
import os
import time
import json
import commands
import platform
import sys
import logging
import socket
import yaml

counter_list = []

plugins_log_dirs = '/opt/gocode/src/github.com/didi/nightingale/logs/plugin/'
plugins_erro_log = plugins_log_dirs+'/error.log'
counterType = 'GAUGE'
ts = int(time.time())

if not os.path.exists(plugins_log_dirs):
    os.makedirs(plugins_log_dirs)

if not os.path.exists(plugins_erro_log):
    os.system(r"touch {}".format(plugins_erro_log))

logging.basicConfig(level=logging.ERROR,  
                    filename=plugins_erro_log,  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def read_endpoint_value():
    try:
        with open('/opt/gocode/src/github.com/didi/nightingale/etc/collector.yml', 'r') as f:
            file_content = f.read()
            x = yaml.load(file_content)
            print(x['identity']['shell'])
            #return load_dict["hostname"]

    except OSError:
        pass

#read_endpoint_value()

def get_ip_address(key):
    if key=='ip':
        return socket.gethostbyname(socket.gethostname())
    elif key=='hostname':
        return socket.gethostname()
    elif key=='endpoint':
        #endpoint = commands.getoutput('''ifconfig `route|grep '^default'|awk '{print $NF}'`|grep inet|awk '{print $2}'|awk -F ':' '{print $NF}'|head -n 1 ''')
        endpoint = commands.getoutput('''ips=`/sbin/ifconfig -a | grep -v 'docker' | grep -v 'veth' | grep -v 'lo:' | grep -v 'enp*' | grep -v '^br' | grep -v '127.0.0.1' | grep -v '172.16.0.1' | grep -v '192.168.0.1' | grep -v '172.18.0.1' | grep -v '172.19.0.1' | grep -v '172.17.0.1' | grep -v 'inet6' | grep 'inet' | awk '{print $2}' | tr -d 'addr:'`; host_name=`hostname --fqdn`; echo ${host_name}-${ips}''')
        return endpoint

def checknginxconf():
    b = False
    val = commands.getoutput('nginx -t')
    if 'syntax is ok' in val:
        b = True
    return b

# 1:正常;0:异常
if __name__ == '__main__':
    value = 0
    if checknginxconf():
        value = 1
    counter_list.append(
        {"endpoint": get_ip_address('endpoint'),
        "metric": "nginx.conf.check.status",
        "tags": "",
        "timestamp": ts,
        "counterType": counterType,
        "value": value})
    print json.dumps(counter_list)
