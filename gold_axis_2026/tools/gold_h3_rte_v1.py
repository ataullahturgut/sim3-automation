from __future__ import annotations

from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor, as_completed
import io, json, math, re, time
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_SRC=AX/"GOLD_H3_RTE_V1_CME_SOURCE_2026-10-03.csv"
OUT_COV=AX/"GOLD_H3_RTE_V1_CME_SOURCE_COVERAGE_2026-10-03.csv"
OUT_PANEL=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OUT_PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_RTE_V1_THRESHOLD_GRID_2026-10-03.csv"
OUT_SUM=AX/"GOLD_H3_RTE_V1_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_RTE_V1_RESULT_2026-10-03.md"

HOST="ftp.cmegroup.com"
DIR="/daily_volume"
DATE_MIN=pd.Timestamp("2022-01-01")
DATE_MAX=pd.Timestamp("2026-09-30")
SEED=20261003
MIN_TRAIN=100
K_TWINS=7
RHO=0.65
THRESH_GRID=[0.55,0.60,0.65,0.70,0.75,0.80]

MATCH_COLS=["abs_h_ret_12","trend_strength","path_consistency","v5_confidence"]
CF_BASE_COLS=[
    "deceleration_6h",
    "opposite_semivar_share",
    "adverse_excursion",
    "signed_opt_pressure",
    "signed_d_opt_pressure",
    "gc_dlog_volume_1",
    "opt_total_z20",
]
CF_COLS=[f"cf_{c}_gap" for c in CF_BASE_COLS]
MODEL_FEATURES=[
    "v5_confidence",
    "trend_strength",
    "opposite_semivar_share",
    "deceleration_6h",
    "path_consistency",
    "trend_close_location",
    "opposite_extreme_recency",
    "adverse_excursion",
    "gc_dlog_volume_1",
    "gc_volume_z20",
    "gc_volume_accel_5",
    "signed_opt_pressure",
    "signed_d_opt_pressure",
    "opt_total_z20",
]+CF_COLS

def norm(x):
    if x is None: return ""
    return re.sub(r"\s+"," ",str(x).strip())

def fnum(x):
    try:
        v=float(x)
        return v if np.isfinite(v) else np.nan
    except Exception:
        return np.nan

def connect():
    ftp=FTP(HOST,timeout=45)
    ftp.login()
    ftp.cwd(DIR)
    return ftp

def parse_xlsx(raw:bytes,d:pd.Timestamp,fn:str):
    wb=load_workbook(io.BytesIO(raw),data_only=True,read_only=True)
    ws=None
    for s in wb.worksheets:
        if "by Product" in s.title:
            ws=s; break
    if ws is None:
        return {"trade_date":d,"filename":fn,"status":"NO_PRODUCT_SHEET"}

    header=None; hr=None
    for i,row in enumerate(ws.iter_rows(values_only=True),1):
        vals=[norm(x) for x in row]
        low=[x.lower() for x in vals]
        if "commodity indicator" in low and any("total volume" in x for x in low):
            header=vals; hr=i; break
    if header is None:
        return {"trade_date":d,"filename":fn,"status":"NO_HEADER"}

    def idx(substr):
        for j,h in enumerate(header):
            if substr in h.lower(): return j
        raise KeyError(substr)

    try:
        i_ex=idx("exchange name")
        i_ci=idx("commodity indicator")
        i_pd=idx("product description")
        i_fo=idx("future/option indicator")
        i_tv=idx("total volume")
    except Exception:
        return {"trade_date":d,"filename":fn,"status":"HEADER_MAP_FAIL"}

    found={}
    for row in ws.iter_rows(min_row=hr+1,values_only=True):
        vals=list(row)
        def g(i): return vals[i] if i < len(vals) else None
        exch=norm(g(i_ex)).upper()
        ci=norm(g(i_ci)).upper()
        pdsc=norm(g(i_pd)).upper()
        foi=norm(g(i_fo)).upper()
        tv=fnum(g(i_tv))
        if "COMEX" not in exch: 
            continue
        if ci=="GC" and foi=="F" and "GOLD FUTURES" in pdsc:
            found["gc_total_volume"]=tv
        elif ci=="OG" and foi=="O" and pdsc=="GOLD CALL":
            found["call_vol"]=tv
        elif ci=="OG" and foi=="O" and pdsc=="GOLD PUT":
            found["put_vol"]=tv

    req=["gc_total_volume","call_vol","put_vol"]
    ok=all(k in found and np.isfinite(found[k]) and found[k]>=0 for k in req)
    return {
        "trade_date":d,"filename":fn,
        "status":"PASS" if ok else "MISSING_REQUIRED_ROW",
        **found
    }

