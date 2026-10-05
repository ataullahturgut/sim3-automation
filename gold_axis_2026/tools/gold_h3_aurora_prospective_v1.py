from __future__ import annotations

import io
import json
import math
import os
import time
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.special import betainc
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris
from gold_h3_data_integrity_gate_v1 import evaluate_row, decision_dict

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_aurora_prospective_out"))
OUT.mkdir(parents=True, exist_ok=True)

TZ = "America/New_York"
NY = ZoneInfo(TZ)

FROZEN_STAK_REF = "54fdf1c8d39b7b6c7b874d0f30f784296e886044"
LIVE_STAK_REF = os.environ["STAK_LIVE_REF"]
FROZEN_PRICE_END = pd.Timestamp("2026-09-29")
FROZEN_EXPERT_FEATURE_END = pd.Timestamp("2026-09-24")
PROSPECTIVE_MIN_FEATURE = pd.Timestamp("2026-10-02")
LOCK_TS_UTC = pd.Timestamp("2026-10-02T19:10:36Z")

FROZEN_PRICE_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"
FROZEN_MATRIX_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv"
PRICE_LEDGER_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PROSPECTIVE_DAILY_PRICES.csv"
FORECAST_LEDGER_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PROSPECTIVE_LEDGER.csv"
MISS_LEDGER_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PROSPECTIVE_MISSES.csv"
INTEGRITY_LEDGER_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PROSPECTIVE_DATA_INTEGRITY.csv"

NOVA_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_NOVA_V1_PREDICTIONS_2026-10-02.csv"
SENTRY_FILE = ROOT / "gold_axis_2026" / "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv"

CORE3 = [
    "gold_r1", "gold_r3", "gold_r5", "gold_r10", "gold_r21", "sigma20",
    "silver_r1", "silver_r5", "silver_r21", "silver_age_days",
    "platinum_r1", "platinum_r5", "platinum_r21", "platinum_age_days",
]
PATH = list(iris.PATH)

A1_RECENT_N = 252
A1_BATCH_SIZE = 5
A1_GLOBAL_WEIGHT = 0.75
A1_RECENT_WEIGHT = 0.25

SENTRY_WINDOW = 63
SENTRY_MIN = 42
SENTRY_ENTER = 3

DART_HAZARD = 0.05
DART_MAX_RUN = 120
DART_MIN_DISAGREEMENTS = 8
DART_EXIT_PROB = 0.10
DART_EXIT_Q = 0.40

FORECAST_COLS = [
    "feature_cutoff_date", "issued_at_utc", "planned_forecast_issue_date",
    "a1_batch_start_date", "expert_month_refit_date",
    "source_stak_ref", "target_start_price",
    "p_A1_arcr", "p_structural", "p_path_global",
    "active_expert", "p_aurora", "direction",
    "matured_pair_n", "net_rescue_63", "matured_disagreements",
    "q_path", "prob_path_superior",
] + PATH + [
    "settlement_status", "target_end_date_h3", "target_end_price",
    "target_r3", "y_up", "correct", "brier_row", "logloss_row", "settled_at_utc",
]

PRICE_LEDGER_COLS = [
    "date", "gold", "silver", "platinum", "palladium",
    "first_seen_stak_ref", "first_seen_at_utc",
]
MISS_COLS = [
    "feature_cutoff_date", "planned_forecast_issue_date", "deadline_utc",
    "recorded_at_utc", "reason",
]
INTEGRITY_COLS = [
    "date", "checked_at_utc", "source_stak_ref",
    "gold", "silver", "platinum", "palladium",
    "integrity_status", "integrity_admit", "integrity_reason",
    "severe_asset_n", "max_abs_logret", "gold_logret",
    "independent_xau", "xau_level_divergence", "independent_available",
]


def now_utc():
    override = os.environ.get("AURORA_NOW_UTC", "").strip()
    if override:
        return pd.Timestamp(override).tz_convert("UTC")
    return pd.Timestamp.now(tz="UTC")


