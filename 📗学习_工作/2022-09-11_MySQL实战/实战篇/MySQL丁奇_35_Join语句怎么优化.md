---
tags: 归档笔记/学习笔记/MySQL
title: 35_Join语句怎么优化
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-10-15
---

## 前言

有表

```sql
create table t1(id int primary key, a int, b int, index(a));
create table t2 like t1;
drop procedure idata;
delimiter ;;
create procedure idata()
begin
  declare i int;
  set i=1;
  while(i<=1000)do
    insert into t1 values(i, 1001-i, i);
    set i=i+1;
  end while;
  
  set i=1;
  while(i<=1000000)do
    insert into t2 values(i, i, i);
    set i=i+1;
  end while;

end;;
delimiter ;
call idata();
```

t1 的 a 有索引, 是逆序的一千条记录, t2 插入了 100 万条记录.

## Join 语句怎么优化

回表怎么查数据?

现在有查询如下:

```sql
select * from t1 where a>=1 and a<=100;
```

回表肯定是一行一行搜索主键索引的,

![[附件/image/35_Join语句怎么优化-1663712495227.jpeg]]

因为 a 是逆序对应主键的, 所以 a 顺序的话, id 的值就是随机的, 就会出现随机访问, 性能相对较差.

因为大多数的数据都是按照主键递增顺序插入得到的, 我们可以认为, 主键递增顺序, 与磁盘顺序读比较接近,能够提升性能.

### Multi-Range Read 优化

以上就是 MRR 的优化, 语句的执行流程变为:

1. 根据索引 a，定位到满足条件的记录，将 id 值放入 read_rnd_buffer 中 ;
2. 将 read_rnd_buffer 中的 id 进行递增排序；
3. 排序后的 id 数组，依次到主键 id 索引中查记录，并作为结果返回。

这里，read_rnd_buffer 的大小是由 read_rnd_buffer_size 参数控制的。如果步骤 1 中，read_rnd_buffer 放满了，就会先执行完步骤 2 和 3，然后清空 read_rnd_buffer。之后继续找索引 a 的下个记录，并继续循环。

另外需要说明的是，如果你想要稳定地使用 MRR 优化的话，需要设置 set optimizer_switch="mrr_cost_based=off"。（官方文档的说法，是现在的优化器策略，判断消耗的时候，会更倾向于不使用 MRR，把 mrr_cost_based 设置为 off，就是固定使用 MRR 了。）

流程对应图

![[附件/image/35_Join语句怎么优化-1663712735756.jpeg]]

explain

![[附件/image/35_Join语句怎么优化-1663712759813.jpeg]]

我们可以看到, extra 一栏多了 using MRR , 我们得到的结果集, 也与没有利用 MRR 算法时相反.

MRR 能够提升性能的核心在于，这条查询语句在索引 a 上做的是一个范围查询（也就是说，这是一个多值查询），**可以得到足够多的主键 id**。这样通过排序以后，再去主键索引查数据，才能体现出“顺序性”的优势。

### Batched Key Access-BKA 算法

理解了 MRR, 我们再来理解 BKA, 优化版的 NLJ

我们就把表 t1 的数据取出来一部分，先放到一个临时内存。这个临时内存不是别人，就是 join_buffer。(在 BNL 里使用过)

![[附件/image/35_Join语句怎么优化-1663715336263.jpeg]]

