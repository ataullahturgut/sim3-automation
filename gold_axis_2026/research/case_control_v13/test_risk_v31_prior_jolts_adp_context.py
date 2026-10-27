import unittest
from datetime import timedelta
import risk_v31_prior_jolts_adp_context as pc
from risk_v31_macro_event_layer import utc

class PreNFPJuneV31Tests(unittest.TestCase):
    def test_may_2026_no_june_context(self):
        self.assertEqual(pc.available_prior_context(utc("2026-05-29T16:30:00Z")),[])
    def test_no_JOLTS_before_first_observed_public_source(self):
        self.assertEqual(pc.available_prior_context(utc("2026-06-02T14:15:00Z")),[])
    def test_only_JOLTS_before_ADP_source_available(self):
        a=pc.available_prior_context(utc("2026-06-03T11:00:00Z"))
        self.assertEqual(len(a),1)
        self.assertTrue(a[0]["event_code"].startswith("JOLTS"))
    def test_June4_prior_context_both_sources_but_no_sell(self):
        a=pc.available_prior_context(utc("2026-06-04T13:45:00Z"))
        self.assertEqual([x["event_code"] for x in a],["JOLTS_20260602","ADP_20260603"])
        self.assertTrue(all(not x["macro_adverse_gold_direction_known"] for x in a))
        self.assertTrue(all(not x["automatic_risk_override"] for x in a))
        self.assertTrue(all(not x["historical_consensus_PIT_certified"] for x in a))
    def test_report_marks_unproven_consensus(self):
        result=pc.main()
        self.assertFalse(result["is_NFP_direction_forecast"])
        self.assertFalse(result["is_actionable_sell"])
        self.assertFalse(result["model_BASE14_CFTC21_V22_changed"])

if __name__=="__main__":unittest.main(verbosity=2)
