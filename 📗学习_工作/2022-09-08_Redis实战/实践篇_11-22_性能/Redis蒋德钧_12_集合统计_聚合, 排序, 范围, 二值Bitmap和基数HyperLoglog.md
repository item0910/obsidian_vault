---
title: 12_集合统计_聚合, 排序, 范围, 二值Bitmap和基数HyperLoglog
date: 2022-09-08
categories: Redis
tags: 归档笔记/学习笔记/Redis
author: 蒋德钧
mtime: 2024-09-25
---

## 学习之前: 各种场景统计

在移动应用中，需要统计每天的新增用户数和第二天的留存用户数；

在电商网站的商品评论中，需要统计评论列表中的最新评论；

在签到打卡中，需要统计一个月内连续打卡的用户数；

在网页访问记录中，需要统计独立访客（Unique Visitor，UV）量。

## 常见的统计场景

### 聚合统计

- 统计每天的新增用户数和第二天的留存用户数
	1. 集合 1 记录所有登陆过 APP 的 ID
	![[附件/image/12_集合统计_聚合, 排序, 范围, 二值Bitmap和基数HyperLoglog.jpg]]
	2. 集合 2 记录每一天登陆过 APP 的 ID
		![[附件/image/12_集合统计_聚合, 排序, 范围, 二值Bitmap和基数HyperLoglog-1.jpg]]
	- 新增用户: 计算每天与集合 1 的差集.
		`SDIFFSTORE  user:new  user:id:20200804 user:id`
	- 累计用户: 计算每天与集合 1 的并集
		`SUNIONSTORE  user:id  user:id  user:id:20200803 `
	- 留存 2 日用户: 计算 23 日与 24 日集合的交集
		`SINTERSTORE user:id:rem user:id:20200803 user:id:20200804`

- 注意点: set 的计算复杂度比较高, 数据量比较大的情况下, 如果直接执行这些计算, 会导致 redis 阻塞. **建议**: 可以将这个任务交给一个从库, 让他专门负责计算; 或者把数据读取到客户端, 让客户端来完成聚合统计.

### 排序统计

- 在 Redis 常用的 4 个集合类型中（List、Hash、Set、Sorted Set），**List 和 Sorted Set 就属于有序集合。**
- List 不适合用分页的情况 (因为只是按照入 List 的先后顺序, 如果获取数据时有新的数据, 那么 List 会按照新的顺序返回结果)
- Sorted Set 就可以完成按权重排序, 可以准确的获取到排序的数据
	- `ZRANGEBYSCORE comments N-9 N`

 #### 某段时间在线用户数

 Sorted Set 可以实现统计一段时间内的在线用户数：

 - 用户上线时使用 `zadd online_users $timestamp $user_id` 把用户添加到 Sorted Set 中，
 - 使用 `zcount online_users $start_timestamp $end_timestamp` 就可以得出指定时间段内的在线用户数。

#### 二值状态统计

- Bitmap
- 用户是否签到:
	- 取一个 31 位的 Bitmap, 一年也只要一个 365 位的 Bitmap
	`SETBIT uid:sign:3000:202008 2 1 `
	- 统计八月份的签到次数 `BITCOUNT uid:sign:3000:202008`
- 统计 1 亿个用户的 10 天的签到情况
	- 以日期为 key, 一亿位的 Bitmap
	- 将十天的结果做与, 就可以得出签到的用户数

### 基数统计: 统计一个集合中不重复的元素

- 用 set 或者 Hash
- HyperLogLog

```
PFADD page1:uv user1 user2 user3 user4 user5

PFCOUNT page1:uv
```

## 评论区收获和思考

- 一个 List 的使用场景
	- 使用 List+Lua 统计最近 200 个客户的触达率。具体做法是，每个 List 元素表示一个客户，元素值为 0，代表触达；元素值为 1，就代表未触达。在进行统计时，应用程序会把代表客户的元素写入队列中。当需要统计触达率时，就使用 LRANGE key 0 -1 取出全部元素，计算 0 的比例，这个比例就是触达率。0000101010101010001011
