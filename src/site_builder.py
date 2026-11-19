"""Programmatic SEO static site compiler for StackPulse AI."""

from __future__ import annotations

import html
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm_brain import ZeroCostLLMBrain

BASE_CSS = """
:root {
  --bg: #070b14;
  --surface: #0f172a;
  --surface-2: #1e293b;
  --border: #334155;
  --text: #f1f5f9;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --accent-2: #22c55e;
  --warn: #f59e0b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.container { max-width: 1120px; margin: 0 auto; padding: 0 20px; }
header.nav {
  border-bottom: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.92);
  position: sticky;
  top: 0;
  backdrop-filter: blur(8px);
  z-index: 20;
}
.nav-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  gap: 12px;
}
.brand { font-weight: 800; font-size: 1.15rem; color: #fff; letter-spacing: -0.02em; }
.brand span { color: var(--accent); }
.nav-links { display: flex; gap: 18px; font-size: 0.92rem; flex-wrap: wrap; }
.nav-links a { color: var(--muted); font-weight: 500; }
.nav-links a:hover { color: #fff; }
.hero { padding: 48px 0 32px; border-bottom: 1px solid var(--border); }
.pill {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent);
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  padding: 4px 12px;
  border-radius: 999px;
}
h1 { font-size: clamp(1.8rem, 3.6vw, 2.8rem); line-height: 1.15; margin: 14px 0 12px; }
h2 { font-size: 1.45rem; margin: 32px 0 14px; }
h3 { font-size: 1.1rem; margin: 0 0 8px; }
.lead { color: var(--muted); font-size: 1.08rem; max-width: 740px; margin: 0 0 22px; }
.btn {
  display: inline-block;
  background: var(--accent);
  color: #04111f;
  font-weight: 700;
  padding: 10px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
}
.btn:hover { opacity: 0.92; text-decoration: none; }
.btn-secondary {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
}
.btn-green { background: var(--accent-2); color: #052e16; }
.grid { display: grid; gap: 18px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.grid-2 { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
.meta { font-size: 0.84rem; color: var(--muted); }
.score {
  font-weight: 800;
  color: var(--accent-2);
  background: rgba(34, 197, 94, 0.12);
  padding: 2px 9px;
  border-radius: 6px;
  font-size: 0.85rem;
}
table { width: 100%; border-collapse: collapse; margin: 16px 0; background: var(--surface); border-radius: 10px; overflow: hidden; }
th, td { border: 1px solid var(--border); padding: 12px 14px; text-align: left; vertical-align: top; }
th { background: var(--surface-2); font-size: 0.9rem; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 22px; }
.filter-btn {
  background: var(--surface);
  color: var(--muted);
  border: 1px solid var(--border);
  padding: 7px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.86rem;
}
.filter-btn.active { background: var(--accent); color: #04111f; border-color: var(--accent); font-weight: 700; }
.search-input {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 9px 14px;
  border-radius: 8px;
  min-width: 240px;
  font-size: 0.94rem;
}
.banner {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.14), rgba(34, 197, 94, 0.10));
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 12px;
  padding: 22px;
  margin: 26px 0;
}
footer {
  margin-top: 56px;
  padding: 28px 0 42px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.88rem;
}
"""


def _render_shell(
    title: str,
    description: str,
    body_html: str,
    settings: dict[str, Any],
    root_prefix: str = "",
    json_ld: dict[str, Any] | None = None,
) -> str:
    site_name = settings.get("site_name", "StackPulse AI")
    base_url = settings.get("base_url", "https://gamehotspot62.github.io/zero-cost-income-engine").rstrip("/")
    ld_block = ""
    if json_ld:
        ld_block = f'<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} | {html.escape(site_name)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}" />
  <link rel="alternate" type="application/rss+xml" title="{html.escape(site_name, quote=True)} RSS" href="{html.escape(base_url + '/feed.xml', quote=True)}" />
  <link rel="alternate" type="application/feed+json" title="{html.escape(site_name, quote=True)} JSON Feed" href="{html.escape(base_url + '/feed.json', quote=True)}" />
  {ld_block}
  <style>{BASE_CSS}</style>
