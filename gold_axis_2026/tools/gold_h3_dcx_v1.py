from pathlib import Path
import json
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
IFBC=AX/"GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv"
LLRS=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"

OUT_FEATURES=AX/"GOLD_H3_DCX_V1_FEATURES_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_DCX_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_DCX_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_DCX_V1_RESULT_2026-10-04.md"

START=pd.Timestamp("2025-01-01",tz="UTC")
END=pd.Timestamp("2026-10-05",tz="UTC")
CAL_BARS=480
MIN_CAL_BARS=240
EVENT_BARS=240
RANK_N=120
MIN_RANK=60
RANK_TH=.80
RETRACE_TH=.50
DEV_START=pd.Timestamp("2025-07-01")

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def as_bool(x):
    if x.dtype==bool:
        return x
    return x.astype(str).str.lower().isin(["true","1","yes"])

def fetch_gc():
    p1=int(START.timestamp()); p2=int(END.timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/GC%3DF"
        params={"period1":p1,"period2":p2,"interval":"1h","events":"history","includeAdjustedClose":"true"}
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"{host} HTTP {r.status_code}: {r.text[:120]}"
                continue
            j=r.json()["chart"]
            if j.get("error") or not j.get("result"):
                last=f"{host} chart_error={j.get('error')}"
                continue
            z=j["result"][0]
            q=z["indicators"]["quote"][0]
            rows=[]
            for t,c in zip(z.get("timestamp",[]),q.get("close",[])):
                if c is None:
                    continue
                v=float(c)
                if not np.isfinite(v) or v<=0:
                    continue
                rows.append((pd.to_datetime(t,unit="s",utc=True),v))
            if len(rows)<3000:
                last=f"{host} too few rows={len(rows)}"
                continue
            x=pd.DataFrame(rows,columns=["ts","GC_close"]).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
            x["logp"]=np.log(x.GC_close.astype(float))
            x["r6"]=x.logp-x.logp.shift(6)
            return x
        except Exception as e:
            last=f"{host}: {type(e).__name__}: {e}"
    raise RuntimeError(f"GC_FETCH_FAIL {last}")

def cutoff_ts(d):
    return (pd.Timestamp(d.date()).tz_localize("America/New_York")+pd.Timedelta(hours=16)).tz_convert("UTC")

def dc_state(logp,delta):
    a=np.asarray(logp,float)
    if len(a)<2 or not np.isfinite(delta) or delta<=0:
        return None
    high=low=float(a[0])
    mode=0
    extreme=float(a[0])
    confirm=np.nan
    age=0
    event_count=0

    for p in a[1:]:
        p=float(p)
        if mode==0:
            if p>high:
                high=p
            if p<low:
                low=p
            if p-low>=delta:
                mode=1
                confirm=low+delta
                extreme=p
                age=0
                event_count+=1
            elif high-p>=delta:
                mode=-1
                confirm=high-delta
                extreme=p
                age=0
                event_count+=1
        elif mode==1:
            age+=1
            if p>extreme:
                extreme=p
            elif extreme-p>=delta:
                mode=-1
                confirm=extreme-delta
                extreme=p
                age=0
                event_count+=1
        else:
            age+=1
            if p<extreme:
                extreme=p
            elif p-extreme>=delta:
                mode=1
                confirm=extreme+delta
                extreme=p
                age=0
                event_count+=1

    if mode==0 or not np.isfinite(confirm):
        return {
            "dc_mode":0,"event_age_bars":np.nan,"overshoot_ratio":np.nan,
            "retracement_ratio":np.nan,"dc_event_count":event_count
        }

    cur=float(a[-1])
    if mode==1:
        overshoot=max(0.0,extreme-confirm)/delta
        retrace=max(0.0,extreme-cur)/delta
    else:
        overshoot=max(0.0,confirm-extreme)/delta
        retrace=max(0.0,cur-extreme)/delta

    return {
        "dc_mode":int(mode),
        "event_age_bars":int(age),
        "overshoot_ratio":float(overshoot),
        "retracement_ratio":float(retrace),
        "dc_event_count":int(event_count)
    }

def rank_le(hist,v):
    a=np.asarray(hist,float)
    a=a[np.isfinite(a)]
    if len(a)<MIN_RANK or not np.isfinite(v):
        return np.nan
    return float((1+np.sum(a<=v))/(len(a)+1))

def load_h3():
    z=pd.read_csv(H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        z[c]=pd.to_datetime(z[c])
    needed=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","month",
            "y_up","target_r3","momentum_up","v5_pred","rescue_target","opal_override_check"]
    miss=[c for c in needed if c not in z.columns]
    if miss:
        raise RuntimeError(f"H3 missing {miss}")
    return z[needed].sort_values("forecast_issue_date").reset_index(drop=True)

def origin_features(hourly,h3):
    rows=[]
    integrity_fail=0
    for r in h3.itertuples():
        if pd.Timestamp(r.forecast_issue_date)<pd.Timestamp("2025-01-01"):
            continue
        co=cutoff_ts(pd.Timestamp(r.feature_cutoff_date))
        hist=hourly[hourly.ts<=co].copy()
        if hist.empty:
            continue
        stale=(co-hist.ts.iloc[-1]).total_seconds()/3600.0
        if stale<0 or stale>3:
            continue

        cur_idx=hist.index[-1]
        cal=hourly.loc[hourly.index<cur_idx].dropna(subset=["r6"]).tail(CAL_BARS)
        if len(cal)<MIN_CAL_BARS:
            continue
        delta=float(np.median(np.abs(cal.r6.to_numpy(float))))
        if not np.isfinite(delta) or delta<=1e-8:
            continue

        win=hist.tail(EVENT_BARS)
        st=dc_state(win.logp.to_numpy(float),delta)
        if st is None:
            continue

        d={
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"target_r3":float(r.target_r3),
            "momentum_up":int(r.momentum_up),"v5_pred":int(r.v5_pred),
            "rescue_target":int(r.rescue_target),
            "opal_override_check":r.opal_override_check,
            "hourly_cutoff":co,"hourly_source_ts":hist.ts.iloc[-1],
            "hourly_stale_h":float(stale),"delta":delta,
            **st
        }
        rows.append(d)

    q=pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    if q.empty:
        return q,integrity_fail

    q["eligible_base"]=(q.v5_pred.astype(int)==q.momentum_up.astype(int)) & (q.dc_mode!=0) & (
        q.dc_mode.astype(int)==np.where(q.momentum_up.astype(int)==1,1,-1)
    )
    ranks=[]
    for i,r in q.iterrows():
        hist=q.iloc[:i]
        hist=hist[hist.eligible_base].tail(RANK_N)
        ranks.append(rank_le(hist.overshoot_ratio,r.overshoot_ratio))
    q["overshoot_rank"]=ranks
    q["dcx_candidate"]=(
        q.eligible_base
        & (q.overshoot_rank>=RANK_TH)
        & (q.retracement_ratio>=RETRACE_TH)
    )
    q["opal_candidate"]=as_bool(q.opal_override_check)
    q["v5_correct"]=q.v5_pred.astype(int)==q.y_up.astype(int)
    q["dcx_pred"]=np.where(q.dcx_candidate,1-q.v5_pred,q.v5_pred)
    q["dcx_correct"]=q.dcx_pred.astype(int)==q.y_up.astype(int)
    q["block"]=q.forecast_issue_date.map(lambda d:f"{d.year}_{'H1' if d.month<=6 else 'H2'}")
    return q,integrity_fail

def merge_ocs(q):
    i=pd.read_csv(IFBC)
    l=pd.read_csv(LLRS)
    for df in [i,l]:
        df["feature_cutoff_date"]=pd.to_datetime(df.feature_cutoff_date)
    keepi=["feature_cutoff_date","ifbc_score","ifbc_count60"]
    keepl=["feature_cutoff_date","llrs_pressure","llrs_incremental","llrs_external_opposes"]
    z=q.merge(i[keepi],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.merge(l[keepl],on="feature_cutoff_date",how="left",validate="one_to_one")
    z["ocs_candidate"]=(
        (z.v5_pred==z.momentum_up)
        & (z.ifbc_count60>=4)
        & (z.ifbc_score>=.70)
        & as_bool(z.llrs_external_opposes)
        & (z.llrs_incremental>0)
        & (z.llrs_pressure>=.10)
    )
    z["dcx_only"]=z.dcx_candidate & (~z.ocs_candidate)
    z["ocs_only"]=z.ocs_candidate & (~z.dcx_candidate)
    z["overlap"]=z.dcx_candidate & z.ocs_candidate
    z["union_candidate"]=z.dcx_candidate | z.ocs_candidate
    z["union_pred"]=np.where(z.union_candidate,1-z.v5_pred,z.v5_pred)
    z["union_correct"]=z.union_pred.astype(int)==z.y_up.astype(int)
    return z

def stats(g,col):
    c=g[col].fillna(False).astype(bool)
    y=g.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    eligible=max(int((g.v5_pred==g.momentum_up).sum()),1)
    return {
        "candidate_n":n,"rescued":r,"broken":b,"net":r-b,
        "precision":r/max(n,1),"candidate_rate":n/eligible,
        "opal_no_candidate_rescues":int((c&y&(~g.opal_candidate)).sum())
    }

def main():
    hourly=fetch_gc()
    h3=load_h3()
    q,integrity_fail=origin_features(hourly,h3)
    if q.empty:
        raise RuntimeError("No DCX origin features")
    z=merge_ocs(q)
    z.to_csv(OUT_FEATURES,index=False)

    dev=z[z.forecast_issue_date>=DEV_START].copy()
    dcx=stats(dev,"dcx_candidate")
    ocs=stats(dev,"ocs_candidate")
    only=stats(dev,"dcx_only")
    oonly=stats(dev,"ocs_only")
    overlap=stats(dev,"overlap")
    union=stats(dev,"union_candidate")

    blocks=[]
    for block,g in dev.groupby("block",sort=False):
        x=stats(g,"dcx_candidate")
        x["block"]=block
        x["v5_accuracy"]=float(g.v5_correct.mean())
        x["dcx_accuracy"]=float(g.dcx_correct.mean())
        blocks.append(x)
    bdf=pd.DataFrame(blocks)
    bdf.to_csv(OUT_BLOCK,index=False)

    positive=int((bdf.net>0).sum()) if len(bdf) else 0
    worst=int(bdf.net.min()) if len(bdf) else 0
    timeline_fail=int((pd.to_datetime(dev.hourly_source_ts,utc=True)>pd.to_datetime(dev.hourly_cutoff,utc=True)).sum())
    failures=integrity_fail+timeline_fail

    gate=bool(
        dcx["candidate_n"]>=6
        and dcx["precision"]>=.60
        and dcx["net"]>=3
        and dcx["candidate_rate"]<=.12
        and worst>=-1
        and positive>=2
        and only["net"]>0
        and union["net"]>ocs["net"]
        and failures==0
    )
    status="DCX_H3_V1_PROMISING" if gate else "DCX_H3_V1_FAIL"

    summary={
        "schema":"DCX_H3_V1","status":status,
        "historical_status":"development_only",
        "hourly_rows":len(hourly),
        "origin_feature_rows":len(q),"development_rows":len(dev),
        "first_issue":str(dev.forecast_issue_date.min().date()),
        "last_issue":str(dev.forecast_issue_date.max().date()),
        "integrity_failures":failures,
        "dcx":dcx,"ocs_reference":ocs,"dcx_only":only,"ocs_only":oonly,
        "overlap":overlap,"union":union,
        "v5_accuracy":float(dev.v5_correct.mean()),
        "dcx_accuracy":float(dev.dcx_correct.mean()),
        "union_accuracy":float(dev.union_correct.mean()),
        "positive_blocks":positive,"worst_block_net":worst,
        "blocks":blocks,
        "feature_summary":{
            "median_delta":float(dev.delta.median()),
            "median_overshoot":float(dev.overshoot_ratio.median()),
            "median_retracement":float(dev.retracement_ratio.median()),
            "eligible_base_n":int(dev.eligible_base.sum()),
            "rank_available_n":int(dev.overshoot_rank.notna().sum())
        }
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# DCX-H3 V1 — DIRECTIONAL-CHANGE OVERSHOOT EXHAUSTION RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective development/stress-test only.","",
        f"- hourly GC rows: **{len(hourly)}**",
        f"- origin feature rows: **{len(q)}**",
        f"- development rows: **{len(dev)}**",
        f"- issue dates: **{summary['first_issue']} .. {summary['last_issue']}**",
        f"- integrity/timeline failures: **{failures}**","",
        "## DCX","",
        f"- candidates: **{dcx['candidate_n']}**",
        f"- rescue / broken / net: **{dcx['rescued']} / {dcx['broken']} / {dcx['net']:+d}**",
        f"- precision: **{100*dcx['precision']:.2f}%**",
        f"- candidate rate: **{100*dcx['candidate_rate']:.2f}%**",
        f"- V5 -> DCX-assisted accuracy: **{100*summary['v5_accuracy']:.2f}% -> {100*summary['dcx_accuracy']:.2f}%**","",
        "## Increment over OCS","",
        f"- OCS reference: **{ocs['candidate_n']} candidates, net {ocs['net']:+d}, precision {100*ocs['precision']:.2f}%**",
        f"- DCX-only: **{only['candidate_n']} candidates, {only['rescued']}/{only['broken']}, net {only['net']:+d}**",
        f"- OCS-only: **{oonly['candidate_n']} candidates, {oonly['rescued']}/{oonly['broken']}, net {oonly['net']:+d}**",
        f"- overlap: **{overlap['candidate_n']} candidates, net {overlap['net']:+d}**",
        f"- union: **{union['candidate_n']} candidates, net {union['net']:+d}, precision {100*union['precision']:.2f}%**",
        f"- V5 -> union-assisted accuracy: **{100*summary['v5_accuracy']:.2f}% -> {100*summary['union_accuracy']:.2f}%**","",
        "## Half-year stability","",
        "| Block | Cand | Rescue | Broken | Net | Precision | V5 acc | DCX acc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net:+d} | "
            f"{100*r.precision:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.dcx_accuracy:.1f}% |"
        )
    lines += ["","## Gate","",
              f"- positive blocks: **{positive}/{len(bdf)}**",
              f"- worst block net: **{worst:+d}**",
              f"- DCX-only marginal net: **{only['net']:+d}**",
              f"- union net vs OCS: **{union['net']:+d} vs {ocs['net']:+d}**"]
    if gate:
        lines += [
            "- DCX V1 passed the frozen development gate.",
            "- A separate prospective freeze is required."
        ]
    else:
        lines += [
            "- DCX V1 failed at least one frozen development criterion.",
            "- Do not tune delta, rank or retracement thresholds on this same replay."
        ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
