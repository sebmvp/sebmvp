"""Snake that eats filled cubes after the graph sits.

Greedy nearest-neighbor through filled cells, starting at the leftmost
letter residue. CSS moves a head (and a short tail) along that path.
"""

from header import config as C
from header.timeline import eat_start


def cell_xy(c, r):
    return C.OX + c * C.PITCH, C.OY + r * C.PITCH


def eat_path(filled):
    remaining = set(filled)
    if not remaining:
        return []
    cur = min(remaining, key=lambda p: (p[0], p[1]))
    path = [cur]
    remaining.remove(cur)
    while remaining:
        x, y = path[-1]
        nxt = min(
            remaining,
            key=lambda p: ((p[0] - x) ** 2 + (p[1] - y) ** 2, p[0], p[1]),
        )
        path.append(nxt)
        remaining.remove(nxt)
    return path


def eat_times(path):
    start = eat_start()
    return {cell: start + i * C.EAT_STEP for i, cell in enumerate(path)}