def worker(chunk):
    ftp=connect()
    rows=[]
    try:
        for d,fn in chunk:
            raw=None; err=None
            for attempt in range(3):
                try:
                    bio=io.BytesIO()
                    ftp.retrbinary(f"RETR {fn}",bio.write)
                    raw=bio.getvalue(); break
                except Exception as e:
                    err=repr(e)
                    try: ftp.quit()
                    except Exception: pass
                    time.sleep(0.5+attempt)
                    ftp=connect()
            if raw is None:
                rows.append({"trade_date":d,"filename":fn,"status":"FTP_FAIL","error":err})
                continue
            try:
                rows.append(parse_xlsx(raw,d,fn))
            except Exception as e:
                rows.append({"trade_date":d,"filename":fn,"status":"PARSE_EXCEPTION","error":repr(e)})
    finally:
        try: ftp.quit()
        except Exception: pass
    return rows

def acquire():
    ftp=connect()
    listing=ftp.nlst()
    try: ftp.quit()
    except Exception: pass

    pat=re.compile(r"daily_volume_(\d{8})\.xlsx$",re.I)
    targets=[]
    for fn in listing:
        m=pat.search(fn)
        if not m: continue
        d=pd.to_datetime(m.group(1),format="%Y%m%d",errors="coerce")
        if pd.isna(d): continue
        if DATE_MIN <= d <= DATE_MAX:
            targets.append((d,fn))
    targets=sorted(set(targets))

    workers=10
    chunks=[targets[i::workers] for i in range(workers)]
    rows=[]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs=[ex.submit(worker,c) for c in chunks if c]
        for i,fut in enumerate(as_completed(futs),1):
            part=fut.result()
            rows.extend(part)
            print(f"source worker {i}/{len(futs)} complete rows={len(rows)}")
    return pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)

def source_features(raw):
    x=raw[raw.status=="PASS"].copy()
    x=x.drop_duplicates("trade_date",keep="last").sort_values("trade_date").reset_index(drop=True)
    # avoid log(0) on rare zero-volume call/put days by using total option volume only for log transforms
    x["gc_logv"]=np.log(x.gc_total_volume.clip(lower=1))
    x["gc_dlog_volume_1"]=x.gc_logv.diff()
    mu=x.gc_logv.shift(1).rolling(20,min_periods=10).mean()
    sd=x.gc_logv.shift(1).rolling(20,min_periods=10).std(ddof=0)
    x["gc_volume_z20"]=(x.gc_logv-mu)/sd.replace(0,np.nan)
    x["gc_volume_accel_5"]=x.gc_dlog_volume_1-x.gc_dlog_volume_1.shift(1).rolling(5,min_periods=3).mean()

    den=(x.call_vol+x.put_vol).replace(0,np.nan)
    x["opt_vol_imbalance"]=(x.call_vol-x.put_vol)/den
    x["d_opt_vol_imbalance_1"]=x.opt_vol_imbalance.diff()
    x["opt_total_volume"]=x.call_vol+x.put_vol
    x["opt_log_total"]=np.log(x.opt_total_volume.clip(lower=1))
    om=x.opt_log_total.shift(1).rolling(20,min_periods=10).mean()
    os=x.opt_log_total.shift(1).rolling(20,min_periods=10).std(ddof=0)
    x["opt_total_z20"]=(x.opt_log_total-om)/os.replace(0,np.nan)
    return x

def coverage(raw):
    q=raw.copy()
    q["year"]=pd.to_datetime(q.trade_date).dt.year
    out=[]
    for y,g in q.groupby("year"):
        p=g[g.status=="PASS"]
        bad=g[g.status!="PASS"]
        out.append({
            "year":int(y),"listed_files":len(g),"pass_rows":len(p),
            "coverage":len(p)/max(len(g),1),
            "first_pass":str(pd.to_datetime(p.trade_date).min().date()) if len(p) else None,
            "last_pass":str(pd.to_datetime(p.trade_date).max().date()) if len(p) else None,
            "missing_rows":len(bad),
            "missing_statuses":";".join(f"{k}:{v}" for k,v in bad.status.value_counts().to_dict().items())
        })
    return pd.DataFrame(out)

