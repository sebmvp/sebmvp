"""Tests for the profile banner generator."""

import random
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from header.contributions import load, simulate
from header.eater import eat_path, eat_times
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

    def test_github_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            load("github", random.Random(0))

    def test_unknown_source(self):
        with self.assertRaises(ValueError):
            load("nope", random.Random(0))


class EaterTests(unittest.TestCase):
    def test_visits_every_cell_once(self):
        cells = [(0, 0), (3, 1), (1, 2), (8, 4)]
        path = eat_path(cells)
        self.assertEqual(len(path), len(cells))
        self.assertEqual(set(path), set(cells))
        self.assertEqual(path[0], (0, 0))

    def test_eat_times_increase(self):
        path = eat_path([(0, 0), (2, 0), (4, 1)])
        times = eat_times(path)
        seq = [times[c] for c in path]
        self.assertEqual(seq, sorted(seq))


class RenderTests(unittest.TestCase):
    def test_svg_has_css_loop_and_snake(self):
        svg = build(rng=random.Random(7))
        self.assertIn("@keyframes L0", svg)
        self.assertIn("@keyframes H", svg)
        self.assertIn("infinite", svg)
        self.assertIn('id="snake"', svg)
        self.assertTrue(svg.startswith("<svg"))


if __name__ == "__main__":
    unittest.main()
