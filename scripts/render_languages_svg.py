#!/usr/bin/env python3
"""
Render data/languages.json (from fetch_languages.py) as a single horizontal
100%-stacked bar -- GitHub's own "language bar" convention -- since one
language (TypeScript) dominates real byte counts and separate per-language
bars would leave most of them as invisible slivers. Color is fixed per
language (GitHub's Linguist colors), never cycled, so identity holds even as
the repo mix changes. A legend row below carries the exact percentages.

Bar reveals once, growing left -> right, then freezes (CSS keyframes, no loop).
"""
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "languages.json")
OUT_PATH = os.path.join(HERE, "..", "languages.svg")

# GitHub Linguist colors -- a fixed, real identity mapping (not a generated
# categorical palette), same convention GitHub's own repo language bar uses.
LANG_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Dockerfile": "#384d54",
    "Vue": "#41b883",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "C++": "#f34b7d",
    "C": "#555555",
    "Rust": "#dea584",
    "Swift": "#F05138",
}
FALLBACK = "#8b949e"

W = 860
PAD = 22
TITLEBAR_H = 30
BAR_H = 22
BAR_TOP = TITLEBAR_H + 34
GAP = 2
MIN_SEG_W = 3

LEG_COLS = 4
LEG_ROW_H = 22
LEG_TOP = BAR_TOP + BAR_H + 26

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
TRACK = "#161b22"

BAR_DUR = 0.9


def render(rows):
    rows = [r for r in rows if r["pct"] > 0]
    n_leg_rows = -(-len(rows) // LEG_COLS)  # ceil
    H = LEG_TOP + n_leg_rows * LEG_ROW_H + PAD

    css = f"""
@keyframes grow {{ 0% {{ transform: scaleX(0); }} 100% {{ transform: scaleX(1); }} }}
.seg {{ transform-box: fill-box; transform-origin: left center; animation: grow {BAR_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
@keyframes fade {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
.leg {{ opacity: 0; animation: fade 0.4s ease-out both; }}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>'
        f'<linearGradient id="lbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        f'<clipPath id="barclip"><rect x="{PAD}" y="{BAR_TOP}" width="{W-2*PAD}" height="{BAR_H}" rx="6"/></clipPath>'
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#lbg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">adi@github: ~$ ./stack.sh --langs</text>')
    parts.append(f'<text x="{PAD}" y="{BAR_TOP - 10}" fill="{MUTED}" font-size="11">'
                 f'Languages across public repos, by bytes</text>')

    track_w = W - 2 * PAD
    parts.append(f'<rect x="{PAD}" y="{BAR_TOP}" width="{track_w}" height="{BAR_H}" rx="6" fill="{TRACK}"/>')

    # allocate widths: proportional, with a visibility floor, renormalized to fill exactly track_w
    raw = [max(r["pct"] / 100.0 * track_w, MIN_SEG_W) for r in rows]
    scale = track_w / sum(raw)
    widths = [w * scale for w in raw]

    x = PAD
    parts.append(f'<g clip-path="url(#barclip)">')
    for i, (row, w) in enumerate(zip(rows, widths)):
        color = LANG_COLORS.get(row["name"], FALLBACK)
        seg_w = max(w - GAP, 0.5)
        delay = i * 0.05
        parts.append(
            f'<rect class="seg" x="{x:.2f}" y="{BAR_TOP}" width="{seg_w:.2f}" height="{BAR_H}" '
            f'fill="{color}" style="animation-delay:{delay:.2f}s">'
            f'<title>{row["name"]}: {row["pct"]:.1f}%</title></rect>'
        )
        x += w
    parts.append('</g>')

    # legend grid: swatch + name + percentage
    col_w = track_w / LEG_COLS
    for i, row in enumerate(rows):
        col, line = i % LEG_COLS, i // LEG_COLS
        lx = PAD + col * col_w
        ly = LEG_TOP + line * LEG_ROW_H
        color = LANG_COLORS.get(row["name"], FALLBACK)
        delay = 0.4 + i * 0.04
        parts.append(
            f'<g class="leg" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{lx}" y="{ly-10}" width="10" height="10" rx="2.5" fill="{color}"/>'
            f'<text x="{lx+16}" y="{ly-1:.0f}" fill="{INK}" font-size="12">{row["name"]}</text>'
            f'<text x="{lx+col_w-8}" y="{ly-1:.0f}" fill="{MUTED}" font-size="11" text-anchor="end">{row["pct"]:.1f}%</text>'
            f'</g>'
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    rows = json.load(open(IN_PATH))
    svg = render(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")
