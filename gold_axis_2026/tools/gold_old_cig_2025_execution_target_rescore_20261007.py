from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"

V5 = AX / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT = AX / "GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA = AX / "GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
SAGE_PRED = AX / "GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
RULEFLOW_TOOL = AX / "tools" / "gold_h3_ruleflow_v3_pre2025_backcast.py"
XAU15 = AX / "GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"

OUT_JSON = AX / "GOLD_OLD_CIG_2025_EXECUTION_TARGET_RESCORE_2026-10-07.json"
OUT_CSV = AX / "GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv"
OUT_MD = AX / "GOLD_OLD_CIG_2025_EXECUTION_TARGET_RESCORE_RESULT_2026-10-07.md"

def bseries(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])

def safe_acc(x: pd.DataFrame, col: str) -> dict:
    q = x[x[col].notna()].copy()
    if q.empty:
        return {"n": 0, "correct": 0, "accuracy": None}
    correct = (q["consensus_pred"].astype(int) == q[col].astype(int))
    return {"n": int(len(q)), "correct": int(correct.sum()), "accuracy": float(correct.mean())}

def side_acc(x: pd.DataFrame, col: str, side: int) -> dict:
    q = x[(x[col].notna()) & (x["consensus_pred"] == side)].copy()
    if q.empty:
        return {"n": 0, "correct": 0, "accuracy": None}
    c = q["consensus_pred"].astype(int).eq(q[col].astype(int))
    return {"n": int(len(q)), "correct": int(c.sum()), "accuracy": float(c.mean())}

