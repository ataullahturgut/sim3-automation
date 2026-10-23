"""Weekly H=1 XAU/USD research: origin-known four-metal 16D weekly MLP.

New separate weekly model, NOT a resampling of monthly ANN or reuse of monthly
FULL7 weights. Weekly targets: next completed Mon–Sun ISO week XAU average and
last shared trading-day XAU close, each conditioned only on earlier completed
weeks. Prices are retrospective research Git snapshots NOT firstprint/PIT.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,warnings
from collections import defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import psycopg
from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning
import gold_monthly_h1_neon_source_v2 as source

M=("AU","AG","PT","PD")
SRC="STAKTRAKR_4_METAL_OLD_NEW_GIT_MONTH_PARITY"
FST=date(2022,4,4)
DEV_LAST=date(2024,12,31)
TEST_LAST=date(2025,12,31)
STRESS_LAST=date(2026,9,27)
MODEL="WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1"
PARAMS={"hidden_layer_sizes":[8],"activation":"tanh","solver":"lbfgs",
        "alpha":1.0,"max_iter":180,"tol":1e-5,"random_state":1701,
        "early_stopping":False}
SHARDS=8

def check(ok,why):
    if not ok:raise RuntimeError("WEEKLY_GOLD_RESEARCH_GATE_FAILED "+why)

def signature(z):
    return hashlib.sha256(json.dumps(z,sort_keys=True,separators=(",",":"),
                       allow_nan=False).encode()).hexdigest()

def mon(d):
    return d-timedelta(days=d.weekday())

def mo(s):
    return date.fromisoformat(s)

def series_rows():
    check(bool(os.getenv("NEON_DATABASE_URL")),"READ_ONLY_NEON_URL_MISSING")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            cur.execute(source.PRICE_SQL)
            daily=cur.fetchall()
            cur.execute(source.MONTHLY_SQL)
            monthly=cur.fetchall()
    _,_,proof=source.normalize_daily(daily,monthly)
    check(proof["source_pit_verified"] is False,"MISCLASSIFIED_RETROSPECTIVE_PRICE")
    return daily,monthly,proof

def snapshot(outfile):
    daily,monthly,proof=series_rows()
    grp=defaultdict(dict)
    bydate=defaultdict(dict)
    for code,d,p,rev in daily:
        check(code in M,"UNKNOWN_METAL")
        check(float(p)>0 and math.isfinite(float(p)),"BAD_DAILY_PRICE")
        check(code not in bydate[d],"DUPLICATE_METAL_DATE")
        bydate[d][code]=float(p)
    shared_dates=sorted(d for d in bydate if len(bydate[d])==4)
    for d in shared_dates:
        grp[mon(d)][d]=bydate[d]
    weeks=[]
    exclude={"<3_aligned_trading_days":0,"last_incomplete_calendar_week":0}
    lastdate=max(shared_dates)
    for wk,days in sorted(grp.items()):
        if wk+timedelta(days=6)>lastdate:
            exclude["last_incomplete_calendar_week"]+=1
            continue
        if len(days)<3:
            exclude["<3_aligned_trading_days"]+=1
            continue
        ordered=sorted(days)
        prices=np.array([[days[d][metal] for metal in M] for d in ordered],float)
        check(np.isfinite(prices).all() and prices.min()>0,"NONFINITE_WEEK_PRICES")
        week={
            "week_monday":wk.isoformat(),
            "first_observation":ordered[0].isoformat(),
            "last_observation":ordered[-1].isoformat(),
            "shared_trading_days":len(ordered),
            "means":prices.mean(0).tolist(),
            "opens":prices[0].tolist(),
            "closes":prices[-1].tolist(),
            "highs":prices.max(0).tolist(),
            "lows":prices.min(0).tolist(),
            "daily_realized_vol":np.sqrt(np.sum(np.diff(np.log(prices),axis=0)**2,axis=0)).tolist(),
        }
        weeks.append(week)
    check(len(weeks)>=800,"WEEKLY_PANEL_NOT_ENOUGH")
    check(weeks[0]["week_monday"][:4]=="2010","2010_PRICE_HISTORY_NOT_PRESENT")
    eligible={w["week_monday"]:w for w in weeks}
    targets=[]
    for wk in sorted(eligible):
        day=mo(wk)
        if not FST<=day<=STRESS_LAST: continue
        prior=(day-timedelta(days=7)).isoformat()
        prior2=(day-timedelta(days=14)).isoformat()
        if prior not in eligible or prior2 not in eligible:continue
        targets.append(wk)
    check(len(targets)>180,"EVALUATION_TOO_FEW_WEEKS")
    check(targets[0]=="2022-04-04","FIRST_FULL_2022_APRIL_TARGET_GAP")
    check(targets[-1]<="2026-09-21","INCOMPLETE_LAST_2026_WEEK_INCLUDED")
    payload={
      "kind":"GOLD_WEEKLY_H1_ALIGNED_FOUR_METAL_SNAPSHOT",
      "model":MODEL,"data_contract":SRC,
      "four_metals_order":list(M),
      "week":"MONDAY_ISO_THROUGH_SUNDAY_UTC",
      "price_target":"NEXT_COMPLETE_WEEK_FOUR_METAL_SHARED_DAY_MEAN_XAU",
      "close_target":"NEXT_COMPLETE_WEEK_LAST_COMMON_TRADING_DAY_XAU_CLOSE",
      "forecast_origin":"PREVIOUS_COMPLETE_WEEK_CLOSE",
      "source_firstprint_certified":False,
      "price_git_commits":{"pre2026":source.PRICE_COMMIT_OLD,"in2026":source.PRICE_COMMIT_2026},
      "monthly_source_verified":True,
      "source_alignment_check":proof,
      "excluded_weeks":exclude,
      "week_summaries":weeks,
      "targets":targets,
    }
    payload["sha256"]=signature({k:v for k,v in payload.items() if k!="sha256"})
    Path(outfile).write_text(json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n")
    print("WEEKLY_CANONICAL_SOURCE_VERIFIED",len(weeks),"weeks",
          len(targets),"targets","coverage",weeks[0]["week_monday"],weeks[-1]["week_monday"],
          "source sha256",payload["sha256"],"excluded",exclude,flush=True)

def read_snapshot(path):
    s=json.loads(Path(path).read_text())
    check(s.get("kind")=="GOLD_WEEKLY_H1_ALIGNED_FOUR_METAL_SNAPSHOT","WRONG_SNAPSHOT_KIND")
    check(s.get("source_firstprint_certified") is False,"WRONG_PIT_FLAG")
    check(s.get("monthly_source_verified") is True,"MONTHLY_SOURCE_PARITY_NOT_ESTABLISHED")
    check(s["sha256"]==signature({k:v for k,v in s.items() if k!="sha256"}),"SNAPSHOT_HASH_INCORRECT")
    check(s["model"]==MODEL and s["data_contract"]==SRC,"MODEL_ID_CHANGED")
    check(len(s["week_summaries"])>=800 and len(s["targets"])>180,"MISSING_WEEKLY_HISTORY")
    check(s["targets"]==sorted(s["targets"]),"UNSORTED_TARGETS")
    return s

def features(weekly,wk):
    """strictly prior two weeks: no target-week observations whatsoever"""
    d=mo(wk)
    p=(d-timedelta(days=7)).isoformat()
    q=(d-timedelta(days=14)).isoformat()
    if p not in weekly or q not in weekly:return None
    a=weekly[p];b=weekly[q]
    amean=np.array(a["means"],float);bmean=np.array(b["means"],float)
    ao=np.array(a["opens"],float);ac=np.array(a["closes"],float)
    hi=np.array(a["highs"],float);lo=np.array(a["lows"],float)
    vol=np.array(a["daily_realized_vol"],float)
    check(np.all(amean>0) and np.all(bmean>0) and np.all(lo>0),"INVALID_FEATURE_PRICE")
    return np.stack([
       np.log(amean/bmean),
       np.log(ac/ao),
       vol,
       np.log(hi/lo),
    ],axis=-1).flatten()

def model_inputs(s,target):
    dic={x["week_monday"]:x for x in s["week_summaries"]}
    origin=(mo(target)-timedelta(days=7)).isoformat()
    check(origin in dic and target in dic,"MISSING_ORIGIN_TARGET_WEEK")
    ks=sorted(k for k in dic if k<target and features(dic,k) is not None)
    check(len(ks)>550,"TOO_FEW_TRAINING_WEEKS")
    X=np.stack([features(dic,k) for k in ks])
    prior=[(mo(k)-timedelta(days=7)).isoformat() for k in ks]
    y=np.array([[
       math.log(dic[k]["means"][0]/dic[pk]["means"][0]),
       math.log(dic[k]["closes"][0]/dic[pk]["closes"][0])
      ] for k,pk in zip(ks,prior)],float)
    tx=features(dic,target)
    check(tx.shape==(16,) and X.shape==(len(ks),16)
          and y.shape==(len(ks),2),"BAD_WEEKLY_MLP_SHAPE")
    check(np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all(),
          "NONFINITE_WEEKLY_FEATURES")
    return ks,X,y,tx,dict(dic[origin]),dict(dic[target])

def probe_poison(s,t):
    original=model_inputs(s,t)
    cp=copy.deepcopy(s)
    targetweek=next(r for r in cp["week_summaries"] if r["week_monday"]==t)
    for key in ("means","closes","opens","highs","lows"):
        targetweek[key]=[v*1234.0 for v in targetweek[key]]
    targetweek["daily_realized_vol"]=[99.0]*4
    cp["week_summaries"].append({
       "week_monday":"2099-01-05","first_observation":"2099-01-05",
       "last_observation":"2099-01-09","shared_trading_days":5,
       **{x:[1e12]*4 for x in ("means","closes","opens","highs","lows","daily_realized_vol")},
    })
    altered=model_inputs(cp,t)
    need=original[:4]
    check(need[0]==altered[0] and
          all(np.array_equal(a,b) for a,b in zip(need[1:],altered[1:4])),
          "TARGET_OR_FUTURE_PRICES_CHANGED_TRAIN_OR_FORECAST_X")
    check(original[5]["means"][0]!=altered[5]["means"][0],"POISON_TARGET_CANARY_IGNORED")
    return {"pass":True,"week":t,"training_weeks":len(original[0]),
            "training_last":original[0][-1],"first_training_week":original[0][0]}

def safe_standardize(X,y,tx):
    xm=X.mean(0);xs=X.std(0);ym=y.mean(0);ys=y.std(0)
    xs=np.where(xs<1e-9,1,xs);ys=np.where(ys<1e-9,1,ys)
    return (X-xm)/xs,(y-ym)/ys,(tx-xm)/xs,ym,ys

def fit_predict(s,t):
    keys,X,y,xt,prior,actual=model_inputs(s,t)
    a,b,z,ym,ys=safe_standardize(X,y,xt)
    model=MLPRegressor(hidden_layer_sizes=(8,),activation="tanh",
       solver="lbfgs",alpha=1.0,max_iter=180,tol=1e-5,
       random_state=1701,early_stopping=False)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=ConvergenceWarning)
        model.fit(a,b)
    pred=np.asarray(model.predict(z.reshape(1,-1))[0]*ys+ym,float)
    check(np.all(np.isfinite(pred)) and np.max(abs(pred))<0.50,"PATHOLOGICAL_WEEKLY_RETURN")
    forecast_mean=prior["means"][0]*math.exp(float(pred[0]))
    forecast_close=prior["closes"][0]*math.exp(float(pred[1]))
    actual_mean=actual["means"][0]; actual_close=actual["closes"][0]
    check(forecast_mean>0 and forecast_close>0,"NONPOSITIVE_WEEKLY_FORECAST")
    return {
      "target_week":t,"origin_week":(mo(t)-timedelta(days=7)).isoformat(),
      "source_firstprint_certified":False,
      "forecast_mean_xau":forecast_mean,"actual_mean_xau":actual_mean,
      "origin_mean_xau":prior["means"][0],
      "forecast_close_xau":forecast_close,"actual_close_xau":actual_close,
      "origin_close_xau":prior["closes"][0],
      "baseline_mean_xau":prior["means"][0],
      "baseline_close_xau":prior["closes"][0],
      "mean_abs_error":abs(forecast_mean-actual_mean),
      "mean_ape_pct":100*abs(forecast_mean-actual_mean)/actual_mean,
      "close_abs_error":abs(forecast_close-actual_close),
      "close_ape_pct":100*abs(forecast_close-actual_close)/actual_close,
      "baseline_mean_abs_error":abs(prior["means"][0]-actual_mean),
      "baseline_mean_ape_pct":100*abs(prior["means"][0]-actual_mean)/actual_mean,
      "baseline_close_abs_error":abs(prior["closes"][0]-actual_close),
      "baseline_close_ape_pct":100*abs(prior["closes"][0]-actual_close)/actual_close,
      "mean_direction_correct":int(np.sign(forecast_mean-prior["means"][0])==
                                    np.sign(actual_mean-prior["means"][0])),
      "close_direction_correct":int(np.sign(forecast_close-prior["closes"][0])==
                                     np.sign(actual_close-prior["closes"][0])),
      "training_first_week":keys[0],"training_last_week":keys[-1],
      "training_n":len(keys),"feature_dim":X.shape[1],
      "fitted_iterations":int(model.n_iter_),
      "target_common_days":actual["shared_trading_days"],
      "actual_last_common_trading_day":actual["last_observation"],
    }

def metrics(rows):
    if not rows:return {}
    return {
      "weeks":len(rows),
      "mean_MAPE_pct":sum(r["mean_ape_pct"] for r in rows)/len(rows),
      "mean_sum_AE":sum(r["mean_abs_error"] for r in rows),
      "mean_direction_correct":sum(r["mean_direction_correct"] for r in rows),
      "close_MAPE_pct":sum(r["close_ape_pct"] for r in rows)/len(rows),
      "close_sum_AE":sum(r["close_abs_error"] for r in rows),
      "close_direction_correct":sum(r["close_direction_correct"] for r in rows),
      "naive_mean_MAPE_pct":sum(r["baseline_mean_ape_pct"] for r in rows)/len(rows),
      "naive_mean_sum_AE":sum(r["baseline_mean_abs_error"] for r in rows),
      "naive_close_MAPE_pct":sum(r["baseline_close_ape_pct"] for r in rows)/len(rows),
      "naive_close_sum_AE":sum(r["baseline_close_abs_error"] for r in rows),
    }

def execute(args):
    if args.mode=="snapshot":
        snapshot(args.output)
        return
    s=read_snapshot(args.snapshot)
    all_t=s["targets"]
    if args.mode=="audit":
        # exact live target labels cannot affect model inputs
        records=[probe_poison(s,t) for t in all_t]
        result={"status":"WEEKLY_ALL_TARGETS_ACTIVE_POISON_PASS",
                "n":len(records),"rows":records}
    elif args.mode=="pilot":
        probe_poison(s,all_t[0])
        records=[fit_predict(s,all_t[0])]
        result={"status":"WEEKLY_ANN_SINGLE_WEEK_PILOT_PASS","n":1,"rows":records}
    elif args.mode=="replay":
        check(args.shard is not None and 0<=args.shard<SHARDS,"BAD_SHARD")
        assigned=[t for i,t in enumerate(all_t) if i%SHARDS==args.shard]
        records=[]
        for i,t in enumerate(assigned,1):
            row=fit_predict(s,t)
            records.append(row)
            print("WEEKLY_ANN_REAL_PRICE_PREDICT",args.shard,i,"/",len(assigned),
                  t,"forecast_mean",format(row["forecast_mean_xau"],".4f"),
                  "actual_mean",format(row["actual_mean_xau"],".4f"),flush=True)
        result={"status":"WEEKLY_ANN_SHARD_REPLAY_PASS","shard":args.shard,
                "n":len(records),"rows":records}
    else:raise RuntimeError("BAD_MODE")
    result.update({
       "model":MODEL,"source_sha256":s["sha256"],
       "source_research_not_firstprint":True,
       "fit_past_only":True,"model_hyperparameters":PARAMS,
       "feature_contract":"4_METALS_X_4_WEEKLY_ORIGIN_ONLY_STATISTICS",
       "baseline":"PREVIOUS_WEEK_LEVEL",
       "model_production_enabled":False,
       "database_writes":"NONE",
    })
    Path(args.output).write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("WEEKLY_GOLD_RUN_GATE",result["status"],"targets",result["n"],flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--mode",required=True,choices=("snapshot","audit","pilot","replay"))
    a.add_argument("--snapshot")
    a.add_argument("--output",required=True)
    a.add_argument("--shard",type=int)
    args=a.parse_args()
    if args.mode!="snapshot":check(bool(args.snapshot),"SNAPSHOT_ARG_REQUIRED")
    execute(args)
if __name__=="__main__":main()
