---
tags: 归档笔记/学习笔记/MySQL
title: 11_如何给字符串字段加索引
date: 2022-09-13
categories: MySQL
author: 丁奇
mtime: 2024-09-25
---

## 前言

有一个邮箱登陆表, 假设你是这样创建的

```sql
mysql> create table SUser(
ID bigint unsigned primary key,
email varchar(64), 
... 
)engine=innodb; 
```

一定有类似的登陆判断语句

```sql
mysql> select f1, f2 from SUser where email='xxx';
```

你可以给他创建全字段索引或者前缀索引

```sql
mysql> alter table SUser add index index1(email);
或
mysql> alter table SUser add index index2(email(6));
```

## 如何给字符串字段加索引

### 前缀索引还是全字段索引

- 结构上的区别: 全字段索引:
![[附件/image/11_如何给字符串字段加索引-1.jpg]]

前缀索引:

![[附件/image/11_如何给字符串字段加索引-2.jpg]]

可以看到, 前缀索引占用空间更少, 但会增加额外的扫描次数.

我们可以从他们的执行过程中看出来.

```sql
select id,name,email from SUser where email='zhangssxyz@xxx.com';
```

- 如果使用 index1
    1. 从 index1 索引树找到满足索引值是 zhangssxyz@xxx.com 的这条记录，取得 ID2 的值；
    2. 取 index1 索引树上刚刚查到的位置的下一条记录，发现已经不满足 email='zhangssxyz@xxx.com’的条件了，循环结束。
- 如果使用 index2
    1. 从 index2 索引树找到满足索引值是’zhangs’的记录，找到的第一个是 ID1；

    2. 到主键上查到主键值是 ID1 的行，判断出 email 的值不是’zhangssxyz@xxx.com’，这行记录丢弃；

    3. 取 index2 上刚刚查到的位置的下一条记录，发现仍然是’zhangs’，取出 ID2，再到 ID 索引上取整行然后判断，这次值对了，将这行记录加入结果集；

    4. 重复上一步，直到在 idxe2 上取到的值不是’zhangs’时，循环结束。

如果前缀索引是 7 位, 那么满足的只有 1 条, 回表一次就结束了.

也就是说 **使用前缀索引，定义好长度，就可以做到既节省空间，又不用额外增加太多的查询成本。**

我们要关注的就是前缀索引的区分度

我们可以用这个语句, 来算出同一列数据的唯一个数, 从而取比较多的那个做为前缀长度的候选.

```sql
mysql> select 
  count(distinct left(email,4)）as L4,
  count(distinct left(email,5)）as L5,
  count(distinct left(email,6)）as L6,
  count(distinct left(email,7)）as L7,
from SUser;
```

### 前缀索引的影响: 无法用覆盖索引

如果是这个查询:

```sql
select id,email from SUser where email='zhangssxyz@xxx.com';
```

不用查 name 了, 如果邮箱用了全字段索引, 那么就无需回表直接可以返回结果

而如果使用的是前缀索引, 即使是 email(18), 也要回表做判断.

### 其它索引的方式

提升前缀索引区分度的方法, 拿身份证来说:

比如，我们国家的身份证号，一共 18 位，其中前 6 位是地址码，所以同一个县的人的身份证号前 6 位一般会是相同的。

假设你维护的数据库是一个市的公民信息系统，这时候如果对身份证号做长度为 6 的前缀索引的话，这个索引的区分度就非常低了。

按照我们前面说的方法，可能你需要创建长度为 12 以上的前缀索引，才能够满足区分度要求。

但是，索引选取的越长，占用的磁盘空间就越大，相同的数据页能放下的索引值就越少，搜索的效率也就会越低。

#### 1. 倒叙存储

倒过来存, 每次查询的时候, 相当于用后六位做了索引.

```sql
mysql> select field_list from t where id_card = reverse('input_id_card_string');
```

后六位可能就提供了区分度.

#### 2. 使用 hash 字段作为索引

```sql
mysql> alter table t add id_card_crc int unsigned, add index(id_card_crc);
```

因为 hash 得到的码有可能发生碰撞, 取出时, 还要判断一下 id 是不是相同

```sql
mysql> select field_list from t where id_card_crc=crc32('input_id_card_string') and id_card='input_id_card_string'
```

这样, 索引的长度变为了 4 字节

**这两种方法有一个共同点, 都不能提供范围查询**

区别:

1. 倒叙存储因为索引还是存储了主键信息, 所以不用额外空间, 而 hash 需要一个额外的字段; 但 4 个字符的倒序显然不够, 当达到 6 个字符之后, 这个消耗跟哈希也差不多了

2. 倒序每次读写都要 reverse, 代价比 crc32() 函数要小

3. hash 字段更稳定, 可以看做近似是每次扫描一行, 而倒序不一定, 还是会增加扫描行数

### 小结

1. 从使用全字段索引和前缀索引的执行过程看去, 找到了二者的优劣
2. 基于前缀索引区分度不高的问题, 提出了倒序存储和新增哈希字段两种方法来提升区分度.

## 如何给字符串字段加索引思考

如果你在维护一个学校的学生信息数据库，学生登录名的统一格式是”学号@gmail.com", 而学号的规则是：十五位的数字，其中前三位是所在城市编号、第四到第六位是学校编号、第七位到第十位是入学年份、最后五位是顺序编号。

系统登录的时候都需要学生输入登录名和密码，验证正确后才能继续使用系统。就只考虑登录验证这个行为的话，你会怎么设计这个登录名的索引呢？

- 如果从答题的角度, 可以给安排一个年份 + 学号这样的索引, 但从实际出发, 因为一个学校的样本不大, 完全可以存全字段索引.
