from __future__ import annotations
import argparse, csv, importlib.util, json, math, sys
from collections import defaultdict
from datetime import date
from pathlib import Path
import numpy as np

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2",type=Path,required=True)
    ap.add_argument("--route",type=Path,required=True)
    ap.add_argument("--cbr",type=Path,required=True)
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--sqrt-auth",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--pre-ledger",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(exist_ok=True)

    up2=load("up2_auth",args.up2)
    route=load("route_auth",args.route)
    cbr=load("cbr_auth",args.cbr)
    base=load("base_auth",args.base)
    sqrt=load("sqrt_auth",args.sqrt_auth)

    # Descriptive extension only.
    base.CUTOFF="2026-09-01T04:00:00Z"

    # ---- Rebuild frozen historical UP2 training cases exactly ----
    ext_spine=route.load_external_spine(args.external_spine)
    ext_raw=route.build_external_5m(args.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]: raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    gov_raw=cbr.load_paths(["2020-01-02","2026-08-31"])
    gov_days=base.load_days()

    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    sqrt_mod=route.load_sqrt_mod(args.sqrt_auth)
    ext_sqrt,ext_sqrt_summary=route.external_sqrt_cases(sqrt_mod,ext_daily)
    ext_router,ext_router_summary=route.external_router_rows(base,ext_spine)
    ext_unresolved,ext_route_summary=route.route_external_sqrt_cases(ext_sqrt,ext_router)
    ext_router_map={(r["origin_date"],r["target_date"]):r for r in ext_router}
    ext_sqrt_map={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    ext_lag=up2.lag_map_from_spine(ext_spine)
    external_cases=[]
    for r in ext_unresolved:
        key=(r["origin_date"],r["target_date"])
        rr=ext_router_map[key]; sr=ext_sqrt_map[key]
        external_cases.append(up2.enrich_case(
          r,sr["sqrt_normalized_risk_score"],rr,ext_lag[r["origin_date"]],
          ext_raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"))

    parent=up2.load_parent(args.sqrt_parent)
    parent_map={(r["origin_date"],r["target_date"]):r for r in parent}
    gov_router=up2.build_governed_router_rows(base,gov_days)
    gov_router_map={(r["origin_date"],r["target_date"]):r for r in gov_router}
    gov_lag=up2.lag_map_from_base_days(gov_days)

    pre=route.load_pre_unresolved(args.pre_ledger)
    pre_cases=[]
    for r in pre:
        key=(r["origin_date"],r["target_date"])
        pr=parent_map[key]; rr=gov_router_map[key]
        pre_cases.append(up2.enrich_case(
          r,pr["sqrt_score"],rr,gov_lag[r["origin_date"]],
          gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"))

    stress25=route.reconstruct_2025(base,args.sqrt_parent)
    stress25_cases=[]
    for r in stress25:
        key=(r["origin_date"],r["target_date"])
        pr=parent_map[key]; rr=gov_router_map[key]
        stress25_cases.append(up2.enrich_case(
          r,pr["sqrt_score"],rr,gov_lag[r["origin_date"]],
          gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"))

    # ---- Canonical SQRT 2026 ----
    ds,close,dr=sqrt.load_days(); srows=sqrt.build_rows(ds,close,dr)
    y26,saug=sqrt.yearly_fit_eval(srows,2026)
    smap={(r["origin_date"],r["target_date"]):r for r in saug}

    # ---- Frozen Router V2 continued causally through 2026 ----
    tdays,bdays,ldays,daily=base.transformed(gov_days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays); lmaps=base.logit_maps(ldays); contexts=base.legacy_context(daily)
    tmap={r["target_date"]:r for r in trows}
    common=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    brows=[]
    for td in common:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]; od=t["origin_date"]
        ctx=contexts[od]
        brows.append({"origin_date":od,"target_date":td,"actual_up":int(t["actual_up"]),
          "TTSM_S2":int(t["ttsm_s2_signal"]==1),"TTSM_S1":int(t["ttsm_s1_signal"]==1),
          "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),"AR1_RM_LOGIT":int(ar["up"]),"RM_LOGIT":int(rm["up"]),**ctx})
    by=defaultdict(list)
    for r in brows: by[int(r["target_date"][:4])].append(r)

    def score_year(eval_rows,history):
        out=[]; hist=[dict(r) for r in history]
        for br in eval_rows:
            row=dict(br); elig=[]
            for expert in base.DIRECT_UP_EXPERTS:
                if row[expert]!=1: continue
                st=base.router_stats(hist,expert,row["legacy_bucket"])
                if st is None or st["n_up"]<30 or st["precision"]<=.50 or st["fpr"]>=.50: continue
                elig.append((expert,st))
            if elig:
                elig.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
                ex,st=elig[0]; row.update({"router_up":1,"selected_expert":ex})
            else: row.update({"router_up":0,"selected_expert":""})
            out.append(row); hist.append(dict(br))
        return out,hist

    s24,h24=score_year(by[2024],by[2023]); s25,h25=score_year(by[2025],h24); s26,_=score_year(by[2026],h25)
    rmap={(r["origin_date"],r["target_date"]):r for r in s26}

    # ---- 2026 residual route and UP2 ----
    residual26=[]
    for s in saug:
        if int(s["sqrt_high_risk_alert"])!=1: continue
        rr=rmap[(s["origin_date"],s["target_date"])]
        if int(rr["router_up"])!=0: continue
        r={"evaluation_year":2026,"origin_date":s["origin_date"],"target_date":s["target_date"],
           "actual_up":int(float(s["target_close_return"])>0)}
        residual26.append(up2.enrich_case(
          r,float(s["sqrt_normalized_risk_score"]),rr,gov_lag[s["origin_date"]],
          gov_raw[s["origin_date"]],"GOVERNED_2026_STRESS_ROUTER_ABSTAIN"))

    train=external_cases+pre_cases+stress25_cases
    scored26,m26=up2.score_year(train,residual26,2026)
    scmap={(r["origin_date"],r["target_date"]):r for r in scored26}

    march=[]
    for s in saug:
        if not s["target_date"].startswith("2026-03"): continue
        rr=rmap[(s["origin_date"],s["target_date"])]
        if int(s["sqrt_high_risk_alert"])!=1:
            final="NO_HIGH_RISK"
        elif rr["router_up"]==1:
            final="UP"
        else:
            u=scmap.get((s["origin_date"],s["target_date"]))
            if u is None: final="ABSTAIN"
            else: final="UP2" if u["up2_call"]==1 else "UNCERTAIN"
        u=scmap.get((s["origin_date"],s["target_date"]))
        march.append({
          "origin_date":s["origin_date"],"target_date":s["target_date"],
          "return":s["target_close_return"],"actual":"UP" if s["target_close_return"]>0 else "DOWN",
          "sqrt_score":s["sqrt_normalized_risk_score"],"sqrt_alert":s["sqrt_high_risk_alert"],
          "router_state":"UP" if rr["router_up"] else "ABSTAIN","router_expert":rr["selected_expert"],
          "up2_p":None if u is None else u["p_up"],"up2_tau":None if u is None else u["tau"],
          "up2_call":None if u is None else u["up2_call"],"final_state":final
        })

    result={"identity":"GOLD_CONTROL_2026_MARCH_FULL_CASCADE_STRESS_V1",
      "up2_2026_metrics":m26,"residual26_n":len(residual26),"march":march,
      "governance":{"stress_only":True,"retuning":False,"selection":False,"production_writes":False}}
    (args.out/"GOLD_CONTROL_2026_MARCH_FULL_CASCADE_STRESS_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
