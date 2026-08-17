---
mtime: 2024-12-30
title: Ragana运动_04面试期间问题收集
date: 2024-12-31
categories: 面试问题
tags: 项目笔记/日常态项目/Java面试工作 
author: 自己
---



## 面试期间问题收集

### Linux

#### 说说查日志的常用指令

`cat *.log|grep xxx`


### Spring

#### 说说Bean的生命周期

1. 实例化 Bean 对象。  
2. 设置 Bean 属性。  
3. 如果我们通过各种 Aware 接口声明了依赖关系，则会注入 Bean 对容器基础设施层面的依赖。具体包括 BeanNameAware、BeanClassLoaderAware、BeanFactoryAware 和 ApplicationContextAware，分别会注入 Bean ID、Bean Factory 或者 ApplicationContext。  
4. 调用 BeanPostProcessor 的前置初始化方法 postProcessBeforeInitialization。  
5. 如果实现了 InitializingBean 接口，则会调用 afterPropertiesSet 方法。  
6. 调用 Bean 自身定义的 init 方法。  
7. 调用 BeanPostProcessor 的后置初始化方法 postProcessAfterInitialization。  
8. 创建过程完毕。

### Spring Boot

#### 说说 SpringBoot 的启动流程

![](附件/image/Ragana运动_04面试问题收集-1735263600134.jpeg)

#### Spring Boot 的扩展点有哪些?

1. 配置 Configuration, 可以自定义
2. Spring Boot Actuator
    - Spring Boot Actuator 提供了许多内建的监控和管理功能，可以通过扩展 `Endpoint` 或 `HealthIndicator` 来自定义健康检查、指标和端点等。
3. 自定义过滤器和拦截器
    - 你可以创建自定义的 `Filter` 或 `Interceptor` 来拦截请求，执行一些前置处理或后置处理。
4. 自定义异常处理: Spring Boot 默认提供了异常处理机制，你可以通过 `@ControllerAdvice` 或 `@ExceptionHandler` 来扩展自定义的异常处理逻辑。
5. 自定义日志配置
6. 服务器定制

#### Spring Boot 自动装配的原理

1. 需要注意项目中引入的一个依赖：`spring-boot-autoconfigure`，其中定义了大量自动配置类
2. 打开WebMvcAutoConfiguration：
	- `@Configuration`：声明这个类是一个配置类
	- `@ConditionalOnWebApplication(type = Type.SERVLET)`
	    满足项目的类是是Type.SERVLET类型，也就是一个普通web工程，
	- `@ConditionalOnClass({ Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class })`
	    **这里的条件是OnClass，也就是满足以下类存在：Servlet、DispatcherServlet、WebMvcConfigurer，其中Servlet只要引入了tomcat依赖自然会有，后两个需要引入SpringMVC才会有。这里就是判断你是否引入了相关依赖，引入依赖后该条件成立，当前类的配置才会生效！**
	- `@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)`
	    这个条件与上面不同，OnMissingBean，是说环境中没有指定的Bean这个才生效。其实这就是自定义配置的入口，也就是说，如果我们自己配置了一个WebMVCConfigurationSupport的类，那么这个默认配置就会失效！
3. 这里通过@EnableAutoConfiguration注解引入了两个属性：WebMvcProperties和ResourceProperties。这不正是SpringBoot的属性注入玩法嘛。

### Spring Cloud

#### Nacos 的底层原理

1

#### GateWay 的底层原理



### Netty

#### 问: 聊聊为什么要用 WebSocket

1. 是实时双工的, 双方可以实时发送数据; 相比 HTTP 的单向通信方式，这种机制更加高效。不需要客户端轮询
2. 握手后是持久的, 数据通过 TCP 协议长连接传输, 避免了 HTTP 每次都需要三次握手, 降低了延迟
3. 相对于 HTTP, 没有 header, 帧结构比较轻量, 减少了不必要的开销
4. 支持性好, 对大部分浏览器客户端都支持, 前后端的 API 也比较成熟.

#### 问: WebSocket 如何保持长连接的机制

