---
tags: 归档笔记/学习笔记/MySQL
title: 30_加锁答疑
date: 2022-09-16
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

## 加锁答疑

### 1. 锁分析 1

```sql
begin;
select * from t where id>9 and id<12 order by id desc for update;
```

从右往左, 锁的依次顺序 (10, 15), (5, 10], (0, 5], 所以最终锁的范围 (0, 15)

### 2. 锁分析 2

```sql
begin;
select id from t where c in(5,20,10) lock in share mode;
```

先锁 5, 再锁 10, 最后锁 20

5: (0,5], (5,10], 10 退化, (0, 10)

同理:

10: (5, 15)

20: (15, 25)

如果还有语句:

```sql
select id from t where c in(5,20,10) order by c desc for update;
```

那么两个加锁的方向是相反的, 就会出现死锁.

### 3. 如何看死锁

1. 执行 `show engine innodb status` 命令得到的部分输出。这个命令会输出很多信息，有一节 LATESTDETECTED DEADLOCK，就是记录的最后一次死锁信息。
![[附件/image/30_加锁答疑-1663686931334.jpeg]]
- 这个结果分成三部分：
	- (1) TRANSACTION，是第一个事务的信息；
	- (2) TRANSACTION，是第二个事务的信息；
	- WE ROLL BACK TRANSACTION (1)，是最终的处理结果，表示回滚了第一个事务。
- 第一部分
	- WAITING FOR THIS LOCK TO BE GRANTED，表示的是这个事务在等待的锁信息；
	- index c of table `test`.`t`，说明在等的是表 t 的索引 c 上面的锁；
	- lock mode S waiting 表示这个语句要自己加一个读锁，当前的状态是等待中；
	- Record lock 说明这是一个记录锁；
	- n_fields 2 表示这个记录是两列，也就是字段 c 和主键字段 id；
	- 0: len 4; hex 0000000a; asc ;; 是第一个字段，也就是 c。值是十六进制 a，也就是 10；
	- 1: len 4; hex 0000000a; asc ;; 是第二个字段，也就是主键 id，值也是 10；
	- 这两行里面的 asc 表示的是，接下来要打印出值里面的“可打印字符”，但 10 不是可打印字符，因此就显示空格。
	- 第一个事务信息就只显示出了等锁的状态，在等待 (c=10,id=10) 这一行的锁。
	- 当然你是知道的，既然出现死锁了，就表示这个事务也占有别的锁，但是没有显示出来。别着急，我们从第二个事务的信息中推导出来。
- 第二部分
	- “ HOLDS THE LOCK(S)”用来显示这个事务持有哪些锁；
	- index c of table `test`.`t` 表示锁是在表 t 的索引 c 上；
	- hex 0000000a 和 hex 00000014 表示这个事务持有 c=10 和 c=20 这两个记录锁；
	- WAITING FOR THIS LOCK TO BE GRANTED，表示在等 (c=5,id=5) 这个记录锁。

- 从以上讯息中我们可知
	- “lock in share mode”的这条语句，持有 c=5 的记录锁，在等 c=10 的锁；
	- “for update”这个语句，持有 c=20 和 c=10 的记录锁，在等 c=5 的记录锁。

由于间隙锁是一个个加的，要避免死锁，对同一组资源，要按照尽量相同的顺序访问；

在发生死锁的时刻，for update 这条语句占有的资源更多，回滚成本更大，所以 InnoDB 选择了回滚成本更小的 lock in share mode 语句，来回滚。

### 4. 看锁等待

1. `show engine innodb status`

## 加锁答疑思考

所谓“间隙”，其实根本就是由“这个间隙右边的那个记录”定义的。那么，一个空表有间隙吗？这个间隙是由谁定义的？你怎么验证这个结论呢？

一个空表只有一个间隙, 例如执行:

```sql
begin;
select * from t where id>1 for update;
```

这个查询语句加锁的范围就是 next-key lock (-∞, supremum]。

![[附件/image/30_加锁答疑-1663689108573.jpeg]]

![[附件/image/30_加锁答疑-1663689218772.jpeg]]
