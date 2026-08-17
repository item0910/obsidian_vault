---
tags: 归档笔记/学习笔记/MySQL
title: 43_分区表
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 分区表

### 分区表是什么

```sql
CREATE TABLE `t` (
  `ftime` datetime NOT NULL,
  `c` int(11) DEFAULT NULL,
  KEY (`ftime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
PARTITION BY RANGE (YEAR(ftime))
(PARTITION p_2017 VALUES LESS THAN (2017) ENGINE = InnoDB,
 PARTITION p_2018 VALUES LESS THAN (2018) ENGINE = InnoDB,
 PARTITION p_2019 VALUES LESS THAN (2019) ENGINE = InnoDB,
PARTITION p_others VALUES LESS THAN MAXVALUE ENGINE = InnoDB);
insert into t values('2017-4-1',1),('2018-4-1',1);
```

磁盘上的表文件

![[附件/image/43_分区表-1663955775956.jpeg]]

我在表 t 中初始化插入了两行记录，按照定义的分区规则，这两行记录分别落在 p_2018 和 p_2019 这两个分区上。

这个表包含了一个.frm 文件和 4 个.ibd 文件，每个分区对应一个.ibd 文件。也就是说：

- 对于引擎层来说，这是 4 个表；
- 对于 Server 层来说，这是 1 个表。

### 分区表的引擎层行为

证明对于 InnoDB 来说, 这是四个表

![[附件/image/43_分区表-1663955930660.jpeg]]

![[附件/image/43_分区表-1663955969874.jpeg]]

如果是一个普通表, 应该会在如图位置加上间隙锁.

而实际的加锁范围为:

![[附件/image/43_分区表-1663956025257.jpeg]]

![[附件/image/43_分区表-1663956045274.jpeg]]

MyISAM 也是 一样

![[附件/image/43_分区表-1663956075760.jpeg]]

MyISAM 引擎只支持表锁，所以这条 update 语句会锁住整个表 t 上的读。但实际上还是没有锁住整个表.

我们使用分区表的一个重要原因就是单表过大。那么，如果不使用分区表的话，我们就是要使用手动分表的方式。接下来，我们一起看看手动分表和分区表有什么区别。

我们就分别创建普通表 t_2017、t_2018、t_2019 等等。手工分表的逻辑，也是找到需要更新的所有分表，然后依次执行更新。在性能上，这和分区表并没有实质的差别。

手动分表, 从直观上来看, 一个就是从应用层来决定应该用哪个表, 一个就是从数据层来看, 从引擎层来说, 这两种方式也是没有区别的.

主要是在 server 层上。从 server 层看，我们就不得不提到分区表一个被广为诟病的问题：打开表的行为。

### 分区策略

每当第一次访问一个分区表的时候，MySQL 需要把所有的分区都访问一遍。一个典型的报错情况是这样的：如果一个分区表的分区很多，比如超过了 1000 个，而 MySQL 启动的时候，open_files_limit 参数使用的是默认值 1024，那么就会在访问这个表的时候，由于需要打开所有的文件，导致打开表文件的个数超过了上限而报错。

![[附件/image/43_分区表-1663956253632.jpeg]]

你一定从表名猜到了，这个表我用的是 MyISAM 引擎。是的，因为使用 InnoDB 引擎的话，并不会出现这个问题。

MyISAM 分区表使用的分区策略，我们称为通用分区策略（generic partitioning），每次访问分区都由 server 层控制。通用分区策略，是 MySQL 一开始支持分区表的时候就存在的代码，在文件管理、表管理的实现上很粗糙，因此有比较严重的性能问题。

从 MySQL 5.7.9 开始，InnoDB 引擎引入了本地分区策略（native partitioning）。这个策略是在 InnoDB 内部自己管理打开分区的行为。

MySQL 从 5.7.17 开始，将 MyISAM 分区表标记为即将弃用 (deprecated)

从 MySQL 8.0 版本开始，就不允许创建 MyISAM 分区表了，只允许创建已经实现了本地分区策略的引擎, 目前来看，只有 InnoDB 和 NDB 这两个引擎支持了本地分区策略

### 分区表的 server 层行为

如果从 server 层来看, 分区表就是一个表

![[附件/image/43_分区表-1663956471362.jpeg]]

![[附件/image/43_分区表-1663956481619.jpeg]]

由于 session 持有 t 的 MDL 锁, 所以 B 被 block

所以当分区表做 DDL 的时候, 影响的范围更大; 当你用普通的分表做 DDL 的时候, 肯定不会对另一个分表造成影响.

小结
- MySQL 在第一次打开分区表的时候，需要访问所有的分区；
- 在 server 层，认为这是同一张表，因此所有分区共用同一个 MDL 锁；
- 在引擎层，认为这是不同的表，因此 MDL 锁之后的执行过程，会根据分区表规则，只访问必要的分区。

而关于“必要的分区”的判断，就是根据 SQL 语句中的 where 条件，结合分区规则来实现的。比如我们上面的例子中，where ftime='2018-4-1'，根据分区规则 year 函数算出来的值是 2018，那么就会落在 p_2019 这个分区。
但是，如果这个 where 条件改成 where ftime>='2018-4-1'，虽然查询结果相同，但是这时候根据 where 条件，就要访问 p_2019 和 p_others 这两个分区。

### 分区表的应用场景

分区表的一个显而易见的优势是对业务透明，相对于用户分表来说，使用分区表的业务代码更简洁。还有，分区表可以很方便的清理历史数据。

如果一项业务跑的时间足够长，往往就会有根据时间删除历史数据的需求。这时候，按照时间分区的分区表，就可以直接通过 alter table t drop partition ... 这个语法删掉分区，从而删掉过期的历史数据。

这个 alter table t drop partition ... 操作是直接删除分区文件，效果跟 drop 普通表类似。与使用 delete 语句删除数据相比，优势是**速度快、对系统影响小**。

### 小结

1. 分区表在 server 层和引擎层的对象是不同的
2. 分区表还有 hash 分区, list 分区等方法, [MySQL :: MySQL 8.0 Reference Manual :: 24.2 Partitioning Types](https://dev.mysql.com/doc/refman/8.0/en/partitioning-types.html)
3. 分区表第一次访问要范文所有的分区; 另一点, 分区表公用 MDL 锁

建议
- 分区并不是越细越好。实际上，单表或者单分区的数据一千万行，只要没有特别大的索引，对于现在的硬件能力来说都已经是小表了。
- 分区也不要提前预留太多，在使用之前预先创建即可。比如，如果是按月分区，每年年底时再把下一年度的 12 个新分区创建上即可。对于没有数据的历史分区，要及时的 drop 掉。

## 分区表思考

我们举例的表中没有用到自增主键， 假设现在要创建一个自增字段 id。 MySQL 要求分区表中的主键必须包含分区字段。 如果要在表 t 的基础上做修改， 你会怎么定义这个表的主键呢？ 为什么这么定义呢？

```sql
CREATE TABLE `t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ftime` datetime NOT NULL,
  `c` int(11) DEFAULT NULL,
  PRIMARY KEY (`ftime`,`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
PARTITION BY RANGE (YEAR(ftime))
(PARTITION p_2017 VALUES LESS THAN (2017) ENGINE = InnoDB,
 PARTITION p_2018 VALUES LESS THAN (2018) ENGINE = InnoDB,
 PARTITION p_2019 VALUES LESS THAN (2019) ENGINE = InnoDB,
 PARTITION p_others VALUES LESS THAN MAXVALUE ENGINE = InnoDB);
```

联合主键, ftime, id

由于 MySQL 要求主键包含所有的分区字段，所以肯定是要创建联合主键的。

如果从利用率上来看，应该使用 (ftime, id) 这种模式。因为用 ftime 做分区 key，说明大多数语句都是包含 ftime 的，使用这种模式，可以利用前缀索引的规则，减少一个索引。

InnoDB 表要求至少有一个索引，以自增字段作为第一个字段，所以需要加一个 id 的单独索引。
