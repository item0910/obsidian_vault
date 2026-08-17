---
title: Redis连接工厂与生产内存排查
date: 2026-03-16
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/Redis
author: 自己
---

## 原始对话来源

- https://gemini.google.com/share/6ca71093d264
- https://gemini.google.com/share/64cec753cf31

## 对话内容大致纲要

这组问答的核心都落在 Redis 的实际使用与排查上，主要包括两部分：

1. **`LettuceConnectionFactory has been stopped` 报错的成因**，以及它到底是不是“本地 Redis 启动方式不对”导致的。
2. **生产环境里怎么看 Redis 的大小/内存**，重点区分服务器物理内存、Redis 配置上限和 Redis 实际使用量。

其中一段原始对话里还夹杂了 MyBatis 自增 ID、Cron 表达式等旁支问题；这次整理按“真实问题归属”收敛到 Redis 主题，只保留和 Redis 相关的主线内容。

---

## 重点复盘点

### 1. `LettuceConnectionFactory has been stopped, use start() to initialize it` 通常不是 Redis 服务端启动方式的问题

这个报错非常容易误导人，因为表面看起来像“本地 Redis 没启动好”，但它多数情况下指向的并不是 Redis 服务端，而是 **Java 应用内部的 Redis 客户端生命周期问题**。

更准确地说，它表达的是：

- 当前 Spring 容器中的 `LettuceConnectionFactory`
- 已经被关闭 / stop 掉了
- 但你的代码还在继续尝试通过它获取 Redis 连接

所以它和下面这种问题不是一类：

- Redis 服务端没启动
- 端口不通
- `localhost:6379` 连不上

如果真是 Redis 服务端没起来，更常见的错误通常会是：

- `Connection refused`
- `RedisConnectionException: Unable to connect to localhost:6379`

而不是 `LettuceConnectionFactory has been stopped`。

---

### 2. 最常见原因：应用正在关闭，但后台任务还在访问 Redis

这是最常见、也最符合实际生产现象的一类场景。

比如：

- Spring Boot 正在停止或重启；
- 容器开始销毁 Bean；
- `LettuceConnectionFactory` 已经进入 stop/destroy 流程；
- 但某个后台线程、定时任务、异步线程、`@PreDestroy` 清理逻辑，仍然在访问 Redis；
- 最终就会抛出这个异常。

这类问题的典型判断方式是：

- 看报错时间点，是不是刚好出现在服务停止、热更新、重启时；
- 如果是，那么重点不是“Redis 怎么启动”，而是“应用关闭顺序和线程停机是否处理干净”。

也就是说，真正该排查的通常是：

- 是否有 `@Scheduled` 任务在容器销毁时还没停；
- 是否有自定义线程池未正常关闭；
- 是否有异步任务在 Spring Bean 生命周期结束后还继续跑。

---

### 3. 开发环境里，Spring Boot DevTools 也可能制造类似现象

如果你本地开了 `spring-boot-devtools`，每次改代码热加载时，Spring 上下文都会尝试重启。

这会带来一种常见副作用：

- 旧上下文正在销毁；
- 新上下文开始建立；
- 某些线程、静态引用、异步逻辑还抓着旧的 Bean；
- 于是旧的 `LettuceConnectionFactory` 被 stop 后，代码还在继续调用它。

如果怀疑是这个问题，可以暂时：

- 注释掉 DevTools 依赖；
- 重启后再试；
- 看异常是否消失。

如果关掉 DevTools 后问题消失，说明更偏向开发环境热部署副作用，而不是 Redis 服务端本身有问题。

---

### 4. 依赖层面：Redis 相关 import 报红时，核心依赖是什么

如果你的代码里这些包报红：

```java
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.jedis.JedisConnectionFactory;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.data.redis.core.HashOperations;
import org.springframework.data.redis.core.BoundSetOperations;
```

那核心依赖通常应该先加：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

这个 starter 会引入 Spring Data Redis 的主要能力，包括：

