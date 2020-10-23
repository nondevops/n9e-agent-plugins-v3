#!/usr/bin/env python
# -*- coding: utf-8 -*-

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

# 监测 ntp 时间同步

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


plugins_log_dirs = '/opt/gocode/src/github.com/didi/nightingale/logs/plugin/'
plugins_erro_log = plugins_log_dirs+'/error.log'

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

def fetch_ntp_state():

    # fail    获取状态: 0 获取成功, 1 获取失败
    # offset  ntp同步的偏移量, 使用绝对值表示
    # timeout 超时状态: 0 成功,     1 超时
    offset, fail, timeout = 0, 1, 0
    ip_addr = get_ip_address('endpoint')

    try:
        raw_data = Popen(['ntpq', '-pn'], stdout=PIPE, stderr=PIPE).communicate()[0]
        for line in raw_data.splitlines():
            if line.startswith('*'):
                l = line.split()
                when, poll, offset = l[4], l[5], l[8]
                offset = abs(float(offset))
                timeout, fail = check_status(when, poll)

    except OSError:
        pass

    create_record(ip_addr, 'sys.ntp.fail', fail)
    create_record(ip_addr, 'sys.ntp.timeout', timeout)
    create_record(ip_addr, 'sys.ntp.offset', offset)


# 判断上次同步状态, return (timeout, fail)
def check_status(when, poll):

    timeout, fail = 0, 1
    try:
        if int(poll) - int(when) >= 0:
            timeout, fail = 0, 0
        else:
            timeout, fail = 1, 0
    except:
        pass

    return timeout, fail

def create_record(ip_addr, metric, value):
    record = {}
    record['Metric']      = metric
    record['Endpoint']    = get_ip_address('endpoint')
    record['Timestamp']   = int(time.time())
    record['Value']       = value
    record['CounterType'] = 'GAUGE'
    record['TAGS']        = ''
    data.append(record)

if __name__ == '__main__':

    retry = 3
    retry_interval = 3

    for i in range(0, retry):

        data = []
        fetch_ntp_state()

        if data[0]['Value'] == 0 and data[1]['Value'] == 0 or retry == i+1:
            break
        time.sleep(retry_interval)
    
    print json.dumps(data)
