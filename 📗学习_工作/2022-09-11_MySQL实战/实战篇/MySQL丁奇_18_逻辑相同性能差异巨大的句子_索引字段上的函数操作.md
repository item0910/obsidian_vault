---
tags: 归档笔记/学习笔记/MySQL
title: 18_逻辑相同性能差异巨大的句子_索引字段上的函数操作
date: 2022-09-14
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

## 逻辑相同性能差异巨大的句子 _ 索引字段上的函数操作

有表:

```sql
mysql> CREATE TABLE `tradelog` (
  `id` int(11) NOT NULL,
  `tradeid` varchar(32) DEFAULT NULL,
  `operator` int(11) DEFAULT NULL,
  `t_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tradeid` (`tradeid`),
  KEY `t_modified` (`t_modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 条件字段函数操作

现在要全部 7 月的数据, 你这样写

```sql
mysql> select count(*) from tradelog where month(t_modified)=7;
```

其实这样执行很慢, 因为如果对字段做了函数计算，就用不上索引了，这是 MySQL 的规定。

现在你已经学过了 InnoDB 的索引结构了，可以再追问一句为什么？为什么条件是 where t_modified='2018-7-1’的时候可以用上索引，而改成 where month(t_modified)=7 的时候就不行了？

![[附件/image/18_逻辑相同性能差异巨大的句子_索引字段上的函数操作.jpg]]

如果你的 SQL 语句条件用的是 where t_modified='2018-7-1’的话，引擎就会按照上面绿色箭头的路线，快速定位到 t_modified='2018-7-1’需要的结果。

如果是用的 month() 函数, 从第一行他就不知道怎么办了.

对索引字段做函数操作，**可能会破坏索引值的有序性，因此优化器就决定放弃走树搜索功能**。

在这个例子里，放弃了树搜索功能，优化器可以选择遍历主键索引，也可以选择遍历索引 t_modified，优化器对比索引大小后发现，索引 t_modified 更小，遍历这个索引比遍历主键索引来得更快。因此最终还是会选择索引 t_modified。

![[附件/image/18_逻辑相同性能差异巨大的句子_索引字段上的函数操作-1.jpg]]

```sql
mysql> select count(*) from tradelog where
    -> (t_modified >= '2016-7-1' and t_modified<'2016-8-1') or
    -> (t_modified >= '2017-7-1' and t_modified<'2017-8-1') or 
    -> (t_modified >= '2018-7-1' and t_modified<'2018-8-1');
```

这样就能用上索引了快速定位了.

对于 select * from tradelog where id + 1 = 10000 这个 SQL 语句，这个加 1 操作并不会改变有序性，但是 MySQL 优化器还是不能用 id 索引快速定位到 9999 这一行。所以，需要你在写 SQL 语句的时候，手动改写成 where id = 10000 -1 才可以。

### 隐式类型转换

```sql
mysql> select * from tradelog where tradeid=110717;
```

类型转换的规则是什么?

看:

select “10” > 9

如果规则是“将字符串转成数字”，那么就是做数字比较，结果应该是 1；

如果规则是“将数字转成字符串”，那么就是做字符串比较，结果应该是 0。

那么对于优化器来说

```sql
mysql> select * from tradelog where  CAST(tradid AS signed int) = 110717;
```

又触发了我们的对索引字段做函数操作, 优化器会放弃走索引树

以下的语句, 就不会触发这种机制

```sql
select * from tradelog where id="83126";
```

### 隐式字符编码转换

现在还有一个表,

```sql
mysql> CREATE TABLE `trade_detail` (
  `id` int(11) NOT NULL,
  `tradeid` varchar(32) DEFAULT NULL,
  `trade_step` int(11) DEFAULT NULL, /*操作步骤*/
  `step_info` varchar(32) DEFAULT NULL, /*步骤信息*/
  PRIMARY KEY (`id`),
  KEY `tradeid` (`tradeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into tradelog values(1, 'aaaaaaaa', 1000, now());
insert into tradelog values(2, 'aaaaaaab', 1000, now());
insert into tradelog values(3, 'aaaaaaac', 1000, now());

