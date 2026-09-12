from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import psycopg
import requests
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef, mean_pinball_loss

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as v159
from gold_axis_2026.v159_thesis import run_v159r1_entry as v159r1

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v161_thesis/contracts/v161_short_horizon_price_discovery_freeze_v1.json"
V157_CONTRACT_PATH = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v161_thesis"


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_V161_RETROSPECTIVE_SCORING":
        raise RuntimeError("V161_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V161_GOVERNANCE_LOCK_FAIL")
    if g["production_authority"] is not False or g["production_writes"] != "NONE":
        raise RuntimeError("V161_PRODUCTION_AUTHORITY_FORBIDDEN")
    return c


def fetch_yahoo_daily(symbol: str, start: str, end: str) -> tuple[pd.DataFrame, dict]:
    p1 = int(pd.Timestamp(start, tz="UTC").timestamp())
    p2 = int((pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=2)).timestamp())
    last = None
    response = None
    for host in ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]:
        url = f"https://{host}/v8/finance/chart/{quote(symbol, safe='')}"
        try:
            r = requests.get(
                url,
                params={"period1": p1, "period2": p2, "interval": "1d", "events": "history", "includeAdjustedClose": "true"},
                headers={"User-Agent": "Mozilla/5.0 Gold-Control-V161-Research"},
                timeout=(15, 60),
            )
            response = r
            if r.status_code == 200:
                break
            last = f"HTTP_{r.status_code}"
        except requests.RequestException as exc:
            last = repr(exc)
            response = None
    if response is None or response.status_code != 200:
        raise RuntimeError(f"V161_YAHOO_FETCH_FAIL:{symbol}:{last}")
    payload = response.content
    raw = response.json()
    result = ((raw.get("chart") or {}).get("result") or [None])[0]
    if result is None:
        raise RuntimeError(f"V161_YAHOO_SCHEMA_FAIL:{symbol}")
    ts = result.get("timestamp") or []
    quote_block = (((result.get("indicators") or {}).get("quote") or [{}])[0])
    if not ts or not quote_block:
        raise RuntimeError(f"V161_YAHOO_EMPTY:{symbol}")
    n = len(ts)
    def arr(name: str):
        x = quote_block.get(name) or [None] * n
        return (x + [None] * n)[:n]
    d = pd.DataFrame({
        "source_date": pd.to_datetime(ts, unit="s", utc=True).tz_convert(None).normalize(),
        "open": arr("open"),
        "high": arr("high"),
        "low": arr("low"),
        "close": arr("close"),
        "volume": arr("volume"),
    })
    for col in ["open", "high", "low", "close", "volume"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d.dropna(subset=["source_date", "close"]).sort_values("source_date").drop_duplicates("source_date", keep="last")
    d = d[(d["source_date"] >= pd.Timestamp(start)) & (d["source_date"] <= pd.Timestamp(end))].reset_index(drop=True)
    if len(d) < 500:
        raise RuntimeError(f"V161_YAHOO_COVERAGE_FAIL:{symbol}:{len(d)}")
    evidence = {
        "symbol": symbol,
        "provider": "Yahoo Finance chart endpoint",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "rows": int(len(d)),
        "first_source_date": d["source_date"].min().date().isoformat(),
        "last_source_date": d["source_date"].max().date().isoformat(),
        "evidence_class": "HISTORICAL_RECONSTRUCTION_NOT_PROSPECTIVE_PIT",
        "same_date_join_forbidden": True,
    }
    return d, evidence


def make_market_features(d: pd.DataFrame, prefix: str) -> pd.DataFrame:
    z = d.copy().sort_values("source_date").reset_index(drop=True)
    c = z["close"].astype(float)
    lp = np.log(c)
    r = lp.diff()
    z[f"{prefix}_ret1"] = r
    z[f"{prefix}_ret3"] = lp - lp.shift(3)
    z[f"{prefix}_ret5"] = lp - lp.shift(5)
    z[f"{prefix}_range1"] = np.log(z["high"].astype(float) / z["low"].astype(float)).replace([np.inf, -np.inf], np.nan)
    z[f"{prefix}_oc1"] = np.log(z["close"].astype(float) / z["open"].astype(float)).replace([np.inf, -np.inf], np.nan)
    z[f"{prefix}_vol5"] = r.rolling(5, min_periods=5).std(ddof=0)
    z[f"{prefix}_vol20"] = r.rolling(20, min_periods=20).std(ddof=0)
    v = np.log1p(z["volume"].astype(float).clip(lower=0))
    z[f"{prefix}_volume_z20"] = (v - v.rolling(20, min_periods=20).mean()) / v.rolling(20, min_periods=20).std(ddof=0).replace(0, np.nan)
    keep = ["source_date", "close", f"{prefix}_ret1", f"{prefix}_ret3", f"{prefix}_ret5", f"{prefix}_range1", f"{prefix}_oc1", f"{prefix}_vol5", f"{prefix}_vol20", f"{prefix}_volume_z20"]
    return z[keep]


def strict_previous_merge(panel: pd.DataFrame, market: pd.DataFrame, prefix: str) -> pd.DataFrame:
    left = panel.copy().sort_values("date")
    right = market.copy().sort_values("source_date").rename(columns={"close": f"{prefix}_prev_close"})
    out = pd.merge_asof(left, right, left_on="date", right_on="source_date", direction="backward", allow_exact_matches=False)
    out = out.rename(columns={"source_date": f"{prefix}_source_date"})
    bad = out[f"{prefix}_source_date"].notna() & (out[f"{prefix}_source_date"] >= out["date"])
    if bad.any():
        raise RuntimeError(f"V161_SAME_OR_FUTURE_DAILY_JOIN:{prefix}")
    return out.sort_values("date").reset_index(drop=True)


def add_price_discovery(panel: pd.DataFrame, gc: pd.DataFrame, gld: pd.DataFrame) -> pd.DataFrame:
    d = strict_previous_merge(panel, make_market_features(gc, "gc"), "gc")
    d = strict_previous_merge(d, make_market_features(gld, "gld"), "gld")
    d["gc_basis_prev"] = np.log(d["gc_prev_close"].astype(float) / d["close"].astype(float))
    return d


def add_corrected_macro(panel: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, dict]:
    start = "2022-01-01"
    end = contract["windows"]["test_end"]
    frames = {}
    evidence = {}
    for sid in ["DTWEXBGS", "DFII10"]:
        d, e = v159r1.fedboard_fetch(sid, start, end)
        frames[sid] = d
        evidence[sid] = e
    v159_contract = v159r1.merged_contract()
    return v159.add_corrected_drivers(panel, frames, v159_contract), evidence


def feature_sets(contract: dict) -> dict[str, list[str]]:
    fs = contract["feature_sets"]
    base = list(fs["BASE"])
    rm = list(fs["REALIZED_MOMENTS"])
    pdx = list(fs["PRICE_DISCOVERY"])
    return {
        "BASE": base,
        "BASE_PLUS_RM": base + rm,
        "BASE_PLUS_RM_PLUS_PD": base + rm + pdx,
    }


def add_target(panel: pd.DataFrame, h: int) -> pd.DataFrame:
    z = panel.copy().sort_values("date").reset_index(drop=True)
    z["target_close"] = z["close"].shift(-h)
    z["target_date"] = z["date"].shift(-h)
    z["target_return"] = np.log(z["target_close"] / z["close"])
    z["future_direction"] = np.where(z["target_return"].notna(), np.where(z["target_return"] > 0, 1, -1), np.nan)
    z["origin_index"] = np.arange(len(z), dtype=int)
    return z


def model(contract: dict, q: float):
    c = contract["model"]
    return HistGradientBoostingRegressor(
        loss="quantile",
        quantile=float(q),
        max_depth=int(c["max_depth"]),
        max_iter=int(c["max_iter"]),
        learning_rate=float(c["learning_rate"]),
        l2_regularization=float(c["l2_regularization"]),
        random_state=int(c["random_state"]),
    )


def sequential(panel: pd.DataFrame, h: int, candidate: str, features: list[str], require_rm: bool, require_pd: bool, contract: dict) -> pd.DataFrame:
    z = add_target(panel, h)
    start = pd.Timestamp(contract["windows"]["formation_start"])
    qs = [float(x) for x in contract["model"]["quantiles"]]
    cap = int(contract["model"]["rolling_window"])
    min_n = int(contract["model"]["minimum_mature_targets"])
    missing = [x for x in features if x not in z.columns]
    if missing:
        raise RuntimeError(f"V161_FEATURES_MISSING:{candidate}:{missing}")
    rows = []
    for t in range(len(z) - h):
        if pd.Timestamp(z.loc[t, "date"]) < start:
            continue
        if require_rm and not bool(z.loc[t, "rm_valid"]):
            continue
        if require_pd and (pd.isna(z.loc[t, "gc_source_date"]) or pd.isna(z.loc[t, "gld_source_date"])):
            continue
        mature = [j for j in range(t) if j + h <= t and pd.notna(z.loc[j, "target_return"])]
        if require_rm:
            mature = [j for j in mature if bool(z.loc[j, "rm_valid"])]
        if require_pd:
            mature = [j for j in mature if pd.notna(z.loc[j, "gc_source_date"]) and pd.notna(z.loc[j, "gld_source_date"])]
        train = mature[-cap:]
        if len(train) < min_n:
            continue
        y = z.loc[train, "target_return"].astype(float)
        preds = []
        for q in qs:
            m = model(contract, q)
            m.fit(z.loc[train, features], y)
            preds.append(float(m.predict(z.loc[[t], features])[0]))
        q25, q50, q75 = sorted(preds)
        signal = 1 if q25 > 0 else (-1 if q75 < 0 else 0)
        rows.append({
            "candidate": candidate,
            "horizon": int(h),
            "origin_index": int(t),
            "origin_date": z.loc[t, "date"],
            "target_date": z.loc[t, "target_date"],
            "target_return": float(z.loc[t, "target_return"]),
            "future_direction": int(z.loc[t, "future_direction"]),
            "q25": q25, "q50": q50, "q75": q75,
            "signal": int(signal),
            "train_n": int(len(train)),
            "gc_source_date": z.loc[t, "gc_source_date"],
            "gld_source_date": z.loc[t, "gld_source_date"],
        })
    return pd.DataFrame(rows)


def period_slice(d: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    if d.empty:
        return d.copy()
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    x = d[(d["origin_date"] >= a) & (d["origin_date"] <= b) & (d["target_date"] <= b)].copy()
    return x


def metrics(d: pd.DataFrame) -> dict:
    if d.empty:
        return {"n": 0, "selective_n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    sig = d["signal"].astype(int)
    take = sig.ne(0)
    g = d[take].copy()
    out = {"n": int(len(d)), "selective_n": int(len(g)), "coverage": float(take.mean())}
    out["mean_pinball"] = float(np.mean([
        mean_pinball_loss(d["target_return"], d["q25"], alpha=0.25),
        mean_pinball_loss(d["target_return"], d["q50"], alpha=0.50),
        mean_pinball_loss(d["target_return"], d["q75"], alpha=0.75),
    ]))
    if g.empty:
        out.update({"status": "NO_SIGNAL", "selective_accuracy": None, "selective_balanced_accuracy": None, "mcc": None, "up_signals": 0, "down_signals": 0})
        return out
    y = (g["future_direction"].astype(int) > 0).astype(int)
    p = (g["signal"].astype(int) > 0).astype(int)
    out.update({
        "status": "OK",
        "selective_accuracy": float(accuracy_score(y, p)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, p)),
        "mcc": float(matthews_corrcoef(y, p)),
        "up_signals": int((g["signal"] > 0).sum()),
        "down_signals": int((g["signal"] < 0).sum()),
        "realized_up": int((g["future_direction"] > 0).sum()),
        "realized_down": int((g["future_direction"] < 0).sum()),
        "median_signed_return": float(np.median(g["target_return"].to_numpy(float) * g["signal"].to_numpy(int))),
    })
    return out


def score_periods(d: pd.DataFrame, contract: dict) -> dict:
    w = contract["windows"]
    return {
        "FORMATION_2024": metrics(period_slice(d, w["formation_start"], w["formation_end"])),
        "VALIDATION_2025": metrics(period_slice(d, w["validation_start"], w["validation_end"])),
        "TEST_2026_AVAILABLE": metrics(period_slice(d, w["test_start"], w["test_end"])),
    }


def gate(results: dict, contract: dict) -> dict:
    c = contract["evaluation"]["primary_support_gate_H5_PD_RM_QB"]
    challenger = results["H5_PD_RM_QB"]
    base = results["H5_BASE_QB"]
    v = challenger["VALIDATION_2025"]
    t = challenger["TEST_2026_AVAILABLE"]
    checks = {
        "validation_coverage": v.get("coverage", 0) >= float(c["validation_2025_coverage_min"]),
        "validation_balanced": (v.get("selective_balanced_accuracy") or 0) >= float(c["validation_2025_balanced_min"]),
        "validation_mcc": (v.get("mcc") or 0) > 0,
        "validation_both_directions": v.get("up_signals", 0) > 0 and v.get("down_signals", 0) > 0,
        "test_coverage": t.get("coverage", 0) >= float(c["test_2026_coverage_min"]),
        "test_balanced": (t.get("selective_balanced_accuracy") or 0) >= float(c["test_2026_balanced_min"]),
        "test_mcc": (t.get("mcc") or 0) > 0,
        "test_both_directions": t.get("up_signals", 0) > 0 and t.get("down_signals", 0) > 0,
        "validation_pinball_beats_base": v.get("mean_pinball", math.inf) < base["VALIDATION_2025"].get("mean_pinball", -math.inf),
        "test_pinball_beats_base": t.get("mean_pinball", math.inf) < base["TEST_2026_AVAILABLE"].get("mean_pinball", -math.inf),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def main() -> int:
    contract = load_contract()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    v157_contract = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, _, _, _ = v157.build_panel(conn, v157_contract)

    panel, fed_evidence = add_corrected_macro(panel, contract)
    gc, gc_evidence = fetch_yahoo_daily("GC=F", "2022-01-01", contract["windows"]["test_end"])
    gld, gld_evidence = fetch_yahoo_daily("GLD", "2022-01-01", contract["windows"]["test_end"])
    panel = add_price_discovery(panel, gc, gld)

    fs = feature_sets(contract)
    candidate_specs = [
        ("H5_BASE_QB", 5, fs["BASE"], False, False),
        ("H5_RM_QB", 5, fs["BASE_PLUS_RM"], True, False),
        ("H5_PD_RM_QB", 5, fs["BASE_PLUS_RM_PLUS_PD"], True, True),
        ("H3_PD_RM_QB", 3, fs["BASE_PLUS_RM_PLUS_PD"], True, True),
    ]
    predictions = []
    scored = {}
    for cid, h, features, require_rm, require_pd in candidate_specs:
        pred = sequential(panel, h, cid, features, require_rm, require_pd, contract)
        if pred.empty:
            raise RuntimeError(f"V161_EMPTY_PREDICTIONS:{cid}")
        scored[cid] = score_periods(pred, contract)
        predictions.append(pred)

    support = gate(scored, contract)
    result = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "price_discovery_source_evidence": {"GC=F": gc_evidence, "GLD": gld_evidence},
        "fed_driver_evidence": fed_evidence,
        "candidate_results": scored,
        "primary_support_gate": support,
        "interpretation_lock": {
            "H5_primary": True,
            "H3_secondary_only": True,
            "same_day_GC_GLD_daily_bars_forbidden": True,
            "Yahoo_GC_is_research_proxy_not_official_CME_settlement": True,
            "2025_2026_researcher_visible": True,
            "future_prospective_shadow_required_even_if_gate_passes": True,
            "post_score_repairs_forbidden_inside_V161": True
        }
    }

    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v161_panel.csv", index=False)
    pd.concat(predictions, ignore_index=True).to_csv(OUT / "v161_predictions.csv", index=False)
    gc.to_csv(OUT / "v161_gc_daily_reconstruction.csv", index=False)
    gld.to_csv(OUT / "v161_gld_daily_reconstruction.csv", index=False)
    (OUT / "v161_results.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
