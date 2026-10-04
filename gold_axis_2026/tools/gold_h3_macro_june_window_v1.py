from __future__ import annotations
from pathlib import Path
import io, json
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"

OUT_CSV=AX/"GOLD_H3_MACRO_JUNE_WINDOW_V1_2026-10-04.csv"
OUT_MD=AX/"GOLD_H3_MACRO_JUNE_WINDOW_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_MACRO_JUNE_WINDOW_V1_SUMMARY_2026-10-04.json"

EVENTS=[
 {"date":"2025-06-03","event":"JOLTS","time":"10:00","surprise":"HAWKISH","actual":"7.391M","consensus":"7.10M","fed_delta_pp":None},
 {"date":"2025-06-04","event":"ADP","time":"08:15","surprise":"DOVISH","actual":"37K","consensus":"110K","fed_delta_pp":None},
 {"date":"2025-06-06","event":"NFP","time":"08:30","surprise":"HAWKISH","actual":"139K","consensus":"130K","fed_delta_pp":None},
 {"date":"2025-06-11","event":"CPI","time":"08:30","surprise":"DOVISH","actual":"0.1% m/m; 2.4% y/y","consensus":"0.2-0.3% m/m; 2.5% y/y","fed_delta_pp":11.0},
 {"date":"2025-06-18","event":"FOMC","time":"14:00","surprise":"DOVISH_REPRICE","actual":"Hold 4.25-4.50%; 50bp 2025 cuts median","consensus":"Hold","fed_delta_pp":6.0},
 {"date":"2025-06-27","event":"Core PCE","time":"08:30","surprise":"HAWKISH","actual":"0.2% m/m","consensus":"0.1% m/m","fed_delta_pp":None},
]

def fetch_gc():
    start=pd.Timestamp("2025-05-25",tz="UTC"); end=pd.Timestamp("2025-07-02",tz="UTC")
    p1=int(start.timestamp()); p2=int(end.timestamp())
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/GC%3DF"
        r=requests.get(url,params={"period1":p1,"period2":p2,"interval":"1h","events":"history","includeAdjustedClose":"true"},
                       headers={"User-Agent":"Mozilla/5.0 academic research"},timeout=60)
        if r.status_code!=200: continue
        j=r.json()["chart"]
        if j.get("error") or not j.get("result"): continue
        z=j["result"][0]
        q=z["indicators"]["quote"][0]
        rows=[]
        for t,c in zip(z.get("timestamp",[]),q.get("close",[])):
            if c is None: continue
            rows.append((pd.to_datetime(t,unit="s",utc=True),float(c)))
        d=pd.DataFrame(rows,columns=["ts","gc"]).drop_duplicates("ts").sort_values("ts")
        if len(d)>100: return d
    raise RuntimeError("GC hourly fetch failed")

def fetch_dgs2():
    url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2&cosd=2025-05-20&coed=2025-07-02"
    r=requests.get(url,timeout=60,headers={"User-Agent":"Mozilla/5.0 academic research"}); r.raise_for_status()
    d=pd.read_csv(io.StringIO(r.text))
    d.columns=["date","dgs2"]
    d["date"]=pd.to_datetime(d.date)
    d["dgs2"]=pd.to_numeric(d.dgs2,errors="coerce")
    return d.dropna().sort_values("date")

def prior_daily(dgs,d):
    t=pd.Timestamp(d)
    prev=dgs[dgs.date<t].tail(1)
    cur=dgs[dgs.date==t].tail(1)
    if prev.empty or cur.empty: return np.nan
    return float((cur.dgs2.iloc[0]-prev.dgs2.iloc[0])*100.0)

def px_before(gc,t):
    q=gc[gc.ts<=t].tail(1)
    if q.empty: return np.nan,np.datetime64("NaT")
    return float(q.gc.iloc[0]),q.ts.iloc[0]

def event_gold(gc,date,time):
    local=pd.Timestamp(f"{date} {time}",tz="America/New_York")
    et=local.tz_convert("UTC")
    # Conservative hourly proxy: use the last hourly observation at least one hour before the scheduled release.
    pre_cut=et-pd.Timedelta(hours=1)
    pre,pre_ts=px_before(gc,pre_cut)
    first,first_ts=px_before(gc,et+pd.Timedelta(hours=2))
    close_cut=pd.Timestamp(date,tz="America/New_York")+pd.Timedelta(hours=16)
    close,close_ts=px_before(gc,close_cut.tz_convert("UTC"))
    if not np.isfinite(pre) or not np.isfinite(first) or not np.isfinite(close):
        return {}
    return {
      "release_utc":et,
      "pre_ts":pre_ts,"first_ts":first_ts,"close_ts":close_ts,
      "gc_pre":pre,"gc_first":first,"gc_close":close,
      "first_ret":float(np.log(first/pre)),
      "close_ret":float(np.log(close/pre)),
      "post_first_ret":float(np.log(close/first)),
    }

