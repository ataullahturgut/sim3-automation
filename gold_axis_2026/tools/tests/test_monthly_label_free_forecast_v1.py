"""Regression tests for label-free next-month VW-MIDAS / ChHHO-ANFIS X.

All fixtures are synthetic. This test asserts *algorithmic as-of separation*
without representing archived prices or official historical PIT availability.
"""
from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_meta_screen_v6 as av6
import vw_midas_anfis_stage3c_literature_v1 as chhho


TARGET = "2026-01"
ORIGIN = "2025-12"
METALS = base.METALS


def synthetic_bundle():
    months = list(base.month_range("2009-01", TARGET))
    daily, monthly = {}, {}
    for j, metal in enumerate(METALS):
        daily[metal] = {}
        monthly[metal] = {}
        for i, m in enumerate(months):
            # Distinct drifting/nonlinear signals, 8 origin-safe features, 4 labels.
            center = (1000 + 110*j) * math.exp(0.0008*i + 0.013*math.sin(i*0.17+j*0.5))
            v = np.asarray([center * math.exp(
                0.0002*d*(j+1)+0.0008*math.sin(i*0.21+d*0.5+j)
            ) for d in range(8)], dtype=float)
            daily[metal][m] = v
            monthly[metal][m] = float(v.mean())
    gpr = {m: 40+10*math.sin(i*0.17)+0.015*i
           for i, m in enumerate(base.month_range("2008-01", ORIGIN))}
    return SimpleNamespace(monthly_metal=monthly,
                           daily_month_values=daily,
                           core_gpr=dict(gpr),
                           gpr_vintages={ORIGIN: dict(gpr)})


def remove_target_prices(bundle):
    for metal in METALS:
        bundle.monthly_metal[metal].pop(TARGET, None)
        bundle.daily_month_values[metal].pop(TARGET, None)


class MonthlyUnlabeledTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_with_future = synthetic_bundle()
        cls.bundle_without_future = copy.deepcopy(cls.bundle_with_future)
        remove_target_prices(cls.bundle_without_future)

    def test_forecast_target_requires_no_future_month_price_for_any_metal(self):
        samples = base.all_samples_at_origin(self.bundle_without_future, TARGET, governed=True)
        self.assertIn(TARGET, samples)
        self.assertIsNone(samples[TARGET][1])
        self.assertEqual(samples[TARGET][0].shape, (8,))
        self.assertTrue(np.isfinite(samples[TARGET][0]).all())
        self.assertGreaterEqual(len(samples)-1, 180)

    def test_future_prices_do_not_change_training_or_target_x(self):
        with_future = base.all_samples_at_origin(self.bundle_with_future, TARGET, governed=True)
        no_future = base.all_samples_at_origin(self.bundle_without_future, TARGET, governed=True)
        self.assertEqual(sorted(with_future), sorted(no_future))
        self.assertIsNone(with_future[TARGET][1])
        self.assertIsNone(no_future[TARGET][1])
        for m in with_future:
            np.testing.assert_array_equal(with_future[m][0], no_future[m][0])
            if m != TARGET:
                np.testing.assert_array_equal(with_future[m][1], no_future[m][1])

    def test_chhho_training_and_validation_arrays_unchanged(self):
        a = base.all_samples_at_origin(self.bundle_with_future, TARGET, governed=True)
        b = base.all_samples_at_origin(self.bundle_without_future, TARGET, governed=True)
        ak, aX, aY, at, asplit = av6.raw_arrays(a, TARGET)
        bk, bX, bY, bt, bsplit = av6.raw_arrays(b, TARGET)
        self.assertEqual(ak, bk)
        self.assertEqual(asplit, bsplit)
        self.assertEqual(len(ak), 190)
        for aa, bb in ((aX,bX), (aY,bY), (at,bt)):
            np.testing.assert_array_equal(aa, bb)

    def test_historical_training_label_unchanged(self):
        month = "2025-01"
        history = self.bundle_with_future.gpr_vintages[ORIGIN]
        x, y = base.sample_for_target(self.bundle_with_future, month, history, True)
        p, pp = "2024-12", "2024-11"
        z = base.gpr_norm(history, pp)
        old_x = []
        old_y = []
        for metal in METALS:
            mm = self.bundle_with_future.monthly_metal[metal]
            old_x.extend([math.log(mm[p]/mm[pp]),
                          base.weighted_daily_return(self.bundle_with_future, metal, p, z)])
            old_y.append(math.log(mm[month]/mm[p]))
        np.testing.assert_array_equal(x, np.asarray(old_x))
        np.testing.assert_array_equal(y, np.asarray(old_y))

    def test_historical_label_contract_does_not_silently_accept_missing_y(self):
        hist = self.bundle_without_future.gpr_vintages[ORIGIN]
        with self.assertRaisesRegex(RuntimeError, "TRAINING_LABEL_MONTH_MISSING"):
            base.sample_for_target(self.bundle_without_future, TARGET, hist, True)

    def test_target_missing_origin_feature_is_hard_fail(self):
        corrupt = copy.deepcopy(self.bundle_without_future)
        corrupt.monthly_metal["Gold"].pop(ORIGIN)
        with self.assertRaisesRegex(RuntimeError, "ORIGIN_FEATURE_MONTH_MISSING"):
            base.all_samples_at_origin(corrupt, TARGET, governed=True)

    def test_target_missing_origin_daily_is_hard_fail(self):
        corrupt = copy.deepcopy(self.bundle_without_future)
        corrupt.daily_month_values["Gold"].pop(ORIGIN)
        with self.assertRaisesRegex(RuntimeError, "INSUFFICIENT_DAILY_ROWS"):
            base.all_samples_at_origin(corrupt, TARGET, governed=True)

    def test_target_missing_relevant_gpr_is_hard_fail(self):
        corrupt = copy.deepcopy(self.bundle_without_future)
        corrupt.gpr_vintages[ORIGIN].pop("2025-11")
        with self.assertRaisesRegex(RuntimeError, "GPR_HISTORY_NOT_AVAILABLE"):
            base.all_samples_at_origin(corrupt, TARGET, governed=True)

    def test_chhho_optimizer_can_predict_with_target_month_absent(self):
        # Research smoke: run the REAL CHHHO optimizer and local ANFIS select
        # with a deliberately tiny search budget. Not a performance backtest.
        a = base.all_samples_at_origin(self.bundle_with_future, TARGET, governed=True)
        b = base.all_samples_at_origin(self.bundle_without_future, TARGET, governed=True)
        with patch.object(chhho, "POP", 4), patch.object(chhho, "GENS", 2), \
             patch.object(chhho, "REPEATS", 1), patch.object(av6, "LOCAL_MAX_EPOCHS", 2):
            first, n1, diag1 = chhho.select(a, TARGET, "CHHHO")
            second, n2, diag2 = chhho.select(b, TARGET, "CHHHO")
            price_first = chhho.forecast_at_origin(self.bundle_with_future, TARGET, 4309.0)
            price_second = chhho.forecast_at_origin(self.bundle_without_future, TARGET, 4309.0)
        self.assertEqual(n1, n2)
        self.assertTrue(np.isfinite(first).all())
        np.testing.assert_array_equal(first, second)
        self.assertEqual(diag1, diag2)
        self.assertEqual(price_first, price_second)
        self.assertEqual(price_first["actual_usd_oz"], None)
        self.assertEqual(price_first["status"], "RESEARCH_ONLY_UNCERTIFIED_ORIGIN_PRICE")
        self.assertEqual(price_first["forecast_usd_oz"],
                         4309.0*math.exp(price_first["pred_log_return_gold"]))

    def test_forward_requires_explicit_positive_origin_level(self):
        for bad in (0, -1, float("nan"), float("inf")):
            with self.assertRaisesRegex(ValueError,
                                        "ASOF_ORIGIN_REFERENCE_MUST_BE_FINITE_POSITIVE"):
                chhho.forecast_at_origin(self.bundle_without_future, TARGET, bad)


if __name__ == "__main__":
    unittest.main()
