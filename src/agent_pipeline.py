"""Autonomous orchestrator CLI for the Zero-Cost Income Engine."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm_brain import ZeroCostLLMBrain
from src.monetization_engine import (
    build_affiliate_redirects,
    build_digital_product_bundle,
    build_newsletter_issue,
)
from src.signal_ingestor import ingest_signals
from src.site_builder import build_full_site


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_pipeline(
    project_root: Path,
    mode: str = "full",
    offline: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end ingestion, AI synthesis, monetization packaging, and pSEO build."""
    config_dir = project_root / "config"
    data_dir = project_root / "data"
    dist_dir = project_root / "dist"

    settings = load_json(config_dir / "settings.json")
    affiliates = load_json(config_dir / "affiliates.json")
    tools: list[dict[str, Any]] = affiliates.get("tools", [])

    # 1. Ingest trending ecosystem signals
    signal_payload = ingest_signals(settings, data_dir=data_dir, offline=offline)

    if mode == "ingest":
        return {"mode": mode, "signals": signal_payload}

    # 2. Initialize zero-cost AI synthesis brain
    brain = ZeroCostLLMBrain(settings, offline=offline)

    # 3. Build monetization assets (affiliate redirects, digital product bundle, newsletter)
    redirect_routes = build_affiliate_redirects(tools, dist_dir=dist_dir)
    product_meta = build_digital_product_bundle(
        settings, tools=tools, signals=signal_payload["signals"], dist_dir=dist_dir
    )
    editorial = brain.synthesize_newsletter_editorial(signal_payload["signals"], tools)
    newsletter_meta = build_newsletter_issue(
        settings, editorial=editorial, signals=signal_payload["signals"], tools=tools, dist_dir=dist_dir
    )

    # 4. Compile full Programmatic SEO static web platform
    site_stats = build_full_site(
        settings=settings,
        tools=tools,
        signal_payload=signal_payload,
        brain=brain,
        redirect_routes=redirect_routes,
        product_meta=product_meta,
        newsletter_meta=newsletter_meta,
        dist_dir=dist_dir,
    )

    # 5. Persist audit trail in data/run_history.json
    data_dir.mkdir(parents=True, exist_ok=True)
    history_path = data_dir / "run_history.json"
    history: list[dict[str, Any]] = []
    if history_path.exists():
        try:
            loaded = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = loaded
        except ValueError:
            history = []

    run_summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "offline": offline,
        "ingestion_mode": signal_payload["ingestion_mode"],
        "signals_collected": signal_payload["signal_count"],
        "llm_usage": brain.providers_used,
        "site_stats": site_stats,
        "product_compiled": product_meta["markdown_file"],
        "newsletter_status": newsletter_meta["dispatch_status"],
    }
    history.append(run_summary)
    history = history[-30:]  # keep latest 30 runs to prevent repo bloat
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return run_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the StackPulse AI Zero-Cost Income Engine")
    parser.add_argument(
        "--mode",
        choices=["full", "ingest"],
        default="full",
        help="Execution mode (full builds complete pSEO site + products; ingest fetches signals only)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip live network and LLM API calls and use curated seed data + deterministic synthesis",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    summary = run_pipeline(project_root=project_root, mode=args.mode, offline=args.offline)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
