"""V11 regression checks: historical data integrity, causal features, reporting gates."""
import csv,json,unittest,hashlib
from pathlib import Path
import numpy as np
import exp_v11_historical_case_control as m

ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.raw=m.historic()
        cls.r=json.loads((ROOT/'outputs/v11_result.json').read_text())
    def test_source_year_counts(self):
        from collections import Counter
        counts=Counter(r['date'][:4] for r in self.raw)
        self.assertEqual([counts[str(y)] for y in range(2010,2020)],[253,251,252,253,253,253,253,252,253,253])
    def test_historical_price_source_hash(self):
        self.assertEqual(len(self.raw),2526)
        self.assertEqual(hashlib.sha256((ROOT/'historical_gold_daily_research_2010_2019.csv').read_bytes()).hexdigest(),
                         self.r['historical_price_csv_sha256'])
    def test_no_2020_to_2022_leak(self):
        self.assertTrue(all('2010'<=r['origin'][:4]<='2019' for r in self.rows))
    def test_causal_exclusion_of_future(self):
        dates=[str(i) for i in range(120)]
        p=np.linspace(100,140,120)
        a=m.features(dates,p)
        q=p.copy();q[67]*=0.6
        b=m.features(dates,q)
        self.assertTrue(np.allclose(a[4]['features'],b[4]['features']))
        self.assertNotEqual(a[4]['future5_min'],b[4]['future5_min'] if len(b)>4 else -999)
    def test_episodes_and_controls(self):
        self.assertEqual(int(sum(r['five'] for r in self.rows)),43)
        cc=m.control_matches(self.rows)
        self.assertEqual(len(cc),16)
        self.assertEqual(sum(len(r['controls']) for r in cc),48)
    def test_v8_reference_exact(self):
        for y,base,cftc in [('2025',31,30),('2026',46,31)]:
            self.assertEqual(self.r['paired_metrics'][y]['BASE14']['alerts'],base)
            self.assertEqual(self.r['paired_metrics'][y]['CFTC21']['alerts'],cftc)
    def test_validated_risk_model_selection(self):
        self.assertEqual(self.r['selected_from_2025_only'],'CFTC21')
        self.assertFalse(self.r['tuned_on_2026'])
        self.assertTrue(self.r['not_promoted'])
        self.assertFalse(self.r['historical_price_first_print_verified'])
    def test_2015_2019_weak_history_model_not_promoted(self):
        v=self.r['historic_validation']
        self.assertEqual(v['heldout_event_origins'],4)
        self.assertLess(v['heldout_roc_auc'],0.5)
        self.assertEqual(sum(x['hit_p_ge_0_5'] for x in v['heldout_by_year']),1)
        self.assertEqual(sum(x['false_p_ge_0_5'] for x in v['heldout_by_year']),92)
    def test_no_missing_or_nan_features(self):
        self.assertTrue(np.isfinite(np.array([r['features'] for r in self.rows])).all())
    def test_event_metrics_distinction(self):
        m26=self.r['paired_metrics']['2026']['BASE14'];self.assertEqual(m26['five_label_groups_total'],4)
        self.assertEqual(m26['next5_origin_total'],13)
        self.assertEqual(m26['prior5_origin_groups'],3)
if __name__=='__main__':unittest.main()