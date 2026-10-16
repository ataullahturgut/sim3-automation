"""DENEYİM v1.1 testleri: C0 = v1 birebir, C1/C2 nedensellik, sonuç belleği olgunlaşması.
Çalıştırma: python3 -m unittest test_deneyim_v1_1 -v
"""
import json, os, tempfile, unittest
from datetime import date
import deneyim_states as S
import deneyim_v1 as D

HERE = os.path.dirname(os.path.abspath(__file__))


class T(unittest.TestCase):
    def test_c0_identical_to_v1(self):
        v1 = json.load(open(os.path.join(HERE, "DENEYIM_V1_MARATON_OZET.json")))
        R = D.marathon(tempfile.mkdtemp(), mode="C0")
        self.assertEqual([(t["date"], t["action"], t["price"]) for t in R["trades"]],
                         [(t["date"], t["action"], t["price"]) for t in v1["model"]["trade_list"]])
        self.assertAlmostEqual(R["nav_hist"][-1][1], v1["model"]["final_nav"], places=3)

    def test_outcome_memory_only_matured(self):
        R = D.marathon(tempfile.mkdtemp(), mode="C1")
        i_end = len(R["rows"]) - 1
        self.assertEqual(len(R["model"].outR), i_end - D.H_OUT - R["i_start"] + 1)

    def test_c1_c2_monthly_causality(self):
        rows_full = S.load_rows()
        cut = [r for r in rows_full if r["date"] <= date(2024, 9, 30)]
        for mode in ("C1", "C2"):
            full = D.marathon(tempfile.mkdtemp(), mode=mode)
            orig = S.load_rows
            try:
                S.load_rows = lambda dev_only=True: cut
                part = D.marathon(tempfile.mkdtemp(), mode=mode)
            finally:
                S.load_rows = orig
            self.assertEqual({i: e for i, e in full["est"].items() if i in part["est"]}, part["est"])
            self.assertEqual([t for t in full["trades"] if t["date"] <= "2024-09-30"], part["trades"])


if __name__ == "__main__":
    unittest.main()
