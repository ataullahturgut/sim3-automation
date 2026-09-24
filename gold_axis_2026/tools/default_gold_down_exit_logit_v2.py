from __future__ import annotations

import argparse, csv, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

IDENTITY="DEFAULT_GOLD_DOWN_EXIT_LOGIT_V2_RESEARCH"
FEATURES=[
 "sqrt_score","lag1_close_return","downside_share","intraday_end_norm",
 "close_location","trough_recovery_norm","last_quarter_return_norm",
 "direct_up_fraction","legacy_up_fraction"
]
THRESHOLDS=[0.55,0.60,0.65,0.70,0.75]
MIN_PREQ=80

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m
    assert spec.loader is not None; spec.loader.exec_module(m); return m

def fit(train):
    X=np.asarray([[r[k] for k in FEATURES] for r in train],float)
    y=np.asarray([r["actual_down"] for r in train],int)
    if len(np.unique(y))<2: raise RuntimeError("ONE_CLASS_TRAIN")
    mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-12,1.0,sd)
    m=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    m.fit((X-mu)/sd,y)
    return m,mu,sd

def predict(model,mu,sd,rows):
    X=np.asarray([[r[k] for k in FEATURES] for r in rows],float)
    return model.predict_proba((X-mu)/sd)[:,1]

def prequential(rows):
    rows=sorted(rows,key=lambda r:r["target_date"])
    out=[]
    for i in range(MIN_PREQ,len(rows)):
      prior=rows[:i]
      m,mu,sd=fit(prior)
      p=float(predict(m,mu,sd,[rows[i]])[0])
      z=dict(rows[i]); z["p_down"]=p; out.append(z)
    return out

def metrics(rows,threshold):
    y=np.asarray([r["actual_down"] for r in rows],int)
    p=np.asarray([r["p_down"] for r in rows],float)
    pred=(p>=threshold).astype(int)
    tp=int(np.sum((pred==1)&(y==1))); fp=int(np.sum((pred==1)&(y==0)))
    tn=int(np.sum((pred==0)&(y==0))); fn=int(np.sum((pred==0)&(y==1)))
    calls=tp+fp; ad=tp+fn; au=fp+tn
    return {
      "n":len(rows),"actual_down":ad,"actual_up":au,"down_calls":calls,
      "correct_down":tp,"false_exit_on_up":fp,"missed_down":fn,"kept_up":tn,
      "down_precision":tp/calls if calls else None,"down_recall":tp/ad if ad else None,
      "false_exit_fpr":fp/au if au else None,"up_retention":tn/au if au else None,
      "coverage":calls/len(rows) if rows else None,
      "balanced_accuracy":((tp/ad)+(tn/au))/2 if ad and au else None,
      "auc":float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None
    }

def enrich(up2,case,sqrt_score,router_row,lag1,rets,source):
    z=up2.enrich_case(case,sqrt_score,router_row,lag1,rets,source)
    z["actual_down"]=1-int(z["actual_up"])
    return z

def read_parent(path):
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
      for r in csv.DictReader(f):
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025): continue
        out.append({"evaluation_year":y,"origin_date":r["origin_date"],"target_date":r["target_date"],
          "sqrt_alert":int(r["sqrt_high_risk_alert"]),"sqrt_score":float(r["sqrt_normalized_risk_score"]),
          "actual_up":int(float(r["target_close_return"])>0),"target_return":float(r["target_close_return"])})
    return out

