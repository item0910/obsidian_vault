---
title: 项目笔记——Hexo_05域名SSL证书
date: 2024-11-14
categories: 博客
tags: 项目笔记/日常态项目/Hexo
author: 自己
mtime: 2024-11-14
---

- 链接:

# Certbot SSL 证书自动更新和手动更新

## 1. Certbot 安装和版本验证

要确认 Certbot 是否正常安装并运行，可以通过以下命令检查版本：

```bash
certbot --version
```

输出示例：

```
certbot 1.22.0
```

如果输出类似上面内容，说明 Certbot 安装正常。

## 2. 查看当前证书状态

要查看 Certbot 管理的证书信息，可以使用以下命令：

```bash
certbot certificates
```

输出示例：

```
Found the following certs:
  Certificate Name: www.itemchen.com
    Domains: itemchen.com www.itemchen.com
    Expiry Date: 2025-02-12
    Certificate Path: /etc/letsencrypt/live/www.itemchen.com/fullchain.pem
    Private Key Path: /etc/letsencrypt/live/www.itemchen.com/privkey.pem
```

这将列出 Certbot 当前管理的所有证书，包括到期时间、路径等信息。

## 3. 测试自动更新功能

要测试 Certbot 的自动更新功能是否正常工作，可以运行以下命令进行模拟续订：

```bash
sudo certbot renew --dry-run
```

如果一切正常，输出会显示类似如下内容：

```
Congratulations, all simulated renewals succeeded
```

这表示自动更新配置无误，并且可以顺利进行证书续订。

## 4. 手动更新证书

如果你想手动更新证书，即使证书尚未到期，可以使用以下命令：

```bash
sudo certbot renew
```

这将会检查所有证书，并在有需要时进行更新。即使证书没有到期，也不会做出多余的操作，只会更新过期的证书。

如果需要确保立即使用新的证书，可以手动重载 Nginx：

```bash
sudo systemctl reload nginx
```

## 5. 自动更新配置

Certbot 会在证书到期前自动更新。为了确保每隔一段时间自动检查并更新证书，可以设置 cron 任务：

```bash
sudo crontab -e
```

添加:

```bash
0 */12 * * * certbot renew --post-hook "systemctl reload nginx"
```

这会每 12 小时检查一次证书，并在成功续订后重载 Nginx 服务以应用新证书。

## 6. 证书更新成功示例

运行 `certbot certificates` 命令后，可以看到证书的有效期已经延长。例如：

```
Expiry Date: 2025-02-12 (VALID: 89 days)
```

这表示证书更新成功。

---

通过这些步骤，你可以确保你的 SSL 证书始终处于最新状态，无需手动干预。Certbot 会自动管理证书更新，并通过 Nginx 自动应用新的证书。
