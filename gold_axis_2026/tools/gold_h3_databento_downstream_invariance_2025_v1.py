from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"

BASE_PATH = AX / "tools" / "gold_h3_2025_source_backfill_dptc_replay_v1.py"
spec = importlib.util.spec_from_file_location("base2025", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

OUTJ = AX / "GOLD_H3_DATABENTO_DOWNSTREAM_INVARIANCE_2025_2026-10-05.json"
OUTM = AX / "GOLD_H3_DATABENTO_DOWNSTREAM_INVARIANCE_2025_2026-10-05.md"
OUTC = AX / "GOLD_H3_DATABENTO_DOWNSTREAM_INVARIANCE_ORIGIN_COMPARE_2025_2026-10-05.csv"

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1h"
START = "2024-10-10"
END = "2026-10-04"
MAX_COST_USD = 1.00

MAPPING = {
    "GC": "GC.v.0",
    "SI": "SI.v.0",
    "NQ": "NQ.v.0",
    "ZN": "ZN.n.0",
    "CL": "CL.c.0",
}

OLD_IFBC = AX / "GOLD_H3_2025_BACKFILL_IFBC_EXTENDED_2026-10-05.csv"
OLD_LLRS = AX / "GOLD_H3_2025_BACKFILL_LLRS_EXTENDED_2026-10-05.csv"
OLD_STATE = AX / "GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
OLD_ACT = AX / "GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"


def fetch_databento():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db

    client = db.Historical(key)
    symbols = list(MAPPING.values())
    cost = float(client.metadata.get_cost(
        dataset=DATASET,
        schema=SCHEMA,
        symbols=symbols,
        stype_in="continuous",
        start=START,
        end=END,
    ))
    if cost > MAX_COST_USD:
        raise RuntimeError(f"ESTIMATED_COST_EXCEEDS_CAP:{cost:.6f}>{MAX_COST_USD:.2f}")

    data = client.timeseries.get_range(
        dataset=DATASET,
        schema=SCHEMA,
        symbols=symbols,
        stype_in="continuous",
        start=START,
        end=END,
    )
    d = data.to_df().reset_index()
    if "ts_event" not in d.columns and "index" in d.columns:
        d = d.rename(columns={"index": "ts_event"})
    if "ts_event" not in d.columns or "symbol" not in d.columns:
        raise RuntimeError(f"BAD_DATABENTO_FRAME:{list(d.columns)}")

    d["ts"] = pd.to_datetime(d["ts_event"], utc=True)
    d["symbol"] = d["symbol"].astype(str)
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d["volume"] = pd.to_numeric(d["volume"], errors="coerce")
    d = d[np.isfinite(d.close) & (d.close > 0)].copy()

    reverse = {v: k for k, v in MAPPING.items()}
    d["root"] = d.symbol.map(reverse)
    d = d[d.root.notna()].copy()
    return d[["ts","root","symbol","instrument_id","close","volume"]], cost


def wide_prices(d):
    p = d.pivot_table(index="ts", columns="root", values="close", aggfunc="last").reset_index()
    need = ["GC","ZN","NQ","SI","CL"]
    p = p.dropna(subset=need).sort_values("ts").reset_index(drop=True)
    return p[["ts"]+need]


def build_vast_from_db(d, h3):
    parts = {}
    for root in ["GC","SI"]:
        q = d[d.root == root][["ts","close","volume"]].copy().sort_values("ts").drop_duplicates("ts")
        q = q.rename(columns={"close":f"{root}_close","volume":f"{root}_volume"})
        q[f"{root}_volume"] = pd.to_numeric(q[f"{root}_volume"], errors="coerce").fillna(0.0).clip(lower=0.0)
        q = base.same_hour_volume_z(q, root)
        parts[root] = q
    x = parts["GC"].merge(parts["SI"], on="ts", how="inner").sort_values("ts").reset_index(drop=True)
    x["GC_ret1"] = np.log(x.GC_close).diff()
    x["SI_ret1"] = np.log(x.SI_close).diff()

    hh = h3[h3.eligible_v5_continuation.map(base.B)].copy()
    hh = hh[hh.forecast_issue_date >= pd.Timestamp("2024-10-15")].sort_values("forecast_issue_date")
    rows = []
    for r in hh.itertuples():
        co = base.cutoff_ts(r.feature_cutoff_date)
        w = x[(x.ts <= co) & (x.ts >= co-pd.Timedelta(hours=18))].tail(12).copy()
        if len(w) < 12:
            continue
        if (co-w.ts.iloc[-1]).total_seconds()/3600 > 3:
            continue
        if (w.ts.iloc[-1]-w.ts.iloc[0]).total_seconds()/3600 > 18:
            continue
        if w[["GC_ret1","SI_ret1"]].isna().any(axis=None):
            continue
        s = 1.0 if int(r.momentum_up) == 1 else -1.0
        out = r._asdict()
        for h in [3,6,12]:
            z = w.tail(h)
            out[f"gc_flow_{h}"] = base.vol_flow(z.GC_ret1.to_numpy(), z.GC_volume.to_numpy(), s)
            out[f"gc_opp_vol_share_{h}"] = base.opp_share(z.GC_ret1.to_numpy(), z.GC_volume.to_numpy(), s)
        for h in [6,12]:
            z = w.tail(h)
            out[f"gc_efficiency_{h}"] = base.efficiency(z.GC_ret1.to_numpy())
        for h in [6,12]:
            z = w.tail(h)
            out[f"si_flow_{h}"] = base.vol_flow(z.SI_ret1.to_numpy(), z.SI_volume.to_numpy(), s)
            out[f"si_opp_vol_share_{h}"] = base.opp_share(z.SI_ret1.to_numpy(), z.SI_volume.to_numpy(), s)
        out["gc_si_flow_gap12"] = float(out["gc_flow_12"] - out["si_flow_12"])
        out["joint_opposition_share12"] = float((out["gc_opp_vol_share_12"] + out["si_opp_vol_share_12"])/2)
        out["hourly_last_ts"] = w.ts.iloc[-1]
        rows.append(out)
    return pd.DataFrame(rows).sort_values("feature_cutoff_date").reset_index(drop=True)


def prep_h3():
    h3 = pd.read_csv(base.H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        h3[c] = pd.to_datetime(h3[c])
    for c in ["eligible_v5_continuation","opal_override_check"]:
        if c in h3.columns:
            h3[c] = h3[c].map(base.B)
    return h3


def make_decision_panel(h3, state):
    z = h3[h3.feature_cutoff_date.dt.year == 2025].copy().sort_values("feature_cutoff_date")
    z["v5_pred"] = (pd.to_numeric(z.p_helios_v5_dce, errors="coerce") >= .5).astype(int)

    sg = pd.read_csv(base.SAGE, parse_dates=["feature_cutoff_date"])
    sdates = set(sg[(sg.feature_cutoff_date.dt.year == 2025) & sg.ocs_candidate.map(base.B)].feature_cutoff_date)
    rf = pd.read_csv(base.RF, parse_dates=["date"])
    rdates = set(rf[(rf.period.astype(str) == "2025") & rf.v3_candidate.map(base.B)].date)
    flips = sdates | rdates
    z["baseline_pred"] = np.where(z.feature_cutoff_date.isin(flips), 1-z.v5_pred, z.v5_pred).astype(int)
    z["baseline_correct"] = z.baseline_pred == z.y_up.astype(int)
    z = z.merge(state, on="feature_cutoff_date", how="left")

    ph = pd.read_csv(base.PHASE, parse_dates=["feature_cutoff_date"])
    z = z.merge(ph[["feature_cutoff_date","strong_pro_risk","strong_run","dep_shift95","dependence_phase"]],
                on="feature_cutoff_date", how="left")
    z["phase_q95"] = z.dependence_phase.map(base.B)
    z["phase_q99"] = z.strong_pro_risk.map(base.B) & (
        (pd.to_numeric(z.strong_run, errors="coerce") > base.Q99_RUN) | z.dep_shift95.map(base.B)
    )

    sc = pd.read_csv(base.SELLR, parse_dates=["feature_cutoff_date"])
    sc = sc[["feature_cutoff_date","sellr_score","baseline_pred","momentum_up"]].rename(
        columns={"baseline_pred":"sellr_baseline_pred","momentum_up":"sellr_momentum_up"}
    )
    z = z.merge(sc, on="feature_cutoff_date", how="left")
    z["sellr_fire"] = (
        (pd.to_numeric(z.sellr_score, errors="coerce") >= base.SELLR_THR) &
        (pd.to_numeric(z.sellr_baseline_pred, errors="coerce") == pd.to_numeric(z.sellr_momentum_up, errors="coerce"))
    )
    z["handoff_alarm"] = (
        (pd.to_numeric(z.leadlag_score_premax, errors="coerce") >= .60) &
        (pd.to_numeric(z.internal_now, errors="coerce") >= .60) &
        (pd.to_numeric(z.internal_d1, errors="coerce") >= 0) &
        (z.baseline_pred.astype(int) == z.momentum_up.astype(int))
    )
    z["competence_y"] = (~z.baseline_correct).astype(int)
    return z


def scalar_compare(new, old, key, cols):
    a = new[[key]+cols].copy()
    b = old[[key]+cols].copy()
    j = a.merge(b, on=key, suffixes=("_db","_yh"))
    out = {"overlap_n": int(len(j)), "columns": {}}
    for c in cols:
        x = pd.to_numeric(j[f"{c}_db"], errors="coerce")
        y = pd.to_numeric(j[f"{c}_yh"], errors="coerce")
        q = pd.DataFrame({"x":x,"y":y}).dropna()
        if q.empty:
            out["columns"][c] = {"n":0,"corr":None,"mae":None,"max_abs":None}
        else:
            out["columns"][c] = {
                "n": int(len(q)),
                "corr": None if len(q)<2 else float(q.x.corr(q.y)),
                "mae": float(np.mean(np.abs(q.x-q.y))),
                "max_abs": float(np.max(np.abs(q.x-q.y))),
            }
    return j, out


def set_stats(a, b):
    a=set(pd.to_datetime(list(a))); b=set(pd.to_datetime(list(b)))
    inter=a&b; union=a|b
    return {
        "new_n":len(a),"old_n":len(b),"matched":len(inter),
        "added":[x.date().isoformat() for x in sorted(a-b)],
        "missing":[x.date().isoformat() for x in sorted(b-a)],
        "jaccard": 1.0 if not union else len(inter)/len(union),
    }


def main():
    d, cost = fetch_databento()
    h3 = prep_h3()

    vast = build_vast_from_db(d, h3)
    ifbc = base.build_ifbc_scores(vast)
    raw = wide_prices(d)
    hourly = base.llrs_prepare_hourly(raw)
    llrs = base.llrs_origin_scores(hourly, h3, "2024-12-01")
    state = base.build_handoff_scores(ifbc, llrs)
    z = make_decision_panel(h3, state)

    old_i = pd.read_csv(OLD_IFBC, parse_dates=["feature_cutoff_date"])
    old_l = pd.read_csv(OLD_LLRS, parse_dates=["feature_cutoff_date"])
    old_s = pd.read_csv(OLD_STATE, parse_dates=["feature_cutoff_date"])
    old_a = pd.read_csv(OLD_ACT, parse_dates=["feature_cutoff_date"])

    ifbc_cols = [
        "gc_flow_12","gc_opp_vol_share_12","gc_efficiency_12",
        "si_flow_12","si_opp_vol_share_12","gc_si_flow_gap12",
        "joint_opposition_share12","ifbc_score","ifbc_count60"
    ]
    llrs_cols = ["llrs_pressure","llrs_incremental"]
    state_cols = ["fragility_score","flow_score","leadlag_score","leadlag_score_premax","internal_now","internal_d1"]

    _, ifbc_cmp = scalar_compare(ifbc, old_i, "feature_cutoff_date", ifbc_cols)
    _, llrs_cmp = scalar_compare(llrs, old_l, "feature_cutoff_date", llrs_cols)
    _, state_cmp = scalar_compare(state, old_s, "feature_cutoff_date", state_cols)

    alarms_new = z[z.handoff_alarm].copy()
    alarms_old = old_s[old_s.handoff_alarm.map(base.B)].copy()
    alarm_stats = set_stats(alarms_new.feature_cutoff_date, alarms_old.feature_cutoff_date)

    variants = {}
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _, a, entry, rescue, broken = base.simulate_dptc(alarms_new, col)
        oldv = old_a[old_a.variant.astype(str) == name].copy()
        ss = set_stats(a.feature_cutoff_date, oldv.feature_cutoff_date)
        mode_match = None
        if len(a) and len(oldv):
            q = a[["feature_cutoff_date","mode"]].merge(
                oldv[["feature_cutoff_date","mode"]], on="feature_cutoff_date", suffixes=("_db","_yh")
            )
            mode_match = float((q.mode_db == q.mode_yh).mean()) if len(q) else None
        variants[name] = {
            "entry": None if entry is None else entry.date().isoformat(),
            "actions": int(len(a)), "rescue": int(rescue), "broken": int(broken), "net": int(rescue-broken),
            "precision": float(rescue/max(len(a),1)),
            "action_set": ss,
            "mode_match_on_shared": mode_match,
        }

    compare = z[["feature_cutoff_date","handoff_alarm","leadlag_score_premax","internal_now","internal_d1"]].copy()
    compare = compare.merge(
        old_s[["feature_cutoff_date","handoff_alarm","leadlag_score_premax","internal_now","internal_d1"]],
        on="feature_cutoff_date", suffixes=("_db","_yh"), how="left"
    )
    compare.to_csv(OUTC,index=False)

    dptc_j = min(variants["Q95"]["action_set"]["jaccard"], variants["Q99"]["action_set"]["jaccard"])
    decision_pass = alarm_stats["jaccard"] >= 0.90 and dptc_j >= 0.90

    out = {
        "schema":"GOLD_H3_DATABENTO_DOWNSTREAM_INVARIANCE_2025_V1",
        "date":"2026-10-05",
        "mapping":MAPPING,
        "window":[START,END],
        "estimated_cost_usd":cost,
        "cost_cap_usd":MAX_COST_USD,
        "raw_vendor_values_committed":False,
        "thresholds_retuned":False,
        "outcomes_used_for_source_selection":False,
        "coverage":{
            "databento_rows":int(len(d)),
            "synchronized_price_rows":int(len(raw)),
            "vast_origins":int(len(vast)),
            "ifbc_origins":int(len(ifbc)),
            "llrs_origins":int(len(llrs)),
            "state_origins":int(len(state)),
        },
        "ifbc_compare":ifbc_cmp,
        "llrs_compare":llrs_cmp,
        "state_compare":state_cmp,
        "handoff_alarm_set":alarm_stats,
        "dptc":variants,
        "decision_invariance_pass_90pct":bool(decision_pass),
        "status":"DOWNSTREAM_DECISION_INVARIANCE_PASS" if decision_pass else "DOWNSTREAM_DECISION_INVARIANCE_REQUIRES_REVIEW",
        "interpretation":(
            "Databento mapping is sufficiently decision-invariant for a source-bridged historical replay, while remaining non-identical to Yahoo raw bars."
            if decision_pass else
            "Source differences materially change Handoff/DPTC decisions; do not call a 2023-2024 replay equivalent without further mechanism-level diagnosis."
        )
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    def fmt_metric(dct, col):
        q=dct["columns"][col]
        if q["corr"] is None: return "—"
        return f"corr={q['corr']:.5f}, MAE={q['mae']:.6g}, max={q['max_abs']:.6g}"

    lines=[
        "# GOLD H3 — Databento Downstream Invariance Audit (2025) — 2026-10-05","",
        f"**Status:** **{out['status']}**  ",
        f"Estimated Databento request cost: **USD {cost:.4f}** (cap USD {MAX_COST_USD:.2f}).  ",
        "**No thresholds or controller rules were retuned; no DPTC outcomes were used to select the source mapping.**","",
        "## Frozen source mapping used","",
        "| Channel | Databento |",
        "|---|---|",
    ]
    for k,v in MAPPING.items(): lines.append(f"| {k} | {v} |")
    lines += ["","## Derived-state agreement","",
              f"- IFBC score: {fmt_metric(ifbc_cmp,'ifbc_score')}",
              f"- LLRS pressure: {fmt_metric(llrs_cmp,'llrs_pressure')}",
              f"- LLRS incremental: {fmt_metric(llrs_cmp,'llrs_incremental')}",
              f"- Handoff leadlag premax: {fmt_metric(state_cmp,'leadlag_score_premax')}",
              f"- Handoff internal_now: {fmt_metric(state_cmp,'internal_now')}",
              f"- Handoff internal_d1: {fmt_metric(state_cmp,'internal_d1')}","",
              "## Decision invariance","",
              f"- Handoff alarms: Databento **{alarm_stats['new_n']}**, Yahoo **{alarm_stats['old_n']}**, matched **{alarm_stats['matched']}**, Jaccard **{100*alarm_stats['jaccard']:.1f}%**.",
              f"- Added Databento alarms: **{', '.join(alarm_stats['added']) if alarm_stats['added'] else 'none'}**.",
              f"- Missing vs Yahoo: **{', '.join(alarm_stats['missing']) if alarm_stats['missing'] else 'none'}**.","",
              "| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net | Shared-mode match |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for name in ["Q95","Q99"]:
        v=variants[name]; s=v["action_set"]
        mm="—" if v["mode_match_on_shared"] is None else f"{100*v['mode_match_on_shared']:.1f}%"
        lines.append(f"| {name} | {s['new_n']} | {s['old_n']} | {s['matched']} | {100*s['jaccard']:.1f}% | {v['rescue']}/{v['broken']}/{v['net']:+d} | {mm} |")
    lines += ["","## Scientific interpretation","",
              out["interpretation"],
              "",
              "- This audit tests downstream invariance, not raw-bar identity.",
              "- The primary objects are IFBC/LLRS states, canonical Handoff alarms, and frozen Q95/Q99 controller actions.",
              "- A 90% decision-set threshold was preregistered in this audit script before observing its results.",
              "- Even if passed, a 2023–2024 Databento replay must be labeled source-bridged historical reconstruction, not Yahoo-identical lineage."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())


if __name__=="__main__":
    main()
