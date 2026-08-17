---
title: 01_Linux命令
date: 2023-02-20
categories: Linux
tags: 归档笔记/学习笔记/Linux
author: 自己
mtime: 2024-09-25
---

## 服务相关命令

### 查询服务列表

systemctl list-unit-files | grep enable

ps -ef | grep python

cent6

chkconfig --list | grep

### 快速删除文件

rsync --delete-before -d /blank/ /usr/hexo/blog

- 安装 rsync 插件
- 先新建一个 blank 文件夹
- 后面是要删除的文件夹

## 用户相关命令

- 删除用户
userdel -r haha
- 切换用户
su - root

## CentOS 7 安装 MySQL 5.7

1. 检查是否安装过 mysql.
	rpm -aq | grep -i mysql
	1. 若安装过, 如何卸载 rpm -e --nodeps
	2. 需要做安装前的 cfg 文件检查 https://blog.csdn.net/weixin_43712228/article/details/116108212
2. 离线安装方法.
	1. 若遭遇冲突, 如何处理
		(https://blog.csdn.net/weixin_43712228/article/details/116108212)
	2. 需要按照怎样的顺序安装 (为什么)
		(https://blog.csdn.net/ai_64/article/details/100557530)
3. 在线安装方法
	1. [https://blog.csdn.net/u014559804/article/details/116565063](https://blog.csdn.net/u014559804/article/details/116565063)
4. 安装完成后, 需要做什么工作
	1. 开启服务, 检查状态
	2. 登录并修改密码
	3. 如何设置简单密码
	[https://blog.csdn.net/weixin_46091073/article/details/121067898](https://blog.csdn.net/weixin_46091073/article/details/121067898)
5. 开启远程登录
	1. 简单方法: 关闭防火墙
	[https://blog.csdn.net/weixin_45075705/article/details/90261880](https://blog.csdn.net/weixin_45075705/article/details/90261880)
	2. 开放防火墙端口, 并重启防火墙
	[https://www.linuxidc.com/Linux/2016-12/138979.htm](https://www.linuxidc.com/Linux/2016-12/138979.htm)
6. 如何登录

## CentOS 7 防火墙设置

 一、防火墙的开启、关闭、禁用命令

（1）设置开机启用防火墙：systemctl enable firewalld.service

（2）设置开机禁用防火墙：systemctl disable firewalld.service

（3）启动防火墙：systemctl start firewalld

（4）关闭防火墙：systemctl stop firewalld

（5）检查防火墙状态：systemctl status firewalld 

二、使用 firewall-cmd 配置端口

（1）查看防火墙状态：firewall-cmd --state

（2）重新加载配置：firewall-cmd --reload

（3）查看开放的端口：firewall-cmd --list-ports

（4）开启防火墙端口：firewall-cmd --zone=public --add-port=9200/tcp --permanent

　　命令含义：

　　–zone 作用域

　　–add-port=9200/tcp 添加端口，格式为：端口/通讯协议

　　–permanent 永久生效，没有此参数重启后失效

　　**注意：添加端口后，必须用命令 firewall-cmd --reload 重新加载一遍才会生效**

（5）关闭防火墙端口：firewall-cmd --zone=public --remove-port=9200/tcp --permanent
