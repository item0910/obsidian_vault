---
tags: 归档笔记/学习笔记/MySQL
title: 15_日志和索引的答疑
date: 2022-09-13
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

## 日志和索引的答疑

![](附件/image/MySQL丁奇_15_日志答疑和设置关注数据库-1695637640774.jpeg)
有关两阶段提交的问题

![](附件/image/MySQL丁奇_15_日志答疑和设置关注数据库-1695637567422.jpeg)

### 分析两阶段的过程出现异常重启会发生什么现象

1. 在 A 点发生了崩溃. 因为已经写入了 redo log 而没有写入 binlog, 事务会回滚.
2. 在 B 点发生了崩溃, 则判断 binlog 是否完整, 如果完整, 则提交事务; 否则, 回滚. 这里可以看做 binlog 已经完成, 所以提交事务.

### 1. 如何知道 binlog 是完整的呢?

- statement 格式的 binlog，最后会有 COMMIT；
- row 格式的 binlog，最后会有一个 XID event。

另外，在 MySQL 5.6.2 版本以后，还引入了 binlog-checksum 参数，用来验证 binlog 内容的正确性。对于 binlog 日志由于磁盘原因，可能会在日志中间出错的情况，MySQL 可以通过校验 checksum 的结果来发现。所以，MySQL 还是有办法验证事务 binlog 的完整性的。

### 2. redo log 和 binlog 是怎么关联起来的?

他们有一个共同的数据段 XID, 当崩溃回复的时候, 会按顺序扫描 redo log:

- 如果碰到既有 prepare, 又有 commit 的 redo log 就直接提交
- 如果碰到只有 prepare, 没有 commit 的 redo log 就拿着 XID 去 binlog 找对应的事务. 如果已经提交了, 那么提交事务, 如果还没有, 那么回滚事务 ^f12a45

### 3. 为什么要这么设计?

有了落盘的 redo log , 备库就可以根据它进行恢复. 而主库只要找到对应的 binlog, 也可以恢复, 使主从一致.

### 4. 为什么要两阶段提交, 干脆先 redo log 写完, 再写 binlog, 恢复的时候要求两个日志都完整不就行了吗?

redo log 写完后不能回滚 (如果允许会影响其它事务的更新), 所以写完 redo log 直接提交然后写 binlog , 如果这时候出了问题, 就数据不一致了.

### 5. 只用 binlog 行不行?写内存 -> 写 binlog, 提交事务

binlog 没有能力恢复数据页

![](附件/image/MySQL丁奇_15_日志答疑和设置关注数据库-1695637701748.jpeg)
比如在图中 的位置 crash 了, 此时, biglog1 认为已经 commit 了, 无法回滚, 而 biglog2 没有 commit, 可以回滚, 就会造成这一页数据页的丢失.

### 6. 只用 redo log 行不行?

1. redo log 是循环写的, 所以无法保存全历史记录.
2. MySQL 一开始就有 binlog 伴随, binlog 被用在了很多地方.
3. 还有一些公司的异构系统就是靠消费 binlog 来构建自己的数据, 关掉 binlog 就无法输入数据了.

### 7. redo log 一般多大?

TB 级别的一般 4 * 1GB ; 太小会导致很快被写满, 然后就要刷脏页, 影响性能.

### 8. 数据最终落盘 是怎么更新的

内存中的脏页 (与磁盘数据不一致的) 写盘, 甚至跟 redo log 没有关系.

崩溃时, 如果系统判断一个数据页可能在崩溃是丢失了数据, 就会把这个页读到内存, 由 redo log 更新内容.

### 9. redo log buffer 是什么, 是先修改内存, 还是先写 redo log 文件?

```sql
begin;
insert into t1 ...
insert into t2 ...
commit;
```

这个事务要往两个表中插入记录，插入数据的过程中，生成的日志都得先保存起来，但又不能在还没 commit 的时候就直接写到 redo log 文件里。

所以 redo log buffer 就是一块内存，用来先存 redo 日志的。也就是说，在执行第一个 insert 的时候，数据的内存被修改了，redo log buffer 也写入了日志。

但是真正把日志 redo log 落盘的, 是在 commit 的时候做的.

### 业务设计问题

业务上有这样的需求，A、B 两个用户，如果互相关注，则成为好友。设计上是有两张表，一个是 like 表，一个是 friend 表，like 表有 user_id、liker_id 两个字段，我设置为复合唯一索引即 uk_user_id_liker_id。语句执行逻辑是这样的：

以 A 关注 B 为例：第一步，先查询对方有没有关注自己（B 有没有关注 A）select * from like where user_id = B and liker_id = A;

如果有，则成为好友 insert into friend;

没有，则只是单向关注关系 insert into like;

但是如果 A、B 同时关注对方，会出现不会成为好友的情况。因为上面第 1 步，双方都没关注对方。第 1 步即使使用了排他锁也不行，因为记录不存在，行锁无法生效。请问这种情况，在 MySQL 锁层面有没有办法处理？