</head>
<body>
  <header class="nav">
    <div class="container nav-inner">
      <a class="brand" href="{root_prefix}index.html">{html.escape(site_name)} <span>$0 Stack</span></a>
      <nav class="nav-links">
        <a href="{root_prefix}index.html#tools">Tools</a>
        <a href="{root_prefix}index.html#comparisons">Comparisons</a>
        <a href="{root_prefix}products/index.html">Products</a>
        <a href="{root_prefix}promotions/index.html">Promotion Hub</a>
        <a href="{root_prefix}newsletter/latest-issue.html">Newsletter</a>
        <a href="{root_prefix}dashboard.html">Dashboard</a>
      </nav>
    </div>
  </header>
  <main class="container">
    {body_html}
  </main>
  <footer>
    <div class="container">
      <p><strong>{html.escape(site_name)}</strong> &mdash; Automated zero-cost research, promotion &amp; comparison engine running on GitHub Actions. <a href="{root_prefix}feed.xml">RSS Feed</a> &bull; <a href="{root_prefix}llms.txt">llms.txt</a>. Some outbound links may earn a referral commission at zero cost to you.</p>
    </div>
  </footer>
</body>
</html>
"""


def _faq_schema(faqs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in faqs
        ],
    }


def _build_comparison_pages(
    tools: list[dict[str, Any]],
    brain: ZeroCostLLMBrain,
    settings: dict[str, Any],
    dist_dir: Path,
) -> list[dict[str, Any]]:
    compare_dir = dist_dir / "compare"
    compare_dir.mkdir(parents=True, exist_ok=True)
    by_category: dict[str, list[dict[str, Any]]] = {}
    for tool in tools:
        by_category.setdefault(tool["category"], []).append(tool)

    built_pages: list[dict[str, Any]] = []
    for category, cat_tools in by_category.items():
        for tool_a, tool_b in itertools.combinations(cat_tools, 2):
            slug = f"{tool_a['id']}-vs-{tool_b['id']}.html"
            rel_path = f"compare/{slug}"
            synthesis = brain.synthesize_comparison(tool_a, tool_b)
            faqs = synthesis["faqs"]
            faq_html = "".join(
                f"<div class='card' style='margin-bottom:12px;'><h3>{html.escape(f['q'])}</h3><p>{html.escape(f['a'])}</p></div>"
                for f in faqs
            )
            pros_a = "".join(f"<li>{html.escape(p)}</li>" for p in tool_a["pros"])
            pros_b = "".join(f"<li>{html.escape(p)}</li>" for p in tool_b["pros"])

            body = f"""
<section class="hero">
  <span class="pill">{html.escape(category)} Comparison</span>
  <h1>{html.escape(tool_a['name'])} vs {html.escape(tool_b['name'])}: 2026 Free Tier &amp; Cost Breakdown</h1>
  <p class="lead">{html.escape(synthesis['verdict'])}</p>
  <div style="display:flex; gap:12px; flex-wrap:wrap;">
    <a class="btn" href="../go/{html.escape(tool_a['id'], quote=True)}.html" rel="sponsored noopener">Try {html.escape(tool_a['name'])} Free &rarr;</a>
    <a class="btn btn-secondary" href="../go/{html.escape(tool_b['id'], quote=True)}.html" rel="sponsored noopener">Try {html.escape(tool_b['name'])} Free &rarr;</a>
  </div>
</section>

