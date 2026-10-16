"""DENEYİM v1 doğruluk testleri: as-of durum, ideal yol (kaba kuvvetle), aylık nedensellik, 2026 yasağı.
Çalıştırma: python3 -m unittest test_deneyim_v1 -v
"""
import copy, itertools, math, random, unittest
from datetime import date
import numpy as np
import deneyim_states as S
import deneyim_v1 as D


def brute(rows, i0, i1):
    best = -1e18
    n = i1 - i0 + 1
    for path in itertools.product((0, 1), repeat=n):
        cash, units, prev = 1.0, 0.0, 0
        for j, p in enumerate(path):
            r = rows[i0 + j]
            if p == 1 and prev == 0: units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0
            if p == 0 and prev == 1: cash = units * r["bid"] * (1 - S.FEE); units = 0.0
            prev = p
        v = cash + units * rows[i1]["bid"] * (1 - S.FEE)
        best = max(best, math.log(v))
    return best


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = S.load_rows()
        cls.raw, _ = S.build_states(cls.rows)
        cls.Z, _ = S.standardize(cls.raw)

    def test_no_2026_in_dev(self):
        self.assertLessEqual(max(r["date"] for r in self.rows), date(2025, 12, 31))

    def test_states_do_not_use_future_prices(self):
        cut = 900
        rows2 = copy.deepcopy(self.rows); rnd = random.Random(3)
        for r in rows2[cut + 1:]:
            f = rnd.uniform(0.6, 1.4); r["p06"] *= f; r["bid"] *= f; r["ask"] *= f
            for s in ("nq", "zn", "cl", "si"):
                if r[s]: r[s] *= rnd.uniform(0.5, 1.5)
        raw2, _ = S.build_states(rows2); Z2, _ = S.standardize(raw2)
        np.testing.assert_array_equal(self.Z[:cut + 1], Z2[:cut + 1])

    def test_truncation_parity_of_states(self):
        for n in (700, 1100):
            raw2, _ = S.build_states(self.rows[:n]); Z2, _ = S.standardize(raw2)
            np.testing.assert_array_equal(self.Z[:n], Z2)

    def test_oracle_matches_brute_force(self):
        rnd = random.Random(5)
        for _ in range(25):
            i0 = rnd.randint(300, 1400); i1 = i0 + rnd.randint(3, 11)
            pos, val = D.oracle(self.rows, i0, i1)
            self.assertAlmostEqual(val - math.log(1.0), brute(self.rows, i0, i1), places=9)

    def test_monthly_decisions_ignore_same_month_labels(self):
        # Ayın kararları yalnız önceki ay sonu modeliyle: veri o ay sonundan sonra kesilse de aynı kalmalı.
        import tempfile
        full = D.marathon(tempfile.mkdtemp())
        rows_cut = [r for r in self.rows if r["date"] <= date(2024, 6, 28)]
        orig = S.load_rows
        try:
            S.load_rows = lambda dev_only=True: rows_cut
            part = D.marathon(tempfile.mkdtemp())
        finally:
            S.load_rows = orig
        a = {i: p for i, (p, _, _) in full["rt"].items() if i in part["rt"]}
        b = {i: p for i, (p, _, _) in part["rt"].items()}
        self.assertEqual(a, b)
        self.assertEqual([t for t in full["trades"] if t["date"] <= "2024-06-28"], part["trades"])


if __name__ == "__main__":
    unittest.main()
