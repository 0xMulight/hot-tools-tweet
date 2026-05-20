---
name: hot-tools-tweet
description: "发现推特上火起来的实用工具，写成带教程的中文推文，推送到 Telegram。不限品类：AI工具、视频下载器、Git客户端、白嫖神器，只要是普通人能懂能用的都行。"
version: 1.2.0
author: 0xMulight
metadata:
  hermes:
    tags: [twitter, tools, tweet, chinese, social-media, tutorial]
    category: social-media
    triggers:
      - "写工具推文"
      - "推一个工具"
      - "找热门工具"
      - "采集工具"
      - "hot tools"
      - "工具推荐"
      - "tools tweet"
---


## 仓库结构

```
hot-tools-tweet/
├── SKILL.md                   # Hermes 技能定义（本文件）
├── README.md                  # 项目说明
├── .gitignore
├── scripts/
│   └── ai_content_scout.py   # 信源采集脚本
├── examples/
│   └── sample-tweets.md      # 推文示例
├── references/
│   └── gateway-proxy-fix.md  # Gateway 代理修复
└── .github/
    └── workflows/
        └── validate-skill.yml # CI 自动校验 SKILL.md 格式
```

# Hot Tools Tweet — 热门工具推文

寻找推特上火起来的实用工具，写成带使用教程的中文推文，推送到 Telegram。

## 选材标准

- 不限品类：AI工具、视频下载器、文件转换、Git客户端、PDF工具、白嫖神器、语音克隆、提效工具……什么好用推什么，**不是非要AI**
- 必须是"大火"的工具：GitHub 50+ 星（7天内）、Twitter/Surf 20+ 互动（likes + reposts×3）、HN 50+ 分 Show HN
- **普通人能懂能用**：不推架构/框架/论文/企业级平台/观点文章，只推个人用户能直接上手的东西
- 每条必须带使用教程：安装命令、操作步骤、常见坑修复
- **不提平台数据**：不说"HN上xxx赞"、"Twitter上xxx互动"，直接讲工具本身

## 优先选题：主流 Agent 生态工具

以下生态的工具享有**选题优先权**，在评分相近时优先入选：

| 生态 | 覆盖范围 |
|---|---|
| **Hermes** | skills、plugins、MCP 服务器、agent 配置工具、工作流工具 |
| **Codex** | CLI 工具、SDK、VSCode 扩展、工作流集成 |
| **Claude Code** | hooks、skills、MCP 工具、agent 编排 |
| **Cursor** | rules、扩展、工作区工具 |
| **Copilot** | 扩展、agent 模式工具、VSCode 集成 |
| **通用 Agent 工具** | MCP 服务器、agent 记忆工具、多 agent 编排、自主 agent 框架 |

### 判定标准

- 工具名称或 README 中明确提到上述 agent 名称
- 工具的核心功能是增强某个 agent 的能力（如添加新工具、优化上下文、持久化记忆）
- MCP 服务器只要实用、有明确 agent 集成路径即可入选

### 不选的内容

- 不知名的 agent 项目（没有 GitHub 星或社区讨论）
- 纯论文、架构设计、概念验证（没有可执行的代码）
- 仅支持某个小众 agent / 已停止维护的项目

## 信源优先级

消费级工具按此优先级搜索：

1. **Twitter/Surf social** — 最佳消费级工具发现渠道。关键词组见下方，engagement ≥20
2. **Hacker News** — Show HN + 工具关键词，score ≥50
3. **GitHub Search API** — 偏向开发者工具，AI/工具类 repo，stars ≥50，7天内

### 关键词组

```
"free tool github useful"
"free alternative to paid tool"  
"开源 免费 工具 好用"
"useful free app tool 2026"
"白嫖 免费 工具"
"file converter tool free"
"pdf tool free open source"
```

### 去重

- `posted_urls.json` — 已推送URL永久排除
- `candidate_history.json` — 24小时内重复出现降权：第2次60%、第3次30%、第4次+10%

### 执行命令

```bash
cd ~/.hermes/scripts && python3 ai_content_scout.py
```

## 推文写作规范

加载 `human-social-copy` 技能作为写作基座，额外叠加以下规则：

### 🔴 强制要求：GitHub/官方链接（CRITICAL）

**每条推文末尾必须包含工具的 GitHub 链接或官方渠道 URL。**

- 链接以独立一行放在推文最末尾，CTA 之前或之后都可以
- 格式示例：`github.com/作者/项目名`
- 不要放裸域名，要放完整可点击的 URL
- 先放链接，再放轻 CTA

正确示例：
```
github.com/shang-zhu/violin
先收藏，需要的时候直接用。
```

错误示例（没有链接）：
```
用 uv tool install violin 就能装，支持33种语言。
先收藏备用。
```

⚠️ **"不提平台数据"仅指不提 star 数、点赞数等数字指标。GitHub 链接本身不受此限制，必须保留。**

### 推文结构

1. 钩子：一句话说清这是什么、为什么值得关注
2. 价值：这工具能干什么，解决什么问题
3. 教程：安装命令+操作步骤+常见坑修复（必须有）
4. **🔗 链接：GitHub 或官方渠道 URL（必须，独立一行）**
5. 软CTA：收藏/试用/分享

### 禁止项

- 不提平台数据指标（"HN上xxx赞"、"GitHub xxx星"、"Twitter上xxx互动"），但 GitHub 链接本身必须保留
- 不写观点评论文章，只写工具
- 不用括号
- 不用 human-social-copy 的 banned words（旨在、赋能、打造、范式、这种、硬生生、扒、助力、路径、逻辑、痛点、说白了、护城河）
- 不用 "不是...而是..." 句式
- 中英文之间不留空格（AI工具、GitHub项目、macOS系统）

### 推送前自检清单

在生成最终推文文本后，逐条检查：

- [ ] 推文末尾有 GitHub 链接或其他官方 URL（如非 GitHub 项目，也必须有一个可访问的官网链接）
- [ ] 没有"xxx星"、"xxx赞"等平台数据指标
- [ ] 没有括号
- [ ] 没有 banned words
- [ ] 中英文无空格

### 教程要求

- 每个平台的安装命令都给全（macOS/Windows/Linux）
- 常见报错附修复命令
- 步骤用数字序号，不用括号

## 推送

```python
import requests
session = requests.Session()
session.proxies = {
    "http": "socks5h://172.26.0.1:10808",
    "https": "socks5h://172.26.0.1:10808",
}
session.post(
    "https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": "5775842537", "text": text},
    timeout=20,
)
```

推送成功后立即将URL追加到 `~/.hermes/scripts/posted_urls.json`。

## 定时任务

已配置3个 cron 任务，均使用此技能：

| 时段 | Job ID | Cron | 投递 |
|------|--------|------|------|
| 早9点 | 73cee23a3ad6 | 0 9 * * * | origin + TG |
| 下午2点 | bd08c51805ec | 0 14 * * * | origin + TG |
| 晚8点 | 67d82f985d40 | 0 20 * * * | origin + TG |

## 参考案例

- VoiceBox：免费语音克隆，替代ElevenLabs，26494星
- Media Downloader：macOS视频下载器，支持1000+网站，867星
- Rebased：JetBrains Git客户端开源替代，3427星

## 常见问题

**TG投递超时**：Gateway 进程缺少代理环境变量。详见 `references/gateway-proxy-fix.md`。
