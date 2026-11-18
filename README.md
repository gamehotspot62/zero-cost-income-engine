# StackPulse AI — Zero-Cost Autonomous Online Income Engine ($0 Capital)

An end-to-end **Programmatic SEO + Recurring SaaS Affiliate + Digital Product + Automated Newsletter** platform powered by zero-cost cloud infrastructure (**GitHub Actions**, **GitHub Pages / Cloudflare Pages**, and **Gemini / Groq free LLM tiers**).

## Why Zero Investment ($0.00)?
- **Compute:** GitHub Actions (unlimited free minutes on public repositories; 2,000 mins/mo on private repositories).
- **Hosting & CDN:** GitHub Pages or Cloudflare Pages (unlimited static bandwidth for $0/month).
- **AI Synthesis:** Google Gemini API free tier (`GEMINI_API_KEY`) or Groq free tier (`GROQ_API_KEY`), with a built-in deterministic fallback when keys are unset.
- **Payments & Affiliates:** Free affiliate networks (PartnerStack, Rewardful, Lemon Squeezy, Gumroad) + zero-monthly-fee Merchant of Record checkouts.
- **Zero External Python Dependencies:** Runs on pure Python 3.10+ standard library.

## Quick Start (Local)
```bash
# 1. Run the autonomous pipeline (live web signals + deterministic/LLM synthesis)
python -m src.agent_pipeline --mode full

# 2. Or force offline deterministic mode
python -m src.agent_pipeline --mode full --offline

# 3. Preview generated platform locally
python -m http.server 8000 --directory dist
# Open http://localhost:8000/index.html and http://localhost:8000/dashboard.html

# 4. Run automated verification suite
python -m unittest discover -s tests -v
```

## Activating Autonomous Cloud Mode ($0/month)
1. Push this repository to a **public GitHub repository** (for unlimited GitHub Actions minutes and free GitHub Pages).
2. In **Settings → Pages**, set **Source** to **GitHub Actions**.
3. In **Settings → Secrets and variables → Actions**, optionally add:
   - `GEMINI_API_KEY` (free key from Google AI Studio)
   - `GROQ_API_KEY` (free key from Groq Console)
   - `BUTTONDOWN_API_KEY` (free newsletter draft syncing)
4. Replace the placeholder affiliate IDs (`stackpulse_replace_me`) in `config/affiliates.json` and checkout links in `config/settings.json` with your real affiliate/checkout URLs.
5. The workflow in `.github/workflows/autonomous_agent.yml` will automatically run every day at `06:00 UTC`, rebuild all pSEO comparison pages, refresh signals, compile your weekly digital product, and redeploy your live site.
