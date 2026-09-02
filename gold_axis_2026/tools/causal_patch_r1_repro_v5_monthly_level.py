from __future__ import annotations

import base64
import gzip
import io
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_MONTHLY_LEVEL_INPUT_CHANGE_CONTROL_V5_2026-09-02.md"
IDENTITY = "CAUSAL_PATCH_R1_REPRO_V1_4_XAU_MONTHLY_LEVEL_ORIGIN_SAFE"
SOURCE_PASS_ID = "PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_PASS"
SOURCE_FAIL_ID = "BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_NOT_PROVEN"
MODEL_PASS_ID = "PATCH_R1_V5_MONTHLY_LEVEL_MODEL_IMPACT_PASS"
MODEL_FAIL_ID = "PATCH_R1_V5_MONTHLY_LEVEL_MODEL_IMPACT_FAIL_NO_RETUNE"
SEED = 20260902
L = 252
P = 21
D = 32
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")
LEVEL_REQUIRED_START = pd.Timestamp("2011-02-01")
LEVEL_REQUIRED_END = pd.Timestamp("2026-07-01")
TWELVE_URL = "https://api.twelvedata.com/time_series"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

# Inherited unchanged from already pre-result-frozen Gold Control monthly-gold
# bridge research. These values must not be altered after V5 output is seen.
LEVEL_CORR_MIN = 0.995
MEDIAN_GAP_BPS_MAX = 50.0
P95_GAP_BPS_MAX = 100.0
RETURN_CORR_MIN = 0.95
SIGN_AGREE_MIN = 0.80
MIN_DAILY_PER_MONTH = 15


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass


def env_key(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_NOT_SET")
    return value


def load_core() -> pd.DataFrame:
    raw = gzip.decompress(
        base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip())
    ).decode()
    return pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()


def request_json(
    session: requests.Session,
    url: str,
    *,
    params: dict,
    headers: dict | None = None,
    attempts: int = 8,
) -> dict:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            response = session.get(url, params=params, headers=headers or {}, timeout=(20, 180))
            payload = response.json()
            code = payload.get("code") if isinstance(payload, dict) else None
            if response.status_code == 429 or code == 429:
                time.sleep(65)
                continue
            response.raise_for_status()
            if isinstance(payload, dict) and payload.get("status") == "error":
                raise RuntimeError(f"PROVIDER_ERROR:{payload.get('code')}:{payload.get('message')}")
            if not isinstance(payload, dict):
                raise RuntimeError("PROVIDER_RESPONSE_NOT_DICT")
            return payload
        except Exception as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(min(30, 2 ** attempt))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{type(last).__name__ if last else 'UNKNOWN'}")