<section>
  <h2>Head-to-Head Specification Matrix</h2>
  <table>
    <thead>
      <tr>
        <th>Dimension</th>
        <th>{html.escape(tool_a['name'])}</th>
        <th>{html.escape(tool_b['name'])}</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>Zero-Cost Rating</strong></td><td><span class="score">{tool_a['score']}/10</span></td><td><span class="score">{tool_b['score']}/10</span></td></tr>
      <tr><td><strong>Free Tier Quota</strong></td><td>{html.escape(tool_a['free_tier_limits'])}</td><td>{html.escape(tool_b['free_tier_limits'])}</td></tr>
      <tr><td><strong>First Paid Tier</strong></td><td>{html.escape(tool_a['paid_start_price'])}</td><td>{html.escape(tool_b['paid_start_price'])}</td></tr>
      <tr><td><strong>Best Built For</strong></td><td>{html.escape(tool_a['best_for'])}</td><td>{html.escape(tool_b['best_for'])}</td></tr>
      <tr><td><strong>Open-Source Escape Hatch</strong></td><td>{html.escape(tool_a['open_source_alt'])}</td><td>{html.escape(tool_b['open_source_alt'])}</td></tr>
    </tbody>
  </table>
</section>

<section class="grid-2">
  <div class="card">
    <h3>Why Pick {html.escape(tool_a['name'])}</h3>
    <ul>{pros_a}</ul>
    <a class="btn" href="../go/{html.escape(tool_a['id'], quote=True)}.html" rel="sponsored noopener">Launch {html.escape(tool_a['name'])}</a>
  </div>
  <div class="card">
    <h3>Why Pick {html.escape(tool_b['name'])}</h3>
    <ul>{pros_b}</ul>
    <a class="btn" href="../go/{html.escape(tool_b['id'], quote=True)}.html" rel="sponsored noopener">Launch {html.escape(tool_b['name'])}</a>
  </div>
</section>

<section class="banner">
  <h2>Total Cost of Ownership &amp; Migration Advice</h2>
  <p>{html.escape(synthesis['tco_analysis'])}</p>
  <p class="meta"><strong>Architect Tip:</strong> {html.escape(synthesis['migration_tip'])}</p>
</section>

<section>
  <h2>Frequently Asked Questions</h2>
  {faq_html}
</section>
"""
            page_html = _render_shell(
                title=f"{tool_a['name']} vs {tool_b['name']} Free Tier",
                description=f"Compare {tool_a['name']} and {tool_b['name']} free-tier limits, scaling prices, and open-source alternatives.",
                body_html=body,
                settings=settings,
                root_prefix="../",
                json_ld=_faq_schema(faqs),
            )
            (compare_dir / slug).write_text(page_html, encoding="utf-8")
            built_pages.append(
                {
                    "title": f"{tool_a['name']} vs {tool_b['name']}",
                    "category": category,
                    "path": rel_path,
                    "winner": synthesis["winner_name"],
                    "provider": synthesis["provider"],
                }
            )
    return built_pages


def _build_alternatives_pages(
    tools: list[dict[str, Any]],
    brain: ZeroCostLLMBrain,
    settings: dict[str, Any],
    dist_dir: Path,
) -> list[dict[str, Any]]:
    alt_dir = dist_dir / "alternatives"
    alt_dir.mkdir(parents=True, exist_ok=True)
    built_pages: list[dict[str, Any]] = []

    for tool in tools:
        peers = [t for t in tools if t["category"] == tool["category"] and t["id"] != tool["id"]]
        if not peers:
            peers = [t for t in tools if t["id"] != tool["id"]][:3]
        peers_sorted = sorted(peers, key=lambda t: t["score"], reverse=True)
        synthesis = brain.synthesize_alternatives(tool, peers_sorted)
        slug = f"{tool['id']}-alternatives.html"
        rel_path = f"alternatives/{slug}"

        cards_html = ""
        for rank, peer in enumerate(peers_sorted, start=1):
            cards_html += f"""
