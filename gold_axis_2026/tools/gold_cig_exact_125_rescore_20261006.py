from __future__ import annotations
import io, json, os, time, calendar, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"CIG_CANONICAL_125_RESCORE_OUT"; OUT.mkdir(exist_ok=True)
PIN="fcbf50080afdf164dae460e8e855faf3f72bb1b0"
NY="America/New_York"
DAILY=AX/"GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv"

def git_text(path):
    return subprocess.run(["git","show",f"{PIN}:{path}"],capture_output=True,text=True,check=True).stdout

def read_pin(path):
    return pd.read_csv(io.StringIO(git_text(path)))

def chunks(start,end):
    out=[]; cur=pd.Timestamp(start); end=pd.Timestamp(end)
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end)
        out.append((f"{cur.date()} 00:00:00",f"{b.date()} 23:59:59"))
        cur=b+pd.Timedelta(days=1)
    return out

def fetch15(a,b):
    p={"symbol":"XAU/USD","interval":"15min","timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":os.environ["TWELVE_DATA_API_KEY"],"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str({"a":a,"b":b,"status":r.status_code,"response":j}))
    rows=[]
    for z in vals:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
        except: pass
    return pd.DataFrame(rows),{"start":a,"end":b,"rows":len(rows)}

def metric(rows,col):
    z=[r for r in rows if r.get(col) is not None]
    if not z:return {}
    y=[1 if r[col]>0 else 0 for r in z]
    p=[r["consensus_pred"] for r in z]
    return {
      "n":len(z),
      "direction_correct":int(sum(int(a==b) for a,b in zip(y,p))),
      "direction_accuracy":float(np.mean(np.asarray(y)==np.asarray(p))),
      "positive_share":float(np.mean(np.asarray([r[col] for r in z])>0)),
      "mean_return":float(np.mean([r[col] for r in z])),
      "median_return":float(np.median([r[col] for r in z])),
      "compound_all_long":float(np.prod([1+r[col] for r in z])-1)
    }

def subset_metric(rows,col,state):
    return metric([r for r in rows if r["consensus_pred"]==state],col)

def main():
    daily=pd.read_csv(DAILY)
    daily["Tarih"]=pd.to_datetime(daily["Tarih"]).dt.strftime("%Y-%m-%d")
    daily["actual"]=(pd.to_numeric(daily["Gerçekleşen"])>pd.to_numeric(daily["Önceki Gün Gerçek"])).astype(int)

    v5=read_pin("gold_axis_2026/GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv")
    rift=read_pin("gold_axis_2026/GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv")
    vega=read_pin("gold_axis_2026/GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv")
    ev=read_pin("gold_axis_2026/GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv")
    for df in [v5,rift,vega]:
        df["forecast_issue_date"]=pd.to_datetime(df.forecast_issue_date).dt.strftime("%Y-%m-%d")
        df["feature_cutoff_date"]=pd.to_datetime(df.feature_cutoff_date).dt.strftime("%Y-%m-%d")
    V={r.forecast_issue_date:int(float(r.p_helios_v5_dce)>=.5) for r in v5.itertuples(index=False)}
    R={r.forecast_issue_date:int(float(r.p_rift)>=.5) for r in rift.itertuples(index=False)}
    G={r.forecast_issue_date:int(float(r.p_vega)>=.5) for r in vega.itertuples(index=False)}
    cutoff_issue={r.feature_cutoff_date:r.forecast_issue_date for r in v5.itertuples(index=False)}
    S=dict(V); mapped=[]
    for e in ev.itertuples(index=False):
        c=pd.Timestamp(e.feature_cutoff_date).strftime("%Y-%m-%d")
        issue=cutoff_issue.get(c)
        if issue:
            S[issue]=int(e.combined_pred)
            mapped.append({"feature_cutoff_date":c,"forecast_issue_date":issue,"source":e.source,
                           "v5_pred":int(e.v5_pred),"combined_pred":int(e.combined_pred)})

    base=[]
    for d in daily.itertuples(index=False):
        date=d.Tarih
        if not all(date in M for M in [V,R,G,S]): continue
        vv,rr,gg,ss=V[date],R[date],G[date],S[date]
        cons=(vv==rr==gg==ss)
        base.append({
          "issue_date":date,"actual_daily_label":int(d.actual),
          "daily_prev":float(getattr(d,"_2")) if False else None,
          "sage":ss,"v5":vv,"rift":rr,"vega":gg,
          "consensus":cons,"consensus_pred":vv if cons else None
        })

    def acc(key,rows=base):
        return {"n":len(rows),"correct":sum(int(r[key]==r["actual_daily_label"]) for r in rows),
                "accuracy":sum(int(r[key]==r["actual_daily_label"]) for r in rows)/len(rows)}
    cons=[r for r in base if r["consensus"]]
    disag=[r for r in base if not r["consensus"]]
    canon={
      "universe_n":len(base),
      "sage":acc("sage"),"v5":acc("v5"),"rift":acc("rift"),"vega":acc("vega"),
      "consensus_n":len(cons),
      "consensus_correct":sum(int(r["consensus_pred"]==r["actual_daily_label"]) for r in cons),
      "consensus_accuracy":sum(int(r["consensus_pred"]==r["actual_daily_label"]) for r in cons)/len(cons),
      "disagreement_n":len(disag),
      "disagreement_v5_correct":sum(int(r["v5"]==r["actual_daily_label"]) for r in disag),
      "mapped_sage_ruleflow_events":mapped
    }
    exp={"universe_n":145,"sage_correct":103,"v5_correct":102,"rift_correct":102,"vega_correct":102,
         "consensus_n":125,"consensus_correct":93,"disagreement_n":20,"disagreement_correct":10}
    checks={
      "universe_n":canon["universe_n"]==exp["universe_n"],
      "sage_correct":canon["sage"]["correct"]==exp["sage_correct"],
      "v5_correct":canon["v5"]["correct"]==exp["v5_correct"],
      "rift_correct":canon["rift"]["correct"]==exp["rift_correct"],
      "vega_correct":canon["vega"]["correct"]==exp["vega_correct"],
      "consensus_n":canon["consensus_n"]==exp["consensus_n"],
      "consensus_correct":canon["consensus_correct"]==exp["consensus_correct"],
      "disagreement_n":canon["disagreement_n"]==exp["disagreement_n"],
      "disagreement_correct":canon["disagreement_v5_correct"]==exp["disagreement_correct"]
    }
    gate=all(checks.values())

    parts=[]; meta=[]
    for a,b in chunks("2025-12-31","2026-08-02"):
        q,m=fetch15(a,b); parts.append(q); meta.append(m); time.sleep(8)
    x=pd.concat(parts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    x["date"]=x.dt.dt.strftime("%Y-%m-%d"); x["hm"]=x.dt.dt.strftime("%H:%M")
    M={(r.date,r.hm):float(r.open) for r in x.itertuples(index=False)}

    # Use exact same canonical consensus rows. 08:15 is strictly after governed 08:00 issue deadline.
    outrows=[]
    for r in cons:
        d=r["issue_date"]
        p0815=M.get((d,"08:15")); p1600=M.get((d,"16:00")); p1700=M.get((d,"17:00")); p2000=M.get((d,"20:00"))
        q=dict(r)
        q["ret_0815_1600"]=(p1600/p0815-1) if p0815 and p1600 else None
        q["ret_0815_2000"]=(p2000/p0815-1) if p0815 and p2000 else None
        q["ret_1700_2000"]=(p2000/p1700-1) if p1700 and p2000 else None
        outrows.append(q)
    pd.DataFrame(outrows).to_csv(OUT/"canonical_125_rows.csv",index=False)

    result={
      "status":"EXACT_CANONICAL_125_RESCORE_PASS" if gate else "CANONICAL_RECONSTRUCTION_FAILED",
      "source":{
        "daily_realization_file":"GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv",
        "daily_realization_origin":"recovered from prior ChatGPT Library artifact",
        "model_source_commit":PIN,
      },
      "daily_label_clock_semantics":{
        "known":"StakTrakr historical daily observation date is a UTC calendar-date label; it must not be timezone-converted as an instant.",
        "not_known":"The recovered daily realization value is not an executable intraday timestamp/print.",
        "governed_issue_deadline":"08:00 America/New_York = about 15:00 Istanbul in US DST, 16:00 Istanbul in US standard time"
      },
      "canonical_expected":exp,
      "canonical_reconstructed":canon,
      "checks":checks,
      "exact_match":gate,
      "post_issue_exact_same_125":{
        "08:15_to_16:00_NY":{"ALL":metric(outrows,"ret_0815_1600"),"UP":subset_metric(outrows,"ret_0815_1600",1),"DOWN":subset_metric(outrows,"ret_0815_1600",0)},
        "08:15_to_20:00_NY":{"ALL":metric(outrows,"ret_0815_2000"),"UP":subset_metric(outrows,"ret_0815_2000",1),"DOWN":subset_metric(outrows,"ret_0815_2000",0)},
        "17:00_to_20:00_NY":{"ALL":metric(outrows,"ret_1700_2000"),"UP":subset_metric(outrows,"ret_1700_2000",1),"DOWN":subset_metric(outrows,"ret_1700_2000",0)}
      } if gate else {},
      "missing_dates_in_old_snapshot":["2026-02-27","2026-03-02","2026-03-03","2026-03-04","2026-03-05","2026-03-06"],
      "guardrails":[
        "The six missing dates are a frozen-snapshot coverage gap, not a session-clock definition.",
        "74.40% is the recovered daily-label accuracy on the exact canonical 125 rows.",
        "Post-issue metrics use the same exact 125 signal rows and begin strictly after 08:00 NY.",
        "15m results are retrospective gross XAU/USD spot diagnostics, not prospective evidence or net instrument P&L."
      ],
      "api_meta":meta
    }
    (OUT/"summary.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__":
    main()
