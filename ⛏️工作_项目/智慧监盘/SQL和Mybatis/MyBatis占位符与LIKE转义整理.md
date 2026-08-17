---
title: MyBatis占位符与LIKE转义整理
date: 2026-03-16
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/MyBatis 项目笔记/AI对话/MySQL
author: 自己
---

## 原始对话来源

- https://gemini.google.com/share/2285ed92d2a0
- https://gemini.google.com/share/862b6ee80eb3

## 对话内容大致纲要

这一组问题的主题非常集中，基本都围绕 **MyBatis / MyBatis-Plus 的 SQL 参数拼接与模糊查询转义**：

1. XML 中为什么有时候用 `${}`，有时候用 `#{}`，它们的底层区别是什么。
2. 用户输入 `%` 时，`LIKE CONCAT('%', #{param}, '%')` 为什么会失效或行为异常。
3. `ESCAPE '\\'`、反斜杠转义、Java 字符串转义、JDBC 预编译之间为什么会越绕越乱。
4. 是否可以改用 `$` 作为转义字符，降低反斜杠转义冲突。
5. 是否可以封装一个统一的工具类，避免每次手写特殊字符转义。

---

## 重点复盘点

### 1. `#{}` 和 `${}` 的根本区别：一个是预编译占位符，一个是字符串直拼

这是 MyBatis 最基础但也最容易被误用的点。

#### `#{}`

`#{}` 对应的是 JDBC 的预编译参数，占位后最终会被替换成 `?`。

例如：

```xml
SELECT * FROM t_procedure_config WHERE id = #{id}
```

它的特点是：
- 会走预编译；
- 会自动处理类型；
- 字符串会自动加引号；
- **能防 SQL 注入**；
- 适合绝大多数“值参数”。

#### `${}`

`${}` 是**纯字符串替换**，相当于把值直接拼进 SQL 文本。

例如：

```xml
SELECT * FROM t_procedure_config ORDER BY ${columnName}
```

它的特点是：
- 不走预编译；
- 不自动处理类型和引号；
- 有 SQL 注入风险；
- 只能用于那些 `?` 不能出现的位置，例如：
  - 动态表名
  - 动态列名
  - 动态排序字段

#### 结论

默认原则就是一句话：

- **能用 `#{}` 就别用 `${}`**

`${}` 不是更灵活，而是更危险，只有在 SQL 结构本身需要动态替换时才用。

---

### 2. `LIKE CONCAT('%', #{param}, '%')` 遇到用户输入 `%` 时，问题不在“没生效”，而在“语义变了”

例如你写：

```sql
AND unit_ch_name LIKE CONCAT('%', #{request.unitChName}, '%')
```

当用户输入：

```text
%
```

最终 SQL 逻辑会接近于：

```sql
LIKE '%%%'
```

这不是“查不到”，而是：
- `%` 在 LIKE 里本身就是通配符；
- `'%%%'` 和 `'%'` 的语义几乎一样；
- 最终会匹配几乎所有非空记录。

所以你会感觉“这个条件不生效”，其实更准确地说，是：
- **用户输入的 `%` 被当成了通配符，而不是字面值字符 `%`。**

如果你的真实需求是：
- 查询字段里**真的包含百分号字符 `%`** 的记录；

那就必须做转义，而不是直接拼进 `LIKE`。

---

### 3. 处理 LIKE 特殊字符时，最容易乱的是“Java 转义”和“SQL 转义”叠在一起

当你尝试这样做：

```sql
LIKE CONCAT('%', ?, '%') ESCAPE '\\'
```

并在 Java 里把 `%` 转成 `\%`，事情就会变得很容易混乱，因为这里其实有 3 层：

1. **Java 字符串层**
2. **JDBC 绑定参数层**
3. **SQL LIKE 模式解析层**

于是你看到的日志里可能会出现：

```sql
LIKE '%\\\%%' ESCAPE '\\'
```

这时候已经很难靠肉眼判断到底：
- 哪个反斜杠是 Java 转义；
- 哪个反斜杠是 SQL 字面量；
- 哪个反斜杠才是真正传给 LIKE 的 ESCAPE 符号；

这也是为什么“理论上没错，但实际就是 bad sql / 行为不对”的情况特别常见。

#### 一个更务实的结论

**不要把“通配符拼接”和“特殊字符转义”都留给 SQL 去做。**

更稳妥的方式是：
- 在 Java 层先生成完整的 LIKE 模式串；
- SQL 层只负责接收这个模式串；
- 并显式声明 `ESCAPE`。

---

### 4. 用 `\` 作为 ESCAPE 字符可行，但在 Java + MyBatis 场景下不够省心

理论上，匹配包含字面值 `%` 的 SQL，可以写成：

```sql
unit_ch_name LIKE '%\%%' ESCAPE '\'
```

这里的含义是：
- 外层 `%`：模糊匹配任意字符；
- `\%`：表示字面值 `%`；
- `ESCAPE '\'`：声明反斜杠是转义字符；

从 SQL 原理上讲这没问题。

