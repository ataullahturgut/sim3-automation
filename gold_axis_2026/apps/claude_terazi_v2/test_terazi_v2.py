"""TERAZİ v2 nedensellik testleri: evre etiketi onay anında belirlenir, gelecek fiyat kararı etkilemez.
Çalıştırma: python3 -m unittest test_terazi_v2 -v
"""
import copy, os, random, sys, tempfile, unittest
from datetime import date
import numpy as np
import terazi_v2 as T
import deneyim_states as S
import run_terazi_v2 as RV


class T2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = S.load_rows()
        cls.P = [r["p06"] for r in cls.rows]
        cls.lab, cls.conf = T.phase_labels(cls.P)

    def test_no_2026(self):
        self.assertLessEqual(max(r["date"] for r in self.rows), date(2025, 12, 31))

    def test_label_determined_at_confirmation(self):
        """lab[i], conf[i] gününe kadarki fiyatlarla belirlenir: seri conf[i]'de kesilse etiket aynı kalır."""
        rng = random.Random(4)
        idx = [i for i in range(len(self.lab)) if self.lab[i] is not None]
        for i in rng.sample(idx, 40):
            c = self.conf[i]
            lab2, _ = T.phase_labels(self.P[:c + 1])
            self.assertEqual(self.lab[i], lab2[i], f"gün {i}, onay {c}")

    def test_label_not_known_before_confirmation(self):
        """Onaydan önce kesilirse o günün etiketi ya yok ya da henüz onaylanmamış olur."""
        rng = random.Random(9)
        idx = [i for i in range(len(self.lab)) if self.lab[i] is not None and self.conf[i] > i + 2]
        for i in rng.sample(idx, 25):
            lab2, conf2 = T.phase_labels(self.P[:self.conf[i]])
            if lab2[i] is not None:
                self.assertGreater(conf2[i], i, "etiket onaydan önce kesinleşmiş görünüyor")

    def test_future_prices_do_not_change_decisions(self):
        cut = 1200
        rows2 = copy.deepcopy(self.rows); rnd = random.Random(7)
        for r in rows2[cut + 1:]:
            f = rnd.uniform(0.6, 1.4); r["p06"] *= f; r["bid"] *= f; r["ask"] *= f
            for s in ("nq", "zn", "cl", "si"):
                if r[s]: r[s] *= rnd.uniform(0.5, 1.5)
        orig = S.load_rows
        try:
            A = RV.marathon(tempfile.mkdtemp(), write=False)
            S.load_rows = lambda dev_only=True: rows2
            B = RV.marathon(tempfile.mkdtemp(), write=False)
        finally:
            S.load_rows = orig
        da = [(i, round(v, 9), p) for (i, v, p) in A["nav_hist"] if i <= cut]
        db = [(i, round(v, 9), p) for (i, v, p) in B["nav_hist"] if i <= cut]
        self.assertEqual(da, db)
        self.assertEqual([t for t in A["trades"] if t["date"] <= str(self.rows[cut]["date"])],
                         [t for t in B["trades"] if t["date"] <= str(self.rows[cut]["date"])])

    def test_truncation_parity(self):
        cut = date(2024, 8, 30)
        rows2 = [r for r in self.rows if r["date"] <= cut]
        orig = S.load_rows
        try:
            A = RV.marathon(tempfile.mkdtemp(), write=False)
            S.load_rows = lambda dev_only=True: rows2
            B = RV.marathon(tempfile.mkdtemp(), write=False)
        finally:
            S.load_rows = orig
        da = [(i, round(v, 9), p) for (i, v, p) in A["nav_hist"] if self.rows[i]["date"] <= cut]
        db = [(i, round(v, 9), p) for (i, v, p) in B["nav_hist"]]
        self.assertEqual(da, db)

    def test_deterministic(self):
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        B = RV.marathon(tempfile.mkdtemp(), write=False)
        self.assertEqual(A["nav_hist"], B["nav_hist"])
        self.assertEqual(A["trades"], B["trades"])

    def test_fee_not_in_decision_but_in_nav(self):
        self.assertFalse(hasattr(T, "BUY_TH"))
        self.assertAlmostEqual(T.FEE, S.FEE)
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        if A["trades"]:
            self.assertGreater(A["gross_hist"][-1][1], A["nav_hist"][-1][1])


if __name__ == "__main__":
    unittest.main()