def get_bytes(url: str, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "aurora-h3-prospective/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_stak_rows(raw: bytes, min_date=None, max_date=None):
    rows = json.loads(raw)
    wanted = {"Gold": "gold", "Silver": "silver", "Platinum": "platinum", "Palladium": "palladium"}
    by = {v: {} for v in wanted.values()}
    for r in rows:
        metal = wanted.get(str(r.get("metal") or ""))
        if not metal:
            continue
        ts = pd.to_datetime(r.get("timestamp"), errors="coerce")
        if pd.isna(ts):
            continue
        d = ts.normalize()
        if d.weekday() >= 5:
            continue
        if min_date is not None and d < pd.Timestamp(min_date):
            continue
        if max_date is not None and d > pd.Timestamp(max_date):
            continue
        try:
            v = float(r.get("spot"))
        except Exception:
            continue
        if np.isfinite(v) and v > 0:
            by[metal][d] = v
    return by


def load_common_prices(ref: str, start_year: int, end_year: int, min_date=None, max_date=None):
    all_by = {k: {} for k in ["gold", "silver", "platinum", "palladium"]}
    for year in range(start_year, end_year + 1):
        url = f"https://raw.githubusercontent.com/lbruton/StakTrakr/{ref}/data/spot-history-{year}.json"
        raw = get_bytes(url)
        yy = parse_stak_rows(raw, min_date=min_date, max_date=max_date)
        for k in all_by:
            all_by[k].update(yy[k])
    common = sorted(set.intersection(*(set(all_by[k]) for k in all_by)))
    if not common:
        return pd.DataFrame(columns=["date", "gold", "silver", "platinum", "palladium"])
    return pd.DataFrame({
        "date": common,
        "gold": [all_by["gold"][d] for d in common],
        "silver": [all_by["silver"][d] for d in common],
        "platinum": [all_by["platinum"][d] for d in common],
        "palladium": [all_by["palladium"][d] for d in common],
    }).sort_values("date").reset_index(drop=True)


def load_or_build_frozen_prices():
    if FROZEN_PRICE_FILE.exists():
        x = pd.read_csv(FROZEN_PRICE_FILE)
        x["date"] = pd.to_datetime(x["date"])
        return x.sort_values("date").reset_index(drop=True), False

    x = load_common_prices(
        FROZEN_STAK_REF, 2010, 2026,
        max_date=FROZEN_PRICE_END,
    )
    if x.empty or x.date.max() != FROZEN_PRICE_END:
        raise RuntimeError(f"FROZEN_PRICE_SNAPSHOT_BAD last={x.date.max() if len(x) else None}")
    x.to_csv(OUT / FROZEN_PRICE_FILE.name, index=False)
    return x, True


def read_price_ledger():
    if PRICE_LEDGER_FILE.exists():
        x = pd.read_csv(PRICE_LEDGER_FILE)
        if len(x):
            x["date"] = pd.to_datetime(x["date"])
        return x
    return pd.DataFrame(columns=PRICE_LEDGER_COLS)


def read_integrity_ledger():
    if not INTEGRITY_LEDGER_FILE.exists():
        return pd.DataFrame(columns=INTEGRITY_COLS)
    x = pd.read_csv(INTEGRITY_LEDGER_FILE)
    if len(x):
        x["date"] = pd.to_datetime(x["date"])
    return x


def independent_xau_map(candidate_dates, ts):
    if not candidate_dates:
        return {}
    start = min(candidate_dates) - pd.Timedelta(days=1)
    end = max(candidate_dates) + pd.Timedelta(days=1)
    try:
        h = fetch_recent_hourly(
            pd.Timestamp(start).strftime("%Y-%m-%d 00:00:00"),
            pd.Timestamp(end).strftime("%Y-%m-%d 23:59:59"),
        )
    except Exception:
        return {}
    if h.empty:
        return {}
    local = h.copy()
    local["local_ts"] = local.ts.dt.tz_convert(NY)
    local["date"] = local.local_ts.dt.tz_localize(None).dt.normalize()
    # Prefer the completed 16:00 NY bar; this is the independent daily anchor
    # already used by the H3 structural layer.
    q = local[local.local_ts.dt.hour == 16].copy()
    if q.empty:
        return {}
    q = q.sort_values("local_ts").drop_duplicates("date", keep="last")
    return dict(zip(q.date, q.value.astype(float)))


def refresh_price_ledger(frozen, ts):
    existing = read_price_ledger()
    integrity = read_integrity_ledger()
    current_year = int(ts.tz_convert(NY).year)
    start_year = int(FROZEN_PRICE_END.year)
    live = load_common_prices(
        LIVE_STAK_REF,
        start_year,
        current_year,
        min_date=FROZEN_PRICE_END + pd.Timedelta(days=1),
        max_date=ts.tz_convert(NY).normalize().tz_localize(None),
    )

    have = set(pd.to_datetime(existing["date"]).dt.normalize()) if len(existing) else set()
    candidate = live[~live.date.isin(have)].copy() if len(live) else live.copy()

    base_extra = existing[["date", "gold", "silver", "platinum", "palladium"]].copy() if len(existing) else pd.DataFrame()
    accepted = pd.concat([frozen, base_extra], ignore_index=True)
    accepted["date"] = pd.to_datetime(accepted["date"])
    accepted = accepted.sort_values("date").drop_duplicates("date", keep="first").reset_index(drop=True)

    ind = independent_xau_map(list(pd.to_datetime(candidate.date)), ts) if len(candidate) else {}
    add = []
    new_audit = []

    for r in candidate.sort_values("date").itertuples():
        d = pd.Timestamp(r.date).normalize()
        prev = accepted[accepted.date < d].tail(1)
        if prev.empty:
            # No usable continuity anchor means fail closed rather than silently
            # accepting an uncheckable new row.
            rec = {
                "date": d, "checked_at_utc": ts.isoformat(), "source_stak_ref": LIVE_STAK_REF,
                "gold": float(r.gold), "silver": float(r.silver),
                "platinum": float(r.platinum), "palladium": float(r.palladium),
                "integrity_status": "QUARANTINE_NO_PREVIOUS_ACCEPTED_ROW",
                "integrity_admit": False,
                "integrity_reason": "no previous accepted retained row available",
                "severe_asset_n": np.nan, "max_abs_logret": np.nan, "gold_logret": np.nan,
                "independent_xau": ind.get(d), "xau_level_divergence": np.nan,
                "independent_available": bool(d in ind),
            }
            new_audit.append(rec)
            continue

        cur = {
            "date": d, "gold": float(r.gold), "silver": float(r.silver),
            "platinum": float(r.platinum), "palladium": float(r.palladium),
        }
        prv = prev.iloc[0].to_dict()
        dec = evaluate_row(cur, prv, independent_xau=ind.get(d))
        rec = {
            **cur, "checked_at_utc": ts.isoformat(), "source_stak_ref": LIVE_STAK_REF,
            **decision_dict(dec),
        }

        # Avoid writing identical repeated quarantine checks for the same source ref.
        append_audit = True
        if len(integrity):
            z = integrity[integrity.date == d].tail(1)
            if len(z):
                last = z.iloc[0]
                if (
                    str(last.get("source_stak_ref", "")) == LIVE_STAK_REF
                    and str(last.get("integrity_status", "")) == str(rec["integrity_status"])
                ):
                    append_audit = False
        if append_audit:
            new_audit.append(rec)

        if dec.admit:
            add.append({
                "date": d,
                "gold": float(r.gold),
                "silver": float(r.silver),
                "platinum": float(r.platinum),
                "palladium": float(r.palladium),
                "first_seen_stak_ref": LIVE_STAK_REF,
                "first_seen_at_utc": ts.isoformat(),
            })
            accepted = pd.concat([accepted, pd.DataFrame([cur])], ignore_index=True)
            accepted = accepted.sort_values("date").drop_duplicates("date", keep="first").reset_index(drop=True)

    if add:
        existing = pd.concat([existing, pd.DataFrame(add)], ignore_index=True)
    if len(existing):
        existing["date"] = pd.to_datetime(existing["date"])
        existing = existing.sort_values("date").drop_duplicates("date", keep="first").reset_index(drop=True)
    existing.to_csv(OUT / PRICE_LEDGER_FILE.name, index=False)

    if new_audit:
        integrity = pd.concat([integrity, pd.DataFrame(new_audit)], ignore_index=True)
    if len(integrity):
        integrity["date"] = pd.to_datetime(integrity["date"])
        integrity = integrity.sort_values(["date", "checked_at_utc"]).reset_index(drop=True)
    integrity.to_csv(OUT / INTEGRITY_LEDGER_FILE.name, index=False, columns=INTEGRITY_COLS)

    extra = existing[["date", "gold", "silver", "platinum", "palladium"]].copy() if len(existing) else pd.DataFrame()
    combined = pd.concat([frozen, extra], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    combined = combined.sort_values("date").drop_duplicates("date", keep="first").reset_index(drop=True)

    quarantine_now = int(sum(not bool(x.get("integrity_admit", False)) for x in new_audit))
    return combined, existing, len(add), integrity, quarantine_now

def build_daily_panel(prices):
    df = prices.copy().sort_values("date").reset_index(drop=True)
    df["feature_cutoff_date"] = df["date"]

    lg = np.log(df.gold.astype(float))
    for h in [1, 3, 5, 10, 21]:
        df[f"gold_r{h}"] = lg.diff(h)
    df["sigma20"] = lg.diff().rolling(20).std(ddof=0)

    for name in ["silver", "platinum"]:
        lp = np.log(df[name].astype(float))
        for h in [1, 5, 21]:
            df[f"{name}_r{h}"] = lp.diff(h)
        # The R2 public panel uses common retained dates for all metals.
        df[f"{name}_age_days"] = 0.0

    df["target_end_date_h3"] = df.date.shift(-3)
    df["target_r3"] = np.log(df.gold.shift(-3) / df.gold)
    df["y_up"] = np.where(df.target_r3.notna(), (df.target_r3 > 0).astype(float), np.nan)
    return df


def logit_model(balanced=False):
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            class_weight="balanced" if balanced else None,
            random_state=20261002,
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


def load_nova():
    x = pd.read_csv(NOVA_FILE)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        x[c] = pd.to_datetime(x[c], errors="raise")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


def fetch_frozen_hourly():
    hist = iris.load_neon_hourly()
    succ, _ = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"FROZEN_HOURLY_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    return hourly.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True), bridge


def reproduction_audit(matrix):
    frozen = pd.read_csv(SENTRY_FILE)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        frozen[c] = pd.to_datetime(frozen[c], errors="raise")

    sep = frozen[(frozen.year == 2026) & (frozen.month == "2026-09")].copy()
    te = matrix[matrix.feature_cutoff_date.isin(sep.feature_cutoff_date)].copy()
    te = te.merge(
        sep[["feature_cutoff_date", "p_structural", "p_path_global"]],
        on="feature_cutoff_date", how="inner", validate="one_to_one"
    )
    if len(te) != len(sep):
        raise RuntimeError(f"REPRO_SEP_MATCH_FAIL matrix={len(te)} frozen={len(sep)}")

    cutoff = sep.feature_cutoff_date.min()
    first_issue = sep.forecast_issue_date.min()
    tr = matrix[
        (matrix.target_end_date_h3 <= cutoff)
        & (matrix.forecast_issue_date < first_issue)
    ].copy()

    Xs, Tes = fill_xy(tr, te, ["base_logit"] + PATH)
    Xp, Tep = fill_xy(tr, te, PATH)
    y = tr.y_up.astype(int).to_numpy()

    ms = logit_model(False)
    mp = logit_model(False)
    ms.fit(Xs, y)
    mp.fit(Xp, y)
    ps = ms.predict_proba(Tes)[:, 1]
    pp = mp.predict_proba(Tep)[:, 1]

    ds = float(np.max(np.abs(ps - te.p_structural.to_numpy(float))))
    dp = float(np.max(np.abs(pp - te.p_path_global.to_numpy(float))))
    passed = bool(ds <= 1e-8 and dp <= 1e-8)
    return {
        "september_rows": int(len(te)),
        "max_abs_diff_structural": ds,
        "max_abs_diff_path": dp,
        "pass": passed,
    }


def load_or_build_frozen_matrix():
    if FROZEN_MATRIX_FILE.exists():
        x = pd.read_csv(FROZEN_MATRIX_FILE)
        for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
            x[c] = pd.to_datetime(x[c], errors="raise")
        audit = reproduction_audit(x)
        if not audit["pass"]:
            raise RuntimeError(f"FROZEN_MATRIX_REPRO_FAIL {audit}")
        return x, False, audit

    nova = load_nova()
    hourly, bridge = fetch_frozen_hourly()
    anchors = iris.build_anchor_features(hourly).copy()
    anchors["feature_date"] = pd.to_datetime(anchors.local_date)

    x = nova[nova.feature_cutoff_date <= FROZEN_EXPERT_FEATURE_END].copy()
    x = x.merge(
        anchors[["feature_date"] + PATH],
        left_on="feature_cutoff_date",
        right_on="feature_date",
        how="inner",
        validate="one_to_one",
    )
    p = np.clip(x.p_A1_arcr.astype(float).to_numpy(), 1e-6, 1 - 1e-6)
    x["base_logit"] = np.log(p / (1.0 - p))
    keep = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
        "target_r3", "y_up", "p_A1_arcr", "base_logit",
    ] + PATH
    x = x[keep].dropna().sort_values("forecast_issue_date").reset_index(drop=True)
    x.to_csv(OUT / FROZEN_MATRIX_FILE.name, index=False)

    audit = reproduction_audit(x)
    audit["source_bridge"] = bridge
    if not audit["pass"]:
        raise RuntimeError(f"BOOTSTRAP_REPRO_FAIL {audit}")
    return x, True, audit


def read_forecast_ledger():
    if not FORECAST_LEDGER_FILE.exists():
        return pd.DataFrame(columns=FORECAST_COLS)
    x = pd.read_csv(FORECAST_LEDGER_FILE)
    for c in ["feature_cutoff_date", "planned_forecast_issue_date", "a1_batch_start_date",
              "expert_month_refit_date", "target_end_date_h3"]:
        if c in x:
            x[c] = pd.to_datetime(x[c], errors="coerce")
    return x


def read_miss_ledger():
    if not MISS_LEDGER_FILE.exists():
        return pd.DataFrame(columns=MISS_COLS)
    x = pd.read_csv(MISS_LEDGER_FILE)
    if len(x):
        x["feature_cutoff_date"] = pd.to_datetime(x["feature_cutoff_date"])
    return x


def settle_forecasts(ledger, daily, ts):
    if ledger.empty:
        return ledger, 0
    dates = list(pd.to_datetime(daily.date))
    px = dict(zip(pd.to_datetime(daily.date), daily.gold.astype(float)))
    changed = 0
    for i, r in ledger.iterrows():
        if str(r.get("settlement_status", "")) == "SETTLED":
            continue
        d = pd.Timestamp(r.feature_cutoff_date)
        future = [q for q in dates if q > d]
        if len(future) < 3:
            continue
        end = future[2]
        start_px = float(r.target_start_price)
        end_px = float(px[end])
        ret = float(math.log(end_px / start_px))
        y = int(ret > 0)
        p = float(r.p_aurora)
        pred = int(p >= 0.5)
        pclip = float(np.clip(p, 1e-6, 1 - 1e-6))

        ledger.loc[i, "settlement_status"] = "SETTLED"
        ledger.loc[i, "target_end_date_h3"] = end
        ledger.loc[i, "target_end_price"] = end_px
        ledger.loc[i, "target_r3"] = ret
        ledger.loc[i, "y_up"] = y
        ledger.loc[i, "correct"] = int(pred == y)
        ledger.loc[i, "brier_row"] = (p - y) ** 2
        ledger.loc[i, "logloss_row"] = -(y * math.log(pclip) + (1-y) * math.log(1-pclip))
        ledger.loc[i, "settled_at_utc"] = ts.isoformat()
        changed += 1
    return ledger, changed


def next_weekday(d):
    return (pd.Timestamp(d) + pd.offsets.BDay(1)).normalize()


def deadline_utc(feature_date):
    issue = next_weekday(feature_date)
    local = pd.Timestamp(f"{issue.date()} 08:00:00").tz_localize(TZ)
    return local.tz_convert("UTC"), issue


def fetch_recent_hourly(start_local, end_local):
    values = iris.api_request(pd.Timestamp(start_local), pd.Timestamp(end_local))
    rows = []
    for row in values:
        dt = row.get("datetime")
        close = row.get("close")
        if dt is None or close is None:
            continue
        try:
            t = pd.Timestamp(dt).tz_localize(TZ, ambiguous="NaT", nonexistent="shift_forward").tz_convert("UTC")
            v = float(close)
        except Exception:
            continue
        if pd.isna(t) or not np.isfinite(v) or v <= 0:
            continue
        rows.append((t, v))
    if not rows:
        return pd.DataFrame(columns=["ts", "value"])
    return pd.DataFrame(rows, columns=["ts", "value"]).sort_values("ts").drop_duplicates("ts", keep="last")


def current_anchor_map(candidate_dates, ts):
    if not candidate_dates:
        return {}
    start = min(candidate_dates) - pd.Timedelta(days=10)
    end = ts.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=1)
    h = fetch_recent_hourly(
        pd.Timestamp(start).strftime("%Y-%m-%d 00:00:00"),
        pd.Timestamp(end).strftime("%Y-%m-%d %H:%M:%S"),
    )
    if h.empty:
        return {}
    a = iris.build_anchor_features(h)
    return {pd.Timestamp(r.local_date): r for r in a.itertuples()}


