from __future__ import annotations
import json, os, time, calendar
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "EXECUTION_15M_COVERAGE_OUT"
OUT.mkdir(exist_ok=True)
PANEL = AX / "GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"

def chunks():
    out=[]
    cur=pd.Timestamp("2025-06-30")
    end=pd.Timestamp("2026-09-27")
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end)
        out.append((str(cur.date())+" 00:00:00",str(b.date())+" 23:59:59"))
        cur=b+pd.Timedelta(days=1)
    return out

def fetch(a,b):
    params={
      "symbol":"XAU/USD","interval":"15min","timezone":"UTC","order":"ASC",
      "outputsize":5000,"apikey":os.environ["TWELVE_DATA_API_KEY"],
      "start_date":a,"end_date":b
    }
    r=requests.get("https://api.twelvedata.com/time_series",params=params,timeout=90)
    j=r.json()
    vals=j.get("values") or []
    if not vals:
        raise RuntimeError(str({"a":a,"b":b,"status":r.status_code,"response":j}))
    rows=[]
    for z in vals:
        rows.append({
          "dt_utc":pd.Timestamp(z["datetime"],tz="UTC"),
          "open":float(z["open"]),"close":float(z["close"])
        })
    return pd.DataFrame(rows), {"start":a,"end":b,"rows":len(rows)}

def period(d):
    if d < "2026-01-01": return "2025_H2"
    if d <= "2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def compound(a):
    a=np.asarray(a,float)
    return float(np.prod(1+a)-1) if len(a) else None

