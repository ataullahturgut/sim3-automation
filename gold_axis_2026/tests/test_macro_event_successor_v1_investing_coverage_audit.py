from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "data_pipeline" / "macro_event_successor_v1_investing_coverage_audit.py"
spec = importlib.util.spec_from_file_location("macro_event_successor_v1_investing_coverage_audit", MOD_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_parse_number_units():
    assert mod.parse_number("55K") == 55.0
    assert mod.parse_number("4.1%") == 4.1
    assert mod.parse_number("0.3%") == 0.3
    assert mod.parse_number("-23.00K") == -23.0
    assert mod.parse_number("") is None


def test_parse_release_reference_previous_year():
    rel, ref = mod.parse_release_date_and_reference("Jan 09, 2026 (Dec)")
    assert rel.isoformat() == "2026-01-09"
    assert ref == "2025-12"


def test_parse_release_reference_same_year():
    rel, ref = mod.parse_release_date_and_reference("Sep 04, 2026 (Aug)")
    assert rel.isoformat() == "2026-09-04"
    assert ref == "2026-08"


def test_parse_history_rows_contract():
    html = """
    <tr><td>Sep 04, 2026 (Aug)</td><td>12:30</td><td>162.00K</td><td>55.00K</td><td>21.00K</td></tr>
    <tr><td>Aug 07, 2026 (Jul)</td><td>12:30</td><td>-23.00K</td><td>85.00K</td><td>20.00K</td></tr>
    """
    rows = mod.parse_history_rows(html)
    assert len(rows) == 2
    assert rows[0].reference_month == "2026-08"
    assert rows[0].forecast == 55.0
    assert rows[1].actual == -23.0


def test_month_range_count():
    months = mod.month_range("2016-01", "2026-08")
    assert len(months) == 128
    assert months[0] == "2016-01"
    assert months[-1] == "2026-08"
