---
title: 29_Redis如何应对并发
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前

1. 加锁: 会影响并发性能; 需要用到分布式锁
2. 原子操作: 无锁.

## Redis 如何应对并发: 原子操作和 Lua 脚本

### 1. 并发访问中需要控制什么

控制并发数据: 库存, 账户余额等.

### 2. Redis 的两种原子操作

1. 把多个操作在 Redis 中实现成一个操作, 单命令操作: INCR/DECR
	- 不加锁的伪代码:

	```sh
	current = GET(id)
	current--
	SET(id, current)
	```

	- 加锁的伪代码:

	```sh
	LOCK()
	current = GET(id)
	current--
	SET(id, current)
	UNLOCK()
	```

	- 原子操作的 Redis 指令

	```sh
	DECR id 
	```

2. 把多个操作写到一个 Lua 脚本中, 以原子性方式执行
	- 场景: 每分钟访问次数不能超过 20 次: 把 IP 作为 key, 访问次数作为 Value, 设置过期时间即可, 伪代码如下:

	```
	//获取ip对应的访问次数
	current = GET(ip)
	//如果超过访问次数超过20次，则报错
	IF current != NULL AND current > 20 THEN
	    ERROR "exceed 20 accesses per second"
	ELSE
	    //如果访问次数不足20次，增加一次访问计数
	    value = INCR(ip)
	    //如果是第一次访问，将键值对的过期时间设置为60s后
	    IF value == 1 THEN
	        EXPIRE(ip,60)
	    END
	    //执行其他操作
	    DO THINGS
	END
	```

	- 问题: 如果在创建时有两个线程对 value INCR 了两次, 那么就永远无法设置过期时间了.
	- Lua 脚本的解决方式:

	```
	local current
	current = redis.call("incr",KEYS[1])
	if tonumber(current) == 1 then
	    redis.call("expire",KEYS[1],60)
	end
	```

	```
	redis-cli  --eval lua.script  keys , args
	```

	脚本所需的参数将通过 keys 和 args 传递.
	这样就实现了操作的原子性.

## 评论区收获和思考

- 问:Redis 在执行 Lua 脚本时，是可以保证原子性的，那么，在课程里举的 Lua 脚本例子（lua.script）中，你觉得是否需要把读取客户端 ip 的访问次数，也就是 GET(ip)，以及判断访问次数是否超过 20 的判断逻辑，也加到 Lua 脚本中吗？
	- 答: 读操作, 不需要