- `RedisTemplate`
- `ValueOperations / HashOperations` 等操作接口
- `LettuceConnectionFactory`

如果项目里还显式用到了：

```java
JedisConnectionFactory
```

那还需要额外判断是不是要继续保留 Jedis。

如果确实要用 Jedis，可以再加：

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
</dependency>
```

但如果没有特殊原因，通常更建议：

- 直接走 Spring Boot 默认的 Lettuce；
- 清理掉 `JedisConnectionFactory` 的旧代码和旧 import；
- 保持客户端实现统一。

另外，如果项目里会配连接池参数，通常还建议带上：

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>
```

---

### 5. 生产环境里看 Redis 的“大小”，重点不是只看服务器内存，而是看 `maxmemory`

在生产环境里讨论 Redis 的大小，至少要分清 3 个概念：

#### 5.1 服务器/容器物理内存

这是宿主机或容器的物理上限。

例如：

- 一台机器 16GB 内存；
- 一个 K8s Pod limit 为 4GB；

这代表 Redis 最终绝对不可能无限超过这个边界。

#### 5.2 Redis 配置上限：`maxmemory`

这是运维或部署配置里真正决定 Redis 可用额度的核心参数。

也就是说，**你平时说“Redis 配了多大”时，更应该看的是 `maxmemory`，而不是服务器总内存。**

如果 `maxmemory=0`，代表不限制，这在生产上通常很危险，因为 Redis 可能一直吃内存，最终把机器顶爆。

#### 5.3 Redis 当前实际使用量：`used_memory`

这是 Redis 当前真实占用的数据内存规模。

所以，真实排查时通常不是问“服务器多少内存”，而是要同时看：

- 宿主资源上限
- Redis 配置上限
- Redis 当前实际使用量

---

### 6. 最常用的排查命令：`info memory`

进入 `redis-cli` 后，可以直接执行：

```bash
info memory
```

重点关注这些字段：

- `maxmemory_human`：配置的内存上限
- `used_memory_human`：当前实际已使用内存
- `used_memory_rss_human`：操作系统视角下 Redis 进程实际占用
- `mem_fragmentation_ratio`：内存碎片率

它们的意义可以这样理解：

#### `maxmemory_human`

这是运维给 Redis 设的“最大额度”。

- 如果是 `0`，通常说明没设限制；
- 如果是具体值，例如 `3.00G`，那更接近你在生产里应该关注的 Redis 可用大小。

#### `used_memory_human`

这是当前 Redis 数据本身大概用了多少内存。

这最能反映业务侧“我现在塞了多少数据”。

#### `used_memory_rss_human`

这是操作系统看到 Redis 进程实际占用了多少内存。

它通常会比 `used_memory` 更大，因为还包含：

- 内存碎片
- 分配器额外开销
- 其他运行时开销

#### `mem_fragmentation_ratio`

这是内存碎片率，常用来判断 Redis 内存使用是否健康。

如果这个值偏大，例如明显高于 1，说明物理内存消耗相对更高，存在碎片或额外浪费。

---

### 7. 生产环境里 `maxmemory` 一般怎么定

不是说“服务器 16G，Redis 就一定能配 16G”。

实际部署时，通常会预留安全空间。

#### 专用物理机/虚拟机场景

如果 Redis 基本独占这台机器，常见做法是：

- `maxmemory` 设为物理内存的 70%~80%

原因是要给下面这些东西留余量：

- 操作系统本身
- Redis fork 子进程时的 Copy-on-Write 开销
- RDB / AOF 重写时的额外内存抖动
- 内存碎片

否则一旦写入高峰遇上持久化，很容易触发：

- Swap
- OOM
- 整机抖动甚至宕机

#### Docker / Kubernetes 场景

如果 Redis 跑在容器里，就更应该看容器限制：

- Pod limit 4GB，不代表 Redis 应该直接配满 4GB；
- 更常见的是 Redis `maxmemory` 配成容器限制的 70%~80%；

这样可以避免：

