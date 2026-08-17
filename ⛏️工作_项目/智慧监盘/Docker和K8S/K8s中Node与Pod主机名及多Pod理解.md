---
title: K8s中Node与Pod主机名及多Pod理解
date: 2026-03-16
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 项目笔记/AI对话/K8S
author: 自己
---

## 对话内容大致纲要

来源对话：

- <https://gemini.google.com/share/e418cf580379>
- <https://gemini.google.com/share/57c1be6e8c3b>

这组对话主要围绕几个连续问题展开：

1. K8s 中 node 的 `hostName` 和 pod 的 `hostName` 会不会相同；
2. 多 pod 是不是就等于多实例；
3. 多实例发布时，能不能给每个 pod 指定不同的 `hostName`；
4. 能不能给每个 pod 指定固定 IP。

顺着这个话题，又自然引出了一个实际开发问题：

- 如果一个服务部署成多个 Pod，像 `@Scheduled` 这种定时任务就可能被多个实例重复执行；
- 这时候就会涉及“实例标识”“节点标识”以及“分布式锁”的问题。

## 重点复盘点

### 1. 默认情况下，Node Hostname 和 Pod Hostname 通常不相同

默认情况下：

- **Node Hostname**：节点宿主机名，例如 `k8s-worker-01`
- **Pod Hostname**：通常是 Pod 自己的名字，例如 `my-app-6d4b5c`

所以在绝大多数普通 Pod 场景下：

- Pod 看到的是自己的 hostname；
- 不会直接等于 Node 的 hostname。

这是因为 Kubernetes 默认会给 Pod 独立的 UTS namespace，主机名是隔离的。

---

### 2. 特殊情况下，Pod 也可能看到宿主机主机名

如果开启一些共享宿主机能力，例如：

- `hostNetwork: true`
- `hostUTS: true`

那么 Pod 就可能直接使用或看到宿主机的主机名。

例如：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shared-hostname
spec:
  hostNetwork: true
  hostUTS: true
  containers:
    - name: busybox
      image: busybox
      command: ["sh", "-c", "hostname && sleep 3600"]
```

这时容器里执行 `hostname`，返回的就更可能是 node 的名字。

但日常业务 Pod 默认不建议依赖这种共享方式。

---

### 3. 多 Pod，本质上就是多实例

这个结论可以直接记住：

- **在 K8s 里，多 Pod 基本就等于多实例。**

例如：

```yaml
replicas: 3
```

表示会运行 3 个 Pod 副本。通常可以理解成：

- 3 个相同服务实例；
- 独立 IP；
- 独立运行环境；
- 通过 Service 共同对外提供服务。

所以它和传统部署中的：

- 启 3 个 Java 进程；
- 分布在不同机器上；

本质目的是一致的：

- 高可用
- 负载均衡
- 滚动发布

---

### 4. 多 Pod 场景下，定时任务会重复执行

这是实际开发里特别容易踩的点。

例如：

- 一个 Spring Boot 服务里有 `@Scheduled`
- 本地单实例没问题
- 上 K8s 后配置了 `replicas: 3`

那么定时任务通常会变成：

- 3 个 Pod 同时执行
- 同一业务被处理 3 次

也就是说：

- 多 Pod 带来了高可用；
- 但也带来了“重复执行”的风险。

所以只要是：

- 定时任务
- 批处理
- 补偿任务
- 扫描任务

在多实例场景下，都要额外考虑“只能由一个实例执行”。

---

### 5. 多实例时，不能在 Deployment 里手工给每个 Pod 指定不同 hostname

这个点也很重要。

如果是：

- `Deployment`
- `replicas > 1`

那么你**不能像配置列表一样**指定：

- Pod A = `host-1`
- Pod B = `host-2`
- Pod C = `host-3`

Deployment 不提供这种“逐个副本手工命名 hostname”的能力。

#### 如果只是想要每个 Pod 都有唯一标识

那其实默认就有：

- Pod 名本身就是唯一的；
- 可以通过 Downward API 注入给应用读取。

例如：

```yaml
env:
  - name: MY_POD_HOSTNAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
