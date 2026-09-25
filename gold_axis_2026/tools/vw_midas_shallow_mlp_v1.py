from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
from sklearn.neural_network import MLPRegressor
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks])
    tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def fit_predict(samples,t,spec):
    hidden,alpha,activation=spec
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    m=MLPRegressor(hidden_layer_sizes=hidden,activation=activation,solver="lbfgs",
                   alpha=alpha,max_iter=2000,tol=1e-7,random_state=1701)
    m.fit(X,Y)
    p=m.predict(tx)[0]*ys+ym
    return p,len(ks),int(m.n_iter_)

def ev(b,cache,spec,a,z):
    rs=[]; es=[]
    for t in base.month_range(a,z):
        p,n,it=fit_predict(cache[t],t,spec)
        pm=base.month_shift(t,-1)
        rs.append({"target":t,"origin":pm,"spec":[list(spec[0]),spec[1],spec[2]],"train_rows":n,"iterations":it,
                   "pred_log_return_gold":float(p[0]),"forecast":float(b.core_gold[pm]*math.exp(float(p[0]))),
                   "actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][pm]); es.append(abs(float(p[0])-ar))
    return float(np.mean(es)),rs

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    specs=[(h,a,act) for h in ((4,),(8,),(4,4)) for a in (0.01,0.1,1.0) for act in ("tanh","relu")]
    cand=[]; saved={}
    for s in specs:
        obj,rs=ev(b,cache,s,DEV_START,DEV_END); saved[s]=rs
        cand.append({"spec":[list(s[0]),s[1],s[2]],"dev_logret_mae":obj,"dev_metrics":base.metrics(rs)})
    cand.sort(key=lambda x:(x["dev_logret_mae"],str(x["spec"])))
    sb=cand[0]["spec"]; best=(tuple(sb[0]),float(sb[1]),sb[2]); dev=saved[best]
    _,tr=ev(b,cache,best,TR_START,TR_END); _,st=ev(b,cache,best,ST_START,ST_END)
    out={"model_id":"VW_MIDAS_SHALLOW_MULTI_OUTPUT_MLP_V1",
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "selection_period":f"{DEV_START}..{DEV_END}","random_validation":"NONE",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "candidates":cand,"selected_spec":sb,
         "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_shallow_mlp_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selected_spec":sb,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__":main()
