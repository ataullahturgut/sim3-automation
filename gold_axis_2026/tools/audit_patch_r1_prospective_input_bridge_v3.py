from __future__ import annotations

import base64
import gzip
import io
import json
import os
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V3.md"
CHANGE_CONTROL = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_INPUT_SOURCE_CHANGE_CONTROL_V3_2026-09-02.md"
V1_EVIDENCE = OUT / "prospective_input_bridge_v1_evidence.json"

TWELVE_URL = "https://api.twelvedata.com/time_series"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
METALS = ["XAU/USD", "XAG/USD", "XPT/USD", "XPD/USD"]
METAL_NAMES = {"XAU/USD": "Gold", "XAG/USD": "Silver", "XPT/USD": "Platinum", "XPD/USD": "Palladium"}
HISTORY_START = pd.Timestamp("2010-01-01")
HISTORY_END = pd.Timestamp("2026-08-31")
RECENT_REQUIRED = pd.Timestamp("2026-08-28")
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")


def secret(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"{name}_NOT_SET")
    return v


def get_json(url: str, *, params: dict, headers: dict | None = None, attempts: int = 7, sleep_base: float = 4.0):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, headers=headers or {}, timeout=(20, 120))
            if r.status_code == 429:
                last = RuntimeError("HTTP_429")
                time.sleep(min(70.0, sleep_base * (i + 1)))
                continue
            r.raise_for_status()
            p = r.json()
            if isinstance(p, dict) and p.get("status") == "error":
                raise RuntimeError(f"PROVIDER_ERROR:{p.get('code')}:{p.get('message')}")
            return p
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(min(45.0, sleep_base * (2 ** i)))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{type(last).__name__}:{last}")


def load_core() -> pd.DataFrame:
    raw = gzip.decompress(base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip())).decode()
    return pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()


def inherited_macro_proof() -> dict:
    if not V1_EVIDENCE.exists():
        raise RuntimeError("V1_EVIDENCE_NOT_FOUND")
    e = json.loads(V1_EVIDENCE.read_text(encoding="utf-8"))
    fed = e["macro_audit"]["series"]["fedfunds"]
    fx = e["macro_audit"]["series"]["usdcny"]
    if not fed.get("pass") or fed.get("reconstructions") != 43:
        raise RuntimeError("V1_FEDFUNDS_PROOF_NOT_PASS")
    if not fx.get("pass") or fx.get("reconstructions") != 43:
        raise RuntimeError("V1_USDCNY_PROOF_NOT_PASS")
    return {
        "fedfunds": {"pass": True, "source": "V1_IMMUTABLE_EVIDENCE", "reconstructions": 43},
        "usdcny": {"pass": True, "source": "V1_IMMUTABLE_EVIDENCE", "reconstructions": 43},
    }


def parse_one_twelve_block(block: dict, symbol: str) -> tuple[pd.Series, dict]:
    if not isinstance(block, dict):
        raise RuntimeError(f"TWELVE_BLOCK_INVALID:{symbol}")
    if block.get("status") == "error":
        raise RuntimeError(f"TWELVE_SYMBOL_ERROR:{symbol}:{block.get('code')}")
    vals = block.get("values") or []
    rows = []
    for z in vals:
        try:
            d = pd.Timestamp(str(z.get("datetime"))).normalize()
            v = float(z.get("close"))
        except Exception:
            continue
        if HISTORY_START <= d <= HISTORY_END and np.isfinite(v) and v > 0:
            rows.append((d, v))
    if not rows:
        raise RuntimeError(f"TWELVE_DAILY_EMPTY:{symbol}")
    df = pd.DataFrame(rows, columns=["date", "close"]).sort_values("date")
    dup = int(df.duplicated("date").sum())
    if dup:
        raise RuntimeError(f"TWELVE_DAILY_DUPLICATE:{symbol}:{dup}")
    s = df.set_index("date")["close"].astype(float)
    meta = block.get("meta") if isinstance(block.get("meta"), dict) else {}
    return s, {
        "symbol": meta.get("symbol", symbol),
        "interval": meta.get("interval", "1day"),
        "type": meta.get("type"),
        "exchange": meta.get("exchange"),
        "rows": int(len(s)),
        "first_date": s.index.min().date().isoformat(),
        "last_date": s.index.max().date().isoformat(),
    }


