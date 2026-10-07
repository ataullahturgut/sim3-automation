from __future__ import annotations

# workflow trigger: TURN V1 contract unchanged

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
AURORAP=AX/"tools"/"gold_session_aurora_v1_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
OUT=AX/"SESSION_TURN_V1_OUT";OUT.mkdir(exist_ok=True)

TAIL_Q=.80
REF_WINDOW=250
MIN_REF=120
SEMI_HOURS=120

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

aur=loadmod("session_aurora",AURORAP)
m05=loadmod("m05",M05P)

def metric(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "up_actual":int((y==1).sum()),
        "up_correct":int(((y==1)&(pred==1)).sum()),
        "down_actual":int((y==0).sum()),
        "down_correct":int(((y==0)&(pred==0)).sum()),
    }

def fresh_aurora():
    ledger=aur.sentry.load_ledger()
    rows=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        pred,_=aur.run_window(g[g.year.isin([2023,2024,2025])].copy())
        if not pred.empty:rows.append(pred)
    q=pd.concat(rows,ignore_index=True)
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def hourly_tail_source():
    x15=m05.load_xau15_extended()
    x1=m05.load_xau1h(x15).copy().sort_values("available_at_utc").reset_index(drop=True)
    x1["logp"]=np.log(x1.value.astype(float))
    x1["hr"]=x1.logp.diff()
    x1["h_ret_12_active"]=x1.logp-x1.logp.shift(12)
    pos=x1.hr.clip(lower=0).pow(2)
    neg=x1.hr.clip(upper=0).pow(2)
    x1["rs_plus_120"]=pos.rolling(SEMI_HOURS,min_periods=SEMI_HOURS).sum()
    x1["rs_minus_120"]=neg.rolling(SEMI_HOURS,min_periods=SEMI_HOURS).sum()
    return x1

def build_tail_anchors():
    t=m05.load_targets_extended()[["partition","window","start_utc","year"]].copy()
    t=t[t.year.isin([2022,2023,2024,2025])].copy()
    h=hourly_tail_source()[[
        "available_at_utc","ts","h_ret_12_active","rs_plus_120","rs_minus_120"
    ]].dropna().sort_values("available_at_utc").copy()

    out=[]
    for (part,win),g in t.groupby(["partition","window"],sort=True):
        left=g.sort_values("start_utc").copy()
        z=pd.merge_asof(
            left,
            h,
            left_on="start_utc",
            right_on="available_at_utc",
            direction="backward",
            allow_exact_matches=False
        )
        timed=z.available_at_utc.notna()
        if not (z.loc[timed,"available_at_utc"]<z.loc[timed,"start_utc"]).all():
            raise RuntimeError(f"TURN_TAIL_TIME_LEAK {part} {win}")

        z["q80_plus"]=np.nan
        z["q80_minus"]=np.nan
        valid=z[["h_ret_12_active","rs_plus_120","rs_minus_120"]].notna().all(axis=1)
        zv=z.loc[valid,["rs_plus_120","rs_minus_120"]].copy()
        z.loc[valid,"q80_plus"]=(
            zv.rs_plus_120.shift(1)
            .rolling(REF_WINDOW,min_periods=MIN_REF)
            .quantile(TAIL_Q)
            .to_numpy()
        )
        z.loc[valid,"q80_minus"]=(
            zv.rs_minus_120.shift(1)
            .rolling(REF_WINDOW,min_periods=MIN_REF)
            .quantile(TAIL_Q)
            .to_numpy()
        )
        z["ref_ready"]=(
            valid & z.q80_plus.notna() & z.q80_minus.notna()
        )
        out.append(z)
    return pd.concat(out,ignore_index=True)

def build_panel():
    a=fresh_aurora()
    tails=build_tail_anchors()
    q=a.merge(
        tails[[
            "partition","window","start_utc","available_at_utc","ts",
            "h_ret_12_active","rs_plus_120","rs_minus_120",
            "q80_plus","q80_minus","ref_ready"
        ]],
        on=["partition","window","start_utc"],
        how="left",validate="one_to_one"
    )
    if q.h_ret_12_active.isna().any():
        raise RuntimeError("TURN_AURORA_TAIL_JOIN_FAIL")
    if not (q.available_at_utc<q.start_utc).all():
        raise RuntimeError("TURN_JOIN_TIME_LEAK")

    rows=[]
    for r in q.itertuples(index=False):
        pa=float(r.p_aurora)
        aur_dir=1 if pa>=.5 else 0
        mom=1 if float(r.h_ret_12_active)>=0 else 0
        ready=bool(r.ref_ready)
        plus=bool(ready and float(r.rs_plus_120)>float(r.q80_plus))
        minus=bool(ready and float(r.rs_minus_120)>float(r.q80_minus))
        both=bool(plus and minus)
        flip=False;signal="KEEP"
        if ready and aur_dir==mom:
            if mom==1 and minus and not plus:
                flip=True;signal="UP_MOMENTUM_MINUS_TAIL_FLIP_DOWN"
            elif mom==0 and plus and not minus:
                flip=True;signal="DOWN_MOMENTUM_PLUS_TAIL_FLIP_UP"
            elif both:
                signal="BOTH_TAIL_RISK_KEEP"
        pt=1-pa if flip else pa
        rows.append({
            "partition":r.partition,"window":r.window,"label_date":r.label_date,
            "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
            "y_up":int(r.y_up),"p_aurora":pa,"p_turn":float(pt),
            "momentum_up":mom,"h_ret_12_active":float(r.h_ret_12_active),
            "rs_plus_120":float(r.rs_plus_120),"rs_minus_120":float(r.rs_minus_120),
            "q80_plus":float(r.q80_plus) if pd.notna(r.q80_plus) else np.nan,
            "q80_minus":float(r.q80_minus) if pd.notna(r.q80_minus) else np.nan,
            "ref_ready":ready,"plus_tail":plus,"minus_tail":minus,
            "both_tail_risk":both,"override":flip,"signal":signal
        })
    return pd.DataFrame(rows)