- 利用 TCP 协议其 Keep-Alive 的功能, 发送活包, 确认对方是否存活; 同时, 服务端通过心跳检测来清理无效链接
- 有 onclose 的重连事件, 客户端通过监听该事件触发重连逻辑
- 因为是用帧传输数据, 比较轻量, 减少了频繁握手的开销, 对于长连接的延迟有好处

### IM 业务

#### 问: 表结构如何设计

1. 用户表（User）

	记录用户的基本信息。

	```sql
	CREATE TABLE User (
	    id BIGINT AUTO_INCREMENT PRIMARY KEY,     -- 用户唯一ID
	    username VARCHAR(255) NOT NULL,           -- 用户名
	    avatar_url VARCHAR(512),                  -- 用户头像URL
	    is_system BOOLEAN DEFAULT FALSE,          -- 是否为系统用户（标记系统消息发送方）
	    last_logout_at TIMESTAMP NULL,            -- 最后下线时间
	    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 用户创建时间
	    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新时间
	) ENGINE=InnoDB COMMENT='用户表：存储用户基本信息，包括系统用户和最后下线时间';
	
	```

2. 用户关系表（Relationship）

	记录用户之间的关系和未读消息数。

	```sql
	CREATE TABLE Relationship (
	    id BIGINT AUTO_INCREMENT PRIMARY KEY,      -- 唯一标识
	    user_id BIGINT NOT NULL,                   -- 当前用户ID
	    peer_id BIGINT NOT NULL,                   -- 关联用户ID（另一方）
	    relationship_type ENUM('friend', 'block') DEFAULT 'friend', -- 关系类型（好友/屏蔽）
	    unread_count INT DEFAULT 0,                -- 未读消息数
	    last_message_id BIGINT,                    -- 最近一条消息的ID（外键，指向消息表）
	    last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 最近交互时间
	    UNIQUE KEY (user_id, peer_id),             -- 确保每对关系唯一
	    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE, -- 关联用户表
	    FOREIGN KEY (peer_id) REFERENCES User(id) ON DELETE CASCADE -- 关联另一方用户
	) ENGINE=InnoDB COMMENT='用户关系表：存储用户之间的关系和未读消息统计';
	```

3. 消息表（Message）

	存储用户之间的消息内容。

	```sql
	CREATE TABLE Message (
	    id BIGINT AUTO_INCREMENT PRIMARY KEY,      -- 消息唯一ID
	    sender_id BIGINT NOT NULL,                 -- 发送方用户ID（外键，指向用户表）
	    receiver_id BIGINT NOT NULL,               -- 接收方用户ID（外键，指向用户表）
	    content TEXT NOT NULL,                     -- 消息内容
	    content_type ENUM('text', 'image', 'video') DEFAULT 'text', -- 消息类型
	    status ENUM('sent', 'delivered', 'read') DEFAULT 'sent',    -- 消息状态
	    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 消息发送时间
	    read_at TIMESTAMP NULL,                     -- 消息阅读时间
	    FOREIGN KEY (sender_id) REFERENCES User(id) ON DELETE CASCADE, -- 关联发送方用户
	    FOREIGN KEY (receiver_id) REFERENCES User(id) ON DELETE CASCADE -- 关联接收方用户
	) ENGINE=InnoDB COMMENT='消息表：存储用户之间的即时消息内容';
	```

4. 系统消息表（SystemNotification）

	存储系统发给用户的通知消息。

	```sql
	CREATE TABLE SystemNotification (
	    id BIGINT AUTO_INCREMENT PRIMARY KEY,      -- 系统消息唯一ID
	    content TEXT NOT NULL,                     -- 系统消息内容
	    target_id BIGINT,                          -- 目标用户ID（为空表示发送给所有用户）
	    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 系统消息创建时间
	    FOREIGN KEY (target_id) REFERENCES User(id) ON DELETE CASCADE -- 关联用户表
	) ENGINE=InnoDB COMMENT='系统消息表：存储平台向用户发送的公告或通知';
	```

#### 问: 用户消息表太大怎么办