def fetch_twelve_four_metals(api_key: str) -> tuple[pd.DataFrame, dict]:
    # One batch request avoids the V2 per-symbol rate-limit failure mode.
    p = get_json(
        TWELVE_URL,
        params={
            "symbol": ",".join(METALS),
            "interval": "1day",
            "start_date": HISTORY_START.date().isoformat(),
            "end_date": HISTORY_END.date().isoformat(),
            "outputsize": 5000,
            "order": "ASC",
            "format": "JSON",
        },
        headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Patch-Input-Bridge-V3/1.0"},
        sleep_base=8.0,
    )

    series = {}
    meta = {}
    # Multi-symbol response is keyed by symbol. A defensive single-symbol shape is also handled.
    for symbol in METALS:
        block = p.get(symbol) if isinstance(p, dict) else None
        if block is None and len(METALS) == 1:
            block = p
        if block is None:
            raise RuntimeError(f"TWELVE_BATCH_SYMBOL_MISSING:{symbol}")
        s, m = parse_one_twelve_block(block, symbol)
        if str(m.get("interval")) != "1day":
            raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{symbol}:{m.get('interval')}")
        series[METAL_NAMES[symbol]] = s
        meta[METAL_NAMES[symbol]] = m

    common = pd.concat(series, axis=1, join="inner").dropna().sort_index()
    if common.empty:
        raise RuntimeError("TWELVE_FOUR_METAL_COMMON_EMPTY")
    if common.index.duplicated().any():
        raise RuntimeError("TWELVE_FOUR_METAL_COMMON_DUPLICATE")
    return common, meta


def metals_depth_audit(api_key: str) -> dict:
    try:
        common, meta = fetch_twelve_four_metals(api_key)
        pre_first_origin = common.loc[common.index <= pd.Timestamp("2011-02-28")]
        enough_pre = len(pre_first_origin) >= 253
        enough_total = len(common) >= 3500
        recent = common.index.max() >= RECENT_REQUIRED
        all_meta = all(meta[k]["rows"] > 0 and meta[k]["interval"] == "1day" for k in meta)
        passed = bool(enough_pre and enough_total and recent and all_meta)
        return {
            "lineage": "PATCH_METALS_TWELVE_DAILY_FULL_HISTORY_V3",
            "symbols": meta,
            "common_rows": int(len(common)),
            "common_first_date": common.index.min().date().isoformat(),
            "common_last_date": common.index.max().date().isoformat(),
            "common_rows_through_2011_02_28": int(len(pre_first_origin)),
            "required_pre_origin_rows": 253,
            "total_common_rows_gate": 3500,
            "recent_required_date": RECENT_REQUIRED.date().isoformat(),
            "pre_origin_depth_pass": bool(enough_pre),
            "total_depth_pass": bool(enough_total),
            "recent_coverage_pass": bool(recent),
            "metadata_pass": bool(all_meta),
            "pass": passed,
            "raw_values_logged": False,
        }
    except Exception as exc:
        return {
            "lineage": "PATCH_METALS_TWELVE_DAILY_FULL_HISTORY_V3",
            "pass": False,
            "not_proven_reason": str(exc).split(":", 1)[0],
            "raw_values_logged": False,
        }


