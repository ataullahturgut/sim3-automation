from __future__ import annotations

import pandas as pd

from piyasa_contract import filter_history_timeframe, gvz_regime, latest_completed_daily_row, price_delta


def _history() -> pd.DataFrame:
    dates = pd.date_range("2025-09-01", "2026-09-01", freq="D")
    return pd.DataFrame({"date": dates, "close": range(1, len(dates) + 1)})


def test_latest_completed_daily_excludes_current_utc_date() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-08-31", "2026-09-01"]),
            "close": [100.0, 999.0],
        }
    )
    row = latest_completed_daily_row(frame, now_utc=pd.Timestamp("2026-09-01T14:00:00Z"))
    assert row is not None
    assert pd.Timestamp(row["date"]).date().isoformat() == "2026-08-31"
    assert float(row["close"]) == 100.0


def test_only_approved_timeframes_are_allowed() -> None:
    frame = _history()
    for code in ("1A", "3A", "6A", "1Y"):
        out = filter_history_timeframe(frame, code)
        assert not out.empty
    try:
        filter_history_timeframe(frame, "1G")
    except ValueError as exc:
        assert "UNAPPROVED_TIMEFRAME" in str(exc)
    else:
        raise AssertionError("1G must remain blocked")


def test_price_delta_is_plain_comparison_not_signal() -> None:
    d = price_delta(105.0, 100.0)
    assert d is not None
    assert d.absolute == 5.0
    assert round(d.percent, 8) == 5.0
    assert price_delta(None, 100.0) is None


def test_gvz_regime_uses_frozen_thresholds_only() -> None:
    assert gvz_regime(20.0, full_max=25.0, half_max=30.0) == "NORMAL"
    assert gvz_regime(27.0, full_max=25.0, half_max=30.0) == "ELEVATED"
    assert gvz_regime(31.0, full_max=25.0, half_max=30.0) == "PANIC"
