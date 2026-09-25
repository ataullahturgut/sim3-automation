from __future__ import annotations

import argparse, json, math, os, datetime as dt
from pathlib import Path
import numpy as np
import psycopg
from sklearn.neural_network import MLPRegressor

import vw_midas_msvr_successor_v1 as base
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
LOOKBACK=21
TEST_START="2026-01-01"
TEST_END="2026-12-31"
FREEZE_TAG="DAILY_H1_V2_GOVERNED_ANALOG_FREEZE_2025_12_31"

def ym(d):
    return d[:7]

def load_raw(dsn):
    raw={m:{} for m in METALS}; lineage={}
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on")
        for m,sid in SERIES.items():
          cur.execute("""SELECT observation_ts::date,value,source,source_symbol,quality_status
                         FROM observations WHERE series_id=%s ORDER BY observation_ts""",(sid,))
          rows=cur.fetchall()
          if not rows: raise RuntimeError(f"NO_ROWS {sid}")
          for d,v,*_ in rows: raw[m][d.isoformat()]=float(v)
          lineage[m]={"series_id":sid,"n":len(rows),"first":rows[0][0].isoformat(),
                      "last":rows[-1][0].isoformat(),"source":rows[-1][2],
                      "source_symbol":rows[-1][3],"quality_status":rows[-1][4]}
    dates=sorted(set.intersection(*(set(raw[m]) for m in METALS)))
    dates=[d for d in dates if dt.date.fromisoformat(d).weekday()<5]
    return raw,dates,lineage

def safe_z(bundle, origin_date):
    # Daily PIT-safe analogue of monthly governed lag:
    # for any day in month M, only prior-month vintage (M-1) is allowed;
    # inside that vintage use GPR from M-2.
    M=ym(origin_date)
    vintage_month=base.month_shift(M,-1)
    gpr_month=base.month_shift(M,-2)
    if vintage_month not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_VINTAGE_MISSING {vintage_month} for {origin_date}")
    hist=bundle.gpr_vintages[vintage_month]
    return base.gpr_norm(hist,gpr_month),vintage_month,gpr_month

def make_samples(raw,dates,bundle):
    vals={m:np.asarray([raw[m][d] for d in dates],float) for m in METALS}
    logs={m:np.log(vals[m]) for m in METALS}
    rets={m:np.diff(logs[m]) for m in METALS}
    out=[]
    for i in range(LOOKBACK,len(dates)-1):
      origin=dates[i]; target=dates[i+1]
      try:
        z,vm,gm=safe_z(bundle,origin)
      except RuntimeError:
        continue
      lam=0.1*math.exp(-10.0*float(np.clip(z,0,1)))
      age=np.arange(LOOKBACK-1,-1,-1,dtype=float)
      w=np.exp(-lam*age); w/=w.sum()
      x=[]; y=[]
      for m in METALS:
        # 21-session analogue of prior-month return.
        x1=float(logs[m][i]-logs[m][i-LOOKBACK])
        # Exact monthly exponential MIDAS weighting form, now on trailing 21 daily returns.
        hist=rets[m][i-LOOKBACK:i]
        x2=float(w@hist)
        x.extend([x1,x2])
        y.append(float(logs[m][i+1]-logs[m][i]))
      out.append({"origin":origin,"target":target,"x":np.asarray(x,float),"y":np.asarray(y,float),
                  "origin_gold":float(vals["Gold"][i]),"actual_gold":float(vals["Gold"][i+1]),
                  "gpr_z":float(z),"gpr_vintage_month":vm,"gpr_month":gm})
    return out

def split(samples):
    train=[s for s in samples if s["target"]<="2025-12-31"]
    test=[s for s in samples if TEST_START<=s["target"]<=TEST_END]
    if len(train)<500: raise RuntimeError(f"TRAIN_TOO_SHORT {len(train)}")
    if not test: raise RuntimeError("NO_TEST")
    X=np.stack([s["x"] for s in train]); Y=np.stack([s["y"] for s in train])
    Xt=np.stack([s["x"] for s in test])
    xm,xs,ymn,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    Xs=(X-xm)/xs; Ys=(Y-ymn)/ys; Xts=(Xt-xm)/xs
    inner=len(Xs)-max(30,int(round(.2*len(Xs))))
    return train,test,Xs,Ys,Xts,ymn,ys,inner

