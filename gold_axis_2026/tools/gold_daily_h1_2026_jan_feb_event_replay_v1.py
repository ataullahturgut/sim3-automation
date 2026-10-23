"""Research-only next shared-trading-day gold daily-price forecast, Jan-Feb 2026.

STRICT D-1 cutoff; target gold daily quote is NOT intraday minimum or 16:00 close.
Independent ANN trained over past shared-day Au, Ag, Pt, Pd history; no
same-target market response, economic news or future bars. Fixed ANN
architecture, no 2026 hyperparameter selection. Explicit 2026-02-27
source anomaly quarantine (does not enter scored result).
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,warnings
from datetime import date
from pathlib import Path
import numpy as np,psycopg
from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning
import gold_monthly_h1_neon_source_v2 as source

M=("AU","AG","PT","PD")
MODEL="DAILY_H1_4_METAL_ANN_FIXED8_TANH_ALPHA1_RESEARCH"
BAD={"2026-02-27":"INDEPENDENT_SOURCE_CONFLICT_AU3516_VS_REUTERS5230"}
PARAM={"hidden_layer_sizes":[8],"activation":"tanh","solver":"lbfgs",
       "alpha":1.0,"max_iter":160,"tol":1e-5,"random_state":1701}
FIRST=date(2026,1,1)
LAST=date(2026,2,28)
SMOKE={"2026-01-29","2026-01-30","2026-02-02","2026-02-03","2026-02-04"}
def need(cond,msg):
    if not cond:raise RuntimeError("DAILY_H1_AUDIT_FAIL "+msg)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def snapshot(output):
    need(bool(os.getenv("NEON_DATABASE_URL")),"NEON_URL_MISSING")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            cur.execute(source.PRICE_SQL);days=cur.fetchall()
            cur.execute(source.MONTHLY_SQL);months=cur.fetchall()
    _,_,proof=source.normalize_daily(days,months)
    bydate={}
    for metal,d,p,rev in days:
        ds=d.isoformat()
        if ds not in bydate:bydate[ds]={}
        need(metal not in bydate[ds],"DUPLICATE_DAY_METAL")
        bydate[ds][metal]=float(p)
    kept=[]
    for d,prices in sorted(bydate.items()):
        if len(prices)==4:
            kept.append({"date":d,"quotes":[prices[k] for k in M]})
    need(len(kept)>4000 and kept[0]["date"].startswith("2010"),"INSUFFICIENT_2010_PRICE_HISTORY")
    need(any(x["date"]=="2026-01-29" for x in kept),"JAN29_ABSENT")
    need(any(x["date"]=="2026-01-30" for x in kept),"JAN30_ABSENT")
    need(any(x["date"]=="2026-02-02" for x in kept),"FEB02_ABSENT")
    anomaly=next(x for x in kept if x["date"]=="2026-02-27")
    need(abs(anomaly["quotes"][0]-3516.02)<0.01,"KNOWN_SUSPECT_ROW_CHANGED_REQUIRE_REAUDIT")
    snap={"kind":"DAILY_H1_4METAL_GIT_RESEARCH_ONLY",
          "model":MODEL,"four_metals":list(M),"price_target":"NEXT_COMMON_TRADING_DAY_DAILY_REFERENCE_XAU",
          "firstprint_certified":False,"monthly_view_exact_parity":True,
          "source_proof":proof,"data":kept,"quarantined_targets":BAD,
          "pinned_commits":{"pre2026":source.PRICE_COMMIT_OLD,"in2026":source.PRICE_COMMIT_2026}}
    snap["sha256"]=digest({k:v for k,v in snap.items() if k!="sha256"})
    Path(output).write_text(json.dumps(snap,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n")
    print("DAILY_JAN_FEB_SOURCE_READ_ONLY",len(kept),"aligned days; anomaly",anomaly,"sha",snap["sha256"],flush=True)

def read(path):
    s=json.loads(Path(path).read_text())
    need(s["kind"]=="DAILY_H1_4METAL_GIT_RESEARCH_ONLY","SNAPSHOT_KIND")
    need(s["firstprint_certified"] is False and s["monthly_view_exact_parity"] is True,"PIT_OR_SOURCE_FALSE")
    need(s["sha256"]==digest({k:v for k,v in s.items() if k!="sha256"}),"SOURCE_SHA")
    need(s["quarantined_targets"]==BAD,"QUARANTINE_MISSING")
    need(len(s["data"])>4000,"HISTORY_SIZE")
    return s

def prepare(s):
    D=[v["date"] for v in s["data"]]
    P=np.asarray([v["quotes"] for v in s["data"]],float)
    need(P.shape==(len(D),4) and np.isfinite(P).all() and P.min()>0,"BAD_SOURCE")
    F=np.full((len(P),16),np.nan,float)
    # target i prediction knows observations up to i-1 ONLY
    lg=np.log(P)
    for i in range(11,len(P)):
        prev=i-1
        r1=lg[prev]-lg[prev-1]
        r3=lg[prev]-lg[prev-3]
        r5=lg[prev]-lg[prev-5]
        rv5=np.sqrt(np.mean(np.diff(lg[prev-5:prev+1],axis=0)**2,axis=0))
        F[i]=np.stack((r1,r3,r5,rv5),axis=1).reshape(-1)
    y=np.zeros(len(P))
    y[1:]=np.diff(lg[:,0])
    return D,P,F,y

def design(D,P,F,y,i):
    # last training label MUST be from the previous observed daily quote
    ids=np.arange(11,i)
    X=F[ids];Y=y[ids]
    need(len(ids)>600,"TOO_SHORT_TRAIN_HISTORY")
    need(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(F[i]).all(),"NAN_INPUT")
    return X,Y,F[i].copy(),D[i-1],float(P[i-1,0]),float(P[i,0]),D[ids[-1]],len(ids)

def poison_audit(s,i):
    D,P,F,y=prepare(s)
    a=design(D,P,F,y,i)
    cp=copy.deepcopy(s)
    t=cp["data"][i]
    t["quotes"]=[v*1234 for v in t["quotes"]]
    cp["data"].append({"date":"2099-01-05","quotes":[1e10]*4})
    _,_,FF,yy=prepare(cp)
    b=design(D,np.asarray([x["quotes"] for x in cp["data"][:len(D)]],float),FF[:len(D)],yy[:len(D)],i)
    need(all(np.array_equal(u,v) for u,v in zip(a[:3],b[:3])) and a[3:5]==b[3:5],
        "TARGET_OR_2099_DATA_AFFECTED_TRAIN_OR_TARGET_FEATURE")
    need(a[6:]==b[6:],"TRAIN_CUTOFF_CHANGED")
    return {"date":D[i],"issue_date":D[i-1],"training_last":a[6],"training_n":a[7],
            "target_label_poison_invariant":True,"future_2099_poison_invariant":True}

def fit(s,i):
    D,P,F,y=prepare(s)
    X,Y,xt,orig,p0,p1,last,n=design(D,P,F,y,i)
    xm=X.mean(0);xs=X.std(0);ym=Y.mean();ys=Y.std()
    xs=np.where(xs<1e-9,1,xs);ys=ys if ys>1e-9 else 1
    model=MLPRegressor(hidden_layer_sizes=(8,),activation="tanh",
       solver="lbfgs",alpha=1.0,max_iter=160,tol=1e-5,random_state=1701)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=ConvergenceWarning)
        model.fit((X-xm)/xs,(Y-ym)/ys)
    pr=float(model.predict(((xt-xm)/xs)[None,:])[0])*ys+ym
    need(math.isfinite(pr) and abs(pr)<.5,"PREDICTED_RETURN_PATHOLOGICAL")
    change=math.expm1(pr)*100
    actual_change=(p1/p0-1)*100
    return {
        "target_date":D[i],"issue_date":orig,"target_quote_available_only_after_issue":True,
        "training_first":D[11],"training_last":last,"training_rows":n,
        "origin_xau_reference":p0,"forecast_xau_reference":p0*math.exp(pr),
        "actual_xau_reference":p1,"predicted_return_pct":change,
        "actual_return_pct":actual_change,
        "predicted_direction":"DOWN" if change<0 else "UP",
        "actual_direction":"DOWN" if actual_change<0 else "UP",
        "correct_direction":bool((change<0)==(actual_change<0)),
        "forecast_severe_drop_3pct":bool(change<=-3.0),
        "actual_severe_drop_3pct":bool(actual_change<=-3.0),
        "forecast_crash_5pct":bool(change<=-5.0),
        "actual_crash_5pct":bool(actual_change<=-5.0),
        "price_error_pct":100*abs(p0*math.exp(pr)-p1)/p1,
        "naive_price_error_pct":100*abs(p0-p1)/p1,
        "naive_previous_momentum_direction":"DOWN" if P[i-1,0]<P[i-2,0] else "UP",
        "fit_iterations":int(model.n_iter_)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",required=True,choices=("source","audit","replay"))
    ap.add_argument("--snapshot")
    ap.add_argument("--output",required=True)
    ap.add_argument("--shard",type=int)
    a=ap.parse_args()
    if a.mode=="source":return snapshot(a.output)
    s=read(a.snapshot)
    D,P,F,y=prepare(s)
    selected=[i for i,d in enumerate(D) if FIRST<=date.fromisoformat(d)<=LAST]
    need("2026-01-30" in [D[i] for i in selected] and "2026-02-02" in [D[i] for i in selected],"EVENT_DATES_ABSENT")
    quarantine=[D[i] for i in selected if D[i] in BAD]
    chosen=[i for i in selected if D[i] not in BAD]
    need(quarantine==["2026-02-27"],"SOURCE_ANOMALY_NOT_EXCLUDED")
    if a.mode=="audit":
        rows=[poison_audit(s,i) for i in chosen]
        result={"status":"JAN_FEB_DAILY_ALL_ORIGIN_AND_FUTURE_POISON_PASS","rows":rows}
    else:
        need(a.shard is not None and 0<=a.shard<4,"SHARD_INVALID")
        rows=[]
        for n,i in enumerate(chosen):
            if n%4!=a.shard:continue
            p=fit(s,i)
            rows.append(p)
            print("GOLD_JAN_FEB_D1_PRED",p["issue_date"],"->",p["target_date"],
                  "expected",format(p["predicted_return_pct"],".4f"),"realized",
                  format(p["actual_return_pct"],".4f"),"alert3",
                  p["forecast_severe_drop_3pct"],"actual3",
                  p["actual_severe_drop_3pct"],flush=True)
        result={"status":"JAN_FEB_DAILY_H1_REAL_ANN_4METAL_REPLAY_SUCCESS",
                "shard":a.shard,"rows":rows}
    result.update({"model":MODEL,"source_sha256":s["sha256"],
       "source_firstprint_certified":False,"source_class":"RETROSPECTIVE_GIT_PRICE_NOT_PIT",
       "prediction_semantics":"PREVIOUS_REFERENCE_DAILY_QUOTE_TO_NEXT_REFERENCE_DAILY_QUOTE",
       "not_intraday_extremum_or_US_1600_tick":True,
       "quarantined_targets":BAD,"database_access":"NONE","data_mutation":False,
       "fixed_params":PARAM,"n":len(rows)})
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("GOLD_DAILY_H1_GATE",result["status"],result["n"],flush=True)
if __name__=="__main__":main()
