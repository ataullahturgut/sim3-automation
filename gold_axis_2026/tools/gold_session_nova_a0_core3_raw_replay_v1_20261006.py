from __future__ import annotations

import hashlib
import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW15=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
OUT=AX/"SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_OUT"; OUT.mkdir(exist_ok=True)

STAK_REPO="lbruton/StakTrakr"
STAK_REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"
METALS={"gold":"Gold","silver":"Silver","platinum":"Platinum"}
YEARS=range(2010,2025)
SEED=20261006
BLOCK=5
MIN_TRAIN=120

GOLD_ONLY=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
CORE3=GOLD_ONLY+[
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"gold-session-nova-a0-raw/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def load_raw_metals():
    by=defaultdict(dict); hashes={}
    for year in YEARS:
        url=f"https://raw.githubusercontent.com/{STAK_REPO}/{STAK_REF}/data/spot-history-{year}.json"
        raw=get_bytes(url)
        hashes[str(year)]=hashlib.sha256(raw).hexdigest()
        rows=json.loads(raw)
        for rec in rows:
            metal=str(rec.get("metal") or "")
            if metal not in METALS.values():
                continue
            ts=pd.to_datetime(rec.get("timestamp"),errors="coerce")
            if pd.isna(ts):
                continue
            d=ts.normalize()
            if d.weekday()>=5:
                continue
            try:
                v=float(rec.get("spot"))
            except Exception:
                continue
            if not np.isfinite(v) or v<=0:
                continue
            by[metal][d]=v

    common=sorted(set.intersection(*(set(by[m]) for m in METALS.values())))
    if not common:
        raise RuntimeError("NO_COMMON_METAL_DATES")
    q=pd.DataFrame({"obs_date":common})
    for key,metal in METALS.items():
        q[key]=[by[metal][d] for d in common]

    # Exact historical CORE3 transform.
    lg=np.log(q["gold"].astype(float))
    for h in [1,3,5,10,21]:
        q[f"gold_r{h}"]=lg.diff(h)
    q["sigma20"]=lg.diff().rolling(20).std(ddof=0)

    for name in ["silver","platinum"]:
        lp=np.log(q[name].astype(float))
        for h in [1,5,21]:
            q[f"{name}_r{h}"]=lp.diff(h)
        # All three metals share common retained dates in this raw reconstruction.
        q[f"{name}_age_days"]=0.0

    q=q.dropna(subset=CORE3).sort_values("obs_date").reset_index(drop=True)
    return q,hashes

def verify_v5_targets():
    raw=pd.read_csv(RAW15)
    raw["dt_utc"]=pd.to_datetime(raw["dt_utc"],utc=True)
    op=dict(zip(raw["dt_utc"],pd.to_numeric(raw["open"],errors="raise")))
    cl=dict(zip(raw["dt_utc"],pd.to_numeric(raw["close"],errors="raise")))

    frames=[]
    for p in [WGC,SOB]:
        z=pd.read_csv(p)
        z=z[z["final_trainable"].astype(str).str.lower().eq("true")].copy()
        frames.append(z)
    q=pd.concat(frames,ignore_index=True)

    errs=[]
    for _,r in q.iterrows():
        s=pd.Timestamp(r["start_utc"])
        e=pd.Timestamp(r["end_utc"])
        ep=e-pd.Timedelta(minutes=15)
        ps=op.get(s); pe=cl.get(ep)
        if ps is None or pe is None:
            errs.append((r["label_date"],r["partition"],r["window"],"RAW_BOUNDARY_MISSING")); continue
        ret=pe/ps-1.0
        direction="UP" if ret>0 else ("DOWN" if ret<0 else "FLAT")
        if abs(float(r["start_price"])-float(ps))>1e-9: errs.append((r["label_date"],r["partition"],r["window"],"START_PRICE"))
        if abs(float(r["end_price"])-float(pe))>1e-9: errs.append((r["label_date"],r["partition"],r["window"],"END_PRICE"))
        if abs(float(r["return"])-float(ret))>1e-12: errs.append((r["label_date"],r["partition"],r["window"],"RETURN"))
        if str(r["direction"])!=direction: errs.append((r["label_date"],r["partition"],r["window"],"DIRECTION"))
    if errs:
        raise RuntimeError(f"V5_RECON_FAIL n={len(errs)} sample={errs[:10]}")
    return q

def align_daily_features(targets,metals):
    t=targets.copy()
    t["start_utc"]=pd.to_datetime(t["start_utc"],utc=True)
    t["end_utc"]=pd.to_datetime(t["end_utc"],utc=True)
    t["start_ny"]=t["start_utc"].dt.tz_convert("America/New_York")
    t["start_ny_date"]=t["start_ny"].dt.tz_localize(None).dt.normalize()

    # Conservative source-ready rule:
    # Stak daily labels have no proven intraday publication time, so a session
    # may only use an observation from a strictly earlier NY calendar date.
    t["daily_cutoff_date"]=t["start_ny_date"]-pd.Timedelta(days=1)

    m=metals.copy().sort_values("obs_date")
    out=pd.merge_asof(
        t.sort_values("daily_cutoff_date"),
        m,
        left_on="daily_cutoff_date",
        right_on="obs_date",
        direction="backward"
    )
    out["daily_age_days"]=(out["start_ny_date"]-out["obs_date"]).dt.days
    if (out["obs_date"]>=out["start_ny_date"]).any():
        raise RuntimeError("DAILY_FEATURE_LEAK")
    out["y_up"]=(out["direction"]=="UP").astype(int)
    return out.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def mdl():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
    ])

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp),
        "prediction_std":float(np.std(p)),
    }

