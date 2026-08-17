---
tags: 归档笔记/学习笔记/MySQL
title: 06_全局锁和表锁
date: 2022-09-10
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 学前:

锁分为: 全局锁, 表锁和行锁, 本章不会涉及锁的具体实现细节

## 全局锁和表锁

### 全局锁的使用和场景

`Flush tables with read lock (FTWRL)`

之后全局的数据更新, 数据定义 (DDL) 和更新类事务的提交语句都会被阻塞

- 全局锁的使用场景是全库逻辑备份.

#### 全局锁的风险点以及解决方法

- 如果全库只读: ^458dbc
	- 主库执行, 全局业务停摆
	- 从库执行, 备份期间从库不能执行主库发来的 binlog, 导致主从延迟.
		![[附件/image/06_全局锁和表锁-1.jpg]]
	备份为什么要加锁? 防止数据不一致

- 官方自带的逻辑备份工具是 mysqldump。当 mysqldump 使用参数–single-transaction 的时候，导数据之前就会启动一个事务，来确保拿到一致性视图。而由于 MVCC 的支持，这个过程中数据是可以正常更新的。 那么为什么还需要 FTWRL?

有的引擎不支持事务, 比如 MyISAM, 那么就只能每次取到最新的数据

所以 `-single-transaction` 只适用于支持事务的引擎.

- 为什么不使用 set global readonly = true 呢, 也能让全库进入只读状态.
	1. 有些场景 readonly 会被用来做其它用途, 比如判断主从.
	2. FTWRL 出现异常, 数据库会释放这个全局锁, 可以恢复到正常状态. 但 readonly 数据库就会一直保持, 风险比较高

不过, 就算没有全局锁, 给数据库加字段也不是一帆风顺的, 还有表锁.

### 表锁

MySQL 里面表级别的锁有两种：一种是表锁，一种是元数据锁（meta data lock，MDL)。每对表进行一次 DML 或者 DDL 时, 都会申请一次 MDL 锁. ^fd0333

- 表锁的语法是 `lock tables T read/write` 可以用 unlock 主动释放

举个例子, 如果在某个线程 A 中执行 `lock tables t1 read, t2 write`; 这个语句，则其他线程写 t1、读写 t2 的语句都会被阻塞。同时，线程 A 在执行 unlock tables 之前，也只能执行读 t1、读写 t2 的操作。连写 t1 都不允许，也不能访问其他表。

- **MDL** 不需要限时使用, 在访问一个表时自动被加上, MDL 就能保证这个线程的读写正确性. 如果 A 线程正在遍历表中的数据, 执行期间另一个线程对 A 进行操作了, 删了一列, 那么拿到的结果跟表对不上, 显然不可以.

   因此，在 MySQL 5.5 版本中引入了 MDL，当对一个表做增删改查操作的时候，加 MDL 读锁；当要对表做结构变更操作的时候，加 MDL 写锁。

  - 读锁之间不互斥，因此你可以有多个线程同时对一张表的数据增删改查 (DML)。
  - 读写锁之间、写锁之间是互斥的，用来保证变更表结构操作的安全性。因此，如果有两个线程要同时给一个表加字段，其中一个要等另一个执行完才能开始执行。

#### 加表锁导致真个库挂掉的案例

![[附件/image/06_全局锁和表锁.jpg]]
老师的解释:

```
我们可以看到 session A 先启动，这时候会对表 t 加一个 MDL 读锁。

由于 session B 需要的也是 MDL 读锁，因此可以正常执行。

之后 session C 会被 blocked，是因为 session A 的 MDL 读锁还没有释放，而 session C 需要 MDL 写锁，因此只能被阻塞。

如果只有 session C 自己被阻塞还没什么关系，但是之后所有要在表 t 上新申请 MDL 读锁的请求也会被 session C 阻塞。

前面我们说了，所有对表的增删改查操作都需要先申请 MDL 读锁，就都被锁住，等于这个表现在完全不可读写了。

```

A 获取了 MDL 读锁, B 没问题 (读锁共享), C 被阻塞, 他需要 MDL 写锁, D 也被阻塞, 因为写锁优先级高于读锁, C 后面的想获取读锁的线程要排队等待 C 拿到写锁并完成事务释放.

申请 MDL 锁的操作会形成一个队列，队列中写锁获取优先级高于读锁。一旦出现写锁等待，不但当前操作会被阻塞，同时还会阻塞后续该表的所有操作。事务一旦申请到 MDL 锁后，直到事务执行完才会将锁释放。（这里有种特殊情况如果事务中包含 DDL 操作，mysql 会在 DDL 操作语句执行后，隐式提交 commit，以保证该 DDL 语句操作作为一个单独的事务存在，同时也保证元数据排他锁的释放，例如 id 44 的语句改为

