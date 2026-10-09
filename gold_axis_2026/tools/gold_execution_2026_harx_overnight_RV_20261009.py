"""Corsi 2009 HAR-X for actual 17TR->next09TR XAU BID realized volatility.
DAY/OVN DIRECTION IS NOT predicted here. Preorigin 4h RV, past 1/5/21
complete normal source-qualified nights; no return from current future night.
"""
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as src
NAME="GOLD_EXECUTION_2026_HARX_17TR_OVERNIGHT_RISK_20261009"
FEATURES=("log_prev1rv","log_prev5rv","log_prev21rv","log_pre4hrv")
BASE=("TRAIL21","TRAIL5","HAR_3","HAR_X")
def one_source(q,alltargets,tag):
    prev=[];rows=[]
    for r in alltargets.sort_values("date").itertuples(index=False):
        d=pd.Timestamp(r.date)
        if d.dayofweek>=4 or r.overnight_gate!="COMPLETE_SINGLE_SOURCE":continue
        start=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
        pre=q.reindex(pd.date_range(start-pd.Timedelta(hours=4),periods=16,freq="15min"))
        future=q.reindex(pd.date_range(start,periods=64,freq="15min"))
        if pre[["open","close"]].isna().any().any() or future[["open","close"]].isna().any().any():
            continue
        vals=np.r_[pre.open.to_numpy(float),pre.close.to_numpy(float),
                   future.open.to_numpy(float),future.close.to_numpy(float)]
        if not np.isfinite(vals).all() or (vals<=0).any():
            raise RuntimeError("INVALID_PRICE_NONPOSITIVE_OR_INF")
        past_rv=float(np.sqrt(np.square(np.log(pre.close/pre.open)).sum()))
        y=float(np.sqrt(np.square(np.log(future.close/future.open)).sum()))
        if y<=1e-9 or past_rv<=1e-9:continue
        if pd.isna(r.ret_OVN) or int(float(r.ret_OVN)>0)!=int(float(future.close.iloc[-1])>float(future.open.iloc[0])):
            raise RuntimeError("SOURCE_REALIZED_TARGET_DAY_ALIGNMENT")
        if len(prev)>=21 and (d-prev[-21][0]).days<=65:
            v=np.array([t[1] for t in prev[-21:]],float)
            x=[np.log(v[-1]),np.log(v[-5:].mean()),np.log(v.mean()),np.log(past_rv)]
            rows.append({"source_test":tag,"date":d,"year":d.year,"month":d.strftime("%Y-%m"),
               "rv_night":y,"rv_pre4h":past_rv,"prev5_mean_rv":float(v[-5:].mean()),
               "prev21_mean_rv":float(v.mean()),
               "prior21_span_days":int((d-prev[-21][0]).days),
               "maturity":d+pd.Timedelta(days=1),
               **dict(zip(FEATURES,x))})
        prev.append((d,y))
    out=pd.DataFrame(rows)
    if out.empty or out.date.duplicated().any():raise RuntimeError("HAR_SOURCE_COHORT_EMPTY_OR_DUPLICATE")
    return out

def forecasts(z):
    records=[];cache={}
    for mo,test in z[z.year>=2023].groupby(z.date.dt.to_period("M")):
        cut=mo.to_timestamp() if mo.year<=2024 else pd.Timestamp(f"{mo.year}-01-01")
        train=z[(z.date<cut)&(z.maturity<=cut)]
        if len(train)<100:continue
        if not(train.date<test.date.min()).all():raise RuntimeError("HAR_FIT_LEAK")
        code=str(cut)
        if code not in cache:
            models={}
            for name,cols in (("HAR_3",FEATURES[:3]),("HAR_X",FEATURES)):
                model=make_pipeline(StandardScaler(),Ridge(alpha=10.,fit_intercept=True))
                model.fit(train[list(cols)].to_numpy(float),np.log(train.rv_night.to_numpy(float)))
                models[name]=(model,cols)
            cache[code]=(models,len(train))
        models,ntrain=cache[code]
        p={
          "TRAIL21":test.prev21_mean_rv.to_numpy(float),
          "TRAIL5":test.prev5_mean_rv.to_numpy(float)}
        for name,(model,cols) in models.items():
            p[name]=np.exp(model.predict(test[list(cols)].to_numpy(float)))
        for name,val in p.items():
            for r,est in zip(test.itertuples(index=False),val):
                if not np.isfinite(est) or est<=0:raise RuntimeError("HAR_NEGATIVE_OR_INF_PRED")
                actual=float(r.rv_night)
                variance=(actual/float(est))**2
                qlike=float(variance-np.log(variance)-1.)
                records.append({"source_test":r.source_test,"date":r.date.strftime("%Y-%m-%d"),
                   "year":int(r.year),"month":r.month,"method":name,
                   "predicted_RV":float(est),"actual_RV":actual,
                   "abs_err":float(abs(est-actual)),"squared_err":float((est-actual)**2),
                   "APE":float(abs(est-actual)/actual),"QLIKE":qlike,
                   "log_abs_error":float(abs(np.log(est)-np.log(actual))),
                   "ntrain":ntrain,"cutoff":str(cut)})
    out=pd.DataFrame(records)
    if out.empty or out.duplicated(["date","method"]).any():raise RuntimeError("HAR_FORECAST_MISSING")
    return out