def model(component,X,Y,Xt,inner):
    if component=="VANILLA":
      m=MLPRegressor(hidden_layer_sizes=(4,),activation="tanh",solver="lbfgs",alpha=1.0,
                     max_iter=2000,tol=1e-7,random_state=1701).fit(X,Y)
      return m.predict(Xt),{"iterations":int(m.n_iter_)}
    if component=="MPA":
      th,val,full,rep,reps=ann2.select_and_refit("MPA",X,Y,inner,FREEZE_TAG)
      return ann2.common.ann_predict(th,Xt),{"validation":val,"full":full,"repeat":rep}
    if component=="SCA":
      th,val,full,rep,reps=ann5.select_and_refit("SCA",X,Y,inner,FREEZE_TAG)
      return ann5.common.ann_predict(th,Xt),{"validation":val,"full":full,"repeat":rep}
    if component=="DE_ABC":
      th,val,full,rep,reps=ann8.select_and_refit("DE_ABC",X,Y,inner,FREEZE_TAG)
      return ann8.common.ann_predict(th,Xt),{"validation":val,"full":full,"repeat":rep}
    if component=="ADAPTIVE_TLBO":
      th,val,full,h,wd,p,rep,outer,trials,reps=ann31.adaptive_tlbo_select(X,Y,FREEZE_TAG)
      return ann31.predict_std(th,Xt,h),{"validation":val,"full":full,"hidden":h,"weight_decay":wd,"repeat":rep}
    if component=="TLBO_TUNED_PSO":
      th,meta,h=ann32.select_and_refit(X,Y,FREEZE_TAG,"TLBO")
      return ann32.predict_std(th,Xt,h),{"hidden":h,**meta}
    if component=="MPA_SCA":
      th,val,full,rep,reps,ss,rs=ann34.select_refit(X,Y,inner,FREEZE_TAG,"MPA_SCA")
      return ann34.common.ann_predict(th,Xt),{"validation":val,"full":full,"repeat":rep}
    if component=="SMA_ELMFIS":
      th,val,full,rep,reps=ef5.select_and_refit("SMA",X,Y,inner,FREEZE_TAG)
      return ef5.common.predict_with_fit(th,X,Y,Xt),{"validation":val,"full":full,"repeat":rep}
    if component=="AOA_ELM":
      th,fit=elm2125.aoa(X,Y,elm2125.SEEDS["AOA"]+sum(map(ord,FREEZE_TAG)))
      W,b=elm2125.decode(th); beta=elm2125.fit_beta(X,Y,W,b)
      return elm2125.act(Xt@W+b)@beta,{"inner_fitness":fit}
    raise ValueError(component)

def metrics(rows):
    a=np.array([r["actual"] for r in rows]); f=np.array([r["forecast"] for r in rows]); o=np.array([r["origin_price"] for r in rows])
    ae=np.abs(f-a); ar=np.log(a/o); pr=np.log(f/o)
    return {"n":len(rows),"mae":float(ae.mean()),"mape_pct":float(np.mean(ae/a)*100),
            "rmse":float(np.sqrt(np.mean((f-a)**2))),"sum_abs_error":float(ae.sum()),
            "direction_accuracy_pct":float(np.mean(np.sign(f-o)==np.sign(a-o))*100),
            "actual_mean_abs_move":float(np.mean(np.abs(a-o))),
            "pred_mean_abs_move":float(np.mean(np.abs(f-o))),
            "actual_return_sd_pct":float(np.std(ar)*100),
            "pred_return_sd_pct":float(np.std(pr)*100),
            "return_corr":float(np.corrcoef(ar,pr)[0,1])}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--component",required=True)
    args=ap.parse_args()
    dsn=os.environ["NEON_DATABASE_URL"]
    bundle=base.load_data(dsn)
    raw,dates,lineage=load_raw(dsn)
    samples=make_samples(raw,dates,bundle)
    train,test,X,Y,Xt,ymn,ys,inner=split(samples)
    ps,meta=model(args.component,X,Y,Xt,inner)
    pred=ps*ys+ymn
    rows=[]
    for s,p in zip(test,pred):
      fc=float(s["origin_gold"]*math.exp(float(p[0])))
      rows.append({"target_date":s["target"],"origin_date":s["origin"],"origin_price":s["origin_gold"],
                   "actual":s["actual_gold"],"forecast":fc,"abs_error":abs(fc-s["actual_gold"]),
                   "actual_direction":"UP" if s["actual_gold"]>s["origin_gold"] else "DOWN",
                   "forecast_direction":"UP" if fc>s["origin_gold"] else "DOWN",
                   "direction_correct":bool(np.sign(fc-s["origin_gold"])==np.sign(s["actual_gold"]-s["origin_gold"])),
                   "gpr_z":s["gpr_z"],"gpr_vintage_month":s["gpr_vintage_month"],"gpr_month":s["gpr_month"]})
    out={"experiment_id":"GOLD_DAILY_H1_TOP_FAMILY_V2_GPR_MIDAS_ANALOG",
         "component":args.component,
         "status":"RETROSPECTIVE_RESEARCH_ONLY_DAILY_METALS_NOT_PIT",
         "feature_contract":{"lookback_sessions":LOOKBACK,
           "per_metal":["21-session log return","GPR-adaptive exponentially weighted trailing-21 daily return"],
           "weight_formula":"lambda=0.1*exp(-10*z); w(age)=exp(-lambda*age), normalized",
           "gpr_daily_safety":"origin month M uses only vintage M-1 and GPR month M-2",
           "outputs":"next-common-weekday log returns Gold/Silver/Platinum/Palladium jointly"},
         "freeze_contract":{"train_last_target":train[-1]["target"],"train_rows":len(train),
           "2026_used_for_training":False,"2026_used_for_model_selection":False,
           "normalization":"pre-2026 training only","random_split":"NONE",
           "model_fit":"single pre-2026 fit; unchanged through 2026 test"},
         "lineage":lineage,"test_first":test[0]["target"],"test_last":test[-1]["target"],
         "metrics":metrics(rows),"model_meta":meta,"rows":rows}
    Path(f"gold_daily_h1_v2_2026_{args.component.lower()}.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"component":args.component,"status":out["status"],"train_rows":len(train),
                      "test_first":out["test_first"],"test_last":out["test_last"],"metrics":out["metrics"]},sort_keys=True))

if __name__=="__main__": main()
