---
title: 18_Redis阻塞之基于自身特性的解决
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: Redis 是不是真的变慢了?

- 在事务中, Redis 变慢会带来严重的连锁反应, 用户的体验可能会非常糟糕: 如应用服务器（App Server）要完成一个事务性操作，包括在 MySQL 上执行一个写事务，在 Redis 上插入一个标记位，并通过一个第三方服务给用户发送一条完成消息。

### 通过基线性能判断 Redis 的变慢

- 需要通过 Redis 的运行环境来判断性能是否优劣
- redis-cli 命令提供了–intrinsic-latency 选项, 检测一段时间内的 Redis 最大延迟

```sh
./redis-cli --intrinsic-latency 120
Max latency so far: 17 microseconds.
Max latency so far: 44 microseconds.
Max latency so far: 94 microseconds.
Max latency so far: 110 microseconds.
Max latency so far: 119 microseconds.

36481658 total runs (avg latency: 3.2893 microseconds / 3289.32 nanoseconds per run).
Worst run took 36x longer than the average latency.
```

- iperf 来测量 Redis 客户端到服务器端的网络延迟

### 应对 Redis 的变慢:

1. Redis 自身特性
2. 文件系统
3. 操作系统
![[附件/image/18_Redis阻塞之基于自身特性的解决.jpg]]

本章就是针对 Redis 自身操作特性来优化.

## 18_Redis 阻塞之基于自身特性的解决

### 1. 慢查询

- O(1) 级别的查询复杂度基本固定
- 面对集合 (Set) 的 SUNION(求并集), SMEMBERS(返回所有元素) 等 操作的复杂度都高于 O(N),
- KEYS: 需要遍历键值对进行匹配, 也会拖慢 Redis

```sh
redis> KEYS *name*
1) "lastname"
2) "firstname"
```

#### 应对

- 使用 latency monitor 查看慢查询操作
- 用其它指令代替慢查询指令, 如 SCAN 多次迭代返回
- 聚合查询如排序, 交集并集等, 不要用 SORT、SUNION、SINTER 这些命令，可以整理数据到客户端完成.

### 2. 删除过期 Key

- ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP 设置每 100 毫秒删除这个数量的过期 KEY, 默认 20, 即一秒内删除 200 个 过期 KEY, 这个级别对 Redis 性能不会有太大影响.
- 如果超过 25% 的 key 过期了，则重复删除的过程，直到过期 key 的比例降至 25% 以下。

#### 问题产生点:

频繁使用带有相同时间参数的 EXPIREAT 命令设置过期 key，这就会导致，在同一秒内有大量的 key 同时过期

解决:
1. 需要设置 EXPIREAT 和 EXPIRE 的过期时间参数
2. 给这两个参数加上一个一定大小范围的随机数, 以期不在同一时间段内过期, 实现分开删除.

## 评论区收获和思考

- 问题: KEYS 的匹配功能是业务必须的, 有什么办法平替以避免阻塞吗?
	- 客户端通过执行 `SCAN $cursor COUNT $count` 可以得到一批 key 以及下一个游标 `$cursor`，然后把这个 `$cursor` 当作 SCAN 的参数，再次执行，以此往复，直到返回的 `$cursor` 为 0 时，就把整个实例中的所有 key 遍历出来了。
	- 缩容时 SCAN 命令会导致返回重复 key(索桶时缩到了前面已经遍历过的 Key ), 扩容时不会.
- 老师: HSCAN, SSCAN 等返回一定量的数据而不是全量

	```sh
	HSCAN user 0  match "103*" 100
	```

	从 user 这个 hash 中返回 103 为前缀的 100 个键值对.
