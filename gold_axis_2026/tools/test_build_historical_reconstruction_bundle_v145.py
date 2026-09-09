from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_historical_reconstruction_bundle_v145.py")
spec = importlib.util.spec_from_file_location("bundle_v145", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


class BundleTests(unittest.TestCase):
    def fixture(self, blocked: bool = False):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        ny_inventory = root / "ny.csv"
        write_csv(ny_inventory, [
            {"trade_date": "2025-01-02", "gap_action": "PROBE_REQUIRED", "impacted_readiness_cells": '["FAST:2025-01"]'},
            {"trade_date": "2025-01-03", "gap_action": "PROBE_REQUIRED", "impacted_readiness_cells": '["FAST:2025-01"]'},
        ])
        status2 = "ENTITLEMENT_BLOCKED" if blocked else "PROVIDER_NO_BAR"
        probe = {
            "probe_id": "GOLD_CONTROL_HISTORICAL_NY17_EXACT_DATE_PROBE_V145",
            "production_write": "NONE",
            "rows": [
                {
                    "trade_date": "2025-01-02", "acquisition_status": "VALID_EXACT_BAR",
                    "retrieved_at": "2026-09-09T09:00:00+00:00", "payload_sha256": "a" * 64,
                    "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min",
                    "timezone": "America/New_York", "accepted_source_time": "16:59:00",
                    "stored_semantic": "17:00 ET", "source_bar_datetime": "2025-01-02 16:59:00",
                    "open": 2600, "high": 2610, "low": 2590, "close": 2605,
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False,
                    "impacted_readiness_cells": ["FAST:2025-01"],
                },
                {
                    "trade_date": "2025-01-03", "acquisition_status": status2,
                    "retrieved_at": "2026-09-09T09:00:10+00:00" if not blocked else None,
                    "payload_sha256": "b" * 64 if not blocked else None,
                    "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min",
                    "timezone": "America/New_York", "accepted_source_time": "16:59:00",
                    "stored_semantic": "17:00 ET", "provider_code": 404 if not blocked else 429,
                    "provider_message": "no data" if not blocked else "quota",
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False,
                    "impacted_readiness_cells": ["FAST:2025-01"],
                },
            ],
        }
        ny_probe = root / "probe.json"; ny_probe.write_text(json.dumps(probe), encoding="utf-8")
        gvz_inventory = root / "gvz.csv"
        write_csv(gvz_inventory, [{
            "observation_date": "2025-01-02", "value": "15.07", "acquisition_status": "AVAILABLE",
            "gap_action": "CONTROLLED_HISTORICAL_RECONSTRUCTION_WRITE_REQUIRED",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": "False",
            "impacted_readiness_cells": '["GVZ_RISK:2025-01"]',
        }])
        gap_summary = root / "summary.json"
        gap_summary.write_text(json.dumps({
            "gvz": {
                "series_id": "GVZ_CBOE", "missing_rows_to_write": 1,
                "official_source": {
                    "source_url": "https://cdn.cboe.com/GVZ_History.csv",
                    "payload_sha256": "c" * 64,
                    "retrieved_at": "2026-09-08T22:33:54+00:00",
                },
            }
        }), encoding="utf-8")
        args = argparse.Namespace(
            ny_inventory=str(ny_inventory), ny_probe=str(ny_probe), gvz_inventory=str(gvz_inventory),
            gap_summary=str(gap_summary), output_dir=str(root / "out"),
        )
        return td, args

    def test_build_passes_only_with_final_adjudications(self):
        td, args = self.fixture(False)
        try:
            result = m.build(args)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["production_database_write"], "NONE")
            self.assertEqual(result["outputs"]["ny17_valid"]["rows"], 1)
            self.assertEqual(result["outputs"]["ny17_no_bar"]["rows"], 1)
            self.assertEqual(result["outputs"]["gvz_valid"]["rows"], 1)
        finally:
            td.cleanup()

    def test_entitlement_blocker_fails_closed(self):
        td, args = self.fixture(True)
        try:
            with self.assertRaisesRegex(RuntimeError, "BLOCKED_DATA:NY17_EXACT_PROBE_INCOMPLETE"):
                m.build(args)
        finally:
            td.cleanup()

    def test_builder_has_no_database_write_path(self):
        text = MODULE_PATH.read_text(encoding="utf-8")
        forbidden = ["psycopg", "persist_bundle", "NEON_DATABASE_URL", "insert into", "update observations", "delete from"]
        for token in forbidden:
            self.assertNotIn(token.lower(), text.lower())

    def test_lane_ids_are_historical_only(self):
        self.assertEqual(m.NY17_LANE_ID, "XAU_EOD_TWELVE_NY17_HISTORICAL_REPLAY_V145")
        self.assertEqual(m.GVZ_LANE_ID, "GVZ_CBOE_HISTORICAL_REPLAY_V145")


if __name__ == "__main__":
    unittest.main()
