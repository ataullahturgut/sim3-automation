import pandas as pd

from gold_r4 import Direction, EmergencyState, FastState, ReversalAlert, gvz_risk, three_month_direction
from gold_r4.tactical import fast_state


def test_three_month_direction_down():
    assert three_month_direction([-0.02, -0.03, 0.01]) == Direction.DOWN


def test_level_emergency_up_at_four_percent():
    s = EmergencyState()
    level, alert = s.update(pd.Timestamp("2025-01-02"), 104.0, 100.0)
    assert level == Direction.UP
    assert alert == ReversalAlert.OFF


def test_reversal_down_alert_after_up_shock():
    s = EmergencyState()
    s.update(pd.Timestamp("2025-01-02"), 104.0, 100.0)
    s.update(pd.Timestamp("2025-01-03"), 110.0, 100.0)
    _, alert = s.update(pd.Timestamp("2025-01-06"), 105.5, 100.0)
    assert alert == ReversalAlert.DOWN_ALERT


def test_gvz_caps():
    assert gvz_risk(25.0).cap == 1.0
    assert gvz_risk(27.0).cap == 0.5
    assert gvz_risk(31.0).cap == 0.25
    assert gvz_risk(31.0).panic is True


def test_fast_requires_two_persistent_days():
    closes = list(range(1, 23))
    assert fast_state(closes) == FastState.ROBUST_UP
