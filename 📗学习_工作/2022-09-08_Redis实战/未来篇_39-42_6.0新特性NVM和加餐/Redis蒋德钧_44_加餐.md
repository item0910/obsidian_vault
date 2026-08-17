---
title: 44_加餐
date: 2022-09-06
categories: 数据库
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学前目标

- 阅读来巩固所学知识. (相当于把记忆提取使用)

## 加餐

### 1. 适合阅读的书籍

- 日常操作: 《Redis 使用手册》
- 关键技术原理: 《Redis 设计与实现》与上面是同一个作者
- 实战使用的心得: 《Redis 开发与运维》

### 2. 源码

- Git 上的库: [redis](https://github.com/redis/redis)
- 有一些注释: [带有详细注释的 Redis 3.0 代码](https://github.com/huangz1990/redis-3.0-annotated)

### 3. Redis 和操作系统

![[附件/image/44_加餐.jpg]]
《操作系统导论》
《大规模分布式存储系统：原理解析与架构实战》
《数据密集型应用系统设计》

### 4. Kaito 的学习路线

1. 掌握基本用法和数据结构 (甚至是业务数据结构)
2. 掌握 Redis 实现高可靠高性能的机制
	1. Redis 宕机了怎么办 -> 持久化
	2. 持久化的时候不能服务怎么办 -> 主从集群
	3. 主从集群怎么自动化 -> 哨兵机制
	4. 数据很多怎么办 -> 切片集群
	5. 性能的思考 -> Redis 底层
3. 精通 Redis 的底层实现原理.

### 5. 运维工具推荐

#### (1) INFO 命令

#### (2) 面向 Prometheus 的 redis_exporter

[Prometheus](https://prometheus.io/)
[Grafana](https://grafana.com/)
[redis_exporter](https://github.com/oliver006/redis_exporter)
[redis-stat](https://github.com/junegunn/redis-stat)
[RedisLive](https://github.com/snakeliwei/RedisLive)
- 数据迁移同步:
[RedisShake](https://github.com/alibaba/RedisShake)
[RedisFullCheck](https://github.com/alibaba/RedisFullCheck)
[redis-manager](https://github.com/ngbdf/redis-manager)

## 学后思考

- 评论区: 《Redis 深度历险：核心原理与应用实践》
