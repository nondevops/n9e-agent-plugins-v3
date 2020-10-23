#!/bin/bash

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

duration=$(cat /proc/uptime | awk '{print $1}')
#localip=$(/usr/sbin/ifconfig `/usr/sbin/route|grep '^default'|awk '{print $NF}'`|grep inet|awk '{print $2}'|head -n 1)
localip=$(ips=`/sbin/ifconfig -a | grep -v "docker" | grep -v "veth" | grep -v "lo:" | grep -v "enp*" | grep -v "^br" | grep -v "127.0.0.1" | grep -v "172.16.0.1" | grep -v "192.168.0.1" | grep -v "172.18.0.1" | grep -v "172.19.0.1" | grep -v "172.17.0.1" | grep -v inet6 | grep "inet" | awk '{print $2}' | tr -d "addr:"`; host_name=`hostname --fqdn`; echo "${host_name}-${ips}")

echo '[
    {
        "endpoint": "'${localip}'",
        "tags": "",
        "timestamp": '$(date +%s)',
        "metric": "sys.uptime.duration",
        "value": '${duration}',
    }
]'