```sql
begin;
alter table testok add z varchar(10) not Null;
select * from testok;
```

此时一旦 alter 语句执行完成会马上提交事务（autocommit=1），后面的 select 就在本次事务之外，其执行完成后不会持有读锁）

- 网友:
基于文中的例子 MDL（metadata lock)，自己做了一个实验（稍微有一些小改动在 session D 上），

`session A: begin; select * from t limit 1; 最先启动sessionA `

`session B: begin; select * from t limit 1; 紧接着启动sessionB `

`session C: alter table t add f int; 然后再是启动sessionC `

`session D: begin; select * from t limit 1; 最后是启动sessionD `

如文中例子，session A 和 B 正常启动，然后 session C 被 block，之后 session D 也被 block。当把 session A 和 session B 都 commit 掉后，发现 session C 依然是 block 的（被 session D 阻塞），只有当把 session D 也 commit 掉后，session C 才执行下去。同样的实验，重复了三遍，结果也是一样。

session D 会“插队”到 session C 前面，也就是原本的队列结构竟然出现了 “插队”现象

这个问题就要涉及到 online ddl 了。

由于 ddl 执行时如果锁表的话会严重影响性能，不锁表又难搞定操作期间 dml 语句的影响，于是 mysql 推出了全新的 online ddl 概念，即通过：

1. 先拿到 MDL 写锁
2. 降级成 MDL 读锁, 此时可以读读不互斥
3. 完成 DDL 的操作
4. 升级成 MDL 写锁
5. 释放 MDL 锁

5 个步骤，第一步拿读锁是为确保没有其他 ddl 语句在执行；第三步是自己申请一块空间开始改表结构、填数据；等填好了之后，执行第四步，这期间由于持有读锁，可以确保不会有其他 ddl 语句造成不一致性；最后等拿到写锁，把表一替代就搞定了。

这样就看出来端倪了。上图中 session A，Bcommit 后，sessionC 确实拿到了写锁，只不过由于锁降级，令 sessionD 拿到了读锁。但 session D 没有 commit，因此 session C 在执行 online commit 到第三步后，又给阻塞了。所以就出现了类似于“插队”的现象。

如果想验证的话，可以再开一个 begin;select...的 session，就叫 sessionE 吧。然后让刚刚没 commit 的 session D commit 一下，会发现这次 session C 并没有阻塞 (代表他获取锁的优先级比较高)

- 结论:

>事务中的 MDL 锁, 在语句执行开始时申请, 但是语句结束后不会马上释放, 必须要等到事务结束后才释放.
>
>如果某个表上的查询语句频繁，而且客户端有重试机制，也就是说超时后会再起一个新 session 再请求的话，这个库的线程很快就会爆满。

- 分析: 如果给安全的给小标加字段?
	- 首先要解决长事务提交的问题, 在 MySQL 的 information_schema 库的 innodb_trx 表中，你可以查到当前执行中的事务。如果你要 DDL 的表有长事务在执行, 要么 kill 掉它, 要么考虑暂停 DDL.
	- 如果要变更一个热点表, 给它加数据, 在 alter table 语句里面设定等待时间，如果在这个指定的等待时间里面能够拿到 MDL 写锁最好，拿不到也不要阻塞后面的业务语句，先放弃。之后开发人员或者 DBA 再通过重试命令重复这个过程.

	```sql
	ALTER TABLE tbl_name NOWAIT add column ...
	ALTER TABLE tbl_name WAIT N add column ... 
	```

### 小结

- 全局备份需要锁时, 建议使用 `–single-transaction`, 当然, 引擎要支持事务.
- 如果你发现你的应用程序里有 lock tables 这样的语句，你需要追查一下，比较可能的情况是：
	- 要么是你的系统现在还在用 MyISAM 这类不支持事务的引擎，那要安排升级换引擎；
	- 要么是你的引擎升级了，但是代码还没升级。我见过这样的情况，最后业务开发就是把 lock tables 和 unlock tables 改成 begin 和 commit，问题就解决了。

## 学后思考

- 备份一般都会在备库上执行，你在用 `–single-transaction` 方法做逻辑备份的过程中，如果主库上的一个小表做了一个 DDL，比如给一个表上加了一列。这时候，从备库上会看到什么现象呢？
