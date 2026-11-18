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
    """Compile a ready-to-sell digital blueprint package (Markdown + JSON) for Gumroad / Lemon Squeezy."""
    products_dir = dist_dir / "products"
    products_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mon = settings.get("monetization", {})
    title = mon.get("digital_product_title", "Zero-Cost Cloud & AI Stack Blueprint")

    lines = [
        f"# {title}",
        f"*Compiled automatically on {generated_at} by {settings.get('site_name', 'StackPulse AI')}*",
        "",
        "## 1. Zero-Investment Cloud Stack Matrix ($0/mo Fixed Cost)",
        "| Tool | Category | Free Tier Limits | Paid Entry | Open-Source Escape Hatch |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for tool in sorted(tools, key=lambda t: t["score"], reverse=True):
        lines.append(
            f"| {tool['name']} | {tool['category']} | {tool['free_tier_limits']} | "
            f"{tool['paid_start_price']} | {tool['open_source_alt']} |"
        )

    lines.extend(
        [
            "",
            "## 2. Live Ecosystem Signals & Opportunity Angles",
        ]
    )
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

    md_path = products_dir / "zero-cost-stack-blueprint.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    meta = {
        "title": title,
        "price_usd": mon.get("digital_product_price_usd", 19),
        "checkout_url": mon.get("digital_product_checkout_url", ""),
        "compiled_at": generated_at,
        "tools_included": len(tools),
        "signals_included": len(signals[:8]),
        "markdown_file": "products/zero-cost-stack-blueprint.md",
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
