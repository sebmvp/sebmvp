"""Snake that eats filled cubes after the graph sits.

Matches platane/snk: four tapered rounded squares, orthogonal 16px steps,
CSS linear slides. Enters from the incomplete last week on the right.
Slightly faster than snk (~220ms/step vs ~276ms).
"""

from header import config as C
from header.timeline import eat_start


def cell_xy(c, r):
    return C.OX + c * C.PITCH, C.OY + r * C.PITCH


def route(a, b):
    """Orthogonal cells from a (exclusive) to b (inclusive)."""
    path = []
    c, r = a
    while c != b[0]:
        c += 1 if b[0] > c else -1
        path.append((c, r))
    while r != b[1]:
        r += 1 if b[1] > r else -1
        path.append((c, r))
    return path


def eat_path(filled):
    """Come in from the right, then greedy-Manhattan through filled cells."""
    remaining = {p for p in filled if C.cell_exists(*p)}
    start = (C.COLS, 0)  # one cell off the last week
    entry = (C.COLS - 1, 0)
    path = [start]
    path.extend(route(start, entry))
    cur = path[-1]
    remaining.discard(cur)
    while remaining:
        nxt = min(
            remaining,
            key=lambda p: (
                abs(p[0] - cur[0]) + abs(p[1] - cur[1]),
                -p[0],
                p[1],
            ),
        )
        path.extend(route(cur, nxt))
        for cell in path:
            remaining.discard(cell)
        cur = path[-1]
    return path


def step_times(path):
    start = eat_start()
    return [start + i * C.EAT_STEP for i in range(len(path))]


def eat_times(path, filled):
    """First time the head visits each filled cell."""
    filled = set(filled)
    times = {}
    for i, cell in enumerate(path):
        if cell in filled and cell not in times:
            times[cell] = eat_start() + i * C.EAT_STEP
    for cell in filled:
        times.setdefault(cell, eat_start() + max(len(path), 1) * C.EAT_STEP)
    return times
