from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

EXPERTS=["TTSM_S2","TTSM_S1","BONATO_AR1_RM_QBOOST_H1","AR1_RM_LOGIT","RM_LOGIT"]
K_GRID=[30,60,90,120]
PREC_GRID=[0.50,0.55,0.60,0.65]
ACC_GRID=[0.50,0.525,0.55]
MIN_HISTORY=120

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m
    assert spec.loader is not None; spec.loader.exec_module(m); return m

def robust_scale(H,x):
    med=np.median(H,axis=0); mad=np.median(np.abs(H-med),axis=0)
    scale=1.4826*mad; std=np.std(H,axis=0)
    scale=np.where(scale>1e-12,scale,np.where(std>1e-12,std,1.0))
    return (H-med)/scale,(x-med)/scale

def metrics(rows):
    n=len(rows)
    tp=sum(r["pred_up"]==1 and r["actual_up"]==1 for r in rows)
    fp=sum(r["pred_up"]==1 and r["actual_up"]==0 for r in rows)
    tn=sum(r["pred_up"]==0 and r["actual_up"]==0 for r in rows)
    fn=sum(r["pred_up"]==0 and r["actual_up"]==1 for r in rows)
    au,ad,pu=tp+fn,tn+fp,tp+fp
    rec=tp/au if au else None; spec=tn/ad if ad else None
    return {"n":n,"actual_up":au,"actual_down":ad,"predicted_up":pu,"tp":tp,"fp":fp,"tn":tn,"fn":fn,
      "up_precision":tp/pu if pu else None,"up_recall":rec,"false_up_fpr":fp/ad if ad else None,
      "down_recall":spec,"balanced_accuracy":(rec+spec)/2 if rec is not None and spec is not None else None,
      "accuracy":(tp+tn)/n if n else None,"coverage":pu/n if n else None}

def subset(rows,ys):
    ys=set(ys); return [r for r in rows if r["year"] in ys]

def run(rows,k,acc_thr,prec_thr):
    hist=[]; scored=[]
    for r in rows:
        if len(hist)<MIN_HISTORY:
            hist.append(r); continue
        H=np.array([h["state"] for h in hist],float); x=np.array(r["state"],float)
        Z,z=robust_scale(H,x); d=np.sqrt(np.sum((Z-z)**2,axis=1))
        idx=np.argsort(d,kind="mergesort")[:min(k,len(hist))]
        neigh=[hist[int(i)] for i in idx]
        nd=np.array([d[int(i)] for i in idx],float); w=1/(nd+1e-6); w=w/np.sum(w)
        comps={}
        for ex in EXPERTS:
            corr=np.array([1.0 if int(h[ex])==int(h["actual_up"]) else 0.0 for h in neigh])
            acc=float(np.sum(w*corr))
            up_den=sum(float(w[j]) for j,h in enumerate(neigh) if h[ex]==1)
            up_num=sum(float(w[j]) for j,h in enumerate(neigh) if h[ex]==1 and h["actual_up"]==1)
            upp=float(up_num/up_den) if up_den>0 else 0.5
            comps[ex]={"acc":acc,"upp":upp,"signal":int(r[ex])}
        ranked=sorted(EXPERTS,key=lambda ex:(-comps[ex]["acc"],-comps[ex]["upp"],EXPERTS.index(ex)))
        selected=ranked[0]; c=comps[selected]
        # Direction from best local expert, but UP requires local evidence.
        if c["signal"]==1:
            pred=int(c["acc"]>=acc_thr and c["upp"]>=prec_thr)
        else:
            pred=0
        zrow=dict(r); zrow["pred_up"]=pred; zrow["selected_expert"]=selected
        zrow["selected_local_accuracy"]=c["acc"]; zrow["selected_local_up_precision"]=c["upp"]
        scored.append(zrow); hist.append(r)
    return scored

