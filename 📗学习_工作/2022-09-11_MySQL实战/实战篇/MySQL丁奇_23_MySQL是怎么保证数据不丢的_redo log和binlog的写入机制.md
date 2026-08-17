---
tags: 归档笔记/学习笔记/MySQL
title: 23_MySQL是怎么保证数据不丢的_redo log和binlog的写法
date: 2022-09-16
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

只要 redo log 和 binlog 保证持久化到磁盘，就能确保 MySQL 异常重启后，数据可以恢复。那么如何保证他们正确持久化到了磁盘呢?

## MySQL 是怎么保证数据不丢的 redo log 和 binlog 的写法

### binlog 的写入机制

事务在运行时, 先写到 binlog cache, 提交时, 才写入 binlog ; 不管事务多大, 也要确保一次性写入.

系统给 binlog cache 分配了一片内存，每个线程一个，参数 binlog_cache_size 用于控制单个线程内 binlog cache 所占内存的大小。如果超过了这个参数规定的大小，就要暂存到磁盘。

![[附件/image/23_MySQL是怎么保证数据不丢的_redo log和binlog的写入机制-1663600154392.jpeg]]

可以看到，每个线程有自己 binlog cache，但是共用同一份 binlog 文件。

1. 图中的 write，指的就是指把日志写入到文件系统的 page cache，并没有把数据持久化到磁盘，所以速度比较快。
2. 图中的 fsync，才是将数据持久化到磁盘的操作。一般情况下，我们认为 fsync 才占磁盘的 IOPS。

write 和 fsync 的时机，是由参数 sync_binlog 控制的：

1. sync_binlog=0 的时候，表示每次提交事务都只 write，不 fsync；
2. sync_binlog=1 的时候，表示每次提交事务都会执行 fsync；
3. sync_binlog=N(N>1) 的时候，表示每次提交事务都 write，但累积 N 个事务后才 fsync。

在出现 IO 瓶颈的场景里，将 sync_binlog 设置成一个比较大的值，可以提升性能。在实际的业务场景中，考虑到丢失日志量的可控性，一般不建议将这个参数设成 0，比较常见的是将其设置为 100~1000 中的某个数值。

风险在于, 会丢失最近事务的 (还未写入 binlog fsync) 的日志

### redo log 的写入机制

基本流程, 先写到 redo log buffer , 再 write 到 page cache, 再持久化

但是事务没提交的时候, redo log 也是有机会被持久化的.

- redo log 的三种
![[附件/image/23_MySQL是怎么保证数据不丢的_redo log和binlog的写入机制-1663600667946.jpeg]]

1. 在 buffer 中, 也就是在进程内存中.
2. 在 page 上, 被 write 了, 但是还没有 fsync
3. 被持久化到磁盘里了.

前两个步骤 (写到 buffer, write 到 page) 都很快

为了控制 redo log 的写入策略，InnoDB 提供了 `innodb_flush_log_at_trx_commit` 参数，它有三种可能取值：

1. 设置为 0 的时候，表示每次事务提交时都只是把 redo log 留在 redo log buffer 中 ;
2. 设置为 1 的时候，表示每次事务提交时都将 redo log 直接持久化到磁盘；
3. 设置为 2 的时候，表示每次事务提交时都只是把 redo log 写到 page cache。

InnoDB 有一个后台线程，每隔 1 秒，就会把 redo log buffer 中的日志，调用 write 写到文件系统的 page cache，然后调用 fsync 持久化到磁盘。

注意，事务执行中间过程的 redo log 也是直接写在 redo log buffer 中的，这些 redo log 也会被后台线程一起持久化到磁盘。也就是说，一个没有提交的事务的 redo log，也是可能已经持久化到磁盘的。

下面这种场景也会使 buffer 中的被持久化

1. 一种是，redo log buffer 占用的空间即将达到 innodb_log_buffer_size 一半的时候，后台线程会主动写盘。注意，由于这个事务并没有提交，所以这个写盘动作只是 write，而没有调用 fsync，也就是只留在了文件系统的 page cache。
2. 并行事务提交的时候, 将这个 buffer 中的一起持久化了.`innodb_flush_log_at_trx_commit` 设置是 1 的情况下

每秒一次的刷盘就使 InnoDB 认为不需要刻意 fsync 这个 redo log 了, 只会在 commit 的时候写到 page cache

