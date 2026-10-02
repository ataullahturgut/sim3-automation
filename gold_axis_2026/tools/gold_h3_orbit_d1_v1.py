from __future__ import annotations

import json
import io
import math
import os
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_monthly_external_authority_v2 as ext2

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_orbit_d1_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"
METALS = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"

RIDGE_LAMBDA = 10.0
SEED = 20261002

BLOCKS = {
    "METALS_D1": [
        "xag_r1", "xag_r3", "xag_r5",
        "xpt_r1", "xpt_r3", "xpt_r5",
        "xpd_r1", "xpd_r3", "xpd_r5",
        "metal_breadth1", "metal_dispersion1",
        "gold_minus_basket1", "gold_minus_basket3",
    ],
    "USD_D1": [
        "broadusd_r1", "broadusd_r3", "broadusd_r5",
        "cnyusd_r1", "cnyusd_r3", "cnyusd_r5",
        "usd_breadth1", "fx_dispersion1",
    ],
    "RATES_D1": [
        "nom10_d1", "nom10_d3", "nom10_d5",
        "real10_d1", "real10_d3", "real10_d5",
        "be10_d1", "be10_d3", "be10_d5",
    ],
    "RISK_D1": [
        "vix_r1", "vix_r3", "vix_r5", "vix_z20",
        "ndx_r1", "ndx_r3", "ndx_r5", "ndx_rv5",
    ],
}


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


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1-1e-6)
    return np.log(p/(1-p))


def fit_offset_logistic(X, y, offset):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    offset = np.asarray(offset, float)

    def fg(beta):
        eta = offset + X @ beta
        loss = np.sum(np.logaddexp(0.0, eta) - y*eta) + 0.5*RIDGE_LAMBDA*np.dot(beta,beta)
        pr = expit(eta)
        grad = X.T @ (pr-y) + RIDGE_LAMBDA*beta
        return float(loss), grad

    b0 = np.zeros(X.shape[1], float)
    res = minimize(lambda b: fg(b)[0], b0, jac=lambda b: fg(b)[1],
                   method="L-BFGS-B", options={"maxiter":1000, "ftol":1e-12})
    if not res.success:
        raise RuntimeError(f"ORBIT_D1_OPT_FAIL {res.message}")
    return res.x


def load_aurora():
    x = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        x[c] = pd.to_datetime(x[c], errors="raise")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


def load_metals():
    x = pd.read_csv(METALS)
    x["date"] = pd.to_datetime(x["date"], errors="raise")
    return x.sort_values("date").reset_index(drop=True)


def dict_series(d):
    return pd.Series({pd.Timestamp(k): float(v) for k,v in d.items()}).sort_index()


def nested_series(d, key):
    out = {}
    for k,z in d.items():
        if z.get(key) is not None:
            out[pd.Timestamp(k)] = float(z[key])
    return pd.Series(out).sort_index()


def eligible(s, cutoff, min_n):
    q = s[s.index <= pd.Timestamp(cutoff)].dropna()
    if len(q) < min_n:
        raise RuntimeError(f"ORBIT_D1_THIN_SERIES cutoff={cutoff} n={len(q)} need={min_n}")
    return q


def lr(s, cutoff, h):
    q = eligible(s, cutoff, h+1)
    a, b = float(q.iloc[-1]), float(q.iloc[-1-h])
    if a <= 0 or b <= 0:
        raise RuntimeError("NONPOSITIVE_LOG_SERIES")
    return float(math.log(a/b))


def diff(s, cutoff, h):
    q = eligible(s, cutoff, h+1)
    return float(q.iloc[-1] - q.iloc[-1-h])


def latest_returns_for_fx(series_map, cutoff):
    # USD-positive convention for all majors.
    broad = {h: lr(series_map["BROAD_USD_INDEX"], cutoff, h) for h in [1,3,5]}
    cny = {h: lr(series_map["CNY_PER_USD"], cutoff, h) for h in [1,3,5]}

    one = []
    # EURUSD and GBPUSD are inverted so positive means USD strengthening.
    one.append(-lr(series_map["EURUSD_QUOTE"], cutoff, 1))
    one.append(-lr(series_map["GBPUSD_QUOTE"], cutoff, 1))
    one.append(lr(series_map["JPY_PER_USD"], cutoff, 1))
    one.append(lr(series_map["CHF_PER_USD"], cutoff, 1))
    one.append(lr(series_map["CNY_PER_USD"], cutoff, 1))

    return {
        "broadusd_r1": broad[1], "broadusd_r3": broad[3], "broadusd_r5": broad[5],
        "cnyusd_r1": cny[1], "cnyusd_r3": cny[3], "cnyusd_r5": cny[5],
        "usd_breadth1": float(np.mean(np.sign(one))),
        "fx_dispersion1": float(np.std(one, ddof=0)),
    }


def metals_features(metals, d):
    q = metals[metals.date <= pd.Timestamp(d)].copy()
    if len(q) < 6:
        raise RuntimeError(f"THIN_METALS {d}")
    out = {}
    for col,prefix in [("silver","xag"),("platinum","xpt"),("palladium","xpd")]:
        lp = np.log(q[col].astype(float).to_numpy())
        for h in [1,3,5]:
            out[f"{prefix}_r{h}"] = float(lp[-1]-lp[-1-h])

    one = np.array([out["xag_r1"],out["xpt_r1"],out["xpd_r1"]], float)
    out["metal_breadth1"] = float(np.mean(np.sign(one)))
    out["metal_dispersion1"] = float(np.std(one, ddof=0))

    gold = np.log(q.gold.astype(float).to_numpy())
    gr1 = float(gold[-1]-gold[-2])
    gr3 = float(gold[-1]-gold[-4])
    basket1 = float(np.mean(one))
    basket3 = float(np.mean([out["xag_r3"],out["xpt_r3"],out["xpd_r3"]]))
    out["gold_minus_basket1"] = gr1 - basket1
    out["gold_minus_basket3"] = gr3 - basket3
    return out


def rates_features(rate_map, cutoff):
    nom, real = rate_map["DGS10"], rate_map["DFII10"]
    be = (nom.reindex(nom.index.union(real.index)).sort_index().ffill()
          - real.reindex(nom.index.union(real.index)).sort_index().ffill()).dropna()
    out = {}
    for h in [1,3,5]:
        out[f"nom10_d{h}"] = diff(nom, cutoff, h)
        out[f"real10_d{h}"] = diff(real, cutoff, h)
        out[f"be10_d{h}"] = diff(be, cutoff, h)
    return out


def risk_features(vix, ndx, cutoff):
    out = {}
    for h in [1,3,5]:
        out[f"vix_r{h}"] = lr(vix, cutoff, h)
        out[f"ndx_r{h}"] = lr(ndx, cutoff, h)

    qv = eligible(vix, cutoff, 20).iloc[-20:]
    sd = float(qv.std(ddof=0))
    out["vix_z20"] = float((qv.iloc[-1] - qv.mean()) / (sd if sd > 1e-12 else 1.0))

    qn = eligible(ndx, cutoff, 6).iloc[-6:]
    rr = np.diff(np.log(qn.to_numpy(float)))
    out["ndx_rv5"] = float(np.sqrt(np.mean(rr*rr)))
    return out


def fetch_fred_window(series_id, start="2022-02-01", end="2026-09-29"):
    url = (
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(series_id)}"
        f"&cosd={start}&coed={end}"
    )
    raw = ext2.get(url, 60)
    df = pd.read_csv(io.BytesIO(raw))
    if len(df.columns) < 2:
        raise RuntimeError(f"FRED_BAD_COLUMNS {series_id} {list(df.columns)}")
    df = df.iloc[:, :2].copy()
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna().sort_values("date").drop_duplicates("date", keep="last")
    if len(df) < 500:
        raise RuntimeError(f"FRED_TOO_FEW {series_id} n={len(df)}")
    vals = {r.date.strftime("%Y-%m-%d"): float(r.value) for r in df.itertuples(index=False)}
    return vals, {"series_id": series_id, "url": url, "first": min(vals), "last": max(vals), "n": len(vals)}


