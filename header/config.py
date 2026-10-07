"""Geometry, copy, and palette. Grid matches aouellets/Platane snk 880x192."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/profile-header.svg"

W, H = 880, 192
COLS, ROWS = 53, 7
# GitHub's last week is incomplete (not a full rectangle). Snake enters here.
LAST_WEEK_DAYS = 3
SIZE, GAP = 12, 4
PITCH = SIZE + GAP
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

# L1 dim → L4 brightest. Letters use L4.
LEVELS = ["#3a3152", "#5c4d86", "#7c6bb0", "#a78bfa"]
TEXT = LEVELS[-1]
MUTED = LEVELS[-1]
SNAKE = "#ddd6fe"  # brighter than L4 contributions so the head reads
# platane/snk is ~276ms/step; faster on average (jitter in eater).
EAT_STEP = 0.12

FONT = "Menlo, SF Mono, Monaco, ui-monospace, monospace"
LINE1 = "hi there!"
LINE2 = "welcome to seb's portfolio"
SIZE1 = SIZE2 = 28
ADV1 = ADV2 = 17.0

X1 = OX + 56
Y1 = OY + GRID_H * 0.42
X2 = OX + GRID_W * 0.88
Y2 = OY + GRID_H * 0.72

CHAR_IN = 0.12
CHAR_DEL = 0.035
CHAR_OUT = 0.04
LINE_PAUSE = 0.45
START_S = 0.25
READ_1 = 0.75
GAP = 0.2
HOLD_S = 3.2
CUBE_HOLD = 2.8
REST = 0.88

# Exact snk snake parts: head largest, tail smallest, extra-round.
SNAKE_PARTS = (
    ("s0", 14.4, 4.5),
    ("s1", 12.3, 4.1),
    ("s2", 10.8, 3.6),
    ("s3", 9.9, 3.3),
)


def cell_exists(c, r):
    if c < 0 or c >= COLS or r < 0 or r >= ROWS:
        return False
    if c == COLS - 1 and r >= LAST_WEEK_DAYS:
        return False
    return True
