import unittest
import pandas as pd
import numpy as np
from risk_v24_event_timelines import load,event_timeline,family_timeline,O
from risk_v24_source_publication_audit import main as verify_external_sources

class PersistedV24ExportsAgreeWithExecutedAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        px,d,ledger=load()
        cls.events=event_timeline(px,d,ledger).set_index("event_id")
        cls.family=family_timeline(cls.events.reset_index()).set_index("economic_family")
        verify_external_sources()

    def test_compact_events_equal_calculated_outputs(self):
        c=pd.read_csv(O/"v24_nine_event_compact_audit.csv").set_index("event_id")
        self.assertEqual(set(c.index),set(self.events.index))
        mapping={"price_peak":"price_peak",
             "first_V22_attention_strict_prepeak_10_sessions":"V22_first_any_prior10",
             "first_V22_attention_strict_prepeak_5_sessions":"V22_first_any_prior5",
             "first_V22_attention_on_or_before_peak":"V22_first_any_before_or_on_peak",
             "first_1pct_drop_close":"first_1pct_drawdown_close",
             "original_onset_proxy":"original_v13_onset_proxy",
             "trough":"price_trough",
             "prior10_model_score_days":"prior10_scoreable_sessions",
             "verdict":"verdict"}
        for short,long in mapping.items():
            left=c[short].fillna("").astype(str).tolist()
            right=self.events.loc[c.index,long].fillna("").astype(str).tolist()
            self.assertEqual(left,right,(short,long))
        np.testing.assert_allclose(c["peak_to_trough_percent"],
             self.events.loc[c.index,"peak_to_trough_pct"],rtol=0,atol=0.000001)
        prelead=c["prepeak_lead_price_sessions"]
        actual=self.events.loc[c.index,"V22_signal_to_peak_sessions"]
        np.testing.assert_allclose(prelead,actual,equal_nan=True,atol=0)
    def test_compact_economic_families_match_generated(self):
        c=pd.read_csv(O/"v24_seven_economic_families_compact_audit.csv").set_index("economic_family")
        self.assertEqual(set(c.index),set(self.family.index))
        for fam,r in c.iterrows():
            actual=self.family.loc[fam]
            self.assertEqual(r.family_verdict,actual.family_verdict)
            self.assertEqual(r.first_component_peak,actual.first_component_peak)
            self.assertEqual(r.component_events,actual.component_events)
    def test_external_price_checks_match_audit(self):
        committed=pd.read_csv(O/"v24_external_price_spotchecks_committed.csv").set_index("date")
        calculated=pd.read_csv(O/"v24_external_price_source_comparison.csv").set_index("date")
        self.assertEqual(set(committed.index),set(calculated.index))
        for date,r in committed.iterrows():
            a=calculated.loc[date]
            self.assertAlmostEqual(r.research_snapshot_usd_oz,a.stored_price)
            self.assertAlmostEqual(r.secondary_LBMA_AM_usd_oz,a.secondary_LBMA_AM)
            self.assertAlmostEqual(r.secondary_LBMA_PM_usd_oz,a.secondary_LBMA_PM)
    def test_official_cftc_checks_match_audit(self):
        committed=pd.read_csv(O/"v24_cftc_release_spotchecks_committed.csv").set_index("report_as_of_date")
        calc=pd.read_csv(O/"v24_cftc_official_schedule_spotchecks.csv").set_index("CFTC_report_as_of")
        self.assertEqual(set(committed.index),set(calc.index))
        for date,r in committed.iterrows():
            self.assertEqual(r.official_release_date,calc.loc[date,"official_released"])
            self.assertEqual(r.conservative_model_usable_date,calc.loc[date,"conservative_usable"])

if __name__=="__main__":unittest.main(verbosity=2)
