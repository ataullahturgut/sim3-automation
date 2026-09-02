from __future__ import annotations

import base64
import gzip
import io
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V2.md"
V1_EVIDENCE = OUT / "prospective_input_bridge_v1_evidence.json"
PIN = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
TWELVE_URL = "https://api.twelvedata.com/time_series"
TARGET_START = pd.Timestamp("2023-01-01")
TARGET_END = pd.Timestamp("2026-07-01")
METAL_START = pd.Timestamp("2025-01-01")
METAL_END = pd.Timestamp("2026-08-19")

METALS = {
    "Gold": {"symbol": "XAU/USD", "median_gap_bps_max": 75.0},
    "Silver": {"symbol": "XAG/USD", "median_gap_bps_max": 75.0},
    "Platinum": {"symbol": "XPT/USD", "median_gap_bps_max": 100.0},
    "Palladium": {"symbol": "XPD/USD", "median_gap_bps_max": 100.0},
}


def secret(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"{name}_NOT_SET")
    return v


def get_json(url: str, *, params: dict, headers: dict | None = None, attempts: int = 6, sleep_base: float = 3.0):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=(15, 90))
            if r.status_code == 429:
                last = RuntimeError("HTTP_429")
                time.sleep(min(60.0, sleep_base * (i + 1)))
                continue
            r.raise_for_status()
            p = r.json()
            if isinstance(p, dict) and p.get("status") == "error":
                raise RuntimeError(f"PROVIDER_ERROR:{p.get('code')}:{p.get('message')}")
            return p
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(min(30.0, sleep_base * (2 ** i)))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{type(last).__name__}:{last}")


def load_core() -> pd.DataFrame:
    raw = gzip.decompress(base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip())).decode()
    return pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()


def load_v1_unchanged_macro_evidence() -> dict:
    if not V1_EVIDENCE.exists():
        raise RuntimeError("V1_EVIDENCE_NOT_FOUND")
    e = json.loads(V1_EVIDENCE.read_text(encoding="utf-8"))
    if e.get("decision") != "BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN":
        raise RuntimeError("V1_PARENT_DECISION_UNEXPECTED")
    fed = e["macro_audit"]["series"]["fedfunds"]
    fx = e["macro_audit"]["series"]["usdcny"]
    if not fed.get("pass") or fed.get("reconstructions") != 43:
        raise RuntimeError("V1_FEDFUNDS_PROOF_NOT_PASS")
    if not fx.get("pass") or fx.get("reconstructions") != 43:
        raise RuntimeError("V1_USDCNY_PROOF_NOT_PASS")
    return {
        "fedfunds": {**fed, "evidence_inherited_from_v1": True, "construction_changed_in_v2": False},
        "usdcny": {**fx, "evidence_inherited_from_v1": True, "construction_changed_in_v2": False},
    }


def fred_month_mean_asof(series_id: str, obs_month: pd.Timestamp, realtime_asof: pd.Timestamp, api_key: str) -> tuple[float, int, str | None]:
    start = obs_month.date().isoformat()
    obs_end_ts = obs_month + pd.offsets.MonthEnd(0)
    obs_end = obs_end_ts.date().isoformat()
    rt = realtime_asof.date().isoformat()
    p = get_json(
        FRED_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": rt,
            "realtime_end": rt,
            "observation_start": start,
            "observation_end": obs_end,
            "sort_order": "asc",
            "limit": 200,
        },
        headers={"User-Agent": "Gold-Control-Patch-Input-Bridge-V2/1.0"},
        sleep_base=1.0,
    )
    vals = []
    max_date = None
    for z in p.get("observations", []):
        sv = str(z.get("value", "."))
        if sv in {".", "", "nan", "None"}:
            continue
        try:
            v = float(sv)
        except Exception:
            continue
        d = pd.Timestamp(str(z.get("date")))
        if d > obs_end_ts or d > realtime_asof:
            raise RuntimeError(f"FUTURE_OBSERVATION:{series_id}:{d.date()}:{rt}")
        vals.append(v)
        max_date = d if max_date is None or d > max_date else max_date
    if not vals:
        raise RuntimeError(f"ALFRED_MONTH_EMPTY:{series_id}:{obs_month.strftime('%Y-%m')}:{rt}")
    return float(np.mean(vals)), len(vals), None if max_date is None else max_date.date().isoformat()