def score_router_year(base,eval_rows,history):
    out=[]; hist=[dict(r) for r in history]
    for br in eval_rows:
        row=dict(br); elig=[]
        for ex in base.DIRECT_UP_EXPERTS:
            if row[ex]!=1: continue
            st=base.router_stats(hist,ex,row["legacy_bucket"])
            if st is None or st["n_up"]<30 or st["precision"]<=.5 or st["fpr"]>=.5: continue
            elig.append((ex,st))
        if elig:
            elig.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
            row["pred_up"]=1
        else: row["pred_up"]=0
        out.append(row); hist.append(dict(br))
    return out,hist

def baseline(base,rows):
    by=defaultdict(list)
    for r in rows: by[r["year"]].append(r)
    s24,h24=score_router_year(base,by[2024],by[2023])
    s25,h25=score_router_year(base,by[2025],h24)
    s26,_=score_router_year(base,by[2026],h25)
    m24,m25,m26=metrics(s24),metrics(s25),metrics(s26)
    if (m24["predicted_up"],m24["tp"],m24["fp"])!=(42,26,16): raise RuntimeError("BASE24")
    if (m25["predicted_up"],m25["tp"],m25["fp"])!=(37,27,10): raise RuntimeError("BASE25")
    return {"2024":m24,"2025":m25,"2026":m26}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--v1",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    base=load("base_auth_v2",a.base); v1=load("local_v1_for_rows",a.v1)
    rows=v1.build_rows(base)

    grid=[]
    for k in K_GRID:
      for at in ACC_GRID:
       for pt in PREC_GRID:
        s=run(rows,k,at,pt); m=metrics(subset(s,[2022,2023]))
        grid.append({"k":k,"acc_threshold":at,"up_precision_threshold":pt,"dev_2022_2023":m})
    grid=sorted(grid,key=lambda g:(
      -(g["dev_2022_2023"]["balanced_accuracy"] or -1),
      -(g["dev_2022_2023"]["up_recall"] or -1),
      -(g["dev_2022_2023"]["up_precision"] or -1),
      g["k"],g["acc_threshold"],g["up_precision_threshold"]))
    sel=grid[0]
    full=run(rows,sel["k"],sel["acc_threshold"],sel["up_precision_threshold"])
    annual={str(y):metrics(subset(full,[y])) for y in [2022,2023,2024,2025,2026]}
    counts={}
    for y in [2024,2025,2026]:
        rr=subset(full,[y]); counts[str(y)]={ex:sum(r["selected_expert"]==ex for r in rr) for ex in EXPERTS}
    result={"identity":"GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V2_RESEARCH",
      "status":"RESEARCH_ONLY_NO_PROMOTION",
      "protocol":{
        "family":"DCS local competence with UP evidence gate",
        "state_features":["lag1_return","momentum_5d","momentum_20d","log_rv","mean_log_rv_5d","realized_skewness","downside_share","FAST_UP","SLOW_UP","MONTHLY_UP"],
        "distance":"robust-scaled Euclidean; inverse-distance kNN; prior observations only",
        "expert_selection":"highest inverse-distance weighted local accuracy",
        "up_gate":"selected expert must signal UP and satisfy local accuracy + local UP precision thresholds",
        "candidate_k":K_GRID,"candidate_acc_threshold":ACC_GRID,"candidate_up_precision_threshold":PREC_GRID,
        "selection":"2022-2023 balanced accuracy only; tie recall then precision",
        "2024_validation_untouched":True,"2025_locked_untouched":True,"2026_stress_only":True},
      "selected":sel,"top_grid":grid[:12],
      "local_competence_v2":{"2022":annual["2022"],"2023":annual["2023"],"2024_validation":annual["2024"],"2025_locked":annual["2025"],"2026_stress":annual["2026"],"selected_expert_counts":counts},
      "router_v2_baseline":baseline(base,rows),
      "governance":{"random_split":False,"future_leakage":False,"no_2025_tuning":True,"no_2026_tuning":True,"canonical_branch_modified":False,"production_writes":False,"runtime_promotion":False}}
    (a.out/"GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V2_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
