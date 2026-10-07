"""One loop of the banner, in seconds."""

from header import config as C


def n_letters():
    return len(C.LINE1) + len(C.LINE2)


def type_span():
    return len(C.LINE1) * C.CHAR_IN + C.LINE_PAUSE + len(C.LINE2) * C.CHAR_IN


def type1_end():
    return C.START_S + type_span()


def delete_start():
    return type1_end() + C.READ_1


def type2_start():
    return delete_start() + n_letters() * C.CHAR_DEL + C.GAP


def type2_end():
    return type2_start() + type_span()


def convert_start():
    return type2_end() + C.HOLD_S


def convert_end():
    return convert_start() + n_letters() * C.CHAR_OUT


def eat_start():
    return convert_end() + C.CUBE_HOLD


def eat_end(n_filled):
    return eat_start() + max(n_filled, 1) * C.EAT_STEP


def total_s(n_filled):
    return eat_end(n_filled) + 0.6


def letter_offset(index):
    if index < len(C.LINE1):
        return index * C.CHAR_IN
    return len(C.LINE1) * C.CHAR_IN + C.LINE_PAUSE + (index - len(C.LINE1)) * C.CHAR_IN


def pct(seconds, total):
    return max(0.0, min(100.0, 100.0 * seconds / total))


def bump(values):
    """Keep keyframe percents strictly increasing and inside 0..99.9."""
    out = []
    last = -0.05
    for x in values:
        x = max(x, last + 0.05)
        x = min(x, 99.9)
        out.append(x)
        last = x
    return out