def determine_a1_batch_start(ledger, current_date):
    issued = ledger[pd.to_datetime(ledger.feature_cutoff_date, errors="coerce") >= PROSPECTIVE_MIN_FEATURE].copy()
    if issued.empty:
        return pd.Timestamp(current_date)
    issued = issued.sort_values("feature_cutoff_date")
    n = len(issued)
    pos = n % A1_BATCH_SIZE
    if pos == 0:
        return pd.Timestamp(current_date)
    block_start_idx = n - pos
    return pd.Timestamp(issued.iloc[block_start_idx].a1_batch_start_date)


def fit_a1_for_origin(daily, feature_date, batch_start):
    tr = daily[
        daily.target_r3.notna()
        & daily.target_end_date_h3.notna()
        & (daily.target_end_date_h3 <= pd.Timestamp(batch_start))
        & daily[CORE3].notna().all(axis=1)
    ].copy()
    te = daily[
        (daily.date == pd.Timestamp(feature_date))
        & daily[CORE3].notna().all(axis=1)
    ].copy()
    if len(te) != 1 or len(tr) < 750:
        raise RuntimeError(f"A1_LIVE_TRAIN_BAD tr={len(tr)} te={len(te)}")

    Xg, Xt = fill_xy(tr, te, CORE3)
    y = (tr.target_r3.astype(float) > 0).astype(int).to_numpy()
    mg = logit_model(False)
    mg.fit(Xg, y)
    pg = float(mg.predict_proba(Xt)[0, 1])

    rr = tr.tail(A1_RECENT_N).copy()
    Xr, Xrt = fill_xy(rr, te, CORE3)
    yr = (rr.target_r3.astype(float) > 0).astype(int).to_numpy()
    mr = logit_model(True)
    mr.fit(Xr, yr)
    pr = float(mr.predict_proba(Xrt)[0, 1])
    return A1_GLOBAL_WEIGHT * pg + A1_RECENT_WEIGHT * pr, len(tr)


