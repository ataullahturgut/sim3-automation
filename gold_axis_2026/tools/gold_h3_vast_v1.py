from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_HOURLY=AX/"GOLD_H3_VAST_V1_HOURLY_PANEL_2026-10-04.csv"
OUT_ORIGIN=AX/"GOLD_H3_VAST_V1_ORIGIN_FEATURES_2026-10-04.csv"
OUT_PRED=AX/"GOLD_H3_VAST_V1_PREDICTIONS_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_VAST_V1_THRESHOLD_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_VAST_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_VAST_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_VAST_V1_RESULT_2026-10-04.md"

START=pd.Timestamp("2025-01-01",tz="UTC")
END=pd.Timestamp("2026-10-04",tz="UTC")
SEED=20261004
THRESH=[.55,.60,.65,.70]
MIN_TRAIN=60

FEATURES=[
    "gc_flow_3","gc_flow_6","gc_flow_12",
    "gc_opp_vol_share_3","gc_opp_vol_share_6","gc_opp_vol_share_12",
    "gc_efficiency_6","gc_efficiency_12",
    "gc_absorption_6","gc_absorption_12",
    "gc_late_rejection_3","gc_late_rejection_6",
    "gc_opp_climax_z6","gc_with_climax_z6","gc_climax_gap6",
    "si_flow_6","si_flow_12",
    "si_opp_vol_share_6","si_opp_vol_share_12",
    "si_late_rejection_3","gc_si_flow_gap12","joint_opposition_share12",
]

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def fetch(sym,label):
    p1=int(START.timestamp()); p2=int(END.timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        params={"period1":p1,"period2":p2,"interval":"1h","events":"history"}
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"{host} HTTP={r.status_code}"; continue
            z=r.json()["chart"]
            if z.get("error") or not z.get("result"):
                last=f"{host} chart_error={z.get('error')}"; continue
            x=z["result"][0]
            q=x["indicators"]["quote"][0]
            rows=[]
            for i,t in enumerate(x["timestamp"]):
                c=q["close"][i]; v=q["volume"][i]
                if c is None: continue
                cv=float(c)
                vv=0.0 if v is None or not np.isfinite(float(v)) else max(0.0,float(v))
                if cv<=0 or not np.isfinite(cv): continue
                rows.append((pd.to_datetime(t,unit="s",utc=True),cv,vv))
            if len(rows)<3000:
                last=f"{host} too few {len(rows)}"; continue
            return pd.DataFrame(rows,columns=["ts",f"{label}_close",f"{label}_volume"]).drop_duplicates("ts").sort_values("ts")
        except Exception as e:
            last=f"{host}: {type(e).__name__}: {e}"
    raise RuntimeError(f"FETCH_FAIL {sym}: {last}")

def same_hour_volume_z(df,label):
    q=df.copy()
    et=q.ts.dt.tz_convert("America/New_York")
    q["et_hour"]=et.dt.hour
    q[f"{label}_logvol"]=np.log1p(q[f"{label}_volume"].astype(float))
    z=pd.Series(np.nan,index=q.index,dtype=float)
    for hr,idx in q.groupby("et_hour").groups.items():
        ids=list(idx)
        s=q.loc[ids,f"{label}_logvol"]
        prior=s.shift(1)
        mu=prior.rolling(40,min_periods=15).mean()
        sd=prior.rolling(40,min_periods=15).std(ddof=0).replace(0,np.nan)
        z.loc[ids]=(s-mu)/sd
    q[f"{label}_volume_z"]=z
    return q.drop(columns=["et_hour",f"{label}_logvol"])

def build_hourly():
    gc=same_hour_volume_z(fetch("GC=F","GC"),"GC")
    si=same_hour_volume_z(fetch("SI=F","SI"),"SI")
    x=gc.merge(si,on="ts",how="inner").sort_values("ts").reset_index(drop=True)
    x["GC_ret1"]=np.log(x.GC_close).diff()
    x["SI_ret1"]=np.log(x.SI_close).diff()
    return x

def cutoff_ts(d):
    return (pd.Timestamp(d.date()).tz_localize("America/New_York")+pd.Timedelta(hours=16)).tz_convert("UTC")

def efficiency(ret):
    den=float(np.abs(ret).sum())
    if den<=1e-12: return 0.0
    return float(abs(ret.sum())/den)

def vol_flow(ret,vol,s):
    den=float(vol.sum())
    if den<=0: return 0.0
    return float(s*np.sum(ret*vol)/den)

def opp_share(ret,vol,s):
    den=float(vol.sum())
    if den<=0: return 0.0
    mask=(s*ret)<0
    return float(vol[mask].sum()/den)

def climax(ret,vz,s,opp=True):
    mask=((s*ret)<0) if opp else ((s*ret)>=0)
    a=vz[mask]
    a=a[np.isfinite(a)]
    if len(a)==0: return 0.0
    return float(max(0.0,np.max(a)))

def origin_features(hourly):
    h3=pd.read_csv(H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        h3[c]=pd.to_datetime(h3[c])
    h3=h3[h3.eligible_v5_continuation.astype(bool)].copy()
    h3=h3[h3.forecast_issue_date>=pd.Timestamp("2025-01-01")].sort_values("forecast_issue_date")

    rows=[]
    for r in h3.itertuples():
        co=cutoff_ts(pd.Timestamp(r.feature_cutoff_date))
        w=hourly[(hourly.ts<=co)&(hourly.ts>=co-pd.Timedelta(hours=18))].tail(12).copy()
        if len(w)<12: continue
        if (co-w.ts.iloc[-1]).total_seconds()/3600.0>3.0: continue
        if (w.ts.iloc[-1]-w.ts.iloc[0]).total_seconds()/3600.0>18.0: continue
        if w[["GC_ret1","SI_ret1","GC_volume_z","SI_volume_z"]].isna().any(axis=None): continue

        s=1.0 if int(r.momentum_up)==1 else -1.0
        d=r._asdict()

        for h in [3,6,12]:
            z=w.tail(h)
            d[f"gc_flow_{h}"]=vol_flow(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)
            d[f"gc_opp_vol_share_{h}"]=opp_share(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)

        for h in [6,12]:
            z=w.tail(h)
            eff=efficiency(z.GC_ret1.to_numpy())
            d[f"gc_efficiency_{h}"]=eff
            posz=np.maximum(z.GC_volume_z.to_numpy(float),0.0)
            d[f"gc_absorption_{h}"]=float(np.mean(posz)*(1-eff))

        d["gc_late_rejection_3"]=float(-s*w.GC_ret1.tail(3).sum())
        d["gc_late_rejection_6"]=float(-s*w.GC_ret1.tail(6).sum())
        z6=w.tail(6)
        opp=climax(z6.GC_ret1.to_numpy(),z6.GC_volume_z.to_numpy(),s,True)
        withc=climax(z6.GC_ret1.to_numpy(),z6.GC_volume_z.to_numpy(),s,False)
        d["gc_opp_climax_z6"]=opp
        d["gc_with_climax_z6"]=withc
        d["gc_climax_gap6"]=opp-withc

        for h in [6,12]:
            z=w.tail(h)
            d[f"si_flow_{h}"]=vol_flow(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)
            d[f"si_opp_vol_share_{h}"]=opp_share(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)

        d["si_late_rejection_3"]=float(-s*w.SI_ret1.tail(3).sum())
        d["gc_si_flow_gap12"]=float(d["gc_flow_12"]-d["si_flow_12"])
        d["joint_opposition_share12"]=float((d["gc_opp_vol_share_12"]+d["si_opp_vol_share_12"])/2.0)
        d["hourly_last_ts"]=w.ts.iloc[-1]
        rows.append(d)

    q=pd.DataFrame(rows)
    q["month_key"]=q.forecast_issue_date.dt.to_period("M").astype(str)
    return q.sort_values("forecast_issue_date").reset_index(drop=True)

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("logit",LogisticRegression(
            C=.5,solver="lbfgs",class_weight="balanced",
            max_iter=3000,random_state=SEED
        ))
    ])

