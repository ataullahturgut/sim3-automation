from __future__ import annotations

import argparse, csv, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

IDENTITY="DEFAULT_GOLD_DOWN_EXIT_LOGIT_V1_RESEARCH"
FEATURES=[
 "sqrt_score","lag1_close_return","downside_share","intraday_end_norm",
 "close_location","trough_recovery_norm","last_quarter_return_norm",
 "direct_up_fraction","legacy_up_fraction"
]
THRESHOLDS=[0.55,0.60,0.65,0.70,0.75]
DEV_END_YEAR=2023

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m
    assert spec.loader is not None; spec.loader.exec_module(m); return m

def fit(train):
    X=np.asarray([[r[k] for k in FEATURES] for r in train],float)
    y=np.asarray([r["actual_down"] for r in train],int)
    mu=X.mean(0); sd=X.std(0); sd=np.where(sd<1e-12,1.0,sd)
    m=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    m.fit((X-mu)/sd,y)
    return m,mu,sd

def probs(model,mu,sd,rows):
    X=np.asarray([[r[k] for k in FEATURES] for r in rows],float)
    return model.predict_proba((X-mu)/sd)[:,1]

def metrics(rows,threshold):
    y=np.asarray([r["actual_down"] for r in rows],int)
    p=np.asarray([r["p_down"] for r in rows],float)
    pred=(p>=threshold).astype(int)
    tp=int(np.sum((pred==1)&(y==1))); fp=int(np.sum((pred==1)&(y==0)))
    tn=int(np.sum((pred==0)&(y==0))); fn=int(np.sum((pred==0)&(y==1)))
    calls=tp+fp; ad=tp+fn; au=fp+tn
    auc=float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None
    return {
      "n":len(rows),"actual_down":ad,"actual_up":au,"down_calls":calls,
      "correct_down":tp,"false_exit_on_up":fp,"missed_down":fn,"kept_up":tn,
      "down_precision":tp/calls if calls else None,
      "down_recall":tp/ad if ad else None,
      "false_exit_fpr":fp/au if au else None,
      "up_retention":tn/au if au else None,
      "coverage":calls/len(rows) if rows else None,
      "balanced_accuracy":((tp/ad)+(tn/au))/2 if ad and au else None,
      "auc":auc
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
        out.append({
          "evaluation_year":y,"origin_date":r["origin_date"],"target_date":r["target_date"],
          "sqrt_alert":int(r["sqrt_high_risk_alert"]),
          "sqrt_score":float(r["sqrt_normalized_risk_score"]),
          "actual_up":int(float(r["target_close_return"])>0),
          "target_return":float(r["target_close_return"]),
        })
    return out

def score_period(train,test,threshold):
    m,mu,sd=fit(train)
    pp=probs(m,mu,sd,test)
    scored=[]
    for r,p in zip(test,pp):
      z=dict(r); z["p_down"]=float(p); z["down_exit"]=int(p>=threshold); scored.append(z)
    mm=metrics(scored,threshold)
    mm["train_n"]=len(train)
    mm["coefficients_standardized"]={k:float(v) for k,v in zip(FEATURES,m.coef_[0])}
    mm["intercept"]=float(m.intercept_[0])
    return scored,mm

def strategy(all_days, exits):
    exit_dates=set(exits)
    wealth=100.0; bh=100.0; oracle=100.0
    cash=0; gold=0
    maxw=100.0; maxdd=0.0
    path=[]
    for r in all_days:
      ret=float(r["target_return"]); down=ret<0
      bh*=math.exp(ret)
      if ret>0: oracle*=math.exp(ret)
      if r["target_date"] in exit_dates:
        cash+=1
      else:
        gold+=1; wealth*=math.exp(ret)
      maxw=max(maxw,wealth); maxdd=min(maxdd,wealth/maxw-1.0)
      path.append({"target_date":r["target_date"],"ret":ret,"cash":r["target_date"] in exit_dates,"wealth":wealth})
    return {
      "final_value":wealth,"return_pct":(wealth/100-1)*100,
      "buy_hold_final":bh,"buy_hold_return_pct":(bh/100-1)*100,
      "oracle_final":oracle,"oracle_return_pct":(oracle/100-1)*100,
      "cash_days":cash,"gold_days":gold,"max_drawdown_pct":maxdd*100
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2",type=Path,required=True)
    ap.add_argument("--route",type=Path,required=True)
    ap.add_argument("--cbr",type=Path,required=True)
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--sqrt-auth",type=Path,required=True)
    ap.add_argument("--sqrt-route-auth",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    up2=load_mod("up2_default_gold",a.up2)
    route=load_mod("route_default_gold",a.route)
    cbr=load_mod("cbr_default_gold",a.cbr)
    base=load_mod("base_default_gold",a.base)
    sqrt=load_mod("sqrt_default_gold",a.sqrt_auth)

    base.CUTOFF="2026-09-01T04:00:00Z"

    ext_spine=route.load_external_spine(a.external_spine)
    ext_raw=route.build_external_5m(a.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]: raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")
    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_route_auth)
    ext_sqrt,ext_summary=route.external_sqrt_cases(sqrt_mod,ext_daily)
    if ext_summary!={"2020":{"alarms":212,"down":97,"up":115},"2021":{"alarms":28,"down":16,"up":12}}:
      raise RuntimeError(f"EXTERNAL_SQRT_MISMATCH:{ext_summary}")
    ext_router,_=route.external_router_rows(base,ext_spine)
    ermap={(r["origin_date"],r["target_date"]):r for r in ext_router}
    esmap={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    elag=up2.lag_map_from_spine(ext_spine)
    external=[]
    for r in ext_sqrt:
      key=(r["origin_date"],r["target_date"]); rr=ermap[key]
      case={"evaluation_year":int(r["target_date"][:4]),"origin_date":r["origin_date"],
            "target_date":r["target_date"],"actual_up":int(r["actual_up"])}
      external.append(enrich(up2,case,float(r["sqrt_normalized_risk_score"]),rr,
        elag[r["origin_date"]],ext_raw[r["origin_date"]]["rets"],"EXTERNAL_ALL_SQRT_ALERTS"))

    gov_raw=cbr.load_paths(["2020-01-02","2026-08-31"])
    gov_days=base.load_days()
    gov_router=up2.build_governed_router_rows(base,gov_days)
    grmap={(r["origin_date"],r["target_date"]):r for r in gov_router}
    glag=up2.lag_map_from_base_days(gov_days)
    parent=read_parent(a.sqrt_parent)

    governed=[]
    daily_by_year={}
    for y in (2022,2023,2024,2025):
      all_y=[r for r in parent if r["evaluation_year"]==y]
      daily_by_year[y]=all_y
      for r in all_y:
        if r["sqrt_alert"]!=1: continue
        key=(r["origin_date"],r["target_date"]); rr=grmap[key]
        governed.append(enrich(up2,r,r["sqrt_score"],rr,glag[r["origin_date"]],
          gov_raw[r["origin_date"]],f"GOVERNED_ALL_SQRT_ALERTS_{y}"))

    # 2026 canonical expanding SQRT stress panel.
    ds,close,dr=sqrt.load_days(); srows=sqrt.build_rows(ds,close,dr)
    y26,saug=sqrt.yearly_fit_eval(srows,2026)
    all26=[]
    gov26=[]
    for s in saug:
      rr=grmap[(s["origin_date"],s["target_date"])]
      row={"evaluation_year":2026,"origin_date":s["origin_date"],"target_date":s["target_date"],
           "actual_up":int(float(s["target_close_return"])>0),
           "target_return":float(s["target_close_return"])}
      all26.append(row)
      if int(s["sqrt_high_risk_alert"])==1:
        gov26.append(enrich(up2,row,float(s["sqrt_normalized_risk_score"]),rr,
          glag[s["origin_date"]],gov_raw[s["origin_date"]],"GOVERNED_ALL_SQRT_ALERTS_2026"))
    daily_by_year[2026]=all26

    all_cases=external+governed+gov26

    # Development threshold selection: 2020-2023 only.
    dev_train=[r for r in all_cases if int(r["evaluation_year"])<=2022]
    dev_test=[r for r in all_cases if int(r["evaluation_year"])==2023]
    # To avoid a two-row 2023 target determining threshold, fit on 2020-2021 and
    # score all governed 2022-2023 chronologically as one development block.
    train_base=[r for r in all_cases if int(r["evaluation_year"])<=2021]
    dev_rows=[]
    for y in (2022,2023):
      tr=[r for r in all_cases if int(r["evaluation_year"])<y]
      te=[r for r in all_cases if int(r["evaluation_year"])==y]
      sc,_=score_period(tr,te,0.50)
      dev_rows.extend(sc)

    grid=[]
    base_rate=sum(r["actual_down"] for r in dev_rows)/len(dev_rows)
    for th in THRESHOLDS:
      m=metrics(dev_rows,th); eligible=bool(
        m["down_calls"]>=5 and m["down_precision"] is not None and m["down_precision"]>base_rate
        and m["false_exit_fpr"] is not None and m["false_exit_fpr"]<=0.30
      )
      grid.append({"threshold":th,"eligible":eligible,"metrics":m})
    elig=[g for g in grid if g["eligible"]]
    if elig:
      elig.sort(key=lambda g:(-(g["metrics"]["down_recall"] or -1),-(g["metrics"]["down_precision"] or -1),g["threshold"]))
      selected=elig[0]
      selection_status="ELIGIBLE_THRESHOLD_SELECTED"
    else:
      # Fail closed: no DOWN exit calls authorized if development gate fails.
      selected=None; selection_status="NO_ELIGIBLE_THRESHOLD"

    result={"identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION",
      "objective":"DEFAULT GOLD; move to CASH only on positive DOWN-exit evidence inside SQRT HIGH-RISK days",
      "features":FEATURES,
      "model":"L2 logistic regression C=1.0 on actual DOWN among all SQRT HIGH-RISK alarms",
      "development":{"years":"2020-2023","threshold_grid":grid,"down_base_rate":base_rate,
        "selection_rule":"calls>=5, precision>development DOWN base rate, false-exit FPR<=30%; maximize DOWN recall, tie precision"},
      "selection_status":selection_status,
      "external_sqrt_summary":ext_summary,
      "governance":{"random_split":False,"2025_used_for_selection":False,"2026_used_for_selection":False,
        "default_position":"GOLD","cash_only_on_positive_down_exit":True,
        "canonical_branch_modified":False,"production_writes":False,"runtime_promotion":False}
    }

    if selected is not None:
      th=float(selected["threshold"]); result["selected_threshold"]=th
      yearly={}
      ledgers={}
      for y in (2024,2025,2026):
        tr=[r for r in all_cases if int(r["evaluation_year"])<y]
        te=[r for r in all_cases if int(r["evaluation_year"])==y]
        sc,m=score_period(tr,te,th)
        yearly[str(y)]=m
        ledgers[str(y)]=[{"target_date":r["target_date"],"p_down":r["p_down"],"down_exit":r["down_exit"],
                          "actual_down":r["actual_down"]} for r in sc]
        exits=[r["target_date"] for r in sc if r["down_exit"]==1]
        if y in daily_by_year:
          yearly[str(y)]["strategy"]=strategy(daily_by_year[y],exits)
      result["yearly"]=yearly
      result["ledgers"]=ledgers
      # Validation interpretation is descriptive; no threshold rescue after 2024.
      v=yearly["2024"]
      result["validation_2024_pass"]=bool(v["down_calls"]>=2 and v["down_precision"] is not None and
          v["down_precision"]>v["actual_down"]/v["n"] and v["false_exit_fpr"] is not None and v["false_exit_fpr"]<0.50)
      if not result["validation_2024_pass"]:
        result["status"]="NOT_SUPPORTED_PRE2025_VALIDATION"
      else:
        result["status"]="PRE2025_VALIDATION_SUPPORTIVE_RESEARCH_ONLY"

    out=a.out/"GOLD_CONTROL_DEFAULT_GOLD_DOWN_EXIT_LOGIT_V1_RESULT_2026-09-24.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