def fetch_xau_daily(session: requests.Session) -> pd.DataFrame:
    payload = request_json(
        session,
        TWELVE_URL,
        params={
            "symbol": "XAU/USD",
            "interval": "1day",
            "start_date": "2010-01-01",
            "end_date": "2026-08-31",
            "outputsize": 5000,
            "order": "ASC",
            "format": "JSON",
        },
        headers={
            "Authorization": f"apikey {env_key('TWELVE_DATA_API_KEY')}",
            "User-Agent": "Gold-Control-Patch-V5-Model-Impact/1.0",
        },
    )
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1day":
        raise RuntimeError(f"XAU_DAILY_META_MISMATCH:{meta.get('symbol')}:{meta.get('interval')}")
    rows = []
    for item in payload.get("values") or []:
        try:
            date = pd.Timestamp(str(item.get("datetime"))).normalize()
            value = float(item.get("close"))
        except Exception:
            continue
        if np.isfinite(value) and value > 0:
            rows.append((date, value))
    frame = pd.DataFrame(rows, columns=["date", "Gold"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("XAU_DAILY_HISTORY_INVALID")
    return frame.set_index("date")


def fetch_xau_hourly_monthly_level(session: requests.Session) -> tuple[pd.Series, pd.Series, dict]:
    start = pd.Timestamp("2011-01-01")
    final = pd.Timestamp("2026-08-31 23:59:59")
    api_key = env_key("TWELVE_DATA_API_KEY")
    selected: dict[pd.Timestamp, float] = {}
    request_count = 0
    metadata_ok = True

    cursor = start
    while cursor <= final:
        end = min(cursor + pd.DateOffset(months=6) - pd.Timedelta(seconds=1), final)
        payload = request_json(
            session,
            TWELVE_URL,
            params={
                "symbol": "XAU/USD",
                "interval": "1h",
                "start_date": cursor.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": "America/New_York",
                "outputsize": 5000,
                "order": "ASC",
                "format": "JSON",
            },
            headers={
                "Authorization": f"apikey {api_key}",
                "User-Agent": "Gold-Control-Patch-V5-Monthly-Level/1.0",
            },
        )
        request_count += 1
        meta = payload.get("meta") or {}
        metadata_ok = metadata_ok and str(meta.get("symbol")) == "XAU/USD" and str(meta.get("interval")) == "1h"
        for item in payload.get("values") or []:
            dt_text = str(item.get("datetime", ""))
            if not dt_text.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(dt_text)
                value = float(item.get("close"))
            except Exception:
                continue
            if not (np.isfinite(value) and value > 0):
                continue
            date = ts.normalize()
            if date in selected:
                raise RuntimeError(f"V5_DUPLICATE_SELECTED_DAILY_DATE:{date.date()}")
            selected[date] = value
        cursor = (end + pd.Timedelta(seconds=1)).normalize()
        time.sleep(8)

    if not metadata_ok:
        raise RuntimeError("V5_HOURLY_METADATA_MISMATCH")
    if not selected:
        raise RuntimeError("V5_NO_SELECTED_HOURLY_CLOSES")

    daily = pd.Series(selected).sort_index()
    monthly_level = daily.resample("MS").mean().dropna()
    monthly_count = daily.resample("MS").count().astype(int)
    stats = {
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "requested_timezone": "America/New_York",
        "selected_bar_open_time": "16:00:00",
        "selected_bar_end_semantic": "17:00_ET_HOURLY_CLOSE",
        "request_count": request_count,
        "selected_daily_observation_count": int(len(daily)),
        "first_selected_date": daily.index.min().date().isoformat(),
        "last_selected_date": daily.index.max().date().isoformat(),
    }
    return monthly_level, monthly_count, stats


def fetch_nasdaq_monthly(session: requests.Session) -> pd.Series:
    payload = request_json(
        session,
        FRED_URL,
        params={
            "series_id": "NASDAQCOM",
            "api_key": env_key("FRED_API_KEY"),
            "file_type": "json",
            "observation_start": "2010-01-01",
            "observation_end": "2026-08-31",
            "sort_order": "asc",
            "limit": 100000,
        },
        headers={"User-Agent": "Gold-Control-Patch-V5-Model-Impact/1.0"},
    )
    rows = []
    for item in payload.get("observations") or []:
        raw = str(item.get("value", "."))
        if raw in {".", "", "nan", "None"}:
            continue
        try:
            date = pd.Timestamp(str(item.get("date"))).normalize()
            value = float(raw)
        except Exception:
            continue
        if np.isfinite(value) and value > 0:
            rows.append((date, value))
    frame = pd.DataFrame(rows, columns=["date", "value"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("NASDAQ_HISTORY_INVALID")
    return frame.set_index("date")["value"].resample("MS").mean().dropna()


def audit_monthly_level_source(core: pd.DataFrame, level: pd.Series, counts: pd.Series, stats: dict) -> dict:
    if "gold_monthly" not in core.columns:
        raise RuntimeError("CORE5_GOLD_MONTHLY_NOT_FOUND")
    required = core.loc[LEVEL_REQUIRED_START:LEVEL_REQUIRED_END, "gold_monthly"].dropna().index
    missing = [m.strftime("%Y-%m") for m in required if m not in level.index]
    low_count = [m.strftime("%Y-%m") for m in required if m in counts.index and int(counts.loc[m]) < MIN_DAILY_PER_MONTH]

    common = [m for m in required if m in level.index and m in counts.index and int(counts.loc[m]) >= MIN_DAILY_PER_MONTH]
    canonical = np.array([float(core.loc[m, "gold_monthly"]) for m in common], dtype=float)
    operational = np.array([float(level.loc[m]) for m in common], dtype=float)
    if len(common) < 2:
        raise RuntimeError("V5_INSUFFICIENT_COMMON_MONTHS")

    rel_bps = np.abs(operational - canonical) / np.abs(canonical) * 10000.0
    level_corr = float(np.corrcoef(canonical, operational)[0, 1])
    median_bps = float(np.median(rel_bps))
    p95_bps = float(np.quantile(rel_bps, 0.95))
    canonical_ret = np.diff(np.log(canonical))
    operational_ret = np.diff(np.log(operational))
    return_corr = float(np.corrcoef(canonical_ret, operational_ret)[0, 1])
    sign_agree = float(np.mean(np.sign(canonical_ret) == np.sign(operational_ret)))

    coverage_pass = len(missing) == 0 and len(low_count) == 0 and len(common) == len(required)
    materiality_pass = bool(
        level_corr >= LEVEL_CORR_MIN
        and median_bps <= MEDIAN_GAP_BPS_MAX
        and p95_bps <= P95_GAP_BPS_MAX
        and return_corr >= RETURN_CORR_MIN
        and sign_agree >= SIGN_AGREE_MIN
    )
    passed = bool(coverage_pass and materiality_pass)

    evidence = {
        "candidate_series_id": "PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V5",
        "source_semantic": stats,
        "required_window": "2011-02..2026-07",
        "required_months": int(len(required)),
        "common_months": int(len(common)),
        "missing_months_count": int(len(missing)),
        "low_daily_count_months_count": int(len(low_count)),
        "min_daily_observations_per_month": MIN_DAILY_PER_MONTH,
        "level_corr": level_corr,
        "median_abs_gap_bps": median_bps,
        "p95_abs_gap_bps": p95_bps,
        "monthly_return_corr": return_corr,
        "monthly_return_sign_agree": sign_agree,
        "frozen_gates": {
            "level_corr_min": LEVEL_CORR_MIN,
            "median_gap_bps_max": MEDIAN_GAP_BPS_MAX,
            "p95_gap_bps_max": P95_GAP_BPS_MAX,
            "return_corr_min": RETURN_CORR_MIN,
            "sign_agree_min": SIGN_AGREE_MIN,
        },
        "coverage_pass": coverage_pass,
        "materiality_pass": materiality_pass,
        "source_bridge_pass": passed,
        "decision": SOURCE_PASS_ID if passed else SOURCE_FAIL_ID,
        "raw_vendor_market_values_logged": False,
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "post_result_threshold_change": False,
    }
    return evidence


def gpr_z_asof(core: pd.DataFrame, asof_month: pd.Timestamp) -> float:
    history = core.loc[:asof_month, "gpr"].dropna().astype(float)
    if history.empty:
        return 0.5
    lo, hi = float(history.min()), float(history.max())
    return 0.5 if hi <= lo else float((history.iloc[-1] - lo) / (hi - lo))


def causal_decomp(values: np.ndarray, win: int = 21) -> np.ndarray:
    trend = np.zeros_like(values)
    for i in range(len(values)):
        trend[i] = values[max(0, i - win + 1) : i + 1].mean(0)
    return np.concatenate([trend, values - trend], axis=1)


class PatchTransformer(nn.Module):
    def __init__(self, channels: int, patch: int, d_model: int):
        super().__init__()
        self.patch = patch
        self.stride = max(1, patch // 2)
        self.emb = nn.Linear(patch * channels, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=4,
            dim_feedforward=4 * d_model,
            dropout=0.10,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.enc = nn.TransformerEncoder(layer, 2)
        self.conv = nn.Conv1d(d_model, d_model, 3, padding=1)
        self.head = nn.Sequential(
            nn.Linear(d_model + 5, 64),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor, macro: torch.Tensor) -> torch.Tensor:
        patches = x.unfold(1, self.patch, self.stride).permute(0, 1, 3, 2).contiguous().flatten(2)
        z = self.enc(self.emb(patches))
        z = self.conv(z.transpose(1, 2)).transpose(1, 2).mean(1)
        return self.head(torch.cat([z, macro], 1)).squeeze(1)


def build_samples(
    xau_daily: pd.DataFrame,
    monthly_level: pd.Series,
    core: pd.DataFrame,
    nas_monthly: pd.Series,
) -> tuple[list[tuple], int]:
    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    samples: list[tuple] = []
    future_violations = 0
    for target in sorted(core.index):
        if target < pd.Timestamp("2011-03-01") or target > LOCKED_END:
            continue
        p = target - pd.offsets.MonthBegin(1)
        pp = p - pd.offsets.MonthBegin(1)
        ppp = p - pd.offsets.MonthBegin(2)
        if any(month not in core.index for month in [p, pp]):
            continue
        if target not in monthly_level.index or p not in monthly_level.index:
            continue
        if pp not in nas_monthly.index or ppp not in nas_monthly.index:
            continue
        origin_end = target - pd.Timedelta(days=1)
        history = daily_returns.loc[:origin_end]
        if len(history) < L:
            continue
        if history.index.max() > origin_end:
            future_violations += 1
        x = causal_decomp(history.iloc[-L:].values.astype(np.float32), 21).astype(np.float32)
        nasdaq = float(np.log(float(nas_monthly.loc[pp]) / float(nas_monthly.loc[ppp])))
        fx = float(np.log(float(core.loc[p, "usdcny"]) / float(core.loc[pp, "usdcny"])))
        gpr = float(core.loc[pp, "gpr"])
        macro = np.array(
            [
                float(core.loc[p, "fedfunds"]),
                nasdaq,
                fx,
                np.log1p(gpr),
                gpr_z_asof(core, pp),
            ],
            dtype=np.float32,
        )
        y = float(np.log(float(monthly_level.loc[target]) / float(monthly_level.loc[p])))
        samples.append((target, x, macro, y))
    return samples, future_violations


def normalize_sets(train: list[tuple], valid: list[tuple]):
    x = np.stack([s[1] for s in train])
    m = np.stack([s[2] for s in train])
    y = np.array([s[3] for s in train], np.float32)
    xm = x.reshape(-1, x.shape[-1]).mean(0)
    xs = x.reshape(-1, x.shape[-1]).std(0) + 1e-6
    mm = m.mean(0)
    ms = m.std(0) + 1e-6
    ym = float(y.mean())
    ys = float(y.std() + 1e-6)

    def transform(sample):
        return (
            (sample[1] - xm) / xs,
            (sample[2] - mm) / ms,
            np.float32((sample[3] - ym) / ys),
        )

    return [transform(s) for s in train], [transform(s) for s in valid], (xm, xs, mm, ms, ym, ys)


def fit_patch(train: list[tuple], valid: list[tuple], seed: int, epochs: int = 140):
    seed_all(seed)
    a, b, scale = normalize_sets(train, valid)
    x = torch.tensor(np.stack([z[0] for z in a]), dtype=torch.float32)
    m = torch.tensor(np.stack([z[1] for z in a]), dtype=torch.float32)
    y = torch.tensor(np.array([z[2] for z in a]), dtype=torch.float32)
    model = PatchTransformer(x.shape[-1], P, D)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.HuberLoss()
    best = None
    best_valid = 1e99
    bad = 0
    for _ in range(epochs):
        model.train()
        order = torch.randperm(len(x))
        for k in range(0, len(x), 32):
            idx = order[k : k + 32]
            optimizer.zero_grad()
            loss = loss_fn(model(x[idx], m[idx]), y[idx])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        if b:
            model.eval()
            vx = torch.tensor(np.stack([z[0] for z in b]), dtype=torch.float32)
            vm = torch.tensor(np.stack([z[1] for z in b]), dtype=torch.float32)
            vy = torch.tensor(np.array([z[2] for z in b]), dtype=torch.float32)
            with torch.no_grad():
                score = float(torch.mean(torch.abs(model(vx, vm) - vy)))
            if score < best_valid - 1e-5:
                best_valid = score
                best = {key: value.detach().clone() for key, value in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if bad >= 24:
                    break
    if best:
        model.load_state_dict(best)
    return model, scale


def predict(model: nn.Module, scale: tuple, sample: tuple) -> float:
    xm, xs, mm, ms, ym, ys = scale
    x = ((sample[1] - xm) / xs).astype(np.float32)
    macro = ((sample[2] - mm) / ms).astype(np.float32)
    model.eval()
    with torch.no_grad():
        normalized = float(model(torch.tensor(x[None]), torch.tensor(macro[None])).item())
    return normalized * ys + ym


def locked_predictions(
    core: pd.DataFrame,
    xau_daily: pd.DataFrame,
    nas_monthly: pd.Series,
    monthly_level: pd.Series,
) -> tuple[pd.DataFrame, int]:
    samples, future_violations = build_samples(xau_daily, monthly_level, core, nas_monthly)
    output = []
    for target in pd.date_range(LOCKED_START, LOCKED_END, freq="MS"):
        all_train = [s for s in samples if s[0] < target]
        test = [s for s in samples if s[0] == target]
        if len(test) != 1:
            raise RuntimeError(f"V5_TARGET_SAMPLE_MISSING:{target.date()}")
        cut = max(48, int(len(all_train) * 0.85))
        cut = min(cut, len(all_train) - 12)
        train, valid = all_train[:cut], all_train[cut:]
        if len(train) < 48 or len(valid) < 12:
            raise RuntimeError(f"V5_TRAIN_VALID_SPLIT_INVALID:{target.date()}:{len(train)}:{len(valid)}")
        repetitions = []
        for offset in [0, 101, 202]:
            model, scale = fit_patch(train, valid, SEED + offset + int(target.strftime("%Y%m")), 140)
            repetitions.append(predict(model, scale, test[0]))
        predicted_return = float(np.median(repetitions))
        p = target - pd.offsets.MonthBegin(1)
        forecast = float(monthly_level.loc[p]) * math.exp(predicted_return)
        output.append((target.strftime("%Y-%m"), forecast, predicted_return))
    return pd.DataFrame(output, columns=["month", "patch_v5", "predicted_log_return"]), future_violations


def metrics(actual, prediction) -> dict:
    a = np.asarray(actual, float)
    p = np.asarray(prediction, float)
    error = p - a
    ape = np.abs(error) / a * 100.0
    return {
        "MAE": float(np.mean(np.abs(error))),
        "MAPE_pct": float(np.mean(ape)),
        "median_APE_pct": float(np.median(ape)),
        "worst_APE_pct": float(np.max(ape)),
        "RMSE": float(np.sqrt(np.mean(error * error))),
    }


def main() -> int:
    contract_text = CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_V5_SOURCE_RESULT" not in contract_text or IDENTITY not in contract_text:
        raise RuntimeError("V5_CONTRACT_NOT_FROZEN")
    geometry = json.loads((OUT / "frozen_geometry.json").read_text(encoding="utf-8"))["selected_pre_2023_geometry"]
    if (int(geometry["L"]), int(geometry["P"]), int(geometry["D"])) != (L, P, D):
        raise RuntimeError(f"V5_FROZEN_GEOMETRY_MISMATCH:{geometry}")

    core = load_core()
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Patch-V5/1.0"})
    monthly_level, monthly_counts, source_stats = fetch_xau_hourly_monthly_level(session)
    source_evidence = audit_monthly_level_source(core, monthly_level, monthly_counts, source_stats)
    source_evidence["candidate_id"] = IDENTITY
    source_evidence["evidence_class"] = "SOURCE_INPUT_SEMANTIC_AUDIT"
    source_evidence["prospective_claim"] = False
    source_path = OUT / "prospective_monthly_level_v5_source_evidence.json"
    source_path.write_text(json.dumps(source_evidence, indent=2), encoding="utf-8")

    print(f"V5_SOURCE_REQUIRED_MONTHS={source_evidence['required_months']}")
    print(f"V5_SOURCE_COMMON_MONTHS={source_evidence['common_months']}")
    print(f"V5_SOURCE_MISSING_MONTHS={source_evidence['missing_months_count']}")
    print(f"V5_SOURCE_LOW_COUNT_MONTHS={source_evidence['low_daily_count_months_count']}")
    print(f"V5_SOURCE_LEVEL_CORR={source_evidence['level_corr']:.12f}")
    print(f"V5_SOURCE_MEDIAN_GAP_BPS={source_evidence['median_abs_gap_bps']:.9f}")
    print(f"V5_SOURCE_P95_GAP_BPS={source_evidence['p95_abs_gap_bps']:.9f}")
    print(f"V5_SOURCE_RETURN_CORR={source_evidence['monthly_return_corr']:.12f}")
    print(f"V5_SOURCE_SIGN_AGREE={source_evidence['monthly_return_sign_agree']:.9f}")
    print(f"V5_SOURCE_BRIDGE_PASS={str(source_evidence['source_bridge_pass']).lower()}")
    print(f"V5_SOURCE_DECISION={source_evidence['decision']}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")

    if not source_evidence["source_bridge_pass"]:
        fail = {
            "candidate_id": IDENTITY,
            "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
            "prospective_claim": False,
            "source_gate": source_evidence["decision"],
            "model_impact_run": "SKIPPED_SOURCE_GATE_FAIL",
            "model_impact_pass": False,
            "decision": MODEL_FAIL_ID,
            "post_result_retune": False,
            "forecast_ledger_write": "NONE",
            "decision_store_write": "NONE",
            "database_write": "NONE",
            "raw_vendor_market_values_logged": False,
        }
        (OUT / "locked_replay_v5_monthly_level_evidence.json").write_text(
            json.dumps(fail, indent=2), encoding="utf-8"
        )
        print("V5_MODEL_IMPACT_SKIPPED_SOURCE_GATE_FAIL")
        print(f"V5_DECISION={MODEL_FAIL_ID}")
        return 2

    xau_daily = fetch_xau_daily(session)
    nasdaq = fetch_nasdaq_monthly(session)
    first, fv1 = locked_predictions(core, xau_daily, nasdaq, monthly_level)
    second, fv2 = locked_predictions(core, xau_daily, nasdaq, monthly_level)
    max_diff = float(np.max(np.abs(first.patch_v5.to_numpy() - second.patch_v5.to_numpy())))

    reference = pd.read_csv(ROOT / "production_closure" / "production_history_43.csv")
    if len(reference) != 43:
        raise RuntimeError("V5_REFERENCE_N_NOT_43")
    joined = reference.merge(first, on="month", how="inner")
    if len(joined) != 43:
        raise RuntimeError(f"V5_COMMON_N_NOT_43:{len(joined)}")

    target_ok = 0
    rw_ok = 0
    for _, row in joined.iterrows():
        target = pd.Timestamp(row["month"] + "-01")
        previous = target - pd.offsets.MonthBegin(1)
        target_ok += int(abs(float(core.loc[target, "gold_monthly"]) - float(row["actual"])) <= 1e-9)
        rw_ok += int(abs(float(core.loc[previous, "gold_monthly"]) - float(row["rw"])) <= 1e-9)

    candidate_metrics = metrics(joined.actual, joined.patch_v5)
    rw_metrics = metrics(joined.actual, joined.rw)
    v4_metrics = metrics(joined.actual, joined.patch_v4 if "patch_v4" in joined.columns else joined.patch_r1)

    hard_gate = bool(target_ok == 43 and rw_ok == 43 and max_diff <= 1e-8 and fv1 == 0 and fv2 == 0)
    performance_gate = bool(
        candidate_metrics["MAPE_pct"] < rw_metrics["MAPE_pct"]
        and candidate_metrics["MAE"] < rw_metrics["MAE"]
        and candidate_metrics["worst_APE_pct"] <= 1.25 * rw_metrics["worst_APE_pct"]
    )
    passed = bool(hard_gate and performance_gate)
    decision = MODEL_PASS_ID if passed else MODEL_FAIL_ID

    joined["patch_v5_ape"] = np.abs(joined.patch_v5 - joined.actual) / joined.actual * 100.0
    joined.to_csv(OUT / "locked_replay_v5_monthly_level_43.csv", index=False)
    evidence = {
        "candidate_id": IDENTITY,
        "parent_candidate_id": "CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE",
        "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
        "prospective_claim": False,
        "source_gate": SOURCE_PASS_ID,
        "monthly_level_series_id": "PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V5",
        "geometry": {"L": L, "P": P, "D": D},
        "geometry_reselected": False,
        "locked_window": "2023-01..2026-07",
        "N": 43,
        "target_reconciliation": f"{target_ok}/43",
        "rw_reconciliation": f"{rw_ok}/43",
        "future_information_violations": int(fv1 + fv2),
        "deterministic_max_abs_diff": max_diff,
        "candidate_metrics": candidate_metrics,
        "rw_metrics": rw_metrics,
        "reference_metrics_for_context_only": v4_metrics,
        "worst_ape_ratio_vs_rw": float(candidate_metrics["worst_APE_pct"] / rw_metrics["worst_APE_pct"]),
        "hard_gate_pass": hard_gate,
        "performance_gate_pass": performance_gate,
        "model_impact_pass": passed,
        "decision": decision,
        "post_result_retune": False,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "database_write": "NONE",
        "raw_vendor_market_values_logged": False,
    }
    (OUT / "locked_replay_v5_monthly_level_evidence.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )

    print(f"V5_TARGET_RECONCILIATION={target_ok}/43")
    print(f"V5_RW_RECONCILIATION={rw_ok}/43")
    print(f"V5_DETERMINISTIC_MAX_ABS_DIFF={max_diff:.12g}")
    print(f"V5_FUTURE_INFORMATION_VIOLATIONS={fv1 + fv2}")
    print(f"V5_MAPE_PCT={candidate_metrics['MAPE_pct']:.9f}")
    print(f"RW_MAPE_PCT={rw_metrics['MAPE_pct']:.9f}")
    print(f"V5_MAE={candidate_metrics['MAE']:.9f}")
    print(f"RW_MAE={rw_metrics['MAE']:.9f}")
    print(f"V5_WORST_APE_PCT={candidate_metrics['worst_APE_pct']:.9f}")
    print(f"RW_WORST_APE_PCT={rw_metrics['worst_APE_pct']:.9f}")
    print(f"V5_WORST_APE_RATIO_VS_RW={evidence['worst_ape_ratio_vs_rw']:.9f}")
    print(f"V5_HARD_GATE_PASS={str(hard_gate).lower()}")
    print(f"V5_PERFORMANCE_GATE_PASS={str(performance_gate).lower()}")
    print(f"V5_MODEL_IMPACT_PASS={str(passed).lower()}")
    print(f"V5_DECISION={decision}")
    print("GEOMETRY_RESELECTED=NO")
    print("POST_RESULT_RETUNE=NO")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
