from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
AURORAP=AX/"tools"/"gold_session_aurora_v1_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
COT_STATE=AX/"GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv"
COT_MAP=AX/"GOLD_V5_SESSION_COT_AVAILABILITY_MAP_2023_2025.csv"
OUT=AX/"SESSION_OPAL_V1_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

aur=loadmod("session_aurora",AURORAP)
m05=loadmod("m05",M05P)

THRESH=.70
MIN_TRAIN=80
SEED=20261003
EPS=1e-8

FEATURES=[
    "opt_mm_net","opt_prod_net","opt_swap_net","opt_other_net",
    "d_opt_mm_net","d_opt_prod_net",
    "opt_mm_z52","opt_prod_z52","opt_swap_z52","opt_other_z52",
    "spec_hedger_gap","spec_swap_gap",
    "fut_mm_net","fut_prod_net",
    "trend_x_opt_mm","trend_x_opt_prod","trend_x_spec_hedger_gap",
    "trend_strength",
]

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

def model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def fresh_aurora_ledger():
    ledger=aur.sentry.load_ledger()
    rows=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        pred,_=aur.run_window(g[g.year.isin([2023,2024,2025])].copy())
        if not pred.empty:rows.append(pred)
    q=pd.concat(rows,ignore_index=True)
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def attach_hourly_momentum(panel):
    x15=m05.load_xau15_extended()
    x1=m05.load_xau1h(x15)
    q0=panel.copy().reset_index(drop=True)
    q0["row_id"]=np.arange(len(q0))
    q=m05.s14.res1h.attach(q0,x1,"g1h","1h")
    need=["g1h_ret_12h","g1h_rv_12","g1h_anchor_available","g1h_max_reference_stale_min"]
    q=q.dropna(subset=need).copy()
    if not (q.g1h_anchor_available<q.start_utc).all():
        raise RuntimeError("OPAL_HOURLY_LEAK")
    if q.g1h_max_reference_stale_min.gt(60).any():
        raise RuntimeError("OPAL_HOURLY_STALE")
    return q

def attach_cot(panel):
    mp=pd.read_csv(COT_MAP)
    mp["target_start_utc"]=pd.to_datetime(mp.target_start_utc,utc=True)
    mp["cot_report_date"]=pd.to_datetime(mp.cot_report_date)
    mp["cot_available_at_utc"]=pd.to_datetime(mp.cot_available_at_utc,utc=True)
    mp["label_date"]=pd.to_datetime(mp.label_date).dt.strftime("%Y-%m-%d")

    q=panel.copy()
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    q=q.merge(
        mp[["label_date","partition","window","target_start_utc","cot_report_date",
            "cot_available_at_utc","cot_availability_reason","cot_age_days_at_start"]],
        left_on=["label_date","partition","window","start_utc"],
        right_on=["label_date","partition","window","target_start_utc"],
        how="inner",validate="one_to_one"
    )
    if not (q.cot_available_at_utc<=q.start_utc).all():
        raise RuntimeError("OPAL_COT_TIME_LEAK")

    cs=pd.read_csv(COT_STATE)
    cs["report_date"]=pd.to_datetime(cs.report_date)
    cs["cot_available_at_utc_state"]=pd.to_datetime(cs.cot_available_at_utc,utc=True)
    keep=["report_date","cot_available_at_utc_state"]+[
        "opt_mm_net","opt_prod_net","opt_swap_net","opt_other_net",
        "d_opt_mm_net","d_opt_prod_net",
        "opt_mm_z52","opt_prod_z52","opt_swap_z52","opt_other_z52",
        "spec_hedger_gap","spec_swap_gap","fut_mm_net","fut_prod_net"
    ]
    q=q.merge(cs[keep],left_on="cot_report_date",right_on="report_date",
              how="inner",validate="many_to_one")
    if not (q.cot_available_at_utc_state<=q.start_utc).all():
        raise RuntimeError("OPAL_COT_STATE_TIME_LEAK")
    return q