- Redis 自身开销 + 内存碎片 + 辅助进程
- 一起把容器顶到 limit
- 最终被 K8s OOM Kill

---

### 8. 超出 `maxmemory` 后会怎样，要看淘汰策略

当 Redis 用到接近或达到 `maxmemory` 时，不同配置会导致完全不同的业务后果。

例如：

#### `noeviction`

这是比较危险但也很常见的一种表现。

达到上限后：

- 写请求会失败；
- 读请求通常仍可继续；
- 业务侧可能看到类似 OOM / 写入报错。

这更适合“不能偷偷删数据”的场景，但前提是上层必须能兜住写失败。

#### `allkeys-lru`、`volatile-lru` 等策略

达到上限后 Redis 会自动淘汰一部分旧 key，为新数据腾空间。

这适用于“Redis 是缓存”的场景。

但如果你把 Redis 当半持久化数据库用，就要非常谨慎，因为淘汰意味着：

- 数据会被自动删掉；
- 不是简单的“写不进去”，而是“旧数据被替换掉”。

所以排查生产环境时，除了看内存大小，也最好一起确认：

- 当前 `maxmemory`
- 当前 `maxmemory-policy`

---

## 可直接记住的结论

- `LettuceConnectionFactory has been stopped` **通常不是 Redis 服务端启动方式不对**，而是 Java 应用内部的 Redis 连接工厂生命周期出了问题。
- 这类错误最常见于：**应用关闭、重启、热部署时，后台线程/定时任务还在访问 Redis。**
- 如果真是 Redis 服务端没启动，更常见的报错会是 `Connection refused` 或 `Unable to connect`，而不是工厂已停止。
- Redis 相关 import 报红时，优先补：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

- 如果没有特殊原因，优先使用 **Lettuce**，不建议 Jedis 和 Lettuce 混搭。
- 生产环境里看 Redis “多大”，**核心先看 `maxmemory`，不是只看服务器总内存。**
- 最常用排查命令：

```bash
info memory
```

- 重点字段：`maxmemory_human`、`used_memory_human`、`used_memory_rss_human`、`mem_fragmentation_ratio`
- Redis 内存上限通常应小于物理机/容器总内存，要给系统、持久化、碎片和突发开销留余量。

---

## 引申知识点

### 1. 排查 Redis 问题时，要先分清“服务端连接失败”还是“客户端 Bean 生命周期异常”

很多 Redis 报错看起来都像“Redis 不可用”，但它们的排查方向完全不同。

可以先粗分成两类：

#### 服务端连不上

常见关键词：

- `Connection refused`
- `timeout`
- `Unable to connect`
- host/port 不通

这类更多是：

- Redis 进程没启动
- 地址端口错误
- 防火墙 / 网络问题
- 容器服务没暴露出来

#### 客户端生命周期问题

常见关键词：

- `LettuceConnectionFactory has been stopped`
- Bean 已销毁
- 上下文关闭中

这类更偏向：

- Spring Bean 被销毁后仍被访问
- 线程池/异步任务未正常停机
- 热部署导致旧上下文残留引用

### 2. 生产环境 Redis 容量排查，最好把“配置值 + 实际值 + 策略”一起看

单独看一个 `used_memory` 不够，至少最好一起确认：

- `maxmemory`
- `used_memory`
- `mem_fragmentation_ratio`
- `maxmemory-policy`

这样才能判断当前问题属于：

- 容量接近上限
- 碎片过高
- 策略导致自动淘汰
- 还是纯粹没有设置安全上限

### 3. 如果服务停止阶段经常报 Redis 相关异常，重点要看关闭顺序

尤其是这些地方：

- `@Scheduled`
- `@Async`
- 自定义线程池
- `@PreDestroy`
- 消息消费线程

如果 Bean 已销毁，但后台逻辑还没停干净，就很容易在服务关闭阶段持续打 Redis / MQ / DB 异常日志。

这类问题通常不是 Redis 本身的问题，而是应用优雅停机做得不完整。
