from __future__ import annotations
import argparse, json, math, re, time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE="https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/{year}/{month:02d}"
UA={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/1.0","Accept":"text/html,application/xhtml+xml"}
START_PAGE="2019-01"
END_PAGE="2026-08"
EVAL_START="2021-11"
EVAL_END="2026-08"
MIN_HISTORY=24

MONTHS={m.lower():i for i,m in enumerate([
    "January","February","March","April","May","June","July","August","September","October","November","December"
],1)}

def mshift(ym,delta):
    y,m=map(int,ym.split("-"))
    q=y*12+(m-1)+delta
    return f"{q//12:04d}-{q%12+1:02d}"

def months(a,b):
    out=[]; cur=a
    while cur<=b:
        out.append(cur); cur=mshift(cur,1)
    return out

def normalize_text(s):
    return re.sub(r"\s+"," ",s.replace("\xa0"," ")).strip()

def signed_from_phrase(num, direction):
    x=float(num.replace(",",""))
    return x if direction.lower().startswith("inflow") else -x

def parse_flow(text, expected_data_month):
    t=normalize_text(text)
    # Focus on early article content; avoid later historical references where possible.
    pubpos=t.lower().find("published:")
    x=t[pubpos:pubpos+6500] if pubpos>=0 else t[:6500]
    mm=int(expected_data_month.split("-")[1])
    mname=list(MONTHS.keys())[mm-1].capitalize()

    candidates=[]

    # Highest confidence: explicit Global ... signed tonne parenthetical.
    for pat in [
        r"Global[^.]{0,220}?\(([-+]\d+(?:\.\d+)?)\s*t(?:,|\))",
        r"Global[^.]{0,220}?(?:holdings|demand)[^.]{0,120}?\(([-+]\d+(?:\.\d+)?)\s*t(?:,|\))",
    ]:
        for m in re.finditer(pat,x,re.I):
            val=float(m.group(1))
            snip=x[max(0,m.start()-80):min(len(x),m.end()+140)]
            candidates.append((0.99,val,normalize_text(snip),"global_signed_parenthetical"))

    # Explicit global phrase: amount then direction.
    patterns_amount_direction=[
        r"Global[^.]{0,180}?(?:registered|recorded|saw|posted|experienced|had)\s+([\d,.]+)\s*t(?:onnes?)?[^.]{0,80}?of\s+(inflows?|outflows?)",
        r"Global[^.]{0,180}?([\d,.]+)\s*t(?:onnes?)?[^.]{0,100}?(inflows?|outflows?)",
    ]
    for pat in patterns_amount_direction:
        for m in re.finditer(pat,x,re.I):
            val=signed_from_phrase(m.group(1),m.group(2))
            snip=x[max(0,m.start()-80):min(len(x),m.end()+140)]
            candidates.append((0.96,val,normalize_text(snip),"global_amount_direction"))

    # Direction then amount.
    for pat in [
        r"Global[^.]{0,180}?(inflows?|outflows?)[^.]{0,100}?([\d,.]+)\s*t(?:onnes?)?\b",
        r"Global[^.]{0,180}?(?:added|gained|increased by)\s+([\d,.]+)\s*t(?:onnes?)?\b",
        r"Global[^.]{0,180}?(?:lost|shed|fell by|decreased by|declined by)\s+([\d,.]+)\s*t(?:onnes?)?\b",
    ]:
        for m in re.finditer(pat,x,re.I):
            if len(m.groups())==2:
                val=signed_from_phrase(m.group(2),m.group(1))
                kind="global_direction_amount"
            else:
                num=float(m.group(1).replace(",",""))
                low=m.group(0).lower()
                val=-num if any(w in low for w in ["lost","shed","fell","decreased","declined"]) else num
                kind="global_verb_amount"
            snip=x[max(0,m.start()-80):min(len(x),m.end()+140)]
            candidates.append((0.94,val,normalize_text(snip),kind))

    # Older style: current-month intro followed by holdings decreased/increased.
    mon_pat=re.escape(mname)
    for pat,sgn in [
        (rf"(?:In\s+)?{mon_pat}[^.]{{0,260}}?holdings\s+(?:decreased|fell|declined)\s+by\s+([\d,.]+)\s+tonnes?",-1),
        (rf"(?:In\s+)?{mon_pat}[^.]{{0,260}}?holdings\s+(?:increased|rose|grew)\s+by\s+([\d,.]+)\s+tonnes?",1),
    ]:
        for m in re.finditer(pat,x,re.I):
            val=sgn*float(m.group(1).replace(",",""))
            snip=x[max(0,m.start()-80):min(len(x),m.end()+140)]
            candidates.append((0.90,val,normalize_text(snip),"month_holdings_change"))

    # Modern style signed tonnes anywhere in first relevant global paragraph.
    # Require 'global' and target month name in nearby sentence.
    sentences=re.split(r"(?<=[.!?])\s+",x)
    for sent in sentences[:45]:
        low=sent.lower()
        if "global" not in low and "gold etf" not in low: continue
        if mname.lower() not in low and "month" not in low: continue
        sm=re.search(r"\(([-+]\d+(?:\.\d+)?)\s*t(?:,|\))",sent,re.I)
        if sm:
            candidates.append((0.88,float(sm.group(1)),normalize_text(sent),"sentence_signed_t"))

    if not candidates:
        return None,None,None
    # Highest confidence; tie -> earliest appearance in x approximated by snippet location.
    candidates.sort(key=lambda z:z[0],reverse=True)
    conf,val,snip,kind=candidates[0]
    return val,conf,{"kind":kind,"snippet":snip,"n_candidates":len(candidates)}

def fetch_page(ym):
    y,m=map(int,ym.split("-"))
    url=BASE.format(year=y,month=m)
    r=requests.get(url,headers=UA,timeout=60)
    if r.status_code!=200:
        return {"page_month":ym,"url":url,"status":r.status_code,"ok":False}
    soup=BeautifulSoup(r.text,"html.parser")
    text=normalize_text(soup.get_text(" ",strip=True))
    pm=re.search(r"Published:\s*(\d{1,2}\s+[A-Za-z]+,\s+\d{4})",text,re.I)
    pub=None
    if pm:
        pub=datetime.strptime(pm.group(1),"%d %B, %Y").date().isoformat()
    expected_data=mshift(ym,-1)
    flow,conf,detail=parse_flow(text,expected_data)
    title=soup.title.get_text(" ",strip=True) if soup.title else ""
    return {
        "page_month":ym,"data_month":expected_data,"url":url,"status":200,"ok":True,
        "publication_date":pub,"global_flow_t":flow,"flow_parse_confidence":conf,
        "flow_parse_detail":detail,"title":title,
    }

def load_severity(path):
    j=json.loads(Path(path).read_text())
    if j.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30":
        raise RuntimeError(("BAD_SEVERITY_SCHEMA",j.get("schema")))
    return {r["target"]:r for r in j["rows"]}

def classify(rows,severity):
    valid=[r for r in rows if r.get("publication_date") and r.get("global_flow_t") is not None]
    valid.sort(key=lambda r:r["publication_date"])
    # compute historical flow delta chronologically by report data month order, not publication order
    by_data={r["data_month"]:r for r in valid}
    for dm,r in by_data.items():
        prev=by_data.get(mshift(dm,-1))
        r["prev_global_flow_t"]=None if prev is None else float(prev["global_flow_t"])
        r["flow_delta_t"]=None if prev is None else float(r["global_flow_t"]-prev["global_flow_t"])

    # PIT rolling Q10 based only on prior published reports (and their known deltas).
    for r in valid:
        pub=r["publication_date"]
        hist=[
            x["flow_delta_t"] for x in valid
            if x["publication_date"]<pub and x.get("flow_delta_t") is not None
        ]
        r["r1_history_n"]=len(hist)
        r["r1_prior_q10_t"]=None if len(hist)<MIN_HISTORY else float(pd.Series(hist).quantile(.10))
        r["R1"]=bool(r["r1_prior_q10_t"] is not None and r["flow_delta_t"] is not None and r["flow_delta_t"]<=r["r1_prior_q10_t"])
        r["R2"]=bool(r["global_flow_t"]<0 and r.get("prev_global_flow_t") is not None and r["prev_global_flow_t"]<0)
        r["T1_ANY"]=bool(r["R1"] or r["R2"])

        target=r["page_month"]
        # timing validity: publication must occur in target month
        pdte=pd.Timestamp(r["publication_date"])
        r["publication_matches_target_month"]=bool(pdte.strftime("%Y-%m")==target)
        r["publish_day"]=int(pdte.day)
        r["TIMELY_T1"]=bool(r["publication_matches_target_month"] and r["publish_day"]<=10)
        s=severity.get(target)
        if s:
            r["ape_pct"]=float(s["ape_pct"])
            r["severity"]=s["ape_severity"]
            r["ABCDH"]=bool(s["ABCDH"])
        else:
            r["ape_pct"]=None; r["severity"]=None; r["ABCDH"]=None
    return valid

def metrics(rows,flag,timely_only=False):
    z=[r for r in rows if r.get("severity") is not None]
    ev=[r for r in z if r.get(flag) and (not timely_only or r.get("TIMELY_T1"))]
    hi=[r for r in z if r["severity"]=="HIGH"]
    elev=[r for r in z if r["severity"] in ("MEDIUM","HIGH")]
    hh=[r for r in ev if r["severity"]=="HIGH"]
    eh=[r for r in ev if r["severity"] in ("MEDIUM","HIGH")]
    return {
        "events":len(ev),
        "event_targets":[r["page_month"] for r in ev],
        "high_n":len(hi),
        "high_hits":len(hh),
        "high_hit_targets":[r["page_month"] for r in hh],
        "high_precision":None if not ev else len(hh)/len(ev),
        "high_recall":None if not hi else len(hh)/len(hi),
        "elevated_n":len(elev),
        "elevated_hits":len(eh),
        "elevated_hit_targets":[r["page_month"] for r in eh],
        "elevated_precision":None if not ev else len(eh)/len(ev),
        "elevated_recall":None if not elev else len(eh)/len(elev),
        "false_alarm_normal_targets":[r["page_month"] for r in ev if r["severity"]=="NORMAL"],
        "medium_hit_targets":[r["page_month"] for r in ev if r["severity"]=="MEDIUM"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    severity=load_severity(a.severity)

    rows=[]
    for ym in months(START_PAGE,END_PAGE):
        rows.append(fetch_page(ym))
        time.sleep(0.05)

    ok=[r for r in rows if r.get("publication_date") and r.get("global_flow_t") is not None]
    coverage=len(ok)/len(rows)
    valid=classify(rows,severity)

    eval_rows=[r for r in valid if EVAL_START<=r["page_month"]<=EVAL_END and r.get("severity") is not None]
    expected_eval=months(EVAL_START,EVAL_END)
    parsed_eval={r["page_month"] for r in eval_rows}
    missing_eval=[m for m in expected_eval if m not in parsed_eval]

    metrics_all={f:metrics(eval_rows,f,False) for f in ["R1","R2","T1_ANY"]}
    metrics_timely={f:metrics(eval_rows,f,True) for f in ["R1","R2","T1_ANY"]}

    core_targets=["2022-05","2022-07","2022-09","2024-03"]
    core=[]
    for t in core_targets:
        rr=next((r for r in eval_rows if r["page_month"]==t),None)
        core.append(None if rr is None else {
            k:rr.get(k) for k in [
                "page_month","data_month","publication_date","publish_day","global_flow_t",
                "prev_global_flow_t","flow_delta_t","r1_prior_q10_t","R1","R2","T1_ANY","TIMELY_T1",
                "ape_pct","severity","ABCDH","flow_parse_confidence","flow_parse_detail"
            ]
        })

    remaining_high=[
        r["page_month"] for r in eval_rows
        if r["severity"]=="HIGH" and not bool(r["ABCDH"]) and not bool(r["T1_ANY"])
    ]
    rescued_t1=[
        r["page_month"] for r in eval_rows
        if r["severity"]=="HIGH" and not bool(r["ABCDH"]) and bool(r["T1_ANY"])
    ]

    out={
        "schema":"GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V1_2026-09-30",
        "status":"COMPLETE" if coverage>=.90 and not missing_eval else "INCOMPLETE",
        "source_window":[START_PAGE,END_PAGE],
        "evaluation_window":[EVAL_START,EVAL_END],
        "parser_coverage":{"pages":len(rows),"parsed":len(ok),"coverage":coverage,"missing_eval":missing_eval},
        "rows":valid,
        "raw_page_status":rows,
        "metrics_all":metrics_all,
        "metrics_timely":metrics_timely,
        "core_rows":core,
        "remaining_high_after_T0_ABCDH_and_T1_ANY":remaining_high,
        "t1_detected_previous_T0_high_misses":rescued_t1,
        "governance":{
            "forecast_modified":False,
            "routing_tested":False,
            "rolling_pit_r1":True,
            "r2_fixed_two_negative_months":True,
            "t1_any_frozen_pre_outcome":True,
            "severity_ape_v3":True,
            "target_month_market_data_used":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE="+("PASS" if out["status"]=="COMPLETE" else "FAIL"))
    print(json.dumps({
        "parser_coverage":out["parser_coverage"],
        "metrics_all":metrics_all,
        "metrics_timely":metrics_timely,
        "core":core,
        "rescued_t1":rescued_t1,
        "remaining_high":remaining_high,
        "low_confidence":[
            {"page_month":r["page_month"],"flow":r.get("global_flow_t"),"conf":r.get("flow_parse_confidence"),
             "snippet":None if not r.get("flow_parse_detail") else r["flow_parse_detail"].get("snippet")}
            for r in valid if (r.get("flow_parse_confidence") or 0)<.9
        ]
    },sort_keys=True))

if __name__=="__main__":
    main()
