"""Independent *forecast-period* market fragility overlay.

Research, NOT production. 2023–2024 robust unsupervised fit -> 2025 diagnostic,
2023–2025 frozen fit -> 2026 Jan–Sep stress. No 2026 refit, no use of base
ANN predictions/errors (therefore "risk warning" NOT measured probability of
ANN error).

SOURCE TIME:
- CBOE GVZ: issue after NY 17:30, same day's option-close quote eligible.
- H.10 Broad USD: observations of the prior business week published following
  Monday at 16:15 NY; first eligible at that Monday 17:30.
- H.15 DGS10: conservative at least next observation day after actual obs.
- Four-metal daily reference spot: historic retrospective non-firstprint;
  not necessarily available as an executable close tick at 17:30. RESEARCH.
Known bad Feb27 2026 price: quarantine any origin whose features/targets
overlap the bad date; NO interpolation or silent replacement.
"""
from __future__ import annotations
import argparse,csv,json,math,hashlib,os
from datetime import date,timedelta
from pathlib import Path
from bisect import bisect_right
import numpy as np
import psycopg
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score,average_precision_score
import gold_monthly_h1_neon_source_v2 as gold

SERIES=["DTWEXBGS_FRB_H10","DGS10_FRB_H15"]
FAMILIES={
 "METAL_ONLY":list(range(0,6)),
 "METAL_GVZ":list(range(0,10)),
 "METAL_GVZ_USD_RATES":list(range(0,14)),
 "USD_RATES_ONLY":list(range(10,14)),
}
FEATURE_NAMES=["au_ret5","au_ret20","au_rsi14","au_ma20_dist","au_vol5","metals_ret5_disp",
 "gvz_level","gvz_z252","gvz_5d_logchange","gvz_1d_logchange",
 "usd_h10_ret5_published","usd_h10_lastweek_ret","dgs10_delta5_pctpt","dgs10_level"]
BAD="2026-02-27"
PANELS={"DIAGNOSTIC_2025":("2025-01-01","2025-12-31"),
        "STRESS_2026":("2026-01-01","2026-09-21")}
MODEL="ISOLATION_FOREST_200_ROBUST_LAGGED_GVZ_USD_RATES_OVERLAY"
THRESHOLDS={"YELLOW":0.90,"RED":0.95}
def require(ok,what):
 if not ok: raise RuntimeError("RISK_OVERLAY_BLOCK:"+what)