<div class="card">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span class="pill">#{rank} Alternative</span>
    <span class="score">{peer['score']}/10</span>
  </div>
  <h3 style="margin-top:12px;">{html.escape(peer['name'])}</h3>
  <p class="meta">{html.escape(peer['tagline'])}</p>
  <p><strong>Free Tier:</strong> {html.escape(peer['free_tier_limits'])}</p>
  <p><strong>Paid Entry:</strong> {html.escape(peer['paid_start_price'])}</p>
  <div style="display:flex; gap:10px; flex-wrap:wrap;">
    <a class="btn" href="../go/{html.escape(peer['id'], quote=True)}.html" rel="sponsored noopener">Try Free Tier &rarr;</a>
  </div>
</div>
"""

        faq_html = "".join(
            f"<div class='card' style='margin-bottom:12px;'><h3>{html.escape(f['q'])}</h3><p>{html.escape(f['a'])}</p></div>"
            for f in synthesis["faqs"]
        )

        body = f"""
<section class="hero">
  <span class="pill">{html.escape(tool['category'])} Alternatives</span>
  <h1>Best Free &amp; Open-Source Alternatives to {html.escape(tool['name'])} (2026)</h1>
  <p class="lead">{html.escape(synthesis['why_switch'])}</p>
  <p class="meta">Self-hosted / open-source path: <strong>{html.escape(tool['open_source_alt'])}</strong></p>
</section>

<section>
  <h2>Top Ranked Zero-Cost Alternatives</h2>
  <div class="grid">{cards_html}</div>
</section>

<section>
  <h2>Migration FAQ</h2>
  {faq_html}
</section>
"""
        page_html = _render_shell(
            title=f"Best Free {tool['name']} Alternatives",
            description=f"Top free-tier and open-source alternatives to {tool['name']} including {synthesis['top_pick_name']}.",
            body_html=body,
            settings=settings,
            root_prefix="../",
            json_ld=_faq_schema(synthesis["faqs"]),
        )
        (alt_dir / slug).write_text(page_html, encoding="utf-8")
        built_pages.append(
            {
                "title": f"{tool['name']} Alternatives",
                "category": tool["category"],
                "path": rel_path,
                "top_pick": synthesis["top_pick_name"],
            }
        )
    return built_pages


def _build_index_page(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    alternatives: list[dict[str, Any]],
    dist_dir: Path,
) -> None:
    mon = settings.get("monetization", {})
    categories = settings.get("categories", [])

    cat_buttons = '<button class="filter-btn active" data-cat="ALL">All Categories</button>' + "".join(
        f'<button class="filter-btn" data-cat="{html.escape(c, quote=True)}">{html.escape(c)}</button>'
        for c in categories
    )

    tool_cards = ""
    for t in sorted(tools, key=lambda x: x["score"], reverse=True):
        tool_cards += f"""
<article class="card tool-card" data-cat="{html.escape(t['category'], quote=True)}" data-search="{html.escape((t['name'] + ' ' + t['category'] + ' ' + t['tagline']).lower(), quote=True)}">
  <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
    <span class="meta">{html.escape(t['category'])}</span>
    <span class="score">{t['score']}/10</span>
  </div>
  <h3 style="margin-top:8px;">{html.escape(t['name'])}</h3>
  <p class="meta">{html.escape(t['tagline'])}</p>
  <p style="font-size:0.9rem;"><strong>Free Tier:</strong> {html.escape(t['free_tier_limits'])}</p>
  <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">
    <a class="btn" href="go/{html.escape(t['id'], quote=True)}.html" rel="sponsored noopener">Get Free Tier &rarr;</a>
    <a class="btn btn-secondary" href="alternatives/{html.escape(t['id'], quote=True)}-alternatives.html">Alternatives</a>
  </div>
