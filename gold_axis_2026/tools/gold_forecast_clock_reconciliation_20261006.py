from __future__ import annotations
import json, os, time, calendar
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"FORECAST_CLOCK_RECON_OUT"; OUT.mkdir(exist_ok=True)
PANEL=AX/"GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"

def chunks():
    out=[]; cur=pd.Timestamp("2025-06-30"); end=pd.Timestamp("2026-09-27")
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end)
        out.append((str(cur.date())+" 00:00:00",str(b.date())+" 23:59:59"))
        cur=b+pd.Timedelta(days=1)
    return out

def fetch(a,b):
    p={"symbol":"XAU/USD","interval":"15min","timezone":NY,"order":"ASC",
       "outputsize":5000,"apikey":os.environ["TWELVE_DATA_API_KEY"],
       "start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str({"a":a,"b":b,"status":r.status_code,"response":j}))
    rows=[]
    for z in vals:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"])})
        except: pass
    return pd.DataFrame(rows)

def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def compound(v):
    a=np.asarray(v,float)
    return float(np.prod(1+a)-1) if len(a) else None

def summarize(g,col,signal_col="signal"):
    r=g[col].dropna()
    if not len(r): return {}
    idx=r.index
    actual=np.where(r.to_numpy(float)>0,1,0)
    sig=g.loc[idx,signal_col].to_numpy(int)
    return {
      "n":int(len(r)),
      "compound":compound(r.to_numpy(float)),
      "mean":float(r.mean()),
      "median":float(r.median()),
      "positive_share":float((r>0).mean()),
      "signal_direction_accuracy":float((sig==actual).mean()),
      "up_signal_n":int((sig==1).sum()),
      "down_signal_n":int((sig==0).sum())
    }

def exact(M,d,hm):
    return M.get((d,hm))

def main():
    sig=pd.read_csv(PANEL)
    sig["consensus"]=sig.consensus.astype(str).str.lower().eq("true")
    sig=sig[(sig.issue_date>="2025-07-01")&(sig.issue_date<="2026-09-25")&sig.consensus].copy()
    sig["signal"]=sig.v5.astype(int)
    sig["period"]=sig.issue_date.map(period)

    parts=[]
    for a,b in chunks():
        parts.append(fetch(a,b)); time.sleep(8)
    x=pd.concat(parts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    x["date"]=x.dt.dt.strftime("%Y-%m-%d")
    x["hm"]=x.dt.dt.strftime("%H:%M")
    M={(r.date,r.hm):float(r.open) for r in x.itertuples(index=False)}

    rows=[]
    for r in sig.itertuples(index=False):
        issue=str(r.issue_date); cutoff=str(r.feature_cutoff_date)
        # Theoretical earliest price-clock proxy from prior audits:
        # next UTC midnight after cutoff = usually 20:00 NY EDT / 19:00 NY EST.
        avail=pd.Timestamp(cutoff,tz="UTC")+pd.Timedelta(days=1)
        avail_ny=avail.tz_convert(NY)
        ad=avail_ny.strftime("%Y-%m-%d"); ah=avail_ny.strftime("%H:%M")
        p_ready=exact(M,ad,ah)
        p08=exact(M,issue,"08:00")
        p20=exact(M,issue,"20:00")
        if p_ready is None or p08 is None or p20 is None:
            continue
        ts_ready=avail_ny
        ts_issue=pd.Timestamp(issue+" 08:00:00",tz=NY)
        ts20=pd.Timestamp(issue+" 20:00:00",tz=NY)
        tr_ready=ts_ready.tz_convert("Europe/Istanbul")
        tr_issue=ts_issue.tz_convert("Europe/Istanbul")
        tr20=ts20.tz_convert("Europe/Istanbul")
        rows.append({
          "issue_date":issue,"feature_cutoff_date":cutoff,"period":r.period,
          "signal":int(r.signal),"signal_name":"UP" if int(r.signal)==1 else "DOWN",
          "theoretical_ready_ny":ts_ready.isoformat(),
          "theoretical_ready_tr":tr_ready.isoformat(),
          "governed_issue_ny":ts_issue.isoformat(),
          "governed_issue_tr":tr_issue.isoformat(),
          "day_end_ny":ts20.isoformat(),
          "day_end_tr":tr20.isoformat(),
          "px_ready":p_ready,"px_08":p08,"px_20":p20,
          "ret_ready_to_08":p08/p_ready-1,
          "ret_08_to_20":p20/p08-1,
          "ret_ready_to_20":p20/p_ready-1
        })
    z=pd.DataFrame(rows)
    z.to_csv(OUT/"clock_rows.csv",index=False)

    summary={}
    for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        g=z[z.period==pp]
        summary[pp]={
          "n":int(len(g)),
          "theoretical_ready_to_governed_08":summarize(g,"ret_ready_to_08"),
          "governed_08_to_20":summarize(g,"ret_08_to_20"),
          "theoretical_ready_to_20":summarize(g,"ret_ready_to_20"),
        }
        for state,name in [(1,"UP"),(0,"DOWN")]:
            q=g[g.signal==state]
            summary[pp][name]={
              "n":int(len(q)),
              "ready_to_08":summarize(q,"ret_ready_to_08"),
              "08_to_20":summarize(q,"ret_08_to_20"),
              "ready_to_20":summarize(q,"ret_ready_to_20")
            }

    # clock ranges actually observed under DST
    clock_ranges={
      "theoretical_ready_istanbul":sorted(z.theoretical_ready_tr.map(lambda s: pd.Timestamp(s).strftime("%H:%M")).unique().tolist()),
      "governed_08_istanbul":sorted(z.governed_issue_tr.map(lambda s: pd.Timestamp(s).strftime("%H:%M")).unique().tolist()),
      "ny20_istanbul":sorted(z.day_end_tr.map(lambda s: pd.Timestamp(s).strftime("%H:%M")).unique().tolist())
    }

    out={
      "status":"RETROSPECTIVE_FORECAST_CLOCK_RECONCILIATION_NOT_PROSPECTIVE",
      "scope":"raw CIG-D1 4/4 consensus, 2025-07-01..2026-09-25",
      "clock_contract":{
        "feature_hourly_anchor":"16:00 America/New_York on feature_cutoff_date",
        "theoretical_daily_reference_ready":"next UTC midnight after feature_cutoff_date; only a lower-bound clock proxy, not proof all sources were ready",
        "governed_issue_deadline":"08:00 America/New_York on issue_date",
        "historical_actual_issued_at":"not available for retrospective rows"
      },
      "clock_ranges":clock_ranges,
      "summary":summary,
      "guardrails":[
        "Do not call theoretical_ready the actual historical issuance time.",
        "Do not count ready_to_08 movement as post-signal P&L under the governed 08:00 issue contract.",
        "08_to_20 is the clean same-day post-governed-issue clock comparison used here.",
        "These are gross XAU/USD spot moves, not instrument-specific net returns."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
