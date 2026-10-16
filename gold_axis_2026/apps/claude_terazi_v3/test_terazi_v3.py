"""TERAZİ v3 nedensellik testleri (ön kayıt G4 — mutlak koşul).
Kırılma etiketi onay anında belirlenir, gelecek fiyat kararı etkilemez, taban oran 2026'yı görmez.
Çalıştırma: python3 -m unittest test_terazi_v3 -v
"""
import copy, os, random, sys, tempfile, unittest
from datetime import date
import numpy as np
import terazi_v3 as T3
import terazi_v2 as T2
import deneyim_states as S
import run_terazi_v3 as RV


class T3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = S.load_rows()
        cls.P = [r["p06"] for r in cls.rows]
        cls.brk, cls.conf, cls.tops = T3.break_labels(cls.P)

    def test_no_2026(self):
        self.assertLessEqual(max(r["date"] for r in self.rows), date(2025, 12, 31))

    def test_break_label_determined_at_confirmation(self):
        """brk[i], conf[i] gününe kadarki fiyatlarla belirlenir: seri conf[i]'de kesilse etiket aynı."""
        rng = random.Random(11)
        idx = [i for i in range(len(self.brk)) if self.brk[i] is not None]
        for i in rng.sample(idx, 60):
            c = self.conf[i]
            brk2, _, _ = T3.break_labels(self.P[:c + 1])
            self.assertEqual(self.brk[i], brk2[i], f"gün {i} ({self.rows[i]['date']}), onay {c}")

    def test_break_window_never_extends_past_confirmation(self):
        """Kırılma penceresi onay gününde kesilir; aksi halde etiket onaydan sonra değişebilirdi."""
        for top, c in self.tops:
            for q in range(len(self.brk)):
                if self.brk[q] == 1 and top < q <= top + T3.M_BREAK:
                    self.assertLessEqual(q, c, f"kırılma günü {q} onay {c}'yi aşıyor")

    def test_break_only_inside_falling_legs(self):
        """brk=1 olan her gün, zigzag evre etiketinde düşme bacağında olmalı."""
        lab, _ = T2.phase_labels(self.P)
        for i, b in enumerate(self.brk):
            if b == 1:
                self.assertEqual(lab[i], 0, f"{self.rows[i]['date']} kırılma ama evre yükselme")

    def test_base_rate_uses_warmup_only(self):
        """p0, yalnız 2022-12-31'e kadar ONAYLANMIŞ etiketlerden; sonraki veri girerse değişir."""
        we = max(i for i, r in enumerate(self.rows) if r["date"] <= date(2022, 12, 31))
        p0, n = RV.warmup_base_rate(self.brk, self.conf, we)
        rows2 = [r for r in self.rows if r["date"] <= date(2022, 12, 31)]
        brk2, conf2, _ = T3.break_labels([r["p06"] for r in rows2])
        we2 = len(rows2) - 1
        p0b, nb = RV.warmup_base_rate(brk2, conf2, we2)
        self.assertAlmostEqual(p0, p0b, places=12)
        self.assertEqual(n, nb)

    def test_entry_channel_is_literally_v2(self):
        """Giriş kanalı v2 nesnesinin kendisidir — kopya değil."""
        net = T3.TeraziV3(0.07)
        self.assertIsInstance(net.entry, T2.TeraziV2)
        self.assertEqual(T3.LAM, T2.LAM)
        self.assertEqual(T3.THETA, T2.THETA)

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
        self.assertFalse(hasattr(T3, "BUY_TH"))
        self.assertAlmostEqual(T3.FEE, S.FEE)
        A = RV.marathon(tempfile.mkdtemp(), write=False)
        if A["trades"]:
            self.assertGreater(A["gross_hist"][-1][1], A["nav_hist"][-1][1])

    def test_macro_gate_missing_values_are_false(self):
        self.assertFalse(T3.macro_confirms({}))
        self.assertFalse(T3.macro_confirms(dict(rr_d5=None, y2_d5=None)))
        self.assertFalse(T3.macro_confirms(dict(rr_d5=-0.1, y2_d5=-0.2)))
        self.assertTrue(T3.macro_confirms(dict(rr_d5=0.1, y2_d5=None)))
        self.assertTrue(T3.macro_confirms(dict(rr_d5=None, y2_d5=0.1)))


if __name__ == "__main__":
    unittest.main()
