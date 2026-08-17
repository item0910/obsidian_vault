---
tags: 归档笔记/学习笔记/MySQL
title: 16_'order by'是怎么工作的
date: 2022-09-13
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

```sql
CREATE TABLE `t` (
  `id` int(11) NOT NULL,
  `city` varchar(16) NOT NULL,
  `name` varchar(16) NOT NULL,
  `age` int(11) NOT NULL,
  `addr` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `city` (`city`)
) ENGINE=InnoDB;
```

现在要查询前 1000 个名字的市民

```sql
select city,name,age from t where city='杭州' order by name limit 1000  ;
```

## 'order by' 是怎么工作的

### 全字段排序

给 'city' 加全字段索引之后, 我们来看这条语句的排序情况

![[附件/image/16_'order by'是怎么工作的.jpg]]

Extra 这个字段中的“Using filesort”表示的就是需要排序，MySQL 会给每个线程分配一块内存用于排序，称为 sort_buffer。

![[附件/image/16_'order by'是怎么工作的-1663715080338.jpeg]]

1. 初始化 sort_buffer，确定放入 name、city、age 这三个字段；
2. 从索引 city 找到第一个满足 city=杭州条件的主键 id，也就是图中的 ID_X；
3. 到主键 id 索引取出整行，取 name、city、age 三个字段的值，存入 sort_buffer 中；
4. 从索引 city 取下一个记录的主键 id；
5. 重复步骤 3、4 直到 city 的值不满足查询条件为止，对应的主键 id 也就是图中的 ID_Y；
6. 对 sort_buffer 中的数据按照字段 name 做快速排序；
7. 按照排序结果取前 1000 行返回给客户端。

“按 name 排序”这个动作，可能在内存中完成，也可能需要使用外部排序，这取决于排序所需的内存和参数 sort_buffer_size。

sort_buffer_size，就是 MySQL 为排序开辟的内存（sort_buffer）的大小。如果要排序的数据量小于 sort_buffer_size，排序就在内存中完成。但如果排序数据量太大，内存放不下，则不得不利用磁盘临时文件辅助排序。

可以用下面的办法来看有没有用到磁盘临时文件

```sql
/* 打开optimizer_trace，只对本线程有效 */
SET optimizer_trace='enabled=on'; 

/* @a保存Innodb_rows_read的初始值 */
select VARIABLE_VALUE into @a from  performance_schema.session_status where variable_name = 'Innodb_rows_read';

/* 执行语句 */
select city, name,age from t where city='杭州' order by name limit 1000; 

/* 查看 OPTIMIZER_TRACE 输出 */
SELECT * FROM `information_schema`.`OPTIMIZER_TRACE`\G

/* @b保存Innodb_rows_read的当前值 */
select VARIABLE_VALUE into @b from performance_schema.session_status where variable_name = 'Innodb_rows_read';

/* 计算Innodb_rows_read差值 */
select @b-@a;
```

这个方法是通过查看 `OPTIMIZER_TRACE` 的结果来确认的，你可以从 `number_of_tmp_files` 中看到是否使用了临时文件。

![[附件/image/16_'order by'是怎么工作的-2.jpg]]

为什么是 12?

外部排序一般使用归并排序算法。可以这么简单理解，MySQL 将需要排序的数据分成 12 份，每一份单独排序后存在这些临时文件中。然后把这 12 个有序文件再合并成一个有序的大文件。

sort_buffer_size 越小，需要分成的份数越多，number_of_tmp_files 的值就越大。

我们的示例表中有 4000 条满足 city=' 杭州’的记录，所以你可以看到 examined_rows=4000，表示参与排序的行数是 4000 行。

sort_mode 里面的 packed_additional_fields 的意思是，排序过程对字符串做了“紧凑”处理。即使 name 字段的定义是 varchar(16)，在排序过程中还是要按照实际长度来分配空间的。

### rowid 排序

如果 MySQL 认为排序的单行长度太大会怎么做呢？接下来，我来修改一个参数，让 MySQL 采用另外一种算法。

设置, max_length_for_sort_data 它的意思是，如果单行的长度超过这个值，MySQL 就认为单行太大，要换一个算法。 ^a87e4f

```sql
SET max_length_for_sort_data = 16;
```

city、name、age 这三个字段的定义总长度是 36，我把 max_length_for_sort_data 设置为 16，我们再来看看计算过程有什么改变。新的算法放入 sort_buffer 的字段，**只有要排序的列（即 name 字段）和主键 id**。

再看一下这个过程有什么改变

```sql
select city,name,age from t where city='杭州' order by name limit 1000  ;
```

1. 初始化 sort_buffer，确定放入两个字段，即 name 和 id；
2. 从索引 city 找到第一个满足 city=' 杭州’条件的主键 id，也就是图中的 ID_X；
3. 到主键 id 索引取出整行，取 name、id 这两个字段，存入 sort_buffer 中；
4. 从索引 city 取下一个记录的主键 id；
5. 重复步骤 3、4 直到不满足 city=' 杭州’条件为止，也就是图中的 ID_Y；
6. 对 sort_buffer 中的数据按照字段 name 进行排序；
7. 遍历排序结果，取前 1000 行，并按照 id 的值回到原表中取出 city、name 和 age 三个字段返回给客户端。

这个过程我们称为 rowid 排序

