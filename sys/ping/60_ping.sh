#!/bin/bash

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

# 传入参数
ip=$1
#ip="www.baidu.com"

# 计数器
count=30

# 实例内网IP
inner_ip=$(ifconfig `route | grep -v "grep" | grep '^default' | awk '{print $NF}'` | grep inet | awk '{print $2}' | head -n 1)

# 上报数据时唯一endpoint
#localip=$(ifconfig `route | grep -v "grep" | grep '^default' | awk '{print $NF}'` | grep inet | awk '{print $2}' | head -n 1)
localip=$(ips=`/sbin/ifconfig -a | grep -v "docker" | grep -v "veth" | grep -v "lo:" | grep -v "enp*" | grep -v "^br" | grep -v "127.0.0.1" | grep -v "172.16.0.1" | grep -v "192.168.0.1" | grep -v "172.18.0.1" | grep -v "172.19.0.1" | grep -v "172.17.0.1" | grep -v inet6 | grep "inet" | awk '{print $2}' | tr -d "addr:"`; host_name=`hostname --fqdn`; echo "${host_name}-${ips}")

# 如果x$1的值为x，则传入的变量为空
if [ x$1 = x ]; then
    ip=$inner_ip
    tmp=ping_$inner_ip.tmp
    #echo "xxxxx"

else
    ip=$1
    tmp=ping_$1.tmp
    #echo "yyyy"
fi

# 时间戳
timestamp=$(date +%s)

# ip="www.baidu.com";ping $ip -c 10 | grep -v "grep" | grep -v "$ip" | grep -v "icmp_seq" > ping_ip.tmp
ping $ip -c $count | grep -v "grep" | grep -v "$ip" | grep -v "icmp_seq" > $tmp

# cat ping_www.baidu.com.tmp | awk -F "," 'NR==2{print $3}' | awk -F " " '{print $1}' | awk -F "%" '{print $1}'
packet_loss=$(cat $tmp | awk -F "," 'NR==2{print $3}' | awk -F " " '{print $1}' | awk -F "%" '{print $1}')

# cat ping_www.baidu.com.tmp | grep -v "grep" | grep "rtt" | awk '{print $4}' | awk -F '/' '{print $4}'
min_response_time=$(cat $tmp | grep -v "grep" | grep "rtt" | awk '{print $4}' | awk -F'/' '{print $1}')

avg_response_time=$(cat $tmp | grep -v "grep" | grep "rtt" | awk '{print $4}' | awk -F'/' '{print $2}')

max_response_time=$(cat $tmp | grep -v "grep" | grep "rtt" | awk '{print $4}' | awk -F'/' '{print $3}')

mdev_response_time=$(cat $tmp | grep -v "grep" | grep "rtt" | awk '{print $4}' | awk -F'/' '{print $4}')

# ping -c 10 172.26.45.178 | grep icmp_seq | awk '{print $7}' | cut -d= -f2
#echo $timestamp --- $packets_transmitted --- $received --- $packet_loss --- $speed_name --- $speed_num >> $rep

echo '[
    {
        "endpoint": "'${localip}'",
        "tags": "'ip=${ip}'",
        "timestamp": '${timestamp}',
        "metric": "sys.ping.packet_loss",
        "value": '${packet_loss}',
    },
    {
        "endpoint": "'${localip}'",
        "tags": "'ip=${ip}'",
        "timestamp": '${timestamp}',
        "metric": "sys.ping.min_response_time",
        "value": '${min_response_time}',
    },
    {
        "endpoint": "'${localip}'",
        "tags": "'ip=${ip}'",
        "timestamp": '${timestamp}',
        "metric": "sys.ping.avg_response_time",
        "value": '${avg_response_time}',
    },
    {
        "endpoint": "'${localip}'",
        "tags": "'ip=${ip}'",
        "timestamp": '${timestamp}',
        "metric": "sys.ping.max_response_time",
        "value": '${max_response_time}',
    },
    {
        "endpoint": "'${localip}'",
        "tags": "'ip=${ip}'",
        "timestamp": '${timestamp}',
        "metric": "sys.ping.mdev_response_time",
        "value": '${mdev_response_time}',
    }

]'

echo "" > $tmp