def load_base(src):
    p=pd.read_csv(PANEL)
    v=pd.read_csv(V5)
    for df in [p,v]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            df[c]=pd.to_datetime(df[c])
    vkeep=v[["feature_cutoff_date","p_helios_v5_dce","opal_override_check"]].copy()
    z=p.merge(vkeep,on="feature_cutoff_date",how="inner",validate="one_to_one")
    z["v5_pred"]=(z.p_helios_v5_dce>=0.5).astype(int)
    z["v5_confidence"]=2*np.abs(z.p_helios_v5_dce-0.5)
    z["abs_h_ret_12"]=np.abs(z.h_ret_12)
    z["eligible_v5_continuation"]=z.v5_pred==z.momentum_up.astype(int)
    z["rescue_target"]=(z.v5_pred!=z.y_up.astype(int)).astype(int)

    s=src.dropna(subset=[
        "gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
        "opt_vol_imbalance","d_opt_vol_imbalance_1","opt_total_z20"
    ]).sort_values("trade_date")

    rows=[]
    for r in z.itertuples():
        hist=s[s.trade_date < r.feature_cutoff_date]
        if hist.empty: continue
        q=hist.iloc[-1]
        stale=(r.feature_cutoff_date-q.trade_date).days
        if stale>7: continue
        d=r._asdict()
        sign=1.0 if int(r.momentum_up)==1 else -1.0
        d.update({
            "cme_trade_date":q.trade_date,
            "cme_stale_days":int(stale),
            "gc_dlog_volume_1":float(q.gc_dlog_volume_1),
            "gc_volume_z20":float(q.gc_volume_z20),
            "gc_volume_accel_5":float(q.gc_volume_accel_5),
            "opt_vol_imbalance":float(q.opt_vol_imbalance),
            "d_opt_vol_imbalance_1":float(q.d_opt_vol_imbalance_1),
            "opt_total_z20":float(q.opt_total_z20),
            "signed_opt_pressure":float(-sign*q.opt_vol_imbalance),
            "signed_d_opt_pressure":float(-sign*q.d_opt_vol_imbalance_1),
        })
        rows.append(d)
    a=pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    a["month_key"]=a.forecast_issue_date.dt.to_period("M").astype(str)
    return a

def robust_match_transform(train, row):
    cont=train[(train.rescue_target==0)&(train.momentum_up.astype(int)==int(row.momentum_up))].copy()
    if len(cont)<K_TWINS:
        return None

    mu=train[MATCH_COLS].mean()
    sd=train[MATCH_COLS].std(ddof=0).replace(0,1.0)
    X=(cont[MATCH_COLS]-mu)/sd
    q=(pd.Series({c:getattr(row,c) for c in MATCH_COLS})-mu)/sd
    dist=((X-q.values)**2).sum(axis=1)
    twins=cont.loc[dist.nsmallest(K_TWINS).index]
    out={}
    for c in CF_BASE_COLS:
        out[f"cf_{c}_gap"]=float(getattr(row,c)-twins[c].median())
    return out

def add_cf_features_origin_safe(base):
    a=base.copy()
    for c in CF_COLS: a[c]=np.nan

    # compute each row using only matured prior rows; expensive but leakage-safe and fixed
    for i,r in enumerate(a.itertuples()):
        matured=a[(a.target_end_date_h3<=r.feature_cutoff_date)&(a.forecast_issue_date<r.forecast_issue_date)].copy()
        matured=matured[matured.eligible_v5_continuation.astype(bool)]
        if len(matured)<MIN_TRAIN: continue
        gaps=robust_match_transform(matured,r)
        if gaps is None: continue
        for c,v in gaps.items():
            a.at[i,c]=v
    return a

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=0.25,solver="lbfgs",max_iter=3000,class_weight="balanced",random_state=SEED
        ))
    ])

