from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_signet_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

C = 0.25
UP_OVERRIDE = 0.70
DOWN_OVERRIDE = 0.30
MIN_TRAIN = 80
SEED = 20261002
REPS = ["SIG24", "SIG48", "SIG_MULTI"]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=C, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def depth2_signature(points):
    p = np.asarray(points, float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 2:
        raise ValueError("2D path required")
    s1 = np.zeros(2, float)
    s2 = np.zeros((2,2), float)
    for dx in np.diff(p, axis=0):
        s2 = s2 + np.outer(s1, dx) + 0.5*np.outer(dx, dx)
        s1 = s1 + dx
    return np.concatenate([s1, s2.reshape(-1)])


def signature_window(rets):
    r = np.asarray(rets, float)
    scale = float(np.sqrt(np.sum(r*r)) + 1e-12)
    rn = r / scale
    x = np.concatenate([[0.0], np.cumsum(rn)])

    t = np.linspace(0.0, 1.0, len(x))
    time_return = np.column_stack([t, x])
    sig_time = depth2_signature(time_return)

    ll = [(x[0], x[0])]
    for i in range(1, len(x)):
        ll.append((x[i], x[i-1]))
        ll.append((x[i], x[i]))
    sig_ll = depth2_signature(np.asarray(ll, float))

    return np.concatenate([sig_time, sig_ll])


def fetch_hourly():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("SIGNET_SOURCE_BRIDGE_FAIL")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    h = pd.concat([hist, ext], ignore_index=True)
    h = h.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return h, bridge, api_calls


def build_embeddings(hourly, dates):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["logp"] = np.log(q.value.astype(float))
    rows = []

    for d in sorted(pd.to_datetime(pd.Series(list(dates))).dropna().unique()):
        d = pd.Timestamp(d)
        anchor_local = pd.Timestamp(f"{d.date()} 16:00:00").tz_localize(iris.TZ)
        anchor_utc = anchor_local.tz_convert("UTC")
        z = q[q.ts <= anchor_utc].tail(49)
        if len(z) < 49:
            continue
        rets48 = np.diff(z.logp.to_numpy(float))
        if len(rets48) != 48:
            continue
        rets24 = rets48[-24:]

        s24 = signature_window(rets24)
        s48 = signature_window(rets48)
        row = {"feature_cutoff_date": d}
        for i,v in enumerate(s24):
            row[f"sig24_{i}"] = float(v)
        for i,v in enumerate(s48):
            row[f"sig48_{i}"] = float(v)
        rows.append(row)

    return pd.DataFrame(rows)


def rep_cols(rep):
    c24=[f"sig24_{i}" for i in range(12)]
    c48=[f"sig48_{i}" for i in range(12)]
    if rep=="SIG24": return c24
    if rep=="SIG48": return c48
    if rep=="SIG_MULTI": return c24+c48
    raise KeyError(rep)


def fill_xy(tr, te, cols):
    a=tr[cols].copy()
    b=te[cols].copy()
    for c in cols:
        a[c]=pd.to_numeric(a[c], errors="coerce")
        b[c]=pd.to_numeric(b[c], errors="coerce")
        med=a[c].median(skipna=True)
        v=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(v)
        b[c]=b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def walk_signature(panel, rep):
    cols=rep_cols(rep)
    test=panel[panel.forecast_issue_date>=pd.Timestamp("2022-06-01")].copy()
    rows=[]

    for mo in sorted(test.month.unique()):
        te=test[test.month==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=panel[
            (panel.target_end_date_h3<=cutoff)
            & (panel.forecast_issue_date<first_issue)
        ].copy()
        if len(tr)<MIN_TRAIN:
            continue

        Xtr,Xte=fill_xy(tr,te,cols)
        ytr=tr.y_up.astype(int).to_numpy()
        m=model()
        m.fit(Xtr,ytr)
        ps=m.predict_proba(Xte)[:,1]

        for r, p_sig in zip(te.itertuples(), ps):
            p_base=float(r.p_aurora)
            base_dir=int(p_base>=0.5)
            rescue=False
            p_out=p_base
            if base_dir==0 and p_sig>=UP_OVERRIDE:
                rescue=True
                p_out=float(p_sig)
            elif base_dir==1 and p_sig<=DOWN_OVERRIDE:
                rescue=True
                p_out=float(p_sig)

            out_dir=int(p_out>=0.5)
            actual=int(r.y_up)
            rows.append({
                "rep":rep,
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),
                "month":str(r.month),
                "y_up":actual,
                "target_r3":float(r.target_r3),
                "p_aurora":p_base,
                "p_signature":float(p_sig),
                "p_signet":p_out,
                "aurora_dir":base_dir,
                "signet_dir":out_dir,
                "rescue":bool(rescue),
                "rescue_correct":bool(rescue and base_dir!=actual and out_dir==actual),
                "rescue_broken":bool(rescue and base_dir==actual and out_dir!=actual),
                "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows)


def period_rows(led):
    rows=[]
    specs=[
        ("SELECT_2022_H2",led.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",led.year==2023),
        ("2024",led.year==2024),
        ("2025",led.year==2025),
        ("2026",led.year==2026),
        ("2023-2024",led.year.isin([2023,2024])),
        ("2025-2026",led.year.isin([2025,2026])),
    ]
    for period,mask in specs:
        z=led[mask].copy()
        if z.empty: continue
        for name,col in [("AURORA","p_aurora"),("SIGNET","p_signet")]:
            m=metrics(z.y_up,z[col])
            rows.append({
                "period":period,"model":name,**m,
                "rescues":int(z.rescue.sum()) if name=="SIGNET" else 0,
                "rescue_correct":int(z.rescue_correct.sum()) if name=="SIGNET" else 0,
                "rescue_broken":int(z.rescue_broken.sum()) if name=="SIGNET" else 0,
            })
    return pd.DataFrame(rows)


def select_rep(ledgers):
    rows=[]
    for rep,led in ledgers.items():
        mdf=period_rows(led)
        b=mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="AURORA")].iloc[0]
        s=mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="SIGNET")].iloc[0]
        eligible=bool(
            s.balanced_accuracy+1e-12>=b.balanced_accuracy
            and s.accuracy+0.005+1e-12>=b.accuracy
            and s.brier<=b.brier+0.0025+1e-12
            and int(s.rescues)>=3
        )
        rows.append({
            "rep":rep,"eligible":eligible,
            "delta_accuracy":float(s.accuracy-b.accuracy),
            "delta_balanced_accuracy":float(s.balanced_accuracy-b.balanced_accuracy),
            "delta_brier":float(s.brier-b.brier),
            "delta_logloss":float(s.logloss-b.logloss),
            "rescues":int(s.rescues),
            "rescue_correct":int(s.rescue_correct),
            "rescue_broken":int(s.rescue_broken),
            "accuracy":float(s.accuracy),
            "balanced_accuracy":float(s.balanced_accuracy),
            "brier":float(s.brier),
            "logloss":float(s.logloss),
        })
    tab=pd.DataFrame(rows)
    e=tab[tab.eligible].copy()
    if e.empty: return tab,None
    e=e.sort_values(["balanced_accuracy","accuracy","brier","logloss"],ascending=[False,False,True,True])
    return tab,str(e.iloc[0].rep)