def hash_json(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def source_extract(outfile,gvzfile):
 with open(gvzfile,encoding="utf-8-sig",newline="") as h:
  rows=list(csv.DictReader(h))
 require(rows and set(rows[0])>=set(["DATE","GVZ"]),"CBOE_GVZ_SOURCE_COLUMNS")
 gvz={}
 from datetime import datetime
 for r in rows:
  if r["GVZ"] and r["GVZ"]!=".":
   d=datetime.strptime(r["DATE"],"%m/%d/%Y").date().isoformat()
   gvz[d]=float(r["GVZ"])
 require(len(gvz)>4000 and abs(gvz["2026-01-29"]-46.02)<.001,"CBOE_GVZ_DATE_AND_COVERAGE")
 require(bool(os.getenv("NEON_DATABASE_URL")),"DATABASE_SECRET_NOT_AVAILABLE")
 with psycopg.connect(os.environ["NEON_DATABASE_URL"],autocommit=True) as conn:
  with conn.cursor() as cur:
   cur.execute("SET default_transaction_read_only = on")
   cur.execute(gold.PRICE_SQL);rows=cur.fetchall()
   cur.execute(gold.MONTHLY_SQL);months=cur.fetchall()
   cur.execute("""SELECT series_id, observation_ts::date, value, provider_as_of, available_as_of
                 FROM public.observations WHERE series_id = ANY(%s)
                 AND observation_ts >= '2022-12-01' AND observation_ts < '2026-10-01'
                 ORDER BY observation_ts""",(SERIES,))
   macro_rows=cur.fetchall()
 _,_,proof=gold.normalize_daily(rows,months)
 daily={}
 for metal,dt,price,version in rows:
  d=dt.isoformat()
  daily.setdefault(d,{})
  require(metal not in daily[d],"DUPLICATE_METAL_DATE")
  daily[d][metal]=float(price)
 price_rows=[{"date":d,"metals":[daily[d][x] for x in ("AU","AG","PT","PD")]}
            for d in sorted(daily) if len(daily[d])==4]
 require(len(price_rows)>4000,"PRICE_PANEL_TOO_SHORT")
 require(abs(next(p for p in price_rows if p["date"]==BAD)["metals"][0]-3516.02)<.01,
         "KNOWN_FALSE_FEB27_SOURCE_ROW_CHANGED")
 macro={name:{} for name in SERIES}
 lineage={}
 for sid,t,v,provider_as_of,available_as_of in macro_rows:
  d=t.isoformat()
  require(sid in macro,"UNKNOWN_MACRO_SERIES")
  require(d not in macro[sid],"DUPLICATE_MACRO_DATE_"+sid)
  macro[sid][d]=float(v)
  lineage.setdefault(sid,{"provider_as_of_example":str(provider_as_of),
                          "available_as_of_example":str(available_as_of)})
 require(all(len(macro[x])>850 for x in SERIES),"MACRO_NOT_ENOUGH_FOR_2023_2026")
 payload={
  "model":MODEL,"original_source_research_only":True,
  "price_firstprint_certified":False,"original_available_as_of_is_backfill_date":True,
  "cboe_gvz_source":"https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
  "cboe_gvz_sha256":hashlib.sha256(Path(gvzfile).read_bytes()).hexdigest(),
  "gvz":gvz,"prices":price_rows,"macro":macro,"macro_lineage":lineage,
  "monthly_source_parity":proof,"quarantine_date":BAD}
 payload["source_sha256"]=hash_json(payload)
 Path(outfile).write_text(json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n")
 print("RISK_OVERLAY_SOURCE_GATE_PASS",len(price_rows),len(gvz),
       {s:len(macro[s]) for s in SERIES},payload["source_sha256"],flush=True)
def next_monday_after_obs(d):
 # official H.10 previous week released following Monday.
 dt=date.fromisoformat(d)
 days=(7-dt.weekday())%7
 if days==0:days=7
 return (dt+timedelta(days=days)).isoformat()
def series_at_issue(dates,mapping,issue,release_type):
 usable=[]
 for dt in dates:
  if release_type=="H10":
   available=next_monday_after_obs(dt)
  elif release_type=="H15_PREVIOUS_DAY":
   available=(date.fromisoformat(dt)+timedelta(days=1)).isoformat()
  else:raise ValueError(release_type)
  if available<=issue:usable.append(dt)
 return usable
def rsi(prices):
 v=np.diff(np.log(prices[-15:]))
 up=np.maximum(0,v).mean();down=np.maximum(0,-v).mean()
 return (100 if down<1e-10 else 100*up/(up+down))/100
def data(s):
 digest=s.pop("source_sha256")
 require(digest==hash_json(s),"SOURCE_SHA256_MISMATCH")
 s["source_sha256"]=digest
 dates=[x["date"] for x in s["prices"]]
 P=np.array([x["metals"] for x in s["prices"]],float)
 L=np.log(P)
 G=s["gvz"];gdays=sorted(G)
 U=s["macro"]["DTWEXBGS_FRB_H10"]; udays=sorted(U)
 R=s["macro"]["DGS10_FRB_H15"];rdays=sorted(R)
 rows=[]
 for i in range(260,len(dates)-5):
  d=dates[i]
  if d<"2023-01-03" or d>"2026-09-21":continue
  if any(v==BAD for v in dates[max(0,i-20):i+6]):continue
  pos=bisect_right(gdays,d)
  if pos<253:continue
  gd=gdays[pos-1]
  if (date.fromisoformat(d)-date.fromisoformat(gd)).days>4:continue
  g=np.array([G[k] for k in gdays[pos-253:pos]],float)
  # strictly release-aware Broad USD end-of-previous-week observations
  # faster cutoff by date while exact availability is checked on chosen value.
  usd_keys=series_at_issue(udays,U,d,"H10")
  rate_keys=series_at_issue(rdays,R,d,"H15_PREVIOUS_DAY")
  if len(usd_keys)<10 or len(rate_keys)<10:continue
  uk=usd_keys[-1];rk=rate_keys[-1]
  u=np.array([U[x] for x in usd_keys[-6:]],float)
  r=np.array([R[x] for x in rate_keys[-6:]],float)
  # Guardrail: not retroactive H.10 same-day observation used.
  require(next_monday_after_obs(uk)<=d and uk<d,"H10_OBS_RELEASE_LEAK")
  require(rk<d,"H15_SAME_DAY_UNVERIFIED")
  x=[
   float(L[i,0]-L[i-5,0]),float(L[i,0]-L[i-20,0]),
   float(rsi(P[i-14:i+1,0])),float(P[i,0]/P[i-19:i+1,0].mean()-1),
   float(np.std(np.diff(L[i-5:i+1,0]))),
   float(np.std(L[i]-L[i-5])),
   float(g[-1]),float((g[-1]-g[:-1].mean())/max(g[:-1].std(),.001)),
   float(math.log(g[-1]/g[-6])),float(math.log(g[-1]/g[-2])),
   float(math.log(u[-1]/u[-6])),float(math.log(u[-1]/u[-2])),
   float(r[-1]-r[-6]),float(r[-1]),
  ]
  next_daily=float(P[i+1,0]/P[i,0]-1)
  min5=float(np.min(P[i+1:i+6,0]/P[i,0]-1))
  max_abs5=float(max(abs(P[k,0]/P[i,0]-1) for k in range(i+1,i+6)))
  row={
   "origin":d,"first_target":dates[i+1],"target5_mature":dates[i+5],
   "gvz_observation":gd,"usd_last_observation":uk,
   "usd_release_date":next_monday_after_obs(uk),"yield_last_observation":rk,
   "xau_price":float(P[i,0]),"features":x,
   "next_day_return_pct":100*next_daily,
   "min_next5_return_pct":100*min5,
   "next_day_drop3":next_daily<=-0.03,
   "next5_drop5":min5<=-0.05,
   "next5_large_abs5":max_abs5>=0.05,
  }
  rows.append(row)
 require(len(rows)>830,"TOO_FEW_ROWS")
 require(any(x["origin"]=="2026-01-29" for x in rows),"JAN29_NOT_IN_PANEL")
 require(all(x["usd_release_date"]<=x["origin"] and
             x["yield_last_observation"]<x["origin"] and
             x["gvz_observation"]<=x["origin"] for x in rows),"DATED_FEATURE_GATE")
 return rows

def run(s,output):
 rows=data(s)
 # 2025 diagnostic: trained only on 2023-24; 2026: trained on completed 2023-25.
 # No regime parameter/effect size selection based on 2026.
 phases=[
   {"name":"2025","train_last":"2024-12-31","scoring_first":"2025-01-01","scoring_last":"2025-12-31"},
   {"name":"2026","train_last":"2025-12-31","scoring_first":"2026-01-01","scoring_last":"2026-09-21"}
 ]
 results={};scores=[]
 for period in phases:
  train=[v for v in rows if v["origin"]<="2024-12-20" if v["target5_mature"]<=period["train_last"]]
  if period["name"]=="2026":
   train=[v for v in rows if v["target5_mature"]<=period["train_last"] and v["origin"]<"2026-01-01"]
  score=[v for v in rows if period["scoring_first"]<=v["origin"]<=period["scoring_last"]]
  require(len(train)>400 and len(score)>100,"TRAIN_SCORE_INADEQUATE_"+period["name"])
  for family,indices in FAMILIES.items():
   a=np.array([v["features"] for v in train],float)[:,indices]
   b=np.array([v["features"] for v in score],float)[:,indices]
   require(np.isfinite(a).all() and np.isfinite(b).all(),"NONFINITE_FEATURES")
   scaler=RobustScaler().fit(a)
   cl=IsolationForest(n_estimators=200,max_samples=min(256,len(train)),
       contamination="auto",random_state=1701,n_jobs=1).fit(scaler.transform(a))
   # Higher risk = more anomalous; train-quantiles never touch target period.
   tr=-cl.score_samples(scaler.transform(a))
   te=-cl.score_samples(scaler.transform(b))
   ycut=float(np.quantile(tr,THRESHOLDS["YELLOW"]))
   rcut=float(np.quantile(tr,THRESHOLDS["RED"]))
   outrows=[]
   for v,risk in zip(score,te):
    level="RED" if risk>=rcut else "YELLOW" if risk>=ycut else "NORMAL"
    x={
     "origin":v["origin"],"forecast_target_start":v["first_target"],"horizon5_last":v["target5_mature"],
     "family":family,"level":level,"risk_anomaly_score":float(risk),
     "threshold_yellow":ycut,"threshold_red":rcut,
     "next_day_drop3":v["next_day_drop3"],"next5_drop5":v["next5_drop5"],
     "next5_large_abs5":v["next5_large_abs5"],
     "next_day_return_pct":v["next_day_return_pct"],"min_next5_return_pct":v["min_next5_return_pct"],
     "gvz":v["features"][6],"gvz_z252":v["features"][7],
     "usd_last_obs":v["usd_last_observation"],
     "usd_last_release":v["usd_release_date"],"dgs10_last_obs":v["yield_last_observation"],
    }
    outrows.append(x)
    scores.append(x)
   stats={"fit_end":period["train_last"],"n_train":len(train),"n_score":len(outrows),
     "train_threshold_yellow":ycut,"train_threshold_red":rcut}
   for label in ("next_day_drop3","next5_drop5","next5_large_abs5"):
    events=[x for x in outrows if x[label]]
    alerted=[x for x in outrows if x["level"]!="NORMAL"]
    hits=[x for x in alerted if x[label]]
    stats[label]={
       "event_issue_days":len(events),"alert_issue_days":len(alerted),
       "true_positive_issue_days":len(hits),
       "miss_issue_days":len(events)-len(hits),
       "false_alarm_issue_days":len(alerted)-len(hits),
       "precision":len(hits)/len(alerted) if alerted else None,
       "recall":len(hits)/len(events) if events else None}
   results.setdefault(period["name"],{})[family]=stats
   print("RISK_OVERLAY_METRIC",period["name"],family,json.dumps(stats,sort_keys=True),flush=True)
 important=["2026-01-22","2026-01-26","2026-01-27","2026-01-28","2026-01-29","2026-01-30","2026-02-02","2026-06-05","2026-08-24"]
 for d in important:
  q=[x for x in scores if x["origin"]==d]
  if q:print("RISK_OVERLAY_EVENT",d,
        json.dumps({x["family"]:{"alert":x["level"],
         "risk":round(x["risk_anomaly_score"],4),
         "next5_dd_pct":round(x["min_next5_return_pct"],2)} for x in q},sort_keys=True),flush=True)
 out={
  "status":"RESEARCH_ONLY_UNCALIBRATED_ANOMALY_RISK_LAYER",
  "source_sha256":s["source_sha256"],"no_base_price_model_changed":True,
  "ann_error_probability_validated":False,
  "forecast_error_lookback_not_present":True,
  "cannot_claim_predicted_crash_2026_ex_ante":True,
  "output_signal_semantics":"HIGHLY_UNUSUAL_MARKET_CONDITIONS, not downside probability or price forecast residual probability",
  "data_vintage_verified":False,
  "train_2025_for_2026_only":True,
  "2025_diagnostic_fitted_2023_2024_only":True,
  "known_bad_2026_price_date":BAD,"feature_names":FEATURE_NAMES,
  "date_lag_rules":{"H10":"next Monday after obs week, 16:15 ET",
     "H15":"at least one calendar day after obs",
     "GVZ":"latest observed <= origin after US options close"},
  "families":FAMILIES,"thresholds":THRESHOLDS,
  "stats":results,"rows":scores,
  "integration_contract":{
   "inputs":"forecast issue date, target interval, risk origin date, family, level",
   "warning_rule":"add uncertainty annotation to active forecast only once the risk origin data existed",
   "no_retroactive_issue_rewrite":True,
   "no_price_override":True,
   "unvalidated_residual_risk":True,
  }}
 Path(output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print("RISK_OVERLAY_ALL_SCORES_SUCCESS",len(scores),flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--mode",required=True,choices=["source","score"])
 p.add_argument("--gvz-csv")
 p.add_argument("--snapshot")
 p.add_argument("--out",required=True)
 a=p.parse_args()
 if a.mode=="source":return source_extract(a.out,a.gvz_csv)
 return run(json.loads(Path(a.snapshot).read_text()),a.out)

if __name__=="__main__":
 main()
