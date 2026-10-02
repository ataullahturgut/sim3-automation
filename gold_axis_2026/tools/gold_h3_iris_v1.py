from __future__ import annotations

import io
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "gold_axis_2026" / "GOLD_H3_NOVA_V1_PREDICTIONS_2026-10-02.csv"
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_iris_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
API = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
TZ = "America/New_York"
SEED = 20261002

BRIDGE_MIN_COMMON = 250
BRIDGE_MIN_PEARSON = 0.99
BRIDGE_MIN_SIGN = 0.95
BRIDGE_MAX_DIFF_SD = 0.0015

PATH = [
    "h_ret_1", "h_ret_3", "h_ret_6", "h_ret_12", "h_ret_24", "h_ret_48",
    "h_lag2", "h_session_ret",
]
VOL = [
    "h_rv_6", "h_rv_12", "h_rv_24", "h_rv_48",
    "h_up_semivol_24", "h_down_semivol_24", "h_down_up_semivol_ratio_24",
    "h_jump_concentration_24", "h_range_24",
]
SHAPE = [
    "h_upfrac_24", "h_slope_6", "h_slope_24",
    "h_max_drawdown_24", "h_recovery_24", "h_close_location_24",
    "h_age_max_pos_24", "h_age_max_neg_24",
]
ALL_HOURLY = PATH + VOL + SHAPE

CANDIDATES = {
    "HOURLY_ONLY_ALL": ALL_HOURLY,
    "A1_PLUS_PATH": ["base_logit"] + PATH,
    "A1_PLUS_VOL": ["base_logit"] + VOL,
    "A1_PLUS_SHAPE": ["base_logit"] + SHAPE,
    "A1_PLUS_ALL": ["base_logit"] + ALL_HOURLY,
}


def load_ledger():
    df = pd.read_csv(LEDGER)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        df[c] = pd.to_datetime(df[c], errors="raise")
    df = df[df.forecast_issue_date.dt.year.between(2022, 2026)].copy()
    p = np.clip(pd.to_numeric(df.p_A1_arcr, errors="coerce").to_numpy(float), 1e-5, 1 - 1e-5)
    df["base_logit"] = np.log(p / (1.0 - p))
    df["base_pred_up"] = (p >= 0.5).astype(int)
    df["feature_date"] = df.feature_cutoff_date.dt.date
    return df.sort_values("forecast_issue_date").reset_index(drop=True)