def confirmation(mdf):
    checks=[]
    ok=True
    for yr in ["2023","2024"]:
        b=mdf[(mdf.period==yr)&(mdf.model=="AURORA")].iloc[0]
        s=mdf[(mdf.period==yr)&(mdf.model=="SIGNET")].iloc[0]
        passed=bool(
            s.accuracy+0.01+1e-12>=b.accuracy
            and s.brier<=b.brier+0.003+1e-12
        )
        checks.append({
            "period":yr,"pass":passed,
            "base_accuracy":float(b.accuracy),
            "signet_accuracy":float(s.accuracy),
            "base_balanced_accuracy":float(b.balanced_accuracy),
            "signet_balanced_accuracy":float(s.balanced_accuracy),
            "base_brier":float(b.brier),
            "signet_brier":float(s.brier),
        })
        ok=ok and passed
    b=mdf[(mdf.period=="2023-2024")&(mdf.model=="AURORA")].iloc[0]
    s=mdf[(mdf.period=="2023-2024")&(mdf.model=="SIGNET")].iloc[0]
    agg=bool(s.balanced_accuracy+1e-12>=b.balanced_accuracy)
    rescue=bool(int(s.rescues)>0)
    return bool(ok and agg and rescue),checks,agg,rescue


def rescue_detail(led,year):
    z=led[(led.year==year)&(led.rescue)].copy()
    if z.empty: return z
    z["base_correct"]=z.aurora_dir.astype(int)==z.y_up.astype(int)
    z["signet_correct"]=z.signet_dir.astype(int)==z.y_up.astype(int)
    return z[[
        "forecast_issue_date","target_end_date_h3","target_r3",
        "p_aurora","p_signature","p_signet","aurora_dir","signet_dir","y_up",
        "base_correct","signet_correct"
    ]]


