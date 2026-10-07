"""Snake that eats filled cubes after the graph sits.

Matches platane/snk: four tapered rounded squares, orthogonal 16px steps,
CSS linear slides. Enters from the incomplete last week on the right.
Path is re-rolled each build; still visits every filled cell.
"""

from header import config as C
from header.timeline import eat_start


def cell_xy(c, r):
    return C.OX + c * C.PITCH, C.OY + r * C.PITCH


def _walkable(c, r):
    return C.cell_exists(c, r) or c == C.COLS or c == -1


def route(a, b, rng):
    """Orthogonal cells from a (exclusive) to b (inclusive). H-then-V or V-then-H."""
    def hv():
        path = []
        c, r = a
        while c != b[0]:
            c += 1 if b[0] > c else -1
            path.append((c, r))
        while r != b[1]:
            r += 1 if b[1] > r else -1
            path.append((c, r))
        return path

    def vh():
        path = []
        c, r = a
        while r != b[1]:
            r += 1 if b[1] > r else -1
            path.append((c, r))
        while c != b[0]:
            c += 1 if b[0] > c else -1
            path.append((c, r))
        return path

    first, second = (hv, vh) if rng.random() < 0.5 else (vh, hv)
    path = first()
    if path and all(_walkable(*p) or p == b for p in path):
        return path
    return second()


def eat_path(filled, rng):
    """Come in from a random last-week row, then nearest-of-few through fills."""
    remaining = {p for p in filled if C.cell_exists(*p)}
    entry_row = rng.randrange(C.LAST_WEEK_DAYS)
    start = (C.COLS, entry_row)
    entry = (C.COLS - 1, entry_row)
    path = [start]
    path.extend(route(start, entry, rng))
    cur = path[-1]
    remaining.discard(cur)
    while remaining:
        ranked = sorted(
            remaining,
            key=lambda p: abs(p[0] - cur[0]) + abs(p[1] - cur[1]),
        )
        min_d = abs(ranked[0][0] - cur[0]) + abs(ranked[0][1] - cur[1])
        pool = [
            p
            for p in ranked
            if abs(p[0] - cur[0]) + abs(p[1] - cur[1]) == min_d
        ]
        if len(ranked) > 1 and rng.random() < 0.28:
            nxt = rng.choice(ranked[:2])
        else:
            nxt = rng.choice(pool)
        path.extend(route(cur, nxt, rng))
        for cell in path:
            remaining.discard(cell)
        cur = path[-1]
    return path


def step_times(path, rng):
    t = eat_start()
    times = []
    for _ in path:
        times.append(t)
        t += C.EAT_STEP * rng.uniform(0.72, 1.12)
    return times


def eat_times(path, filled, times):
    """First time the head visits each filled cell."""
    filled = set(filled)
    out = {}
    for i, cell in enumerate(path):
        if cell in filled and cell not in out:
            out[cell] = times[i]
    end = times[-1] if times else eat_start()
    for cell in filled:
        out.setdefault(cell, end)
    return out
