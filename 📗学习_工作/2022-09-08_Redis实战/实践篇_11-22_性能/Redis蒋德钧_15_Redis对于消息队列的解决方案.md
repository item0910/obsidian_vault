---
title: 15_Redis对于消息队列的解决方案
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 消息队列的需求是什么

1. 消息保序
2. 识别处理重复消息
	当消息由于某些原因发生重复时, 能够判断不进行重复执行
3. 保证消息的可靠性.
	宕机没有处理完的情况, 要保证消息能正确处理完.

## Redis 是如何充当消息队列的

### 1. 基于 List 的消息队列

1. 保序: List 本来就是按照顺序保存的, 所以可以保证保序性.
	- 具体来说, 消息的生产者进行 Lpush , 消费者通过 Rpop 来获取消息.
	- 缺点: 消费者要不断的进行 Rpop 来获取消息, 对消费者的 CPU 占用严重, 所以提供 BRpop 来提供阻塞式的消息获取.(阻塞连接, 直到队列中有消息可以获取)
2. 重复性问题:
	- 在往 list 内添加消息时, 添加一个唯一 ID, 帮助识别消息

	```
	LPUSH mq "101030001:stock:5"
	(integer) 1
	```

3. 可靠性问题
	- BRPOPLPUSH 指令, 会把弹出的消息存到一个备份队列中, 当执行消息队列时发生宕机时, 再从备份的队列中进行读取即可.
4. 问题: List 如果生产者生产速度远大于消费者的速度时, 消息会累积, 给内存带来压力. 而 List 是无法实现消费者组一起消费消息队列的., 由此, 5.0 版本之后 Redis 添加了 Streams 的数据类型.

### 2. Streams 实现消息队列

- Streams 是 Redis 专门基于消息队列设计的数据类型.
- 指令
	1. 插入消息: 表示插入一个键 repo, 值 5 的消息, `*` 代表生成一个全局唯一的 ID, 比如 "1599203861727-0"

	```
	XADD mqstream * repo 5
	"1599203861727-0"
	```

	2. 读消息: block 表示阻塞式读消息, 后面根的是阻塞时间. 从 mqstream 内, 由 `1599203861727-0` 后读消息

	```
	XREAD BLOCK 100 STREAMS  mqstream 1599203861727-0
	1) 1) "mqstream"
	   2) 1) 1) "1599274912765-0"
	         2) 1) "repo"
	            2) "3"
	      2) 1) "1599274925823-0"
	         2) 1) "repo"
	            2) "2"
	      3) 1) "1599274927910-0"
	         2) 1) "repo"
	            2) "1"
    ```

		`$`表示读取最新的消息, 后面表示10秒后没有消息, 返回nil

	```
	XREAD block 10000 streams mqstream $
	(nil)
	(10.00s)
	```

	3. 消费组相关指令:
		- 创建消费组, 这个消费组的消费队列是 mqstream

			```
			XGROUP create mqstream group1 0
			OK
			```

		- 消费者的消费者 consumer1 从 `>` 代表的未被消费的 mqstream 的第一条消息开始读取.

			```
			XREADGROUP group group1 consumer1 streams mqstream >
			1) 1) "mqstream"
			   2) 1) 1) "1599203861727-0"
			         2) 1) "repo"
			            2) "5"
			      2) 1) "1599274912765-0"
			         2) 1) "repo"
			            2) "3"
			      3) 1) "1599274925823-0"
			         2) 1) "repo"
			            2) "2"
			      4) 1) "1599274927910-0"
			         2) 1) "repo"
			            2) "1"
			```

		- 再读取该消费队列的消息就是空值

			```
			XREADGROUP group group1 consumer2  streams mqstream 0
			1) 1) "mqstream"
			   2) (empty list or set)
			```

		- 每个消费者读取一定量的消息, 完成负载均衡

			```
			XREADGROUP group group2 consumer1 count 1 streams mqstream >
			1) 1) "mqstream"
			   2) 1) 1) "1599203861727-0"
			         2) 1) "repo"
			            2) "5"
		
			XREADGROUP group group2 consumer2 count 1 streams mqstream >
			1) 1) "mqstream"
			   2) 1) 1) "1599274912765-0"
			         2) 1) "repo"
			            2) "3"
		
			XREADGROUP group group2 consumer3 count 1 streams mqstream >
			1) 1) "mqstream"
			   2) 1) 1) "1599274925823-0"
			         2) 1) "repo"
			            2) "2"
			```

		- 为了实现可靠性, Streams 会自动使用内部队列, pending List, 留存每个消费者读取的消息, 直到消费者使用 XACK 命令通知 Streams 表示消息已经处理完成. 所以可以在断连之后用 XPENDING 命令查看已读取, 但尚未确认处理完成的消息.

			```
			XPENDING mqstream group2
			1) (integer) 3
			2) "1599203861727-0"
			3) "1599274925823-0"
			4) 1) 1) "consumer1"
			      2) "1"
			   2) 1) "consumer2"
			      2) "1"
			   3) 1) "consumer3"
			      2) "1"
			```

		- 查看哪条数据被哪个消费者读取了, 但还没有返回

			```
			XPENDING mqstream group2 - + 10 consumer2
			1) 1) "1599274912765-0"
			   2) "consumer2"
			   3) (integer) 513336
			   4) (integer) 1
			
			```

		- 一旦该消息被消费, 那么这条消息就会被删除

			```
			 XACK mqstream group2 1599274912765-0
			(integer) 1
			XPENDING mqstream group2 - + 10 consumer2
			(empty list or set)
			```

![[附件/image/15_Redis对于消息队列的解决方案.jpg]]

### 3. 总结, 能否用 Redis 做消息队列

消息通信量不大, 可以考虑; 如果消息量多, 那么考虑重量级的 Kafka, RabbitMQ 等消息队列.

## 评论区收获和思考

- 如果一个生产者发送给消息队列的消息需要被多个消费者进行读取和处理, 你会采用什么数据类型来解决这个问题.
	- Streams, 需要让不同的消费者在不同的消费组 (等于把消息发送给不同的组由他们消费)
	- Redis 发布和订阅的功能 (基于字典和链表的数据结构), 满足多消费者的需求.
