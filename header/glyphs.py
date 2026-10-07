"""Real terminal glyphs. Letters do not snap to the cube grid."""

from header import config as C


def glyphs():
    out = []
    for i, ch in enumerate(C.LINE1):
        out.append(
            {
                "ch": ch,
                "x": C.X1 + i * C.ADV1,
                "y": C.Y1,
                "size": C.SIZE1,
                "fill": C.TEXT,
                "appear": C.START_S + i * C.CHAR_IN,
                "index": i,
            }
        )
    t2 = C.START_S + len(C.LINE1) * C.CHAR_IN + C.LINE_PAUSE
    n2 = len(C.LINE2)
    for i, ch in enumerate(C.LINE2):
        out.append(
            {
                "ch": ch,
                "x": C.X2 - (n2 - i) * C.ADV2,
                "y": C.Y2,
                "size": C.SIZE2,
                "fill": C.MUTED,
                "appear": t2 + i * C.CHAR_IN,
                "index": len(C.LINE1) + i,
            }
        )
    return out


def letter_centers():
    return [(g["x"] + C.ADV1 / 2, g["y"]) for g in glyphs()]
