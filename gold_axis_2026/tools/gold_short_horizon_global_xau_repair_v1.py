from __future__ import annotations

import argparse, hashlib, io, json, math, os, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED=20261001
BLOCK=5
H=3
CORE_SERIES={
    "gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
PUBLIC_METAL={"gold":"Gold","silver":"Silver","platinum":"Platinum","palladium":"Palladium"}
CORE3=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]
EXPECTED={
    "brier":0.246731,
    "baseline_brier":0.249712,
    "logloss":0.686634,
}
SOURCE_HINTS=(
    "XAU_","XAG_","XPT_","XPD_","DGS10","DFII10","DTWEX","DEX",
    "VIX","GVZ","NASDAQ100","SP500","DJIA","WTI","BRENT","GPR"
)

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"global-xau-repair/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def parse_stak_annual(raw):
    rows=json.loads(raw)
    out=defaultdict(dict)
    for r in rows:
        metal=str(r.get("metal") or "")
        if metal not in set(PUBLIC_METAL.values()): continue
        ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
        if pd.isna(ts): continue
        try: v=float(r.get("spot"))
        except Exception: continue
        if np.isfinite(v) and v>0:
            out[metal][ts.date().isoformat()]=v
    return out

def parse_hourly12(raw,day):
    rows=json.loads(raw); out={}
    for r in rows:
        metal=str(r.get("metal") or "")
        if metal not in set(PUBLIC_METAL.values()): continue
        if str(r.get("timestamp") or "") != day+" 12:00:00": continue
        try: v=float(r.get("spot"))
        except Exception: continue
        if np.isfinite(v) and v>0: out[metal]=v
    if set(out)!=set(PUBLIC_METAL.values()):
        raise RuntimeError(f"HOURLY12_INCOMPLETE {day} {sorted(out)}")
    return out

