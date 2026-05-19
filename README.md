# hot-tools-tweet

发现推特上火起来的实用工具，写成带教程的中文推文，推送到 Telegram。

不限品类：AI工具、视频下载器、Git客户端、文件转换、PDF工具、白嫖神器、语音克隆……什么好用推什么。

## 选材标准

- GitHub 50+ 星、Surf/Twitter 20+ 互动、HN 50+ 分
- 普通人能懂能用，不推架构、框架、论文
- 每条必须带安装命令 + 操作步骤 + 常见坑修复

## 推文结构

1. 钩子 — 一句话说清这是什么
2. 价值 — 能干什么，解决什么问题
3. 教程 — 安装命令 + 使用步骤 + 排坑
4. 链接 — GitHub 或官方 URL
5. 软CTA — 收藏/试用

## 信源

- Twitter / Surf 社交
- Hacker News Show HN
- GitHub Trending

## 安装

把目录放到 Hermes Agent 的 skills 下：

    cp -r hot-tools-tweet ~/.hermes/skills/social-media/

配合 `human-social-copy` 技能使用，负责写作风格。

## 定时推送

三个 cron 任务，每天早9点、下午2点、晚8点自动执行。

## 许可

MIT
