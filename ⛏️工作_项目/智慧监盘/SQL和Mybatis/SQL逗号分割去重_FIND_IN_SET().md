---
title: SQL逗号分割去重
date: 2026-03-15
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/数据库
author: 自己
---

## 对话内容大致纲要

来源对话：<https://gemini.google.com/share/172932ac172b>

这次真正落地使用的需求，不是“把整个 `ids` 字段拆开后全量去重导出”，而是：

- 表里有一个 `ids` 字段；
- 这个字段里保存的是**逗号分隔的多个 id**；
- 现在需要根据某个指定 id 去筛选数据；
- 最后采用的方案是 MySQL 的 `FIND_IN_SET()`。

所以这篇文档只围绕 **“如何在逗号分隔字段中查找指定 id 并返回结果”** 记录，不再展开其他无关问题。

## 重点复盘点

### 1. 实际需求不是“整体 distinct”，而是“在 ids 字段里找到目标 id”

例如表中数据可能是这样：

```sql
id | ids
1  | 1,2,3
2  | 2,4,5
3  | 3,6
4  | 7,8
```

如果现在要找 **包含 id=3 的记录**，目标结果应该返回：

- 第 1 行：`1,2,3`
- 第 3 行：`3,6`

这个时候，核心不是把所有 id 拆出来去重，而是判断某个值是否存在于逗号分隔字符串中。

---

### 2. 最终采用方案：`FIND_IN_SET()`

MySQL 中可以直接用：

```sql
FIND_IN_SET('3', ids)
```

它的含义是：

- 如果 `3` 在 `ids` 这个逗号分隔字符串里，返回位置；
- 如果不存在，返回 `0`；
- 如果任一参数为 `NULL`，结果通常为 `NULL`。

因此常见筛选写法是：

```sql
SELECT *
FROM your_table
WHERE FIND_IN_SET('3', ids) > 0;
```

或者更直接：

```sql
SELECT *
FROM your_table
WHERE FIND_IN_SET('3', ids);
```

更稳一点的写法还是显式判断 `> 0`，可读性更好。

---

### 3. 示例

#### 示例一：查询包含指定 id 的记录

```sql
SELECT id, ids
FROM your_table
WHERE FIND_IN_SET('3', ids) > 0;
```

如果表数据为：

```sql
1 | 1,2,3
2 | 2,4,5
3 | 3,6
4 | 7,8
```

那么返回结果应为：

```sql
1 | 1,2,3
3 | 3,6
```

---

#### 示例二：MyBatis 中的常见写法

如果查询参数叫 `targetId`，可以这样写：

```xml
<select id="selectByTargetId" resultType="xxx">
    SELECT *
    FROM your_table
    WHERE FIND_IN_SET(#{targetId}, ids) > 0
</select>
```

如果这个条件是可选的，也可以写成动态 SQL：

```xml
<select id="selectList" resultType="xxx">
    SELECT *
    FROM your_table
    <where>
        <if test="targetId != null and targetId != ''">
            AND FIND_IN_SET(#{targetId}, ids) > 0
        </if>
    </where>
</select>
```

这样只有传了 `targetId` 时才会参与筛选。

---

### 4. 为什么这里适合用 `FIND_IN_SET()`

因为当前场景是：

- 字段本来就是逗号分隔字符串；
- 需求只是判断“某个值在不在里面”；
- 不需要复杂拆分；
- 不需要把所有元素单独展开成结果集。

这种情况下，`FIND_IN_SET()` 是最直接、最省事的方案。

比起：

- 自己用字符串截取函数拼 SQL；
- 手动拆分成多行再筛选；
- 额外做复杂子查询；

`FIND_IN_SET()` 更贴合当时的真实需求。

## 引申知识点

### 1. `FIND_IN_SET()` 的适用边界

它适合：

- 字段格式稳定，确实是逗号分隔；
- 查询目标是“是否包含某个值”；
- 数据量不算特别夸张；
- 属于历史表或暂时无法改结构的场景。

要注意：

- `ids` 中如果有空格，比如 `1, 2, 3`，可能影响匹配结果；
- 如果分隔规则不统一，查询容易出现脏数据问题；
- 这种写法通常不容易充分利用普通索引，大数据量下性能可能一般。

所以最好保证字段值尽量规整，例如统一存成：

```text
1,2,3
```

而不是：

```text
1, 2, 3
```

---

### 2. 更长期的方案：拆成中间表

如果这个 `ids` 字段在业务里会被频繁筛选、统计、关联，那么更合理的做法是拆成中间表。

例如原来主表是：

```sql
main_table
-----------
id
ids   -- 例如 1,2,3
```

可以改成：

```sql
main_table
-----------
id
...

main_table_relation
-------------------
main_id
ref_id
```

示例数据：

```sql
main_table
1
2

main_table_relation
1 | 1
1 | 2
1 | 3
2 | 2
2 | 4
2 | 5
```

这样查询包含某个 id 的记录时，就能直接写：

```sql
SELECT m.*
FROM main_table m
JOIN main_table_relation r ON m.id = r.main_id
WHERE r.ref_id = 3;
```

这个方案的优点是：

- 查询逻辑更清晰；
- 更容易加索引；
- 更适合统计和关联；
- 后续维护成本更低。

也就是说：

- **短期落地**：`FIND_IN_SET()` 很实用；
- **长期优化**：中间表更规范。

## 可直接记住的结论

- 这次实际需求是：**在 `ids` 逗号分隔字段中查找指定 id，并返回对应记录**。
- 这类场景在 MySQL 下可直接用：

```sql
WHERE FIND_IN_SET(#{targetId}, ids) > 0
```

- 如果只是临时查询或历史结构不好改，`FIND_IN_SET()` 足够实用。
- 如果该字段会长期参与筛选、统计、关联，后续应考虑拆成中间表。
