from __future__ import annotations

import base64
import gzip
import io
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V1.md"
PIN = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
TWELVE_URL = "https://api.twelvedata.com/time_series"
TWELVE_COMMODITIES_URL = "https://api.twelvedata.com/commodities"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
TARGET_START = pd.Timestamp("2023-01-01")
TARGET_END = pd.Timestamp("2026-07-01")
METAL_START = pd.Timestamp("2026-01-01")
METAL_END = pd.Timestamp("2026-08-19")

METALS = {
    "Gold": {"symbol": "XAU/USD", "hour": 15, "median_gap_bps_max": 75.0},
    "Silver": {"symbol": "XAG/USD", "hour": 12, "median_gap_bps_max": 75.0},
    "Platinum": {"symbol": "XPT/USD", "hour": 14, "median_gap_bps_max": 100.0},
    "Palladium": {"symbol": "XPD/USD", "hour": 14, "median_gap_bps_max": 100.0},
}

MACROS = {
    "fedfunds": {"fred": "DFF", "median_rel_pct_max": 0.50, "p95_rel_pct_max": 1.50},
    "nasdaq": {"fred": "NASDAQCOM", "median_rel_pct_max": 0.30, "p95_rel_pct_max": 1.00},
    "usdcny": {"fred": "DEXCHUS", "median_rel_pct_max": 0.20, "p95_rel_pct_max": 0.75},
}


def key(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"{name}_NOT_SET")
    return v


def get_json(url: str, *, params: dict, headers: dict | None = None, attempts: int = 5, sleep_base: float = 3.0):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=(15, 90))
            if r.status_code == 429:
                last = RuntimeError("HTTP_429")
                time.sleep(min(45.0, sleep_base * (i + 1)))
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


def fetch_pinned_metals() -> pd.DataFrame:
    rows = []
    s = requests.Session()
    for year in (2025, 2026):
        u = f"https://raw.githubusercontent.com/lbruton/StakTrakr/{PIN}/data/spot-history-{year}.json"
        r = s.get(u, timeout=90, headers={"User-Agent": "Gold-Control-Patch-Input-Bridge/1.0"})
        r.raise_for_status()
        for z in r.json():
            metal = z.get("metal")
            if metal not in METALS:
                continue
            provider = str(z.get("provider", ""))
            if provider.upper() != "LBMA":
                continue
            d = pd.to_datetime(z["timestamp"]).normalize()
            if METAL_START <= d <= METAL_END:
                rows.append((d, metal, float(z["spot"])))
    d = pd.DataFrame(rows, columns=["date", "metal", "spot"])
    if d.empty:
        raise RuntimeError("PINNED_METALS_OVERLAP_EMPTY")
    d = d.sort_values(["date", "metal"]).drop_duplicates(["date", "metal"], keep="last")
    return d.pivot(index="date", columns="metal", values="spot").sort_index()


def verify_twelve_symbol(symbol: str, api_key: str) -> dict:
    p = get_json(
        TWELVE_COMMODITIES_URL,
        params={"symbol": symbol, "format": "JSON"},
        headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Patch-Input-Bridge/1.0"},
    )
    data = p.get("data") or []
    hit = [z for z in data if z.get("symbol") == symbol]
    if not hit:
        raise RuntimeError(f"TWELVE_SYMBOL_NOT_FOUND:{symbol}")
    z = hit[0]
    return {"symbol": symbol, "name": z.get("name"), "category": z.get("category")}


