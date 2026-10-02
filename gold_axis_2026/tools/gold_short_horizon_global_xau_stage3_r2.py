from __future__ import annotations
import io, json, math, os, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import log_loss

REPO="ataullahturgut/sim3-automation"
STAGE2_ARTIFACT=int(os.environ["STAGE2_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_r2_stage3_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5
H=3
MIN_CAL=100

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-stage3"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def clip(p):
    return np.clip(np.asarray(p,float),1e-6,1-1e-6)

def logit(p):
    p=clip(p)
    return np.log(p/(1-p))

def metrics(y,p):
    y=np.asarray(y,int); p=clip(p)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "prediction_std":float(np.std(p)),
        "mean_prediction":float(np.mean(p)),
        "actual_up_rate":float(np.mean(y)),
    }

def calibration_intercept_slope(y,p):
    x=logit(p).reshape(-1,1)
    y=np.asarray(y,int)
    m=LogisticRegression(C=1e9,solver="lbfgs",max_iter=2000,random_state=SEED)
    m.fit(x,y)
    return float(m.intercept_[0]),float(m.coef_[0,0])

def ece_table(y,p):
    y=np.asarray(y,int); p=clip(p)
    bins=np.linspace(0,1,11)
    rows=[]
    total=len(y)
    ece=0.0
    for i in range(10):
        lo,hi=bins[i],bins[i+1]
        mask=(p>=lo)&((p<hi) if i<9 else (p<=hi))
        n=int(mask.sum())
        if n:
            mp=float(p[mask].mean()); ay=float(y[mask].mean())
            ece += n/total*abs(mp-ay)
        else:
            mp=ay=None
        rows.append({"bin_low":lo,"bin_high":hi,"n":n,"mean_prediction":mp,"actual_up_rate":ay})
    return float(ece),rows

def fit_platt(p,y):
    m=LogisticRegression(C=1e9,solver="lbfgs",max_iter=2000,random_state=SEED)
    m.fit(logit(p).reshape(-1,1),np.asarray(y,int))
    return m

def apply_platt(m,p):
    return m.predict_proba(logit(p).reshape(-1,1))[:,1]

def fit_iso(p,y):
    m=IsotonicRegression(out_of_bounds="clip")
    m.fit(np.asarray(p,float),np.asarray(y,int))
    return m

def band_name(p):
    if p<=0.40: return "<=0.40"
    if p<0.45: return "0.40-0.45"
    if p<0.50: return "0.45-0.50"
    if p<0.55: return "0.50-0.55"
    if p<0.60: return "0.55-0.60"
    return ">=0.60"

def main():
    z=get_zip(STAGE2_ARTIFACT)
    pred=read_csv(z,"global_xau_r2_stage2_h3_predictions.csv")
    q=pred[(pred["representation"]=="CORE3")&(pred["model"]=="LOGIT_L2")].copy()
    q=q.sort_values("row_index").drop_duplicates("row_index").reset_index(drop=True)
    if len(q)!=755: raise RuntimeError(f"CORE3_DEV_N {len(q)} != 755")
    q["feature_cutoff_date"]=pd.to_datetime(q["feature_cutoff_date"])
    q["forecast_issue_date"]=pd.to_datetime(q["forecast_issue_date"])
    if q["forecast_issue_date"].dt.year.min()!=2022 or q["forecast_issue_date"].dt.year.max()!=2024:
        raise RuntimeError("DEV chronology mismatch")

    raw=q["prediction"].astype(float).to_numpy()
    y=q["y_up"].astype(int).to_numpy()
    calibrated={"RAW":raw.copy(),"PLATT":raw.copy(),"ISOTONIC":raw.copy()}
    fit_audit=[]

    # Refit calibrators only at the same 5-origin cadence. Maturity rule: prior position j is
    # calibrator-eligible when j + H <= current block start position.
    for start in range(0,len(q),BLOCK):
        stop=min(start+BLOCK,len(q))
        elig=np.arange(len(q))
        elig=elig[(elig+H)<=start]
        if len(elig)<MIN_CAL:
            fit_audit.append({"block_start_pos":start,"test_n":stop-start,"cal_n":int(len(elig)),"status":"RAW_FALLBACK_MIN_SUPPORT"})
            continue
        pcal=raw[elig]; ycal=y[elig]
        pl=fit_platt(pcal,ycal)
        iso=fit_iso(pcal,ycal)
        calibrated["PLATT"][start:stop]=apply_platt(pl,raw[start:stop])
        calibrated["ISOTONIC"][start:stop]=iso.predict(raw[start:stop])
        fit_audit.append({"block_start_pos":start,"test_n":stop-start,"cal_n":int(len(elig)),"status":"CALIBRATED",
                          "platt_intercept":float(pl.intercept_[0]),"platt_slope":float(pl.coef_[0,0])})

    q["p_raw"]=calibrated["RAW"]
    q["p_platt"]=calibrated["PLATT"]
    q["p_isotonic"]=calibrated["ISOTONIC"]
    q.to_csv(OUT/"global_xau_r2_stage3_probability_ledger.csv",index=False)
    pd.DataFrame(fit_audit).to_csv(OUT/"global_xau_r2_stage3_calibrator_fit_audit.csv",index=False)

    rows=[]; annual=[]
    for method,col in [("RAW","p_raw"),("PLATT","p_platt"),("ISOTONIC","p_isotonic")]:
        m=metrics(y,q[col])
        ci,cs=calibration_intercept_slope(y,q[col])
        ece,etable=ece_table(y,q[col])
        rows.append({"method":method,**m,"calibration_intercept":ci,"calibration_slope":cs,"ece":ece})
        for r in etable:
            r["method"]=method
        if method=="RAW":
            reliability=etable
        else:
            reliability.extend(etable)
        for yr,zr in q.groupby(q["forecast_issue_date"].dt.year):
            mm=metrics(zr["y_up"],zr[col])
            annual.append({"method":method,"year":int(yr),**mm})

    agg=pd.DataFrame(rows)
    ann=pd.DataFrame(annual)
    agg.to_csv(OUT/"global_xau_r2_stage3_calibration_metrics.csv",index=False)
    ann.to_csv(OUT/"global_xau_r2_stage3_calibration_annual.csv",index=False)
    pd.DataFrame(reliability).to_csv(OUT/"global_xau_r2_stage3_reliability_bins.csv",index=False)

    rawm=agg[agg.method=="RAW"].iloc[0]
    decisions=[]
    for method in ["PLATT","ISOTONIC"]:
        r=agg[agg.method==method].iloc[0]
        a=ann[ann.method==method].merge(ann[ann.method=="RAW"][["year","brier"]],on="year",suffixes=("","_raw"))
        a["rel_vs_raw"]=(a["brier_raw"]-a["brier"])/a["brier_raw"]
        gate=bool(
            (rawm.brier-r.brier)/rawm.brier>=0.005 and
            r.logloss<=rawm.logloss and
            r.prediction_std>=0.02 and
            int((a.rel_vs_raw>=0).sum())>=2 and
            float(a.rel_vs_raw.min())>=-0.02
        )
        decisions.append({"method":method,"replace_raw":gate,
                          "relative_brier_improvement_vs_raw":float((rawm.brier-r.brier)/rawm.brier),
                          "nonnegative_years":int((a.rel_vs_raw>=0).sum()),"worst_year_rel":float(a.rel_vs_raw.min())})
    ddf=pd.DataFrame(decisions)
    ddf.to_csv(OUT/"global_xau_r2_stage3_calibration_decisions.csv",index=False)

    passing=ddf[ddf.replace_raw]
    if passing.empty:
        selected="RAW"
    else:
        selected=str(agg[agg.method.isin(passing.method)].sort_values(["brier","logloss"]).iloc[0].method)
    scol={"RAW":"p_raw","PLATT":"p_platt","ISOTONIC":"p_isotonic"}[selected]

    q["selected_probability"]=q[scol]
    q["band"]=q["selected_probability"].map(band_name)
    band_rows=[]; band_year=[]
    order=["<=0.40","0.40-0.45","0.45-0.50","0.50-0.55","0.55-0.60",">=0.60"]
    for band in order:
        zb=q[q.band==band]
        if len(zb):
            band_rows.append({"band":band,**metrics(zb.y_up,zb.selected_probability)})
        else:
            band_rows.append({"band":band,"n":0,"brier":None,"logloss":None,"prediction_std":None,"mean_prediction":None,"actual_up_rate":None})
        for yr in [2022,2023,2024]:
            zy=zb[zb.forecast_issue_date.dt.year==yr]
            band_year.append({"band":band,"year":yr,"n":int(len(zy)),
                              "actual_up_rate":float(zy.y_up.mean()) if len(zy) else None,
                              "mean_prediction":float(zy.selected_probability.mean()) if len(zy) else None})
    bdf=pd.DataFrame(band_rows)
    bydf=pd.DataFrame(band_year)
    bdf.to_csv(OUT/"global_xau_r2_stage3_probability_bands.csv",index=False)
    bydf.to_csv(OUT/"global_xau_r2_stage3_probability_bands_by_year.csv",index=False)

    hi=q[q.selected_probability>=0.55]
    lo=q[q.selected_probability<=0.45]
    hi_years=[int((hi.forecast_issue_date.dt.year==yr).sum()) for yr in [2022,2023,2024]]
    lo_years=[int((lo.forecast_issue_date.dt.year==yr).sum()) for yr in [2022,2023,2024]]
    hi_rate=float(hi.y_up.mean()) if len(hi) else None
    lo_rate=float(lo.y_up.mean()) if len(lo) else None
    separation=(hi_rate-lo_rate) if (hi_rate is not None and lo_rate is not None) else None
    conviction=bool(
        len(hi)>=60 and len(lo)>=60 and
        hi_rate is not None and hi_rate>=0.575 and
        lo_rate is not None and lo_rate<=0.425 and
        separation is not None and separation>=0.15 and
        sum(n>=15 for n in hi_years)>=2 and
        sum(n>=15 for n in lo_years)>=2
    )

    summary={
        "status":"CONVICTION_PASS" if conviction else "NO_CONVICTION_PASS",
        "selected_calibration":selected,
        "raw_metrics":rawm.to_dict(),
        "calibration_decisions":decisions,
        "high_up_side":{"threshold":">=0.55","n":int(len(hi)),"actual_up_rate":hi_rate,"year_counts":hi_years},
        "low_up_side":{"threshold":"<=0.45","n":int(len(lo)),"actual_up_rate":lo_rate,"year_counts":lo_years},
        "up_rate_separation":separation,
        "conviction_gate_pass":conviction,
        "transport_2025":"UNOPENED",
    }

    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU R2 — Stage 3 Probability Calibration / Conviction Result","",
        f"**Status:** **{summary['status']}**","",
        f"Selected probability stream: **{selected}**","",
        "## Calibration metrics","",
        "| Method | Brier | Log loss | Pred SD | Cal intercept | Cal slope | ECE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in agg.iterrows():
        lines.append(f"| {r.method} | {r.brier:.6f} | {r.logloss:.6f} | {r.prediction_std:.4f} | {r.calibration_intercept:.4f} | {r.calibration_slope:.4f} | {r.ece:.4f} |")
    lines += ["","## Frozen probability bands","",
              "| Band | N | Mean p | Realized UP rate | Brier |",
              "|---|---:|---:|---:|---:|"]
    for _,r in bdf.iterrows():
        mp="—" if pd.isna(r.mean_prediction) else f"{r.mean_prediction:.3f}"
        ur="—" if pd.isna(r.actual_up_rate) else f"{100*r.actual_up_rate:.1f}%"
        br="—" if pd.isna(r.brier) else f"{r.brier:.4f}"
        lines.append(f"| {r.band} | {int(r.n)} | {mp} | {ur} | {br} |")
    lines += ["","## Conviction gate","",
              f"- p >= 0.55: n={len(hi)}, realized UP={100*hi_rate:.1f}%" if hi_rate is not None else f"- p >= 0.55: n={len(hi)}",
              f"- p <= 0.45: n={len(lo)}, realized UP={100*lo_rate:.1f}%" if lo_rate is not None else f"- p <= 0.45: n={len(lo)}",
              f"- UP-rate separation: {100*separation:.1f} pp" if separation is not None else "- UP-rate separation: unavailable",
              f"- conviction gate pass: **{conviction}**","",
              "2025 remained unopened. No P&L or cost threshold was tested."]
    (OUT/"STAGE3_RESULT.md").write_text("\n".join(lines)+"\n")

    files=[p for p in OUT.iterdir() if p.is_file()]
    summary["hashes"]={p.name:sha(p) for p in files}
    (OUT/"stage3_summary.json").write_text(json.dumps(summary,indent=2,default=str,sort_keys=True)+"\n")
    print("GLOBAL_XAU_R2_STAGE3_SUMMARY="+json.dumps(summary,sort_keys=True,default=str))
    print((OUT/"STAGE3_RESULT.md").read_text())

if __name__=="__main__":
    main()