1. 分表: 根据用户 ID, 取模, 然后在映射到相应的表中
2. 对历史消息归档, 根据消息的重要程度, 已读, 未读, 归档一部分消息
3. 使用 NoSQL 数据库, 支持并发, 如 MongoDB; 而且用他的 TTL 机制可以自动删除过期数据

#### 问: 分页技术了解吗

1. 基于 OFFSET 的分页,

	```sql
	SELECT * 
	FROM Message
	ORDER BY created_at DESC
	LIMIT 10 OFFSET 20; 跳过前20条, 取10条, 可以理解为, 我取第三页
	``` 

2. 游标分页

	```sql
	SELECT * 
	FROM Message
	WHERE id > ? //ID大于的一个游标
	ORDER BY id ASC
	LIMIT 10;
	```

3. 聚合分页: Keyset Pagination

	更多约束条件

	```sql
	SELECT * 
	FROM Message
	WHERE (created_at < ? OR (created_at = ? AND id < ?))
	ORDER BY created_at DESC, id DESC
	LIMIT 10;
	```

4. 分页缓存

	给常用的页面进行缓存

5. 分段分页

	先查年份列表

	```sql
	SELECT DISTINCT YEAR(created_at) AS year
	FROM Message
	ORDER BY year DESC;
	
	```

	然后用户选择某年, 进行查询

	```sql
	SELECT * 
	FROM Message
	WHERE YEAR(created_at) = 2023
	ORDER BY created_at DESC
	LIMIT 10 OFFSET 20;
	
	```

	- 核心思想, 我一开始不知道怎么分段的, 所以先获取分段, 然后根据分段查询
6. 前端虚拟化技术
	- 核心思想: 全部读取, 部分渲染

#### 问: 多人群聊的路由如何设计

1. 按群维护群成员的在线消息:
	1. 在线状态
	2. IM 长连接位置
2. IM Server 收到群消息后，按群 ID 将消息路由到"**群消息服务**"模块；
3. 群消息模块检查并预处理消息内容，然后通过"**群成员在线状态**"服务获取在线成员的路由，完成消息转发的基础工作。
4. 为了减少群消息模块和群在线成员服务之间的网络流量，采用了"本地缓存 + 增量同步"的缓存策略，即**本地缓存记录最后更新版本号和时间戳**，每次同步群在线成员前先检查缓存版本号是否有变更，若有则按最后更新时间增量同步；
5. 通过"群成员在线服务"获取在线群成员的 Link 链接信息，按 Link 分组路由消息（分组路由的原因：同一 Link 上的全部群成员只需要路由一条消息即可）。同样为了减少网络开销，成员 Link 信息也采用"本地缓存 + 增量同步"的方案；
6. 群消息采用"漫游 + 历史"的存储方案，漫游的消息存储在分布式缓存中，历史消息异步写入 HBase。用户登录后可以通过漫游快速的获取到最新消息，并可以通过拉取历史查看更早的消息。

### 定时任务

#### 问: 为什么选 XXL-job 呢

1. 分布式调度能力强，适合微服务场景。
2. 界面友好，易于管理和监控。
3. 支持任务分片、失败重试和高可扩展性，适应多种业务场景。
4. 与项目技术栈（Spring Boot）集成简单。
5. 开源, 成本低，社区资源丰富。用的人多

| **框架**          | **优势**              | **劣势**             |
| --------------- | ------------------- | ------------------ |
| **XXL-JOB**     | 分布式支持强、界面化管理简单、扩展性高 | 需要单独部署调度中心，增加初始复杂度 |
| **Quartz**      | 功能强大、支持复杂任务调度       | 配置复杂，分布式支持较弱       |
| **Elastic-Job** | 强大的分布式任务调度框架，支持分片任务 | 学习曲线较陡，文档较少        |
| **Spring Task** | 简单轻量，适合小规模定时任务      | 不支持分布式，无法动态修改任务配置  |

### 运维部署其他工具

#### 对 docker 有了解吗, 写过 dockerfile 吗