def fetch_public_stak(stak_ref,api_ref,start_day,end_day):
    years=range(pd.Timestamp(start_day).year,pd.Timestamp(end_day).year+1)
    by=defaultdict(dict); annual_hashes={}; api_hashes={}
    for y in years:
        raw=get_bytes(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{stak_ref}/data/spot-history-{y}.json")
        annual_hashes[str(y)]=sha256_bytes(raw)
        q=parse_stak_annual(raw)
        for m in PUBLIC_METAL.values(): by[m].update(q[m])
    common_annual=sorted(set.intersection(*(set(by[m]) for m in PUBLIC_METAL.values())))
    if not common_annual: raise RuntimeError("NO_PUBLIC_ANNUAL_COMMON_DATES")
    annual_last=common_annual[-1]
    first_api=max(pd.Timestamp(start_day),pd.Timestamp(annual_last)+pd.Timedelta(days=1))
    for d in pd.date_range(first_api,pd.Timestamp(end_day),freq="D"):
        day=d.date().isoformat()
        url=f"https://raw.githubusercontent.com/lbruton/StakTrakrApi/{api_ref}/data/hourly/{day[:4]}/{day[5:7]}/{day[8:10]}/12.json"
        try: raw=get_bytes(url)
        except Exception:
            # weekends/holidays and legitimately absent snapshots are skipped.
            continue
        try: h=parse_hourly12(raw,day)
        except RuntimeError:
            continue
        api_hashes[day]=sha256_bytes(raw)
        for m,v in h.items(): by[m][day]=v
    common=sorted(set.intersection(*(set(by[m]) for m in PUBLIC_METAL.values())))
    common=[d for d in common if start_day<=d<=end_day and pd.Timestamp(d).weekday()<5]
    if not common: raise RuntimeError("NO_PUBLIC_COMMON_DATES")
    frame=pd.DataFrame({"date":pd.to_datetime(common)})
    for key,metal in PUBLIC_METAL.items():
        frame[key]=[float(by[metal][d]) for d in common]
    return frame,{
        "annual_hashes":annual_hashes,
        "api_hash_count":len(api_hashes),
        "annual_last":annual_last,
        "public_first":common[0],
        "public_last":common[-1],
        "public_n":len(common),
    }

def load_db(dsn):
    raw={}; inv=[]
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for key,sid in CORE_SERIES.items():
                cur.execute("""
                    SELECT observation_ts::date, value
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts, retrieved_at
                """,(sid,))
                rows=cur.fetchall()
                if not rows: raise RuntimeError(f"NO_DB_ROWS {sid}")
                q=pd.DataFrame(rows,columns=["date",key])
                q["date"]=pd.to_datetime(q["date"])
                q[key]=pd.to_numeric(q[key],errors="coerce")
                q=q.dropna()
                q=q[q[key]>0].sort_values("date").drop_duplicates("date",keep="last")
                q=q[q.date.dt.weekday<5].reset_index(drop=True)
                raw[key]=q
            cur.execute("""
                SELECT series_id,
                       MIN(observation_ts)::date,
                       MAX(observation_ts)::date,
                       COUNT(*),
                       COUNT(*) FILTER (WHERE observation_ts::date BETWEEN DATE '2026-08-01' AND DATE '2026-09-30')
                FROM observations
                GROUP BY series_id
                ORDER BY series_id
            """)
            for sid,d0,d1,n,nlate in cur.fetchall():
                s=str(sid)
                if any(h.upper() in s.upper() for h in SOURCE_HINTS):
                    inv.append({"series_id":s,"first_date":str(d0),"last_date":str(d1),"rows":int(n),"aug_sep_rows":int(nlate)})
        conn.rollback()
    return raw,pd.DataFrame(inv)

def continuity_and_extend(db,pub):
    checks=[]
    merged={}
    for key in CORE_SERIES:
        a=db[key].copy()
        b=pub[["date",key]].copy()
        ov=a.merge(b,on="date",suffixes=("_db","_pub"))
        if len(ov)<20: raise RuntimeError(f"OVERLAP_TOO_SMALL {key} n={len(ov)}")
        lhs=ov[f"{key}_db"].to_numpy(float); rhs=ov[f"{key}_pub"].to_numpy(float)
        rel=np.abs(lhs-rhs)/np.maximum(np.abs(lhs),1e-12)
        ok=np.isclose(lhs,rhs,rtol=1e-8,atol=1e-8)
        checks.append({
            "metal":key,"overlap_n":int(len(ov)),
            "max_abs_diff":float(np.max(np.abs(lhs-rhs))),
            "max_rel_diff":float(np.max(rel)),
            "all_match":bool(ok.all()),
            "db_last":str(a.date.max().date()),
            "public_last":str(b.date.max().date()),
        })
        if not ok.all(): raise RuntimeError(f"SAME_SOURCE_CONTINUITY_FAIL {key} maxrel={rel.max()}")
        ext=b[b.date>a.date.max()].copy()
        q=pd.concat([a,ext],ignore_index=True).sort_values("date").drop_duplicates("date",keep="first")
        merged[key]=q.reset_index(drop=True)
    return merged,pd.DataFrame(checks)

def build_panel(metals):
    gold=metals["gold"].copy().sort_values("date").reset_index(drop=True)
    df=gold.rename(columns={"date":"feature_cutoff_date"}).copy()
    df["forecast_issue_date"]=df["feature_cutoff_date"].shift(-1)
    df["target_start_date"]=df["feature_cutoff_date"]
    lg=np.log(df.gold)
    for h in [1,3,5]:
        df[f"target_end_date_h{h}"]=df["feature_cutoff_date"].shift(-h)
        df[f"target_r{h}"]=np.log(df.gold.shift(-h)/df.gold)
    for h in [1,3,5,10,21]:
        df[f"gold_r{h}"]=lg.diff(h)
    df["sigma20"]=lg.diff().rolling(20).std(ddof=0)

    for name in ["silver","platinum","palladium"]:
        q=metals[name].copy().sort_values("date")
        lp=np.log(q[name])
        for h in [1,5,21]:
            q[f"{name}_r{h}"]=lp.diff(h)
        q=q.rename(columns={"date":f"{name}_obs_date",name:f"{name}_price"})
        df=pd.merge_asof(
            df.sort_values("feature_cutoff_date"),q.sort_values(f"{name}_obs_date"),
            left_on="feature_cutoff_date",right_on=f"{name}_obs_date",direction="backward"
        )
        df[f"{name}_age_days"]=(df.feature_cutoff_date-df[f"{name}_obs_date"]).dt.days

    df=df[df.forecast_issue_date.notna()].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    df["role"]=np.select(
        [
            df.forecast_issue_date.dt.year<=2021,
            df.forecast_issue_date.dt.year.between(2022,2024),
            df.forecast_issue_date.dt.year==2025,
            df.forecast_issue_date.dt.year==2026,
        ],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025","OPENED_2026"],
        default="OTHER"
    )
    return df

def fill(train,test,features):
    a=train[features].copy(); b=test[features].copy()
    for c in features:
        med=pd.to_numeric(a[c],errors="coerce").median(skipna=True)
        v=0.0 if pd.isna(med) else float(med)
        a[c]=pd.to_numeric(a[c],errors="coerce").fillna(v)
        b[c]=pd.to_numeric(b[c],errors="coerce").fillna(v)
    return a,b

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))
    ])

