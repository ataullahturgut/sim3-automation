from __future__ import annotations

import json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "EXECUTION_CHANNEL_AUDIT_OUT"
OUT.mkdir(exist_ok=True)

START = "2026-08-04"
END = "2026-09-25"
CPG_TRES_THRESHOLD = 0.164484
NY = "America/New_York"
IST = "Europe/Istanbul"

SAGE_FILE = AX / "GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
V5_FILE = AX / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT_FILE = AX / "GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA_FILE = AX / "GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
PX_FILE = AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"

def yahoo_chart(symbol: str, interval: str, p1: str, p2: str):
    t1 = int(pd.Timestamp(p1, tz="UTC").timestamp())
    t2 = int(pd.Timestamp(p2, tz="UTC").timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{requests.utils.quote(symbol, safe='')}?"
    url += f"period1={t1}&period2={t2}&interval={interval}&events=history&includeAdjustedClose=true"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=60)
    r.raise_for_status()
    j = r.json()
    res = j.get("chart",{}).get("result")
    if not res:
        raise RuntimeError(f"YAHOO_FAIL_{symbol}_{interval}: {j}")
    x = res[0]
    ts = x.get("timestamp") or []
    q = (x.get("indicators",{}).get("quote") or [{}])[0]
    meta = x.get("meta",{})
    tz = meta.get("exchangeTimezoneName") or IST
    rows = []
    for i,t in enumerate(ts):
        rec = {"ts": pd.Timestamp(t, unit="s", tz="UTC").tz_convert(tz)}
        ok = False
        for k in ["open","high","low","close","volume"]:
            vals = q.get(k) or []
            v = vals[i] if i < len(vals) else None
            rec[k] = np.nan if v is None else float(v)
            if k in ("open","close") and v is not None:
                ok = True
        if ok:
            rows.append(rec)
    df = pd.DataFrame(rows)
    return df, {"url":url, "timezone":tz, "meta":meta}

def twelve_intraday():
    key = os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    api = "https://api.twelvedata.com/time_series"
    base = {
        "symbol":"XAU/USD",
        "timezone":NY,
        "order":"ASC",
        "outputsize":5000,
        "apikey":key,
        "start_date":"2026-08-04 00:00:00",
        "end_date":"2026-09-25 23:59:59",
    }
    last_err = None
    for interval in ["15min","30min","1h"]:
        params = dict(base, interval=interval)
        for attempt in range(4):
            r = requests.get(api, params=params, timeout=90)
            try:
                j = r.json()
            except Exception:
                j = {"status":"error","message":r.text[:200]}
            if r.status_code == 429 or (isinstance(j,dict) and j.get("code")==429):
                time.sleep(65)
                continue
            vals = j.get("values") if isinstance(j,dict) else None
            if r.status_code == 200 and vals:
                rows=[]
                for z in vals:
                    try:
                        dt=pd.Timestamp(z["datetime"])
                        rows.append({
                            "dt":dt,
                            "open":float(z["open"]),
                            "high":float(z["high"]),
                            "low":float(z["low"]),
                            "close":float(z["close"]),
                        })
                    except Exception:
                        pass
                df=pd.DataFrame(rows).sort_values("dt").drop_duplicates("dt",keep="last")
                if len(df):
                    return df, {"interval":interval,"n":int(len(df)),"meta":j.get("meta",{})}
            last_err = {"interval":interval,"http":r.status_code,"payload":j}
            break
    raise RuntimeError(f"TWELVE_INTRADAY_FAIL {last_err}")

def exact_or_near(df: pd.DataFrame, d: str, hhmm: str, field: str, tol_min: int):
    target = pd.Timestamp(f"{d} {hhmm}:00")
    z = df.copy()
    z["delta"] = (z["dt"] - target).abs()
    z = z[z["delta"] <= pd.Timedelta(minutes=tol_min)].sort_values(["delta","dt"])
    if z.empty:
        return np.nan, None
    r = z.iloc[0]
    return float(r[field]), str(r["dt"])