#### docker K8S 的了解程度

#### JMAT 有用过吗

#### JMETER 有用过吗

#### Graylog 的优缺点

### Mysql

#### Mysql 的 MVCC 解决了什么问题, 场景

- **MVCC 的典型场景**

	1. **在线电商系统：**
	    - 用户 A 正在浏览商品库存（读操作）。
	    - 用户 B 正在购买同样的商品，更新库存（写操作）。
	    - 用户 A 通过 MVCC 快照读，可以看到事务开始时的库存数量，而不受用户 B 事务的影响。
	2. **银行交易系统：**
	    - 客户 A 正在查询账户余额（读操作）。
	    - 客户 B 在给 A 转账，修改了 A 的账户余额（写操作）。
	    - 客户 A 看到的是转账操作之前的余额，而不会因为并发操作导致数据不一致。
	3. **分析型查询：**
	    - 数据库执行大批量查询分析时（如报表生成），需要维持一致性视图而不被并发写操作影响。

- **MVCC 解决的问题：**

	1. **读写冲突**：解决了事务间的读写冲突问题，让读操作无需阻塞写操作。
	2. **一致性视图**：在事务中，用户能读取到自己操作的一致性数据快照，而不会被其他事务的更新打扰。
	3. **提升并发性**：通过快照读的方式避免了加锁，提升了读操作的性能。

- **MVCC 的实现方式**

	1. **版本控制：**
	    - 每行数据有两个隐藏字段：`row trx_id`（最近修改它的事务 ID）和两个版本号（`create_version` 和 `delete_version`）。
	2. **快照读：**
	    - 使用 Undo Log 保存数据的旧版本，提供一致性视图。
	3. **当前读：**
	    - 如 `SELECT... FOR UPDATE`，获取最新版本数据，可能需要加锁。

#### 10000 页的深度分页, 连 Offset Limit size 都要一会, 怎么办

1. **基于主键（或唯一索引）的游标分页**
	- 思路：使用上一次分页查询结果的最大值作为下一页的起点（通过 `WHERE` 子句限制）。
	- 示例：

	```sql
	-- 假设有一个自增主键 id
	SELECT * FROM table_name 
	WHERE id > last_id_in_previous_page
	ORDER BY id
	LIMIT page_size;
	```

	- 优点：
	    - 直接跳过无关行，不需要扫描 `OFFSET` 的所有行。
	- 场景：
	    - 适合有连续自增主键或唯一字段的场景。
2. 使用窗口函数优化深分页
	- 通过窗口函数，我们可以对数据进行编号，然后直接筛选所需的范围。

	```sql
	WITH ranked_users AS (
	    SELECT id, name, score, ROW_NUMBER() OVER (ORDER BY score DESC) AS rn
	    FROM users
	)
	SELECT id, name, score
	FROM ranked_users
	WHERE rn BETWEEN 10000 AND 10010;
	```

3. **使用覆盖索引优化**
	- 思路：只扫描索引列，而不是整行数据。
	- 示例：

	```sql
	    SELECT id FROM table_name  ORDER BY id LIMIT 10000, 20;
	    
	    然后根据查询到的 `id` 再获取具体数据：
	    
	    SELECT * FROM table_name WHERE id IN (list_of_ids);
	```

	- 优点：
	    - 减少数据读取量，仅扫描索引。
4. **限制深度分页**
	- 思路：禁止直接查询超深分页，引导用户采用更高效的方式（如搜索或筛选）。
	- 示例：
	    - 通过前端提示用户 "数据量过大，请缩小查询范围"。
	    - 只允许分页到第 X 页，后续采用游标加载。

*从存储角度来说*

1. **提前分区分页**
	- 思路：将数据按时间、地域、类型等字段分区，限制每次分页的数据范围。

	```sql
		SELECT * FROM table_name WHERE create_date BETWEEN '2024-01-01' AND '2024-01-31' ORDER BY id LIMIT 20;
	```

	- 优点：
	    - 减少单次分页需要扫描的数据量。
	- 场景：
	    - 适合时间序列、分布式业务等。