def fit_walk(a):
    rows=[]
    test=a[(a.forecast_issue_date>=pd.Timestamp("2023-01-01")) & a.eligible_v5_continuation.astype(bool)].copy()
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=a[
            (a.target_end_date_h3<=cutoff)
            & (a.forecast_issue_date<first_issue)
            & a.eligible_v5_continuation.astype(bool)
        ].copy()
        tr=tr.dropna(subset=MODEL_FEATURES+["rescue_target"])
        te=te.dropna(subset=MODEL_FEATURES)
        if len(tr)<MIN_TRAIN or te.empty or tr.rescue_target.nunique()<2:
            continue
        m=make_model()
        m.fit(tr[MODEL_FEATURES].to_numpy(float),tr.rescue_target.astype(int).to_numpy())
        p=m.predict_proba(te[MODEL_FEATURES].to_numpy(float))[:,1]
        base_rate=float(np.clip(tr.rescue_target.mean(),1e-4,1-1e-4))
        for rr,pp in zip(te.itertuples(),p):
            rows.append({
                "feature_cutoff_date":rr.feature_cutoff_date,
                "forecast_issue_date":rr.forecast_issue_date,
                "target_end_date_h3":rr.target_end_date_h3,
                "year":int(rr.year),"month":str(rr.month),
                "y_up":int(rr.y_up),"target_r3":float(rr.target_r3),
                "momentum_up":int(rr.momentum_up),
                "p_helios_v5_dce":float(rr.p_helios_v5_dce),
                "v5_pred":int(rr.v5_pred),
                "rescue_target":int(rr.rescue_target),
                "opal_override_check":bool(rr.opal_override_check) if isinstance(rr.opal_override_check,(bool,np.bool_)) else str(rr.opal_override_check).lower() in ("true","1","yes"),
                "p_inst":float(pp),
                "base_rate":base_rate,
                "train_n":int(len(tr))
            })
    g=pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    return add_tension(g)

def logit(x):
    x=np.clip(float(x),1e-6,1-1e-6)
    return math.log(x/(1-x))

def logistic(x):
    if x>=0:
        z=math.exp(-x); return 1/(1+z)
    z=math.exp(x); return z/(1+z)

def add_tension(g):
    g=g.copy()
    tensions=[]; probs=[]
    prev_T=0.0; prev_date=None; prev_mom=None
    for r in g.itertuples():
        innovation=logit(r.p_inst)-logit(r.base_rate)
        continue_state=(
            prev_date is not None
            and int(r.momentum_up)==int(prev_mom)
            and (r.feature_cutoff_date-prev_date).days<=5
        )
        T=RHO*prev_T+innovation if continue_state else innovation
        pr=logistic(logit(r.base_rate)+T)
        tensions.append(T); probs.append(pr)
        prev_T=T; prev_date=r.feature_cutoff_date; prev_mom=r.momentum_up
    g["rte_tension"]=tensions
    g["p_rte"]=probs
    return g

def threshold_metrics(z,th):
    q=z.copy()
    cand=q.p_rte>=th
    y=q.rescue_target.astype(bool)
    rescued=int((cand&y).sum())
    broken=int((cand&~y).sum())
    n=int(len(q)); cn=int(cand.sum())
    precision=rescued/max(cn,1)
    rate=cn/max(n,1)
    return {
        "threshold":th,"eligible_n":n,"candidate_n":cn,
        "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
        "rescue_precision":precision,"candidate_rate":rate,
        "eligible":bool(precision>=.55 and rate<=.25 and rescued-broken>0)
    }

def period_result(g,th,year):
    q=g[g.year==year].copy()
    cand=q.p_rte>=th
    v5=q.v5_pred.astype(int)
    rte=np.where(cand,1-v5,v5).astype(int)
    y=q.y_up.astype(int).to_numpy()
    rescued=int((cand & (v5.to_numpy()!=y) & (rte==y)).sum())
    broken=int((cand & (v5.to_numpy()==y) & (rte!=y)).sum())
    return {
        "year":int(year),"eligible_n":len(q),"candidate_n":int(cand.sum()),
        "candidate_rate":float(cand.mean()) if len(q) else np.nan,
        "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
        "rescue_precision":rescued/max(rescued+broken,1),
        "v5_accuracy":float((v5.to_numpy()==y).mean()) if len(q) else np.nan,
        "rte_accuracy":float((rte==y).mean()) if len(q) else np.nan,
        "missed_reversal_n":int(q.rescue_target.sum()),
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))).sum()),
        "rte_hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))&cand).sum()),
    }

