"""2020-2025 historical-length experiment on EXISTING LIT model identities.
No PRAMV upgrade, no 2025 tuning, no 2026 leakage. Private XAU bars never exported.
Features/labels follow gold_execution_lit_stage1_20261007.py exactly.
"""
from __future__ import annotations
import json, os, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, brier_score_loss
from scipy.stats import binomtest

AX=Path(__file__).resolve().parents[1]
RESULT=AX/"GOLD_EXECUTION_LONG_HISTORY_LIT_RESULT_2026-10-08.md"
SUMMARY=AX/"GOLD_EXECUTION_LONG_HISTORY_LIT_SUMMARY_2026-10-08.json"
SCORES=AX/"GOLD_EXECUTION_LONG_HISTORY_LIT_METRICS_2026-10-08.csv"
# 2023/2024 DEV were previously inspected, 2025 retrospected; not pristine future.
FEATURES={
 "LIT_OVN0_1600_1630":("OVN",["r1600_1630"]),
 "LIT_OVN1_PAIR":("OVN",["r1600_1630","r1630_1700","pair_inter","pair_same"]),
 "LIT_DAY0_EXEC_0900":("DAY",["r0800_0830","r0830_0900","prev_ovn"])
}
HORIZONS={"SHORT_2022_PLUS":2022,"LONG_2020_PLUS":2020}
MIN_TRAIN=80

def native_2022_25():
    a=pd.read_csv(AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",
      usecols=["dt_utc","open","close"],low_memory=False)
    b=pd.read_csv(AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv",
      usecols=["dt_utc","open","close"],low_memory=False)
    for frame in (a,b):
        frame["ts"]=pd.to_datetime(frame.dt_utc,utc=True,errors="raise")
    a=a[(a.ts>="2022-01-01")&(a.ts<"2023-01-01")]
    b=b[(b.ts>="2023-01-01")&(b.ts<"2026-01-10")]
    return pd.concat([a,b])[["ts","open","close"]].copy()

