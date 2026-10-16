"""TERAZİ v4 nedensellik testleri (ön kayıt G4 — mutlak koşul).
Hedef etiketi yuvarlanan idealden gelir; ay sonundan sonraki fiyatlar kararı etkilememeli.
Çalıştırma: python3 -m unittest test_terazi_v4 -v
"""
import copy, os, random, sys, tempfile, unittest
from datetime import date
import numpy as np
import terazi_v4 as T4
import deneyim_states as S
import run_terazi_v4 as RV


class T4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = S.load_rows()
        cls.d2i = {str(r["date"]): i for i, r in enumerate(cls.rows)}

    def test_no_2026(self):
        self.assertLessEqual(max(r["date"] for r in self.rows), date(2025, 12, 31))

    def test_target_labels_read_only_past(self):
        """target_labels(i_end) seri i_end'de kesilse birebir aynı etiketleri vermeli."""
        for d in ("2022-12-30", "2023-06-30", "2024-03-28", "2025-05-30"):
            i = self.d2i[d]
            a, _, _ = T4.target_labels(self.rows, i)
            b, _, _ = T4.target_labels(self.rows[: i + 1], i)
            self.assertEqual(a, b, f"{d}: kesilmiş seri farklı etiket verdi")

    def test_target_labels_ignore_future_prices(self):
        """i_end'den sonraki fiyatları bozmak etiketleri değiştirmemeli."""
        rng = random.Random(3)
        cut = self.d2i["2024-03-28"]
        rows2 = copy.deepcopy(self.rows)
        for r in rows2[cut + 1:]:
            f = rng.uniform(0.5, 1.6)
            r["p06"] *= f; r["bid"] *= f; r["ask"] *= f
        a, _, _ = T4.target_labels(self.rows, cut)
        b, _, _ = T4.target_labels(rows2, cut)
        self.assertEqual(a, b)

    def test_open_leg_days_are_unlabelled(self):
        """Açık kalan son bacağın günleri etiketlenmemeli."""
        for d in ("2023-06-30", "2024-09-30", "2025-07-31"):
            i = self.d2i[d]
            lab, closed, last_known = T4.target_labels(self.rows, i)
            self.assertLessEqual(last_known, i)
            for q in range(last_known + 1, i + 1):
                self.assertNotIn(q, lab, f"{d}: onaylanmamış gün {q} etiketlenmiş")

    def test_label_is_the_first_maturation_value(self):
        """Öğrenilen etiket, o günün İLK olgunlaştığı ay sonundaki değeridir.

        Yuvarlanan ideal ufka duyarlıdır: aynı gün, ufuk uzadıkça farklı etiketlenebilir
        (ölçüldü: 1546 günün 74'ü, %4,8, hepsi 0→1). Ön kayıt §1.1 ilk olgunlaşmayı kesin
        sayar, yani model geriye dönük olarak düzeltilmez. Test bunu bağımsız olarak doğrular.
        """
        from collections import OrderedDict
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        learned = A["learned"]
        months = OrderedDict()
        for i in range(len(self.rows)):
            months.setdefault(str(self.rows[i]["date"])[:7], []).append(i)
        first = {}
        for mo, idxs in months.items():
            lab, _, _ = T4.target_labels(self.rows, idxs[-1])
            for q, y in lab.items():
                if q not in first:
                    first[q] = y
        self.assertEqual(set(first), set(learned))
        for q in first:
            self.assertEqual(learned[q], first[q], f"gün {q}: ilk olgunlaşma değeri korunmamış")

    def test_base_rate_uses_learned_labels_only(self):
        """p0, yalnız öğrenilmiş etiketlerin ortalaması olmalı (gelecek sızmamalı)."""
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        learned = A["learned"]
        self.assertAlmostEqual(A["net"].p0,
                               float(np.mean([learned[q] for q in sorted(learned)])), places=12)

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
        self.assertFalse(hasattr(T4, "BUY_TH"))
        self.assertAlmostEqual(T4.FEE, S.FEE)
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        if A["trades"]:
            self.assertGreater(A["gross_hist"][-1][1], A["nav_hist"][-1][1])

    def test_threshold_reproduces_user_selection(self):
        """net ≥ %2,4 eşiği kullanıcının 24 seçimini birebir vermeli (hedefin tanımı)."""
        from deneyim_v1 import oracle, legs_from_positions
        i0, i1 = self.d2i["2023-01-03"], self.d2i["2025-12-31"]
        pos, _ = oracle(self.rows, i0, i1)
        legs = legs_from_positions(self.rows, i0, pos)
        keep = {(L["entry_date"], L["exit_date"]) for L in legs if (L["net_pct"] or 0) >= T4.NET_MIN}
        self.assertEqual(len(keep), 24)
        self.assertIn(("2023-01-03", "2023-01-26"), keep)
        self.assertIn(("2025-08-20", "2025-10-17"), keep)
        self.assertNotIn(("2023-01-31", "2023-02-02"), keep)


if __name__ == "__main__":
    unittest.main()
