---
title: MySQL Too Many Connections 故障排查
date: 2025-12-31
categories: 工作记录
tags: MySQL 连接池 Druid 定时任务 线程池 Kubernetes
author: 自己
---

## 原始对话来源

- Gemini 对话：https://gemini.google.com/share/5383a8e727e1
- 整理时间：2026-03-17

## 问题背景

6 个 Pod 环境，有很多定时任务，需要配置合理的线程池和数据库连接池参数，避免"Too many connections"错误。

## 核心配置方案

### 1. 定时任务线程池配置

#### 方式 A：通过 application.yml 配置

```yaml
spring:
  task:
    scheduling:
      pool:
        size: 20  # 默认是 1，改为 20，避免任务积压
      shutdown:
        await-termination: true  # K8s 杀 Pod 时，等待任务做完
        await-termination-period: 60s
      thread-name-prefix: my-scheduled-task-  # 方便查日志
```

#### 方式 B：Java Config 配置（更灵活）

```java
@Configuration
public class SchedulerConfig {
    
    @Bean
    public ThreadPoolTaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        
        // 线程池大小
        scheduler.setPoolSize(20);
        
        // 线程名称前缀
        scheduler.setThreadNamePrefix("scheduled-task-pool-");
        
        // 优雅停机（适配 K8s）
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        scheduler.setAwaitTerminationSeconds(60);
        
        // 错误处理
        scheduler.setErrorHandler(t -> 
            System.err.println("定时任务执行异常: " + t.getMessage())
        );
        
        return scheduler;
    }
}
```

### 2. Druid 连接池配置

```yaml
spring:
  datasource:
    druid:
      # 核心连接数配置
      max-active: 30  # 最大连接数
      min-idle: 10    # 最小空闲连接数
      initial-size: 10  # 初始化连接数
      
      # 获取连接控制
      max-wait: 30000  # 获取连接最大等待时间（30秒）
      
      # 稳定性与保活（K8s 环境必配）
      validation-query: SELECT 1
      test-while-idle: true  # 空闲时检查连接有效性
      test-on-borrow: false  # 借连接时不检查（高并发下影响性能）
      test-on-return: false  # 归还时不检查
      
      # 检查空闲连接的间隔时间（60秒）
      time-between-eviction-runs-millis: 60000
      
      # 连接在池中最小生存时间（5分钟）
      min-evictable-idle-time-millis: 300000
      
      # 监控与扩展
      filters: stat,wall
```

## 参数设计理由

### 线程池大小：20

- **I/O 密集型任务**：查库、发 HTTP 请求、发邮件，耗时主要在等待
- **配置建议**：Pool Size = 20 ~ 50
- **判断标准**：即使有 100 个任务，它们错峰执行，20 个线程通常足够

### 连接池大小：30

- **计算逻辑**：定时任务线程(20) + 预留给 Web/其他(10) = 30
- **总账控制**：6 个 Pod × 30 = 180 总连接数
- **数据库容量**：大多数 MySQL 生产环境默认支持 500-1000 连接

### 为什么要匹配线程池大小？

- **最坏情况**：20 个任务同时启动，且都是复杂的 SQL 查询
- **如果 DB 连接数只有 10**：只有 10 个任务能跑，另外 10 个任务虽然有线程，但会在 HikariCP/Druid 这一层阻塞等待连接
- **结论**：`maximum-pool-size` ≥ `定时任务并发数` + `Web业务并发数`

## 验证配置是否生效

### 方式一：使用 Druid 监控页面

```yaml
spring:
  datasource:
    druid:
      stat-view-servlet:
        enabled: true
        url-pattern: /druid/*
        # login-username: admin  # 可选
        # login-password: admin  # 可选
```

访问：`http://<你的IP>:<端口>/druid/index.html`

查看关键指标：
- `MaxActive`：应该是 30
- `MinIdle`：应该是 10
- `PoolingCount`：闲置时应该稳定在 10 左右

### 方式二：查看启动日志

```bash
kubectl logs -f <你的pod名字> | grep "maxActive"
```

应该看到类似：
- `maxActive=30`
- `minIdle=10`
- `initialSize=10`

### 方式三：数据库侧验证

#### 查看总连接数

```sql
-- 查看当前连接到数据库的客户端总数
SHOW STATUS LIKE 'Threads_connected';
```

预期结果：
- 闲置时：约 `6 (Pod) × 10 (min-idle)` = 60 左右
- 高负荷时：不应超过 `6 × 30` = 180

#### 分组查看每个 Pod 的连接数

```sql
-- 按 IP 统计连接数
SELECT SUBSTRING_INDEX(host, ':', 1) as pod_ip, 
       COUNT(*) as connection_count
FROM information_schema.processlist
WHERE user = '你的数据库用户名'
GROUP BY pod_ip;
```

预期结果：6 个不同的 IP 地址，每个 IP 后面的 count 大概是 10 (闲置时) 到 30 (忙碌时)。

### 方式四：验证定时任务线程池

在某个 `@Scheduled` 任务里打印线程名：

```java
@Scheduled(cron = "0/5 * * * * ?")
public void testTask() {
    System.out.println("当前执行线程: " + Thread.currentThread().getName());
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {}
}
```

观察日志：
- 默认配置：线程名通常是 `scheduling-1` 一直不变（单线程）
- 配置生效后：会看到 `scheduled-task-pool-1`、`scheduled-task-pool-2` ... 一直到 `scheduled-task-pool-20` 交替出现

## 数据库参数调整

### 查看当前 MySQL 最大连接数

```sql
SHOW VARIABLES LIKE 'max_connections';
```

### 场景分析

#### 场景 A：结果 > 300
- 恭喜，当前 Druid 配置（`max-active: 30`）是安全且有意义的
- 数据库完全撑得住 180 个并发

#### 场景 B：结果 = 151（标准默认值）
- **危险**，有两个选择：
  1. **改 MySQL（上策）**：找 DBA 把 `max_connections` 调大到 500
  2. **改 Druid（下策）**：把 `max-active` 从 30 降级为 20
     - 代价：定时任务线程池是 20，Web 流量也要用连接，连接池只有 20 的话，并发高时会发生排队等待

#### 场景 C：结果 < 100（低配云数据库）
- **极度危险**，6 个 Pod 启动都可能随时把库打挂
- 必须立刻降低 Druid 配置到 10 左右，或者升级数据库规格

### 调整 MySQL 参数

```sql
-- 临时修改（重启失效）
SET GLOBAL max_connections = 500;
```

```ini
# 永久修改（my.cnf 或 my.ini）
[mysqld]
max_connections=500
```

## 核心风险提示

### 6 个 Pod 的陷阱

如果不做处理，每个 Pod 都会启动自己的定时器，意味着每一个定时任务都会在同一时间被执行 6 次。

**必须引入分布式锁（Distributed Lock）**：
- 最常用方案：集成 **ShedLock**（配合 Redis 或 JDBC）
- 确保同一时间，6 个 Pod 中只有一个"抢"到了锁去执行任务，其他 5 个 Pod 保持空闲

## 引申知识点

- Spring Boot 定时任务线程池配置
- Druid 连接池参数调优
- Kubernetes 环境下的优雅停机
- 分布式锁（ShedLock）的必要性
- MySQL 连接数容量规划
