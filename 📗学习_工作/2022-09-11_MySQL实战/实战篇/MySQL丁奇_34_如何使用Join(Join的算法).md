---
tags: 归档笔记/学习笔记/MySQL
title: 34_如何使用Join
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

有人说 DBA 不让使用 JOIN 的问题

有表

```sql
CREATE TABLE `t2` (
  `id` int(11) NOT NULL,
  `a` int(11) DEFAULT NULL,
  `b` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `a` (`a`)
) ENGINE=InnoDB;

drop procedure idata;
delimiter ;;
create procedure idata()
begin
  declare i int;
  set i=1;
  while(i<=1000)do
    insert into t2 values(i, i, i);
    set i=i+1;
  end while;
end;;
delimiter ;
call idata();

create table t1 like t2;
insert into t1 (select * from t2 where id<=100)
```

这两个表都有一个主键索引 id 和一个索引 a，字段 b 上无索引。

存储过程 idata() 往表 t2 里插入了 1000 行数据，

在表 t1 里插入的是 100 行数据。

先来看贯穿本课程的驱动表和被驱动表的意思

```sql
select * from t1 straight_join t2 on (t1.a=t2.a);
```

其中 t1(前) 是驱动表, t2(后) 是被驱动表

含义:**拿驱动表的数据, 去 t2 里找 (利用 t2 的表结构)**

## 如何使用 Join(Join 的算法)

### Index Nested-Loop Join

```sql
select * from t1 straight_join t2 on (t1.a=t2.a);
```

来看 explain

![[附件/image/34_如何使用Join(Join的算法)-1663704525066.jpeg]]

1. 从表 t1 中读入一行数据 R；
2. 从数据行 R 中，取出 a 字段到表 t2 里去查找；
3. 取出表 t2 中满足条件的行，跟 R 组成一行，作为结果集的一部分；
4. 重复执行步骤 1 到 3，直到表 t1 的末尾循环结束。

这个过程是先遍历表 t1，然后根据从表 t1 中取出的每行数据中的 a 值，去表 t2 中查找满足条件的记录。在形式上，这个过程就跟我们写程序时的嵌套查询类似，并且可以用上被驱动表的索引，所以我们称之为“Index Nested-Loop Join”，简称 NLJ。

![[附件/image/34_如何使用Join(Join的算法)-1663704871014.jpeg]]

1. 对驱动表 t1 做了全表扫描，这个过程需要扫描 100 行；
2. 而对于每一行 R，根据 a 字段去表 t2 查找，走的是树搜索过程。由于我们构造的数据都是一一对应的，因此每次的搜索过程都只扫描一行，也是总共扫描 100 行；
3. 所以，整个执行流程，总扫描行数是 200。

那么针对不让用 JOIN 的问题, 我们如果不用, 应该怎么做呢?

1. 执行 select * from t1，查出表 t1 的所有数据，这里有 100 行；
2. 循环遍历这 100 行数据：
	- 从每一行 R 取出字段 a 的值 $R.a；
	- 执行 select * from t2 where a=$R.a；
	- 把返回的结果和 R 构成结果集的一行。

可以看到，在这个查询过程，也是扫描了 200 行，但是总共执行了 101 条语句，比直接 join 多了 100 次交互。除此之外，客户端还要自己拼接 SQL 语句和结果。显然，这么做还不如直接 join 好。

选谁做驱动表? 设驱动表行数为 N, 被驱动表行数为 M

每次在被驱动表查一行数据，要先搜索索引 a，再搜索主键索引。每次搜索一棵树近似复杂度是以 2 为底的 M 的对数，记为 log₂M，所以在被驱动表上查一行的时间复杂度是 2* log₂M。

有 N 行要匹配, 加上自己的扫描行数, 近似复杂度 N + 2Nlog₂M。

显然 N 的行数对这个复杂度影响更大

- 小结:
	1. 使用 join 语句，性能比强行拆成多个单表执行 SQL 语句的性能要好；
	2. 如果使用 join 语句的话，需要让小表做驱动表。

### Simple Nested-Loop Join

```sql
select * from t1 straight_join t2 on (t1.a=t2.b);
```

这时, b 上没有索引.

这时, 如果继续使用上面这个流程 (只是 t2 要做全表扫描), 是不是能得到正确的结果呢?

如果只看结果, 是可以的, 而且这个算法名称叫 Simple Nested-Loop Join

这样 t2 就要扫描 100 次, 需要扫描行数为 100 x 1000 = 10 万行 (因为不能复用, 所以每次都要扫描, 这跟 join buffer 不同)

这很笨重, 所以 MySQL 没有使用

### Block Nested-Loop Join

被驱动表上没有可用的索引，算法的流程是这样的：

1. 把表 t1 的数据读入线程内存 join_buffer 中，由于我们这个语句中写的是 select * ，因此是把整个表 t1 放入了内存；
2. 扫描表 t2，把表 t2 中的每一行取出来，跟 join_buffer 中的数据做对比，满足 join 条件的，作为结果集的一部分返回。

![[附件/image/34_如何使用Join(Join的算法)-1663719059492.jpeg]]

![[附件/image/34_如何使用Join(Join的算法)-1663705743856.jpeg]]

在这个过程中，对表 t1 和 t2 都做了一次全表扫描，因此总的扫描行数是 1100。由于 join_buffer 是以无序数组的方式组织的，因此对表 t2 中的每一行，都要做 100 次判断，总共需要在内存中做的扫描行数是：100* 1000=10 万次。

BNL 扫描行数和上一种一样, 但是因为用了 join buffer, 所以内存计算要快很多.

我们来看一下这时候用哪个表做驱动表, 设小表行数为 N, 大表为 M

