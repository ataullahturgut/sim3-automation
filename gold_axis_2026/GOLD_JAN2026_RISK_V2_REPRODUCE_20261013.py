#!/usr/bin/env python3
"""Independent stdlib-only Stage-D risk-state replay on stored factor data.
Run inside gold_axis_2026: python GOLD_JAN2026_RISK_V2_REPRODUCE_20261013.py
This does not certify PIT source vintages, economic causality or bank tradability.
"""
from pathlib import Path
from collections import defaultdict
from statistics import median
from math import hypot
import csv, json

HERE=Path(__file__).resolve().parent
SOURCE="GOLD_JAN2026_RISK_HAZARD_V2_HISTORICAL_VENDOR_SAFE_PANEL_20261013.csv"
RESULT="GOLD_JAN2026_RISK_V2_STAGE_D_CALIBRATION_ALERTS_AND_BACKTEST_20261013.json"
source=defaultdict(list)
with (HERE/SOURCE).open(newline="",encoding="utf8") as f:
    for r in csv.DictReader(f):
        arr=source[r["source"]]
        p=arr[-1]["close"] if arr else 1.
        arr.append({"date":r["date"],"open":p*float(r["open_factor"]),
                    "close":p*float(r["close_factor"]),
                    "high":p*float(r["high_factor"]),
                    "low":p*float(r["low_factor"]),
                    "dd":float(r["ordered_dd_pct"])})
score_by_day={}
points=[]
for src,a in source.items():
    for i in range(60,len(a)):
        current=a[i]
        historical=a[i-60:i]
        d=abs(current["dd"])
        w=max(0.,100.*(current["high"]-current["close"])/current["high"])
        denom_d=max(.1,median(abs(z["dd"]) for z in historical))
        denom_w=max(.1,median(max(0.,100.*(z["high"]-z["close"])/z["high"]) for z in historical))
        score=hypot(d/denom_d,w/denom_w)
        future=a[i+1:i+4]
        known=len(future)==3
        event=None if not known else int(any(z["low"]<=.97*current["close"] for z in future))
        points.append({"src":src,"day":current["date"],"score":score,"y3":event})
        score_by_day[(src,current["date"])]=score
train=sorted(z["score"] for z in points if z["src"]=="EV" and z["day"]<"2024-01-01")
pos=.99*(len(train)-1)
i=int(pos)
threshold=train[i]+(train[min(i+1,len(train)-1)]-train[i])*(pos-i)
saved=json.loads((HERE/RESULT).read_text(encoding="utf8"))
assert abs(threshold-saved["cutoff"])<1e-8, (threshold,saved["cutoff"])

for year in ["2022","2023","2024","2025"]:
    group=[z for z in points if z["src"]=="EV" and z["day"].startswith(year)]
    alarms=[z for z in group if z["score"]>=threshold]
    expected=next(z for z in saved["year_metrics"] if z["period"]==year)
    assert len(group)==expected["n"]
    assert len(alarms)==expected["alerts"]
    assert sum(z["y3"]==1 for z in alarms)==expected["flag_predict_next3_drop3"]
    print(year,len(group),"alerts",len(alarms),
          "next3>=3pct down",sum(z["y3"]==1 for z in alarms))
jan=[z for z in points if z["src"]=="HIST" and z["day"].startswith("2026-01")]
assert [z["day"] for z in jan if z["score"]>=threshold]==["2026-01-29","2026-01-30"]

periods=[("2023","EV","2023-01-01","2023-12-31"),
         ("2024","EV","2024-01-01","2024-12-31"),
         ("2025","EV","2025-01-01","2025-12-31"),
         ("Jan2026","HIST","2026-01-01","2026-01-31")]
def trial(entry,overlay):
    name,src,left,right=entry
    allrows=source[src]
    indices=[i for i,r in enumerate(allrows) if left<=r["date"]<=right]
    start,end=indices[0],indices[-1]
    pos,cash,units,cool,pending="CASH",1.,0.,0,None
    fees=0
    peak,ddmax=1.,0.
    actions=0
    for i in range(start,end+1):
        z=allrows[i]
        if pending:
            if pending=="AL":
                units=cash*.992/z["open"];cash=0.;pos="GOLD"
            else:
                cash=units*z["open"]*.992;units=0.;pos="CASH";cool=5
            actions+=1
            pending=None
        r60=100*(z["close"]/allrows[i-60]["close"]-1) if i>=60 else None
        is_alert=score_by_day.get((src,z["date"]),0)>=threshold
        if pos=="GOLD" and ((r60 is not None and r60<=-2) or (overlay and is_alert)):
            pending="SAT"
        elif pos=="CASH" and cool==0 and r60 is not None and r60>=2:
            pending="AL"
        nav=units*z["close"] if pos=="GOLD" else cash
        peak=max(peak,nav)
        ddmax=min(ddmax,nav/peak-1)
        if cool>0:cool-=1
    cash_equiv=units*allrows[end]["close"]*.992 if pos=="GOLD" else cash
    return 100*(cash_equiv-1),100*ddmax,actions
for p in periods:
    for switch in [False,True]:
        ret,dd,n=trial(p,switch)
        policy="S4_PLUS_ANOMALY" if switch else "S4_ONLY"
        record=next(x for x in saved["performance"] if x["cohort"]==p[0] and x["policy"]==policy)
        assert abs(ret-record["net_return_pct"])<1e-8,(p,policy,ret,record["net_return_pct"])
        assert abs(dd-record["maxdd_pct"])<1e-8
        assert n==record["actions"]
        print(p[0],policy,f"{ret:+.3f}%",f"orders={n}")
print("Stage D reproducibility PASS; Jan comparison remains EX-POST, not bank executable.")
