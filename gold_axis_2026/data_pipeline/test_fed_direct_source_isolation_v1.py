"""Offline regression tests: Federal Reserve DDP outages must not mask EFFR."""
from __future__ import annotations
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime, timezone
import fed_direct


class FedIsolationTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 30, tzinfo=timezone.utc)

    @staticmethod
    def fake_frb(_session, _run, _time, _mode, series_ids):
        sid = series_ids[0]
        if sid == "DGS10_FRB_H15":
            raise RuntimeError("FED_DIRECT_EMPTY_HTTP_BODY")
        return [SimpleNamespace(series_id=sid)]

    @staticmethod
    def fake_effr(*_):
        return [SimpleNamespace(series_id="EFFR_NYFED")]

    def test_one_ddp_empty_preserves_other_authorities(self):
        errors = []
        with patch.object(fed_direct, "_collect_frb_series", self.fake_frb), \
                patch.object(fed_direct, "_collect_effr", self.fake_effr):
            rows = fed_direct.collect_fed_direct("run", self.now, "daily", errors)
        self.assertEqual(
            {x.series_id for x in rows},
            {"DEXCHUS_FRB_H10", "DTWEXBGS_FRB_H10", "EFFR_NYFED"})
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["series"], "DGS10_FRB_H15")
        self.assertEqual(errors[0]["code"], "FED_DIRECT_SERIES_UNAVAILABLE")
        self.assertIn("FED_DIRECT_EMPTY_HTTP_BODY", errors[0]["detail"])

    def test_legacy_all_or_nothing_mode_kept(self):
        with patch.object(fed_direct, "_collect_frb_series", self.fake_frb):
            with self.assertRaisesRegex(RuntimeError, "FED_DIRECT_EMPTY_HTTP_BODY"):
                fed_direct.collect_fed_direct("run", self.now, "daily")

    def test_no_fake_price_from_all_official_source_failures(self):
        with patch.object(fed_direct, "_collect_frb_series",
                          side_effect=ValueError("OFFICIAL_UNAVAILABLE")), \
                patch.object(fed_direct, "_collect_effr",
                             side_effect=ValueError("OFFICIAL_UNAVAILABLE")):
            errors = []
            rows = fed_direct.collect_fed_direct("run", self.now, "daily", errors)
        self.assertEqual(rows, [])
        self.assertEqual(len(errors), 4)
        self.assertEqual({x["series"] for x in errors},
                         {"DGS10_FRB_H15", "DEXCHUS_FRB_H10",
                          "DTWEXBGS_FRB_H10", "EFFR_NYFED"})


if __name__ == "__main__":
    unittest.main()
