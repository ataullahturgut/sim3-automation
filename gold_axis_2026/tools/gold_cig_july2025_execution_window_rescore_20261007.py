from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
RAW = AX / "GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
SIGNALS = AX / "GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
OUT = AX / "CIG_JULY2025_EXECUTION_WINDOW_RESCORE_OUT"
OUT.mkdir(exist_ok=True)

START = "2025-07-01"
END = "2025-07-31"
TZ_TR = "Europe/Istanbul"
TZ_NY = "America/New_York"


def bal_acc(actual, pred):
    if not actual:
        return None
    a = pd.Series(actual)
    p = pd.Series(pred)
    vals = []
    for cls in ["UP", "DOWN"]:
        m = a.eq(cls)
        if m.sum():
            vals.append(float((p[m] == cls).mean()))
    return float(np.mean(vals)) if vals else None


def pct(x):
    return "NA" if x is None or pd.isna(x) else f"{100*x:.2f}%"


def main():
    sig = pd.read_csv(SIGNALS)
    sig = sig[(sig.issue_date >= START) & (sig.issue_date <= END)].copy()
    sig["consensus"] = sig["consensus"].astype(str).str.lower().eq("true")
    sig["state"] = np.where(~sig.consensus, "UNCERTAIN",
                            np.where(pd.to_numeric(sig.v5, errors="coerce").eq(1), "UP", "DOWN"))

    raw = pd.read_csv(RAW, usecols=["dt_utc", "open", "close"])
    raw["dt_utc"] = pd.to_datetime(raw["dt_utc"], utc=True)
    raw["open"] = pd.to_numeric(raw["open"], errors="coerce")
    raw["close"] = pd.to_numeric(raw["close"], errors="coerce")
    raw = raw.dropna().sort_values("dt_utc").drop_duplicates("dt_utc", keep="last")
    raw["dt_tr"] = raw.dt_utc.dt.tz_convert(TZ_TR)
    raw["tr_date"] = raw.dt_tr.dt.strftime("%Y-%m-%d")
    raw["tr_hm"] = raw.dt_tr.dt.strftime("%H:%M")

    key = {(r.tr_date, r.tr_hm): (float(r.open), float(r.close), r.dt_utc)
           for r in raw.itertuples(index=False)}

    dates_with_0845 = sorted(raw.loc[raw.tr_hm.eq("08:45"), "tr_date"].unique().tolist())

    rows = []
    for r in sig.itertuples(index=False):
        d = str(r.issue_date)
        state = str(r.state)

        k09 = (d, "09:00")
        k1645 = (d, "16:45")
        k17 = (d, "17:00")

        day_start = key.get(k09)
        day_end = key.get(k1645)
        on_start = key.get(k17)

        next_dates = [x for x in dates_with_0845 if x > d]
        next_d = next_dates[0] if next_dates else None
        on_end = key.get((next_d, "08:45")) if next_d else None

        day_ret = None
        day_actual = None
        if day_start and day_end:
            day_ret = day_end[1] / day_start[0] - 1.0
            day_actual = "UP" if day_ret > 0 else "DOWN"

        on_ret = None
        on_actual = None
        if on_start and on_end:
            on_ret = on_end[1] / on_start[0] - 1.0
            on_actual = "UP" if on_ret > 0 else "DOWN"

        available_ny = pd.Timestamp(r.available_ny).tz_localize(TZ_NY)
        available_tr = available_ny.tz_convert(TZ_TR)
        day_decision = pd.Timestamp(f"{d} 09:00:00", tz=TZ_TR)
        available_by_09 = bool(available_tr <= day_decision)

        rows.append({
            "issue_date": d,
            "feature_cutoff_date": str(r.feature_cutoff_date),
            "old_cig_state": state,
            "consensus": bool(r.consensus),
            "available_ny": str(r.available_ny),
            "available_tr": available_tr.isoformat(),
            "available_by_09_tr": available_by_09,
            "day_start_09_open": None if not day_start else day_start[0],
            "day_end_1645_close": None if not day_end else day_end[1],
            "day_return_09_to_17": day_ret,
            "day_actual": day_actual,
            "day_correct": None if state == "UNCERTAIN" or day_actual is None else bool(state == day_actual),
            "overnight_start_17_open": None if not on_start else on_start[0],
            "overnight_next_date": next_d,
            "overnight_end_0845_close": None if not on_end else on_end[1],
            "overnight_return_17_to_next09": on_ret,
            "overnight_actual": on_actual,
            "overnight_correct": None if state == "UNCERTAIN" or on_actual is None else bool(state == on_actual),
        })

    z = pd.DataFrame(rows)
    z.to_csv(OUT / "rows.csv", index=False)

    cons = z[z.consensus].copy()
    day = cons[cons.day_actual.notna()].copy()
    ov = cons[cons.overnight_actual.notna()].copy()
    both = cons[cons.day_actual.notna() & cons.overnight_actual.notna()].copy()

    day_acc = float(day.day_correct.mean()) if len(day) else None
    ov_acc = float(ov.overnight_correct.mean()) if len(ov) else None
    day_ba = bal_acc(day.day_actual.tolist(), day.old_cig_state.tolist()) if len(day) else None
    ov_ba = bal_acc(ov.overnight_actual.tolist(), ov.old_cig_state.tolist()) if len(ov) else None
    both_correct = int((both.day_correct.astype(bool) & both.overnight_correct.astype(bool)).sum()) if len(both) else 0

    summary = {
        "schema": "CIG_D1_JULY2025_EXECUTION_WINDOW_RESCORE_V1",
        "status": "RETROSPECTIVE_DIAGNOSTIC_ONLY",
        "month": "2025-07",
        "signal_source": SIGNALS.name,
        "price_source": RAW.name,
        "old_consensus_rule": "consensus==True; direction = V5 state (all four agree by construction)",
        "target_semantics": {
            "DAY": "Europe/Istanbul 09:00 exact 15m OPEN -> 16:45 exact 15m CLOSE (17:00 boundary)",
            "OVERNIGHT": "Europe/Istanbul 17:00 exact 15m OPEN -> next available trading date 08:45 exact 15m CLOSE (09:00 boundary)"
        },
        "calendar_signal_rows": int(len(z)),
        "consensus_rows": int(len(cons)),
        "uncertain_rows": int((~z.consensus).sum()),
        "consensus_coverage": float(len(cons) / len(z)) if len(z) else None,
        "available_by_09_all_consensus": bool(cons.available_by_09_tr.all()) if len(cons) else None,
        "day": {
            "n": int(len(day)),
            "correct": int(day.day_correct.sum()) if len(day) else 0,
            "accuracy": day_acc,
            "balanced_accuracy": day_ba,
            "up_signal_n": int((day.old_cig_state == "UP").sum()),
            "down_signal_n": int((day.old_cig_state == "DOWN").sum()),
        },
        "overnight": {
            "n": int(len(ov)),
            "correct": int(ov.overnight_correct.sum()) if len(ov) else 0,
            "accuracy": ov_acc,
            "balanced_accuracy": ov_ba,
            "up_signal_n": int((ov.old_cig_state == "UP").sum()),
            "down_signal_n": int((ov.old_cig_state == "DOWN").sum()),
        },
        "joint_same_signal": {
            "n": int(len(both)),
            "both_correct": both_correct,
            "both_correct_rate": float(both_correct / len(both)) if len(both) else None,
        },
        "guardrail": "This does not retrain or retune CIG. July 2025 is already historical/seen evidence and is not untouched OOS for new policy selection."
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# GOLD CIG-D1 — JULY 2025 EXECUTION-WINDOW RESCORE",
        "",
        "**Status:** retrospective diagnostic only; no model retraining, no threshold tuning, no new consensus.",
        "",
        "Old CIG-D1 signal states are held fixed and rescored against the two current investment objectives.",
        "",
        "## Window definitions",
        "",
        "- DAY: 09:00 Europe/Istanbul OPEN -> 16:45 CLOSE (17:00 boundary).",
        "- OVERNIGHT-HOLD: 17:00 Europe/Istanbul OPEN -> next available trading date 08:45 CLOSE (09:00 boundary).",
        "",
        "## Summary",
        "",
        f"- July signal rows: **{len(z)}**",
        f"- old CIG 4/4 consensus rows: **{len(cons)}**",
        f"- UNCERTAIN rows: **{int((~z.consensus).sum())}**",
        f"- consensus coverage: **{pct(summary['consensus_coverage'])}**",
        f"- old state available by 09:00 TRT on all consensus rows: **{summary['available_by_09_all_consensus']}**",
        f"- DAY: **{summary['day']['correct']}/{summary['day']['n']} = {pct(day_acc)}**, BA **{pct(day_ba)}**",
        f"- OVERNIGHT: **{summary['overnight']['correct']}/{summary['overnight']['n']} = {pct(ov_acc)}**, BA **{pct(ov_ba)}**",
        f"- same old signal correct on BOTH windows: **{both_correct}/{len(both)} = {pct(summary['joint_same_signal']['both_correct_rate'])}**",
        "",
        "## Daily rows",
        "",
        "| Date | Old CIG | DAY actual | DAY correct | Overnight actual | Overnight correct |",
        "|---|---|---|---:|---|---:|",
    ]
    for q in z.itertuples(index=False):
        dc = "" if pd.isna(q.day_correct) else ("YES" if bool(q.day_correct) else "NO")
        oc = "" if pd.isna(q.overnight_correct) else ("YES" if bool(q.overnight_correct) else "NO")
        lines.append(f"| {q.issue_date} | {q.old_cig_state} | {q.day_actual or ''} | {dc} | {q.overnight_actual or ''} | {oc} |")

    lines += [
        "",
        "## Interpretation guardrail",
        "",
        "This test answers only: if the historical old CIG state were reused unchanged, how often would its direction match the two new execution-aligned windows in July 2025? It does not validate a new DAY/OVERNIGHT model and it must not be used as untouched OOS evidence for selecting a new policy."
    ]
    (OUT / "result.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
