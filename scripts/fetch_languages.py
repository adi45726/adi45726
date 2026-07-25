#!/usr/bin/env python3
"""
Aggregate real per-language byte counts across all public, non-fork repos
using GitHub's public REST API (unauthenticated -- fine for a handful of
repos once a day within the 60 req/hr anonymous rate limit).

Writes data/languages.json: [{"name": "TypeScript", "bytes": 123, "pct": 88.1}, ...]
sorted by share, descending.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

USERNAME = os.environ.get("GH_PROFILE_USER", "adi45726")
API = "https://api.github.com"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "languages.json")


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "profile-readme-bot/1.0",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def list_repos():
    repos, page = [], 1
    while True:
        batch = get(f"{API}/users/{USERNAME}/repos?per_page=100&page={page}&type=public")
        if not batch:
            break
        repos.extend(r for r in batch if not r["fork"])
        if len(batch) < 100:
            break
        page += 1
    return repos


def aggregate():
    totals = {}
    for repo in list_repos():
        try:
            langs = get(f"{API}/repos/{USERNAME}/{repo['name']}/languages")
        except urllib.error.HTTPError as e:
            print(f"skip {repo['name']}: {e}", file=sys.stderr)
            continue
        for lang, n in langs.items():
            totals[lang] = totals.get(lang, 0) + n
        time.sleep(0.2)  # be polite to the anonymous rate limit
    return totals


if __name__ == "__main__":
    totals = aggregate()
    grand = sum(totals.values()) or 1
    rows = sorted(
        ({"name": k, "bytes": v, "pct": round(v / grand * 100, 2)} for k, v in totals.items()),
        key=lambda r: r["bytes"], reverse=True,
    )
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)
    top = ", ".join(f"{r['name']} {r['pct']}%" for r in rows[:5])
    print(f"wrote {OUT_PATH}: {top}")
