from __future__ import annotations

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
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_orbit_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

API = "https://api.twelvedata.com/time_series"
TZ = iris.TZ
SILVER_SYMBOL = "XAG/USD"

C = 0.25
UP_OVERRIDE = 0.70
DOWN_OVERRIDE = 0.30
MIN_TRAIN = 80
SEED = 20261002
HEADS = ["CROSS_ONLY", "AURORA_PLUS_CROSS"]

HORIZONS = [1,3,6,12,24,48]
LAGS = [1,3,6]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1-1e-6)
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
        ("model", LogisticRegression(C=C, solver="lbfgs", max_iter=3000, random_state=SEED)),
    ])


def fetch_gold():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("ORBIT_GOLD_SOURCE_BRIDGE_FAIL")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    g = pd.concat([hist, ext], ignore_index=True)
    g = g.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return g, bridge, api_calls


def api_request_symbol(symbol, start_local, end_local):
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    params = {
        "symbol": symbol,
        "interval": "1h",
        "start_date": pd.Timestamp(start_local).strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": pd.Timestamp(end_local).strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": TZ,
        "order": "ASC",
        "outputsize": 5000,
        "apikey": key,
    }
    for attempt in range(5):
        r = requests.get(API, params=params, timeout=60)
        try:
            payload = r.json()
        except Exception:
            payload = {"status":"error","code":f"NON_JSON_{r.status_code}"}
        code = payload.get("code") if isinstance(payload, dict) else None
        if r.status_code == 429 or code == 429:
            if attempt == 4:
                raise RuntimeError("ORBIT_TWELVE_RATE_LIMIT_EXHAUSTED")
            time.sleep(65)
            continue
        if r.status_code != 200:
            raise RuntimeError(f"ORBIT_TWELVE_HTTP_{r.status_code}_CODE_{code}")
        vals = payload.get("values") if isinstance(payload, dict) else None
        if not vals:
            msg = payload.get("message") if isinstance(payload, dict) else None
            raise RuntimeError(f"ORBIT_TWELVE_EMPTY_{symbol}_{code}_{str(msg)[:120]}")
        return vals
    raise AssertionError


def fetch_silver():
    start = pd.Timestamp("2022-01-01 00:00:00")
    final = pd.Timestamp("2026-10-01 00:00:00")
    cur = start
    rows = []
    calls = 0
    while cur < final:
        nxt = min(cur + pd.DateOffset(months=5), final)
        print(f"ORBIT_XAG_CHUNK start={cur} end={nxt}", flush=True)
        try:
            vals = api_request_symbol(SILVER_SYMBOL, cur, nxt)
        except Exception as e:
            raise RuntimeError(f"ORBIT_XAG_CHUNK_FAIL start={cur} end={nxt} err={e}") from e
        calls += 1
        for row in vals:
            dt = row.get("datetime")
            close = row.get("close")
            if dt is None or close is None:
                continue
            try:
                ts = pd.Timestamp(dt).tz_localize(TZ, ambiguous="NaT", nonexistent="shift_forward").tz_convert("UTC")
                v = float(close)
            except Exception:
                continue
            if pd.isna(ts) or not np.isfinite(v) or v <= 0:
                continue
            rows.append((ts,v))
        cur = nxt
        if cur < final:
            time.sleep(8)
    if not rows:
        raise RuntimeError("ORBIT_NO_SILVER_ROWS")
    x = pd.DataFrame(rows, columns=["ts","silver"])
    x = x.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return x, calls


def safe_corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if len(a)<4 or len(b)<4 or np.std(a)<1e-10 or np.std(b)<1e-10:
        return 0.0
    v=np.corrcoef(a,b)[0,1]
    return float(v) if np.isfinite(v) else 0.0


def depth2_area(points):
    p=np.asarray(points,float)
    s1=np.zeros(2,float)
    s2=np.zeros((2,2),float)
    for dx in np.diff(p,axis=0):
        s2 = s2 + np.outer(s1,dx) + 0.5*np.outer(dx,dx)
        s1 = s1 + dx
    return float(s2[0,1]-s2[1,0])


def signature_area(rs, rg):
    rs=np.asarray(rs,float); rg=np.asarray(rg,float)
    ss=float(np.sqrt(np.sum(rs*rs))+1e-12)
    sg=float(np.sqrt(np.sum(rg*rg))+1e-12)
    xs=np.concatenate([[0.0],np.cumsum(rs/ss)])
    xg=np.concatenate([[0.0],np.cumsum(rg/sg)])
    return depth2_area(np.column_stack([xs,xg]))