但在 Java + MyBatis 里，你还要处理：
- Java 字符串里的 `\\`
- JDBC 参数里的 `\`
- SQL 里的 `ESCAPE '\\'`

所以虽然它“理论正确”，但实操很容易绕进去。

#### 因此，一个更务实的选择是：改用 `$` 之类不敏感的符号做 ESCAPE 字符

例如：

```sql
unit_ch_name LIKE '%$%%' ESCAPE '$'
```

含义同样是：
- 前后 `%` 负责模糊匹配；
- `$%` 表示字面值 `%`；
- `ESCAPE '$'` 说明 `$` 是转义符；

这样能显著减少 Java / SQL 双重反斜杠带来的混乱。

---

### 5. 更稳的做法：在 Java 层统一构造 LIKE 模式，再把完整模式传入 SQL

如果决定使用 `$` 作为 ESCAPE 字符，一个相对稳定的思路是：

#### Java 层

先统一处理用户输入：

```java
public String createSafeLikePattern(String input) {
    if (input == null) {
        return null;
    }

    String escaped = input
        .replace("$", "$$")
        .replace("%", "$%")
        .replace("_", "$_");

    return "%" + escaped + "%";
}
```

这里做了三件事：
- 先把 `$` 自己转义掉，避免和 ESCAPE 字符冲突；
- 再把 `%` 转成 `$%`；
- 再把 `_` 转成 `$_`；
- 最后手动包上前后 `%`，形成完整的模糊查询模式。

#### SQL 层

```xml
AND unit_ch_name LIKE #{request.likePattern} ESCAPE '$'
```

这样 SQL 本身就很干净：
- 不再拼 `CONCAT('%', ..., '%')`
- 不再在 SQL 里处理转义逻辑
- SQL 只负责接收一个已经准备好的模式串

这通常比“Java 转义一半 + SQL 里再 CONCAT 一半”稳定得多。

---

### 6. 如果只是想统计“包含 `%` 的记录数”，可以直接写死一个可执行 SQL

如果目标非常明确：
- 查 `unit_ch_name` 中包含字面值 `%` 的记录；
- 不需要走动态参数；

那最清晰的写法反而就是直接写死：

```sql
SELECT COUNT(*)
FROM t_param_unit
WHERE del_flag = 0
  AND unit_ch_name LIKE '%$%%' ESCAPE '$';
```

这条 SQL 的含义就是：
- 任意前缀；
- 中间包含字面值 `%`；
- 任意后缀；

适合直接在数据库客户端验证结果。

这个思路也说明了一个现实经验：
- 当动态版本一直调不通时，先写一条**静态可执行 SQL**验证语义；
- 确认 SQL 本身没问题后，再回到 MyBatis 里处理参数传递。

---

### 7. MyBatis-Plus / MyBatis 没有一个“万能官方一键 LIKE 转义”方案，通常还是自己封装工具方法

实际项目里，最可控的方式还是自己封装一个统一入口，例如：

```java
public class MySqlLikeUtil {
    public static String escapeLikeWithDollar(String str) {
        if (str == null || str.isBlank()) {
            return str;
        }
        return "%" + str
            .replace("$", "$$")
            .replace("%", "$%")
            .replace("_", "$_")
            + "%";
    }
}
```

然后在 Service 层统一调用：

```java
String likePattern = MySqlLikeUtil.escapeLikeWithDollar(request.getUnitChName());
```

SQL 里统一写：

```xml
AND unit_ch_name LIKE #{likePattern} ESCAPE '$'
```

如果项目中已经引入 Hutool，也可以借助 `StrUtil` 做基础字符串处理，但**核心转义规则还是要你自己定**，因为：
- 具体用 `\` 还是 `$` 作为 ESCAPE 字符，是你的项目决策；
- 各数据库方言对 LIKE 转义也存在差异；
- 所以与其到处散着写，不如自己封装一个明确的工具类。

---

## 可直接记住的结论

- `#{}` 是预编译占位符，默认优先用它；
- `${}` 是字符串直拼，只有动态表名/列名/排序字段这类场景才用；
- 用户输入 `%` 时，直接放进 `LIKE CONCAT('%', #{param}, '%')`，会被当成通配符，不会被当成字面值 `%`；
- 如果要匹配字面值 `%`，必须配合 `ESCAPE` 做转义；
- 在 Java + MyBatis 场景下，直接用反斜杠 `\` 作为 ESCAPE 字符容易把转义链条搞乱；
- 更省心的做法是改用 `$` 作为 ESCAPE 字符，例如：

```sql
LIKE '%$%%' ESCAPE '$'
```

- 更稳的整体方案是：
  - Java 层生成完整 LIKE 模式；
  - SQL 层只接收模式串；
  - SQL 显式写 `ESCAPE '$'`；
- 常用可执行验证 SQL：

```sql
SELECT COUNT(*)
FROM t_param_unit
WHERE del_flag = 0
  AND unit_ch_name LIKE '%$%%' ESCAPE '$';
```

---

## 引申知识点

### 1. LIKE 模糊查询里不只 `%` 需要关注，`_` 也一样是通配符

很多人一开始只盯着 `%`，但 `_` 在 LIKE 里表示：
- 匹配任意单个字符

所以如果用户输入也可能包含 `_`，你通常要一起处理：

- `%` → `$%`
- `_` → `$_`
- `$` → `$$`

否则你的“精确包含某个字符串”的模糊查询仍然可能跑偏。

### 2. 动态 SQL 出问题时，先把问题拆成“SQL 语义”与“参数传递”两层

例如本题里：
- 先写一条静态 SQL，确认数据库层面：

```sql
LIKE '%$%%' ESCAPE '$'
```

本身是成立的；

- 再去处理 Java / MyBatis 参数传递；

这样调试效率会比直接在动态 SQL 里盲猜高很多。

### 3. 越是容易重复踩坑的规则，越值得沉淀成工具类

像：
- LIKE 特殊字符转义
- `${}` / `#{}` 使用边界
- 动态排序字段白名单

这些都属于“不是难，但特别容易错”的问题。

所以比起每个 Mapper 各写一遍，更适合：
- 统一封装；
- 统一约定；
- 后续所有查询复用同一套逻辑。
