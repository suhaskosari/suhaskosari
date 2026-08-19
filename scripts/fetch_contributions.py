"""
Fetches a GitHub user's public contribution calendar (no token/API needed) from
https://github.com/users/<username>/contributions and writes data/contributions.json
with raw days plus derived stats (streaks, best day, monthly totals).

Usage:
    python fetch_contributions.py [username]
Output:
    data/contributions.json
"""
import sys
import os
import re
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "suhaskosari"
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT = os.path.join(REPO_ROOT, "data", "contributions.json")


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    tooltip_by_for = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if target:
            tooltip_by_for[target] = tip.get_text(strip=True)

    days = []
    cells = soup.find_all("td", attrs={"data-date": True})
    for td in cells:
        d = td["data-date"]
        level = int(td.get("data-level", 0))

        count = None
        if td.has_attr("data-count"):
            try:
                count = int(td["data-count"])
            except ValueError:
                count = None

        if count is None:
            text = None
            if td.has_attr("id") and td["id"] in tooltip_by_for:
                text = tooltip_by_for[td["id"]]
            elif td.has_attr("aria-label"):
                text = td["aria-label"]
            if text:
                m = re.match(r"([\d,]+)\s+contribution", text)
                if m:
                    count = int(m.group(1).replace(",", ""))
                elif text.lower().startswith("no contributions"):
                    count = 0

        if count is None:
            count = level  # best-effort fallback

        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])

    summary_text = None
    header = soup.find(string=re.compile(r"contributions? in the last year", re.I))
    if header:
        summary_text = header.strip()

    return days, summary_text


def compute_stats(days):
    total = sum(d["count"] for d in days)

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda x: x["count"]) if days else None

    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    html = fetch_html(username)
    days, summary_text = parse_days(html)

    if not days:
        print("No contribution data parsed — GitHub's markup may have changed.")
        sys.exit(1)

    stats = compute_stats(days)

    out = {
        "username": username,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "summary_text": summary_text,
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {OUTPUT} ({len(days)} days, {stats['total']} contributions)")


if __name__ == "__main__":
    main()
