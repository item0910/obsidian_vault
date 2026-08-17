---
title: 项目笔记_Hexo_07插件
date: 2025-01-19
categories: 项目笔记
tags: hexo
author: 自己
---

## 问题描述: obsidian 中的反向代理不能在 hexo 中被渲染出来

### 解决方法: 安装 hexo-backlink

[Hexo-Backlink：为你的Hexo博客添加智能反向链接-CSDN博客](https://blog.csdn.net/gitblog_00588/article/details/142196778)

````bash
npm install hexo-backlink
````

在 hexo 主目录下的 `_config.yaml` 中配置
`backlink: true`
