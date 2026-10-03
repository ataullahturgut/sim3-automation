from __future__ import annotations
import json, math, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_daily_average_semantic_audit_out"))
OUT.mkdir(parents=True,exist_ok=True)
KEY=os.environ["TWELVE_DATA_API_KEY"]
FROZEN=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"
PATCH_DATE=pd.Timestamp("2026-02-27")
PATCH_GOLD=5183.80

def fetch_month(start,end):
    params={
      "symbol":"XAU/USD","interval":"1h","start_date":start,"end_date":end,
      "timezone":"UTC","order":"ASC","outputsize":5000,"apikey":KEY
    }
    for a in range(5):
      r=requests.get("https://api.twelvedata.com/time_series",params=params,timeout=60)
      try: j=r.json()
      except Exception: j={}
      if r.status_code==429 or j.get("code")==429:
        if a==4: raise RuntimeError("RATE_LIMIT")
        time.sleep(65); continue
      if r.status_code!=200 or not j.get("values"):
        raise RuntimeError(f"FETCH_FAIL {start} {end} {r.status_code} {str(j)[:500]}")
      rows=[]
      for z in j["values"]:
        try: rows.append((pd.Timestamp(z["datetime"],tz="UTC"),float(z["close"])))
        except Exception: pass
      return pd.DataFrame(rows,columns=["ts","close"]).sort_values("ts")
    raise RuntimeError("FETCH_LOOP")

