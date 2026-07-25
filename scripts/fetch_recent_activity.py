#!/usr/bin/env python3
"""
Pull the last few REAL public events from GitHub's public events API
(unauthenticated, no token) and turn them into short human-readable lines
for the activity ticker panel.

Writes data/recent_activity.json: [{"text": "...", "date": "2026-07-25T..."}]
"""
import datetime
import json
import os
import urllib.request

USERNAME = os.environ.get("GH_PROFILE_USER", "adi45726")
URL = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "recent_activity.json")
LIMIT = 6


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "profile-readme-bot/1.0",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def describe(e):
    repo = e["repo"]["name"].split("/", 1)[-1]
    t = e["type"]
    p = e.get("payload", {})
    if t == "PushEvent":
        branch = (p.get("ref") or "").rsplit("/", 1)[-1] or "main"
        return f"pushed to {repo} ({branch})"
    if t == "CreateEvent":
        rt = p.get("ref_type")
        if rt == "repository":
            return f"created {repo}"
        if rt == "branch":
            return f"created branch {p.get('ref')} in {repo}"
        if rt == "tag":
            return f"tagged {p.get('ref')} in {repo}"
        return f"created {rt or 'something'} in {repo}"
    if t == "PublicEvent":
        return f"made {repo} public"
    if t == "PullRequestEvent":
        action = p.get("action", "updated")
        return f"{action} a pull request in {repo}"
    if t == "IssuesEvent":
        action = p.get("action", "updated")
        return f"{action} an issue in {repo}"
    if t == "WatchEvent":
        return f"starred {repo}"
    if t == "ForkEvent":
        return f"forked {repo}"
    return None


def relative(dt, now):
    delta = now - dt
    secs = delta.total_seconds()
    if secs < 3600:
        return f"{max(1, int(secs // 60))}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    if secs < 86400 * 30:
        return f"{int(secs // 86400)}d ago"
    return f"{int(secs // (86400*30))}mo ago"


if __name__ == "__main__":
    events = get(URL)
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for e in events:
        text = describe(e)
        if not text:
            continue
        dt = datetime.datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
        rows.append({"text": text, "date": e["created_at"], "relative": relative(dt, now)})
        if len(rows) >= LIMIT:
            break

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"wrote {OUT_PATH}: {len(rows)} events")
