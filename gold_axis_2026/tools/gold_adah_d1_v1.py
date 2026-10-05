from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"ADAH_D1_V1_OUT"
OUT.mkdir(exist_ok=True)

OPAL=AX/"GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv"
AURORA=AX/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PRICE=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
CIG=AX/"GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv"

ACTION_LO=0.35
ACTION_HI=0.65
K=9
KAPPA=4.0
CANDIDATES=["DBH93","DBH97","ANALOG9","ENSEMBLE"]

def dt(s): return pd.to_datetime(s,errors="coerce").dt.normalize()
def b(x): return x.astype(str).str.lower().eq("true")
def clip(p): return float(np.clip(p,1e-6,1-1e-6))
def logloss(y,p):
    p=clip(p); return -(y*math.log(p)+(1-y)*math.log(1-p))

def build_events():
    op=pd.read_csv(OPAL); op["feature_cutoff_date"]=dt(op["feature_cutoff_date"]); op["forecast_issue_date"]=dt(op["forecast_issue_date"])
    pn=pd.read_csv(PANEL); pn["feature_cutoff_date"]=dt(pn["feature_cutoff_date"]); pn["cot_available_date"]=dt(pn["cot_available_date"])
    a=pd.read_csv(AURORA); a["feature_cutoff_date"]=dt(a["feature_cutoff_date"])
    v=pd.read_csv(V5); v["feature_cutoff_date"]=dt(v["feature_cutoff_date"])
    px=pd.read_csv(PRICE); px["date"]=dt(px["date"]); pmap=dict(zip(px.date,px.gold.astype(float)))

    z=op.drop(columns=["cot_report_date","cot_available_date"],errors="ignore").merge(pn[[
      "feature_cutoff_date","trend_strength","cot_report_date","cot_available_date",
      "opt_mm_z52","opt_swap_z52","spec_swap_gap"
    ]],on="feature_cutoff_date",how="inner")
    z=z.merge(a[["feature_cutoff_date","p_aurora"]],on="feature_cutoff_date",how="inner",suffixes=("","_clean"))
    z=z.merge(v[["feature_cutoff_date","p_helios_v5_dce"]],on="feature_cutoff_date",how="inner")
    z=z[b(z["override"])].copy()
    z["opal_dir"]=(z["p_opal"].astype(float)>=0.5).astype(int)
    z["aurora_dir"]=(z["p_aurora_clean"].astype(float)>=0.5).astype(int)
    z["v5_dir"]=(z["p_helios_v5_dce"].astype(float)>=0.5).astype(int)
    z["final_v5_flip"]=(z.opal_dir!=z.aurora_dir)&(z.v5_dir!=z.aurora_dir)
    z["gold0"]=z.feature_cutoff_date.map(pmap)
    z["gold1"]=z.forecast_issue_date.map(pmap)
    z=z.dropna(subset=["gold0","gold1"]).copy()
    z["d1_actual"]=(z.gold1>z.gold0).astype(int)
    z["immediate"]=(z.d1_actual==z.opal_dir).astype(int)
    z["cot_age_days"]=(z.feature_cutoff_date-z.cot_available_date).dt.days.astype(float)
    z["fresh"]=(z.cot_age_days<=2).astype(int)
    z["year"]=z.forecast_issue_date.dt.year.astype(int)
    z["month"]=z.forecast_issue_date.dt.strftime("%Y-%m")
    for c in ["p_reversal","trend_strength","opt_mm_z52","opt_swap_z52","spec_swap_gap","cot_age_days"]:
        z[c]=pd.to_numeric(z[c],errors="coerce")
    z=z.dropna(subset=["p_reversal","trend_strength","opt_mm_z52","opt_swap_z52","spec_swap_gap","cot_age_days"])
    return z.sort_values(["feature_cutoff_date","forecast_issue_date"]).reset_index(drop=True)

FEATURES=["p_reversal","trend_strength","opt_mm_z52","opt_swap_z52","spec_swap_gap","cot_age_days","opal_dir"]

def weighted_prob(hist, row, lam):
    if len(hist)==0:return 0.5
    age_days=(row.feature_cutoff_date-hist.feature_cutoff_date).dt.days.clip(lower=0).astype(float)
    w=np.power(lam,age_days/30.0)
    # global
    sg=float(np.sum(w*hist.immediate.to_numpy(float))); ng=float(np.sum(w))
    pg=(0.5+sg)/(1.0+ng)
    # direction x fresh cell
    mask=(hist.opal_dir.to_numpy(int)==int(row.opal_dir))&(hist.fresh.to_numpy(int)==int(row.fresh))
    wc=w.to_numpy()[mask]
    yy=hist.immediate.to_numpy(float)[mask]
    nc=float(wc.sum()); sc=float(np.sum(wc*yy)) if len(wc) else 0.0
    pc=(0.5+sc)/(1.0+nc)
    shrink=nc/(nc+KAPPA)
    return clip(shrink*pc+(1-shrink)*pg)

def analog_prob(hist,row):
    if len(hist)<3:return 0.5
    X=hist[FEATURES].to_numpy(float); q=np.array([getattr(row,c) for c in FEATURES],float)
    med=np.nanmedian(X,axis=0)
    q25=np.nanpercentile(X,25,axis=0); q75=np.nanpercentile(X,75,axis=0)
    scale=q75-q25
    sd=np.nanstd(X,axis=0,ddof=0)
    scale=np.where(scale>1e-9,scale,np.where(sd>1e-9,sd,1.0))
    Z=(X-med)/scale; zq=(q-med)/scale
    dist=np.sqrt(np.sum((Z-zq)**2,axis=1))
    idx=np.argsort(dist)[:min(K,len(hist))]
    sel=hist.iloc[idx]
    dd=dist[idx]
    age=(row.feature_cutoff_date-sel.feature_cutoff_date).dt.days.clip(lower=0).to_numpy(float)
    w=np.exp(-dd)*np.exp(-age/365.0)
    n=float(w.sum()); s=float(np.sum(w*sel.immediate.to_numpy(float)))
    return clip((0.5+s)/(1.0+n))

def predict_prequential(z):
    rows=[]
    for i,row in z.iterrows():
        hist=z.iloc[:i]
        p93=weighted_prob(hist,row,0.93)
        p97=weighted_prob(hist,row,0.97)
        pa=analog_prob(hist,row)
        pe=clip((p97+pa)/2.0)
        rows.append({
          "feature_cutoff_date":row.feature_cutoff_date,
          "forecast_issue_date":row.forecast_issue_date,
          "year":int(row.year),"month":row.month,
          "immediate":int(row.immediate),"opal_dir":int(row.opal_dir),"aurora_dir":int(row.aurora_dir),"v5_dir":int(row.v5_dir),
          "final_v5_flip":bool(row.final_v5_flip),"fresh":int(row.fresh),"cot_age_days":float(row.cot_age_days),
          "p_reversal":float(row.p_reversal),
          "DBH93":p93,"DBH97":p97,"ANALOG9":pa,"ENSEMBLE":pe
        })
    return pd.DataFrame(rows)

def score(df,pcol):
    if len(df)==0:return {"n":0,"brier":None,"logloss":None,"acc":None}
    y=df.immediate.to_numpy(int); p=df[pcol].to_numpy(float)
    return {
      "n":int(len(df)),
      "brier":float(np.mean((p-y)**2)),
      "logloss":float(np.mean([logloss(int(a),float(b)) for a,b in zip(y,p)])),
      "acc":float(np.mean((p>=0.5).astype(int)==y))
    }

def static_global_predictions(z):
    ps=[]
    for i,row in z.iterrows():
        h=z.iloc[:i]
        if len(h)==0: ps.append(0.5)
        else: ps.append((0.5+float(h.immediate.sum()))/(1.0+len(h)))
    return np.array(ps,float)

def selective(df,pcol):
    acts=[]
    for r in df.itertuples(index=False):
        p=float(getattr(r,pcol))
        if p>=ACTION_HI:
            pred=int(r.opal_dir); src="OPAL"
        elif p<=ACTION_LO:
            pred=int(r.aurora_dir); src="AURORA"
        else:
            pred=None; src="ABSTAIN"
        acts.append((pred,src,p))
    d=df.copy()
    d["sel_pred"]=[x[0] for x in acts]
    d["sel_source"]=[x[1] for x in acts]
    d["sel_p"]=[x[2] for x in acts]
    a=d[d.sel_pred.notna()].copy()
    return d,{
      "n":int(len(d)),
      "actions":int(len(a)),
      "coverage":float(len(a)/len(d)) if len(d) else None,
      "correct":int((a.sel_pred.astype(int)==a.immediate.map(lambda y: None)).sum()) if False else int((a.sel_pred.astype(int)==a.apply(lambda x:int(x.opal_dir) if int(x.immediate)==1 else int(x.aurora_dir),axis=1)).sum()),
      "accuracy":float((a.sel_pred.astype(int)==a.apply(lambda x:int(x.opal_dir) if int(x.immediate)==1 else int(x.aurora_dir),axis=1)).mean()) if len(a) else None
    }

def main():
    z=build_events()
    pr=predict_prequential(z)
    pr["STATIC"]=static_global_predictions(z)

    sel_rows=[]
    for cand in CANDIDATES:
        s=score(pr[pr.year==2024],cand)
        sel_rows.append({"candidate":cand,**s})
    sel=pd.DataFrame(sel_rows)
    order={x:i for i,x in enumerate(CANDIDATES)}
    sel["_ord"]=sel.candidate.map(order)
    selected=str(sel.sort_values(["brier","logloss","_ord"],ascending=[True,True,True]).iloc[0].candidate)

    static2025=score(pr[pr.year==2025],"STATIC")
    chosen2025=score(pr[pr.year==2025],selected)
    flip25=pr[(pr.year==2025)&pr.final_v5_flip].copy()
    flip25d,flip25s=selective(flip25,selected)
    confirm=bool(
      chosen2025["brier"]<=static2025["brier"] and
      flip25s["actions"]>=4 and
      flip25s["accuracy"] is not None and flip25s["accuracy"]>=0.70 and
      (flip25s["actions"]-flip25s["correct"])<=2
    )

    test26=score(pr[pr.year==2026],selected)
    flip26=pr[(pr.year==2026)&pr.final_v5_flip].copy()
    flip26d,flip26s=selective(flip26,selected)

    # CIG integration: only 2026 replay exists.
    cig=pd.read_csv(CIG); cig["feature_cutoff_date"]=dt(cig["feature_cutoff_date"]); cig["forecast_issue_date"]=dt(cig["forecast_issue_date"])
    pmap=pr.set_index("feature_cutoff_date")
    integ=[]
    for x in cig.itertuples(index=False):
        new=x.consensus; src="UNCHANGED"; prob=np.nan
        if x.consensus=="UNCERTAIN" and x.feature_cutoff_date in pmap.index:
            r=pmap.loc[x.feature_cutoff_date]
            if isinstance(r,pd.DataFrame): r=r.iloc[0]
            if bool(r.final_v5_flip):
                prob=float(r[selected])
                if prob>=ACTION_HI:
                    new="UP" if int(r.opal_dir)==1 else "DOWN"; src="ADAH_OPAL"
                elif prob<=ACTION_LO:
                    new="UP" if int(r.aurora_dir)==1 else "DOWN"; src="ADAH_AURORA"
                else:
                    src="ADAH_ABSTAIN"
        integ.append({
          "feature_cutoff_date":x.feature_cutoff_date,
          "forecast_issue_date":x.forecast_issue_date,
          "actual":x.d1_actual,
          "original_consensus":x.consensus,
          "adah_consensus":new,
          "adah_source":src,
          "p_immediate":prob
        })
    integ=pd.DataFrame(integ)
    def cstat(q,col):
        a=q[q[col]!="UNCERTAIN"]
        return {"n":len(q),"actions":len(a),"coverage":float(len(a)/len(q)) if len(q) else None,
          "correct":int((a[col]==a.actual).sum()),"accuracy":float((a[col]==a.actual).mean()) if len(a) else None}
    sum26={
      "original":cstat(integ,"original_consensus"),
      "adah":cstat(integ,"adah_consensus")
    }
    aug=integ[integ.forecast_issue_date.dt.strftime("%Y-%m")=="2026-08"].copy()
    sumaug={"original":cstat(aug,"original_consensus"),"adah":cstat(aug,"adah_consensus")}
    aug_unc=aug[aug.original_consensus=="UNCERTAIN"].copy()

    promotion=bool(
      confirm and
      sum26["adah"]["accuracy"]>=sum26["original"]["accuracy"] and
      sumaug["adah"]["accuracy"] is not None and sumaug["adah"]["accuracy"]>=0.75 and
      (sumaug["adah"]["actions"]-sumaug["original"]["actions"])>=3
    )

    out={
      "identity":"ADAH_D1_V1",
      "status":"PROMOTION_PASS" if promotion else "REJECTED_OR_DIAGNOSTIC",
      "selected_candidate":selected,
      "selection_2024":sel.drop(columns=["_ord"]).to_dict("records"),
      "confirmation_2025":{
        "selected":chosen2025,"static":static2025,"final_flip_selective":flip25s,"pass":confirm
      },
      "test_2026":{
        "all_override":test26,"final_flip_selective":flip26s
      },
      "cig_2026":sum26,
      "cig_august_2026":sumaug,
      "promotion_pass":promotion,
      "governance":{
        "action_band":[ACTION_LO,ACTION_HI],
        "selection_year":2024,
        "confirmation_year":2025,
        "holdout_year":2026,
        "online_update":"strictly prior matured OPAL events only"
      }
    }

    sel.drop(columns=["_ord"]).to_csv(OUT/"ADAH_D1_V1_SELECTION_2024.csv",index=False)
    pr.to_csv(OUT/"ADAH_D1_V1_PREQUENTIAL_EVENTS.csv",index=False)
    integ.to_csv(OUT/"ADAH_D1_V1_CIG_INTEGRATION.csv",index=False)
    aug_unc.to_csv(OUT/"ADAH_D1_V1_AUGUST_UNCERTAIN.csv",index=False)
    (OUT/"ADAH_D1_V1_RESULT.json").write_text(json.dumps(out,indent=2,default=str)+"\n")

    def pct(x): return "—" if x is None else f"{100*x:.2f}%"
    lines=[
      "# ADAH-D1 V1 — Adaptive Direction-Age Hazard Result","",
      f"**Selected 2024 candidate:** **{selected}**  ",
      f"**2025 confirmation:** **{'PASS' if confirm else 'FAIL'}**  ",
      f"**Promotion:** **{'PASS' if promotion else 'FAIL'}**","",
      "## 2024 candidate selection","",
      "| Candidate | N | Brier | Log loss | Directional acc |",
      "|---|---:|---:|---:|---:|"
    ]
    for rr in sel.drop(columns=["_ord"]).itertuples(index=False):
        lines.append(f"| {rr.candidate} | {rr.n} | {rr.brier:.4f} | {rr.logloss:.4f} | {pct(rr.acc)} |")
    lines += ["","## 2025 confirmation","",
      f"- selected Brier: **{chosen2025['brier']:.4f}** vs static **{static2025['brier']:.4f}**",
      f"- final V5 flip selective actions: **{flip25s['actions']}/{flip25s['n']}**",
      f"- selective accuracy: **{pct(flip25s['accuracy'])}**",
      f"- confirmation: **{'PASS' if confirm else 'FAIL'}**","",
      "## 2026 frozen test","",
      f"- all OPAL overrides Brier: **{test26['brier']:.4f}**",
      f"- final V5 flip actions: **{flip26s['actions']}/{flip26s['n']}**",
      f"- final V5 flip selective accuracy: **{pct(flip26s['accuracy'])}**","",
      "## CIG integration","",
      "| Period | Original actions | Original acc | ADAH actions | ADAH acc | Original coverage | ADAH coverage |",
      "|---|---:|---:|---:|---:|---:|---:|",
      f"| 2026 | {sum26['original']['actions']} | {pct(sum26['original']['accuracy'])} | {sum26['adah']['actions']} | {pct(sum26['adah']['accuracy'])} | {pct(sum26['original']['coverage'])} | {pct(sum26['adah']['coverage'])} |",
      f"| 2026-08 | {sumaug['original']['actions']} | {pct(sumaug['original']['accuracy'])} | {sumaug['adah']['actions']} | {pct(sumaug['adah']['accuracy'])} | {pct(sumaug['original']['coverage'])} | {pct(sumaug['adah']['coverage'])} |",
      "","## August original UNCERTAIN dates","",
      "| Issue | Actual | p(immediate) | ADAH |",
      "|---|---|---:|---|"
    ]
    for rr in aug_unc.itertuples(index=False):
        lines.append(f"| {rr.forecast_issue_date.date()} | {rr.actual} | {'' if pd.isna(rr.p_immediate) else f'{rr.p_immediate:.3f}'} | {rr.adah_consensus} / {rr.adah_source} |")
    lines += ["","## Decision","",
      "ADAH is promoted only if the preregistered 2025 confirmation gate passes and the 2026/August promotion constraints pass. No 2026 result is used to alter the candidate, state definition, forgetting rate, analog k, or action thresholds."
    ]
    (OUT/"ADAH_D1_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"ADAH_D1_V1_RESULT.md").read_text())
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    main()