def nasdaq_lag1_audit(core: pd.DataFrame, api_key: str) -> dict:
    rows = []
    missing = []
    pooled_level_gaps = []
    for t in pd.date_range(TARGET_START, TARGET_END, freq="MS"):
        p = t - pd.offsets.MonthBegin(1)
        m1 = p - pd.offsets.MonthBegin(1)
        m2 = m1 - pd.offsets.MonthBegin(1)
        rt = p + pd.offsets.MonthEnd(0)
        try:
            v1, n1, d1 = fred_month_mean_asof("NASDAQCOM", m1, rt, api_key)
            v2, n2, d2 = fred_month_mean_asof("NASDAQCOM", m2, rt, api_key)
            c1 = float(core.loc[m1, "nasdaq"])
            c2 = float(core.loc[m2, "nasdaq"])
            g1 = abs(v1 - c1) / max(abs(c1), 1e-12) * 100.0
            g2 = abs(v2 - c2) / max(abs(c2), 1e-12) * 100.0
            pooled_level_gaps.extend([g1, g2])
            rows.append({
                "target": t.strftime("%Y-%m"),
                "origin_month": p.strftime("%Y-%m"),
                "older_completed_months_used": [m2.strftime("%Y-%m"), m1.strftime("%Y-%m")],
                "obs_counts": [n2, n1],
                "max_source_dates": [d2, d1],
            })
        except Exception as exc:
            missing.append({
                "target": t.strftime("%Y-%m"),
                "origin_month": p.strftime("%Y-%m"),
                "reason": str(exc).split(":", 1)[0],
            })
        time.sleep(0.25)
    gaps = np.asarray(pooled_level_gaps, float)
    med = None if len(gaps) == 0 else float(np.median(gaps))
    p95 = None if len(gaps) == 0 else float(np.quantile(gaps, 0.95))
    hard = len(rows) == 43 and not missing
    material = bool(med is not None and p95 is not None and med <= 0.30 and p95 <= 1.00)
    return {
        "construction": "NASDAQCOM_LAG1_RETURN_ORIGIN_SAFE_V2",
        "reconstructions": len(rows),
        "missing_reconstructions": len(missing),
        "missing_examples": missing[:10],
        "pooled_level_comparisons": int(len(gaps)),
        "median_abs_relative_level_gap_pct": med,
        "p95_abs_relative_level_gap_pct": p95,
        "median_gate_pct": 0.30,
        "p95_gate_pct": 1.00,
        "hard_gate_pass": hard,
        "materiality_gate_pass": material,
        "pass": bool(hard and material),
        "current_origin_month_nasdaq_required": False,
        "raw_values_logged": False,
    }


def fetch_pinned_metals() -> pd.DataFrame:
    rows = []
    s = requests.Session()
    for year in (2024, 2025, 2026):
        u = f"https://raw.githubusercontent.com/lbruton/StakTrakr/{PIN}/data/spot-history-{year}.json"
        r = s.get(u, timeout=90, headers={"User-Agent": "Gold-Control-Patch-Input-Bridge-V2/1.0"})
        r.raise_for_status()
        for z in r.json():
            metal = z.get("metal")
            if metal not in METALS or str(z.get("provider", "")).upper() != "LBMA":
                continue
            d = pd.to_datetime(z["timestamp"]).normalize()
            if METAL_START <= d <= METAL_END:
                rows.append((d, metal, float(z["spot"])))
    d = pd.DataFrame(rows, columns=["date", "metal", "spot"])
    if d.empty:
        raise RuntimeError("PINNED_METALS_V2_OVERLAP_EMPTY")
    d = d.sort_values(["date", "metal"]).drop_duplicates(["date", "metal"], keep="last")
    return d.pivot(index="date", columns="metal", values="spot").sort_index()


