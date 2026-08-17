---
tags: 归档笔记/学习笔记/MySQL
title: 37_union,group_by和内部临时表
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-10-15
---

## 前言

有表

```sql
create table t1(id int primary key, a int, b int, index(a));
delimiter ;;
create procedure idata()
begin
  declare i int;

  set i=1;
  while(i<=1000)do
    insert into t1 values(i, i, i);
    set i=i+1;
  end while;
end;;
delimiter ;
call idata();
```

## union,group_by 和内部临时表

### Union 的执行流程

我们执行

```sql
(select 1000 as f) union (select id from t1 order by id desc limit 2);
```

(这条语句用到了 union，它的语义是，取这两个子查询结果的并集。并集的意思就是这两个集合加起来，重复的行只保留一行。)

explain

![[附件/image/37_union,group_by和内部临时表-1663938140266.jpeg]]

- 第二行的 key=PRIMARY，说明第二个子句用到了索引 id。
- 第三行的 Extra 字段，表示在对子查询的结果集做 union 的时候，使用了临时表 (Using temporary)。

执行流程

1. 创建一个内存临时表，这个临时表只有一个整型字段 f，并且 f 是主键字段。
2. 执行第一个子查询，得到 1000 这个值，并存入临时表中。
3. 执行第二个子查询：拿到第一行 id=1000，试图插入临时表中。但由于 1000 这个值已经存在于临时表了，违反了唯一性约束，所以插入失败，然后继续执行；
4. 取到第二行 id=999，插入临时表成功。从临时表中按行取出数据，返回结果，并删除临时表，结果中包含两行数据分别是 1000 和 999。

![[附件/image/37_union,group_by和内部临时表-1663938242101.jpeg]]

如果把上面这个语句中的 union 改成 union all 的话，就没有了“去重”的语义。这样执行的时候，就依次执行子查询，得到的结果直接作为结果集的一部分，发给客户端。因此也就不需要临时表了。

explain

![[附件/image/37_union,group_by和内部临时表-1663938269677.jpeg]]

### group by 执行流程

```sql
select id%10 as m, count(*) as c from t1 group by m;
```

![[附件/image/37_union,group_by和内部临时表-1663938608848.jpeg]]

- Using index，表示这个语句使用了覆盖索引，选择了索引 a，不需要回表；
- Using temporary，表示使用了临时表；
- Using filesort，表示需要排序。

执行流程

1. 创建内存临时表，表里有两个字段 m 和 c，主键是 m；
2. 扫描表 t1 的索引 a，依次取出叶子节点上的 id 值，计算 id%10 的结果，记为 x；
	1. 如果临时表中没有主键为 x 的行，就插入一个记录 (x,1);
	2. 如果表中有主键为 x 的行，就将 x 这一行的 c 值加 1；
3. 遍历完成后，再根据字段 m 做排序，得到结果集返回给客户端。

![[附件/image/37_union,group_by和内部临时表-1663938744097.jpeg]]

对临时表的排序:

![[附件/image/37_union,group_by和内部临时表-1663938767244.jpeg]]

执行结果如下:

![[附件/image/37_union,group_by和内部临时表-1663938797729.jpeg]]

如果不需要排序, 可以是

```sql
select id%10 as m, count(*) as c from t1 group by m order by null;
```

![[附件/image/37_union,group_by和内部临时表-1663938837437.jpeg]]

由于表 t1 中的 id 值是从 1 开始的，因此返回的结果集中第一行是 id=1；扫描到 id=10 的时候才插入 m=0 这一行，因此结果集里最后一行才是 m=0。

这个例子里由于临时表只有 10 行，内存可以放得下，因此全程只使用了内存临时表。但是，内存临时表的大小是有限制的，参数 tmp_table_size 就是控制这个内存大小的，默认是 16M。

```sql
set tmp_table_size=1024;
select id%100 as m, count(*) as c from t1 group by m order by null limit 10;
```

把内存临时表的大小限制为最大 1024 字节，并把语句改成 id % 100，这样返回结果里有 100 行数据。但是，这时的内存临时表大小不够存下这 100 行数据，也就是说，执行过程中会发现内存临时表大小到达了上限（1024 字节）。

这时候就会把内存临时表转成磁盘临时表，磁盘临时表默认使用的引擎是 InnoDB。 这时，返回的结果如图所示。

![[附件/image/37_union,group_by和内部临时表-1663938899043.jpeg]]

