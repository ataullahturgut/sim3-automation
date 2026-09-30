from __future__ import annotations
import argparse,json,re,time
from datetime import datetime
from pathlib import Path
import pandas as pd, requests
from bs4 import BeautifulSoup

BASE="https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/{year}/{month:02d}"
UA={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/3.0","Accept":"text/html,application/xhtml+xml"}
START_PAGE="2019-01"; END_PAGE="2026-08"; EVAL_START="2021-11"; EVAL_END="2026-08"

def mshift(ym,d):
    y,m=map(int,ym.split("-")); q=y*12+(m-1)+d
    return f"{q//12:04d}-{q%12+1:02d}"
def mrange(a,b):
    out=[]; c=a
    while c<=b: out.append(c); c=mshift(c,1)
    return out
def norm(s): return re.sub(r"\s+"," ",s.replace("\xa0"," ")).strip()

def parse_direction(text):
    t=norm(text); p=t.lower().find("published:")
    x=t[p:p+5000] if p>=0 else t[:5000]
    sentences=re.split(r"(?<=[.!?])\s+",x)
    candidates=[]
    # Prefer sentences explicitly about global gold ETFs and current monthly net direction.
    for idx,s in enumerate(sentences[:35]):
        low=s.lower()
        if "global" not in low or "gold etf" not in low: continue
        # exclude YTD/quarter-only statements unless sentence also says month.
        if any(k in low for k in ["y-t-d","year-to-date","year to date"]) and "month" not in low and not re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",low):
            continue
        if re.search(r"\b(net\s+)?outflows?\b",low) or re.search(r"holdings\s+(?:fell|declined|decreased|dropped|lost)",low):
            candidates.append((0.99,-1,s,idx,"global_outflow_sentence"))
        if re.search(r"\b(net\s+)?inflows?\b",low) or re.search(r"holdings\s+(?:rose|increased|grew|gained|rebounded)",low):
            candidates.append((0.99,1,s,idx,"global_inflow_sentence"))
    # Highlights often omit 'global gold ETF' in same sentence but mention collective holdings.
    for idx,s in enumerate(sentences[:30]):
        low=s.lower()
        if "collective holdings" in low or "collective global holdings" in low:
            if re.search(r"\b(fell|declined|decreased|dropped|lost)\b",low):
                candidates.append((0.97,-1,s,idx,"collective_holdings_down"))
            if re.search(r"\b(rose|increased|grew|gained|rebounded|bounced)\b",low):
                candidates.append((0.97,1,s,idx,"collective_holdings_up"))
    if not candidates: return None,None,None
    # Prefer earlier sentence among same confidence.
    candidates.sort(key=lambda z:(-z[0],z[3]))
    conf,sgn,snip,_,kind=candidates[0]
    return sgn,conf,{"kind":kind,"snippet":norm(snip),"n_candidates":len(candidates)}

def parse_slowdown_note(text):
    t=norm(text); p=t.lower().find("published:")
    x=t[p:p+4000] if p>=0 else t[:4000]
    pats=[
      r"\b(\d{1,3})%\s+(?:lower|less)\s+than\s+(?:the\s+)?previous\s+month\b",
      r"\b(?:slowed|declined|fell|dropped)\s+(?:by\s+)?(\d{1,3})%\s+(?:m-o-m|m/m|month-on-month)\b",
    ]
    for pat in pats:
        m=re.search(pat,x,re.I)
        if m:
            return True,{"pct":int(m.group(1)),"snippet":norm(x[max(0,m.start()-120):m.end()+160])}
    # Non-quantified explicit deterioration.
    m=re.search(r"[^.]{0,100}(?:outflows narrowed|outflows slowed|inflows slowed|inflows fell sharply|flow momentum weakened)[^.]{0,180}\.",x,re.I)
    if m: return True,{"pct":None,"snippet":norm(m.group(0))}
    return False,None

def fetch(ym):
    y,m=map(int,ym.split("-")); url=BASE.format(year=y,month=m)
    r=requests.get(url,headers=UA,timeout=60)
    if r.status_code!=200: return {"page_month":ym,"data_month":mshift(ym,-1),"url":url,"status":r.status_code}
    soup=BeautifulSoup(r.text,"html.parser"); text=norm(soup.get_text(" ",strip=True))
    pm=re.search(r"Published:\s*(\d{1,2}\s+[A-Za-z]+,\s+\d{4})",text,re.I)
    pub=datetime.strptime(pm.group(1),"%d %B, %Y").date().isoformat() if pm else None
    sgn,conf,detail=parse_direction(text); slow,slow_detail=parse_slowdown_note(text)
    return {"page_month":ym,"data_month":mshift(ym,-1),"url":url,"status":200,
            "publication_date":pub,"global_direction":sgn,"direction_confidence":conf,
            "direction_detail":detail,"slowdown_note":slow,"slowdown_detail":slow_detail,
            "title":soup.title.get_text(" ",strip=True) if soup.title else ""}

def load_severity(path):
    j=json.loads(Path(path).read_text())
    if j.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30": raise RuntimeError("BAD_SEVERITY")
    return {r["target"]:r for r in j["rows"]}

def score(rows,timely=False):
    z=[r for r in rows if r.get("severity")]
    ev=[r for r in z if r["R2_WGC"] and (not timely or r["TIMELY_T1"])]
    hi=[r for r in z if r["severity"]=="HIGH"]; elev=[r for r in z if r["severity"] in ("MEDIUM","HIGH")]
    hh=[r for r in ev if r["severity"]=="HIGH"]; eh=[r for r in ev if r["severity"] in ("MEDIUM","HIGH")]
    return {"events":len(ev),"event_targets":[r["page_month"] for r in ev],
            "high_n":len(hi),"high_hits":len(hh),"high_hit_targets":[r["page_month"] for r in hh],
            "high_precision":None if not ev else len(hh)/len(ev),"high_recall":None if not hi else len(hh)/len(hi),
            "elevated_n":len(elev),"elevated_hits":len(eh),"elevated_hit_targets":[r["page_month"] for r in eh],
            "elevated_precision":None if not ev else len(eh)/len(ev),"elevated_recall":None if not elev else len(eh)/len(elev),
            "normal_false_alarm_targets":[r["page_month"] for r in ev if r["severity"]=="NORMAL"],
            "medium_hit_targets":[r["page_month"] for r in ev if r["severity"]=="MEDIUM"]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--severity",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    sev=load_severity(a.severity)
    raw=[]
    for ym in mrange(START_PAGE,END_PAGE):
        raw.append(fetch(ym)); time.sleep(.03)
    parsed=[r for r in raw if r.get("publication_date") and r.get("global_direction") in (-1,1)]
    by_data={r["data_month"]:r for r in parsed}
    rows=sorted(parsed,key=lambda r:r["publication_date"])
    for r in rows:
        prev=by_data.get(mshift(r["data_month"],-1))
        r["prev_global_direction"]=None if prev is None else prev.get("global_direction")
        r["R2_WGC"]=bool(r["global_direction"]==-1 and r["prev_global_direction"]==-1)
        ts=pd.Timestamp(r["publication_date"])
        r["publication_matches_target_month"]=bool(ts.strftime("%Y-%m")==r["page_month"])
        r["publish_day"]=int(ts.day); r["TIMELY_T1"]=bool(r["publication_matches_target_month"] and r["publish_day"]<=10)
        s=sev.get(r["page_month"])
        if s:
            r["ape_pct"]=float(s["ape_pct"]); r["severity"]=s["ape_severity"]; r["ABCDH"]=bool(s["ABCDH"])
        else:
            r["ape_pct"]=None; r["severity"]=None; r["ABCDH"]=None

    coverage=len(parsed)/len(raw)
    expected=mrange(EVAL_START,EVAL_END)
    eval_rows=[r for r in rows if EVAL_START<=r["page_month"]<=EVAL_END and r.get("severity")]
    have={r["page_month"] for r in eval_rows}; missing=[x for x in expected if x not in have]
    met=score(eval_rows,False); tim=score(eval_rows,True)
    core_targets=["2022-05","2022-07","2022-09","2024-03"]
    core=[]
    for t in core_targets:
        r=next((x for x in eval_rows if x["page_month"]==t),None)
        core.append(None if r is None else {k:r.get(k) for k in [
          "page_month","data_month","publication_date","publish_day","global_direction","prev_global_direction",
          "R2_WGC","TIMELY_T1","slowdown_note","slowdown_detail","ape_pct","severity","ABCDH","direction_detail"
        ]})
    t0=[r for r in eval_rows if r["severity"]=="HIGH" and not r["ABCDH"]]
    rescued=[r["page_month"] for r in t0 if r["R2_WGC"]]
    remaining=[r["page_month"] for r in t0 if not r["R2_WGC"]]
    status="COMPLETE" if coverage>=.95 and not missing and all(r["publication_matches_target_month"] for r in eval_rows) else "INCOMPLETE"
    out={"schema":"GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V3_2026-09-30","status":status,
         "parser_coverage":{"pages":len(raw),"parsed":len(parsed),"coverage":coverage,"missing_eval":missing},
         "rows":rows,"raw_page_status":raw,"metrics_all":met,"metrics_timely":tim,"core_rows":core,
         "t0_high_miss_targets":[r["page_month"] for r in t0],"t1_r2_detected_t0_high_misses":rescued,
         "remaining_high_after_T0_ABCDH_and_T1_R2":remaining,
         "slowdown_note_targets":[r["page_month"] for r in eval_rows if r.get("slowdown_note")],
         "governance":{"forecast_modified":False,"routing_tested":False,"numeric_threshold_used":False,
                       "r2_fixed_two_consecutive_outflow_reports":True,"severity_ape_v3":True,"target_month_market_data_used":False}}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE="+("PASS" if status=="COMPLETE" else "FAIL"))
    print(json.dumps({"coverage":out["parser_coverage"],"all":met,"timely":tim,"core":core,"rescued":rescued,"remaining":remaining,
                      "slowdown_notes":out["slowdown_note_targets"],
                      "low_conf":[{"page_month":r["page_month"],"conf":r.get("direction_confidence"),"snippet":r.get("direction_detail")} for r in rows if (r.get("direction_confidence") or 0)<.95]},sort_keys=True))

if __name__=="__main__": main()
