#!/usr/bin/env python3
"""
check_status.py

Queries the GitHub API for every `type: repo` entry in data/entries.yml and
writes a live maintenance-status report to docs/STATUS.md. Also writes
data/status_cache.json for anything that wants the raw numbers.

This does not touch README.md - the entry list in README.md is static and
only changes when data/entries.yml changes (see scripts/generate_readme.py).
STATUS.md is the one file in this repo that's expected to drift on its own,
via the weekly scheduled workflow.

Flags an entry as "may be unmaintained" when it has had no push in 18+
months, or as "archived" when GitHub reports it archived. Neither flag
removes an entry from the list - see CONTRIBUTING.md for why.

Usage:
    python scripts/check_status.py [--token TOKEN]

Reads GITHUB_TOKEN from the environment if --token isn't passed. Works
unauthenticated too, just at GitHub's much lower unauthenticated rate limit.

Requires: PyYAML, requests (see scripts/requirements.txt)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import sys

import requests
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES_FILE = REPO_ROOT / "data" / "entries.yml"
STATUS_MD = REPO_ROOT / "docs" / "STATUS.md"
STATUS_JSON = REPO_ROOT / "data" / "status_cache.json"

STALE_MONTHS = 18
API_ROOT = "https://api.github.com"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    return p.parse_args()


def fetch_repo_status(repo: str, session: requests.Session) -> dict:
    resp = session.get(f"{API_ROOT}/repos/{repo}", timeout=20)
    if resp.status_code != 200:
        return {"repo": repo, "error": f"HTTP {resp.status_code}"}
    body = resp.json()
    return {
        "repo": repo,
        "archived": body.get("archived", False),
        "pushed_at": body.get("pushed_at"),
        "stargazers_count": body.get("stargazers_count", 0),
    }


def months_since(iso_date: str) -> float:
    pushed = datetime.datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - pushed).days / 30.44


def render_status_md(results: list[dict], checked_at: str) -> str:
    lines = [
        "# Live status report",
        "",
        "Generated automatically by `scripts/check_status.py`, run weekly by "
        "`.github/workflows/check-status.yml`. Do not hand-edit - changes are "
        "overwritten on the next run.",
        "",
        f"Last checked: {checked_at}",
        "",
        f"Flag threshold: no push in {STALE_MONTHS}+ months → \"may be unmaintained\". "
        "This is informational, not a reason to remove an entry - see CONTRIBUTING.md.",
        "",
        "| Repo | Stars | Last push | Flag |",
        "|---|---|---|---|",
    ]
    for r in sorted(results, key=lambda x: x["repo"].lower()):
        if r.get("error"):
            lines.append(f"| [{r['repo']}](https://github.com/{r['repo']}) | - | - | ⚠️ check failed: {r['error']} |")
            continue
        flag = ""
        if r["archived"]:
            flag = "🗄️ archived"
        elif r["pushed_at"] and months_since(r["pushed_at"]) >= STALE_MONTHS:
            flag = "⏳ may be unmaintained"
        pushed = r["pushed_at"][:10] if r["pushed_at"] else "unknown"
        lines.append(
            f"| [{r['repo']}](https://github.com/{r['repo']}) | {r['stargazers_count']} | {pushed} | {flag} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not ENTRIES_FILE.exists():
        print(f"Missing {ENTRIES_FILE}", file=sys.stderr)
        return 1

    data = yaml.safe_load(ENTRIES_FILE.read_text())
    repos = [e["repo"] for e in data["entries"] if e.get("type", "repo") == "repo" and e.get("repo")]

    session = requests.Session()
    headers = {"Accept": "application/vnd.github+json"}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"
    session.headers.update(headers)

    results = [fetch_repo_status(repo, session) for repo in repos]

    checked_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    STATUS_MD.parent.mkdir(parents=True, exist_ok=True)
    STATUS_MD.write_text(render_status_md(results, checked_at))
    STATUS_JSON.write_text(json.dumps({"checked_at": checked_at, "results": results}, indent=2) + "\n")

    errors = [r for r in results if r.get("error")]
    flagged = [r for r in results if not r.get("error") and (r["archived"] or (r["pushed_at"] and months_since(r["pushed_at"]) >= STALE_MONTHS))]
    print(f"Checked {len(results)} repos: {len(flagged)} flagged, {len(errors)} failed to fetch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
