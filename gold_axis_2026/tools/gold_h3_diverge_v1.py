from __future__ import annotations
# workflow diagnostic rerun: preregistered logic unchanged
import io, json, math
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

BASE_PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
METALS=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_PANEL=AX/"GOLD_H3_DIVERGE_V1_PANEL_2026-10-03.csv"
OUT_DEV=AX/"GOLD_H3_DIVERGE_V1_DEV_PREDICTIONS_2026-10-03.csv"
OUT_CONFIRM=AX/"GOLD_H3_DIVERGE_V1_2025_PREDICTIONS_2026-10-03.csv"
OUT_HOLD=AX/"GOLD_H3_DIVERGE_V1_2026_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_DIVERGE_V1_THRESHOLD_GRID_2026-10-03.csv"
OUT_SOURCE=AX/"GOLD_H3_DIVERGE_V1_SOURCE_AUDIT_2026-10-03.csv"
OUT_JSON=AX/"GOLD_H3_DIVERGE_V1_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_DIVERGE_V1_RESULT_2026-10-03.md"

SEED=20261003
THRESH_GRID=[0.35,0.40,0.45,0.50,0.55,0.60]

FEATURES=[
    "silver_ret1","gold_daily_ret1","usd_ret1","dgs10_chg1","ndx_ret1","vix_ret1",
    "mom_x_silver","mom_x_usd","mom_x_yield","mom_x_ndx","mom_x_vix",
    "mom_x_gold_silver_gap","core_confirmation","cross_dispersion"
]

SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"Mozilla/5.0 (compatible; DIVERGE-H3 academic research/1.1)","Accept":"*/*"})

DDP_SOURCES={
    "usd":{
        "rel":"H10",
        "package":"122e3bcb627e8e53f1bf72a1a09cfb81",
        "column":"JRXWTFB_N.B",
    },
    "yield":{
        "rel":"H15",
        "package":"0b98a66d3ff5e1ea0fbf88adc59b387f",
        "column":"RIFLGFCY10_N.B",
    },
}

def parse_fed_ddp_csv(text,target_code):
    lines=text.splitlines()
    header_i=None
    for i,line in enumerate(lines):
        if "Time Period" in line and target_code in line:
            header_i=i
            break
    if header_i is None:
        # Some DDP exports put metadata on separate rows; look for any Time Period header.
        for i,line in enumerate(lines):
            if "Time Period" in line:
                header_i=i
                break
    if header_i is None:
        raise RuntimeError(f"FED_DDP_HEADER_NOT_FOUND {target_code} head={text[:500]!r}")
    df=pd.read_csv(io.StringIO("\n".join(lines[header_i:])))
    date_col=df.columns[0]
    candidates=[x for x in df.columns if target_code in str(x)]
    if not candidates:
        raise RuntimeError(f"FED_DDP_COLUMN_NOT_FOUND {target_code} cols={df.columns.tolist()}")
    vcol=candidates[0]
    out=df[[date_col,vcol]].rename(columns={date_col:"date",vcol:"value"})
    out["date"]=pd.to_datetime(out["date"],errors="coerce")
    out["value"]=pd.to_numeric(out["value"],errors="coerce")
    return out.dropna(subset=["date","value"]).sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def fed_ddp_fetch(name):
    cfg=DDP_SOURCES[name]
    url="https://www.federalreserve.gov/datadownload/Output.aspx"
    params={
        "rel":cfg["rel"],"series":cfg["package"],"lastObs":"",
        "from":"01/01/2021","to":"10/02/2026",
        "filetype":"csv","label":"include","layout":"seriescolumn","type":"package"
    }
    r=SESSION.get(url,params=params,timeout=60)
    if r.status_code!=200:
        raise RuntimeError(f"FED_DDP_FETCH_FAIL {name} HTTP={r.status_code} {r.text[:300]}")
    df=parse_fed_ddp_csv(r.text,cfg["column"])
    if len(df)<500:
        raise RuntimeError(f"FED_DDP_TOO_FEW {name} n={len(df)} head={r.text[:500]!r}")
    return df,{
        "source":"FED_DDP","series_id":cfg["column"],"status":"PASS","rows":int(len(df)),
        "min_date":str(df.date.min().date()),"max_date":str(df.date.max().date()),
        "source_url":r.url
    }

