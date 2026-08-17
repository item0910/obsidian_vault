---
title: Step02_Git使用
date: 2025-01-13
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘
author: 自己
---

## 1. 事前工作

- 需要联系项目经理把你加入后端组里
- 安装 git

## 2. Git 使用

### 命令行下

右键 git bush here
1. 配置 ssh
	1. `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"` 其中 `-t rsa`：指定使用 RSA 算法生成密钥。`-b 4096`：设置密钥长度为 4096 位（更安全）。`-C "your_email@example.com"`：添加一个注释（通常是你的电子邮件）。执行后，命令会提示你选择保存密钥的位置。默认情况下，密钥保存在 `~/.ssh/id_rsa`。如果没有特别需求，按 Enter 键即可使用默认路径。
	2. `cat ~/.ssh/id_rsa.pub` 复制
	3. 到 git 页面的 preferences 里, 粘贴公钥
2. 配置姓名和邮箱
	1. `git config user.name "name"` 设置当前项目名
	2. `git config --global user.name "Your Name"` 设置全局
	3. `git config user.email` 同理设置
3. 拉取 dev
	1. 首先先 `clone` 主库代码
	2. 然后查看 `branch` `git branch -r`
	3. 然后 check out 过去

### Idea 下

1. 首先有 git 插件
2. 配置 git 路径 settings -> version control -> git 配置路径
3. 然后就可以在左下角或者右上角 check out 了.

## 特殊情况的处理

### 代码被其他人用了, 没有办法改

每次 commit 之前最好手动留存一份
然后别人的代码尽量不要动, 不然处理冲突首先要面对的就是人的问题

## Git 忽略

设置, editor -> file types -> ignore
.idea 和 `/*/target`

.gitignore 文件

```txt
# Default ignored files
/shelf/
/workspace.xml
/.idea/
target/
/*/target/
logs
*.iml
*.ipr
.idea
```

## 不在 push 时 merge

git -> **Update Method** 中，选择 **Rebase**

## 记一次成功的 merge

### 一次还算成功的 Merge

1. 使用 `git reflog` 找到本地提交的哈希值。
2. 使用 `git reset --hard <commit-hash>` 重置到本地提交。
3. 使用 `git pull --rebase` 重新拉取远程更改并解决冲突。
4. 解决冲突后，使用 `git rebase --continue` 完成 rebase。
5. 推送到远程仓库（如果需要）。

### 最近一次回滚的经历

1. 首先是 reset hard 到一个位置
2. 然后是 push -f 强制推送了
3. 然后是 重新 merge 了

### 另一次直接凌乱的一次

1. 先是因为代码冲突和提交冲突没处理好 一下子凌乱了, 有了很多提交记录, 简直了..
2. 然后 git rm 啥的, 把本地库删了, 还好物理保存了一份 (可见物理手动保存一份是多么重要)
3. 然后通过新建一个仓库的方式, 把代码 copy 进去, 然后重新 commit, pull, 处理冲突, 然后 push, 才显得提交记录清爽, 也完成了代码合并. 这真的是一个好办法..

### Cherry Pick

Cherry Pick 主要是用来拉取某些分支的特性代码用的

点击小眼睛, 可以看代码是不是被 pick 过

![[智慧监盘_Step02_Git使用-1759508322551.jpeg]]

### Patch

就是把本地的变更应用到分支上.