def fetch_twelve_proxy(symbol: str, hour: int, api_key: str) -> pd.Series:
    # Fixed chunks keep every 1h request safely below outputsize=5000.
    chunks = [
        ("2026-01-01", "2026-03-20"),
        ("2026-03-21", "2026-06-10"),
        ("2026-06-11", "2026-08-19"),
    ]
    rows = []
    for start, end in chunks:
        p = get_json(
            TWELVE_URL,
            params={
                "symbol": symbol,
                "interval": "1h",
                "start_date": start,
                "end_date": end,
                "timezone": "Europe/London",
                "outputsize": 5000,
                "order": "ASC",
                "format": "JSON",
            },
            headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Patch-Input-Bridge/1.0"},
            sleep_base=6.0,
        )
        vals = p.get("values") or []
        for z in vals:
            dt = pd.Timestamp(str(z.get("datetime")))
            if dt.hour != hour or dt.minute != 0:
                continue
            try:
                close = float(z["close"])
            except Exception:
                continue
            if close > 0:
                rows.append((dt.normalize(), close))
        time.sleep(7.0)
    if not rows:
        raise RuntimeError(f"TWELVE_PROXY_EMPTY:{symbol}")
    d = pd.DataFrame(rows, columns=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last")
    return d.set_index("date")["close"]


def return_metrics(a: pd.Series, b: pd.Series) -> dict:
    z = pd.concat([a.rename("hist"), b.rename("proxy")], axis=1, join="inner").dropna()
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


def fred_month_mean_asof(series_id: str, month: pd.Timestamp, api_key: str) -> tuple[float, int, str | None]:
    start = month.date().isoformat()
    end_ts = month + pd.offsets.MonthEnd(0)
    end = end_ts.date().isoformat()
    p = get_json(
        FRED_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": end,
            "realtime_end": end,
            "observation_start": start,
            "observation_end": end,
            "sort_order": "asc",
            "limit": 200,
        },
        headers={"User-Agent": "Gold-Control-Patch-Input-Bridge/1.0"},
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
        if d > end_ts:
            raise RuntimeError(f"FUTURE_OBSERVATION:{series_id}:{d.date()}:{end}")
        vals.append(v)
        max_date = d if max_date is None or d > max_date else max_date
    if not vals:
        raise RuntimeError(f"ALFRED_MONTH_EMPTY:{series_id}:{month.strftime('%Y-%m')}")
    return float(np.mean(vals)), len(vals), None if max_date is None else max_date.date().isoformat()


def macro_audit(core: pd.DataFrame, fred_key: str) -> dict:
    raw = {k: [] for k in MACROS}
    for t in pd.date_range(TARGET_START, TARGET_END, freq="MS"):
        pmonth = t - pd.offsets.MonthBegin(1)
        if pmonth not in core.index:
            raise RuntimeError(f"CORE_MONTH_MISSING:{pmonth.date()}")
        for i, (name, cfg) in enumerate(MACROS.items()):
            val, n, max_date = fred_month_mean_asof(cfg["fred"], pmonth, fred_key)
            locked = float(core.loc[pmonth, name])
            rel = abs(val - locked) / max(abs(locked), 1e-12) * 100.0
            raw[name].append({"target": t.strftime("%Y-%m"), "rel_gap_pct": rel, "obs_count": n, "max_source_date": max_date})
            time.sleep(0.25)
    out = {}
    all_pass = True
    for name, rows in raw.items():
        cfg = MACROS[name]
        gaps = np.array([r["rel_gap_pct"] for r in rows], float)
        hard = len(rows) == 43 and all(r["obs_count"] > 0 for r in rows)
        med = float(np.median(gaps))
        p95 = float(np.quantile(gaps, 0.95))
        material = med <= cfg["median_rel_pct_max"] and p95 <= cfg["p95_rel_pct_max"]
        passed = hard and material
        all_pass = all_pass and passed
        out[name] = {
            "fred_series": cfg["fred"],
            "reconstructions": len(rows),
            "median_abs_relative_gap_pct": med,
            "p95_abs_relative_gap_pct": p95,
            "median_gate_pct": cfg["median_rel_pct_max"],
            "p95_gate_pct": cfg["p95_rel_pct_max"],
            "hard_gate_pass": hard,
            "materiality_gate_pass": material,
            "pass": passed,
            "source_observation_counts_min": int(min(r["obs_count"] for r in rows)),
            "source_observation_counts_max": int(max(r["obs_count"] for r in rows)),
        }
    return {"series": out, "pass": all_pass, "raw_values_logged": False}


def metal_audit(api_key: str) -> dict:
    pinned = fetch_pinned_metals()
    out = {}
    all_pass = True
    identities = {}
    for metal, cfg in METALS.items():
        identities[metal] = verify_twelve_symbol(cfg["symbol"], api_key)
        proxy = fetch_twelve_proxy(cfg["symbol"], cfg["hour"], api_key)
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
        passed = hard and material
        all_pass = all_pass and passed
        out[metal] = {
            **m,
            "symbol": cfg["symbol"],
            "london_hour": cfg["hour"],
            "median_gap_gate_bps": cfg["median_gap_bps_max"],
            "p95_gap_gate_bps": 300.0,
            "corr_gate": 0.90,
            "sign_gate": 0.75,
            "hard_gate_pass": hard,
            "materiality_gate_pass": material,
            "pass": passed,
        }
    return {"series": out, "identities": identities, "pass": all_pass, "raw_values_logged": False}


def main() -> None:
    if not CONTRACT.exists():
        raise RuntimeError("BRIDGE_CONTRACT_NOT_FOUND")
    if "FROZEN_BEFORE_BRIDGE_AUDIT" not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("BRIDGE_CONTRACT_NOT_FROZEN")
    core = load_core()
    macro = macro_audit(core, key("FRED_API_KEY"))
    metals = metal_audit(key("TWELVE_DATA_API_KEY"))
    passed = bool(macro["pass"] and metals["pass"])
    decision = "PATCH_PROSPECTIVE_INPUT_BRIDGE_V1_PASS" if passed else "BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN"
    evidence = {
        "contract": CONTRACT.name,
        "candidate_id": "CAUSAL_PATCH_R1_REPRO_V1",
        "evidence_class": "INPUT_SOURCE_COMPATIBILITY_AUDIT",
        "prospective_claim": False,
        "macro_audit": macro,
        "metals_audit": metals,
        "bridge_pass": passed,
        "decision": decision,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "database_write": "NONE",
        "raw_vendor_market_values_logged": False,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "prospective_input_bridge_v1_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"PATCH_INPUT_BRIDGE_MACRO_PASS={str(macro['pass']).lower()}")
    for k, v in macro["series"].items():
        print(f"MACRO_{k.upper()}_N={v['reconstructions']}")
        print(f"MACRO_{k.upper()}_MEDIAN_REL_GAP_PCT={v['median_abs_relative_gap_pct']:.9f}")
        print(f"MACRO_{k.upper()}_P95_REL_GAP_PCT={v['p95_abs_relative_gap_pct']:.9f}")
        print(f"MACRO_{k.upper()}_PASS={str(v['pass']).lower()}")
    print(f"PATCH_INPUT_BRIDGE_METALS_PASS={str(metals['pass']).lower()}")
    for k, v in metals["series"].items():
        u = k.upper()
        print(f"METAL_{u}_COMMON_N={v['common_daily_observations']}")
        print(f"METAL_{u}_RETURN_PAIRS={v['return_pairs']}")
        print(f"METAL_{u}_RETURN_CORR={v['return_corr']:.9f}")
        print(f"METAL_{u}_SIGN_AGREE={v['sign_agreement']:.9f}")
        print(f"METAL_{u}_MEDIAN_GAP_BPS={v['median_abs_return_gap_bps']:.6f}")
        print(f"METAL_{u}_P95_GAP_BPS={v['p95_abs_return_gap_bps']:.6f}")
        print(f"METAL_{u}_PASS={str(v['pass']).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V1_PASS={str(passed).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V1_DECISION={decision}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")


if __name__ == "__main__":
    main()