def walk(panel):
    test=panel[panel.forecast_issue_date>=pd.Timestamp("2025-04-01")].copy()
    out=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].dropna(subset=FEATURES).copy()
        if te.empty: continue
        cutoff=te.feature_cutoff_date.min()
        issue=te.forecast_issue_date.min()
        tr=panel[
            (panel.target_end_date_h3<=cutoff)
            & (panel.forecast_issue_date<issue)
        ].dropna(subset=FEATURES+["rescue_target"]).copy()
        if len(tr)<MIN_TRAIN or tr.rescue_target.nunique()<2: continue
        m=model()
        m.fit(tr[FEATURES].to_numpy(float),tr.rescue_target.astype(int))
        p=m.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        for rr,pp in zip(te.itertuples(),p):
            out.append({
                "feature_cutoff_date":rr.feature_cutoff_date,
                "forecast_issue_date":rr.forecast_issue_date,
                "target_end_date_h3":rr.target_end_date_h3,
                "year":int(rr.year),"month":str(rr.month),
                "y_up":int(rr.y_up),"target_r3":float(rr.target_r3),
                "v5_pred":int(rr.v5_pred),"rescue_target":int(rr.rescue_target),
                "opal_override_check":rr.opal_override_check,
                "p_vast_reversal":float(pp),"train_n":len(tr)
            })
    return pd.DataFrame(out).sort_values("forecast_issue_date").reset_index(drop=True)

def block_name(ts):
    t=pd.Timestamp(ts)
    return f"{t.year}_{'H1' if t.month<=6 else 'H2'}"

def metr(g,th):
    c=g.p_vast_reversal>=th
    y=g.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "threshold":th,"eligible_n":len(g),"candidate_n":n,
        "rescued":r,"broken":b,"net":r-b,
        "precision":r/max(n,1),
        "recall":r/max(int(y.sum()),1),
        "candidate_rate":n/max(len(g),1)
    }

