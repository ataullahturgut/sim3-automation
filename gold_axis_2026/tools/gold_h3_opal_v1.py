from __future__ import annotations

import io
import json
import math
import os
import re
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_opal_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

YEARS = list(range(2021, 2027))
CFTC_CODE = "088691"
AVAIL_LAG_DAYS = 7
THRESH = 0.70
SEED = 20261003
REPS = 10000
BLOCKS = [5, 10]
EPS = 1e-8

FEATURES = [
    "opt_mm_net",
    "opt_prod_net",
    "opt_swap_net",
    "opt_other_net",
    "d_opt_mm_net",
    "d_opt_prod_net",
    "opt_mm_z52",
    "opt_prod_z52",
    "opt_swap_z52",
    "opt_other_z52",
    "spec_hedger_gap",
    "spec_swap_gap",
    "fut_mm_net",
    "fut_prod_net",
    "trend_x_opt_mm",
    "trend_x_opt_prod",
    "trend_x_spec_hedger_gap",
    "trend_strength",
]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            class_weight="balanced",
            random_state=SEED,
        )),
    ])


def norm_col(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")


def get_bytes(url, attempts=5):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent":"opal-h3/1.0"})
            r.raise_for_status()
            return r.content
        except Exception as e:
            last = e
            if i == attempts - 1:
                raise RuntimeError(f"CFTC_FETCH_FAIL {url} {e}")
            time.sleep(5*(i+1))
    raise RuntimeError(last)


def read_zip_table(raw, label):
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = [n for n in z.namelist() if not n.endswith("/")]
    if not names:
        raise RuntimeError(f"EMPTY_CFTC_ZIP {label}")
    # Prefer text/csv member; annual compressed files normally contain one.
    names = sorted(names, key=lambda n: (0 if n.lower().endswith((".txt",".csv")) else 1, n))
    payload = z.read(names[0])
    df = pd.read_csv(io.BytesIO(payload), low_memory=False)
    df.columns = [norm_col(c) for c in df.columns]
    return df, names[0]


def fetch_socrata(dataset_id):
    url = (
        f"https://publicreporting.cftc.gov/resource/{dataset_id}.csv"
        f"?cftc_contract_market_code={CFTC_CODE}&$limit=5000"
    )
    raw = get_bytes(url)
    df = pd.read_csv(io.BytesIO(raw), low_memory=False)
    df.columns = [norm_col(c) for c in df.columns]
    return df, {"url":url, "bytes":len(raw), "rows":int(len(df))}

def gold_rows(df):
    code_col = "cftc_contract_market_code"
    date_col = "report_date_as_yyyy_mm_dd" if "report_date_as_yyyy_mm_dd" in df.columns else "as_of_date_form_yyyy_mm_dd"
    if code_col not in df.columns or date_col not in df.columns:
        raise RuntimeError(f"CFTC_COLUMNS_MISSING code={code_col in df.columns} date={date_col in df.columns} cols={list(df.columns)[:20]}")
    code = df[code_col].astype(str).str.replace(r"\.0$","",regex=True).str.zfill(6)
    market = df.get("market_and_exchange_names", pd.Series([""]*len(df))).astype(str).str.upper()
    mask = (code == CFTC_CODE) | market.str.contains("GOLD - COMMODITY EXCHANGE", regex=False)
    g = df[mask].copy()
    if g.empty:
        raise RuntimeError("NO_GOLD_ROWS")
    g["report_date"] = pd.to_datetime(g[date_col], errors="raise")
    return g.sort_values("report_date").drop_duplicates("report_date", keep="last").reset_index(drop=True)


def col(g, name):
    if name not in g.columns:
        raise RuntimeError(f"CFTC_FIELD_MISSING {name}")
    return pd.to_numeric(g[name], errors="raise").astype(float)


def build_cot():
    # Official CFTC Public Reporting Environment datasets:
    # futures-only disaggregated = 72hh-3qpy
    # futures+options combined disaggregated = kh3c-gbw2
    fut_raw, fm = fetch_socrata("72hh-3qpy")
    com_raw, cm = fetch_socrata("kh3c-gbw2")
    fut = gold_rows(fut_raw)
    com = gold_rows(com_raw)

    lo = pd.Timestamp("2021-01-01")
    hi = pd.Timestamp("2026-12-31")
    fut = fut[(fut.report_date >= lo) & (fut.report_date <= hi)].copy()
    com = com[(com.report_date >= lo) & (com.report_date <= hi)].copy()

    meta = {
        "transport": "CFTC_PUBLIC_REPORTING_API",
        "futures": fm,
        "combined": cm,
        "fut_gold_rows": int(len(fut)),
        "com_gold_rows": int(len(com)),
    }

    keys = [
        "report_date","open_interest_all",
        "prod_merc_positions_long_all","prod_merc_positions_short_all",
        "swap_positions_long_all","swap_positions_short_all",
        "m_money_positions_long_all","m_money_positions_short_all",
        "other_rept_positions_long_all","other_rept_positions_short_all",
    ]
    ff = fut[keys].copy()
    cc = com[keys].copy()
    ff = ff.rename(columns={k:f"f_{k}" for k in keys if k!="report_date"})
    cc = cc.rename(columns={k:f"c_{k}" for k in keys if k!="report_date"})
    x = ff.merge(cc, on="report_date", how="inner", validate="one_to_one")
    if len(x) < 250:
        raise RuntimeError(f"CFTC_MATCH_TOO_SMALL {len(x)}")

    f_oi = col(x, "f_open_interest_all")
    c_oi = col(x, "c_open_interest_all")
    den = np.where(c_oi > 0, c_oi, np.nan)

    cohorts = {
        "mm": ("m_money_positions_long_all","m_money_positions_short_all"),
        "prod": ("prod_merc_positions_long_all","prod_merc_positions_short_all"),
        "swap": ("swap_positions_long_all","swap_positions_short_all"),
        "other": ("other_rept_positions_long_all","other_rept_positions_short_all"),
    }
    for short,(lcol,scol) in cohorts.items():
        fnet = col(x, f"f_{lcol}") - col(x, f"f_{scol}")
        cnet = col(x, f"c_{lcol}") - col(x, f"c_{scol}")
        onet = cnet - fnet
        x[f"opt_{short}_net"] = onet / den
        x[f"fut_{short}_net"] = fnet / np.where(f_oi > 0, f_oi, np.nan)

    x["d_opt_mm_net"] = x.opt_mm_net.diff()
    x["d_opt_prod_net"] = x.opt_prod_net.diff()
    x["spec_hedger_gap"] = x.opt_mm_net - x.opt_prod_net
    x["spec_swap_gap"] = x.opt_mm_net - x.opt_swap_net

    for short in ["mm","prod","swap","other"]:
        s = x[f"opt_{short}_net"].astype(float)
        mu = s.shift(1).rolling(52, min_periods=26).mean()
        sd = s.shift(1).rolling(52, min_periods=26).std(ddof=0)
        x[f"opt_{short}_z52"] = (s - mu) / sd.replace(0, np.nan)

    x["available_date"] = x.report_date + pd.Timedelta(days=AVAIL_LAG_DAYS)
    keep = [
        "report_date","available_date",
        "opt_mm_net","opt_prod_net","opt_swap_net","opt_other_net",
        "d_opt_mm_net","d_opt_prod_net",
        "opt_mm_z52","opt_prod_z52","opt_swap_z52","opt_other_z52",
        "spec_hedger_gap","spec_swap_gap",
        "fut_mm_net","fut_prod_net",
    ]
    x = x[keep].dropna().sort_values("available_date").reset_index(drop=True)
    return x, meta

def latest_cot(cot, feature_date):
    q = cot[cot.available_date <= pd.Timestamp(feature_date)]
    if q.empty:
        return None
    return q.iloc[-1]


def load_panel():
    a = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        a[c] = pd.to_datetime(a[c], errors="raise")
    a["feature_date"] = a.feature_cutoff_date.dt.date

    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"OPAL_SOURCE_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    anchors = iris.build_anchor_features(hourly)

    p = a.merge(
        anchors[["local_date","h_ret_12","h_rv_12"]],
        left_on="feature_date", right_on="local_date",
        how="inner", validate="one_to_one"
    )
    if len(p) != len(a):
        raise RuntimeError(f"OPAL_ANCHOR_MATCH_FAIL aurora={len(a)} panel={len(p)}")

    cot, cot_meta = build_cot()
    rows = []
    for r in p.itertuples():
        cr = latest_cot(cot, r.feature_cutoff_date)
        if cr is None:
            continue
        trend_sign = 1.0 if float(r.h_ret_12) >= 0 else -1.0
        row = {
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"target_r3":float(r.target_r3),
            "p_aurora":float(r.p_aurora),
            "momentum_up":int(trend_sign > 0),
            "reversal_target":int(int(r.y_up) != int(trend_sign > 0)),
            "trend_strength":abs(float(r.h_ret_12))/(float(r.h_rv_12)+EPS),
            "cot_report_date":cr.report_date,
            "cot_available_date":cr.available_date,
        }
        for name in [
            "opt_mm_net","opt_prod_net","opt_swap_net","opt_other_net",
            "d_opt_mm_net","d_opt_prod_net",
            "opt_mm_z52","opt_prod_z52","opt_swap_z52","opt_other_z52",
            "spec_hedger_gap","spec_swap_gap","fut_mm_net","fut_prod_net"
        ]:
            row[name] = float(cr[name])
        row["trend_x_opt_mm"] = trend_sign * row["opt_mm_net"]
        row["trend_x_opt_prod"] = trend_sign * row["opt_prod_net"]
        row["trend_x_spec_hedger_gap"] = trend_sign * row["spec_hedger_gap"]
        row["aurora_pred"] = int(row["p_aurora"] >= .5)
        row["aurora_follows_momentum"] = bool(row["aurora_pred"] == row["momentum_up"])
        rows.append(row)

    panel = pd.DataFrame(rows).dropna().sort_values("forecast_issue_date").reset_index(drop=True)
    panel["month_key"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    if panel.forecast_issue_date.min() > pd.Timestamp("2022-07-01"):
        raise RuntimeError(f"OPAL_PANEL_START_TOO_LATE {panel.forecast_issue_date.min()}")
    return panel, bridge, api_calls, cot, cot_meta


def run_opal(panel):
    test = panel[panel.forecast_issue_date >= pd.Timestamp("2022-07-01")].copy()
    rows = []
    for mo in sorted(test.month_key.unique()):
        te = test[test.month_key == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < first_issue)
        ].copy()
        if len(tr) < 80:
            continue
        model = make_model()
        model.fit(tr[FEATURES].to_numpy(float), tr.reversal_target.astype(int).to_numpy())
        pr = model.predict_proba(te[FEATURES].to_numpy(float))[:,1]

        for r,p_rev in zip(te.itertuples(),pr):
            p = float(r.p_aurora)
            follows = bool(r.aurora_follows_momentum)
            flip = bool(follows and p_rev >= THRESH)
            if flip:
                p_opal = float(1-p_rev) if int(r.momentum_up)==1 else float(p_rev)
            else:
                p_opal = p
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "p_aurora":p,"p_reversal":float(p_rev),
                "momentum_up":int(r.momentum_up),
                "aurora_follows_momentum":follows,
                "cot_report_date":r.cot_report_date,
                "cot_available_date":r.cot_available_date,
                "override":flip,"p_opal":p_opal,
                "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)


def score_periods(g):
    specs=[
        ("2022_H2",g.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",g.year==2023),("2024",g.year==2024),
        ("2025",g.year==2025),("2026",g.year==2026),
        ("2023-2024",g.year.isin([2023,2024])),
        ("2025-2026",g.year.isin([2025,2026])),
    ]
    rows=[]
    for label,mask in specs:
        z=g[mask].copy()
        if z.empty: continue
        ma=metrics(z.y_up,z.p_aurora); mo=metrics(z.y_up,z.p_opal)
        ap=(z.p_aurora>=.5).astype(int); op=(z.p_opal>=.5).astype(int); y=z.y_up.astype(int)
        ch=ap!=op
        rescued=int((ch&(ap!=y)&(op==y)).sum())
        broken=int((ch&(ap==y)&(op!=y)).sum())
        rows.append({
            "period":label,"override_n":int(z.override.sum()),
            "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"opal_{k}":v for k,v in mo.items()},
        })
    return pd.DataFrame(rows)


def mechanism_gate(mdf):
    ok=True; checks=[]
    for yr in ["2023","2024"]:
        r=mdf[mdf.period==yr].iloc[0]
        passed=bool(
            r.opal_accuracy+.01+1e-12>=r.aurora_accuracy
            and r.opal_brier<=r.aurora_brier+.003+1e-12
        )
        checks.append({"period":yr,"pass":passed})
        ok=ok and passed
    agg=mdf[mdf.period=="2023-2024"].iloc[0]
    agg_ok=bool(
        agg.opal_balanced_accuracy+1e-12>=agg.aurora_balanced_accuracy
        and int(agg.net_rescue)>0
    )
    return bool(ok and agg_ok),checks,agg_ok


def logloss_row(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6); y=np.asarray(y,int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def paired_diff(y,cand,base):
    y=np.asarray(y,int); cand=np.asarray(cand,float); base=np.asarray(base,float)
    return {
        "accuracy":((cand>=.5).astype(int)==y).astype(float)-((base>=.5).astype(int)==y).astype(float),
        "brier":(cand-y)**2-(base-y)**2,
        "logloss":logloss_row(y,cand)-logloss_row(y,base),
    }


def circular_boot(diff,block_len,rng):
    diff=np.asarray(diff,float); n=len(diff); nb=int(np.ceil(n/block_len))
    vals=np.empty(REPS,float); offs=np.arange(block_len); batch=500
    for st in range(0,REPS,batch):
        m=min(batch,REPS-st)
        starts=rng.integers(0,n,size=(m,nb))
        idx=(starts[:,:,None]+offs[None,None,:])%n
        idx=idx.reshape(m,-1)[:,:n]
        vals[st:st+m]=diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows=[]; si=0
    for period,mask in {
        "2023-2024":g.year.isin([2023,2024]),
        "2025-2026":g.year.isin([2025,2026]),
        "2026":g.year==2026,
    }.items():
        z=g[mask].copy()
        for metric,d in paired_diff(z.y_up,z.p_opal,z.p_aurora).items():
            for b in BLOCKS:
                si+=1
                boot=circular_boot(d,b,np.random.default_rng(SEED+si))
                lo,hi=np.quantile(boot,[.025,.975])
                improve=float(np.mean(boot>0)) if metric=="accuracy" else float(np.mean(boot<0))
                rows.append({
                    "period":period,"metric":metric,"block_len":b,
                    "observed_diff":float(np.mean(d)),
                    "ci95_low":float(lo),"ci95_high":float(hi),
                    "bootstrap_improve_share":improve,"n":int(len(z)),
                })
    return pd.DataFrame(rows)


def main():
    panel,bridge,api_calls,cot,cot_meta=load_panel()
    panel.to_csv(OUT/"opal_v1_panel.csv",index=False)
    cot.to_csv(OUT/"opal_v1_cot_options_state.csv",index=False)

    pred=run_opal(panel)
    pred.to_csv(OUT/"opal_v1_predictions.csv",index=False)

    mdf=score_periods(pred)
    mdf.to_csv(OUT/"opal_v1_metrics.csv",index=False)

    passed,checks,agg_ok=mechanism_gate(mdf)
    status="MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    inf=inference(pred) if passed else pd.DataFrame()
    if passed: inf.to_csv(OUT/"opal_v1_inference.csv",index=False)

    z=pred[pred.year==2026].copy()
    z["aurora_dir"]=np.where(z.p_aurora>=.5,"UP","DOWN")
    z["opal_dir"]=np.where(z.p_opal>=.5,"UP","DOWN")
    z["actual_dir"]=np.where(z.y_up==1,"UP","DOWN")
    z["aurora_correct"]=z.aurora_dir==z.actual_dir
    z["opal_correct"]=z.opal_dir==z.actual_dir
    changed=z[z.override].copy()
    changed["effect"]=np.where(
        (~changed.aurora_correct)&changed.opal_correct,"RESCUED",
        np.where(changed.aurora_correct&(~changed.opal_correct),"BROKEN","NO_NET")
    )
    changed.to_csv(OUT/"opal_v1_2026_changed.csv",index=False)

    summary={
        "schema":"OPAL_H3_V1","status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "availability_lag_days":AVAIL_LAG_DAYS,
        "threshold":THRESH,
        "cot_meta":cot_meta,
        "source_bridge":bridge,"api_calls":int(api_calls),
        "mechanism_pass":bool(passed),"confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "metrics":mdf.to_dict(orient="records"),
        "inference":inf.to_dict(orient="records") if passed else [],
        "changed_2026":int(len(changed)),
        "rescued_2026":int((changed.effect=="RESCUED").sum()),
        "broken_2026":int((changed.effect=="BROKEN").sum()),
    }
    (OUT/"opal_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# OPAL-H3 V1 — OPTIONS POSITIONING ASYMMETRY LAYER RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  ",
        f"**CFTC availability lag:** {AVAIL_LAG_DAYS} calendar days; **reversal threshold:** {THRESH:.2f}","",
        "## Period metrics","",
        "| Period | AURORA Acc | OPAL Acc | AURORA BA | OPAL BA | AURORA Brier | OPAL Brier | Overrides | Rescued | Broken |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in mdf.iterrows():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.opal_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.opal_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.opal_brier:.4f} | {int(r.override_n)} | "
            f"{int(r.rescued)} | {int(r.broken)} |"
        )

    lines += ["","## 2026 changed calls",""]
    if changed.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | COT report | AURORA | P(reversal) | OPAL | Actual | H3 return | Effect |",
            "|---|---|---|---|---:|---|---|---:|---|",
        ]
        for r in changed.itertuples():
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{pd.Timestamp(r.cot_report_date).date()} | {r.aurora_dir} | {100*r.p_reversal:.1f}% | "
                f"{r.opal_dir} | {r.actual_dir} | {100*r.target_r3:+.2f}% | {r.effect} |"
            )

    if passed:
        lines += ["","## Dependence-aware bootstrap",""]
        for r in inf.itertuples():
            scale=100 if r.metric=="accuracy" else 1
            unit=" pp" if r.metric=="accuracy" else ""
            lines.append(
                f"- {r.period} {r.metric} block{r.block_len}: diff={scale*r.observed_diff:+.4f}{unit}; "
                f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
                f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
            )

    lines += ["","## Governance","",
              "OPAL reconstructs delta-adjusted options-only cohort exposures from official CFTC combined minus futures-only disaggregated reports. "
              "The 7-day lag is intentionally conservative. No feature, lag, model hyperparameter or reversal threshold may be retuned from 2022-2026 outcomes. "
              "Frozen AURORA prospective validation is unchanged."]

    (OUT/"OPAL_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"OPAL_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