扫描行数是 M + N, 判断次数是 M * N, 所以哪个驱动没差别

如果驱动表是一个大表, join buffer 放不下怎么办呢? join_buffer 的大小是由参数 join_buffer_size 设定的，默认值是 256k。如果放不下表 t1 的所有数据话，策略很简单，就是分段放。我把 join_buffer_size 改成 1200，再执行：

执行过程就变成了

1. 扫描表 t1，顺序读取数据行放入 join_buffer 中，放完第 88 行 join_buffer 满了，继续第 2 步；

2. 扫描表 t2，把 t2 中的每一行取出来，跟 join_buffer 中的数据做对比，满足 join 条件的，作为结果集的一部分返回；

3. 清空 join_buffer；

4. 继续扫描表 t1，顺序读取最后的 12 行数据放入 join_buffer 中，继续执行第 2 步。

![[附件/image/34_如何使用Join(Join的算法)-1663706164636.jpeg]]

Block 名字由此而来, 分块.

判断次数依然是 M * N(结合律), 那我们如何选择呢? 看分段次数

如果驱动表要分 K 次才能, 注意这里 K 不是常数, 而是跟 N 相关的. N = k * buffer 大小

1. 那么扫描行数就是 N + N / buffer 大小 * M 即 N + αNM, 其中 0< α < 1.
2. 内存判断 N * M 次

N 的大小对这个扫描行数的大小影响更大

结论: 让小表做驱动表.

另一种理解, 如果驱动表能一次性一直放在 join_buffer 里, 就不用再分段了, 自然快.

所以, 如果你的 join 语句很慢，就把 join_buffer_size 改大。

### 能不能使用 Join? 选哪个表做驱动表?

能不能用 join:

1. 如果可以使用 Index Nested-Loop Join 算法，也就是说可以用上被驱动表上的索引，其实是没问题的；
2. 如果使用 Block Nested-Loop Join 算法，扫描行数就会过多。尤其是在大表上的 join 操作，这样可能要扫描被驱动表很多次，会占用大量的系统资源。所以这种 join 尽量不要用。

驱动表选择:

1. 如果是 Index Nested-Loop Join 算法，应该选择小表做驱动表；
2. 如果是 Block Nested-Loop Join 算法：在 join_buffer_size 足够大的时候，是一样的；在 join_buffer_size 不够大的时候（这种情况更常见），应该选择小表做驱动表。

所以始终应该选择 " 小表 " 做驱动表, 不过这个小表, 也是相对的.

```sql
select * from t1 straight_join t2 on (t1.b=t2.b) where t2.id<=50;
select * from t2 straight_join t1 on (t1.b=t2.b) where t2.id<=50;
```

都用不上索引, 所以肯定是 BNL 算法

如果是语句 2, t2 只用放入前 50 行, 小表就是 t2(这里也侧面说明了, 先 where, 再进行 buffer 判断)

另一个例子:

```sql
select t1.b,t2.* from  t1  straight_join t2 on (t1.b=t2.b) where t2.id<=100;
select t1.b,t2.* from  t2  straight_join t1 on (t1.b=t2.b) where t2.id<=100;
```

t1 只查 b, 所以放入 join buffer 里的只有 b

而 t2 查询所有字段, 所以放入的是 id, a,b

这里我们还是要选 t1 作为驱动表.

在决定哪个表做驱动表的时候，应该是两个表按照各自的条件过滤，过滤完成之后，计算参与 join 的各个字段的总数据量，数据量小的那个表，就是“小表”，应该作为驱动表。

### 小结:

本章从要不要用 join 出发

1. 介绍了三种 join 的算法, 其中比较重要的是 NLJ 和 BNL
	1. NLJ 利用的是表自身带的索引, 优先级比较高
	2. BNL 是在使用没有索引的字段使用的, 利用了 join buffer

## 如何使用 Join 思考

- 我的问题是， 如果被驱动表是一个大表， 并且是一个冷数据表， 除了查询过程中可能会导致 IO 压力大以外， 你觉得对这个 MySQL 服务还有什么更严重的影响吗？ （这个问题需要结合上一篇文章的知识点）

	- 答: 在第 33 篇文章中，我们说到 InnoDB 的 LRU 算法的时候提到，由于 InnoDB 对 Bufffer Pool 的 LRU 算法做了优化，即：第一次从磁盘读入内存的数据页，会先放在 old 区域。如果 1 秒之后这个数据页不再被访问了，就不会被移动到 LRU 链表头部，这样对 Buffer Pool 的命中率影响就不大。
		1. 情况 1: 时间 > 1, 且冷表 < 3 / 8 占据了热区, 影响正常业务
			但是，如果一个使用 BNL 算法的 join 语句，多次扫描一个冷表，而且这个语句执行时间超过 1 秒，就会在再次扫描冷表的时候，把冷表的数据页移到 LRU 链表头部。
			这种情况对应的，是冷表的数据量小于整个 Buffer Pool 的 3/8，能够完全放入 old 区域的情况。

		2. 情况 2: 读取 < 1, 冷表很大占据 IO, 不断的挤占 old, 导致正常刚进入 old 的业务数据页无法进入 young

			如果这个冷表很大，就会出现另外一种情况：业务正常访问的数据页，没有机会进入 young 区域。

			由于优化机制的存在，一个正常访问的数据页，要进入 young 区域，需要隔 1 秒后再次被访问到。但是，由于我们的 join 语句在循环读磁盘和淘汰内存页，进入 old 区域的数据页，很可能在 1 秒之内就被淘汰了。这样，就会导致这个 MySQL 实例的 Buffer Pool 在这段时间内，young 区域的数据页没有被合理地淘汰。

			也就是说，这两种情况都会影响 Buffer Pool 的正常运作。
