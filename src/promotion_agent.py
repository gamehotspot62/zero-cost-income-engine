"""Autonomous Global Promotion & Traffic Agent (AEO, RSS/JSON feeds, IndexNow, WebSub, and multi-channel syndication)."""

from __future__ import annotations

import html
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

from src.brand_assets import BRAND_LOGO_SVG, head_favicon_links

INDEXNOW_KEY = "stackpulseindexnow2026key"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
WEBSUB_HUB_URL = "https://pubsubhubbub.appspot.com/"


def _build_llms_files(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    alternatives: list[dict[str, Any]],
    product_meta: dict[str, Any],
    dist_dir: Path,
) -> None:
    site_name = settings.get("site_name", "StackPulse AI")
    tagline = settings.get("site_tagline", "")
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")

    llms_lines = [
        f"# {site_name}",
        f"> {tagline}",
        "",
        f"{site_name} is an automated developer infrastructure & SaaS free-tier intelligence hub at {base_url}/.",
        "",
        "## Digital Products & Blueprints",
    ]
    for prod in product_meta.get("products", []):
        price = "Free ($0)" if prod["price_usd"] == 0 else f"${prod['price_usd']}"
        url = prod["checkout_url"]
        if not url.startswith("http"):
            url = f"{base_url}/products/{url}"
        llms_lines.append(f"- [{prod['title']} ({price})]({url}): {prod['description']}")

    llms_lines.extend(
        [
            "",
            "## Key Directory Endpoints",
            f"- [Home Directory]({base_url}/index.html): Searchable catalog of {len(tools)} verified free-tier developer tools",
            f"- [Digital Products Storefront]({base_url}/products/index.html): Cheat sheets, automation templates, and sponsor slots",
            f"- [Latest AI Digest Newsletter]({base_url}/newsletter/latest-issue.html): Daily ecosystem signal summary",
            f"- [RSS 2.0 Feed]({base_url}/feed.xml) | [JSON Feed]({base_url}/feed.json)",
            "",
            "## Top Head-to-Head Comparisons",
        ]
    )
    for comp in comparisons[:15]:
        llms_lines.append(f"- [{comp['title']}]({base_url}/{comp['path']}) — {comp['category']} (Top pick: {comp['winner']})")

    (dist_dir / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")

    full_lines = list(llms_lines)
    full_lines.extend(["", "## All Verified $0 Tools"])
    for tool in sorted(tools, key=lambda t: t["score"], reverse=True):
        full_lines.append(
            f"- **{tool['name']}** ({tool['category']}, {tool['score']}/10): "
            f"Free tier: {tool['free_tier_limits']} | Paid: {tool['paid_start_price']} | "
            f"Link: {base_url}/go/{tool['id']}.html"
        )
    full_lines.extend(["", "## All Programmatic Comparison Pages"])
    for comp in comparisons:
        full_lines.append(f"- [{comp['title']}]({base_url}/{comp['path']})")
    full_lines.extend(["", "## All Open-Source Alternatives Pages"])
    for alt in alternatives:
        full_lines.append(f"- [{alt['title']}]({base_url}/{alt['path']}) (Top pick: {alt['top_pick']})")

    (dist_dir / "llms-full.txt").write_text("\n".join(full_lines) + "\n", encoding="utf-8")


def _build_syndication_feeds(
    settings: dict[str, Any],
    signals: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    editorial: dict[str, Any],
    dist_dir: Path,
) -> list[dict[str, Any]]:
    site_name = settings.get("site_name", "StackPulse AI")
    tagline = settings.get("site_tagline", "")
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")
    now = datetime.now(timezone.utc)
    rfc_date = format_datetime(now)
    iso_date = now.isoformat()

    feed_items: list[dict[str, str]] = [
        {
            "id": f"{base_url}/newsletter/latest-issue.html#{now.strftime('%Y-%m-%d')}",
            "title": editorial.get("headline", f"{site_name} Daily Free-Tier Digest"),
            "url": f"{base_url}/newsletter/latest-issue.html",
            "summary": f"{editorial.get('intro', '')} {editorial.get('actionable_play', '')}".strip(),
        },
        {
            "id": f"{base_url}/products/index.html#{now.strftime('%Y-%m-%d')}",
            "title": f"2026 Zero-Cost Cloud & AI Stack Blueprints + Free Cheat Sheet",
            "url": f"{base_url}/products/index.html",
            "summary": "Download the free 2026 Developer Free-Tier Cheat Sheet or explore GitHub Actions & Make.com AI agent packs.",
        },
    ]

    for comp in comparisons[:8]:
        feed_items.append(
            {
                "id": f"{base_url}/{comp['path']}",
                "title": f"{comp['title']} (2026 Free Tier & Pricing Breakdown)",
                "url": f"{base_url}/{comp['path']}",
                "summary": f"Automated comparison in {comp['category']}. Top zero-cost pick: {comp['winner']}.",
            }
        )

    for sig in signals[:4]:
        feed_items.append(
            {
                "id": sig["url"],
                "title": f"[{sig['topic']}] {sig['title']}",
                "url": f"{base_url}/index.html#signals",
                "summary": sig["summary"],
            }
        )

    rss_items = "\n".join(
        f"""    <item>
      <title>{html.escape(item['title'])}</title>
      <link>{html.escape(item['url'])}</link>
      <guid isPermaLink="false">{html.escape(item['id'])}</guid>
      <pubDate>{rfc_date}</pubDate>
      <description>{html.escape(item['summary'])}</description>
    </item>"""
        for item in feed_items
    )
    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(site_name)}</title>
    <link>{html.escape(base_url + '/')}</link>
    <description>{html.escape(tagline)}</description>
    <language>en-us</language>
    <lastBuildDate>{rfc_date}</lastBuildDate>
    <atom:link href="{html.escape(base_url + '/feed.xml')}" rel="self" type="application/rss+xml" />
{rss_items}
  </channel>
