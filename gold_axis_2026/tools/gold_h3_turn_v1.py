from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_turn_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

TAIL_Q = 0.80
REF_WINDOW = 250
MIN_REF = 120
SEMI_HOURS = 120
SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_hourly():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"TURN_SOURCE_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    h = pd.concat([hist, ext], ignore_index=True)
    h = h.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return h, bridge, api_calls


def build_tail_anchors(hourly):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q.ts.dt.tz_convert(iris.TZ)
    q["local_date"] = pd.to_datetime(q.ts_ny.dt.date)
    q["local_hour"] = q.ts_ny.dt.hour
    q["local_minute"] = q.ts_ny.dt.minute
    q["logp"] = np.log(q.value.astype(float))
    q["hr"] = q.logp.diff()
    q["h_ret_12"] = q.logp - q.logp.shift(12)

    pos_sq = q.hr.clip(lower=0).pow(2)
    neg_sq = q.hr.clip(upper=0).pow(2)
    q["rs_plus_120"] = pos_sq.rolling(SEMI_HOURS, min_periods=SEMI_HOURS).sum()
    q["rs_minus_120"] = neg_sq.rolling(SEMI_HOURS, min_periods=SEMI_HOURS).sum()

    a = q[
        (q.local_hour == 16)
        & (q.local_minute == 0)
    ][["local_date","ts","h_ret_12","rs_plus_120","rs_minus_120"]].copy()
    a = a.dropna().sort_values("ts").drop_duplicates("local_date", keep="last").reset_index(drop=True)

    a["q80_plus"] = (
        a.rs_plus_120.shift(1)
        .rolling(REF_WINDOW, min_periods=MIN_REF)
        .quantile(TAIL_Q)
    )
    a["q80_minus"] = (
        a.rs_minus_120.shift(1)
        .rolling(REF_WINDOW, min_periods=MIN_REF)
        .quantile(TAIL_Q)
    )
    a["ref_ready"] = a.q80_plus.notna() & a.q80_minus.notna()
    return a


def apply_turn():
    a = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        a[c] = pd.to_datetime(a[c], errors="raise")
    a["feature_date"] = a.feature_cutoff_date.dt.normalize()

    hourly, bridge, api_calls = load_hourly()
    tails = build_tail_anchors(hourly)
    tails["feature_date"] = pd.to_datetime(tails.local_date).dt.normalize()

    g = a.merge(
        tails[[
            "feature_date","h_ret_12","rs_plus_120","rs_minus_120",
            "q80_plus","q80_minus","ref_ready"
        ]],
        on="feature_date",
        how="left",
        validate="one_to_one",
    )
    if g.h_ret_12.isna().any():
        bad = g[g.h_ret_12.isna()].feature_cutoff_date.astype(str).tolist()
        raise RuntimeError(f"TURN_ANCHOR_MATCH_FAIL {bad[:20]}")

    out = []
    for r in g.itertuples():
        p = float(r.p_aurora)
        aur_dir = 1 if p >= 0.5 else 0
        mom = 1 if float(r.h_ret_12) >= 0 else 0

        plus_tail = bool(r.ref_ready and float(r.rs_plus_120) > float(r.q80_plus))
        minus_tail = bool(r.ref_ready and float(r.rs_minus_120) > float(r.q80_minus))
        both_tail = bool(plus_tail and minus_tail)

        signal = "KEEP"
        flip = False
        if bool(r.ref_ready) and aur_dir == mom:
            if mom == 1 and minus_tail and not plus_tail:
                flip = True
                signal = "UP_MOMENTUM_MINUS_TAIL_FLIP_DOWN"
            elif mom == 0 and plus_tail and not minus_tail:
                flip = True
                signal = "DOWN_MOMENTUM_PLUS_TAIL_FLIP_UP"
            elif both_tail:
                signal = "BOTH_TAIL_RISK_KEEP"

        p_turn = 1.0 - p if flip else p

        out.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_aurora": p,
            "h_ret_12": float(r.h_ret_12),
            "rs_plus_120": float(r.rs_plus_120),
            "rs_minus_120": float(r.rs_minus_120),
            "q80_plus": float(r.q80_plus) if pd.notna(r.q80_plus) else np.nan,
            "q80_minus": float(r.q80_minus) if pd.notna(r.q80_minus) else np.nan,
            "ref_ready": bool(r.ref_ready),
            "plus_tail": plus_tail,
            "minus_tail": minus_tail,
            "both_tail_risk": both_tail,
            "signal": signal,
            "override": flip,
            "p_turn": float(p_turn),
        })
    return pd.DataFrame(out), bridge, api_calls