def main():
    sig=pd.read_csv(PANEL)
    sig["consensus"]=sig.consensus.astype(str).str.lower().eq("true")
    sig=sig[(sig.issue_date>="2025-07-01")&(sig.issue_date<="2026-09-25")].copy()
    sig["state"]=np.where(~sig.consensus,"UNCERTAIN",np.where(sig.v5.astype(int)==1,"UP","DOWN"))

    parts=[]; meta=[]
    for a,b in chunks():
        q,m=fetch(a,b); parts.append(q); meta.append(m); time.sleep(8)
    x=pd.concat(parts,ignore_index=True).sort_values("dt_utc").drop_duplicates("dt_utc")
    x["dt_ny"]=x.dt_utc.dt.tz_convert("America/New_York")
    x["dt_tr"]=x.dt_utc.dt.tz_convert("Europe/Istanbul")
    x["ny_date"]=x.dt_ny.dt.strftime("%Y-%m-%d")

    daily=x.groupby("ny_date").size()
    cov=[]
    for r in sig.itertuples(index=False):
        n=int(daily.get(r.issue_date,0))
        cov.append({"issue_date":r.issue_date,"period":period(r.issue_date),"state":r.state,
                    "bars_15m_ny_day":n,"has_data":n>0,"near_full":n>=90})
    cov=pd.DataFrame(cov)
    cov.to_csv(OUT/"signal_date_coverage.csv",index=False)

    # 24-hour research cycle: prior calendar day 20:00 NY -> issue day 20:00 NY.
    profiles=[]
    session_rows=[]
    for r in sig[sig.consensus].itertuples(index=False):
        d=pd.Timestamp(r.issue_date)
        start=pd.Timestamp(str((d-pd.Timedelta(days=1)).date())+" 20:00:00",tz="America/New_York")
        end=pd.Timestamp(str(d.date())+" 20:00:00",tz="America/New_York")
        g=x[(x.dt_ny>=start)&(x.dt_ny<end)].copy()
        if len(g)<80: continue
        p0=float(g.iloc[0].open)
        g["cum_ret"]=g.open/p0-1
        g["inc_ret"]=g.open.pct_change()
        g["rel_min"]=((g.dt_ny-start).dt.total_seconds()/60).astype(int)
        for z in g.itertuples(index=False):
            profiles.append({
              "issue_date":r.issue_date,"period":period(r.issue_date),"state":r.state,
              "rel_min":int(z.rel_min),
              "ny_hm":z.dt_ny.strftime("%H:%M"),
              "tr_hm":z.dt_tr.strftime("%H:%M"),
              "cum_ret":float(z.cum_ret),
              "inc_ret":None if pd.isna(z.inc_ret) else float(z.inc_ret)
            })

        # Academic/session clock buckets in NY time.
        def px_at_or_after(ts):
            q=g[g.dt_ny>=ts]
            return float(q.iloc[0].open) if len(q) else None
        marks=[
          ("START",start),
          ("EUROPE_START",pd.Timestamp(str(d.date())+" 03:30:00",tz="America/New_York")),
          ("OVERLAP_START",pd.Timestamp(str(d.date())+" 08:00:00",tz="America/New_York")),
          ("US_ONLY_START",pd.Timestamp(str(d.date())+" 14:30:00",tz="America/New_York")),
          ("END",end-pd.Timedelta(minutes=15))
        ]
        pm={k:px_at_or_after(t) for k,t in marks}
        if all(v is not None for v in pm.values()):
            session_rows.append({
              "issue_date":r.issue_date,"period":period(r.issue_date),"state":r.state,
              "asia_to_europe":pm["EUROPE_START"]/pm["START"]-1,
              "europe_pre_overlap":pm["OVERLAP_START"]/pm["EUROPE_START"]-1,
              "ny_london_overlap":pm["US_ONLY_START"]/pm["OVERLAP_START"]-1,
              "late_us":pm["END"]/pm["US_ONLY_START"]-1
            })

    prof=pd.DataFrame(profiles)
    prof.to_csv(OUT/"profile_rows.csv",index=False)
    sess=pd.DataFrame(session_rows)
    sess.to_csv(OUT/"session_rows.csv",index=False)

    agg=[]
    if len(prof):
        for (per,state,rel),g in prof.groupby(["period","state","rel_min"]):
            # most common Istanbul label at this relative minute; DST differences can create two labels.
            mode_tr=g.tr_hm.mode()
            agg.append({
              "period":per,"state":state,"rel_min":int(rel),
              "ny_hm":g.ny_hm.iloc[0],
              "tr_hm_mode":mode_tr.iloc[0] if len(mode_tr) else g.tr_hm.iloc[0],
              "n":len(g),
              "mean_cum_ret":float(g.cum_ret.mean()),
              "median_cum_ret":float(g.cum_ret.median()),
              "mean_inc_ret":float(g.inc_ret.dropna().mean()) if g.inc_ret.notna().any() else None
            })
    pd.DataFrame(agg).to_csv(OUT/"profile_aggregate.csv",index=False)

    sm={}
    for (per,state),g in sess.groupby(["period","state"]):
        sm[f"{per}_{state}"]={"n":int(len(g))}
        for c in ["asia_to_europe","europe_pre_overlap","ny_london_overlap","late_us"]:
            sm[f"{per}_{state}"][c]={
              "compound":compound(g[c].to_numpy()),
              "mean":float(g[c].mean()),
              "hit":float((g[c]>0).mean())
            }

    periods={}
    for per,g in cov.groupby("period"):
        periods[per]={
          "signal_dates":int(len(g)),
          "dates_with_data":int(g.has_data.sum()),
          "near_full_dates":int(g.near_full.sum()),
          "min_bars":int(g.bars_15m_ny_day.min()),
          "median_bars":float(g.bars_15m_ny_day.median()),
          "up":int((g.state=="UP").sum()),
          "down":int((g.state=="DOWN").sum()),
          "uncertain":int((g.state=="UNCERTAIN").sum())
        }

    out={
      "status":"RETROSPECTIVE_15M_COVERAGE_AND_PROFILE_AUDIT",
      "window":"2025-07-01..2026-09-25",
      "xau_rows":int(len(x)),
      "first_utc":str(x.dt_utc.min()),"last_utc":str(x.dt_utc.max()),
      "request_chunks":meta,
      "coverage_by_period":periods,
      "missing_signal_dates":cov.loc[~cov.has_data,"issue_date"].tolist(),
      "thin_signal_dates_under_90_bars":cov.loc[cov.has_data & ~cov.near_full,["issue_date","bars_15m_ny_day"]].to_dict("records"),
      "coverage_gate_pass":bool(cov.has_data.all()),
      "session_summary":sm,
      "guardrail":"Pre-08:00 NY bars are attribution only for CIG-D1 V1; they are not executable using an 08:00 issuance."
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
