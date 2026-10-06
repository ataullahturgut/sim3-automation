from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"XAU15M_HOUR_COVERAGE_AUDIT_OUT"; OUT.mkdir(exist_ok=True)

def main():
    x=pd.read_csv(RAW)
    x["dt_utc"]=pd.to_datetime(x["dt_utc"],utc=True)
    x["date"]=x.dt_utc.dt.strftime("%Y-%m-%d")
    x["year"]=x.dt_utc.dt.year
    x["month"]=x.dt_utc.dt.strftime("%Y-%m")
    x["hour"]=x.dt_utc.dt.hour
    x["minute"]=x.dt_utc.dt.minute
    x["hm"]=x.dt_utc.dt.strftime("%H:%M")

    # restrict core 2023-2025
    c=x[(x.dt_utc>=pd.Timestamp("2023-01-01",tz="UTC"))&(x.dt_utc<pd.Timestamp("2026-01-01",tz="UTC"))].copy()

    hour_rows=(c.groupby(["year","hour"]).size().rename("rows").reset_index())
    hour_dates=(c.groupby(["year","hour"])["date"].nunique().rename("dates_with_any_bar").reset_index())
    h=hour_rows.merge(hour_dates,on=["year","hour"],how="outer").sort_values(["year","hour"])
    h.to_csv(OUT/"hour_coverage.csv",index=False)

    # Exact candidate boundaries.
    marks=["01:30","03:30","07:00","08:00","12:00","13:00","14:30","18:30","19:30","21:00","22:00","23:30"]
    m=[]
    for yr in [2023,2024,2025]:
        g=c[c.year==yr]
        for hm in marks:
            ds=set(g.loc[g.hm==hm,"date"])
            m.append({"year":yr,"hm":hm,"dates_with_exact_bar":len(ds)})
    pd.DataFrame(m).to_csv(OUT/"exact_boundary_coverage.csv",index=False)

    daily=(c.groupby("date").agg(
        year=("year","first"),
        n=("dt_utc","size"),
        first_utc=("dt_utc","min"),
        last_utc=("dt_utc","max")
    ).reset_index())
    daily["first_hm"]=pd.to_datetime(daily.first_utc,utc=True).dt.strftime("%H:%M")
    daily["last_hm"]=pd.to_datetime(daily.last_utc,utc=True).dt.strftime("%H:%M")
    daily.to_csv(OUT/"daily_coverage.csv",index=False)

    monthly=(c.groupby("month").agg(
        rows=("dt_utc","size"),
        active_dates=("date","nunique")
    ).reset_index())
    monthly["median_bars_active_date"]=monthly["month"].map(
        daily.assign(month=daily["date"].str[:7]).groupby("month")["n"].median()
    )
    monthly["min_bars_active_date"]=monthly["month"].map(
        daily.assign(month=daily["date"].str[:7]).groupby("month")["n"].min()
    )
    monthly["max_bars_active_date"]=monthly["month"].map(
        daily.assign(month=daily["date"].str[:7]).groupby("month")["n"].max()
    )
    monthly.to_csv(OUT/"monthly_coverage.csv",index=False)

    summary={"status":"XAU15M_UTC_HOUR_COVERAGE_AUDIT"}
    summary["yearly"]={}
    for yr in [2023,2024,2025]:
        g=c[c.year==yr]
        d=daily[daily.year==yr]
        summary["yearly"][str(yr)]={
            "rows":int(len(g)),
            "active_dates":int(g.date.nunique()),
            "median_bars_active_date":float(d.n.median()),
            "p10_bars_active_date":float(d.n.quantile(.1)),
            "p90_bars_active_date":float(d.n.quantile(.9)),
            "first_hm_modes":d.first_hm.value_counts().head(8).to_dict(),
            "last_hm_modes":d.last_hm.value_counts().head(8).to_dict(),
            "exact_21_00_dates":int(g.loc[g.hm=="21:00","date"].nunique()),
            "exact_22_00_dates":int(g.loc[g.hm=="22:00","date"].nunique()),
            "exact_12_00_dates":int(g.loc[g.hm=="12:00","date"].nunique()),
            "exact_07_00_dates":int(g.loc[g.hm=="07:00","date"].nunique()),
        }
    # Detect structural change by monthly median.
    summary["monthly"]=monthly.to_dict("records")
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__": main()