```

然后在应用里读取：

```java
String podName = System.getenv("MY_POD_HOSTNAME");
```

这通常就够用了。

#### 如果确实需要稳定、有序、不变的 hostname

那更适合改用：

- **StatefulSet**

例如会得到：

- `my-app-0`
- `my-app-1`
- `my-app-2`

这种名字在 Pod 重建后仍然稳定，更适合：

- 有状态服务
- 需要固定身份标识的场景

---

### 6. 不要在多副本 Deployment 里硬写固定 hostname

例如这种：

```yaml
spec:
  template:
    spec:
      hostname: "my-fixed-name"
```

如果副本数大于 1，那么所有 Pod 都会叫同一个名字。

这会带来很多问题：

- 日志难以区分来源；
- 应用注册中心里的实例标识可能互相覆盖；
- 某些依赖 hostname 做节点标识的逻辑会混乱。

所以固定 `hostname` 在多实例 Deployment 里通常不是正确方案。

---

### 7. Pod IP 默认也是临时的，不能在标准 Deployment 里逐个写死

K8s 的设计里，Pod 本来就是临时资源：

- 删除重建后 IP 可能变化；
- 调度到别的节点后 IP 可能变化；
- 扩缩容时也会变化。

所以在标准 Kubernetes 用法里，通常**不应该依赖固定 Pod IP**。

#### 如果你只是想让别人稳定访问服务

正确做法不是固定 Pod IP，而是使用：

- `Service`
- `Ingress`
- `LoadBalancer`

例如集群内部访问，用 Service 名称就行。

#### 如果你是为了白名单

通常也不是固定每个 Pod IP，而是考虑：

- 节点出口 IP
- NAT 网关
- Egress Gateway

而不是强行要求每个 Pod 都固定 IP。

---

### 8. `hostNetwork: true` 会让 Pod 直接使用宿主机网络，但不是通用解法

如果配置：

```yaml
hostNetwork: true
```

那么：

- Pod IP 会变成宿主机 IP；
- 端口直接占用宿主机端口；
- 同一台机器上相同端口无法起多个副本。

所以它只适合少数特殊场景，例如：

- 节点级 agent
- 网络插件
- 监控/日志采集守护进程

不适合作为普通业务服务“固定 IP”的常规方案。

## 引申知识点

### 1. `hostName` 更适合做“实例标识”或“日志标识”，不适合单独充当真正的分布式锁

这个点要特别记一下。

你可以把 `hostName` 用在：

- 打日志，标识是哪个 Pod / 哪个节点执行的；
- 作为锁持有者信息的一部分，写进 Redis / DB；
- 做问题排查时标记执行来源。

但 **不能只靠 `hostName` 本身就认为实现了分布式锁**。

因为：

- 仅知道“我是谁”不等于“我抢到了唯一执行权”；
- 多个 Pod 都有自己的 hostname，它们依然可能同时执行；
- 分布式锁的核心不是 hostname，而是一个**共享介质上的原子抢占动作**，例如 Redis、数据库、ZooKeeper 等。

所以正确理解应该是：

- `hostName` 可以是锁的“持有者标识”；
- Redis / DB 才是锁的“竞争与约束机制”。

---

### 2. 一个可理解的例子：用 `hostName` 作为锁拥有者标识

假设现在有 3 个 Pod：

- `task-service-6c8f7d`
- `task-service-7a2d91`
- `task-service-9b1e33`

每个 Pod 都会执行同一个定时任务，但你希望同一时刻只能一个实例执行。

可以这样设计：

#### 思路

1. 每个 Pod 启动时拿到自己的 hostname；
2. 执行任务前去 Redis 抢锁；
3. 锁的 value 写入自己的 hostname；
4. 抢到锁的那个 Pod 才执行；
5. 执行完成后只允许锁持有者自己释放。

#### Java 示例（示意）

```java
import java.net.InetAddress;
import java.time.Duration;
import org.springframework.data.redis.core.StringRedisTemplate;

public class JobRunner {

    private final StringRedisTemplate redisTemplate;

