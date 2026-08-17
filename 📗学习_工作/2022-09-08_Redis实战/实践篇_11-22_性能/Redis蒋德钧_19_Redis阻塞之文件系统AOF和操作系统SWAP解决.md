---
title: 19_Redis阻塞之文件系统AOF和操作系统SWAP解决
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 持久化和内存数据库

- 持久化依赖文件系统
- 内存数据库对应操作系统的内存机制

## Redis 阻塞之文件系统 AOF 和操作系统 SWAP 解决

### 1. AOF 的模式与处理

AOF 的三种写回策略与 文件系统的 write 和 fsync 的调用.

- write 把日志记录到内核缓冲区, 不需要等待实际写回到磁盘
- fsync 需要等待实际写回到磁盘
![[附件/image/19_Redis阻塞之文件系统AOF和操作系统SWAP解决.jpg]]

everysec 和 always 虽然都会调用 fsync, 但二者有所区别, **everysec 是在后台子进程里完成的, 而 Always 不是**, 因为 Always 需要知道每次 fsync 是不是完成了. 我们可以看一下 appendfsync 配置项, 一目了然.

![[附件/image/19_Redis阻塞之文件系统AOF和操作系统SWAP解决-1.jpg]]

#### AOF 重写时可能出现的阻塞

虽然 fsync 是后台子线程完成的, 但主线程会监视他的进度. 一种可能的情况, 当 AOF 在重写时, 占用了系统 IO, 阻塞了第一个 fsync 的完成; 当第二个 fsync 需要执行时, 就被阻塞, 以至于主线程也被阻塞, 如图

![[附件/image/19_Redis阻塞之文件系统AOF和操作系统SWAP解决-2.jpg]]

1. 解决方式 1: 那么我们只要配置 fsync 在 AOF 重写时不进行就行了, 配置方法如下:

```sh
no-appendfsync-on-rewrite yes
```

1. 解决方式 2: 另外, 为了缓解 IO 压力, 可以使用高速固态硬盘来作为 AOF 的写入设备.

### 2. 操作系统的 SWAP 和 内存大页

#### SWAP

SWAP: 内存读写被换为磁盘读写

- 原因: 内存不足
查看 SWAP 情况:
1. 获取进程号

```sh
$ redis-cli info | grep process_id
process_id: 5332
```

1. 进入进程目录中

```sh
$ cd /proc/5332
```

1. 查看进程使用情况, 关注 swap 了多少

```sh
$cat smaps | egrep '^(Swap|Size)'
Size: 584 kB
Swap: 0 kB
Size: 4 kB
Swap: 4 kB
Size: 4 kB
Swap: 0 kB
Size: 462044 kB
Swap: 462008 kB
Size: 21392 kB
Swap: 0 kB
```

- 当出现百 MB 甚至 GB 大小的 SWAP 时, 就要考虑增加机器内存或者切换主从来解决问题

#### 内存大页

- 收益: 内存分配更高效
- 缺点: 写时复制要将一大页内存全部复制, 即使只修改了 100B

解决方法: 关闭内存大页

- 查看:

```
cat /sys/kernel/mm/transparent_hugepage/enabled
```

- 关闭:

```
echo never /sys/kernel/mm/transparent_hugepage/enabled
```

## 评论区收获和思考

### Redis 变慢的总结:

1. 获取 Redis 实例在当前环境下的基线性能。
2. 是否用了慢查询命令？如果是的话，就使用其他命令替代慢查询命令，或者把聚合计算命令放在客户端做。
3. 是否对过期 key 设置了相同的过期时间？对于批量删除的 key，可以在每个 key 的过期时间上加一个随机数，避免同时删除。
4. 是否存在 bigkey？ 对于 bigkey 的删除操作，如果你的 Redis 是 4.0 及以上的版本，可以直接利用异步线程机制减少主线程阻塞；如果是 Redis 4.0 以前的版本，可以使用 SCAN 命令迭代删除；对于 bigkey 的集合查询和聚合操作，可以使用 SCAN 命令在客户端完成。
5. Redis AOF 配置级别是什么？业务层面是否的确需要这一可靠性级别？如果我们需要高性能，同时也允许数据丢失，可以将配置项 no-appendfsync-on-rewrite 设置为 yes，避免 AOF 重写和 fsync 竞争磁盘 IO 资源，导致 Redis 延迟增加。当然， 如果既需要高性能又需要高可靠性，最好使用高速固态盘作为 AOF 日志的写入盘。
6. Redis 实例的内存使用是否过大？发生 swap 了吗？如果是的话，就增加机器内存，或者是使用 Redis 集群，分摊单机 Redis 的键值对数量和内存压力。同时，要避免出现 Redis 和其他内存需求大的应用共享机器的情况。
7. 在 Redis 实例的运行环境中，是否启用了透明大页机制？如果是的话，直接关闭内存大页机制就行了。
8. 是否运行了 Redis 主从集群？如果是的话，把主库实例的数据量大小控制在 2~4GB，以免主从复制时，从库因加载大的 RDB 文件而阻塞。
9. 是否使用了多核 CPU 或 NUMA 架构的机器运行 Redis 实例？使用多核 CPU 时，可以给 Redis 实例绑定物理核；使用 NUMA 架构时，注意把 Redis 实例和网络中断处理程序运行在同一个 CPU Socket 上。
10. 观察运行环境有没有恼人的邻居, 考虑做迁移

