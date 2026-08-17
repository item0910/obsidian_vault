---
tags: 归档笔记/学习笔记/MySQL
title: 40_insert语句的阻塞和加锁
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-10-15
---

## 前言

这期讲 insert select 语句

## insert 语句的阻塞和加锁

### insert...select 语句加锁的原因 - 并发一致性

```sql
CREATE TABLE `t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c` int(11) DEFAULT NULL,
  `d` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `c` (`c`)
) ENGINE=InnoDB;

insert into t values(null, 1,1);
insert into t values(null, 2,2);
insert into t values(null, 3,3);
insert into t values(null, 4,4);

create table t2 like t
```

我们来看, 可重复读隔离级别下, 下面语句的执行

```sql
insert into t2(c,d) select c,d from t;
```

[[MySQL丁奇_39_自增主键不连续-自增值和自增锁#自增主键不连续 - 自增值和自增锁思考]]

为什么要对表 t 加行和间隙锁呢?

其实我们考虑的还是并发时数据的一致性问题.

![[附件/image/40_insert语句的阻塞和加锁-1663948896667.jpeg]]

如果不加锁, 读到的结果就有可能因为 session 的介入而变得不一致

比如 sessionB 先执行, 但是后写入 binlog, 主备数据就不一致了.

### insert 循环写入

```sql
insert into t2(c,d)  (select c+1, d from t force index(c) order by c desc limit 1);
```

![[附件/image/40_insert语句的阻塞和加锁-1663949046417.jpeg]]

我们可以看到, 扫描行数是 1.

如果我们要把这样一行插入表 t 中的话

```sql
insert into t(c,d)  (select c+1, d from t force index(c) order by c desc limit 1);
```

![[附件/image/40_insert语句的阻塞和加锁-1663949117420.jpeg]]

扫描行数是 5, explain 一下

![[附件/image/40_insert语句的阻塞和加锁-1663949145613.jpeg]]

用了临时表, 也就是说, 执行过程中, 把 t 的内容全部读出来, 写到了临时表中.

rows 显示的是 1, 是什么原因呢? 如果说是把子查询读出来到临时表, 再从临时表读出来扫描行数就应该是 2.

我们可以看看 InnoDB 扫描了多少行。如图 5 所示，是在执行这个语句前后查看 Innodb_rows_read 的结果。

![[附件/image/40_insert语句的阻塞和加锁-1663949310873.jpeg]]

这个语句执行前后，Innodb_rows_read 的值增加了 4。因为默认临时表是使用 Memory 引擎的，所以这 4 行查的都是表 t，也就是说对表 t 做了全表扫描。

limit 在里面起了作用:

1. 创建临时表，表里有两个字段 c 和 d。
2. 按照索引 c 扫描表 t，依次取 c=4、3、2、1，然后回表，读到 c 和 d 的值写入临时表。这时，Rows_examined=4。
3. 由于语义里面有 limit 1，所以只取了临时表的第一行，再插入到表 t 中。这时，Rows_examined 的值加 1，变成了 5。

这个语句会导致在表 t 上做全表扫描，并且会给索引 c 上的所有间隙都加上共享的 next-key lock。所以，这个语句执行期间，其他事务不能在这个表上插入数据。

这个语句的执行为什么需要临时表，原因是这类一边遍历数据，一边更新数据的情况，如果读出来的数据直接写回原表，就可能在遍历过程中，读到刚刚插入的记录，新插入的记录如果参与计算逻辑，就跟语义不符。

由于实现上这个语句没有在子查询中就直接使用 limit 1，从而导致了这个语句的执行需要遍历整个表 t。它的优化方法也比较简单，就是用前面介绍的方法，先 insert into 到临时表 temp_t，这样就只需要扫描一行；然后再从表 temp_t 里面取出这行数据插入表 t1。

```sql
create temporary table temp_t(c int,d int) engine=memory;
insert into temp_t  (select c+1, d from t force index(c) order by c desc limit 1);
insert into t select * from temp_t;
drop table temp_t;
```

对比原语句:

```sql
insert into t(c,d)  (select c+1, d from t force index(c) order by c desc limit 1);
```

### insert 唯一键冲突

例子:

![[附件/image/40_insert语句的阻塞和加锁-1663949678092.jpeg]]

session A 执行的 insert 语句，发生唯一键冲突的时候，并不只是简单地报错返回，还在冲突的索引上加了锁。我们前面说过，一个 next-key lock 就是由它右边界的值定义的。这时候，session A 持有索引 c 上的 (5,10] 共享 next-key lock（读锁）。

从作用上来看，这样做可以避免这一行被别的事务删掉。

这里官方文档有一个描述错误，认为如果冲突的是主键索引，就加记录锁，唯一索引才加 next-key lock。但实际上，这两类索引冲突加的都是 next-key lock。

一个死锁现场

![[附件/image/40_insert语句的阻塞和加锁-1663949836847.jpeg]]

1. 在 T1 时刻，启动 session A，并执行 insert 语句，此时在索引 c 的 c=5 上加了记录锁。注意，这个索引是唯一索引，因此退化为记录锁（如果你的印象模糊了，可以回顾下第 21 篇文章介绍的加锁规则）。
2. 在 T2 时刻，session B 要执行相同的 insert 语句，发现了唯一键冲突，加上读锁；同样地，session C 也在索引 c 上，c=5 这一个记录上，加了读锁。
3. T3 时刻，session A 回滚。这时候，session B 和 session C 都试图继续执行插入操作，都要加上写锁。两个 session 都要等待对方的行锁，所以就出现了死锁。

### insert into ...on duplicate key update

如果把 `insert into t values(11, 10, 10)` 这个冲突报错的语句改为:

```sql
insert into t values(11,10,10) on duplicate key update d=100; 
```

就会给索引 c 上 (5,10] 加一个排他的 next - key lock 写锁.

insert into … on duplicate key update 这个语义的逻辑是，插入一行数据，如果碰到唯一键约束，就执行后面的更新语句。

注意，如果有多个列违反了唯一性约束，就会按照索引的顺序，修改跟第一个索引冲突的行。

比如下面这个语句和结果

![[附件/image/40_insert语句的阻塞和加锁-1663950249376.jpeg]]

更新的就是第一个冲突的 (主键) 那一行的值.

执行这条语句的 affected rows 返回的是 2，很容易造成误解。实际上，真正更新的只有一行，只是在代码实现上，insert 和 update 都认为自己成功了，update 计数加了 1， insert 计数也加了 1。

### 小结

1. 为了并发时 binlog 的一致性 (statement 状态下), 需要给 insert ... select 语句加锁
2. 防止循环写入, insert select 会采用临时表的方式来执行
3. 唯一键冲突时, 如果在事务中, 也会加锁, 甚至导致死锁
4. insert into duplicate key 的用法, 和多个唯一键冲突时的判断.

## insert 语句的阻塞和加锁思考

你平时在两个表之间拷贝数据用的是什么方法， 有什么注意事项吗？ 在你的应用场景里， 这个方法， 相较于其他方法的优势是什么呢？
