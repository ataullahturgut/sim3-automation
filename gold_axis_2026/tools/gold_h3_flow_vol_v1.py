from __future__ import annotations
import json, math, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import brier_score_loss, log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
OUT_PRED=AX/"GOLD_H3_FLOW_VOL_V1_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_FLOW_VOL_V1_THRESHOLD_GRID_2026-10-03.csv"
OUT_SRC=AX/"GOLD_H3_FLOW_VOL_V1_SOURCE_2026-10-03.csv"
OUT_JSON=AX/"GOLD_H3_FLOW_VOL_V1_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_FLOW_VOL_V1_RESULT_2026-10-03.md"

SEED=20261003
THRESH_GRID=[0.35,0.40,0.45,0.50,0.55]
FEATURES=["dlog_volume_1","volume_z20","volume_ratio_20","volume_accel_5",
          "momentum_x_dlog_volume","momentum_x_volume_z20"]

def fetch_yahoo():
    start=int(pd.Timestamp("2021-01-01",tz="UTC").timestamp())
    end=int(pd.Timestamp("2026-10-03",tz="UTC").timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/GC=F"
        params={"period1":start,"period2":end,"interval":"1d","events":"history","includeAdjustedClose":"true"}
        try:
            r=requests.get(url,params=params,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},timeout=60)
            if r.status_code!=200:
                last=f"{host} HTTP {r.status_code}: {r.text[:300]}"
                continue
            j=r.json()
            res=j["chart"]["result"][0]
            ts=res["timestamp"]
            q=res["indicators"]["quote"][0]
            rows=[]
            for i,t in enumerate(ts):
                v=q["volume"][i]
                if v is None or float(v)<=0: continue
                d=pd.to_datetime(t,unit="s",utc=True).tz_convert("America/New_York").date()
                rows.append({"trade_date":pd.Timestamp(d),"volume":float(v),"source_host":host})
            x=pd.DataFrame(rows).drop_duplicates("trade_date",keep="last").sort_values("trade_date").reset_index(drop=True)
            if len(x)<500:
                last=f"{host} too few rows {len(x)}"
                continue
            return x,{"status":"PASS","host":host,"rows":len(x),"url":r.url}
        except Exception as e:
            last=f"{host} {type(e).__name__}: {e}"
    return None,{"status":"SOURCE_BLOCKED","error":last}

def build_source_features(x):
    x=x.copy()
    x["logv"]=np.log(x.volume)
    x["dlog_volume_1"]=x.logv.diff()
    mu=x.logv.shift(1).rolling(20,min_periods=10).mean()
    sd=x.logv.shift(1).rolling(20,min_periods=10).std(ddof=0)
    x["volume_z20"]=(x.logv-mu)/sd.replace(0,np.nan)
    x["volume_ratio_20"]=x.volume/x.volume.shift(1).rolling(20,min_periods=10).mean()
    x["volume_accel_5"]=x.dlog_volume_1-x.dlog_volume_1.shift(1).rolling(5,min_periods=3).mean()
    return x.dropna(subset=["dlog_volume_1","volume_z20","volume_ratio_20","volume_accel_5"]).reset_index(drop=True)

def align(panel,src):
    p=panel.copy()
    p["feature_cutoff_date"]=pd.to_datetime(p.feature_cutoff_date)
    p["forecast_issue_date"]=pd.to_datetime(p.forecast_issue_date)
    p["target_end_date_h3"]=pd.to_datetime(p.target_end_date_h3)
    s=src.sort_values("trade_date").copy()
    rows=[]
    for r in p.itertuples():
        z=s[s.trade_date < r.feature_cutoff_date]
        if z.empty: continue
        q=z.iloc[-1]
        sign=1.0 if int(r.momentum_up)==1 else -1.0
        d=r._asdict()
        for c in ["trade_date","volume","dlog_volume_1","volume_z20","volume_ratio_20","volume_accel_5"]:
            d["flow_"+c]=q[c]
        d["dlog_volume_1"]=float(q.dlog_volume_1)
        d["volume_z20"]=float(q.volume_z20)
        d["volume_ratio_20"]=float(q.volume_ratio_20)
        d["volume_accel_5"]=float(q.volume_accel_5)
        d["momentum_x_dlog_volume"]=sign*float(q.dlog_volume_1)
        d["momentum_x_volume_z20"]=sign*float(q.volume_z20)
        rows.append(d)
    a=pd.DataFrame(rows)
    a["month_key"]=a.forecast_issue_date.dt.to_period("M").astype(str)
    return a

def model():
    return Pipeline([("scale",StandardScaler()),("model",LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=3000,class_weight="balanced",random_state=SEED
    ))])

