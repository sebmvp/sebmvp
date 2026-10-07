"""Which cubes fill, and when.

Each letter owns a narrow column band. Spread cubes stay in that vertical
range so the dissolve reads as words turning into boxes, not cubes jumping
across the grid. End layout is still sporadic.

`github` is next: map sebmvp's real year onto this 53x7 grid.
"""

from header import config as C
from header.glyphs import letter_centers
from header.timeline import convert_start


def cell_at(x, y):
    c = int(round((x - C.OX) / C.PITCH))
    r = int(round((y - C.OY) / C.PITCH))
    return max(0, min(C.COLS - 1, c)), max(0, min(C.ROWS - 1, r))


def neighborhood(c, r, radius):
    cells = []
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            cc, rr = c + dc, r + dr
            if C.cell_exists(cc, rr):
                cells.append((cc, rr))
    return cells


def pick_level(rng):
    return rng.choices(C.LEVELS, weights=(4, 3, 2, 1))[0]


def simulate(rng):
    """Per-letter vertical spray. No cube from 'h' landing under 'portfolio'."""
    start = convert_start()
    taken = set()
    assigned = {}

    for i, (x, y) in enumerate(letter_centers()):
        t = start + i * C.CHAR_OUT
        c0, r0 = cell_at(x, y)
        if not C.cell_exists(c0, r0):
            continue
        if (c0, r0) not in taken:
            taken.add((c0, r0))
            assigned[(c0, r0)] = (t, rng.choice(C.LEVELS[2:]))
        near = [p for p in neighborhood(c0, r0, 1) if p not in taken]
        rng.shuffle(near)
        for cell in near[:3]:
            taken.add(cell)
            assigned[cell] = (t + 0.05, rng.choice(C.LEVELS[1:]))

        for r in range(C.ROWS):
            for dc in (-2, -1, 0, 1, 2):
                c = c0 + dc
                if not C.cell_exists(c, r) or (c, r) in taken:
                    continue
                d_row = abs(r - r0)
                d_col = abs(dc)
                if d_row == 0 and d_col <= 1:
                    continue
                if d_col == 0:
                    p = 0.82 * (0.62 ** max(d_row - 1, 0))
                elif d_col == 1:
                    p = 0.48 * (0.55 ** d_row)
                else:
                    p = 0.26 * (0.5 ** d_row)
                if rng.random() >= p:
                    continue
                taken.add((c, r))
                assigned[(c, r)] = (t + 0.08 + d_row * C.CHAR_OUT * 0.7, pick_level(rng))
    return assigned


def from_github(_rng):
    raise NotImplementedError(
        "Next: load sebmvp's real GitHub contribution year into this 53x7 grid"
    )


def load(source, rng):
    if source == "github":
        return from_github(rng)
    if source == "simulated":
        return simulate(rng)
    raise ValueError("source must be 'simulated' or 'github', got %r" % (source,))
