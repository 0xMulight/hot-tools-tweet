#!/usr/bin/env python3
"""
AI Content Scout — 每日 AI 热点采集器
信源：GitHub Trending / Hacker News / Surf (社交+新闻)
输出 JSON → Agent 筛选后写推文

环境要求：requests, PySocks (SOCKS5 代理), surf CLI
"""

import json, os, sys, time, subprocess
from datetime import datetime, timezone, timedelta

import re
import requests
from requests.adapters import HTTPAdapter

tz_shanghai = timezone(timedelta(hours=8))

# ─── SOCKS5 代理 ──────────────────────────────────────
PROXY = os.environ.get("all_proxy") or os.environ.get("ALL_PROXY") or "socks5h://172.26.0.1:10808"

def get_session():
    s = requests.Session()
    s.proxies = {"http": PROXY, "https": PROXY}
    s.headers.update({
        "User-Agent": "AI-Content-Scout/1.0",
        "Accept": "application/json",
    })
    s.timeout = 20
    return s

session = get_session()

def fetch_json(url, timeout=15):
    try:
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[scout] WARN {url[:80]}: {e}", file=sys.stderr)
        return None

def now_str():
    return datetime.now(tz_shanghai).strftime("%Y-%m-%d %H:%M")


# ─── 信源 1: GitHub Trending (AI repos, 7天内) ───────

def fetch_github_ai():
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    # 用 topic:ai 搜所有打 AI 标签的新项目
    query = "topic:ai+created:>%s" % since
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
    data = fetch_json(url)
    if not data:
        return []
    results = []
    for repo in data.get("items", []):
        results.append({
            "source": "github",
            "title": repo["full_name"],
            "desc": (repo.get("description") or "").strip()[:200],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "lang": repo.get("language") or "",
            "topics": repo.get("topics", [])[:5],
            "score": repo["stargazers_count"],
        })
    return results


# ─── 信源 2: Hacker News AI 热帖 ─────────────────────

AI_KW = {"ai", "llm", "gpt", "claude", "openai", "deepseek", "gemini",
          "agent", "rag", "mcp", "prompt", "fine-tun", "transformer",
          "copilot", "cursor", "codex", "langchain", "llama", "mistral",
          "cuda", "nvidia", "ollama", "neural", "rlhf", "dpo", "grpo",
          "autonomous", "reasoning", "whisper", "vibe coding", "sora",
          "midjourney", "stable diffusion", "image generat",
          "machine learning", "deep learning"}

def fetch_hackernews_ai():
    """拉 HN Top 80，本地用关键词筛选 AI 相关内容"""
    top = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not top:
        return []
    # 只拉前 80 条 top stories 的详情 — 比逐个拉 200 条快
    import concurrent.futures
    results = []
    ids_to_fetch = top[:80]
    
    def get_story(item_id):
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
        if not item or item.get("type") != "story":
            return None
        title_lower = (item.get("title") or "").lower()
        score = item.get("score", 0)
        if score < 10:
            return None
        # Word-boundary match for short keywords (ai, rag, mcp etc.), substring for longer ones
        matched = False
        for kw in AI_KW:
            if len(kw) <= 3:
                if re.search(r'\b' + re.escape(kw) + r'\b', title_lower):
                    matched = True
                    break
            elif kw in title_lower:
                matched = True
                break
        if not matched:
            return None
        url = item.get("url") or f"https://news.ycombinator.com/item?id={item_id}"
        return {
            "source": "hackernews",
            "title": item["title"],
            "desc": "",
            "url": url,
            "score": score,
            "comments": item.get("descendants", 0),
        }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(get_story, i): i for i in ids_to_fetch}
        for fut in concurrent.futures.as_completed(futures, timeout=60):
            r = fut.result()
            if r:
                results.append(r)
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:15]


# ─── 信源 3: Surf 社交 — Crypto Twitter AI 工具帖 ───

