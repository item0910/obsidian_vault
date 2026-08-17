---
title: MySQL更新回填与批量处理整理
date: 2026-03-16
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/MySQL 项目笔记/AI对话/MyBatis
author: 自己
---

## 原始对话来源

- https://gemini.google.com/share/348abacd2091
- https://gemini.google.com/share/d85cfb0bcd3c
- https://gemini.google.com/share/5da72973bb96
- https://gemini.google.com/share/c2d18fd0cb29
- https://gemini.google.com/share/231b24d43303
- https://gemini.google.com/share/f5a294bf0131
- https://gemini.google.com/share/153c79b4314c

## 对话内容大致纲要

这一组更偏向 **更新、回填、批量处理、MyBatis 落地写法**，主要包括：

1. 根据复合条件批量更新多条记录。
2. 用 MyBatis 的 `CASE WHEN` 批量更新不同记录的不同值。
3. 将 `datetime` 转成 13 位时间戳后批量回填到表字段。
4. 通过一组 `ids` 查询结果，再在 MyBatis/Java 中转成 `Map<Long, String>`。
5. 用 `param_ids` 关联 `t_param.id`，把 `param_code` 回填到别的表。
6. 删除面板表中找不到主表关联记录的“孤儿数据”。
7. 最基础的 `UPDATE ... WHERE ... IN (...)` 单表更新写法。

---

## 重点复盘点

### 1. 复合条件批量更新，核心是 `(col1, col2) IN ((v1, v2), ...)`

如果手里有一个 `configList`，每个元素包含：
- `id`
- `type`

要把 `t_panel_record` 中满足：
- `alarm_config_id = item.id`
- `type = item.type`

的记录统一改成 `screen_status = 1`，最适合的 SQL 结构是：

```sql
UPDATE t_panel_record
SET screen_status = 1
WHERE (alarm_config_id, type) IN (
    (101, 'TYPE_A'),
    (102, 'TYPE_B')
);
```

在 MyBatis XML 里，一般写成：

```xml
<update id="updateStatusByConfigs">
    UPDATE t_panel_record
    SET screen_status = 1
    WHERE (alarm_config_id, type) IN
    <foreach collection="list" item="item" open="(" separator="," close=")">
        (#{item.id}, #{item.type})
    </foreach>
</update>
```

这个思路适合：
- 批量更新条件值不同，但更新结果相同；
- 并且条件是复合键，不只是单个主键。

如果数据量很大，记得分批。

---

### 2. `CASE WHEN` 批量更新适合“每一行更新成不同值”的场景

与上一类不同，`CASE WHEN` 的目标是：
- 一次更新多行；
- 但每一行更新后的值都不一样。

例如：
- `alarm_record_id = 1001` → `end_time = '2026-01-12 10:00:00'`, `endMethod = 1`
- `alarm_record_id = 1002` → `end_time = '2026-01-12 12:30:00'`, `endMethod = 2`

对应 SQL 可以展开成：

```sql
UPDATE t_panel_cord
SET end_time = CASE alarm_record_id
        WHEN 1001 THEN '2026-01-12 10:00:00'
        WHEN 1002 THEN '2026-01-12 12:30:00'
    END,
    endMethod = CASE alarm_record_id
        WHEN 1001 THEN 1
        WHEN 1002 THEN 2
    END
WHERE alarm_record_id IN (1001, 1002);
```

这个模式的本质是：
- 不是一条条发 SQL；
- 而是一次提交一个大更新；
- 由数据库根据 `CASE` 分支给不同记录赋不同值。

注意：
- `WHERE ... IN (...)` 非常重要，不要省；
- 集合为空时不要执行，否则容易拼出非法 SQL；
- 条数太多时要分批，否则 SQL 过长、解析成本高。

---

### 3. `datetime` 转 13 位毫秒时间戳：`UNIX_TIMESTAMP(col) * 1000`

如果表中有：
- `start_time datetime`
- `end_time datetime`

想回填到：
- `start_timestamp bigint`
- `end_timestamp bigint`

可以直接写：

```sql
UPDATE t_alarm_record
SET 
    start_timestamp = UNIX_TIMESTAMP(start_time) * 1000,
    end_timestamp = UNIX_TIMESTAMP(end_time) * 1000
WHERE start_time IS NOT NULL
   OR end_time IS NOT NULL;
```

这里要注意：
- `UNIX_TIMESTAMP()` 默认返回秒级；
- 乘 `1000` 后才是 13 位毫秒级；
- 如果列值为 `NULL`，结果仍然会是 `NULL`；
- 时区依赖数据库当前会话时区配置，业务上最好确认数据库时区和数据语义一致。

执行完后建议先抽样验证：

```sql
SELECT id, start_time, start_timestamp, end_time, end_timestamp
FROM t_alarm_record
LIMIT 10;
```

---

### 4. MyBatis 里根据 `Set<Long> ids` 查 `id -> param_code`，SQL 返回列表，Map 在 Java 层组装更稳

需求是：
- 入参是 `Set<Long> ids`
- 结果想要 `Map<Long, String>`

SQL 层最自然的写法是先查两列：

