---
title: 20_Redis之内存碎片
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: Redis 内存碎片如何形成

### 内因: 分配策略

- Redis 可以使用 libc、jemalloc、tcmalloc 多种内存分配器来分配内存，默认使用 jemalloc。
- 默认申请 > 需要的 2 的幂次的内存. 比如需要 20 字节, 就申请 32 字节.

### 外因: 键值对的修改删除

![[附件/image/20_Redis之内存碎片.jpg]]

## Redis 之内存碎片发现和删除

### 1. 如何判断有没有内存碎片

- INFO memory

```
INFO memory
# Memory
used_memory:1073741736
used_memory_human:1024.00M
used_memory_rss:1997159792
used_memory_rss_human:1.86G
…
mem_fragmentation_ratio:1.86
```

- 最后一行的指标计算
`mem_fragmentation_ratio = used_memory_rss/ used_memory`

- 经验之谈:
	- mem_fragmentation_ratio 大于 1 但小于 1.5。这种情况是合理的。这是因为，刚才我介绍的那些因素是难以避免的。毕竟，内因的内存分配器是一定要使用的，分配策略都是通用的，不会轻易修改；而外因由 Redis 负载决定，也无法限制。所以，存在内存碎片也是正常的。
	- mem_fragmentation_ratio 大于 1.5 。这表明内存碎片率已经超过了 50%。一般情况下，这个时候，我们就需要采取一些措施来降低内存碎片率了。

### 2. 如何处理内存碎片

1. 手动清理: 重启 Redis, 并通过持久化文件恢复, 有可能导致数据丢失.
2. 自动清理: 会带来时间开销, 解决方式, 手动设置参数来控制清理时机
	- 开启自动清理

		```sh
		config set activedefrag yes
		```

	- 参数
		- active-defrag-ignore-bytes 100mb：表示内存碎片的字节数达到 100MB 时，开始清理；
		- active-defrag-threshold-lower 10：表示内存碎片空间占操作系统分配给 Redis 的总空间比例达到 10% 时，开始清理。
		- active-defrag-cycle-min 25： 表示自动清理过程所用 CPU 时间的比例不低于 25%，保证清理能正常开展；
		- active-defrag-cycle-max 75：表示自动清理过程所用 CPU 时间的比例不高于 75%，一旦超过，就停止清理，从而避免在清理时，大量的内存拷贝阻塞 Redis，导致响应延迟升高。如果影响了正常的请求处理, 可以调小该值.

## 评论区收获和思考

- mem_fragmentation_ratio 小于 1 了是什么情况?
	- SWAP 了.