</rss>
"""
    (dist_dir / "feed.xml").write_text(rss_xml, encoding="utf-8")

    json_feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": site_name,
        "home_page_url": f"{base_url}/",
        "feed_url": f"{base_url}/feed.json",
        "description": tagline,
        "items": [
            {
                "id": item["id"],
                "url": item["url"],
                "title": item["title"],
                "content_text": item["summary"],
                "date_published": iso_date,
            }
            for item in feed_items
        ],
    }
    (dist_dir / "feed.json").write_text(json.dumps(json_feed, indent=2), encoding="utf-8")
    return feed_items


def _ping_indexnow(base_url: str, url_list: list[str], offline: bool) -> str:
    if offline:
        return "skipped-offline"
    parsed = urllib.parse.urlparse(base_url)
    payload = {
        "host": parsed.netloc,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{base_url}/{INDEXNOW_KEY}.txt",
        "urlList": url_list[:100],
    }
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return f"http-{resp.status}"
    except urllib.error.HTTPError as exc:
        return f"http-{exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return f"error:{type(exc).__name__}"


def _ping_websub(base_url: str, offline: bool) -> str:
    if offline:
        return "skipped-offline"
    data = urllib.parse.urlencode(
        {
            "hub.mode": "publish",
            "hub.url": f"{base_url}/feed.xml",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        WEBSUB_HUB_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return f"http-{resp.status}"
    except urllib.error.HTTPError as exc:
        return f"http-{exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return f"error:{type(exc).__name__}"


def _generate_campaigns(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    editorial: dict[str, Any],
    product_meta: dict[str, Any],
) -> dict[str, Any]:
    site_name = settings.get("site_name", "StackPulse AI")
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    top_signal = signals[0] if signals else {"title": "Zero-Cost Cloud & AI Stacks", "topic": "Automation & Workflows"}
    featured_comp = comparisons[0] if comparisons else {"title": "Make vs n8n", "path": "index.html", "winner": "GitHub Actions"}
    comp_url = f"{base_url}/{featured_comp['path']}"
    products_url = f"{base_url}/products/index.html"
    free_sheet_url = f"{base_url}/products/free-tier-cheatsheet.md"
    make_tool = next((t for t in tools if t["id"] == "make-automation"), None)
    make_promo_url = make_tool["affiliate_url"] if make_tool else f"{base_url}/go/make-automation.html"

    x_post = (
        f"Building online with $0 capital in 2026:\n\n"
        f"We benchmarked {len(tools)} free-tier AI, DB, & automation tools across {len(comparisons)} comparisons.\n\n"
        f"Today's trend: {top_signal['title'][:90]}\n"
        f"Full comparison + free cheat sheet:\n{comp_url}\n{products_url}"
    )
    linkedin_post = (
        f"How solo builders run automated AI & SaaS stacks at $0/month fixed overhead:\n\n"
        f"{editorial.get('intro', '')}\n\n"
        f"We compiled {len(tools)} verified free-tier limits (including Gemini, Supabase, Turso, Cloudflare Pages, and Make) "
        f"plus {len(comparisons)} side-by-side comparisons.\n\n"
        f"Explore the live directory & free cheat sheet: {products_url}\n"
        f"Featured comparison ({featured_comp['title']}): {comp_url}\n\n"
        f"#BuildInPublic #AIAutomation #MicroSaaS #ZeroCost #DevTools"
    )
    reddit_title = f"I built a $0-overhead directory comparing {len(tools)} free-tier DevTools, AI APIs & open-source alternatives ({len(comparisons)} pages)"
    reddit_body = (
        f"Sharing a free resource for anyone bootstrapping projects with $0 server budget:\n\n"
        f"- **Directory ({len(tools)} tools across 7 categories):** {base_url}/\n"
        f"- **Featured Breakdown ({featured_comp['title']}):** {comp_url}\n"
        f"- **Free 2026 Cheat Sheet (no email gate):** {free_sheet_url}\n\n"
        f"Every tool entry lists exact free-tier quotas, paid step-up price, and an open-source self-hostable escape hatch. "
        f"Curious which free-tier limits caught you off guard recently?"
    )
    hn_title = f"Show HN: StackPulse AI – Automated $0 free-tier benchmark directory ({len(tools)} tools, open-source alternatives)"
    devto_title = f"Zero-Cost 2026 Stack: {len(tools)} Free-Tier AI, Database & Automation Tools Compared ({date_str})"
    devto_markdown = (
        f"---\n"
        f"title: \"{devto_title}\"\n"
        f"published: true\n"
        f"tags: opensource, ai, webdev, productivity\n"
        f"canonical_url: {base_url}/index.html\n"
        f"---\n\n"
        f"{editorial.get('intro', '')}\n\n"
        f"## Featured Comparison: {featured_comp['title']}\n"
        f"Top zero-cost pick: **{featured_comp['winner']}** — read the full TCO & FAQ breakdown here: {comp_url}\n\n"
        f"## Free Cheat Sheet & Automation Blueprints\n"
        f"- Download the free Cheat Sheet: {free_sheet_url}\n"
        f"- Explore all {product_meta.get('product_count', 4)} digital packs & sponsor slots: {products_url}\n"
        f"- Automate social & RSS distribution with Make (free Core promo): {make_promo_url}\n\n"
        f"## Actionable Play Today\n"
        f"{editorial.get('actionable_play', '')}\n"
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": date_str,
        "site_url": f"{base_url}/",
        "products_url": products_url,
        "featured_comparison_url": comp_url,
        "channels": {
            "x_twitter": {
                "label": "X / Twitter Post",
                "text": x_post,
                "share_intent_url": "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(x_post),
            },
            "linkedin": {
                "label": "LinkedIn Post",
                "text": linkedin_post,
                "share_intent_url": "https://www.linkedin.com/sharing/share-offsite/?url=" + urllib.parse.quote(products_url),
            },
            "reddit": {
                "label": "Reddit (r/SideProject / r/selfhosted / r/SaaS)",
                "title": reddit_title,
                "text": reddit_body,
                "share_intent_url": (
                    "https://www.reddit.com/submit?url="
                    + urllib.parse.quote(f"{base_url}/")
                    + "&title="
                    + urllib.parse.quote(reddit_title)
                ),
            },
            "hacker_news": {
                "label": "Hacker News (Show HN)",
                "title": hn_title,
                "text": f"Submit {base_url}/ with title: {hn_title}",
                "share_intent_url": (
                    "https://news.ycombinator.com/submitlink?u="
                    + urllib.parse.quote(f"{base_url}/")
                    + "&t="
                    + urllib.parse.quote(hn_title)
                ),
            },
            "devto_article": {
                "label": "Dev.to / Hashnode Long-Form Article",
                "title": devto_title,
                "text": devto_markdown,
                "share_intent_url": "https://dev.to/new",
            },
        },
    }


def _dispatch_webhooks(campaigns: dict[str, Any], offline: bool) -> dict[str, str]:
    if offline:
        return {
            "make_webhook": "skipped-offline",
            "discord_webhook": "skipped-offline",
            "devto_api": "skipped-offline",
        }

    results: dict[str, str] = {}

    make_url = os.environ.get("MAKE_PROMO_WEBHOOK_URL", "").strip()
    if not make_url:
        results["make_webhook"] = "not-configured"
    else:
        try:
            req = urllib.request.Request(
                make_url,
                data=json.dumps(campaigns).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                results["make_webhook"] = f"http-{resp.status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            results["make_webhook"] = f"error:{type(exc).__name__}"

    discord_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not discord_url:
        results["discord_webhook"] = "not-configured"
    else:
        msg = (
            f"**{campaigns['date']} Global Promotion Campaign Ready**\n"
            f"Site: {campaigns['site_url']}\n"
            f"Products: {campaigns['products_url']}\n"
            f"X Copy:\n```{campaigns['channels']['x_twitter']['text']}```"
        )
        try:
            req = urllib.request.Request(
                discord_url,
                data=json.dumps({"content": msg[:1950]}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                results["discord_webhook"] = f"http-{resp.status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            results["discord_webhook"] = f"error:{type(exc).__name__}"

    devto_key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not devto_key:
        results["devto_api"] = "not-configured"
    else:
        art = campaigns["channels"]["devto_article"]
        payload = {
            "article": {
                "title": art["title"],
                "published": os.environ.get("DEVTO_PUBLISH", "true").lower() == "true",
                "body_markdown": art["text"],
                "tags": ["opensource", "ai", "webdev", "productivity"],
                "canonical_url": campaigns["site_url"],
            }
        }
        try:
            req = urllib.request.Request(
                "https://dev.to/api/articles",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "api-key": devto_key,
                    "User-Agent": "StackPulseAI-PromoAgent/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                results["devto_api"] = f"http-{resp.status}"
        except urllib.error.HTTPError as exc:
            results["devto_api"] = f"http-{exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            results["devto_api"] = f"error:{type(exc).__name__}"

    return results


def _build_promotion_hub_html(
    settings: dict[str, Any],
    campaigns: dict[str, Any],
    telemetry: dict[str, Any],
    dist_dir: Path,
) -> None:
    promo_dir = dist_dir / "promotions"
    promo_dir.mkdir(parents=True, exist_ok=True)
    site_name = settings.get("site_name", "StackPulse AI")

    cards_html = ""
    for key, ch in campaigns["channels"].items():
        escaped_text = html.escape(ch["text"])
        cards_html += f"""