def cls_metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_precision":float(precision_score(y,pred,zero_division=0)),
        "up_recall":float(recall_score(y,pred,zero_division=0)),
        "down_recall":float(recall_score(1-y,1-pred,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "mean_p_up":float(np.mean(p)),
        "actual_up_rate":float(np.mean(y)),
    }

def reproduce_dev(df):
    dev=df[(df.role=="DEV") & df.target_r3.notna()].copy()
    rows=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy()
        start=te.feature_cutoff_date.min()
        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=start) &
            (df.forecast_issue_date<pd.Timestamp("2025-01-01"))
        ].copy()
        if len(tr)<252: raise RuntimeError(f"DEV_TRAIN_TOO_SMALL {len(tr)}")
        ytr=(tr.target_r3>0).astype(int)
        yte=(te.target_r3>0).astype(int).to_numpy()
        pexp=float(ytr.mean()); proll=float(ytr.iloc[-252:].mean())
        Xtr,Xte=fill(tr,te,CORE3)
        m=model(); m.fit(Xtr,ytr); pp=m.predict_proba(Xte)[:,1]
        for r,y,p in zip(te.itertuples(),yte,pp):
            rows.append({
                "row_index":int(r.Index),
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "y_up":int(y),"p_core3":float(p),"p_expand":pexp,"p_roll252":proll,
            })
    z=pd.DataFrame(rows)
    core=cls_metrics(z.y_up,z.p_core3)
    b1=cls_metrics(z.y_up,z.p_expand)
    b2=cls_metrics(z.y_up,z.p_roll252)
    base_name,base=("EXPAND_PREV",b1) if (b1["brier"],b1["logloss"]) <= (b2["brier"],b2["logloss"]) else ("ROLL252_PREV",b2)
    core["baseline_model"]=base_name
    core["baseline_brier"]=base["brier"]
    core["baseline_logloss"]=base["logloss"]
    core["relative_brier_improvement"]=(base["brier"]-core["brier"])/base["brier"]
    annual=[]
    z["year"]=pd.to_datetime(z.forecast_issue_date).dt.year
    for yr,g in z.groupby("year"):
        cm=cls_metrics(g.y_up,g.p_core3)
        bp=g.p_expand if base_name=="EXPAND_PREV" else g.p_roll252
        bm=cls_metrics(g.y_up,bp)
        annual.append({"year":int(yr),**cm,"baseline_brier":bm["brier"],"relative_brier_improvement":(bm["brier"]-cm["brier"])/bm["brier"]})
    diffs={
        "brier_abs_diff":abs(core["brier"]-EXPECTED["brier"]),
        "baseline_brier_abs_diff":abs(core["baseline_brier"]-EXPECTED["baseline_brier"]),
        "logloss_abs_diff":abs(core["logloss"]-EXPECTED["logloss"]),
    }
    repro_pass=all(v<=5e-6 for v in diffs.values())
    return z,core,pd.DataFrame(annual),diffs,repro_pass

