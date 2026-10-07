#!/usr/bin/env python3
"""Intro banner: real SVG text, GitHub contribution grid overlaid on top.

Grid geometry matches aouellets/Platane snk: 880x192, 53x7, 12px cells,
4px gap. Letters are real type and do not follow the cube grid.
No fade, no crawl — get the intro readable first.
"""

from pathlib import Path

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
TEXT = "#e8e3f4"
MUTED = "#c8c0d8"
CUBE = "#262430"
CUBE_OPACITY = 0.42
CUBE_STROKE = "#323040"

LINE1 = "Hi there"
LINE2 = "This is Seb's portfolio"


def build() -> str:
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

    cx = W / 2
    cy = H / 2
    text = [
        f'<text x="{cx:.1f}" y="{cy - 18:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" '
        f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
        f'font-size="34" font-weight="600" fill="{TEXT}" '
        f'letter-spacing="0.6">{LINE1}</text>',
        f'<text x="{cx:.1f}" y="{cy + 20:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" '
        f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
        f'font-size="26" font-weight="500" fill="{MUTED}" '
        f'letter-spacing="0.4">{LINE2}</text>',
    ]

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Hi there. This is Seb\'s portfolio.">',
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8" '
            f'fill="{CARD}" stroke="{BORDER}" stroke-width="1"/>',
            # Type first, grid on top — letters do not snap to cubes.
            *text,
            *cubes,
            "</svg>",
            "",
        ]
    )


def main():
    OUT.write_text(build())
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes) grid {COLS}x{ROWS} {W}x{H}")


if __name__ == "__main__":
    main()
