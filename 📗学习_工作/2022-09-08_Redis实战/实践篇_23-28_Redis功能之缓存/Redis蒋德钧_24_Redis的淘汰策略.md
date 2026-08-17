---
title: 24_Redis的淘汰策略
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前

## Redis 的淘汰策略

### 1. Redis 设置多大: 八二原理

- 长尾效应和重尾分布
![[附件/image/24_Redis的淘汰策略.jpg]]
- 建议把缓存容量设置为总数据量的 15% 到 30%，兼顾访问性能和内存空间开销。
- 设置 Redis 的大小

```
CONFIG SET maxmemory 4gb
```

### 2. 淘汰策略

- 不进行数据淘汰的策略，只有 noeviction 这一种。
- 在设置了过期时间的数据中进行淘汰，包括
	- volatile-random、
	- volatile-ttl、
	- volatile-lru、
	- volatile-lfu（Redis 4.0 后新增）四种。
- 在所有数据范围内进行淘汰，包括
	- allkeys-lru、
	- allkeys-random、
	- allkeys-lfu（Redis 4.0 后新增）三种。
- LRU 算法:
	- 通常的 LRU 算法: 链表管理. 后端移除, 缺点, 带来额外的空间开销和链表的操作, 浪费性能
	- Redis 的简化 LRU : 记录每个数据的时间戳, 随机取出 N 个数据, 把时间戳最靠前的淘汰出去. 这个 N 靠这个值设置.

		```sh
		CONFIG SET maxmemory-samples 100
		```

		再次淘汰数据是, 能够进入候选的必须要小于第一次创建的, 这样就保证了一个集合中的时间戳相对较小.
- 建议优先使用 	`allkeys-lru`、
- 如果业务没有热点数据, 那么就用 `allkeys-random`
- 如果业务有置顶需求, 使用 `volatile-lru`, 并不给置顶数据设置过期时间

### 3. 如何处理被淘汰的数据

- 脏数据: 被修改过的数据, 写回数据库
- 干净的数据: 删除.

## 评论区收获和思考

- 问: 只读缓存，以及读写缓存中的两种写回策略，请你思考下，Redis 缓存对应哪一种或哪几种模式？
	- 答: 脏数据异步写回. 对应异步写回的读写缓存模式
