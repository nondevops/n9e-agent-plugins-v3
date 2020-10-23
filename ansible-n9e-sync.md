# ansible 批量操作n9e

# 环境

| 物理位置 | 实例IP | 作用 |
| ---- | ---- | ---- |
| 阿里云 | 1.1.1.1 | n9e服务端 |
| 阿里云 | 1.2.1.1 | n9e被采集端 |
| ucloud | 1.3.1.1 | n9e被采集端 |
| 滴滴云 | 1.4.1.1 | n9e被采集端 |

从表格可以得知，n9e的监控主机对象存在跨网跨云现象，所以collector的服务必须走公网调用。

# 主机host
```
[aliyun]
1.2.1.1 ansible_ssh_port=22

[didiyun]
1.3.1.1 ansible_ssh_port=22

[ucloud]
1.4.1.1 ansible_ssh_port=22

```

# 前提条件
服务端与被采集端要做好免密登录，具体怎么做免密，请baidu

# 背景
由于事先未约定俗成统一插件目录以及服务启动路径等问题，为解决一系列问题特编写了一些简单的ansible命令以备不时之需

# 从n9e服务端同步推送plugin目录到被采集端
``` shell
ansible -i /etc/ansible/hosts all -m synchronize -a 'delete=yes archive=yes rsync_opts=--exclude=.tmp rsync_opts=--exclude=.pyc src=/opt/gocode/src/github.com/didi/nightingale/plugin/ dest=/opt/gocode/src/github.com/didi/nightingale/plugin/'
```

# 从n9e服务端同步推送n9e-collector服务到被采集端并重启服务
``` shell
同步n9e-collector服务文件到被采集端初始化目录
ansible -i /etc/ansible/hosts all -m synchronize -a 'src=/opt/gocode/src/github.com/didi/nightingale/etc/service/n9e-collector.service dest=/opt/gocode/src/github.com/didi/nightingale/etc/service/n9e-collector.service'

同步n9e-collector服务文件到被采集端服务启动目录
ansible -i /etc/ansible/hosts all -m synchronize -a 'src=/opt/gocode/src/github.com/didi/nightingale/etc/service/n9e-collector.service dest=/usr/lib/systemd/system/n9e-collector.service'

由于更新了服务文件需批量重载服务
ansible -i /etc/ansible/hosts all -m systemd -a "name=n9e-collector daemon_reload=yes"

批量重启n9e-collector服务
ansible -i /etc/ansible/hosts all -m service -a 'name=n9e-collector state=restarted enabled=yes'
```