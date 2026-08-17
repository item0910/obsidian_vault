---
title: 专项技术_Grafana_01搭建grafana文档
date: 2026-03-15
categories: 工作记录
tags: 项目笔记/工作项目/智慧监盘 
author: 自己
---



## 一. 部署准备

### 1.1 虚拟机软件和 CentOS 镜像

这里用的是 virtualBox 软件, 镜像选择

[centos-7.9.2009-isos-x86_64安装包下载_开源镜像站-阿里云](https://mirrors.aliyun.com/centos/7.9.2009/isos/x86_64/?spm=a2c6h.25603864.0.0.733ef5adP9S4S5)

> [!note] 安装好后配置网络
> 为虚拟机设置两张网卡：
> 网卡 1 设置为网络地址转换（NAT）,实现虚拟机通过主机网络访问互联网；
> 网卡 2 设置为 host-only；实现主机与虚拟机互联,重启虚拟机；

命令试一试 ipconfig, ifconfig, ip addr
然后用 SecureCRT 连接一下虚拟机.

### 1.2 安装

#### 先安装其他依赖

yum, Docker, 改镜像源等等

[国内能用的Docker镜像源【2025最新持续更新】_docker 镜像-CSDN博客](https://blog.csdn.net/u014390502/article/details/143472743?spm=1001.2014.3001.5506)

#### 创建目录结构并设置权限

- Grafana

```bash
# 创建Grafana配置、插件及数据目录
sudo mkdir -p /etc/grafana/{plugins,data}

# 创建空配置文件（需自行填充配置内容）
sudo touch /etc/grafana/grafana.ini

# 设置目录所有权给Grafana用户（UID 472）
sudo chown -R 472:472 /etc/grafana
```

- Prometheus

```bash
# 创建Prometheus配置、规则、告警、数据及日志目录
sudo mkdir -p /etc/prometheus/{config,rules,alerts,data,logs}

# 创建空配置文件（需自行填充配置内容）
sudo touch /etc/prometheus/config/prometheus.yml
sudo touch /etc/prometheus/config/alertmanager.yml

# 设置目录权限（Prometheus默认使用nobody用户，UID 65534）
sudo chown -R 65534:65534 /etc/prometheus
sudo chmod -R 775 /etc/prometheus
```

- Pushgateway

```bash
# 创建Pushgateway数据目录（与Prometheus共享存储路径）
sudo mkdir -p /etc/prometheus/data

# 设置目录权限（Pushgateway默认使用nobody用户，UID 65534）
sudo chown 65534:65534 /etc/prometheus/data
sudo chmod 775 /etc/prometheus/data
```

#### 网络准备

```bash
# 创建Docker自定义网络
docker network create monitoring
```

#### 配置文件修改

- **Grafana**
   需手动填充 `/etc/grafana/grafana.ini` 或从容器中复制默认配置：

   ```bash
   docker run --rm grafana/grafana cat /etc/grafana/grafana.ini > /etc/grafana/grafana.ini
   ```

配置文件 1. `grafana.ini`

```ini
http_addr = 0.0.0.0

serve_from_sub_path = true


[smtp]
enabled = true
host = smtp.163.com:465
user = chen6762382@163.com
password = ***(网易云token)
from_address = chen6762382@163.com
from_name = Grafana

[security]
allow_embedding = true
enabled = true
enable_cors = true

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer   

[cors]
allow_origins = http://localhost:5173
allow_headers = Authorization,X-Grafana-Device-Id,X-Grafana-Org-Id,Content-Type
allow_methods = GET,POST,OPTIONS
```

- **Prometheus**
   需配置以下文件：

   - `/etc/prometheus/config/prometheus.yml` - 主配置文件
   - `/etc/prometheus/config/alertmanager.yml` - 告警管理器配置
   - `/etc/prometheus/rules/` - 存放告警规则文件（*.rules）
   - `/etc/prometheus/alerts/` - 存放告警模板文件（*.tmpl）

要在 `/etc/prometheus/prometheus.yml`

```yml
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pushgateway'
    static_configs:
      - targets: ['pushgateway:9091']
```

- 启动 Grafana 容器，映射端口 3000，配置文件挂载到容器内

```bash
docker run -d \
  --name grafana \
  --network monitoring \
  --restart=always \
  -p 3000:3000 \
  -v /etc/grafana/grafana.ini:/etc/grafana/grafana.ini \
  -v /etc/grafana/plugins:/var/lib/grafana/plugins \
  -v /etc/grafana/data:/var/lib/grafana \
  --user "472:472" \
  grafana/grafana
```

- 清理并重启

```bash
docker exec grafana rm -rf /var/lib/grafana/grafana.db
docker restart grafana
```

```bash
# 启动 Prometheus Push Gateway 容器，映射端口 9091，设置时区为上海
docker run -d \
  --name pushgateway \
  --network monitoring \
  --restart=always \
  -p 9091:9091 \
  -v /etc/prometheus/data:/data \
  -e TZ="Asia/Shanghai" \
  prom/pushgateway

```

```bash
# 启动 Prometheus 容器，映射端口 9090，配置文件和数据目录挂载，设置相关环境变量
docker run -d \
  --name prometheus \
  --network monitoring \
  --restart=always \
  -p 9090:9090 \
  -v /etc/prometheus/config/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v /etc/prometheus/data:/prometheus \
  -v /etc/prometheus/rules:/etc/prometheus/rules \
  -v /etc/prometheus/alerts:/etc/prometheus/alerts \
  -v /etc/prometheus/logs:/var/log/prometheus \
  -v /etc/prometheus/config/alertmanager.yml:/etc/prometheus/alertmanager.yml \
  -v /etc/hosts:/etc/hosts \
  -v /etc/hostname:/etc/hostname \
  -e "PROMETHEUS_USER=prometheus" \
  -e "PROMETHEUS_GROUP=prometheus" \
  --storage.tsdb.retention.size=10GB \
  prom/prometheus

```

- 清理并重启

```bash
# 进入 Prometheus 容器
docker exec -it prometheus rm -rf /prometheus/data/*

# 重启容器使生效
docker restart prometheus
```

这里有一个 `network`, 可以使三个服务在同一个网络, 方便以后的互通.

- prometheus.yaml

```yaml
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pushgateway'
    static_configs:
      - targets: ['pushgateway:9091']
```

正常部署的话, 可以看到 pushgateway 是 up 的状态

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740077734743.jpeg)

- *番外* postgres 的搭建

```bash
docker pull postgres:latest
```

```bash
mkdir -p ~/postgres-data
```

```bash
docker run -d \
  --name postgres \
  --network monitoring \
  --restart unless-stopped \
  -e POSTGRES_USER=grafana \
  -e POSTGRES_PASSWORD=grafana \
  -e POSTGRES_DB=grafana_db \
  -p 5432:5432 \
  -v ~/postgres-data:/var/lib/postgresql/data \
  postgres:latest
```


> [!note] 一个坑
> `- targets: ['172.19.0.3:9091']`
> 这一行, 也就是 pushgateway 的实际 ip, 最好要通过 `docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 4c5b39589a6c` 获得

ChatGPT 的解释

> [!note]
> ### 1. **`localhost` 或 `127.0.0.1` 在容器内的行为**
>
> - **容器内部网络**：每个 Docker 容器都有自己的网络命名空间。在容器内，`localhost` 和 `127.0.0.1` 仅指向容器自身，而不是宿主机或其他容器。也就是说，如果你在 Prometheus 容器内使用 `localhost` 或 `127.0.0.1` 来访问 Pushgateway，它实际上会尝试连接到自己容器内的服务，而不是宿主机或其他容器的服务。
>
> - **为什么 `localhost` 不行**：在你的配置中，Prometheus 容器试图通过 `localhost` 连接 Pushgateway，但 Pushgateway 可能在另一个容器中运行，而不是 Prometheus 容器内部，所以连接失败。
>
>
> ### 2. **宿主机 IP (`192.168.56.101`) 的问题**
>
> - **网络模式**：Docker 容器通常运行在桥接网络（`bridge`）模式中。在这种模式下，容器和宿主机虽然可以通信，但容器并不能直接使用宿主机的 `localhost` 地址进行访问。宿主机的 `localhost` 和容器的 `localhost` 是不同的，宿主机无法直接通过容器内部的 `localhost` 访问服务。
>
> - **为什么宿主机 IP 不行**：即使你使用宿主机的 IP（如 `192.168.56.101`），如果你的容器网络配置没有正确设置，或者网络隔离阻止了 Prometheus 容器访问宿主机服务，连接会失败。容器会通过 `bridge` 网络进行通信，但它不会自动知道宿主机的 IP，除非显式配置或连接到正确的网络。
>
>
> ### 3. **Docker 网络隔离**
>
> Docker 容器运行在隔离的网络环境中，默认情况下它们不会直接通过宿主机的 `localhost` 访问其他容器或宿主机的服务。容器通过 Docker 网络来通信，不同容器之间可以通过容器名称（如 `pushgateway`）来访问，而不是宿主机的 IP 或 `localhost`。
>
> - **正确的网络配置**：通过 `docker inspect` 获得容器的 IP 地址并直接在 Prometheus 配置文件中使用它，或者让所有相关容器（Prometheus 和 Pushgateway）在同一个 Docker 网络中运行，这样容器可以通过容器名称（如 `pushgateway`）来相互访问。

- 权限验证

```bash
# 检查Grafana目录权限
ls -ld /etc/grafana && ls -l /etc/grafana

# 检查Prometheus目录权限
ls -ld /etc/prometheus && ls -l /etc/prometheus
```

之后 docker ps 一下

## 二. 准备数据脚本

- 没有太多好说的, 为了数据美观, 异常数据和正常数据应该分割开一些

```python
import random
import time
import threading
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# 创建独立的注册器和指标
registry = CollectorRegistry()
g_normal = Gauge('random_value', 'Normal(2.1-2.2) or abnormal(0-0.1/5.1-5.2)', registry=registry)

# 初始化计数器
counter = 0

def log(message):
    print(f"[{time.ctime()}] {message}")

def generate_random_value():
    global counter
    while True:
        cycle_position = counter % 120
        
        if 0 <= cycle_position < 40 or 60 <= cycle_position < 100:
            value = random.uniform(2.1, 2.2)
            log(f"[Normal Cycle {counter//120}] Value: {value:.2f}")
            g_normal.set(value)
        else:
            if 40 <= cycle_position < 60:
                value = random.uniform(5.1, 5.2)
                log(f"[High Abnormal Cycle {counter//120}] Value: {value:.2f}")
            else:
                value = random.uniform(0.0, 0.1)
                log(f"[Low Abnormal Cycle {counter//120}] Value: {value:.2f}")
            g_normal.set(value)

        push_to_gateway('localhost:9091', job='random_value_job', registry=registry)
        time.sleep(5)
        counter += 1

if __name__ == "__main__":
    threading.Thread(target=generate_random_value).start()
    while True:
        time.sleep(1)
```

上下爬升的脚本

```
import random
import time
import threading
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# 创建独立的注册器和指标
registry = CollectorRegistry()
g_updown = Gauge('upDown', 'Gradual up/down pattern with maintenance', registry=registry)

# 初始化计数器
updown_counter = 0

def log(message):
    print(f"[{time.ctime()}] {message}")

def generate_up_then_down():
    global updown_counter
    while True:
        # Phase 1: 基础值
        for _ in range(10):
            value = random.uniform(2.1, 2.2)
            log(f"[UpDown Phase1] Baseline: {value:.2f}")
            g_updown.set(value)
            push_to_gateway('localhost:9091', job='upThenDownJob', registry=registry)
            time.sleep(5)

        # Phase 2: 线性上升
        current = 2.1
        for step in range(10):
            current += 0.59
            log(f"[UpDown Phase2] Rising step {step+1}: {current:.2f}")
            g_updown.set(current)
            push_to_gateway('localhost:9091', job='upThenDownJob', registry=registry)
            time.sleep(5)

        # Phase 3: 平台期
        for _ in range(20):
            value = 8.0 + random.uniform(-0.05, 0.05)
            log(f"[UpDown Phase3] Maintaining: {value:.2f}")
            g_updown.set(value)
            push_to_gateway('localhost:9091', job='upThenDownJob', registry=registry)
            time.sleep(5)

        # Phase 4: 线性下降
        current = 8.0
        for step in range(10):
            current -= 0.59
            log(f"[UpDown Phase4] Descending step {step+1}: {current:.2f}")
            g_updown.set(current)
            push_to_gateway('localhost:9091', job='upThenDownJob', registry=registry)
            time.sleep(5)

        # Phase 5: 恢复期
        for _ in range(10):
            value = random.uniform(2.1, 2.2)
            log(f"[UpDown Phase5] Recovery: {value:.2f}")
            g_updown.set(value)
            push_to_gateway('localhost:9091', job='upThenDownJob', registry=registry)
            time.sleep(5)

        updown_counter += 1

if __name__ == "__main__":
    threading.Thread(target=generate_up_then_down).start()
    while True:
        time.sleep(1)
```

启动所有脚本的 `start_all.sh`

```bash
#!/bin/bash
# 启动所有脚本并保留前台进程（防止 SecureCRT 退出时终止）
python3 topOnly_push.py &
python3 bottomOnly_push.py &
python3 topAndBottom_push.py &
python3 upDown_value_push.py &

# 保持脚本运行（防止退出）
wait
```

- 赋予一点权限

```bash
chmod +x start_all.sh
./start_all.sh
```

- 修改了一下格式

```bash
vi start_all.sh

# 进入 Vim 后输入以下命令：
:set ff=unix
:wq

# 再次运行脚本
./start_all.sh
```

## 三. Grafana 报警设置

### 1. 新建数据源

这里新建了一个 prometheus
![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078141346.jpeg)

### 2. 新建联络点

需要对 grafana.ini 做配置, 才能发送邮件

### 3. 新建仪表盘

选择查询和内置拉取周期
![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078286689.jpeg)

### 4. 新建警报

#### 4.1 query

警报名称不再赘述

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078386506.jpeg)

