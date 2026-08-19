"""
Converts scripts/source-prepped.png into a self-typing monochrome ASCII SVG.
Each row wipes in left-to-right with a small "cursor" block, staggered top to bottom.

Usage:
    python make_ascii_svg.py
Output:
    suhas-ascii.svg (repo root)
"""
import os
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
SOURCE = os.path.join(os.path.dirname(__file__), "source-prepped.png")
OUTPUT = os.path.join(REPO_ROOT, "suhas-ascii.svg")

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

COLS = 100
CHAR_ASPECT = 0.55  # monospace glyph width/height ratio
CROP_TOP = 0.16     # trim empty headroom above the subject
CROP_BOTTOM = 0.60  # keep only the top fraction of the image (crop out crossed arms)
FONT_SIZE = 13
CELL_W = FONT_SIZE * 0.6
CELL_H = FONT_SIZE * 1.15
WIPE_DUR = 0.5       # seconds per row
STAGGER = 0.035      # seconds between row starts


def brightness_to_char(v: int) -> str:
    idx = int((255 - v) / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    if not os.path.isfile(SOURCE):
        print(f"Missing {SOURCE}. Run prep_photo.py first.")
        raise SystemExit(1)

    img = Image.open(SOURCE).convert("L")
    w, h = img.size
    img = img.crop((0, int(h * CROP_TOP), w, int(h * CROP_BOTTOM)))
    w, h = img.size
    rows = max(1, round(COLS * (h / w) * CHAR_ASPECT))
    small = img.resize((COLS, rows))
    pixels = small.load()

    lines = []
    for y in range(rows):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(COLS)]
        lines.append("".join(row_chars))

    total_w = COLS * CELL_W
    total_h = rows * CELL_H

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {total_w:.1f} {total_h:.1f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, Monaco, monospace" font-size="{FONT_SIZE}">'
    )
    parts.append(
        "<style>"
        ".ascii-text{fill:#24292f;} .ascii-cursor{fill:#24292f;}"
        "@media (prefers-color-scheme: dark){.ascii-text{fill:#c9d1d9;} .ascii-cursor{fill:#c9d1d9;}}"
        "</style>"
    )

    for i, line in enumerate(lines):
        begin = i * STAGGER
        y_baseline = (i + 1) * CELL_H - (CELL_H - FONT_SIZE) / 2 - 2
        clip_id = f"clip{i}"
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{i * CELL_H:.1f}" width="0" height="{CELL_H + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{total_w:.1f}" '
            f'dur="{WIPE_DUR}s" begin="{begin:.3f}s" fill="freeze"/></rect>'
        )
        parts.append("</clipPath>")
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'<text class="ascii-text" x="0" y="{y_baseline:.1f}" xml:space="preserve">'
            f"{escape_xml(line)}</text>"
        )
        parts.append("</g>")
        parts.append(
            f'<rect class="ascii-cursor" y="{i * CELL_H:.1f}" width="{CELL_W:.1f}" height="{CELL_H:.1f}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{total_w:.1f}" '
            f'dur="{WIPE_DUR}s" begin="{begin:.3f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.9;1" '
            f'dur="{WIPE_DUR}s" begin="{begin:.3f}s" fill="freeze"/>'
            f"</rect>"
        )

    parts.append("</svg>")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUTPUT} ({COLS}x{rows} chars)")


if __name__ == "__main__":
    main()