def prospective_training_rows(ledger):
    if ledger.empty:
        return pd.DataFrame()
    z = ledger[ledger.settlement_status == "SETTLED"].copy()
    if z.empty:
        return pd.DataFrame()
    z["feature_cutoff_date"] = pd.to_datetime(z.feature_cutoff_date)
    z["forecast_issue_date"] = pd.to_datetime(z.planned_forecast_issue_date)
    z["target_end_date_h3"] = pd.to_datetime(z.target_end_date_h3)
    p = np.clip(z.p_A1_arcr.astype(float).to_numpy(), 1e-6, 1 - 1e-6)
    z["base_logit"] = np.log(p / (1-p))
    keep = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
        "target_r3", "y_up", "p_A1_arcr", "base_logit",
    ] + PATH
    return z[keep].copy()


def fit_experts(frozen_matrix, ledger, feature_date, p_a1, anchor_row, month_refit):
    pros = prospective_training_rows(ledger)
    train_all = pd.concat([frozen_matrix, pros], ignore_index=True)
    issue_min = next_weekday(month_refit)
    tr = train_all[
        (train_all.target_end_date_h3 <= pd.Timestamp(month_refit))
        & (train_all.forecast_issue_date < issue_min)
    ].copy()

    row = {
        "base_logit": float(math.log(np.clip(p_a1, 1e-6, 1-1e-6) / (1-np.clip(p_a1, 1e-6, 1-1e-6)))),
    }
    for f in PATH:
        row[f] = float(getattr(anchor_row, f))
    te = pd.DataFrame([row])

    Xs, Tes = fill_xy(tr, te, ["base_logit"] + PATH)
    Xp, Tep = fill_xy(tr, te, PATH)
    y = tr.y_up.astype(int).to_numpy()
    if len(tr) < 180:
        raise RuntimeError(f"EXPERT_LIVE_TRAIN_TOO_SMALL {len(tr)}")

    ms = logit_model(False)
    mp = logit_model(False)
    ms.fit(Xs, y)
    mp.fit(Xp, y)
    return (
        float(ms.predict_proba(Tes)[0, 1]),
        float(mp.predict_proba(Tep)[0, 1]),
        len(tr),
    )