def load_neon_hourly():
    dsn = os.environ["NEON_DATABASE_URL"]
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT observation_ts, value, retrieved_at
                FROM observations
                WHERE series_id=%s
                ORDER BY observation_ts, retrieved_at
                """,
                (SERIES_ID,),
            )
            rows = cur.fetchall()
        conn.rollback()
    if not rows:
        raise RuntimeError("NO_NEON_HOURLY_ROWS")
    x = pd.DataFrame(rows, columns=["ts", "value", "retrieved_at"])
    x["ts"] = pd.to_datetime(x.ts, utc=True)
    x["value"] = pd.to_numeric(x.value, errors="coerce")
    x = x.dropna(subset=["value"])
    x = x[x.value > 0].copy()
    x = (
        x.sort_values(["ts", "retrieved_at"])
        .drop_duplicates("ts", keep="last")
        .sort_values("ts")
        .reset_index(drop=True)
    )
    return x[["ts", "value"]].copy()


def api_request(start_local: pd.Timestamp, end_local: pd.Timestamp):
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    params = {
        "symbol": SYMBOL,
        "interval": "1h",
        "start_date": start_local.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_local.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": TZ,
        "order": "ASC",
        "outputsize": 5000,
        "apikey": key,
    }
    for attempt in range(4):
        r = requests.get(API, params=params, timeout=60)
        try:
            payload = r.json()
        except Exception:
            payload = {"status": "error", "code": f"NON_JSON_HTTP_{r.status_code}"}
        if r.status_code == 429 or (isinstance(payload, dict) and payload.get("code") == 429):
            if attempt == 3:
                raise RuntimeError("TWELVE_RATE_LIMIT_EXHAUSTED")
            time.sleep(65)
            continue
        if r.status_code != 200:
            code = payload.get("code") if isinstance(payload, dict) else None
            raise RuntimeError(f"TWELVE_HTTP_{r.status_code}_CODE_{code}")
        values = payload.get("values") if isinstance(payload, dict) else None
        if not values:
            code = payload.get("code") if isinstance(payload, dict) else None
            msg = payload.get("message") if isinstance(payload, dict) else None
            raise RuntimeError(f"TWELVE_EMPTY_CODE_{code}_MSG_{str(msg)[:120]}")
        return values
    raise AssertionError("unreachable")


def fetch_extension():
    # Query 2024-12 for overlap plus two-month chunks through 2026-09-30.
    start = pd.Timestamp("2024-12-01 00:00:00")
    final = pd.Timestamp("2026-10-01 00:00:00")
    rows = []
    cur = start
    calls = 0
    while cur < final:
        nxt = min(cur + pd.DateOffset(months=2), final)
        values = api_request(cur, nxt)
        calls += 1
        for row in values:
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
            rows.append((ts, v))
        cur = nxt
        if cur < final:
            time.sleep(8)
    if not rows:
        raise RuntimeError("NO_SUCCESSOR_HOURLY_ROWS")
    x = pd.DataFrame(rows, columns=["ts", "value"])
    x = x.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return x, calls


def bridge_metrics(hist, succ):
    h = hist[(hist.ts >= pd.Timestamp("2024-12-01", tz="UTC")) & (hist.ts < pd.Timestamp("2025-01-01", tz="UTC"))].copy()
    s = succ[(succ.ts >= pd.Timestamp("2024-12-01", tz="UTC")) & (succ.ts < pd.Timestamp("2025-01-01", tz="UTC"))].copy()
    b = h.rename(columns={"value": "hist"}).merge(
        s.rename(columns={"value": "succ"}), on="ts", how="inner"
    ).sort_values("ts")
    if len(b) < 2:
        return b, {
            "common_level_rows": int(len(b)),
            "common_return_rows": 0,
            "pearson": np.nan,
            "sign_agreement": np.nan,
            "return_diff_sd": np.nan,
            "pass": False,
        }
    b["rh"] = np.log(pd.to_numeric(b["hist"], errors="coerce")).diff()
    b["rs"] = np.log(pd.to_numeric(b["succ"], errors="coerce")).diff()
    q = b.dropna(subset=["rh", "rs"]).copy()
    diff = q.rh - q.rs
    pear = float(q.rh.corr(q.rs)) if len(q) > 1 else np.nan
    sign = float(((q.rh > 0) == (q.rs > 0)).mean()) if len(q) else np.nan
    dsd = float(diff.std(ddof=0)) if len(q) else np.nan
    m = {
        "common_level_rows": int(len(b)),
        "common_return_rows": int(len(q)),
        "pearson": pear,
        "sign_agreement": sign,
        "return_diff_sd": dsd,
    }
    m["pass"] = bool(
        len(q) >= BRIDGE_MIN_COMMON
        and np.isfinite(pear) and pear >= BRIDGE_MIN_PEARSON
        and np.isfinite(sign) and sign >= BRIDGE_MIN_SIGN
        and np.isfinite(dsd) and dsd <= BRIDGE_MAX_DIFF_SD
    )
    return b[["ts", "rh", "rs"]].copy(), m


def slope(a):
    a = np.asarray(a, float)
    if len(a) < 2 or not np.isfinite(a).all():
        return np.nan
    x = np.arange(len(a), dtype=float)
    xm = x.mean()
    ym = a.mean()
    den = np.sum((x - xm) ** 2)
    if den <= 0:
        return np.nan
    return float(np.sum((x - xm) * (a - ym)) / den)


def max_drawdown(a):
    a = np.asarray(a, float)
    if len(a) < 2 or not np.isfinite(a).all():
        return np.nan
    peak = np.maximum.accumulate(a)
    dd = a - peak
    return float(np.min(dd))


def age_extreme(a, which):
    a = np.asarray(a, float)
    if len(a) == 0 or not np.isfinite(a).all():
        return np.nan
    rev = a[::-1]
    idx = int(np.argmax(rev) if which == "max" else np.argmin(rev))
    return float(idx)


def build_anchor_features(hourly):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q.ts.dt.tz_convert(TZ)
    q["local_date"] = q.ts_ny.dt.date
    q["local_hour"] = q.ts_ny.dt.hour
    q["local_minute"] = q.ts_ny.dt.minute
    q["logp"] = np.log(q.value.astype(float))
    q["hr"] = q.logp.diff()

    for h in [1, 3, 6, 12, 24, 48]:
        q[f"h_ret_{h}"] = q.logp - q.logp.shift(h)

    q["h_lag2"] = q.hr.shift(2)

    for h in [6, 12, 24, 48]:
        q[f"h_rv_{h}"] = np.sqrt((q.hr.pow(2)).rolling(h, min_periods=h).sum())

    pos_sq = q.hr.clip(lower=0).pow(2)
    neg_sq = q.hr.clip(upper=0).pow(2)
    q["h_up_semivol_24"] = np.sqrt(pos_sq.rolling(24, min_periods=24).sum())
    q["h_down_semivol_24"] = np.sqrt(neg_sq.rolling(24, min_periods=24).sum())
    q["h_down_up_semivol_ratio_24"] = (
        q.h_down_semivol_24 / (q.h_up_semivol_24 + 1e-8)
    )
    q["h_jump_concentration_24"] = (
        q.hr.abs().rolling(24, min_periods=24).max() / (q.h_rv_24 + 1e-8)
    )
    q["h_range_24"] = (
        q.logp.rolling(24, min_periods=24).max()
        - q.logp.rolling(24, min_periods=24).min()
    )
    q["h_upfrac_24"] = (q.hr > 0).astype(float).rolling(24, min_periods=24).mean()
    q["h_slope_6"] = q.logp.rolling(6, min_periods=6).apply(slope, raw=True)
    q["h_slope_24"] = q.logp.rolling(24, min_periods=24).apply(slope, raw=True)
    q["h_max_drawdown_24"] = q.logp.rolling(24, min_periods=24).apply(max_drawdown, raw=True)
    trough = q.logp.rolling(24, min_periods=24).min()
    hi = q.logp.rolling(24, min_periods=24).max()
    q["h_recovery_24"] = q.logp - trough
    q["h_close_location_24"] = (q.logp - trough) / (hi - trough + 1e-8)
    q["h_age_max_pos_24"] = q.hr.rolling(24, min_periods=24).apply(
        lambda a: age_extreme(a, "max"), raw=True
    )
    q["h_age_max_neg_24"] = q.hr.rolling(24, min_periods=24).apply(
        lambda a: age_extreme(a, "min"), raw=True
    )

    first_log = q.groupby("local_date")["logp"].transform("first")
    q["h_session_ret"] = q.logp - first_log

    anchors = q[(q.local_hour == 16) & (q.local_minute == 0)].copy()
    anchors = anchors.sort_values("ts").drop_duplicates("local_date", keep="last")
    anchors = anchors.dropna(subset=ALL_HOURLY).copy()
    return anchors[["local_date", "ts"] + ALL_HOURLY].reset_index(drop=True)


def prepare_panel(ledger, anchors):
    panel = ledger.merge(
        anchors,
        left_on="feature_date",
        right_on="local_date",
        how="inner",
        validate="many_to_one",
    )
    # Explicit safety check: anchor local date equals feature cutoff date.
    if not (panel.feature_date == panel.local_date).all():
        raise RuntimeError("ANCHOR_DATE_MISMATCH")
    panel = panel.dropna(subset=["target_r3", "y_up", "p_A1_arcr", "base_logit"] + ALL_HOURLY).copy()
    panel["year"] = panel.forecast_issue_date.dt.year.astype(int)
    panel["month"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    return panel.sort_values("forecast_issue_date").reset_index(drop=True)


def make_logit():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def fill_xy(tr, te, features):
    a = tr[features].copy()
    b = te[features].copy()
    for c in features:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "false_call_rate": float(np.mean(pred != y)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def run_candidate(panel, model_name, features):
    test = panel[panel.year.between(2023, 2026)].copy()
    rows = []
    for month in sorted(test.month.unique()):
        te = test[test.month == month].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < te.forecast_issue_date.min())
        ].copy()
        if len(tr) < 180:
            raise RuntimeError(f"IRIS_TRAIN_TOO_SMALL {month} n={len(tr)}")
        Xtr, Xte = fill_xy(tr, te, features)
        ytr = tr.y_up.astype(int).to_numpy()
        model = make_logit()
        model.fit(Xtr, ytr)
        p = model.predict_proba(Xte)[:, 1]
        for r, pp in zip(te.itertuples(), p):
            rows.append({
                "model": model_name,
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_up": float(pp),
                "p_base_a1": float(r.p_A1_arcr),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows)


def base_ledger(panel):
    z = panel[panel.year.between(2023, 2026)].copy()
    return pd.DataFrame({
        "model": "BASE_A1",
        "feature_cutoff_date": z.feature_cutoff_date,
        "forecast_issue_date": z.forecast_issue_date,
        "target_end_date_h3": z.target_end_date_h3,
        "year": z.year.astype(int),
        "month": z.month.astype(str),
        "y_up": z.y_up.astype(int),
        "target_r3": z.target_r3.astype(float),
        "p_up": z.p_A1_arcr.astype(float),
        "p_base_a1": z.p_A1_arcr.astype(float),
        "train_n": np.nan,
    })


def score_periods(ledger):
    rows = []
    periods = [
        ("2023", lambda x: x.year == 2023),
        ("2024", lambda x: x.year == 2024),
        ("2025", lambda x: x.year == 2025),
        ("2026", lambda x: x.year == 2026),
        ("2023-2024", lambda x: x.year.isin([2023, 2024])),
        ("2025-2026", lambda x: x.year.isin([2025, 2026])),
    ]
    for model, g0 in ledger.groupby("model"):
        for label, fn in periods:
            g = g0[fn(g0)]
            if g.empty:
                continue
            rows.append({"model": model, "period": label, **metrics(g.y_up, g.p_up)})
    return pd.DataFrame(rows)


def select_2023(mdf):
    b = mdf[(mdf.model == "BASE_A1") & (mdf.period == "2023")].iloc[0]
    rows = []
    for name in CANDIDATES:
        r = mdf[(mdf.model == name) & (mdf.period == "2023")]
        if r.empty:
            continue
        r = r.iloc[0]
        eligible = bool(
            r.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and r.accuracy + 0.005 + 1e-12 >= b.accuracy
            and r.brier <= b.brier + 0.0025 + 1e-12
            and r.prediction_std >= 0.02
        )
        rows.append({
            "model": name,
            "eligible": eligible,
            "delta_accuracy": float(r.accuracy - b.accuracy),
            "delta_balanced_accuracy": float(r.balanced_accuracy - b.balanced_accuracy),
            "delta_brier": float(r.brier - b.brier),
            "delta_logloss": float(r.logloss - b.logloss),
            **{k: r[k] for k in [
                "n", "accuracy", "balanced_accuracy", "brier", "logloss",
                "up_recall", "down_recall", "false_call_rate", "prediction_std"
            ]},
        })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["balanced_accuracy", "accuracy", "brier", "logloss"],
        ascending=[False, False, True, True],
    )
    return tab, elig.iloc[0].to_dict()


def descriptive_coefficients(panel, selected):
    if selected is None:
        return pd.DataFrame()
    name = str(selected["model"])
    feats = CANDIDATES[name]
    cutoff = pd.Timestamp("2024-01-01")
    tr = panel[(panel.target_end_date_h3 < cutoff) & (panel.forecast_issue_date.dt.year <= 2023)].copy()
    X, _ = fill_xy(tr, tr.iloc[:1], feats)
    y = tr.y_up.astype(int).to_numpy()
    m = make_logit()
    m.fit(X, y)
    co = m.named_steps["model"].coef_[0]
    return pd.DataFrame({
        "feature": feats,
        "coef_std": co,
        "abs_coef": np.abs(co),
    }).sort_values("abs_coef", ascending=False)


def main():
    ledger = load_ledger()
    hist = load_neon_hourly()
    succ, api_calls = fetch_extension()

    bridge_df, bridge = bridge_metrics(hist, succ)
    bridge_df.to_csv(OUT / "iris_v1_bridge_return_diagnostics.csv", index=False)
    (OUT / "iris_v1_source_bridge.json").write_text(
        json.dumps({
            **bridge,
            "historical_hourly_rows": int(len(hist)),
            "historical_first": str(hist.ts.min()),
            "historical_last": str(hist.ts.max()),
            "successor_rows": int(len(succ)),
            "successor_first": str(succ.ts.min()),
            "successor_last": str(succ.ts.max()),
            "api_calls": int(api_calls),
            "raw_vendor_values_logged_to_repo": False,
        }, indent=2, default=str) + "\n"
    )
    if not bridge["pass"]:
        result = {
            "schema": "IRIS_H3_V1",
            "status": "SOURCE_BRIDGE_FAIL_CLOSED",
            "bridge": bridge,
        }
        (OUT / "iris_v1_summary.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        (OUT / "IRIS_V1_RESULT.md").write_text(
            "# IRIS-H3 V1 — RESULT\n\n**Status:** SOURCE BRIDGE FAIL CLOSED.\n\n"
            + json.dumps(bridge, indent=2, default=str) + "\n"
        )
        print((OUT / "IRIS_V1_RESULT.md").read_text())
        return

    # Stored history is authority through 2024; successor extends 2025 onward.
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    anchors = build_anchor_features(hourly)
    panel = prepare_panel(ledger, anchors)

    cov = (
        panel.groupby("year")
        .agg(n=("forecast_issue_date", "size"),
             first_issue=("forecast_issue_date", "min"),
             last_issue=("forecast_issue_date", "max"))
        .reset_index()
    )
    cov.to_csv(OUT / "iris_v1_matched_coverage.csv", index=False)

    ledgers = [base_ledger(panel)]
    for name, feats in CANDIDATES.items():
        ledgers.append(run_candidate(panel, name, feats))
    pred = pd.concat(ledgers, ignore_index=True)
    pred.to_csv(OUT / "iris_v1_predictions.csv", index=False)

    mdf = score_periods(pred)
    mdf.to_csv(OUT / "iris_v1_metrics.csv", index=False)

    sel_grid, selected = select_2023(mdf)
    sel_grid.to_csv(OUT / "iris_v1_selection_grid_2023.csv", index=False)

    if selected is None:
        status = "NOT_PROMOTED_NO_ELIGIBLE_2023_CANDIDATE"
        confirm_pass = False
        selected_name = None
    else:
        selected_name = str(selected["model"])
        b24 = mdf[(mdf.model == "BASE_A1") & (mdf.period == "2024")].iloc[0]
        s24 = mdf[(mdf.model == selected_name) & (mdf.period == "2024")].iloc[0]
        confirm_pass = bool(
            s24.balanced_accuracy > b24.balanced_accuracy
            and s24.accuracy + 0.005 >= b24.accuracy
            and s24.brier <= b24.brier + 0.0025
        )
        status = "MECHANISM_PASS" if confirm_pass else "NOT_PROMOTED_2024_CONFIRM_FAIL"

    coef = descriptive_coefficients(panel, selected)
    if not coef.empty:
        coef.to_csv(OUT / "iris_v1_selected_logit_coefficients_through_2023.csv", index=False)

    def row(model, period):
        q = mdf[(mdf.model == model) & (mdf.period == period)]
        return None if q.empty else q.iloc[0]

    summary = {
        "schema": "IRIS_H3_V1",
        "status": status,
        "source_bridge": bridge,
        "hourly_combined_rows": int(len(hourly)),
        "anchor_feature_rows": int(len(anchors)),
        "matched_rows_by_year": cov.to_dict(orient="records"),
        "selection_window": "2023",
        "confirmation_window": "2024",
        "selected": selected,
        "confirmation_pass": bool(confirm_pass),
        "selected_model": selected_name,
        "metrics": mdf.to_dict(orient="records"),
    }
    (OUT / "iris_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# IRIS-H3 V1 — INTRADAY REALIZED-STATE RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Selected 2023 representation:** **{selected_name or 'NONE'}**  ",
        f"**2024 mechanism confirmation:** **{confirm_pass}**", "",
        "## Source bridge", "",
        f"- common return rows: **{bridge['common_return_rows']}**",
        f"- 1h return Pearson: **{bridge['pearson']:.6f}**",
        f"- return sign agreement: **{100*bridge['sign_agreement']:.2f}%**",
        f"- return-difference SD: **{bridge['return_diff_sd']:.8f}**",
        f"- bridge pass: **{bridge['pass']}**", "",
        "## Matched H3 origins", "",
        "| Year | N | First issue | Last issue |",
        "|---:|---:|---|---|",
    ]
    for r in cov.itertuples():
        lines.append(
            f"| {int(r.year)} | {int(r.n)} | {pd.Timestamp(r.first_issue).date()} | {pd.Timestamp(r.last_issue).date()} |"
        )

    lines += ["", "## Direction metrics", "",
              "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    models = ["BASE_A1"] + list(CANDIDATES.keys())
    for period in ["2023", "2024", "2025", "2026", "2023-2024", "2025-2026"]:
        for model in models:
            r = row(model, period)
            if r is None:
                continue
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.false_call_rate:.2f}% |"
            )

    lines += ["", "## 2023 selection grid", "",
              "| Candidate | Eligible | Δ accuracy | Δ balanced | Δ Brier |",
              "|---|---|---:|---:|---:|"]
    for r in sel_grid.itertuples():
        lines.append(
            f"| {r.model} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} |"
        )

    lines += ["", "## Governance", "",
              "2023 alone selected the representation. 2024 did not modify the model. "
              "2025/2026 are frozen transport/stress reports. "
              "Raw successor vendor prices were not committed to the repository."]

    (OUT / "IRIS_V1_RESULT.md").write_text("\n".join(lines) + "\n")

    print("IRIS_H3_V1_SUMMARY=" + json.dumps(summary, separators=(",", ":"), default=str))
    print((OUT / "IRIS_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