P1 - P100, 表示只会取查询需要的字段, 在这里就是指 a; 如果 join buffer 放不下, 那么还是像 BNL 一样, 分段放.[[MySQL丁奇_34_如何使用Join(Join的算法)#Block Nested-Loop Join|BNL]]

启用 BKA

```sql
set optimizer_switch='mrr=on,mrr_cost_based=off,batched_key_access=on';
```

其中，前两个参数的作用是要启用 MRR。这么做的原因是，BKA 算法的优化要依赖于 MRR。

### BNL 算法的性能问题

上一章的问题 [[MySQL丁奇_34_如何使用Join(Join的算法)]], 我们得出结论, 冷表如果很大, 或者小于 3 / 8 都有可能对业务命中率造成影响

为了减少这种影响，你可以考虑增大 join_buffer_size 的值，减少对被驱动表的扫描次数。

BNL 算法对系统的影响主要包括

1. 可能会多次扫描被驱动表，占用磁盘 IO 资源；
2. 判断 join 条件需要执行 M* N 次对比（M、N 分别是两张表的行数），如果是大表就会占用非常多的 CPU 资源；
3. 可能会导致 Buffer Pool 的热数据被淘汰，影响内存命中率。

常见的优化方法, 就是把 BNL 算法, 添加索引, 变为 BKA 算法.

### BNL 转 BKA

一般情况, 我们可以直接在被驱动表上加索引, 就可以直接转化为 BKA 算法了.

但也会碰到一些不适合在被驱动表上做索引的情况:, 比如

```sql
select * from t1 join t2 on (t1.b=t2.b) where t2.b>=1 and t2.b<=2000;
```

t2 中有 100 万条数据, 但需要查询的只有 2000 条, 如果这又是一个低频操作, 那么建索引就很浪费了.

但是，如果使用 BNL 算法来 join 的话，这个语句的执行流程是这样的：

1. 把表 t1 的所有字段取出来，存入 join_buffer 中。这个表只有 1000 行，join_buffer_size 默认值是 256k，可以完全存入。
2. 扫描表 t2，取出每一行数据跟 join_buffer 中的数据进行对比，
	1. 如果不满足 t1.b=t2.b，则跳过；
	2. 如果满足 t1.b=t2.b, 再判断其他条件，也就是是否满足 t2.b 处于 [1,2000] 的条件，如果是，就作为结果集的一部分返回，否则跳过。

每判断一次 join 是否满足, 都要遍历 join buffer 中的所有航, 所以判断的次数是 1000 * 100 万 = 10 亿次, 工作量很大.

![[附件/image/35_Join语句怎么优化-1663731444281.jpeg]]

![[附件/image/35_Join语句怎么优化-1663731449256.jpeg]]

可以看到 extra 里使用了 BNL.这条语句执行了将近 1 分 12 秒

这时, 我们可以考虑使用临时表。使用临时表的大致思路是：

1. 把表 t2 中满足条件的数据放在临时表 tmp_t 中；
2. 为了让 join 使用 BKA 算法，给临时表 tmp_t 的字段 b 加上索引；让表 t1 和 tmp_t 做 join 操作。

对应的 SQL 语句如下 ^76e386

```sql
create temporary table temp_t(id int primary key, a int, b int, index(b))engine=innodb;
insert into temp_t select * from t2 where b>=1 and b<=2000;
select * from t1 join temp_t on (t1.b=temp_t.b);
```

![[附件/image/35_Join语句怎么优化-1663731538266.jpeg]]

过程消耗:

1. 执行 insert 语句构造 temp_t 表并插入数据的过程中，对表 t2 做了全表扫描，这里扫描行数是 100 万。
2. 之后的 join 语句，扫描表 t1，这里的扫描行数是 1000；join 比较过程中，做了 1000 次带索引的查询。相比于优化前的 join 语句需要做 10 亿次条件判断来说，这个优化效果还是很明显的。

### 扩展 -hash join

如果 join buffer 里维护的不是一个无序数组, 而是一个哈希表的话, 那么就不需要判断十亿次, 只需要做 100 万次哈希查找就行了.

但是 MySQL 优化器和执行器不支持 hash join, 我们只能自己在业务端实现

1. select * from t1; 取得表 t1 的全部 1000 行数据，在业务端存入一个 hash 结构，比如 C++ 里的 set、PHP 的数组这样的数据结构。
2. select * from t2 where b>=1 and b<=2000; 获取表 t2 中满足条件的 2000 行数据。
3. 把这 2000 行数据，一行一行地取到业务端，到 hash 结构的数据表中寻找匹配的数据。满足匹配的条件的这行数据，就作为结果集的一行。

理论上比临时表还要快一点.

### 小结:

1. 从 MRR -> BKA, 建议使用 BKA.
2. BNL 转化为 BKA 的方法, 给被驱动表关联字段加索引, 或者取临时表再加索引
3. hash 算法可以在服务端实现.

## Join 语句怎么优化思考

有三个表:

```sql
CREATE TABLE `t1` (
 `id` int(11) NOT NULL,
 `a` int(11) DEFAULT NULL,
 `b` int(11) DEFAULT NULL,
 `c` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

create table t2 like t1;
create table t3 like t2;
insert into ... //初始化三张表的数据
```

执行以下逻辑

```sql
select * from t1 join t2 on(t1.a=t2.a) join t3 on (t2.b=t3.b) where t1.c>=X and t2.c>=Y and t3.c>=Z;
```

同时，如果我希望你用 straight_join 来重写这个语句，配合你创建的索引，你就需要安排连接顺序，你主要考虑的因素是什么呢？

第一原则是要尽量使用 BKA 算法。需要注意的是，使用 BKA 算法的时候，并不是“先计算两个表 join 的结果，再跟第三个表 join”，而是直接嵌套查询的。

具体实现是：在 t1.c>=X、t2.c>=Y、t3.c>=Z 这三个条件里，选择一个经过过滤以后，数据最少的那个表，作为第一个驱动表。此时，可能会出现如下两种情况。

第一种情况，如果选出来是表 t1 或者 t3，那剩下的部分就固定了。

1. 如果驱动表是 t1，则连接顺序是 t1->t2->t3，要在被驱动表字段创建上索引，也就是 t2.a 和 t3.b 上创建索引；
2. 如果驱动表是 t3，则连接顺序是 t3->t2->t1，需要在 t2.b 和 t1.a 上创建索引。同时，我们还需要在第一个驱动表的字段 c 上创建索引。

第二种情况是，如果选出来的第一个驱动表是表 t2 的话，则需要评估另外两个条件的过滤效果。

总之，整体的思路就是，尽量让每一次参与 join 的驱动表的数据集，越小越好，因为这样我们的驱动表就会越小。
