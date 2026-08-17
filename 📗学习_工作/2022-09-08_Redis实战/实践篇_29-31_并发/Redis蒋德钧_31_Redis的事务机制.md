---
title: 31_Redis的事务机制
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 事务的 ACID 属性要求

原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）和持久性（Durability）
- 原子性: 第一重要的属性, 多个操作必须一次性完成
- 一致性: 各个数据库数据一致
- 隔离性: 发生在并发时, 其它操作无法读写正在事务中的数据
- 持久性: 事务的发生要被持久化保留下来.

## Redis 对事务 ACID 的支持

### 1. Redis 如何实现事务

![[附件/image/31_Redis的事务机制.jpg]]

```sh
#开启事务
127.0.0.1:6379> MULTI
OK
#将a:stock减1，
127.0.0.1:6379> DECR a:stock
QUEUED
#将b:stock减1
127.0.0.1:6379> DECR b:stock
QUEUED
#实际执行事务
127.0.0.1:6379> EXEC
1) (integer) 4
2) (integer) 9
```

### 2. Redis 保证事务的哪些属性

#### 原子性讨论:

- 如果命令本身有错, 那么事务不会被执行. 可以保证原子性.

	```sh
	#开启事务
	127.0.0.1:6379> MULTI
	OK
	#发送事务中的第一个操作，但是Redis不支持该命令，返回报错信息
	127.0.0.1:6379> PUT a:stock 5
	(error) ERR unknown command `PUT`, with args beginning with: `a:stock`, `5`, 
	#发送事务中的第二个操作，这个操作是正确的命令，Redis把该命令入队
	127.0.0.1:6379> DECR b:stock
	QUEUED
	#实际执行事务，但是之前命令有错误，所以Redis拒绝执行
	127.0.0.1:6379> EXEC
	(error) EXECABORT Transaction discarded because of previous errors.
	```

- 如果命令没错, 事务操作入队时，命令和操作的数据类型不匹配，但 Redis 实例没有检查出错误。就会破坏原子性

	```sh
	#开启事务
	127.0.0.1:6379> MULTI
	OK
	#发送事务中的第一个操作，LPOP命令操作的数据类型不匹配，此时并不报错
	127.0.0.1:6379> LPOP a:stock
	QUEUED
	#发送事务中的第二个操作
	127.0.0.1:6379> DECR b:stock
	QUEUED
	#实际执行事务，事务第一个操作执行报错
	127.0.0.1:6379> EXEC
	1) (error) WRONGTYPE Operation against a key holding the wrong kind of value
	2) (integer) 8
	```

- Redis 不提供回滚, 只提供 DISCARD 来 放弃事务执行.

	```sh
	#读取a:stock的值4
	127.0.0.1:6379> GET a:stock
	"4"
	#开启事务
	127.0.0.1:6379> MULTI 
	OK
	#发送事务的第一个操作，对a:stock减1
	127.0.0.1:6379> DECR a:stock
	QUEUED
	#执行DISCARD命令，主动放弃事务
	127.0.0.1:6379> DISCARD
	OK
	#再次读取a:stock的值，值没有被修改
	127.0.0.1:6379> GET a:stock
	"4"
	```

- 在执行事务中途, Redis 实例发生故障
	- 这时如果有 AOF 日志, 那么可以从日志中查询事务的操作, 将其修改, 可以保证原子性; 如果没有日志, 那么就无从谈起了.
- 因为原子性无法保证, 建议严格按照 Redis 的命令规范进行程序开发，并且通过 code review 确保命令的正确性

#### 一致性: 是否能保证主从一致

- 命令入队就报错:
	- 可以保证一致性
- 命令执行时报错
	- 有错的命令不会被执行, 可以保证一致性
- 执行时实例故障
	- 有 RDB, 因为 RDB 不会在事务中执行, 可以保证一致性
	- 有 AOF, 可以恢复, 可以保证一致性: 用 redis-check-aof 清除事务中已经执行的操作.
	- 都没有的话, 反正数据库都没了, 那么就是一致的.

#### 隔离性: 是否能保证不被并发弄错

- WATCH 机制: 在事务开始前判断检测的数据有没有发生变化, 如果变化了就不执行事务了.
- 情况 1: 并发操作在事务执行之前发生:
	![[附件/image/31_Redis的事务机制-1.jpg]]
- 情况 2: 并发操作在 EXEC 之后, 因为 Redis 是单线程的, 一定会先把事务执行完才执行下一个操作, 所以可以保证隔离
	![[附件/image/31_Redis的事务机制-2.jpg]]

#### 持久性: 是否能保证数据被保存

因为 Redis 是内存数据库, 是否持久化取决于 Redis 的持久化配置
- 如果有 RDB, 那么如果事务执行后还没有记录到 RDB, 就不能保证持久化.
- 如果有 AOF, 那么根据 AOF 的配置情况, no, everysec, always, 都会存在丢失的情况, 持久性无法完全保证.

## 评论区收获和思考

- 如果 Redis 发生实例故障, 而 Redis 采用了 RDB 机制, 那么事务的原子性还能保证吗
	- 答: 可以保证原子性.(RDB 快照存在的情况下)
