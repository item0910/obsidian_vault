---
title: Java_Stream常见处理
date: 2026-03-15
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/Java
author: 自己
---

## 对话内容大致纲要

来源对话：<https://gemini.google.com/share/77d6619dd6da>

这段对话虽然连续问了 3 个问题，但都属于 **Java Stream / 集合处理的常见写法**，所以合并记录更合适。

主要包含这 3 个点：

1. `Collectors.toMap(..., Function.identity(), ...)` 里的 `Function.identity()` 是什么意思；
2. 逗号分隔的 id 字符串，如何拆成 `List<Long>`；
3. `List<SystemDo>` 中如何把 `systemCode` 提取出来，再拼成逗号分隔字符串。

这几个问题本质上都在处理：

- 集合转 Map
- 字符串转集合
- 集合转字符串

## 重点复盘点

### 1. `Function.identity()` 的含义

原始代码大意：

```java
Map<String, ProcedureDo> updateProcedureMap = updateProcedureList.stream()
    .collect(Collectors.toMap(
        item -> item.getProcedureId() + dataSource,
        Function.identity(),
        (t1, t2) -> t1
    ));
```

这里的：

```java
Function.identity()
```

意思就是：

- 直接把当前流里的对象本身，当成 `Map` 的 value；
- 它本质上等价于：

```java
item -> item
```

也就是说，这段 `toMap` 的含义可以拆成：

- `key`：`item.getProcedureId() + dataSource`
- `value`：当前 `item` 对象本身
- `merge`：如果 key 冲突，保留旧值 `t1`，丢掉新值 `t2`

所以这段代码最终得到的是：

- 一个 `Map<String, ProcedureDo>`
- key 是拼接后的业务主键
- value 是原始的 `ProcedureDo`

---

### 2. `toMap` 第三个参数也值得顺手记住

这里的：

```java
(t1, t2) -> t1
```

表示如果有重复 key：

- 保留先出现的值；
- 后出现的值丢弃。

如果改成：

```java
(t1, t2) -> t2
```

那就是保留后者，覆盖前者。

这个点在实际业务里很容易忽略，但非常关键。

---

### 3. 逗号分隔字符串转 `List<Long>`

例如字符串：

```java
String idsStr = "101,102, 103";
```

推荐写法：

```java
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

List<Long> idList = Arrays.stream(idsStr.split(","))
        .map(String::trim)
        .map(Long::parseLong)
        .collect(Collectors.toList());
```

这个过程分成三步：

1. `split(",")`：按逗号拆分；
2. `trim()`：去掉空格；
3. `parseLong()`：把字符串转成 Long。

最终结果：

```java
[101, 102, 103]
```

---

### 4. 这类字符串转换最好加防御性处理

如果字符串可能为空、为 null、或者有连续逗号，建议写得更稳一点：

```java
public List<Long> splitIds(String idsStr) {
    if (idsStr == null || idsStr.trim().isEmpty()) {
        return new ArrayList<>();
    }

    return Arrays.stream(idsStr.split(","))
            .filter(str -> str != null && !str.trim().isEmpty())
            .map(String::trim)
            .map(Long::parseLong)
            .collect(Collectors.toList());
}
```

这里主要防的是：

- 空字符串；
- 连续逗号产生空元素；
- 有空格导致 `NumberFormatException`。

---

### 5. 如果项目里有 Hutool，也能更快转 `List<Long>`

对话里还提到 Hutool 写法：

```java
List<Long> ids = Convert.toList(Long.class, idsStr);
```

这个写法确实短，但前提是：

- 项目里已经有 Hutool；
- 团队也接受这种工具类风格。

如果只是普通 Java 项目，`split + stream` 还是最通用。

---

### 6. `List<SystemDo>` 提取 `systemCode` 再逗号拼接

如果要把一个对象列表中的 `systemCode` 提取出来，并拼成：

```text
CODE_A,CODE_B,CODE_C
```

标准写法是：

```java
String result = systems.stream()
        .map(SystemDo::getSystemCode)
        .collect(Collectors.joining(","));
```

这就是典型的：

- `map`：提取字段
- `joining`：按指定分隔符拼接字符串

---

### 7. 如果 `systemCode` 不是字符串，要先转成字符串

如果字段类型是 `Long` 或 `Integer`，那就要先显式转成字符串：

```java
String result = systems.stream()
        .map(item -> String.valueOf(item.getSystemCode()))
        .collect(Collectors.joining(","));
```

因为 `Collectors.joining()` 只能处理字符流。

---

### 8. 拼接前最好过滤 null

更稳妥的写法：

```java
String result = systems.stream()
        .filter(item -> item != null && item.getSystemCode() != null)
        .map(SystemDo::getSystemCode)
        .collect(Collectors.joining(","));
```

避免：

- list 中对象本身是 null；
- `systemCode` 是 null；
- 最终拼接出字符串 `"null"`。

## 引申知识点

### 1. 这几个问题其实是三类常见流式转换模板

可以直接当模板记住：

#### 集合 -> Map

```java
list.stream().collect(Collectors.toMap(keyMapper, valueMapper, mergeFunction))
```

#### 字符串 -> 集合

```java
Arrays.stream(str.split(",")).map(...).collect(Collectors.toList())
```

#### 集合 -> 字符串

```java
list.stream().map(...).collect(Collectors.joining(","))
```

这三类基本覆盖了很多日常开发里的 Stream 处理。

---

### 2. `Function.identity()` 适合“value 就是对象本身”的场景

比如：

```java
Map<Long, User> userMap = userList.stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));
```

这种写法比：

```java
item -> item
```

更标准，也更符合 Stream 习惯用法。

---

### 3. `Collectors.joining()` 很适合替代手写循环拼字符串

比起传统写法：

```java
StringBuilder sb = new StringBuilder();
for (...) {
    ...
}
```

这种写法更直接：

```java
list.stream().map(...).collect(Collectors.joining(","))
```

尤其适合“提字段 + 拼接”的场景。

## 可直接记住的结论

- `Function.identity()` 就是“返回对象本身”，等价于：

```java
item -> item
```

- `Collectors.toMap(key, Function.identity(), merge)` 常用于把对象列表转成以业务字段为 key 的 Map。
- 逗号字符串转 `List<Long>` 常用：

```java
Arrays.stream(idsStr.split(",")).map(String::trim).map(Long::parseLong).collect(Collectors.toList())
```

- 对象列表提字段并逗号拼接常用：

```java
systems.stream().map(SystemDo::getSystemCode).collect(Collectors.joining(","))
```

- 实际使用时要重点注意：
  - 空值过滤
  - `trim()`
  - `toMap` 重复 key 的处理策略
