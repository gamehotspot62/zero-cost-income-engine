"""Monetization engine: affiliate redirect routes, digital blueprint compilation, and newsletter dispatch."""

from __future__ import annotations

import html
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_affiliate_redirects(tools: list[dict[str, Any]], dist_dir: Path) -> list[dict[str, Any]]:
    """Create clean /go/<tool-id>.html redirect pages so affiliate IDs are centrally managed."""
    go_dir = dist_dir / "go"
    go_dir.mkdir(parents=True, exist_ok=True)
    routes: list[dict[str, Any]] = []

    for tool in tools:
        target = tool["affiliate_url"]
        escaped_target = html.escape(target, quote=True)
        escaped_name = html.escape(tool["name"])
        redirect_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="robots" content="noindex, nofollow" />
  <meta http-equiv="refresh" content="0; url={escaped_target}" />
  <title>Redirecting to {escaped_name}...</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #0b0f19; color: #e5e7eb; display: grid; place-items: center; min-height: 100vh; margin: 0; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 28px; max-width: 460px; text-align: center; }}
    a {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>Opening {escaped_name}...</h2>
    <p>Taking you to the verified free-tier offer. If nothing happens automatically, click below:</p>
    <p><a href="{escaped_target}" rel="sponsored noopener noreferrer">Continue to {escaped_name} &rarr;</a></p>
  </div>
  <script>window.location.replace({json.dumps(target)});</script>
</body>
</html>
"""
        out_path = go_dir / f"{tool['id']}.html"
        out_path.write_text(redirect_html, encoding="utf-8")
        routes.append(
            {
                "tool_id": tool["id"],
                "tool_name": tool["name"],
                "local_route": f"go/{tool['id']}.html",
                "target_url": target,
                "estimated_epc_usd": tool.get("estimated_epc_usd", 0.5),
                "commission_notes": tool.get("commission_notes", ""),
            }
        )
    return routes


def build_digital_product_bundle(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    dist_dir: Path,
) -> dict[str, Any]:
    """Compile a 4-product digital storefront (Markdown packs, catalog.json, and storefront HTML)."""
    products_dir = dist_dir / "products"
    products_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    site_name = settings.get("site_name", "StackPulse AI")
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")
    mon = settings.get("monetization", {})
    title = mon.get("digital_product_title", "2026 Zero-Cost Cloud & AI Stack Blueprint + Automation Prompt Pack")
    blueprint_checkout = mon.get("digital_product_checkout_url", "https://hotspot41.gumroad.com/l/ryqznu")
    sponsor_checkout = mon.get("featured_sponsor_checkout_url", "https://hotspot41.gumroad.com/l/lcpwob")
    blueprint_price = mon.get("digital_product_price_usd", 19)
    sponsor_price = mon.get("featured_sponsor_price_usd", 49)

    # Product 1: Full Zero-Cost Stack Blueprint ($19)
    lines = [
        f"# {title}",
        f"*Compiled automatically on {generated_at} by {site_name}*",
        "",
        "## 1. Zero-Investment Cloud Stack Matrix ($0/mo Fixed Cost)",
        "| Tool | Category | Free Tier Limits | Paid Entry | Open-Source Escape Hatch |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    sorted_tools = sorted(tools, key=lambda t: t["score"], reverse=True)
    for tool in sorted_tools:
        lines.append(
            f"| {tool['name']} | {tool['category']} | {tool['free_tier_limits']} | "
            f"{tool['paid_start_price']} | {tool['open_source_alt']} |"
        )

    lines.extend(["", "## 2. Live Ecosystem Signals & Opportunity Angles"])
    for idx, sig in enumerate(signals[:8], start=1):
        lines.append(f"{idx}. **[{sig['topic']}] {sig['title']}** ({sig['source']}, score: {sig['score']})")
        lines.append(f"   - Angle: {sig['summary']}")

    lines.extend(
        [
            "",
            "## 3. Ready-to-Use AI Synthesis Prompt Templates",
            "### Prompt A: High-Converting SaaS Comparison Matrix",
            "```text",
            "Compare [Tool A] vs [Tool B] specifically for solo founders starting with $0 capital.",
            "Output: 1) Free-tier breaking point, 2) Exact monthly cost at 10k users, 3) 3-step migration checklist.",
            "```",
            "### Prompt B: Programmatic SEO Alternatives Brief",
            "```text",
            "List the top 3 free-tier and open-source alternatives to [Expensive SaaS] for developers.",
            "Highlight setup time, vendor lock-in risks, and ideal use case for each.",
            "```",
        ]
    )
    (products_dir / "zero-cost-stack-blueprint.md").write_text("\n".join(lines), encoding="utf-8")

    # Product 2: Free 2026 Developer Free-Tier Cheat Sheet & TCO Calculator ($0 Lead Magnet)
    cheat_lines = [
        f"# Free 2026 Developer Free-Tier Cheat Sheet & TCO Calculator",
        f"*Updated {generated_at} by {site_name} — Share freely!*",
        "",
        "Launch full-stack AI apps, databases, analytics, and payments at **$0.00/month**.",
        "",
        "## Quick-Launch $0 Stack Picks (Direct Free-Tier Links)",
    ]
    for tool in sorted_tools[:12]:
        cheat_lines.append(
            f"- **{tool['name']}** ({tool['category']}) — {tool['free_tier_limits']} "
            f"([Open Free Tier]({base_url}/go/{tool['id']}.html))"
        )
    cheat_lines.extend(
        [
            "",
            "## Monthly TCO Benchmark (0 to 10,000 Monthly Visitors)",
            "| Component | Recommended $0 Tool | Monthly Cost at MVP |",
            "| :--- | :--- | :---: |",
            "| Static Hosting & Edge | GitHub Pages / Cloudflare Pages | **$0** |",
            "| Daily Compute / Cron | GitHub Actions (Public Repo) | **$0** |",
            "| AI Reasoning API | Google Gemini 3.5 Flash-Lite / Groq | **$0** |",
            "| Edge SQLite / Postgres | Turso / Supabase / Neon | **$0** |",
            "| Global Checkout & Tax | Gumroad / Polar.sh | **$0 fixed** |",
            "| Product Analytics | PostHog (1M events/mo) | **$0** |",
            "",
            f"---",
            f"**Want all {len(tools)} tools, live opportunity angles, and AI prompt packs?** "
            f"[Upgrade to the Full 2026 Blueprint (${blueprint_price})]({blueprint_checkout})",
        ]
    )
    (products_dir / "free-tier-cheatsheet.md").write_text("\n".join(cheat_lines), encoding="utf-8")

    # Product 3: Autonomous GitHub Actions & Make.com AI Agent Blueprint Pack ($19 / Make Promo)
    make_tool = next((t for t in tools if t["id"] == "make-automation"), None)
    make_url = make_tool["affiliate_url"] if make_tool else f"{base_url}/go/make-automation.html"
    agent_lines = [
        "# Autonomous GitHub Actions & Make.com AI Agent Blueprint Pack",
        f"*Compiled {generated_at} by {site_name}*",
        "",
        "Turn zero-cost cloud runners into an automated research, content, and social promotion system.",
        "",
        "## Architecture Blueprint 1: GitHub Actions Daily Cron Agent",
        "1. Schedule `0 6,18 * * *` on Ubuntu runner (`0` external server cost).",
        "2. Fetch Hacker News + GitHub Search trends via zero-auth REST endpoints.",
        "3. Synthesize comparisons using Gemini Free Tier (`gemini-3.5-flash-lite`) + deterministic fallback.",
        "4. Build static HTML, RSS/JSON feeds, `llms.txt`, and auto-ping IndexNow.",
        "",
        "## Architecture Blueprint 2: Make.com Zero-Cost Social Distribution Scenario",
        f"1. **Create a free Make.com account (includes 1-month Core promo / 10,000 credits):** {make_url}",
        f"2. **Trigger Module:** RSS Watch Feed Items pointing to `{base_url}/feed.xml` (or Webhooks -> Custom Webhook).",
        "3. **Router Module:** Fan out each daily update simultaneously to X/Twitter, LinkedIn, Mastodon, Discord, and Buffer.",
        "4. **Attribution:** Append `?utm_source=make_auto` or route CTAs through `/go/<tool-id>.html`.",
        "",
        f"---",
        f"**Includes full prompt templates & config exports:** [Get the Bundle on Gumroad (${blueprint_price})]({blueprint_checkout})",
    ]
    (products_dir / "ai-agent-workflow-templates.md").write_text("\n".join(agent_lines), encoding="utf-8")

    products_catalog = [
        {
            "id": "zero-cost-stack-blueprint",
            "title": title,
            "price_usd": blueprint_price,
            "badge": "Best Seller",
            "description": f"Complete verified free-tier matrix across {len(tools)} developer & AI tools, live market signals, and ready-to-use synthesis prompts.",
            "checkout_url": blueprint_checkout,
            "cta_label": f"Buy on Gumroad (${blueprint_price})",
            "file": "products/zero-cost-stack-blueprint.md",
        },
        {
            "id": "free-tier-cheatsheet",
            "title": "Free 2026 Developer Free-Tier Cheat Sheet & TCO Calculator",
            "price_usd": 0,
            "badge": "Free Download",
            "description": "Zero-cost quick-start reference sheet with direct verified free-tier routes and 10k-visitor TCO cost breakdown.",
            "checkout_url": "free-tier-cheatsheet.md",
            "cta_label": "Download Free Cheat Sheet",
            "file": "products/free-tier-cheatsheet.md",
        },
        {
            "id": "ai-agent-workflow-templates",
            "title": "Autonomous GitHub Actions & Make.com AI Agent Blueprint Pack",
            "price_usd": blueprint_price,
            "badge": "Automation Pack",
            "description": "Step-by-step blueprints to connect GitHub Actions, RSS feeds, and Make.com social auto-distribution at $0 overhead.",
            "checkout_url": blueprint_checkout,
            "cta_label": f"Get Agent Pack (${blueprint_price})",
            "file": "products/ai-agent-workflow-templates.md",
            "secondary_url": "../go/make-automation.html",
            "secondary_label": "Claim Free Make.com Promo",
        },
        {
            "id": "featured-sponsor-slot",
            "title": f"{site_name} — Weekly Featured Tool & Newsletter Sponsor Slot",
            "price_usd": sponsor_price,
            "badge": "B2B Sponsorship",
            "description": "Pin your DevTool, SaaS, or AI product across our homepage directory header, RSS feed, and automated developer digest.",
            "checkout_url": sponsor_checkout,
            "cta_label": f"Book Sponsor Slot (${sponsor_price})",
            "file": "",
        },
    ]

    cards_html = ""
    for prod in products_catalog:
        price_str = "FREE ($0)" if prod["price_usd"] == 0 else f"${prod['price_usd']}"
        sec_btn = ""
        if prod.get("secondary_url"):
            sec_btn = (
                f'<a class="btn btn-secondary" href="{html.escape(prod["secondary_url"], quote=True)}">'
                f'{html.escape(prod["secondary_label"])}</a>'
            )
        dl_link = ""
        if prod["file"] and prod["price_usd"] > 0:
            fname = prod["file"].split("/")[-1]
            dl_link = f'<p class="meta" style="margin-top:10px;">Preview file: <a href="{html.escape(fname, quote=True)}">{html.escape(fname)}</a></p>'
        cards_html += f"""
<article class="card">
  <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
    <span class="pill">{html.escape(prod['badge'])}</span>
    <span class="score">{html.escape(price_str)}</span>
  </div>
  <h2 style="font-size:1.2rem; margin:14px 0 8px;">{html.escape(prod['title'])}</h2>
  <p class="meta">{html.escape(prod['description'])}</p>
  <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:16px;">
    <a class="btn btn-green" href="{html.escape(prod['checkout_url'], quote=True)}">{html.escape(prod['cta_label'])} &rarr;</a>
    {sec_btn}
  </div>
  {dl_link}
</article>
"""

    storefront_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Digital Products &amp; Blueprints | {html.escape(site_name)}</title>
  <meta name="description" content="Download free $0 cheat sheets, AI automation blueprints, and sponsor slots from {html.escape(site_name, quote=True)}." />
  <style>
    :root {{ --bg:#070b14; --surface:#0f172a; --surface-2:#1e293b; --border:#334155; --text:#f1f5f9; --muted:#94a3b8; --accent:#38bdf8; --accent-2:#22c55e; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
    a {{ color:var(--accent); text-decoration:none; }}
    .container {{ max-width:1100px; margin:0 auto; padding:0 20px; }}
    header {{ border-bottom:1px solid var(--border); background:rgba(15,23,42,0.92); padding:14px 0; }}
    .nav {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px; }}
    .nav-links {{ display:flex; gap:18px; flex-wrap:wrap; font-size:0.92rem; }}
    .nav-links a {{ color:var(--muted); font-weight:500; }}
    .hero {{ padding:42px 0 28px; border-bottom:1px solid var(--border); }}
    .grid {{ display:grid; gap:20px; grid-template-columns:repeat(auto-fit, minmax(290px, 1fr)); margin:28px 0; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:22px; }}
    .pill {{ display:inline-block; font-size:0.76rem; font-weight:700; text-transform:uppercase; color:var(--accent); background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.35); padding:3px 10px; border-radius:999px; }}
    .score {{ font-weight:800; color:var(--accent-2); background:rgba(34,197,94,0.12); padding:3px 10px; border-radius:6px; font-size:0.86rem; }}
    .meta {{ color:var(--muted); font-size:0.92rem; }}
    .btn {{ display:inline-block; background:var(--accent); color:#04111f; font-weight:700; padding:10px 16px; border-radius:8px; font-size:0.92rem; }}
    .btn-green {{ background:var(--accent-2); color:#052e16; }}
    .btn-secondary {{ background:var(--surface-2); color:var(--text); border:1px solid var(--border); }}
  </style>
</head>
<body>
  <header>
    <div class="container nav">
      <a href="../index.html" style="font-weight:800; color:#fff;">{html.escape(site_name)} <span style="color:var(--accent);">$0 Stack</span></a>
      <nav class="nav-links">
        <a href="../index.html">Directory</a>
        <a href="index.html" style="color:#fff;">Products ({len(products_catalog)})</a>
        <a href="../promotions/index.html">Promotion Hub</a>
        <a href="../newsletter/latest-issue.html">Newsletter</a>
        <a href="../dashboard.html">Dashboard</a>
      </nav>
    </div>
  </header>
  <main class="container">
    <section class="hero">
      <span class="pill">Digital Storefront &bull; Instant Delivery</span>
      <h1 style="margin:12px 0 10px;">Playbooks, Automation Packs &amp; Sponsor Slots</h1>
      <p class="meta">Zero-cost lead magnets and ready-to-deploy blueprints compiled automatically from {len(tools)} verified SaaS &amp; AI tools.</p>
    </section>
    <section class="grid">{cards_html}</section>
  </main>
</body>
</html>
"""
    (products_dir / "index.html").write_text(storefront_html, encoding="utf-8")

    meta = {
        "title": title,
        "price_usd": blueprint_price,
        "checkout_url": blueprint_checkout,
        "compiled_at": generated_at,
        "tools_included": len(tools),
        "signals_included": len(signals[:8]),
        "markdown_file": "products/zero-cost-stack-blueprint.md",
        "storefront_html": "products/index.html",
        "product_count": len(products_catalog),
        "products": products_catalog,
    }
    (products_dir / "catalog.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def build_newsletter_issue(
    settings: dict[str, Any],
    editorial: dict[str, Any],
    signals: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    dist_dir: Path,
) -> dict[str, Any]:
    """Generate a ready-to-send HTML & Markdown newsletter issue, optionally pushing to Buttondown."""
    nl_dir = dist_dir / "newsletter"
    nl_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mon = settings.get("monetization", {})

    top_affiliate = max(tools, key=lambda t: t.get("estimated_epc_usd", 0))
    signal_items_html = "\n".join(
        f"<li><strong>[{html.escape(s['topic'])}]</strong> "
        f"<a href='{html.escape(s['url'], quote=True)}'>{html.escape(s['title'])}</a> "
        f"({html.escape(s['source'])} &bull; {s['score']} pts)</li>"
        for s in signals[:5]
    )

    newsletter_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(editorial['headline'])}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 24px; }}
    .wrap {{ max-width: 640px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; }}
    .badge {{ display: inline-block; background: #0ea5e9; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px; }}
    .cta {{ display: inline-block; background: #0f172a; color: #ffffff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 12px; }}
    .sponsor {{ background: #f1f5f9; border-left: 4px solid #0ea5e9; padding: 14px 16px; border-radius: 6px; margin: 20px 0; }}
  </style>
</head>
<body>
  <div class="wrap">
    <span class="badge">{html.escape(settings['site_name'])} Digest &bull; {date_str}</span>
    <h1>{html.escape(editorial['headline'])}</h1>
    <p>{html.escape(editorial['intro'])}</p>

    <div class="sponsor">
      <strong>Featured Zero-Cost Stack Pick: {html.escape(top_affiliate['name'])}</strong>
      <p>{html.escape(top_affiliate['tagline'])} Free tier: {html.escape(top_affiliate['free_tier_limits'])}.</p>
      <a href="../go/{html.escape(top_affiliate['id'], quote=True)}.html">Explore {html.escape(top_affiliate['name'])} Free Tier &rarr;</a>
    </div>

    <h2>Top Ecosystem Signals</h2>
    <ul>
      {signal_items_html}
    </ul>

    <h2>Actionable $0 Monetization Play</h2>
    <p>{html.escape(editorial['actionable_play'])}</p>

    <hr />
    <p><strong>Want the complete blueprint &amp; automation prompt pack?</strong></p>
    <a class="cta" href="{html.escape(mon.get('digital_product_checkout_url', '#'), quote=True)}">Get the Blueprint (${mon.get('digital_product_price_usd', 19)}) &rarr;</a>
    <p style="font-size: 12px; color: #64748b; margin-top: 24px;">
      Sponsor this newsletter slot for ${mon.get('featured_sponsor_price_usd', 49)}:
      <a href="{html.escape(mon.get('featured_sponsor_checkout_url', '#'), quote=True)}">Book Sponsor Slot</a>
    </p>
  </div>
</body>
</html>
"""
    html_path = nl_dir / "latest-issue.html"
    html_path.write_text(newsletter_html, encoding="utf-8")

    # Optional live Buttondown draft push if BUTTONDOWN_API_KEY is configured
    dispatch_status = "saved-locally"
    bd_key = os.environ.get(mon.get("newsletter_provider_webhook_env", "BUTTONDOWN_API_KEY"), "").strip()
    if bd_key:
        try:
            req = urllib.request.Request(
                "https://api.buttondown.com/v1/emails",
                data=json.dumps(
                    {
                        "subject": editorial["headline"],
                        "body": f"{editorial['intro']}\n\n## Actionable Play\n{editorial['actionable_play']}",
                        "status": "draft",
                    }
                ).encode("utf-8"),
                headers={
                    "Authorization": f"Token {bd_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if 200 <= resp.status < 300:
                    dispatch_status = "pushed-buttondown-draft"
        except (urllib.error.URLError, TimeoutError, OSError):
            dispatch_status = "buttondown-error-saved-locally"

    return {
        "date": date_str,
        "headline": editorial["headline"],
        "html_file": "newsletter/latest-issue.html",
        "dispatch_status": dispatch_status,
        "editorial_provider": editorial.get("provider", "deterministic"),
    }