这里是建立一个查询

#### 4.2 建立一个规则表达式

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078479857.jpeg)

这里就是对 A 中的查询, 有一个判断

#### 4.3 归类警报

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078519189.jpeg)

警报标签

#### 4.4 设置 pending 周期和警报判断时间

如果 pending 超过了警报判断时间, 那么就是一次警报

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740078581158.jpeg)

#### 4.5 设置通知点, 消息和关联的 Pannel

## 三. 导出 Panel 和警报数据

### 1. Iframe 方式

```html
        <iframe
            src="http://192.168.56.101:3000/d-solo/fedi3z9hbw83ke/randomd?orgId=1&from=now-1h&to=now&timezone=browser&refresh=5s&panelId=1&__feature.dashboardSceneSolo"
            width="450"
            height="200"
            frameborder="0"
        ></iframe>

        <iframe
            src="http://192.168.56.101:3000/d-solo/fedi3z9hbw83ke/randomd?orgId=1&from=now-1h&to=now&timezone=browser&refresh=5s&panelId=2&__feature.dashboardSceneSolo"
            width="450"
            height="200"
            frameborder="0"
        ></iframe>
        <iframe
            src="http://192.168.56.101:3000/alerting/grafana/dedi8v3f3aps0b/view?tab=history"
            width="800"
            height="400"
            frameborder="0"
        ></iframe>
```

