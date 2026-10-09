"""Bounded user-authorized free/quota-only historical EURUSD/USDJPY H1 signed experiment.
Never persist/reveal vendor FX quotes, private secrets, user data or licensed rows.
Historical model comparison is NON-CANONICAL because GitHub LIT label differs from
newly governed EV DUKA by five of 589 regular matched 2023–25 overnight labels.
"""
from __future__ import annotations
import csv,datetime as dt,json,math,os,time,urllib.parse,urllib.request,urllib.error
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"GOLD_R4_FX2_EURJPY_HISTORY_2023_2025_RETRO_RESULTS_20261009.json"
HIST=ROOT/"GOLD_EXECUTION_LIT_STAGE1_PREDICTIONS_2026-10-07.csv"
PAIRS=("EUR/USD","USD/JPY")
WINDOWS=[(f"{yr}-{a}-01T00:00:00",f"{yr}-{b}-01T00:00:00")
         for yr in (2023,2024,2025) for a,b in (("01","07"),("07","01"))]
# IMPORTANT annual end year correction: (year July1 through NEXT year Jan1)
WINDOWS=[(f"{yr}-01-01T00:00:00",f"{yr}-07-01T00:00:00") for yr in (2023,2024,2025)]+[
         (f"{yr}-07-01T00:00:00",f"{yr+1}-01-01T00:00:00") for yr in (2023,2024,2025)]
WINDOWS.sort()
IST=ZoneInfo("Europe/Istanbul")
def metrics(rows,key):
    tp=fp=fn=tn=0
    for z in rows:
        y=z["y"];p=z[key]
        if p==-1 and y==-1:tp+=1
        elif p==-1:fp+=1
        elif y==-1:fn+=1
        else:tn+=1
    n=tp+fp+fn+tn
    if n==0:return {"N":0}
    return {"N":n,"accuracy_pct":round(100*(tp+tn)/n,2),
            "BA_pct":round(50*(tp/(tp+fn) if tp+fn else 0)+50*(tn/(tn+fp) if tn+fp else 0),2),
            "DOWN_recall_pct":round(100*tp/(tp+fn),2) if tp+fn else None,
            "DOWN_precision_pct":round(100*tp/(tp+fp),2) if tp+fp else None,
            "tp":tp,"fp":fp,"fn":fn,"tn":tn}
def mcnemar(a,b):
    n=a+b
    if not n:return 1.0
    term=.5**n;p=term
    for k in range(1,min(a,b)+1):
        term *= (n-k+1)/k;p+=term
    return round(min(1,2*p),6)
def read_baselines():
    if not HIST.exists():raise RuntimeError("LOCKED_LEGACY_LIT_PREDICTION_FILE_MISSING")
    out=[]
    with HIST.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            spec=row.get("spec");d=row.get("date","")
            if spec not in ("LIT_OVN0_1530_1600","LIT_DAY0_EXEC_0900") or not d:continue
            date=dt.date.fromisoformat(d)
            w="OVN" if spec.startswith("LIT_OVN") else "DAY"
            if w=="OVN" and date.weekday()>=4:continue
            if date.weekday()>=5:continue
            y=1 if int(row["actual_y"])==1 else -1
            base=1 if int(row["pred_logit"])==1 else -1
            out.append({"date":d,"year":date.year,"w":w,"y":y,"B":base})
    return out
