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
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_MONTHLY_LEVEL_INPUT_CHANGE_CONTROL_V6_2026-09-02.md"
IDENTITY = "CAUSAL_PATCH_R1_REPRO_V1_5_DAILY_TRAIN_HOURLY_ANCHOR_ORIGIN_SAFE"
SOURCE_PASS_ID = "PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS"
SOURCE_FAIL_ID = "BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_NOT_PROVEN"
MODEL_PASS_ID = "PATCH_R1_V6_MONTHLY_LEVEL_MODEL_IMPACT_PASS"
MODEL_FAIL_ID = "PATCH_R1_V6_MONTHLY_LEVEL_MODEL_IMPACT_FAIL_NO_RETUNE"
SEED = 20260902
L, P, D = 252, 21, 32
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")
TRAIN_LEVEL_START = pd.Timestamp("2011-02-01")
TRAIN_LEVEL_END = pd.Timestamp("2026-07-01")
ANCHOR_START = pd.Timestamp("2022-12-01")
ANCHOR_END = pd.Timestamp("2026-06-01")
TWELVE_URL = "https://api.twelvedata.com/time_series"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

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
    raw = gzip.decompress(base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip())).decode()
    return pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()


def request_json(session: requests.Session, url: str, *, params: dict, headers: dict | None = None, attempts: int = 6) -> dict:
    last_type = "UNKNOWN"
    last_status = None
    last_code = None
    for attempt in range(attempts):
        try:
            response = session.get(url, params=params, headers=headers or {}, timeout=(20, 180))
            last_status = int(response.status_code)
            try:
                payload = response.json()
            except Exception:
                payload = None
            if isinstance(payload, dict):
                last_code = payload.get("code")
            if response.status_code == 429 or last_code == 429:
                last_type = "RATE_LIMIT"
                time.sleep(65)
                continue
            response.raise_for_status()
            if not isinstance(payload, dict):
                raise RuntimeError("PROVIDER_RESPONSE_NOT_DICT")
            if payload.get("status") == "error":
                raise RuntimeError(f"PROVIDER_ERROR_CODE_{payload.get('code')}")
            return payload
        except Exception as exc:
            last_type = type(exc).__name__
            if attempt + 1 < attempts:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{last_type}:HTTP_{last_status}:API_{last_code}")


def fetch_xau_daily(session: requests.Session) -> pd.DataFrame:
    payload = request_json(
        session,
        TWELVE_URL,
        params={
            "symbol": "XAU/USD", "interval": "1day", "start_date": "2010-01-01",
            "end_date": "2026-08-31", "outputsize": 5000, "order": "ASC", "format": "JSON",
        },
        headers={"Authorization": f"apikey {env_key('TWELVE_DATA_API_KEY')}", "User-Agent": "Gold-Control-Patch-V6/1.0"},
    )
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1day":
        raise RuntimeError("V6_DAILY_META_MISMATCH")
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
        raise RuntimeError("V6_DAILY_HISTORY_INVALID")
    return frame.set_index("date")


