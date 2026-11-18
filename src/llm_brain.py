"""Zero-cost multi-provider AI synthesis router (Gemini Free -> Groq Free -> Deterministic)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class ZeroCostLLMBrain:
    """Routes synthesis requests across free-tier LLM APIs with deterministic fallback."""

    def __init__(self, settings: dict[str, Any], offline: bool = False) -> None:
        self.settings = settings
        self.offline = offline
        llm_cfg = settings.get("llm", {})
        self.priority = llm_cfg.get("provider_priority", ["gemini", "groq", "deterministic"])
        self.gemini_model = llm_cfg.get("gemini_model", "gemini-3.5-flash-lite")
        self.groq_model = llm_cfg.get("groq_model", "llama-3.3-70b-versatile")
        self.max_live_calls = int(
            llm_cfg.get("max_live_llm_calls_per_run", llm_cfg.get("max_live_calls_per_run", 6))
        )
        self.timeout = int(llm_cfg.get("timeout_seconds", 25))
        self.live_calls_used = 0
        self.providers_used: dict[str, int] = {"gemini": 0, "groq": 0, "deterministic": 0}

    def _call_gemini(self, prompt: str) -> str | None:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            return None
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        candidates = data.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in reversed(parts):
            if not part.get("thought") and part.get("text"):
                return str(part["text"])
        return None

    def _call_groq(self, prompt: str) -> str | None:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        body = {
            "model": self.groq_model,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Respond strictly with valid JSON."},
                {"role": "user", "content": prompt},
            ],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices", [])
        if not choices:
            return None
        return choices[0].get("message", {}).get("content")

    def _try_live_json(self, prompt: str) -> tuple[dict[str, Any] | None, str]:
        if self.offline or self.live_calls_used >= self.max_live_calls:
            return None, "deterministic"

        for provider in self.priority:
            if provider == "deterministic":
                break
            try:
                raw: str | None = None
                if provider == "gemini":
                    raw = self._call_gemini(prompt)
                elif provider == "groq":
                    raw = self._call_groq(prompt)
                if raw:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        self.live_calls_used += 1
                        self.providers_used[provider] = self.providers_used.get(provider, 0) + 1
                        return parsed, provider
            except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError):
                continue
        return None, "deterministic"

    def synthesize_comparison(self, tool_a: dict[str, Any], tool_b: dict[str, Any]) -> dict[str, Any]:
        """Generate structured head-to-head comparison insights and FAQs."""
        prompt = (
            f"Compare {tool_a['name']} vs {tool_b['name']} for a zero-budget solo builder. "
            f"Tool A free tier: {tool_a['free_tier_limits']}. Paid start: {tool_a['paid_start_price']}. "
            f"Tool B free tier: {tool_b['free_tier_limits']}. Paid start: {tool_b['paid_start_price']}. "
            'Return JSON with keys: "verdict" (2 sentences), "tco_analysis" (2 sentences), '
            '"migration_tip" (1 sentence), "faqs" (array of 3 objects with "q" and "a").'
        )
        live, provider = self._try_live_json(prompt)
        winner = tool_a if tool_a["score"] >= tool_b["score"] else tool_b
        runner_up = tool_b if winner["id"] == tool_a["id"] else tool_a

        if live and isinstance(live.get("faqs"), list) and live.get("verdict"):
            return {
                "winner_id": winner["id"],
                "winner_name": winner["name"],
                "verdict": str(live["verdict"]),
                "tco_analysis": str(live.get("tco_analysis", "")),
                "migration_tip": str(live.get("migration_tip", "")),
                "faqs": live["faqs"][:3],
                "provider": provider,
            }

        self.providers_used["deterministic"] += 1
        return {
            "winner_id": winner["id"],
            "winner_name": winner["name"],
            "verdict": (
                f"For zero-investment builders in {tool_a['category']}, {winner['name']} edges ahead "
                f"with a {winner['score']}/10 stack rating because it maximizes runway via: "
                f"{winner['free_tier_limits']}. Choose {runner_up['name']} specifically if your workload "
                f"prioritizes {runner_up['best_for'].lower()}."
            ),
            "tco_analysis": (
                f"At $0/month MVP scale, both {tool_a['name']} and {tool_b['name']} eliminate fixed server bills. "
                f"When traffic scales past free quotas, {tool_a['name']} starts at {tool_a['paid_start_price']} "
                f"while {tool_b['name']} starts at {tool_b['paid_start_price']}."
            ),
            "migration_tip": (
                f"Keep your business logic decoupled via standard interfaces or {winner['open_source_alt']} "
                f"so you can switch between {tool_a['name']} and {tool_b['name']} without rewriting core workflows."
            ),
            "faqs": [
                {
                    "q": f"Can I use {tool_a['name']} or {tool_b['name']} completely free for commercial projects?",
                    "a": (
                        f"{tool_a['name']} offers {tool_a['free_tier_limits']}. "
                        f"{tool_b['name']} provides {tool_b['free_tier_limits']}. Always check each vendor's "
                        f"commercial terms—for example, {winner['name']} is ideal for {winner['best_for'].lower()}."
                    ),
                },
                {
                    "q": f"Which has lower scaling costs after leaving the free tier: {tool_a['name']} or {tool_b['name']}?",
                    "a": (
                        f"{tool_a['name']} transitions to paid usage at {tool_a['paid_start_price']}, whereas "
                        f"{tool_b['name']} starts at {tool_b['paid_start_price']}."
                    ),
                },
                {
                    "q": f"What is the best open-source alternative to {tool_a['name']} and {tool_b['name']}?",
                    "a": (
                        f"Builders wanting zero vendor lock-in typically pair {tool_a['open_source_alt']} "
                        f"or {tool_b['open_source_alt']} with self-hosted containers or GitHub Actions."
                    ),
                },
            ],
            "provider": "deterministic",
        }

    def synthesize_alternatives(self, tool: dict[str, Any], peers: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate migration rationale and FAQs for an alternatives page."""
        sorted_peers = sorted(peers, key=lambda p: p["score"], reverse=True)
        top_pick = sorted_peers[0] if sorted_peers else tool
        self.providers_used["deterministic"] += 1
        return {
            "top_pick_id": top_pick["id"],
            "top_pick_name": top_pick["name"],
            "why_switch": (
                f"Developers search for {tool['name']} alternatives primarily due to: "
                f"{'; '.join(tool['cons'])}. Switching to {top_pick['name']} or self-hosting "
                f"{tool['open_source_alt']} preserves $0 fixed cost while expanding headroom."
            ),
            "faqs": [
                {
                    "q": f"What is the #1 free alternative to {tool['name']} in 2026?",
                    "a": (
                        f"{top_pick['name']} ({top_pick['score']}/10) is our top pick, offering "
                        f"{top_pick['free_tier_limits']} and excelling at {top_pick['best_for'].lower()}."
                    ),
                },
                {
                    "q": f"Is there an open-source self-hosted replacement for {tool['name']}?",
                    "a": f"Yes—{tool['open_source_alt']} provides an open-source migration path with full data ownership.",
                },
            ],
            "provider": "deterministic",
        }

    def synthesize_newsletter_editorial(
        self, signals: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Synthesize weekly digest headline, commentary, and actionable earning play."""
        top_signal = signals[0] if signals else {"title": "Zero-Cost Cloud Automation", "topic": "Automation & Workflows"}
        top_tool = max(tools, key=lambda t: t.get("estimated_epc_usd", 0))
        prompt = (
            f"Write a brief, sharp newsletter intro for solo online founders building $0-cost AI businesses. "
            f"Top web trend today: {top_signal['title']}. Featured high-commission tool: {top_tool['name']}. "
            'Return JSON with keys: "headline" (under 12 words), "intro" (2 sentences), '
            '"actionable_play" (2 sentences explaining how to monetize this trend with $0 investment).'
        )
        live, provider = self._try_live_json(prompt)
        if live and live.get("headline") and live.get("intro"):
            return {
                "headline": str(live["headline"]),
                "intro": str(live["intro"]),
                "actionable_play": str(live.get("actionable_play", "")),
                "provider": provider,
            }

        self.providers_used["deterministic"] += 1
        return {
            "headline": f"Zero-Cost Stack Pulse: {top_signal['topic']} & {top_tool['name']} Playbook",
            "intro": (
                f"This week's strongest builder signal—\"{top_signal['title']}\"—confirms that solo operators "
                f"can replace paid cloud infrastructure with automated static pipelines and free-tier LLM APIs. "
                f"Every hour of compute below runs at $0 fixed overhead."
            ),
            "actionable_play": (
                f"Pair GitHub Actions cron automation with {top_tool['name']} ({top_tool['commission_notes']}) "
                f"inside a niche comparison page targeting bottom-of-funnel buyer queries, then bundle the workflow "
                f"as a $19 template on Lemon Squeezy or Gumroad."
            ),
            "provider": "deterministic",
        }
