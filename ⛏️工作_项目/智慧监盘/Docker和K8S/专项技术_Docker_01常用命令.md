---
title: 专项技术_Docker_01Docker常用命令
date: 2025-02-19
categories: 
tags: 
author: 
---

- 需要对最近的几个AI提问做一个整理

## 容器操作

```bash
docker images
```


## 查询命令

- 查看Log

```bash
docker logs 4c5b39589a6c
```

- 查看容器网络信息

```bash
docker inspect prometheus
```

- 查看具体的网络ip

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 4c5b39589a6c
```



## 网络相关

- 创建网络并链接

```bash
docker network create mynetwork
docker network connect mynetwork prometheus
docker network connect mynetwork pushgateway
```