def daily_monthly_levels(xau_daily: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    level = xau_daily["Gold"].resample("MS").mean().dropna()
    count = xau_daily["Gold"].resample("MS").count().astype(int)
    return level, count


def fetch_hourly_anchor_levels(session: requests.Session) -> tuple[pd.Series, pd.Series, dict]:
    api_key = env_key("TWELVE_DATA_API_KEY")
    selected: dict[pd.Timestamp, float] = {}
    cursor = pd.Timestamp("2022-12-01")
    final = pd.Timestamp("2026-06-30 23:59:59")
    request_count = 0
    while cursor <= final:
        end = min(cursor + pd.DateOffset(months=6) - pd.Timedelta(seconds=1), final)
        try:
            payload = request_json(
                session,
                TWELVE_URL,
                params={
                    "symbol": "XAU/USD", "interval": "1h",
                    "start_date": cursor.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
                    "timezone": "America/New_York", "outputsize": 5000,
                    "order": "ASC", "format": "JSON",
                },
                headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Patch-V6-Anchor/1.0"},
            )
        except Exception as exc:
            raise RuntimeError(
                f"V6_HOURLY_WINDOW_UNAVAILABLE:{cursor.strftime('%Y-%m')}..{end.strftime('%Y-%m')}:{exc}"
            ) from exc
        request_count += 1
        meta = payload.get("meta") or {}
        if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
            raise RuntimeError("V6_HOURLY_META_MISMATCH")
        for item in payload.get("values") or []:
            text = str(item.get("datetime", ""))
            if not text.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(text)
                value = float(item.get("close"))
            except Exception:
                continue
            if not (np.isfinite(value) and value > 0):
                continue
            date = ts.normalize()
            if date in selected:
                raise RuntimeError(f"V6_DUPLICATE_ANCHOR_DAILY_DATE:{date.date()}")
            selected[date] = value
        cursor = (end + pd.Timedelta(seconds=1)).normalize()
        time.sleep(8)
    if not selected:
        raise RuntimeError("V6_HOURLY_ANCHOR_EMPTY")
    daily = pd.Series(selected).sort_index()
    level = daily.resample("MS").mean().dropna()
    count = daily.resample("MS").count().astype(int)
    return level, count, {
        "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1h",
        "requested_timezone": "America/New_York", "selected_bar_open_time": "16:00:00",
        "selected_bar_end_semantic": "17:00_ET_HOURLY_CLOSE", "request_count": request_count,
        "selected_daily_observation_count": int(len(daily)),
        "first_selected_date": daily.index.min().date().isoformat(),
        "last_selected_date": daily.index.max().date().isoformat(),
    }


def bridge_metrics(reference: pd.Series, candidate: pd.Series, months: pd.DatetimeIndex) -> dict:
    common = [m for m in months if m in reference.index and m in candidate.index]
    if len(common) < 2:
        raise RuntimeError("V6_BRIDGE_COMMON_MONTHS_INSUFFICIENT")
    a = np.array([float(reference.loc[m]) for m in common], float)
    b = np.array([float(candidate.loc[m]) for m in common], float)
    rel_bps = np.abs(b - a) / np.abs(a) * 10000.0
    ar = np.diff(np.log(a))
    br = np.diff(np.log(b))
    return {
        "common_months": len(common),
        "level_corr": float(np.corrcoef(a, b)[0, 1]),
        "median_abs_gap_bps": float(np.median(rel_bps)),
        "p95_abs_gap_bps": float(np.quantile(rel_bps, 0.95)),
        "monthly_return_corr": float(np.corrcoef(ar, br)[0, 1]),
        "monthly_return_sign_agree": float(np.mean(np.sign(ar) == np.sign(br))),
    }


def metrics_pass(m: dict) -> bool:
    return bool(
        m["level_corr"] >= LEVEL_CORR_MIN
        and m["median_abs_gap_bps"] <= MEDIAN_GAP_BPS_MAX
        and m["p95_abs_gap_bps"] <= P95_GAP_BPS_MAX
        and m["monthly_return_corr"] >= RETURN_CORR_MIN
        and m["monthly_return_sign_agree"] >= SIGN_AGREE_MIN
    )


def source_audit(core: pd.DataFrame, daily_level: pd.Series, daily_count: pd.Series, hourly_level: pd.Series, hourly_count: pd.Series, hourly_stats: dict) -> dict:
    train_months = core.loc[TRAIN_LEVEL_START:TRAIN_LEVEL_END, "gold_monthly"].dropna().index
    anchor_months = pd.date_range(ANCHOR_START, ANCHOR_END, freq="MS")
    train_missing = [m.strftime("%Y-%m") for m in train_months if m not in daily_level.index]
    train_low = [m.strftime("%Y-%m") for m in train_months if m in daily_count.index and int(daily_count.loc[m]) < MIN_DAILY_PER_MONTH]
    anchor_missing = [m.strftime("%Y-%m") for m in anchor_months if m not in hourly_level.index]
    anchor_low = [m.strftime("%Y-%m") for m in anchor_months if m in hourly_count.index and int(hourly_count.loc[m]) < MIN_DAILY_PER_MONTH]

    core_gold = core["gold_monthly"].astype(float)
    train_bridge = bridge_metrics(core_gold, daily_level, pd.DatetimeIndex(train_months))
    anchor_bridge = bridge_metrics(daily_level, hourly_level, anchor_months)
    train_coverage = len(train_missing) == 0 and len(train_low) == 0 and train_bridge["common_months"] == len(train_months)
    anchor_coverage = len(anchor_missing) == 0 and len(anchor_low) == 0 and anchor_bridge["common_months"] == len(anchor_months)
    passed = bool(train_coverage and anchor_coverage and metrics_pass(train_bridge) and metrics_pass(anchor_bridge))
    return {
        "candidate_id": IDENTITY,
        "evidence_class": "SOURCE_INPUT_SEMANTIC_AUDIT",
        "prospective_claim": False,
        "daily_training_series_id": "PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN",
        "hourly_anchor_series_id": "PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR",
        "daily_training_required_months": len(train_months),
        "daily_training_missing_months": len(train_missing),
        "daily_training_low_count_months": len(train_low),
        "hourly_anchor_required_months": len(anchor_months),
        "hourly_anchor_missing_months": len(anchor_missing),
        "hourly_anchor_low_count_months": len(anchor_low),
        "minimum_daily_observations_per_month": MIN_DAILY_PER_MONTH,
        "daily_training_vs_core5": train_bridge,
        "hourly_anchor_vs_daily_training": anchor_bridge,
        "hourly_source_semantic": hourly_stats,
        "frozen_gates": {
            "level_corr_min": LEVEL_CORR_MIN, "median_gap_bps_max": MEDIAN_GAP_BPS_MAX,
            "p95_gap_bps_max": P95_GAP_BPS_MAX, "return_corr_min": RETURN_CORR_MIN,
            "sign_agree_min": SIGN_AGREE_MIN,
        },
        "daily_training_coverage_pass": train_coverage,
        "hourly_anchor_coverage_pass": anchor_coverage,
        "daily_training_materiality_pass": metrics_pass(train_bridge),
        "hourly_anchor_materiality_pass": metrics_pass(anchor_bridge),
        "source_bridge_pass": passed,
        "decision": SOURCE_PASS_ID if passed else SOURCE_FAIL_ID,
        "thresholds_relaxed": False, "post_result_source_substitution": False,
        "raw_vendor_market_values_logged": False, "database_write": "NONE",
        "forecast_ledger_write": "NONE", "decision_store_write": "NONE",
    }


def fetch_nasdaq_monthly(session: requests.Session) -> pd.Series:
    payload = request_json(
        session, FRED_URL,
        params={"series_id": "NASDAQCOM", "api_key": env_key("FRED_API_KEY"), "file_type": "json", "observation_start": "2010-01-01", "observation_end": "2026-08-31", "sort_order": "asc", "limit": 100000},
        headers={"User-Agent": "Gold-Control-Patch-V6/1.0"},
    )
    rows = []
    for item in payload.get("observations") or []:
        raw = str(item.get("value", "."))
        if raw in {".", "", "nan", "None"}:
            continue
        try:
            date = pd.Timestamp(str(item.get("date"))).normalize(); value = float(raw)
        except Exception:
            continue
        if np.isfinite(value) and value > 0:
            rows.append((date, value))
    frame = pd.DataFrame(rows, columns=["date", "value"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("V6_NASDAQ_HISTORY_INVALID")
    return frame.set_index("date")["value"].resample("MS").mean().dropna()


def gpr_z_asof(core: pd.DataFrame, asof_month: pd.Timestamp) -> float:
    history = core.loc[:asof_month, "gpr"].dropna().astype(float)
    if history.empty:
        return 0.5
    lo, hi = float(history.min()), float(history.max())
    return 0.5 if hi <= lo else float((history.iloc[-1] - lo) / (hi - lo))


def causal_decomp(values: np.ndarray, win: int = 21) -> np.ndarray:
    trend = np.zeros_like(values)
    for i in range(len(values)):
        trend[i] = values[max(0, i - win + 1): i + 1].mean(0)
    return np.concatenate([trend, values - trend], axis=1)


class PatchTransformer(nn.Module):
    def __init__(self, channels: int, patch: int, d_model: int):
        super().__init__(); self.patch = patch; self.stride = max(1, patch // 2)
        self.emb = nn.Linear(patch * channels, d_model)
        layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=4, dim_feedforward=4*d_model, dropout=0.10, batch_first=True, activation="gelu", norm_first=True)
        self.enc = nn.TransformerEncoder(layer, 2); self.conv = nn.Conv1d(d_model, d_model, 3, padding=1)
        self.head = nn.Sequential(nn.Linear(d_model + 5, 64), nn.GELU(), nn.Dropout(0.10), nn.Linear(64, 1))
    def forward(self, x, macro):
        patches = x.unfold(1, self.patch, self.stride).permute(0,1,3,2).contiguous().flatten(2)
        z = self.enc(self.emb(patches)); z = self.conv(z.transpose(1,2)).transpose(1,2).mean(1)
        return self.head(torch.cat([z, macro], 1)).squeeze(1)


def feature_sample(target: pd.Timestamp, xau_daily: pd.DataFrame, core: pd.DataFrame, nas_monthly: pd.Series) -> tuple[pd.Timestamp, np.ndarray, np.ndarray]:
    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    p = target - pd.offsets.MonthBegin(1); pp = p - pd.offsets.MonthBegin(1); ppp = p - pd.offsets.MonthBegin(2)
    if any(q not in core.index for q in [p, pp]) or pp not in nas_monthly.index or ppp not in nas_monthly.index:
        raise RuntimeError(f"V6_FEATURE_MONTH_MISSING:{target.date()}")
    origin_end = target - pd.Timedelta(days=1)
    history = daily_returns.loc[:origin_end]
    if len(history) < L or history.index.max() > origin_end:
        raise RuntimeError(f"V6_DAILY_FEATURE_HISTORY_INVALID:{target.date()}")
    x = causal_decomp(history.iloc[-L:].values.astype(np.float32), 21).astype(np.float32)
    nasdaq = float(np.log(float(nas_monthly.loc[pp]) / float(nas_monthly.loc[ppp])))
    fx = float(np.log(float(core.loc[p, "usdcny"]) / float(core.loc[pp, "usdcny"])))
    gpr = float(core.loc[pp, "gpr"])
    macro = np.array([float(core.loc[p, "fedfunds"]), nasdaq, fx, np.log1p(gpr), gpr_z_asof(core, pp)], dtype=np.float32)
    return target, x, macro


def training_samples(xau_daily: pd.DataFrame, daily_level: pd.Series, core: pd.DataFrame, nas_monthly: pd.Series) -> list[tuple]:
    samples = []
    for target in sorted(core.index):
        if target < pd.Timestamp("2011-03-01") or target > LOCKED_END:
            continue
        p = target - pd.offsets.MonthBegin(1)
        if target not in daily_level.index or p not in daily_level.index:
            continue
        try:
            _, x, macro = feature_sample(target, xau_daily, core, nas_monthly)
        except RuntimeError:
            continue
        y = float(np.log(float(daily_level.loc[target]) / float(daily_level.loc[p])))
        samples.append((target, x, macro, y))
    return samples


def normalize_sets(train, valid):
    x = np.stack([s[1] for s in train]); m = np.stack([s[2] for s in train]); y = np.array([s[3] for s in train], np.float32)
    xm = x.reshape(-1, x.shape[-1]).mean(0); xs = x.reshape(-1, x.shape[-1]).std(0) + 1e-6
    mm = m.mean(0); ms = m.std(0) + 1e-6; ym = float(y.mean()); ys = float(y.std() + 1e-6)
    def tr(s): return ((s[1]-xm)/xs, (s[2]-mm)/ms, np.float32((s[3]-ym)/ys))
    return [tr(s) for s in train], [tr(s) for s in valid], (xm,xs,mm,ms,ym,ys)


def fit_patch(train, valid, seed, epochs=140):
    seed_all(seed); a,b,scale = normalize_sets(train,valid)
    x=torch.tensor(np.stack([z[0] for z in a]),dtype=torch.float32); m=torch.tensor(np.stack([z[1] for z in a]),dtype=torch.float32); y=torch.tensor(np.array([z[2] for z in a]),dtype=torch.float32)
    model=PatchTransformer(x.shape[-1],P,D); opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4); loss_fn=nn.HuberLoss(); best=None; best_v=1e99; bad=0
    for _ in range(epochs):
        model.train(); order=torch.randperm(len(x))
        for k in range(0,len(x),32):
            idx=order[k:k+32]; opt.zero_grad(); loss=loss_fn(model(x[idx],m[idx]),y[idx]); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        if b:
            model.eval(); vx=torch.tensor(np.stack([z[0] for z in b]),dtype=torch.float32); vm=torch.tensor(np.stack([z[1] for z in b]),dtype=torch.float32); vy=torch.tensor(np.array([z[2] for z in b]),dtype=torch.float32)
            with torch.no_grad(): score=float(torch.mean(torch.abs(model(vx,vm)-vy)))
            if score < best_v-1e-5: best_v=score; best={key:value.detach().clone() for key,value in model.state_dict().items()}; bad=0
            else:
                bad += 1
                if bad >= 24: break
    if best: model.load_state_dict(best)
    return model, scale


def predict(model, scale, xraw, mraw):
    xm,xs,mm,ms,ym,ys=scale; x=((xraw-xm)/xs).astype(np.float32); m=((mraw-mm)/ms).astype(np.float32); model.eval()
    with torch.no_grad(): normalized=float(model(torch.tensor(x[None]),torch.tensor(m[None])).item())
    return normalized*ys+ym


def locked_predictions(core, xau_daily, nas_monthly, daily_level, hourly_anchor):
    samples = training_samples(xau_daily,daily_level,core,nas_monthly); output=[]; future_violations=0
    for target in pd.date_range(LOCKED_START,LOCKED_END,freq="MS"):
        p = target - pd.offsets.MonthBegin(1)
        all_train = [s for s in samples if s[0] < p]
        _, test_x, test_macro = feature_sample(target,xau_daily,core,nas_monthly)
        if p not in hourly_anchor.index: raise RuntimeError(f"V6_ANCHOR_MISSING:{p.date()}")
        cut=max(48,int(len(all_train)*0.85)); cut=min(cut,len(all_train)-12); train,valid=all_train[:cut],all_train[cut:]
        if len(train)<48 or len(valid)<12: raise RuntimeError(f"V6_TRAIN_VALID_INVALID:{target.date()}:{len(train)}:{len(valid)}")
        reps=[]
        for offset in [0,101,202]:
            model,scale=fit_patch(train,valid,SEED+offset+int(target.strftime("%Y%m")),140); reps.append(predict(model,scale,test_x,test_macro))
        predicted_return=float(np.median(reps)); forecast=float(hourly_anchor.loc[p])*math.exp(predicted_return)
        output.append((target.strftime("%Y-%m"),forecast,predicted_return,len(all_train)))
    return pd.DataFrame(output,columns=["month","patch_v6","predicted_log_return","training_sample_count"]), future_violations


def error_metrics(actual,pred):
    a=np.asarray(actual,float); p=np.asarray(pred,float); e=p-a; ape=np.abs(e)/a*100
    return {"MAE":float(np.mean(np.abs(e))),"MAPE_pct":float(np.mean(ape)),"median_APE_pct":float(np.median(ape)),"worst_APE_pct":float(np.max(ape)),"RMSE":float(np.sqrt(np.mean(e*e)))}


def write_fail(reason: str) -> int:
    source={"candidate_id":IDENTITY,"evidence_class":"SOURCE_INPUT_SEMANTIC_AUDIT","prospective_claim":False,"source_bridge_pass":False,"decision":SOURCE_FAIL_ID,"failure_reason":reason,"thresholds_relaxed":False,"post_result_source_substitution":False,"raw_vendor_market_values_logged":False,"database_write":"NONE","forecast_ledger_write":"NONE","decision_store_write":"NONE"}
    model={"candidate_id":IDENTITY,"evidence_class":"HISTORICAL_REPLAY_MODEL_IMPACT","prospective_claim":False,"source_gate":SOURCE_FAIL_ID,"model_impact_run":"SKIPPED_SOURCE_GATE_NOT_PROVEN","model_impact_pass":False,"decision":MODEL_FAIL_ID,"post_result_retune":False,"raw_vendor_market_values_logged":False,"database_write":"NONE","forecast_ledger_write":"NONE","decision_store_write":"NONE"}
    (OUT/"prospective_monthly_level_v6_source_evidence.json").write_text(json.dumps(source,indent=2),encoding="utf-8"); (OUT/"locked_replay_v6_monthly_level_evidence.json").write_text(json.dumps(model,indent=2),encoding="utf-8")
    print(f"V6_SOURCE_DECISION={SOURCE_FAIL_ID}"); print(f"V6_MODEL_IMPACT=SKIPPED_SOURCE_GATE_NOT_PROVEN"); print("THRESHOLDS_RELAXED=NO"); print("POST_RESULT_SOURCE_SUBSTITUTION=NO"); print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO"); print("DATABASE_WRITES=NONE"); print("FORECAST_LEDGER_WRITE=NONE"); print("DECISION_STORE_WRITE=NONE")
    return 2


def main() -> int:
    text=CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_V6_SOURCE_RESULT" not in text or IDENTITY not in text: raise RuntimeError("V6_CONTRACT_NOT_FROZEN")
    geometry=json.loads((OUT/"frozen_geometry.json").read_text(encoding="utf-8"))["selected_pre_2023_geometry"]
    if (int(geometry["L"]),int(geometry["P"]),int(geometry["D"])) != (L,P,D): raise RuntimeError("V6_GEOMETRY_MISMATCH")
    core=load_core(); session=requests.Session(); session.headers.update({"User-Agent":"Gold-Control-Patch-V6/1.0"})
    try:
        xau_daily=fetch_xau_daily(session); daily_level,daily_count=daily_monthly_levels(xau_daily); hourly_anchor,hourly_count,hourly_stats=fetch_hourly_anchor_levels(session)
        source=source_audit(core,daily_level,daily_count,hourly_anchor,hourly_count,hourly_stats)
    except Exception as exc:
        return write_fail(str(exc)[:500])
    (OUT/"prospective_monthly_level_v6_source_evidence.json").write_text(json.dumps(source,indent=2),encoding="utf-8")
    print(f"V6_DAILY_REQUIRED_MONTHS={source['daily_training_required_months']}"); print(f"V6_DAILY_MISSING_MONTHS={source['daily_training_missing_months']}"); print(f"V6_DAILY_LOW_COUNT_MONTHS={source['daily_training_low_count_months']}")
    print(f"V6_DAILY_LEVEL_CORR={source['daily_training_vs_core5']['level_corr']:.12f}"); print(f"V6_DAILY_MEDIAN_GAP_BPS={source['daily_training_vs_core5']['median_abs_gap_bps']:.9f}"); print(f"V6_DAILY_P95_GAP_BPS={source['daily_training_vs_core5']['p95_abs_gap_bps']:.9f}"); print(f"V6_DAILY_RETURN_CORR={source['daily_training_vs_core5']['monthly_return_corr']:.12f}"); print(f"V6_DAILY_SIGN_AGREE={source['daily_training_vs_core5']['monthly_return_sign_agree']:.9f}")
    print(f"V6_ANCHOR_REQUIRED_MONTHS={source['hourly_anchor_required_months']}"); print(f"V6_ANCHOR_MISSING_MONTHS={source['hourly_anchor_missing_months']}"); print(f"V6_ANCHOR_LOW_COUNT_MONTHS={source['hourly_anchor_low_count_months']}")
    print(f"V6_ANCHOR_LEVEL_CORR={source['hourly_anchor_vs_daily_training']['level_corr']:.12f}"); print(f"V6_ANCHOR_MEDIAN_GAP_BPS={source['hourly_anchor_vs_daily_training']['median_abs_gap_bps']:.9f}"); print(f"V6_ANCHOR_P95_GAP_BPS={source['hourly_anchor_vs_daily_training']['p95_abs_gap_bps']:.9f}"); print(f"V6_ANCHOR_RETURN_CORR={source['hourly_anchor_vs_daily_training']['monthly_return_corr']:.12f}"); print(f"V6_ANCHOR_SIGN_AGREE={source['hourly_anchor_vs_daily_training']['monthly_return_sign_agree']:.9f}"); print(f"V6_SOURCE_BRIDGE_PASS={str(source['source_bridge_pass']).lower()}"); print(f"V6_SOURCE_DECISION={source['decision']}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO"); print("DATABASE_WRITES=NONE"); print("FORECAST_LEDGER_WRITE=NONE"); print("DECISION_STORE_WRITE=NONE")
    if not source["source_bridge_pass"]:
        model={"candidate_id":IDENTITY,"evidence_class":"HISTORICAL_REPLAY_MODEL_IMPACT","prospective_claim":False,"source_gate":source["decision"],"model_impact_run":"SKIPPED_SOURCE_GATE_FAIL","model_impact_pass":False,"decision":MODEL_FAIL_ID,"post_result_retune":False,"raw_vendor_market_values_logged":False,"database_write":"NONE","forecast_ledger_write":"NONE","decision_store_write":"NONE"}
        (OUT/"locked_replay_v6_monthly_level_evidence.json").write_text(json.dumps(model,indent=2),encoding="utf-8"); print("V6_MODEL_IMPACT_SKIPPED_SOURCE_GATE_FAIL"); print(f"V6_DECISION={MODEL_FAIL_ID}"); return 2
    nasdaq=fetch_nasdaq_monthly(session); first,fv1=locked_predictions(core,xau_daily,nasdaq,daily_level,hourly_anchor); second,fv2=locked_predictions(core,xau_daily,nasdaq,daily_level,hourly_anchor)
    maxdiff=float(np.max(np.abs(first.patch_v6.to_numpy()-second.patch_v6.to_numpy()))); reference=pd.read_csv(ROOT/"production_closure"/"production_history_43.csv")
    joined=reference.merge(first,on="month",how="inner");
    if len(reference)!=43 or len(joined)!=43: raise RuntimeError(f"V6_REFERENCE_RECONCILIATION_FAIL:{len(reference)}:{len(joined)}")
    target_ok=0; rw_ok=0
    for _,row in joined.iterrows():
        target=pd.Timestamp(row["month"]+"-01"); previous=target-pd.offsets.MonthBegin(1); target_ok+=int(abs(float(core.loc[target,"gold_monthly"])-float(row["actual"]))<=1e-9); rw_ok+=int(abs(float(core.loc[previous,"gold_monthly"])-float(row["rw"]))<=1e-9)
    candidate=error_metrics(joined.actual,joined.patch_v6); rw=error_metrics(joined.actual,joined.rw); hard=bool(target_ok==43 and rw_ok==43 and maxdiff<=1e-8 and fv1+fv2==0); perf=bool(candidate["MAPE_pct"]<rw["MAPE_pct"] and candidate["MAE"]<rw["MAE"] and candidate["worst_APE_pct"]<=1.25*rw["worst_APE_pct"]); passed=bool(hard and perf); decision=MODEL_PASS_ID if passed else MODEL_FAIL_ID
    joined["patch_v6_ape"]=np.abs(joined.patch_v6-joined.actual)/joined.actual*100; joined.to_csv(OUT/"locked_replay_v6_monthly_level_43.csv",index=False)
    evidence={"candidate_id":IDENTITY,"parent_candidate_id":"CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE","evidence_class":"HISTORICAL_REPLAY_MODEL_IMPACT","prospective_claim":False,"source_gate":SOURCE_PASS_ID,"daily_training_series_id":"PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN","hourly_anchor_series_id":"PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR","training_target_lag_months":1,"geometry":{"L":L,"P":P,"D":D},"geometry_reselected":False,"locked_window":"2023-01..2026-07","N":43,"target_reconciliation":f"{target_ok}/43","rw_reconciliation":f"{rw_ok}/43","future_information_violations":int(fv1+fv2),"deterministic_max_abs_diff":maxdiff,"candidate_metrics":candidate,"rw_metrics":rw,"worst_ape_ratio_vs_rw":float(candidate["worst_APE_pct"]/rw["worst_APE_pct"]),"hard_gate_pass":hard,"performance_gate_pass":perf,"model_impact_pass":passed,"decision":decision,"post_result_retune":False,"raw_vendor_market_values_logged":False,"database_write":"NONE","forecast_ledger_write":"NONE","decision_store_write":"NONE"}
    (OUT/"locked_replay_v6_monthly_level_evidence.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
    print(f"V6_TARGET_RECONCILIATION={target_ok}/43"); print(f"V6_RW_RECONCILIATION={rw_ok}/43"); print(f"V6_DETERMINISTIC_MAX_ABS_DIFF={maxdiff:.12g}"); print(f"V6_FUTURE_INFORMATION_VIOLATIONS={fv1+fv2}"); print(f"V6_MAPE_PCT={candidate['MAPE_pct']:.9f}"); print(f"RW_MAPE_PCT={rw['MAPE_pct']:.9f}"); print(f"V6_MAE={candidate['MAE']:.9f}"); print(f"RW_MAE={rw['MAE']:.9f}"); print(f"V6_WORST_APE_PCT={candidate['worst_APE_pct']:.9f}"); print(f"RW_WORST_APE_PCT={rw['worst_APE_pct']:.9f}"); print(f"V6_WORST_APE_RATIO_VS_RW={evidence['worst_ape_ratio_vs_rw']:.9f}"); print(f"V6_HARD_GATE_PASS={str(hard).lower()}"); print(f"V6_PERFORMANCE_GATE_PASS={str(perf).lower()}"); print(f"V6_MODEL_IMPACT_PASS={str(passed).lower()}"); print(f"V6_DECISION={decision}"); print("GEOMETRY_RESELECTED=NO"); print("POST_RESULT_RETUNE=NO"); print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO"); print("DATABASE_WRITES=NONE"); print("FORECAST_LEDGER_WRITE=NONE"); print("DECISION_STORE_WRITE=NONE")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
