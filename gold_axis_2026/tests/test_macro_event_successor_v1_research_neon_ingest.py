from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DP = ROOT / "data_pipeline"
if str(DP) not in sys.path:
    sys.path.insert(0, str(DP))
MOD_PATH = DP / "macro_event_successor_v1_research_neon_ingest.py"
spec = importlib.util.spec_from_file_location("macro_event_successor_v1_research_neon_ingest", MOD_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_contract_r4_and_six_series():
    contract = mod.load_contract()
    assert contract["version"] == mod.EXPECTED_CONTRACT_VERSION
    assert contract["coverage_contract"]["known_excluded_reference_months"] == ["2020-08", "2025-10"]
    assert len(mod.ALL_SERIES_IDS) == 6


def test_release_timestamp_dst_and_standard_time():
    summer = mod.release_ts_utc(date(2026, 9, 4))
    winter = mod.release_ts_utc(date(2026, 1, 9))
    assert summer.isoformat() == "2026-09-04T12:30:00+00:00"
    assert winter.isoformat() == "2026-01-09T13:30:00+00:00"


def test_reference_month_dates():
    assert mod.ref_dates("2026-08") == ("2026-08-01", "2026-07-01")
    assert mod.ref_dates("2026-01") == ("2026-01-01", "2025-12-01")


def test_stable_hash_deterministic():
    a = mod.stable_hash({"b": 2, "a": 1})
    b = mod.stable_hash({"a": 1, "b": 2})
    assert a == b
    assert len(a) == 64


def test_expected_complete_month_count():
    months = mod.month_range(mod.START_REFERENCE, mod.END_REFERENCE)
    assert len(months) == 128
    expected = [m for m in months if m not in {"2020-08", "2025-10"}]
    assert len(expected) == mod.EXPECTED_COMPLETE_MONTHS == 126