def fetch_external():
    # Compact credential-free FRED reconstruction, limited to the window needed
    # for the H3 screen. Conservative origin lags remain unchanged.
    ids = {
        "BROAD_USD_INDEX": "DTWEXBGS",
        "EURUSD_QUOTE": "DEXUSEU",
        "GBPUSD_QUOTE": "DEXUSUK",
        "JPY_PER_USD": "DEXJPUS",
        "CHF_PER_USD": "DEXSZUS",
        "CNY_PER_USD": "DEXCHUS",
        "DGS10": "DGS10",
        "DFII10": "DFII10",
        "VIX": "VIXCLS",
        "NDX": "NASDAQ100",
    }
    raw, meta = {}, {}
    for key, sid in ids.items():
        vals, m = fetch_fred_window(sid)
        raw[key] = dict_series(vals)
        meta[key] = m

    fx_keys = ["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]
    return {
        "fx": {k: raw[k] for k in fx_keys},
        "rates": {"DGS10": raw["DGS10"], "DFII10": raw["DFII10"]},
        "vix": raw["VIX"],
        "ndx": raw["NDX"],
        "meta": meta,
    }


def build_panel(active_blocks=None):
    active_blocks = list(active_blocks or BLOCKS.keys())
    a = load_aurora()
    metals = load_metals()
    need_external = any(b != "METALS_D1" for b in active_blocks)
    e = fetch_external() if need_external else {"meta": {"mode": "METALS_ONLY_LOCAL_FROZEN"}}

    rows = []
    for r in a.itertuples():
        d = pd.Timestamp(r.feature_cutoff_date)
        row = {
            "feature_cutoff_date":d,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),
            "month":str(r.month),
            "y_up":int(r.y_up),
            "target_r3":float(r.target_r3),
            "p_aurora":float(r.p_aurora),
        }
        if "METALS_D1" in active_blocks:
            row.update(metals_features(metals,d))
        if "USD_D1" in active_blocks:
            row.update(latest_returns_for_fx(e["fx"], d-pd.Timedelta(days=7)))
        if "RATES_D1" in active_blocks:
            row.update(rates_features(e["rates"], d-pd.Timedelta(days=2)))
        if "RISK_D1" in active_blocks:
            row.update(risk_features(e["vix"], e["ndx"], d-pd.Timedelta(days=1)))
        rows.append(row)

    panel = pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    return panel, e["meta"]


def standardize(tr, te, cols):
    X = tr[cols].to_numpy(float)
    T = te[cols].to_numpy(float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd > 1e-10, sd, 1.0)
    return (X-mu)/sd, (T-mu)/sd


