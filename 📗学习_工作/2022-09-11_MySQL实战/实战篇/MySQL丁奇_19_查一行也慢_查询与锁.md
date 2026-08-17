---
tags: 归档笔记/学习笔记/MySQL
title: 19_查一行也慢_查询与锁
date: 2022-09-14
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

有表

```sql
mysql> CREATE TABLE `t` (
  `id` int(11) NOT NULL,
  `c` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

delimiter ;;
create procedure idata()
begin
  declare i int;
  set i=1;
  while(i<=100000) do
    insert into t values(i,i);
    set i=i+1;
  end while;
end;;
delimiter ;

call idata();
```

## 查一行也慢 _ 查询与锁

### 第一类: 查询长时间不返回

```sql
mysql> select * from t where id=1;
```

#### 等表锁

大概率是表 t 被锁住了。接下来分析原因的时候，一般都是首先执行一下 show processlist 命令，看看当前语句处于什么状态。

![[附件/image/19_查一行也慢_查询与锁.jpg]]

复现方法:

![[附件/image/19_查一行也慢_查询与锁-1.jpg]]

session A 通过 lock table 命令持有表 t 的 MDL 写锁，而 session B 的查询需要获取 MDL 读锁。所以，session B 进入等待状态。

这类问题的处理方式，就是找到谁持有 MDL 写锁，然后把它 kill 掉。

但是，由于在 show processlist 的结果里面，session A 的 Command 列是“Sleep”，导致查找起来很不方便。不过有了 performance_schema 和 sys 系统库以后，就方便多了。（MySQL 启动时需要设置 performance_schema=on，相比于设置为 off 会有 10% 左右的性能损失)

通过查询 sys.schema_table_lock_waits 这张表，我们就可以直接找出造成阻塞的 process id，把这个连接用 kill 命令断开即可。

![[附件/image/19_查一行也慢_查询与锁-2.jpg]]

```sql
mysql> select * from information_schema.processlist where id=1;
```

查出这个状态是

![[附件/image/19_查一行也慢_查询与锁-3.jpg]]

MySQL 里面对表做 flush 操作的用法，一般有以下两个：

```sql
flush tables t with read lock;

flush tables with read lock;
```

这两个 flush 语句，如果指定表 t 的话，代表的是只关闭表 t；如果没有指定具体的表名，则表示关闭 MySQL 里所有打开的表。

出现 Waiting for table flush 状态的可能情况是：有一个 flush tables 命令被别的语句堵住了，然后它又堵住了我们的 select 语句。

![[附件/image/19_查一行也慢_查询与锁-4.jpg]]

在 session A 中，我故意每行都调用一次 sleep(1)，这样这个语句默认要执行 10 万秒，在这期间表 t 一直是被 session A“打开”着。然后，session B 的 flush tables t 命令再要去关闭表 t，就需要等 session A 的查询结束。这样，session C 要再次查询的话，就会被 flush 命令堵住了。

![[附件/image/19_查一行也慢_查询与锁-5.jpg]]

将 select sleep(1) from t 的进程结束

#### 等行锁

```sql
mysql> select * from t where id=1 lock in share mode; 
```

![[附件/image/19_查一行也慢_查询与锁-6.jpg]]

![[附件/image/19_查一行也慢_查询与锁-7.jpg]]

可以通过 sys.innodb_lock_waits 表查到。查询方法是：

```sql
mysql> select * from t sys.innodb_lock_waits where locked_table='`test`.`t`'\G
```

![[附件/image/19_查一行也慢_查询与锁-8.jpg]]

可以看到，这个信息很全，4 号线程是造成堵塞的罪魁祸首。而干掉这个罪魁祸首的方式，就是 KILL QUERY 4 或 KILL 4。

不过，这里不应该显示“KILL QUERY 4”。这个命令表示停止 4 号线程当前正在执行的语句，而这个方法其实是没有用的。因为占有行锁的是 update 语句，这个语句已经是之前执行完成了的，现在执行 KILL QUERY，无法让这个事务去掉 id=1 上的行锁。

实际上，KILL 4 才有效，也就是说直接断开这个连接。这里隐含的一个逻辑就是，连接被断开的时候，会自动回滚这个连接里面正在执行的线程，也就释放了 id=1 上的行锁。

### 第二类: 查询慢

```sql
mysql> select * from t where c=50000 limit 1;
```

由于字段 c 上没有索引，这个语句只能走 id 主键顺序扫描，因此需要扫描 5 万行。

作为确认，你可以看一下慢查询日志。注意，这里为了把所有语句记录到 slow log 里，我在连接后先执行了 set long_query_time=0，将慢查询日志的时间阈值设置为 0。

![[附件/image/19_查一行也慢_查询与锁-9.jpg]]

扫描行数多，所以执行慢，这个很好理解。

但是

```sql
mysql> select * from t where id=1；
```

![[附件/image/19_查一行也慢_查询与锁-10.jpg]]

时间都花哪儿去了?

![[附件/image/19_查一行也慢_查询与锁-11.jpg]]

这个加锁的却只花了 0.2 毫秒.

两个语句的结果

![[附件/image/19_查一行也慢_查询与锁-12.jpg]]

中间 sessionB 把 c 加了 100000 次, 第一句语句要回滚的时候, 需要读大量 redo log

![[附件/image/19_查一行也慢_查询与锁-13.jpg]]

带 lock in share mode 的 SQL 语句，是当前读，因此会直接读到 1000001 这个结果，所以速度很快；而 select * from t where id=1 这个语句，是一致性读，因此需要从 1000001 开始，依次执行 undo log，执行了 100 万次以后，才将 1 这个结果返回。

### 小结

查询慢的原因:
1. 等表锁
2. 等行锁
3. flush
4. 遇到需要大回滚的情况

## 查一行也慢 _ 查询与锁思考

- 但如果是下面的 SQL 语句，

	```sql
	begin;
	select * from t where c=5 for update;
	commit;
	```

这个语句会命中 d=5 的这一行，对应的主键 id=5，因此在 select 语句执行完成后，id=5 这一行会加一个写锁，而且由于两阶段锁协议，这个写锁会在执行 commit 语句的时候释放。

由于字段 d 上没有索引，因此这条查询语句会做全表扫描。那么，其他被扫描到的，但是不满足条件的 5 行记录上，会不会被加锁呢？

RR 级别：扫描到的数据都会加行锁和间隙锁 RC 级别：扫描到的数据都会加行锁，但是不满足条件的数据，没有到 commit 阶段，就会释放