class DARTDetector:
    def __init__(self):
        self.mass = np.array([1.0], float)
        self.alpha = np.array([1.0], float)
        self.beta = np.array([1.0], float)
        self.runlen = np.array([0], int)
        self.n = 0

    def update(self, x):
        x = int(x)
        prior_pred = 0.5
        pred = np.where(
            x == 1,
            self.alpha / (self.alpha + self.beta),
            self.beta / (self.alpha + self.beta),
        )
        growth = self.mass * (1-DART_HAZARD) * pred
        cp = float(np.sum(self.mass) * DART_HAZARD * prior_pred)
        mass = np.concatenate([[cp], growth])
        alpha = np.concatenate([[1.0 + x], self.alpha + x])
        beta = np.concatenate([[1.0 + (1-x)], self.beta + (1-x)])
        runlen = np.concatenate([[1], self.runlen + 1])
        keep = runlen <= DART_MAX_RUN
        mass, alpha, beta, runlen = mass[keep], alpha[keep], beta[keep], runlen[keep]
        mass = mass / mass.sum()
        self.mass, self.alpha, self.beta, self.runlen = mass, alpha, beta, runlen
        self.n += 1

    def summary(self):
        means = self.alpha / (self.alpha + self.beta)
        q = float(np.sum(self.mass * means))
        prob = float(np.sum(self.mass * (1.0 - betainc(self.alpha, self.beta, 0.5))))
        return self.n, q, prob


