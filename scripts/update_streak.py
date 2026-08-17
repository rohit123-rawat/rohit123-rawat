#!/usr/bin/env python3
"""Refresh assets/streak.svg — the self-hosted contribution streak card.

Fills the placeholders in assets/streak.template.svg with live data from the
GitHub GraphQL API (contribution calendar) and writes assets/streak.svg.
Run by .github/workflows/update-dashboard.yml.

Why self-hosted: the public streak-stats.demolab.com instance answers in
~8 s, but GitHub's image proxy (camo) gives up after ~4 s and returns 504,
so the README showed a broken image. Rendering the card here makes it a
static file served by GitHub itself — no third-party latency involved.

Auth: any token works — the Actions-issued GITHUB_TOKEN is enough, because
the calendar for USER is public (private contribution *counts* are included
whenever the profile's "private contributions" setting is on, which is how
GitHub itself renders the graph for visitors). PROFILE_TOKEN is used first
when present, for parity with update_dashboard.py.

Streak rules mirror github-readme-streak-stats: a day counts when it has at
least one contribution; today does not break the current streak if it has
none yet (the day isn't over). "Today" is evaluated in USER_TZ.
"""
import datetime as dt
import json
import math
import os
import sys
import urllib.request

USER = "rohit123-rawat"
USER_TZ = "Asia/Kolkata"  # local day boundary for the "today doesn't break the streak" rule
TRAIL_DAYS = 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "assets", "streak.template.svg")
TARGET = os.path.join(ROOT, "assets", "streak.svg")
RING_CIRCUMFERENCE = 2 * math.pi * 42  # keep in sync with gen_streak_template()

TOKEN = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")

# palette (subset of scripts/generate_assets.py)
CYAN_BRIGHT = "#7DF9FF"
PURPLE_BRIGHT = "#A78BFA"
STAR_WHITE = "#E0E7FF"
GREEN = "#4ADE80"
GOLD = "#FBBF24"
AMBER = "#FB923C"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