所以如果数据量很大, 临时表也可能占据很大的空间.

### group by 优化方法 - 索引

执行 group by 语句为什么需要临时表？

group by 的语义逻辑，是统计不同的值出现的个数。但是，由于每一行的 id%100 的结果是无序的，所以我们就需要有一个临时表，来记录并统计结果。

那么，如果扫描过程中可以保证出现的数据是有序的，是不是就简单了呢？假设，现在有一个类似图 10 的这么一个数据结构，我们来看看 group by 可以怎么做。

![[附件/image/37_union,group_by和内部临时表-1663938997286.jpeg]]

如果从左往右顺序扫描, 那么

- 当碰到第一个 1 的时候，已经知道累积了 X 个 0，结果集里的第一行就是 (0,X);
- 当碰到第一个 2 的时候，已经知道累积了 Y 个 1，结果集里的第二行就是 (1,Y);
按照这个逻辑执行的话，扫描到整个输入的数据结束，就可以拿到 group by 的结果，不需要临时表，也不需要再额外排序。

在 MySQL 5.7 版本支持了 generated column 机制，用来实现列数据的关联更新。你可以用下面的方法创建一个列 z，然后在 z 列上创建一个索引（如果是 MySQL 5.6 及之前的版本，你也可以创建普通列和索引，来解决这个问题）。

```sql
alter table t1 add column z int generated always as(id % 100), add index(z);
```

```sql
select z, count(*) as c from t1 group by z;
```

这时候 z 就是有序的了, 可以直接按照 z 来取出结果, explain 如下:

![[附件/image/37_union,group_by和内部临时表-1663939136591.jpeg]]

### group by 优化方法 - 直接排序

如果碰上不适合创建索引的场景，我们还是要老老实实做排序的。

那么，这时候的 group by 要怎么优化呢？如果我们明明知道，一个 group by 语句中需要放到临时表上的数据量特别大，却还是要按照“先放到内存临时表，插入一部分数据后，发现内存临时表不够用了再转成磁盘临时表”

有没有让我们直接走磁盘临时表的方法呢？

在 group by 语句中加入 SQL_BIG_RESULT 这个提示（hint），就可以告诉优化器：这个语句涉及的数据量很大，请直接用磁盘临时表。

MySQL 的优化器一看，磁盘临时表是 B+ 树存储，存储效率不如数组来得高。所以，既然你告诉我数据量很大，那从磁盘空间考虑，还是直接用数组来存吧。

```sql
select SQL_BIG_RESULT id%100 as m, count(*) as c from t1 group by m;
```

之后的流程:

1. 初始化 sort_buffer，确定放入一个整型字段，记为 m；
2. 扫描表 t1 的索引 a，依次取出里面的 id 值, 将 id%100 的值存入 sort_buffer 中；
3. 扫描完成后，对 sort_buffer 的字段 m 做排序（如果 sort_buffer 内存不够用，就会利用磁盘临时文件辅助排序）；
4. 排序完成后，就得到了一个有序数组。

![[附件/image/37_union,group_by和内部临时表-1663939785811.jpeg]]

![[附件/image/37_union,group_by和内部临时表-1663939806804.jpeg]]

小结, MySQL 什么时候会使用内部临时表

1. 如果语句执行过程可以一边读数据，一边直接得到结果，是不需要额外内存的，否则就需要额外的内存，来保存中间结果；
2. join_buffer 是无序数组，sort_buffer 是有序数组，临时表是二维表结构；
3. 如果执行逻辑需要用到二维表特性，就会优先考虑使用临时表。比如我们的例子中，union 需要用到唯一索引约束， group by 还需要用到另外一个字段来存累积计数。(二维表简单来说就是一种统计)
![](MySQL丁奇_00_MySQL术语.md#^5e1ac1)

### 小结

1. union 的逻辑, 和执行过程
2. group by 的执行流程和利用索引的优化方法
3. 在面对大表数据时, 直接给 MySQL 提示来优化排序.

## union,group_by 和内部临时表思考

文章中图 8 和图 9 都是 order by null，为什么图 8 的返回结果里面，0 是在结果集的最后一行，而图 9 的结果里面，0 是在结果集的第一行？

用内存表 (Memory):

![[附件/image/37_union,group_by和内部临时表-1663938837437.jpeg]]

用磁盘临时表 (InnoDB):

![[附件/image/37_union,group_by和内部临时表-1663938899043.jpeg]]