def evaluate(z):
    stats=[];intervals=[]
    for (source,year,method),g in z.groupby(["source_test","year","method"]):
        stats.append({"source_test":source,"year":int(year),"method":method,"n":len(g),
           "mean_RV_percent":float(g.actual_RV.mean()*100),
           "MAE_RV_pctpoint":float(g.abs_err.mean()*100),
           "RMSE_RV_pctpoint":float(np.sqrt(g.squared_err.mean())*100),
           "MAPE":float(g.APE.mean()),"median_APE":float(g.APE.median()),
           "mean_QLIKE":float(g.QLIKE.mean()),
           "mean_log_abs_error":float(g.log_abs_error.mean()),
           "predicted_RV_pct":float(g.predicted_RV.mean()*100),
           "no_overnight_direction_reported":True})
    rng=np.random.default_rng(20261009)
    for (source,year),g in z.groupby(["source_test","year"]):
        base=g[g.method=="TRAIL21"].set_index("date").sort_index()
        for method in ("HAR_X","HAR_3"):
            cand=g[g.method==method].set_index("date").sort_index()
            if not base.index.equals(cand.index):raise RuntimeError("HAR_COMPARATOR_DIFFERENT_DAYS")
            months=base.month.to_numpy()
            u=np.unique(months)
            aa=np.array([cand.loc[months==m,"abs_err"].sum() for m in u])
            bb=np.array([base.loc[months==m,"abs_err"].sum() for m in u])
            draws=rng.integers(0,len(u),(500,len(u)))
            gain=1-aa[draws].sum(axis=1)/np.maximum(1e-10,bb[draws].sum(axis=1))
            intervals.append({"source_test":source,"year":int(year),"method":method,
               "relative_MAE_RV_gain_over_previous21":float(1-cand.abs_err.mean()/base.abs_err.mean()),
               "month_block_gain_lower95":float(np.quantile(gain,.025)),
               "month_block_gain_upper95":float(np.quantile(gain,.975)),
               "inspected_2026_not_confirmatory":True})
    return pd.DataFrame(stats),pd.DataFrame(intervals)

def main():
    t0=time.monotonic()
    q,t,sources=src.source_sets()
    out=[];cohorts=[]
    for tag,p,ts in sources:
        combined=pd.concat([q,p]).sort_index()
        if combined.index.duplicated().any():raise RuntimeError("DUPLICATE_PRICE_H1")
        cases=pd.concat([t,ts],ignore_index=True)
        if cases.date.duplicated().any():raise RuntimeError("MIXED_SESSION_DATES")
        features=one_source(combined,cases,tag)
        result=forecasts(features)
        out.append(result)
        cohorts.append({"source":tag,"eligible_all_years":features.groupby("year").size().to_dict(),
           "score_sample":result.groupby(["year","method"]).size().groupby(level=0).first().to_dict()})
        print("HAR_OVERNIGHT_SOURCE_READY",cohorts[-1],flush=True)
    p=pd.concat(out,ignore_index=True)
    m,unc=evaluate(p)
    root=str(AX/NAME)
    m.to_csv(root+"_YEAR_METRICS.csv",index=False)
    unc.to_csv(root+"_MONTHBLOCK.csv",index=False)
    p.to_csv(root+"_PRIVATE_DATED.csv",index=False)
    status={"status":"HAR_CORSI_VOLATILITY_RISK_EXPERIMENT_COMPLETED",
       "model":"preorigin HAR_X 1/5/21 mature night volatility + pre17 last4h, fixed Ridge alpha10",
       "two_2026_sources_not_independent":True,"target":"17TR next09TR 64 M15 BID open-close realized RV",
       "not_direction_model":True,"target_no_weekend64":True,
       "2026_target_not_fit":True,"2026_inspected_not_blind":True,
       "bank_execution_spread_profit_not_proven":True,
       "cohorts":cohorts,"elapsed_sec":int(time.monotonic()-t0)}
    Path(root+"_SUMMARY.json").write_text(json.dumps(status,indent=2,default=str)+"\n")
    print("HAR_RISK_REAL_TEST",m.to_string(index=False),flush=True)
    print("HAR_RISK_MONTHBLOCK",unc.to_string(index=False),flush=True)
    print("HAR_RISK_QC",json.dumps(status,default=str),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        s=traceback.extract_tb(e.__traceback__)[-1]
        obj={"status":"HAR_RISK_NOT_SCORED","error_type":type(e).__name__,
             "message":str(e)[:140],"function":s.name,"line":s.lineno}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(obj,indent=2)+"\n")
        print("HAR_RISK_FAILURE",json.dumps(obj),flush=True)
