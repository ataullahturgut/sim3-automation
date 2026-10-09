"""Strict original RFR + NEW independent preorigin CME hour returns case analogue.

No HGB or legacy same-XAU imitated "extra" factors; five licensed GC, SI,
ZN, NQ, CL H1 sources. Feature as-of H1 end+15min <= 17TR. K25 historical
same-first-impulse analog predicts next-day UP versus empirical same-sign prior.
"""
from pathlib import Path
import os,sys,json,time
import numpy as np,pandas as pd,psycopg
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_pramv_frozen_rfr_price_check_20261008 as rfr
import gold_execution_2026_cme_five_hourly_private_acquisition_20261008 as dbsrc
NAME="GOLD_EXECUTION_2026_CME5_CROSSVENUE_RFR_K25_ANALOGUE_20261008"
SYM=dbsrc.SYMBOLS
FEATURES=[f"{x}_{hours}" for x in ["GC","SI","NQ","ZN","CL"] for hours in ("r1","r3")]
def cme_source():
    qc=json.loads(dbsrc.OUTPUT.read_text())
    if qc.get("status")!="DATABENTO_NATIVE_H1_SOURCE_ACQUIRED_PRIVATE_QC_PASS":
        raise RuntimeError("CME_SOURCE_NOT_ACCEPTED_NO_CROSSVENUE_SCORE")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=25) as cn:
      with cn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute(f"""SELECT ts_event,symbol,instrument_id,close
               FROM {dbsrc.TABLE} WHERE source_id=%s
               AND ts_event >= '2023-01-01' AND ts_event < '2026-10-08'
               ORDER BY symbol,ts_event""",(dbsrc.SOURCE,))
        rows=cur.fetchall()
    data=pd.DataFrame(rows,columns=["ts","symbol","id","close"])
    if data.empty or set(data.symbol)!=set(SYM):raise RuntimeError("NO_FIVE_CME_NATIVE_SOURCES")
    data.ts=pd.to_datetime(data.ts,utc=True)
    if data.duplicated(["ts","symbol"]).any():raise RuntimeError("DUPLICATE_FUTURES_BAR")
    return data

def asof_crossvenue(raw,ref):
    g=ref.copy()
    g["issue"]=pd.to_datetime(g.date,utc=True)+pd.Timedelta(hours=14)
    g["max_vendor_bar_start"]=g.issue-pd.Timedelta(minutes=75)
    for asset in ("GC","SI","NQ","ZN","CL"):
      sym=asset+".c.0"
      x=raw[raw.symbol==sym].sort_values("ts").copy()
      x["r1"]=np.log(x.close/x.close.shift(1))
      x["r3"]=np.log(x.close/x.close.shift(3))
      stable=(x.ts-x.ts.shift(1)==pd.Timedelta(hours=1))&(
          x.ts-x.ts.shift(3)==pd.Timedelta(hours=3))&(x.id==x.id.shift(3))
      x.loc[~stable,["r1","r3"]]=np.nan
      x=x.rename(columns={"ts":"source_hour_"+asset,"r1":asset+"_r1","r3":asset+"_r3"})
      cols=["source_hour_"+asset,asset+"_r1",asset+"_r3"]
      g=pd.merge_asof(g.sort_values("max_vendor_bar_start"),
           x[cols].sort_values("source_hour_"+asset),
           left_on="max_vendor_bar_start",right_on="source_hour_"+asset,
           direction="backward",tolerance=pd.Timedelta(hours=3))
      valid=g["source_hour_"+asset]+pd.Timedelta(minutes=75)<=g.issue
      g.loc[~valid,[asset+"_r1",asset+"_r3"]]=np.nan
    g=g.dropna(subset=FEATURES).copy()
    if g.duplicated("date").any():raise RuntimeError("SOURCE_ISSUE_NOT_UNIQUE")
    if len(g)<200:raise RuntimeError("FIVE_CME_PREORIGIN_FEATURE_POPULATION_SHORT")
    g["date"]=pd.to_datetime(g.date)
    g["matured"]=g.date+pd.Timedelta(days=1)
    return g.sort_values("date")

def conditional_kernel(train,current):
    fit=[]
    for rr in current.itertuples(index=False):
      tr=train[train.first_sign==rr.first_sign]
      if len(tr)<30:
        fit.append((np.nan,np.nan,len(tr)));continue
      vec=tr[FEATURES].to_numpy(float)
      mean=vec.mean(axis=0);sd=np.maximum(1e-6,vec.std(axis=0))
      query=((np.array([getattr(rr,col) for col in FEATURES])-mean)/sd)
      dist=np.sqrt(np.mean(((vec-mean)/sd-query)**2,axis=1))
      count=min(25,len(dist))
      ix=np.argpartition(dist,count-1)[:count]
      weights=np.exp(-dist[ix]/max(float(np.median(dist[ix])),1e-6))
      cls=tr.label.to_numpy(int)
      prior=float(cls.mean())
      p=float((np.dot(weights,cls[ix])+5*prior)/(weights.sum()+5))
      fit.append((p,prior,len(tr)))
    return fit