def frozen_transport(df):
    eligible=df[df.target_r3.notna() & df.target_end_date_h3.notna()].copy()
    train=eligible[eligible.target_end_date_h3<=pd.Timestamp("2024-12-31")].copy()
    test=eligible[
        eligible.forecast_issue_date.dt.year.isin([2025,2026]) &
        (eligible.target_end_date_h3<=pd.Timestamp("2026-09-30"))
    ].copy()
    Xtr,Xte=fill(train,test,CORE3)
    m=model(); ytr=(train.target_r3>0).astype(int); m.fit(Xtr,ytr)
    pp=m.predict_proba(Xte)[:,1]
    rows=[]
    for r,p in zip(test.itertuples(),pp):
        y=int(r.target_r3>0); pred=int(p>=.5)
        rows.append({
            "mode":"STRICT_FROZEN_FIT",
            "feature_cutoff_date":str(r.feature_cutoff_date.date()),
            "forecast_issue_date":str(r.forecast_issue_date.date()),
            "target_start_date":str(r.target_start_date.date()),
            "target_end_date_h3":str(r.target_end_date_h3.date()),
            "actual_h3_return":float(r.target_r3),
            "actual_direction":"UP" if y else "DOWN",
            "p_up":float(p),
            "predicted_direction":"UP" if pred else "DOWN",
            "correct":bool(pred==y),
            "conviction_band":"HIGH_UP" if p>=.55 else ("LOW_UP" if p<=.45 else "NEUTRAL"),
            "signal_year":int(r.forecast_issue_date.year),
            "signal_month":str(r.forecast_issue_date.strftime("%Y-%m")),
            "train_n":int(len(train)),
        })
    led=pd.DataFrame(rows)
    metrics=[]
    for key,g in led.groupby("signal_year"):
        mm=cls_metrics((g.actual_direction=="UP").astype(int),g.p_up)
        hi=g[g.p_up>=.55]; lo=g[g.p_up<=.45]
        metrics.append({
            "period":str(int(key)),**mm,
            "high_up_n":int(len(hi)),
            "high_up_realized_up":None if len(hi)==0 else float((hi.actual_direction=="UP").mean()),
            "low_up_n":int(len(lo)),
            "low_up_realized_up":None if len(lo)==0 else float((lo.actual_direction=="UP").mean()),
        })
    for key,g in led[led.signal_year==2026].groupby("signal_month"):
        mm=cls_metrics((g.actual_direction=="UP").astype(int),g.p_up)
        metrics.append({"period":str(key),**mm,"high_up_n":int((g.p_up>=.55).sum()),"high_up_realized_up":None,"low_up_n":int((g.p_up<=.45).sum()),"low_up_realized_up":None})
    coef=m.named_steps["model"].coef_[0]
    return led,pd.DataFrame(metrics),train,m,{f:float(v) for f,v in zip(CORE3,coef)}