def fetch_fred_nasdaq(api_key: str) -> pd.Series:
    p = get_json(
        FRED_URL,
        params={
            "series_id": "NASDAQCOM",
            "api_key": api_key,
            "file_type": "json",
            "observation_start": HISTORY_START.date().isoformat(),
            "observation_end": HISTORY_END.date().isoformat(),
            "sort_order": "asc",
            "limit": 100000,
        },
        headers={"User-Agent": "Gold-Control-Patch-Input-Bridge-V3/1.0"},
        sleep_base=2.0,
    )
    rows = []
    for z in p.get("observations", []):
        sv = str(z.get("value", "."))
        if sv in {".", "", "nan", "None"}:
            continue
        try:
            d = pd.Timestamp(str(z.get("date"))).normalize()
            v = float(sv)
        except Exception:
            continue
        if HISTORY_START <= d <= HISTORY_END and np.isfinite(v) and v > 0:
            rows.append((d, v))
    if not rows:
        raise RuntimeError("FRED_NASDAQCOM_EMPTY")
    d = pd.DataFrame(rows, columns=["date", "close"]).sort_values("date")
    if d.duplicated("date").any():
        raise RuntimeError("FRED_NASDAQCOM_DUPLICATE")
    return d.set_index("date")["close"].astype(float)


def nasdaq_v3_audit(core: pd.DataFrame, api_key: str) -> dict:
    try:
        daily = fetch_fred_nasdaq(api_key)
        monthly = daily.resample("MS").mean().dropna()
        req_core = core.loc[(core.index >= HISTORY_START) & (core.index <= pd.Timestamp("2026-07-01")), "nasdaq"].dropna().astype(float)
        z = pd.concat([req_core.rename("core"), monthly.rename("fred")], axis=1, join="inner").dropna()
        missing_months = [m.strftime("%Y-%m") for m in req_core.index if m not in z.index]
        gaps = np.abs(z["fred"].to_numpy() - z["core"].to_numpy()) / np.maximum(np.abs(z["core"].to_numpy()), 1e-12) * 100.0
        med = None if len(gaps) == 0 else float(np.median(gaps))
        p95 = None if len(gaps) == 0 else float(np.quantile(gaps, 0.95))
        material = bool(med is not None and p95 is not None and med <= 0.30 and p95 <= 1.00)

        availability_violations = []
        locked_inputs = 0
        for t in pd.date_range(LOCKED_START, LOCKED_END, freq="MS"):
            p = t - pd.offsets.MonthBegin(1)
            for m in [p - pd.offsets.MonthBegin(2), p - pd.offsets.MonthBegin(1)]:
                vals = daily.loc[(daily.index >= m) & (daily.index <= m + pd.offsets.MonthEnd(0))]
                if vals.empty:
                    availability_violations.append({"target": t.strftime("%Y-%m"), "month": m.strftime("%Y-%m"), "reason": "MONTH_EMPTY"})
                    continue
                last_obs = vals.index.max()
                conservative_available = last_obs + pd.Timedelta(days=1)
                origin_end = p + pd.offsets.MonthEnd(0)
                if conservative_available > origin_end:
                    availability_violations.append({"target": t.strftime("%Y-%m"), "month": m.strftime("%Y-%m"), "reason": "NEXT_DAY_AFTER_ORIGIN"})
                locked_inputs += 1

        hard = bool(len(req_core) >= 190 and not missing_months and locked_inputs == 86 and not availability_violations)
        passed = bool(hard and material)
        return {
            "feature": "NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3",
            "availability_policy": "MARKET_CLOSE_AVAILABILITY_RECONSTRUCTION_NEXT_DAY_V1",
            "availability_evidence_class": "HISTORICAL_REPLAY_MARKET_CLOSE_AVAILABILITY_RECONSTRUCTION",
            "core_required_months": int(len(req_core)),
            "common_months": int(len(z)),
            "missing_months": missing_months[:20],
            "locked_completed_month_inputs_checked": int(locked_inputs),
            "availability_violations": availability_violations[:20],
            "median_abs_relative_level_gap_pct": med,
            "p95_abs_relative_level_gap_pct": p95,
            "median_gate_pct": 0.30,
            "p95_gate_pct": 1.00,
            "hard_gate_pass": hard,
            "materiality_gate_pass": material,
            "pass": passed,
            "raw_values_logged": False,
        }
    except Exception as exc:
        return {
            "feature": "NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3",
            "pass": False,
            "not_proven_reason": str(exc).split(":", 1)[0],
            "raw_values_logged": False,
        }