def walk(panel):
    test=panel[panel.forecast_issue_date>=pd.Timestamp("2023-01-01")].copy()
    out=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=panel[(panel.target_end_date_h3<=cutoff)&(panel.forecast_issue_date<first_issue)].copy()
        tr=tr.dropna(subset=FEATURES+["reversal_target"])
        if len(tr)<80 or tr.reversal_target.nunique()<2: continue
        m=model(); m.fit(tr[FEATURES].to_numpy(float),tr.reversal_target.astype(int).to_numpy())
        pr=m.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        for r,pv in zip(te.itertuples(),pr):
            out.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),"y_up":int(r.y_up),
                "target_r3":float(r.target_r3),"p_aurora":float(r.p_aurora),
                "momentum_up":int(r.momentum_up),"reversal_target":int(r.reversal_target),
                "aurora_pred":int(r.aurora_pred),"aurora_follows_momentum":bool(r.aurora_follows_momentum),
                "flow_trade_date":r.flow_trade_date,"flow_volume":float(r.flow_volume),
                "p_flow_reversal":float(pv),"train_n":int(len(tr))
            })
    return pd.DataFrame(out).sort_values("forecast_issue_date").reset_index(drop=True)

def f2(p,r):
    if p<=0 or r<=0: return 0.0
    return 5*p*r/(4*p+r)

