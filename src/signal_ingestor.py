"""Zero-cost signal ingestion from public APIs with resilient offline fallback."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
GITHUB_SEARCH_URL = (
    "https://api.github.com/search/repositories"
    "?q=ai+OR+saas+OR+automation+OR+serverless+stars:%3E200"
    "&sort=updated&order=desc&per_page={limit}"
)

SEED_SIGNALS: list[dict[str, Any]] = [
    {
        "source": "Curated Intelligence",
        "title": "Zero-Cost AI Workflows with GitHub Actions & Free LLM Tiers",
        "url": "https://github.com/features/actions",
        "score": 342,
        "topic": "Automation & Workflows",
        "summary": "Builders are replacing paid VPS cron servers with public-repo GitHub Actions workflows paired with Gemini and Groq free APIs.",
    },
    {
        "source": "Curated Intelligence",
        "title": "Programmatic SEO Directories Built on Serverless SQLite & Cloudflare Pages",
        "url": "https://pages.cloudflare.com/",
        "score": 289,
        "topic": "Cloud Hosting & Edge",
        "summary": "Unlimited free static bandwidth on Cloudflare Pages enables zero-cost comparison hubs targeting high-intent SaaS buyer keywords.",
    },
    {
        "source": "Curated Intelligence",
        "title": "Merchant of Record Platforms (Lemon Squeezy vs Gumroad) for Indie Digital Products",
        "url": "https://www.lemonsqueezy.com/",
        "score": 256,
        "topic": "Payments & MoR",
        "summary": "Zero-monthly-fee Merchant of Record tools remove upfront incorporation and VAT hurdles for solo digital entrepreneurs.",
    },
    {
        "source": "Curated Intelligence",
        "title": "Serverless Postgres & Edge SQLite Free Tier Benchmarks (Supabase vs Neon vs Turso)",
        "url": "https://turso.tech/",
        "score": 218,
        "topic": "Serverless Databases",
        "summary": "Free-tier limits across modern databases now support millions of reads per month before requiring a $19-$29 upgrade.",
    },
    {
        "source": "Curated Intelligence",
        "title": "High-Speed Inference Routing Across Free-Tier LLM APIs",
        "url": "https://openrouter.ai/",
        "score": 195,
        "topic": "AI & LLM APIs",
        "summary": "Multi-provider fallback chains prevent rate-limit downtime when operating autonomous content pipelines at $0 API cost.",
    },
]

RELEVANCE_KEYWORDS = {
    "ai", "llm", "gemini", "claude", "openai", "groq", "open-source", "opensource",
    "saas", "free", "api", "sqlite", "postgres", "supabase", "cloudflare", "github",
    "automation", "agent", "seo", "serverless", "docker", "python", "self-host",
}


def _fetch_json(url: str, timeout: int = 8) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "StackPulseAI-ZeroCostAgent/1.0 (+https://github.com)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _infer_topic(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("llm", "ai", "gemini", "gpt", "model", "inference", "groq")):
        return "AI & LLM APIs"
    if any(k in lowered for k in ("sql", "postgres", "supabase", "neon", "turso", "db", "database")):
        return "Serverless Databases"
    if any(k in lowered for k in ("cloudflare", "vercel", "hosting", "edge", "deploy", "cdn")):
        return "Cloud Hosting & Edge"
    if any(k in lowered for k in ("stripe", "payment", "gumroad", "lemon", "billing", "saas pricing")):
        return "Payments & MoR"
    return "Automation & Workflows"


def fetch_hacker_news_signals(limit: int = 12, timeout: int = 8) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    story_ids = _fetch_json(HN_TOP_STORIES_URL, timeout=timeout)
    for story_id in story_ids[: max(limit * 2, 20)]:
        item = _fetch_json(HN_ITEM_URL.format(item_id=story_id), timeout=timeout)
        if not item or item.get("type") != "story" or not item.get("title"):
            continue
        title = str(item["title"])
        url = str(item.get("url") or f"https://news.ycombinator.com/item?id={story_id}")
        tokens = set(title.lower().replace("-", " ").split())
        is_relevant = bool(tokens & RELEVANCE_KEYWORDS) or any(k in title.lower() for k in RELEVANCE_KEYWORDS)
        if is_relevant or len(signals) < 3:
            signals.append(
                {
                    "source": "Hacker News",
                    "title": title,
                    "url": url,
                    "score": int(item.get("score") or 0),
                    "topic": _infer_topic(title),
                    "summary": f"Trending HN discussion ({item.get('descendants', 0)} comments) relevant to developer builders.",
                }
            )
        if len(signals) >= limit:
            break
    return signals


def fetch_github_trending_signals(limit: int = 6, timeout: int = 8) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    data = _fetch_json(GITHUB_SEARCH_URL.format(limit=limit), timeout=timeout)
    for repo in data.get("items", [])[:limit]:
        full_name = repo.get("full_name", "unknown/repo")
        desc = repo.get("description") or "Open-source developer tool trending on GitHub."
        signals.append(
            {
                "source": "GitHub",
                "title": f"{full_name} — {desc[:90]}",
                "url": repo.get("html_url", "https://github.com"),
                "score": int(repo.get("stargazers_count") or 0),
                "topic": _infer_topic(f"{full_name} {desc}"),
                "summary": desc[:200],
            }
        )
    return signals


def ingest_signals(
    settings: dict[str, Any],
    data_dir: Path,
    offline: bool = False,
) -> dict[str, Any]:
    """Gather web signals from zero-auth endpoints, falling back safely to seed/cached signals."""
    sig_cfg = settings.get("signals", {})
    hn_limit = int(sig_cfg.get("hn_story_limit", 10))
    gh_limit = int(sig_cfg.get("github_repo_limit", 6))
    timeout = int(sig_cfg.get("timeout_seconds", 8))

    collected: list[dict[str, Any]] = []
    errors: list[str] = []
    mode = "offline-seed"

    if not offline:
        try:
            collected.extend(fetch_hacker_news_signals(limit=hn_limit, timeout=timeout))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append(f"HN fetch skipped: {exc}")

        try:
            collected.extend(fetch_github_trending_signals(limit=gh_limit, timeout=timeout))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append(f"GitHub fetch skipped: {exc}")

        if collected:
            mode = "live-web"

    if not collected:
        collected = list(SEED_SIGNALS)
        mode = "offline-seed" if offline else "fallback-seed"

    # Deduplicate by title and sort by score descending
    seen: set[str] = set()
    unique_signals: list[dict[str, Any]] = []
    for item in sorted(collected, key=lambda x: x.get("score", 0), reverse=True):
        key = item["title"].strip().lower()
        if key not in seen:
            seen.add(key)
            unique_signals.append(item)

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ingestion_mode": mode,
        "signal_count": len(unique_signals),
        "errors": errors,
        "signals": unique_signals[:15],
    }

    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "latest_signals.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload
