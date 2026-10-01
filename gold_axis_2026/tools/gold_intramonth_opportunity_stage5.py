import os, io, json, math, hashlib, zipfile, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import log_loss, average_precision_score, roc_auc_score

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
STAGE2_ARTIFACT=11161358194
STAGE3_ARTIFACT=11163151830
OUT=Path(os.environ.get("OUT_DIR","stage5_out"))
OUT.mkdir(parents=True,exist_ok=True)

THRESHOLDS=[0.20,0.25,0.30,0.35,0.40,0.45,0.50]
PLATT_MIN=126
ISO_MIN=252
SEED=20261001

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def get_zip(artifact_id):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{artifact_id}/zip"
    r=requests.get(u,headers={
        "Authorization":f"Bearer {tok}",
        "Accept":"application/vnd.github+json",
        "User-Agent":"gold-intramonth-stage5"
    },timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv_from(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return np.log(p/(1-p))

def sigmoid(x):
    x=np.asarray(x,float)
    return 1/(1+np.exp(-x))

def ece10(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float)
    bins=np.linspace(0,1,11)
    acc=0.0
    n=len(y)
    for i in range(10):
        lo,hi=bins[i],bins[i+1]
        if i<9: m=(p>=lo)&(p<hi)
        else: m=(p>=lo)&(p<=hi)
        if m.sum():
            acc += (m.sum()/n)*abs(float(y[m].mean())-float(p[m].mean()))
    return float(acc)

def calib_slope_intercept(y,p):
    y=np.asarray(y,int); x=logit(p).reshape(-1,1)
    if len(np.unique(y))<2: return None,None
    try:
        m=LogisticRegression(C=1e6,solver="lbfgs",max_iter=2000)
        m.fit(x,y)
        return float(m.coef_[0,0]),float(m.intercept_[0])
    except Exception:
        return None,None

def prob_metrics(y,p):
    y=np.asarray(y,float); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    slope,intercept=calib_slope_intercept(y,p)
    out={
        "n":int(len(y)),
        "prevalence":float(np.mean(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "ece10":ece10(y,p),
        "prediction_mean":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
        "calibration_slope":slope,
        "calibration_intercept":intercept,
    }
    try: out["pr_auc"]=float(average_precision_score(y,p))
    except: out["pr_auc"]=None
    try: out["roc_auc"]=float(roc_auc_score(y,p))
    except: out["roc_auc"]=None
    return out

def load_data():
    z2=get_zip(STAGE2_ARTIFACT)
    d=read_csv_from(z2,"intramonth_opportunity_stage2_dataset.csv")
    d["origin_date"]=pd.to_datetime(d["origin_date"])
    d["signal_date"]=pd.to_datetime(d["signal_date"])
    d=d.sort_values("origin_date").reset_index(drop=True)
    d["label_end_date"]=d["origin_date"].shift(-5)

    z3=get_zip(STAGE3_ARTIFACT)
    p=read_csv_from(z3,"stage3_dev_predictions_long.csv")
    p["origin_date"]=pd.to_datetime(p["origin_date"])
    p["signal_date"]=pd.to_datetime(p["signal_date"])
    core=p[
        (p["kind"]=="cls") &
        (p["feature_block"]=="G_ONLY") &
        (p["target"]=="opp5_k100") &
        (p["model"]=="HGB_CLASS")
    ].copy()
    core=core.rename(columns={"prediction":"p_raw"})
    if len(core)!=749: raise RuntimeError(f"Expected 749 core rows, got {len(core)}")
    keep=[
        "origin_date","signal_date","label_end_date","opp5_k100","mfe5","mae5",
        "mfe5_pct","mae5_pct","sigma20","monthly_direction","signal_month"
    ]
    x=core.merge(d[keep],on=["origin_date","signal_date"],how="left")
    x["y"]=x["y"].astype(int)
    x=x.sort_values("origin_date").reset_index(drop=True)
    return x

def calibrate_prequential(x):
    out=[]
    # preserve Stage3 5-origin blocks
    for block_id in sorted(x["block_id"].unique()):
        te=x[x["block_id"]==block_id].copy()
        if te.empty: continue
        start=pd.to_datetime(te["block_start_origin"].iloc[0])
        tr=x[
            (x["label_end_date"].notna()) &
            (x["label_end_date"]<=start)
        ].copy()
        # Because x contains only DEV OOS predictions, this training set is prior OOS predictions only.
        p_raw=te["p_raw"].to_numpy(float)
        p_platt=p_raw.copy()
        p_iso=p_raw.copy()
        platt_fallback=1
        iso_fallback=1

        if len(tr)>=PLATT_MIN and tr["y"].sum()>=20 and (len(tr)-tr["y"].sum())>=20:
            m=LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED)
            m.fit(logit(tr["p_raw"]).reshape(-1,1),tr["y"].astype(int))
            p_platt=m.predict_proba(logit(p_raw).reshape(-1,1))[:,1]
            platt_fallback=0

        if len(tr)>=ISO_MIN and tr["y"].sum()>=50 and (len(tr)-tr["y"].sum())>=50:
            m=IsotonicRegression(out_of_bounds="clip")
            m.fit(tr["p_raw"].to_numpy(float),tr["y"].to_numpy(float))
            p_iso=m.predict(p_raw)
            iso_fallback=0

        q=te.copy()
        q["p_platt"]=p_platt
        q["p_isotonic"]=p_iso
        q["platt_fallback"]=platt_fallback
        q["isotonic_fallback"]=iso_fallback
        q["cal_train_n"]=len(tr)
        out.append(q)
    return pd.concat(out,ignore_index=True)

def calibration_audit(z):
    rows=[]
    methods={"RAW":"p_raw","PLATT":"p_platt","ISOTONIC":"p_isotonic"}
    for name,col in methods.items():
        m=prob_metrics(z["y"],z[col])
        rows.append({"method":name,"slice":"ALL",**m})
        for yr,zz in z.groupby(z["signal_date"].dt.year):
            rows.append({"method":name,"slice":f"YEAR_{yr}",**prob_metrics(zz["y"],zz[col])})
        for lab,zz in z[z["monthly_direction"].notna()].groupby("monthly_direction"):
            rows.append({"method":name,"slice":f"MONTHLY_{lab}",**prob_metrics(zz["y"],zz[col])})
    return pd.DataFrame(rows)

def select_calibration(audit):
    allm=audit[audit["slice"]=="ALL"].set_index("method")
    raw=allm.loc["RAW"]
    candidates=[]
    for method in ["PLATT","ISOTONIC"]:
        m=allm.loc[method]
        rel=(raw["brier"]-m["brier"])/raw["brier"]
        ll_ok=m["logloss"]<=raw["logloss"]
        year_ok=True
        year_details={}
        for yr in [2022,2023,2024]:
            rr=audit[(audit["method"]=="RAW")&(audit["slice"]==f"YEAR_{yr}")].iloc[0]
            mm=audit[(audit["method"]==method)&(audit["slice"]==f"YEAR_{yr}")].iloc[0]
            r=(rr["brier"]-mm["brier"])/rr["brier"]
            year_details[str(yr)]=float(r)
            if r < -0.03: year_ok=False
        passed=rel>=0.005 and ll_ok and year_ok
        candidates.append({"method":method,"relative_brier_improvement":float(rel),"logloss_ok":bool(ll_ok),"year_ok":bool(year_ok),"year_rel":year_details,"pass":bool(passed)})
    passing=[x for x in candidates if x["pass"]]
    if not passing:
        return "RAW",candidates
    passing.sort(key=lambda x:x["relative_brier_improvement"],reverse=True)
    return passing[0]["method"],candidates

def threshold_metrics(z,pcol,thr):
    alert=z[pcol]>=thr
    y=z["y"].astype(int)
    tp=int((alert & (y==1)).sum())
    fp=int((alert & (y==0)).sum())
    fn=int((~alert & (y==1)).sum())
    n_alert=int(alert.sum())
    precision=tp/n_alert if n_alert else None
    recall=tp/int((y==1).sum()) if int((y==1).sum()) else None
    fpr=fp/n_alert if n_alert else None  # false share among alerts
    f1=(2*precision*recall/(precision+recall)) if precision is not None and recall is not None and precision+recall>0 else None
    a=z[alert]
    return {
        "threshold":thr,"n":int(len(z)),"alerts":n_alert,"alert_rate":float(alert.mean()),
        "positives":int((y==1).sum()),"tp":tp,"fp":fp,"fn":fn,
        "precision":precision,"recall":recall,"false_opportunity_rate":fpr,"f1":f1,
        "mean_mfe5_pct":float(a["mfe5_pct"].mean()) if len(a) else None,
        "median_mfe5_pct":float(a["mfe5_pct"].median()) if len(a) else None,
        "mean_mae5_pct":float(a["mae5_pct"].mean()) if len(a) else None,
        "median_mae5_pct":float(a["mae5_pct"].median()) if len(a) else None,
    }

def episode_metrics(z,pcol,thr):
    q=z.sort_values("origin_date").reset_index(drop=True).copy()
    q["alert"]=q[pcol]>=thr
    episodes=[]
    current=[]
    last_i=None
    for i,row in q.iterrows():
        if not row["alert"]: continue
        if last_i is None or i-last_i<=2:
            current.append(i)
        else:
            episodes.append(current); current=[i]
        last_i=i
    if current: episodes.append(current)
    succ=0; members=0
    for ep in episodes:
        members+=len(ep)
        if (q.loc[ep,"y"]==1).any(): succ+=1
    return {
        "threshold":thr,"episodes":len(episodes),"successful_episodes":succ,
        "episode_precision":succ/len(episodes) if episodes else None,
        "alert_members":members,"mean_alerts_per_episode":members/len(episodes) if episodes else None
    }

def volatility_buckets(z):
    q=z.copy()
    q["vol_bucket"]=pd.qcut(q["sigma20"],3,labels=["LOW","MID","HIGH"],duplicates="drop")
    return q

def main():
    x=load_data()
    z=calibrate_prequential(x)
    z.to_csv(OUT/"stage5_calibrated_predictions.csv",index=False)

    audit=calibration_audit(z)
    selected,cal_decisions=select_calibration(audit)
    pcol={"RAW":"p_raw","PLATT":"p_platt","ISOTONIC":"p_isotonic"}[selected]
    audit.to_csv(OUT/"stage5_calibration_metrics.csv",index=False)

    base_prev=float(z["y"].mean())
    thr_rows=[]; year_rows=[]; dir_rows=[]; vol_rows=[]; ep_rows=[]
    zv=volatility_buckets(z)

    for thr in THRESHOLDS:
        m=threshold_metrics(z,pcol,thr)
        # yearly stability
        year_pass=True
        for yr,yy in z.groupby(z["signal_date"].dt.year):
            ym=threshold_metrics(yy,pcol,thr)
            ym["year"]=int(yr)
            year_rows.append(ym)
            if ym["alerts"]<5 or ym["precision"] is None or ym["precision"]<0.25:
                year_pass=False
        down=z[z["monthly_direction"]=="DOWN"]
        up=z[z["monthly_direction"]=="UP"]
        dm=threshold_metrics(down,pcol,thr)
        um=threshold_metrics(up,pcol,thr)
        dm["monthly_direction"]="DOWN"; um["monthly_direction"]="UP"
        dir_rows += [dm,um]
        down_ok=dm["alerts"]>=10 and dm["precision"] is not None and dm["precision"]>=0.25

        for vb,vv in zv.groupby("vol_bucket",observed=True):
            vm=threshold_metrics(vv,pcol,thr); vm["vol_bucket"]=str(vb)
            vol_rows.append(vm)

        ep_rows.append(episode_metrics(z,pcol,thr))

        precision_ok=m["precision"] is not None and m["precision"]>=0.35
        recall_ok=m["recall"] is not None and m["recall"]>=0.20
        rate_ok=0.05<=m["alert_rate"]<=0.35
        lift_ok=m["precision"] is not None and m["precision"]>=base_prev+0.05
        gate=precision_ok and recall_ok and rate_ok and lift_ok and year_pass and down_ok
        m.update({
            "unconditional_prevalence":base_prev,
            "precision_lift_pp":(m["precision"]-base_prev) if m["precision"] is not None else None,
            "year_gate":year_pass,"down_gate":down_ok,
            "scientific_gate":"PASS" if gate else "FAIL"
        })
        thr_rows.append(m)

    th=pd.DataFrame(thr_rows)
    yr=pd.DataFrame(year_rows)
    dr=pd.DataFrame(dir_rows)
    vr=pd.DataFrame(vol_rows)
    ep=pd.DataFrame(ep_rows)
    th.to_csv(OUT/"stage5_threshold_metrics.csv",index=False)
    yr.to_csv(OUT/"stage5_threshold_year_metrics.csv",index=False)
    dr.to_csv(OUT/"stage5_threshold_monthly_direction_metrics.csv",index=False)
    vr.to_csv(OUT/"stage5_threshold_volatility_metrics.csv",index=False)
    ep.to_csv(OUT/"stage5_episode_metrics.csv",index=False)

    passing=th[th["scientific_gate"]=="PASS"].copy()
    if len(passing):
        max_recall=float(passing["recall"].max())
        near=passing[passing["recall"]>=max_recall-0.05].copy()
        if len(near):
            sel=near.sort_values(["precision","threshold"],ascending=[False,False]).iloc[0]
        else:
            sel=passing.sort_values("f1",ascending=False).iloc[0]
        selected_thr=float(sel["threshold"])
        alert_status="PASS"
    else:
        selected_thr=None
        alert_status="NO_THRESHOLD_PASS"

    summary={
        "status":alert_status,
        "selected_calibration":selected,
        "calibration_decisions":cal_decisions,
        "selected_threshold":selected_thr,
        "dev_n":int(len(z)),
        "dev_prevalence":base_prev,
        "calibration_all":audit[audit["slice"]=="ALL"].to_dict(orient="records"),
        "thresholds":th.to_dict(orient="records"),
        "fallbacks":{
            "platt_rows":int(z["platt_fallback"].sum()),
            "isotonic_rows":int(z["isotonic_fallback"].sum())
        }
    }

    lines=[
        "# GOLD INTRAMONTH OPPORTUNITY — Stage 5 Calibration & Alert Threshold Result","",
        f"**Status:** **{alert_status}**","",
        f"**Selected calibration:** **{selected}**","",
        f"**Selected threshold:** **{selected_thr if selected_thr is not None else 'NONE'}**","",
        "## Calibration","",
        "| Method | Brier | Log loss | ECE10 | PR-AUC | ROC-AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _,r in audit[audit["slice"]=="ALL"].iterrows():
        lines.append(f"| {r['method']} | {r['brier']:.5f} | {r['logloss']:.5f} | {r['ece10']:.5f} | {r['pr_auc']:.4f} | {r['roc_auc']:.4f} |")
    lines += ["","## Threshold audit","",
        "| Thr | Alerts | Rate | Precision | Recall | Lift pp | Mean MFE5 | Mean MAE5 | Gate |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for _,r in th.iterrows():
        lines.append(
            f"| {r['threshold']:.2f} | {int(r['alerts'])} | {100*r['alert_rate']:.1f}% | "
            f"{100*r['precision']:.1f}% | {100*r['recall']:.1f}% | {100*r['precision_lift_pp']:.1f} | "
            f"{r['mean_mfe5_pct']:.2f}% | {r['mean_mae5_pct']:.2f}% | {r['scientific_gate']} |"
        )
    lines += ["","## Binding decision"]
    if alert_status=="PASS":
        lines.append(f"Freeze {selected} probability with alert threshold p >= {selected_thr:.2f}. 2025 transport may now be run without retuning.")
    else:
        lines.append("No threshold satisfies the frozen operability gate. Retain the probability model without a binary alert and do not inspect 2025 for threshold rescue.")
    (OUT/"STAGE5_RESULT.md").write_text("\n".join(lines),encoding="utf-8")

    files=[
        OUT/"stage5_calibrated_predictions.csv",OUT/"stage5_calibration_metrics.csv",
        OUT/"stage5_threshold_metrics.csv",OUT/"stage5_threshold_year_metrics.csv",
        OUT/"stage5_threshold_monthly_direction_metrics.csv",OUT/"stage5_threshold_volatility_metrics.csv",
        OUT/"stage5_episode_metrics.csv",OUT/"STAGE5_RESULT.md"
    ]
    summary["hashes"]={p.name:sha256_file(p) for p in files}
    (OUT/"stage5_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    print("STAGE5_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE5_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