def private_2020_21():
    url=os.environ.get("NEON_DATABASE_URL","")
    if not url:raise RuntimeError("NEON_DATABASE_URL_UNAVAILABLE")
    with psycopg.connect(url,connect_timeout=20) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT bar_start_utc,open_price,close_price
             FROM gold_research_twelve_xau15m_gap_candidate
             WHERE source_id=%s
               AND bar_start_utc>='2020-01-01' AND bar_start_utc<'2022-01-01'
             ORDER BY bar_start_utc""",
             ("TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1",))
            rows=cur.fetchall()
    if len(rows)<44000:raise RuntimeError("Twelve 2020-2021 backfill NOT COMPLETE")
    x=pd.DataFrame(rows,columns=["ts","open","close"])
    x["ts"]=pd.to_datetime(x.ts,utc=True)
    return x

def check_prices(q):
    if q.ts.duplicated().any():raise RuntimeError("duplicate timestamp")
    if not ((q.open>0)&(q.close>0)).all():raise RuntimeError("invalid prices")
    if not ((q.ts.dt.minute%15)==0).all():raise RuntimeError("bad 15m cadence")
    byyear=q.groupby(q.ts.dt.year).size().to_dict()
    for y in range(2020,2026):
        if byyear.get(y,0)<17000:raise RuntimeError("thin year "+str(y))
    return {str(y):int(n) for y,n in byyear.items()}

def lret(a,b):
    if pd.isna(a) or pd.isna(b) or a<=0 or b<=0:return np.nan
    return float(np.log(b/a))

def build(q):
    q=q.sort_values("ts").set_index("ts")
    if q.index.duplicated().any():raise RuntimeError("duplicate index")
    days=sorted({x.date() for x in q.index if x.hour==6 and x.minute==0})
    row=[]
    def p(d,hm,col):
        hh,mm=map(int,hm.split(":"))
        t=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=hh,minutes=mm)
        return q.at[t,col] if t in q.index else np.nan
    def segment(d,a,b):
        return lret(p(d,a,"open"),p(d,b,"close"))
    for i,d in enumerate(days):
        prev=days[i-1] if i else None
        nex=days[i+1] if i+1<len(days) else None
        x16=segment(d,"13:00","13:15")
        x1630=segment(d,"13:30","13:45")
        day=segment(d,"06:00","13:45")
        ovn=lret(p(d,"14:00","open"),p(nex,"05:45","close")) if nex else np.nan
        prev_ovn=lret(p(prev,"14:00","open"),p(d,"05:45","close")) if prev else np.nan
        # Do not calculate a mixed-vintage return across the 2021/2022 archive join.
        if nex and d.year==2021 and nex.year==2022: ovn=np.nan
        if prev and prev.year==2021 and d.year==2022: prev_ovn=np.nan
        row.append({"date":pd.Timestamp(d),"year":d.year,
            "next_date":pd.Timestamp(nex) if nex else pd.NaT,
            "r0800_0830":segment(d,"05:00","05:15"),
            "r0830_0900":segment(d,"05:30","05:45"),
            "r1600_1630":x16,"r1630_1700":x1630,
            "pair_inter":x16*x1630 if np.isfinite(x16) and np.isfinite(x1630) else np.nan,
            "pair_same":float(np.sign(x16)==np.sign(x1630))
                if np.isfinite(x16) and np.isfinite(x1630) and x16!=0 and x1630!=0 else np.nan,
            "prev_ovn":prev_ovn,"ret_DAY":day,"ret_OVN":ovn,
            "y_DAY":int(day>0) if np.isfinite(day) else np.nan,
            "y_OVN":int(ovn>0) if np.isfinite(ovn) else np.nan
        })
    d=pd.DataFrame(row)
    # Only completed targets and valid days. An observed 06:00 pivot is required.
    return d

def audit_legacy_labels(d):
    path=AX/"GOLD_EXECUTION_LIT_STAGE1_PREDICTIONS_2026-10-07.csv"
    h=pd.read_csv(path,parse_dates=["date"])
    h=h[(h.spec=="LIT_OVN1_PAIR") | (h.spec=="LIT_DAY0_EXEC_0900")]
    issues=[]
    for target,spec in (("OVN","LIT_OVN1_PAIR"),("DAY","LIT_DAY0_EXEC_0900")):
        t=h[h.spec==spec][["date","actual_y","actual_ret"]].drop_duplicates("date")
        z=d[["date","y_"+target,"ret_"+target]].merge(t,on="date",how="inner",validate="one_to_one")
        mismatch=z[z["y_"+target].to_numpy()!=z.actual_y.to_numpy()]
        wrong=len(mismatch)
        if wrong: print("LABEL_MISMATCH_DATES",target,mismatch.date.dt.strftime("%Y-%m-%d").tolist(),flush=True)
        mag=float(np.nanmax(np.abs(z["ret_"+target]-z.actual_ret))) if len(z) else None
        issues.append({"target":target,"matched":len(z),"direction_mismatch":wrong,
                       "max_abs_return_delta":mag})
        if len(z)<450 or wrong or mag is None or mag>1e-10:
            raise RuntimeError("LABEL_IDENTITY_VS_FROZEN_FAIL:"+target+":"+str(issues[-1]))
    return issues

def calc(y,p):
    y=np.asarray(y,int); p=np.asarray(p,float)
    pred=(p>=.5).astype(int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,pred,labels=[0,1]).ravel())
    return {"n":len(y),"accuracy":float((pred==y).mean()),
        "ba":(float(tn/(tn+fp))+float(tp/(tp+fn)))/2 if tn+fp and tp+fn else np.nan,
        "up_recall":float(tp/(tp+fn)) if tp+fn else np.nan,
        "down_recall":float(tn/(tn+fp)) if tn+fp else np.nan,
        "brier":float(brier_score_loss(y,p)),
        "pred_up_rate":float(pred.mean()),
        "tn":tn,"fp":fp,"fn":fn,"tp":tp}

def run_spec(d,spec,target,features):
    q=d.dropna(subset=features+["ret_"+target,"y_"+target]).sort_values("date").reset_index(drop=True)
    results=[]
    for year in (2023,2024,2025):
        test=q[q.year==year]
        for horizon,minyear in HORIZONS.items():
            for _,r in test.iterrows():
                if year in (2023,2024):
                    tr=q[(q.year>=minyear)&(q.date<r.date)].copy()
                    if target=="OVN":tr=tr[tr.next_date<=r.date]
                else:
                    tr=q[(q.year>=minyear)&(q.date<pd.Timestamp("2025-01-01"))].copy()
                    if target=="OVN":tr=tr[tr.next_date<=pd.Timestamp("2025-01-01")]
                if len(tr)<MIN_TRAIN or tr["y_"+target].nunique()!=2:continue
                model=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000))
                model.fit(tr[features].to_numpy(float),tr["y_"+target].astype(int).to_numpy())
                p=float(model.predict_proba(r[features].to_numpy(float).reshape(1,-1))[0,1])
                results.append({"spec":spec,"target":target,"year":year,
                   "date":r.date,"horizon":horizon,"y":int(r["y_"+target]),
                   "p":p,"ntrain":len(tr)})
    return pd.DataFrame(results)

def evaluate(res):
    allmetrics=[]
    allpairs=[]
    for (spec,year),g in res.groupby(["spec","year"]):
        left=g[g.horizon=="SHORT_2022_PLUS"][["date","y","p","ntrain"]].rename(
            columns={"p":"p_short","ntrain":"train_short"})
        right=g[g.horizon=="LONG_2020_PLUS"][["date","y","p","ntrain"]].rename(
            columns={"p":"p_long","ntrain":"train_long","y":"y_long"})
        z=left.merge(right,on="date",validate="one_to_one")
        if len(z)<180 or (z.y!=z.y_long).any():
            raise RuntimeError("MATCHED_TEST_COUNT_OR_TARGET_FAILURE:"+spec+":"+str(year)+":"+str(len(z)))
        y=z.y.astype(int).to_numpy()
        a=calc(y,z.p_short)
        b=calc(y,z.p_long)
        pa=(z.p_short>=.5).to_numpy()
        pb=(z.p_long>=.5).to_numpy()
        resq=int(((pb==y)&(pa!=y)).sum())
        broken=int(((pb!=y)&(pa==y)).sum())
        out={"spec":spec,"target":"DAY" if "DAY" in spec else "OVN","year":year,
             "period":"DEV" if year<2025 else "ALREADY_INSPECTED_2025",
             "common_n":len(z),"train_short_last":int(z.train_short.iloc[-1]),
             "train_long_last":int(z.train_long.iloc[-1]),
             "short_acc":a["accuracy"],"short_ba":a["ba"],
             "short_up_recall":a["up_recall"],"short_down_recall":a["down_recall"],
             "short_brier":a["brier"],
             "long_acc":b["accuracy"],"long_ba":b["ba"],
             "long_up_recall":b["up_recall"],"long_down_recall":b["down_recall"],
             "long_brier":b["brier"],
             "delta_accuracy_pp":100*(b["accuracy"]-a["accuracy"]),
             "delta_ba_pp":100*(b["ba"]-a["ba"]),
             "delta_brier":b["brier"]-a["brier"],
             "rescues":resq,"breaks":broken,"net_rescues":resq-broken,
             "mcnemar_exact_p":float(binomtest(resq,resq+broken,.5).pvalue)
                            if resq+broken else 1.}
        allmetrics.append(out)
    return pd.DataFrame(allmetrics)

def main():
    t=time.time()
    history=private_2020_21()
    current=native_2022_25()
    q=pd.concat([history,current],ignore_index=True).sort_values("ts")
    q[["open","close"]]=q[["open","close"]].apply(pd.to_numeric,errors="coerce")
    q=q.dropna(subset=["ts","open","close"])
    coverage=check_prices(q)
    d=build(q)
    identity=audit_legacy_labels(d)
    predictions=pd.concat([run_spec(d,spec,*cfg) for spec,cfg in FEATURES.items()],ignore_index=True)
    metrics=evaluate(predictions)
    metrics.to_csv(SCORES,index=False)
    summary={"status":"COMPLETE_SAME_DATE_HISTORICAL_LENGTH_CHALLENGER",
       "research_identity":"LIT model specifications; NOT PRAMV V1; no extra variables or thresholds",
       "source_private_2020_21":"Twelve Data native 15m, 2020 Jan 1-23 unavailable",
       "source_2022_25":"preexisting repo frozen 15m archives",
       "source_splice_warning":"No same-instrument transition overlap at 2022-01; mixed-vintage historical learning remains provisional",
       "period_roles":{"2020-2021":"long_history_train_only","2022":"short_history_train",
                       "2023-2024":"previously inspected development",
                       "2025":"already inspected retrospective fixed-cutoff transport"},
       "train_definition":{"SHORT_2022_PLUS":"all matured rows from 2022 onward",
                           "LONG_2020_PLUS":"all matured rows from 2020 Jan24 onward"},
       "feature_identity":"LIT_OVN0_1600_1630 / LIT_OVN1_PAIR / LIT_DAY0_EXEC_0900; sklearn StandardScaler+LogisticRegression(C=1)",
       "min_train":MIN_TRAIN,"source_yearly_rows":coverage,
       "frozen_2023_25_label_equivalence":identity,
       "metrics":metrics.to_dict("records"),
       "no_new_selection_from_2025":True,
       "elapsed_seconds":round(time.time()-t,3),"no_model_promotion":True}
    SUMMARY.write_text(json.dumps(summary,indent=2,default=str)+"\n")
    lines=["# 2020–2025 historical-depth matched-origin test — LIT execution windows","",
      "**Status:** COMPLETED RETROSPECTIVE RESEARCH — NOT PRAMV, NOT EXECUTABLE P&L","",
      "2020–2021 Twelve Data native 15m prices are read from private Neon; 2022–2025 same frozen source/target archive. No raw licensed data exported. Frozen prior target values checked for exact-match. Fixed 2023–2024 chronological train-at-origin, fixed train-through-2024 for 2025. Earlier 2025 was observed; do not claim unseen OOS.","",
      "| Spec | Year | N | Short BA | Long BA | Δ BA pp | Short Acc | Long Acc | Δ Brier | Rescues / breaks | McNemar p |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in metrics.itertuples(index=False):
        lines.append(f"| {r.spec} | {r.year} | {r.common_n} | {100*r.short_ba:.2f}% | {100*r.long_ba:.2f}% | {r.delta_ba_pp:+.2f} | {100*r.short_acc:.2f}% | {100*r.long_acc:.2f}% | {r.delta_brier:+.5f} | {r.rescues}/{r.breaks} | {r.mcnemar_exact_p:.4f} |")
    lines+=["","**Promotion gate:** Only if both development years improve without downside class collapse and same-date corrected 2025 supports it; significant evidence and future prospective test still required.",
       "**Unresolved:** this experiment does not rebuild the macro feature/veto data for PRAMV or certify real bank bid/ask; no PRAMV improvement may be claimed.",""]
    RESULT.write_text("\n".join(lines))
    print(RESULT.read_text(),flush=True)
if __name__=="__main__":main()
