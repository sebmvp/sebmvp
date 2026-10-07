"""Which cubes fill, and when.

`simulated` (default): letter-shaped residue plus a halo. Seeded RNG so a
build can be reproduced, or omitted so each build is a new spread.

`github` is the next step: map sebmvp's real year onto this 53x7 grid.
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
            if 0 <= cc < C.COLS and 0 <= rr < C.ROWS:
                cells.append((cc, rr))
    return cells


def pick_level(rng):
    return rng.choices(C.LEVELS, weights=(4, 3, 2, 1))[0]


def simulate(rng):
    """Glyph cores stay readable; extra cubes halo outward from the words."""
    start = convert_start()
    taken = set()
    assigned = {}
    cores = []

    for i, (x, y) in enumerate(letter_centers()):
        t = start + i * C.CHAR_OUT
        c0, r0 = cell_at(x, y)
        cores.append((c0, r0, t))
        if (c0, r0) not in taken:
            taken.add((c0, r0))
            assigned[(c0, r0)] = (t, rng.choice(C.LEVELS[2:]))
        near = [p for p in neighborhood(c0, r0, 1) if p not in taken]
        rng.shuffle(near)
        for cell in near[:2]:
            taken.add(cell)
            assigned[cell] = (t, rng.choice(C.LEVELS[1:]))

    def nearest(cell):
        return min(max(abs(cell[0] - c), abs(cell[1] - r)) for c, r, _ in cores)

    for r in range(C.ROWS):
        for c in range(C.COLS):
            if (c, r) in taken:
                continue
            d = nearest((c, r))
            if d < 2:
                continue
            p = 0.28 * (0.62 ** (d - 2))
            if rng.random() >= p:
                continue
            t = start + min(d, 8) * C.CHAR_OUT * 0.7
            taken.add((c, r))
            assigned[(c, r)] = (t, pick_level(rng))
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