def yahoo_fetch(symbol,label):
    start=int(pd.Timestamp("2021-01-01",tz="UTC").timestamp())
    end=int(pd.Timestamp("2026-10-03",tz="UTC").timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(symbol,safe='')}"
        params={"period1":start,"period2":end,"interval":"1d","events":"history","includeAdjustedClose":"true"}
        try:
            r=SESSION.get(url,params=params,timeout=60,headers={"Accept":"application/json","User-Agent":SESSION.headers["User-Agent"]})
            if r.status_code!=200:
                last=f"{host} HTTP {r.status_code}: {r.text[:200]}"
                continue
            j=r.json()["chart"]["result"][0]
            q=j["indicators"]["quote"][0]
            rows=[]
            for i,t in enumerate(j["timestamp"]):
                close=q["close"][i]
                if close is None or not np.isfinite(float(close)) or float(close)<=0:
                    continue
                d=pd.to_datetime(t,unit="s",utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
                rows.append({"date":d,"value":float(close)})
            df=pd.DataFrame(rows).drop_duplicates("date",keep="last").sort_values("date").reset_index(drop=True)
            if len(df)<500:
                last=f"{host} too few rows {len(df)}"
                continue
            return df,{
                "source":"YAHOO_CHART","series_id":label,"status":"PASS","rows":int(len(df)),
                "min_date":str(df.date.min().date()),"max_date":str(df.date.max().date()),
                "source_url":r.url
            }
        except Exception as e:
            last=f"{host} {type(e).__name__}: {e}"
    raise RuntimeError(f"YAHOO_FETCH_FAIL {label} {last}")

def z_against_prior(s,window=60,minp=30):
    mu=s.shift(1).rolling(window,min_periods=minp).mean()
    sd=s.shift(1).rolling(window,min_periods=minp).std(ddof=0)
    return (s-mu)/sd.replace(0,np.nan)

def build_sources():
    # Frozen clean Gold/Silver daily snapshot.
    m=pd.read_csv(METALS)
    m["date"]=pd.to_datetime(m["date"],errors="raise")
    m=m.sort_values("date").drop_duplicates("date",keep="last")
    m["gold_daily_ret1"]=np.log(m.gold.astype(float)).diff()
    m["silver_ret1"]=np.log(m.silver.astype(float)).diff()
    m["z_silver"]=z_against_prior(m.silver_ret1)
    m=m.dropna(subset=["gold_daily_ret1","silver_ret1","z_silver"]).reset_index(drop=True)

    audits=[{
        "source":"FROZEN_METALS","series_id":"GOLD/SILVER",
        "status":"PASS","rows":int(len(m)),
        "min_date":str(m.date.min().date()),"max_date":str(m.date.max().date()),
        "source_url":"repo:frozen_clean_daily_prices"
    }]

    usd,meta=fed_ddp_fetch("usd"); audits.append(meta)
    yld,meta=fed_ddp_fetch("yield"); audits.append(meta)
    ndx,meta=yahoo_fetch("^NDX","NDX"); audits.append(meta)
    vix,meta=yahoo_fetch("^VIX","VIX"); audits.append(meta)

    usd["usd_ret1"]=np.log(usd.value.astype(float)).diff()
    usd["z_usd"]=z_against_prior(usd.usd_ret1)
    usd=usd.dropna(subset=["usd_ret1","z_usd"]).reset_index(drop=True)

    yld["dgs10_chg1"]=yld.value.astype(float).diff()
    yld["z_yield"]=z_against_prior(yld.dgs10_chg1)
    yld=yld.dropna(subset=["dgs10_chg1","z_yield"]).reset_index(drop=True)

    ndx["ndx_ret1"]=np.log(ndx.value.astype(float)).diff()
    ndx["z_ndx"]=z_against_prior(ndx.ndx_ret1)
    ndx=ndx.dropna(subset=["ndx_ret1","z_ndx"]).reset_index(drop=True)

    vix["vix_ret1"]=np.log(vix.value.astype(float)).diff()
    vix["z_vix"]=z_against_prior(vix.vix_ret1)
    vix=vix.dropna(subset=["vix_ret1","z_vix"]).reset_index(drop=True)

    return {"metal":m,"usd":usd,"yield":yld,"ndx":ndx,"vix":vix},pd.DataFrame(audits)

def latest_before(df,cutoff,max_stale):
    z=df[df.date<cutoff]
    if z.empty:
        return None
    r=z.iloc[-1]
    age=(cutoff-r.date).days
    if age>max_stale:
        return None
    return r

def build_panel(src):
    p=pd.read_csv(BASE_PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        p[c]=pd.to_datetime(p[c],errors="raise")
    p=p.sort_values("feature_cutoff_date").reset_index(drop=True)

    rows=[]
    for r in p.itertuples():
        cutoff=pd.Timestamp(r.feature_cutoff_date)
        mr=latest_before(src["metal"],cutoff,STALE_DAYS["metal"])
        ur=latest_before(src["usd"],cutoff,STALE_DAYS["usd"])
        yr=latest_before(src["yield"],cutoff,STALE_DAYS["yield"])
        nr=latest_before(src["ndx"],cutoff,STALE_DAYS["ndx"])
        vr=latest_before(src["vix"],cutoff,STALE_DAYS["vix"])
        if any(x is None for x in [mr,ur,yr,nr,vr]):
            continue

        s=1.0 if int(r.momentum_up)==1 else -1.0
        silver=float(mr.silver_ret1)
        gold=float(mr.gold_daily_ret1)
        usd=float(ur.usd_ret1)
        yld=float(yr.dgs10_chg1)
        ndx=float(nr.ndx_ret1)
        vix=float(vr.vix_ret1)

        z_silver=float(mr.z_silver)
        z_usd=float(ur.z_usd)
        z_yield=float(yr.z_yield)
        z_ndx=float(nr.z_ndx)
        z_vix=float(vr.z_vix)

        d=r._asdict()
        d.update({
            "metal_source_date":mr.date,
            "usd_source_date":ur.date,
            "yield_source_date":yr.date,
            "ndx_source_date":nr.date,
            "vix_source_date":vr.date,
            "silver_ret1":silver,
            "gold_daily_ret1":gold,
            "usd_ret1":usd,
            "dgs10_chg1":yld,
            "ndx_ret1":ndx,
            "vix_ret1":vix,
            "mom_x_silver":s*silver,
            "mom_x_usd":s*usd,
            "mom_x_yield":s*yld,
            "mom_x_ndx":s*ndx,
            "mom_x_vix":s*vix,
            "mom_x_gold_silver_gap":s*(gold-silver),
            "core_confirmation":float(np.mean([s*z_silver,-s*z_usd,-s*z_yield])),
            "cross_dispersion":float(np.std([z_silver,z_usd,z_yield,z_ndx,z_vix],ddof=0)),
        })
        rows.append(d)

    q=pd.DataFrame(rows)
    if q.empty:
        raise RuntimeError("DIVERGE_EMPTY_PANEL")
    q=q.dropna(subset=FEATURES+["reversal_target","aurora_follows_momentum"])
    q["month_key"]=pd.to_datetime(q.forecast_issue_date).dt.to_period("M").astype(str)
    return q.sort_values("forecast_issue_date").reset_index(drop=True)

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,solver="lbfgs",max_iter=4000,
            class_weight="balanced",random_state=SEED
        ))
    ])