- 双 '1' 配置 : `sync_binlog` (1 意思每次 commit 都持久化) 和 `innodb_flush_log_at_trx_commit` 都设置成 1。也就是说，一个事务完整提交前，需要等待两次刷盘，一次是 redo log（prepare 阶段），一次是 binlog。

### 组提交

这里，我需要先和你介绍日志逻辑序列号（log sequence number，LSN）的概念。LSN 是单调递增的，用来对应 redo log 的一个个写入点。每次写入长度为 length 的 redo log， LSN 的值就会加上 length。

LSN 也会写到 InnoDB 的数据页中，来确保数据页不会被多次执行重复的 redo log。

如图 3 所示，是三个并发事务 (trx1, trx2, trx3) 在 prepare 阶段，都写完 redo log buffer，持久化到磁盘的过程，对应的 LSN 分别是 50、120 和 160。

![[附件/image/23_MySQL是怎么保证数据不丢的_redo log和binlog的写入机制-1663601206425.jpeg]]

组提交策略:

1. trx1 是第一个到达的，会被选为这组的 leader；

2. 等 trx1 要开始写盘的时候，这个组里面已经有了三个事务，这时候 LSN 也变成了 160；

3. trx1 去写盘的时候，带的就是 LSN=160，因此等 trx1 返回时，所有 LSN 小于等于 160 的 redo log，都已经被持久化到磁盘；

4. 这时候 trx2 和 trx3 就可以直接返回了。

组员越多, 越节约 IO, 所以 redo log 的持久化也被称为顺序写. ^21ea8a

******

![[附件/image/23_MySQL是怎么保证数据不丢的_redo log和binlog的写入机制-1663601453496.jpeg]]

因为 binlog 也是分两步写的 (write, fsync) 上图细化之后, 就变成了

![[附件/image/23_MySQL是怎么保证数据不丢的_redo log和binlog的写入机制-1663601495057.jpeg]]

这样的好处是, binlog 的 fsync 也是组提交的. 不过通常第三步的执行会比较快, 所以 binlog 的组提交效果不如 redo log, 如果你想提升这个效果, 可以通过设置 binlog_group_commit_sync_delay 和 binlog_group_commit_sync_no_delay_count 来实现。

1. binlog_group_commit_sync_delay 参数，表示延迟多少微秒后才调用 fsync;
2. binlog_group_commit_sync_no_delay_count 参数，表示累积多少次以后才调用 fsync。
这两者是或的关系, 比如把第一个设置为 0, 那还是会直接提交.

你就能理解了，WAL 机制主要得益于两个方面：

1. redo log 和 binlog 都是顺序写，磁盘的顺序写比随机写速度要快；
2. 组提交机制，可以大幅度降低磁盘的 IOPS 消耗。

所以, 如果你的 IO 出现了瓶颈, 那么可以通过那些方法来提升呢?

1. 设置 binlog_group_commit_sync_delay 和 binlog_group_commit_sync_no_delay_count 参数，减少 binlog 的写盘次数。这个方法是基于“额外的故意等待”来实现的，因此可能会增加语句的响应时间，但没有丢失数据的风险。
2. 将 sync_binlog 设置为大于 1 的值（比较常见是 100~1000）。这样做的风险是，主机掉电时会丢 binlog 日志。
3. 将 innodb_flush_log_at_trx_commit 设置为 2。这样做的风险是，主机掉电的时候会丢数据。

### 小结

1. 介绍 binlog 的写入机制
2. 介绍 redolog 的写入机制
3. 介绍了组提交, 并且重新理解了两阶段提交

## MySQL 是怎么保证数据不丢的 redo log 和 binlog 的写法思考

今天我留给你的思考题是：你的生产库设置的是“双 1”吗？ 如果平时是的话，你有在什么场景下改成过“非双 1”吗？你的这个操作又是基于什么决定的？另外，我们都知道这些设置可能有损，如果发生了异常，你的止损方案是什么？

1. 业务高峰期。一般如果有预知的高峰期，DBA 会有预案，把主库设置成“非双 1”。
2. 备库延迟，为了让备库尽快赶上主库。@永恒记忆和 @Second Sight 提到了这个场景。
3. 用备份恢复主库的副本，应用 binlog 的过程，这个跟上一种场景类似。
4. 批量导入数据的时候。

非双一推荐设置: innodb_flush_logs_at_trx_commit=2、sync_binlog=1000。
