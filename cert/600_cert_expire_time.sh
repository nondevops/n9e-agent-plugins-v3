#!/bin/bash

# V3 版本的采集频率直接在采集策略里配置，不需要上报 step 字段

# 检测证书过期时间

domain_list=(
baidu.com
)

function check_ssl(){
domain=$1
ts=$(date +%s)
#localip=$(/usr/sbin/ifconfig `/usr/sbin/route|grep '^default'|awk '{print $NF}'`|grep inet|awk '{print $2}'|head -n 1)
localip=$(ips=`/sbin/ifconfig -a | grep -v "docker" | grep -v "veth" | grep -v "lo:" | grep -v "enp*" | grep -v "^br" | grep -v "127.0.0.1" | grep -v "172.16.0.1" | grep -v "192.168.0.1" | grep -v "172.18.0.1" | grep -v "172.19.0.1" | grep -v "172.17.0.1" | grep -v inet6 | grep "inet" | awk '{print $2}' | tr -d "addr:"`; host_name=`hostname --fqdn`; echo "${host_name}-${ips}")
timestamp=$(date +%s)


counterType="GAUGE"

ping -c1 223.5.5.5 &> /dev/null
if [ $? -eq 0 ]
then
    END_TIME=$(echo | timeout 3 openssl s_client -servername ${domain} -connect "${domain}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | awk -F '=' '{print $2}' )
    #将日期转化为时间戳
    END_TIME_STAMP=$(date +%s -d "${END_TIME}") 
    #echo "cccccc=$END_TIME1"
    NOW_TIME__STAMP=$(date +%s)
    #echo "ddddddd=$NOW_TIME"
    # 到期时间减去目前时间再转化为天数
    ssl_expire_days=$(($((${END_TIME_STAMP} - ${NOW_TIME__STAMP}))/(60*60*24))) 
    #echo "域名${domain}的证书还有${ssl_expire_days}天过期..."
    metrics="{\"metric\": \"ssl.cert.expiredays\", \"endpoint\": \"${localip}\", \"timestamp\": ${ts},\"value\": ${ssl_expire_days},\"counterType\": \"${counterType}\",\"tags\": \"domain_name=${domain}\"}"
    echo $metrics
else
    pass
fi
}

for i in ${domain_list[*]}
do
  data=''''${data}','$(check_ssl ${i})''''
done

echo "$data"|sed "s/^,//g;s/^/[/g;s/$/]/g"
