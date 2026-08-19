"""
Hand-authored neofetch-style info card SVG.
Lines fade + slide in on a short stagger, like a terminal printing output.

Usage:
    python make_info_card.py
    STATIC=1 python make_info_card.py   # frozen frame, no animation
Output:
    info-card.svg (repo root)
"""
import os

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT = os.path.join(REPO_ROOT, "info-card.svg")

STATIC = os.environ.get("STATIC") == "1"

TITLE = "suhas@github"
ROWS = [
    ("Now", "AI / ML Engineer, open to relocation"),
    ("Prev", "Generative AI & RAG Pipelines"),
    ("Stack", "LangChain · FastAPI · AWS/GCP · Docker"),
    ("Loc", "Malmo, Sweden"),
    ("Highlights", "+38% recommendation relevance, 0.92 F1-score"),
]

WIDTH = 520
ROW_H = 34
PAD_TOP = 56
PAD_X = 24
HEIGHT = PAD_TOP + ROW_H * len(ROWS) + 24
STAGGER = 0.18
DUR = 0.4


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, Monaco, monospace">'
    )
    parts.append(
        "<style>"
        ".card-bg{fill:#0d1117;} .titlebar{fill:#161b22;} .dot-r{fill:#ff5f56;} "
        ".dot-y{fill:#ffbd2e;} .dot-g{fill:#27c93f;} .title-text{fill:#8b949e;font-size:13px;} "
        ".key{fill:#39d353;font-size:14px;font-weight:bold;} .val{fill:#c9d1d9;font-size:14px;} "
        ".row{opacity:0;} "
        "@media (prefers-color-scheme: light){"
        ".card-bg{fill:#f6f8fa;} .titlebar{fill:#eaeef2;} .title-text{fill:#57606a;} "
        ".key{fill:#116329;} .val{fill:#24292f;}"
        "}"
        "</style>"
    )
    parts.append(f'<rect class="card-bg" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10"/>')
    parts.append(f'<rect class="titlebar" x="0" y="0" width="{WIDTH}" height="32" rx="10"/>')
    parts.append(f'<rect class="titlebar" x="0" y="16" width="{WIDTH}" height="16"/>')
    parts.append('<circle class="dot-r" cx="20" cy="16" r="6"/>')
    parts.append('<circle class="dot-y" cx="40" cy="16" r="6"/>')
    parts.append('<circle class="dot-g" cx="60" cy="16" r="6"/>')
    parts.append(f'<text class="title-text" x="{WIDTH / 2}" y="20" text-anchor="middle">{escape_xml(TITLE)}</text>')

    for i, (key, val) in enumerate(ROWS):
        y = PAD_TOP + i * ROW_H
        row_opacity_style = "" if STATIC else ' class="row"'
        begin = i * STAGGER
        parts.append(f'<g{row_opacity_style} transform="translate(0,0)">')
        if not STATIC:
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" dur="{DUR}s" '
                f'begin="{begin:.2f}s" fill="freeze"/>'
            )
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-12,0" to="0,0" dur="{DUR}s" begin="{begin:.2f}s" fill="freeze"/>'
            )
        else:
            parts[-1] = parts[-1].replace('<g transform', '<g opacity="1" transform')
        parts.append(f'<text class="key" x="{PAD_X}" y="{y}">{escape_xml(key)}</text>')
        parts.append(f'<text class="val" x="{PAD_X + 110}" y="{y}">{escape_xml(val)}</text>')
        parts.append("</g>")

    parts.append("</svg>")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
