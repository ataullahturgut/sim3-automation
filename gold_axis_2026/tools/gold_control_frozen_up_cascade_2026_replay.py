from __future__ import annotations
import argparse,csv,importlib.util,json,sys
from collections import Counter,defaultdict
from pathlib import Path

IDENTITY="GOLD_CONTROL_FROZEN_UP_CASCADE_2026_REPLAY"
DIRECT=["TTSM_S2","TTSM_S1","BONATO_AR1_RM_QBOOST_H1","AR1_RM_LOGIT","RM_LOGIT"]

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("IMPORT_FAIL:"+name+":"+str(path))
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def make_base_rows(base,days):
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    tmap={r["target_date"]:r for r in trows}
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    common=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    rows=[]
    for td in common:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]
        od=t["origin_date"]
        vals=[int(t["actual_up"]),int(b["actual_up"]),int(ar["actual_up"]),int(rm["actual_up"])]
        if not (od==b["origin_date"]==ar["origin_date"]==rm["origin_date"]):
            raise RuntimeError("ORIGIN_MISMATCH:"+td)
        if len(set(vals))!=1:
            raise RuntimeError("ACTUAL_MISMATCH:"+td)
        rows.append({
            "origin_date":od,"target_date":td,"actual_up":vals[0],
            "TTSM_S2":int(t["ttsm_s2_signal"]==1),
            "TTSM_S1":int(t["ttsm_s1_signal"]==1),
            "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),
            "AR1_RM_LOGIT":int(ar["up"]),
            "RM_LOGIT":int(rm["up"]),
            **contexts[od],
        })
    return rows,daily

def score_router(base,rows):
    by=defaultdict(list)
    for r in rows:
        by[int(r["target_date"][:4])].append(r)
    hist=[dict(r) for r in by[2023]]
    out=[]
    for year in (2024,2025,2026):
        for r0 in sorted(by[year],key=lambda x:x["target_date"]):
            r=dict(r0); eligible=[]
            for e in DIRECT:
                if int(r[e])!=1:
                    continue
                st=base.router_stats(hist,e,r["legacy_bucket"])
                if st is None:
                    continue
                if st["n_up"]<30 or st["precision"]<=0.50 or st["fpr"]>=0.50:
                    continue
                eligible.append((e,st))
            if eligible:
                eligible.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
                e,st=eligible[0]
                r["router_up"]=1; r["selected_expert"]=e
            else:
                r["router_up"]=0; r["selected_expert"]=""
            out.append(r)
            hist.append(dict(r0))
    return out

def router_metrics(rows):
    calls=[r for r in rows if int(r["router_up"])==1]
    n=len(rows); tp=sum(int(r["actual_up"])==1 for r in calls); fp=len(calls)-tp
    au=sum(int(r["actual_up"])==1 for r in rows); ad=n-au
    return {
        "n":n,"actual_up":au,"actual_down":ad,
        "up_calls":len(calls),"true_up":tp,"false_up":fp,
        "precision":tp/len(calls) if calls else None,
        "call_error_rate":fp/len(calls) if calls else None,
        "false_up_fpr":fp/ad if ad else None,
        "actual_up_recall":tp/au if au else None,
        "coverage":len(calls)/n if n else None,
        "selected_counts":dict(Counter(r["selected_expert"] for r in calls)),
    }

