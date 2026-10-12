#!/usr/bin/env python3
"""R60 all-weekday H3 clock audit; NEVER alter frozen model/history.

Runnable from repository checkout (pandas, numpy). Re-derives D0/D1/D3
calendar, five macro source dates, hourly bar completion and COT release
mapping for every issue, with official CFTC-special schedule + documented
holiday exceptions. Existing R56/R59 scores must not be promoted from this
sidecar until a genuinely release-calendar-refit successor runs.
"""
from __future__ import annotations
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

AX = Path(__file__).resolve().parents[1]
NY = ZoneInfo("America/New_York")
TR = ZoneInfo("Europe/Istanbul")
COT_FEATURES = ("opt_mm_net opt_prod_net opt_swap_net opt_other_net d_opt_mm_net "
                "d_opt_prod_net opt_mm_z52 opt_prod_z52 opt_swap_z52 opt_other_z52 "
                "spec_hedger_gap spec_swap_gap fut_mm_net fut_prod_net").split()
# All dates below refer to COT *position reports*, not forecast-issue dates.
# Do not overstate the 2023/2025 dated news as an official archived CFTC API timestamp.
LATE_REPORT_RELEASE = {
    "2023-07-03": ("2023-07-07", "HISTORICAL_2023_GOLD_REPORT_DATED_JUL07"),
    "2025-07-01": ("2025-07-07", "HISTORICAL_2025_GOLD_REPORT_DATED_JUL07"),
    "2025-12-30": ("2026-01-05", "OFFICIAL_CFTC_2026"),
    "2026-06-16": ("2026-06-22", "OFFICIAL_CFTC_2026"),
    "2026-06-30": ("2026-07-06", "OFFICIAL_CFTC_2026"),
}
OUT = AX / "GOLD_R60_20261012_H3_ALL_WEEKDAYS_SOURCE_COT_RELEASE_CLOCK_1029.csv"


def release_utc(r: pd.Series, corrected: bool) -> tuple[pd.Timestamp, str]:
    special = r["cot_official_special_release_at_utc"]
    if pd.notna(special) and str(special).strip():
        return pd.to_datetime(special, utc=True), "CFTC_SPECIAL_OFFICIAL"
    k = r["report_date"].strftime("%Y-%m-%d")
    delayed = LATE_REPORT_RELEASE.get(k) if corrected else None
    release_date = pd.Timestamp(delayed[0]) if delayed else r["report_date"] + pd.Timedelta(days=3)
    release_at = pd.Timestamp(datetime.combine(release_date.date(), time(15, 30), tzinfo=NY))
    return release_at.tz_convert("UTC"), (delayed[1] if delayed else "FRIDAY_RULE_INFERRED")


