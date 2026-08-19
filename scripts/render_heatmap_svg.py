"""
Renders data/contributions.json as the classic 53-week x 7-day contribution
calendar, with a diagonal slide-down reveal (CSS keyframes, plays once on load)
plus a Less->More legend and a stats footer.

Usage:
    python render_heatmap_svg.py
Output:
    contrib-heatmap.svg (repo root)
"""
import os
import json
from datetime import datetime, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(REPO_ROOT, "data", "contributions.json")
OUTPUT = os.path.join(REPO_ROOT, "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none ->                                              brightest (best-day accent)

TARGET_WIDTH = 890
GAP = 3
LEFT_LABEL_W = 28
TOP_LABEL_H = 20
BOTTOM_H = 46
RIGHT_PAD = 12
STAGGER = 0.012
DUR = 0.35

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_weeks(days):
    by_date = {d["date"]: d for d in days}
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()

    start = first - timedelta(days=(first.weekday() + 1) % 7)  # back up to Sunday

    weeks = []
    cur = start
    week = []
    while cur <= last:
        key = cur.isoformat()
        entry = by_date.get(key, {"date": key, "count": 0, "level": 0})
        week.append(entry)
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append({"date": None, "count": 0, "level": 0})
        weeks.append(week)

    return weeks


def main():
    if not os.path.isfile(DATA_PATH):
        print(f"Missing {DATA_PATH}. Run fetch_contributions.py first.")
        raise SystemExit(1)

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    days = data["days"]
    stats = data["stats"]
    weeks = build_weeks(days)
    num_weeks = len(weeks)

    best_date = stats["best_day"]["date"] if stats.get("best_day") else None

    cell_total = (TARGET_WIDTH - LEFT_LABEL_W - RIGHT_PAD) / num_weeks
    cell = cell_total - GAP

    grid_w = num_weeks * (cell + GAP)
    width = LEFT_LABEL_W + grid_w + RIGHT_PAD
    height = TOP_LABEL_H + 7 * (cell + GAP) + BOTTOM_H

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.1f} {height:.1f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, Monaco, monospace">'
    )
    parts.append(
        "<style>"
        f".cell{{opacity:0;animation:cellIn {DUR}s ease-out forwards;}}"
        "@keyframes cellIn{from{opacity:0;transform:translateY(-6px);}to{opacity:1;transform:translateY(0);}}"
        ".lbl{fill:#8b949e;font-size:10px;}"
        ".footer{fill:#8b949e;font-size:12px;}"
        "@media (prefers-color-scheme: light){.lbl{fill:#57606a;}.footer{fill:#57606a;}}"
        "</style>"
    )

    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in day_labels.items():
        y = TOP_LABEL_H + row * (cell + GAP) + cell * 0.75
        parts.append(f'<text class="lbl" x="0" y="{y:.1f}">{label}</text>')

    last_month = None
    for w, week in enumerate(weeks):
        first_valid = next((d for d in week if d["date"]), None)
        if first_valid:
            m = datetime.strptime(first_valid["date"], "%Y-%m-%d").month
            if m != last_month:
                x = LEFT_LABEL_W + w * (cell + GAP)
                parts.append(f'<text class="lbl" x="{x:.1f}" y="12">{MONTH_NAMES[m - 1]}</text>')
                last_month = m

    for w, week in enumerate(weeks):
        for r, day in enumerate(week):
            x = LEFT_LABEL_W + w * (cell + GAP)
            y = TOP_LABEL_H + r * (cell + GAP)
            if day["date"] is None:
                continue
            level = min(day["level"], 4)
            color = PALETTE[level]
            if day["date"] == best_date and day["count"] > 0:
                color = PALETTE[5]
            delay = (w + r) * STAGGER
            title = escape_xml(f'{day["count"]} contributions on {day["date"]}')
            parts.append(
                f'<rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f"<title>{title}</title></rect>"
            )

    legend_y = height - BOTTOM_H + 30
    legend_x = width - RIGHT_PAD - (len(PALETTE) - 1) * 14 - 40
    parts.append(f'<text class="footer" x="{legend_x - 34:.1f}" y="{legend_y + 8:.1f}">Less</text>')
    for i in range(5):
        lx = legend_x + i * 14
        parts.append(f'<rect x="{lx:.1f}" y="{legend_y:.1f}" width="10" height="10" rx="2" fill="{PALETTE[i]}"/>')
    parts.append(f'<text class="footer" x="{legend_x + 5 * 14 + 6:.1f}" y="{legend_y + 8:.1f}">More</text>')

    summary = data.get("summary_text") or f'{stats["total"]:,} contributions'
    footer_line = f'{summary}  ·  current streak {stats["current_streak"]}  ·  longest streak {stats["longest_streak"]}'
    parts.append(f'<text class="footer" x="{LEFT_LABEL_W}" y="{legend_y + 8:.1f}">{escape_xml(footer_line)}</text>')

    parts.append("</svg>")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUTPUT} ({num_weeks} weeks)")


if __name__ == "__main__":
    main()
