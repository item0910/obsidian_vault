---
date: 2024-09-07
mtime: 2024-09-25
---

# 一. Netty 是什么

## 1.1 是什么

```
Netty is an asynchronous event-driven network application framework
for rapid development of maintainable high performance protocol servers & clients.
```

Netty 是一个异步的、基于事件驱动的网络应用框架，用于快速开发可维护、高性能的网络服务器和客户端

## 1.2 应用场景

## 1.3 优势

## 1.4 性能 (面试题中)

# 二. Netty 的工作模式与核心组件

## 例 1: 回声服务器

## 例 2: 基本使用 (黑马)

- 服务器端

```java
public class HelloServer {
    public static void main(String[] args) {
        // 1. 启动器，负责组装 netty 组件，启动服务器
        new ServerBootstrap()
                // 2. BossEventLoop, WorkerEventLoop(selector,thread), group 组
                .group(new NioEventLoopGroup())
                // 3. 选择 服务器的 ServerSocketChannel 实现
                .channel(NioServerSocketChannel.class) // OIO BIO
                // 4. boss 负责处理连接 worker(child) 负责处理读写，决定了 worker(child) 能执行哪些操作（handler）
                .childHandler(
                        // 5. channel 代表和客户端进行数据读写的通道 Initializer 初始化，负责添加别的 handler(需要在连接建立后才进行)
                        new ChannelInitializer<NioSocketChannel>() {
                            @Override
                            protected void initChannel(NioSocketChannel ch) throws Exception {
                                // 6. 添加具体 handler
                                ch.pipeline().addLast(new LoggingHandler());
                                ch.pipeline().addLast(new StringDecoder()); // 将 ByteBuf 转换为字符串
                                ch.pipeline().addLast(new ChannelInboundHandlerAdapter() { // 自定义 handler
                                    @Override // 读事件
                                    public void channelRead(ChannelHandlerContext ctx,Object msg) throws Exception {
                                        System.out.println(msg); // 打印上一步转换好的字符串
                                    }
                                });
                            }
                        })
                // 7. 绑定监听端口
                .bind(8080);
    }
}

```

- 客户端

```java
public class HelloClient {
    public static void main(String[] args) throws InterruptedException {
        // 1. 启动类
        new Bootstrap()
                // 2. 添加 EventLoop
                .group(new NioEventLoopGroup())
                // 3. 选择客户端 channel 实现
                .channel(NioSocketChannel.class)
                // 4. 添加处理器
                .handler(
                        new ChannelInitializer<NioSocketChannel>() {
                            @Override // 在连接建立后被调用
                            protected void initChannel(NioSocketChannel ch) throws Exception {
                                ch.pipeline().addLast(new StringEncoder());
                            }
                        })
                // 5. 连接到服务器
                .connect(new InetSocketAddress("localhost", 8080))
                .sync()
                .channel()
                // 6. 向服务器发送数据
                .writeAndFlush("hello, world");
    }
}
```

## 2.1 ChannelHandler 和 ChannelPipeline(书上第六章和第三章)

## 2.2 EventLoop 线程模型与任务调度 (ChannelFuture)(书上第七章, 面试题)

### NioEventLoop 源码

## 2.3 ByteBuf(第五章, 视频, 面试题)

### 零拷贝

### 黏包和半包

### 协议设计与解析 (视频)

## 2.4 引导类 (BootStrap)

## 2.5 单元测试 (EmbeddedChannel)

## 2.6 编解码器

# 三. Netty 的优化

## 3.1 聊天业务 (心跳)(视频)

## 3.2 扩展序列化算法

## 3.3 参数设置