def build_cross_features(gold, silver, dates):
    g=gold.rename(columns={"value":"gold"})[["ts","gold"]].copy()
    m=g.merge(silver,on="ts",how="inner").sort_values("ts").reset_index(drop=True)
    m["lg"]=np.log(m.gold.astype(float))
    m["ls"]=np.log(m.silver.astype(float))

    rows=[]
    for d in sorted(pd.to_datetime(pd.Series(list(dates))).dropna().unique()):
        d=pd.Timestamp(d)
        anchor_local=pd.Timestamp(f"{d.date()} 16:00:00").tz_localize(TZ)
        anchor_utc=anchor_local.tz_convert("UTC")
        z=m[m.ts<=anchor_utc].tail(49).copy()
        if len(z)<49:
            continue
        rg=np.diff(z.lg.to_numpy(float))
        rs=np.diff(z.ls.to_numpy(float))
        if len(rg)!=48 or len(rs)!=48:
            continue

        row={"feature_cutoff_date":d}
        for h in HORIZONS:
            row[f"xag_r{h}"]=float(np.sum(rs[-h:]))
            row[f"rel_r{h}"]=float(np.sum(rg[-h:])-np.sum(rs[-h:]))

        for h in [24,48]:
            gg=rg[-h:]; ss=rs[-h:]
            row[f"corr{h}"]=safe_corr(gg,ss)
            row[f"sign_agree{h}"]=float(np.mean(np.sign(gg)==np.sign(ss)))
            row[f"vol_ratio{h}"]=float((np.sqrt(np.sum(gg*gg))+1e-12)/(np.sqrt(np.sum(ss*ss))+1e-12))
            row[f"sig_area{h}"]=signature_area(ss,gg)

        for lag in LAGS:
            row[f"s_leads_g_{lag}"]=safe_corr(rs[:-lag],rg[lag:])
            row[f"g_leads_s_{lag}"]=safe_corr(rg[:-lag],rs[lag:])
            row[f"lead_diff_{lag}"]=row[f"s_leads_g_{lag}"]-row[f"g_leads_s_{lag}"]

        rows.append(row)
    return pd.DataFrame(rows), m


def cross_cols():
    cols=[]
    for h in HORIZONS:
        cols += [f"xag_r{h}",f"rel_r{h}"]
    for h in [24,48]:
        cols += [f"corr{h}",f"sign_agree{h}",f"vol_ratio{h}",f"sig_area{h}"]
    for lag in LAGS:
        cols += [f"s_leads_g_{lag}",f"g_leads_s_{lag}",f"lead_diff_{lag}"]
    return cols


def fill_xy(tr,te,cols):
    a=tr[cols].copy(); b=te[cols].copy()
    for c in cols:
        a[c]=pd.to_numeric(a[c],errors="coerce")
        b[c]=pd.to_numeric(b[c],errors="coerce")
        med=a[c].median(skipna=True)
        v=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(v); b[c]=b[c].fillna(v)
    return a.to_numpy(float),b.to_numpy(float)


