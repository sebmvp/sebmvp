#!/usr/bin/env python3
"""Intro banner: real SVG text, GitHub contribution grid overlaid on top.

Grid geometry matches aouellets/Platane snk: 880x192, 53x7, 12px cells,
4px gap. Letters are real terminal type and do not follow the cube grid.

hi there! types on upper-left (toward middle); welcome types lower-right
(shifted left, toward middle). One glyph at a time, typewriter cadence.
"""

import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/profile-header.svg"

# One-to-one with Alexander's contribution strip.
W, H = 880, 192
COLS, ROWS = 53, 7
SIZE, GAP = 12, 4
PITCH = SIZE + GAP  # 16
RX = 2
GRID_W = COLS * PITCH - GAP
GRID_H = ROWS * PITCH - GAP
OX = (W - GRID_W) / 2
OY = (H - GRID_H) / 2

CARD = "#0c0b12"
BORDER = "#24202c"
TEXT = "#b4adbf"
MUTED = "#9a93a6"
CUBE = "#262430"
CUBE_OPACITY = 0.48
CUBE_STROKE = "#2e2b38"

FONT = "Menlo, SF Mono, Monaco, ui-monospace, monospace"
LINE1 = "hi there!"
LINE2 = "welcome to seb's portfolio"

# readme-typing-svg-ish: ~120ms/glyph, not a fade of the whole line.
CHAR_S = 0.12
LINE_PAUSE = 0.45
START_S = 0.25
HOLD_S = 4.0
FADE_S = 0.9
REST = 0.88


def loop_s() -> float:
    typed = START_S + len(LINE1) * CHAR_S + LINE_PAUSE + len(LINE2) * CHAR_S
    return typed + HOLD_S + FADE_S + 0.7


def letter_anim(appear_s: float, fade_s: float, total: float) -> str:
    a = appear_s / total
    snap = min(0.999, (appear_s + 0.04) / total)
    f0 = fade_s / total
    f1 = min(0.999, (fade_s + FADE_S) / total)
    return (
        f'<animate attributeName="opacity" '
        f'values="0;0;{REST};{REST};0;0" '
        f'keyTimes="0;{a:.4f};{snap:.4f};{f0:.4f};{f1:.4f};1" '
        f'keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1" '
        f'calcMode="spline" dur="{total:.2f}s" repeatCount="indefinite"/>'
    )


def type_line(text: str, start_s: float, fade_s: float, total: float, preview: bool) -> str:
    parts = []
    for i, ch in enumerate(text):
        anim = "" if preview else letter_anim(start_s + i * CHAR_S, fade_s, total)
        parts.append(f'<tspan opacity="{REST}">{escape(ch)}{anim}</tspan>')
    return "".join(parts)


def build(*, preview: bool = False) -> str:
    cubes = []
    for r in range(ROWS):
        for c in range(COLS):
            x = OX + c * PITCH
            y = OY + r * PITCH
            cubes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" '
                f'rx="{RX}" fill="{CUBE}" fill-opacity="{CUBE_OPACITY}" '
                f'stroke="{CUBE_STROKE}" stroke-width="0.8"/>'
            )

    # Left/upper toward center; right/lower shifted left toward center.
    x1 = OX + 48
    y1 = OY + GRID_H * 0.40
    x2 = OX + GRID_W * 0.82
    y2 = OY + GRID_H * 0.74

    total = loop_s()
    t2 = START_S + len(LINE1) * CHAR_S + LINE_PAUSE
    fade_at = t2 + len(LINE2) * CHAR_S + HOLD_S

    text = [
        f'<text x="{x1:.1f}" y="{y1:.1f}" text-anchor="start" '
        f'dominant-baseline="middle" xml:space="preserve" '
        f'font-family="{FONT}" font-size="26" font-weight="400" fill="{TEXT}">'
        f"{type_line(LINE1, START_S, fade_at, total, preview)}</text>",
        f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="end" '
        f'dominant-baseline="middle" xml:space="preserve" '
        f'font-family="{FONT}" font-size="20" font-weight="400" fill="{MUTED}">'
        f"{type_line(LINE2, t2, fade_at, total, preview)}</text>",
    ]

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="hi there! welcome to seb\'s portfolio">',
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8" '
            f'fill="{CARD}" stroke="{BORDER}" stroke-width="1"/>',
            *text,
            *cubes,
            "</svg>",
            "",
        ]
    )


def main():
    preview = os.environ.get("PREVIEW") == "1"
    OUT.write_text(build(preview=preview))
    total = loop_s()
    print(
        f"wrote {OUT} ({OUT.stat().st_size} bytes) "
        f"grid {COLS}x{ROWS} {W}x{H} loop={total:.1f}s char={CHAR_S}s"
    )


if __name__ == "__main__":
    main()
