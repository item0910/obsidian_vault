---
date: 2024-09-07
mtime: 2024-11-18
title: 经验记录_AI_常用Prompt记录
categories: 网络经验
tags: 归档笔记/生活经验/数字经验
author: 自己
---

## 生成 RSS 链接

**Prompt:**

" 我将会发送两种不同格式的链接给你，请根据不同的格式生成相应的字符串。

**格式一：**
- 链接格式：https://space.bilibili.com/[id], [中文名字]
- 生成的字符串格式：

```  

<outline text="[中文名字]" title="[中文名字]" type="rss"
			xmlUrl="https://rsshub.app/bilibili/user/dynamic/[id]/disableEmbed=1" htmlUrl="https://space.bilibili.com/[id]/dynamic"/>

```  

**格式二：**
- 链接格式：https://www.141jav.com/actress/[EnglishName], [ChineseName]
- 生成的字符串格式：

```  

<outline text="[ChineseName]" title="[ChineseName]" type="rss"
			xmlUrl="https://rsshub.app/141jav/actress/[EnglishName]" htmlUrl="https://www.141jav.com/actress/[EnglishName]"/>

```  

请根据发送的链接和名字，自动选择合适的格式生成字符串。"

## 重新组织豆瓣游戏的格式

```prompt
我会发给你一段游戏的背景信息, 请帮助我按以下格式组织

类型: [游戏类型]
平台: [游戏平台]
别名: [游戏别名]
开发商: [开发商名称]
发行商: [发行商名称]
发行日期: [发行日期]

如果我的信息中没有提供相关行的信息, 就将那一行删去
```

## Zlib 机器人字符串修改

```prompt
我会给你发一个网页地址，请帮我按照以下规则处理并返回结果：

- 网页地址格式为：`https://zh.singlelogin.re/book/一串数字/一串字母/描述`
- 请将地址中的 `/book/` 后的一串数字和一串字母提取出来
- 删除第二个 `/`，并将第三个 `/` 替换为 `_`
- 结果格式：`/book数字_字母`

**示例：**

输入：`https://zh.singlelogin.re/book/5332205/561e1a/描述.html`

输出：`/book5332205_561e1a`

直接返回结果即可，不要加任何多余修饰。
```

## pdf 去除换行

```prompt
**任务：** 作为阅读助手，帮助用户对他们提供的阅读材料进行文本整理。具体包括：

1. **去除不必要的空格和换行**：确保文本连贯、清晰。
2. **重新整理成通顺的句子**：保持原文内容不变的情况下，使句子更自然流畅。

**格式：** 仅处理文本内容，不对原文内容进行增减或修改。

**例子：**

- 原文片段：  
    “很多⼈会 不由 ⾃主地 ⾃我设限，他觉得 ⾃⼰以前是做某某⾏业的， 然后就⼀厢情愿地按照 ⽼的 思路做⼀个单⼀的业务。”
    
- 处理后：  
    “很多人会不由自主地自我设限，他觉得自己以前是做某某行业的，然后就一厢情愿地按照老的思路做一个单一的业务。”
```