具体的参数应该可以再调整, 试

### 2. 导出 警报记录 (annotation api)

#### 2.1. 导出报警记录的 api

`/api/annotations?limit=100&matchAny=false&dashboardUID=fedi3z9hbw83ke`

- 可选参数看文档
[Annotations HTTP API | Grafana documentation](https://grafana.com/docs/grafana/latest/developers/http_api/annotations/)

#### 2. **过程中遇到的问题**

最重要的就是跨域问题

 ```javascript
//server.js
import express from 'express';
import axios from 'axios';

const app = express();
const PORT = 3001;

// 允许跨域请求
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'http://localhost:5173'); // 明确指定允许的源
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Authorization, X-Grafana-Device-Id, X-Grafana-Org-Id, Content-Type');
  res.header('Access-Control-Allow-Credentials', 'true'); // 允许携带凭据
  next();
});

// 转发请求到 Grafana API
app.get('/api/annotations', async (req, res) => {
  try {
    const response = await axios.get('http://192.168.56.101:3000/api/annotations', {
      params: req.query, // 传递查询参数
      headers: {
        'Authorization': 'Basic YWRtaW46cm9vdA==', // Basic Auth: admin:root (Base64 编码后)
        'X-Grafana-Device-Id': 'a69a6d1fdc8dffaa21f2061379a7aa10',
        'X-Grafana-Org-Id': '1',
      },
    });
    res.json(response.data); // 返回 Grafana 的响应数据
  } catch (error) {
    console.error('Failed to fetch annotations:', error);
    res.status(500).json({ error: 'Failed to fetch annotations' });
  }
});

// 启动服务
app.listen(PORT, () => {
  console.log(`中间服务运行在 http://localhost:${PORT}`);
}); 
```

```vue
//Grafana.vue
<template>
  <div>
    <h1>Embedded Grafana Dashboard</h1>
    <div v-for="panel in panels" :key="panel.id">
      <iframe
        :src="getPanelUrl(panel)"
        width="450"
        height="200"
        frameborder="0"
      ></iframe>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

