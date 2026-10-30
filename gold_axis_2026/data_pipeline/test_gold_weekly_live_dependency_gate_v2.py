#!/usr/bin/env python3
"""Offline fail-closed and provenance invariance tests for dependency gate V2."""
import unittest
from datetime import date, datetime, timedelta, timezone
from gold_weekly_live_dependency_gate_v2 import (
    METALS, compose, inspect_metals, target_monday,
)

UTC = timezone.utc
FRIDAY_PRE_CLOSE = datetime(2026, 10, 30, 7, 30, tzinfo=UTC)
SATURDAY_AFTER = datetime(2026, 10, 31, 8, tzinfo=UTC)


def rows(evidence="FIRSTPRINT_PROSPECTIVE",
         capture=datetime(2026, 10, 29, 7, tzinfo=UTC), days=3):
    return [{"price_date": date(2026, 10, 26) + timedelta(days=d),
             "metal": m, "evidence_status": evidence,
             "source_captured_at": capture}
            for d in range(days) for m in METALS]


class TestLiveDependencies(unittest.TestCase):
    def test_no_current_week_backdated_origin(self):
        self.assertEqual(target_monday(FRIDAY_PRE_CLOSE), date(2026, 11, 2))
        a = inspect_metals(rows(), FRIDAY_PRE_CLOSE)
        self.assertEqual(a["status"], "BLOCKED_ORIGIN_NOT_CLOSED")

    def test_all_good_four_metals_only_candidate(self):
        a = inspect_metals(rows(), SATURDAY_AFTER)
        self.assertEqual(a["status"], "FOUR_METAL_INPUT_PIT_CANDIDATE_ONLY")
        self.assertEqual(a["fourMetalAlignedDays"], 3)
        report = compose(SATURDAY_AFTER, {"status": "READY"}, a, 0, 0)
        self.assertEqual(report["status"], "BLOCKED_NOT_LIVE")
        self.assertEqual(report["weeklyANN"]["status"],
                         "BLOCKED_ORIGINAL_CHECKPOINT_AND_EXECUTOR_UNVERIFIED")
        self.assertFalse(report["liveForecastPublished"])
        self.assertFalse(report["liveRiskSignalPublished"])

    def test_research_source_cannot_be_promoted(self):
        a = inspect_metals(rows("RESEARCH_GIT_SNAPSHOT_NOT_PIT"), SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_RESEARCH_SNAPSHOT_NOT_FIRSTPRINT")

    def test_cannot_use_gold_ny17_to_replace_missing_metals(self):
        a = inspect_metals([r for r in rows() if r["metal"] == "AU"], SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_FOUR_METAL_ORIGIN_WEEK_MISSING")

    def test_future_capture_not_pit(self):
        a = inspect_metals(
            rows(capture=datetime(2026, 11, 1, tzinfo=UTC)), SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_SOURCE_NOT_AVAILABLE_AT_ORIGIN")

    def test_missing_source_capture_not_pit(self):
        a = inspect_metals(rows(capture=None), SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_SOURCE_NOT_AVAILABLE_AT_ORIGIN")

    def test_duplicate_metal_rejected(self):
        many = rows()
        many.append(dict(many[0]))
        a = inspect_metals(many, SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_INVALID_FOUR_METAL_ROWS")

    def test_only_two_aligned_days_block(self):
        a = inspect_metals(rows(days=2), SATURDAY_AFTER)
        self.assertEqual(a["status"], "BLOCKED_FOUR_METAL_ORIGIN_WEEK_MISSING")

    def test_even_fake_rows_never_promote_live(self):
        four = inspect_metals(rows(), SATURDAY_AFTER)
        got = compose(SATURDAY_AFTER, {"status": "READY"}, four, 10, 10)
        self.assertEqual(got["status"], "BLOCKED_NOT_LIVE")
        self.assertTrue(got["monthlyCalibrationPaused"])
        self.assertTrue(got["portfolioUnchanged"])
        self.assertFalse(got["databaseWrites"])


if __name__ == "__main__":
    unittest.main()