def build_panel():
    q=fresh_aurora_ledger()
    q=attach_hourly_momentum(q)
    q=attach_cot(q)

    q["momentum_up"]=(q.g1h_ret_12h>=0).astype(int)
    q["reversal_target"]=(q.y_up.astype(int)!=q.momentum_up.astype(int)).astype(int)
    q["trend_strength"]=q.g1h_ret_12h.abs()/(q.g1h_rv_12+EPS)
    sign=np.where(q.momentum_up.eq(1),1.0,-1.0)
    q["trend_x_opt_mm"]=sign*q.opt_mm_net.astype(float)
    q["trend_x_opt_prod"]=sign*q.opt_prod_net.astype(float)
    q["trend_x_spec_hedger_gap"]=sign*q.spec_hedger_gap.astype(float)
    q["aurora_pred"]=(q.p_aurora>=.5).astype(int)
    q["aurora_follows_momentum"]=q.aurora_pred.eq(q.momentum_up)
    q["year"]=pd.to_datetime(q.start_utc,utc=True).dt.year
    q["month_key"]=pd.to_datetime(q.start_utc,utc=True).dt.to_period("M").astype(str)
    q=q.dropna(subset=FEATURES+["p_aurora","y_up"]).copy()
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def run_window(g,years):
    g=g.sort_values("start_utc").reset_index(drop=True)
    test=g[g.year.isin(years)].copy()
    rows=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key.eq(mo)].copy()
        if te.empty:continue
        cutoff=te.start_utc.min()
        tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
        if len(tr)<MIN_TRAIN or tr.reversal_target.nunique()<2:continue
        sc=StandardScaler().fit(tr[FEATURES].astype(float).to_numpy())
        m=model().fit(sc.transform(tr[FEATURES].astype(float).to_numpy()),
                      tr.reversal_target.astype(int).to_numpy())
        pr=m.predict_proba(sc.transform(te[FEATURES].astype(float).to_numpy()))[:,1]
        for r,p_rev in zip(te.itertuples(index=False),pr):
            follows=bool(r.aurora_follows_momentum)
            override=bool(follows and float(p_rev)>=THRESH)
            p_aur=float(r.p_aurora)
            if override:
                p_opal=float(1-p_rev) if int(r.momentum_up)==1 else float(p_rev)
            else:
                p_opal=p_aur
            rows.append({
                "partition":r.partition,"window":r.window,"label_date":r.label_date,
                "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
                "y_up":int(r.y_up),"p_aurora":p_aur,
                "p_reversal":float(p_rev),"momentum_up":int(r.momentum_up),
                "aurora_follows_momentum":follows,"override":override,
                "p_opal":p_opal,"train_n":int(len(tr)),
                "cot_report_date":str(pd.Timestamp(r.cot_report_date).date()),
                "cot_available_at_utc":str(r.cot_available_at_utc)
            })
    return pd.DataFrame(rows)

