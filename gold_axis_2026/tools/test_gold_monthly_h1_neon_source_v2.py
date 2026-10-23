"""Unit tests for the source-authority and no-leakage H1 algorithm adapter.

No network, Neon password or forecast backtest is needed.
"""
from __future__ import annotations

import copy
import math
import unittest
from datetime import date, datetime, timedelta, timezone

import numpy as np
import gold_monthly_h1_neon_source_v2 as adapter


def days_of_month(ym, n=16):
    y, m = map(int, ym.split("-"))
    d = date(y, m, 1)
    result = []
    while len(result) < n:
        if d.isoweekday() <= 5:
            result.append(d)
        d += timedelta(days=1)
    return result


def make_metal_panel():
    rows = []
    monthly = []
    for index, mo in enumerate(adapter.months_between(adapter.FIRST_MONTH, adapter.LAST_MONTH)):
        revision = "lbruton/StakTrakr@" + (
            adapter.PRICE_COMMIT_OLD if mo < "2026-01" else adapter.PRICE_COMMIT_2026
        )
        daylist = days_of_month(mo)
        for code, name in adapter.METAL_CODES.items():
            prices = []
            for k, d in enumerate(daylist):
                price = 100.0 + index + (list(adapter.METAL_CODES).index(code) * 100) + k / 10
                prices.append(price)
                rows.append((code, d, price, revision))
            monthly.append((code, date.fromisoformat(mo + "-01"),
                            sum(prices) / len(prices), len(prices), revision, True))
    return rows, monthly


def make_gpr_records():
    audits = []
    hist = []
    special = []
    origin = adapter.FIRST_ORIGIN
    while origin <= adapter.LAST_ORIGIN:
        last_obs = adapter.previous(origin)
        source = "gpr_archive_files/data_gpr_export_" + origin.replace("-", "") + ".xls"
        y, m = map(int, origin.split("-"))
        released = datetime(y, m, 5, tzinfo=timezone.utc)
        cutoff = datetime.fromisoformat(adapter.next_month(origin) + "-01T00:00:00+00:00")
        commit = "a" * 40
        audit = (date.fromisoformat(origin + "-01"), date.fromisoformat(last_obs + "-01"),
                 100.0, adapter.GPR_REPOSITORY, source, commit, released, cutoff,
                 "GPR_OFFICIAL_GIT_PIT",
                 adapter.EVIDENCE_SEPTEMBER if origin == adapter.LAST_ORIGIN
                 else adapter.EVIDENCE_ARCHIVE, False)
        audits.append(audit)
        history = []
        m0 = last_obs
        for _ in range(24):
            history.append(m0)
            m0 = adapter.previous(m0)
        for h in history:
            d = date.fromisoformat(h + "-01")
            if origin == adapter.LAST_ORIGIN:
                special.append((d, 100.0, "253056ac5d54881c1f3e5767087ef682e258c7a5",
                                commit, released))
            else:
                hist.append((origin, d, 100.0, released, source, commit))
        origin = adapter.next_month(origin)
    return audits, hist, special


class TestGoldH1NeonAuthority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prices, cls.expected = make_metal_panel()
        cls.audit, cls.gpr_rows, cls.sep = make_gpr_records()

    def test_full_price_panel_four_metals_201_months_parity(self):
        daily, means, checks = adapter.normalize_daily(self.prices, self.expected)
        self.assertEqual(checks["metal_months"], 804)
        self.assertFalse(checks["source_pit_verified"])
        self.assertEqual(len(means["Gold"]), 201)
        self.assertEqual(len(daily["Palladium"]["2026-09"]), 16)
        self.assertTrue(all(np.isfinite(v).all() for s in daily.values() for v in s.values()))

    def test_price_authority_rejects_old_2026_revision(self):
        rows = list(self.prices)
        i = next(i for i, r in enumerate(rows) if adapter.month(r[1]) == "2026-08")
        bad = list(rows[i])
        bad[3] = "lbruton/StakTrakr@" + adapter.PRICE_COMMIT_OLD
        rows[i] = tuple(bad)
        with self.assertRaisesRegex(RuntimeError, "PRICE_WRONG_PINNED_COMMIT"):
            adapter.normalize_daily(rows, self.expected)

    def test_monthly_price_parity_rejects_audit_mismatch(self):
        bad = list(self.expected)
        v = list(bad[0])
        v[2] = float(v[2]) * 1.2
        bad[0] = tuple(v)
        with self.assertRaisesRegex(RuntimeError, "DAILY_MONTHLY_PRICE_MISMATCH"):
            adapter.normalize_daily(self.prices, bad)

    def test_complete_gpr_55_origin_vintages_with_full_history(self):
        vintage, checks = adapter.validate_gpr(self.audit, self.gpr_rows, self.sep)
        self.assertEqual(checks["gpr_origin_vintages"], 55)
        self.assertEqual(len(vintage["2026-08"]), 24)
        self.assertEqual(len(vintage["2026-09"]), 24)
        self.assertFalse(checks["original_live_capture"])

    def test_final_2026_october_archive_cannot_replace_historical_gpr(self):
        bad = list(self.audit)
        first = list(bad[0])
        first[4] = "gpr_archive_files/data_gpr_export_202610.xls"
        bad[0] = tuple(first)
        with self.assertRaisesRegex(RuntimeError, "GPR_WRONG_VINTAGE_FILENAME"):
            adapter.validate_gpr(bad, self.gpr_rows, self.sep)

    def test_future_gpr_publication_rejected(self):
        bad = list(self.audit)
        first = list(bad[0])
        first[6] = first[7] + timedelta(days=1)
        bad[0] = tuple(first)
        with self.assertRaisesRegex(RuntimeError, "GPR_FUTURE_RELEASE"):
            adapter.validate_gpr(bad, self.gpr_rows, self.sep)

    def test_wrong_published_history_lag_rejected(self):
        bad = list(self.gpr_rows)
        first = list(bad[0])
        first[5] = "b" * 40
        bad[0] = tuple(first)
        with self.assertRaisesRegex(RuntimeError, "GPR_HISTORY_WRONG_VINTAGE"):
            adapter.validate_gpr(self.audit, bad, self.sep)

    def test_missing_2026_september_gpr_hard_stops(self):
        with self.assertRaisesRegex(RuntimeError, "GPR_MISSING_REQUIRED_LAG"):
            adapter.validate_gpr(self.audit, self.gpr_rows, [])

    def test_wrong_september_gpr_blob_rejected(self):
        bad = list(self.sep)
        first = list(bad[0])
        first[2] = "c" * 40
        bad[0] = tuple(first)
        with self.assertRaisesRegex(RuntimeError, "GPR_SEPTEMBER_BLOB_MISMATCH"):
            adapter.validate_gpr(self.audit, self.gpr_rows, bad)

    def test_no_target_month_or_production_authorship(self):
        self.assertEqual(adapter.FIRST_MONTH, "2010-01")
        self.assertEqual(adapter.LAST_MONTH, "2026-09")
        self.assertNotIn("CORE5", adapter.PRICE_SQL)
        self.assertNotIn("gpr_official_monthly_snapshot_v1", adapter.GPR_HISTORY_SQL)
        self.assertNotIn("data_gpr_export_202610", adapter.GPR_HISTORY_SQL)


if __name__ == "__main__":
    unittest.main()