def raw_router_rows(base,days):
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays); lmaps=base.logit_maps(ldays); contexts=base.legacy_context(daily)
    tmap={r["target_date"]:r for r in trows}
    common=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    out=[]
    for td in common:
      t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]
      od=t["origin_date"]; ctx=contexts[od]
      out.append({"origin_date":od,"target_date":td,"actual_up":int(t["actual_up"]),
        "TTSM_S2":int(t["ttsm_s2_signal"]==1),"TTSM_S1":int(t["ttsm_s1_signal"]==1),
        "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),"AR1_RM_LOGIT":int(ar["up"]),"RM_LOGIT":int(rm["up"]),**ctx})
    return out

def score_year(train,test,threshold):
    m,mu,sd=fit(train); pp=predict(m,mu,sd,test)
    out=[]
    for r,p in zip(test,pp):
      z=dict(r); z["p_down"]=float(p); z["down_exit"]=int(p>=threshold); out.append(z)
    mm=metrics(out,threshold); mm["train_n"]=len(train)
    mm["coefficients_standardized"]={k:float(v) for k,v in zip(FEATURES,m.coef_[0])}
    return out,mm

def strategy(days,exit_dates):
    exits=set(exit_dates); w=100.; bh=100.; oracle=100.; maxw=100.; maxdd=0.; cash=gold=0
    for r in days:
      ret=float(r["target_return"]); bh*=math.exp(ret)
      if ret>0: oracle*=math.exp(ret)
      if r["target_date"] in exits: cash+=1
      else: gold+=1; w*=math.exp(ret)
      maxw=max(maxw,w); maxdd=min(maxdd,w/maxw-1)
    return {"final_value":w,"return_pct":(w/100-1)*100,"buy_hold_final":bh,"buy_hold_return_pct":(bh/100-1)*100,
      "oracle_final":oracle,"oracle_return_pct":(oracle/100-1)*100,"cash_days":cash,"gold_days":gold,
      "max_drawdown_pct":maxdd*100}

def main():
    ap=argparse.ArgumentParser()
    for name in ["up2","route","cbr","base","sqrt-auth","sqrt-route-auth","sqrt-parent","external-spine","raw-root","out"]:
      ap.add_argument("--"+name,type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    up2=load_mod("up2_dg_v2",a.up2); route=load_mod("route_dg_v2",a.route); cbr=load_mod("cbr_dg_v2",a.cbr)
    base=load_mod("base_dg_v2",a.base); sqrt=load_mod("sqrt_dg_v2",getattr(a,"sqrt_auth"))
    base.CUTOFF="2026-09-01T04:00:00Z"

    ext_spine=route.load_external_spine(getattr(a,"external_spine"))
    ext_raw=route.build_external_5m(getattr(a,"raw_root"))
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]: raise RuntimeError("EXT_RECON_FAIL")
    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    smod=route.load_sqrt_mod(getattr(a,"sqrt_route_auth"))
    ext_sqrt,ext_summary=route.external_sqrt_cases(smod,ext_daily)
    if ext_summary!={"2020":{"alarms":212,"down":97,"up":115},"2021":{"alarms":28,"down":16,"up":12}}:
      raise RuntimeError("EXT_SQRT_MISMATCH")
    ext_router,_=route.external_router_rows(base,ext_spine)
    ermap={(r["origin_date"],r["target_date"]):r for r in ext_router}
    elag=up2.lag_map_from_spine(ext_spine)
    cases=[]
    for r in ext_sqrt:
      rr=ermap[(r["origin_date"],r["target_date"])]
      case={"evaluation_year":int(r["target_date"][:4]),"origin_date":r["origin_date"],"target_date":r["target_date"],
        "actual_up":int(float(r["target_return"])>0)}
      cases.append(enrich(up2,case,float(r["sqrt_normalized_risk_score"]),rr,elag[r["origin_date"]],
        ext_raw[r["origin_date"]]["rets"],"EXTERNAL_ALL_SQRT_ALERTS"))

    gov_raw=cbr.load_paths(["2020-01-02","2026-08-31"])
    gov_days=base.load_days(); grow=raw_router_rows(base,gov_days); grmap={(r["origin_date"],r["target_date"]):r for r in grow}
    glag=up2.lag_map_from_base_days(gov_days)
    parent=read_parent(getattr(a,"sqrt_parent"))
    daily={}
    missing=[]
    for y in (2022,2023,2024,2025):
      yy=[r for r in parent if r["evaluation_year"]==y]; daily[y]=yy
      for r in yy:
        if r["sqrt_alert"]!=1: continue
        rr=grmap.get((r["origin_date"],r["target_date"]))
        if rr is None or r["origin_date"] not in glag or r["origin_date"] not in gov_raw:
          missing.append(r["target_date"]); continue
        cases.append(enrich(up2,r,r["sqrt_score"],rr,glag[r["origin_date"]],gov_raw[r["origin_date"]],
          f"GOVERNED_ALL_SQRT_ALERTS_{y}"))

    ds,close,dr=sqrt.load_days(); srows=sqrt.build_rows(ds,close,dr); _,saug=sqrt.yearly_fit_eval(srows,2026)
    all26=[]
    for s in saug:
      row={"evaluation_year":2026,"origin_date":s["origin_date"],"target_date":s["target_date"],
        "actual_up":int(float(s["target_close_return"])>0),"target_return":float(s["target_close_return"])}
      all26.append(row)
      if int(s["sqrt_high_risk_alert"])!=1: continue
      rr=grmap.get((s["origin_date"],s["target_date"]))
      if rr is None or s["origin_date"] not in glag or s["origin_date"] not in gov_raw:
        missing.append(s["target_date"]); continue
      cases.append(enrich(up2,row,float(s["sqrt_normalized_risk_score"]),rr,glag[s["origin_date"]],
        gov_raw[s["origin_date"]],"GOVERNED_ALL_SQRT_ALERTS_2026"))
    daily[2026]=all26

    dev=[r for r in cases if int(r["evaluation_year"])<=2023]
    preq=prequential(dev)
    base_rate=sum(r["actual_down"] for r in preq)/len(preq)
    grid=[]
    for th in THRESHOLDS:
      m=metrics(preq,th); eligible=bool(m["down_calls"]>=10 and m["down_precision"] is not None and
        m["down_precision"]>base_rate and m["false_exit_fpr"] is not None and m["false_exit_fpr"]<=0.30)
      grid.append({"threshold":th,"eligible":eligible,"metrics":m})
    eligible=[x for x in grid if x["eligible"]]
    if eligible:
      eligible.sort(key=lambda x:(-(x["metrics"]["down_recall"] or -1),-(x["metrics"]["down_precision"] or -1),x["threshold"]))
      sel=eligible[0]; th=float(sel["threshold"]); select_status="ELIGIBLE_THRESHOLD_SELECTED"
    else:
      sel=None; th=None; select_status="NO_ELIGIBLE_THRESHOLD"

    result={"identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION","objective":"DEFAULT GOLD; CASH only on positive DOWN evidence",
      "method":{"features":FEATURES,"model":"L2 LogisticRegression C=1.0","min_prequential_history":MIN_PREQ,
        "threshold_grid":THRESHOLDS,"selection":"2020-2023 strictly prequential scores; calls>=10; precision>base rate; false-exit FPR<=30%; maximize DOWN recall"},
      "development":{"prequential_n":len(preq),"down_base_rate":base_rate,"grid":grid},
      "selection_status":select_status,"selected_threshold":th,"missing_feature_dates":missing,
      "governance":{"random_split":False,"2025_used_for_selection":False,"2026_used_for_selection":False,
        "default_position":"GOLD","cash_only_on_positive_down_exit":True,"canonical_branch_modified":False,
        "production_writes":False,"runtime_promotion":False}}

    if sel is not None:
      yearly={}
      for y in (2024,2025,2026):
        tr=[r for r in cases if int(r["evaluation_year"])<y]
        te=[r for r in cases if int(r["evaluation_year"])==y]
        sc,m=score_year(tr,te,th)
        m["strategy"]=strategy(daily[y],[r["target_date"] for r in sc if r["down_exit"]==1])
        yearly[str(y)]=m
      result["yearly"]=yearly
      v=yearly["2024"]
      result["validation_2024_pass"]=bool(v["down_calls"]>=2 and v["down_precision"] is not None and
        v["down_precision"]>(v["actual_down"]/v["n"]) and v["false_exit_fpr"] is not None and v["false_exit_fpr"]<0.50)
      result["status"]="PRE2025_VALIDATION_SUPPORTIVE_RESEARCH_ONLY" if result["validation_2024_pass"] else "NOT_SUPPORTED_PRE2025_VALIDATION"

    out=a.out/"GOLD_CONTROL_DEFAULT_GOLD_DOWN_EXIT_LOGIT_V2_RESULT_2026-09-24.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
