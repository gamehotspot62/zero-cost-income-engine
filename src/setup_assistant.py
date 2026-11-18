"""Beginner-friendly setup assistant for configuring links and deploying without git.exe."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from src.agent_pipeline import run_pipeline

DEPLOY_EXCLUDE_DIRS = {"dist", "__pycache__", ".git", ".pytest_cache"}
DEPLOY_EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _validate_http_url(url: str) -> str:
    cleaned = url.strip()
    if not (cleaned.startswith("https://") or cleaned.startswith("http://")):
        raise ValueError(f"URL must start with https:// or http:// (got: {url!r})")
    return cleaned


def _check_gh_auth() -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return {"authenticated": True, "username": proc.stdout.strip()}
        return {"authenticated": False, "error": proc.stderr.strip() or "Not logged in"}
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"authenticated": False, "error": str(exc)}


def get_setup_status(project_root: Path, check_gh: bool = True) -> dict[str, Any]:
    """Return structured readiness summary for links, checkout URLs, and GitHub CLI."""
    settings = _read_json(project_root / "config" / "settings.json")
    affiliates = _read_json(project_root / "config" / "affiliates.json")
    tools = affiliates.get("tools", [])
    mon = settings.get("monetization", {})

    placeholder_tools = [
        {"id": t["id"], "name": t["name"], "category": t["category"]}
        for t in tools
        if "replace_me" in str(t.get("affiliate_url", ""))
    ]
    customized_count = len(tools) - len(placeholder_tools)

    product_url = str(mon.get("digital_product_checkout_url", ""))
    sponsor_url = str(mon.get("featured_sponsor_checkout_url", ""))
    newsletter_url = str(mon.get("newsletter_signup_action", ""))

    product_ready = bool(product_url) and "yourstore.lemonsqueezy.com" not in product_url
    sponsor_ready = bool(sponsor_url) and "test_replace_with_your_free_payment_link" not in sponsor_url
    newsletter_ready = bool(newsletter_url) and "your-newsletter-handle" not in newsletter_url

    gh_status = _check_gh_auth() if check_gh else {"authenticated": False, "skipped": True}

    return {
        "site_name": settings.get("site_name", "StackPulse AI"),
        "base_url": settings.get("base_url", ""),
        "total_tools": len(tools),
        "customized_affiliate_count": customized_count,
        "placeholder_affiliate_count": len(placeholder_tools),
        "placeholder_tools": placeholder_tools,
        "digital_product_ready": product_ready,
        "digital_product_checkout_url": product_url,
        "featured_sponsor_ready": sponsor_ready,
        "featured_sponsor_checkout_url": sponsor_url,
        "newsletter_ready": newsletter_ready,
        "github_cli": gh_status,
    }


def set_affiliate_url(
    project_root: Path,
    tool_id: str,
    url: str,
    rebuild: bool = True,
) -> dict[str, Any]:
    """Update a tool's affiliate_url in config/affiliates.json and optionally rebuild dist/."""
    valid_url = _validate_http_url(url)
    aff_path = project_root / "config" / "affiliates.json"
    affiliates = _read_json(aff_path)
    tools = affiliates.get("tools", [])

    matched = None
    for tool in tools:
        if tool.get("id") == tool_id:
            tool["affiliate_url"] = valid_url
            matched = tool
            break

    if matched is None:
        valid_ids = ", ".join(t["id"] for t in tools)
        raise KeyError(f"Unknown tool_id {tool_id!r}. Available IDs: {valid_ids}")

    _write_json(aff_path, affiliates)
    build_summary = run_pipeline(project_root, mode="full", offline=True) if rebuild else None
    return {"updated_tool": matched["id"], "affiliate_url": valid_url, "rebuilt": rebuild, "build": build_summary}


def set_monetization_url(
    project_root: Path,
    field_name: str,
    url: str,
    rebuild: bool = True,
) -> dict[str, Any]:
    """Update a checkout URL inside config/settings.json monetization block."""
    valid_url = _validate_http_url(url)
    settings_path = project_root / "config" / "settings.json"
    settings = _read_json(settings_path)
    mon = settings.setdefault("monetization", {})
    if field_name not in mon:
        raise KeyError(f"Unknown monetization field: {field_name!r}")
    mon[field_name] = valid_url
    _write_json(settings_path, settings)
    build_summary = run_pipeline(project_root, mode="full", offline=True) if rebuild else None
    return {"updated_field": field_name, "url": valid_url, "rebuilt": rebuild, "build": build_summary}