### Kaito 的 CheckList

关于如何分析、排查、解决 Redis 变慢问题，我总结的 checklist 如下：

1. 使用复杂度过高的命令（例如 SORT/SUION/ZUNIONSTORE/KEYS），或一次查询全量数据（例如 LRANGE key 0 N，但 N 很大）
	- 分析：
	a) 查看 slowlog 是否存在这些命令
	b) Redis 进程 CPU 使用率是否飙升（聚合运算命令导致）
	- 解决：
	a) 不使用复杂度过高的命令，或用其他方式代替实现（放在客户端做）
	b) 数据尽量分批查询（LRANGE key 0 N，建议 N<=100，查询全量数据建议使用 HSCAN/SSCAN/ZSCAN）
2. 操作 bigkey
	- 分析：
	a) slowlog 出现很多 SET/DELETE 变慢命令（bigkey 分配内存和释放内存变慢）
	b) 使用 redis-cli -h $host -p $port --bigkeys 扫描出很多 bigkey
	- 解决：
	a) 优化业务，避免存储 bigkey
	b) Redis 4.0+ 可开启 lazy-free 机制
3. 大量 key 集中过期
	- 分析：
	a) 业务使用 EXPIREAT/PEXPIREAT 命令
	b) Redis info 中的 expired_keys 指标短期突增
	- 解决：
	a) 优化业务，过期增加随机时间，把时间打散，减轻删除过期 key 的压力
	b) 运维层面，监控 expired_keys 指标，有短期突增及时报警排查
4. Redis 内存达到 maxmemory
	- 分析：
	a) 实例内存达到 maxmemory，且写入量大，淘汰 key 压力变大
	b) Redis info 中的 evicted_keys 指标短期突增
	- 解决：
	a) 业务层面，根据情况调整淘汰策略（随机比 LRU 快）
	b) 运维层面，监控 evicted_keys 指标，有短期突增及时报警
	c) 集群扩容，多个实例减轻淘汰 key 的压力
5. 大量短连接请求
	- 分析：Redis 处理大量短连接请求，TCP 三次握手和四次挥手也会增加耗时
	- 解决：使用长连接操作 Redis
6. 生成 RDB 和 AOF 重写 fork 耗时严重
	- 分析：
	a) Redis 变慢只发生在生成 RDB 和 AOF 重写期间
	b) 实例占用内存越大，fork 拷贝内存页表越久
	c) Redis info 中 latest_fork_usec 耗时变长
	- 解决：
	a) 实例尽量小
	b) Redis 尽量部署在物理机上
	c) 优化备份策略（例如低峰期备份）
	d) 合理配置 repl-backlog 和 slave client-output-buffer-limit，避免主从全量同步
	e) 视情况考虑关闭 AOF
	f) 监控 latest_fork_usec 耗时是否变长
7. AOF 使用 awalys 机制
	- 分析：磁盘 IO 负载变高
	- 解决：
	a) 使用 everysec 机制
	b) 丢失数据不敏感的业务不开启 AOF
8. 使用 Swap
	- 分析：
	a) 所有请求全部开始变慢
	b) slowlog 大量慢日志
	c) 查看 Redis 进程是否使用到了 Swap
	- 解决：
	a) 增加机器内存
	b) 集群扩容
	c) Swap 使用时监控报警
9. 进程绑定 CPU 不合理
	- 分析：
	a) Redis 进程只绑定一个 CPU 逻辑核
	b) NUMA 架构下，网络中断处理程序和 Redis 进程没有绑定在同一个 Socket 下
	- 解决：
	a) Redis 进程绑定多个 CPU 逻辑核
	b) 网络中断处理程序和 Redis 进程绑定在同一个 Socket 下
10. 开启透明大页机制
	- 分析：生成 RDB 和 AOF 重写期间，主线程处理写请求耗时变长（拷贝内存副本耗时变长）
	- 解决：关闭透明大页机制
11. 网卡负载过高
	- 分析：
	a) TCP/IP 层延迟变大，丢包重传变多
	b) 是否存在流量过大的实例占满带宽
	- 解决：
	a) 机器网络资源监控，负载过高及时报警
	b) 提前规划部署策略，访问量大的实例隔离部署

总之，Redis 的性能与 CPU. 内存. 网络. 磁盘都息息相关，任何一处发生问题，都会影响到 Redis 的性能。

主要涉及到的包括业务使用层面和运维层面：业务人员需要了解 Redis 基本的运行原理，使用合理的命令、规避 bigke 问题和集中过期问题。运维层面需要 DBA 提前规划好部署策略，预留足够的资源，同时做好监控，这样当发生问题时，能够及时发现并尽快处理。