    public JobRunner(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void executeJob() throws Exception {
        String hostName = InetAddress.getLocalHost().getHostName();
        String lockKey = "job:daily-report:lock";

        // setIfAbsent = Redis SETNX
        Boolean locked = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, hostName, Duration.ofMinutes(5));

        if (!Boolean.TRUE.equals(locked)) {
            System.out.println("未抢到锁，当前实例跳过执行，hostName=" + hostName);
            return;
        }

        try {
            System.out.println("抢到锁，开始执行任务，hostName=" + hostName);
            // 这里写真正的任务逻辑
        } finally {
            String currentOwner = redisTemplate.opsForValue().get(lockKey);
            if (hostName.equals(currentOwner)) {
                redisTemplate.delete(lockKey);
            }
        }
    }
}
```

这个例子里：

- `hostName` 不是锁本身；
- 它只是“谁抢到了锁”的标识；
- 真正保证互斥的是 Redis 的原子 `setIfAbsent`。

---

### 3. 如果只是想让“每个节点只执行一次”，可以把 hostName 当作分组维度

有些场景不是“全局只执行一次”，而是：

- 每个节点执行一次；
- 同一节点上的多个 Pod 不要重复执行。

这种场景可以利用 `nodeName / hostName` 做锁 key 分组。

例如锁 key 设计成：

```text
job:sync:node:k8s-worker-01
```

这样效果是：

- 同一 node 上的 Pod 竞争同一把锁；
- 不同 node 上可以各执行一次。

#### 示例思路

```java
String nodeName = System.getenv("NODE_NAME");
String lockKey = "job:sync:node:" + nodeName;
```

这里的 `NODE_NAME` 一般通过 K8s downward API 注入，而不是在 Pod 里盲猜。

这个模式适合：

- 节点级缓存刷新
- 节点级本地文件处理
- 节点级 agent 任务

但如果你的目标是“全局全集群只执行一次”，那锁 key 就不该带 nodeName。

---

### 4. K8s 里区分“我是谁”和“我在哪”最好显式注入

对话里其实暗示了一个很有用的认知：

- Pod 名：表示“我是谁”
- Node 名：表示“我在哪”

在 Java 程序里，如果想稳定拿到这两个值，最好通过环境变量注入。

例如：

```yaml
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
```

应用中再读取：

```java
String podName = System.getenv("POD_NAME");
String nodeName = System.getenv("NODE_NAME");
```

这通常比单纯依赖 `InetAddress.getLocalHost().getHostName()` 更稳，更清晰。

---

### 5. 如果真正需要“稳定身份”，优先考虑 StatefulSet，而不是在 Deployment 上硬改 hostname/IP

这个是这组对话里很值得记下来的架构判断。

如果你需要的是：

- 稳定名字
- 固定顺序
- 重建后身份不变
- 稳定 DNS

那通常应该优先考虑：

- `StatefulSet + Headless Service`

而不是在 Deployment 上强行做：

- 固定 hostname
- 固定 Pod IP
- 各种手工注入唯一值后再假装成有状态实例

因为从模型上说，这已经更接近 StatefulSet 的职责了。

## 可直接记住的结论

- 默认情况下，**Node Hostname 和 Pod Hostname 通常不相同**。
- 多 Pod 在业务语义上，基本就等于多实例。
- 多实例后，`@Scheduled` 这类任务通常会重复执行，必须考虑分布式锁或调度协调。
- `Deployment` 多副本场景下，**不能逐个手工给每个 Pod 指定不同 hostname**。
- 如果需要稳定、有序的主机名，更适合用 `StatefulSet`。
- 标准 K8s 场景下，**不要依赖固定 Pod IP**；服务访问优先用 `Service`，白名单优先考虑出口 IP / NAT / Egress Gateway。
- `hostName` 可以用来做：
  - 实例标识
  - 日志标识
  - 锁持有者标识
- 但 **不能只靠 `hostName` 本身实现分布式锁**。
- 真正的分布式锁，仍然要依赖 Redis / 数据库等共享存储上的原子操作。
- 如果想区分 Pod 和 Node，优先用 K8s downward API 注入环境变量来拿值。
