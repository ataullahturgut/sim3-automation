from __future__ import annotations
import argparse, importlib.util, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def nearest_rank(vals,q):
    a=np.asarray(vals,float); k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def fit_policy(rows, cutoff_year, w=None):
    from datetime import date
    cutoff=date(cutoff_year-1,12,31)
    train=[r for r in rows if r["target_date"]<=cutoff]
    test=[r for r in rows if r["target_date"].year==cutoff_year]
    use=train if w is None else train[-w:]
    X=np.array([[1.,r["sd_d"],r["sd_w"],r["sd_m"]] for r in use],float)
    y=np.array([r["target_sd"] for r in use],float)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    Xt=np.array([[1.,r["sd_d"],r["sd_w"],r["sd_m"]] for r in test],float)
    sd=Xt@b
    if np.any(sd<=0): raise RuntimeError("NONPOSITIVE_SD")
    pred=sd*sd
    thr=nearest_rank([r["target_dr"] for r in use],.80)
    out=[]
    for r,p in zip(test,pred):
        z=dict(r); z["forecast_dr"]=float(p); z["threshold"]=thr
        z["score"]=float(p/thr); z["alert"]=int(p>=thr); out.append(z)
    return use,test,out,thr

def auc(y,s):
    y=np.asarray(y,int); s=np.asarray(s,float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if n1==0 or n0==0: return None
    order=np.argsort(s); ranks=np.empty(len(s),float)
    i=0
    while i<len(s):
        j=i
        while j+1<len(s) and s[order[j+1]]==s[order[i]]: j+=1
        avg=(i+j+2)/2.0
        for k in range(i,j+1): ranks[order[k]]=avg
        i=j+1
    return float((np.sum(ranks[y==1])-n1*(n1+1)/2)/(n1*n0))

def main():
    ap=argparse.ArgumentParser()
    for x in ["up2","route","cbr","base","sqrt-route-auth","sqrt-parent","pre-ledger","external-spine","raw-root","memory"]:
        ap.add_argument("--"+x,type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(exist_ok=True)

    up2=load("up2_auth",args.up2); route=load("route_auth",args.route)
    cbr=load("cbr_auth",args.cbr); base=load("base_auth",args.base); mem=load("mem_auth",args.memory)
    base.CUTOFF="2026-09-01T04:00:00Z"

    # Frozen UP2 training reconstruction.
    ext_spine=route.load_external_spine(args.external_spine)
    ext_raw=route.build_external_5m(args.raw_root)
    if not route.external_reconstruction_audit(ext_raw,ext_spine)["passed"]: raise RuntimeError("EXT_FAIL")
    gov_raw=cbr.load_paths(["2020-01-02","2026-08-31"]); gov_days=base.load_days()
    ext_daily=route.load_external_daily_for_sqrt(ext_spine); sqrt_mod=route.load_sqrt_mod(args.sqrt_route_auth)
    ext_sqrt,_=route.external_sqrt_cases(sqrt_mod,ext_daily); ext_router,_=route.external_router_rows(base,ext_spine)
    ext_unresolved,_=route.route_external_sqrt_cases(ext_sqrt,ext_router)
    erm={(r["origin_date"],r["target_date"]):r for r in ext_router}; esm={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    ext_lag=up2.lag_map_from_spine(ext_spine); external=[]
    for r in ext_unresolved:
        k=(r["origin_date"],r["target_date"])
        external.append(up2.enrich_case(r,esm[k]["sqrt_normalized_risk_score"],erm[k],ext_lag[r["origin_date"]],ext_raw[r["origin_date"]]["rets"],"EXT"))

    parent=up2.load_parent(args.sqrt_parent); pm={(r["origin_date"],r["target_date"]):r for r in parent}
    gr=up2.build_governed_router_rows(base,gov_days); grm={(r["origin_date"],r["target_date"]):r for r in gr}
    glag=up2.lag_map_from_base_days(gov_days)
    pre=route.load_pre_unresolved(args.pre_ledger); pre_cases=[]
    for r in pre:
        k=(r["origin_date"],r["target_date"])
        pre_cases.append(up2.enrich_case(r,pm[k]["sqrt_score"],grm[k],glag[r["origin_date"]],gov_raw[r["origin_date"]],"PRE"))
    s25=route.reconstruct_2025(base,args.sqrt_parent); stress25=[]
    for r in s25:
        k=(r["origin_date"],r["target_date"])
        stress25.append(up2.enrich_case(r,pm[k]["sqrt_score"],grm[k],glag[r["origin_date"]],gov_raw[r["origin_date"]],"S25"))
    frozen_train=external+pre_cases+stress25

    # Frozen Router V2 continued through 2026.
    tdays,bdays,ldays,daily=base.transformed(gov_days)
    trows=base.ttsm_mod.build_signal_rows(tdays); bmaps=base.bonato_maps(bdays); lmaps=base.logit_maps(ldays); contexts=base.legacy_context(daily)
    tmap={r["target_date"]:r for r in trows}; common=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    brows=[]
    for td in common:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]; od=t["origin_date"]; ctx=contexts[od]
        brows.append({"origin_date":od,"target_date":td,"actual_up":int(t["actual_up"]),
          "TTSM_S2":int(t["ttsm_s2_signal"]==1),"TTSM_S1":int(t["ttsm_s1_signal"]==1),
          "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),"AR1_RM_LOGIT":int(ar["up"]),"RM_LOGIT":int(rm["up"]),**ctx})
    by=defaultdict(list)
    for r in brows: by[int(r["target_date"][:4])].append(r)
    def score_router(eval_rows,hist):
        out=[]; hist=[dict(x) for x in hist]
        for br in eval_rows:
            row=dict(br); elig=[]; audit={}
            for ex in base.DIRECT_UP_EXPERTS:
                if row[ex]!=1:
                    audit[ex]={"signal":0,"reason":"NO_UP_SIGNAL"}
                    continue
                st=base.router_stats(hist,ex,row["legacy_bucket"])
                if st is None:
                    audit[ex]={"signal":1,"reason":"NO_STATS"}
                    continue
                reason="ELIGIBLE"
                if st["n_up"]<30: reason="N_UP_LT_30"
                elif st["precision"]<=.5: reason="PRECISION_LE_0_50"
                elif st["fpr"]>=.5: reason="FPR_GE_0_50"
                audit[ex]={"signal":1,"reason":reason,**st}
                if reason!="ELIGIBLE": continue
                elig.append((ex,st))
            row["router_audit"]=audit
            if elig:
                elig.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]])); ex,st=elig[0]
                row["router_up"]=1; row["selected_expert"]=ex
            else: row["router_up"]=0; row["selected_expert"]=""
            out.append(row); hist.append(dict(br))
        return out,hist
    s24,h24=score_router(by[2024],by[2023]); s25r,h25=score_router(by[2025],h24); s26,_=score_router(by[2026],h25)
    def router_year_summary(rows):
        ups=[r for r in rows if r["router_up"]==1]
        return {"n":len(rows),"router_up":len(ups),"tp":sum(r["actual_up"]==1 for r in ups),
                "fp":sum(r["actual_up"]==0 for r in ups),
                "selected":{ex:sum(r["selected_expert"]==ex for r in rows) for ex in base.DIRECT_UP_EXPERTS}}
    authority_reproduction={"2024":router_year_summary(s24),"2025":router_year_summary(s25r)}
    if authority_reproduction["2024"]["router_up"]!=42 or authority_reproduction["2024"]["tp"]!=26 or authority_reproduction["2024"]["fp"]!=16:
        raise RuntimeError("ROUTER_2024_AUTHORITY_MISMATCH:"+json.dumps(authority_reproduction["2024"],sort_keys=True))
    if authority_reproduction["2025"]["router_up"]!=37 or authority_reproduction["2025"]["tp"]!=27 or authority_reproduction["2025"]["fp"]!=10:
        raise RuntimeError("ROUTER_2025_AUTHORITY_MISMATCH:"+json.dumps(authority_reproduction["2025"],sort_keys=True))
    router_2026=router_year_summary(s26)
    router_2026["experts"]={}
    for ex in base.DIRECT_UP_EXPERTS:
        sig=[r for r in s26 if r[ex]==1]
        reasons=defaultdict(int)
        for r in sig: reasons[r["router_audit"][ex]["reason"]]+=1
        router_2026["experts"][ex]={"raw_up_signals":len(sig),"reasons":dict(reasons)}
    rmap={(r["origin_date"],r["target_date"]):r for r in s26}

    # Two memory policies on identical 2026 panel.
    ext=mem.load_external(args.external_spine); gov=mem.load_governed(); ds,close,dr=mem.combine(ext,gov); rows=mem.build_rows(ds,close,dr)
    exp_train,test,exp,exp_thr=fit_policy(rows,2026,None)
    w_train,_,w500,w_thr=fit_policy(rows,2026,500)
    if [r["target_date"] for r in exp] != [r["target_date"] for r in w500]: raise RuntimeError("DATE_MISMATCH")
    common_event_thr=exp_thr

    def evaluate(name,pol):
        # Direction cascade only on this policy's native risk alerts; UP2 frozen, not retrained.
        residual=[]
        for s in pol:
            if not s["alert"]: continue
            key=(s["origin_date"].isoformat(),s["target_date"].isoformat())
            rr=rmap[key]
            if rr["router_up"]==0:
                case={"evaluation_year":2026,"origin_date":key[0],"target_date":key[1],"actual_up":int(s["target_close_return"]>0)}
                residual.append(up2.enrich_case(case,s["score"],rr,glag[key[0]],gov_raw[key[0]],name))
        scored,m=up2.score_year(frozen_train,residual,2026)
        um={(r["origin_date"],r["target_date"]):r for r in scored}

        ledger=[]
        for s in pol:
            od=s["origin_date"].isoformat(); td=s["target_date"].isoformat(); rr=rmap[(od,td)]
            actual_up=int(s["target_close_return"]>0); actual_common_hi=int(s["target_dr"]>=common_event_thr)
            if not s["alert"]: final="NO_HIGH_RISK"
            elif rr["router_up"]==1: final="UP"
            else:
                u=um.get((od,td)); final="UP2" if u and u["up2_call"]==1 else "UNCERTAIN"
            u=um.get((od,td))
            ledger.append({"origin_date":od,"target_date":td,"return":s["target_close_return"],"actual_up":actual_up,
              "actual_common_high":actual_common_hi,"forecast_dr":s["forecast_dr"],"native_threshold":s["threshold"],
              "risk_score":s["score"],"alert":s["alert"],"final_state":final,
              "TTSM_S2":int(rr["TTSM_S2"]),"TTSM_S1":int(rr["TTSM_S1"]),
              "BONATO_AR1_RM_QBOOST_H1":int(rr["BONATO_AR1_RM_QBOOST_H1"]),
              "AR1_RM_LOGIT":int(rr["AR1_RM_LOGIT"]),"RM_LOGIT":int(rr["RM_LOGIT"]),
              "FAST_UP":int(rr["FAST_UP"]),"SLOW_UP":int(rr["SLOW_UP"]),"MONTHLY_UP":int(rr["MONTHLY_UP"]),
              "legacy_up_count":int(rr["legacy_up_count"]),"legacy_bucket":rr["legacy_bucket"],
              "router_up":int(rr["router_up"]),"selected_expert":rr["selected_expert"],
              "up2_p":None if u is None else float(u["p_up"]),
              "up2_tau":None if u is None else float(u["tau"]),
              "up2_call":None if u is None else int(u["up2_call"])})
        y=[x["actual_common_high"] for x in ledger]; scores=[x["forecast_dr"] for x in ledger]
        alerts=[x for x in ledger if x["alert"]]; common_hi=[x for x in ledger if x["actual_common_high"]]
        tp=sum(x["alert"] and x["actual_common_high"] for x in ledger)
        fp=sum(x["alert"] and not x["actual_common_high"] for x in ledger)
        fn=sum((not x["alert"]) and x["actual_common_high"] for x in ledger)
        direction_scope=common_hi
        up_calls=[x for x in direction_scope if x["final_state"] in ("UP","UP2")]
        true_up=sum(x["actual_up"] for x in direction_scope); true_down=len(direction_scope)-true_up
        correct_up=sum(x["actual_up"] for x in up_calls); false_up=len(up_calls)-correct_up
        return {
          "native_threshold":pol[0]["threshold"],"n":len(ledger),
          "common_event_threshold":common_event_thr,"common_high_n":len(common_hi),
          "risk_alerts":len(alerts),"common_high_caught":tp,"common_high_missed":fn,
          "common_high_recall":tp/(tp+fn) if tp+fn else None,
          "common_high_precision":tp/(tp+fp) if tp+fp else None,
          "common_high_auc":auc(y,scores),
          "direction_on_common_high":{"actual_up":true_up,"actual_down":true_down,"up_or_up2_calls":len(up_calls),
            "correct_up_calls":correct_up,"false_up_calls_on_down":false_up,
            "up_precision":correct_up/len(up_calls) if up_calls else None,
            "up_recall":correct_up/true_up if true_up else None,
            "down_protection_rate":(true_down-false_up)/true_down if true_down else None,
            "uncertain_on_down":sum((not x["actual_up"]) and x["final_state"]=="UNCERTAIN" for x in direction_scope),
            "no_high_risk_on_down":sum((not x["actual_up"]) and x["final_state"]=="NO_HIGH_RISK" for x in direction_scope)},
          "up2_residual_metrics":m,
          "ledger":ledger}
    result={"identity":"GOLD_CONTROL_2026_VOLATILITY_DIRECTION_MOTOR_LEDGER_V1",
      "method":"same common realized high-risk definition; native alert thresholds; frozen Router V2 and frozen UP2 training; no retraining by 2026",
      "router_authority_reproduction":authority_reproduction,
      "router_2026_summary":router_2026,
      "EXPANDING":evaluate("EXPANDING",exp),"W500":evaluate("W500",w500),
      "governance":{"stress_only":True,"2026_selection":False,"retuning":False,"production_writes":False,"runtime_promotion":False}}
    out=args.out/"GOLD_CONTROL_2026_VOLATILITY_DIRECTION_MOTOR_LEDGER_V1_RESULT_2026-09-24.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("EXPANDING","W500")} | {
      "EXPANDING":{kk:vv for kk,vv in result["EXPANDING"].items() if kk!="ledger"},
      "W500":{kk:vv for kk,vv in result["W500"].items() if kk!="ledger"}},indent=2))

if __name__=="__main__": main()
