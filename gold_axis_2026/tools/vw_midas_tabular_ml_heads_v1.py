from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

def arrays(samples,t):
    keys=sorted(k for k in samples if k<t)
    if len(keys)<24: raise RuntimeError(f"TRAIN_TOO_SMALL {t}")
    X=np.stack([samples[k][0] for k in keys]); Y=np.stack([samples[k][1] for k in keys])
    tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return keys,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def build_model(family,params):
    if family=="EXTRATREES":
        return ExtraTreesRegressor(
            n_estimators=params["n_estimators"], max_depth=params["max_depth"],
            min_samples_leaf=params["min_samples_leaf"], max_features=params["max_features"],
            random_state=1701, n_jobs=-1
        )
    if family=="RANDOMFOREST":
        return RandomForestRegressor(
            n_estimators=params["n_estimators"], max_depth=params["max_depth"],
            min_samples_leaf=params["min_samples_leaf"], max_features=params["max_features"],
            random_state=1701, n_jobs=-1
        )
    if family=="HGB":
        base_est=HistGradientBoostingRegressor(
            learning_rate=params["learning_rate"], max_leaf_nodes=params["max_leaf_nodes"],
            l2_regularization=params["l2_regularization"], max_iter=params["max_iter"],
            random_state=1701
        )
        return MultiOutputRegressor(base_est)
    if family=="XGBOOST":
        base_est=XGBRegressor(
            n_estimators=params["n_estimators"], max_depth=params["max_depth"],
            learning_rate=params["learning_rate"], subsample=params["subsample"],
            colsample_bytree=params["colsample_bytree"], reg_lambda=params["reg_lambda"],
            objective="reg:squarederror", random_state=1701, n_jobs=2, tree_method="hist"
        )
        return MultiOutputRegressor(base_est)
    raise ValueError(family)

def predict(samples,t,family,params):
    keys,X,Y,tx,ym,ys=arrays(samples,t)
    m=build_model(family,params); m.fit(X,Y)
    pz=np.asarray(m.predict(tx))[0]
    return pz*ys+ym,len(keys)

def make_row(b,t,pred,n,family,params):
    p=base.month_shift(t,-1)
    return {"target":t,"origin":p,"family":family,"params":params,"train_rows":n,
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
            "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p])}

def eval_spec(b,cache,family,params,a,z):
    rows=[]; errs=[]
    for t in base.month_range(a,z):
        pred,n=predict(cache[t],t,family,params)
        rows.append(make_row(b,t,pred,n,family,params))
        p=base.month_shift(t,-1)
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p])
        errs.append(abs(float(pred[0])-ar))
    return float(np.mean(errs)),rows

def grids():
    g={}
    g["EXTRATREES"]=[
        {"n_estimators":300,"max_depth":d,"min_samples_leaf":leaf,"max_features":mf}
        for d in (2,3,4) for leaf in (2,4) for mf in (0.75,1.0)
    ]
    g["RANDOMFOREST"]=[
        {"n_estimators":300,"max_depth":d,"min_samples_leaf":leaf,"max_features":mf}
        for d in (2,3,4) for leaf in (2,4) for mf in (0.75,1.0)
    ]
    g["HGB"]=[
        {"learning_rate":lr,"max_leaf_nodes":leaves,"l2_regularization":l2,"max_iter":150}
        for lr in (0.03,0.08) for leaves in (3,5,7) for l2 in (1.0,5.0)
    ]
    g["XGBOOST"]=[
        {"n_estimators":n,"max_depth":d,"learning_rate":lr,"subsample":0.8,
         "colsample_bytree":0.8,"reg_lambda":reg}
        for n in (80,150) for d in (1,2,3) for lr in (0.03,0.08) for reg in (1.0,5.0)
    ]
    return g

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    selected={}; all_dev={}
    for family,specs in grids().items():
        recs=[]
        for params in specs:
            obj,rows=eval_spec(b,cache,family,params,DEV_START,DEV_END)
            recs.append({"family":family,"params":params,"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
        recs.sort(key=lambda r:(r["dev_logret_mae"],json.dumps(r["params"],sort_keys=True)))
        selected[family]=recs[0]; all_dev[family]=recs

    results={}
    for family,rec in selected.items():
        params=rec["params"]
        _,dev=eval_spec(b,cache,family,params,DEV_START,DEV_END)
        _,tr=eval_spec(b,cache,family,params,TR_START,TR_END)
        _,st=eval_spec(b,cache,family,params,ST_START,ST_END)
        results[family]={
            "selection":rec,
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st},
        }

    leaderboard=[{
        "family":f,
        "dev_mape_pct":r["dev"]["metrics"]["mape_pct"],
        "transport_2025_mape_pct":r["transport_2025"]["metrics"]["mape_pct"],
        "stress_2026_mape_pct":r["stress_2026"]["metrics"]["mape_pct"],
        "transport_2025_direction_accuracy_pct":r["transport_2025"]["metrics"]["direction_accuracy_pct"],
        "stress_2026_direction_accuracy_pct":r["stress_2026"]["metrics"]["direction_accuracy_pct"],
        "selected_params":r["selection"]["params"],
    } for f,r in results.items()]
    leaderboard.sort(key=lambda x:(x["stress_2026_mape_pct"],x["family"]))

    out={
        "model_id":"VW_MIDAS_TABULAR_ML_HEADS_V1",
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "selection_period":f"{DEV_START}..{DEV_END}","random_split":"NONE",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"
        },
        "results":results,"leaderboard":leaderboard
    }
    Path("vw_midas_tabular_ml_heads_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(leaderboard,sort_keys=True))

if __name__=="__main__": main()