def fetch_twelve_daily(symbol: str, api_key: str) -> tuple[pd.Series, dict]:
    p = get_json(
        TWELVE_URL,
        params={
            "symbol": symbol,
            "interval": "1day",
            "start_date": METAL_START.date().isoformat(),
            "end_date": METAL_END.date().isoformat(),
            "timezone": "Europe/London",
            "outputsize": 1000,
            "order": "ASC",
            "format": "JSON",
        },
        headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Patch-Input-Bridge-V2/1.0"},
        sleep_base=7.0,
    )
    rows = []
    for z in p.get("values") or []:
        try:
            dt = pd.Timestamp(str(z.get("datetime"))).normalize()
            close = float(z["close"])
        except Exception:
            continue
        if METAL_START <= dt <= METAL_END and close > 0:
            rows.append((dt, close))
    if not rows:
        raise RuntimeError(f"TWELVE_DAILY_EMPTY:{symbol}")
    d = pd.DataFrame(rows, columns=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last")
    meta = p.get("meta") if isinstance(p.get("meta"), dict) else {}
    return d.set_index("date")["close"], {
        "symbol": meta.get("symbol", symbol),
        "interval": meta.get("interval", "1day"),
        "currency": meta.get("currency"),
        "type": meta.get("type"),
    }


def return_metrics(hist: pd.Series, proxy: pd.Series) -> dict:
    z = pd.concat([hist.rename("hist"), proxy.rename("proxy")], axis=1, join="inner").dropna()
    lr = np.log(z).diff().dropna()
    if len(lr) < 2:
        raise RuntimeError("RETURN_OVERLAP_INSUFFICIENT")
    corr = float(np.corrcoef(lr["hist"], lr["proxy"])[0, 1])
    sign = float(np.mean(np.sign(lr["hist"].to_numpy()) == np.sign(lr["proxy"].to_numpy())))
    gaps = np.abs(lr["hist"].to_numpy() - lr["proxy"].to_numpy()) * 10000.0
    return {
        "common_daily_observations": int(len(z)),
        "return_pairs": int(len(lr)),
        "return_corr": corr,
        "sign_agreement": sign,
        "median_abs_return_gap_bps": float(np.median(gaps)),
        "p95_abs_return_gap_bps": float(np.quantile(gaps, 0.95)),
    }


def metals_v2_audit(api_key: str) -> dict:
    pinned = fetch_pinned_metals()
    out = {}
    all_pass = True
    for metal, cfg in METALS.items():
        try:
            proxy, meta = fetch_twelve_daily(cfg["symbol"], api_key)
            if metal not in pinned.columns:
                raise RuntimeError(f"PINNED_METAL_MISSING:{metal}")
            m = return_metrics(pinned[metal].dropna(), proxy)
            hard = m["common_daily_observations"] >= 120 and m["return_pairs"] >= 100
            material = (
                m["return_corr"] >= 0.90
                and m["sign_agreement"] >= 0.75
                and m["median_abs_return_gap_bps"] <= cfg["median_gap_bps_max"]
                and m["p95_abs_return_gap_bps"] <= 300.0
            )
            passed = bool(hard and material)
            out[metal] = {
                **m,
                "operational_candidate": cfg["symbol"],
                "interval": "1day",
                "provider_meta": meta,
                "not_lbma_benchmark": True,
                "median_gap_gate_bps": cfg["median_gap_bps_max"],
                "p95_gap_gate_bps": 300.0,
                "corr_gate": 0.90,
                "sign_gate": 0.75,
                "hard_gate_pass": hard,
                "materiality_gate_pass": material,
                "pass": passed,
            }
        except Exception as exc:
            passed = False
            out[metal] = {
                "operational_candidate": cfg["symbol"],
                "interval": "1day",
                "not_lbma_benchmark": True,
                "hard_gate_pass": False,
                "materiality_gate_pass": False,
                "pass": False,
                "not_proven_reason": str(exc).split(":", 1)[0],
            }
        all_pass = all_pass and passed
        time.sleep(8.0)
    return {"series": out, "pass": bool(all_pass), "raw_values_logged": False}


def main() -> None:
    if not CONTRACT.exists() or "FROZEN_BEFORE_V2_RESULT" not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("V2_CONTRACT_NOT_FROZEN")
    core = load_core()
    inherited = load_v1_unchanged_macro_evidence()
    nas = nasdaq_lag1_audit(core, secret("FRED_API_KEY"))
    macro_pass = bool(inherited["fedfunds"]["pass"] and inherited["usdcny"]["pass"] and nas["pass"])
    metals = metals_v2_audit(secret("TWELVE_DATA_API_KEY"))
    passed = bool(macro_pass and metals["pass"])
    decision = "PATCH_PROSPECTIVE_INPUT_BRIDGE_V2_SOURCE_PASS" if passed else "BLOCKED_PATCH_PROSPECTIVE_INPUT_V2_SOURCE_NOT_PROVEN"
    evidence = {
        "contract": CONTRACT.name,
        "candidate_architecture": "CAUSAL_PATCH_R1_REPRO_V1",
        "reserved_identity_after_model_impact_only": "CAUSAL_PATCH_R1_REPRO_V1_1_ORIGIN_SAFE",
        "evidence_class": "INPUT_SOURCE_COMPATIBILITY_AUDIT",
        "prospective_claim": False,
        "geometry_changed": False,
        "geometry": {"L": 252, "P": 21, "D": 32},
        "macro_audit": {
            "fedfunds": inherited["fedfunds"],
            "usdcny": inherited["usdcny"],
            "nasdaq_lag1": nas,
            "pass": macro_pass,
        },
        "metals_audit": metals,
        "source_bridge_pass": passed,
        "decision": decision,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "database_write": "NONE",
        "raw_vendor_market_values_logged": False,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "prospective_input_bridge_v2_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"V2_MACRO_FEDFUNDS_PASS={str(inherited['fedfunds']['pass']).lower()}")
    print(f"V2_MACRO_USDCNY_PASS={str(inherited['usdcny']['pass']).lower()}")
    print(f"V2_NASDAQ_LAG1_N={nas['reconstructions']}")
    print(f"V2_NASDAQ_LAG1_MISSING_N={nas['missing_reconstructions']}")
    if nas["median_abs_relative_level_gap_pct"] is not None:
        print(f"V2_NASDAQ_LAG1_MEDIAN_LEVEL_GAP_PCT={nas['median_abs_relative_level_gap_pct']:.9f}")
        print(f"V2_NASDAQ_LAG1_P95_LEVEL_GAP_PCT={nas['p95_abs_relative_level_gap_pct']:.9f}")
    print(f"V2_NASDAQ_LAG1_PASS={str(nas['pass']).lower()}")
    print(f"V2_MACRO_BLOCK_PASS={str(macro_pass).lower()}")
    for name, v in metals["series"].items():
        u = name.upper()
        if "common_daily_observations" in v:
            print(f"V2_METAL_{u}_COMMON_N={v['common_daily_observations']}")
            print(f"V2_METAL_{u}_RETURN_PAIRS={v['return_pairs']}")
            print(f"V2_METAL_{u}_RETURN_CORR={v['return_corr']:.9f}")
            print(f"V2_METAL_{u}_SIGN_AGREE={v['sign_agreement']:.9f}")
            print(f"V2_METAL_{u}_MEDIAN_GAP_BPS={v['median_abs_return_gap_bps']:.6f}")
            print(f"V2_METAL_{u}_P95_GAP_BPS={v['p95_abs_return_gap_bps']:.6f}")
        else:
            print(f"V2_METAL_{u}_NOT_PROVEN_REASON={v.get('not_proven_reason')}")
        print(f"V2_METAL_{u}_PASS={str(v['pass']).lower()}")
    print(f"V2_METALS_BLOCK_PASS={str(metals['pass']).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V2_SOURCE_PASS={str(passed).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V2_DECISION={decision}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")


if __name__ == "__main__":
    main()