// 定义 Grafana 面板的接口
interface Panel {
  id: number
  dashboardUid: string
  from: string
  to: string
  refresh: string
}

// 定义面板数据
const panels = ref<Panel[]>([
  {
    id: 1,
    dashboardUid: 'fedi3z9hbw83ke',
    from: 'now-1h',
    to: 'now',
    refresh: '5s',
  },
  {
    id: 2,
    dashboardUid: 'fedi3z9hbw83ke',
    from: 'now-1h',
    to: 'now',
    refresh: '5s',
  },
])

// 动态生成 iframe 的 URL
const getPanelUrl = (panel: Panel) => {
  return `http://192.168.56.101:3000/d-solo/${panel.dashboardUid}/randomd?orgId=1&from=${panel.from}&to=${panel.to}&timezone=browser&refresh=${panel.refresh}&panelId=${panel.id}&__feature.dashboardSceneSolo`
}
</script>

<style scoped>
iframe {
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 10px;
}
</style> 
```

两个的启动

```bash
npm run dev

node server.js
```

然后就能正常的获取 data 了

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740079437983.jpeg)

- 其他 nginx 设置之类, 不是很重要. 其中不同浏览器工具的调试方法, 比较重要.

## 四. 开发

### 常用网站

- API: [HTTP API | Grafana documentation](https://grafana.com/docs/grafana/latest/developers/http_api/) 
	- 中文: [grafana.org.cn](https://grafana.org.cn/docs/grafana/latest/developers/http_api/)
- PromSQL
	- [PromQL 查询之 rate 函数的使用-腾讯云开发者社区-腾讯云](https://cloud.tencent.com/developer/article/1891190)

## 五. Issues

### 1. Prometheus 提示时间不同步

![](附件/image/专项技术_Grafana_01搭建grafana文档-1740788033550.jpeg)

手动同步时间

```bash
sudo ntpdate -u ntp.aliyun.com
```

```bash
sudo chronyc -a makestep
```

```bash
# 2. 关闭自动NTP同步
sudo timedatectl set-ntp false

