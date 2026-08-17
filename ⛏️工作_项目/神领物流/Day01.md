## 问题

### 登不上虚拟机的 git

在登录 [http://git.sl-express.com/](http://git.sl-express.com/) 时, 发现登不上

#### 解决方法

关掉 clash

### 留档需要经常查看的服务账号密码

需要经常查看账号密码

#### 解决方法

| 名称         | 地址                                                                                                                       | 用户名/密码         | 端口    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ | -------------- | ----- |
| git        | [http://git.sl-express.com/](http://git.sl-express.com/)                                                                 | sl/sl123       | 10880 |
| maven      | [http://maven.sl-express.com/nexus/](http://maven.sl-express.com/nexus/)                                                 | admin/admin123 | 8081  |
| jenkins    | [http://jenkins.sl-express.com/](http://jenkins.sl-express.com/)                                                         | root/123       | 8090  |
| 权限管家       | [http://auth.sl-express.com/api/authority/static/index.html](http://auth.sl-express.com/api/authority/static/index.html) | admin/123456   | 8764  |
| RabbitMQ   | [http://rabbitmq.sl-express.com/](http://rabbitmq.sl-express.com/)                                                       | sl/sl321       | 15672 |
| MySQL      | -                                                                                                                        | root/123       | 3306  |
| nacos      | [http://nacos.sl-express.com/nacos/](http://nacos.sl-express.com/nacos/)                                                 | nacos/nacos    | 8848  |
| neo4j      | [http://neo4j.sl-express.com/browser/](http://neo4j.sl-express.com/browser/)                                             | neo4j/neo4j123 | 7474  |
| xxl-job    | [http://xxl-job.sl-express.com/xxl-job-admin](http://xxl-job.sl-express.com/xxl-job-admin)                               | admin/123456   | 28080 |
| EagleMap   | [http://eaglemap.sl-express.com/](http://eaglemap.sl-express.com/)                                                       | eagle/eagle    | 8484  |
| seata      | [http://seata.sl-express.com/](http://seata.sl-express.com/)                                                             | seata/seata    | 7091  |
| Gateway    | [http://api.sl-express.com/](http://api.sl-express.com/)                                                                 | -              | 9527  |
| admin      | [http://admin.sl-express.com/](http://admin.sl-express.com/)                                                             | -              | 80    |
| skywalking | [http://skywalking.sl-express.com/](http://skywalking.sl-express.com/)                                                   | -              | 48080 |
| Redis      | -                                                                                                                        | 123321         | 6379  |
| MongoDB    | -                                                                                                                        | sl/123321      | 27017 |

### 本地没有 docker image

`Unable to find image 'sl-express-gateway:1.1-SNAPSHOT' locally`

#### 解决方法: 修改 docker 加速器地址

[关于神领物流中部署后台web服务出现的错误_unable to find image 'sl-express-ms-web-manager:1.-CSDN博客](https://blog.csdn.net/CSDN_xiaoyueyue/article/details/142315920)

```bash
 sudo vim /etc/docker/daemon.json
 ```

```
{
 
    "registry-mirrors": ["https://shgtk489.mirror.aliyuncs.com", 
            "https://dockerproxy.com", 
            "https://mirror.baidubce.com", 
            "https://docker.m.daocloud.io", 
            "https://docker.nju.edu.cn", 
            "https://docker.mirrors.sjtug.sjtu.edu.cn", 
            "https://registry.docker-cn.com", 
            "http://hub-mirror.c.163.com", 
            "https://docker.mirrors.ustc.edu.cn", 
            "https://docker.120322.xyz"]
 
}
```

```重启Docker
sudo systemctl restart docker
```

### 显示问号

[centos7中文显示问号_mob6454cc67bcfb的技术博客_51CTO博客](https://blog.51cto.com/u_16099209/12724085)

SecureCRT: 会话字体选择为黑体

### Git 拉取单个项目

在 Idea 里 new, 选择从 Git new 出来

### 各种依赖冲突

修改maven的settings.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings
        xmlns="http://maven.apache.org/SETTINGS/1.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

    <!-- 本地仓库 -->
    <localRepository>C:\shenlingMavenRepo</localRepository>

    <!-- 配置私服中deploy的账号 -->
    <servers>
        <server>
            <id>sl-releases</id>
            <username>deployment</username>
            <password>deployment123</password>
        </server>
        <server>
            <id>sl-snapshots</id>
            <username>deployment</username>
            <password>deployment123</password>
        </server>
    </servers>

    <!-- 使用阿里云maven镜像，排除私服资源库 -->
    <mirrors>
        <mirror>
            <id>mirror</id>
            <mirrorOf>central,jcenter,!sl-releases,!sl-snapshots</mirrorOf>
            <name>mirror</name>
            <url>https://maven.aliyun.com/nexus/content/groups/public</url>
			<blocked>false</blocked>
        </mirror>
		  <mirror>
			<id>sl-snapshots</id>
			<mirrorOf>sl-snapshots</mirrorOf>
			<url>http://maven.sl-express.com/nexus/content/repositories/snapshots/</url>
			<blocked>false</blocked>
		  </mirror>
		  <mirror>
			<id>sl-releases</id>
			<mirrorOf>sl-releases</mirrorOf>
			<url>http://maven.sl-express.com/nexus/content/repositories/releases/</url>
			<blocked>false</blocked>
		  </mirror>
    </mirrors>

    <profiles>
        <profile>
            <id>sl</id>
            <!-- 配置项目deploy的地址 -->
            <properties>
                <altReleaseDeploymentRepository>
                    sl-releases::default::http://maven.sl-express.com/nexus/content/repositories/releases/
                </altReleaseDeploymentRepository>
                <altSnapshotDeploymentRepository>
                    sl-snapshots::default::http://maven.sl-express.com/nexus/content/repositories/snapshots/
                </altSnapshotDeploymentRepository>
            </properties>
            <!-- 配置项目下载依赖的私服地址 -->
            <repositories>
                <repository>
                    <id>sl-releases</id>
                    <url>http://maven.sl-express.com/nexus/content/repositories/releases/</url>
                    <releases>
                        <enabled>true</enabled>
                    </releases>
                    <snapshots>
                        <enabled>false</enabled>
                    </snapshots>
                </repository>
                <repository>
                    <id>sl-snapshots</id>
                    <url>http://maven.sl-express.com/nexus/content/repositories/snapshots/</url>
                    <releases>
                        <enabled>false</enabled>
                    </releases>
                    <snapshots>
                        <enabled>true</enabled>
                    </snapshots>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
         <!-- 激活配置 -->
        <activeProfile>sl</activeProfile>
    </activeProfiles>

</settings>
```
最后完成了依赖管理

进度Day01-20