def evidence_frame(ledger, cutoff):
    frozen = pd.read_csv(SENTRY_FILE)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        frozen[c] = pd.to_datetime(frozen[c], errors="raise")
    f = frozen[frozen.target_end_date_h3 <= pd.Timestamp(cutoff)][
        ["forecast_issue_date", "target_end_date_h3", "y_up", "p_structural", "p_path_global"]
    ].copy()

    if ledger.empty:
        return f
    p = ledger[ledger.settlement_status == "SETTLED"].copy()
    if not p.empty:
        p["forecast_issue_date"] = pd.to_datetime(p.planned_forecast_issue_date)
        p["target_end_date_h3"] = pd.to_datetime(p.target_end_date_h3)
        p = p[p.target_end_date_h3 <= pd.Timestamp(cutoff)][
            ["forecast_issue_date", "target_end_date_h3", "y_up", "p_structural", "p_path_global"]
        ]
        f = pd.concat([f, p], ignore_index=True)
    return f.sort_values(["target_end_date_h3", "forecast_issue_date"]).reset_index(drop=True)


def current_evidence(ledger, cutoff):
    e = evidence_frame(ledger, cutoff)
    y = e.y_up.astype(int).to_numpy()
    s = (e.p_structural.astype(float).to_numpy() >= 0.5).astype(int)
    p = (e.p_path_global.astype(float).to_numpy() >= 0.5).astype(int)
    s_ok = s == y
    p_ok = p == y
    adv = ((~s_ok) & p_ok).astype(int) - (s_ok & (~p_ok)).astype(int)
    last = adv[-SENTRY_WINDOW:]
    pair_n = int(min(len(adv), SENTRY_WINDOW))
    net = int(last.sum()) if len(last) else 0

    det = DARTDetector()
    disagree = s != p
    for yy, ss, pp in zip(y[disagree], s[disagree], p[disagree]):
        det.update(int(pp == yy))
    dn, q, prob = det.summary()
    return pair_n, net, dn, q, prob


def previous_state(ledger):
    if ledger.empty:
        return "PATH_GLOBAL"
    return str(ledger.sort_values("feature_cutoff_date").iloc[-1].active_expert)


def route_state(prev, pair_n, net, dn, q, prob):
    state = prev
    if state == "STRUCTURAL_IRIS":
        if pair_n >= SENTRY_MIN and net >= SENTRY_ENTER:
            state = "PATH_GLOBAL"
    else:
        if dn >= DART_MIN_DISAGREEMENTS and prob <= DART_EXIT_PROB and q <= DART_EXIT_Q:
            state = "STRUCTURAL_IRIS"
    return state


def month_refit_date(ledger, current_date):
    d = pd.Timestamp(current_date)
    if not ledger.empty:
        x = ledger.copy()
        x["feature_cutoff_date"] = pd.to_datetime(x.feature_cutoff_date)
        same = x[
            (x.feature_cutoff_date.dt.year == d.year)
            & (x.feature_cutoff_date.dt.month == d.month)
        ]
        if len(same):
            return pd.Timestamp(same.feature_cutoff_date.min())
    return d


