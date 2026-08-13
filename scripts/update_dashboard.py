#!/usr/bin/env python3
"""Refresh assets/mission-control.svg with live GitHub stats.

Fetches public profile numbers from the GitHub API, fills the
placeholders in assets/mission-control.template.svg and writes
assets/mission-control.svg. Run daily by .github/workflows/update-dashboard.yml.
"""
import datetime
import json
import math
import os
import urllib.request

USER = "rohit123-rawat"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "assets", "mission-control.template.svg")
TARGET = os.path.join(ROOT, "assets", "mission-control.svg")
GAUGE_CIRCUMFERENCE = 2 * math.pi * 27


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def gauge_offset(fraction):
    """Dashoffset for a gauge arc filled to `fraction` (keeps a visible sliver)."""
    fraction = max(0.06, min(1.0, fraction))
    return f"{GAUGE_CIRCUMFERENCE * (1 - fraction):.2f}"


def main():
    user = fetch(f"https://api.github.com/users/{USER}")
    repos = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100")

    n_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    joined = int(user.get("created_at", "2022")[0:4])
    years = max(1, datetime.date.today().year - joined)

    with open(TEMPLATE) as f:
        svg = f.read()

    svg = (svg
           .replace("{REPOS_OFF}", gauge_offset(n_repos / 20))
           .replace("{FOLLOWERS_OFF}", gauge_offset(followers / 20))
           .replace("{STARS_OFF}", gauge_offset(stars / 10))
           .replace("{YEARS_OFF}", gauge_offset(years / 8))
           .replace("{REPOS}", str(n_repos))
           .replace("{FOLLOWERS}", str(followers))
           .replace("{STARS}", str(stars))
           .replace("{YEARS}", str(years))
           .replace("{SYNC_DATE}", datetime.date.today().isoformat()))

    with open(TARGET, "w") as f:
        f.write(svg)
    print(f"mission-control.svg updated: repos={n_repos} followers={followers} stars={stars} years={years}")


if __name__ == "__main__":
    main()