def load_h3():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"])
    p=pd.read_csv(PANEL,usecols=["feature_cutoff_date","momentum_up","h_ret_12"],parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z.sort_values("feature_cutoff_date")

def main():
    gc=fetch_gc(); dgs=fetch_dgs2(); h=load_h3()
    dates=h.feature_cutoff_date.dt.strftime("%Y-%m-%d").tolist()
    rows=[]
    for e in EVENTS:
        d=e["date"]
        cur=h[h.feature_cutoff_date==pd.Timestamp(d)].tail(1)
        prev=h[h.feature_cutoff_date<pd.Timestamp(d)].tail(1)
        if cur.empty or prev.empty: continue
        c=cur.iloc[0]; p=prev.iloc[0]
        g=event_gold(gc,d,e["time"])
        if not g: continue
        pre_mom=int(p.momentum_up)
        post_mom=int(c.momentum_up)
        y=int(c.y_up)
        pred=int(c.v5_pred)
        first_dir=1 if g["first_ret"]>0 else 0
        close_dir=1 if g["close_ret"]>0 else 0
        # "failed first reaction" means the first post-release move and the eventual event-day close have opposite signs.
        failed_first=first_dir!=close_dir and abs(g["first_ret"])>1e-8 and abs(g["close_ret"])>1e-8
        # Did the first move oppose the pre-release momentum?
        first_opposes_pre=(first_dir!=pre_mom)
        close_opposes_pre=(close_dir!=pre_mom)
        rows.append({
            **e,
            "prior_origin":p.feature_cutoff_date,
            "pre_momentum_up":pre_mom,
            "eventday_momentum_up":post_mom,
            "eventday_momentum_flip":pre_mom!=post_mom,
            "h3_actual_up":y,
            "h3_reversal_vs_eventday_momentum":y!=post_mom,
            "v5_pred_up":pred,
            "v5_missed_reversal":pred==post_mom and y!=post_mom,
            "h3_return":float(c.target_r3),
            "dgs2_change_bp":prior_daily(dgs,d),
            "first_2h_gold_ret":g["first_ret"],
            "eventday_gold_ret":g["close_ret"],
            "post_first_gold_ret":g["post_first_ret"],
            "first_opposes_pre_momentum":first_opposes_pre,
            "close_opposes_pre_momentum":close_opposes_pre,
            "failed_first_reaction":failed_first,
            "pre_ts":g["pre_ts"],"first_ts":g["first_ts"],"close_ts":g["close_ts"],
        })
    q=pd.DataFrame(rows)
    q.to_csv(OUT_CSV,index=False)

    # simple pattern audit, no tuning
    q["rate_reprice_dir"]=np.sign(q.dgs2_change_bp.fillna(0))
    q["first_dir"]=np.sign(q.first_2h_gold_ret)
    q["close_dir"]=np.sign(q.eventday_gold_ret)
    q["h3_rev"]=q.h3_reversal_vs_eventday_momentum.astype(bool)

    stats={
      "n":len(q),
      "h3_reversals":int(q.h3_rev.sum()),
      "v5_missed":int(q.v5_missed_reversal.sum()),
      "eventday_momentum_flips":int(q.eventday_momentum_flip.sum()),
      "failed_first_reactions":int(q.failed_first_reaction.sum()),
      "reversal_when_failed_first":int(q.loc[q.failed_first_reaction,"h3_rev"].sum()),
      "n_failed_first":int(q.failed_first_reaction.sum()),
      "reversal_when_first_opposes_pre":int(q.loc[q.first_opposes_pre_momentum,"h3_rev"].sum()),
      "n_first_opposes_pre":int(q.first_opposes_pre_momentum.sum()),
    }
    OUT_JSON.write_text(json.dumps({"stats":stats,"events":q.to_dict("records")},indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 — JUNE 2025 MACRO REPRICING WINDOW V1","",
      "**Window:** 2025-06-01 .. 2025-06-30",
      "**Status:** retrospective six-event diagnostic; no promotion claim.","",
      "## Event table","",
      "| Date | Event | Surprise | 2Y Δ bp | Fed odds Δ pp | Gold first ~2h | Gold to 16ET | First failed? | Event-day momentum flip? | H3 reversal? | V5 missed? |",
      "|---|---|---|---:|---:|---:|---:|---|---|---|---|"
    ]
    for r in q.itertuples():
        fd="—" if pd.isna(r.fed_delta_pp) else f"{float(r.fed_delta_pp):+.1f}"
        lines.append(f"| {pd.Timestamp(r.date).date()} | {r.event} | {r.surprise} | {r.dgs2_change_bp:+.1f} | {fd} | {100*r.first_2h_gold_ret:+.2f}% | {100*r.eventday_gold_ret:+.2f}% | {r.failed_first_reaction} | {r.eventday_momentum_flip} | {r.h3_reversal_vs_eventday_momentum} | {r.v5_missed_reversal} |")
    lines += ["","## Aggregate","",
      f"- events: **{stats['n']}**",
      f"- H3 reversals after event-day origin: **{stats['h3_reversals']}/{stats['n']}**",
      f"- V5 missed reversals: **{stats['v5_missed']}/{stats['n']}**",
      f"- event-day 12h momentum flips versus prior origin: **{stats['eventday_momentum_flips']}/{stats['n']}**",
      f"- failed first reactions: **{stats['n_failed_first']}**; H3 reversal among them: **{stats['reversal_when_failed_first']}/{max(stats['n_failed_first'],1)}**",
      f"- first Gold reaction opposed pre-release momentum: **{stats['n_first_opposes_pre']}**; H3 reversal among them: **{stats['reversal_when_first_opposes_pre']}/{max(stats['n_first_opposes_pre'],1)}**",
      "",
      "## Clock caution","",
      "Gold first-reaction values use Yahoo hourly GC=F as a retrospective proxy. Because hourly timestamp semantics are not exchange-authority timestamps, the test uses a conservative pre-release bar at least one hour before the scheduled release. These values are mechanism diagnostics only."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
