from __future__ import annotations

import io
import json
import math
import os
import time
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
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_vega_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

THRESH = 0.70
SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]
EPS = 1e-8

FEATURES = [
    "gvz_z252",
    "gvz_r1",
    "gvz_r3",
    "gvz_r5",
    "gvz_vs_med20",
    "iv_rv24_gap",
    "iv_rv48_gap",
    "trend_strength",
    "gvz_shock_x_trend",
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


def fetch_gvz():
    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv?"
        "id=GVZCLS&cosd=2021-01-01&coed=2026-09-30"
    )
    last = None
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            break
        except Exception as e:
            last = e
            if attempt == 4:
                raise RuntimeError(f"GVZ_FETCH_FAIL {e}")
            time.sleep(5 * (attempt + 1))
    df = df.iloc[:, :2].copy()
    df.columns = ["date", "gvz"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["gvz"] = pd.to_numeric(df["gvz"], errors="coerce")
    df = df.dropna().sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    if len(df) < 1000 or df.date.min() > pd.Timestamp("2021-01-10") or df.date.max() < pd.Timestamp("2026-09-20"):
        raise RuntimeError(
            f"GVZ_COVERAGE_FAIL n={len(df)} min={df.date.min()} max={df.date.max()}"
        )
    return df, {"url": url, "n": int(len(df)), "min": str(df.date.min().date()), "max": str(df.date.max().date())}


def gvz_features_for_date(gvz, feature_date):
    cutoff = pd.Timestamp(feature_date) - pd.Timedelta(days=1)
    q = gvz[gvz.date <= cutoff].copy()
    if len(q) < 253:
        return None
    vals = q.gvz.to_numpy(float)
    cur = float(vals[-1])
    hist252 = vals[-253:-1]
    mu = float(np.mean(hist252))
    sd = float(np.std(hist252, ddof=0))
    med20 = float(np.median(vals[-21:-1]))
    return {
        "gvz_level": cur,
        "gvz_z252": (cur-mu)/(sd if sd > 1e-8 else 1.0),
        "gvz_r1": float(math.log(cur/vals[-2])),
        "gvz_r3": float(math.log(cur/vals[-4])),
        "gvz_r5": float(math.log(cur/vals[-6])),
        "gvz_vs_med20": float(math.log(cur/med20)),
    }


def load_panel():
    a = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        a[c] = pd.to_datetime(a[c], errors="raise")
    a["feature_date"] = a.feature_cutoff_date.dt.date

    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"VEGA_SOURCE_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)

    anchors = iris.build_anchor_features(hourly)
    p = a.merge(
        anchors,
        left_on="feature_date",
        right_on="local_date",
        how="inner",
        validate="one_to_one",
    )
    if len(p) != len(a):
        raise RuntimeError(f"VEGA_ANCHOR_MATCH_FAIL aurora={len(a)} panel={len(p)}")

    gvz, gvz_meta = fetch_gvz()
    rows = []
    for r in p.itertuples():
        gf = gvz_features_for_date(gvz, r.feature_cutoff_date)
        if gf is None:
            continue
        implied_daily = float(gf["gvz_level"]) / 100.0 / math.sqrt(252.0)
        rv24 = float(r.h_rv_24)
        rv48_daily = float(r.h_rv_48) / math.sqrt(2.0)
        trend_strength = abs(float(r.h_ret_12)) / (float(r.h_rv_12) + EPS)
        row = {
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_aurora": float(r.p_aurora),
            "h_ret_12": float(r.h_ret_12),
            "momentum_up": int(float(r.h_ret_12) >= 0),
            "reversal_target": int(int(r.y_up) != int(float(r.h_ret_12) >= 0)),
            "trend_strength": trend_strength,
            "gvz_z252": float(gf["gvz_z252"]),
            "gvz_r1": float(gf["gvz_r1"]),
            "gvz_r3": float(gf["gvz_r3"]),
            "gvz_r5": float(gf["gvz_r5"]),
            "gvz_vs_med20": float(gf["gvz_vs_med20"]),
            "iv_rv24_gap": float(math.log((implied_daily + EPS)/(rv24 + EPS))),
            "iv_rv48_gap": float(math.log((implied_daily + EPS)/(rv48_daily + EPS))),
            "gvz_shock_x_trend": float(gf["gvz_r3"]) * trend_strength,
        }
        row["aurora_pred"] = int(row["p_aurora"] >= 0.5)
        row["aurora_follows_momentum"] = bool(row["aurora_pred"] == row["momentum_up"])
        rows.append(row)

    panel = pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    panel["month_key"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    if panel.forecast_issue_date.min() > pd.Timestamp("2022-07-01"):
        raise RuntimeError(f"VEGA_PANEL_START_TOO_LATE {panel.forecast_issue_date.min()}")
    return panel, bridge, api_calls, gvz_meta


def run_vega(panel):
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
        p_rev = model.predict_proba(te[FEATURES].to_numpy(float))[:,1]

        for r,pr in zip(te.itertuples(),p_rev):
            p = float(r.p_aurora)
            ap = int(p >= .5)
            follows = bool(ap == int(r.momentum_up))
            flip = bool(follows and pr >= THRESH)
            if flip:
                p_vega = float(1-pr) if int(r.momentum_up)==1 else float(pr)
            else:
                p_vega = p
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "p_aurora":p,"p_reversal":float(pr),
                "momentum_up":int(r.momentum_up),
                "aurora_follows_momentum":follows,
                "override":flip,"p_vega":p_vega,
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
        ma=metrics(z.y_up,z.p_aurora); mv=metrics(z.y_up,z.p_vega)
        ap=(z.p_aurora>=.5).astype(int); vp=(z.p_vega>=.5).astype(int); y=z.y_up.astype(int)
        ch=ap!=vp
        rescued=int((ch&(ap!=y)&(vp==y)).sum())
        broken=int((ch&(ap==y)&(vp!=y)).sum())
        rows.append({
            "period":label,"override_n":int(z.override.sum()),
            "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"vega_{k}":v for k,v in mv.items()},
        })
    return pd.DataFrame(rows)


def mechanism_gate(mdf):
    ok=True; checks=[]
    for yr in ["2023","2024"]:
        r=mdf[mdf.period==yr].iloc[0]
        passed=bool(
            r.vega_accuracy+.01+1e-12>=r.aurora_accuracy
            and r.vega_brier<=r.aurora_brier+.003+1e-12
        )
        checks.append({"period":yr,"pass":passed})
        ok=ok and passed
    agg=mdf[mdf.period=="2023-2024"].iloc[0]
    agg_ok=bool(
        agg.vega_balanced_accuracy+1e-12>=agg.aurora_balanced_accuracy
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
        for metric,d in paired_diff(z.y_up,z.p_vega,z.p_aurora).items():
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
    panel,bridge,api_calls,gvz_meta=load_panel()
    panel.to_csv(OUT/"vega_v1_panel.csv",index=False)

    pred=run_vega(panel)
    pred.to_csv(OUT/"vega_v1_predictions.csv",index=False)

    mdf=score_periods(pred)
    mdf.to_csv(OUT/"vega_v1_metrics.csv",index=False)

    passed,checks,agg_ok=mechanism_gate(mdf)
    status="MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    inf=inference(pred) if passed else pd.DataFrame()
    if passed: inf.to_csv(OUT/"vega_v1_inference.csv",index=False)

    z=pred[pred.year==2026].copy()
    z["aurora_dir"]=np.where(z.p_aurora>=.5,"UP","DOWN")
    z["vega_dir"]=np.where(z.p_vega>=.5,"UP","DOWN")
    z["actual_dir"]=np.where(z.y_up==1,"UP","DOWN")
    z["aurora_correct"]=z.aurora_dir==z.actual_dir
    z["vega_correct"]=z.vega_dir==z.actual_dir
    changed=z[z.override].copy()
    changed["effect"]=np.where(
        (~changed.aurora_correct)&changed.vega_correct,"RESCUED",
        np.where(changed.aurora_correct&(~changed.vega_correct),"BROKEN","NO_NET")
    )
    changed.to_csv(OUT/"vega_v1_2026_changed.csv",index=False)

    summary={
        "schema":"VEGA_H3_V1","status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "threshold":THRESH,"gvz_meta":gvz_meta,
        "source_bridge":bridge,"api_calls":int(api_calls),
        "mechanism_pass":bool(passed),"confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "metrics":mdf.to_dict(orient="records"),
        "inference":inf.to_dict(orient="records") if passed else [],
        "changed_2026":int(len(changed)),
        "rescued_2026":int((changed.effect=="RESCUED").sum()),
        "broken_2026":int((changed.effect=="BROKEN").sum()),
    }
    (OUT/"vega_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# VEGA-H3 V1 — VOLATILITY-EXPECTATIONS GAP REVERSAL RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  ",
        f"**GVZ lag:** D-1 or earlier; **reversal threshold:** {THRESH:.2f}","",
        "## Period metrics","",
        "| Period | AURORA Acc | VEGA Acc | AURORA BA | VEGA BA | AURORA Brier | VEGA Brier | Overrides | Rescued | Broken |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in mdf.iterrows():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.vega_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.vega_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.vega_brier:.4f} | {int(r.override_n)} | "
            f"{int(r.rescued)} | {int(r.broken)} |"
        )

    lines += ["","## 2026 changed calls",""]
    if changed.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | AURORA | P(reversal) | VEGA | Actual | H3 return | Effect |",
            "|---|---|---|---:|---|---|---:|---|",
        ]
        for r in changed.itertuples():
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{r.aurora_dir} | {100*r.p_reversal:.1f}% | {r.vega_dir} | {r.actual_dir} | "
                f"{100*r.target_r3:+.2f}% | {r.effect} |"
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
              "VEGA adds forward-looking options-implied volatility information but remains retrospective mechanism research. "
              "No GVZ lag, feature, model hyperparameter or reversal threshold may be retuned from 2022-2026 outcomes. "
              "Frozen AURORA prospective validation is unchanged."]

    (OUT/"VEGA_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"VEGA_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
