from __future__ import annotations
import argparse, importlib.util, json, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sqrt",type=Path,required=True)
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(exist_ok=True)

    sqrt=load("sqrt_auth",args.sqrt)
    base=load("base_auth",args.base)

    # Extend the frozen research readers only for descriptive 2026 stress.
    base.CUTOFF="2026-09-01T04:00:00Z"

    ds,close,dr=sqrt.load_days()
    rows=sqrt.build_rows(ds,close,dr)
    y26,aug=sqrt.yearly_fit_eval(rows,2026)
    smap={(r["origin_date"],r["target_date"]):r for r in aug}

    days=base.load_days()
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)

    tmap={r["target_date"]:r for r in trows}
    common_dates=sorted(set(tmap)&set(bmaps["BONATO_AR1_RM_QBOOST_H1"])&set(lmaps["AR1_RM_LOGIT"])&set(lmaps["RM_LOGIT"]))
    base_rows=[]
    for td in common_dates:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]; ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]
        od=t["origin_date"]
        if not (od==b["origin_date"]==ar["origin_date"]==rm["origin_date"]): raise RuntimeError("ORIGIN_MISMATCH")
        vals=[int(t["actual_up"]),int(b["actual_up"]),int(ar["actual_up"]),int(rm["actual_up"])]
        if len(set(vals))!=1: raise RuntimeError("ACTUAL_MISMATCH")
        ctx=contexts[od]
        base_rows.append({
          "origin_date":od,"target_date":td,"actual_up":vals[0],
          "TTSM_S2":int(t["ttsm_s2_signal"]==1),
          "TTSM_S1":int(t["ttsm_s1_signal"]==1),
          "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),
          "AR1_RM_LOGIT":int(ar["up"]),"RM_LOGIT":int(rm["up"]),**ctx
        })

    by=defaultdict(list)
    for r in base_rows: by[int(r["target_date"][:4])].append(r)

    def score_year(eval_rows,history):
        scored=[]; hist=[dict(r) for r in history]
        for br in eval_rows:
            row=dict(br); elig=[]
            for expert in base.DIRECT_UP_EXPERTS:
                if row[expert]!=1: continue
                st=base.router_stats(hist,expert,row["legacy_bucket"])
                if st is None or st["n_up"]<30 or st["precision"]<=0.50 or st["fpr"]>=0.50: continue
                elig.append((expert,st))
            if elig:
                elig.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
                selected,st=elig[0]
                row.update({"router_up":1,"selected_expert":selected,"selected_lcb":st["lcb"],
                  "selected_precision":st["precision"],"selected_fpr":st["fpr"],"selected_history_n_up":st["n_up"],"selected_scope":st["scope"]})
            else:
                row.update({"router_up":0,"selected_expert":"","selected_lcb":None,"selected_precision":None,
                  "selected_fpr":None,"selected_history_n_up":None,"selected_scope":""})
            scored.append(row); hist.append(dict(br))
        return scored,hist

    s24,h24=score_year(by.get(2024,[]),by.get(2023,[]))
    s25,h25=score_year(by.get(2025,[]),h24)
    s26,h26=score_year(by.get(2026,[]),h25)

    # Reproduction guards for frozen 2024-2025 authority.
    def summary(rr):
        ups=[r for r in rr if r["router_up"]==1]
        return {"n":len(rr),"up":len(ups),"tp":sum(r["actual_up"]==1 for r in ups),"fp":sum(r["actual_up"]==0 for r in ups)}
    q24=summary(s24); q25=summary(s25)
    if q24["up"]!=42 or q24["tp"]!=26 or q24["fp"]!=16: raise RuntimeError(f"ROUTER24_REPRO_FAIL:{q24}")
    if q25["up"]!=37 or q25["tp"]!=27 or q25["fp"]!=10: raise RuntimeError(f"ROUTER25_REPRO_FAIL:{q25}")

    rmap={(r["origin_date"],r["target_date"]):r for r in s26}
    march=[]
    for s in aug:
        if not s["target_date"].startswith("2026-03"): continue
        rr=rmap.get((s["origin_date"],s["target_date"]))
        if rr is None: raise RuntimeError(f"NO_ROUTER:{s['target_date']}")
        march.append({
          "origin_date":s["origin_date"],"target_date":s["target_date"],
          "target_close_return":s["target_close_return"],
          "actual_direction":"UP" if s["target_close_return"]>0 else "DOWN",
          "sqrt_high_risk_alert":s["sqrt_high_risk_alert"],
          "sqrt_score":s["sqrt_normalized_risk_score"],
          "actual_high_risk":s["actual_high_risk"],
          "router_up":rr["router_up"],
          "router_state":"UP" if rr["router_up"] else "ABSTAIN",
          "selected_expert":rr["selected_expert"],
          "legacy_bucket":rr["legacy_bucket"],
          "legacy_up_count":rr["legacy_up_count"]
        })

    result={
      "identity":"GOLD_CONTROL_2026_MARCH_FROZEN_DIRECTION_STRESS_V1",
      "status":"SQRT_AND_PRIMARY_ROUTER_COMPLETE",
      "authority_reproduction":{"2024":q24,"2025":q25},
      "sqrt_2026_summary":y26["SQRT_HAR_DR"],
      "march":march,
      "governance":{"stress_only":True,"2026_selection":False,"retuning":False,"production_writes":False}
    }
    (args.out/"GOLD_CONTROL_2026_MARCH_FROZEN_DIRECTION_STRESS_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
