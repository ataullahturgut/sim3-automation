from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

# Governance:
# - Default remains intentionally conservative: report-date + 7 calendar days at
#   15:30 America/New_York.
# - Where CFTC officially documented a publication delay beyond that buffer,
#   the actual announced publication date at the normal COT release clock
#   (15:30 ET) overrides the default.
# - If an announced publication is earlier than the default +7d buffer, the
#   conservative default is retained.
#
# Official sources:
# CFTC COT Release Schedule: normal release clock = 15:30 ET.
# CFTC Historical Special Announcements: 2023 ION backlog.
# CFTC Dec. 9 2025 revised backlog schedule: 2025 appropriations lapse.

OFFICIAL_DELAY_RELEASE_DATES = {
    # 2023 ION incident. Keys are COT report/as-of dates.
    date(2023, 1, 31): date(2023, 2, 24),
    date(2023, 2, 7): date(2023, 3, 3),
    date(2023, 2, 14): date(2023, 3, 8),
    date(2023, 2, 21): date(2023, 3, 10),
    date(2023, 2, 28): date(2023, 3, 14),
    date(2023, 3, 7): date(2023, 3, 16),
    date(2023, 3, 14): date(2023, 3, 21),

    # 2025 federal appropriations lapse / final accelerated schedule announced
    # Dec. 9, 2025.
    date(2025, 9, 30): date(2025, 11, 19),
    date(2025, 10, 7): date(2025, 11, 21),
    date(2025, 10, 14): date(2025, 11, 25),
    date(2025, 10, 21): date(2025, 12, 2),
    date(2025, 10, 28): date(2025, 12, 5),
    date(2025, 11, 4): date(2025, 12, 9),
    date(2025, 11, 10): date(2025, 12, 10),
    date(2025, 11, 18): date(2025, 12, 12),
    date(2025, 11, 25): date(2025, 12, 15),
    date(2025, 12, 2): date(2025, 12, 17),
    date(2025, 12, 9): date(2025, 12, 19),
    date(2025, 12, 16): date(2025, 12, 23),
    date(2025, 12, 23): date(2025, 12, 29),
}

# Informational exception: Jan. 2025 Carter National Day of Mourning.
# The announced Jan. 13 release is still earlier than the governed +7-day
# conservative buffer for the Jan. 7 report, so it does not move governed
# availability earlier.
OFFICIAL_EARLY_WITHIN_BUFFER = {
    date(2025, 1, 7): date(2025, 1, 13),
}


def _ny_1530(d: date) -> pd.Timestamp:
    return pd.Timestamp(datetime(d.year, d.month, d.day, 15, 30, tzinfo=NY))


def governed_cot_available_at(report_date) -> pd.Timestamp:
    rd = pd.Timestamp(report_date).date()
    conservative = _ny_1530(rd + timedelta(days=7))
    delayed_date = OFFICIAL_DELAY_RELEASE_DATES.get(rd)
    if delayed_date is None:
        return conservative
    official = _ny_1530(delayed_date)
    return max(conservative, official)


def official_special_release_at(report_date):
    rd = pd.Timestamp(report_date).date()
    d = OFFICIAL_DELAY_RELEASE_DATES.get(rd) or OFFICIAL_EARLY_WITHIN_BUFFER.get(rd)
    return None if d is None else _ny_1530(d)


def availability_reason(report_date) -> str:
    rd = pd.Timestamp(report_date).date()
    if rd in OFFICIAL_DELAY_RELEASE_DATES:
        return "OFFICIAL_DELAY_OVERRIDE"
    if rd in OFFICIAL_EARLY_WITHIN_BUFFER:
        return "DEFAULT_7D_CONSERVATIVE_OFFICIAL_RELEASE_EARLIER"
    return "DEFAULT_7D_CONSERVATIVE"


def attach_cot_availability(df: pd.DataFrame, report_col: str = "report_date") -> pd.DataFrame:
    out = df.copy()
    out[report_col] = pd.to_datetime(out[report_col], errors="raise")
    out["cot_available_at_ny"] = out[report_col].map(governed_cot_available_at)
    out["cot_available_at_utc"] = pd.to_datetime(out["cot_available_at_ny"], utc=True)
    out["cot_availability_reason"] = out[report_col].map(availability_reason)
    out["cot_official_special_release_at_ny"] = out[report_col].map(official_special_release_at)
    out["cot_official_special_release_at_utc"] = pd.to_datetime(
        out["cot_official_special_release_at_ny"], utc=True, errors="coerce"
    )
    return out


def latest_available_cot(cot: pd.DataFrame, as_of) -> pd.Series | None:
    as_of_utc = pd.Timestamp(as_of)
    if as_of_utc.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")
    as_of_utc = as_of_utc.tz_convert("UTC")
    q = cot[pd.to_datetime(cot["cot_available_at_utc"], utc=True) <= as_of_utc]
    if q.empty:
        return None
    return q.sort_values(["cot_available_at_utc", "report_date"]).iloc[-1]
