#!/usr/bin/env python3
"""Build assets/profile-header.svg from the header package.

  python3 scripts/build_header.py
  python3 scripts/build_header.py --seed 2026
  python3 scripts/build_header.py --source github   # not implemented yet
"""

import argparse
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from header.render import build, plan, write  # noqa: E402
from header.timeline import eat_start, phases  # noqa: E402


def parse_args(argv):
    p = argparse.ArgumentParser(description="Generate the profile README banner SVG")
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Reproduce a cube spread. Default: a new random spread each build.",
    )
    p.add_argument(
        "--source",
        choices=("simulated", "github"),
        default="simulated",
        help="simulated (letter residue) or github (real year — not yet)",
    )
    p.add_argument(
        "--preview",
        choices=("hold", "cubes"),
        default=None,
        help="Static frame without animation",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    preview = args.preview or os.environ.get("PREVIEW") or None
    seed = args.seed
    if seed is None:
        seed = random.randrange(1, 2 ** 31)
    rng = random.Random(seed)
    try:
        svg = build(preview=preview, source=args.source, rng=rng)
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        return 2
    out = write(svg)
    _fills, path, times, _eaten, total = plan(args.source, random.Random(seed))
    print("wrote %s (%d bytes) seed=%s source=%s" % (out, out.stat().st_size, seed, args.source))
    print("loop %.1fs until hi there restarts:" % total)
    eat0 = times[0] if times else eat_start()
    eat1 = times[-1] if times else eat0
    for name, a, b in phases(len(path)):
        if name == "snake eats":
            a, b = eat0, eat1
        elif name == "reset":
            a, b = eat1, total
        print("  %4.1f–%5.1fs  %s  (%.1fs)" % (a, b, name, b - a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
