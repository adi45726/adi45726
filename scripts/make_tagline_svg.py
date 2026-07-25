"""
A slim terminal-prompt banner that sits above the contribution graph: a fixed
"adi@github ~ $" prompt followed by a rotating tagline that wipes in
character-by-character (same clipPath+animate wipe as the ASCII portrait),
holds, fades, then the next line takes over -- looping forever (unlike the
one-shot portrait/heatmap, a rotating banner is expected to keep cycling).

Pure SMIL: each phrase's reveal + hold + fade is one repeatCount="indefinite"
cycle of length TOTAL, phase-shifted by `begin`, so all phrases stay in lockstep
without a driving script.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "tagline-banner.svg")

# EDIT THESE -- same story as info-card.svg, condensed to one line each.
PHRASES = [
    "Building @ Novexa IT",
    "TypeScript . Python . React . Firebase",
    "CareOps . secure vault . invoicing . 6+ shipped demos",
]

W = 860
H = 56
PAD = 20
FONT_SIZE = 16
CHAR_W = FONT_SIZE * 0.6
CPS = 18  # characters/second while "typing"
HOLD = 1.6
FADE = 0.35

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

PROMPT = "adi@github ~ $ "
prompt_w = len(PROMPT) * CHAR_W
text_x = PAD + prompt_w
mid_y = H / 2 + FONT_SIZE * 0.33

# ---- compute each phrase's slot within one shared cycle -------------------
slots = []
for p in PHRASES:
    type_dur = len(p) / CPS
    slots.append({"text": p, "type": type_dur, "slot": type_dur + HOLD + FADE})
TOTAL = sum(s["slot"] for s in slots)

t = 0.0
for s in slots:
    s["begin"] = t
    s["typed_at"] = t + s["type"]
    s["hold_end"] = s["typed_at"] + HOLD
    s["fade_end"] = s["hold_end"] + FADE
    t += s["slot"]

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="tbg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="10" fill="url(#tbg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{FRAME}"/>',
    f'<text x="{PAD}" y="{mid_y:.1f}" font-size="{FONT_SIZE}" font-weight="700">'
    f'<tspan fill="{GREEN}">adi</tspan><tspan fill="{MUTED}">@github</tspan>'
    f'<tspan fill="{ACCENT}"> ~ $ </tspan></text>',
]

for i, s in enumerate(slots):
    safe = html.escape(s["text"])
    art_w = len(s["text"]) * CHAR_W
    cursor_x = text_x + art_w + 2
    clip_id = f"tclip{i}"
    parts.append(
        f'<g opacity="0">'
        f'<animate attributeName="opacity" '
        f'keyTimes="0;{s["typed_at"]/TOTAL:.5f};{s["hold_end"]/TOTAL:.5f};{s["fade_end"]/TOTAL:.5f};1" '
        f'values="1;1;1;0;0" begin="{s["begin"]:.3f}s" dur="{TOTAL:.3f}s" repeatCount="indefinite" fill="freeze"/>'
        f'<clipPath id="{clip_id}"><rect x="{text_x:.1f}" y="0" height="{H}" width="0">'
        f'<animate attributeName="width" from="0" to="{art_w:.1f}" '
        f'begin="{s["begin"]:.3f}s" dur="{s["type"]:.3f}s" fill="freeze"/></rect></clipPath>'
        f'<g clip-path="url(#{clip_id})">'
        f'<text xml:space="preserve" x="{text_x:.1f}" y="{mid_y:.1f}" fill="{INK}" '
        f'font-size="{FONT_SIZE}">{safe}</text></g>'
        f'<rect x="{cursor_x:.1f}" y="{mid_y-FONT_SIZE*0.8:.1f}" width="{CHAR_W*0.6:.1f}" height="{FONT_SIZE}" fill="{INK}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
        f'</g>'
    )

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "cycle", round(TOTAL, 2), "s")