<article class="card">
  <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
    <h2 style="margin:0; font-size:1.12rem;">{html.escape(ch['label'])}</h2>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      <button class="btn btn-secondary copy-btn" data-target="copy-{html.escape(key, quote=True)}">Copy Text</button>
      <a class="btn" href="{html.escape(ch['share_intent_url'], quote=True)}" target="_blank" rel="noopener">Share Now &rarr;</a>
    </div>
  </div>
  <pre id="copy-{html.escape(key, quote=True)}">{escaped_text}</pre>
</article>
"""

    hub_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Global Promotion &amp; Traffic Hub | {html.escape(site_name)}</title>
  <meta name="description" content="Automated search indexing, RSS/JSON feeds, AI discovery (llms.txt), and multi-channel promotion campaigns." />
  {head_favicon_links("../")}
  <style>
    :root {{ --bg:#070b14; --surface:#0f172a; --surface-2:#1e293b; --border:#334155; --text:#f1f5f9; --muted:#94a3b8; --accent:#38bdf8; --accent-2:#22c55e; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
    a {{ color:var(--accent); text-decoration:none; }}
    .container {{ max-width:1100px; margin:0 auto; padding:0 20px; }}
    header {{ border-bottom:1px solid var(--border); background:rgba(15,23,42,0.92); padding:14px 0; }}
    .nav {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px; }}
    .brand {{ display:inline-flex; align-items:center; gap:10px; font-weight:800; color:#fff; }}
    .nav-links {{ display:flex; gap:18px; flex-wrap:wrap; font-size:0.92rem; }}
    .nav-links a {{ color:var(--muted); font-weight:500; }}
    .hero {{ padding:42px 0 26px; border-bottom:1px solid var(--border); }}
    .grid {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); margin:22px 0; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:18px; }}
    .pill {{ display:inline-block; font-size:0.76rem; font-weight:700; text-transform:uppercase; color:var(--accent); background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.35); padding:3px 10px; border-radius:999px; }}
    .meta {{ color:var(--muted); font-size:0.9rem; }}
    .btn {{ display:inline-block; background:var(--accent); color:#04111f; font-weight:700; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; font-size:0.88rem; }}
    .btn-secondary {{ background:var(--surface-2); color:var(--text); border:1px solid var(--border); }}
    pre {{ background:#020617; border:1px solid var(--border); border-radius:8px; padding:14px; white-space:pre-wrap; word-break:break-word; font-size:0.86rem; color:#cbd5e1; margin-top:12px; }}
  </style>
</head>
<body>
  <header>
    <div class="container nav">
      <a class="brand" href="../index.html">{BRAND_LOGO_SVG}<span>{html.escape(site_name)} <span style="color:var(--accent);">$0 Stack</span></span></a>
      <nav class="nav-links">
        <a href="../index.html">Directory</a>
        <a href="../products/index.html">Products</a>
        <a href="index.html" style="color:#fff;">Promotion Hub</a>
        <a href="../newsletter/latest-issue.html">Newsletter</a>
        <a href="../dashboard.html">Dashboard</a>
      </nav>
    </div>
  </header>
  <main class="container">
    <section class="hero">
      <span class="pill">Autonomous Traffic &amp; Distribution Agent</span>
      <h1 style="margin:12px 0 8px;">Global Promotion &amp; Syndication Hub</h1>
      <p class="meta">Zero-cost global discovery across Search Engines (IndexNow + WebSub), AI Answer Engines (llms.txt), RSS Syndication, and one-click Social Distribution.</p>
    </section>

    <section class="grid">
      <div class="card"><h3>IndexNow Global Ping</h3><p><strong>{html.escape(telemetry['indexnow_status'])}</strong></p><p class="meta">{telemetry['urls_submitted']} URLs pushed to Bing, DuckDuckGo, ChatGPT Search &amp; Yandex</p></div>
      <div class="card"><h3>WebSub RSS Hub Ping</h3><p><strong>{html.escape(telemetry['websub_status'])}</strong></p><p class="meta"><a href="../feed.xml">RSS 2.0</a> &bull; <a href="../feed.json">JSON Feed</a></p></div>
      <div class="card"><h3>AI Answer Discovery</h3><p><strong>Active</strong></p><p class="meta"><a href="../llms.txt">llms.txt</a> &bull; <a href="../llms-full.txt">llms-full.txt</a></p></div>
      <div class="card"><h3>Auto Webhooks</h3><p><strong>Make: {html.escape(telemetry['webhooks']['make_webhook'])}</strong></p><p class="meta">Dev.to: {html.escape(telemetry['webhooks']['devto_api'])} &bull; Discord: {html.escape(telemetry['webhooks']['discord_webhook'])}</p></div>
    </section>

    <section>
      <h2>Ready-to-Publish Global Campaigns ({html.escape(campaigns['date'])})</h2>
      {cards_html}
    </section>
  </main>
  <script>
    document.querySelectorAll('.copy-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const target = document.getElementById(btn.dataset.target);
        if (!target || !navigator.clipboard) return;
        navigator.clipboard.writeText(target.textContent);
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {{ btn.textContent = orig; }}, 1500);
      }});
    }});
  </script>
</body>
</html>
"""
    (promo_dir / "index.html").write_text(hub_html, encoding="utf-8")