def build_signal_panel():
    sage=pd.read_csv(SAGE_FILE)
    v5=pd.read_csv(V5_FILE)
    rift=pd.read_csv(RIFT_FILE)
    vega=pd.read_csv(VEGA_FILE)

    for x in [sage,v5,rift,vega]:
        x["forecast_issue_date"]=pd.to_datetime(x["forecast_issue_date"]).dt.strftime("%Y-%m-%d")

    S=sage.set_index("forecast_issue_date")
    V=v5.set_index("forecast_issue_date")
    R=rift.set_index("forecast_issue_date")
    G=vega.set_index("forecast_issue_date")

    issue_dates=sorted(d for d in V.index.unique() if START <= d <= END and d in R.index and d in G.index)
    rows=[]
    for d in issue_dates:
        vr=V.loc[d]
        rr=R.loc[d]
        gr=G.loc[d]
        v=int(float(vr["p_helios_v5_dce"])>=0.5)
        r=int(float(rr["p_rift"])>=0.5)
        g=int(float(gr["p_vega"])>=0.5)
        sage_present=d in S.index
        if sage_present:
            sr=S.loc[d]
            if isinstance(sr,pd.DataFrame): sr=sr.iloc[-1]
            s=int(float(sr["assisted_pred_forced"]))
            frev=float(sr["F_reversal"])
        else:
            # SAGE V2 is exception-only over V5; if no eligible SAGE row exists,
            # fail-closed KEEP V5 is the operational diagnostic state.
            s=v
            frev=np.nan
        consensus=(s==v==r==g)
        cpg_up=bool(consensus and v==1 and (np.isnan(frev) or frev < CPG_TRES_THRESHOLD))
        rows.append({
            "date":d,"sage":s,"v5":v,"rift":r,"vega":g,
            "sage_row_present":sage_present,"F_reversal":frev,
            "consensus_4of4":consensus,"cpg_up":cpg_up
        })
    return pd.DataFrame(rows)

def daily_gold_close_to_close(panel):
    px=pd.read_csv(PX_FILE)
    px["date"]=pd.to_datetime(px["date"]).dt.strftime("%Y-%m-%d")
    px=px.sort_values("date").reset_index(drop=True)
    prev=dict(zip(px["date"].iloc[1:],px["date"].iloc[:-1]))
    p=px.set_index("date")["gold"].astype(float).to_dict()
    vals=[]
    for d in panel.loc[panel.cpg_up,"date"]:
        pd0=prev.get(d)
        if pd0 is None: continue
        vals.append((d,pd0,p[d]/p[pd0]-1.0))
    wealth=float(np.prod([1+r for _,_,r in vals])) if vals else np.nan
    return wealth-1.0, vals

def compound(rs):
    rs=[float(x) for x in rs if pd.notna(x)]
    return float(np.prod([1+x for x in rs])-1.0) if rs else np.nan