```xml
<select id="selectParamCodeByIds" resultType="java.util.Map">
    SELECT id, param_code
    FROM t_param
    WHERE del_flag = 0
      AND id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

然后在 Java 层转：

```java
resultList.stream().collect(Collectors.toMap(
    row -> (Long) row.get("id"),
    row -> (String) row.get("param_code"),
    (oldVal, newVal) -> newVal
));
```

为什么不强行让 MyBatis 直接返回 `Map<Long, String>`？

因为：
- MyBatis 原生更擅长返回行列表；
- 直接 mapKey 常常得到的是 `Map<Long, Map<String,Object>>`；
- 业务上最稳妥的做法还是“SQL 查两列，Java 再转目标结构”。

---

### 5. 用 `param_ids` 回填 `param_code` 到其它表前，先确认 `param_ids` 是单值还是逗号串

如果：
- `target.param_ids` 存的是**单个 ID**；
- `t_param.id` 是主键；

那么可以直接回填：

```sql
UPDATE t_relevance_param_alarm_record target
INNER JOIN t_param source
    ON target.param_ids = source.id
SET target.param_code = source.param_code
WHERE target.param_ids IS NOT NULL
  AND target.param_ids != '';
```

`t_panel_record` 类似：

```sql
UPDATE t_panel_record target
INNER JOIN t_param source
    ON target.param_ids = source.id
SET target.param_codes = source.param_code
WHERE target.param_ids IS NOT NULL
  AND target.param_ids != '';
```

但这里有个非常重要的前提：
- **只适用于 `param_ids` 存单个 ID 的情况。**

如果 `param_ids = '1,2,3'` 这种逗号串，就不能这么直接更新，必须：
- 要么先拆解；
- 要么用 `FIND_IN_SET` 查出后再聚合；
- 要么在应用层处理。

所以做这种回填之前，第一步一定是确认真实数据形态。

---

### 6. 删除孤儿面板记录：`LEFT JOIN + IS NULL`

需求是删除 `t_panel_record` 中：
- `alarm_source = 1`
- 且 `alarm_record_id` 在主表 `t_alarm_record.id` 中找不到对应值

可直接写：

```sql
DELETE p
FROM t_panel_record p
LEFT JOIN t_alarm_record a
    ON p.alarm_record_id = a.id
WHERE p.alarm_source = 1
  AND a.id IS NULL;
```

这类写法的逻辑是：
- 左连接后，如果右表找不到匹配，右表字段为 `NULL`；
- `a.id IS NULL` 就等价于“从表记录失联了”。

正式删除前，建议先确认行数：

```sql
SELECT COUNT(*)
FROM t_panel_record p
LEFT JOIN t_alarm_record a
    ON p.alarm_record_id = a.id
WHERE p.alarm_source = 1
  AND a.id IS NULL;
```

大表上执行删除要格外注意：
- 最好在低峰期；
- 必要时分批删；
- 先确认是否需要逻辑删除而不是物理删除。

---

### 7. 最基础的单表更新：`UPDATE ... SET ... WHERE ... IN (...)`

例如：
- 更新 `t_user`
- 把 `endTime = NOW()`
- `end_method = 2`
- 条件是 `alarm_record_id IN (1,2,3)`

就是最标准的：

```sql
UPDATE t_user
SET endTime = NOW(),
    end_method = 2
WHERE alarm_record_id IN (1, 2, 3);
```

这个问题虽然简单，但在业务里很常见，真正要记住的是：
- 更新前最好先 `SELECT` 看一下目标数据；
- 不要漏掉 `WHERE`；
- 对批量 ID 更新，用 `IN (...)` 很自然。

---

## 可直接记住的结论

- 批量更新时，如果“条件不同但更新值相同”，优先考虑：

```sql
WHERE (col1, col2) IN ((v1, v2), (v3, v4))
```

- 如果“每条记录更新成不同值”，优先考虑：

```sql
SET col = CASE id WHEN ... THEN ... END
```

- `CASE WHEN` 批量更新一定要配 `WHERE ... IN (...)` 限定范围。
- `datetime` 转 13 位时间戳：

```sql
UNIX_TIMESTAMP(time_col) * 1000
```

- `Set<Long> ids -> Map<Long, String>` 这类需求，SQL 先查两列，Java 再转 Map，通常最稳。
- 回填 `param_code` 前，一定先确认 `param_ids` 是不是单值；如果是逗号串，不能直接 `=` JOIN。
- 删除孤儿记录的经典写法：

```sql
LEFT JOIN ... WHERE right_table.id IS NULL
```

- 简单批量更新就是：

```sql
UPDATE table SET ... WHERE id IN (...)
```

---

## 引申知识点

### 1. 批量更新的关键不是“能不能写”，而是“写法和数据规模是否匹配”

常见 3 种场景：

1. **多行更新为同一个值**
   - 最简单，直接 `WHERE ... IN (...)`
2. **多行按不同条件更新为同一个值**
   - 适合复合条件 `IN`
3. **多行更新成不同值**
   - 适合 `CASE WHEN`

不要用一条思路硬套所有批量更新。

### 2. 大批量更新和删除要优先考虑分批执行

无论是：
- 大量 `CASE WHEN`
- 大量 `IN (...)`
- 大表 `DELETE JOIN`

都可能带来：
- SQL 太长
- 锁时间过长
- 回滚代价高
- 影响线上业务

所以一旦量级从几十条变成几千、几万条，就该优先想：
- 是否分批
- 是否低峰执行
- 是否要先跑 count/select 验证

### 3. SQL 能做的事很多，但结构转换经常放在 Java 层更清晰

像：
- 返回 `Map<Long, String>`
- 复杂聚合后的业务对象组装
- 多表查完再按业务结构重排

并不一定都应该在 SQL 中一次性强行做完。

很多时候：
- SQL 负责查“正确的原子数据”；
- Java 负责转成“业务需要的最终结构”；

会更稳，也更易维护。