def fetch_surf_social():
    """用 Surf 搜 Twitter 上关于 AI 工具/开源项目的帖子"""
    try:
        r = subprocess.run(
            ["surf", "search-social-posts", "--q", "AI tool open source", "--limit", "10"],
            capture_output=True, text=True, timeout=20
        )
        if r.returncode != 0:
            print(f"[scout] WARN surf social: {r.stderr[:100]}", file=sys.stderr)
            return []
        data = json.loads(r.stdout)
    except Exception as e:
        print(f"[scout] WARN surf social: {e}", file=sys.stderr)
        return []

    results = []
    for p in data.get("data", []):
        text = p.get("text", "")
        likes = p.get("stats", {}).get("likes", 0)
        reposts = p.get("stats", {}).get("reposts", 0)
        views = p.get("stats", {}).get("views", 0)
        engagement = likes + reposts * 2 + views * 0.01  # 综合热度分
        if engagement < 1:
            continue
        # 从正文提取 URL
        import re
        urls = re.findall(r"https?://[^\s]+", text)
        url = urls[0] if urls else p.get("url", "")
        results.append({
            "source": "surf/social",
            "title": text[:120],
            "desc": text[120:250] if len(text) > 120 else "",
            "url": url,
            "score": round(engagement, 1),
            "handle": p.get("author", {}).get("handle", ""),
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:8]


# ─── 信源 4: Surf 新闻 — Crypto+AI 交叉热点 ──────────

def fetch_surf_news():
    """用 Surf 搜 crypto 媒体的 AI 相关新闻"""
    try:
        r = subprocess.run(
            ["surf", "search-news", "--q", "AI agent open source", "--limit", "10"],
            capture_output=True, text=True, timeout=20
        )
        if r.returncode != 0:
            print(f"[scout] WARN surf news: {r.stderr[:100]}", file=sys.stderr)
            return []
        data = json.loads(r.stdout)
    except Exception as e:
        print(f"[scout] WARN surf news: {e}", file=sys.stderr)
        return []

    results = []
    for article in data.get("data", []):
        title = article.get("title", "")
        summary = article.get("summary", "")
        url = article.get("url", "")
        published = article.get("published_at", 0)
        if not title:
            continue
        # 时效性衰减：24小时内的新闻加权
        age_hours = (time.time() - published) / 3600 if published else 999
        freshness = max(0, 1 - age_hours / 48)  # 48小时内线性衰减
        results.append({
            "source": f"surf/news",
            "title": title,
            "desc": (summary or "")[:200],
            "url": url,
            "score": round(5 * freshness, 1),  # 基础分 + 时效加权
            "age_hours": round(age_hours, 1),
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:6]


# ─── 主流程 ──────────────────────────────────────────

POSTED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted_urls.json")
CANDIDATE_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidate_history.json")

def load_posted():
    try:
        with open(POSTED_FILE, "r") as f:
            data = json.load(f)
        urls = set()
        for item in data:
            if isinstance(item, dict):
                urls.add(item.get("url", ""))
            else:
                urls.add(item)
        return urls
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def load_candidate_history():
    """返回 {url: [timestamp1, timestamp2, ...]}，自动清理超过24h的记录"""
    try:
        with open(CANDIDATE_HISTORY_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    now = time.time()
    cleaned = {}
    for url, timestamps in data.items():
        recent = [t for t in timestamps if now - t < 86400]  # 24小时内
        if recent:
            cleaned[url] = recent
    return cleaned

def update_candidate_history(current_urls):
    """把本轮候选URL写入历史，追加时间戳"""
    now = time.time()
    history = load_candidate_history()
    for url in current_urls:
        if url not in history:
            history[url] = []
        history[url].append(now)
    with open(CANDIDATE_HISTORY_FILE, "w") as f:
        json.dump(history, f, ensure_ascii=False)
    return history

def candidate_penalty(url, history):
    """根据过去24h内出现的次数计算降权系数 (0.0-1.0)"""
    if url not in history:
        return 1.0  # 首次出现，满分
    count = len(history[url])
    if count == 1:
        return 0.6   # 出现过1次 → 打6折
    elif count == 2:
        return 0.3   # 出现过2次 → 打3折
    else:
        return 0.1   # 出现过3次+ → 打到骨折

def main():
    print(f"[scout] AI Content Scout — {now_str()}", file=sys.stderr)

    # 加载已发链接，过滤重复
    posted = load_posted()
    print(f"[scout] 已发链接: {len(posted)} 条", file=sys.stderr)

    all_items = []

    print("[scout] GitHub Trending...", file=sys.stderr)
    gh = fetch_github_ai()
    print(f"[scout]   → {len(gh)} repos", file=sys.stderr)
    all_items.extend(gh)

    print("[scout] Hacker News...", file=sys.stderr)
    hn = fetch_hackernews_ai()
    print(f"[scout]   → {len(hn)} stories", file=sys.stderr)
    all_items.extend(hn)

    print("[scout] Surf 社交 (Crypto Twitter AI)...", file=sys.stderr)
    ss = fetch_surf_social()
    print(f"[scout]   → {len(ss)} posts", file=sys.stderr)
    all_items.extend(ss)

    print("[scout] Surf 新闻 (Crypto+AI)...", file=sys.stderr)
    sn = fetch_surf_news()
    print(f"[scout]   → {len(sn)} articles", file=sys.stderr)
    all_items.extend(sn)

    # 加载候选历史，用于降权老面孔
    candidate_hist = load_candidate_history()
    penalized_count = 0

    # 去重 + 过滤已发 + 候选降权 + 按降权后分数排序
    seen = set()
    skipped_posted = 0
    unique = []
    for item in sorted(all_items, key=lambda x: x.get("score", 0), reverse=True):
        url = item["url"]
        if url in seen:
            continue
        seen.add(url)
        if url in posted:
            skipped_posted += 1
            continue
        # 24h内候选降权
        penalty = candidate_penalty(url, candidate_hist)
        if penalty < 1.0:
            item["original_score"] = item.get("score", 0)
            item["score"] = round(item.get("score", 0) * penalty, 1)
            item["candidate_penalty"] = penalty
            penalized_count += 1
        unique.append(item)

    # 按降权后分数重新排序
    unique.sort(key=lambda x: x.get("score", 0), reverse=True)

    print(f"[scout] 去重后共 {len(unique)} 条 (跳过已发 {skipped_posted} 条, 候选降权 {penalized_count} 条)", file=sys.stderr)

    output = {
        "scout_time": now_str(),
        "total": len(unique),
        "items": unique[:50],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # 更新候选历史
    all_urls = [item["url"] for item in unique[:50]]
    update_candidate_history(all_urls)


if __name__ == "__main__":
    main()
