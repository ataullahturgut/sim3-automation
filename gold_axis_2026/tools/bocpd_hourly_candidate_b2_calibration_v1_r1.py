from __future__ import annotations

import numpy as np
import pandas as pd

import bocpd_hourly_candidate_b2_calibration_v1 as cal


def build_returns_pre2025(prices: pd.DataFrame) -> pd.DataFrame:
    frame = prices.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").reset_index(drop=True).copy()
    frame["prev_ts"] = frame["bar_start_utc"].shift(1)
    frame["prev_value"] = frame["value"].shift(1)
    frame["elapsed_hours"] = (frame["bar_start_utc"] - frame["prev_ts"]).dt.total_seconds() / 3600.0
    frame["raw_log_return"] = np.log(frame["value"] / frame["prev_value"])
    frame = frame[np.isclose(frame["elapsed_hours"], 1.0, atol=1e-12)].copy()
    frame["bar_start_ny"] = frame["bar_start_utc"].dt.tz_convert(cal.base.NY_TZ)
    frame["bar_start_hour"] = frame["bar_start_ny"].dt.hour.astype(int)
    frame["local_date"] = frame["bar_start_ny"].dt.strftime("%Y-%m-%d")
    frame["available_at_utc"] = frame["bar_start_utc"] + pd.Timedelta(hours=1)

    actual_hours = sorted(frame[frame["bar_start_ny"].dt.year.isin([2023, 2024])]["bar_start_hour"].unique().tolist())
    if actual_hours != cal.base.EXPECTED_HOURS:
        raise RuntimeError(f"FORMATION_ELIGIBLE_HOUR_SET_MISMATCH:{actual_hours}")

    return frame[[
        "bar_start_utc",
        "bar_start_ny",
        "available_at_utc",
        "local_date",
        "bar_start_hour",
        "raw_log_return",
    ]].reset_index(drop=True)


def main() -> None:
    cal.base.build_returns = build_returns_pre2025
    cal.main()


if __name__ == "__main__":
    main()
