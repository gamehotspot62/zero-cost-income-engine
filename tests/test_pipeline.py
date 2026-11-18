"""Automated test suite for the Zero-Cost Income Engine."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from src.agent_pipeline import run_pipeline
from src.llm_brain import ZeroCostLLMBrain
from src.setup_assistant import get_setup_status, set_affiliate_url, set_monetization_url
from src.signal_ingestor import ingest_signals

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestZeroCostIncomeEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="zc_income_test_"))
        shutil.copytree(PROJECT_ROOT / "config", self.temp_dir / "config")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_offline_signal_ingestion_fallback(self) -> None:
        settings = json.loads((self.temp_dir / "config" / "settings.json").read_text(encoding="utf-8"))
        payload = ingest_signals(settings, data_dir=self.temp_dir / "data", offline=True)
        self.assertEqual(payload["ingestion_mode"], "offline-seed")
        self.assertGreaterEqual(payload["signal_count"], 5)
        self.assertTrue((self.temp_dir / "data" / "latest_signals.json").exists())

    def test_deterministic_llm_synthesis(self) -> None:
        settings = json.loads((self.temp_dir / "config" / "settings.json").read_text(encoding="utf-8"))
        tools = json.loads((self.temp_dir / "config" / "affiliates.json").read_text(encoding="utf-8"))["tools"]
        brain = ZeroCostLLMBrain(settings, offline=True)
        result = brain.synthesize_comparison(tools[0], tools[1])
        self.assertEqual(result["provider"], "deterministic")
        self.assertIn("winner_id", result)
        self.assertEqual(len(result["faqs"]), 3)

    def test_full_end_to_end_pipeline_outputs(self) -> None:
        summary = run_pipeline(project_root=self.temp_dir, mode="full", offline=True)
        dist = self.temp_dir / "dist"

        self.assertGreaterEqual(summary["site_stats"]["comparison_pages"], 15)
        self.assertGreaterEqual(summary["site_stats"]["alternatives_pages"], 12)

        required_files = [
            dist / "index.html",
            dist / "dashboard.html",
            dist / "sitemap.xml",
            dist / "robots.txt",
            dist / "newsletter" / "latest-issue.html",
            dist / "products" / "zero-cost-stack-blueprint.md",
            dist / "products" / "catalog.json",
        ]
        for file_path in required_files:
            self.assertTrue(file_path.exists(), f"Missing generated file: {file_path}")
            self.assertGreater(file_path.stat().st_size, 100, f"Generated file too small: {file_path}")

        compare_files = list((dist / "compare").glob("*.html"))
        alt_files = list((dist / "alternatives").glob("*.html"))
        go_files = list((dist / "go").glob("*.html"))

        self.assertGreaterEqual(len(compare_files), 15)
        self.assertGreaterEqual(len(alt_files), 12)
        self.assertGreaterEqual(len(go_files), 12)

        # Verify Schema.org FAQPage JSON-LD inside a comparison page is valid JSON
        sample_compare = compare_files[0].read_text(encoding="utf-8")
        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            sample_compare,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Missing JSON-LD schema block")
        schema_obj = json.loads(match.group(1))
        self.assertEqual(schema_obj["@type"], "FAQPage")
        self.assertGreaterEqual(len(schema_obj["mainEntity"]), 2)

        # Verify sitemap files (xml, v2 xml, txt) and .nojekyll include generated pages
        sitemap_text = (dist / "sitemap.xml").read_text(encoding="utf-8")
        sitemap_v2_text = (dist / "sitemap-v2.xml").read_text(encoding="utf-8")
        sitemap_txt = (dist / "sitemap.txt").read_text(encoding="utf-8")
        self.assertEqual(sitemap_text, sitemap_v2_text)
        self.assertIn(compare_files[0].name, sitemap_text)
        self.assertIn(alt_files[0].name, sitemap_text)
        self.assertIn(compare_files[0].name, sitemap_txt)
        self.assertTrue((dist / ".nojekyll").exists(), "Missing .nojekyll file")

        # Verify Google Search Console verification file is preserved in dist/
        gsc_file = dist / "google99ee1ec53fe652a5.html"
        self.assertTrue(gsc_file.exists(), "Missing Google Search Console verification file")
        self.assertEqual(
            gsc_file.read_text(encoding="utf-8").strip(),
            "google-site-verification: google99ee1ec53fe652a5.html",
        )

    def test_setup_assistant_status_and_updates(self) -> None:
        # Ensure isolated test fixture starts with placeholder URLs regardless of user's live config
        settings_path = self.temp_dir / "config" / "settings.json"
        settings_data = json.loads(settings_path.read_text(encoding="utf-8"))
        settings_data["monetization"]["digital_product_checkout_url"] = (
            "https://yourstore.lemonsqueezy.com/buy/zero-cost-stack-blueprint"
        )
        settings_path.write_text(json.dumps(settings_data, indent=2), encoding="utf-8")

        aff_path = self.temp_dir / "config" / "affiliates.json"
        aff_data = json.loads(aff_path.read_text(encoding="utf-8"))
        aff_data["tools"][0]["affiliate_url"] = "https://example.com/?ref=stackpulse_replace_me"
        aff_path.write_text(json.dumps(aff_data, indent=2), encoding="utf-8")

        status_before = get_setup_status(self.temp_dir, check_gh=False)
        self.assertGreater(status_before["placeholder_affiliate_count"], 0)
        self.assertFalse(status_before["digital_product_ready"])

        target_tool_id = aff_data["tools"][0]["id"]
        res_aff = set_affiliate_url(
            self.temp_dir, target_tool_id, "https://example.com/?ref=my_real_id", rebuild=True
        )
        self.assertEqual(res_aff["updated_tool"], target_tool_id)
        self.assertTrue((self.temp_dir / "dist" / "go" / f"{target_tool_id}.html").exists())
        go_html = (self.temp_dir / "dist" / "go" / f"{target_tool_id}.html").read_text(encoding="utf-8")
        self.assertIn("https://example.com/?ref=my_real_id", go_html)

        res_prod = set_monetization_url(
            self.temp_dir,
            "digital_product_checkout_url",
            "https://gumroad.com/l/stackpulse-pack",
            rebuild=True,
        )
        self.assertEqual(res_prod["updated_field"], "digital_product_checkout_url")

        status_after = get_setup_status(self.temp_dir, check_gh=False)
        self.assertEqual(
            status_after["placeholder_affiliate_count"],
            status_before["placeholder_affiliate_count"] - 1,
        )
        self.assertTrue(status_after["digital_product_ready"])


if __name__ == "__main__":
    unittest.main()
