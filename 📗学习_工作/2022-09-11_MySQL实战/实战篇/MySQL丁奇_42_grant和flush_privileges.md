---
tags: 归档笔记/学习笔记/MySQL
title: 42_grant和flush_privileges
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

首先, 我先创建一个用户

```sql
create user 'ua'@'%' identified by 'pa';
```

这条语句的逻辑是创建一个用户’ua’@’%’，密码是 pa。注意，在 MySQL 里面，用户名 (user)+ 地址 (host) 才表示一个用户，因此 ua@ip1 和 ua@ip2 代表的是两个不同的用户。

在磁盘和内存上, MySQL 会做两个动作

1. 磁盘上，往 mysql.user 表里插入一行，由于没有指定权限，所以这行数据上所有表示权限的字段的值都是 N；
2. 内存里，往数组 acl_users 里插入一个 acl_user 对象，这个对象的 access 字段值为 0。

在 mysql.user 中

![[附件/image/42_grant和flush_privileges-1663954758554.jpeg]]

本节就是将如何给用户赋予权限和 flush privileges 的用法

## grant 和 flush_privileges

### 全局权限

```sql
grant all privileges on *.* to 'ua'@'%' with grant option;
```

这条语句有两个动作:

1. 磁盘上，将 mysql.user 表里，用户’ua’@’%' 这一行的所有表示权限的字段的值都修改为‘Y’；
2. 内存里，从数组 acl_users 中找到这个用户对应的对象，将 access 值（权限位）修改为二进制的“全 1”。

在这个 grant 命令执行完成后，如果有新的客户端使用用户名 ua 登录成功，MySQL 会为新连接维护一个线程对象，然后从 acl_users 数组里查到这个用户的权限，并将权限值拷贝到这个线程对象中。之后在这个连接中执行的语句，所有关于全局权限的判断，都直接使用线程对象内部保存的权限位。

我们可以知道

1. grant 命令对于全局权限，同时更新了磁盘和内存。命令完成后即时生效，接下来新创建的连接会使用新的权限。
2. 对于一个已经存在的连接，它的全局权限不受 grant 命令的影响。

>一般在生产环境上要合理控制用户权限的范围。我们上面用到的这个 grant 语句就是一个典型的错误示范。如果一个用户有所有权限，一般就不应该设置为所有 IP 地址都可以访问。

回收权限:

```sql
revoke all privileges on *.* from 'ua'@'%';
```

也是两个动作

1. 磁盘上，将 mysql.user 表里，用户’ua’@’%' 这一行的所有表示权限的字段的值都修改为“N”；
2. 内存里，从数组 acl_users 中找到这个用户对应的对象，将 access 的值修改为 0。

### db 权限

赋予 db1 的权限

```sql
grant all privileges on db1.* to 'ua'@'%' with grant option;
```

动作:

1. 磁盘上，往 mysql.db 表中插入了一行记录，所有权限位字段设置为“Y”；
2. 内存里，增加一个对象到数组 acl_dbs 中，这个对象的权限位为“全 1”。
![[附件/image/42_grant和flush_privileges-1663955010037.jpeg]]

每次需要判断一个用户对一个数据库读写权限的时候，都需要遍历一次 acl_dbs 数组，根据 user、host 和 db 找到匹配的对象，然后根据对象的权限位来判断。

grant 修改 db 权限的时候，是同时对磁盘和内存生效的。

但是对于已经存在的连接, 效果是不一样的

![[附件/image/42_grant和flush_privileges-1663964908303.jpeg]]

 set global sync_binlog 这个操作是需要 super 权限的

 因为 super 是全局权限，这个权限信息在线程对象中，所以 t3 时, revoke 操作影响不到线程对象。

而在 T5 时刻去掉 ua 对 db1 库的所有权限后，在 T6 时刻 session B 再操作 db1 库的表，就会报错“权限不足”。这是因为 acl_dbs 是一个全局数组，所有线程判断 db 权限都用这个数组，这样 revoke 操作马上就会影响到 session B。

C 之所以没有被影响, 是因为之前使用了 use db1, 已经获取了这个 db 的权限, 在切换出之前, 就一直有权限.

### 表权限和列权限

MySQL 支持更细粒度的表权限和列权限。其中，表权限定义存放在表 mysql.tables_priv 中，列权限定义存放在表 mysql.columns_priv 中。这两类权限，组合起来存放在内存的 hash 结构 column_priv_hash 中。

```sql
create table db1.t1(id int, a int);

grant all privileges on db1.t1 to 'ua'@'%' with grant option;
GRANT SELECT(id), INSERT (id,a) ON mydb.mytbl TO 'ua'@'%' with grant option;
```

与上面一样, grant 操作也是同时对磁盘和内存生效的

flush privileges 命令会清空 acl_users 数组，然后从 mysql.user 表中读取数据重新加载，重新构造一个 acl_users 数组。也就是说，以数据表中的数据为准，会将全局权限内存数组重新加载一遍。

也就是说，如果内存的权限数据和磁盘数据表相同的话，不需要执行 flush privileges。而如果我们都是用 grant/revoke 语句来执行的话，内存和数据表本来就是保持同步更新的。

### flush privileges 使用场景

显然，当数据表中的权限数据跟内存中的权限数据不一致的时候，flush privileges 语句可以用来重建内存数据，达到一致状态。

这种不一致往往是由不规范的操作导致的，比如直接用 DML 语句操作系统权限表。我们来看一下下面这个场景：

![[附件/image/42_grant和flush_privileges-1663955557481.jpeg]]

T3 时刻虽然已经用 delete 语句删除了用户 ua，但是在 T4 时刻，仍然可以用 ua 连接成功。原因就是，这时候内存中 acl_users 数组中还有这个用户，因此系统判断时认为用户还正常存在。

flush 之后, 才无法访问.

一个现象:

![[附件/image/42_grant和flush_privileges-1663955605908.jpeg]]

又不能赋权, 又不能新建用户.

### 小结

1. 正常使用 grant 和 revoke 是不需要 flush privileges 的
2. 当不规范的操作权限表时, 需要用 flush privileges 来统一权限与磁盘表格一致.

## grant 和 flush_privileges 思考

在使用数据库或者写代码的过程中， 有没有遇到过类似的场景： 误用了很长时间以后， 由于一个契机发现“啊， 原来我错了这么久”？
