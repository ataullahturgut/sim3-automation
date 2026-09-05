from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "data_pipeline" / "macro_event_successor_v1_consensus_provider_audit.py"
spec = importlib.util.spec_from_file_location("macro_event_successor_v1_consensus_provider_audit", MOD_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_parse_number_units():
    assert mod.parse_number("175K") == 175.0
    assert mod.parse_number("4.2%") == 4.2
    assert mod.parse_number("0.3%") == 0.3
    assert mod.parse_number(56) == 56.0
    assert mod.parse_number("") is None


def test_select_event_exact_us_category_and_date():
    payload = [
        {
            "Country": "United States",
            "Category": "Non Farm Payrolls",
            "Event": "Non Farm Payrolls",
            "Date": "2024-09-06T12:30:00",
        },
        {
            "Country": "Canada",
            "Category": "Employment Change",
            "Event": "Employment Change",
            "Date": "2024-09-06T12:30:00",
        },
    ]
    row, n = mod.select_event(payload, "Non Farm Payrolls", "2024-09-06")
    assert n == 1
    assert row is payload[0]


def test_audit_row_keeps_forecast_and_teforecast_separate():
    row = {
        "CalendarId": "1",
        "Date": "2024-09-06T12:30:00",
        "Country": "United States",
        "Category": "Non Farm Payrolls",
        "Event": "Non Farm Payrolls",
        "Reference": "Aug",
        "ReferenceDate": "2024-08-31T00:00:00",
        "Source": "U.S. Bureau of Labor Statistics",
        "SourceURL": "https://www.bls.gov/",
        "Actual": "142K",
        "Previous": "89K",
        "Forecast": "160K",
        "TEForecast": "165K",
        "DateSpan": "0",
        "Importance": 3,
        "LastUpdate": "2024-09-06T12:31:00",
        "Revised": "",
        "Unit": "K",
        "Ticker": "NFP TCH",
        "Symbol": "NFP TCH",
    }
    sample = {
        "release_date": "2024-09-06",
        "reference_month": "2024-08",
    }
    out = mod.audit_row(row, mod.EVENTS["nfp"], sample, 160.0)
    assert out["structural_status"] == "PASS"
    assert out["forecast_and_teforecast_separately_identifiable"] is True
    assert out["teforecast_eligible_for_consensus"] is False
    assert out["last_update_used_as_consensus_timestamp"] is False
    assert out["licensed_raw_values_logged"] is False
    assert out["public_external_spot_check"]["difference_abs"] == 0.0
