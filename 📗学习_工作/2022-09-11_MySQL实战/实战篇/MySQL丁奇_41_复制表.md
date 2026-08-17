---
tags: 归档笔记/学习笔记/MySQL
title: 41_复制表
date: 2022-09-17
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

上期问题是如何快速的复制表, 如果表的数据量较小的话, insert .. select 即可实现. 更稳妥的方法是将数据写到外部文本文件, 再写回表.

## 复制表

```sql
create database db1;
use db1;

create table t(id int primary key, a int, b int, index(a))engine=innodb;
delimiter ;;
  create procedure idata()
  begin
    declare i int;
    set i=1;
    while(i<=1000)do
      insert into t values(i,i,i);
      set i=i+1;
    end while;
  end;;
delimiter ;
call idata();

create database db2;
create table db2.t like db1.t
```

假设我们要将里面 a > 900 的行找出来导入到 db2

### mysqldump 方法

可以使用下面的命令

```shell
mysqldump -h$host -P$port -u$user --add-locks=0 --no-create-info --single-transaction  --set-gtid-purged=OFF db1 t --where="a>900" --result-file=/client_tmp/t.sql
```

就可以导出到临时文件中, 其中, 参数的含义如下

1. –single-transaction 的作用是，在导出数据的时候不需要对表 db1.t 加表锁，而是使用 START TRANSACTION WITH CONSISTENT SNAPSHOT 的方法；
2. –add-locks 设置为 0，表示在输出的文件结果里，不增加 " LOCK TABLES t WRITE;" ；
3. –no-create-info 的意思是，不需要导出表结构；
4. –set-gtid-purged=off 表示的是，不输出跟 GTID 相关的信息；
5. –result-file 指定了输出文件的路径，其中 client 表示生成的文件是在客户端机器上的。

输出文件 t.sql 如下:

![[附件/image/41_复制表-1663951924424.jpeg]]

一条 insert, 对应多个 value 对, 这样执行的速度更快

如果希望一条插入一行的话, 可以在执行上面的命令时, 加上参数–skip-extended-insert。

```shell
mysql -h127.0.0.1 -P13000  -uroot db2 -e "source /client_tmp/t.sql"
```

将文件放入 db2 执行

source 并不是一条 SQL 语句，而是一个客户端命令。mysql 客户端执行这个命令的流程是这样的：

1. 打开文件，默认以分号为结尾读取一条条的 SQL 语句；
2. 将 SQL 语句发送到服务端执行。

### 导出 CSV 文件

MySQL 提供了下面的语法将 sql 导出到本地

```sql
select * from db1.t where a>900 into outfile '/server_tmp/t.csv';
```

注意:

1. 这条语句会将结果保存在服务端。如果你执行命令的客户端和 MySQL 服务端不在同一个机器上，客户端机器的临时目录下是不会生成 t.csv 文件的。
2. into outfile 指定了文件的生成位置（/server_tmp/），这个位置必须受参数 secure_file_priv 的限制。参数 secure_file_priv 的可选值和作用分别是：
	1. 如果设置为 empty，表示不限制文件生成的位置，这是不安全的设置；
	2. 如果设置为一个表示路径的字符串，就要求生成的文件只能放在这个指定的目录，或者它的子目录；
	3. 如果设置为 NULL，就表示禁止在这个 MySQL 实例上执行 select … into outfile 操作。
3. 这条命令不会帮你覆盖文件，因此你需要确保 /server_tmp/t.csv 这个文件不存在，否则执行语句时就会因为有同名文件的存在而报错。
4. 这条命令生成的文本文件中，原则上一个数据行对应文本文件的一行。但是，如果字段中包含换行符，在生成的文本中也会有换行符。不过类似换行符、制表符这类符号，前面都会跟上“\”这个转义符，这样就可以跟字段之间、数据行之间的分隔符区分开。

导出 csv 文件后, 就可以通过下面的命令进行 load

```sql
load data infile '/server_tmp/t.csv' into table db2.t;
```

1. 打开文件 /server_tmp/t.csv，以制表符 (\t) 作为字段间的分隔符，以换行符（\n）作为记录之间的分隔符，进行数据读取；
2. 启动事务。
3. 判断每一行的字段数与表 db2.t 是否相同：
	1. 若不相同，则直接报错，事务回滚；
	2. 若相同，则构造成一行，调用 InnoDB 引擎接口，写入到表中。
4. 重复步骤 3，直到 /server_tmp/t.csv 整个文件读入完成，提交事务。

主库写完后, 在 binlog 中, 会有如下流程

