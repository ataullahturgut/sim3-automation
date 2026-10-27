import csv
import unittest
from datetime import timedelta,timezone
from pathlib import Path
import risk_v31_macro_event_layer as v31

class MacroLayerV31Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events=v31.events()
        cls.thresholds=v31.calibrated_2023_2024(cls.events)
    def row(self,day,family):
        return next(x for x in self.events if x["release_utc"].startswith(day) and x["family"]==family)
    def test_108_events_and_source_provenance_reconstructed(self):
        self.assertEqual(len(self.events),108)
        self.assertFalse(any(x["source_macro_consensus_before_release_proven"]=="true" for x in self.events))
    def test_training_only_2023_2024_frozen_thresholds(self):
        copy=[x.copy() for x in self.events]
        for x in copy:
            if x["event_year"] in ("2025","2026"):
                x["gold_return_30m_pct"]="-999.0"
        self.assertEqual(self.thresholds,v31.calibrated_2023_2024(copy))
    def test_release_before_no_surprise_or_reaction(self):
        e=self.row("2026-06-05","NFP");now=v31.utc(e["release_utc"])
        thr=self.thresholds["NFP"]["q10_30m_pct"]
        pre=v31.assess(e,now-timedelta(seconds=1),thr)
        self.assertIsNone(pre["gold_return_30m_pct"])
        self.assertEqual(pre["published_event_surprise_sign"],"NOT_AVAILABLE_PRE_RELEASE")
        self.assertEqual(pre["state"],"PENDING_UNVERIFIED_CALENDAR")
        self.assertFalse(pre["live_eligible"])
        release=v31.assess(e,now,thr)
        self.assertEqual(release["state"],"AWAIT_REACTION_30M_BAR")
        self.assertIsNone(release["gold_return_30m_pct"])
    def test_june_nfp_event_detection_only_at_1605_turkey(self):
        e=self.row("2026-06-05","NFP");dt=v31.utc(e["release_utc"])
        t=self.thresholds["NFP"]["q10_30m_pct"]
        self.assertLessEqual(-1.207191906,t)
        p=v31.assess(e,dt+timedelta(minutes=34,seconds=59),t)
        self.assertIsNone(p["gold_return_30m_pct"])
        hit=v31.assess(e,dt+timedelta(minutes=35),t)
        self.assertEqual(hit["state"],"EVENT_REPRICING_RESEARCH_REVIEW")
        self.assertTrue(hit["earliest_30m_complete_TR"].startswith("2026-06-05T16:05:"))
        self.assertFalse(hit["live_eligible"])
        self.assertEqual(hit["published_event_surprise_sign"],"POSITIVE")
    def test_june_CPI_not_fake_negative_surprise(self):
        e=self.row("2026-06-10","CPI");t=self.thresholds["CPI"]["q10_30m_pct"]
        self.assertEqual(e["cpi_actual_minus_consensus_sign"],"ZERO")
        res=v31.assess(e,v31.utc(e["release_utc"])+timedelta(minutes=35),t)
        self.assertEqual(res["state"],"NO_RARE_ADVERSE_REACTION")
        self.assertGreater(res["gold_return_30m_pct"],0)
    def test_june_FOMC_outside_bank_hours(self):
        e=self.row("2026-06-17","FOMC")
        hit=v31.assess(e,v31.utc(e["release_utc"])+timedelta(minutes=35),self.thresholds["FOMC"]["q10_30m_pct"])
        self.assertEqual(hit["bank_window"],"OUTSIDE_BANK_WINDOW")
        self.assertFalse(hit["live_eligible"])
    def test_calendar_captured_before_vs_after(self):
        e=self.row("2026-06-05","NFP")
        time=v31.utc(e["release_utc"])
        kwargs=dict(calendar_url="https://www.bls.gov/schedule/news_release/empsit.htm",
                    official_schedule_captured=True)
        valid=dict(kwargs,calendar_captured_at=(time-timedelta(days=2)).isoformat())
        future=dict(kwargs,calendar_captured_at=(time+timedelta(hours=1)).isoformat())
        self.assertEqual(v31.assess(e,time-timedelta(minutes=10),-0.1,valid)["state"],"EVENT_PENDING")
        self.assertEqual(v31.assess(e,time-timedelta(minutes=10),-0.1,future)["state"],"PENDING_UNVERIFIED_CALENDAR")
    def test_live_must_really_have_captured_at_and_no_auto_sell(self):
        e=self.row("2026-06-05","NFP")
        release=v31.utc(e["release_utc"])
        approved=dict(calendar_captured_at=(release-timedelta(days=1)).isoformat(),
                     calendar_url="https://www.bls.gov/schedule/news_release/empsit.htm",
                     official_schedule_captured=True,
                     actual_captured_at=(release+timedelta(minutes=1)).isoformat(),
                     consensus_captured_at=(release-timedelta(minutes=1)).isoformat(),
                     original_firstprint_verified=True,
                     bars_captured_at=(release+timedelta(minutes=36)).isoformat(),
                     bars_firstprint_verified=True)
        t=self.thresholds["NFP"]["q10_30m_pct"]
        # Historical mode blocks even with a manufactured-looking proof object.
        historical=v31.assess(e,release+timedelta(minutes=40),t,approved,historical=True)
        self.assertFalse(historical["live_eligible"])
        self.assertEqual(historical["action"],"INFORMATIONAL_NOT_AL_SAT")
        missing=v31.assess(e,release+timedelta(minutes=40),t,
                 {k:v for k,v in approved.items() if k!="consensus_captured_at"},historical=False)
        self.assertFalse(missing["live_eligible"])
        eligible=v31.assess(e,release+timedelta(minutes=40),t,approved,historical=False)
        self.assertTrue(eligible["live_eligible"])
        self.assertEqual(eligible["action"],"INFORMATIONAL_NOT_AL_SAT")
    def test_no_presumed_DXY_US2Y_OIL_or_original_model_change(self):
        r=v31.run()
        self.assertFalse(r["live_promotion_allowed"])
        self.assertTrue(r["original_model_unchanged"])
        self.assertEqual(r["events"],108)
        with (v31.OUT/"v31_june2026_macro_event_replay.csv").open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),3)
        self.assertTrue(all(z["DXY_2Y_OIL_intraday_confirmation"]=="NOT_FOUND" for z in rows))
        self.assertTrue(all(z["legacy_BASE14_CFTC21_V22_modified"]=="False" for z in rows))

if __name__=="__main__":unittest.main(verbosity=2)
