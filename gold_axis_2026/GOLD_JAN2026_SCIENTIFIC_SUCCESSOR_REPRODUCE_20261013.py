#!/usr/bin/env python3
"""Reproduce all Jan-2026 scientific-successor DEV/validation/stress scenarios.
Only Python stdlib, no vendor spot price redistribution. Rebuild synthetic quote
price INDEX from daily quote-relative factors; all portfolio returns invariant to
absolute USD/oz price scale inside a single source.
Run from anywhere: python GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_REPRODUCE_20261013.py
"""
from pathlib import Path
from collections import defaultdict
import csv, json, math

HERE=Path(__file__).resolve().parent
PREFIX="GOLD_JAN2026_"
rows=defaultdict(list)
with (HERE/(PREFIX+"SCIENTIFIC_SUCCESSOR_DERIVED_DAILY_FEATURE_INPUT_20261013.csv")).open(newline="",encoding="utf8") as f:
    for z in csv.DictReader(f):
        src=z["source"]
        prev=rows[src][-1]["c"] if rows[src] else 1.
        rows[src].append({"date":z["day"],"open":prev*float(z["open_rel_prev_close"]),
             "c":prev*float(z["close_rel_prev_close"]), "dd":float(z["intraday_ordered_dd_pct"])})
periods=[
    ("2023_DEV","EV","2023-01-01","2023-12-31"),
    ("2024_DEV","EV","2024-01-01","2024-12-31"),
    ("2025_VALIDATION","EV","2025-01-01","2025-12-31"),
    ("2026JAN_PRIOR_EXPOSED","HIST","2026-01-01","2026-01-31")
]
A=["B0_ORIGINAL","B1_DD2","B2_DD3","B3_DD4","B4_DD5"]
B=["B0_ORIGINAL","S1_SMA20_60","S2_SMA50","S3_R20","S4_R60","S5_TREND_TRAIL"]
C=["C0_S4_ONLY","C1_S4_DD3","C2_S4_DD4","C3_S4_DD5"]

def run(per,policy):
    name,source,lo,hi=per
    dates=rows[source]
    inds=[i for i,z in enumerate(dates) if lo<=z["date"]<=hi]
    begin,end=inds[0],inds[-1]
    series=[z["c"] for z in dates]
    cash,units,position,pending,cool,peak,mdd,actions,held=1.,0.,"CASH",None,0,1.,0.,[],0
    for i in range(begin,end+1):
        z=dates[i]
        if pending is not None:
            signal,origin,reason=pending
            if signal=="AL":
                assert position=="CASH"
                units=cash*.992/z["open"];cash=0;position="GOLD"
            else:
                assert position=="GOLD"
                cash=units*z["open"]*.992;units=0;position="CASH"
                if policy.startswith("C") or policy.startswith("S"):cool=5
                elif policy.startswith("B") and policy!="B0_ORIGINAL" and reason=="INTRADAY_DD":cool=3
            actions.append((origin,z["date"],signal,reason))
            pending=None
        def ret(k):
            return 100*(series[i]/series[i-k]-1) if i>=k else None
        def ma(k):
            return sum(series[i-k+1:i+1])/k if i>=k-1 else None
        r3,r5,r20,r60=(ret(k) for k in [3,5,20,60])
        m10,m20,m50,m60=(ma(k) for k in [10,20,50,60])
        d10=100*(series[i]/max(series[i-9:i+1])-1) if m10 is not None else None
        buy=sell=False
        reason=""
        if policy=="B0_ORIGINAL" or policy.startswith("B") and "DD" in policy:
            buy=r5 is not None and r20 is not None and m10 is not None and r5>=1.2 and r20>0 and z["c"]>=m10
            sell=(r3 is not None and r3<=-1.5) or (d10 is not None and d10<=-2) or (m10 is not None and r5 is not None and z["c"]<m10 and r5<=-.5)
            reason="BASELINE"
            if policy!="B0_ORIGINAL" and not sell and z["dd"]<=-float(policy.split("DD")[1]):
                sell=True;reason="INTRADAY_DD"
        elif policy=="S1_SMA20_60":
            buy=m20 is not None and m60 is not None and m20>=m60*1.01 and z["c"]>m60
            sell=m20 is not None and m60 is not None and m20<=m60*.99
        elif policy=="S2_SMA50":
            buy=m50 is not None and r20 is not None and z["c"]>=m50*1.01 and r20>=1
            sell=(m50 is not None and z["c"]<=m50*.97) or (r20 is not None and r20<=-3)
        elif policy=="S3_R20":
            buy=r20 is not None and r20>=3
            sell=r20 is not None and r20<=-3
        elif policy=="S4_R60" or policy.startswith("C"):
            buy=r60 is not None and r60>=2
            sell=r60 is not None and r60<=-2
            reason="S4"
            if policy.startswith("C") and policy!="C0_S4_ONLY":
                if z["dd"]<=-float(policy.split("DD")[1]) and not sell:
                    sell=True;reason="INTRADAY_DD"
        elif policy=="S5_TREND_TRAIL":
            buy=r20 is not None and m20 is not None and r20>=1 and z["c"]>=m20
            sell=i>=59 and r5 is not None and z["c"]<=.92*max(series[i-59:i+1]) and r5<0
        else:raise ValueError(policy)
        sig=("SAT" if sell else None) if position=="GOLD" else ("AL" if buy and cool==0 else None)
        if sig:pending=(sig,z["date"],reason)
        value=units*z["c"] if position=="GOLD" else cash
        peak=max(peak,value);mdd=min(mdd,value/peak-1)
        held+=(position=="GOLD")
        if cool>0:cool-=1
    gross=units*series[end] if position=="GOLD" else cash
    term=gross*.992 if position=="GOLD" else gross
    return {"period":name,"policy":policy,"netPct":100*(term-1),
      "mddPct":100*mdd,"actions":len(actions),"exposurePct":100*held/(end-begin+1),
      "openEnd":position,"pending":pending[0] if pending else None}

def check(filename, family, mapping):
    saved=json.loads((HERE/(PREFIX+filename)).read_text(encoding="utf8"))
    listed=saved["results"] if isinstance(saved["results"],list) else saved["summary"]
    num=0
    for a in listed:
        got=run(periods[[x[0] for x in periods].index(a["period"])],a["policy"])
        for actual,savedKey in mapping.items():
            assert math.isclose(got[actual],float(a[savedKey]),rel_tol=0,abs_tol=1e-7), (filename,a["period"],a["policy"],actual,got[actual],a[savedKey])
        num+=1
    print(f"{family} PASS: {num} source-preserving normalized replays")

check("SCIENTIFIC_SUCCESSOR_CROSSYEAR_OUTCOMES_20261013.json","STAGE_A",
      {"netPct":"total_return_cash_equivalent_pct","mddPct":"max_drawdown_daily_pct","actions":"paid_actions"})
check("STAGE_B_SLOW_REGIME_CROSSYEAR_RESULTS_20261013.json","STAGE_B",
      {"netPct":"netReturnPct","mddPct":"maxDrawdownPct","actions":"paidActions"})
check("STAGE_C_REGIME_SHOCK_COMBINATION_RESULTS_20261013.json","STAGE_C",
      {"netPct":"netPct","mddPct":"maxDrawdownPct","actions":"paidActions"})