1. 主库执行完成后，将 /server_tmp/t.csv 文件的内容直接写到 binlog 文件中。
2. 往 binlog 文件中写入语句 load data local infile ‘/tmp/SQL_LOAD_MB-1-0’ INTO TABLE ‘db2’.‘t’。
3. 把这个 binlog 日志传到备库。
4. 备库的 apply 线程在执行这个事务日志时：
	1. 先将 binlog 中 t.csv 文件的内容读出来，写入到本地临时目录 /tmp/SQL_LOAD_MB-1-0 中；
	2. 再执行 load data 语句，往备库的 db2.t 表中插入跟主库相同的数据。
![[41_复制表-1663952632221.jpeg]]

这里语句中 local 的意思是 将执行备库本地的内容. 如果不加 local 意思是不一样的.

1. 不加“local”，是读取服务端的文件，这个文件必须在 secure_file_priv 指定的目录或子目录下；
2. 加上“local”，读取的是客户端的文件，只要 mysql 客户端有访问这个文件的权限即可。这时候，MySQL 客户端会先把本地文件传给服务端，然后执行上述的 load data 流程。

注意: select …into outfile 方法不会生成表结构文件, 所以我们导数据时还需要单独的命令得到表结构定义。mysqldump 提供了一个–tab 参数，可以同时导出表结构定义文件和 csv 数据文件。这条命令的使用方法如下：

```shell
mysqldump -h$host -P$port -u$user ---single-transaction  --set-gtid-purged=OFF db1 t --where="a>900" --tab=$secure_file_priv
```

这条命令会在 $secure_file_priv 定义的目录下，创建一个 t.sql 文件保存建表语句，同时创建一个 t.txt 文件保存 CSV 数据。

### 物理拷贝方法

直接把 db1.t 表的.frm 文件和.ibd 文件拷贝到 db2 目录下，是否可行呢？ 不可行

因为，一个 InnoDB 表，除了包含这两个物理文件外，还需要在数据字典中注册。直接拷贝这两个文件的话，因为数据字典中没有 db2.t 这个表，系统是不会识别和接受它们的。

但是, 在 MySQL 5.6 版本引入了可传输表空间 (transportable tablespace) 的方法，可以通过导出 + 导入表空间的方式，实现物理拷贝表的功能。

假设我们现在的目标是在 db1 库下，复制一个跟表 t 相同的表 r，具体的执行步骤如下：

1. 执行 create table r like t，创建一个相同表结构的空表；
2. 执行 alter table r discard tablespace，这时候 r.ibd 文件会被删除；
3. 执行 flush table t for export，这时候 db1 目录下会生成一个 t.cfg 文件；
4. 在 db1 目录下执行 `cp t.cfg r.cfg`; `cp t.ibd r.ibd`；这两个命令（这里需要注意的是，拷贝得到的两个文件，MySQL 进程要有读写权限）；
5. 执行 unlock tables，这时候 t.cfg 文件会被删除；
6. 执行 alter table r import tablespace，将这个 r.ibd 文件作为表 r 的新的表空间，由于这个文件的数据内容和 t.ibd 是相同的，所以表 r 中就有了和表 t 相同的数据。

![[附件/image/41_复制表-1663953182936.jpeg]]

注意点:

1. 在第 3 步执行完 flush table 命令之后，db1.t 整个表处于只读状态，直到执行 unlock tables 命令后才释放读锁；
2. 在执行 import tablespace 的时候，为了让文件里的表空间 id 和数据字典中的一致，会修改 r.ibd 的表空间 id。而这个表空间 id 存在于每一个数据页中。因此，如果是一个很大的文件（比如 TB 级别），每个数据页都需要修改，所以你会看到这个 import 语句的执行是需要一些时间的。当然，如果是相比于逻辑导入的方法，import 语句的耗时是非常短的。

### 小结

拷贝方式小结:

1. 很小的数据, insert select from 就可以
2. mysqldump, 可以生成 sql 语句执行
3. csv 文件 (配合表结构使用), 和 mysqldump 类似, 要注意 local 的情况
4. 物理拷贝方法, 5.6 之后, 可以直接 import, 根据 cfg 和 ibd 文件.但是要注意原表会被锁住.

## 复制表思考

我们前面介绍 binlog_format=statement 的时候，binlog 记录的 load data 命令是带 local 的。既然这条命令是发送到备库去执行的，那么备库执行的时候也是本地执行，为什么需要这个 local 呢？如果写到 binlog 中的命令不带 local，又会出现什么问题呢？

这样做的一个原因是，为了确保备库应用 binlog 正常。因为备库可能配置了 secure_file_priv=null，所以如果不用 local 的话，可能会导入失败，造成主备同步延迟。

另一种应用场景是使用 mysqlbinlog 工具解析 binlog 文件，并应用到目标库的情况。你可以使用下面这条命令 ：

```shell
mysqlbinlog $binlog_file | mysql -h$host -P$port -u$user -p$pwd
```

把日志直接解析出来发给目标库执行。增加 local，就能让这个方法支持非本地的 $host。