def fetch_one(symbol,start,end,key):
    params={"symbol":symbol,"interval":"1h","timezone":"UTC","start_date":start,
             "end_date":end,"outputsize":5000,"format":"JSON"}
    req=urllib.request.Request(
      "https://api.twelvedata.com/time_series?"+urllib.parse.urlencode(params),
      headers={"Authorization":"apikey "+key,"Accept":"application/json",
               "User-Agent":"GoldControl-IndependentFXR4/1.0"})
    with urllib.request.urlopen(req,timeout=42) as rsp:
        obj=json.loads(rsp.read(1400000).decode("utf-8"))
    if obj.get("status")=="error":
        raise RuntimeError("FX_PROVIDER_ERROR_CODE_"+str(obj.get("code","UNKNOWN")))
    if (obj.get("meta") or {}).get("symbol")!=symbol:
        raise RuntimeError("FX_PROVIDER_IDENTITY_MISMATCH")
    result={}
    for row in obj.get("values") or []:
        stamp=dt.datetime.strptime(row["datetime"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
        val=float(row["close"])
        if not math.isfinite(val) or not val>0:continue
        if stamp in result and abs(result[stamp]-val)>1e-10:
            raise RuntimeError("FX_DUPLICATE_HOURLY_SOURCE_CONFLICT")
        result[stamp]=val
    if len(result)<500:
        raise RuntimeError("FX_HISTORY_WINDOW_TOO_SHORT_"+str(len(result)))
    return result

def execute():
    receipt={"asof_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "status":"NOT_RUN","calls_attempted":0,"calls_max":12,
       "provider":"Twelve Data",
       "pair_symbols":PAIRS,"source_interval":"1h","timezone":"UTC",
       "labels":"legacy_LIT_STAGE1_not_latest_private_DUKA_canonical",
       "known_label_mismatch_legacy_vs_new_canonical":"5 of 589 matched regular overnight 2023-25 nights",
       "2025_retrospective_inspected":True,
       "historical_PIT_first_seen_from_2026_only":True,
       "FX_quotes_stored":False,"FX_quotes_redistributed":False,
       "provider_secret_logged":False,
       "no_paid_plan_upgrade_or_background_runs":True,
       "no_bank_trades":True,"source_windows":[],"metrics":[]}
    key=os.getenv("TWELVE_DATA_API_KEY","").strip()
    if not key:receipt["status"]="SOURCE_BLOCKED_NO_SECRET";return receipt
    baselines=read_baselines()
    if not baselines:receipt["status"]="SOURCE_BLOCKED_NO_BASELINES";return receipt
    px={pair:{} for pair in PAIRS}
    for year in (2023,2024,2025):
        for first,last in ((f"{year}-01-01T00:00:00",f"{year}-07-01T00:00:00"),
                           (f"{year}-07-01T00:00:00",f"{year+1}-01-01T00:00:00")):
            for pair in PAIRS:
                if receipt["calls_attempted"]>=12:
                    raise RuntimeError("CALL_CAP_REACHED")
                if receipt["calls_attempted"]:time.sleep(8.2)
                receipt["calls_attempted"]+=1
                try:
                    data=fetch_one(pair,first,last,key)
                except urllib.error.HTTPError as exc:
                    raise RuntimeError("FX_HTTP_"+str(exc.code)) from None
                except (urllib.error.URLError,TimeoutError) as exc:
                    raise RuntimeError("FX_NETWORK_"+type(exc).__name__) from None
                duplicates=0
                for k,v in data.items():
                    if k in px[pair]:
                        duplicates+=1
                        if abs(px[pair][k]-v)>1e-10:raise RuntimeError("FX_ADJACENT_CHUNK_CONFLICT")
                    px[pair][k]=v
                receipt["source_windows"].append({
                    "pair":pair,"start":first,"end":last,"hourly_observations":len(data),
                    "overlap_rows":duplicates,
                    "first_observed_UTC":min(data).isoformat(),
                    "last_observed_UTC":max(data).isoformat()
                })
    qualified=[];missing=defaultdict(int)
    for row in baselines:
        d=dt.date.fromisoformat(row["date"])
        window=row["w"]
        # Hour starts local 06 and 07 for DAY, 14 and 15 for OVN.
        base=6 if window=="DAY" else 14
        stamps=[dt.datetime.combine(d,dt.time(h,0),IST).astimezone(dt.timezone.utc)
                for h in (base,base+1)]
        dec={}
        for pair in PAIRS:
            a=px[pair].get(stamps[0]);b=px[pair].get(stamps[1])
            if not (a is not None and b is not None and a>0 and b>0):
                missing[window+":"+str(row["year"])]+=1
                dec={};break
            rr=math.log(b/a)
            if not math.isfinite(rr) or abs(rr)>0.1:
                missing[window+":"+str(row["year"])]+=1;dec={};break
            dec[pair]=(1 if rr>0 else -1 if rr<0 else 0)
        if len(dec)!=2:continue
        # BOTH signal gold UP if EURUSD grows and USDJPY falls.
        e=dec["EUR/USD"];j=-dec["USD/JPY"]
        agree=(e!=0 and e==j)
        qualified.append({**row,"agree":agree,"FX":e if agree else None,
                          "HYBRID":e if agree else row["B"]})
    for window in ("DAY","OVN"):
        for year in (2023,2024,2025):
            arr=[x for x in qualified if x["w"]==window and x["year"]==year]
            agree=[x for x in arr if x["agree"]]
            before=[x for x in baselines if x["w"]==window and x["year"]==year]
            if not arr:continue
            res={"target":window,"year":year,"eligible_LIT_dates":len(before),
              "FX_H1_source_ready":len(arr),
              "pair_agreement_calls":len(agree),
              "agreement_coverage_pct":round(100*len(agree)/len(before),2),
              "baseline_same_all":metrics(arr,"B"),
              "FX_overlay_full":metrics(arr,"HYBRID"),
              "baseline_on_FX_agree_only":metrics(agree,"B"),
              "FX_pair_on_same_agree_dates":metrics(agree,"FX")}
            rescues=breaks=0
            for z in arr:
                b=z["B"]==z["y"];a=z["HYBRID"]==z["y"]
                if a and not b:rescues+=1
                if b and not a:breaks+=1
            res.update(rescues=rescues,breaks=breaks,
                       paired_mcnemar_exact_p=mcnemar(rescues,breaks),
                       source_missing=missing[window+":"+str(year)])
            receipt["metrics"].append(res)
    receipt["status"]="COMPLETED_RETROSPECTIVE_NOT_CANONICAL"
    return receipt
def main():
    try:result=execute()
    except Exception as exc:
        why=str(exc)
        if len(why)>90:why=type(exc).__name__
        result={"status":"SOURCE_OR_EXECUTION_BLOCKED","safe_error":why,
           "no_raw_vendor_quotes_committed":True}
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("FX2_RESEARCH_STATUS",result["status"],
          "requests",result.get("calls_attempted","UNKNOWN"),
          "metric_groups",len(result.get("metrics",[])),flush=True)
    if result.get("metrics"):
        for row in result["metrics"]:
            print("FX2_METRIC",row["target"],row["year"],
              "source",row["FX_H1_source_ready"],
              "agree",row["pair_agreement_calls"],
              "base_BA",row["baseline_same_all"]["BA_pct"],
              "overlay_BA",row["FX_overlay_full"]["BA_pct"],
              "rescue/break",row["rescues"],row["breaks"],flush=True)
    return 0 if result["status"]=="COMPLETED_RETROSPECTIVE_NOT_CANONICAL" else 1
if __name__=="__main__":
    raise SystemExit(main())