# 3. 手动设置时间（替换为实际时间）
sudo timedatectl set-time "2025-3-19 08:57:33"
```

```bash
sudo systemctl restart chronyd
```

确认命令:
- `timedatectl`

### 2. 跨域

前端或者浏览器发出请求时, 有跨域问题

1. 用 `server.js` 封装请求

```js
//server.js
import express from 'express';
import axios from 'axios';

const app = express();
const PORT = 3001;

// 允许跨域请求
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'http://localhost:5173'); // 明确指定允许的源
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Authorization, X-Grafana-Device-Id, X-Grafana-Org-Id, Content-Type');
  res.header('Access-Control-Allow-Credentials', 'true'); // 允许携带凭据
  next();
});

// 转发请求到 Grafana API
app.get('/api/annotations', async (req, res) => {
  try {
    const response = await axios.get('http://192.168.56.101:3000/api/annotations', {
      params: req.query, // 传递查询参数
      headers: {
        'Authorization': 'Basic YWRtaW46cm9vdA==', // Basic Auth: admin:root (Base64 编码后)
        'X-Grafana-Device-Id': 'a69a6d1fdc8dffaa21f2061379a7aa10',
        'X-Grafana-Org-Id': '1',
      },
    });
    res.json(response.data); // 返回 Grafana 的响应数据
  } catch (error) {
    console.error('Failed to fetch annotations:', error);
    res.status(500).json({ error: 'Failed to fetch annotations' });
  }
});

// 启动服务
app.listen(PORT, () => {
  console.log(`中间服务运行在 http://localhost:${PORT}`);
}); 
```