def score_periods(g):
    specs = [
        ("2022_H2", g.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023,2024])),
        ("2025-2026", g.year.isin([2025,2026])),
    ]
    rows=[]
    for label,mask in specs:
        z=g[mask].copy()
        if z.empty: continue
        ma=metrics(z.y_up,z.p_aurora)
        mt=metrics(z.y_up,z.p_turn)
        ap=(z.p_aurora>=.5).astype(int)
        tp=(z.p_turn>=.5).astype(int)
        y=z.y_up.astype(int)
        changed=ap!=tp
        rescued=int((changed&(ap!=y)&(tp==y)).sum())
        broken=int((changed&(ap==y)&(tp!=y)).sum())
        rows.append({
            "period":label,
            "override_n":int(z.override.sum()),
            "both_tail_n":int(z.both_tail_risk.sum()),
            "rescued":rescued,
            "broken":broken,
            "net_rescue":rescued-broken,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"turn_{k}":v for k,v in mt.items()},
        })
    return pd.DataFrame(rows)


def mechanism_gate(mdf):
    ok=True
    checks=[]
    for yr in ["2023","2024"]:
        r=mdf[mdf.period==yr].iloc[0]
        passed=bool(
            r.turn_accuracy + .01 + 1e-12 >= r.aurora_accuracy
            and r.turn_brier <= r.aurora_brier + .003 + 1e-12
        )
        checks.append({"period":yr,"pass":passed})
        ok=ok and passed
    agg=mdf[mdf.period=="2023-2024"].iloc[0]
    agg_ok=bool(
        agg.turn_balanced_accuracy + 1e-12 >= agg.aurora_balanced_accuracy
        and int(agg.net_rescue) > 0
    )
    return bool(ok and agg_ok),checks,agg_ok


