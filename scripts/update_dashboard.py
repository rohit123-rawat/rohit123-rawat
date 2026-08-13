#!/usr/bin/env python3
"""Refresh assets/mission-control.svg with live GitHub stats.

Fills the placeholders in assets/mission-control.template.svg and writes
assets/mission-control.svg. Run daily by .github/workflows/update-dashboard.yml.

Repo/star counts include PRIVATE repos when an authenticated token belonging
to USER is available (env PROFILE_TOKEN, or GITHUB_TOKEN when it is a user
PAT). The Actions-issued GITHUB_TOKEN cannot see the user's private repos, so
the workflow passes secrets.PROFILE_TOKEN — a fine-grained PAT with metadata
read access. Without a usable token this falls back to public-only numbers.
"""
import datetime
import json
import math
import os
import urllib.error
import urllib.request

USER = "rohit123-rawat"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "assets", "mission-control.template.svg")
TARGET = os.path.join(ROOT, "assets", "mission-control.svg")
GAUGE_CIRCUMFERENCE = 2 * math.pi * 27

TOKEN = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")


def fetch(url, auth=True):
    req = urllib.request.Request(url, headers={"User-Agent": USER})
    if auth and TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_all_owned_repos():
    """All repos owned by the token's user, private included (paginated)."""
    repos, page = [], 1
    while True:
        batch = fetch(f"https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def gather_stats():
    public_user = fetch(f"https://api.github.com/users/{USER}")
    followers = public_user.get("followers", 0)
    joined = int(public_user.get("created_at", "2022")[0:4])
    years = max(1, datetime.date.today().year - joined)

    # Authenticated path: private repos count only if the token IS the user.
    if TOKEN:
        try:
            me = fetch("https://api.github.com/user")
            if me.get("login", "").lower() == USER.lower():
                repos = fetch_all_owned_repos()
                n_repos = len(repos)
                stars = sum(r.get("stargazers_count", 0) for r in repos)
                print(f"authenticated as {USER}: counting private repos too")
                return n_repos, followers, stars, years
            print(f"token belongs to {me.get('login')!r}, not {USER!r} — public-only fallback")
        except urllib.error.HTTPError as e:
            # Actions' installation GITHUB_TOKEN cannot call /user (403).
            print(f"/user not accessible with this token ({e.code}) — public-only fallback")

    public_repos = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100")
    n_repos = public_user.get("public_repos", 0)
    stars = sum(r.get("stargazers_count", 0) for r in public_repos)
    return n_repos, followers, stars, years


def gauge_offset(fraction):
    """Dashoffset for a gauge arc filled to `fraction` (keeps a visible sliver)."""
    fraction = max(0.06, min(1.0, fraction))
    return f"{GAUGE_CIRCUMFERENCE * (1 - fraction):.2f}"


def main():
    n_repos, followers, stars, years = gather_stats()

    with open(TEMPLATE) as f:
        svg = f.read()

    svg = (svg
           .replace("{REPOS_OFF}", gauge_offset(n_repos / 60))
           .replace("{FOLLOWERS_OFF}", gauge_offset(followers / 20))
           .replace("{STARS_OFF}", gauge_offset(stars / 50))
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