QUERY_YEARS = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionYears }
  }
}"""

QUERY_CALENDAR = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def graphql(query, variables):
    if not TOKEN:
        sys.exit("No GITHUB_TOKEN/PROFILE_TOKEN in the environment — GraphQL needs one.")
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": USER,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def local_today():
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(USER_TZ)
    except Exception:  # no tz database available — IST fallback
        tz = dt.timezone(dt.timedelta(hours=5, minutes=30))
    return dt.datetime.now(tz).date()


def fetch_calendar(today):
    """{date -> contribution count} for every day from the first year of activity through today."""
    years = sorted(graphql(QUERY_YEARS, {"login": USER})["user"]["contributionsCollection"]["contributionYears"])
    days = {}
    for year in years:
        # GitHub caps each contributionsCollection at one year. For the current year the
        # API pads every future day with 0, so bound the range at today and drop the rest.
        end = f"{year}-12-31T23:59:59Z" if year < today.year else f"{today.isoformat()}T23:59:59Z"
        data = graphql(QUERY_CALENDAR, {"login": USER, "from": f"{year}-01-01T00:00:00Z", "to": end})
        for week in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                if day["date"] <= today.isoformat():
                    days[day["date"]] = day["contributionCount"]
    return days


def compute_streaks(days, today):
    """Total, first contribution date, current streak and longest streak."""
    today_s = today.isoformat()
    total = sum(days.values())
    first = next((d for d in sorted(days) if days[d] > 0), None)

    current = {"length": 0, "start": None, "end": None}
    longest = {"length": 0, "start": None, "end": None}
    for date in sorted(days):
        if days[date] > 0:
            current["length"] += 1
            current["end"] = date
            if current["length"] == 1:
                current["start"] = date
            if current["length"] > longest["length"]:
                longest = dict(current)
        elif date != today_s:  # a blank today doesn't end the streak — the day isn't over
            current = {"length": 0, "start": None, "end": None}
    return total, first, current, longest


def fmt_date(iso, today, force_year=False):
    d = dt.date.fromisoformat(iso)
    s = f"{MONTHS[d.month - 1]} {d.day}"
    if force_year or d.year != today.year:
        s += f", {d.year}"
    return s


def fmt_range(streak, today):
    if not streak["length"]:
        return "no active streak — launch a commit"
    start, end = streak["start"], streak["end"]
    force_year = dt.date.fromisoformat(start).year != dt.date.fromisoformat(end).year
    if start == end:
        return fmt_date(start, today, force_year)
    return f"{fmt_date(start, today, force_year)} — {fmt_date(end, today, force_year)}"


def ring_offset(fraction):
    fraction = max(0.0, min(1.0, fraction))
    return f"{RING_CIRCUMFERENCE * (1 - fraction):.2f}"


def build_trail(days, today, current):
    """Last TRAIL_DAYS days as a row of stars: size/brightness by contribution count,
    the current streak's stars linked by a brighter line, today's star pulsing."""
    dates = [(today - dt.timedelta(days=i)).isoformat() for i in range(TRAIL_DAYS - 1, -1, -1)]
    x0, x1, y = 150, 850, 236
    step = (x1 - x0) / (TRAIL_DAYS - 1)
    xs = {d: round(x0 + i * step, 1) for i, d in enumerate(dates)}
    out = []

    # brighter segment over the current streak (needs >= 2 visible days)
    if current["length"] >= 2:
        seg = [d for d in dates if current["start"] <= d <= current["end"]]
        if len(seg) >= 2:
            out.append(f'<line x1="{xs[seg[0]]}" y1="{y}" x2="{xs[seg[-1]]}" y2="{y}" '
                       f'stroke="{CYAN_BRIGHT}" stroke-opacity="0.55" stroke-width="1.5"/>')

    for i, d in enumerate(dates):
        c = days.get(d, 0)
        x = xs[d]
        if c == 0:
            out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{STAR_WHITE}" opacity="0.18"/>')
            continue
        r = 3.2 if c < 5 else 4.2 if c < 15 else 5.2
        color = CYAN_BRIGHT if (current["length"] and current["start"] <= d <= current["end"]) else PURPLE_BRIGHT
        glow = ' filter="url(#softGlow)"' if c >= 15 else ""
        dur = 2.2 + (i % 5) * 0.4
        begin = -(i % 7) * 0.5  # negative begin desynchronises the twinkles
        anim = (f'<animate attributeName="opacity" values="0.55;1;0.55" dur="{dur:.1f}s" '
                f'begin="{begin:.1f}s" repeatCount="indefinite"/>')
        if d == today.isoformat():
            anim += f'<animate attributeName="r" values="{r};{r+2.5};{r}" dur="1.6s" repeatCount="indefinite"/>'
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"{glow}>{anim}</circle>')

    # date ticks under the first and last star
    mono = "'Courier New',ui-monospace,Menlo,Consolas,monospace"
    out.append(f'<text x="{x0}" y="{y+18}" text-anchor="middle" font-family="{mono}" font-size="9" '
               f'letter-spacing="1" fill="#8B949E" opacity="0.8">{fmt_date(dates[0], today).upper()}</text>')
    out.append(f'<text x="{x1}" y="{y+18}" text-anchor="middle" font-family="{mono}" font-size="9" '
               f'letter-spacing="1" fill="#8B949E" opacity="0.8">TODAY</text>')
    return "\n".join(out)


def main():
    today = local_today()
    days = fetch_calendar(today)
    total, first, current, longest = compute_streaks(days, today)

    if current["length"] == 0:
        status_color, status_text = AMBER, "NO SIGNAL — RELAUNCH TODAY"
    elif current["length"] >= longest["length"]:
        status_color, status_text = GOLD, "RECORD STREAK"
    else:
        status_color, status_text = GREEN, "STREAK ACTIVE"

    with open(TEMPLATE) as f:
        svg = f.read()

    svg = (svg
           .replace("{TOTAL}", f"{total:,}")
           .replace("{TOTAL_RANGE}", f"{fmt_date(first, today, force_year=True)} — Present" if first else "—")
           .replace("{CURRENT}", str(current["length"]))
           .replace("{CURRENT_RANGE}", fmt_range(current, today))
           .replace("{LONGEST}", str(longest["length"]))
           .replace("{LONGEST_RANGE}", fmt_range(longest, today))
           .replace("{RING_OFF}", ring_offset(current["length"] / max(longest["length"], 1)))
           .replace("{STATUS_COLOR}", status_color)
           .replace("{STATUS_TEXT}", status_text)
           .replace("{TRAIL}", build_trail(days, today, current))
           .replace("{SYNC_DATE}", today.isoformat()))

    with open(TARGET, "w") as f:
        f.write(svg)
    print(f"streak.svg updated: total={total} current={current['length']} "
          f"({current['start']}..{current['end']}) longest={longest['length']} "
          f"({longest['start']}..{longest['end']}) today={today}")


if __name__ == "__main__":
    main()