def main():
    panel=build_signal_panel()
    theo, theo_rows=daily_gold_close_to_close(panel)

    xau,xmeta=twelve_intraday()

    # XAU same-day windows on CPG-UP dates.
    x_rows=[]
    for d in panel.loc[panel.cpg_up,"date"]:
        p08,t08=exact_or_near(xau,d,"08:00","open",20)
        p11,t11=exact_or_near(xau,d,"11:00","open",20)
        p16,t16=exact_or_near(xau,d,"16:00","open",20)
        x_rows.append({
            "date":d,"xau_0800":p08,"xau_1100":p11,"xau_1600":p16,
            "ts08":t08,"ts11":t11,"ts16":t16,
            "ret_0800_1100":(p11/p08-1) if np.isfinite(p08) and np.isfinite(p11) else np.nan,
            "ret_0800_1600":(p16/p08-1) if np.isfinite(p08) and np.isfinite(p16) else np.nan,
        })
    xdf=pd.DataFrame(x_rows)

    # Decision-to-decision XAU: hold from 08:00 on each CPG-UP issue date
    # to 08:00 on the next issue date. Consecutive UP days naturally compound.
    all_dates=panel["date"].tolist()
    d2d=[]
    for i,d in enumerate(all_dates[:-1]):
        if not bool(panel.iloc[i]["cpg_up"]):
            continue
        nd=all_dates[i+1]
        p0,t0=exact_or_near(xau,d,"08:00","open",20)
        p1,t1=exact_or_near(xau,nd,"08:00","open",20)
        d2d.append({"date":d,"next_date":nd,"p0":p0,"p1":p1,"ts0":t0,"ts1":t1,
                    "ret":(p1/p0-1) if np.isfinite(p0) and np.isfinite(p1) else np.nan})
    d2d_df=pd.DataFrame(d2d)

    # GLDTR Yahoo daily + hourly. Yahoo does not always expose BIST ETF
    # history. Treat that source as optional so the XAU execution audit is
    # still recorded rather than losing the whole experiment.
    gldtr_error = None
    try:
        gd,gdm=yahoo_chart("GLDTR.IS","1d","2026-08-01","2026-09-28")
        gh,ghm=yahoo_chart("GLDTR.IS","1h","2026-08-01","2026-09-28")
        if gh.empty or "ts" not in gh.columns:
            raise RuntimeError(f"YAHOO_GLDTR_HOURLY_EMPTY hourly_n={len(gh)}")
        gh["date"]=gh["ts"].dt.strftime("%Y-%m-%d")
        gh["hm"]=gh["ts"].dt.strftime("%H:%M")
        if gd.empty or "ts" not in gd.columns:
            # Yahoo currently exposes GLDTR hourly history but may return an
            # empty 1d payload. Reconstruct daily OHLC from the same hourly
            # exchange feed rather than mixing vendors.
            gd=(gh.sort_values("ts").groupby("date",as_index=False)
                  .agg(open=("open","first"),high=("high","max"),
                       low=("low","min"),close=("close","last"),
                       volume=("volume","sum")))
            gd["ts"]=pd.to_datetime(gd["date"]).dt.tz_localize(IST)
            gdm={"timezone":IST,"derived_from":"Yahoo 1h GLDTR.IS"}
        else:
            gd["date"]=gd["ts"].dt.strftime("%Y-%m-%d")

        gl_rows=[]
        for d in panel.loc[panel.cpg_up,"date"]:
            dz=gd[gd.date==d]
            hz=gh[gh.date==d].sort_values("ts")
            if dz.empty:
                gl_rows.append({"date":d})
                continue
            dr=dz.iloc[-1]
            target=pd.Timestamp(f"{d} 15:00",tz=IST)
            hh=hz.copy()
            if len(hh):
                hh["delta"]=(hh["ts"]-target).abs()
                ent=hh.sort_values(["delta","ts"]).iloc[0]
                closecand=hz[hz["ts"].dt.hour <= 18]
                ex=closecand.iloc[-1] if len(closecand) else hz.iloc[-1]
                epx=float(ent["open"]); xpx=float(ex["close"])
                ets=str(ent["ts"]); xts=str(ex["ts"])
            else:
                epx=xpx=np.nan; ets=xts=None
            gl_rows.append({
                "date":d,
                "daily_open":float(dr["open"]),"daily_close":float(dr["close"]),
                "ret_daily_open_close":float(dr["close"])/float(dr["open"])-1,
                "entry_15":epx,"exit_last":xpx,"entry_ts":ets,"exit_ts":xts,
                "ret_15_close":xpx/epx-1 if np.isfinite(epx) and np.isfinite(xpx) else np.nan
            })
        gldf=pd.DataFrame(gl_rows)

        gd2d=[]
        def gl_15_open(d):
            hz=gh[gh.date==d].sort_values("ts")
            if hz.empty: return np.nan,None
            target=pd.Timestamp(f"{d} 15:00",tz=IST)
            zz=hz.copy(); zz["delta"]=(zz["ts"]-target).abs()
            r=zz.sort_values(["delta","ts"]).iloc[0]
            if r["delta"]>pd.Timedelta(minutes=70): return np.nan,None
            return float(r["open"]),str(r["ts"])
        for i,d in enumerate(all_dates[:-1]):
            if not bool(panel.iloc[i]["cpg_up"]):
                continue
            nd=all_dates[i+1]
            p0,t0=gl_15_open(d); p1,t1=gl_15_open(nd)
            gd2d.append({"date":d,"next_date":nd,"p0":p0,"p1":p1,"ts0":t0,"ts1":t1,
                         "ret":(p1/p0-1) if np.isfinite(p0) and np.isfinite(p1) else np.nan})
        gd2d_df=pd.DataFrame(gd2d)
    except Exception as e:
        gldtr_error = str(e)
        gd=pd.DataFrame(columns=["ts","date","open","close"])
        gh=pd.DataFrame(columns=["ts","date","hm","open","close"])
        gdm={"timezone":None}
        ghm={"timezone":None}
        gldf=pd.DataFrame(columns=["date","ret_daily_open_close","ret_15_close"])
        gd2d_df=pd.DataFrame(columns=["date","next_date","ret"])

    summary={
        "status":"RETROSPECTIVE_EXECUTION_AUDIT_NOT_PROSPECTIVE_EVIDENCE",
        "window":{"start":START,"end":END},
        "rule":{
            "identity":"CPG_FILTERED_CIG_D1_RECONSTRUCTION",
            "cpg":"Consensus Precision Governor",
            "consensus":"SAGE+RuleFlow / V5-DCE / RIFT / VEGA all UP",
            "tres_block":f"F_reversal >= {CPG_TRES_THRESHOLD} blocks long",
            "sage_missing_semantics":"exception-only fail-closed KEEP V5",
        },
        "signal_count":int(panel.cpg_up.sum()),
        "signal_dates":panel.loc[panel.cpg_up,"date"].tolist(),
        "returns":{
            "theoretical_prev_close_to_current_close_compound":theo,
            "xau_executable_0800NY_to_1600NY_same_day_compound":compound(xdf["ret_0800_1600"]),
            "xau_executable_0800NY_to_1100NY_bist_window_proxy_compound":compound(xdf["ret_0800_1100"]),
            "xau_decision_to_decision_0800NY_compound":compound(d2d_df["ret"]),
            "gldtr_daily_open_to_close_prior_style_compound":compound(gldf["ret_daily_open_close"]),
            "gldtr_1500IST_to_session_close_compound":compound(gldf["ret_15_close"]),
            "gldtr_decision_to_decision_1500IST_compound":compound(gd2d_df["ret"]),
        },
        "source_meta":{
            "xau":xmeta,
            "gldtr_daily":{"timezone":gdm["timezone"],"n":int(len(gd))},
            "gldtr_hourly":{"timezone":ghm.get("timezone"),"n":int(len(gh)),
                            "sample_times":gh[["date","hm"]].drop_duplicates().head(40).to_dict("records")},
            "gldtr_error":gldtr_error,
        },
        "interpretation_notes":[
            "The 12.3% benchmark uses previous close -> current close on days selected by a signal issued the current day; it is not executable if issuance occurs at 08:00 New York.",
            "The GLDTR daily-open -> close comparison is also pre-issuance for an 08:00 New York / 15:00 Istanbul decision clock.",
            "Decision-to-decision returns are the cleanest implementable comparison: enter at issuance and stay long until the next issue time while CPG-UP remains active.",
            "The XAU 08:00->11:00 New York series is a VIOP-underlying session proxy, not actual F_XAUUSD contract P&L; actual VIOP basis/spread/fees require licensed contract history."
        ]
    }

    panel.to_csv(OUT/"signal_panel.csv",index=False)
    xdf.to_csv(OUT/"xau_same_day.csv",index=False)
    d2d_df.to_csv(OUT/"xau_decision_to_decision.csv",index=False)
    gldf.to_csv(OUT/"gldtr_same_day.csv",index=False)
    gd2d_df.to_csv(OUT/"gldtr_decision_to_decision.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    md=[]
    md.append("# GOLD EXECUTION CHANNEL AUDIT — 2026-10-06")
    md.append("")
    md.append("Evidence class: retrospective execution diagnostic; not prospective OOS evidence.")
    md.append("")
    md.append(f"CPG-UP signals: **{summary['signal_count']}**")
    md.append("")
    for k,v in summary["returns"].items():
        md.append(f"- {k}: **{v*100:.4f}%**" if v is not None and np.isfinite(v) else f"- {k}: NA")
    md.append("")
    md.append("Signal dates: "+", ".join(summary["signal_dates"]))
    md.append("")
    md.append("Key governance note: prior-close/current-close and GLDTR open/close are not executable under the 08:00 New York issuance clock.")
    (OUT/"report.md").write_text("\n".join(md)+"\n")

    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
