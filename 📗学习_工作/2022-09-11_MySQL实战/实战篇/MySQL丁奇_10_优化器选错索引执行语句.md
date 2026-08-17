---
tags: 归档笔记/学习笔记/MySQL
title: 10_优化器选错索引执行语句
date: 2022-09-13
categories: MySQL
author: 丁奇
mtime: 2024-11-20
---

## 前言: 一条可以快的语句很慢

- 表格

```sql
CREATE TABLE `t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `a` int(11) DEFAULT NULL,
  `b` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `a` (`a`),
  KEY `b` (`b`)
) ENGINE=InnoDB;
```

ab 建索引, 插入 10 万行记录

```sql
delimiter ;;
create procedure idata()
begin
  declare i int;
  set i=1;
  while(i<=100000)do
    insert into t values(i, i, i);
    set i=i+1;
  end while;
end;;
delimiter ;
call idata();
```

执行

```sql
mysql> select * from t where a between 10000 and 20000;
```

explain 观察

![[附件/image/10_优化器选错索引执行语句.jpg]]

加入 session B, 观察

![[附件/image/10_优化器选错索引执行语句-1.jpg]]

B 是先删数据再执行原过程.模拟我们删除历史数据新增数据的场景.

```sql
set long_query_time=0; ## 将慢查询日志的阈值设为0, 使接下来的操作都会被记入慢查询
select * from t where a between 10000 and 20000; /*Q1*/
select * from t force index(a) where a between 10000 and 20000;/*Q2 force A了*/ 
```

观察两个语句的执行状态

![[附件/image/10_优化器选错索引执行语句-2.jpg]]

- 注意, 第一条语句扫描了十万行, 显然没有用到索引 a

## 优化器选错索引执行语句

### 优化器的逻辑

预估要扫描的行数 (根据区分度, 来得知一个索引上的基数, 也就是索引区分度越高, 基数越大)

用 `show index` 可以看到对每个索引预估的区分度.

![[附件/image/10_优化器选错索引执行语句-3.jpg]]

Mysql 如何得到这个基数? 采样统计

采样统计的时候，InnoDB 默认会选择 N 个数据页，统计每个页面上的不同值，得到一个平均值，然后乘以这个索引的页面数，就得到了这个索引的基数。

而数据表是会持续更新的，索引统计信息也不会固定不变。所以，当变更的数据行数超过 1/M 的时候，会自动触发重新做一次索引统计。

在 MySQL 中，有两种存储索引统计的方式，可以通过设置参数 innodb_stats_persistent 的值来选择：

- 设置为 on 的时候，表示统计信息会持久化存储。这时，默认的 N 是 20，M 是 10。
- 设置为 off 的时候，表示统计信息只存储在内存中。这时，默认的 N 是 8，M 是 16。

由于是采样统计，所以不管 N 是 20 还是 8，这个基数都是很容易不准的。

******

再来看看优化器预估的扫描行数

![[附件/image/10_优化器选错索引执行语句-4.jpg]]

结果: Q1 是跟前面结果相同, 10 万行, Q2 不是 10000 行, 而是 30000 行?

另外, 优化器为什么放着 30000 行的预估不用呢?

另外, 这个数字为什么是 30000 行呢? 留给你分析

这是因为如果是扫描主键, 数据可以直接使用; 而扫描索引 a, 还要通过主键回表, 优化器会把这一部分代价也计算在内.

analyze table t 命令，可以用来重新统计索引信息。我们来看一下执行效果。

![[附件/image/10_优化器选错索引执行语句-5.jpg]]

这次对了. 所以实际情况如果发生, 可以通过这种方式处理

#### 另一个案例

```sql
mysql> select * from t where (a between 1 and 1000)  and (b between 50000 and 100000) order by b limit 1;
```

回顾一下表结构, 表中都有十万条记录

```sql
CREATE TABLE `t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `a` int(11) DEFAULT NULL,
  `b` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `a` (`a`),
  KEY `b` (`b`)
) ENGINE=InnoDB;
```

这个语句显然会返回空集合, 我们来看一下 a, b 两个索引的结构, 预估一下需要扫描的行数

![[附件/image/10_优化器选错索引执行语句-6.jpg]]

判断, 如果使用索引 a , 需要扫描 1000 行, 然后回主键再判断 b

如果使用索引 b, 则需要扫描 50000 行, 然后回主键判断 a;

explain 试试

```sql
mysql> explain select * from t where (a between 1 and 1000) and (b between 50000 and 100000) order by b limit 1;
```

![[附件/image/10_优化器选错索引执行语句-7.jpg]]

选择了 b.又选错了

为什么呢, 因为后面会 order by b , 优化器认为选 b 可以避免排序.

### 索引选择异常和处理

如何让他强行选对呢?

1. force index
![[附件/image/10_优化器选错索引执行语句-8.jpg]]
但这过程需要测试发布, 不够敏捷
2. 第二种方法就是，我们可以考虑修改语句，引导 MySQL 使用我们期望的索引。比如，在这个例子里，显然把“order by b limit 1” 改成 “order by b,a limit 1”
	![[附件/image/10_优化器选错索引执行语句-9.jpg]]
	当然, 必须要逻辑一致, 才可以这样做
	- 另一种改法:

	```sql
	mysql> select * from  (select * from t where (a between 1 and 1000)  and (b between 50000 and 100000) order by b limit 100)alias limit 1;
	```

	强行让优化器认为, 使用 b 索引的排序代价也不低哦, 有诱导, 也不是很通用

3. 第三种方法, 我们新建一个更合适的索引, 来给优化器做选择, 或者删除不合适的索引.

### 小结

1. 通过一个意料之外的长查询, 发现优化器有时候会选错索引
2. 优化器会考虑回表的代价, 也会考虑排序的代价
3. 选错索引的处理方式, 一般性的可以 anylize, 特殊性的强行指定索引, 修改查询语句, 或者删除某些索引.

## 选错索引思考

- 通过 session A 的配合，让 session B 删除数据后又重新插入了一遍数据，然后就发现 explain 结果中，rows 字段从 10001 变成 37000 多。
  而如果没有 session A 的配合，只是单独执行 delete from t 、call idata()、explain 这三句话，会看到 rows 字段其实还是 10000 左右。为什么?
