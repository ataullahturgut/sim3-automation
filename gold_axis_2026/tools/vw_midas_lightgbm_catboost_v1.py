from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"

def arr(samples,t):
    ks=sorted(k for k in samples if k<t)
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks]); tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0); xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def model(f,p):
    if f=="LIGHTGBM":
        return MultiOutputRegressor(LGBMRegressor(n_estimators=p["n_estimators"],learning_rate=p["learning_rate"],num_leaves=p["num_leaves"],max_depth=p["max_depth"],min_child_samples=p["min_child_samples"],reg_lambda=p["reg_lambda"],verbosity=-1,random_state=1701,n_jobs=2))
    return CatBoostRegressor(iterations=p["iterations"],depth=p["depth"],learning_rate=p["learning_rate"],l2_leaf_reg=p["l2_leaf_reg"],loss_function="MultiRMSE",verbose=False,random_seed=1701,allow_writing_files=False)

def pred(samples,t,f,p):
    ks,X,Y,tx,ym,ys=arr(samples,t); m=model(f,p); m.fit(X,Y); z=np.asarray(m.predict(tx))[0]; return z*ys+ym,len(ks)
def ev(b,cache,f,p,a,z):
    rows=[]; es=[]
    for t in base.month_range(a,z):
        ph,n=pred(cache[t],t,f,p); pm=base.month_shift(t,-1)
        rows.append({"target":t,"forecast":float(b.core_gold[pm]*math.exp(float(ph[0]))),"actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][pm]); es.append(abs(float(ph[0])-ar))
    return float(np.mean(es)),rows

def grids():
    return {
      "LIGHTGBM":[{"n_estimators":n,"learning_rate":lr,"num_leaves":leaves,"max_depth":depth,"min_child_samples":10,"reg_lambda":reg}
                  for n in (80,150) for lr in (0.03,0.08) for leaves,depth in ((3,2),(7,3)) for reg in (1.0,5.0)],
      "CATBOOST":[{"iterations":n,"depth":d,"learning_rate":lr,"l2_leaf_reg":reg}
                  for n in (100,200) for d in (2,3) for lr in (0.03,0.08) for reg in (3.0,10.0)]
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL");
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn); cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    results={}
    for f,specs in grids().items():
        cand=[]
        for p in specs:
            obj,rows=ev(b,cache,f,p,DEV_START,DEV_END); cand.append({"params":p,"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
        cand.sort(key=lambda x:(x["dev_logret_mae"],json.dumps(x["params"],sort_keys=True))); best=cand[0]["params"]
        _,dev=ev(b,cache,f,best,DEV_START,DEV_END); _,tr=ev(b,cache,f,best,TR_START,TR_END); _,st=ev(b,cache,f,best,ST_START,ST_END)
        results[f]={"selection":cand[0],"dev":base.metrics(dev),"transport_2025":base.metrics(tr),"stress_2026":base.metrics(st)}
    out={"model_id":"VW_MIDAS_LIGHTGBM_CATBOOST_V1","authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","selection_period":f"{DEV_START}..{DEV_END}","random_split":"NONE","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},"results":results}
    Path("vw_midas_lightgbm_catboost_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(results,sort_keys=True))
if __name__=="__main__": main()
