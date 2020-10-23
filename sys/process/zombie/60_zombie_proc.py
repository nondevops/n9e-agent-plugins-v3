#!/usr/bin/env python
# -*- coding: utf-8 -*-

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

import os
import time
import json
import commands
import platform
import sys
import logging
import socket

data = []
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

try:
    value = int(commands.getoutput("ps -aux | awk '{print $8}' | grep -v 'grep' | grep '^Z$' |wc -l").strip())
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(2)

def create_record():
    record = {}
    record['metric'] = 'sys.process.zombie'
    record['endpoint'] = get_ip_address('endpoint')
    record['timestamp'] = ts
    record['value'] = value
    record['counterType'] = counterType
    record['tags'] = ''
    data.append(record)

create_record()

if data:
   print json.dumps(data)