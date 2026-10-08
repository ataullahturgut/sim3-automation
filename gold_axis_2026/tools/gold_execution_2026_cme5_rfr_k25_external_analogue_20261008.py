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
