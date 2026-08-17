---
title: YAML 数据库配置层级问题
date: 2026-02-09
categories: 工作记录
tags: Spring-Boot Druid YAML 数据库配置 多数据源
author: 自己
---

## 原始对话来源

- Gemini 对话：https://gemini.google.com/share/c31450112d1c
- Gemini 对话：https://gemini.google.com/share/d659d6dce5e0
- 整理时间：2026-03-17

## 问题背景

开发手册要求这样写数据库配置：

```yaml
dataSource:
  type: com.alibaba.druid.pool.DruidDataSource
  druid:
    db1:
      driver-class-name: com.mysql.cj.jdbc.Driver
      url: ***
      username: ****
      password: ****
```

想简化成只配一个数据库时去掉 `db1` 层级：

```yaml
dataSource:
  type: com.alibaba.druid.pool.DruidDataSource
  druid:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: ***
    username: ****
    password: ****
```

## 核心结论

**不能直接删掉 `db1` 层级。**

原因：Spring Boot 配置类通过 `@ConfigurationProperties(prefix = "dataSource.druid")` 读取配置时，代码预期 `druid` 下面是一个 `Map<String, DataSourceProperties>` 结构，其中 `db1` 是 Map 的 Key。

如果直接把 `driver-class-name` 等属性挂在 `druid` 下面，程序会去寻找名为 `driverClassName` 的字段，而不是去寻找 Map 里的 Key，导致启动报错或数据源初始化失败。

## 正确做法

### 方案 A：保留一层名称（最稳妥）

即便只有一个数据库，也保留那个 Key，可以改成更有意义的名字：

```yaml
dataSource:
  type: com.alibaba.druid.pool.DruidDataSource
  druid:
    master:  # 或 default
      driver-class-name: com.mysql.cj.jdbc.Driver
      url: ***
      username: ****
      password: ****
```

### 方案 B：修改 Java 配置类（不推荐）

除非有权限修改公司底层框架代码，否则不建议。需要将配置类中的 `Map` 结构改为普通 POJO 结构。

## 如何确认是否可行

检查项目代码中是否有类似注解：

```java
@ConfigurationProperties("dataSource.druid")
private Map<String, DruidProperties> dataSources;
```

如果存在 `Map`，就必须写那个 `db1`（或任何你起的名字）。

## 设计原因

手册这样设计是为了后续方便扩展成"多数据源"。在分布式或标准化开发环境中，随意改动层级可能会破坏框架自动装配的逻辑。

## 引申知识点

- `@ConfigurationProperties` 的绑定机制
- Spring Boot 多数据源配置的 Map 结构设计
- YAML 层级与 Java 对象映射的对应关系
