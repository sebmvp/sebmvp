"""Tests for the profile banner generator."""

import random
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from header import config as C
from header.contributions import cell_at, load, simulate
from header.eater import eat_path, eat_times, step_times
from header.glyphs import glyphs, letter_centers
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

    def test_spread_stays_in_letter_column_band(self):
        fills = simulate(random.Random(5))
        cols = [cell_at(x, y)[0] for x, y in letter_centers()]
        first = cols[0]
        last = cols[-1]
        self.assertGreater(last - first, 10)
        for c, r in fills:
            nearest = min(abs(c - lc) for lc in cols)
            self.assertLessEqual(nearest, 1)

    def test_github_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            load("github", random.Random(0))

    def test_unknown_source(self):
        with self.assertRaises(ValueError):
            load("nope", random.Random(0))


class EaterTests(unittest.TestCase):
    def test_enters_from_the_right(self):
        cells = [(10, 2), (40, 1), (C.COLS - 1, 0)]
        path = eat_path(cells, random.Random(0))
        self.assertEqual(path[0][0], C.COLS)
        self.assertIn(path[0][1], range(C.LAST_WEEK_DAYS))

    def test_steps_are_orthogonal(self):
        fills = simulate(random.Random(3))
        path = eat_path(list(fills), random.Random(3))
        for a, b in zip(path, path[1:]):
            self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)

    def test_visits_every_filled_cell(self):
        cells = [(0, 0), (3, 1), (1, 2), (8, 4)]
        path = eat_path(cells, random.Random(1))
        self.assertTrue(set(cells).issubset(set(path)))

    def test_path_changes_with_seed(self):
        cells = [(i, i % 7) for i in range(0, 40, 3)]
        a = eat_path(cells, random.Random(1))
        b = eat_path(cells, random.Random(2))
        self.assertNotEqual(a, b)
        self.assertTrue(set(cells).issubset(set(a)))
        self.assertTrue(set(cells).issubset(set(b)))

    def test_eat_times_cover_fills(self):
        fills = [(0, 0), (2, 0), (4, 1)]
        rng = random.Random(0)
        path = eat_path(fills, rng)
        times = step_times(path, random.Random(0))
        eaten = eat_times(path, fills, times)
        self.assertEqual(len(eaten), 3)


class RenderTests(unittest.TestCase):
    def test_svg_has_snk_snake_and_partial_last_week(self):
        svg = build(rng=random.Random(7))
        self.assertIn("@keyframes L0", svg)
        self.assertIn("@keyframes s0", svg)
        self.assertIn('id="snake"', svg)
        self.assertTrue(svg.startswith("<svg"))
        self.assertGreaterEqual(svg.count("<rect"), 50)


if __name__ == "__main__":
    unittest.main()