def prediction_panel(cand):
    rows=[]
    for period,te in cand[cand.year>=2023].groupby(cand.date.dt.to_period("M")):
      cutoff=period.to_timestamp() if period.year<=2024 else pd.Timestamp(f"{period.year}-01-01")
      history=cand[(cand.date<cutoff)&(cand.matured<=cutoff)]
      if len(history)<75:continue
      estimate=conditional_kernel(history,te)
      for row,(p,prior,n) in zip(te.itertuples(index=False),estimate):
        if not np.isfinite(p):continue
        rows.append({"source_test":row.source_test,"date":row.date.strftime("%Y-%m-%d"),
           "year":int(row.year),"month":str(period),"y":int(row.label),
           "signed_OVN":float(row.signed_OVN),
           "rfr_dir":int(row.first_sign),"p_up_CME5":float(p),
           "p_up_signconditional_prior":float(prior),
           "cme5_pred":int(p>=.5),"naive_conditional_pred":int(prior>=.5),
           "train_n_same_rfr_sign":n,
           "fitted_before":str(cutoff),
           "source_H1_max_available_at_origin_minus_15min":True})
    return pd.DataFrame(rows)

def eval_model(results):
    rows=[]
    for (src,yr),g in results.groupby(["source_test","year"]):
       y=g.y.to_numpy(int);p=g.p_up_CME5.to_numpy(float)
       ref=g.p_up_signconditional_prior.to_numpy(float)
       estimate=g.cme5_pred.to_numpy(int);baseline=g.rfr_dir.to_numpy(int)
       d=y==0;u=y==1
       saved=int(np.sum((estimate==y)&(baseline!=y)))
       broken=int(np.sum((estimate!=y)&(baseline==y)))
       mcnemar=float(binomtest(saved,saved+broken,.5).pvalue) if saved+broken else 1.0
       rows.append({"source_test":src,"year":int(yr),"n":len(y),
         "k25_BA":float(.5*(np.mean(estimate[d]==0)+np.mean(estimate[u]==1))) if d.any() and u.any() else None,
         "k25_DOWN_recall":float(np.mean(estimate[d]==0)) if d.any() else None,
         "k25_UP_recall":float(np.mean(estimate[u]==1)) if u.any() else None,
         "k25_accuracy":float(np.mean(estimate==y)),
         "k25_Brier":float(np.mean((p-y)**2)),
         "past_signconditional_frequency_Brier":float(np.mean((ref-y)**2)),
         "k25_Brier_gain_vs_simple_history":float(1-np.mean((p-y)**2)/np.mean((ref-y)**2)),
         "original_RFR_accuracy_same_dates":float(np.mean(baseline==y)),
         "original_RFR_BA_same_dates":float(.5*(np.mean(baseline[d]==0)+np.mean(baseline[u]==1))) if d.any() and u.any() else None,
         "k25_RFR_rescues":saved,"k25_RFR_breaks":broken,
         "net_rescues":saved-broken,"exact_McNemar_p":mcnemar,
         "prior_class_accuracy":float(np.mean(g.naive_conditional_pred.to_numpy(int)==y)),
         "wrong_large_move_ge_1pct":int(np.sum((estimate!=y)&(g.signed_OVN.abs().to_numpy(float)>=.01))),
         "bank_spread_backtest":False,"2026_untouched":False})
    return pd.DataFrame(rows)

def main():
    start=time.time()
    raw=cme_source()
    q,t,sets=rfr.sources.source_sets()
    reports=[];forecasts=[]
    for tag,px,tx in sets:
        prices=pd.concat([q,px]).sort_index()
        labels=pd.concat([t,tx],ignore_index=True)
        source_q=rfr.extract(prices,labels)
        source_q=source_q[source_q.reversal].copy()
        source_q["source_test"]=tag
        exogenous=asof_crossvenue(raw,source_q)
        pred=prediction_panel(exogenous)
        if pred.empty:raise RuntimeError("CME5_K25_NO_FORECAST_SAMPLES_"+tag)
        reports.append({"source":tag,
          "candidate_counts":source_q.groupby("year").size().to_dict(),
          "CME5_H1_all_10_features_counts":exogenous.groupby("year").size().to_dict(),
          "scored_counts":pred.groupby("year").size().to_dict()})
        forecasts.append(pred)
        print("ACTUAL_INDEPENDENT_ASSET_PIT_COHORT",reports[-1],flush=True)
    result=pd.concat(forecasts,ignore_index=True)
    outcome=eval_model(result)
    stem=str(AX/NAME)
    outcome.to_csv(stem+"_METRICS.csv",index=False)
    result.to_csv(stem+"_PRIVATE_DATED.csv",index=False)
    summary={"status":"NEW_INDEPENDENT_NATIVE_CME_FIVE_FUTURES_RFR_K25_SCORED",
      "source":"Databento GLBX.MDP3 ohlcv-1h continuous c.0 private Neon 2023-Oct7",
      "five_venue_roots":list(SYM),"features":FEATURES,
      "causality":"last complete 1h bar ends plus 15min before 17TR issue; no same-venue futures roll transition in lookback",
      "2023_2024":"asof monthly prior-matured historical case kernel",
      "2025_2026":"frozen pre-year and already-inspected retrospective",
      "forecast_object":"on RFR opposite halfhour candidates only, 17TR-next09TR normal OVN",
      "full_source_coverage":reports,
      "no_banking_bidask_PnL":True,"no_strategy_promotion":True,
      "runtime_seconds":int(time.time()-start)}
    Path(stem+"_SUMMARY.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print("CME5_ORTHOGONAL_RFR_NOVEL_SOURCE_REAL_TEST",outcome.to_string(index=False),flush=True)
    print("CME5_K25_STATUS",json.dumps(summary,default=str),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        fr=traceback.extract_tb(e.__traceback__)[-1]
        qc={"status":"CME5_K25_MODEL_BLOCKED_NO_APPROVED_SCORE",
           "error_type":type(e).__name__,"reason":str(e)[:100],
           "function":fr.name,"line":fr.lineno,"no_results_claimed":True}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(qc,indent=2)+"\n")
        print("CME5_K25_BLOCK",json.dumps(qc),flush=True)