def paired(g):
    ma=metric(g.y_up,g.p_aurora);mt=metric(g.y_up,g.p_turn)
    ad=(g.p_aurora>=.5).astype(int);td=(g.p_turn>=.5).astype(int);y=g.y_up.astype(int)
    ch=ad.ne(td)
    rescue=int((ch&ad.ne(y)&td.eq(y)).sum())
    broken=int((ch&ad.eq(y)&td.ne(y)).sum())
    return ma,mt,{
        "override_n":int(g.override.sum()),
        "changed_n":int(ch.sum()),
        "rescued":rescue,"broken":broken,"net_rescue":rescue-broken,
        "both_tail_n":int(g.both_tail_risk.sum())
    }

def development_gate(g):
    reasons=[]
    if int(g.override.sum())==0:reasons.append("NO_OVERRIDE")
    ma,mt,extra=paired(g)
    if extra["net_rescue"]<=0:reasons.append("NET_RESCUE_NOT_POSITIVE")
    if mt["balanced_accuracy"]+1e-12<ma["balanced_accuracy"]:reasons.append("DEV_BA")
    if mt["brier"]>ma["brier"]+.003+1e-12:reasons.append("DEV_BRIER")
    for yr in [2023,2024]:
        z=g[g.year.eq(yr)]
        if z.empty:continue
        ya,yt,_=paired(z)
        if yt["accuracy"]+.01+1e-12<ya["accuracy"]:
            reasons.append(f"{yr}_ACC")
    return len(reasons)==0,("PASS" if not reasons else "|".join(reasons)),ma,mt,extra

def summarize(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        ma,mt,x=paired(g)
        rows.append({
            "period":period,"partition":part,"window":win,
            **x,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"turn_{k}":v for k,v in mt.items()}
        })
    return pd.DataFrame(rows)

def main():
    panel=build_panel()
    dev=panel[panel.year.isin([2023,2024])&panel.ref_ready].copy()
    if dev.empty:raise RuntimeError("TURN_NO_DEV")

    gates=[]
    for (part,win),g in dev.groupby(["partition","window"],sort=True):
        ok,reason,ma,mt,x=development_gate(g)
        gates.append({
            "partition":part,"window":win,"eligible":ok,"reason":reason,
            "dev_n":int(len(g)),
            "aurora_ba":ma["balanced_accuracy"],"turn_ba":mt["balanced_accuracy"],
            "aurora_brier":ma["brier"],"turn_brier":mt["brier"],
            "turn_up_recall":mt["up_recall"],"turn_down_recall":mt["down_recall"],
            **x
        })
    gate=pd.DataFrame(gates)
    eligible={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}

    tr=panel[
        panel.year.eq(2025)&panel.ref_ready&
        panel.apply(lambda r:(r.partition,r.window) in eligible,axis=1)
    ].copy()

    panel.to_csv(OUT/"panel.csv",index=False)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    gate.to_csv(OUT/"eligibility.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_TURN_V1_COMPLETE",
        "rule":{"semi_hours":SEMI_HOURS,"ref_window":REF_WINDOW,"min_ref":MIN_REF,"tail_q":TAIL_Q},
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "development_gate":gate.to_dict("records"),
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "guardrails":[
            "2022 used only as tail-history warm-up.",
            "Every hourly bar must be fully available before session start.",
            "Tail quantiles use only prior same-window anchors.",
            "TURN has no fitted threshold or classifier.",
            "2025 does not select or retune the rule.",
            "2026 remains unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION TURN V1 — RESULT","",
           "## Development eligibility","",
           "| Partition | Window | N | AURORA BA | TURN BA | TURN UP | TURN DOWN | Overrides | Rescue | Break | Net | Both-tail | Eligible | Reason |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
            f"{100*r.aurora_ba:.2f}% | {100*r.turn_ba:.2f}% | "
            f"{100*r.turn_up_recall:.2f}% | {100*r.turn_down_recall:.2f}% | "
            f"{int(r.override_n)} | {int(r.rescued)} | {int(r.broken)} | "
            f"{int(r.net_rescue):+d} | {int(r.both_tail_n)} | {r.eligible} | {r.reason} |"
        )
    lines+=["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No TURN head passed development; 2025 remained closed.")
    else:
        tm=summarize(tr,"FROZEN_2025")
        lines+=["| Partition | Window | N | AURORA BA | TURN BA | TURN UP | TURN DOWN | AURORA Brier | TURN Brier | Overrides | Rescue | Break | Net |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {int(r.turn_n)} | "
                f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.turn_balanced_accuracy:.2f}% | "
                f"{100*r.turn_up_recall:.2f}% | {100*r.turn_down_recall:.2f}% | "
                f"{r.aurora_brier:.4f} | {r.turn_brier:.4f} | "
                f"{int(r.override_n)} | {int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
