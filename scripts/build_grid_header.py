#!/usr/bin/env python3
"""Compact GitHub-block intro banner.

Real type is sampled onto the contribution grid (the grid sits over the
letters). Cubes the glyph actually touches fill at GitHub-like intensity
and stay filled after the word fades. No 5x7 box font.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/profile-header.svg"

W, H = 860, 152
ROWS, COLS = 11, 79
SIZE, GAP = 8, 2
RX = 1.8
PITCH = SIZE + GAP
GRID_W = COLS * PITCH - GAP
GRID_H = ROWS * PITCH - GAP
OX = (W - GRID_W) / 2
OY = (H - GRID_H) / 2

FONT_CANDIDATES = [
    ("/System/Library/Fonts/HelveticaNeue.ttc", 10),  # Medium
    ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
    ("/System/Library/Fonts/Helvetica.ttc", 0),
]
FONT_SIZE = 84
SCALE = 4

DURATION = 26.0
FADE = 0.8
PHRASES = [
    (0.4, 5.0, "HI THERE"),
    (5.8, 10.6, "THIS IS SEB"),
    (11.4, 16.4, "PORTFOLIO"),
]
SETTLE = 0.7
END_FADE_START = 17.6
END_FADE_DONE = 19.0

C0 = "#16141c"
C1 = "#2c2540"
C2 = "#433564"
C3 = "#5e4d8a"
C4 = "#7a68b0"
LEVELS = [C0, C1, C2, C3, C4]
RESIDUAL = C1
CARD = "#0c0b12"
BORDER = "#24202c"


def load_font(size: int) -> ImageFont.FreeTypeFont:
    last = None
    for path, index in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size, index=index)
        except OSError as exc:
            last = exc
    raise RuntimeError(f"no usable font ({last})")


def raster_phrase(text: str) -> Image.Image:
    font = load_font(FONT_SIZE * SCALE)
    img = Image.new("L", (W * SCALE, H * SCALE), 0)
    draw = ImageDraw.Draw(img)
    tracking = int(FONT_SIZE * SCALE * 0.09)
    space = int(FONT_SIZE * SCALE * 0.48)
    widths = []
    for ch in text:
        if ch == " ":
            widths.append(space)
            continue
        box = draw.textbbox((0, 0), ch, font=font)
        widths.append(box[2] - box[0] + tracking)
    total = sum(widths)
    probe = draw.textbbox((0, 0), "Hg", font=font)
    y = (H * SCALE - (probe[3] - probe[1])) / 2 - probe[1]
    x = (W * SCALE - total) / 2
    for ch, w in zip(text, widths):
        if ch != " ":
            draw.text((x, y), ch, fill=255, font=font)
        x += w
    return img


def coverage_grid(img: Image.Image) -> list:
    pix = img.load()
    iw, ih = img.size
    grid = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            x0 = max(int((OX + c * PITCH) * SCALE), 0)
            y0 = max(int((OY + r * PITCH) * SCALE), 0)
            x1 = min(int((OX + c * PITCH + SIZE) * SCALE), iw)
            y1 = min(int((OY + r * PITCH + SIZE) * SCALE), ih)
            if x1 <= x0 or y1 <= y0:
                row.append(0.0)
                continue
            total = 0
            n = 0
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    total += pix[xx, yy]
                    n += 1
            row.append((total / n) / 255.0 if n else 0.0)
        grid.append(row)
    return grid


def level_for(cov: float) -> int:
    if cov < 0.05:
        return 0
    if cov < 0.22:
        return 1
    if cov < 0.42:
        return 2
    if cov < 0.68:
        return 3
    return 4


def pct(t: float) -> str:
    return f"{min(max(t / DURATION * 100.0, 0), 100):.2f}%"


def keyframes(stops: list) -> str:
    stops = sorted((min(max(t, 0), DURATION), col) for t, col in stops)
    merged = []
    for t, col in stops:
        if merged and abs(merged[-1][0] - t) < 0.02 and merged[-1][1] == col:
            continue
        if merged and merged[-1][1] == col:
            merged[-1] = (t, col)
        else:
            merged.append((t, col))
    return "".join(f"{pct(t)}{{fill:{col}}}" for t, col in merged)


def timeline_for(cell_levels: list) -> str:
    stops = [(0.0, C0)]
    ever = False
    for i, (t0, hold_end, _text) in enumerate(PHRASES):
        lv = cell_levels[i]
        if lv:
            ever = True
            color = LEVELS[lv]
            stops.append((t0, stops[-1][1]))
            stops.append((t0 + FADE * 0.4, LEVELS[max(lv - 2, 1)]))
            stops.append((t0 + FADE, color))
            stops.append((hold_end, color))
            if i < len(PHRASES) - 1:
                stops.append((hold_end + SETTLE, RESIDUAL))
        elif ever:
            stops.append((t0, RESIDUAL))
            stops.append((hold_end + SETTLE, RESIDUAL))
    if ever:
        stops.append((END_FADE_START, stops[-1][1]))
        stops.append((END_FADE_DONE, C0))
    stops.append((DURATION, C0))
    return keyframes(stops)


def build(preview_phrase=None) -> str:
    phrase_levels = []
    for _t0, _t1, text in PHRASES:
        cov = coverage_grid(raster_phrase(text))
        phrase_levels.append(
            [[level_for(cov[r][c]) for c in range(COLS)] for r in range(ROWS)]
        )

    css = [
        ".c{shape-rendering:geometricPrecision}",
        "@media (prefers-reduced-motion:reduce){.c{animation:none!important}}",
    ]
    rects = []
    kf_id = 0
    seb = phrase_levels[1]

    for r in range(ROWS):
        for c in range(COLS):
            x = OX + c * PITCH
            y = OY + r * PITCH
            levels = [phrase_levels[i][r][c] for i in range(len(PHRASES))]
            fill = C0
            cls = "c"
            if preview_phrase is not None:
                lv = phrase_levels[preview_phrase][r][c]
                if lv:
                    fill = LEVELS[lv]
                elif preview_phrase > 0 and any(
                    phrase_levels[i][r][c] for i in range(preview_phrase)
                ):
                    fill = RESIDUAL
            else:
                if any(levels):
                    body = timeline_for(levels)
                    name = f"k{kf_id}"
                    kf_id += 1
                    css.append(f"@keyframes {name}{{{body}}}")
                    css.append(
                        f".{name}{{animation:{name} {DURATION:.0f}s linear infinite}}"
                    )
                    cls = f"c {name}"
                    if seb[r][c]:
                        cls += " rm"
                        fill = LEVELS[seb[r][c]]
            rects.append(
                f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" '
                f'width="{SIZE}" height="{SIZE}" rx="{RX}" fill="{fill}"/>'
            )

    if preview_phrase is None:
        css.append(
            "@media (prefers-reduced-motion:reduce){.c{fill:%s}.rm{fill:%s}}"
            % (C0, C3)
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Hi there. This is Seb\'s portfolio.">\n'
        f"<style>{''.join(css)}</style>\n"
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8" '
        f'fill="{CARD}" stroke="{BORDER}" stroke-width="1"/>\n'
        + "\n".join(rects)
        + "\n</svg>\n"
    )


def main():
    OUT.write_text(build())
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
