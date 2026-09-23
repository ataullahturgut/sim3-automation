from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

IDENTITY="UP2_STRICT_PREQUENTIAL_ERROR_POOL_2019_2021_V1_RESEARCH"
MIN_HISTORY=40
MIN_DOWN_CAL=20


def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_FAIL:{name}:{path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def build_raw_2019_2021(raw_root: Path):
    ask_dir=raw_root/"xauusd"/"ask"/"m1"
    bid_dir=raw_root/"xauusd"/"bid"/"m1"
    patterns=[f"xauusd_ask_m1_{y}_*.csv" for y in (2019,2020,2021)]
    ask_files=[]
    for p in patterns: ask_files += sorted(ask_dir.glob(p))
    ask_files += sorted(ask_dir.glob("xauusd_ask_m1_2022_01.csv"))
    patterns=[f"xauusd_bid_m1_{y}_*.csv" for y in (2019,2020,2021)]
    bid_files=[]
    for p in patterns: bid_files += sorted(bid_dir.glob(p))
    bid_files += sorted(bid_dir.glob("xauusd_bid_m1_2022_01.csv"))
    if len(ask_files)!=37 or len(bid_files)!=37:
        raise RuntimeError(f"RAW_FILE_COUNT:{len(ask_files)}/{len(bid_files)}")

    def read_side(files,side):
        frames=[]
        for p in files:
            z=pd.read_csv(p,usecols=["timestamp","close"])
            z["timestamp"]=pd.to_numeric(z["timestamp"],errors="raise").astype("int64")
            z["close"]=pd.to_numeric(z["close"],errors="raise").astype(float)
            z=z.rename(columns={"close":f"close_{side}"})
            frames.append(z)
        out=pd.concat(frames,ignore_index=True)
        return out.drop_duplicates("timestamp",keep="last").sort_values("timestamp")

    ask=read_side(ask_files,"ask")
    bid=read_side(bid_files,"bid")
    m=bid.merge(ask,on="timestamp",how="inner",validate="one_to_one")
    m["mid"]=(m["close_bid"]+m["close_ask"])/2.0
    m["dt_utc"]=pd.to_datetime(m["timestamp"],unit="ms",utc=True)
    m["bin_utc"]=m["dt_utc"].dt.floor("5min")
    bars=(m.sort_values("timestamp").groupby("bin_utc",as_index=False).agg(mid=("mid","last")))
    bars["dt_ny"]=bars["bin_utc"].dt.tz_convert("America/New_York")
    bars=bars[(bars["dt_ny"].dt.weekday<5)&(bars["dt_ny"].dt.hour!=17)].copy()
    bars["date"]=bars["dt_ny"].dt.strftime("%Y-%m-%d")
    bars=bars.sort_values(["date","bin_utc"])

    out={}
    for d,g in bars.groupby("date",sort=True):
        if not d.startswith(("2019-","2020-","2021-")): continue
        close=g["mid"].to_numpy(float)
        if len(close)<240: continue
        rets=np.diff(np.log(close))
        rv=float(np.sum(rets*rets))
        if not math.isfinite(rv) or rv<=0: continue
        out[d]={
            "n_bars":len(close),
            "close":float(close[-1]),
            "rv":rv,
            "dr":float(np.sum(np.where(rets<=0,rets*rets,0.0))),
            "r3":float(np.sum(rets**3)),
            "rs_plus":float(np.sum(np.where(rets>0,rets*rets,0.0))),
            "rs_minus":float(np.sum(np.where(rets<0,rets*rets,0.0))),
            "rets":rets,
        }
    return out


def audit_year(raw,spine,year):
    ref={r["date"]:r for r in spine if r["date"].startswith(f"{year}-")}
    rr={d:v for d,v in raw.items() if d.startswith(f"{year}-")}
    missing=sorted(set(ref)-set(rr)); extra=sorted(set(rr)-set(ref))
    common=sorted(set(ref)&set(rr))
    bad=[d for d in common if rr[d]["n_bars"]!=276 or ref[d]["n_bars"]!=276]
    max_close=max((abs(rr[d]["close"]-ref[d]["close"]) for d in common),default=float("inf"))
    max_rv=max((abs(rr[d]["rv"]-ref[d]["rv"]) for d in common),default=float("inf"))
    max_dr=max((abs(rr[d]["dr"]-ref[d]["dr"]) for d in common),default=float("inf"))
    passed=(not missing and not extra and not bad and max_close<=1e-8 and max_rv<=1e-12 and max_dr<=1e-12)
    return {
        "passed":passed,"raw_n":len(rr),"spine_n":len(ref),"common_n":len(common),
        "missing_dates":missing[:20],"extra_dates":extra[:20],"bad_276_bar_dates":bad[:20],
        "max_abs_close_diff":max_close,"max_abs_rv_diff":max_rv,"max_abs_dr_diff":max_dr
    }


def generic_sqrt(sqrt_mod,daily):
    rows=[]; summary={}
    for year in (2019,2020,2021):
        yr=sqrt_mod.sqrt_rows(daily,year)
        alarms=[r for r in yr if int(r["sqrt_alarm"])==1]
        summary[str(year)]={
            "alarms":len(alarms),
            "down":sum(float(r["target_return"])<0 for r in alarms),
            "up":sum(float(r["target_return"])>0 for r in alarms),
        }
        for r in alarms:
            z=dict(r); z["evaluation_year"]=year; z["actual_up"]=int(float(r["target_return"])>0)
            rows.append(z)
    return rows,summary


def generic_router(route,base,spine):
    days=route.external_base_days(base,spine)
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    tmap={r["target_date"]:r for r in trows}
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    common=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    base_rows=[]
    for td in common:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]
        od=t["origin_date"]
        if not (od==b["origin_date"]==ar["origin_date"]==rm["origin_date"]):
            raise RuntimeError(f"ROUTER_ORIGIN_MISMATCH:{td}")
        vals=[int(t["actual_up"]),int(b["actual_up"]),int(ar["actual_up"]),int(rm["actual_up"])]
        if len(set(vals))!=1: raise RuntimeError(f"ROUTER_LABEL_MISMATCH:{td}")
        base_rows.append({
            "origin_date":od,"target_date":td,"actual_up":vals[0],
            "TTSM_S2":int(t["ttsm_s2_signal"]==1),
            "TTSM_S1":int(t["ttsm_s1_signal"]==1),
            "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),
            "AR1_RM_LOGIT":int(ar["up"]),
            "RM_LOGIT":int(rm["up"]),
            **contexts[od],
        })
    by_year={}
    for r in base_rows: by_year.setdefault(int(r["target_date"][:4]),[]).append(r)

    def score_year(eval_rows,history):
        hist=[dict(r) for r in history]; scored=[]
        for base_row in eval_rows:
            row=dict(base_row); eligible=[]
            for expert in base.DIRECT_UP_EXPERTS:
                if row[expert]!=1: continue
                st=base.router_stats(hist,expert,row["legacy_bucket"])
                if st is None or st["n_up"]<30 or st["precision"]<=0.50 or st["fpr"]>=0.50: continue
                eligible.append((expert,st))
            if eligible:
                eligible.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
                row["router_up"]=1; row["selected_expert"]=eligible[0][0]
            else:
                row["router_up"]=0; row["selected_expert"]=""
            scored.append(row); hist.append(dict(base_row))
        return scored

    scored=[]
    for y in (2019,2020,2021):
        scored += score_year(by_year.get(y,[]),by_year.get(y-1,[]))
    summary={}
    for y in (2019,2020,2021):
        rr=[r for r in scored if int(r["target_date"][:4])==y]
        up=[r for r in rr if r["router_up"]==1]
        summary[str(y)]={"n":len(rr),"router_up":len(up),"tp":sum(r["actual_up"]==1 for r in up),"fp":sum(r["actual_up"]==0 for r in up)}
    return scored,summary


