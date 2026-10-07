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
            pct(fill_at + 0.08, total),
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


def snake_css(path, times, total, lag=0, name="s0"):
    """One snk-style body part. `lag` cells behind the head. Orthogonal slides."""
    if len(path) <= lag:
        return ""
    steps = []
    for i in range(lag, len(path)):
        x, y = cell_xy(*path[i - lag])
        steps.append((pct(times[i], total), x, y))
    if not steps:
        return ""
    percents = bump(
        [pct(times[lag], total)]
        + [s[0] for s in steps]
        + [pct(times[-1] + 0.2, total)]
    )
    hidden_p = percents[0]
    gone_p = percents[-1]
    x0, y0 = steps[0][1], steps[0][2]
    n = max(len(steps) - 1, 1)
    frames = [
        "      0%%, %.2f%% { opacity: 0; transform: translate(%.1fpx, %.1fpx); }"
        % (hidden_p, x0, y0)
    ]
    for j, ((_p, x, y), kp) in enumerate(zip(steps, percents[1:-1])):
        # Ease-in fade: stays readable, then drops fast, 0 on the last box.
        fade = 1.0 - (float(j) / n) ** 3
        if j == n:
            fade = 0.0
        frames.append(
            "      %.2f%% { opacity: %.3f; transform: translate(%.1fpx, %.1fpx); }"
            % (kp, fade, x, y)
        )
    lx, ly = steps[-1][1], steps[-1][2]
    frames.append(
        "      %.2f%%, 100%% { opacity: 0; transform: translate(%.1fpx, %.1fpx); }"
        % (gone_p, lx, ly)
    )
    return (
        "    @keyframes %s {\n%s\n    }\n"
        "    .%s { animation: %s %.2fs linear infinite; }\n"
        % (name, "\n".join(frames), name, name, total)
    )
