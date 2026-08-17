---
title: 软件使用_Anki_自己做面试题
date: 2024-12-22
categories: 软件使用
tags: 归档笔记/生活经验/数字经验
author: 自己
mtime: 2024-12-22
---

## 第一步 将 PDF 的题目拷贝到 `1.txt` 中

例如:

```txt
43. 了解主从复制的原理吗？
```

## 第二步 用脚本将 txt 转化为 ob 中的 anki 格式的问题模板

```markdown
# 前缀字典
prefix_list = [
    "01·面试小抄·",
    "02·JavaGuide·",
    "03·10万字总结·",
    "04·Docker面试题·",
    "05·K8S面试题·",
    "06·Netty面试题·",
    "07·分布式面试题·"
]

# 选择需要的前缀，通过调整索引来选择
prefix_index = 6 # 根据需要调整为 0, 1, 或 2
prefix_name = prefix_list[prefix_index]

# 文件路径定义
input_file = "1.txt"
output_file = "1_output.txt"

# 读取并处理文件内容
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 重写输出文件
with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        line = line.strip()
        if line:
            f.write(f"- {prefix_name}{line} #card\n")
            f.write("    \n\n")

print(f"处理完成，结果已保存到 {output_file}")

```

- 说明: 前缀模板用来标记问题的出处, 以方便后续寻找答案

## 第三步 在 ob 中准备好 Anki 的模板文件, 将上一步获得的 `1_output.txt` 复制到这里

```markdown
---
cards-deck: Anki_八股文面试题
mtime: 2024-12-19
---

## 分布式

- 07·分布式面试题·43. 了解主从复制的原理吗？ #card
    



```

然后填写简要的答案提纲, 当做第一遍复习, 之后 flashCard 到 Anki 中
如果对问题的数量不放心, 可以放到 notepad++ 中, 数一下 `#card` 的数量, 进行比对.

## 如何在 Anki 中添加 ob 链接?

- 复制 ob 链接, 并包裹在这里面
	``<a href="">标题</a>``
- 举个例子
	`<a href="obsidian://open?vault=TechNotes&amp;file=%F0%9F%94%A7%E9%A1%B9%E7%9B%AE_%E5%AD%A6%E4%B9%A0%2FIT%E9%A1%B9%E7%9B%AE%2F2022.09.08_Redis%E5%AE%9E%E6%88%98%2F%E5%9F%BA%E7%A1%80%E7%AF%87_00-10_Redis%E5%9F%BA%E6%9C%AC%E7%94%A8%E6%B3%95%E5%8A%9F%E8%83%BD%2FRedis%E8%92%8B%E5%BE%B7%E9%92%A7_06_Redis%E5%A6%82%E4%BD%95%E5%AE%9E%E7%8E%B0%E4%B8%BB%E4%BB%8E%E4%B8%80%E8%87%B4">Redis如何实现主从一致</a>`