def main():
    v5 = pd.read_csv(V5)
    r = pd.read_csv(RIFT)
    g = pd.read_csv(VEGA)
    for df in (v5, r, g):
        df["forecast_issue_date"] = pd.to_datetime(df["forecast_issue_date"]).dt.normalize()
        df["feature_cutoff_date"] = pd.to_datetime(df["feature_cutoff_date"]).dt.normalize()

    v5 = v5[v5["forecast_issue_date"].dt.year.eq(2025)].copy()
    r = r[r["forecast_issue_date"].dt.year.eq(2025)].copy()
    g = g[g["forecast_issue_date"].dt.year.eq(2025)].copy()

    base = v5[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","y_up","p_helios_v5_dce"]].copy()
    base["v5_pred"] = (pd.to_numeric(base["p_helios_v5_dce"]) >= 0.5).astype(int)

    rr = r[["feature_cutoff_date","forecast_issue_date","p_rift"]].copy()
    rr["rift_pred"] = (pd.to_numeric(rr["p_rift"]) >= 0.5).astype(int)
    vv = g[["feature_cutoff_date","forecast_issue_date","p_vega"]].copy()
    vv["vega_pred"] = (pd.to_numeric(vv["p_vega"]) >= 0.5).astype(int)

    base = base.merge(rr[["feature_cutoff_date","forecast_issue_date","rift_pred"]],
                      on=["feature_cutoff_date","forecast_issue_date"], how="left", validate="one_to_one")
    base = base.merge(vv[["feature_cutoff_date","forecast_issue_date","vega_pred"]],
                      on=["feature_cutoff_date","forecast_issue_date"], how="left", validate="one_to_one")

    # Reuse the frozen historical SAGE action identity rather than recreating
    # actions from later retrospective IFBC/LLRS backfills.  The V2 freeze
    # explicitly prohibits a later backfill from creating a historical action.
    sage = pd.read_csv(SAGE_PRED, low_memory=False)
    sage["forecast_issue_date"] = pd.to_datetime(sage["forecast_issue_date"], errors="coerce").dt.normalize()
    sage["feature_cutoff_date"] = pd.to_datetime(sage["feature_cutoff_date"], errors="coerce").dt.normalize()
    sage25 = sage[
        sage["forecast_issue_date"].dt.year.eq(2025)
        & bseries(sage["ocs_candidate"])
    ][["feature_cutoff_date","forecast_issue_date"]].drop_duplicates()
    sage_keys = set(map(tuple, sage25[["feature_cutoff_date","forecast_issue_date"]].to_numpy()))
    base["sage_exception"] = [
        (a,b) in sage_keys for a,b in zip(base["feature_cutoff_date"], base["forecast_issue_date"])
    ]

    # Reconstruct the frozen RuleFlow V3-TG 2025 QA identity with the original
    # producer functions.  RuleFlow's event/action date is the H3 feature
    # cutoff date, not the following forecast-issue date.
    spec = importlib.util.spec_from_file_location("ruleflow_pre2025", RULEFLOW_TOOL)
    rfmod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(rfmod)
    ev = rfmod.build_event_table()
    z, dpanel = rfmod.load()
    rf25 = rfmod.score_year(ev, z, dpanel, 2025)
    rf25 = rf25[bseries(rf25["v3_candidate"])].copy()
    rf_dates = set(pd.to_datetime(rf25["date"], errors="coerce").dt.normalize().dropna().tolist())
    base["ruleflow_exception"] = base["feature_cutoff_date"].isin(rf_dates)

    # The old combined expert flips V5 on the union.  Identity checks below
    # must reproduce the published 171/248 and the old CIG 218 consensus rows.
    base["combined_exception"] = base["sage_exception"] | base["ruleflow_exception"]
    base["sage_ruleflow_pred"] = np.where(base["combined_exception"], 1-base["v5_pred"], base["v5_pred"]).astype(int)

    base["consensus"] = (
        base["sage_ruleflow_pred"].eq(base["v5_pred"])
        & base["v5_pred"].eq(base["rift_pred"])
        & base["v5_pred"].eq(base["vega_pred"])
    )
    base["consensus_pred"] = np.where(base["consensus"], base["v5_pred"], np.nan)

    # Identity checks against published H3 / CIG diagnostics.
    v5_h3_correct = int(base["v5_pred"].eq(base["y_up"].astype(int)).sum())
    combined_h3_correct = int(base["sage_ruleflow_pred"].eq(base["y_up"].astype(int)).sum())
    consensus_n = int(base["consensus"].sum())

    # Raw 15m execution targets. Turkey is UTC+3 throughout 2025.
    q = pd.read_csv(XAU15, low_memory=False)
    need = {"dt_utc","open","close"}
    if not need.issubset(q.columns):
        raise RuntimeError(f"XAU15_SCHEMA_FAIL:{q.columns.tolist()}")
    q["ts"] = pd.to_datetime(q["dt_utc"], utc=True, errors="raise")
    q["open"] = pd.to_numeric(q["open"], errors="coerce")
    q["close"] = pd.to_numeric(q["close"], errors="coerce")
    q = q[(q["ts"] >= "2024-12-20") & (q["ts"] < "2026-01-10")].dropna(subset=["ts","open","close"]).copy()
    q = q.sort_values("ts").drop_duplicates("ts", keep="last").set_index("ts")

    exact_0600_dates = sorted({t.date() for t in q.index if t.hour == 6 and t.minute == 0})

    def point_open(ts: pd.Timestamp):
        try:
            return float(q.at[ts, "open"])
        except KeyError:
            return np.nan

    def point_close(ts: pd.Timestamp):
        try:
            return float(q.at[ts, "close"])
        except KeyError:
            return np.nan

    def next_eligible_date(d):
        for x in exact_0600_dates:
            if x > d:
                return x
        return None

    rows = []
    for _, z in base[base["consensus"]].sort_values("forecast_issue_date").iterrows():
        d = z["forecast_issue_date"].date()
        day_start = pd.Timestamp(f"{d} 06:00:00", tz="UTC")       # 09:00 TRT
        day_endbar = pd.Timestamp(f"{d} 13:45:00", tz="UTC")      # closes 17:00 TRT
        ov_start = pd.Timestamp(f"{d} 14:00:00", tz="UTC")        # 17:00 TRT
        nd = next_eligible_date(d)
        ov_endbar = pd.Timestamp(f"{nd} 05:45:00", tz="UTC") if nd else pd.NaT  # closes 09:00 TRT

        p09 = point_open(day_start)
        p17 = point_close(day_endbar)
        po17 = point_open(ov_start)
        pnext09 = point_close(ov_endbar) if pd.notna(ov_endbar) else np.nan

        day_ret = p17/p09 - 1 if np.isfinite(p09) and np.isfinite(p17) and p09 > 0 else np.nan
        ov_ret = pnext09/po17 - 1 if np.isfinite(po17) and np.isfinite(pnext09) and po17 > 0 else np.nan

        rows.append({
            "forecast_issue_date": z["forecast_issue_date"].date().isoformat(),
            "feature_cutoff_date": z["feature_cutoff_date"].date().isoformat(),
            "consensus_pred": int(z["consensus_pred"]),
            "consensus_direction": "UP" if int(z["consensus_pred"]) == 1 else "DOWN",
            "sage_exception": bool(z["sage_exception"]),
            "ruleflow_exception": bool(z["ruleflow_exception"]),
            "day_09_price": p09,
            "day_17_price": p17,
            "day_return": day_ret,
            "day_actual": (1 if day_ret > 0 else 0) if np.isfinite(day_ret) else np.nan,
            "overnight_17_price": po17,
            "overnight_next_date": nd.isoformat() if nd else None,
            "overnight_09_price": pnext09,
            "overnight_return": ov_ret,
            "overnight_actual": (1 if ov_ret > 0 else 0) if np.isfinite(ov_ret) else np.nan,
        })
    out = pd.DataFrame(rows)
    out["day_correct"] = np.where(out["day_actual"].notna(), out["consensus_pred"].eq(out["day_actual"]), np.nan)
    out["overnight_correct"] = np.where(out["overnight_actual"].notna(), out["consensus_pred"].eq(out["overnight_actual"]), np.nan)

    day = safe_acc(out, "day_actual")
    ov = safe_acc(out, "overnight_actual")
    both = out[out["day_actual"].notna() & out["overnight_actual"].notna()].copy()
    both_correct = int((both["day_correct"].eq(True) & both["overnight_correct"].eq(True)).sum()) if len(both) else 0

    summary = {
        "status": "COMPLETE",
        "identity": "OLD_CIG_D1_V1_2025_RESCORED_ON_EXECUTION_TARGETS",
        "signal_contract": {
            "experts": ["SAGE V2 + RuleFlow V3-TG", "HELIOS V5-DCE", "RIFT", "VEGA"],
            "rule": "4/4 same direction -> consensus; otherwise UNCERTAIN",
            "no_retraining": True,
        },
        "reconstruction_qa": {
            "2025_h3_rows": int(len(base)),
            "published_expected_h3_rows": 248,
            "v5_h3_correct_reconstructed": v5_h3_correct,
            "published_expected_v5_h3_correct": 165,
            "sage_ruleflow_h3_correct_reconstructed": combined_h3_correct,
            "published_expected_sage_ruleflow_h3_correct": 171,
            "consensus_n_reconstructed": consensus_n,
            "published_expected_consensus_n": 218,
            "sage_exception_n": int(base["sage_exception"].sum()),
            "ruleflow_exception_n": int(base["ruleflow_exception"].sum()),
            "sage_action_keys_2025": [
                {"feature_cutoff_date": a.date().isoformat(), "forecast_issue_date": b.date().isoformat()}
                for a,b in sorted(sage_keys)
            ],
            "ruleflow_action_dates_2025": [d.date().isoformat() for d in sorted(rf_dates)],
            "pass": bool(
                len(base) == 248
                and v5_h3_correct == 165
                and combined_h3_correct == 171
                and consensus_n == 218
            )
        },
        "targets": {
            "DAY_09_17_TRT": {
                **day,
                "up_signals": side_acc(out, "day_actual", 1),
                "down_signals": side_acc(out, "day_actual", 0),
                "causal_use": "NOT_EXECUTABLE_AT_09_TRT",
                "reason": "Old CIG governed issue deadline is 08:00 America/New_York, approximately 15:00/16:00 Europe/Istanbul in 2025; this is after the 09:00 target origin.",
            },
            "OVERNIGHT_17_NEXT09_TRT": {
                **ov,
                "up_signals": side_acc(out, "overnight_actual", 1),
                "down_signals": side_acc(out, "overnight_actual", 0),
                "causal_use": "CLOCK_COMPATIBLE",
                "reason": "Old CIG governed 08:00 New York deadline occurs before 17:00 Europe/Istanbul in 2025.",
            }
        },
        "joint": {
            "both_targets_observed_n": int(len(both)),
            "both_correct_n": both_correct,
            "both_correct_rate": float(both_correct/len(both)) if len(both) else None,
            "day_and_overnight_same_actual_direction_rate": float((both["day_actual"].astype(int) == both["overnight_actual"].astype(int)).mean()) if len(both) else None,
        },
        "price_semantics": {
            "day_start": "09:00 Europe/Istanbul = 06:00 UTC 15m bar OPEN",
            "day_end": "17:00 Europe/Istanbul = 13:45 UTC 15m bar CLOSE",
            "overnight_start": "17:00 Europe/Istanbul = 14:00 UTC 15m bar OPEN",
            "overnight_end": "next eligible 09:00 Europe/Istanbul = 05:45 UTC 15m bar CLOSE",
            "turkey_offset": "UTC+3 fixed",
        }
    }

    if not summary["reconstruction_qa"]["pass"]:
        summary["status"] = "FAIL_IDENTITY_RECONSTRUCTION"
        OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")
        raise RuntimeError("OLD_CIG_IDENTITY_RECONSTRUCTION_FAIL " + json.dumps(summary["reconstruction_qa"]))

    out.to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")

    def pct(v):
        return "NA" if v is None else f"{100*v:.2f}%"
    md = f"""# OLD CIG-D1 2025 — EXECUTION-TARGET RESCORE RESULT

**Status:** COMPLETE / RETROSPECTIVE DIAGNOSTIC  
**Identity:** old CIG-D1 V1 unchanged; no retraining or new consensus selection.

## Identity reconstruction

- H3 rows: **{len(base)} / 248**
- V5 H3 correct: **{v5_h3_correct} / 248** (expected 165)
- SAGE V2 + RuleFlow V3-TG H3 correct: **{combined_h3_correct} / 248** (expected 171)
- Old 4/4 consensus rows: **{consensus_n}** (expected 218)
- Reconstruction QA: **PASS**

## Rescore on the two current execution targets

| Target | N | Correct | Direction accuracy | Clock usability |
|---|---:|---:|---:|---|
| 09:00 -> 17:00 Europe/Istanbul | {day['n']} | {day['correct']} | **{pct(day['accuracy'])}** | **NOT executable at 09:00** |
| 17:00 -> next eligible 09:00 Europe/Istanbul | {ov['n']} | {ov['correct']} | **{pct(ov['accuracy'])}** | **Clock-compatible** |

### Signal-side detail

DAY 09->17:
- old-consensus UP calls: {summary['targets']['DAY_09_17_TRT']['up_signals']['correct']}/{summary['targets']['DAY_09_17_TRT']['up_signals']['n']} = **{pct(summary['targets']['DAY_09_17_TRT']['up_signals']['accuracy'])}**
- old-consensus DOWN calls: {summary['targets']['DAY_09_17_TRT']['down_signals']['correct']}/{summary['targets']['DAY_09_17_TRT']['down_signals']['n']} = **{pct(summary['targets']['DAY_09_17_TRT']['down_signals']['accuracy'])}**

OVERNIGHT 17->09:
- old-consensus UP calls: {summary['targets']['OVERNIGHT_17_NEXT09_TRT']['up_signals']['correct']}/{summary['targets']['OVERNIGHT_17_NEXT09_TRT']['up_signals']['n']} = **{pct(summary['targets']['OVERNIGHT_17_NEXT09_TRT']['up_signals']['accuracy'])}**
- old-consensus DOWN calls: {summary['targets']['OVERNIGHT_17_NEXT09_TRT']['down_signals']['correct']}/{summary['targets']['OVERNIGHT_17_NEXT09_TRT']['down_signals']['n']} = **{pct(summary['targets']['OVERNIGHT_17_NEXT09_TRT']['down_signals']['accuracy'])}**

## Critical interpretation

The DAY score is only a **retrospective alignment diagnostic**. The old CIG signal was governed for **08:00 America/New_York**, which is about **15:00/16:00 Türkiye time** in 2025. Therefore it could not have been known at the 09:00 origin of the new DAY target.

The OVERNIGHT target is different: the governed old-CIG issue deadline occurs before 17:00 Türkiye time, so its 17:00->next-09:00 rescore is clock-compatible as a historical execution diagnostic.

Neither result is prospective OOS evidence. No 2025 outcome was used here to alter the old consensus membership or direction.
"""
    OUT_MD.write_text(md)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