def whole_2026_score(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    base_correct=int(((z.p_helios_v5_dce>=.5).astype(int)==z.y_up.astype(int)).sum())
    n=len(z)
    return {
        "whole_2026_n":int(n),
        "v5_correct":base_correct,
        "rte_assisted_correct":int(base_correct+net),
        "v5_accuracy":base_correct/max(n,1),
        "rte_assisted_accuracy":(base_correct+net)/max(n,1)
    }

def main():
    raw=acquire()
    raw.to_csv(OUT_SRC,index=False)
    cov=coverage(raw)
    cov.to_csv(OUT_COV,index=False)

    src=source_features(raw)
    base=load_base(src)
    feat=add_cf_features_origin_safe(base)
    feat.to_csv(OUT_PANEL,index=False)

    pred=fit_walk(feat)
    pred.to_csv(OUT_PRED,index=False)

    dev=pred[pred.year.isin([2023,2024])].copy()
    grid=pd.DataFrame([threshold_metrics(dev,t) for t in THRESH_GRID])
    grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.eligible].copy()
    selected=None; confirm=None; holdout=None; whole=None
    if elig.empty:
        status="NO_ELIGIBLE_RTE_THRESHOLD"
    else:
        elig=elig.sort_values(
            ["net_rescue","rescued","rescue_precision","candidate_rate","threshold"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].threshold)
        c25=period_result(pred,selected,2025)
        confirm=bool(
            c25["net_rescue"]>=2
            and c25["rescue_precision"]>=.55
            and c25["candidate_rate"]<=.25
            and c25["rte_accuracy"]>c25["v5_accuracy"]
        )
        status="CONFIRM_PASS" if confirm else "CONFIRM_FAIL"
        if confirm:
            holdout=period_result(pred,selected,2026)
            whole=whole_2026_score(holdout["net_rescue"])

    summary={
        "schema":"RTE_H3_V1","status":status,
        "source_coverage":cov.to_dict("records"),
        "feature_rows":len(feat),"prediction_rows":len(pred),
        "selected_threshold":selected,
        "dev_grid":grid.to_dict("records"),
        "confirmation_2025":period_result(pred,selected,2025) if selected is not None else None,
        "confirmation_pass":confirm,
        "holdout_2026":holdout,
        "whole_2026":whole,
        "frozen":{"k_twins":K_TWINS,"rho":RHO,"min_train":MIN_TRAIN,"threshold_grid":THRESH_GRID}
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# RTE-H3 V1 — RESULT","",
        f"**Status:** **{status}**  ",
        "**Architecture:** V5-conditioned rescue target + matched continuation twins + sequential transition memory.  ",
        "**CME PIT:** strict prior-trade-date GC / Gold Call / Gold Put total volume only.","",
        "## Source coverage","",
        "| Year | PASS / Listed | Coverage |",
        "|---:|---:|---:|"
    ]
    for r in cov.itertuples():
        lines.append(f"| {r.year} | {r.pass_rows}/{r.listed_files} | {100*r.coverage:.2f}% |")

    lines += ["","## DEV 2023-2024 threshold grid","",
              "| Th | Cand | Rescued | Broken | Net | Precision | Rate | Eligible |",
              "|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(
            f"| {r.threshold:.2f} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.eligible} |"
        )

    if selected is not None:
        c25=period_result(pred,selected,2025)
        lines += ["",f"## Selected threshold: {selected:.2f}","",
                  "## 2025 confirmation","",
                  f"- eligible origins: **{c25['eligible_n']}**",
                  f"- candidates: **{c25['candidate_n']} ({100*c25['candidate_rate']:.2f}%)**",
                  f"- rescued / broken / net: **{c25['rescued']} / {c25['broken']} / {c25['net_rescue']:+d}**",
                  f"- rescue precision: **{100*c25['rescue_precision']:.2f}%**",
                  f"- V5 accuracy: **{100*c25['v5_accuracy']:.2f}%**",
                  f"- RTE-assisted accuracy: **{100*c25['rte_accuracy']:.2f}%**",
                  f"- confirmation: **{'PASS' if confirm else 'FAIL'}**"]
        if confirm and holdout is not None:
            h=holdout
            lines += ["","## 2026 final holdout","",
                      f"- eligible origins: **{h['eligible_n']}**",
                      f"- candidates: **{h['candidate_n']} ({100*h['candidate_rate']:.2f}%)**",
                      f"- rescued / broken / net: **{h['rescued']} / {h['broken']} / {h['net_rescue']:+d}**",
                      f"- rescue precision: **{100*h['rescue_precision']:.2f}%**",
                      f"- V5 eligible accuracy: **{100*h['v5_accuracy']:.2f}%**",
                      f"- RTE-assisted eligible accuracy: **{100*h['rte_accuracy']:.2f}%**",
                      f"- V5 missed reversal + OPAL-no-candidate: **{h['missed_opal_no_candidate_n']}**",
                      f"- RTE hits inside that set: **{h['rte_hits_missed_opal_no_candidate']}**"]
            if whole is not None:
                lines += [f"- whole clean 2026: **{whole['v5_correct']} -> {whole['rte_assisted_correct']} correct / {whole['whole_2026_n']}**",
                          f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['rte_assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "No 2026 outcome was used to choose features, twin matching, K, decay, model C, threshold grid, or 2025 confirmation gate. "
              "If DEV or confirmation fails, 2026 remains formally unopened."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: rte-workflow-ready