def prospective_metrics(ledger):
    z = ledger[ledger.settlement_status == "SETTLED"].copy() if not ledger.empty else pd.DataFrame()
    if z.empty:
        return {"n": 0}
    y = z.y_up.astype(int).to_numpy()
    p = z.p_aurora.astype(float).to_numpy()
    pred = (p >= 0.5).astype(int)
    out = {
        "n": int(len(z)),
        "accuracy": float(np.mean(pred == y)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, np.clip(p, 1e-6, 1-1e-6), labels=[0,1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
    }
    out["balanced_accuracy"] = (
        float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    )
    return out


def write_status(ts, ledger, misses, price_ledger, integrity_ledger, audit, changes):
    m = prospective_metrics(ledger)
    pending = int((ledger.settlement_status != "SETTLED").sum()) if len(ledger) else 0
    latest = None
    if len(ledger):
        r = ledger.sort_values("feature_cutoff_date").iloc[-1]
        latest = {
            "feature_cutoff_date": str(pd.Timestamp(r.feature_cutoff_date).date()),
            "direction": str(r.direction),
            "p_aurora": float(r.p_aurora),
            "active_expert": str(r.active_expert),
            "settlement_status": str(r.settlement_status),
        }
    summary = {
        "identity": "AURORA_H3_V1_PROSPECTIVE",
        "freeze_timestamp_utc": str(LOCK_TS_UTC),
        "status": "ACTIVE",
        "live_stak_ref": LIVE_STAK_REF,
        "frozen_reproduction_audit": audit,
        "forecast_rows": int(len(ledger)),
        "settled_rows": int(m.get("n", 0)),
        "pending_rows": pending,
        "missed_origins": int(len(misses)),
        "postfreeze_daily_price_rows": int(len(price_ledger)),
        "integrity_gate_version": "GOLD_H3_DATA_INTEGRITY_GATE_V1",
        "integrity_audit_rows": int(len(integrity_ledger)),
        "integrity_quarantine_rows": int((integrity_ledger.integrity_admit.astype(str).str.lower() == "false").sum()) if len(integrity_ledger) else 0,
        "metrics": m,
        "latest_forecast": latest,
        "this_run_changes": changes,
    }
    (OUT / "aurora_prospective_status.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")

    lines = [
        "# AURORA-H3 V1 — PROSPECTIVE VALIDATION STATUS", "",
        f"**Identity:** `AURORA_H3_V1_PROSPECTIVE`  ",
        f"**Freeze:** {LOCK_TS_UTC}  ",
        f"**Forecast rows:** **{len(ledger)}**  ",
        f"**Settled:** **{m.get('n',0)}**  ",
        f"**Pending:** **{pending}**  ",
        f"**Missed origins:** **{len(misses)}**  ",
        f"**Frozen September reproduction:** **{'PASS' if audit.get('pass') else 'FAIL'}**",
        f"**Data integrity gate:** **GOLD_H3_DATA_INTEGRITY_GATE_V1**",
        f"**Integrity quarantines:** **{int((integrity_ledger.integrity_admit.astype(str).str.lower() == 'false').sum()) if len(integrity_ledger) else 0}**", "",
    ]
    if m.get("n", 0):
        bal_text = "NA" if m["balanced_accuracy"] is None else f"{100*m['balanced_accuracy']:.2f}%"
        lines += [
            "## Prospective-only settled metrics", "",
            f"- accuracy: **{100*m['accuracy']:.2f}%**",
            f"- balanced accuracy: **{bal_text}**",
            f"- Brier: **{m['brier']:.4f}**",
            f"- log loss: **{m['logloss']:.4f}**",
            f"- UP recall: **{100*m['up_recall']:.2f}%**",
            f"- DOWN recall: **{100*m['down_recall']:.2f}%**", "",
        ]
    else:
        lines += ["No prospective H3 target has matured yet.", ""]
    if latest:
        lines += [
            "## Latest issued forecast", "",
            f"- feature cutoff: **{latest['feature_cutoff_date']}**",
            f"- direction: **{latest['direction']}**",
            f"- p(UP): **{latest['p_aurora']:.4f}**",
            f"- active expert: **{latest['active_expert']}**",
            f"- settlement: **{latest['settlement_status']}**", "",
        ]
    lines += [
        "## Governance", "",
        "This file reports only forecasts created after the prospective freeze. "
        "No missed origin is backfilled after its issuance deadline, and forecast fields are immutable after issuance.",
    ]
    (OUT / "AURORA_PROSPECTIVE_STATUS.md").write_text("\n".join(lines) + "\n")
    return summary


def main():
    ts = now_utc()

    frozen_prices, built_prices = load_or_build_frozen_prices()
    daily_prices, price_ledger, price_added, integrity_ledger, quarantined_now = refresh_price_ledger(frozen_prices, ts)
    daily = build_daily_panel(daily_prices)

    frozen_matrix, built_matrix, audit = load_or_build_frozen_matrix()
    if not audit["pass"]:
        raise RuntimeError("FROZEN_REPRODUCTION_FAILED")

    ledger = read_forecast_ledger()
    misses = read_miss_ledger()

    ledger, settled_now = settle_forecasts(ledger, daily, ts)

    issued_dates = set(pd.to_datetime(ledger.feature_cutoff_date, errors="coerce").dropna().dt.normalize()) if len(ledger) else set()
    missed_dates = set(pd.to_datetime(misses.feature_cutoff_date, errors="coerce").dropna().dt.normalize()) if len(misses) else set()

    possible = [
        pd.Timestamp(d).normalize()
        for d in daily.date
        if pd.Timestamp(d).normalize() >= PROSPECTIVE_MIN_FEATURE
        and pd.Timestamp(d).normalize() not in issued_dates
        and pd.Timestamp(d).normalize() not in missed_dates
    ]

    # Mark expired origins as misses before any attempt to backfill.
    still_possible = []
    for d in possible:
        deadline, issue = deadline_utc(d)
        if ts > deadline:
            misses = pd.concat([misses, pd.DataFrame([{
                "feature_cutoff_date": d,
                "planned_forecast_issue_date": issue,
                "deadline_utc": deadline.isoformat(),
                "recorded_at_utc": ts.isoformat(),
                "reason": "NOT_ISSUED_BEFORE_08NY_DEADLINE_NO_BACKFILL",
            }])], ignore_index=True)
        else:
            still_possible.append(d)

    # Only dates whose 16:00 NY bar should already be complete are candidates.
    now_ny = ts.tz_convert(NY)
    ready_dates = []
    for d in still_possible:
        ready_local = pd.Timestamp(f"{d.date()} 17:05:00").tz_localize(TZ)
        if now_ny >= ready_local:
            ready_dates.append(d)

    anchors = current_anchor_map(ready_dates, ts) if ready_dates else {}
    issued_now = 0

    for d in sorted(ready_dates):
        if d not in anchors:
            continue

        deadline, issue = deadline_utc(d)
        if ts > deadline:
            continue

        anchor = anchors[d]
        batch_start = determine_a1_batch_start(ledger, d)
        p_a1, _ = fit_a1_for_origin(daily, d, batch_start)
        mrefit = month_refit_date(ledger, d)
        ps, pp, _ = fit_experts(frozen_matrix, ledger, d, p_a1, anchor, mrefit)

        pair_n, net, dn, q, prob = current_evidence(ledger, d)
        prev = previous_state(ledger)
        state = route_state(prev, pair_n, net, dn, q, prob)
        p = pp if state == "PATH_GLOBAL" else ps

        start_px = float(daily.loc[daily.date == d, "gold"].iloc[0])
        row = {
            "feature_cutoff_date": d,
            "issued_at_utc": ts.isoformat(),
            "planned_forecast_issue_date": issue,
            "a1_batch_start_date": batch_start,
            "expert_month_refit_date": mrefit,
            "source_stak_ref": LIVE_STAK_REF,
            "target_start_price": start_px,
            "p_A1_arcr": p_a1,
            "p_structural": ps,
            "p_path_global": pp,
            "active_expert": state,
            "p_aurora": p,
            "direction": "UP" if p >= 0.5 else "DOWN",
            "matured_pair_n": pair_n,
            "net_rescue_63": net,
            "matured_disagreements": dn,
            "q_path": q,
            "prob_path_superior": prob,
            "settlement_status": "PENDING",
            "target_end_date_h3": np.nan,
            "target_end_price": np.nan,
            "target_r3": np.nan,
            "y_up": np.nan,
            "correct": np.nan,
            "brier_row": np.nan,
            "logloss_row": np.nan,
            "settled_at_utc": "",
        }
        for f in PATH:
            row[f] = float(getattr(anchor, f))

        ledger = pd.concat([ledger, pd.DataFrame([row])], ignore_index=True)
        issued_now += 1

    if len(ledger):
        ledger["feature_cutoff_date"] = pd.to_datetime(ledger.feature_cutoff_date)
        ledger = ledger.sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date", keep="first").reset_index(drop=True)
    if len(misses):
        misses["feature_cutoff_date"] = pd.to_datetime(misses.feature_cutoff_date)
        misses = misses.sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date", keep="first").reset_index(drop=True)

    ledger.to_csv(OUT / FORECAST_LEDGER_FILE.name, index=False, columns=FORECAST_COLS)
    misses.to_csv(OUT / MISS_LEDGER_FILE.name, index=False, columns=MISS_COLS)

    changes = {
        "built_frozen_price_snapshot": built_prices,
        "built_frozen_expert_matrix": built_matrix,
        "new_price_rows": int(price_added),
        "integrity_quarantined_now": int(quarantined_now),
        "new_forecasts": int(issued_now),
        "new_settlements": int(settled_now),
    }
    summary = write_status(ts, ledger, misses, price_ledger, integrity_ledger, audit, changes)
    print("AURORA_PROSPECTIVE=" + json.dumps(summary, separators=(",", ":"), default=str))
    print((OUT / "AURORA_PROSPECTIVE_STATUS.md").read_text())


if __name__ == "__main__":
    main()

# trigger: 2026-10-05 prospective issuance check
