#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: ulric.qin@gmail.com

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

import time
import commands
import json
import sys
import os

items = []


def collect_myself_status():
    item = {}
    item["metric"] = "plugin.myself.status"
    item["value"] = 1
    item["tags"] = ""
    items.append(item)


def main():
    #code, endpoint = commands.getstatusoutput("timeout 1 /usr/sbin/ifconfig `/usr/sbin/route|grep '^default'|awk '{print $NF}'`|grep inet|awk '{print $2}'|head -n 1")
    code, endpoint = commands.getstatusoutput("ips=`/sbin/ifconfig -a | grep -v 'docker' | grep -v 'veth' | grep -v 'lo:' | grep -v 'enp*' | grep -v '^br' | grep -v '127.0.0.1' | grep -v '172.16.0.1' | grep -v '192.168.0.1' | grep -v '172.18.0.1' | grep -v '172.19.0.1' | grep -v '172.17.0.1' | grep -v 'inet6' | grep 'inet' | awk '{print $2}' | tr -d 'addr:'`; host_name=`hostname --fqdn`; echo ${host_name}-${ips}")
    if code != 0:
        sys.stderr.write('cannot get local ip')
        return

    timestamp = int("%d" % time.time())
    plugin_name = os.path.basename(sys.argv[0])

    collect_myself_status()

    for item in items:
        item["endpoint"] = endpoint
        item["timestamp"] = timestamp

    print json.dumps(items)


if __name__ == "__main__":
    sys.stdout.flush()
    main()
    sys.stdout.flush()
