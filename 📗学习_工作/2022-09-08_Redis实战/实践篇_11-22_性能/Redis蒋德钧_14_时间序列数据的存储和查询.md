---
title: 14_时间序列数据的存储和查询
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 时间序列数据的特点

1. 读写特点:
	1. 写多, 读的情况一般分两种
	2. 范围查询
	3. 聚合查询: 查一段时间的平均值, 最大值等等.

## 用 Redis 存储时间序列数据

### 1. Hash 和 sorted set 共同存储

#### (1) 哈希存储数据的形式

![[附件/image/14_时间序列数据的存储和查询.jpg]]

```
HGET device:temperature 202008030905
"25.1"

HMGET device:temperature 202008030905 202008030907 202008030908
1) "25.1"
2) "25.9"
3) "24.9"
```

- 缺点, 不能范围查询. 每查询一个都需要进行遍历.

#### (2) sorted set 类型的数据

![[附件/image/14_时间序列数据的存储和查询-1.jpg]]

- 可以进行范围查询

```
ZRANGEBYSCORE device:temperature 202008030907 202008030910
1) "25.9"
2) "24.9"
3) "25.3"
4) "25.2"
```

#### (3) 如何保证他们的原子性: 数据一致

- MULTI 和 EXEC 来进行小范围的事务机制

```
127.0.0.1:6379> MULTI
OK

127.0.0.1:6379> HSET device:temperature 202008030911 26.8
QUEUED

127.0.0.1:6379> ZADD device:temperature 202008030911 26.8
QUEUED

127.0.0.1:6379> EXEC
1) (integer) 1
2) (integer) 1
```

#### (4) 如何进行聚合计算

只能将数据拷贝到客户端进行聚合计算, 会占用大量的网络资源, 造成系统变慢

### 2. RedisTimeSeries

#### (1) 启用

因为 RedisTimeSeries 不属于 Redis 的内建功能模块，在使用时，我们需要先把它的源码单独编译成动态链接库 redistimeseries.so，再使用 loadmodule 命令进行加载，如下所示：

```
loadmodule redistimeseries.so
```

#### (2) 命令

- 创建一个生命为 600s 的 ID 号为 1 的数据, 表明这个集合是属于 ID 号为 1 的数据记录

```
TS.CREATE device:temperature RETENTION 600000 LABELS device_id 1
OK
```

- 插入数据和读取数据 (最新)

```
TS.ADD device:temperature 1596416700 25.1
1596416700

TS.GET device:temperature 
25.1
```

- 按标签读取数据

```
TS.MGET FILTER device_id!=2 
1) 1) "device:temperature:1"
   2) (empty list or set)
   3) 1) (integer) 1596417000
      2) "25.3"
2) 1) "device:temperature:3"
   2) (empty list or set)
   3) 1) (integer) 1596417000
      2) "29.5"
3) 1) "device:temperature:4"
   2) (empty list or set)
   3) 1) (integer) 1596417000
      2) "30.1"
```

#### (3) 聚合计算

计算这段时间内每 180s 的平均温度

```
TS.RANGE device:temperature 1596416700 1596417120 AGGREGATION avg 180000
1) 1) (integer) 1596416700
   2) "25.6"
2) 1) (integer) 1596416880
   2) "25.8"
3) 1) (integer) 1596417060
   2) "26.1"
```

## 思考:Sorted Set 保存时间序列有什么风险?

- Sorted Set 作为保存时间序列数据的潜在风险? 如果你是开发者, 你会给 Sorted Set 添加聚合计算的功能吗?
	- 风险:
		- 某一时间段的数据相同 (温度相同), 那么就只会记录一个数据, 只是在更新 Score 而已.
		- 精度高, 保存太多温度产生 BigKey 问题
		- 不能完成聚合计算
	- 不会, 单核的 Redis 不能充分利用多核的性能. 除非更改 Redis 的线程模型, 比如使用额外的线程池做聚合计算