def walk_head(panel, head):
    ccols=cross_cols()
    cols=ccols if head=="CROSS_ONLY" else ["base_logit"]+ccols
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
        md=model(); md.fit(Xtr,ytr)
        pcross=md.predict_proba(Xte)[:,1]

        for r,p_orbit in zip(te.itertuples(),pcross):
            p_base=float(r.p_aurora)
            bdir=int(p_base>=0.5)
            rescue=False; pout=p_base
            if bdir==0 and p_orbit>=UP_OVERRIDE:
                rescue=True; pout=float(p_orbit)
            elif bdir==1 and p_orbit<=DOWN_OVERRIDE:
                rescue=True; pout=float(p_orbit)
            odir=int(pout>=0.5)
            actual=int(r.y_up)
            rows.append({
                "head":head,
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":actual,"target_r3":float(r.target_r3),
                "p_aurora":p_base,"p_orbit_head":float(p_orbit),"p_orbit":pout,
                "aurora_dir":bdir,"orbit_dir":odir,
                "rescue":bool(rescue),
                "rescue_correct":bool(rescue and bdir!=actual and odir==actual),
                "rescue_broken":bool(rescue and bdir==actual and odir!=actual),
                "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows)


def period_rows(led):
    rows=[]
    specs=[
        ("SELECT_2022_H2",led.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",led.year==2023),("2024",led.year==2024),
        ("2025",led.year==2025),("2026",led.year==2026),
        ("2023-2024",led.year.isin([2023,2024])),
        ("2025-2026",led.year.isin([2025,2026])),
    ]
    for period,mask in specs:
        z=led[mask].copy()
        if z.empty: continue
        for name,col in [("AURORA","p_aurora"),("ORBIT","p_orbit")]:
            mm=metrics(z.y_up,z[col])
            rows.append({
                "period":period,"model":name,**mm,
                "rescues":int(z.rescue.sum()) if name=="ORBIT" else 0,
                "rescue_correct":int(z.rescue_correct.sum()) if name=="ORBIT" else 0,
                "rescue_broken":int(z.rescue_broken.sum()) if name=="ORBIT" else 0,
            })
    return pd.DataFrame(rows)


def select_head(ledgers):
    rows=[]
    for head,led in ledgers.items():
        mdf=period_rows(led)
        b=mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="AURORA")].iloc[0]
        o=mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="ORBIT")].iloc[0]
        eligible=bool(
            o.balanced_accuracy+1e-12>=b.balanced_accuracy
            and o.accuracy+0.005+1e-12>=b.accuracy
            and o.brier<=b.brier+0.0025+1e-12
            and int(o.rescues)>=3
        )
        rows.append({
            "head":head,"eligible":eligible,
            "delta_accuracy":float(o.accuracy-b.accuracy),
            "delta_balanced_accuracy":float(o.balanced_accuracy-b.balanced_accuracy),
            "delta_brier":float(o.brier-b.brier),
            "delta_logloss":float(o.logloss-b.logloss),
            "rescues":int(o.rescues),"rescue_correct":int(o.rescue_correct),"rescue_broken":int(o.rescue_broken),
            "accuracy":float(o.accuracy),"balanced_accuracy":float(o.balanced_accuracy),
            "brier":float(o.brier),"logloss":float(o.logloss),
        })
    tab=pd.DataFrame(rows)
    e=tab[tab.eligible].copy()
    if e.empty: return tab,None
    e=e.sort_values(["balanced_accuracy","accuracy","brier","logloss"],ascending=[False,False,True,True])
    return tab,str(e.iloc[0]["head"])


def confirmation(mdf):
    checks=[]; ok=True
    for yr in ["2023","2024"]:
        b=mdf[(mdf.period==yr)&(mdf.model=="AURORA")].iloc[0]
        o=mdf[(mdf.period==yr)&(mdf.model=="ORBIT")].iloc[0]
        passed=bool(o.accuracy+0.01+1e-12>=b.accuracy and o.brier<=b.brier+0.003+1e-12)
        checks.append({
            "period":yr,"pass":passed,
            "base_accuracy":float(b.accuracy),"orbit_accuracy":float(o.accuracy),
            "base_balanced_accuracy":float(b.balanced_accuracy),"orbit_balanced_accuracy":float(o.balanced_accuracy),
            "base_brier":float(b.brier),"orbit_brier":float(o.brier),
        })
        ok=ok and passed
    b=mdf[(mdf.period=="2023-2024")&(mdf.model=="AURORA")].iloc[0]
    o=mdf[(mdf.period=="2023-2024")&(mdf.model=="ORBIT")].iloc[0]
    agg=bool(o.balanced_accuracy+1e-12>=b.balanced_accuracy)
    rescue=bool(int(o.rescue_correct)>0)
    return bool(ok and agg and rescue),checks,agg,rescue


def rescue_detail(led,year):
    z=led[(led.year==year)&(led.rescue)].copy()
    if z.empty: return z
    z["base_correct"]=z.aurora_dir.astype(int)==z.y_up.astype(int)
    z["orbit_correct"]=z.orbit_dir.astype(int)==z.y_up.astype(int)
    return z[[
        "forecast_issue_date","target_end_date_h3","target_r3",
        "p_aurora","p_orbit_head","p_orbit","aurora_dir","orbit_dir","y_up",
        "base_correct","orbit_correct"
    ]]


