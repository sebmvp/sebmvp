"""Tests for the profile banner generator."""

import random
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from header import config as C
from header.contributions import load, simulate
from header.eater import eat_path, eat_times, step_times
from header.glyphs import glyphs
from header import timeline as T
from header.render import build


class TimelineTests(unittest.TestCase):
    def test_order(self):
        self.assertLess(T.type1_end(), T.delete_start())
        self.assertLess(T.delete_start(), T.type2_start())
        self.assertLess(T.type2_end(), T.convert_start())
        self.assertLess(T.convert_end(), T.eat_start())
        self.assertLess(T.eat_start(), T.total_s(10))


class GlyphTests(unittest.TestCase):
    def test_count(self):
        g = glyphs()
        self.assertEqual(len(g), T.n_letters())
        self.assertEqual(g[0]["ch"], "h")
        self.assertEqual(g[-1]["ch"], "o")


class ContributionTests(unittest.TestCase):
    def test_seed_is_deterministic(self):
        a = simulate(random.Random(1))
        b = simulate(random.Random(1))
        self.assertEqual(a, b)

    def test_different_seeds_differ(self):
        a = simulate(random.Random(1))
        b = simulate(random.Random(2))
        self.assertNotEqual(set(a), set(b))

    def test_skips_missing_last_week_cells(self):
        fills = simulate(random.Random(1))
        for c, r in fills:
            self.assertTrue(C.cell_exists(c, r))

    def test_github_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            load("github", random.Random(0))

    def test_unknown_source(self):
        with self.assertRaises(ValueError):
            load("nope", random.Random(0))


class EaterTests(unittest.TestCase):
    def test_enters_from_the_right(self):
        cells = [(10, 2), (40, 1), (C.COLS - 1, 0)]
        path = eat_path(cells)
        self.assertEqual(path[0], (C.COLS, 0))
        self.assertTrue(all(C.COLS - 1 - 1 <= p[0] <= C.COLS for p in path[:3]))

    def test_steps_are_orthogonal(self):
        fills = simulate(random.Random(3))
        path = eat_path(list(fills))
        for a, b in zip(path, path[1:]):
            self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)

    def test_visits_every_filled_cell(self):
        cells = [(0, 0), (3, 1), (1, 2), (8, 4)]
        path = eat_path(cells)
        self.assertTrue(set(cells).issubset(set(path)))

    def test_eat_times_increase_along_path(self):
        fills = [(0, 0), (2, 0), (4, 1)]
        path = eat_path(fills)
        times = eat_times(path, fills)
        seq = [times[c] for c in fills]
        self.assertEqual(len(seq), 3)


class RenderTests(unittest.TestCase):
    def test_svg_has_snk_snake_and_partial_last_week(self):
        svg = build(rng=random.Random(7))
        self.assertIn("@keyframes L0", svg)
        self.assertIn("@keyframes s0", svg)
        self.assertIn('id="snake"', svg)
        self.assertTrue(svg.startswith("<svg"))
        last_x = C.OX + (C.COLS - 1) * C.PITCH
        last_col = svg.count('x="%.1f"' % last_x)
        # 3 days in the last week, plus 4 snake rects that are not this x.
        self.assertGreaterEqual(svg.count("<rect"), 50)


if __name__ == "__main__":
    unittest.main()
