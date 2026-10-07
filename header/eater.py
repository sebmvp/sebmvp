"""Snake that eats filled cubes after the graph sits.

Geometry matches platane/snk: four tapered rounded squares, orthogonal
slides. Enters from the leftover last-week column. Wanders off the grid
a few times like snk. Less greedy about the next cube. Speeds up as it
fades. Still visits every filled cell.
"""

from header import config as C
from header.timeline import eat_start


def cell_xy(c, r):
    return C.OX + c * C.PITCH, C.OY + r * C.PITCH


def _walkable(c, r):
    """Grid plus a 1-cell halo (snk steps outside) and the leftover hole."""
    return -1 <= c <= C.COLS and -1 <= r <= C.ROWS


def _outside_spots():
    spots = []
    for c in range(0, C.COLS, 6):
        spots.append((c, -1))
        spots.append((c, C.ROWS))
    for r in range(C.ROWS):
        spots.append((-1, r))
        spots.append((C.COLS, min(r, C.LAST_WEEK_DAYS)))
    for r in range(C.LAST_WEEK_DAYS, C.ROWS + 1):
        spots.append((C.COLS - 1, r))
    return spots


def _pick_outside(a, b, rng):
    ranked = sorted(
        _outside_spots(),
        key=lambda s: abs(s[0] - (a[0] + b[0]) / 2.0)
        + abs(s[1] - (a[1] + b[1]) / 2.0),
    )
    return rng.choice(ranked[:8])


def route(a, b, rng=None):
    """Orthogonal a → b. Longer axis first, sometimes the other elbow."""

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

    dc, dr = abs(b[0] - a[0]), abs(b[1] - a[1])
    first, second = (hv, vh) if dc >= dr else (vh, hv)
    if rng is not None and rng.random() < 0.38:
        first, second = second, first
    path = first()
    if path and all(_walkable(*p) or p == b for p in path):
        return path
    return second()


def eat_path(filled, rng):
    """Leftover stub, then a wandering eat with a few off-grid escapes."""
    remaining = {p for p in filled if C.cell_exists(*p)}
    path = [(C.COLS - 1, r) for r in range(C.LAST_WEEK_DAYS, -1, -1)]
    cur = path[-1]
    remaining.discard(cur)
    n0 = len(remaining)
    escape_after = set()
    if n0 >= 6:
        n_esc = rng.randint(2, 4)
        n_esc = min(n_esc, n0 - 1)
        escape_after = set(rng.sample(range(1, n0), n_esc))
    targets_done = 0
    while remaining:
        def dist(p):
            return abs(p[0] - cur[0]) + abs(p[1] - cur[1])

        ranked = sorted(remaining, key=dist)
        k = min(6, len(ranked))
        if rng.random() < 0.4:
            nxt = ranked[0]
        else:
            near = ranked[:k]
            weights = [1.0 / (dist(p) ** 1.1 + 0.6) for p in near]
            nxt = rng.choices(near, weights=weights)[0]
        if targets_done in escape_after:
            via = _pick_outside(cur, nxt, rng)
            extra = route(cur, via, rng) + route(via, nxt, rng)
        else:
            extra = route(cur, nxt, rng)
        path.extend(extra)
        targets_done += 1
        for cell in path:
            remaining.discard(cell)
        cur = path[-1]
    return path


def step_times(path, _rng=None):
    """snk-ish step that speeds up as the snake goes transparent."""
    t = eat_start()
    times = []
    n = max(len(path) - 1, 1)
    for i, _ in enumerate(path):
        times.append(t)
        p = float(i) / n
        fade = 1.0 - p ** 3
        t += C.EAT_STEP * (0.45 + 0.55 * fade)
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