def walk_forward(panel, block):
    cols = BLOCKS[block]
    test = panel[
        (panel.forecast_issue_date >= pd.Timestamp("2022-07-01"))
        & (panel.forecast_issue_date.dt.year <= 2026)
    ].copy()
    rows = []

    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < first_issue)
        ].copy()
        if len(tr) < 15:
            continue

        X,T = standardize(tr,te,cols)
        beta = fit_offset_logistic(X, tr.y_up.astype(int).to_numpy(), logit(tr.p_aurora.to_numpy(float)))
        pp = expit(logit(te.p_aurora.to_numpy(float)) + T@beta)

        for r,p in zip(te.itertuples(),pp):
            rows.append({
                "block":block,
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "p_aurora":float(r.p_aurora),"p_orbit":float(p),
                "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows)


def score(led):
    rows=[]
    specs=[
        ("SELECT_2022_H2",led.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",led.year==2023),("2024",led.year==2024),
        ("2025",led.year==2025),("2026",led.year==2026),
        ("2023-2024",led.year.isin([2023,2024])),
        ("2025-2026",led.year.isin([2025,2026])),
    ]
    for label,mask in specs:
        z=led[mask].copy()
        if z.empty: continue
        ma=metrics(z.y_up,z.p_aurora); mo=metrics(z.y_up,z.p_orbit)
        ap=(z.p_aurora>=.5).astype(int); op=(z.p_orbit>=.5).astype(int); y=z.y_up.astype(int)
        changed=ap!=op
        rescued=int((changed&(ap!=y)&(op==y)).sum())
        broken=int((changed&(ap==y)&(op!=y)).sum())
        rows.append({
            "block":str(z.block.iloc[0]),"period":label,
            "changed":int(changed.sum()),"rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"orbit_{k}":v for k,v in mo.items()},
        })
    return pd.DataFrame(rows)


def gates(mdf):
    s=mdf[mdf.period=="SELECT_2022_H2"].iloc[0]
    eligible=bool(
        s.orbit_balanced_accuracy+1e-12>=s.aurora_balanced_accuracy
        and s.orbit_accuracy+0.005+1e-12>=s.aurora_accuracy
        and s.orbit_brier<=s.aurora_brier+0.0025+1e-12
        and s.orbit_prediction_std>=0.02
    )
    checks=[]
    confirm=eligible
    if eligible:
        for yr in ["2023","2024"]:
            r=mdf[mdf.period==yr].iloc[0]
            passed=bool(
                r.orbit_accuracy+0.01+1e-12>=r.aurora_accuracy
                and r.orbit_balanced_accuracy+0.01+1e-12>=r.aurora_balanced_accuracy
                and r.orbit_brier<=r.aurora_brier+0.003+1e-12
            )
            checks.append({"period":yr,"pass":passed})
            confirm=confirm and passed
        agg=mdf[mdf.period=="2023-2024"].iloc[0]
        agg_ok=bool(
            agg.orbit_balanced_accuracy+1e-12>=agg.aurora_balanced_accuracy
            and agg.orbit_brier<=agg.aurora_brier+1e-12
        )
        confirm=confirm and agg_ok
    else:
        agg_ok=False
    return eligible,bool(confirm),checks,bool(agg_ok)


def main():
    requested = os.environ.get("ORBIT_BLOCKS","").strip()
    active_blocks = [x.strip() for x in requested.split(",") if x.strip()] if requested else list(BLOCKS)
    unknown = [x for x in active_blocks if x not in BLOCKS]
    if unknown:
        raise RuntimeError(f"UNKNOWN_ORBIT_BLOCKS {unknown}")

    panel,meta=build_panel(active_blocks)
    panel.to_csv(OUT/"orbit_d1_panel.csv",index=False)

    all_metrics=[]
    results={}
    for block in active_blocks:
        led=walk_forward(panel,block)
        led.to_csv(OUT/f"orbit_d1_predictions_{block.lower()}.csv",index=False)
        mdf=score(led)
        all_metrics.append(mdf)
        eligible,confirm,checks,agg_ok=gates(mdf)
        results[block]={
            "selection_eligible":eligible,
            "confirmation_pass":confirm,
            "confirmation_checks":checks,
            "aggregate_guard":agg_ok,
            "metrics":mdf.to_dict(orient="records"),
        }

    met=pd.concat(all_metrics,ignore_index=True)
    met.to_csv(OUT/"orbit_d1_metrics.csv",index=False)

    hourly_candidates=[b for b,v in results.items() if v["confirmation_pass"]]
    status="HOURLY_CANDIDATE_FOUND" if hourly_candidates else "NO_DAILY_BLOCK_CONFIRMED"

    summary={
        "schema":"ORBIT_D1_V1",
        "status":status,
        "evidence_class":"RECONSTRUCTED_AVAILABILITY_RESEARCH",
        "ridge_lambda":RIDGE_LAMBDA,
        "source_meta":meta,
        "blocks":results,
        "hourly_candidates":hourly_candidates,
    }
    (OUT/"orbit_d1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# ORBIT-D1 V1 — DAILY CROSS-MARKET INFORMATION SCREEN","",
        f"**Status:** **{status}**  ",
        f"**Hourly-data candidates:** **{', '.join(hourly_candidates) if hourly_candidates else 'NONE'}**","",
        "## Block gates","",
        "| Block | 2022-H2 eligible | 2023-24 confirmation | 2022 ΔAcc | 2022 ΔBA | 2022 ΔBrier |",
        "|---|---|---|---:|---:|---:|",
    ]
    for block,v in results.items():
        s=[x for x in v["metrics"] if x["period"]=="SELECT_2022_H2"][0]
        lines.append(
            f"| {block} | {v['selection_eligible']} | {v['confirmation_pass']} | "
            f"{100*(s['orbit_accuracy']-s['aurora_accuracy']):+.2f} pp | "
            f"{100*(s['orbit_balanced_accuracy']-s['aurora_balanced_accuracy']):+.2f} pp | "
            f"{s['orbit_brier']-s['aurora_brier']:+.4f} |"
        )

    for block,v in results.items():
        lines += ["",f"## {block}","",
                  "| Period | AURORA Acc | ORBIT Acc | AURORA BA | ORBIT BA | AURORA Brier | ORBIT Brier | Rescue | Broken |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for period in ["SELECT_2022_H2","2023","2024","2025","2026","2025-2026"]:
            q=[x for x in v["metrics"] if x["period"]==period]
            if not q: continue
            r=q[0]
            transport_mark="" if (period in ["SELECT_2022_H2","2023","2024"] or v["confirmation_pass"]) else "†"
            lines.append(
                f"| {period}{transport_mark} | {100*r['aurora_accuracy']:.2f}% | {100*r['orbit_accuracy']:.2f}% | "
                f"{100*r['aurora_balanced_accuracy']:.2f}% | {100*r['orbit_balanced_accuracy']:.2f}% | "
                f"{r['aurora_brier']:.4f} | {r['orbit_brier']:.4f} | {int(r['rescued'])} | {int(r['broken'])} |"
            )
        if not v["confirmation_pass"]:
            lines.append("\n† Later-period values are diagnostic only because the block did not pass frozen confirmation.")

    lines += ["","## Decision",""]
    if hourly_candidates:
        lines.append(
            "Acquire hourly history only for the confirmed daily information family/families: "
            + ", ".join(hourly_candidates) + "."
        )
    else:
        lines.append("No daily external family justified broad hourly acquisition under this V1 screen.")

    lines += ["","## Governance","",
              "Official historical FX/rates/risk series are reconstructed with conservative release lags; they are not claimed as original stored PIT observations. "
              "No 2025/2026 result changed a feature, block, lag or ridge penalty. Frozen AURORA prospective validation remains untouched."]

    (OUT/"ORBIT_D1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"ORBIT_D1_RESULT.md").read_text())


if __name__=="__main__":
    main()
