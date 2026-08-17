---
title: List取最后一个元素
date: 2026-03-15
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/Java
author: 自己
---

## 对话内容大致纲要

来源对话：<https://gemini.google.com/share/1c769ea2922a>

这部分对话最初的问题很简单：

- `List<Date> dateList` 怎么取最后一个值。

后面又继续追问：

- 有没有更快捷的工具类写法；
- 比如 Spring、Hutool、Guava 里有没有现成方法。

最后这部分的结论比较明确：

- **只用 JDK 时，标准写法就是 `dateList.get(dateList.size() - 1)`；**
- **如果项目里已经引入 Hutool，可以直接用 `CollUtil.getLast(dateList)`；**
- **如果项目里已经引入 Guava，可以用 `Iterables.getLast(dateList, null)`；**
- **Spring 本身没有直接的 `getLast()`。**

## 重点复盘点

### 1. JDK 标准写法

最常见写法：

```java
Date lastDate = null;
if (dateList != null && !dateList.isEmpty()) {
    lastDate = dateList.get(dateList.size() - 1);
}
```

核心点是：

- 先判空；
- 再取 `size() - 1`；
- 避免空列表直接 `get()` 导致异常。

如果不判空，下面这种写法在空列表时会报错：

```java
dateList.get(dateList.size() - 1)
```

---

### 2. 如果项目里有 Hutool，写法会更顺手

Gemini 这段里提到，Hutool 提供了：

```java
CollUtil.getLast(dateList)
```

示例：

```java
import cn.hutool.core.collection.CollUtil;

Date lastDate = CollUtil.getLast(dateList);
```

这个写法的优点：

- 方法名直观；
- 不用自己写 `size() - 1`；
- 对空集合更友好，返回值处理更顺手。

如果当前项目本来就已经用了 Hutool，这个写法确实更省心。

---

### 3. 如果项目里有 Guava，也可以直接取最后一个

Guava 可以用：

```java
Iterables.getLast(dateList, null)
```

示例：

```java
import com.google.common.collect.Iterables;

Date lastDate = Iterables.getLast(dateList, null);
```

这个写法的优点：

- 可以指定默认值；
- 空集合时不至于直接报错；
- 对已经用 Guava 的项目也很自然。

---

### 4. Spring 没有专门的 `getLast()`

对话里专门问到了 Spring 工具类，但这里要记住一点：

- `CollectionUtils` 主要是判空、合并、基础判断；
- **Spring 没有提供直接获取 List 最后一个元素的快捷方法。**

所以如果是 Spring 项目，但没引入 Hutool / Guava，通常还是老老实实用 JDK 原生写法。

## 引申知识点

### 1. 这个问题本质上不值得为了“少写几个字符”额外加依赖

如果项目本身没有 Hutool 或 Guava，只是为了取一个最后元素，不建议专门引入新依赖。

因为 JDK 写法已经非常清楚：

```java
dateList.get(dateList.size() - 1)
```

这种场景下：

- **可读性已经足够；**
- **维护成本也最低；**
- **不会额外增加依赖。**

---

### 2. 如果集合来源不稳定，要先想清楚空值策略

例如：

- 空列表时返回 `null`；
- 空列表时抛业务异常；
- 空列表时返回默认时间。

这其实比“用哪个工具类”更重要。

比如业务强依赖最后一个时间点时，可以直接在前面校验：

```java
if (dateList == null || dateList.isEmpty()) {
    throw new IllegalArgumentException("dateList 不能为空");
}
Date lastDate = dateList.get(dateList.size() - 1);
```

而不是默认返回 `null` 后面再埋雷。

## 可直接记住的结论

- JDK 标准写法：

```java
dateList.get(dateList.size() - 1)
```

- 使用前最好先判空。
- 如果项目已引入 Hutool，可用：

```java
CollUtil.getLast(dateList)
```

- 如果项目已引入 Guava，可用：

```java
Iterables.getLast(dateList, null)
```

- Spring 没有直接的 `getLast()` 工具方法。
- 没有现成依赖时，优先用 JDK 原生写法，不必为了这个小需求额外引库。
