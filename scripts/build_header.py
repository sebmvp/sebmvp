#!/usr/bin/env python3
"""Intro banner: real SVG text, GitHub contribution grid overlaid on top.

Grid geometry matches aouellets/Platane snk: 880x192, 53x7, 12px cells,
4px gap. Letters are real terminal type and do not follow the cube grid.

Source of the animation is this file. It writes assets/profile-header.svg
with indented CSS keyframes (same approach as the contribution snake, which
Safari and GitHub actually play). Loop: type in, fast delete, type in again,
hold a few seconds, letters snap into nearby contribution cubes, reset.
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
CUBE = "#262430"
CUBE_OPACITY = 0.24
CUBE_STROKE = "#2e2b38"
CUBE_STROKE_OPACITY = 0.5

# GitHub-style contribution intensities, in this profile's violet.
# L1 dim → L4 brightest. Letters use the highest (L4).
LEVELS = ["#3a3152", "#5c4d86", "#7c6bb0", "#a78bfa"]
TEXT = LEVELS[-1]
MUTED = LEVELS[-1]

FONT = "Menlo, SF Mono, Monaco, ui-monospace, monospace"
LINE1 = "hi there!"
LINE2 = "welcome to seb's portfolio"
SIZE1, SIZE2 = 28, 28
ADV1, ADV2 = 17.0, 17.0  # Menlo Regular, same size both lines

# Placement (keep — user signed off).
X1 = OX + 56
Y1 = OY + GRID_H * 0.42
X2 = OX + GRID_W * 0.88
Y2 = OY + GRID_H * 0.72

CHAR_IN = 0.12
CHAR_DEL = 0.035  # nards-style backspace, much faster than type-in
CHAR_OUT = 0.04  # dissolve into cubes
LINE_PAUSE = 0.45
START_S = 0.25
READ_1 = 0.75  # beat after the first full message, then delete
GAP = 0.2
HOLD_S = 3.2  # sit on the second display before cubes
CUBE_HOLD = 6.5  # graph stays up before the loop resets (eater comes later)
REST = 0.88
SEED = 2026


def n_letters():
    return len(LINE1) + len(LINE2)


def type_span():
    return len(LINE1) * CHAR_IN + LINE_PAUSE + len(LINE2) * CHAR_IN


def type1_end():
    return START_S + type_span()


def delete_start():
    return type1_end() + READ_1


def type2_start():
    return delete_start() + n_letters() * CHAR_DEL + GAP


def type2_end():
    return type2_start() + type_span()


def convert_start():
    return type2_end() + HOLD_S


def convert_end():
    return convert_start() + n_letters() * CHAR_OUT


def total_s():
    return convert_end() + CUBE_HOLD + 0.5


def letter_offset(index):
    if index < len(LINE1):
        return index * CHAR_IN
    return len(LINE1) * CHAR_IN + LINE_PAUSE + (index - len(LINE1)) * CHAR_IN


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


def pick_level(rng):
    # Real graphs are mostly quieter days. L4 is rare.
    return rng.choices(LEVELS, weights=(4, 3, 2, 1))[0]


def assign_cubes(rng):
    """Glyph cells stay readable; extra cubes halo outward from the words.

    Later: mix in Sebastian's real contribution year around this residue.
    """
    start = convert_start()
    taken = set()
    assigned = {}
    cores = []

    for i, (x, y) in enumerate(letter_centers()):
        t = start + i * CHAR_OUT
        c0, r0 = cell_at(x, y)
        cores.append((c0, r0, t))
        if (c0, r0) not in taken:
            taken.add((c0, r0))
            assigned[(c0, r0)] = (t, rng.choice(LEVELS[2:]))
        near = [p for p in neighborhood(c0, r0, 1) if p not in taken]
        rng.shuffle(near)
        for cell in near[:2]:
            taken.add(cell)
            assigned[cell] = (t, rng.choice(LEVELS[1:]))

    def nearest(cell):
        return min(max(abs(cell[0] - c), abs(cell[1] - r)) for c, r, _ in cores)

    for r in range(ROWS):
        for c in range(COLS):
            if (c, r) in taken:
                continue
            d = nearest((c, r))
            if d < 2:
                continue
            # Falloff from the words: spread, not a full random year.
            p = 0.28 * (0.62 ** (d - 2))
            if rng.random() >= p:
                continue
            t = start + min(d, 8) * CHAR_OUT * 0.7
            taken.add((c, r))
            assigned[(c, r)] = (t, pick_level(rng))
    return assigned


def bump(values):
    """Keep keyframe percents strictly increasing and inside 0..99.9."""
    out = []
    last = -0.05
    for x in values:
        x = max(x, last + 0.05)
        x = min(x, 99.9)
        out.append(x)
        last = x
    return out


def letter_css(g, total):
    i = g["index"]
    n = n_letters()
    a1 = g["appear"]
    dlt = delete_start() + (n - 1 - i) * CHAR_DEL
    a2 = type2_start() + letter_offset(i)
    conv = convert_start() + i * CHAR_OUT
    a1p, a1on, dp, doff, a2p, a2on, cp, coff = bump(
        [
            pct(a1, total),
            pct(a1 + 0.02, total),
            pct(dlt, total),
            pct(dlt + 0.02, total),
            pct(a2, total),
            pct(a2 + 0.02, total),
            pct(conv, total),
            pct(conv + 0.02, total),
        ]
    )
    return (
        f"    @keyframes L{i} {{\n"
        f"      0%, {a1p:.2f}% {{ opacity: 0; }}\n"
        f"      {a1on:.2f}%, {dp:.2f}% {{ opacity: {REST}; }}\n"
        f"      {doff:.2f}%, {a2p:.2f}% {{ opacity: 0; }}\n"
        f"      {a2on:.2f}%, {cp:.2f}% {{ opacity: {REST}; }}\n"
        f"      {coff:.2f}%, 100% {{ opacity: 0; }}\n"
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
                f'stroke="{CUBE_STROKE}" stroke-opacity="{CUBE_STROKE_OPACITY}" '
                f'stroke-width="0.8"/>'
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
        f"loop={total_s():.1f}s in={CHAR_IN}s del={CHAR_DEL}s out={CHAR_OUT}s"
    )


if __name__ == "__main__":
    main()
