from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import tlbo_pso_core_v1 as core

DS,DE,TS,TE,SS,SE="2022-04","2024-12","2025-01","2025-12","2026-01","2026-07"

def arr(s,t):
    k=sorted(x for x in s if x<t)
    X=np.stack([s[x][0] for x in k]); Y=np.stack([s[x][1] for x in k]); q=s[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return k,(X-xm)/xs,(Y-ym)/ys,(q-xm)/xs,ym,ys

def pred(s,t):
    k,X,Y,q,ym,ys=arr(s,t); sd=50711+sum(map(ord,t))
    hp,outer=core.tlbo(X,Y,sd)
    th,inner,h,a,p=core.pso(X,Y,hp,sd+777777)
    W,b=core.dec(th,h); B=core.beta(X,Y,W,b,a)
    y=(core.sig(q@W+b)@B)[0]*ys+ym
    return y,len(k),outer,inner,h,a,p

def ev(B,C,a,z):
    R=[]
    for t in base.month_range(a,z):
        y,n,o,i,h,al,p=pred(C[t],t); pm=base.month_shift(t,-1)
        R.append({"target":t,"origin":pm,"train_rows":n,"outer_inner_score":o,"final_inner_fitness":i,
                  "selected_hidden":h,"selected_alpha":al,
                  "selected_pso":{"w":p[0],"c1":p[1],"c2":p[2],"vmax_frac":p[3]},
                  "forecast":float(B.core_gold[pm]*math.exp(float(y[0]))),
                  "actual":float(B.core_gold[t]),"rw":float(B.core_gold[pm])})
    return R

def main():
    d=os.environ["NEON_DATABASE_URL"]
    B=base.load_data(d)
    C={t:base.all_samples_at_origin(B,t,governed=True) for t in base.month_range(DS,SE)}
    d1,d2,d3=ev(B,C,DS,DE),ev(B,C,TS,TE),ev(B,C,SS,SE)
    O={"model_id":"VW_MIDAS_TLBO_TUNED_PSO_ELM_V1",
       "authority":{"database_access":"READ_ONLY","inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                    "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
       "method":{"outer_optimizer":"TLBO","tuned":["w","c1","c2","vmax_frac","hidden","alpha"],
                 "hidden_grid":core.HG,"alpha_grid":core.AG,"pso_population":core.PP,"pso_iterations":core.PI,
                 "tlbo_population":core.TP,"tlbo_iterations":core.TI},
       "dev":{"metrics":base.metrics(d1),"rows":d1},
       "transport_2025":{"metrics":base.metrics(d2),"rows":d2},
       "stress_2026":{"metrics":base.metrics(d3),"rows":d3}}
    Path("vw_midas_tlbo_tuned_pso_elm_v1_result.json").write_text(json.dumps(O,indent=2)+"\n")
    print(json.dumps({k:O[k]["metrics"] for k in ["dev","transport_2025","stress_2026"]}))
if __name__=="__main__": main()