def main() -> None:
    if not CONTRACT.exists() or "FROZEN_BEFORE_V3_SOURCE_RESULT" not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("V3_CONTRACT_NOT_FROZEN")
    if not CHANGE_CONTROL.exists() or "FROZEN_BEFORE_V3_SOURCE_RESULT" not in CHANGE_CONTROL.read_text(encoding="utf-8"):
        raise RuntimeError("V3_CHANGE_CONTROL_NOT_FROZEN")

    inherited = inherited_macro_proof()
    core = load_core()
    metals = metals_depth_audit(secret("TWELVE_DATA_API_KEY"))
    nasdaq = nasdaq_v3_audit(core, secret("FRED_API_KEY"))

    passed = bool(inherited["fedfunds"]["pass"] and inherited["usdcny"]["pass"] and metals.get("pass") and nasdaq.get("pass"))
    decision = "PATCH_PROSPECTIVE_INPUT_BRIDGE_V3_SOURCE_PASS" if passed else "BLOCKED_PATCH_PROSPECTIVE_INPUT_V3_SOURCE_NOT_PROVEN"

    evidence = {
        "contract": CONTRACT.name,
        "change_control": CHANGE_CONTROL.name,
        "candidate_architecture": "CAUSAL_PATCH_R1_REPRO_V1",
        "reserved_identity_after_model_impact_only": "CAUSAL_PATCH_R1_REPRO_V1_2_TWELVE_DAILY_ORIGIN_SAFE",
        "evidence_class": "INPUT_SOURCE_READINESS_AUDIT",
        "prospective_claim": False,
        "geometry_changed": False,
        "geometry": {"L": 252, "P": 21, "D": 32},
        "inherited_macro": inherited,
        "metals_source_depth": metals,
        "nasdaq_source_identity_availability": nasdaq,
        "source_bridge_pass": passed,
        "decision": decision,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "database_write": "NONE",
        "raw_vendor_market_values_logged": False,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "prospective_input_bridge_v3_source_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"V3_FEDFUNDS_INHERITED_PASS={str(inherited['fedfunds']['pass']).lower()}")
    print(f"V3_USDCNY_INHERITED_PASS={str(inherited['usdcny']['pass']).lower()}")
    if "common_rows" in metals:
        print(f"V3_METALS_COMMON_ROWS={metals['common_rows']}")
        print(f"V3_METALS_COMMON_PRE_ORIGIN_ROWS={metals['common_rows_through_2011_02_28']}")
        print(f"V3_METALS_COMMON_FIRST_DATE={metals['common_first_date']}")
        print(f"V3_METALS_COMMON_LAST_DATE={metals['common_last_date']}")
    else:
        print(f"V3_METALS_NOT_PROVEN_REASON={metals.get('not_proven_reason')}")
    print(f"V3_METALS_SOURCE_DEPTH_PASS={str(bool(metals.get('pass'))).lower()}")
    if "common_months" in nasdaq:
        print(f"V3_NASDAQ_COMMON_MONTHS={nasdaq['common_months']}")
        print(f"V3_NASDAQ_MISSING_MONTHS_N={len(nasdaq['missing_months'])}")
        print(f"V3_NASDAQ_LOCKED_INPUTS_CHECKED={nasdaq['locked_completed_month_inputs_checked']}")
        print(f"V3_NASDAQ_AVAILABILITY_VIOLATIONS_N={len(nasdaq['availability_violations'])}")
        print(f"V3_NASDAQ_MEDIAN_GAP_PCT={nasdaq['median_abs_relative_level_gap_pct']:.9f}")
        print(f"V3_NASDAQ_P95_GAP_PCT={nasdaq['p95_abs_relative_level_gap_pct']:.9f}")
    else:
        print(f"V3_NASDAQ_NOT_PROVEN_REASON={nasdaq.get('not_proven_reason')}")
    print(f"V3_NASDAQ_SOURCE_PASS={str(bool(nasdaq.get('pass'))).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V3_SOURCE_PASS={str(passed).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V3_DECISION={decision}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")


if __name__ == "__main__":
    main()
