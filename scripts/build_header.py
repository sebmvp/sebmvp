#!/usr/bin/env python3
"""Intro banner: real SVG text, GitHub contribution grid overlaid on top.

Grid geometry matches aouellets/Platane snk: 880x192, 53x7, 12px cells,
4px gap. Letters are real terminal type and do not follow the cube grid.

Source of the animation is this file. It writes assets/profile-header.svg
with indented CSS keyframes (same approach as the contribution snake, which
Safari and GitHub actually play). Loop: type in, hold, letters snap into
nearby contribution cubes, hold, reset.
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

# Placement (keep — user signed off).
X1 = OX + 56
Y1 = OY + GRID_H * 0.42
X2 = OX + GRID_W * 0.80
Y2 = OY + GRID_H * 0.72

CHAR_IN = 0.12
CHAR_OUT = 0.04
LINE_PAUSE = 0.45
START_S = 0.25
HOLD_S = 2.8
CUBE_HOLD = 2.4
REST = 0.88
SEED = 2026


def type_end():
    return START_S + len(LINE1) * CHAR_IN + LINE_PAUSE + len(LINE2) * CHAR_IN


def convert_start():
    return type_end() + HOLD_S


def convert_end():
    return convert_start() + (len(LINE1) + len(LINE2)) * CHAR_OUT


def total_s():
    return convert_end() + CUBE_HOLD + 0.5


def pct(seconds, total):
    return max(0.0, min(100.0, 100.0 * seconds / total))


def glyphs():
    """One real character, with its own x/y. Spaces keep timing for cube fill."""
    out = []
    for i, ch in enumerate(LINE1):
        out.append(
            {
                "ch": ch,
                "x": X1 + i * ADV1,
                "y": Y1,
                "size": SIZE1,
                "fill": TEXT,
                "appear": START_S + i * CHAR_IN,
                "index": i,
            }
        )
    t2 = START_S + len(LINE1) * CHAR_IN + LINE_PAUSE
    n2 = len(LINE2)
    for i, ch in enumerate(LINE2):
        out.append(
            {
                "ch": ch,
                "x": X2 - (n2 - i) * ADV2,
                "y": Y2,
                "size": SIZE2,
                "fill": MUTED,
                "appear": t2 + i * CHAR_IN,
                "index": len(LINE1) + i,
            }
        )
    return out


def letter_centers():
    return [(g["x"] + (ADV1 if g["size"] == SIZE1 else ADV2) / 2, g["y"]) for g in glyphs()]


def cell_at(x, y):
    c = int(round((x - OX) / PITCH))
    r = int(round((y - OY) / PITCH))
    return max(0, min(COLS - 1, c)), max(0, min(ROWS - 1, r))


def neighborhood(c, r, radius):
    cells = []
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            cc, rr = c + dc, r + dr
            if 0 <= cc < COLS and 0 <= rr < ROWS:
                cells.append((cc, rr))
    return cells


def assign_cubes(rng):
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


def letter_css(g, total):
    i = g["index"]
    appear = pct(g["appear"], total)
    on = pct(g["appear"] + 0.02, total)
    out = pct(convert_start() + i * CHAR_OUT, total)
    off = pct(convert_start() + i * CHAR_OUT + 0.02, total)
    if on <= appear:
        on = min(100.0, appear + 0.05)
    if out <= on:
        out = min(100.0, on + 0.05)
    if off <= out:
        off = min(100.0, out + 0.05)
    return (
        f"    @keyframes L{i} {{\n"
        f"      0%, {appear:.2f}% {{ opacity: 0; }}\n"
        f"      {on:.2f}%, {out:.2f}% {{ opacity: {REST}; }}\n"
        f"      {off:.2f}%, 100% {{ opacity: 0; }}\n"
        f"    }}\n"
        f"    .L{i} {{ animation: L{i} {total:.2f}s linear infinite; }}\n"
    )


def cube_css(idx, at_s, color, total):
    t = pct(at_s, total)
    on = pct(at_s + 0.08, total)
    hold = pct(convert_end() + CUBE_HOLD, total)
    reset = pct(convert_end() + CUBE_HOLD + 0.2, total)
    if on <= t:
        on = min(100.0, t + 0.05)
    if hold <= on:
        hold = min(100.0, on + 0.05)
    if reset <= hold:
        reset = min(100.0, hold + 0.05)
    return (
        f"    @keyframes C{idx} {{\n"
        f"      0%, {t:.2f}% {{ fill: {CUBE}; fill-opacity: {CUBE_OPACITY}; }}\n"
        f"      {on:.2f}%, {hold:.2f}% {{ fill: {color}; fill-opacity: 1; }}\n"
        f"      {reset:.2f}%, 100% {{ fill: {CUBE}; fill-opacity: {CUBE_OPACITY}; }}\n"
        f"    }}\n"
        f"    .C{idx} {{ animation: C{idx} {total:.2f}s linear infinite; }}\n"
    )


def build(preview=None):
    rng = random.Random(SEED)
    fills = assign_cubes(rng)
    total = total_s()
    letters = glyphs()

    css = [
        "    text { font-family: Menlo, 'SF Mono', Monaco, ui-monospace, monospace; }",
    ]
    if preview is None:
        for g in letters:
            css.append(letter_css(g, total).rstrip())

    cube_class = {}
    idx = 0
    for cell, (at_s, color) in sorted(fills.items()):
        cube_class[cell] = (f"C{idx}", color)
        if preview is None:
            css.append(cube_css(idx, at_s, color, total).rstrip())
        idx += 1

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="hi there! welcome to seb\'s portfolio">',
        "  <!-- generated by scripts/build_header.py — animation lives here -->",
        "  <style>",
        *css,
        "  </style>",
        f'  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" '
        f'fill="{CARD}" stroke="{BORDER}" stroke-width="1"/>',
        '  <g id="letters">',
    ]

    if preview != "cubes":
        for g in letters:
            op = REST
            cls = "glyph" if preview else f"glyph L{g['index']}"
            lines.append(
                f'    <text class="{cls}" x="{g["x"]:.1f}" y="{g["y"]:.1f}" '
                f'text-anchor="start" dominant-baseline="middle" '
                f'font-size="{g["size"]}" fill="{g["fill"]}" opacity="{op}">'
                f'{escape(g["ch"])}</text>'
            )

    lines.append("  </g>")
    lines.append('  <g id="grid">')

    for r in range(ROWS):
        for c in range(COLS):
            x = OX + c * PITCH
            y = OY + r * PITCH
            event = cube_class.get((c, r))
            if preview == "cubes" and event:
                lines.append(
                    f'    <rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" '
                    f'rx="{RX}" fill="{event[1]}" fill-opacity="1" '
                    f'stroke="{CUBE_STROKE}" stroke-width="0.8"/>'
                )
                continue
            cls = f' class="{event[0]}"' if (preview is None and event) else ""
            lines.append(
                f'    <rect{cls} x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" '
                f'rx="{RX}" fill="{CUBE}" fill-opacity="{CUBE_OPACITY}" '
                f'stroke="{CUBE_STROKE}" stroke-width="0.8"/>'
            )

    lines.append("  </g>")
    lines.append("</svg>")
    lines.append("")
    return "\n".join(lines)


def main():
    preview = os.environ.get("PREVIEW") or None
    OUT.write_text(build(preview=preview))
    print(
        f"wrote {OUT} ({OUT.stat().st_size} bytes) "
        f"loop={total_s():.1f}s in={CHAR_IN}s out={CHAR_OUT}s css-loop"
    )


if __name__ == "__main__":
    main()
