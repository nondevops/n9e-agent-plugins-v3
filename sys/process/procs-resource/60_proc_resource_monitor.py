#!/usr/bin/env python
#-*- coding:utf-8 -*-

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

import os,sys
import os.path
from os.path import isfile
from traceback import format_exc
import xmlrpclib
import socket
import time
import json
import copy
import httplib
from subprocess import Popen, PIPE
import commands
import platform
import logging
import yaml



timestamp = int(time.time())
plugins_log_dirs = '/opt/gocode/src/github.com/didi/nightingale/logs/plugin/'
plugins_erro_log = plugins_log_dirs+'/error.log'
counterType = 'GAUGE'


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

class Resource():

    def __init__(self, pid, tag):
        self.host = get_ip_address('endpoint')
        self.pid = pid
        self.tag = tag

    def get_cpu_user(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $14+$16}'"
        return os.popen(cmd).read().strip("\n")

    def get_cpu_sys(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $15+$17}'"
        return os.popen(cmd).read().strip("\n")

    def get_cpu_all(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $14+$15+$16+$17}'"
        return os.popen(cmd).read().strip("\n")

    # 进程总内存(文件映射，共享内存，堆，任何其它的内存的总和，它包含VmRSS)
    def get_mem_vmsize(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep VmSize | awk '{print $2*1024}'"
        return os.popen(cmd).read().strip("\n")
    
    # 进程实际用到的物理内存
    def get_mem_vmrss(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep VmRSS | awk '{print $2*1024}'"
        return os.popen(cmd).read().strip("\n")

    def get_mem_swap(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $(NF-7)+$(NF-8)}' "
        return os.popen(cmd).read().strip("\n")

    def get_fd(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep FDSize | awk '{print $2}'"
        return os.popen(cmd).read().strip("\n")

    def get_process_status(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep State | awk '{print $2}'"
        return os.popen(cmd).read().strip("\n")

    def run(self):
        self.resources_d = {
            'sys.process.cpu.user':[self.get_cpu_user,'COUNTER'],
            'sys.process.cpu.sys':[self.get_cpu_sys,'COUNTER'],
            'sys.process.cpu.all':[self.get_cpu_all,'COUNTER'],
            'sys.process.mem.vmsize':[self.get_mem_vmsize,'GAUGE'],
            'sys.process.mem.used':[self.get_mem_vmrss,'GAUGE'],
            'sys.process.mem.swap':[self.get_mem_swap,'GAUGE'],
            'sys.process.fdsize':[self.get_fd,'GAUGE'],
            'sys.process.status':[self.get_process_status,'GAUGE']
        }

        if not os.path.isdir("/proc/" + str(self.pid)):
            return

        output = []
        for resource in self.resources_d.keys():
                t = {}
                t['endpoint'] = self.host
                t['timestamp'] = timestamp
                t['counterType'] = self.resources_d[resource][1]
                t['metric'] = resource
                t['value'] = self.resources_d[resource][0]()
                #t['tags'] = "module=cpu_resource,pro_cmd=%s" % ( self.tag)
                t['tags'] = "process_cmd=%s,process_pid=%s" % (self.tag, self.pid)

                output.append(t)

        return output

def get_pid():
    # cpu使用大于98或内存大于98, 取排名前3的进程
    cmd = "ps aux | awk '{ if ($3>98 || $4>98) print $2, $3, $4, $11$12; }' | sort -k2rn | head -n 3"
    ret = []
    for item in os.popen(cmd).readlines():
        pid = {}
        try:
            assert(isinstance(int(item.split()[0]), (int, long)))
        except AssertionError:
            #print "ERROR: key is not int."
            continue
        pid[int(item.split()[0])] = item.split()[-1].strip("\n")
        ret.append(pid)
    return ret

if __name__ == "__main__":
    pids = get_pid()
    #print pids
    payload = []
    for item in pids:
        for pid in item:            
            d = Resource(pid=pid, tag=item[pid]).run()
            if d:
                payload.extend(d)
    if payload:
        print json.dumps(payload)