def drift_audit(df,train,model_obj):
    rows=[]
    ref=train[CORE3].apply(pd.to_numeric,errors="coerce")
    med=ref.median(); sd=ref.std(ddof=0).replace(0,np.nan)
    for period,mask in [
        ("DEV_2022_2024",df.role=="DEV"),
        ("TRANSPORT_2025",df.role=="TRANSPORT_2025"),
        ("OPENED_2026",df.role=="OPENED_2026"),
    ]:
        z=df[mask & df.target_r3.notna()].copy()
        if z.empty: continue
        for f in CORE3:
            vals=pd.to_numeric(z[f],errors="coerce")
            mean_z=float((vals.mean()-ref[f].mean())/sd[f]) if pd.notna(sd[f]) else None
            std_ratio=float(vals.std(ddof=0)/sd[f]) if pd.notna(sd[f]) and sd[f]!=0 else None
            rows.append({
                "period":period,"feature":f,"n":int(vals.notna().sum()),
                "mean":float(vals.mean()),"ref_mean":float(ref[f].mean()),
                "mean_shift_z":mean_z,"std_ratio_vs_ref":std_ratio,
            })
    out=pd.DataFrame(rows)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stak-ref",required=True)
    ap.add_argument("--stak-api-ref",required=True)
    ap.add_argument("--cutoff",default="2026-09-30")
    ap.add_argument("--out-dir",default="global_xau_repair_out")
    a=ap.parse_args()
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    db,inventory=load_db(dsn)
    public,pubmeta=fetch_public_stak(a.stak_ref,a.stak_api_ref,"2025-01-01",a.cutoff)
    metals,continuity=continuity_and_extend(db,public)
    panel=build_panel(metals)

    inventory.to_csv(out/"source_inventory.csv",index=False)
    continuity.to_csv(out/"same_source_continuity.csv",index=False)
    panel.to_csv(out/"corrected_timeline_panel.csv",index=False)

    devpred,devmetric,annual,diffs,repro_pass=reproduce_dev(panel)
    devpred.to_csv(out/"dev_reproduction_predictions.csv",index=False)
    annual.to_csv(out/"dev_reproduction_annual.csv",index=False)

    ledger,tmetrics,train,m,coef=frozen_transport(panel)
    ledger.to_csv(out/"h3_transport_predictions_v2.csv",index=False)
    tmetrics.to_csv(out/"h3_transport_metrics_v2.csv",index=False)

    drift=drift_audit(panel,train,m)
    drift.to_csv(out/"distribution_shift_diagnostics.csv",index=False)

    aug=ledger[(ledger.signal_month=="2026-08")]
    sep=ledger[(ledger.signal_month=="2026-09")]
    latest_issue=None if ledger.empty else str(pd.to_datetime(ledger.forecast_issue_date).max().date())
    top_shift={}
    for p,g in drift.groupby("period"):
        gg=g.assign(absz=pd.to_numeric(g.mean_shift_z,errors="coerce").abs()).sort_values("absz",ascending=False).head(5)
        top_shift[p]=[{"feature":r.feature,"mean_shift_z":None if pd.isna(r.mean_shift_z) else float(r.mean_shift_z)} for r in gg.itertuples()]

    summary={
        "schema":"GOLD_SHORT_HORIZON_GLOBAL_XAU_REPAIR_V1_2026-10-02",
        "status":"PASS" if repro_pass else "REPRODUCTION_FAIL",
        "stak_ref":a.stak_ref,
        "stak_api_ref":a.stak_api_ref,
        "cutoff":a.cutoff,
        "public_source":pubmeta,
        "continuity":continuity.to_dict(orient="records"),
        "panel":{
            "first_feature_cutoff":str(panel.feature_cutoff_date.min().date()),
            "last_feature_cutoff":str(panel.feature_cutoff_date.max().date()),
            "last_forecast_issue":str(panel.forecast_issue_date.max().date()),
            "n":int(len(panel)),
        },
        "dev_reproduction":{"metrics":devmetric,"expected":EXPECTED,"diffs":diffs,"pass":repro_pass,"annual":annual.to_dict(orient="records")},
        "transport":{
            "train_n":int(len(train)),
            "last_fully_matured_issue_through_cutoff":latest_issue,
            "august_2026_n":int(len(aug)),
            "september_2026_n":int(len(sep)),
            "metrics":tmetrics.to_dict(orient="records"),
            "coefficients":coef,
        },
        "diagnostic_only":{
            "top_feature_shifts":top_shift,
            "no_retuning":True,
        },
        "governance":{
            "db_access":"READ_ONLY",
            "new_provider_search":False,
            "target_formula_changed":False,
            "model_or_threshold_changed":False,
            "opened_2025_2026_used_for_selection":False,
        },
    }

    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU — Repair / Reproduction Result","",
        f"**Status:** **{summary['status']}**","",
        "## Same-source extension","",
        f"- StakTrakr ref: `{a.stak_ref}`",
        f"- StakTrakrApi ref: `{a.stak_api_ref}`",
        f"- public four-metal coverage used: {pubmeta['public_first']} .. {pubmeta['public_last']}",
        f"- repaired panel last issue date: {summary['panel']['last_forecast_issue']}",
        f"- August 2026 fully matured H3 forecasts: **{len(aug)}**",
        f"- September 2026 fully matured H3 forecasts: **{len(sep)}**","",
        "Continuity gate:",
    ]
    for r in continuity.itertuples():
        lines.append(f"- {r.metal}: overlap n={r.overlap_n}, max rel diff={r.max_rel_diff:.3e}, match={r.all_match}, DB last={r.db_last}, public last={r.public_last}.")
    lines += [
        "","## Timeline correction",
        "- `feature_cutoff_date` = last retained Gold observation used by features.",
        "- `forecast_issue_date` = next retained Gold date; supersedes ambiguous `signal_date` wording.",
        "- `target_end_date_h3` = exact H3 outcome maturity date.",
        "","## Frozen DEV reproduction",
        f"- CORE3 / Logistic-L2 Brier: **{devmetric['brier']:.6f}**",
        f"- baseline ({devmetric['baseline_model']}) Brier: **{devmetric['baseline_brier']:.6f}**",
        f"- relative improvement: **{100*devmetric['relative_brier_improvement']:.2f}%**",
        f"- log loss: **{devmetric['logloss']:.6f}**",
        f"- reproduction gate: **{repro_pass}**","",
        "## Frozen transport",
        "| Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in tmetrics.itertuples():
        if r.period in ("2025","2026","2026-08","2026-09"):
            lines.append(f"| {r.period} | {int(r.n)} | {100*r.accuracy:.1f}% | {100*r.balanced_accuracy:.1f}% | {r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.1f}% | {100*r.down_recall:.1f}% |")
    lines += [
        "","## Interpretation",
        "- This repair does not tune the model on 2025/2026.",
        "- August/September are included only because the same StakTrakr four-metal lineage continuity gate passed.",
        "- External source families remain registry/audit context; the frozen CORE3 engine is unchanged.",
        "- Distribution-shift diagnostics are descriptive only and cannot create a post-hoc regime gate.",
    ]

    (out/"REPAIR_RESULT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    summary["hashes"]={p.name:sha256_file(p) for p in out.iterdir()}
    (out/"repair_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print("GLOBAL_XAU_REPAIR_SUMMARY="+json.dumps(summary,separators=(",",":"),default=str))
    print((out/"REPAIR_RESULT.md").read_text())

if __name__=="__main__":
    main()
