#!/bin/bash

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

TS=$(date +%s)
counterType="GAUGE"
pings="/bin/ping"
localip=$(ifconfig `route | grep -v "grep" | grep '^default' | awk '{print $NF}'` | grep inet | awk '{print $2}' | head -n 1)

# -c 次数; -w ping退出之前的超时秒数; -W 等待超时时间s; -q 静默输出
# ping -c 50 -w 10 -W 10 -q "10.200.7.106" | grep -oE "[0-9]*% packet loss" | awk -F'%' '{print $1}'
loss=$($pings -c 60 -w 10 -W 10 -q "${localip}" | grep -oE "[0-9]*% packet loss" | awk -F'%' '{print $1}')

echo '[
    {
        "endpoint": "'$localip'", 
        "tags": "",
        "timestamp": '$TS',
        "metric": "sys.ping.packet_loss.percent",
        "value": '$loss',
    }
]'
