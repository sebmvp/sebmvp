"""CSS keyframes. Same technique as platane/snk — Safari/GitHub actually play it."""

from header import config as C
from header.eater import cell_xy
from header.timeline import (
    bump,
    convert_start,
    delete_start,
    letter_offset,
    n_letters,
    pct,
    type2_start,
)


def letter_css(g, total):
    i = g["index"]
    n = n_letters()
    a1 = g["appear"]
    dlt = delete_start() + (n - 1 - i) * C.CHAR_DEL
    a2 = type2_start() + letter_offset(i)
    conv = convert_start() + i * C.CHAR_OUT
    a1p, a1on, dp, doff, a2p, a2on, cp, coff = bump(
        [
            pct(a1, total),
            pct(a1 + 0.02, total),
            pct(dlt, total),
            pct(dlt + 0.02, total),
            pct(a2, total),
            pct(a2 + 0.02, total),
            pct(conv, total),
            pct(conv + 0.02, total),
        ]
    )
    return (
        "    @keyframes L%d {\n"
        "      0%%, %.2f%% { opacity: 0; }\n"
        "      %.2f%%, %.2f%% { opacity: %.2f; }\n"
        "      %.2f%%, %.2f%% { opacity: 0; }\n"
        "      %.2f%%, %.2f%% { opacity: %.2f; }\n"
        "      %.2f%%, 100%% { opacity: 0; }\n"
        "    }\n"
        "    .L%d { animation: L%d %.2fs linear infinite; }\n"
        % (
            i,
            a1p,
            a1on,
            dp,
            C.REST,
            doff,
            a2p,
            a2on,
            cp,
            C.REST,
            coff,
            i,
            i,
            total,
        )
    )


def cube_css(idx, fill_at, eat_at, color, total):
    t, on, eaten, gone = bump(
        [
            pct(fill_at, total),
            pct(fill_at + 0.18, total),
            pct(eat_at, total),
            pct(eat_at + 0.08, total),
        ]
    )
    return (
        "    @keyframes C%d {\n"
        "      0%%, %.2f%% { fill: %s; fill-opacity: %.2f; }\n"
        "      %.2f%%, %.2f%% { fill: %s; fill-opacity: 1; }\n"
        "      %.2f%%, 100%% { fill: %s; fill-opacity: %.2f; }\n"
        "    }\n"
        "    .C%d { animation: C%d %.2fs linear infinite; }\n"
        % (
            idx,
            t,
            C.CUBE,
            C.CUBE_OPACITY,
            on,
            eaten,
            color,
            gone,
            C.CUBE,
            C.CUBE_OPACITY,
            idx,
            idx,
            total,
        )
    )


def _corners(path):
    """Keep endpoints and turns. CSS linear-interpolates the long runs, like snk."""
    if len(path) <= 2:
        return list(range(len(path)))
    keep = [0]
    for i in range(1, len(path) - 1):
        a, u, b = path[i - 1], path[i], path[i + 1]
        if abs((a[0] + b[0]) / 2.0 - u[0]) < 0.01 and abs(
            (a[1] + b[1]) / 2.0 - u[1]
        ) < 0.01:
            continue
        keep.append(i)
    keep.append(len(path) - 1)
    return keep


def snake_css(path, times, total, lag=0, name="s0"):
    """One snk-style body part. `lag` cells behind the head. Orthogonal slides."""
    if len(path) <= lag:
        return ""
    body = []
    body_times = []
    for i in range(lag, len(path)):
        body.append(path[i - lag])
        body_times.append(times[i])
    if not body:
        return ""
    idxs = _corners(body)
    n = max(len(body) - 1, 1)
    percents = bump(
        [pct(body_times[0], total)]
        + [pct(body_times[i], total) for i in idxs]
        + [pct(body_times[-1] + 0.2, total)]
    )
    hidden_p = percents[0]
    gone_p = percents[-1]
    x0, y0 = cell_xy(*body[0])
    frames = [
        "      0%%, %.2f%% { opacity: 0; transform: translate(%.1fpx, %.1fpx); }"
        % (hidden_p, x0, y0)
    ]
    for k, i in enumerate(idxs):
        x, y = cell_xy(*body[i])
        fade = 1.0 - (float(i) / n) ** 3
        if i == n:
            fade = 0.0
        kp = percents[1 + k]
        frames.append(
            "      %.2f%% { opacity: %.3f; transform: translate(%.1fpx, %.1fpx); }"
            % (kp, fade, x, y)
        )
    lx, ly = cell_xy(*body[-1])
    frames.append(
        "      %.2f%%, 100%% { opacity: 0; transform: translate(%.1fpx, %.1fpx); }"
        % (gone_p, lx, ly)
    )
    return (
        "    @keyframes %s {\n%s\n    }\n"
        "    .%s { animation: %s %.2fs linear infinite; }\n"
        % (name, "\n".join(frames), name, name, total)
    )
