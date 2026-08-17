---
title: 38_通信开销-Redis_Cluster规模的关键
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 为什么集群会受限制

Redis 官方给出了 Redis Cluster 的规模上限，就是一个集群运行 1000 个实例。
实例间的通信开销会随着实例规模增加而增大，在集群超过一定规模时（比如 800 节点），集群吞吐量反而会下降。

## 通信开销 -Redis_Cluster 规模的关键

### 1. Redis Cluster 的通信规则和运行机制

为了让集群中的每个实例都知道其它所有实例的状态信息，实例之间会按照一定的规则进行通信。这个规则就是 Gossip 协议。

Gossip 协议的工作原理可以概括成两点。
- 一是，每个实例之间会按照一定的频率，从集群中随机挑选一些实例，把 PING 消息发送给挑选出来的实例，用来检测这些实例是否在线，并交换彼此的状态信息。PING 消息中封装了发送消息的实例自身的状态信息、部分其它实例的状态信息，以及 Slot 映射表。
- 二是，一个实例在接收到 PING 消息后，会给发送 PING 消息的实例，发送一个 PONG 消息。PONG 消息包含的内容和 PING 消息一样。
![[附件/image/38_通信开销-Redis_Cluster规模的关键.jpg]]

#### Gossip 消息大小

Redis 实例发送的 PING 消息的消息体是由 clusterMsgDataGossip 结构体组成的，这个结构体的定义如下所示：

```c
typedef struct {
    char nodename[CLUSTER_NAMELEN];  //40字节
    uint32_t ping_sent; //4字节
    uint32_t pong_received; //4字节
    char ip[NET_IP_STR_LEN]; //46字节
    uint16_t port;  //2字节
    uint16_t cport;  //2字节
    uint16_t flags;  //2字节
    uint32_t notused1; //4字节
} clusterMsgDataGossip;
```

CLUSTER_NAMELEN 和 NET_IP_STR_LEN 的值分别是 40 和 46，分别表示，nodename 和 ip 这两个字节数组的长度是 40 字节和 46 字节; 这个结构体的总大小一共是 104 字节

1000 个实例集群发送一个 ping 会包含 100 个实例的消息, 加上自身的信息, 一共就是 10kb, 还会附加一个 bitmap 在某个位置上标 1 指示自己, 大小为 2kb, 所以一个 ping 消息就是 12kb, pingpong 加起来一共 24kb

绝对值虽然不大, 但是比起本身只有几 kb 的请求就比较大了, 随着集群增多心跳消息的数量也会增多, 占用网络带宽.

#### 实例间的通信频率

RedisCluster 启动会默认每秒从本地列表中随机选出 5 个实例挑选一个最久没有通信的给他发 ping.(不能保证是本地最长没有通信的)
另外, Redis Cluster 的实例会按照每 100ms 一次的频率，扫描本地的实例列表，如果发现有实例最近一次接收 PONG 消息的时间，已经大于配置项 cluster-node-timeout 的一半了（cluster-node-timeout/2），就会立刻给该实例发送 PING 消息，更新这个实例上的集群状态信息。

>PING 消息发送数量 = 1 + 10 * 实例数（最近一次接收 PONG 消息的时间超出 cluster-node-timeout/2）

假设单个实例检测发现，每 100 毫秒有 10 个实例的 PONG 消息接收超时，那么，这个实例每秒就会发送 101 个 PING 消息，约占 1.2MB/s 带宽。如果集群中有 30 个实例按照这种频率发送消息，就会占用 36MB/s 带宽，这就会挤占集群中用于服务正常请求的带宽。

### 2. 如何降低实例间的通信开销

- PING PONG 消息大小: 不能调
- 心跳查询间隔: 系统统一, 不方便调
- 只能调整 cluster-node-timeout 比如调大到 20 秒或 25 秒: 不好的方面是, 这又会使系统可靠性降低.

你可以在调整 cluster-node-timeout 值的前后，使用 tcpdump 命令抓取实例发送心跳信息网络包的情况。例如，执行下面的命令后，我们可以抓取到 192.168.10.3 机器上的实例从 16379 端口发送的心跳网络包，并把网络包的内容保存到 r1.cap 文件中：

```
tcpdump host 192.168.10.3 port 16379 -i 网卡名 -w /tmp/r1.cap
```

通过分析网络包的数量和大小，就可以判断调整 cluster-node-timeout 值前后，心跳消息占用的带宽情况了。

### 总结:

- 在实际应用中，如果不是特别需要大容量集群，我建议你把 Redis Cluster 的规模控制在 400~500 个实例。主从一半, QPS 为 8 万, 每秒也可以处理 1600 万 ~ 2000 万个请求了.

## 评论区收获和思考

- 如果我们采用跟 Codis 保存 Slot 分配信息相类似的方法，把集群实例状态信息和 Slot 分配信息保存在第三方的存储系统上（例如 Zookeeper），这种方法会对集群规模产生什么影响吗？
	- 实例间不用发送大量心跳来同步状态, 这一部分的网络资源就节约出来了, 所以可以扩大集群规模.
	- 但是 Zookeeper 会面临和许多实例交互, 需要保证其一定的带宽.
