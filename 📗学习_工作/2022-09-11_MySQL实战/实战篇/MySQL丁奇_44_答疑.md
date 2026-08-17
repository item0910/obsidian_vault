---
tags: 归档笔记/学习笔记/MySQL
title: 44_答疑
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 答疑

### Join 的写法

用 where 还是 on 呢?

比如:

```sql
create table a(f1 int, f2 int, index(f1))engine=innodb;
create table b(f1 int, f2 int)engine=innodb;
insert into a values(1,1),(2,2),(3,3),(4,4),(5,5),(6,6);
insert into b values(3,3),(4,4),(5,5),(6,6),(7,7),(8,8);
```

```sql
select * from a left join b on(a.f1=b.f1) and (a.f2=b.f2); /*Q1*/
select * from a left join b on(a.f1=b.f1) where (a.f2=b.f2);/*Q2*/
```

![[附件/image/44_答疑-1663961106153.jpeg]]
语句 1 的执行顺序
1. 把表 a 的内容读入 join_buffer 中。因为是 select * ，所以字段 f1 和 f2 都被放入 join_buffer 了。
2. 顺序扫描表 b，对于每一行数据，判断 join 条件（也就是 (a.f1=b.f1) and (a.f1=1)）是否满足，满足条件的记录, 作为结果集的一行返回。如果语句中有 where 子句，需要先判断 where 部分满足条件后，再返回。
3. 表 b 扫描完成后，对于没有被匹配的表 a 的行（在这个例子中就是 (1,1)、(2,2) 这两行），把剩余字段补上 NULL，再放入结果集中。

![[附件/image/44_答疑-1663961091701.jpeg]]

所以语句 2 的执行顺序
1. 顺序扫描表 b，每一行用 b.f1 到表 a 中去查，
2. 匹配到记录后判断 a.f2=b.f2 是否满足，满足条件的话就作为结果集的一部分返回。

结论:
1. 用 left join, 有区别. 其实两条语句语意也是不一样的.
2. 用 join , 没区别.(而且某些情况 MySQL 优化器自己会改写语句)

### simple nested loop join 的性能问题

BNL 算法的执行逻辑是：
1. 首先，将驱动表的数据全部读入内存 join_buffer 中，这里 join_buffer 是无序数组；
2. 然后，顺序遍历被驱动表的所有行，每一行数据都跟 join_buffer 中的数据进行匹配，匹配成功则作为结果集的一部分返回。

Simple Nested Loop Join 算法的执行逻辑是：顺序取出驱动表中的每一行数据，到被驱动表去做全表扫描匹配，匹配成功则作为结果集的一部分返回。

Simple Nested Loop Join 算法，其实也是把数据读到内存里，然后按照匹配条件进行判断，为什么性能差距会这么大呢？

解释这个问题，需要用到 MySQL 中索引结构和 Buffer Pool 的相关知识点：在对被驱动表做全表扫描的时候，如果数据没有在 Buffer Pool 中，就需要等待这部分数据从磁盘读入；

从磁盘读入数据到内存中，会影响正常业务的 Buffer Pool 命中率，而且这个算法天然会对被驱动表的数据做多次访问，更容易将这些数据页放到 Buffer Pool 的头部（请参考第 35 篇文章中的相关内容)；

即使被驱动表数据都在内存中，每次查找“下一个记录的操作”，都是类似指针操作。而 join_buffer 中是数组，遍历的成本更低。所以说，BNL 算法的性能会更好。

### distinct 和 group by 的性能

如果只需要去重，不需要执行聚合函数，distinct 和 group by 哪种效率高一些呢？

```sql
select a from t group by a order by null;
select distinct a from t;
```

标准写法

```sql
select a,count(*) from t group by a order by null;
```

没有了 count(* ) 以后，也就是不再需要执行“计算总数”的逻辑时，第一条语句的逻辑就变成是：按照字段 a 做分组，相同的 a 的值只返回一行。而这就是 distinct 的语义，所以不需要执行聚合函数时，distinct 和 group by 这两条语句的语义和执行流程是相同的，因此执行性能也相同。

执行逻辑
1. 创建一个临时表，临时表有一个字段 a，并且在这个字段 a 上创建一个唯一索引；
	1. 遍历表 t，依次取数据插入临时表中：如果发现唯一键冲突，就跳过；
	2. 否则插入成功；遍历完成后，将临时表作为结果集返回给客户端。

### 备库自增主键的问题

两个 INSERT 语句在主备库的执行顺序不同，自增主键字段的值会不一致吗。

不会, 因为 binlog 是这样写的

```sql
SET INSERT_ID=2;
语句B；
SET INSERT_ID=1;
语句A；
```

## 答疑思考

他查看了一下 innodb_trx，发现这个事务的 trx_id 是一个很大的数（281479535353408），而且似乎在同一个 session 中启动的会话得到的 trx_id 是保持不变的。当执行任何加写锁的语句后，trx_id 都会变成一个很小的数字（118378）。

你可以通过实验验证一下，然后分析看看，事务 id 的分配规则是什么，以及 MySQL 为什么要这么设计呢？