def cand_metrics(z,th):
    e=z[z.aurora_follows_momentum.astype(bool)].copy()
    c=e.p_flow_reversal>=th
    y=e.reversal_target.astype(bool)
    tp=int((c&y).sum()); fp=int((c&~y).sum()); fn=int((~c&y).sum())
    precision=tp/max(tp+fp,1); recall=tp/max(tp+fn,1); rate=float(c.mean()) if len(c) else 0.0
    return {"threshold":th,"eligible_n":len(e),"candidate_n":int(c.sum()),"true_reversal_n":int(y.sum()),
            "tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"candidate_rate":rate,
            "f2":f2(precision,recall),"eligible":bool(precision>=.45 and rate<=.35)}

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def merge_opal(pred):
    v=pd.read_csv(V5)
    v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date)
    keep=["feature_cutoff_date","p_helios_v5_dce","opal_override_check"]
    z=pred.merge(v[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z

def period_stats(z,th,year):
    q=z[(z.year==year)&z.aurora_follows_momentum.astype(bool)].copy()
    q["flow_candidate"]=q.p_flow_reversal>=th
    y=q.reversal_target.astype(bool)
    c=q.flow_candidate.astype(bool)
    tp=int((c&y).sum()); fp=int((c&~y).sum())
    precision=tp/max(tp+fp,1); recall=tp/max(int(y.sum()),1); rate=float(c.mean()) if len(c) else 0
    op=q.opal_candidate.astype(bool)
    op_tp=int((op&y).sum()); op_rec=op_tp/max(int(y.sum()),1); op_prec=op_tp/max(int(op.sum()),1)
    flow_only_true=int((c&y&~op).sum())
    union=(c|op); union_rec=float((union&y).sum()/max(int(y.sum()),1))
    brier=float(np.mean((q.p_flow_reversal-q.reversal_target)**2)) if len(q) else np.nan
    ll=float(log_loss(q.reversal_target,np.clip(q.p_flow_reversal,1e-6,1-1e-6),labels=[0,1])) if len(q) else np.nan
    return {"year":year,"eligible_n":len(q),"true_reversal_n":int(y.sum()),"flow_candidate_n":int(c.sum()),
            "flow_precision":precision,"flow_recall":recall,"flow_candidate_rate":rate,
            "opal_candidate_n":int(op.sum()),"opal_precision":op_prec,"opal_recall":op_rec,
            "flow_only_true_reversal_n":flow_only_true,"union_recall":union_rec,"brier":brier,"logloss":ll}

def main():
    raw,meta=fetch_yahoo()
    if raw is None:
        OUT_JSON.write_text(json.dumps({"schema":"FLOW_VOL_H3_V1","status":"SOURCE_BLOCKED","source":meta},indent=2)+"\n")
        OUT_MD.write_text("# FLOW-VOL-H3 V1 RESULT\n\n**Status: SOURCE_BLOCKED**\n\n"+str(meta)+"\n")
        print(OUT_MD.read_text()); return
    src=build_source_features(raw)
    src.to_csv(OUT_SRC,index=False)
    panel=pd.read_csv(PANEL)
    a=align(panel,src)
    pred=walk(a)
    if pred.empty:
        raise RuntimeError("NO_PREDICTIONS")
    pred=merge_opal(pred)
    dev=pred[pred.year.isin([2023,2024])].copy()
    grid=pd.DataFrame([cand_metrics(dev,t) for t in THRESH_GRID])
    grid.to_csv(OUT_GRID,index=False)
    elig=grid[grid.eligible].copy()
    if elig.empty:
        status="NO_ELIGIBLE_FLOW_VOL_THRESHOLD"; selected=None
        confirm=None; holdout=None
    else:
        elig=elig.sort_values(["f2","recall","precision","candidate_rate","threshold"],ascending=[False,False,False,True,False])
        selected=float(elig.iloc[0].threshold)
        s25=period_stats(pred,selected,2025)
        confirm=bool(s25["flow_recall"]>s25["opal_recall"] and s25["flow_only_true_reversal_n"]>=1 and s25["flow_precision"]>=.40)
        status="CONFIRM_PASS" if confirm else "CONFIRM_FAIL"
        holdout=period_stats(pred,selected,2026) if confirm else None
        if confirm:
            z=pred[(pred.year==2026)&pred.aurora_follows_momentum.astype(bool)].copy()
            z["flow_candidate"]=z.p_flow_reversal>=selected
            miss=(z.reversal_target==1)&(z.v5_pred==z.momentum_up)&(~z.opal_candidate)
            known=int(miss.sum())
            hit=int((miss&z.flow_candidate).sum())
            flow_dir=1-z.momentum_up.astype(int)
            changed=z.flow_candidate & (flow_dir!=z.v5_pred)
            rescue=int((changed&(z.v5_pred!=z.y_up)&(flow_dir==z.y_up)).sum())
            broken=int((changed&(z.v5_pred==z.y_up)&(flow_dir!=z.y_up)).sum())
            holdout.update({"v5_missed_reversal_opal_no_candidate_n":known,
                            "flow_hits_in_v5_missed_opal_no_candidate":hit,
                            "diagnostic_v5_rescue":rescue,"diagnostic_v5_broken":broken,
                            "diagnostic_v5_net":rescue-broken})
    pred.to_csv(OUT_PRED,index=False)
    summ={"schema":"FLOW_VOL_H3_V1","status":status,"source":meta,"source_rows":len(src),
          "selected_threshold":selected,"threshold_grid":grid.to_dict("records"),
          "confirmation_2025":period_stats(pred,selected,2025) if selected is not None else None,
          "confirmation_pass":confirm,"holdout_2026":holdout}
    OUT_JSON.write_text(json.dumps(summ,indent=2,default=str)+"\n")
    lines=["# FLOW-VOL-H3 V1 — RESULT","",f"**Status:** **{status}**  ",
           f"**Source:** Yahoo Finance GC=F daily volume proxy, host {meta.get('host')}  ",
           "**PIT:** strict prior-trade-date volume only; same-day forbidden.","",
           "## DEV threshold grid","",
           "| Threshold | Candidate | Precision | Recall | Rate | F2 | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.threshold:.2f} | {r.candidate_n} | {100*r.precision:.2f}% | {100*r.recall:.2f}% | {100*r.candidate_rate:.2f}% | {r.f2:.4f} | {r.eligible} |")
    if selected is not None:
        s25=period_stats(pred,selected,2025)
        lines+=["",f"## Selected threshold: {selected:.2f}","",
                "## 2025 confirmation","",
                f"- FLOW recall: **{100*s25['flow_recall']:.2f}%**",
                f"- OPAL recall same universe: **{100*s25['opal_recall']:.2f}%**",
                f"- FLOW precision: **{100*s25['flow_precision']:.2f}%**",
                f"- FLOW-only true OPAL-missed reversals: **{s25['flow_only_true_reversal_n']}**",
                f"- Candidate-union recall: **{100*s25['union_recall']:.2f}%**",
                f"- Confirmation: **{'PASS' if confirm else 'FAIL'}**"]
        if confirm and holdout is not None:
            h=holdout
            lines+=["","## 2026 final holdout","",
                    f"- FLOW recall: **{100*h['flow_recall']:.2f}%**",
                    f"- FLOW precision: **{100*h['flow_precision']:.2f}%**",
                    f"- OPAL recall same universe: **{100*h['opal_recall']:.2f}%**",
                    f"- OPAL ∪ FLOW recall: **{100*h['union_recall']:.2f}%**",
                    f"- V5 missed reversal + OPAL no-candidate universe reconstructed: **{h['v5_missed_reversal_opal_no_candidate_n']}**",
                    f"- FLOW candidates inside that universe: **{h['flow_hits_in_v5_missed_opal_no_candidate']}**",
                    f"- Diagnostic forced-route rescue / broken / net: **{h['diagnostic_v5_rescue']} / {h['diagnostic_v5_broken']} / {h['diagnostic_v5_net']:+d}**"]
    lines+=["","## Governance","",
            "FLOW-VOL is an ablation only. It does not replace the blocked official Volume+OI FLOW-H3 V1 and does not alter HELIOS V5-DCE. 2026 was opened only if the preregistered 2025 confirmation gate passed."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
