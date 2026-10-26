import json,unittest
from pathlib import Path
import pandas as pd
D=Path(__file__).parent/"outputs"
class RuleQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=pd.read_csv(D/"v16_bi_daily.csv")
        cls.metrics=pd.read_csv(D/"v16_bi_metrics.csv")
        cls.original=pd.read_csv(D/"v15_daily_intelligence.csv")
        cls.audit=json.loads((D/"v16_bi_audit.json").read_text())

    def test_original_alerts_bit_exact(self):
        a=self.data.sort_values(["origin","model"])
        b=self.original.sort_values(["origin","model"])
        self.assertEqual(len(a),len(b))
        self.assertEqual(a.alert_level.tolist(),b.alert_level.tolist())
        self.assertEqual(a.risk_score.tolist(),b.risk_score.tolist())

    def test_2010_2022_historical_comparators_only(self):
        z=self.data[self.data.BI_priority=="BI_CONFIRMED"]
        self.assertTrue(z.nearest_historic_crash_date.str[:4].astype(int).le(2022).all())
        self.assertTrue(z.nearest_historic_no_crash_date.str[:4].astype(int).le(2022).all())

    def test_all_nonred_never_escalate(self):
        self.assertTrue((self.data.loc[~self.data.original_red_unchanged,"BI_priority"]=="NOT_RED").all())
        self.assertTrue(self.data.loc[self.data.BI_priority=="BI_CONFIRMED","original_red_unchanged"].all())

    def test_frozen_2025_and_retrospective_2026_results(self):
        def get(year,layer):
            x=self.metrics[(self.metrics.year==year)&(self.metrics.model=="BASE14")&(self.metrics.layer==layer)]
            return x.iloc[0]
        for yr,layer,red,false,cluster,h1 in [
            (2025,"ORIGINAL_RED",32,27,3,2),
            (2025,"BI_CONFIRMED",28,23,3,2),
            (2026,"ORIGINAL_RED",50,40,4,4),
            (2026,"BI_CONFIRMED",28,19,4,3)]:
            x=get(yr,layer)
            self.assertEqual((x.flag_days,x.false_5d_days,x.group_hit,x.hit_nextday3),(red,false,cluster,h1))

    def test_audit_guards(self):
        self.assertFalse(self.audit["predictor_trained"])
        self.assertFalse(self.audit["red_levels_changed"])
        self.assertFalse(self.audit["uses_future_outcome_as_input"])
        self.assertFalse(self.audit["2026_is_blind_test"])
        self.assertFalse(self.audit["first_print_verified"])

if __name__=="__main__":
    unittest.main(verbosity=2)