def main():
    base=pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        base[c]=pd.to_datetime(base[c],errors="raise")

    hourly,bridge,api_calls=fetch_hourly()
    emb=build_embeddings(hourly,base.feature_cutoff_date.unique())
    panel=base.merge(emb,on="feature_cutoff_date",how="inner",validate="one_to_one")
    if len(panel)!=len(base):
        raise RuntimeError(f"SIGNET_EMBEDDING_MATCH_FAIL base={len(base)} panel={len(panel)}")
    panel=panel.sort_values("forecast_issue_date").reset_index(drop=True)

    ledgers={}
    for rep in REPS:
        led=walk_signature(panel,rep)
        ledgers[rep]=led
        led.to_csv(OUT/f"signet_v1_predictions_{rep.lower()}.csv",index=False)

    grid,selected=select_rep(ledgers)
    grid.to_csv(OUT/"signet_v1_selection_grid.csv",index=False)

    if selected is None:
        summary={
            "schema":"SIGNET_H3_V1",
            "status":"FAIL_CLOSED_NO_ELIGIBLE_SIGNATURE_REPRESENTATION",
            "source_bridge":bridge,
            "api_calls":int(api_calls),
            "selection_grid":grid.to_dict(orient="records"),
        }
        (OUT/"signet_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")
        (OUT/"SIGNET_V1_RESULT.md").write_text(
            "# SIGNET-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 signature representation.\n"
        )
        print((OUT/"SIGNET_V1_RESULT.md").read_text())
        return

    led=ledgers[selected]
    mdf=period_rows(led)
    mdf.to_csv(OUT/"signet_v1_metrics.csv",index=False)

    ok,checks,agg_ok,rescue_ok=confirmation(mdf)
    status="MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    led.to_csv(OUT/"signet_v1_selected_predictions.csv",index=False)
    d26=rescue_detail(led,2026)
    d26.to_csv(OUT/"signet_v1_2026_rescue_detail.csv",index=False)

    summary={
        "schema":"SIGNET_H3_V1",
        "status":status,
        "selected_representation":selected,
        "source_bridge":bridge,
        "api_calls":int(api_calls),
        "selection_grid":grid.to_dict(orient="records"),
        "confirmation_pass":bool(ok),
        "confirmation_checks":checks,
        "aggregate_balanced_guard":bool(agg_ok),
        "rescue_present":bool(rescue_ok),
        "metrics":mdf.to_dict(orient="records"),
        "rescue_2026":d26.to_dict(orient="records"),
    }
    (OUT/"signet_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# SIGNET-H3 V1 — SIGNATURE GEOMETRY RESCUE RESULT","",
        f"**Status:** **{status}**  ",
        f"**Selected representation (2022-H2 only):** **{selected}**  ",
        f"**Logistic C:** {C}  ",
        f"**Override:** signature p>=0.70 against DOWN / <=0.30 against UP  ",
        f"**2023 + 2024 confirmation:** **{ok}**","",
        "## Selection grid — 2022 H2","",
        "| Representation | Eligible | ΔAcc | ΔBA | ΔBrier | Rescues | Correct rescue | Broken |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.rep} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} | "
            f"{int(r.rescues)} | {int(r.rescue_correct)} | {int(r.rescue_broken)} |"
        )

    lines += ["","## Period metrics","",
              "| Model | Period | N | Accuracy | Balanced | Brier | Rescues | Correct rescue | Broken |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2","2023","2024","2025","2026","2025-2026"]:
        for name in ["AURORA","SIGNET"]:
            q=mdf[(mdf.period==period)&(mdf.model==name)]
            if q.empty: continue
            r=q.iloc[0]
            lines.append(
                f"| {name} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{int(r.rescues)} | {int(r.rescue_correct)} | {int(r.rescue_broken)} |"
            )

    lines += ["","## 2026 override details",""]
    if d26.empty:
        lines.append("- no 2026 overrides")
    else:
        lines += ["| Issue | Target end | AURORA pUP | Signature pUP | AURORA | SIGNET | Actual | H3 return | Base correct | SIGNET correct |",
                  "|---|---|---:|---:|---|---|---|---:|---|---|"]
        for r in d26.itertuples():
            ad="UP" if int(r.aurora_dir)==1 else "DOWN"
            sd="UP" if int(r.signet_dir)==1 else "DOWN"
            yy="UP" if int(r.y_up)==1 else "DOWN"
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{100*r.p_aurora:.1f}% | {100*r.p_signature:.1f}% | {ad} | {sd} | {yy} | "
                f"{100*r.target_r3:+.2f}% | {bool(r.base_correct)} | {bool(r.signet_correct)} |"
            )

    lines += ["","## Governance","",
              "Only signature representation used 2022-H2 selection. C=0.25, depth=2 and rescue thresholds 0.70/0.30 were fixed before the run. "
              "2025/2026 did not alter V1. Frozen AURORA prospective validation remains untouched."]

    (OUT/"SIGNET_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"SIGNET_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
