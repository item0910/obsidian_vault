---
title: Step01_环境安装和Maven配置
date: 2025-01-12
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘
author: 自己
---

## 1. 安装环境

### 后端

- 工具
	- DBeaver 数据库链接工具
	- RedisClient redis 链接工具
	- IDEA 社区版
	- Maven
	- JDK
	- npp
	- openVPN
	- PostMan
- 代码和配置文件
	- Maven xml 文件
	- Maven 本地仓库 (从公司机拉取之后)
	- dev -> dip-demo-java
	- 数据库链接地址 (需要 vpn 链接)

### 前端

- 工具
	- VScode
		- extensions, 在 user, admin,.vscode 文件夹内
	- node.js
		- 需要调整库的获取位置, 或者直接拖 modules

## 2. Demo 理解

- 项目结构

```menu.txt
dip-demo-java (根目录)
├── config
│   └── manifests
│       └── deployment.yaml
├── dip-demo-api
│   └── src/main/java/com/cnnp/dip/demo/model
│       ├── DemoRequest.java
│       └── DemoResponse.java
├── dip-demo-boot
│   └── src/main/
│       ├── java/com/cnnp/dip/demo
│       │   └── Bootstrap.java
│       └── resources
│           ├── application.yaml
│           ├── bootstrap.yaml
│           ├── logback-spring.xml
│           └── META-INF/app.properties
├── dip-demo-business
│   └── src/main/
│       ├── java/com/cnnp/dip/demo
│       │   ├── dal
│       │   │   ├── dto/DemoDto.java
│       │   │   ├── entity/DemoDo.java
│       │   │   ├── mapper/DemoMapper.java
│       │   │   └── vo/DemoVo.java
│       │   └── service
│       │       ├── IDemoService.java
│       │       └── impl/DemoServiceImp.java
│       └── resources/mapper
│           └── DemoMapper.xml
├── dip-demo-present
│   └── src/main/java/com/cnnp/dip/demo/service/demo
│       └── DemoService.java
├── pom.xml (父pom)
└── .gitlab-ci.yml


```

- 区分 DO, DTO, VO
	- DO: 一个数据库对应一个 DO
	- DTO: Service 需要的封装结构, 可能由多个 DO 组合而成
	- VO: 返回需要的 VO
- present 层
	- 实际上就是 controller 层, 但是区别于 API, 其可能包含具体的 advice, 逻辑处理等切面, 算是更详细的接口.

## 问题以及解决

### Maven 的 xml 文件问题

最初的 xml 文件, 比较粗犷的把 xml 文件设置了一个 `*` 在 `http://test.cnnp.com.cn:8080/nexus/` 来进行依赖拉取, 发现有依赖获取的位置问题

#### 问题解决

```xml
<mirrors>
    <mirror>
      <id>rdc-releases</id>
      <mirrorOf>rdc-releases</mirrorOf>
      <name>Human Readable Name for this Mirror.</name>
      <url>http://test.cnnp.com.cn:8080/nexus/repository/maven-public/</url>
    </mirror>
    <mirror>
      <id>maven-snapshots</id>
      <mirrorOf>maven-snapshots</mirrorOf>
      <name>Human Readable Name for this Mirror.</name>
      <url>http://test.cnnp.com.cn:8080/nexus/repository/maven-central/</url>
    </mirror>
  <mirror>
      <id>com.cnnp</id>
      <mirrorOf>dip-snapshots</mirrorOf>
      <name>com.cnnp</name>
      <url>http://test.cnnp.com.cn:8080/nexus/repository/dip-snapshots/</url>
   </mirror>

  <mirror>
      <id>com.cnnp</id>
      <mirrorOf>dip-releases</mirrorOf>
      <name>com.cnnp</name>
      <url>http://test.cnnp.com.cn:8080/nexus/repository/dip-releases/</url>
    </mirror>
  </mirrors>
```

#### Maven 读取 config 的机制, 以及给项目单独配置 xml 文件的方法

Maven 的一个重要特性，让我来解释下原理：
1. **Maven 构建工具的配置加载顺序**：
    - Maven 启动时会按以下优先级加载配置：
        1. 命令行参数 (`mvn -s /path/to/settings.xml`)
        2. 项目级配置 (`.mvn/*`)
        3. 用户级配置 (`~/.m2/settings.xml`)
        4. 全局配置 (`$MAVEN_HOME/conf/settings.xml`)
2. **`.mvn` 目录的特殊性**：
    - Maven 3.3.1+ 版本引入了 `.mvn` 机制
    - Maven 会自动识别项目根目录下的 `.mvn` 目录
    - 这个目录中的配置文件优先级高于用户级和全局配置
3. **配置文件的作用**：
    项目根目录/
    └──.mvn/
        ├── jvm.config     # JVM 参数配置
        ├── maven.config   # Maven 命令行参数
        └── settings.xml   # Maven 仓库和构建配置

    - `jvm.config`: 配置 Maven 运行时的 JVM 参数
    - `maven.config`: 相当于预设的命令行参数
    - `settings.xml`: 项目特定的 Maven 配置

4. **工作流程**：

    1. Cursor（或其他 IDE）调用 Maven 时，会先检测项目根目录
    2. 发现 `.mvn` 目录后，自动加载其中的配置
    3. 使用这些配置覆盖默认的 Maven 设置
    4. 然后再执行具体的 Maven 命令

这种机制的好处是：

- 配置跟随项目
- 不同项目可以有不同配置
- 团队成员可以共享相同的构建环境
- 不会影响其他项目的 Maven 配置

### VSCode extension 读不出来的问题

extension 单个挪到 `C:\Users\admin\.vscode\extensions`

### 缺少测试环境的问题

要注意保留开发环境, 有时候有用

## Maven

