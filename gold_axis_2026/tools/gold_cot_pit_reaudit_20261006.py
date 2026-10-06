from __future__ import annotations

import io
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from gold_cot_publication_pit_v1 import attach_cot_availability, latest_available_cot

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "COT_PIT_REAUDIT_OUT"
OUT.mkdir(exist_ok=True)

OLD_PANEL = AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv"
WGC = AX / "GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB = AX / "GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"

CFTC_CODE = "088691"
DATASETS = {
    "futures_only": "72hh-3qpy",
    "futures_options_combined": "kh3c-gbw2",
}


def norm_col(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")


def fetch_dataset(dataset_id):
    url = (
        f"https://publicreporting.cftc.gov/resource/{dataset_id}.csv"
        f"?cftc_contract_market_code={CFTC_CODE}&$limit=5000"
    )
    r = requests.get(url, timeout=90, headers={"User-Agent": "gold-cot-pit-audit/1.0"})
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), low_memory=False)
    df.columns = [norm_col(c) for c in df.columns]
    return df, {"url": url, "bytes": len(r.content), "rows": int(len(df))}


def gold_rows(df):
    aliases = {
        "prod_merc_positions_long": "prod_merc_positions_long_all",
        "prod_merc_positions_short": "prod_merc_positions_short_all",
        "other_rept_positions_long": "other_rept_positions_long_all",
        "other_rept_positions_short": "other_rept_positions_short_all",
    }
    df = df.copy()
    for src, dst in aliases.items():
        if dst not in df.columns and src in df.columns:
            df[dst] = df[src]

    date_col = (
        "report_date_as_yyyy_mm_dd"
        if "report_date_as_yyyy_mm_dd" in df.columns
        else "as_of_date_form_yyyy_mm_dd"
    )
    code = df["cftc_contract_market_code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    market = df.get("market_and_exchange_names", pd.Series([""] * len(df))).astype(str).str.upper()
    g = df[(code == CFTC_CODE) | market.str.contains("GOLD - COMMODITY EXCHANGE", regex=False)].copy()
    g["report_date"] = pd.to_datetime(g[date_col], errors="raise")
    g = g.sort_values("report_date").drop_duplicates("report_date", keep="last").reset_index(drop=True)
    return g


def feature_state(fut, com):
    keys = [
        "report_date",
        "open_interest_all",
        "prod_merc_positions_long_all",
        "prod_merc_positions_short_all",
        "swap_positions_long_all",
        "swap_positions_short_all",
        "m_money_positions_long_all",
        "m_money_positions_short_all",
        "other_rept_positions_long_all",
        "other_rept_positions_short_all",
    ]
    ff = fut[keys].copy().rename(columns={k: f"f_{k}" for k in keys if k != "report_date"})
    cc = com[keys].copy().rename(columns={k: f"c_{k}" for k in keys if k != "report_date"})
    x = ff.merge(cc, on="report_date", how="inner", validate="one_to_one")
    for c in x.columns:
        if c != "report_date":
            x[c] = pd.to_numeric(x[c], errors="raise").astype(float)

    f_oi = x["f_open_interest_all"].replace(0, np.nan)
    c_oi = x["c_open_interest_all"].replace(0, np.nan)
    cohorts = {
        "mm": ("m_money_positions_long_all", "m_money_positions_short_all"),
        "prod": ("prod_merc_positions_long_all", "prod_merc_positions_short_all"),
        "swap": ("swap_positions_long_all", "swap_positions_short_all"),
        "other": ("other_rept_positions_long_all", "other_rept_positions_short_all"),
    }
    for short, (lc, sc) in cohorts.items():
        fnet = x[f"f_{lc}"] - x[f"f_{sc}"]
        cnet = x[f"c_{lc}"] - x[f"c_{sc}"]
        x[f"opt_{short}_net"] = (cnet - fnet) / c_oi
        x[f"fut_{short}_net"] = fnet / f_oi

    x["d_opt_mm_net"] = x["opt_mm_net"].diff()
    x["d_opt_prod_net"] = x["opt_prod_net"].diff()
    x["spec_hedger_gap"] = x["opt_mm_net"] - x["opt_prod_net"]
    x["spec_swap_gap"] = x["opt_mm_net"] - x["opt_swap_net"]
    for short in ["mm", "prod", "swap", "other"]:
        s = x[f"opt_{short}_net"]
        mu = s.shift(1).rolling(52, min_periods=26).mean()
        sd = s.shift(1).rolling(52, min_periods=26).std(ddof=0)
        x[f"opt_{short}_z52"] = (s - mu) / sd.replace(0, np.nan)

    keep = [
        "report_date",
        "opt_mm_net", "opt_prod_net", "opt_swap_net", "opt_other_net",
        "d_opt_mm_net", "d_opt_prod_net",
        "opt_mm_z52", "opt_prod_z52", "opt_swap_z52", "opt_other_z52",
        "spec_hedger_gap", "spec_swap_gap", "fut_mm_net", "fut_prod_net",
    ]
    x = x[keep].copy()
    x = attach_cot_availability(x, "report_date")
    return x.sort_values("report_date").reset_index(drop=True)


def audit_old_opal(cot):
    p = pd.read_csv(OLD_PANEL)
    p["feature_cutoff_date"] = pd.to_datetime(p["feature_cutoff_date"], errors="raise")
    p["cot_report_date"] = pd.to_datetime(p["cot_report_date"], errors="raise")
    # Legacy H3 feature clock is 16:00 America/New_York.
    p["feature_cutoff_at_ny"] = pd.to_datetime(
        p["feature_cutoff_date"].dt.strftime("%Y-%m-%d") + " 16:00"
    ).dt.tz_localize("America/New_York")
    p["feature_cutoff_at_utc"] = p["feature_cutoff_at_ny"].dt.tz_convert("UTC")

    avail = cot[["report_date", "cot_available_at_utc", "cot_availability_reason"]].copy()
    p = p.merge(avail, left_on="cot_report_date", right_on="report_date", how="left", validate="many_to_one")
    if p["cot_available_at_utc"].isna().any():
        raise RuntimeError("OLD_OPAL_REPORT_NOT_FOUND_IN_REBUILT_COT")

    p["proven_early_use"] = p["feature_cutoff_at_utc"] < pd.to_datetime(p["cot_available_at_utc"], utc=True)

    latest_rows = []
    for r in p.itertuples(index=False):
        cr = latest_available_cot(cot, r.feature_cutoff_at_utc)
        latest_rows.append(None if cr is None else pd.Timestamp(cr["report_date"]))
    p["latest_governed_report_date"] = latest_rows
    p["report_should_change"] = (
        p["latest_governed_report_date"].notna()
        & (p["cot_report_date"] != p["latest_governed_report_date"])
    )

    early = p[p["proven_early_use"]].copy()
    early.to_csv(OUT / "old_opal_proven_early_rows.csv", index=False)
    p.to_csv(OUT / "old_opal_pit_reaudit_rows.csv", index=False)
    return p, early


def session_map(cot):
    frames = []
    for path in [WGC, SOB]:
        q = pd.read_csv(path)
        q = q[q["final_trainable"].astype(str).str.lower().eq("true")].copy()
        frames.append(q)
    t = pd.concat(frames, ignore_index=True)
    t["start_utc"] = pd.to_datetime(t["start_utc"], utc=True)

    rows = []
    for r in t.itertuples(index=False):
        cr = latest_available_cot(cot, r.start_utc)
        rows.append({
            "label_date": r.label_date,
            "year": int(r.year),
            "partition": r.partition,
            "window": r.window,
            "target_start_utc": r.start_utc.isoformat(),
            "cot_report_date": None if cr is None else pd.Timestamp(cr["report_date"]).date().isoformat(),
            "cot_available_at_utc": None if cr is None else pd.Timestamp(cr["cot_available_at_utc"]).isoformat(),
            "cot_availability_reason": None if cr is None else cr["cot_availability_reason"],
            "cot_age_days_at_start": None if cr is None else float(
                (r.start_utc - pd.Timestamp(cr["cot_available_at_utc"])).total_seconds() / 86400.0
            ),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "v5_session_cot_availability_map.csv", index=False)
    return out


def main():
    raw = {}
    meta = {}
    for name, did in DATASETS.items():
        z, m = fetch_dataset(did)
        raw[name] = gold_rows(z)
        meta[name] = m

    fdates = set(raw["futures_only"]["report_date"])
    cdates = set(raw["futures_options_combined"]["report_date"])
    if fdates != cdates:
        raise RuntimeError(
            f"CFTC_FUT_COM_REPORT_DATE_MISMATCH only_fut={len(fdates-cdates)} only_comb={len(cdates-fdates)}"
        )

    state = feature_state(raw["futures_only"], raw["futures_options_combined"])
    state.to_csv(OUT / "cot_gold_pit_state_raw_rebuilt.csv", index=False)
    state[[
        "report_date", "cot_available_at_ny", "cot_available_at_utc",
        "cot_availability_reason", "cot_official_special_release_at_ny",
        "cot_official_special_release_at_utc",
    ]].to_csv(OUT / "cot_publication_calendar.csv", index=False)

    old, early = audit_old_opal(state)
    smap = session_map(state)

    by_year = (
        early.assign(year=pd.to_datetime(early["feature_cutoff_date"]).dt.year)
        .groupby("year").size().to_dict()
    )
    change_by_year = (
        old[old["report_should_change"]]
        .assign(year=lambda d: pd.to_datetime(d["feature_cutoff_date"]).dt.year)
        .groupby("year").size().to_dict()
    )
    session_counts = (
        smap.groupby(["year", "partition", "window"])
        .agg(rows=("label_date", "size"), cot_mapped=("cot_report_date", lambda s: int(s.notna().sum())))
        .reset_index()
        .to_dict("records")
    )

    summary = {
        "status": "COT_PIT_REAUDIT_COMPLETE",
        "source": "CFTC_PUBLIC_REPORTING_API",
        "cftc_code": CFTC_CODE,
        "transport_meta": meta,
        "governance": {
            "default": "report_date + 7 calendar days at 15:30 America/New_York",
            "override": "if official documented delayed publication is later, use official delayed date at 15:30 ET",
            "normal_release_reference": "CFTC states COT reports are usually released Friday at 15:30 ET",
            "special_authorities": [
                "CFTC Historical Special Announcements — 2023 ION backlog",
                "CFTC Dec. 9 2025 accelerated COT backlog schedule",
            ],
        },
        "rebuilt_report_rows": int(len(state)),
        "rebuilt_report_first": str(state["report_date"].min().date()),
        "rebuilt_report_last": str(state["report_date"].max().date()),
        "old_opal_rows": int(len(old)),
        "proven_early_use_rows": int(len(early)),
        "proven_early_use_by_feature_year": {str(k): int(v) for k, v in by_year.items()},
        "old_rows_whose_selected_report_changes_under_governed_pit": int(old["report_should_change"].sum()),
        "changed_report_by_feature_year": {str(k): int(v) for k, v in change_by_year.items()},
        "v5_session_cot_mapping": session_counts,
        "pass_condition": "proven_early_use_rows must reproduce the audited lower-bound issue; clean OPAL/session models must use cot_available_at_utc as-of target/feature cutoff",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