def separation(panel):
    out=[]
    panel=panel.copy(); panel["block"]=panel.forecast_issue_date.map(block_name)
    for name,g in panel.groupby("block",sort=False):
        r=g[g.rescue_target==1]; c=g[g.rescue_target==0]
        feats={}
        for f in FEATURES:
            a=r[f].dropna().to_numpy(float); b=c[f].dropna().to_numpy(float)
            if len(a)>1 and len(b)>1:
                sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
                sm=(np.mean(a)-np.mean(b))/sp if sp>0 else np.nan
            else: sm=np.nan
            feats[f]=float(sm) if np.isfinite(sm) else None
        out.append({"block":name,"n":len(g),"reversals":int(g.rescue_target.sum()),"feature_smd":feats})
    return out

def main():
    hourly=build_hourly()
    hourly.to_csv(OUT_HOURLY,index=False)
    feat=origin_features(hourly)
    feat.to_csv(OUT_ORIGIN,index=False)
    pred=walk(feat)
    pred.to_csv(OUT_PRED,index=False)

    score_blocks=["2025_H2","2026_H1","2026_H2"]
    pp=pred.copy(); pp["block"]=pp.forecast_issue_date.map(block_name)
    scored=pp[pp.block.isin(score_blocks)].copy()

    grid=[]; blockrows=[]
    for th in THRESH:
        agg=metr(scored,th)
        bl=[]
        for name,g in scored.groupby("block",sort=False):
            x=metr(g,th); x["block"]=name; bl.append(x)
        pos=sum(1 for x in bl if x["net"]>0)
        worst=min([x["net"] for x in bl],default=0)
        agg["positive_blocks"]=pos; agg["worst_block_net"]=worst
        agg["eligible"]=bool(
            agg["candidate_n"]>=10 and agg["net"]>0
            and agg["precision"]>=.55 and pos>=2 and worst>=-2
        )
        grid.append(agg); blockrows.extend(bl)

    gdf=pd.DataFrame(grid); bdf=pd.DataFrame(blockrows)
    gdf.to_csv(OUT_GRID,index=False); bdf.to_csv(OUT_BLOCK,index=False)

    elig=gdf[gdf.eligible].copy()
    selected=None
    if elig.empty:
        status="NO_ELIGIBLE_VAST_V1_MECHANISM"
    else:
        elig=elig.sort_values(
            ["net","precision","rescued","candidate_n","threshold"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].threshold)
        status="VAST_V1_MECHANISM_PASS"

    sep=separation(feat[feat.forecast_issue_date>=pd.Timestamp("2025-07-01")])
    summary={
        "schema":"VAST_H3_V1","status":status,
        "hourly_rows":len(hourly),"origin_feature_rows":len(feat),
        "prediction_rows":len(pred),"selected_threshold":selected,
        "threshold_grid":grid,"separation":sep
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# VAST-H3 V1 — VOLUME ABSORPTION & SESSION TRANSITION RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective hourly-volume mechanism; 2026 is development only.","",
        f"- synchronized hourly rows: **{len(hourly)}**",
        f"- origin feature rows: **{len(feat)}**",
        f"- expanding-origin predictions: **{len(pred)}**","",
        "## Frozen threshold grid","",
        "| Th | Cand | Rescue | Broken | Net | Precision | Recall | Rate | + blocks | Worst | Eligible |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for x in grid:
        lines.append(
            f"| {x['threshold']:.2f} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | "
            f"{100*x['precision']:.2f}% | {100*x['recall']:.2f}% | {100*x['candidate_rate']:.2f}% | "
            f"{x['positive_blocks']} | {x['worst_block_net']:+d} | {x['eligible']} |"
        )

    if selected is not None:
        q=bdf[np.isclose(bdf.threshold,selected)]
        lines += ["",f"## Selected threshold: {selected:.2f}","",
                  "| Block | Cand | Rescue | Broken | Net | Precision | Recall |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
        for r in q.itertuples():
            lines.append(f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% | {100*r.recall:.2f}% |")

    # largest absolute SMD per block for interpretability
    lines += ["","## Strongest feature separations by block",""]
    for x in sep:
        vals=[(k,v) for k,v in x["feature_smd"].items() if v is not None]
        vals=sorted(vals,key=lambda kv:abs(kv[1]),reverse=True)[:5]
        lines.append(f"### {x['block']} (n={x['n']}, reversals={x['reversals']})")
        for k,v in vals:
            lines.append(f"- {k}: SMD **{v:+.3f}**")
        lines.append("")

    lines += ["## Governance","",
              "No historical result here is a clean 2026 holdout claim. Yahoo hourly volume is a research proxy. "
              "HELIOS V5-DCE remains binding unless a separately frozen prospective challenger earns promotion."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: vast-v1-workflow-ready