def _run_gh(args: list[str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["gh", *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )


def _run_gh_retry(
    args: list[str],
    input_bytes: bytes | None = None,
    attempts: int = 3,
) -> subprocess.CompletedProcess[bytes]:
    last = _run_gh(args, input_bytes=input_bytes)
    for attempt in range(1, attempts):
        if last.returncode == 0:
            return last
        time.sleep(2 * attempt)
        last = _run_gh(args, input_bytes=input_bytes)
    return last


def _git_blob_sha(raw_bytes: bytes) -> str:
    header = f"blob {len(raw_bytes)}\0".encode("utf-8")
    return hashlib.sha1(header + raw_bytes).hexdigest()


def _iter_deploy_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(project_root).parts
        if any(part in DEPLOY_EXCLUDE_DIRS for part in rel_parts):
            continue
        if path.suffix in DEPLOY_EXCLUDE_SUFFIXES:
            continue
        files.append(path)
    return files


def deploy_to_github(project_root: Path, repo_name: str = "zero-cost-income-engine") -> dict[str, Any]:
    """Create public GitHub repo via gh CLI and upload files via GitHub REST API (no git.exe needed)."""
    gh = _check_gh_auth()
    if not gh.get("authenticated"):
        raise RuntimeError(f"GitHub CLI is not authenticated: {gh.get('error')}")
    owner = gh["username"]
    full_repo = f"{owner}/{repo_name}"

    view = _run_gh(["repo", "view", full_repo])
    repo_created = False
    if view.returncode != 0:
        create = _run_gh(
            [
                "repo",
                "create",
                full_repo,
                "--public",
                "--description",
                "StackPulse AI — Zero-Cost Autonomous pSEO & Recurring SaaS Affiliate Engine",
            ]
        )
        if create.returncode != 0:
            raise RuntimeError(f"Failed to create repo {full_repo}: {create.stderr.decode('utf-8', 'replace')}")
        repo_created = True

    # Ensure settings.json base_url matches owner/repo_name
    settings_path = project_root / "config" / "settings.json"
    settings = _read_json(settings_path)
    expected_base = f"https://{owner}.github.io/{repo_name}"
    if settings.get("base_url") != expected_base:
        settings["base_url"] = expected_base
        _write_json(settings_path, settings)

    remote_shas: dict[str, str] = {}
    if not repo_created:
        tree_res = _run_gh_retry(["api", f"repos/{full_repo}/git/trees/HEAD?recursive=1"])
        if tree_res.returncode == 0:
            try:
                tree_data = json.loads(tree_res.stdout.decode("utf-8", "replace"))
                for item in tree_data.get("tree", []):
                    if item.get("type") == "blob" and item.get("path") and item.get("sha"):
                        remote_shas[item["path"]] = item["sha"]
            except ValueError:
                remote_shas = {}

    deploy_files = _iter_deploy_files(project_root)
    uploaded_files: list[str] = []
    for file_path in deploy_files:
        rel = file_path.relative_to(project_root).as_posix()
        raw_bytes = file_path.read_bytes()
        local_sha = _git_blob_sha(raw_bytes)
        existing_sha = remote_shas.get(rel)
        if existing_sha == local_sha:
            continue

        if existing_sha is None and not repo_created:
            check = _run_gh_retry(["api", f"repos/{full_repo}/contents/{rel}", "--jq", ".sha"])
            if check.returncode == 0:
                existing_sha = check.stdout.decode("utf-8", "replace").strip()

        raw_b64 = base64.b64encode(raw_bytes).decode("ascii")
        payload: dict[str, Any] = {
            "message": f"chore(setup): sync {rel}",
            "content": raw_b64,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        put = _run_gh_retry(
            [
                "api",
                "--method",
                "PUT",
                f"repos/{full_repo}/contents/{rel}",
                "--input",
                "-",
            ],
            input_bytes=json.dumps(payload).encode("utf-8"),
        )
        if put.returncode != 0:
            raise RuntimeError(f"Failed uploading {rel}: {put.stderr.decode('utf-8', 'replace')}")
        uploaded_files.append(rel)

    # Enable GitHub Pages (GitHub Actions source)
    pages_payload = json.dumps({"build_type": "workflow"}).encode("utf-8")
    pages_res = _run_gh(
        ["api", "--method", "POST", f"repos/{full_repo}/pages", "--input", "-"],
        input_bytes=pages_payload,
    )
    if pages_res.returncode != 0:
        pages_res = _run_gh_retry(
            ["api", "--method", "PUT", f"repos/{full_repo}/pages", "--input", "-"],
            input_bytes=pages_payload,
        )

    # Trigger initial workflow run
    wf_res = _run_gh_retry(["workflow", "run", "autonomous_agent.yml", "--repo", full_repo])

    return {
        "repo": full_repo,
        "repo_url": f"https://github.com/{full_repo}",
        "site_url": expected_base,
        "repo_created": repo_created,
        "files_checked": len(deploy_files),
        "files_uploaded": len(uploaded_files),
        "pages_configured": pages_res.returncode == 0,
        "workflow_triggered": wf_res.returncode == 0,
    }


def _print_readable_status(status: dict[str, Any]) -> None:
    print(f"=== {status['site_name']} Setup Checklist ===")
    print(f"Target Site URL   : {status['base_url']}")
    gh = status["github_cli"]
    gh_msg = f"Connected as @{gh['username']}" if gh.get("authenticated") else f"Not connected ({gh.get('error', 'unknown')})"
    print(f"1. GitHub CLI     : {gh_msg}")
    print(
        f"2. Affiliate Links: {status['customized_affiliate_count']}/{status['total_tools']} customized "
        f"({status['placeholder_affiliate_count']} still using placeholder IDs)"
    )
    print(f"3. Digital Product: {'Ready' if status['digital_product_ready'] else 'Needs your Gumroad/Lemon Squeezy link'}")
    print(f"4. Sponsor Slot   : {'Ready' if status['featured_sponsor_ready'] else 'Needs your Stripe/Lemon Squeezy payment link'}")
    print(f"5. Newsletter     : {'Ready' if status['newsletter_ready'] else 'Optional: add Buttondown handle'}")
    if status["placeholder_tools"]:
        print("\nTools still waiting for your affiliate ID:")
        for item in status["placeholder_tools"]:
            print(f"  - {item['id']:22s} ({item['name']})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Beginner setup assistant for StackPulse AI")
    parser.add_argument("--status", action="store_true", help="Show setup readiness checklist")
    parser.add_argument(
        "--set-affiliate",
        nargs=2,
        metavar=("TOOL_ID", "URL"),
        help="Update a tool affiliate URL and rebuild site",
    )
    parser.add_argument(
        "--set-product-url",
        metavar="URL",
        help="Update digital_product_checkout_url and rebuild site",
    )
    parser.add_argument(
        "--set-sponsor-url",
        metavar="URL",
        help="Update featured_sponsor_checkout_url and rebuild site",
    )
    parser.add_argument(
        "--deploy-github",
        action="store_true",
        help="Create public GitHub repo and upload files via gh CLI (no git.exe required)",
    )
    parser.add_argument(
        "--repo-name",
        default="zero-cost-income-engine",
        help="Target GitHub repository name when using --deploy-github",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent

    if args.set_affiliate:
        res = set_affiliate_url(project_root, args.set_affiliate[0], args.set_affiliate[1])
        print(json.dumps(res, indent=2))
        return 0
    if args.set_product_url:
        res = set_monetization_url(project_root, "digital_product_checkout_url", args.set_product_url)
        print(json.dumps(res, indent=2))
        return 0
    if args.set_sponsor_url:
        res = set_monetization_url(project_root, "featured_sponsor_checkout_url", args.set_sponsor_url)
        print(json.dumps(res, indent=2))
        return 0
    if args.deploy_github:
        res = deploy_to_github(project_root, repo_name=args.repo_name)
        print(json.dumps(res, indent=2))
        return 0

    status = get_setup_status(project_root)
    _print_readable_status(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