def replay_window(g):
    g=g.sort_values("start_utc").reset_index(drop=True)
    test=g[g["start_utc"].dt.year.isin([2023,2024])].copy()
    rows=[]
    for bs in range(0,len(test),BLOCK):
        te=test.iloc[bs:bs+BLOCK].copy()
        if te.empty: continue
        first_start=te["start_utc"].min()
        tr=g[
            (g["end_utc"]<=first_start)
            & (g["start_utc"]<first_start)
            & (g["start_utc"].dt.year.isin([2023,2024]))
        ].copy()
        if len(tr)<MIN_TRAIN:
            continue
        Xtr=tr[CORE3].astype(float)
        Xte=te[CORE3].astype(float)
        ytr=tr["y_up"].to_numpy(int)
        model=mdl(); model.fit(Xtr,ytr)
        p=model.predict_proba(Xte)[:,1]
        for r,pp in zip(te.itertuples(index=False),p):
            rows.append({
                "label_date":r.label_date,
                "partition":r.partition,
                "window":r.window,
                "start_utc":r.start_utc.isoformat(),
                "end_utc":r.end_utc.isoformat(),
                "feature_obs_date":pd.Timestamp(r.obs_date).date().isoformat(),
                "daily_age_days":int(r.daily_age_days),
                "year":int(r.start_utc.year),
                "y_up":int(r.y_up),
                "direction":r.direction,
                "p_up":float(pp),
                "pred":"UP" if pp>=.5 else "DOWN",
                "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows)

def main():
    metals,annual_hashes=load_raw_metals()
    targets=verify_v5_targets()
    # 2025 remains unopened in Stage-1 development replay.
    targets=targets[pd.to_datetime(targets["label_date"]).dt.year.isin([2023,2024])].copy()
    panel=align_daily_features(targets,metals)
    panel=panel.dropna(subset=CORE3+["direction","obs_date"]).copy()

    preds=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        z=replay_window(g)
        if not z.empty:
            preds.append(z)
    pred=pd.concat(preds,ignore_index=True) if preds else pd.DataFrame()

    mrows=[]
    if not pred.empty:
        for (part,win,yr),g in pred.groupby(["partition","window","year"],sort=True):
            mrows.append({"partition":part,"window":win,"period":str(yr),**metrics(g["y_up"],g["p_up"])})
        for (part,win),g in pred.groupby(["partition","window"],sort=True):
            mrows.append({"partition":part,"window":win,"period":"2023-2024_SCORED",**metrics(g["y_up"],g["p_up"])})
    mdf=pd.DataFrame(mrows)

    coverage=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        pp=pred[(pred["partition"]==part)&(pred["window"]==win)] if not pred.empty else pd.DataFrame()
        coverage.append({
            "partition":part,"window":win,
            "feature_rows_2023_2024":int(len(g)),
            "scored_rows":int(len(pp)),
            "first_feature_start":None if g.empty else str(g["start_utc"].min()),
            "first_scored_start":None if pp.empty else str(pp["start_utc"].min()),
            "last_scored_start":None if pp.empty else str(pp["start_utc"].max()),
            "median_daily_age_days":float(g["daily_age_days"].median()) if len(g) else None,
            "max_daily_age_days":int(g["daily_age_days"].max()) if len(g) else None,
        })

    panel.to_csv(OUT/"nova_a0_core3_raw_feature_panel_2023_2024.csv",index=False)
    pred.to_csv(OUT/"nova_a0_core3_raw_predictions_2023_2024.csv",index=False)
    mdf.to_csv(OUT/"nova_a0_core3_raw_metrics_2023_2024.csv",index=False)

    summary={
        "status":"NOVA_A0_CORE3_RAW_SESSION_REPLAY_V1_COMPLETE",
        "model_role":"STAGE1_PRIMARY_DIRECTION_ENGINE",
        "model":"NOVA A0 / CORE3 / Logistic L2",
        "raw_daily_source":{
            "repo":STAK_REPO,"ref":STAK_REF,
            "years":[min(YEARS),max(YEARS)],
            "annual_payload_sha256":annual_hashes,
            "common_feature_first":str(metals["obs_date"].min().date()),
            "common_feature_last":str(metals["obs_date"].max().date()),
            "feature_rows":int(len(metals)),
        },
        "daily_source_ready_rule":"Use only the latest common Gold/Silver/Platinum daily observation from a strictly earlier America/New_York calendar date than session start because intraday publication time of the daily label is not proven.",
        "target_raw_15m":RAW15.name,
        "target_raw_15m_sha256":sha(RAW15),
        "target_reproduction":"PASS",
        "development_scope":"2023-2024 only; 2025 unopened",
        "training":{"block":BLOCK,"min_matured_same_window_train":MIN_TRAIN,"features":CORE3},
        "coverage":coverage,
        "metrics":mdf.to_dict("records"),
        "guardrails":[
            "No readiness FEATURE_PANEL or historical NOVA PREDICTIONS used as model input.",
            "CORE3 transforms reconstructed from pinned raw daily metal payloads.",
            "Same-day daily metal observation prohibited for all sessions.",
            "Only matured same-window session outcomes enter training.",
            "2025 and 2026 outcomes not used."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# NOVA A0 / CORE3 — RAW SESSION REPLAY V1","",
        "**Status:** completed from raw daily metals + raw 15m targets.","",
        "- model role: Stage-1 primary direction engine",
        "- 2023–2024 only; 2025 unopened",
        "- same-day daily metal values: prohibited",
        "- V5 raw target reproduction: PASS","",
        "## Metrics","",
        "| Partition | Window | Period | N | Accuracy | Balanced | UP recall | DOWN recall | Brier |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {r.period} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
