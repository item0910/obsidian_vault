1. 项目拉取
	1. 每个项目分别拉 git 的脚本, 拉下来若干个没有.git 文件夹的项目;
	2. 获取主要项目配置 nacos, ddl, yapi 接口文档
	3. 获取次要项目配置, opt, maven.xml
2. 建立一个总的 git 项目, 用来保存本次开始的代码, 并完成 commit. commit 内容, XX 日开始
3. claude 相关
	1. 准备一个通用的 claude 使用说明, 用来记录使用中遇到的技巧
	2. 准备一个项目相关的 claude prompt 文件, 用来记录项目相关的提示内容
4. 完成代码的编写, 誊写到项目中
	1. 最后 add, status 来确认修改了哪些内容,
	2. 用脚本来完成内容的复制.

新工作流:

1. 通过 `0. init_commit.py` 来复制并完成代码的首次 commit, 以建立修改的基点
2. 通过 `1. 获取git修改` 脚本来获取本次的 changes.patch
3. 拿到 change.patch 用 `3. git_apply_tool_pauseVersion.bat` 脚本去执行 进入后选择 2

### win10 中的 ubuntu

进入 `\\wsl$`
`mnt` 文件夹对应的就是物理机的文件夹

### 生成和执行 diff

1. 进入 dip-imb
2. 执行 `git apply` 时, 我们实际需要进入到 a/dip-imb 内部, 所以我们如果在 dip-imb 内部执行 git 时, 实际上我们要忽略两层目录, 也就是要输入 -p2; 但是如果在 dip-imb 同目录下执行时, 我们只需要输入 1 来忽略 a/这么一个层级.(但是 dip-imb 同目录下要有 git 待尝试)

### 测试 PE

1. 先通过安装 PE 系统, 来测试如何操作
2. 然后用 x 的电脑, 试一下能不能把文件放进去.
3. 不行就要用硬盘盒试一下.