insert into trade_detail values(1, 'aaaaaaaa', 1, 'add');
insert into trade_detail values(2, 'aaaaaaaa', 2, 'update');
insert into trade_detail values(3, 'aaaaaaaa', 3, 'commit');
insert into trade_detail values(4, 'aaaaaaab', 1, 'add');
insert into trade_detail values(5, 'aaaaaaab', 2, 'update');
insert into trade_detail values(6, 'aaaaaaab', 3, 'update again');
insert into trade_detail values(7, 'aaaaaaab', 4, 'commit');
insert into trade_detail values(8, 'aaaaaaac', 1, 'add');
insert into trade_detail values(9, 'aaaaaaac', 2, 'update');
insert into trade_detail values(10, 'aaaaaaac', 3, 'update again');
insert into trade_detail values(11, 'aaaaaaac', 4, 'commit');
```

如果要查询 id = 2 的交易的所有细节信息, 可以这样写

```sql
mysql> select d.* from tradelog l, trade_detail d where d.tradeid=l.tradeid and l.id=2; /*语句Q1*/
```

我们看结果:
![](附件/image/MySQL丁奇_18_逻辑相同性能差异巨大的句子_索引字段上的函数操作-1695637925001.jpeg)

第一行显示优化器会先在交易记录表 tradelog 上查到 id=2 的行，这个步骤用上了主键索引，rows=1 表示只扫描一行；

第二行 key=NULL，表示没有用上交易详情表 trade_detail 上的 tradeid 索引，进行了全表扫描。

在这个执行计划里，是从 tradelog 表中取 tradeid 字段，再去 trade_detail 表里查询匹配字段。因此，我们把 tradelog 称为驱动表，把 trade_detail 称为被驱动表，把 tradeid 称为关联字段。

![[附件/image/18_逻辑相同性能差异巨大的句子_索引字段上的函数操作-2.jpg]]

- 第 1 步，是根据 id 在 tradelog 表里找到 L2 这一行；
- 第 2 步，是从 L2 中取出 tradeid 字段的值；
- 第 3 步，是根据 tradeid 值到 trade_detail 表中查找条件匹配的行。explain 的结果里面第二行的 key=NULL 表示的就是，这个过程是通过遍历主键索引的方式，一个一个地判断 tradeid 的值是否匹配。

进行到这里，你会发现第 3 步不符合我们的预期。因为表 trade_detail 里 tradeid 字段上是有索引的，我们本来是希望通过使用 tradeid 索引能够快速定位到等值的行。但，这里并没有。

因为这两个表的字符集不同，一个是 utf8，一个是 utf8mb4，所以做表连接查询的时候用不上关联字段的索引。这个回答，也是通常你搜索这个问题时会得到的答案。

```sql
mysql> select * from trade_detail where tradeid=$L2.tradeid.value; 
```

字符集 utf8mb4 是 utf8 的超集，所以当这两个类型的字符串在做比较的时候，MySQL 内部的操作是，先把 utf8 字符串转成 utf8mb4 字符集，再做比较。(超集信息多于一般集合)

>这个设定很好理解，utf8mb4 是 utf8 的超集。类似地，在程序设计语言里面，做自动类型转换的时候，为了避免数据在转换过程中由于截断导致数据错误，也都是“按数据长度增加的方向”进行转换的。

```sql
select * from trade_detail  where CONVERT(traideid USING utf8mb4)=$L2.tradeid.value; 
```

这就再次触发了我们上面说到的原则：对索引字段做函数操作，优化器会放弃走树搜索功能。到这里，你终于明确了，字符集不同只是条件之一，连接过程中要求在被驱动表的索引字段上加函数操作，是直接导致对被驱动表做全表扫描的原因。

现在有一个需求, 查 id = 4 的操作者是谁

```sql
mysql>select l.operator from tradelog l , trade_detail d where d.tradeid=l.tradeid and d.id=4;
```

![[附件/image/18_逻辑相同性能差异巨大的句子_索引字段上的函数操作-3.jpg]]

这个语句里 trade_detail 表成了驱动表，但是 explain 结果的第二行显示，这次的查询操作用上了被驱动表 tradelog 里的索引 (tradeid)，扫描行数是 1。

因为执行过程的第三步, 用上了类似这样的语句

```sql
select operator from tradelog  where traideid =$R4.tradeid.value; 
```

这时候 $R4.tradeid.value 的字符集是 utf8, 按照字符集转换规则，要转成 utf8mb4，所以这个过程就被改写成：

```sql
select operator from tradelog  where traideid =CONVERT($R4.tradeid.value USING utf8mb4); 
```

现在, 如果要优化我们的语句

```sql
select d.* from tradelog l, trade_detail d where d.tradeid=l.tradeid and l.id=2;
```

比较常见的优化方法是，把 trade_detail 表上的 tradeid 字段的字符集也改成 utf8mb4，这样就没有字符集转换的问题了。

```sql
alter table trade_detail modify tradeid varchar(32) CHARACTER SET utf8mb4 default null;
```

如果能够修改字段的字符集的话，是最好不过了。但如果数据量比较大， 或者业务上暂时不能做这个 DDL 的话，那就只能采用修改 SQL 语句的方法了。

```sql
mysql> select d.* from tradelog l , trade_detail d where d.tradeid=CONVERT(l.tradeid USING utf8) and l.id=2; 
```

这里，我主动把 l.tradeid 转成 utf8，就避免了被驱动表上的字符编码转换，从 explain 结果可以看到，这次索引走对了。

![[附件/image/18_逻辑相同性能差异巨大的句子_索引字段上的函数操作-4.jpg]]

### 小结

总而言之, **对索引字段做函数操作，可能会破坏索引值的有序性，因此优化器就决定放弃走树搜索功能。**

因此，每次你的业务代码升级时，把可能出现的、新的 SQL 语句 explain 一下，是一个很好的习惯。

## 逻辑相同性能差异巨大的句子 _ 索引字段上的函数操作思考

你遇到过别的、类似今天我们提到的性能问题吗？你认为原因是什么，又是怎么解决的呢？

有表:

```sql
mysql> CREATE TABLE `table_a` (
  `id` int(11) NOT NULL,
  `b` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `b` (`b`)
) ENGINE=InnoDB;
```

有一个查询

```sql
mysql> select * from table_a where b='1234567890abcd';
```

但实际上，MySQL 也不是这么做的。这条 SQL 语句的执行很慢，流程是这样的：

1. 在传给引擎执行的时候，做了字符截断。因为引擎里面这个行只定义了长度是 10，所以只截了前 10 个字节，就是’1234567890’进去做匹配；
2. 这样满足条件的数据有 10 万行；
3. 因为是 select * ， 所以要做 10 万次回表；
4. 但是每次回表以后查出整行，到 server 层一判断，b 的值都不是’1234567890abcd’;
5. 返回结果是空。
