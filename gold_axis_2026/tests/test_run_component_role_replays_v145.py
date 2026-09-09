from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "gold_axis_2026/tools/run_component_role_replays_v145.py"
SPEC = importlib.util.spec_from_file_location("role_replays", MODULE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def test_simple_august_uses_only_april_through_july():
    index = pd.date_range("2026-04-01", "2026-07-01", freq="MS")
    result = m.simple_august(pd.Series([100.0, 102.0, 101.0, 104.0], index=index))
    assert result["RANDOM_WALK"]["forecast"] == 104.0
    assert result["MOMENTUM_3M"]["future_information_violations"] == 0
    assert all(row["target_month"] == "2026-08" for row in result.values())


def test_context_replay_is_chronological_and_covers_20_months():
    dates = pd.date_range("2024-09-02", "2026-08-31", freq="B")
    ny = pd.DataFrame({"date": dates, "close": [2000.0 + i for i in range(len(dates))]})
    refs = {month: 2100.0 for month in m.PILOT_MONTHS}
    rows, evidence = m.context_replay(ny, refs)
    assert sorted({row["target_month"] for row in rows}) == m.PILOT_MONTHS
    assert set(evidence) == set(m.NY_IDS)
    assert all(item["pilot_cells_executed"] == 20 for item in evidence.values())
    assert all(item["determinism"] == "PASS" for item in evidence.values())


def test_bocpd_extension_fails_closed_without_august_exact_source():
    result = m.bocpd_extension_preflight()
    assert result["status"] == "BLOCKED_DATA"
    assert result["blocker_code"] == "CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND"
    assert result["output_computed"] is False


def test_no_write_sql_literals_present():
    text = MODULE.read_text().lower()
    for forbidden in ("insert into", "update observations", "delete from", "truncate ", "create table"):
        assert forbidden not in text