def external_cases(route,up2,base,sqrt_mod,raw_root,spine_path):
    spine=route.load_external_spine(spine_path)
    raw=route.build_external_5m(raw_root)
    audit=route.external_reconstruction_audit(raw,spine)
    if not audit["passed"]:
        raise RuntimeError("EXTERNAL_RECON_FAIL")
    sq,sqsum=route.external_sqrt_cases(sqrt_mod,route.load_external_daily_for_sqrt(spine))
    rr,rsum=route.external_router_rows(base,spine)
    unres,usum=route.route_external_sqrt_cases(sq,rr)
    if sqsum!={"2020":{"alarms":212,"down":97,"up":115},"2021":{"alarms":28,"down":16,"up":12}}:
        raise RuntimeError("EXT_SQRT_MISMATCH")
    if rsum!={"2020":{"n":260,"router_up":185,"tp":111,"fp":74},"2021":{"n":258,"router_up":33,"tp":19,"fp":14}}:
        raise RuntimeError("EXT_ROUTER_MISMATCH")
    exp={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,"router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,"router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if usum!=exp:
        raise RuntimeError("EXT_ROUTE_MISMATCH")
    rmap={(r["origin_date"],r["target_date"]):r for r in rr}
    smap={(r["origin_date"],r["target_date"]):r for r in sq}
    lag=up2.lag_map_from_spine(spine); out=[]
    for r in unres:
        key=(r["origin_date"],r["target_date"])
        out.append(up2.enrich_case(r,smap[key]["sqrt_normalized_risk_score"],rmap[key],lag[r["origin_date"]],raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"))
    if len(out)!=98 or sum(r["actual_up"] for r in out)!=46:
        raise RuntimeError("EXTERNAL_CASE_COUNT_FAIL")
    return out,audit

def frozen_hist(path):
    rows=[]
    for r in read_csv(path):
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025):
            continue
        z={"evaluation_year":y,"origin_date":r["origin_date"],"target_date":r["target_date"],"actual_up":int(r["actual_up"]),"source":r["source"]}
        for k in ["sqrt_score","lag1_close_return","downside_share","intraday_end_norm","close_location","trough_recovery_norm","last_quarter_return_norm","direct_up_fraction","legacy_up_fraction"]:
            z[k]=float(r[k])
        rows.append(z)
    c=Counter(r["evaluation_year"] for r in rows)
    if c!={2022:11,2023:2,2024:13,2025:74}:
        raise RuntimeError("FROZEN_LEDGER_COUNT_MISMATCH:"+str(dict(c)))
    return rows

def build_residual_2026(up2,cbr,router26,sqrt26,days):
    rmap={(r["origin_date"],r["target_date"]):r for r in router26}
    lag=up2.lag_map_from_base_days(days)
    alarms=[r for r in sqrt26 if int(r["sqrt_alarm"])==1]
    tmp=[]
    for s in alarms:
        key=(s["origin_date"],s["target_date"])
        rr=rmap.get(key)
        if rr is None:
            raise RuntimeError("ROUTER_JOIN_FAIL:"+str(key))
        actual_up=int(float(s["target_return"])>0)
        if actual_up!=int(rr["actual_up"]):
            raise RuntimeError("SIGN_MISMATCH:"+str(key))
        if int(rr["router_up"])==0:
            tmp.append((s,rr,actual_up))
    raw=cbr.load_paths([s["origin_date"] for s,rr,y in tmp])
    out=[]
    for s,rr,y in tmp:
        od=s["origin_date"]
        case={"evaluation_year":2026,"origin_date":od,"target_date":s["target_date"],"actual_up":y}
        out.append(up2.enrich_case(case,float(s["sqrt_normalized_risk_score"]),rr,lag[od],raw[od],"GOVERNED_2026_ROUTER_ABSTAIN"))
    return out,alarms

def combined(router26,scored26):
    p={(r["origin_date"],r["target_date"]) for r in router26 if int(r["router_up"])==1}
    s={(r["origin_date"],r["target_date"]) for r in scored26 if int(r["up2_call"])==1}
    keys=p|s; amap={(r["origin_date"],r["target_date"]):r for r in router26}
    tp=sum(int(amap[k]["actual_up"])==1 for k in keys); fp=len(keys)-tp
    n=len(router26); au=sum(int(r["actual_up"]) for r in router26); ad=n-au
    return {
        "n":n,"up_calls":len(keys),"true_up":tp,"false_up":fp,
        "precision":tp/len(keys) if keys else None,
        "call_error_rate":fp/len(keys) if keys else None,
        "coverage":len(keys)/n if n else None,
        "actual_up_recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "primary_calls":len(p),"secondary_up2_calls":len(s),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--cbr-module",type=Path,required=True)
    ap.add_argument("--up2-module",type=Path,required=True)
    ap.add_argument("--frozen-up2-ledger",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",args.route_module)
    sqrt_mod=route.load_sqrt_mod(args.sqrt_code)
    base=load_mod("base_authority",args.base_module)
    cbr=load_mod("cbr_authority",args.cbr_module)
    up2=load_mod("up2_authority",args.up2_module)

    base.CUTOFF="2026-09-01T05:00:00Z"
    days=base.load_days()
    base_rows,daily=make_base_rows(base,days)
    router=score_router(base,base_rows)
    by={y:[r for r in router if int(r["target_date"][:4])==y] for y in (2024,2025,2026)}
    m24=router_metrics(by[2024]); m25=router_metrics(by[2025]); m26=router_metrics(by[2026])

    if (m24["up_calls"],m24["true_up"],m24["false_up"])!=(42,26,16):
        raise RuntimeError("ROUTER24_REPRO_FAIL:"+json.dumps(m24))
    if (m25["up_calls"],m25["true_up"],m25["false_up"])!=(37,27,10):
        raise RuntimeError("ROUTER25_REPRO_FAIL:"+json.dumps(m25))
    if m25["selected_counts"]!={"RM_LOGIT":37}:
        raise RuntimeError("ROUTER25_EXPERT_REPRO_FAIL:"+json.dumps(m25["selected_counts"]))

    sqrt26=sqrt_mod.sqrt_rows(daily,2026)
    res26,alarms26=build_residual_2026(up2,cbr,by[2026],sqrt26,days)
    alarm_up=sum(float(r["target_return"])>0 for r in alarms26); alarm_down=len(alarms26)-alarm_up

    ext,audit=external_cases(route,up2,base,sqrt_mod,args.raw_root,args.external_spine)
    hist=frozen_hist(args.frozen_up2_ledger)
    train=ext+hist
    scored26,mup2=up2.score_year(train,res26,2026)
    mup2["call_error_rate"]=mup2["false_up"]/mup2["up2_calls"] if mup2.get("up2_calls") else None
    mup2["residual_up_base_rate"]=sum(r["actual_up"] for r in res26)/len(res26) if res26 else None
    comb=combined(by[2026],scored26)

    old=read_csv(args.frozen_up2_ledger)
    a=[r for r in old if int(r["evaluation_year"]) in (2022,2023,2024)]
    b=[r for r in old if int(r["evaluation_year"])==2025]
    if (len(a),sum(int(r["up2_call"]) for r in a),sum(int(r["actual_up"]) and int(r["up2_call"]) for r in a))!=(26,11,8):
        raise RuntimeError("UP2_PRE2025_LEDGER_REPRO_FAIL")
    if (len(b),sum(int(r["up2_call"]) for r in b),sum(int(r["actual_up"]) and int(r["up2_call"]) for r in b))!=(74,25,13):
        raise RuntimeError("UP2_2025_LEDGER_REPRO_FAIL")

    result={
        "identity":IDENTITY,
        "status":"2026_RETROSPECTIVE_STRESS_REPLAY_COMPLETE",
        "data_last_day":str(max(d.d for d in days)),
        "primary_router":{"2024_reproduction":m24,"2025_reproduction":m25,"2026":m26},
        "sqrt_2026":{"test_rows":len(sqrt26),"high_risk_alarms":len(alarms26),"alarm_actual_up":alarm_up,"alarm_actual_down":alarm_down},
        "primary_residual_2026":{"n":len(res26),"actual_up":sum(r["actual_up"] for r in res26),"actual_down":len(res26)-sum(r["actual_up"] for r in res26)},
        "up2_2026":mup2,
        "combined_up_2026":comb,
        "external_reconstruction":audit,
        "governance":{"2026_tuning":False,"parameter_changes":False,"feature_changes":False,"runtime_promotion":False}
    }
    (args.out/"GOLD_CONTROL_FROZEN_UP_CASCADE_2026_REPLAY_RESULT_2026-10-02.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

    with (args.out/"GOLD_CONTROL_PRIMARY_UP_V2_2026_LEDGER_2026-10-02.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["origin_date","target_date","actual_up","router_up","selected_expert","legacy_bucket","legacy_up_count"]+DIRECT
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in by[2026]: w.writerow({k:r.get(k,"") for k in fields})

    with (args.out/"GOLD_CONTROL_FROZEN_UP2_2026_LEDGER_2026-10-02.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["evaluation_year","origin_date","target_date","actual_up"]+list(up2.FEATURES)+["p_up","tau","up2_call"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in scored26: w.writerow({k:r.get(k,"") for k in fields})

    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