def main() -> None:
    p = pd.read_csv(AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv")
    cot = pd.read_csv(AX / "GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv")
    prices = pd.read_csv(AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv")
    cross = pd.read_csv(AX / "GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv")
    ifbc = pd.read_csv(AX / "GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv")
    llrs = pd.read_csv(AX / "GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv")
    h = pd.read_csv(AX / "GOLD_R56_20261012_H3_FRIDAY_COT_DYNAMIC_HELIOS_V1_V5_931ROW_REPLAY.csv")
    stored = pd.read_csv(OUT)
    assert (len(p), len(h), len(cross), len(ifbc), len(llrs), len(stored)) == (1029, 931, 1029, 280, 332, 1029)
    p = p.sort_values("forecast_issue_date").reset_index(drop=True)
    for col in ("feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"):
        p[col] = pd.to_datetime(p[col])
    p["issued"] = p.forecast_issue_date.map(
        lambda t: pd.Timestamp(datetime.combine(t.date(), time(15), tzinfo=TR)).tz_convert("UTC"))
    daily = list(prices.date)
    by_price = {d: i for i, d in enumerate(daily)}
    by_cross = cross.set_index("forecast_issue_date")
    by_ifbc = ifbc.set_index("forecast_issue_date")
    by_llrs = llrs.set_index("forecast_issue_date")
    by_h = h.set_index("issue_date")
    prior = stored.set_index("issue_date")

    cot["report_date"] = pd.to_datetime(cot.report_date)
    for c in COT_FEATURES:
        cot[c] = pd.to_numeric(cot[c], errors="coerce")
    cot = cot.dropna(subset=COT_FEATURES).copy()
    cot["r56_release"] = [release_utc(r, False)[0] for _, r in cot.iterrows()]
    cor = [release_utc(r, True) for _, r in cot.iterrows()]
    cot["r60_release"] = [x[0] for x in cor]
    cot["r60_basis"] = [x[1] for x in cor]
    old = cot.sort_values("r56_release").reset_index(drop=True)
    corrected = cot.sort_values("r60_release").reset_index(drop=True)
    a = b = 0
    prev_old = prev_new = None
    records = []
    macro_cols = ["metal_source_date", "usd_source_date", "yield_source_date",
                  "ndx_source_date", "vix_source_date"]

    for row in p.itertuples(index=False):
        issue = row.forecast_issue_date.strftime("%Y-%m-%d")
        D0 = row.feature_cutoff_date.strftime("%Y-%m-%d")
        D3 = row.target_end_date_h3.strftime("%Y-%m-%d")
        j = by_price[D0]
        assert daily[j + 1] == issue and daily[j + 3] == D3
        m = by_cross.loc[issue]
        assert all(pd.notna(m[c]) and m[c] <= D0 for c in macro_cols)
        assert row.issued >= pd.Timestamp(datetime.combine(
            (row.feature_cutoff_date + pd.Timedelta(days=1)).date(),
            time(0), tzinfo=ZoneInfo("UTC")))
        if issue in by_ifbc.index:
            f = by_ifbc.loc[issue]
            assert pd.to_datetime(f.hourly_last_ts, utc=True) + pd.Timedelta(hours=1) <= row.issued
            assert f.cme_trade_date <= D0
        if issue in by_llrs.index:
            f = by_llrs.loc[issue]
            assert pd.to_datetime(f.hourly_source_ts, utc=True) + pd.Timedelta(hours=1) <= row.issued
        while a < len(old) and old.loc[a, "r56_release"] <= row.issued:
            prev_old = old.loc[a]
            a += 1
        while b < len(corrected) and corrected.loc[b, "r60_release"] <= row.issued:
            prev_new = corrected.loc[b]
            b += 1
        assert prev_old is not None and prev_new is not None
        assert row.issued >= prev_new.r60_release
        r60 = prior.loc[issue]
        assert r60.feature_cutoff_D0 == D0 and r60.native_H3_D3_target == D3
        assert r60.legacy_OPAL_COT_report == row.cot_report_date
        assert r60.R56_inferred_Friday_COT_report == prev_old.report_date.strftime("%Y-%m-%d")
        assert r60.corrected_release_COT_report == prev_new.report_date.strftime("%Y-%m-%d")
        assert r60.COT_report_release_clock_basis == prev_new.r60_basis
        assert r60.COT_report_release_utc == prev_new.r60_release.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        if issue in by_h.index:
            hc = by_h.loc[issue]
            assert hc.friday_COT_report == prev_old.report_date.strftime("%Y-%m-%d")
            assert hc.original_COT_report == row.cot_report_date
        records.append({
            "issue": issue,
            "day": row.forecast_issue_date.day_name(),
            "legacy_report": row.cot_report_date,
            "r56_report": prev_old.report_date.strftime("%Y-%m-%d"),
            "r60_report": prev_new.report_date.strftime("%Y-%m-%d"),
        })
    q = pd.DataFrame(records)
    assert len(q) == 1029
    assert int((q.r56_report != q.r60_report).sum()) == 5
    assert int((q.legacy_report != q.r60_report).sum()) == 410
    assert set(q.loc[q.r56_report != q.r60_report, "issue"]) == {
        "2023-07-07", "2025-07-07", "2026-01-05",
        "2026-06-22", "2026-07-06",
    }
    print(json.dumps({
        "status": "R60_ALL_WEEKDAYS_1029_ROW_PARITY_PASS",
        "source_target_rows": 1029, "original_R56_COT_rows": 931,
        "COT_source_clock_corrected_vs_R56_rows": 5,
        "calendar_report_diff_vs_legacy": 410,
        "by_day": q.groupby("day").size().to_dict(),
        "caveat": "The 15:00 TRT issue clock is assumed, not a certified archived live issue timestamp."
    }, indent=2))


if __name__ == "__main__":
    main()
