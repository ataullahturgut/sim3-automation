"""V14 integration acceptance tests on frozen genuine historical outputs."""
import unittest
import json
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).parent
OUT=ROOT/"outputs"

class V14ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=pd.read_csv(OUT/"v14_training_audit.csv")
        cls.metrics=pd.read_csv(OUT/"v14_metrics_2025_2026.csv")
        cls.daily=pd.read_csv(OUT/"v14_daily_signals.csv")
        cls.freeze=json.loads((OUT/"v14_freeze.json").read_text())

    def test_incumbents_not_changed(self):
        m=self.metrics.set_index(["period","model"])
        for model,red,false5,hit1,groups in [
            ("BASE14",50,40,4,4),("CFTC21",32,25,4,3)
        ]:
            a=m.loc[(2026,model)]
            self.assertEqual((a.red,a.false5,a.hit1,a.groups_hit),(red,false5,hit1,groups))

    def test_2013_included(self):
        p=pd.read_csv(OUT/"v14_event_control_pairs.csv")
        for family in self.audit.family:
            q=p[p.family==family]
            self.assertGreaterEqual(len(q[q.peak.str.startswith("2013")]),3)
            self.assertGreaterEqual(len(q),15)

    def test_independent_policy_exists(self):
        m=set(self.metrics.model)
        self.assertTrue(any(x.endswith("_INDEPENDENT") for x in m))
        self.assertTrue(any(x.endswith("_PLUS") for x in m))

    def test_2026_did_not_train_or_select(self):
        self.assertFalse(self.freeze["trained_on_2026"])
        self.assertFalse(self.freeze["selected_on_2026"])
        self.assertFalse(self.freeze["signal_approved_for_production"])

    def test_origins_matched(self):
        d=self.daily
        self.assertEqual(len(d[d.origin.str.startswith("2026")]),161)
        self.assertEqual(len(d[d.origin.str.startswith("2025")]),232)
        self.assertTrue(d.origin.is_unique)
        self.assertFalse(d.live_signals_changed.astype(str).str.lower().eq("true").any())

    def test_control_limit(self):
        p=pd.read_csv(OUT/"v14_event_control_pairs.csv")
        self.assertTrue(p.controls.between(2,3).all())
        self.assertTrue((p.positive_samples>0).all())

    def test_candidate_selection_gate(self):
        selected=self.freeze["selected_research_candidate"]
        m=self.metrics
        if selected:
            sel=m[(m.period==2025)&(m.model==selected)].iloc[0]
            base=m[(m.period==2025)&(m.model=="BASE14")].iloc[0]
            self.assertEqual(sel.hit1,sel.total1)
            self.assertEqual(sel.groups_hit,sel.groups)
            self.assertLess(sel.false5,base.false5)
        else:
            self.assertEqual(self.freeze["shadow_model"],"BASE14")

if __name__=="__main__":
    unittest.main(verbosity=2)