def route_cases(sqrt_rows,router_rows):
    rmap={(r["origin_date"],r["target_date"]):r for r in router_rows}
    residual=[]; summary={}
    for y in (2019,2020,2021):
        alarms=[r for r in sqrt_rows if r["evaluation_year"]==y]
        overlap=[]; abst=[]
        for s in alarms:
            rr=rmap.get((s["origin_date"],s["target_date"]))
            if rr is None: raise RuntimeError(f"ROUTER_NOT_FOUND:{s['origin_date']}->{s['target_date']}")
            if rr["actual_up"]!=s["actual_up"]: raise RuntimeError(f"SIGN_MISMATCH:{s['target_date']}")
            z=dict(s); z["router_up"]=rr["router_up"]; z["selected_expert"]=rr["selected_expert"]
            if rr["router_up"]==1: overlap.append(z)
            else: abst.append(z); residual.append(z)
        summary[str(y)]={
            "sqrt_alarms":len(alarms),"router_up_overlap":len(overlap),
            "overlap_actual_up":sum(r["actual_up"]==1 for r in overlap),
            "overlap_actual_down":sum(r["actual_up"]==0 for r in overlap),
            "router_abstain":len(abst),
            "abstain_actual_up":sum(r["actual_up"]==1 for r in abst),
            "abstain_actual_down":sum(r["actual_up"]==0 for r in abst),
        }
    return residual,summary