</article>
"""

    comp_links = "".join(
        f'<div class="card"><span class="meta">{html.escape(c["category"])}</span>'
        f'<h3 style="margin:6px 0;"><a href="{html.escape(c["path"], quote=True)}">{html.escape(c["title"])}</a></h3>'
        f'<p class="meta">Top pick: {html.escape(c["winner"])}</p></div>'
        for c in comparisons
    )

    signal_cards = "".join(
        f'<div class="card"><span class="pill">{html.escape(s["source"])} &bull; {s["score"]} pts</span>'
        f'<h3 style="margin-top:10px;"><a href="{html.escape(s["url"], quote=True)}" target="_blank" rel="noopener">{html.escape(s["title"])}</a></h3>'
        f'<p class="meta">{html.escape(s["summary"])}</p></div>'
        for s in signals[:6]
    )

    body = f"""
<section class="hero">
  <span class="pill">100% Autonomous &bull; $0 Infrastructure</span>
  <h1>Build &amp; Monetize Online with Verified $0 Free-Tier Stacks</h1>
  <p class="lead">
    {html.escape(settings.get('site_name', 'StackPulse AI'))} autonomously tracks developer ecosystems daily,
    compiles {len(comparisons)} head-to-head comparisons and {len(alternatives)} open-source migration guides,
    and updates automatically via GitHub Actions.
  </p>
  <div style="display:flex; gap:12px; flex-wrap:wrap;">
    <a class="btn btn-green" href="products/index.html">Explore 4 Digital Products &amp; Free Cheat Sheet</a>
    <a class="btn" href="{html.escape(mon.get('digital_product_checkout_url', '#'), quote=True)}">Get Blueprint Pack (${mon.get('digital_product_price_usd', 19)})</a>
    <a class="btn btn-secondary" href="promotions/index.html">Global Promotion Hub</a>
    <a class="btn btn-secondary" href="newsletter/latest-issue.html">AI Digest</a>
  </div>
</section>

<section id="tools">
  <h2>Zero-Cost Stack Directory ({len(tools)} Verified Tools)</h2>
  <div class="filter-bar">
    <input id="toolSearch" class="search-input" type="search" placeholder="Search Supabase, Gemini, Groq, Lemon Squeezy..." />
    {cat_buttons}
  </div>
  <div class="grid" id="toolGrid">{tool_cards}</div>
</section>

<section class="banner">
  <h2>Promote Your DevTool or Micro-SaaS Here</h2>
  <p>Reach technical founders actively comparing infrastructure and monetization tools. Instant self-serve slot booking.</p>
  <a class="btn" href="{html.escape(mon.get('featured_sponsor_checkout_url', '#'), quote=True)}">Book Featured Slot (${mon.get('featured_sponsor_price_usd', 49)}) &rarr;</a>
</section>

<section id="comparisons">
  <h2>Programmatic Head-to-Head Comparisons ({len(comparisons)} Pages)</h2>
  <div class="grid">{comp_links}</div>
</section>

<section id="signals">
  <h2>Latest Automated Web Signals</h2>
  <div class="grid">{signal_cards}</div>
</section>

