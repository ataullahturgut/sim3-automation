from pathlib import Path
import sys

import pandas as pd

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import audit_august_2026_exact_target_v146 as audit


def test_direction():
    assert audit.direction(1) == 1
    assert audit.direction(0) == 0
    assert audit.direction(-1) == -1


def test_prefix_check_exact_and_fail_closed():
    idx = pd.to_datetime(["2016-01-01", "2026-07-01"])
    core = pd.DataFrame({"gold_monthly": [100.0, 200.0]}, index=idx)
    assert audit.exact_prefix_check(core, pd.Series([100.0, 200.0], index=idx))["status"] == "PASS"
    assert audit.exact_prefix_check(core, pd.Series([100.0, 200.4], index=idx))["status"] == "PASS"
    assert audit.exact_prefix_check(core, pd.Series([100.0, 201.0], index=idx))["status"] == "FAIL"
