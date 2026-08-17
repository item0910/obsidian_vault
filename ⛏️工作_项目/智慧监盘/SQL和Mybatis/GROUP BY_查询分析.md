---
title: group_by_查询分析
date: 2026-03-15
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/数据库
author: 自己
---

## 对话内容大致纲要

来源对话：<https://gemini.google.com/share/172932ac172b>

这部分问题聚焦在 MySQL 使用 `GROUP BY` 时，报错提示：

```sql
sql_mode=only_full_group_by
```

当时的困惑点是：

- 为什么一个字符串字段也不能直接查；
- 为什么写了 `GROUP BY` 之后，`SELECT` 里的字段还会报错。

核心结论是：**这个问题和字段是不是 String 没关系，而是和 SQL 分组后的语义是否明确有关。**

## 重点复盘点

### 1. `ONLY_FULL_GROUP_BY` 的本质

当 MySQL 开启 `ONLY_FULL_GROUP_BY` 时，要求：

- `SELECT` 里的非聚合字段；
- 如果没有被 `SUM / COUNT / MAX / MIN / GROUP_CONCAT` 等聚合函数处理；
- 那么它就必须出现在 `GROUP BY` 子句中。

否则数据库会认为结果有歧义。

---

### 2. 为什么会有歧义

例如数据如下：

```sql
id | name | address
1  | A    | Shanghai
2  | A    | Beijing
3  | B    | Shenzhen
```

如果写：

```sql
SELECT name, address
FROM your_table
GROUP BY name;
```

那么对于 `name = A` 这一组：

- address 到底该返回 `Shanghai`
- 还是 `Beijing`

数据库无法确定。

所以在 `ONLY_FULL_GROUP_BY` 模式下，这种写法会直接报错。

这和 `address` 是不是字符串没有关系。就算它是数字、日期，逻辑上只要“组内可能有多个值”，一样会有问题。

---

### 3. 常见解决方式

#### 方式一：把非聚合字段补进 `GROUP BY`

```sql
SELECT name, address, COUNT(*)
FROM your_table
GROUP BY name, address;
```

适合本来就需要按 `name + address` 维度一起分组的情况。

---

#### 方式二：对该字段使用聚合函数

例如：

```sql
SELECT name, MAX(address) AS address
FROM your_table
GROUP BY name;
```

或者：

```sql
SELECT name, GROUP_CONCAT(address) AS address_list
FROM your_table
GROUP BY name;
```

这表示你明确告诉数据库：

- 要么取一条代表值；
- 要么把这一组的所有值汇总起来。

---

#### 方式三：关闭 `ONLY_FULL_GROUP_BY`

例如：

```sql
SET sql_mode = (SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));
```

这能让 SQL 暂时跑起来，但不推荐作为常规方案。

原因是：

- SQL 虽然不报错了；
- 但数据库帮你“随便取哪个值”并不总是可控；
- 在生产环境里容易造成结果不稳定。

## 引申知识点

### 1. 写 `GROUP BY` 时，先想清楚“每组到底要返回什么”

这是最关键的一点。

只要用了 `GROUP BY`，就意味着多行会压成一行。那就必须明确：

- 哪些字段是分组维度；
- 哪些字段是统计值；
- 哪些字段需要聚合后再展示。

如果这一点没想清楚，SQL 很容易写出“能跑但结果不可靠”的版本。

---

### 2. `GROUP_CONCAT` 在排查问题时很有用

当你不确定组内到底有哪些值时，可以先写：

```sql
SELECT name, GROUP_CONCAT(address) AS address_list
FROM your_table
GROUP BY name;
```

这样至少能先看清楚一组里到底有哪些 `address`，再决定后面是取 `MAX/MIN`，还是调整分组维度。

## 可直接记住的结论

- `ONLY_FULL_GROUP_BY` 报错，**不是字段类型问题**。
- 根本原因是：`GROUP BY` 后，`SELECT` 中出现了未明确处理的非聚合字段。
- 优先方案是：
  - 要么把字段补进 `GROUP BY`；
  - 要么对字段使用聚合函数。
- 不建议靠关闭 `ONLY_FULL_GROUP_BY` 来长期兜底。
