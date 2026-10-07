#!/usr/bin/env python3
"""Compact GitHub-block intro banner.

Same shape as the original profile-header (860x152). Cubes are the
contribution-graph language, not a snake sprite. Three short intros
light up as letters, then a quiet path crawls the grid.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/profile-header.svg"

W, H = 860, 152
ROWS, COLS = 7, 59
SIZE, GAP = 11, 3
RX = 2
PITCH = SIZE + GAP
GRID_W = COLS * PITCH - GAP
GRID_H = ROWS * PITCH - GAP
OX = (W - GRID_W) / 2
OY = (H - GRID_H) / 2

LETTER_GAP = 2
WORD_GAP = 3

DURATION = 28.0
# fade in, hold, fade out — long enough to read
PHRASES = [
    (0.4, 5.2, "HI THERE"),
    (6.0, 10.8, "THIS IS SEB"),
    (11.6, 16.4, "PORTFOLIO"),
]
CRAWL_START = 17.4
CRAWL_END = 26.8
TRAIL = 14
FADE = 0.7

# Quiet GitHub-green analog in violet. Empty cubes sit close to the card.
C0 = "#16141c"
C1 = "#2a2438"
C2 = "#3f335c"
C3 = "#5c4a86"
C4 = "#7a68b0"
HEAD = "#9b8bc4"
CARD = "#0c0b12"
BORDER = "#24202c"

# 5-wide glyphs; I is 3-wide so spaced phrases fit 59 columns.
FONT = {
    " ": ["     "] * 7,
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["###", " # ", " # ", " # ", " # ", " # ", "###"],
    "J": ["#####", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ### ", "#   #", "#    ", " ### ", "    #", "#   #", " ### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
}


def glyph_width(ch: str) -> int:
    return len(FONT[ch][0])


def measure(text: str) -> int:
    w = 0
    prev_space = True
    for ch in text:
        if ch == " ":
            w += WORD_GAP
            prev_space = True
            continue
        if not prev_space:
            w += LETTER_GAP
        w += glyph_width(ch)
        prev_space = False
    return w


def blit(text: str) -> set:
    cells = set()
    width = measure(text)
    x = max((COLS - width) // 2, 0)
    prev_space = True
    for ch in text:
        if ch == " ":
            x += WORD_GAP
            prev_space = True
            continue
        if not prev_space:
            x += LETTER_GAP
        rows = FONT[ch]
        gw = glyph_width(ch)
        for r, row in enumerate(rows):
            for c, mark in enumerate(row):
                if mark == "#" and 0 <= x + c < COLS:
                    cells.add((x + c, r))
        x += gw
        prev_space = False
    return cells


def zigzag_path():
    path = []
    for r in range(ROWS):
        cols = range(COLS) if r % 2 == 0 else range(COLS - 1, -1, -1)
        for c in cols:
            path.append((c, r))
    return path


def pct(t: float) -> str:
    return f"{min(max(t / DURATION * 100, 0), 100):.2f}%"


def keyframes_for(letter_windows, crawl_index, n_path):
    stops = [(0.0, C0)]
    for t0, t1 in letter_windows:
        # ease through the violet ramp so letters bloom instead of popping
        stops.append((t0, C0))
        stops.append((t0 + FADE * 0.35, C1))
        stops.append((t0 + FADE * 0.65, C3))
        stops.append((t0 + FADE, C4))
        stops.append((t1 - FADE, C4))
        stops.append((t1 - FADE * 0.65, C3))
        stops.append((t1 - FADE * 0.35, C1))
        stops.append((t1, C0))

    if n_path:
        span = CRAWL_END - CRAWL_START
        step = span / n_path
        t_head = CRAWL_START + crawl_index * step
        stops.append((max(t_head - step * 0.8, CRAWL_START), C0))
        stops.append((t_head, HEAD))
        stops.append((t_head + step * 2, C4))
        stops.append((t_head + step * 5, C3))
        stops.append((t_head + step * 9, C2))
        stops.append((t_head + step * TRAIL, C1))
        stops.append((t_head + step * (TRAIL + 3), C0))

    stops.append((DURATION, C0))
    stops.sort(key=lambda s: s[0])

    merged = []
    for t, col in stops:
        t = min(max(t, 0.0), DURATION)
        if merged and abs(merged[-1][0] - t) < 0.01 and merged[-1][1] == col:
            continue
        if merged and merged[-1][1] == col:
            merged[-1] = (t, col)
        else:
            merged.append((t, col))

    return "".join(f"{pct(t)}{{fill:{col}}}" for t, col in merged)


def build(preview_phrase=None, preview_crawl=None) -> str:
    phrase_cells = [(t0, t1, blit(text)) for t0, t1, text in PHRASES]
    path = zigzag_path()
    path_index = {cell: i for i, cell in enumerate(path)}

    css = [
        ".c{shape-rendering:geometricPrecision}",
        "@media (prefers-reduced-motion:reduce){.c{animation:none!important}}",
    ]
    rects = []
    kf_id = 0
    for r in range(ROWS):
        for c in range(COLS):
            x = OX + c * PITCH
            y = OY + r * PITCH
            cell = (c, r)
            fill = C0
            cls = "c"
            if preview_phrase is not None:
                if cell in phrase_cells[preview_phrase][2]:
                    fill = C4
            elif preview_crawl is not None:
                idx = path_index[cell]
                if idx == preview_crawl:
                    fill = HEAD
                elif 0 < preview_crawl - idx <= TRAIL:
                    ramp = [HEAD, C4, C4, C3, C3, C2, C2, C2, C1, C1, C1, C1, C1, C1]
                    fill = ramp[preview_crawl - idx - 1]
            else:
                windows = [
                    (t0, t1) for t0, t1, cells in phrase_cells if cell in cells
                ]
                body = keyframes_for(windows, path_index[cell], len(path))
                name = f"k{kf_id}"
                kf_id += 1
                css.append(f"@keyframes {name}{{{body}}}")
                css.append(
                    f".{name}{{animation:{name} {DURATION:.0f}s linear infinite}}"
                )
                cls = f"c {name}"
                if cell in phrase_cells[1][2]:
                    cls += " rm"

            rects.append(
                f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" '
                f'width="{SIZE}" height="{SIZE}" rx="{RX}" fill="{fill}"/>'
            )

    if preview_phrase is None and preview_crawl is None:
        css.append(
            "@media (prefers-reduced-motion:reduce){.c{fill:%s}.rm{fill:%s}}"
            % (C0, C4)
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Hi there. This is Seb\'s portfolio.">',
        f"<style>{''.join(css)}</style>",
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8" '
        f'fill="{CARD}" stroke="{BORDER}" stroke-width="1"/>',
        *rects,
        "</svg>",
    ]
    return "\n".join(svg) + "\n"


def main():
    for t0, t1, text in PHRASES:
        print(f"{text!r:16} width={measure(text)} / {COLS}")
    OUT.write_text(build())
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