<script>
(function () {{
  const buttons = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.tool-card');
  const search = document.getElementById('toolSearch');
  let activeCat = 'ALL';

  function applyFilter() {{
    const q = (search.value || '').trim().toLowerCase();
    cards.forEach(card => {{
      const matchesCat = activeCat === 'ALL' || card.dataset.cat === activeCat;
      const matchesText = !q || card.dataset.search.includes(q);
      card.style.display = (matchesCat && matchesText) ? '' : 'none';
    }});
  }}

  buttons.forEach(btn => {{
    btn.addEventListener('click', () => {{
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCat = btn.dataset.cat;
      applyFilter();
    }});
  }});
  search.addEventListener('input', applyFilter);
}})();
</script>
"""
    index_html = _render_shell(
        title="Zero-Cost Developer Stack & SaaS Free-Tier Engine",
        description=settings.get("site_tagline", ""),
        body_html=body,
        settings=settings,
        root_prefix="",
    )
    (dist_dir / "index.html").write_text(index_html, encoding="utf-8")


def _build_dashboard_page(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signal_payload: dict[str, Any],
    comparisons: list[dict[str, Any]],
    alternatives: list[dict[str, Any]],
    redirect_routes: list[dict[str, Any]],
    product_meta: dict[str, Any],
    newsletter_meta: dict[str, Any],
    brain: ZeroCostLLMBrain,
    dist_dir: Path,
) -> None:
    total_pages = 2 + len(comparisons) + len(alternatives) + len(redirect_routes) + 1
    avg_epc = sum(float(t.get("estimated_epc_usd", 0)) for t in tools) / max(len(tools), 1)
    needs_affiliate_setup = sum(1 for t in tools if "replace_me" in t["affiliate_url"])

    rows = ""
    for r in redirect_routes:
        status_badge = "Needs Your ID" if "replace_me" in r["target_url"] else "Ready"
        rows += (
            f"<tr><td>{html.escape(r['tool_name'])}</td>"
            f"<td><code>/{html.escape(r['local_route'])}</code></td>"
            f"<td>${r['estimated_epc_usd']:.2f}</td>"
            f"<td>{html.escape(r['commission_notes'])}</td>"
            f"<td>{status_badge}</td></tr>"
        )

    body = f"""
<section class="hero">
  <span class="pill">Owner Operations Console</span>
  <h1>Autonomous Income Engine Telemetry</h1>
  <p class="lead">Live build diagnostics for your $0-overhead programmatic SEO, affiliate routing, newsletter, and digital product pipeline.</p>
</section>

<section class="grid">
  <div class="card"><h3>Total Static Assets</h3><p style="font-size:2rem; font-weight:800; margin:6px 0;">{total_pages}</p><p class="meta">{len(comparisons)} comparisons &bull; {len(alternatives)} alternatives &bull; {len(redirect_routes)} redirects</p></div>
  <div class="card"><h3>Signal Ingestion Mode</h3><p style="font-size:1.5rem; font-weight:800; margin:6px 0;">{html.escape(signal_payload['ingestion_mode'])}</p><p class="meta">{signal_payload['signal_count']} signals processed at {html.escape(signal_payload['fetched_at'][:19])}Z</p></div>
  <div class="card"><h3>AI Synthesis Usage</h3><p style="font-size:1.25rem; font-weight:800; margin:6px 0;">Gemini: {brain.providers_used.get('gemini',0)} | Groq: {brain.providers_used.get('groq',0)}</p><p class="meta">Deterministic fallback syntheses: {brain.providers_used.get('deterministic',0)} ($0.00 cost)</p></div>
  <div class="card"><h3>Affiliate Setup Status</h3><p style="font-size:1.5rem; font-weight:800; margin:6px 0;">Avg Est. EPC: ${avg_epc:.2f}</p><p class="meta">{needs_affiliate_setup} URLs still have placeholder IDs in config/affiliates.json</p></div>
</section>

<section class="grid-2" style="margin-top:24px;">
  <div class="card">
    <h3>Digital Product Storefront ({product_meta.get('product_count', 1)} Offers)</h3>
    <p><strong>{html.escape(product_meta['title'])}</strong> (${product_meta['price_usd']}) + Free Cheat Sheet</p>
    <p class="meta">Compiled storefront: <code>products/index.html</code> ({product_meta['tools_included']} tools)</p>
    <a class="btn btn-secondary" href="products/index.html">Open Digital Storefront</a>
  </div>
  <div class="card">
    <h3>Newsletter &amp; Global Promotion Agent</h3>
    <p><strong>{html.escape(newsletter_meta['headline'])}</strong></p>
    <p class="meta">Dispatch status: <code>{html.escape(newsletter_meta['dispatch_status'])}</code></p>
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <a class="btn btn-secondary" href="newsletter/latest-issue.html">Preview Newsletter</a>
      <a class="btn btn-secondary" href="promotions/index.html">Global Promotion Hub</a>
    </div>
  </div>
