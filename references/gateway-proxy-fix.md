# Gateway 代理与 TG 投递问题

## 问题现象

Cron 任务生成了推文但 TG 投递报 `Timed out`。

## 根因

Gateway 进程没有 `all_proxy` 环境变量，TG API 直连被 DNS 污染导致超时。

WSL 环境必须通过 `socks5h://172.26.0.1:10808` 代理访问 Telegram API。

## 排查步骤

```bash
# 1. 找到 gateway 进程
ps aux | grep "hermes gateway run"

# 2. 检查进程是否有代理环境变量（用实际PID替换）
cat /proc/<PID>/environ | tr '\0' '\n' | grep -i proxy

# 3. 如果没有输出，说明代理未注入
```

## 修复方法

Gateway 必须通过 `start_gateway.sh` 启动以注入代理：

```bash
# 停掉旧 gateway
kill <GATEWAY_PID>

# 用脚本重启（已预设代理环境变量）
bash ~/.hermes/start_gateway.sh
```

## 验证

```bash
# 确认新 gateway 进程有代理
cat /proc/$(pgrep -f "hermes gateway run")/environ | tr '\0' '\n' | grep -i proxy
# 应输出: all_proxy=socks5h://172.26.0.1:10808
```

## 手动推送测试（绕过 gateway）

如果 gateway 未修复，可临时用 Python 直发：

```python
import requests
session = requests.Session()
session.proxies = {"http": "socks5h://172.26.0.1:10808", "https": "socks5h://172.26.0.1:10808"}
session.post("https://api.telegram.org/bot<TOKEN>/sendMessage",
             json={"chat_id": "5775842537", "text": "test"}, timeout=20)
```