def nested_cal(up2,rows,upto):
    cal=[]
    for j in range(MIN_HISTORY,upto):
        prior=rows[:j]
        if len({r["actual_up"] for r in prior})<2: continue
        model,mu,sd=up2.standardize_fit(prior)
        p=float(up2.predict_rows(model,mu,sd,[rows[j]])[0])
        cal.append((rows[j]["actual_up"],p))
    down=[p for y,p in cal if y==0]
    if len(down)<MIN_DOWN_CAL: return None,len(cal),len(down)
    return max(0.50,float(up2.nearest_rank(down,.80))),len(cal),len(down)


def group(actual,call):
    if actual==1 and call==1:return "CAPTURED_UP"
    if actual==1 and call==0:return "MISSED_UP"
    if actual==0 and call==1:return "FALSE_UP_ACTUAL_DOWN"
    return "REJECTED_DOWN"


def cliffs(a,b):
    if not a or not b:return None
    gt=lt=0
    for x in a:
        for y in b:
            if x>y:gt+=1
            elif x<y:lt+=1
    return (gt-lt)/(len(a)*len(b))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--up2-module",type=Path,required=True)
    ap.add_argument("--mechanism-module",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",a.route_module)
    base=load_mod("base_authority",a.base_module)
    up2=load_mod("up2_authority",a.up2_module)
    mech=load_mod("mech_authority",a.mechanism_module)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_code)

    spine=route.load_external_spine(a.external_spine)
    raw=build_raw_2019_2021(a.raw_root)
    audits={str(y):audit_year(raw,spine,y) for y in (2019,2020,2021)}
    if not all(v["passed"] for v in audits.values()):
        raise RuntimeError(f"RAW_AUDIT_FAIL:{audits}")

    daily=route.load_external_daily_for_sqrt(spine)
    sqrt_rows,sqrt_summary=generic_sqrt(sqrt_mod,daily)
    router_rows,router_summary=generic_router(route,base,spine)
    residual,route_summary=route_cases(sqrt_rows,router_rows)

    # Binding backward compatibility for 2020-2021.
    if route_summary["2020"]["router_abstain"]!=72 or route_summary["2020"]["abstain_actual_up"]!=35 or route_summary["2020"]["abstain_actual_down"]!=37:
        raise RuntimeError(f"ROUTE2020_DRIFT:{route_summary['2020']}")
    if route_summary["2021"]["router_abstain"]!=26 or route_summary["2021"]["abstain_actual_up"]!=11 or route_summary["2021"]["abstain_actual_down"]!=15:
        raise RuntimeError(f"ROUTE2021_DRIFT:{route_summary['2021']}")

    router_map={(r["origin_date"],r["target_date"]):r for r in router_rows}
    sqrt_map={(r["origin_date"],r["target_date"]):r for r in sqrt_rows}
    lag=up2.lag_map_from_spine(spine)
    cases=[]
    for r in residual:
        key=(r["origin_date"],r["target_date"])
        if r["origin_date"] not in raw:
            raise RuntimeError(f"RAW_PATH_MISSING:{key}")
        rr=router_map[key]; sr=sqrt_map[key]
        z=up2.enrich_case(r,sr["sqrt_normalized_risk_score"],rr,lag[r["origin_date"]],raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN")
        z.update(mech.features(raw[r["origin_date"]]["rets"]))
        cases.append(z)
    cases=sorted(cases,key=lambda r:r["target_date"])

    ledger=[]
    for i,row in enumerate(cases):
        z={"index":i,"evaluation_year":row["evaluation_year"],"origin_date":row["origin_date"],"target_date":row["target_date"],"actual_up":row["actual_up"]}
        if i<MIN_HISTORY:
            z["status"]="NOT_SCORABLE_PREQUENTIAL_SUPPORT"; ledger.append(z); continue
        tau,cal_n,down_n=nested_cal(up2,cases,i)
        if tau is None:
            z.update({"status":"NOT_SCORABLE_PREQUENTIAL_SUPPORT","calibration_n":cal_n,"down_calibration_n":down_n}); ledger.append(z); continue
        model,mu,sd=up2.standardize_fit(cases[:i])
        p=float(up2.predict_rows(model,mu,sd,[row])[0]); call=int(p>tau)
        z.update({"status":"SCORABLE","calibration_n":cal_n,"down_calibration_n":down_n,"tau":tau,"p_up":p,"up2_call":call,"group":group(row["actual_up"],call)})
        for f in mech.FEATURES:z[f]=row[f]
        ledger.append(z)

    scored=[r for r in ledger if r["status"]=="SCORABLE"]
    calls=[r for r in scored if r["up2_call"]==1]
    cap=[r for r in scored if r.get("group")=="CAPTURED_UP"]
    false=[r for r in scored if r.get("group")=="FALSE_UP_ACTUAL_DOWN"]
    groups={g:sum(r.get("group")==g for r in scored) for g in ("CAPTURED_UP","MISSED_UP","FALSE_UP_ACTUAL_DOWN","REJECTED_DOWN")}
    support=len(calls)>=5 and len(false)>=2

    result={
        "identity":IDENTITY,"date":"2026-09-23",
        "status":"ERROR_POOL_2019_2021_SUPPORTIVE" if support else "ERROR_POOL_2019_2021_INSUFFICIENT",
        "integrity_errors":[],
        "raw_reconstruction":audits,
        "sqrt_summary":sqrt_summary,
        "router_summary":router_summary,
        "route_summary":route_summary,
        "combined_residual_n":len(cases),
        "combined_residual_by_year":{str(y):sum(r["evaluation_year"]==y for r in cases) for y in (2019,2020,2021)},
        "scorable_n":len(scored),
        "first_scorable_target_date":scored[0]["target_date"] if scored else None,
        "last_scorable_target_date":scored[-1]["target_date"] if scored else None,
        "calls":len(calls),
        "error_cells":groups,
        "precision":sum(r["actual_up"]==1 for r in calls)/len(calls) if calls else None,
        "mechanism_check_last_hour_trend_r2":{
            "captured_median":float(np.median([r["last_hour_trend_r2"] for r in cap])) if cap else None,
            "false_median":float(np.median([r["last_hour_trend_r2"] for r in false])) if false else None,
            "cliffs_delta":cliffs([r["last_hour_trend_r2"] for r in cap],[r["last_hour_trend_r2"] for r in false]),
        },
        "future_veto_sample_gate_passed":support,
        "governance":{"strictly_prequential":True,"2025_used":False,"2026_used":False,"veto_fitted":False}
    }
    (a.out/"GOLD_CONTROL_UP2_STRICT_PREQUENTIAL_ERROR_POOL_2019_2021_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    import csv
    fields=["index","evaluation_year","origin_date","target_date","actual_up","status","calibration_n","down_calibration_n","tau","p_up","up2_call","group",*mech.FEATURES]
    with (a.out/"GOLD_CONTROL_UP2_STRICT_PREQUENTIAL_ERROR_POOL_2019_2021_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in ledger:w.writerow({k:r.get(k,"") for k in fields})

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