</section>

<section>
  <h2>Affiliate Redirect Router Matrix</h2>
  <table>
    <thead><tr><th>Tool</th><th>Local Cloaked Route</th><th>Est. EPC</th><th>Program Notes</th><th>Config Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>
"""
    dash_html = _render_shell(
        title="Owner Telemetry Dashboard",
        description="Operational metrics for StackPulse AI automated income engine.",
        body_html=body,
        settings=settings,
        root_prefix="",
    )
    (dist_dir / "dashboard.html").write_text(dash_html, encoding="utf-8")


def _build_sitemap_and_robots(
    settings: dict[str, Any],
    comparisons: list[dict[str, Any]],
    alternatives: list[dict[str, Any]],
    dist_dir: Path,
) -> None:
    base_url = settings.get("base_url", "https://example.com").rstrip("/")
    rel_paths = [
        "index.html",
        "products/index.html",
        "promotions/index.html",
        "newsletter/latest-issue.html",
        "llms.txt",
    ]
    rel_paths.extend(c["path"] for c in comparisons)
    rel_paths.extend(a["path"] for a in alternatives)
    full_urls = [f"{base_url}/"] + [f"{base_url}/{path}" for path in rel_paths]

    url_entries = "\n".join(
        f"  <url>\n    <loc>{html.escape(loc)}</loc>\n  </url>"
        for loc in full_urls
    )
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_entries}
</urlset>
"""
    (dist_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (dist_dir / "sitemap-v2.xml").write_text(sitemap_xml, encoding="utf-8")
    (dist_dir / "sitemap.txt").write_text("\n".join(full_urls) + "\n", encoding="utf-8")
    (dist_dir / ".nojekyll").write_text("", encoding="utf-8")
    (dist_dir / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /go/\n"
        f"Sitemap: {base_url}/sitemap.xml\n"
        f"Sitemap: {base_url}/sitemap-v2.xml\n"
        f"Sitemap: {base_url}/sitemap.txt\n",
        encoding="utf-8",
    )
    verify_file = str(settings.get("google_site_verification_file", "")).strip()
    if verify_file:
        safe_name = Path(verify_file).name
        (dist_dir / safe_name).write_text(
            f"google-site-verification: {safe_name}\n",
            encoding="utf-8",
        )


def build_full_site(
    settings: dict[str, Any],
    tools: list[dict[str, Any]],
    signal_payload: dict[str, Any],
    brain: ZeroCostLLMBrain,
    redirect_routes: list[dict[str, Any]],
    product_meta: dict[str, Any],
    newsletter_meta: dict[str, Any],
    dist_dir: Path,
    return_details: bool = False,
) -> dict[str, Any]:
    """Compile all programmatic SEO pages, index, dashboard, sitemap, and robots.txt."""
    dist_dir.mkdir(parents=True, exist_ok=True)
    comparisons = _build_comparison_pages(tools, brain, settings, dist_dir)
    alternatives = _build_alternatives_pages(tools, brain, settings, dist_dir)
    _build_index_page(settings, tools, signal_payload["signals"], comparisons, alternatives, dist_dir)
    _build_dashboard_page(
        settings,
        tools,
        signal_payload,
        comparisons,
        alternatives,
        redirect_routes,
        product_meta,
        newsletter_meta,
        brain,
        dist_dir,
    )
    _build_sitemap_and_robots(settings, comparisons, alternatives, dist_dir)
    stats: dict[str, Any] = {
        "comparison_pages": len(comparisons),
        "alternatives_pages": len(alternatives),
        "redirect_pages": len(redirect_routes),
        "total_indexable_urls": 6 + len(comparisons) + len(alternatives),
    }
    if return_details:
        stats["_comparisons"] = comparisons
        stats["_alternatives"] = alternatives
    return stats