def paired_summary(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        ma=metric(g.y_up,g.p_aurora);mo=metric(g.y_up,g.p_opal)
        ad=(g.p_aurora>=.5).astype(int);od=(g.p_opal>=.5).astype(int);y=g.y_up.astype(int)
        ch=ad.ne(od)
        rescued=int((ch&ad.ne(y)&od.eq(y)).sum())
        broken=int((ch&ad.eq(y)&od.ne(y)).sum())
        rows.append({
            "period":period,"partition":part,"window":win,
            "override_n":int(g.override.sum()),"changed_n":int(ch.sum()),
            "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"opal_{k}":v for k,v in mo.items()},
        })
    return pd.DataFrame(rows)

def development_gate(pred):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        reasons=[]
        annual={}
        for yr in [2023,2024]:
            z=g[g.year.eq(yr)]
            if z.empty:continue
            ma=metric(z.y_up,z.p_aurora);mo=metric(z.y_up,z.p_opal)
            annual[yr]=(ma,mo)
            if mo["accuracy"]+.01+1e-12<ma["accuracy"]:reasons.append(f"{yr}_ACC")
            if mo["brier"]>ma["brier"]+.003+1e-12:reasons.append(f"{yr}_BRIER")
        ma=metric(g.y_up,g.p_aurora);mo=metric(g.y_up,g.p_opal)
        ad=(g.p_aurora>=.5).astype(int);od=(g.p_opal>=.5).astype(int);y=g.y_up.astype(int)
        ch=ad.ne(od)
        rescued=int((ch&ad.ne(y)&od.eq(y)).sum())
        broken=int((ch&ad.eq(y)&od.ne(y)).sum())
        net=rescued-broken
        if mo["balanced_accuracy"]+1e-12<ma["balanced_accuracy"]:reasons.append("DEV_BA")
        if min(mo["up_recall"],mo["down_recall"])<.30:reasons.append("RECALL_FLOOR")
        if net<=0:reasons.append("NET_RESCUE_NOT_POSITIVE")
        if int(g.override.sum())==0:reasons.append("NO_OVERRIDE")
        rows.append({
            "partition":part,"window":win,"eligible":len(reasons)==0,
            "reason":"PASS" if not reasons else "|".join(reasons),
            "dev_n":int(len(g)),
            "aurora_ba":ma["balanced_accuracy"],"opal_ba":mo["balanced_accuracy"],
            "opal_up_recall":mo["up_recall"],"opal_down_recall":mo["down_recall"],
            "aurora_brier":ma["brier"],"opal_brier":mo["brier"],
            "override_n":int(g.override.sum()),"rescued":rescued,
            "broken":broken,"net_rescue":net
        })
    return pd.DataFrame(rows)

def main():
    panel=build_panel()

    dev_parts=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        z=run_window(g,[2023,2024])
        if not z.empty:dev_parts.append(z)
    dev=pd.concat(dev_parts,ignore_index=True) if dev_parts else pd.DataFrame()
    if dev.empty:raise RuntimeError("OPAL_NO_DEV_PREDICTIONS")
    gate=development_gate(dev)

    eligible={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}
    tr_parts=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        if (part,win) not in eligible:continue
        z=run_window(g,[2025])
        if not z.empty:tr_parts.append(z)
    tr=pd.concat(tr_parts,ignore_index=True) if tr_parts else pd.DataFrame(columns=dev.columns)

    panel.to_csv(OUT/"panel.csv",index=False)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    paired_summary(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    gate.to_csv(OUT/"eligibility.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        paired_summary(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_OPAL_V1_COMPLETE",
        "threshold":THRESH,"min_train":MIN_TRAIN,"features":FEATURES,
        "upstream":"fresh SESSION AURORA recomputed from corrected session expert ledger",
        "momentum":"canonical pre-target 1h XAU ret_12h and rv_12",
        "cot":"corrected publication-time COT via governed V5 session availability map",
        "development_gate":gate.to_dict("records"),
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "transport_2025_metrics":(
            paired_summary(tr,"FROZEN_2025").to_dict("records") if not tr.empty else []
        ),
        "guardrails":[
            "No archived H3 AURORA/OPAL prediction file used as input.",
            "COT availability uses corrected timestamp authority.",
            "Only matured same-window outcomes train each monthly reversal fit.",
            "18-feature identity, C=1.0, balanced class weighting and threshold 0.70 are frozen.",
            "2025 opened only for heads passing the pre-2025 gate.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION OPAL V1 — RESULT","",
           "## Pre-2025 eligibility","",
           "| Partition | Window | N | AURORA BA | OPAL BA | UP recall | DOWN recall | Overrides | Net rescue | Eligible | Reason |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
            f"{100*r.aurora_ba:.2f}% | {100*r.opal_ba:.2f}% | "
            f"{100*r.opal_up_recall:.2f}% | {100*r.opal_down_recall:.2f}% | "
            f"{int(r.override_n)} | {int(r.net_rescue):+d} | {r.eligible} | {r.reason} |"
        )
    lines += ["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No OPAL head passed the pre-2025 gate; 2025 remained closed.")
    else:
        tm=paired_summary(tr,"FROZEN_2025")
        lines += ["| Partition | Window | N | AURORA BA | OPAL BA | OPAL UP | OPAL DOWN | AURORA Brier | OPAL Brier | Overrides | Net rescue |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {int(r.opal_n)} | "
                f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.opal_balanced_accuracy:.2f}% | "
                f"{100*r.opal_up_recall:.2f}% | {100*r.opal_down_recall:.2f}% | "
                f"{r.aurora_brier:.4f} | {r.opal_brier:.4f} | "
                f"{int(r.override_n)} | {int(r.net_rescue):+d} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
