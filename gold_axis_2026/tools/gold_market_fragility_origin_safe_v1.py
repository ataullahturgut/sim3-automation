"""Model-independent pre-event XAU fragility core, provenance-gated research only.

Source price: four-metal StakTrakr pinned 2010-Sep2026 retrospective daily quotes,
same-source monthly parity; 2026-02-27 known anomalous quote quarantined.
Source volatility: CBOE GVZCLS via FRED official daily close CSV, fetched in
the GitHub workflow, hashed and archived. Not originally-recorded live ticks.

Issue: after NY equity-option close day t; most recent *already published*
GVZ daily close and same-day LBMA-labeled four-metal observations. Forecast
next common four-metal price day t+1 and worst next 5 trading-day daily quotes.
No prediction of intraday ticks, no CME silver-margin training (incomplete).
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
import numpy as np
import psycopg
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score,roc_auc_score
import gold_monthly_h1_neon_source_v2 as source

MODEL_ID="GOLD_MARKET_FRAGILITY_ORIGIN_SAFE_LOGIT_V1"
SRC_GVZ="https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS"
BAD_DAY="2026-02-27"
PRICE_FEATURES=["gold_ret1","gold_ret5","gold_ret20","gold_rsi14",
                "gold_ma20_distance","gold_peak20_dd","gold_rv5","gold_rv20"]
CROSS_FEATURES=["silver_ret1","silver_ret5","silver_rv5","cross_metal_ret5_dispersion"]
VOL_FEATURES=["gvz_level","gvz_z252","gvz_ret5","gvz_ret1"]
FEATURES=PRICE_FEATURES+CROSS_FEATURES+VOL_FEATURES
VARIANTS={"GOLD_ONLY":list(range(8)),
          "GOLD_GVZ":list(range(8))+list(range(12,16)),
          "GOLD_CROSS_GVZ":list(range(16))}
TARGETS={"DROP_1D_3PCT":"next single daily XAU quote return <=-3%",
         "DRAWDOWN_NEXT5D_5PCT":"minimum of next five daily XAU quotes <=-5% of issue reference",
         "MOVE_1D_3PCT":"next daily XAU absolute quote return >=3%"}
TRAIN_CUTOFF="2023-12-29"
VALID_START,VALID_END="2024-01-01","2024-12-31"
TEST_START,TEST_END="2025-01-01","2025-12-31"
STRESS_START,STRESS_END="2026-01-01","2026-02-19"
TRAIN_MIN=2000
ALERT_BUDGET=0.10
PARAMS={"C":0.25,"penalty":"l2","solver":"lbfgs","class_weight":"balanced",
        "max_iter":1500,"random_state":1701}
def gate(ok,err):
    if not ok: raise RuntimeError("MARKET_FRAGILITY_FAIL_CLOSED: "+err)
def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def source_extract(outfile,fred_path):
    with open(fred_path,encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    gate(bool(rows),"GVZ_CSV_EMPTY")
    header={k.lower():k for k in rows[0]}
    if "observation_date" in header and "gvzcls" in header:
        datekey,valuekey=header["observation_date"],header["gvzcls"]
        actual_source="CBOE_GVZ_VIA_FRED_OFFICIAL"
    elif "date" in header and ("close" in header or "gvz" in header):
        datekey,valuekey=header["date"],header.get("gvz",header.get("close"))
        actual_source="CBOE_GVZ_CBOE_OFFICIAL_HISTORICAL_DOWNLOAD"
    else:
        raise RuntimeError("MARKET_FRAGILITY_FAIL_CLOSED: UNKNOWN_GVZ_CSV_COLUMNS_"+str(list(rows[0])))
    gvz={}
    for row in rows:
        rawdate=row[datekey].strip();v=row[valuekey].strip()
        if not v or v==".":continue
        if "/" in rawdate:
            from datetime import datetime
            d=datetime.strptime(rawdate,"%m/%d/%Y").date().isoformat()
        else:
            d=rawdate
        gate(len(d)==10 and d[4]=="-" and d[7]=="-","INVALID_GVZ_DATE")
        num=float(v)
        gate(math.isfinite(num) and num>0,"GVZ_NONFINITE")
        gvz[d]=num
    gate("2010-01-04" in gvz and "2026-01-29" in gvz and "2025-12-31" in gvz,"MISSING_OFFICIAL_GVZ_PERIOD")
    gate(len(gvz)>3600,"GVZ_INCOMPLETE_HISTORICAL_BACKFILL")
    gate(abs(gvz["2026-01-29"]-46.02)<1e-6,"GVZ_2026_JAN29_OFFICIAL_CROSSCHECK")
    gate(bool(os.getenv("NEON_DATABASE_URL")),"NEON_READ_ONLY_URL_MISSING")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            cur.execute(source.PRICE_SQL);daily=cur.fetchall()
            cur.execute(source.MONTHLY_SQL);monthly=cur.fetchall()
    _,_,proof=source.normalize_daily(daily,monthly)
    gate(proof.get("source_firstprint_verified") is not True and proof["source_pit_verified"] is False,"FALSE_POINT_IN_TIME_ASSERTION")
    bydate={}
    for code,d,p,rev in daily:
        k=d.isoformat()
        if k not in bydate:bydate[k]={}
        gate(code not in bydate[k],"DUPLICATE_PRICE")
        bydate[k][code]=float(p)
    dates=sorted(k for k,v in bydate.items() if len(v)==4)
    panel=[{"date":d,"four_prices":[bydate[d][m] for m in ("AU","AG","PT","PD")]} for d in dates]
    gate(len(panel)>4000 and dates[0].startswith("2010"),"ALIGNED_PANEL_INSUFFICIENT")
    bad=next(x for x in panel if x["date"]==BAD_DAY)
    gate(abs(bad["four_prices"][0]-3516.02)<1e-2,"BAD_SOURCE_PRICE_CHANGED_REAUDIT")
    # Alarm on suspect large historical 1-day quote moves; do NOT silently delete.
    changes=[]
    for a,b in zip(panel,panel[1:]):
        if a["date"]>="2026-01-01":continue
        delta=b["four_prices"][0]/a["four_prices"][0]-1
        if abs(delta)>0.15:
            changes.append({"prev":a["date"],"date":b["date"],"ret_pct":100*delta})
    payload={"source":"OFFICIAL_CBOE_GVZ_AND_PINNED_STAKTRAKR_RESEARCH_PRICE",
       "gvz_actual_provider":actual_source,
       "gvz_url": SRC_GVZ if actual_source=="CBOE_GVZ_VIA_FRED_OFFICIAL" else "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
       "gvz_csv_sha256":hashlib.sha256(Path(fred_path).read_bytes()).hexdigest(),
       "gvz_count":len(gvz),"gvz":gvz,
       "prices":panel,"monthly_parity":proof,
       "firstprint_verified":False,"known_bad_price_date":BAD_DAY,
       "suspect_pre2026_gt15pct_gold_moves":changes,
       "training_cutoff":TRAIN_CUTOFF,"model":MODEL_ID,
       "end_of_us_options_close_issue":True}
    payload["sha256"]=sha(payload)
    Path(outfile).write_text(json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n")
    print("FRAGILITY_SOURCE_AUDIT",json.dumps({"gvz_n":len(gvz),"aligned_price_n":len(panel),
      "gvz_sha256":payload["gvz_csv_sha256"],"panel_sha256":payload["sha256"],
      "pre2026_gold_gt15pct":changes,"GVZ_JAN29":gvz["2026-01-29"]}),flush=True)

def rsi14(v):
    x=np.diff(np.log(v[-15:]))
    up=np.maximum(0,x).mean();down=np.maximum(0,-x).mean()
    return 100.0 if down<1e-12 else 100*up/(up+down)

def build(s):
    gate(s["source"]=="OFFICIAL_CBOE_GVZ_AND_PINNED_STAKTRAKR_RESEARCH_PRICE","SRC_WRONG")
    digest=s.pop("sha256");gate(digest==sha(s),"SOURCE_CHANGED");s["sha256"]=digest
    dates=[p["date"] for p in s["prices"]]
    P=np.asarray([p["four_prices"] for p in s["prices"]],float)
    gate(np.isfinite(P).all() and P.min()>0 and P.shape==(len(dates),4),"PRICE_BAD")
    L=np.log(P)
    gvz=s["gvz"];gd=sorted(gvz)
    # locate the newest GVZ close by the day after it is complete; do not use any future date.
    gvindex=0
    dataset=[]
    for i in range(260,len(dates)-5):
        d=dates[i]
        if d>STRESS_END:break
        # All test horizons through 2026-02-19 avoid notorious 2026-02-27 source row.
        if d>=BAD_DAY or any(v==BAD_DAY for v in dates[i+1:i+6]):continue
        while gvindex+1<len(gd) and gd[gvindex+1]<=d:gvindex+=1
        gdt=gd[gvindex]
        if (date.fromisoformat(d)-date.fromisoformat(gdt)).days>4:continue
        histgv=[gvz[x] for x in gd[max(0,gvindex-254):gvindex+1]]
        if len(histgv)<253:continue
        gh=np.array(histgv,dtype=float)
        gold=L[:,0];silver=L[:,1]
        rv5=float(np.sqrt(np.mean(np.diff(gold[i-5:i+1])**2)))
        rv20=float(np.sqrt(np.mean(np.diff(gold[i-20:i+1])**2)))
        goldret5=L[i,0]-L[i-5,0]
        sr5=L[i,1]-L[i-5,1]
        fx=[
          float(gold[i]-gold[i-1]),
          float(goldret5),
          float(gold[i]-gold[i-20]),
          float(rsi14(P[i-14:i+1,0]))/100.0,
          float(P[i,0]/P[i-19:i+1,0].mean()-1),
          float(P[i,0]/P[i-19:i+1,0].max()-1),
          rv5,rv20,
          float(silver[i]-silver[i-1]),float(sr5),
          float(np.sqrt(np.mean(np.diff(silver[i-5:i+1])**2))),
          float(np.std(L[i]-L[i-5])),
          float(gh[-1]),float((gh[-1]-gh[-253:-1].mean())/max(gh[-253:-1].std(),1e-8)),
          float(np.log(gh[-1]/gh[-6])),float(np.log(gh[-1]/gh[-2]))
        ]
        nextret=float(P[i+1,0]/P[i,0]-1)
        dd5=float(np.min(P[i+1:i+6,0]/P[i,0]-1))
        flags={"DROP_1D_3PCT":bool(nextret<=-0.03),
               "DRAWDOWN_NEXT5D_5PCT":bool(dd5<=-0.05),
               "MOVE_1D_3PCT":bool(abs(nextret)>=0.03)}
        dataset.append({"date":d,"next_target_date":dates[i+1],"h5_matures":dates[i+5],
          "gvz_date":gdt,"x":fx,"events":flags,
          "xau_level":float(P[i,0]),"next_return_pct":100*nextret,
          "min_next5_day_return_pct":100*dd5})
    gate(len(dataset)>2500,"TOO_FEW_SIGNAL_TRAIN_DAYS")
    gate(all(r["h5_matures"]>r["date"] and r["gvz_date"]<=r["date"] for r in dataset),"FUTURE_INPUT_DATED")
    gate(any(r["date"]=="2026-01-29" for r in dataset),"JAN29_MISSING")
    gate(any(r["date"]=="2026-01-28" for r in dataset),"JAN28_MISSING")
    return dataset

def confusion(rows,key):
    flagged=[r for r in rows if r[key]["warn"]]
    y=[r["events"][key] for r in rows]
    TP=sum(r["events"][key] for r in flagged)
    FN=sum(y)-TP
    FP=len(flagged)-TP
    TN=len(rows)-TP-FN-FP
    return {"origins":len(rows),"events":sum(y),"alerts":len(flagged),
      "TP":TP,"FP":FP,"FN":FN,"TN":TN,
      "recall":(TP/sum(y) if sum(y)>0 else None),
      "precision":(TP/len(flagged) if flagged else None),
      "alert_rate":len(flagged)/len(rows),
      "false_alarms_per_100_origin_days":100*FP/len(rows)}

def run(s,out):
    D=build(s)
    # Completed future-five-day labels only, *not* arbitrary origin dates.
    train=[r for r in D if r["h5_matures"]<=TRAIN_CUTOFF]
    valid=[r for r in D if VALID_START<=r["date"]<=VALID_END]
    test=[r for r in D if TEST_START<=r["date"]<=TEST_END]
    stress=[r for r in D if STRESS_START<=r["date"]<=STRESS_END]
    gate(len(train)>TRAIN_MIN and len(valid)>200 and len(test)>200 and len(stress)>=30,"SPLIT_UNEXPECTED")
    gate(max(x["h5_matures"] for x in train)<=TRAIN_CUTOFF,"TRAIN_TARGET_AFTER_CUTOFF")
    gate(min(x["date"] for x in valid)>max(x["date"] for x in train),"TRAIN_OVERLAPS_VALID")
    Xtr=np.asarray([r["x"] for r in train],float)
    gate(Xtr.shape[1]==len(FEATURES),"FEATURE_COUNT_CHANGED")
    buckets={"VALID_2024":valid,"TEST_2025":test,"STRESS_JAN_FEB2026":stress}
    allscores={}
    for family,indices in VARIANTS.items():
        scaler=StandardScaler().fit(Xtr[:,indices])
        A=scaler.transform(Xtr[:,indices])
        gate(np.isfinite(A).all(),"TRAIN_SCALE_NOT_FINITE")
        bytarget={}
        for target in TARGETS:
            Y=np.asarray([int(r["events"][target]) for r in train],int)
            gate(Y.min()==0 and Y.max()==1 and Y.sum()>=8,"NOT_ENOUGH_HISTORIC_SHOCKS_"+target)
            clf=LogisticRegression(C=.25,penalty="l2",solver="lbfgs",
              class_weight="balanced",max_iter=1500,random_state=1701)
            clf.fit(A,Y)
            train_scores=clf.decision_function(A)
            threshold=float(np.quantile(train_scores,1-ALERT_BUDGET))
            pred={}
            for name,subset in buckets.items():
                inputX=np.asarray([r["x"] for r in subset],float)[:,indices]
                scores=clf.decision_function(scaler.transform(inputX))
                rows=[]
                for r,v in zip(subset,scores):
                    row={"date":r["date"],"issue_after_options_close":True,
                         "gvz_used_from_date":r["gvz_date"],"event":r["events"][target],
                         "score":float(v),"warn":bool(v>=threshold)}
                    rows.append(row)
                n=len(rows);evt=sum(r["event"] for r in rows);warn=sum(r["warn"] for r in rows)
                TP=sum(r["warn"] and r["event"] for r in rows)
                prc=float(average_precision_score([r["event"] for r in rows],[r["score"] for r in rows])) if evt else None
                auc=float(roc_auc_score([r["event"] for r in rows],[r["score"] for r in rows])) if 0<evt<n else None
                pred[name]={"n":n,"events":evt,"warn":warn,"true_positives":TP,
                  "false_alarms":warn-TP,"misses":evt-TP,
                  "recall":TP/evt if evt else None,"precision":TP/warn if warn else None,
                  "alert_rate":warn/n,"average_precision":prc,"roc_auc":auc}
            bytarget[target]={"train_events":int(Y.sum()),"train_rows":len(train),
              "threshold_train_top10pct":threshold,"model":PARAMS,"splits":pred}
        allscores[family]=bytarget
    # exact date-by-date risk outputs, with labels, for audit and discovery.
    detailed=[]
    models={}
    for family,indices in VARIANTS.items():
        scale=StandardScaler().fit(Xtr[:,indices])
        X=scale.transform(Xtr[:,indices])
        models[family]={}
        for target in TARGETS:
            Y=np.array([int(r["events"][target]) for r in train])
            clf=LogisticRegression(C=.25,penalty="l2",solver="lbfgs",
              class_weight="balanced",max_iter=1500,random_state=1701).fit(X,Y)
            threshold=allscores[family][target]["threshold_train_top10pct"]
            models[family][target]=(scale,clf,indices,threshold)
    for row in valid+test+stress:
        scores={}
        for family,targets in models.items():
            scores[family]={}
            for target,(scale,clf,indices,threshold) in targets.items():
                v=float(clf.decision_function(scale.transform(np.array(row["x"])[indices][None,:]))[0])
                scores[family][target]={"score":v,"alert":bool(v>=threshold)}
        detailed.append({
          "origin":row["date"],"target_next_quote_date":row["next_target_date"],
          "five_day_target_matures":row["h5_matures"],"gvz_obs_date":row["gvz_date"],
          "gvz":row["x"][12],"gvz_z252":row["x"][13],
          "gvz_5d_return_pct":100*(math.exp(row["x"][14])-1),
          "gold_rsi14_proxy":row["x"][3]*100,
          "gold_ma20_distance_pct":row["x"][4]*100,
          "gold_prev1_pct":100*math.expm1(row["x"][0]),
          "xau_level":row["xau_level"],"next_day_return_pct":row["next_return_pct"],
          "next5d_min_return_pct":row["min_next5_day_return_pct"],
          "actual_events":row["events"],"risk_scores":scores,
        })
    report={"model":MODEL_ID,"source_snapshot_sha":s["sha256"],"source_firstprint_proven":False,
      "status":"FRAGILITY_RESEARCH_EXPERIMENT_FINISHED_NOT_PRODUCTION_VALIDATED",
      "fit_end":"2023-12-29 horizon-matured","development_2024_used_to_select_model":False,
      "model_family":"frozen logistic balanced standardized, ranking uncalibrated",
      "alert_rule":"train history (2010-2023) 90th percentile risk rank; 10 percent TRAIN alert budget only",
      "not_used_as_training":"CME SILVER MARGIN HISTORY incomplete; analyst RSI90.89 not original point-price series",
      "source_limitation":"FRED archived current snapshot not original real-time vintage; same-day end options close issue; StakTrakr historical research data not firstprint",
      "bad_2026_day":BAD_DAY,
      "labels":TARGETS,"feature_names":FEATURES,
      "splits":{"train_n":len(train),"validation_2024_n":len(valid),"test_2025_n":len(test),
                "stress_2026_Jan_to_Feb19_n":len(stress)},
      "models":allscores,"daily_scores":detailed}
    Path(out).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    for family,targets in allscores.items():
        for target,obj in targets.items():
            print("FRAGILITY_FROZEN_TEST",family,target, "train_events",obj["train_events"],
              "2024",json.dumps(obj["splits"]["VALID_2024"],sort_keys=True),
              "2025",json.dumps(obj["splits"]["TEST_2025"],sort_keys=True),
              "2026",json.dumps(obj["splits"]["STRESS_JAN_FEB2026"],sort_keys=True),flush=True)
    for day in ("2026-01-22","2026-01-26","2026-01-27","2026-01-28","2026-01-29",
                "2026-01-30","2026-02-02","2026-02-03"):
        r=next((v for v in detailed if v["origin"]==day),None)
        if r:
            print("FRAGILITY_EVENT_ORIGIN",json.dumps(r,sort_keys=True),flush=True)
    print("FRAGILITY_RESEARCH_SCORE_DONE",len(train),len(valid),len(test),len(stress),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("source","score"))
    p.add_argument("--gvz_csv")
    p.add_argument("--snapshot")
    p.add_argument("--out",required=True)
    args=p.parse_args()
    if args.mode=="source":return source_extract(args.out,args.gvz_csv)
    s=json.loads(Path(args.snapshot).read_text())
    return run(s,args.out)
if __name__=="__main__":main()
