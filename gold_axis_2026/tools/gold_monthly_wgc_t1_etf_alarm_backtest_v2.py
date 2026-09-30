from __future__ import annotations
import argparse, json, re, time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE="https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/{year}/{month:02d}"
UA={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/2.0","Accept":"text/html,application/xhtml+xml"}
START_PAGE="2019-01"
END_PAGE="2026-08"
EVAL_START="2021-11"
EVAL_END="2026-08"
MIN_HISTORY=24

def mshift(ym,delta):
    y,m=map(int,ym.split("-"))
    q=y*12+(m-1)+delta
    return f"{q//12:04d}-{q%12+1:02d}"

def month_range(a,b):
    out=[]; cur=a
    while cur<=b:
        out.append(cur); cur=mshift(cur,1)
    return out

def norm(s):
    return re.sub(r"\s+"," ",s.replace("\xa0"," ")).strip()

def valid_level(x):
    return x is not None and 1000.0 <= float(x) <= 6000.0

def parse_holdings_level(text):
    t=norm(text)
    p=t.lower().find("published:")
    x=t[p:p+7500] if p>=0 else t[:7500]
    candidates=[]

    pats=[
      (r"collective(?:\s+global)?\s+(?:gold ETF\s+)?holdings[^.]{0,150}?(?:stood at|stand at|reached|rose to|increased to|grew to|fell to|declined to|dropped to|decreased to|bounced to|rebounded to|to)\s+([1-5]\d{0,1}(?:,\d{3})?(?:\.\d+)?)\s*t\b",0.999,"collective_holdings_level"),
      (r"total(?:\s+global)?\s+holdings[^.]{0,150}?(?:stood at|stand at|reached|rose to|increased to|grew to|fell to|declined to|dropped to|decreased to|bounced to|rebounded to|at|to)\s+([1-5]\d{0,1}(?:,\d{3})?(?:\.\d+)?)\s*t\b",0.998,"total_holdings_level"),
      (r"global\s+(?:gold ETF\s+)?holdings[^.]{0,150}?(?:stood at|stand at|reached|rose to|increased to|grew to|fell to|declined to|dropped to|decreased to|bounced to|rebounded to|at|to)\s+([1-5]\d{0,1}(?:,\d{3})?(?:\.\d+)?)\s*t\b",0.997,"global_holdings_level"),
      (r"holdings[^.]{0,100}?(?:now\s+)?(?:stood at|stand at|reached|ended at|at)\s+([1-5]\d{0,1}(?:,\d{3})?(?:\.\d+)?)\s*t\b",0.985,"holdings_level"),
    ]
    for pat,conf,kind in pats:
        for m in re.finditer(pat,x,re.I):
            val=float(m.group(1).replace(",",""))
            if not valid_level(val): continue
            snip=norm(x[max(0,m.start()-120):min(len(x),m.end()+160)])
            candidates.append((conf,val,snip,kind,m.start()))

    # Fallback: sentence contains holdings and a plausible 1,000-6,000t level.
    for sm in re.finditer(r"[^.!?]{0,220}holdings[^.!?]{0,260}[.!?]",x,re.I):
        sent=norm(sm.group(0))
        nums=[]
        for nm in re.finditer(r"([1-5]\d{0,1}(?:,\d{3})?(?:\.\d+)?)\s*t\b",sent,re.I):
            val=float(nm.group(1).replace(",",""))
            if valid_level(val): nums.append((nm.start(),val))
        if not nums: continue
        low=sent.lower()
        # Avoid sentences that are purely historical-record comparisons when possible.
        if any(w in low for w in ["record of","record set","all-time high of","peak in"]) and not any(w in low for w in ["current","end of","by the end","now","stood","total","collective"]):
            continue
        pos,val=nums[0]
        candidates.append((0.86,val,sent,"fallback_holdings_sentence",sm.start()+pos))

    if not candidates:
        return None,None,None
    candidates.sort(key=lambda z:(-z[0],z[4]))
    conf,val,snip,kind,_=candidates[0]
    return val,conf,{"kind":kind,"snippet":snip,"n_candidates":len(candidates)}

def fetch_page(ym):
    y,m=map(int,ym.split("-"))
    url=BASE.format(year=y,month=m)
    r=requests.get(url,headers=UA,timeout=60)
    if r.status_code!=200:
        return {"page_month":ym,"data_month":mshift(ym,-1),"url":url,"status":r.status_code}
    soup=BeautifulSoup(r.text,"html.parser")
    text=norm(soup.get_text(" ",strip=True))
    pm=re.search(r"Published:\s*(\d{1,2}\s+[A-Za-z]+,\s+\d{4})",text,re.I)
    pub=datetime.strptime(pm.group(1),"%d %B, %Y").date().isoformat() if pm else None
    h,conf,detail=parse_holdings_level(text)
    return {
      "page_month":ym,"data_month":mshift(ym,-1),"url":url,"status":200,
      "publication_date":pub,"holdings_t":h,"holdings_parse_confidence":conf,
      "holdings_parse_detail":detail,
      "title":soup.title.get_text(" ",strip=True) if soup.title else ""
    }

def load_severity(path):
    j=json.loads(Path(path).read_text())
    if j.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30":
        raise RuntimeError(("BAD_SEVERITY_SCHEMA",j.get("schema")))
    return {r["target"]:r for r in j["rows"]}

def score(rows,flag,timely=False):
    z=[r for r in rows if r.get("severity")]
    ev=[r for r in z if r.get(flag) and (not timely or r.get("TIMELY_T1"))]
    hi=[r for r in z if r["severity"]=="HIGH"]
    elevated=[r for r in z if r["severity"] in ("MEDIUM","HIGH")]
    hh=[r for r in ev if r["severity"]=="HIGH"]
    eh=[r for r in ev if r["severity"] in ("MEDIUM","HIGH")]
    return {
      "events":len(ev),"event_targets":[r["page_month"] for r in ev],
      "high_n":len(hi),"high_hits":len(hh),"high_hit_targets":[r["page_month"] for r in hh],
      "high_precision":None if not ev else len(hh)/len(ev),
      "high_recall":None if not hi else len(hh)/len(hi),
      "elevated_n":len(elevated),"elevated_hits":len(eh),
      "elevated_hit_targets":[r["page_month"] for r in eh],
      "elevated_precision":None if not ev else len(eh)/len(ev),
      "elevated_recall":None if not elevated else len(eh)/len(elevated),
      "normal_false_alarm_targets":[r["page_month"] for r in ev if r["severity"]=="NORMAL"],
      "medium_hit_targets":[r["page_month"] for r in ev if r["severity"]=="MEDIUM"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    severity=load_severity(a.severity)

    raw=[]
    for ym in month_range(START_PAGE,END_PAGE):
        raw.append(fetch_page(ym))
        time.sleep(.04)

    # Valid report rows by data month.
    parsed=[r for r in raw if r.get("publication_date") and valid_level(r.get("holdings_t"))]
    by_data={r["data_month"]:r for r in parsed}
    for dm,r in sorted(by_data.items()):
        p=by_data.get(mshift(dm,-1))
        r["prev_holdings_t"]=None if p is None else float(p["holdings_t"])
        r["demand_t"]=None if p is None else float(r["holdings_t"]-p["holdings_t"])
    for dm,r in sorted(by_data.items()):
        p=by_data.get(mshift(dm,-1))
        r["prev_demand_t"]=None if p is None else p.get("demand_t")
        r["delta_demand_t"]=None if p is None or p.get("demand_t") is None or r.get("demand_t") is None else float(r["demand_t"]-p["demand_t"])

    rows=sorted(parsed,key=lambda r:r["publication_date"])
    for r in rows:
        hist=[x["delta_demand_t"] for x in rows if x["publication_date"]<r["publication_date"] and x.get("delta_demand_t") is not None]
        r["r1_history_n"]=len(hist)
        r["r1_prior_q10_t"]=None if len(hist)<MIN_HISTORY else float(pd.Series(hist).quantile(.10))
        r["R1"]=bool(r["r1_prior_q10_t"] is not None and r.get("delta_demand_t") is not None and r["delta_demand_t"]<=r["r1_prior_q10_t"])
        r["R2"]=bool(r.get("demand_t") is not None and r.get("prev_demand_t") is not None and r["demand_t"]<0 and r["prev_demand_t"]<0)
        r["T1_ANY"]=bool(r["R1"] or r["R2"])
        ts=pd.Timestamp(r["publication_date"])
        r["publication_matches_target_month"]=bool(ts.strftime("%Y-%m")==r["page_month"])
        r["publish_day"]=int(ts.day)
        r["TIMELY_T1"]=bool(r["publication_matches_target_month"] and r["publish_day"]<=10)
        s=severity.get(r["page_month"])
        if s:
            r["ape_pct"]=float(s["ape_pct"]); r["severity"]=s["ape_severity"]; r["ABCDH"]=bool(s["ABCDH"])
        else:
            r["ape_pct"]=None; r["severity"]=None; r["ABCDH"]=None

    coverage=len(parsed)/len(raw)
    eval_expected=month_range(EVAL_START,EVAL_END)
    eval_rows=[r for r in rows if EVAL_START<=r["page_month"]<=EVAL_END and r.get("severity")]
    have={r["page_month"] for r in eval_rows}
    missing_eval=[m for m in eval_expected if m not in have]

    metrics_all={f:score(eval_rows,f,False) for f in ["R1","R2","T1_ANY"]}
    metrics_timely={f:score(eval_rows,f,True) for f in ["R1","R2","T1_ANY"]}

    core_targets=["2022-05","2022-07","2022-09","2024-03"]
    core=[]
    for t in core_targets:
        r=next((x for x in eval_rows if x["page_month"]==t),None)
        core.append(None if r is None else {k:r.get(k) for k in [
          "page_month","data_month","publication_date","publish_day","holdings_t","prev_holdings_t",
          "demand_t","prev_demand_t","delta_demand_t","r1_prior_q10_t","R1","R2","T1_ANY","TIMELY_T1",
          "ape_pct","severity","ABCDH","holdings_parse_confidence","holdings_parse_detail"
        ]})

    t0_misses=[r for r in eval_rows if r["severity"]=="HIGH" and not r["ABCDH"]]
    rescued=[r["page_month"] for r in t0_misses if r["T1_ANY"]]
    remaining=[r["page_month"] for r in t0_misses if not r["T1_ANY"]]

    status="COMPLETE" if coverage>=.90 and not missing_eval and all(r["publication_matches_target_month"] for r in eval_rows) else "INCOMPLETE"
    out={
      "schema":"GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V2_2026-09-30",
      "status":status,
      "parser_coverage":{"pages":len(raw),"parsed":len(parsed),"coverage":coverage,"missing_eval":missing_eval},
      "rows":rows,"raw_page_status":raw,
      "metrics_all":metrics_all,"metrics_timely":metrics_timely,
      "core_rows":core,
      "t0_high_miss_targets":[r["page_month"] for r in t0_misses],
      "t1_detected_previous_T0_high_misses":rescued,
      "remaining_high_after_T0_ABCDH_and_T1_ANY":remaining,
      "governance":{
        "forecast_modified":False,"routing_tested":False,
        "holdings_change_used_as_wgc_demand":True,
        "rolling_pit_r1":True,"r2_fixed_two_negative_months":True,
        "t1_any_frozen_pre_outcome":True,"severity_ape_v3":True,
        "target_month_market_data_used":False,
      }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE="+("PASS" if status=="COMPLETE" else "FAIL"))
    print(json.dumps({
      "parser_coverage":out["parser_coverage"],
      "metrics_all":metrics_all,"metrics_timely":metrics_timely,
      "core":core,"rescued":rescued,"remaining":remaining,
      "low_confidence":[{"page_month":r["page_month"],"holdings_t":r["holdings_t"],"conf":r["holdings_parse_confidence"],
                         "snippet":r["holdings_parse_detail"]["snippet"] if r.get("holdings_parse_detail") else None}
                        for r in rows if (r.get("holdings_parse_confidence") or 0)<.95]
    },sort_keys=True))

if __name__=="__main__":
    main()