def main():
    base=pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        base[c]=pd.to_datetime(base[c],errors="raise")
    pp=np.clip(base.p_aurora.astype(float).to_numpy(),1e-6,1-1e-6)
    base["base_logit"]=np.log(pp/(1-pp))

    gold,bridge,gold_calls=fetch_gold()
    silver,silver_calls=fetch_silver()
    feats,aligned=build_cross_features(gold,silver,base.feature_cutoff_date.unique())

    panel=base.merge(feats,on="feature_cutoff_date",how="inner",validate="one_to_one")
    coverage=float(len(panel)/len(base))
    if coverage<0.95:
        raise RuntimeError(f"ORBIT_COVERAGE_FAIL {coverage:.4f}")
    panel=panel.sort_values("forecast_issue_date").reset_index(drop=True)

    ledgers={}
    for head in HEADS:
        led=walk_head(panel,head)
        ledgers[head]=led
        led.to_csv(OUT/f"orbit_v1_predictions_{head.lower()}.csv",index=False)

    grid,selected=select_head(ledgers)
    grid.to_csv(OUT/"orbit_v1_selection_grid.csv",index=False)

    source={
        "gold_bridge":bridge,
        "gold_api_calls":int(gold_calls),
        "silver_api_calls":int(silver_calls),
        "silver_rows":int(len(silver)),
        "aligned_hourly_rows":int(len(aligned)),
        "origin_coverage":coverage,
        "silver_first":str(silver.ts.min()),
        "silver_last":str(silver.ts.max()),
        "raw_vendor_values_committed":False,
    }
    (OUT/"orbit_v1_source.json").write_text(json.dumps(source,indent=2,default=str)+"\n")

    if selected is None:
        summary={"schema":"ORBIT_H3_V1","status":"FAIL_CLOSED_NO_ELIGIBLE_CROSS_ASSET_HEAD",
                 "selected_head":None,"selection_grid":grid.to_dict(orient="records"),"source":source}
        (OUT/"orbit_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")
        (OUT/"ORBIT_V1_RESULT.md").write_text(
            "# ORBIT-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 cross-asset rescue head.\n"
        )
        print((OUT/"ORBIT_V1_RESULT.md").read_text())
        return

    led=ledgers[selected]
    mdf=period_rows(led)
    mdf.to_csv(OUT/"orbit_v1_metrics.csv",index=False)
    ok,checks,agg_ok,rescue_ok=confirmation(mdf)
    status="MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    led.to_csv(OUT/"orbit_v1_selected_predictions.csv",index=False)
    d26=rescue_detail(led,2026)
    d26.to_csv(OUT/"orbit_v1_2026_rescue_detail.csv",index=False)

    summary={
        "schema":"ORBIT_H3_V1","status":status,"selected_head":selected,
        "source":source,"selection_grid":grid.to_dict(orient="records"),
        "confirmation_pass":bool(ok),"confirmation_checks":checks,
        "aggregate_balanced_guard":bool(agg_ok),"rescue_present":bool(rescue_ok),
        "metrics":mdf.to_dict(orient="records"),"rescue_2026":d26.to_dict(orient="records"),
    }
    (OUT/"orbit_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# ORBIT-H3 V1 — CROSS-BULLION LEAD-LAG RESCUE RESULT","",
        f"**Status:** **{status}**  ",
        f"**Selected head (2022-H2 only):** **{selected}**  ",
        f"**Silver origin coverage:** **{100*coverage:.2f}%**  ",
        f"**Override:** ORBIT p>=0.70 against DOWN / <=0.30 against UP  ",
        f"**2023 + 2024 confirmation:** **{ok}**","",
        "## Selection grid — 2022 H2","",
        "| Head | Eligible | ΔAcc | ΔBA | ΔBrier | Overrides | Correct rescue | Broken |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.head} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} | "
            f"{int(r.rescues)} | {int(r.rescue_correct)} | {int(r.rescue_broken)} |"
        )

    lines += ["","## Period metrics","",
              "| Model | Period | N | Accuracy | Balanced | Brier | Overrides | Correct rescue | Broken |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2","2023","2024","2025","2026","2025-2026"]:
        for name in ["AURORA","ORBIT"]:
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
        lines += ["| Issue | Target end | AURORA pUP | ORBIT head pUP | AURORA | ORBIT | Actual | H3 return | Base correct | ORBIT correct |",
                  "|---|---|---:|---:|---|---|---|---:|---|---|"]
        for r in d26.itertuples():
            ad="UP" if int(r.aurora_dir)==1 else "DOWN"
            od="UP" if int(r.orbit_dir)==1 else "DOWN"
            yy="UP" if int(r.y_up)==1 else "DOWN"
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{100*r.p_aurora:.1f}% | {100*r.p_orbit_head:.1f}% | {ad} | {od} | {yy} | "
                f"{100*r.target_r3:+.2f}% | {bool(r.base_correct)} | {bool(r.orbit_correct)} |"
            )

    lines += ["","## Governance","",
              "Only CROSS_ONLY vs AURORA_PLUS_CROSS used 2022-H2 selection. Feature set, lags, C and rescue thresholds were frozen before the run. "
              "2025/2026 did not alter V1. The AURORA prospective champion remains frozen and unchanged."]

    (OUT/"ORBIT_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"ORBIT_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
