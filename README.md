# 🔥 hot-tools-tweet

<p align="center">
  <img src="https://img.shields.io/badge/status-active-success" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/Hermes-skill-8A2BE2" alt="Hermes Skill">
  <img src="https://img.shields.io/badge/language-简体中文-red" alt="Language">
</p>

<p align="center">
  <b>发现热门实用工具 → 写成中文教程推文 → 自动推送到 Telegram</b>
</p>

---

## 这是什么

一个运行在 Hermes Agent 上的自动化技能，每天三次从 GitHub Trending、Hacker News、Twitter/Surf 等信源采集当下最火的实用工具，用真人风格的中文写成带完整使用教程的推文，自动推送到 Telegram 频道或私聊。

### 不限于 AI

视频下载器、文件转换、PDF 工具、Git 客户端、语音克隆、截图工具、终端美化……**什么好用推什么**。唯一标准：普通人能懂能用。

### 和普通工具推荐号的区别

| | 普通推荐号 | hot-tools-tweet |
|---|---|---|
| 选题 | 编辑主观判断 | 多信源交叉验证 + 热度阈值 |
| 内容 | 标题+介绍 | 安装命令 + 操作步骤 + 排坑 |
| 频率 | 不固定 | 每天 3 次，早9/午2/晚8 |
| 语言 | 营销味 | 真人风格，禁止 AI 八股词 |
| 去重 | 无 | 永久去重 + 24h 重复降权 |

## 效果示例

```
🔧 VoiceBox — 免费开源的语音克隆，ElevenLabs 的平替

想克隆自己的声音做播客或视频配音？VoiceBox 用浏览器就能跑，
不需要 GPU，支持中英日韩等 15 种语言，克隆效果接近 ElevenLabs。

安装：
  git clone https://github.com/shang-zhu/voicebox
  cd voicebox && pip install -r requirements.txt
  python app.py

然后浏览器打开 http://localhost:7860，上传 30 秒音频样本就能克隆。
常见坑：首次启动会下载约 2GB 模型文件，建议挂代理。

github.com/shang-zhu/voicebox
先收藏，需要的时候直接用。
```

## 目录结构

```
hot-tools-tweet/
├── SKILL.md                   # Hermes 技能定义（核心）
├── README.md                  # 项目说明
├── .gitignore
├── scripts/
│   └── ai_content_scout.py   # 信源采集脚本
├── examples/
│   └── sample-tweets.md      # 更多推文示例
├── references/
│   └── gateway-proxy-fix.md  # Gateway 代理修复指南
└── .github/
    └── workflows/
        └── validate-skill.yml # CI：自动校验 SKILL.md
```

## 选材标准

三条硬门槛，缺一不可：

- **够火** — GitHub 50+ 星、Twitter/Surf 20+ 互动、HN 50+ 分
- **能用** — 普通人能直接上手，不推架构/框架/论文
- **有教程** — 每条必须带安装命令 + 操作步骤 + 常见坑修复

## 信源 & 采集

| 信源 | 方法 | 特点 |
|---|---|---|
| GitHub Trending | Search API, 7天内 | AI 标签项目为主 |
| Hacker News | Firebase API, Top 80 | 关键词过滤 AI 相关 |
| Twitter / Surf | Surf CLI 社交搜索 | 消费级工具发现最佳渠道 |

采集脚本 `scripts/ai_content_scout.py` 每次运行：
1. 从四个信源拉取最新内容
2. 去重（已推送的永久排除）
3. 24h 内重复出现降权（第2次打6折、第3次打3折）
4. 输出 JSON 给 Agent 做最终筛选和写作

```bash
python3 scripts/ai_content_scout.py
```

## 推文规范

加载 `human-social-copy` 技能保证写作风格，额外规则：

- **必须有链接** — 推文末尾必须有 GitHub/官网 URL
- **不提数据** — 不说"xxx星"、"xxx赞"，但链接本身必须保留
- **中英文不空格** — AI工具、GitHub项目、macOS系统
- **禁止 AI 八股** — 旨在、赋能、打造、范式……通通不用

详见 `SKILL.md` 的完整写作规范。

## 安装

### 前置

- Python 3.11+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) 已安装
- Telegram Bot 已配置
- Surf CLI（社交信源采集，可选）

### 步骤

```bash
# 1. 安装依赖
pip install requests PySocks

# 2. 安装技能到 Hermes
cp -r hot-tools-tweet ~/.hermes/skills/social-media/

# 3. 安装配套技能
hermes skills install human-social-copy

# 4. 创建数据文件
echo '[]' > ~/.hermes/scripts/posted_urls.json
echo '{}' > ~/.hermes/scripts/candidate_history.json
```

## 定时任务

已配置三个 cron 任务，每天自动执行：

| 时间 | Job ID | 说明 |
|---|---|---|
| 09:00 | `73cee23a3ad6` | 早间推文 |
| 14:00 | `bd08c51805ec` | 午间推文 |
| 20:00 | `67d82f985d40` | 晚间推文 |

```bash
# 查看全部 cron 任务
hermes cron list

# 手动触发某次推送
hermes cron run 73cee23a3ad6
```

## 依赖技能

- **hot-tools-tweet** — 选题 + 采集 + 结构（本项目）
- **human-social-copy** — 真人风格中文写作

## 贡献

欢迎提交 PR 改进采信源关键词、推文模板或筛选逻辑。

1. Fork 本项目
2. 修改 `SKILL.md` 或 `scripts/ai_content_scout.py`
3. 提交 PR 到 `main` 分支

CI 会自动校验 SKILL.md 格式。

## 许可

MIT © 2026 [0xMulight](https://github.com/0xMulight)
