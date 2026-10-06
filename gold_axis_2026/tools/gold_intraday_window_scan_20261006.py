from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"INTRADAY_WINDOW_SCAN_OUT"
OUT.mkdir(exist_ok=True)
SIGNAL_FILE=AX/"GOLD_EXECUTION_CHANNEL_AUDIT_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"
START="2026-08-04"
END="2026-09-25"

def twelve_15m():
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key: raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    params={
      "symbol":"XAU/USD","interval":"15min","timezone":NY,"order":"ASC",
      "outputsize":5000,"apikey":key,
      "start_date":"2026-08-04 00:00:00","end_date":"2026-09-25 23:59:59"
    }
    r=requests.get("https://api.twelvedata.com/time_series",params=params,timeout=90)
    r.raise_for_status()
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(f"TWELVE_EMPTY {j}")
    rows=[]
    for z in vals:
        try:
            rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
        except Exception: pass
    return pd.DataFrame(rows).sort_values("dt").drop_duplicates("dt",keep="last").reset_index(drop=True), j.get("meta",{})

def compound(rs):
    rs=[float(x) for x in rs if np.isfinite(x)]
    return float(np.prod(1+np.array(rs))-1) if rs else np.nan

def max_dd_from_trade_returns(rs):
    w=1.0; peak=1.0; mdd=0.0
    for r in rs:
        if not np.isfinite(r): continue
        w*=1+r; peak=max(peak,w); mdd=min(mdd,w/peak-1)
    return float(mdd)

def main():
    sig=pd.read_csv(SIGNAL_FILE)
    days=sig.loc[sig.cpg_up==True,"date"].astype(str).tolist()
    x,meta=twelve_15m()
    x["date"]=x.dt.dt.strftime("%Y-%m-%d")
    x["hm"]=x.dt.dt.strftime("%H:%M")
    by={(r.date,r.hm):r for r in x.itertuples(index=False)}

    # Signal is available at 08:00 New York. Search only causally executable
    # fixed windows at/after 08:00, no entries before the decision time.
    grid=pd.date_range("08:00","16:00",freq="15min").strftime("%H:%M").tolist()
    rows=[]
    for i,ent in enumerate(grid[:-1]):
        for ex in grid[i+1:]:
            # require at least 30 min holding to avoid a single-bar artifact
            t0=pd.Timestamp("2000-01-01 "+ent); t1=pd.Timestamp("2000-01-01 "+ex)
            hold=(t1-t0).total_seconds()/60
            if hold<30: continue
            rets=[]; valid_days=[]
            for d in days:
                a=by.get((d,ent)); b=by.get((d,ex))
                if a is None or b is None: continue
                r=float(b.open)/float(a.open)-1.0
                rets.append(r); valid_days.append(d)
            if len(rets)<10: continue
            aug=[r for d,r in zip(valid_days,rets) if d.startswith("2026-08")]
            sep=[r for d,r in zip(valid_days,rets) if d.startswith("2026-09")]
            rows.append({
              "entry_ny":ent,"exit_ny":ex,"hold_min":int(hold),"n":len(rets),
              "compound":compound(rets),"mean":float(np.mean(rets)),"median":float(np.median(rets)),
              "hit_rate":float(np.mean(np.array(rets)>0)),
              "max_drawdown":max_dd_from_trade_returns(rets),
              "aug_compound":compound(aug),"sep_compound":compound(sep),
              "worst_month_compound":min(compound(aug),compound(sep)),
              "min_trade":float(np.min(rets)),"max_trade":float(np.max(rets)),
            })
    res=pd.DataFrame(rows)
    res=res.sort_values(["compound","worst_month_compound","hit_rate"],ascending=False).reset_index(drop=True)

    # Robust windows: positive in both Aug and Sep, >=60% hit rate.
    robust=res[(res.aug_compound>0)&(res.sep_compound>0)&(res.hit_rate>=0.60)].copy()
    robust=robust.sort_values(["worst_month_compound","compound","hit_rate"],ascending=False).reset_index(drop=True)

    # GLDTR-compatible NY overlap: 08:30-10:30 NY corresponds to approx
    # 15:30-17:30 Istanbul for this Aug-Sep DST window.
    overlap=res[(res.entry_ny>="08:30")&(res.exit_ny<="10:30")].copy()
    overlap=overlap.sort_values(["compound","worst_month_compound"],ascending=False).reset_index(drop=True)

    # Entry fixed exactly at signal time (08:00): useful if execution can be immediate.
    fixed08=res[res.entry_ny=="08:00"].sort_values("compound",ascending=False).reset_index(drop=True)

    res.to_csv(OUT/"all_windows.csv",index=False)
    robust.head(100).to_csv(OUT/"robust_windows.csv",index=False)
    overlap.head(100).to_csv(OUT/"gldtr_overlap_windows.csv",index=False)
    fixed08.to_csv(OUT/"fixed_0800_exit_scan.csv",index=False)

    best=res.iloc[0].to_dict()
    best_robust=robust.iloc[0].to_dict() if len(robust) else None
    best_overlap=overlap.iloc[0].to_dict() if len(overlap) else None
    best_fixed08=fixed08.iloc[0].to_dict() if len(fixed08) else None

    # Per-day details for selected windows.
    selected={"raw_best":best,"robust_best":best_robust,"gldtr_overlap_best":best_overlap,"fixed08_best":best_fixed08}
    details=[]
    for label,w in selected.items():
        if not w: continue
        for d in days:
            a=by.get((d,w["entry_ny"])); b=by.get((d,w["exit_ny"]))
            if a is None or b is None: continue
            details.append({
              "window":label,"date":d,"entry_ny":w["entry_ny"],"exit_ny":w["exit_ny"],
              "entry_price":float(a.open),"exit_price":float(b.open),
              "ret":float(b.open)/float(a.open)-1.0
            })
    pd.DataFrame(details).to_csv(OUT/"selected_window_daily_details.csv",index=False)

    summary={
      "status":"RETROSPECTIVE_INTRADAY_WINDOW_DISCOVERY_NOT_PROSPECTIVE_RULE",
      "signal_count":len(days),"signal_dates":days,"xau_meta":meta,
      "constraints":{"signal_time_ny":"08:00","search_start_ny":"08:00","search_end_ny":"16:00","grid":"15min","min_hold_min":30},
      "raw_best":best,
      "robust_best_positive_both_months_hit_ge_60pct":best_robust,
      "gldtr_overlap_best_0830_1030_ny":best_overlap,
      "fixed_0800_entry_best_exit":best_fixed08,
      "warning":"This is an ex-post discovery scan over 12 signals. The winning window must not be promoted to a production rule without older-period/backtest or forward validation."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