def main():
    chunks=[]
    for m in range(1,10):
      start=pd.Timestamp(2026,m,1)
      end=(start+pd.offsets.MonthEnd(1)).normalize()+pd.Timedelta(hours=23)
      x=fetch_month(start.strftime("%Y-%m-%d %H:%M:%S"),end.strftime("%Y-%m-%d %H:%M:%S"))
      chunks.append(x)
      time.sleep(8)
    h=pd.concat(chunks,ignore_index=True).sort_values("ts").drop_duplicates("ts")
    h["date"]=h.ts.dt.tz_localize(None).dt.normalize()
    d=h.groupby("date").agg(twelve_hourly_mean=("close","mean"),hour_n=("close","size"),
                             twelve_min=("close","min"),twelve_max=("close","max")).reset_index()
    d.to_csv(OUT/"twelve_utc_daily_hourly_means.csv",index=False)

    f=pd.read_csv(FROZEN)
    f["date"]=pd.to_datetime(f.date).dt.normalize()
    f=f[(f.date>=pd.Timestamp("2026-01-01"))&(f.date<=pd.Timestamp("2026-09-30"))].copy()
    f["gold_original"]=pd.to_numeric(f.gold,errors="coerce")
    f["gold_clean"]=f.gold_original
    f.loc[f.date==PATCH_DATE,"gold_clean"]=PATCH_GOLD

    q=f.merge(d,on="date",how="left")
    q=q.dropna(subset=["twelve_hourly_mean"]).copy()
    q["log_ratio_original"]=np.log(q.gold_original/q.twelve_hourly_mean)
    q["log_ratio_clean"]=np.log(q.gold_clean/q.twelve_hourly_mean)
    med=float(q.log_ratio_clean.median())
    q["dev_clean"]=np.abs(np.expm1(q.log_ratio_clean-med))
    q["dev_original"]=np.abs(np.expm1(q.log_ratio_original-med))
    q["inside_twelve_intraday_range_clean"]=(q.gold_clean>=q.twelve_min)&(q.gold_clean<=q.twelve_max)
    q.to_csv(OUT/"stak_vs_twelve_daily_average.csv",index=False)

    flags=q[(q.dev_clean>=.02)|(~q.inside_twelve_intraday_range_clean)].copy().sort_values("dev_clean",ascending=False)
    flags.to_csv(OUT/"stak_vs_twelve_daily_average_flags.csv",index=False)

    # H3 direction using same frozen weekday clock but Twelve UTC daily means.
    q2=f[["date","gold_clean"]].merge(d[["date","twelve_hourly_mean"]],on="date",how="left")
    q2["target_date_h3"]=q2.date.shift(-3)
    q2["stak_r3"]=np.log(q2.gold_clean.shift(-3)/q2.gold_clean)
    means=dict(zip(d.date,d.twelve_hourly_mean))
    q2["td_start"]=q2.date.map(means)
    q2["td_end"]=q2.target_date_h3.map(means)
    q2["td_r3"]=np.log(q2.td_end/q2.td_start)
    t=q2.dropna(subset=["stak_r3","td_r3"]).copy()
    t["stak_dir"]=(t.stak_r3>0).astype(int)
    t["td_dir"]=(t.td_r3>0).astype(int)
    t["disagree"]=t.stak_dir!=t.td_dir
    t["both_ge_0_5"]=(t.stak_r3.abs()>=.005)&(t.td_r3.abs()>=.005)
    t["both_ge_1"]=(t.stak_r3.abs()>=.01)&(t.td_r3.abs()>=.01)
    t.to_csv(OUT/"h3_daily_average_target_comparison.csv",index=False)
    dis=t[t.disagree].copy()
    dis.to_csv(OUT/"h3_daily_average_target_disagreements.csv",index=False)

    summary={
      "schema":"GOLD_H3_DAILY_AVERAGE_SEMANTIC_AUDIT_V1",
      "hourly_rows":int(len(h)),
      "daily_overlap_n":int(len(q)),
      "median_stak_to_twelve_mean_ratio":float(math.exp(med)),
      "dev_ge_1pct_n":int((q.dev_clean>=.01).sum()),
      "dev_ge_2pct_n":int((q.dev_clean>=.02).sum()),
      "dev_ge_3pct_n":int((q.dev_clean>=.03).sum()),
      "dev_ge_5pct_n":int((q.dev_clean>=.05).sum()),
      "max_dev_pct":float(100*q.dev_clean.max()),
      "max_dev_date":str(q.loc[q.dev_clean.idxmax(),"date"].date()),
      "outside_intraday_range_n":int((~q.inside_twelve_intraday_range_clean).sum()),
      "target_overlap_n":int(len(t)),
      "target_direction_disagree_n":int(t.disagree.sum()),
      "target_direction_disagree_pct":float(100*t.disagree.mean()) if len(t) else None,
      "target_disagree_both_ge_0_5_n":int((t.disagree&t.both_ge_0_5).sum()),
      "target_disagree_both_ge_1_n":int((t.disagree&t.both_ge_1).sum()),
    }
    (OUT/"daily_average_semantic_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 DAILY-AVERAGE SEMANTIC AUDIT — 2026-10-03","",
      "Comparator: Twelve Data XAU/USD 1h, requested in UTC, aggregated to arithmetic mean of hourly closes per UTC calendar day. "
      "This is a cross-provider approximation to the StakTrakr STRK-403 full-UTC-day-average semantic.","",
      "## Level audit","",
      f"- hourly observations: **{len(h)}**",
      f"- weekday daily overlaps: **{len(q)}**",
      f"- median Stak / Twelve-hourly-mean ratio: **{math.exp(med):.6f}**",
      f"- clean deviations >=1%: **{int((q.dev_clean>=.01).sum())}**",
      f"- >=2%: **{int((q.dev_clean>=.02).sum())}**",
      f"- >=3%: **{int((q.dev_clean>=.03).sum())}**",
      f"- >=5%: **{int((q.dev_clean>=.05).sum())}**",
      f"- max deviation: **{100*q.dev_clean.max():.2f}%** on **{q.loc[q.dev_clean.idxmax(),'date'].date()}**",
      f"- clean Stak value outside Twelve hourly min/max: **{int((~q.inside_twelve_intraday_range_clean).sum())}**","",
      "## H3 direction using matched daily-average semantics","",
      f"- comparable origins: **{len(t)}**",
      f"- direction disagreements: **{int(t.disagree.sum())} ({100*t.disagree.mean():.2f}%)**",
      f"- disagreements with both |H3| >=0.5%: **{int((t.disagree&t.both_ge_0_5).sum())}**",
      f"- disagreements with both |H3| >=1.0%: **{int((t.disagree&t.both_ge_1).sum())}**","",
      "## Flagged daily levels","",
      "| Date | Clean Stak | Twelve mean | Hour n | Twelve min | max | Deviation | In range |",
      "|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in flags.head(50).itertuples():
      lines.append(f"| {r.date.date()} | {r.gold_clean:.2f} | {r.twelve_hourly_mean:.2f} | {r.hour_n} | {r.twelve_min:.2f} | {r.twelve_max:.2f} | {100*r.dev_clean:.2f}% | {bool(r.inside_twelve_intraday_range_clean)} |")
    lines += ["","## Direction disagreements","",
      "| Start | End | Stak H3 | Twelve-mean H3 |",
      "|---|---|---:|---:|"]
    for r in dis.head(80).itertuples():
      lines.append(f"| {r.date.date()} | {r.target_date_h3.date()} | {100*r.stak_r3:+.3f}% | {100*r.td_r3:+.3f}% |")
    (OUT/"DAILY_AVERAGE_SEMANTIC_AUDIT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"DAILY_AVERAGE_SEMANTIC_AUDIT.md").read_text())

if __name__=="__main__": main()
