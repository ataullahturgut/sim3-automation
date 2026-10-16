"""PREREG §11 zorunlu testleri: gelecek bilgisi, olgunlaşma, tekrar üretilebilirlik.
Performans metriği hesaplamaz. Çalıştırma: python3 -m unittest test_pusula_v1 -v
"""
import os, copy, random, unittest
from datetime import date
import pusula_v1 as P

PANEL = os.path.join(os.path.dirname(__file__), "data", "PUSULA_V1_DAILY_ASOF_PANEL.csv")
KEYS = ("mu", "sd", "v", "c2", "action", "pos", "nav", "nav_passive", "nav_trend", "w")


def perturb_after(rows, cut, seed=7):
    rnd = random.Random(seed); out = copy.deepcopy(rows)
    for r in out:
        if r["date"] > cut:
            f = rnd.uniform(0.7, 1.3)
            r["p06"] *= f; r["bid"] *= f * rnd.uniform(0.99, 1.0); r["ask"] = max(r["bid"] * 1.0001, r["ask"] * f)
            for s in ("nq", "zn", "cl", "si"):
                if r[s] is not None: r[s] *= rnd.uniform(0.5, 1.5)
    return out


class TestPusula(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = P.load_panel(PANEL)
        cls.log, _, _ = P.run(cls.rows)

    def test_no_future_leak_by_perturbation(self):
        for cut in (date(2022, 6, 30), date(2024, 3, 15), date(2025, 11, 28)):
            log2, _, _ = P.run(perturb_after(self.rows, cut))
            for a, b in zip(self.log, log2):
                if a["date"] > cut.isoformat(): break
                for k in KEYS:
                    self.assertEqual(a[k], b[k], f"{cut} {a['date']} {k}")

    def test_truncated_run_matches_full_run(self):
        for n in (300, 900, 1400):
            log2, _, _ = P.run(self.rows[:n])
            for k in KEYS:
                self.assertEqual(self.log[n - 1][k], log2[n - 1][k], f"n={n} {k}")

    def test_labels_mature_only_after_horizon(self):
        # t gününün etiketi y_t yalnız t+H+1 kararından itibaren öğrenilir: kesilmiş koşuda
        # son H+1 günün etiketi olmamalı, daha eskiler olmalı.
        n = 700; log2, _, _ = P.run(self.rows[:n])
        last_with_y = max(g["t"] for g in log2 if g["y"] is not None)
        self.assertEqual(last_with_y, n - 1 - P.H - 1)

    def test_deterministic(self):
        log2, _, _ = P.run(self.rows)
        self.assertEqual([tuple(g[k] for k in KEYS) for g in self.log], [tuple(g[k] for k in KEYS) for g in log2])

    def test_no_trading_before_start_and_costs(self):
        for g in self.log:
            if g["date"] < P.TRADE_START.isoformat():
                self.assertEqual(g["action"], "WAIT"); self.assertIsNone(g["nav"])
        self.assertAlmostEqual(P.B, P.C_RT / 6)
        self.assertTrue(abs(P.C_RT - 1.6064) < 1e-3)


if __name__ == "__main__":
    unittest.main()
