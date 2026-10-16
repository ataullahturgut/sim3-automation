"""TERAZİ v5.1 nedensellik testleri (G4 — mutlak). python3 -m unittest test_terazi_v5 -v"""
import copy, os, random, sys, unittest
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for p in ("claude_terazi_v4", "claude_terazi_v2", "claude_deneyim_v1"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import deneyim_states as S
import hedef_v5 as H
import run_terazi_v5 as RV
FORGET = os.environ.get("V54") == "1"   # V54=1 → aynı testler ek-4 (unutan referans) ile


class T5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = S.load_rows()
        cls.d2i = {str(r["date"]): i for i, r in enumerate(cls.rows)}
        cls.A = RV.marathon("month", 2, relabel=True, forget=FORGET)

    def test_no_2026(self):
        self.assertLessEqual(max(r["date"] for r in self.rows), date(2025, 12, 31))

    def test_target_reads_only_past(self):
        for d in ("2022-12-30", "2023-06-30", "2024-09-30", "2025-07-31"):
            i = self.d2i[d]
            a, _, _ = H.target_labels(self.rows, i, 2)
            b, _, _ = H.target_labels(self.rows[: i + 1], i, 2)
            self.assertEqual(a, b, d)

    def test_target_ignores_future_prices(self):
        cut = self.d2i["2024-03-28"]; rows2 = copy.deepcopy(self.rows); rng = random.Random(3)
        for r in rows2[cut + 1:]:
            f = rng.uniform(0.5, 1.6); r["p06"] *= f; r["bid"] *= f; r["ask"] *= f
        self.assertEqual(H.target_labels(self.rows, cut, 2)[0], H.target_labels(rows2, cut, 2)[0])

    def test_future_prices_do_not_change_decisions(self):
        cut = 1200; rows2 = copy.deepcopy(self.rows); rnd = random.Random(7)
        for r in rows2[cut + 1:]:
            f = rnd.uniform(0.6, 1.4); r["p06"] *= f; r["bid"] *= f; r["ask"] *= f
            for s in ("nq", "zn", "cl", "si"):
                if r[s]: r[s] *= rnd.uniform(0.5, 1.5)
        orig = S.load_rows
        try:
            S.load_rows = lambda dev_only=True: rows2
            B = RV.marathon("month", 2, relabel=True, forget=FORGET)
        finally:
            S.load_rows = orig
        da = [(i, round(v, 9), p) for (i, v, p) in self.A["nav_hist"] if i <= cut]
        db = [(i, round(v, 9), p) for (i, v, p) in B["nav_hist"] if i <= cut]
        self.assertEqual(da, db)

    def test_truncation_parity(self):
        cut = date(2024, 8, 30); rows2 = [r for r in self.rows if r["date"] <= cut]
        orig = S.load_rows
        try:
            S.load_rows = lambda dev_only=True: rows2
            B = RV.marathon("month", 2, relabel=True, forget=FORGET)
        finally:
            S.load_rows = orig
        da = [(i, round(v, 9), p) for (i, v, p) in self.A["nav_hist"] if self.rows[i]["date"] <= cut]
        db = [(i, round(v, 9), p) for (i, v, p) in B["nav_hist"]]
        self.assertEqual(da, db)

    def test_deterministic(self):
        B = RV.marathon("month", 2, relabel=True, forget=FORGET)
        self.assertEqual(self.A["nav_hist"], B["nav_hist"]); self.assertEqual(self.A["trades"], B["trades"])

    def test_fee_in_nav(self):
        self.assertGreater(self.A["gross_hist"][-1][1], self.A["nav_hist"][-1][1])

    def test_base_rate_from_learned_labels_only(self):
        """p0 yalnız öğrenilmiş etiketlerden; ek-4'te kronolojik unutan ortalama."""
        import numpy as np
        L = self.A["learned"]; ys = [L[q] for q in sorted(L)]
        want = RV.forget_mean(ys) if FORGET else float(np.mean(ys))
        self.assertAlmostEqual(self.A["net"].p0, want, places=12)


if __name__ == "__main__":
    unittest.main()