```sql
CREATE TABLE `like` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `liker_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id_liker_id` (`user_id`,`liker_id`)
) ENGINE=InnoDB;

CREATE TABLE `friend` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `friend_1_id` int(11) NOT NULL,
  `friend_2_id` int(11) NOT NULL,
  UNIQUE KEY `uk_friend` (`friend_1_id`,`friend_2_id`),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
```

我把他的疑问翻译一下，在并发场景下，同时有两个人，设置为关注对方，就可能导致无法成功加为朋友关系。

![](附件/image/MySQL丁奇_15_日志答疑和设置关注数据库-1695637736132.jpeg)
由于一开始 A 和 B 之间没有关注关系，所以两个事务里面的 select 语句查出来的结果都是空。

因此，session 1 的逻辑就是“既然 B 没有关注 A，那就只插入一个单向关注关系”。session 2 也同样是这个逻辑。

这个结果对业务来说就是 bug 了。因为在业务设定里面，这两个逻辑都执行完成以后，是应该在 friend 表里面插入一行记录的。

如提问里面说的，“第 1 步即使使用了排他锁也不行，因为记录不存在，行锁无法生效”。

不过，我想到了另外一个方法，来解决这个问题。首先，要给“like”表增加一个字段，比如叫作 relation_ship，并设为整型，取值 1、2、3。

值是 1 的时候，表示 user_id 关注 liker_id;

值是 2 的时候，表示 liker_id 关注 user_id;

值是 3 的时候，表示互相关注。

然后，当 A 关注 B 的时候，逻辑改成如下所示的样子：应用代码里面，比较 A 和 B 的大小，如果 A < B, 就执行下面的逻辑

```sql
mysql> begin; /*启动事务*/
insert into `like`(user_id, liker_id, relation_ship) values(A, B, 1) on duplicate key update relation_ship=relation_ship | 1;
select relation_ship from `like` where user_id=A and liker_id=B;
/*代码中判断返回的 relation_ship，
  如果是1，事务结束，执行 commit
  如果是3，则执行下面这两个语句：
  */
insert ignore into friend(friend_1_id, friend_2_id) values(A,B);
commit;
```

如果 A > B, 就执行下面的逻辑

```sql
mysql> begin; /*启动事务*/
insert into `like`(user_id, liker_id, relation_ship) values(B, A, 2) on duplicate key update relation_ship=relation_ship | 2;
select relation_ship from `like` where user_id=B and liker_id=A;
/*代码中判断返回的 relation_ship，
  如果是2，事务结束，执行 commit
  如果是3，则执行下面这两个语句：
*/
insert ignore into friend(friend_1_id, friend_2_id) values(B,A);
commit;
```

这个设计里，让“like”表里的数据保证 user_id < liker_id，这样不论是 A 关注 B，还是 B 关注 A，在操作“like”表的时候，如果反向的关系已经存在，就会出现行锁冲突。

然后，insert … on duplicate 语句，确保了在事务内部，执行了这个 SQL 语句后，就强行占住了这个行锁，之后的 select 判断 relation_ship 这个逻辑时就确保了是在行锁保护下的读操作。

操作符 “|” 是按位或，连同最后一句 insert 语句里的 ignore，是为了保证重复调用时的幂等性。

这样，即使在双方“同时”执行关注操作，最终数据库里的结果，也是 like 表里面有一条关于 A 和 B 的记录，而且 relation_ship 的值是 3， 并且 friend 表里面也有了 A 和 B 的这条记录。

## 日志和索引的答疑思考

- 有如下操作

```sql
mysql> CREATE TABLE `t` (
`id` int(11) NOT NULL primary key auto_increment,
`a` int(11) DEFAULT NULL
) ENGINE=InnoDB;
insert into t values(1,2);
```

现在要执行:

```sql
mysql> update t set a=2 where id=1;
```

![](附件/image/MySQL丁奇_15_日志答疑和设置关注数据库-1695637763380.jpeg)
1. 更新都是先读后写的，MySQL 读出数据，发现 a 的值本来就是 2，不更新，直接返回，执行结束；
2. MySQL 调用了 InnoDB 引擎提供的“修改为 (1,2)”这个接口，但是引擎发现值与原来相同，不更新，直接返回；
3. InnoDB 认真执行了“把这个值修改成 (1,2)" 这个操作，该加锁的加锁，该更新的更新。

你觉得实际情况会是以上哪种呢？你可否用构造实验的方式，来证明你的结论？进一步地，可以思考一下，MySQL 为什么要选择这种策略呢？

回答:

![[附件/image/15_日志答疑和设置关注数据库.jpg]]

1. session 被阻塞, 所以排除不更新的情况

![[附件/image/15_日志答疑和设置关注数据库-1.jpg]]

session A 的第二个 select 语句是一致性读（快照读)，它是不能看见 session B 的更新的。现在它返回的是 (1,3)，表示它看见了某个新的版本，这个版本只能是 session A 自己的 update 语句做更新的时候生成。

信息只有 id = 1, a = 3 需不需要修改, MySQL 是判断不出来的.

![[附件/image/15_日志答疑和设置关注数据库-2.jpg]]

根据既然读了数据, 就会判断的原则, 这里就没有发生修改操作, SessionA 自然只能读到自己版本的数据了.
