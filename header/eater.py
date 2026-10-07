"""Snake that eats filled cubes after the graph sits.

Geometry matches platane/snk: four tapered rounded squares, orthogonal
slides. Enters from the leftover last-week column, clears a column, then
wraps along the top or bottom halo to the next one — an intentional
snk-style run around the graph, not a random poke off the grid.
Speeds up as it fades. Still visits every filled cell.
"""

from header import config as C
from header.timeline import eat_start


def cell_xy(c, r):
    return C.OX + c * C.PITCH, C.OY + r * C.PITCH


def _walkable(c, r):
    """Grid plus a 1-cell halo (snk walks the rim) and the leftover hole."""
    return -1 <= c <= C.COLS and -1 <= r <= C.ROWS


def route(a, b, rng=None):
    """Orthogonal a → b. Longer axis first. rng unused; kept for callers."""
    del rng

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
    path = first()
    if path and all(_walkable(*p) or p == b for p in path):
        return path
    return second()


def _dedupe(cells):
    out = []
    for cell in cells:
        if not out or out[-1] != cell:
            out.append(cell)
    return out


def _wrap(a, b, rail):
    """Climb to the rim, long slide, dive in. Looks like snk hugging the graph."""
    return _dedupe(
        route(a, (a[0], rail))
        + route((a[0], rail), (b[0], rail))
        + route((b[0], rail), b)
    )


def eat_path(filled, rng):
    """Column sweep from the leftover week, wrapping the rim between columns."""
    remaining = {p for p in filled if C.cell_exists(*p)}
    path = [(C.COLS - 1, r) for r in range(C.LAST_WEEK_DAYS, -1, -1)]
    cur = path[-1]
    remaining.discard(cur)
    vdir = -1
    while remaining:
        col = cur[0]
        in_col = [p for p in remaining if p[0] == col]
        if in_col:
            ahead = [p for p in in_col if (p[1] - cur[1]) * vdir > 0]
            if not ahead:
                vdir *= -1
                ahead = [p for p in in_col if (p[1] - cur[1]) * vdir > 0] or in_col
            nxt = min(ahead, key=lambda p: abs(p[1] - cur[1]))
            extra = route(cur, nxt)
        else:
            cols = sorted({p[0] for p in remaining})
            left = sorted((c for c in cols if c < col), reverse=True)
            right = sorted(c for c in cols if c > col)
            if left and (not right or rng.random() < 0.85):
                nxt_col = left[1] if len(left) > 1 and rng.random() < 0.16 else left[0]
            else:
                nxt_col = right[0]
            in_next = [p for p in remaining if p[0] == nxt_col]
            if abs(nxt_col - col) > 1:
                use_top = cur[1] <= (C.ROWS - 1) / 2.0
                if rng.random() < 0.22:
                    use_top = not use_top
                rail = -1 if use_top else C.ROWS
                edge = 0 if use_top else C.ROWS - 1
                nxt = min(in_next, key=lambda p: abs(p[1] - edge))
                extra = _wrap(cur, nxt, rail)
                vdir = 1 if use_top else -1
            else:
                nxt = min(in_next, key=lambda p: abs(p[1] - cur[1]))
                extra = route(cur, nxt)
        path.extend(extra)
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
