# AGENTS.md — 任何 AI Agent 可用

将此文件放入项目根目录，任何支持 AGENTS.md 的 coding agent（Claude Code、Codex、OpenCode、Cursor 等）在打开项目时会自动读取。

## 项目概述

自动发现热门实用工具 → 写成中文教程推文 → 推送到 Telegram 的自动化流水线。

## 工作流程

### 1. 采集

```bash
cd scripts && python3 ai_content_scout.py
```

从 GitHub Trending / Hacker News / Surf 社交采集热门工具，输出 JSON，自动去重 + 24h 重复降权。

### 2. 筛选

读取脚本输出的 JSON，用以下标准筛选：

- GitHub 50+ 星、Twitter/Surf 20+ 互动、HN 50+ 分
- 必须是个人用户能直接用的工具（不推框架/架构/论文）
- 排除 `scripts/../posted_urls.json` 中已推送的

### 3. 写作

读 `SKILL.md` 获取完整写作规范。核心规则：

- **结构**：钩子 → 价值 → 安装教程 → 链接 → 软 CTA
- **必须有链接**：推文末尾 GitHub/官网 URL，独立一行
- **不提平台数据**：不说"xxx星""xxx赞"
- **中英文不空格**：AI工具、GitHub项目
- **禁止 AI 八股**：旨在、赋能、打造、范式等不用
- **参考**：`examples/sample-tweets.md` 有范文

### 4. 推送

```python
import requests
session = requests.Session()
session.proxies = {"http": "socks5h://172.26.0.1:10808", "https": "socks5h://172.26.0.1:10808"}
session.post(
    "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage",
    json={"chat_id": "<CHAT_ID>", "text": tweet_text},
    timeout=20
)
```

推送后把工具 URL 追加到 `posted_urls.json`。

## 配置文件

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 完整写作规范、选材标准、信源关键词 |
| `examples/sample-tweets.md` | 三条范文 + 结构拆解 |
| `scripts/ai_content_scout.py` | 采集脚本 |
| `scripts/posted_urls.json` | 已推送 URL（运行时生成） |
| `scripts/candidate_history.json` | 候选历史（运行时生成） |

## 依赖

```bash
pip install requests PySocks
# Surf CLI（可选，社交信源）
```

## 定时推送

Hermes Agent 用户配置 cron：

```bash
hermes cron create "0 9,14,20 * * *" \
  --prompt "运行 ai_content_scout.py，筛选热门工具，写中文教程推文，推送到 Telegram" \
  --skill hot-tools-tweet --skill human-social-copy \
  --deliver telegram:5775842537
```

其他 agent 用户配置系统 cron 或 CI schedule。

## 代理

WSL 环境下需要 SOCKS5 代理访问 Telegram API：

```bash
export all_proxy=socks5h://172.26.0.1:10808
```

非 WSL 环境可跳过。