def run_promotion_agent(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    alternatives: list[dict[str, Any]],
    editorial: dict[str, Any],
    product_meta: dict[str, Any],
    dist_dir: Path,
    offline: bool = False,
) -> dict[str, Any]:
    """Generate global discovery feeds, build social campaigns, and push free indexing/webhook pings."""
    dist_dir.mkdir(parents=True, exist_ok=True)
    promo_dir = dist_dir / "promotions"
    promo_dir.mkdir(parents=True, exist_ok=True)
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")

    # 1. Write IndexNow key verification file
    (dist_dir / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")

    # 2. Generate AI Answer Engine discovery files (llms.txt & llms-full.txt)
    _build_llms_files(settings, tools, comparisons, alternatives, product_meta, dist_dir)

    # 3. Generate RSS 2.0 & JSON syndication feeds
    feed_items = _build_syndication_feeds(settings, signals, comparisons, editorial, dist_dir)

    # 4. Collect all public indexable URLs for IndexNow
    all_urls = [
        f"{base_url}/",
        f"{base_url}/index.html",
        f"{base_url}/products/index.html",
        f"{base_url}/promotions/index.html",
        f"{base_url}/newsletter/latest-issue.html",
    ]
    all_urls.extend(f"{base_url}/{c['path']}" for c in comparisons)
    all_urls.extend(f"{base_url}/{a['path']}" for a in alternatives)

    # 5. Ping IndexNow & WebSub Hub
    indexnow_status = _ping_indexnow(base_url, all_urls, offline=offline)
    websub_status = _ping_websub(base_url, offline=offline)

    # 6. Generate multi-channel promotion campaigns and dispatch optional zero-cost webhooks
    campaigns = _generate_campaigns(settings, tools, signals, comparisons, editorial, product_meta)
    (promo_dir / "latest-campaigns.json").write_text(json.dumps(campaigns, indent=2), encoding="utf-8")
    webhook_results = _dispatch_webhooks(campaigns, offline=offline)

    telemetry = {
        "indexnow_status": indexnow_status,
        "websub_status": websub_status,
        "urls_submitted": len(all_urls),
        "feed_items": len(feed_items),
        "campaigns_generated": len(campaigns["channels"]),
        "webhooks": webhook_results,
        "llms_file": "llms.txt",
        "rss_feed": "feed.xml",
        "json_feed": "feed.json",
        "promotion_hub": "promotions/index.html",
    }
    _build_promotion_hub_html(settings, campaigns, telemetry, dist_dir)
    return telemetry
