from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
from collections import defaultdict

import numpy as np
import psycopg
from sklearn.neural_network import MLPRegressor

import vw_midas_ann_meta_batch_2_v1 as ann2
import vw_midas_ann_meta_batch_5_v1 as ann5
import vw_midas_ann_meta_batch_8_v1 as ann8
import vw_midas_ann_stage3_batch31_v1 as ann31
import vw_midas_ann_stage3_batch32_v1 as ann32
import vw_midas_ann_stage3_batch34_v1 as ann34
import vw_midas_elmfis_meta_batch_5_v1 as ef5
import vw_midas_elm_meta_batch_21_25_v1 as elm2125

SERIES={
    "Gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
METALS=("Gold","Silver","Platinum","Palladium")
TRAIN_ROWS=504
EWMA_DAYS=20
TEST_START="2026-01-01"
TEST_END="2026-12-31"
FREEZE_TAG="DAILY_H1_FREEZE_2025_12_31"

def load_daily(dsn):
    raw={m:{} for m in METALS}
    lineage={}
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            for m,sid in SERIES.items():
                cur.execute("""
                    SELECT observation_ts::date,value,source,source_symbol,quality_status
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts
                """,(sid,))
                rows=cur.fetchall()
                if not rows: raise RuntimeError(f"NO_ROWS {sid}")
                for d,v,source,symbol,q in rows:
                    raw[m][d.isoformat()]=float(v)
                lineage[m]={
                    "series_id":sid,"n":len(rows),"first":rows[0][0].date().isoformat(),
                    "last":rows[-1][0].date().isoformat(),"source":rows[-1][2],
                    "source_symbol":rows[-1][3],"quality_status":rows[-1][4]
                }
    dates=sorted(set.intersection(*(set(raw[m]) for m in METALS)))
    return raw,dates,lineage

def make_samples(raw,dates):
    vals={m:np.array([raw[m][d] for d in dates],float) for m in METALS}
    logs={m:np.log(vals[m]) for m in METALS}
    rets={m:np.diff(logs[m]) for m in METALS}
    samples=[]
    alpha=2.0/(EWMA_DAYS+1.0)
    weights=np.array([(1-alpha)**k for k in range(EWMA_DAYS-1,-1,-1)],float)
    weights/=weights.sum()

    # origin index i, target i+1
    for i in range(EWMA_DAYS,len(dates)-1):
        origin=dates[i]; target=dates[i+1]
        x=[]; y=[]
        for m in METALS:
            r=rets[m]  # r[j] = log P[j+1]/P[j]
            one=float(r[i-1])
            hist=r[i-EWMA_DAYS:i]
            ew=float(weights@hist)
            x.extend([one,ew])
            y.append(float(logs[m][i+1]-logs[m][i]))
        samples.append({
            "origin":origin,"target":target,
            "x":np.asarray(x,float),"y":np.asarray(y,float),
            "origin_gold":float(vals["Gold"][i]),"actual_gold":float(vals["Gold"][i+1])
        })
    return samples

def training_and_test(samples):
    pre=[s for s in samples if s["target"]<="2025-12-31"]
    if len(pre)<TRAIN_ROWS: raise RuntimeError(f"PRE2026_TOO_SHORT {len(pre)}")
    train=pre[-TRAIN_ROWS:]
    test=[s for s in samples if TEST_START<=s["target"]<=TEST_END]
    if not test: raise RuntimeError("NO_2026_TEST_ROWS")
    X=np.stack([s["x"] for s in train]); Y=np.stack([s["y"] for s in train])
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    Xs=(X-xm)/xs; Ys=(Y-ym)/ys
    Xt=np.stack([s["x"] for s in test]); Xts=(Xt-xm)/xs
    split=len(Xs)-max(6,int(round(.2*len(Xs))))
    return train,test,Xs,Ys,Xts,ym,ys,split

def train_predict(component,X,Y,Xtest,split):
    meta={}
    if component=="VANILLA":
        m=MLPRegressor(hidden_layer_sizes=(4,),activation="tanh",solver="lbfgs",
                       alpha=1.0,max_iter=2000,tol=1e-7,random_state=1701)
        m.fit(X,Y)
        return m.predict(Xtest),{"iterations":int(m.n_iter_)}

    if component=="MPA":
        th,val,full,rep,reps=ann2.select_and_refit("MPA",X,Y,split,FREEZE_TAG)
        return ann2.common.ann_predict(th,Xtest),{"validation":val,"full":full,"repeat":rep}

    if component=="SCA":
        th,val,full,rep,reps=ann5.select_and_refit("SCA",X,Y,split,FREEZE_TAG)
        return ann5.common.ann_predict(th,Xtest),{"validation":val,"full":full,"repeat":rep}

    if component=="DE_ABC":
        th,val,full,rep,reps=ann8.select_and_refit("DE_ABC",X,Y,split,FREEZE_TAG)
        return ann8.common.ann_predict(th,Xtest),{"validation":val,"full":full,"repeat":rep}

    if component=="ADAPTIVE_TLBO":
        th,val,full,h,wd,p,rep,outer,trials,reps=ann31.adaptive_tlbo_select(X,Y,FREEZE_TAG)
        return ann31.predict_std(th,Xtest,h),{"validation":val,"full":full,"hidden":h,"weight_decay":wd,"repeat":rep,"outer":outer}

    if component=="TLBO_TUNED_PSO":
        th,meta,h=ann32.select_and_refit(X,Y,FREEZE_TAG,"TLBO")
        return ann32.predict_std(th,Xtest,h),{"hidden":h,**meta}

    if component=="MPA_SCA":
        th,val,full,rep,reps,ss,rs=ann34.select_refit(X,Y,split,FREEZE_TAG,"MPA_SCA")
        return ann34.common.ann_predict(th,Xtest),{"validation":val,"full":full,"repeat":rep}

    if component=="SMA_ELMFIS":
        th,val,full,rep,reps=ef5.select_and_refit("SMA",X,Y,split,FREEZE_TAG)
        pred=ef5.common.predict_with_fit(th,X,Y,Xtest)
        return pred,{"validation":val,"full":full,"repeat":rep}

    if component=="AOA_ELM":
        th,fit=elm2125.aoa(X,Y,elm2125.SEEDS["AOA"]+sum(map(ord,FREEZE_TAG)))
        W,b=elm2125.decode(th); beta=elm2125.fit_beta(X,Y,W,b)
        pred=elm2125.act(Xtest@W+b)@beta
        return pred,{"inner_fitness":fit}

    raise ValueError(component)

def metrics(rows):
    a=np.array([r["actual"] for r in rows],float)
    f=np.array([r["forecast"] for r in rows],float)
    o=np.array([r["origin_price"] for r in rows],float)
    ae=np.abs(f-a)
    return {
        "n":len(rows),
        "mae":float(ae.mean()),
        "mape_pct":float(np.mean(ae/a)*100),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "direction_accuracy_pct":float(np.mean(np.sign(f-o)==np.sign(a-o))*100),
        "sum_abs_error":float(ae.sum()),
        "worst_abs_error":float(ae.max()),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--component",required=True,choices=[
        "VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA","SMA_ELMFIS","AOA_ELM"
    ])
    args=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    raw,dates,lineage=load_daily(dsn)
    samples=make_samples(raw,dates)
    train,test,X,Y,Xtest,ym,ys,split=training_and_test(samples)
    pred_std,meta=train_predict(args.component,X,Y,Xtest,split)
    pred=pred_std*ys+ym

    rows=[]
    for s,p in zip(test,pred):
        forecast=float(s["origin_gold"]*math.exp(float(p[0])))
        rows.append({
            "target_date":s["target"],"origin_date":s["origin"],
            "origin_price":s["origin_gold"],"actual":s["actual_gold"],
            "forecast":forecast,"pred_log_return_gold":float(p[0]),
            "abs_error":abs(forecast-s["actual_gold"]),
            "actual_direction":"UP" if s["actual_gold"]>s["origin_gold"] else ("DOWN" if s["actual_gold"]<s["origin_gold"] else "FLAT"),
            "forecast_direction":"UP" if forecast>s["origin_gold"] else ("DOWN" if forecast<s["origin_gold"] else "FLAT"),
            "direction_correct":bool(np.sign(forecast-s["origin_gold"])==np.sign(s["actual_gold"]-s["origin_gold"]))
        })

    out={
        "experiment_id":"GOLD_DAILY_H1_TOP_FAMILY_EXPLORATORY_V1",
        "component":args.component,
        "target":"next_common_trading_day_XAU_price",
        "feature_contract":{
            "inputs":8,
            "per_metal":["latest_1d_log_return","20_trading_day_EWMA_log_return"],
            "metals":list(METALS),
            "outputs":"next-trading-day log returns of Gold/Silver/Platinum/Palladium jointly",
        },
        "freeze_contract":{
            "training_rows":TRAIN_ROWS,
            "training_last_target":train[-1]["target"],
            "all_model_parameters_frozen_before_2026":True,
            "2026_retraining":False,
            "normalization":"training-only fixed",
            "inner_validation":"chronological final 20% of frozen training window where optimizer requires validation",
        },
        "lineage":lineage,
        "test_first":test[0]["target"],"test_last":test[-1]["target"],
        "metrics":metrics(rows),"model_meta":meta,"rows":rows,
    }
    Path(f"gold_daily_h1_2026_{args.component.lower()}_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"component":args.component,"metrics":out["metrics"],"test_first":out["test_first"],"test_last":out["test_last"],"lineage":lineage},sort_keys=True))

if __name__=="__main__": main()
