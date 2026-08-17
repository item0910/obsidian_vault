---
title: 01在CentOS上部署直播源
date: 2024-09-03
categories: 技术
tags: 归档笔记/生活经验/数字经验
author: 自己
mtime: 2024-09-25
---

## 步骤

### 1. 打开服务器端口

### 2. 部署流程

1. docker 镜像 allinone_linux_amd64

```
[root@iZbp130c4i11xkls35ggnjZ chen]# uname -m

常见的输出包括：

- `x86_64`：表示 64 位的 AMD 或 Intel 处理器，适用于 `amd64` 镜像。
- `aarch64`：表示 ARM 64 位架构，适用于 `arm64` 镜像。
- `i386` 或 `i686`：表示 32 位的处理器，适用于 `i386` 镜像。
```

1. 准备 dockfile 来部署
	1. 在镜像所在目录创建名为 Dockerfile 的文件, 内容如下

	```Dockerfile
	FROM ubuntu:22.04
	
	RUN apt-get update && apt-get install -y ca-certificates libc6
	
	COPY allinone_linux_amd64 /usr/local/bin/allinone
	RUN chmod +x /usr/local/bin/allinone
	
	CMD ["/usr/local/bin/allinone"]
	```

	2. 运行以下命令来构建

	```bash
	docker build -t allinone:latest .
	```

	3. 用命令行部署 或者用 docker-compose.yaml 文件 (推荐, 文件位置依然在该目录内), 然后用 `docker-compose up -d`

	```bash
	docker network create my-network
	
	docker run -d --restart unless-stopped --net=my-network --privileged=true -p 35455:35455 --name allinone allinone:latest
	```

	```yaml
	services:
	  allinone:
		    image: allinone:latest
		    container_name: allinone
		    privileged: true
		    restart: unless-stopped
		    ports:
		      - "35455:35455"
		    networks:
		      - my-network

		networks:
		  my-network:
			driver: bridge

	```

	4. 检查: 查看容器状态, 日志, 端口映射, 测试服务等

	```
	docker ps
	
	docker logs allinone
	
	netstat -tuln | grep 35455
	
	curl http://localhost:35455
	
	docker network ls
	docker network inspect my-network
	```

	5. 检查是否能下载列表:

	```bash
	wget http://127.0.0.1:35455/huyayqk.m3u

	```

### 3. 一些无关紧要的操作

1. 更改 docker 的镜像源: 在 [容器镜像服务 (aliyun.com)](https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors) 中有一个镜像源地址, 反正我也没有拉取成功过
2. av3a 推流工具, 好像是解决高清 4k 的问题的, 暂时没有用
