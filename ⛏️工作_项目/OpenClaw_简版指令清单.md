---
title: OpenClaw_简版指令清单
date: 2026-03-16
categories: 工作记录
tags: 项目笔记/AI协作/OpenClaw
author: 自己
---

## 简版指令清单

### 1. 读书

#### 指令 A
`读一下《某某书》`

默认执行：
- 去 `D:\待阅读书目` 找书
- 阅读并总结
- 总结保存到 `E:\openClaw\read\书名-总结.md`
- 默认把 **原书 + 总结** 一起发到默认邮箱

#### 指令 B
`邮箱查收一下《某某书》`

默认执行：
- 去邮箱查找对应读书邮件
- 附件下载到 `D:\待阅读书目\openClaw`
- 阅读并总结
- 总结保存到 `E:\openClaw\read\书名-总结.md`
- **不回发原书**，只发送总结

---

### 2. 记忆

#### 长期记忆原则
- 主会话只读取当天和前一天的每日记录，以及精炼后的 `MEMORY.md`
- 普通对话、测试、排错过程和临时状态默认不保存
- 只持久化双方确认、长期稳定、会影响后续执行的约定或结论
- 助手认为值得保存的内容，也需先征得确认
- 只保留最终有效结论，及时清理过期或重复内容
- 项目专属信息优先写入项目文档，不放入全局记忆

#### 指令
`同步记忆`

默认执行：
- 将当前约定范围内的记忆同步到 Gitee 记忆仓库

---

### 3. AI 问答整理

#### 指令
`整理AI问答`

默认执行：
- 你告知目标文件或目录
- 我按真实问题归属整理
- 同类问题优先合并
- 不同主题先确认是否拆分
- 衍生问题优先并入原文档
- 如果你明确说只保留某个结论/命令/方案，就做最小必要整理
- ToDo 类内容记成待办项

---

### 4. Obsidian 仓库备份

#### 指令
`备份我的 Obsidian 仓库`

默认执行：
- 优先使用脚本：`E:\openClaw\js\backup_obsidian_vault.ps1`
- 备份链路：
  - 源仓库：`D:\icloud\iCloudDrive\iCloud~md~obsidian\OnlineVault`
  - 本地镜像：`D:\obsidian_backup\OnlineVault`
  - 远程仓库：`https://gitee.com/chen-pei3/Obsidian_backUp.git`

---

### 5. Codex Auth 同步

#### 指令
`把 codex 的 auth 文件同步给我`

默认执行：
- 直接执行桌面脚本：`C:\Users\Administrator\Desktop\codex_auth更新脚本.py`

---

### 6. 默认邮箱规则

如果你没有特别指定收件地址，或者说“给我发邮件”，默认邮箱为：

`cahujitencha@163.com`
