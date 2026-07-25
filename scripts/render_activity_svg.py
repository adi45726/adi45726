#!/usr/bin/env python3
"""
Render data/recent_activity.json (from fetch_recent_activity.py) as a small
terminal-style ticker: real recent public events, one line each, fading in on
a short stagger (same one-shot reveal as info-card.svg -- refreshed daily by
the workflow, so it doesn't need to loop).
"""
import html
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "recent_activity.json")
OUT_PATH = os.path.join(HERE, "..", "activity-ticker.svg")

W = 860
PAD = 20
TITLEBAR_H = 30
LINE_H = 24

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
GREEN = "#3fb950"
ACCENT = "#22d3ee"


def esc(s):
    return html.escape(s)


def rise(inner, i):
    delay = 0.15 + i * 0.08
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def render(rows):
    H = TITLEBAR_H + 22 + len(rows) * LINE_H + PAD * 0.6

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="abg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H:.0f}" rx="12" fill="url(#abg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1:.1f}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">adi@github: ~$ tail -f activity.log</text>')

    y = TITLEBAR_H + 26
    for i, row in enumerate(rows):
        text = esc(row["text"])
        rel = esc(row["relative"])
        inner = (f'<circle cx="{PAD+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{PAD+14}" y="{y:.1f}" fill="{INK}" font-size="13">{text}</text>'
                 f'<text x="{W-PAD}" y="{y:.1f}" fill="{ACCENT}" font-size="11" text-anchor="end">{rel}</text>')
        parts.append(rise(inner, i))
        y += LINE_H

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    rows = json.load(open(IN_PATH))
    svg = render(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")
