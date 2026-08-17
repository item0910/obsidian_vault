---
title: 35_Codis集群方案
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-10-15
---

## 学习之前:

[[Redis蒋德钧_09_Redis_Cluster切片集群方案]]

## Codis 集群方案

### Codis 整体架构和基本流程

Codis 集群包含四类组件:
- codis server：这是进行了二次开发的 Redis 实例，其中增加了额外的数据结构，支持数据迁移操作，主要负责处理具体的数据读写请求。
- codis proxy：接收客户端请求，并把请求转发给 codis server。
- Zookeeper 集群：保存集群元数据，例如数据位置信息和 codis proxy 信息。
- codis dashboard 和 codis fe：共同组成了集群管理工具。其中，codis dashboard 负责执行集群管理工作，包括增删 codis server、codis proxy 和进行数据迁移。而 codis fe 负责提供 dashboard 的 Web 操作界面，便于我们直接在 Web 界面上进行集群管理。
![[附件/image/35_Codis集群方案.jpg]]
客户端查询数据流程
![[附件/image/35_Codis集群方案-1.jpg]]

### Codis 关键技术原理

1. 第一步，把编号从 0 - 1023 的 1024 个 Slot 在 dashboard 上做分配
2. 第二步，客户端使用 CRC32 算法 key 的哈希值并对 1024 取模。而取模后的值，则对应 Slot 的编号。
![[附件/image/35_Codis集群方案-2.jpg]]
与 Redis Cluster 的区别
- Redis Cluster 会通过实例间的相互通信在每个实力上都保存一份 slot 的位置表, 如果 slot 位置有变化, 就需要在每个实例上都传输一份.

### Codis 集群扩容和迁移

1. 增加 codis server
	1. 从源 server 中选出 slot 中的一个 key, 发给目标, 目标收到后, 返回确认, 源数据删除.
	2. 重复这个过程, 直到完成这个 slot 的迁移.
	3. 这个过程分为同步和异步, 同步是阻塞的, 无法处理其它请求. 异步有两个特点,
		1. 第一个是不阻塞, 但迁移数据会在源数据上设置为只读 (避免了不一致的问题).
		2. 第二个特点是针对 bigkey, 异步迁移, 是化整为零的. 如果中途发生鼓掌就会数据不一致, 为了避免这种情况, 会在迁移完成前在目标 server 上设置一个过期时间, 只有在完成迁移后才消除这个过期时间.
		3. 允许每次迁移多个, 你可以通过异步迁移命令 SLOTSMGRTTAGSLOT-ASYNC 的参数 numkeys 设置每次迁移的 key 数量。
2. 增加 proxy:
	1. 启动 proxy, 通过 codis dashboard 把它加入到集群中就行了.
	2. proxy 的信息会被保存在 zookeeper 上, 客户端通过获取 zookeeper 上的信息就会访问新的 proxy 了.

### 使用 Codis 客户端需要重新开发吗?

客户端的具体访问由 proxy 来控制, 所以不需要客户端重新开发.
而且, 还可以复用以前的客户端单实例连接.

### Codis 集群可靠性

- server 的可靠性
	- 给每个 server 一主多从的配置, 并且用哨兵集群对他们进行监控
- proxy 和 zookeeper 的可靠性.
	- zookeeper 有多个实例来保存数据, 只要超过半数的实例可以正常工作, 就可以提供服务
	- proxy 是无状态的, 路由信息都保存在 zookeeper 里, 发生故障可以直接重启.

![[附件/image/35_Codis集群方案-3.jpg]]

### 集群方案的建议

两种方案的对比
![[附件/image/35_Codis集群方案-4.jpg]]
1. 从稳定性和成熟性来说, codis 更久,.
2. 从业务兼容性来说, 因为不要额外修改配置, codis 也是更好
3. 从数据迁移来说, codis 更方便
4. 如果要用新特性, 就选择 Redis Cluster

- 小建议: 如果有多个业务线需要使用 Codis, 可以启动多个 codis dashboard, 分别管理一部分, 然后再用一个 dashboard 来管理这些集群, 做到一个 codis 集群管理多条线.

## 评论区收获和思考

- 假设 Codis 集群中保存的 80% 的键值对都是 Hash 类型，每个 Hash 集合的元素数量在 10 万～20 万个，每个集合元素的大小是 2KB。你觉得，迁移一个这样的 Hash 集合数据，会对 Codis 的性能造成影响吗？
	- 影响不大, Codis 支持分批异步迁移.
