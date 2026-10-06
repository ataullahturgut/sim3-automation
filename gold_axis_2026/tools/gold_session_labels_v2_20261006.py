from __future__ import annotations
import hashlib, json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_LABELS_V2_OUT"; OUT.mkdir(exist_ok=True)

UTC=ZoneInfo("UTC")
NY=ZoneInfo("America/New_York")
LON=ZoneInfo("Europe/London")
SHA=ZoneInfo("Asia/Shanghai")
IST=ZoneInfo("Europe/Istanbul")
START=date(2023,1,1)
END=date(2025,12,31)

def sha256_file(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def aware(d,hh,mm,tz=NY):
    return pd.Timestamp(datetime(d.year,d.month,d.day,hh,mm,tzinfo=tz))

def loc(ts,tz): return ts.tz_convert(tz).isoformat()

def direction(r):
    if r is None or pd.isna(r): return None
    if r>0:return "UP"
    if r<0:return "DOWN"
    return "FLAT"

def build_maps(x):
    op={pd.Timestamp(r.dt_utc):float(r.open) for r in x.itertuples(index=False)}
    cl={pd.Timestamp(r.dt_utc):float(r.close) for r in x.itertuples(index=False)}
    return op,cl

def boundary_price(op,cl,t):
    u=t.tz_convert("UTC")
    if u in op:
        return op[u],"OPEN_AT_T",u
    p=u-pd.Timedelta(minutes=15)
    if p in cl:
        # the previous 15m bar ends exactly at boundary T
        return cl[p],"PREV_15M_CLOSE_AT_T",u
    return None,"MISSING",u

def row(op,cl,d,partition,window,s,e):
    ps,ms,su=boundary_price(op,cl,s)
    pe,me,eu=boundary_price(op,cl,e)
    ok=ps is not None and pe is not None
    r=(pe/ps-1.0) if ok else None
    return {
      "label_date":d.isoformat(),"year":d.year,"weekday":d.weekday(),
      "partition":partition,"window":window,
      "start_utc":su.isoformat(),"end_utc":eu.isoformat(),
      "start_ny":loc(su,NY),"end_ny":loc(eu,NY),
      "start_london":loc(su,LON),"end_london":loc(eu,LON),
      "start_shanghai":loc(su,SHA),"end_shanghai":loc(eu,SHA),
      "start_istanbul":loc(su,IST),"end_istanbul":loc(eu,IST),
      "start_boundary_method":ms,"end_boundary_method":me,
      "start_price":ps,"end_price":pe,"return":r,"direction":direction(r),
      "coverage":"PASS" if ok else "MISSING_BOUNDARY"
    }

def coverage(df):
    out={}
    for (yr,w),g in df.groupby(["year","window"]):
        good=g[g.coverage=="PASS"]
        out[f"{yr}_{w}"]={
          "eligible_weekdays":int(len(g)),
          "pass":int(len(good)),
          "missing":int((g.coverage!="PASS").sum()),
          "pass_rate":float(len(good)/len(g)) if len(g) else None,
          "start_open_at_t":int((good.start_boundary_method=="OPEN_AT_T").sum()),
          "start_prev_close":int((good.start_boundary_method=="PREV_15M_CLOSE_AT_T").sum()),
          "end_open_at_t":int((good.end_boundary_method=="OPEN_AT_T").sum()),
          "end_prev_close":int((good.end_boundary_method=="PREV_15M_CLOSE_AT_T").sum()),
          "up":int((good.direction=="UP").sum()),
          "down":int((good.direction=="DOWN").sum()),
          "flat":int((good.direction=="FLAT").sum()),
        }
    return out

def source_regime(x):
    z=x[(x.dt_utc>=pd.Timestamp("2023-01-01",tz="UTC"))&(x.dt_utc<pd.Timestamp("2026-01-01",tz="UTC"))].copy()
    z["date"]=z.dt_utc.dt.strftime("%Y-%m-%d")
    z["year"]=z.dt_utc.dt.year
    d=z.groupby("date").agg(n=("dt_utc","size"),year=("year","first")).reset_index()
    d["date_ts"]=pd.to_datetime(d.date)
    d["weekday"]=d.date_ts.dt.weekday
    wd=d[d.weekday<5].copy()
    out={}
    for yr,g in wd.groupby("year"):
        out[str(int(yr))]={
          "weekday_dates_with_any_data":int(len(g)),
          "bar_count_distribution":{str(int(k)):int(v) for k,v in g.n.value_counts().sort_index().items()},
          "median_bars":float(g.n.median())
        }
    g25=wd[wd.year==2025].sort_values("date")
    full=g25[g25.n==96]
    out["2025_first_weekday_with_96_bars"]=None if full.empty else str(full.iloc[0].date)
    after=g25[g25.date>="2025-04-22"]
    out["2025_04_22_onward_96bar_share"]=float((after.n==96).mean()) if len(after) else None
    return out

def main():
    x=pd.read_csv(RAW)
    x["dt_utc"]=pd.to_datetime(x.dt_utc,utc=True)
    op,cl=build_maps(x)

    wgc=[]; sob=[]
    d=START
    while d<=END:
        if d.weekday()<5:
            prev=d-timedelta(days=1)
            wgc.append(row(op,cl,d,"WGC_2026_NY3","ASIA",
                           aware(prev,18,0,NY),aware(d,3,0,NY)))
            wgc.append(row(op,cl,d,"WGC_2026_NY3","EUROPE",
                           aware(d,3,0,NY),aware(d,8,0,NY)))
            wgc.append(row(op,cl,d,"WGC_2026_NY3","US",
                           aware(d,8,0,NY),aware(d,17,0,NY)))

            sob.append(row(op,cl,d,"SOBTI_5_ET","ASIA_MORNING_LIT",
                           aware(prev,21,0,NY),aware(prev,23,30,NY)))
            sob.append(row(op,cl,d,"SOBTI_5_ET","ASIA_AFTERNOON_LIT",
                           aware(d,1,30,NY),aware(d,3,30,NY)))
            sob.append(row(op,cl,d,"SOBTI_5_ET","EUROPE_LIT",
                           aware(d,3,30,NY),aware(d,8,0,NY)))
            sob.append(row(op,cl,d,"SOBTI_5_ET","NY_LONDON_LIT",
                           aware(d,8,0,NY),aware(d,14,30,NY)))
            sob.append(row(op,cl,d,"SOBTI_5_ET","US_LATE_LIT",
                           aware(d,14,30,NY),aware(d,21,0,NY)))
        d+=timedelta(days=1)

    wgc=pd.DataFrame(wgc); sob=pd.DataFrame(sob)
    pw=OUT/"labels_wgc2026_ny3_2023_2025.csv"
    ps=OUT/"labels_sobti5_et_2023_2025.csv"
    wgc.to_csv(pw,index=False); sob.to_csv(ps,index=False)

    # Target clock audit: demonstrate winter/summer and US/UK mismatch periods.
    audit=[]
    probes=[date(2023,1,17),date(2023,3,13),date(2023,3,20),date(2023,3,27),
            date(2023,7,17),date(2023,10,30),date(2023,11,6),
            date(2024,1,16),date(2024,3,11),date(2024,3,25),date(2024,4,1),
            date(2024,7,15),date(2024,10,28),date(2024,11,4),
            date(2025,1,15),date(2025,3,10),date(2025,3,24),date(2025,3,31),
            date(2025,7,15),date(2025,10,27),date(2025,11,3)]
    for d0 in probes:
        for name,t in [
          ("WGC_ASIA_START",aware(d0,18,0,NY)),
          ("WGC_EUROPE_START",aware(d0,3,0,NY)),
          ("WGC_US_START",aware(d0,8,0,NY)),
          ("WGC_US_END",aware(d0,17,0,NY)),
          ("SOBTI_NYLON_START",aware(d0,8,0,NY)),
          ("SOBTI_NYLON_END",aware(d0,14,30,NY)),
        ]:
            u=t.tz_convert("UTC")
            audit.append({"date":d0.isoformat(),"marker":name,
                          "utc":u.isoformat(),"new_york":loc(u,NY),
                          "london":loc(u,LON),"shanghai":loc(u,SHA),"istanbul":loc(u,IST)})
    pa=OUT/"clock_probe_audit.csv"; pd.DataFrame(audit).to_csv(pa,index=False)

    summary={
      "status":"CORRECTED_SESSION_LABEL_GATE_V2",
      "raw_file":RAW.name,
      "raw_sha256":sha256_file(RAW),
      "label_window":"2023-01-01..2025-12-31",
      "eligible_dates":"MONDAY_TO_FRIDAY; holidays remain explicit missing-boundary cases",
      "boundary_rule":"OPEN_AT_T; if absent, PREV_15M_CLOSE_AT_T only when exact T-15 bar exists; otherwise MISSING",
      "boundary_fallback_scope":"SESSION_DIRECTION attribution only; never an executable-entry backfill",
      "partitions":{
        "WGC_2026_NY3":"18:00-03:00 / 03:00-08:00 / 08:00-17:00 America/New_York, date-aware",
        "SOBTI_5_ET":"21:00-23:30(prev date), 01:30-03:30, 03:30-08:00, 08:00-14:30, 14:30-21:00 America/New_York"
      },
      "coverage":{"WGC_2026_NY3":coverage(wgc),"SOBTI_5_ET":coverage(sob)},
      "source_regime":source_regime(x),
      "hashes":{
        pw.name:sha256_file(pw),
        ps.name:sha256_file(ps),
        pa.name:sha256_file(pa)
      },
      "guardrails":[
        "Old fixed-UTC WGC3 label file is superseded.",
        "Old hybrid modern-SGE two-subsession clock is superseded.",
        "No 2026 outcome was used to tune a boundary.",
        "WGC and Sobti partitions are external analytical candidates, not universal market-open definitions."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    md=[
      "# GOLD SESSION LABEL V2 RESULT — 2026-10-06","",
      "**Status:** corrected clock/data gate",
      f"- Raw SHA256: `{summary['raw_sha256']}`",
      "- WGC candidate: **18:00–03:00 / 03:00–08:00 / 08:00–17:00 New York, DST-aware**",
      "- Sobti candidate: **five ET zones, DST-aware**",
      "- Eligible dates: Monday–Friday; holidays are not imputed.",
      "- Boundary fallback: exact previous 15m close only when it ends exactly at T; attribution only.",
      "- Old fixed-UTC WGC3 labels: **SUPERSEDED / DO NOT TRAIN**",
      ""
    ]
    (OUT/"result.md").write_text("\n".join(md))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