2. **分页缓存**
	- 思路：对于深度分页的请求，提前计算分页结果并存储缓存。
	- 示例：
	    - 将深度分页结果预先缓存到 Redis 等内存数据库。
	    - 请求时直接从缓存中获取，而不是实时查询数据库。
	- 优点场景：
	    - 缓解数据库压力。
	    - 适合热门数据查询，如排行榜。
3. **分布式查询**
	- 思路：对于特别大的表，将数据分布式存储（如 ShardingSphere）。
	- 优点：
	    - 利用多节点同时处理，提高查询速度。

#### 大量 Binlog 的修改, 需要同步, 有了解 Binlog 的订阅机制吗

### 多线程 JUC

#### 线程池的核心线程数和物理机相关性更大还是业务相关性更大

#### CountdownLatch CyclicBarrier 业务中的使用场景 (业务汇总, 就比如分布式计算，多个计算节点分别处理部分数据，处理完后要汇总中间结果，所有节点必须在同一时刻到达一个汇总点)

#### NIO 在 Linux 层面的进化, 从 select/poll 到 epoll 到啥啥的 (第一个问题是想问你多路复用机制的, 原理)

### 设计模式

#### 谈谈对设计模式的理解

### ES

#### 图文消息是如何用 ES, Mysql, redis 存储的.

#### ES 在哪些场景使用的

#### ES 的索引优化

### JVM

#### JVM 优化怎么做的

1. 代码层面和工具层面 控制大对象的创建, 监控大对象的生命周期,
	- **开启 GC 日志**：
	    `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/path/to/gc.log`
		- 使用分析工具查看 GC 性能瓶颈：
		    - 如 GC 停顿时间过长，考虑调整堆大小或换用低延迟 GC。
	- **性能监控工具**
		- **JVM 本身工具：**
		    - `jstat`：监控内存使用、GC 活动。
		    - `jmap`：生成堆快照（Heap Dump）。
		    - `jstack`：查看线程堆栈，排查死锁或性能瓶颈。
		- **可视化工具：**
		    - JConsole/VisualVM：适合基础监控。
		    - Arthas：深入分析线程、内存和代码问题。
		    - 专业监控工具：如 Skywalking、Prometheus。

2. JVM 参数优化
	- **堆大小参数：**
		- `-Xms`: 初始堆大小。
		- `-Xmx`: 最大堆大小。
		- `-XX:NewRatio`: 新生代与老年代的比例。
		- `-XX:SurvivorRatio`: Eden 区与 Survivor 区的比例。

	```bash
	-Xms2g -Xmx2g -XX:NewRatio=2 -XX:SurvivorRatio=8; #应对高并发场景, 所以增大堆内存
	```

	- **常用垃圾回收器：**
		- **串行 GC**（`-XX:+UseSerialGC`）：单线程，适合小型应用。
		- **并行 GC**（`-XX:+UseParallelGC`）：多线程，适合高吞吐。
		- **CMS GC**（`-XX:+UseConcMarkSweepGC`）：低延迟，适合响应时间敏感。
		- **G1 GC**（`-XX:+UseG1GC`）：平衡吞吐与延迟，适合大堆内存。

		```bash
		-XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:ParallelGCThreads=4
		```

		- 延迟敏感系统：调整 `MaxGCPauseMillis` 控制停顿时间。
		- 吞吐优先系统：使用并行 GC。
	- **线程栈大小** -Xss

		```bash
		-Xss512k  # 减小栈大小，允许更多线程
		```

### Redis

#### Redis 的底层数据结构

[Redis蒋德钧_02_Redis中的数据类型和其数据结构](Redis蒋德钧_02_Redis中的数据类型和其数据结构.md)

### 场景题

#### 几十万的文件上传到服务器, 每个几 M 大小, 如何设计

#### 系统同时大量会员注册, 怎么设计

#### SqlSession 连接池, 其中有的链接因为执行时间过长而断开了, 怎么办

#### 如果有一个 age, 想在 Springboot 启动的时候做一些数据校验怎么做