需要说明的是，最后的“结果集”是一个逻辑概念，实际上 MySQL 服务端从排序后的 sort_buffer 中依次取出 id，然后到原表查到 city、name 和 age 这三个字段的结果，不需要在服务端再耗费内存存储结果，是直接返回给客户端的。 任务已经完成, 无需存储. 查到一个就返回一个

再看 select @b-@a :

首先，图中的 `examined_rows` 的值还是 4000，表示用于排序的数据是 4000 行。但是 select @b-@a 这个语句的值变成 5000 了。因为这时候除了排序过程外，在排序完成后，还要根据 id 去原表取值。由于语句是 limit 1000，因此会多读 1000 行。

![[附件/image/16_'order by'是怎么工作的-3.jpg]]

- `sort_mode` 变成了 <sort_key, rowid>，表示参与排序的只有 name 和 id 这两个字段。

- `number_of_tmp_files` 变成 10 了，是因为这时候参与排序的行数虽然仍然是 4000 行，但是每一行都变小了，因此需要排序的总数据量就变小了，需要的临时文件也相应地变少了。

### 二者比较

这也就体现了 MySQL 的一个设计思想：如果内存够，就要多利用内存，尽量减少磁盘访问。

对于 InnoDB 表来说，rowid 排序会要求回表多造成磁盘读，因此不会被优先选择。

如果, 我们在这个市民表上创建一个 city 和 name 的联合索引，对应的 SQL 语句是：

```sql
alter table t add index city_user(city, name);
```

![[附件/image/16_'order by'是怎么工作的-4.jpg]]

只要 city 的值是杭州，name 的值就一定是有序的。

1. 从索引 (city,name) 找到第一个满足 city=' 杭州’条件的主键 id；
2. 到主键 id 索引取出整行，取 name、city、age 三个字段的值，作为结果集的一部分直接返回；
3. 从索引 (city,name) 取下一个记录主键 id；
4. 重复步骤 2、3，直到查到第 1000 条记录，或者是不满足 city=' 杭州’条件时循环结束。

![[附件/image/16_'order by'是怎么工作的-5.jpg]]

Extra 字段中没有 Using filesort 了，也就是不需要排序了。而且由于 (city,name) 这个联合索引本身有序

图中 rows 是预估行数, 实际扫描行数可以从慢查询日志中看

```sql
set long_query_time=0; ## 将慢查询日志的阈值设为0, 使接下来的操作都会被记入慢查询
```

更进一步的, 有一个更深入的联合索引

```sql
alter table t add index city_user_age(city, name, age);
```

1. 从索引 (city,name,age) 找到第一个满足 city=' 杭州’条件的记录，取出其中的 city、name 和 age 这三个字段的值，作为结果集的一部分直接返回；
2. 从索引 (city,name,age) 取下一个记录，同样取出这三个字段的值，作为结果集的一部分直接返回；
3. 重复执行步骤 2，直到查到第 1000 条记录，或者是不满足 city=' 杭州’条件时循环结束。

连回表也不用了

![[附件/image/16_'order by'是怎么工作的-6.jpg]]

直接就是 using index

### 小结

1. 全字段排序, sort_buffer
2. rowid 排序, 只用到需要的字段
3. 利用联合索引完成排序

## 'order by' 是怎么工作的思考

- 假设你的表里面已经有了 city_name(city, name) 这个联合索引，然后你要查杭州和苏州两个城市中所有的市民的姓名，并且按名字排序，显示前 100 条记录。如果 SQL 查询语句是这么写的 ：

```sql
mysql> select * from t where city in ('杭州',"苏州") order by name limit 100;
```

  那么，这个语句执行的时候会有排序过程吗，为什么？如果业务端代码由你来开发，需要实现一个在数据库端不需要排序的方案，你会怎么实现呢？

  进一步地，如果有分页需求，要显示第 101 页，也就是说语句最后要改成 “limit 10000,100”， 你的实现方法又会是什么呢？

  那怎么避免排序呢？这里，我们要用到 (city,name) 联合索引的特性，把这一条语句拆成两条语句，执行流程如下：

1. 执行 `select * from t where city=“杭州” order by name limit 100;` 这个语句是不需要排序的，客户端用一个长度为 100 的内存数组 A 保存结果。
2. 执行 `select * from t where city=“苏州” order by name limit 100;` 用相同的方法，假设结果被存进了内存数组 B。
3. 现在 A 和 B 是两个有序数组，然后你可以用归并排序的思想，得到 name 最小的前 100 值，就是我们需要的结果了。

如果把这条 SQL 语句里“limit 100”改成“limit 10000,100”的话，处理方式其实也差不多，即：要把上面的两条语句改成写：

```sql
select * from t where city="杭州" order by name limit 10100; 
```

和

```sql
select * from t where city="苏州" order by name limit 10100
```

这时候数据量较大，可以同时起两个连接一行行读结果，用归并排序算法拿到这两个结果集里，

按顺序取第 10001~10100 的 name 值，就是需要的结果了。

当然这个方案有一个明显的损失，就是从数据库返回给客户端的数据量变大了。所以，如果数据的单行比较大的话，可以考虑把这两条 SQL 语句改成下面这种写法：

```sql
select id,name from t where city="杭州" order by name limit 10100; 
```

和

```sql
select id,name from t where city="苏州" order by name limit 10100。
```

然后，再用归并排序的方法取得按 name 顺序第 10001~10100 的 name、id 的值，然后拿着这 100 个 id 到数据库中去查出所有记录。上面这些方法，需要你根据性能需求和开发的复杂度做出权衡。
