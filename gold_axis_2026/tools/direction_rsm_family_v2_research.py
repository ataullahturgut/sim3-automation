#!/usr/bin/env python3
"""Corrected source-family RSM/ERSM weekly direction research.

Authority:
  GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_PREREG_2026-09-18.md

Input CSV requires:
  observation_ts,value
Optional:
  retrieved_at,quality_status
"""

from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from datetime import datetime,date,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY=ZoneInfo("America/New_York")
KS=(26,52,104)

def parse_ts(s):
    s=s.strip()
    if s.endswith("Z"): s=s[:-1]+"+00:00"
    x=datetime.fromisoformat(s)
    if x.tzinfo is None: raise ValueError("timezone-aware observation_ts required")
    return x

def monday(d): return d-timedelta(days=d.weekday())

def load_daily(path):
    latest={}
    with path.open(encoding="utf-8",newline="") as fh:
        rd=csv.DictReader(fh)
        for r in rd:
            key=r["observation_ts"].strip()
            old=latest.get(key)
            if old is None or r.get("retrieved_at","")>old.get("retrieved_at",""):
                latest[key]=r
    rows=[]
    for r in latest.values():
        if r.get("quality_status") and "APPROV" not in r["quality_status"].upper(): continue
        dt=parse_ts(r["observation_ts"]).astimezone(NY)
        if dt.weekday()>=5: continue
        v=float(r["value"])
        if not math.isfinite(v) or v<=0: raise ValueError("invalid price")
        rows.append((dt.date(),v))
    return sorted(rows)

def weekly_signs(daily):
    # Source-text-faithful: daily simple percentage returns aggregated by week.
    wk=defaultdict(float); closes=defaultdict(list)
    prev=None
    for d,c in daily:
        closes[monday(d)].append((d,c))
        if prev is not None:
            wk[monday(d)] += c/prev-1.0
        prev=c

    weeks=sorted(closes)
    out=[]
    last_week_close=None
    for w in weeks:
        last_close=max(closes[w],key=lambda z:z[0])[1]
        r=wk[w]
        source_sign=1 if r>0 else 0
        close_sign=None
        if last_week_close is not None:
            close_sign=1 if math.log(last_close/last_week_close)>0 else 0
        out.append({"week_start":w,"weekly_return":r,"x":source_sign,"close_sign":close_sign})
        last_week_close=last_close
    return out

def score(hist,family,k):
    x=[r["x"] for r in hist[-k:]]
    if family=="RSM":
        return sum(x)/k
    alpha=2.0/(k+1.0)
    # newest observation has exponent 0; finite weights intentionally not normalized.
    return sum(alpha*((1-alpha)**lag)*x[-1-lag] for lag in range(k))

def forecasts(weeks):
    rows=[]
    for family in ("RSM","ERSM"):
        for k in KS:
            for i in range(k,len(weeks)):
                p=score(weeks[:i],family,k)
                rows.append({
                    "family":family,"k":k,
                    "target_week":weeks[i]["week_start"],
                    "p_up":p,"pred_up":1 if p>=.5 else 0,
                    "actual_up":weeks[i]["x"],
                    "previous_up":weeks[i-1]["x"],
                })
    return rows

def metrics(rows):
    if not rows: return {"n":0}
    n=len(rows); up=sum(r["actual_up"] for r in rows); dn=n-up
    tp=sum(r["pred_up"]==1 and r["actual_up"]==1 for r in rows)
    tn=sum(r["pred_up"]==0 and r["actual_up"]==0 for r in rows)
    fp=sum(r["pred_up"]==1 and r["actual_up"]==0 for r in rows)
    fn=sum(r["pred_up"]==0 and r["actual_up"]==1 for r in rows)
    eps=1e-12
    brier=sum((r["p_up"]-r["actual_up"])**2 for r in rows)/n
    ll=-sum(r["actual_up"]*math.log(min(max(r["p_up"],eps),1-eps))+
            (1-r["actual_up"])*math.log(min(max(1-r["p_up"],eps),1-eps))
            for r in rows)/n
    return {
        "n":n,"accuracy":(tp+tn)/n,
        "balanced_accuracy":((tp/up)+(tn/dn))/2 if up and dn else None,
        "actual_up":up,"actual_down":dn,"forecast_up":tp+fp,"forecast_down":tn+fn,
        "up_sensitivity":tp/up if up else None,"down_sensitivity":tn/dn if dn else None,
        "tp":tp,"tn":tn,"fp":fp,"fn":fn,
        "always_up_accuracy":up/n,
        "previous_sign_accuracy":sum(r["previous_up"]==r["actual_up"] for r in rows)/n,
        "brier":brier,"log_loss":ll,
        "mean_p_up":sum(r["p_up"] for r in rows)/n,
        "min_p_up":min(r["p_up"] for r in rows),"max_p_up":max(r["p_up"] for r in rows),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input_csv",type=Path)
    ap.add_argument("--through-year",type=int,required=True)
    ap.add_argument("--summary-json",type=Path,required=True)
    ap.add_argument("--forecast-csv",type=Path,required=True)
    a=ap.parse_args()

    weeks=weekly_signs(load_daily(a.input_csv))
    fc=[r for r in forecasts(weeks) if r["target_week"].year<=a.through_year]

    fields=["family","k","target_week","p_up","pred_up","actual_up","previous_up"]
    with a.forecast_csv.open("w",encoding="utf-8",newline="") as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n");wr.writeheader();wr.writerows(fc)

    by={}
    for fam in ("RSM","ERSM"):
        for k in KS:
            for y in sorted({r["target_week"].year for r in fc}):
                z=[r for r in fc if r["family"]==fam and r["k"]==k and r["target_week"].year==y]
                if z: by[f"{fam}_{k}_{y}"]=metrics(z)

    y24=[r for r in fc if r["target_week"].year==2024]
    starts=[]
    for fam in ("RSM","ERSM"):
        for k in KS:
            z=[r["target_week"] for r in y24 if r["family"]==fam and r["k"]==k]
            if z: starts.append(min(z))
    common=max(starts)
    common_metrics={}
    for fam in ("RSM","ERSM"):
        for k in KS:
            z=[r for r in y24 if r["family"]==fam and r["k"]==k and r["target_week"]>=common]
            common_metrics[f"{fam}_{k}"]=metrics(z)

    comparable=[w for w in weeks if w["close_sign"] is not None and w["week_start"].year<=a.through_year]
    concord=sum(w["x"]==w["close_sign"] for w in comparable)

    a.summary_json.write_text(json.dumps({
        "identity":"DIRECTION_RSM_FAMILY_V2_RESEARCH",
        "source_feasible_k":list(KS),
        "weekly_return":"sum of governed daily simple percentage returns",
        "ersm_alpha":"2/(k+1)",
        "ersm_weights_normalized":False,
        "decision_rule":"UP iff p>=0.5",
        "by_variant_year":by,
        "common_2024_start":common.isoformat(),
        "common_2024":common_metrics,
        "construction_concordance":{"n":len(comparable),"matches":concord,
                                    "rate":concord/len(comparable) if comparable else None},
    },indent=2,default=str)+"\n",encoding="utf-8")

if __name__=="__main__": main()
