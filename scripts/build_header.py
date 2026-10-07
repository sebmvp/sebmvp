#!/usr/bin/env python3
"""Intro banner: real SVG text, GitHub contribution grid overlaid on top.

Grid geometry matches aouellets/Platane snk: 880x192, 53x7, 12px cells,
4px gap. Letters are real terminal type and do not follow the cube grid.

Plays once: type in, hold, then each letter snaps off faster and fills
a couple of nearby cubes at random contribution levels. No fade.
"""

import os
import random
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

# GitHub-style contribution intensities, in this profile's violet.
LEVELS = ["#3a3152", "#5c4d86", "#7c6bb0", "#a78bfa"]

FONT = "Menlo, SF Mono, Monaco, ui-monospace, monospace"
LINE1 = "hi there!"
LINE2 = "welcome to seb's portfolio"
SIZE1, SIZE2 = 28, 22
ADV1, ADV2 = 17.0, 13.0  # Menlo Regular advances

CHAR_IN = 0.12
CHAR_OUT = 0.04  # faster dissolve
LINE_PAUSE = 0.45
START_S = 0.25
HOLD_S = 2.8
REST = 0.88
SEED = 2026


def type_end() -> float:
    return START_S + len(LINE1) * CHAR_IN + LINE_PAUSE + len(LINE2) * CHAR_IN


def convert_start() -> float:
    return type_end() + HOLD_S


def total_s() -> float:
    n = len(LINE1) + len(LINE2)
    return convert_start() + n * CHAR_OUT + 0.35


def letter_in_out(appear_s: float, out_s: float, total: float) -> str:
    a = appear_s / total
    snap_in = min(0.999, (appear_s + 0.04) / total)
    o = out_s / total
    snap_out = min(0.999, (out_s + 0.03) / total)
    return (
        f'<animate attributeName="opacity" '
        f'values="0;0;{REST};{REST};0" '
        f'keyTimes="0;{a:.4f};{snap_in:.4f};{o:.4f};{snap_out:.4f}" '
        f'keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1" '
        f'calcMode="spline" dur="{total:.2f}s" repeatCount="1" fill="freeze"/>'
    )


def cube_fill_anim(at_s: float, color: str, total: float) -> str:
    t = at_s / total
    snap = min(0.999, (at_s + 0.12) / total)
    return (
        f'<animate attributeName="fill" values="{CUBE};{CUBE};{color}" '
        f'keyTimes="0;{t:.4f};{snap:.4f}" dur="{total:.2f}s" '
        f'repeatCount="1" fill="freeze"/>'
        f'<animate attributeName="fill-opacity" values="{CUBE_OPACITY};{CUBE_OPACITY};1" '
        f'keyTimes="0;{t:.4f};{snap:.4f}" dur="{total:.2f}s" '
        f'repeatCount="1" fill="freeze"/>'
    )


def cell_at(x: float, y: float):
    c = int(round((x - OX) / PITCH))
    r = int(round((y - OY) / PITCH))
    return max(0, min(COLS - 1, c)), max(0, min(ROWS - 1, r))


def neighborhood(c: int, r: int, radius: int):
    cells = []
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            cc, rr = c + dc, r + dr
            if 0 <= cc < COLS and 0 <= rr < ROWS:
                cells.append((cc, rr))
    return cells


def letter_centers():
    x1 = OX + 56
    y1 = OY + GRID_H * 0.42
    x2 = OX + GRID_W * 0.80
    y2 = OY + GRID_H * 0.72
    pts = []
    for i in range(len(LINE1)):
        pts.append((x1 + (i + 0.5) * ADV1, y1))
    n2 = len(LINE2)
    for i in range(n2):
        pts.append((x2 - (n2 - i - 0.5) * ADV2, y2))
    return pts


def assign_cubes(rng):
    """Map grid cell -> (fill_time, level color). First letter to claim a cell wins."""
    start = convert_start()
    taken = set()
    assigned = {}
    for i, (x, y) in enumerate(letter_centers()):
        t = start + i * CHAR_OUT
        c0, r0 = cell_at(x, y)
        pool = [p for p in neighborhood(c0, r0, 2) if p not in taken]
        if len(pool) < 2:
            pool = [p for p in neighborhood(c0, r0, 3) if p not in taken]
        n = rng.choice((2, 3))
        rng.shuffle(pool)
        for cell in pool[:n]:
            taken.add(cell)
            assigned[cell] = (t, rng.choice(LEVELS))
    return assigned


def type_line(text, start_s, index0, total, preview):
    conv = convert_start()
    parts = []
    for i, ch in enumerate(text):
        if preview == "cubes":
            op, anim = "0", ""
        elif preview == "hold":
            op, anim = str(REST), ""
        else:
            op = str(REST)
            anim = letter_in_out(start_s + i * CHAR_IN, conv + (index0 + i) * CHAR_OUT, total)
        parts.append(f'<tspan opacity="{op}">{escape(ch)}{anim}</tspan>')
    return "".join(parts)


def build(preview=None):
    rng = random.Random(SEED)
    fills = assign_cubes(rng)
    total = total_s()
    freeze = preview is not None

    cubes = []
    for r in range(ROWS):
        for c in range(COLS):
            x = OX + c * PITCH
            y = OY + r * PITCH
            event = fills.get((c, r))
            if preview == "cubes" and event:
                cubes.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" '
                    f'rx="{RX}" fill="{event[1]}" fill-opacity="1" '
                    f'stroke="{CUBE_STROKE}" stroke-width="0.8"/>'
                )
                continue
            anim = ""
            if not freeze and event:
                anim = cube_fill_anim(event[0], event[1], total)
            cubes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" '
                f'rx="{RX}" fill="{CUBE}" fill-opacity="{CUBE_OPACITY}" '
                f'stroke="{CUBE_STROKE}" stroke-width="0.8">{anim}</rect>'
            )

    x1 = OX + 56
    y1 = OY + GRID_H * 0.42
    x2 = OX + GRID_W * 0.80
    y2 = OY + GRID_H * 0.72
    t2 = START_S + len(LINE1) * CHAR_IN + LINE_PAUSE

    text = []
    if preview != "cubes":
        text = [
            f'<text x="{x1:.1f}" y="{y1:.1f}" text-anchor="start" '
            f'dominant-baseline="middle" xml:space="preserve" '
            f'font-family="{FONT}" font-size="{SIZE1}" font-weight="400" fill="{TEXT}">'
            f"{type_line(LINE1, START_S, 0, total, preview)}</text>",
            f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="end" '
            f'dominant-baseline="middle" xml:space="preserve" '
            f'font-family="{FONT}" font-size="{SIZE2}" font-weight="400" fill="{MUTED}">'
            f"{type_line(LINE2, t2, len(LINE1), total, preview)}</text>",
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
    preview = os.environ.get("PREVIEW") or None
    OUT.write_text(build(preview=preview))
    print(
        f"wrote {OUT} ({OUT.stat().st_size} bytes) "
        f"once={total_s():.1f}s in={CHAR_IN}s out={CHAR_OUT}s"
    )


if __name__ == "__main__":
    main()