def walk(panel,years):
    test=panel[panel.year.isin(years)].copy()
    rows=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=panel[
            (panel.target_end_date_h3<=cutoff)
            & (panel.forecast_issue_date<first_issue)
        ].copy()
        tr=tr.dropna(subset=FEATURES+["reversal_target"])
        if len(tr)<80 or tr.reversal_target.nunique()<2:
            continue
        m=make_model()
        m.fit(tr[FEATURES].to_numpy(float),tr.reversal_target.astype(int).to_numpy())
        pr=m.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        for row,pv in zip(te.itertuples(),pr):
            rows.append({
                "feature_cutoff_date":row.feature_cutoff_date,
                "forecast_issue_date":row.forecast_issue_date,
                "target_end_date_h3":row.target_end_date_h3,
                "year":int(row.year),"month":str(row.month),
                "y_up":int(row.y_up),"target_r3":float(row.target_r3),
                "p_aurora":float(row.p_aurora),
                "momentum_up":int(row.momentum_up),
                "reversal_target":int(row.reversal_target),
                "aurora_pred":int(row.aurora_pred),
                "aurora_follows_momentum":bool(row.aurora_follows_momentum),
                "p_diverge_reversal":float(pv),
                "train_n":int(len(tr)),
                "metal_source_date":row.metal_source_date,
                "usd_source_date":row.usd_source_date,
                "yield_source_date":row.yield_source_date,
                "ndx_source_date":row.ndx_source_date,
                "vix_source_date":row.vix_source_date,
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def parse_bool(s):
    if s.dtype==bool:
        return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def merge_v5(pred):
    v=pd.read_csv(V5)
    v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date)
    keep=["feature_cutoff_date","p_helios_v5_dce","opal_override_check"]
    z=pred.merge(v[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z

def f2(p,r):
    if p<=0 or r<=0:
        return 0.0
    return 5*p*r/(4*p+r)

def candidate_metrics(z,th):
    e=z[z.aurora_follows_momentum.astype(bool)].copy()
    c=e.p_diverge_reversal>=th
    y=e.reversal_target.astype(bool)
    tp=int((c&y).sum())
    fp=int((c&~y).sum())
    fn=int((~c&y).sum())
    precision=tp/max(tp+fp,1)
    recall=tp/max(tp+fn,1)
    rate=float(c.mean()) if len(c) else 0.0
    return {
        "threshold":float(th),"eligible_n":int(len(e)),
        "candidate_n":int(c.sum()),"true_reversal_n":int(y.sum()),
        "tp":tp,"fp":fp,"fn":fn,
        "precision":precision,"recall":recall,
        "candidate_rate":rate,"f2":f2(precision,recall),
        "eligible":bool(precision>=.45 and rate<=.40),
    }

def period_stats(z,th,year):
    q=z[(z.year==year)&z.aurora_follows_momentum.astype(bool)].copy()
    q["diverge_candidate"]=q.p_diverge_reversal>=th
    y=q.reversal_target.astype(bool)
    c=q.diverge_candidate.astype(bool)
    tp=int((c&y).sum())
    fp=int((c&~y).sum())
    precision=tp/max(tp+fp,1)
    recall=tp/max(int(y.sum()),1)
    rate=float(c.mean()) if len(c) else 0.0

    op=q.opal_candidate.astype(bool)
    op_tp=int((op&y).sum())
    op_recall=op_tp/max(int(y.sum()),1)
    op_precision=op_tp/max(int(op.sum()),1)
    only=int((c&y&~op).sum())
    union=(c|op)
    union_recall=float((union&y).sum()/max(int(y.sum()),1))
    brier=float(np.mean((q.p_diverge_reversal-q.reversal_target)**2)) if len(q) else np.nan
    ll=float(log_loss(q.reversal_target,np.clip(q.p_diverge_reversal,1e-6,1-1e-6),labels=[0,1])) if len(q) else np.nan

    return {
        "year":int(year),"eligible_n":int(len(q)),
        "true_reversal_n":int(y.sum()),
        "diverge_candidate_n":int(c.sum()),
        "diverge_precision":precision,
        "diverge_recall":recall,
        "diverge_candidate_rate":rate,
        "opal_candidate_n":int(op.sum()),
        "opal_precision":op_precision,
        "opal_recall":op_recall,
        "diverge_only_true_reversal_n":only,
        "union_recall":union_recall,
        "brier":brier,"logloss":ll,
    }

def main():
    try:
        src,audit=build_sources()
    except Exception as e:
        payload={"schema":"DIVERGE_H3_V1","status":"SOURCE_BLOCKED","error":repr(e)}
        OUT_JSON.write_text(json.dumps(payload,indent=2)+"\n")
        OUT_MD.write_text("# DIVERGE-H3 V1 — RESULT\n\n**Status:** **SOURCE_BLOCKED**\n\n"+repr(e)+"\n")
        print(OUT_MD.read_text())
        return

    audit.to_csv(OUT_SOURCE,index=False)
    panel=build_panel(src)
    panel.to_csv(OUT_PANEL,index=False)

    dev=merge_v5(walk(panel,[2023,2024]))
    if dev.empty:
        raise RuntimeError("NO_DIVERGE_DEV_PREDICTIONS")
    dev.to_csv(OUT_DEV,index=False)

    grid=pd.DataFrame([candidate_metrics(dev,t) for t in THRESH_GRID])
    grid.to_csv(OUT_GRID,index=False)
    elig=grid[grid.eligible].copy()

    selected=None
    confirm_pass=None
    confirm_stats=None
    holdout_stats=None
    status=None

    if elig.empty:
        status="NO_ELIGIBLE_DIVERGE_THRESHOLD"
    else:
        elig=elig.sort_values(
            ["f2","recall","precision","candidate_rate","threshold"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].threshold)

        confirm=merge_v5(walk(panel,[2025]))
        confirm.to_csv(OUT_CONFIRM,index=False)
        confirm_stats=period_stats(confirm,selected,2025)
        confirm_pass=bool(
            confirm_stats["diverge_recall"]>confirm_stats["opal_recall"]
            and confirm_stats["diverge_only_true_reversal_n"]>=1
            and confirm_stats["diverge_precision"]>=.40
            and confirm_stats["union_recall"]>confirm_stats["opal_recall"]
        )
        status="CONFIRM_PASS" if confirm_pass else "CONFIRM_FAIL"

        if confirm_pass:
            hold=merge_v5(walk(panel,[2026]))
            hold["diverge_candidate"]=(
                hold.aurora_follows_momentum.astype(bool)
                & (hold.p_diverge_reversal>=selected)
            )
            hold.to_csv(OUT_HOLD,index=False)
            holdout_stats=period_stats(hold,selected,2026)

            # Reconstruct the main known failure universe across all 2026 rows.
            miss=(
                (hold.reversal_target==1)
                & (hold.v5_pred==hold.momentum_up)
                & (~hold.opal_candidate)
            )
            reverse_dir=1-hold.momentum_up.astype(int)
            changed=hold.diverge_candidate & (reverse_dir!=hold.v5_pred)
            rescue=int((changed&(hold.v5_pred!=hold.y_up)&(reverse_dir==hold.y_up)).sum())
            broken=int((changed&(hold.v5_pred==hold.y_up)&(reverse_dir!=hold.y_up)).sum())
            holdout_stats.update({
                "v5_missed_reversal_opal_no_candidate_n":int(miss.sum()),
                "diverge_hits_in_v5_missed_opal_no_candidate":int((miss&hold.diverge_candidate).sum()),
                "diagnostic_v5_rescue":rescue,
                "diagnostic_v5_broken":broken,
                "diagnostic_v5_net":rescue-broken,
            })

    summary={
        "schema":"DIVERGE_H3_V1",
        "evidence_class":"RETROSPECTIVE_RESEARCH_NOT_FULL_PIT",
        "status":status,
        "features":FEATURES,
        "source_audit":audit.to_dict("records"),
        "panel_rows":int(len(panel)),
        "panel_min_issue":str(panel.forecast_issue_date.min().date()),
        "panel_max_issue":str(panel.forecast_issue_date.max().date()),
        "selected_threshold":selected,
        "threshold_grid":grid.to_dict("records"),
        "confirmation_2025":confirm_stats,
        "confirmation_pass":confirm_pass,
        "holdout_2026":holdout_stats,
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# DIVERGE-H3 V1 — RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective research with strict prior-date alignment; not claimed as pristine historical PIT.","",
        "## Source audit","",
        "| Source | Series | Rows | Min | Max | Status |",
        "|---|---|---:|---|---|---|",
    ]
    for r in audit.itertuples():
        lines.append(f"| {r.source} | {r.series_id} | {r.rows} | {r.min_date} | {r.max_date} | {r.status} |")

    lines += [
        "","## DEV 2023-2024 threshold grid","",
        "| Th | Candidate | Precision | Recall | Rate | F2 | Eligible |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.threshold:.2f} | {r.candidate_n} | {100*r.precision:.2f}% | "
            f"{100*r.recall:.2f}% | {100*r.candidate_rate:.2f}% | {r.f2:.4f} | {r.eligible} |"
        )

    if selected is not None and confirm_stats is not None:
        s=confirm_stats
        lines += [
            "",f"## Selected threshold: {selected:.2f}","",
            "## 2025 confirmation","",
            f"- DIVERGE recall: **{100*s['diverge_recall']:.2f}%**",
            f"- OPAL recall same universe: **{100*s['opal_recall']:.2f}%**",
            f"- DIVERGE precision: **{100*s['diverge_precision']:.2f}%**",
            f"- DIVERGE-only true OPAL-missed reversals: **{s['diverge_only_true_reversal_n']}**",
            f"- OPAL ∪ DIVERGE recall: **{100*s['union_recall']:.2f}%**",
            f"- Confirmation: **{'PASS' if confirm_pass else 'FAIL'}**",
        ]

    if confirm_pass and holdout_stats is not None:
        h=holdout_stats
        lines += [
            "","## 2026 final holdout","",
            f"- DIVERGE recall: **{100*h['diverge_recall']:.2f}%**",
            f"- DIVERGE precision: **{100*h['diverge_precision']:.2f}%**",
            f"- OPAL recall same universe: **{100*h['opal_recall']:.2f}%**",
            f"- OPAL ∪ DIVERGE recall: **{100*h['union_recall']:.2f}%**",
            f"- DIVERGE-only true reversals: **{h['diverge_only_true_reversal_n']}**",
            f"- V5 missed reversal + OPAL no-candidate universe: **{h['v5_missed_reversal_opal_no_candidate_n']}**",
            f"- DIVERGE hits in that universe: **{h['diverge_hits_in_v5_missed_opal_no_candidate']}**",
            f"- Diagnostic V5 forced-flip rescue / broken / net: "
            f"**{h['diagnostic_v5_rescue']} / {h['diagnostic_v5_broken']} / {h['diagnostic_v5_net']:+d}**",
        ]

    lines += [
        "","## Governance","",
        "No 2026 outcome was used for feature, lag, threshold, source, or confirmation selection. "
        "2026 was evaluated only if the preregistered 2025 confirmation gate passed. "
        "DIVERGE is not promoted to HELIOS from this result alone."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