def logloss_row(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    y=np.asarray(y,int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def paired_diff(y,cand,base):
    y=np.asarray(y,int); cand=np.asarray(cand,float); base=np.asarray(base,float)
    return {
        "accuracy":((cand>=.5).astype(int)==y).astype(float)-((base>=.5).astype(int)==y).astype(float),
        "brier":(cand-y)**2-(base-y)**2,
        "logloss":logloss_row(y,cand)-logloss_row(y,base),
    }


def circular_boot(diff,block_len,rng):
    diff=np.asarray(diff,float); n=len(diff); nb=int(np.ceil(n/block_len))
    vals=np.empty(REPS,float); offs=np.arange(block_len); batch=500
    for st in range(0,REPS,batch):
        m=min(batch,REPS-st)
        starts=rng.integers(0,n,size=(m,nb))
        idx=(starts[:,:,None]+offs[None,None,:])%n
        idx=idx.reshape(m,-1)[:,:n]
        vals[st:st+m]=diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows=[]; seed_i=0
    for period,mask in {
        "2023-2024":g.year.isin([2023,2024]),
        "2025-2026":g.year.isin([2025,2026]),
        "2026":g.year==2026,
    }.items():
        z=g[mask].copy()
        for metric,d in paired_diff(z.y_up,z.p_turn,z.p_aurora).items():
            for block in BLOCKS:
                seed_i+=1
                boot=circular_boot(d,block,np.random.default_rng(SEED+seed_i))
                lo,hi=np.quantile(boot,[.025,.975])
                improve=float(np.mean(boot>0)) if metric=="accuracy" else float(np.mean(boot<0))
                rows.append({
                    "period":period,"metric":metric,"block_len":block,
                    "observed_diff":float(np.mean(d)),
                    "ci95_low":float(lo),"ci95_high":float(hi),
                    "bootstrap_improve_share":improve,"n":int(len(z)),
                })
    return pd.DataFrame(rows)


def main():
    pred,bridge,api_calls=apply_turn()
    pred.to_csv(OUT/"turn_v1_predictions.csv",index=False)

    mdf=score_periods(pred)
    mdf.to_csv(OUT/"turn_v1_metrics.csv",index=False)

    passed,checks,agg_ok=mechanism_gate(mdf)
    status="MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    inf=inference(pred) if passed else pd.DataFrame()
    if passed:
        inf.to_csv(OUT/"turn_v1_inference.csv",index=False)

    z=pred[pred.year==2026].copy()
    z["aurora_dir"]=np.where(z.p_aurora>=.5,"UP","DOWN")
    z["turn_dir"]=np.where(z.p_turn>=.5,"UP","DOWN")
    z["actual_dir"]=np.where(z.y_up==1,"UP","DOWN")
    z["aurora_correct"]=z.aurora_dir==z.actual_dir
    z["turn_correct"]=z.turn_dir==z.actual_dir
    changed=z[z.override].copy()
    changed["effect"]=np.where(
        (~changed.aurora_correct)&changed.turn_correct,"RESCUED",
        np.where(changed.aurora_correct&(~changed.turn_correct),"BROKEN","NO_NET")
    )
    changed.to_csv(OUT/"turn_v1_2026_changed.csv",index=False)

    summary={
        "schema":"TURN_H3_V1",
        "status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "rule":{"semi_hours":SEMI_HOURS,"ref_window":REF_WINDOW,"tail_quantile":TAIL_Q,"min_ref":MIN_REF},
        "source_bridge":bridge,
        "api_calls":int(api_calls),
        "mechanism_pass":bool(passed),
        "confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "metrics":mdf.to_dict(orient="records"),
        "inference":inf.to_dict(orient="records") if passed else [],
        "changed_2026":int(len(changed)),
        "rescued_2026":int((changed.effect=="RESCUED").sum()),
        "broken_2026":int((changed.effect=="BROKEN").sum()),
    }
    (OUT/"turn_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# TURN-H3 V1 — TAIL-UNBALANCED REVERSAL NAVIGATOR RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  ",
        f"**Rule:** 120 active-hour semivariance; prior-250-anchor 80th-percentile tails.","",
        "## Period metrics","",
        "| Period | AURORA Acc | TURN Acc | AURORA BA | TURN BA | AURORA Brier | TURN Brier | Overrides | Rescued | Broken | Both-tail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in mdf.iterrows():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.turn_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.turn_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.turn_brier:.4f} | {int(r.override_n)} | "
            f"{int(r.rescued)} | {int(r.broken)} | {int(r.both_tail_n)} |"
        )

    lines += ["","## 2026 changed calls",""]
    if changed.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | AURORA | TURN | Actual | H3 return | RS+ tail | RS- tail | Effect |",
            "|---|---|---|---|---|---:|---|---|---|",
        ]
        for r in changed.itertuples():
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{r.aurora_dir} | {r.turn_dir} | {r.actual_dir} | {100*r.target_r3:+.2f}% | "
                f"{r.plus_tail} | {r.minus_tail} | {r.effect} |"
            )

    if passed:
        lines += ["","## Dependence-aware bootstrap",""]
        for r in inf.itertuples():
            scale=100 if r.metric=="accuracy" else 1
            unit=" pp" if r.metric=="accuracy" else ""
            lines.append(
                f"- {r.period} {r.metric} block{r.block_len}: diff={scale*r.observed_diff:+.4f}{unit}; "
                f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
                f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
            )

    lines += ["","## Governance","",
              "TURN is a fixed literature-derived tail-region rule. No threshold, horizon, or state action was selected from 2022-2026 outcomes. "
              "Because the decision to study reversal was itself informed by historical error anatomy, only future frozen origins can provide prospective confirmation."]

    (OUT/"TURN_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"TURN_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
