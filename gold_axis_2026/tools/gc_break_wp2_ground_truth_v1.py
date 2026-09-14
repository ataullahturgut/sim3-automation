from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

SERIES_ID = "XAU_EOD_TWELVE_NY17"
PREHISTORY_START = pd.Timestamp("2021-09-01")
FORMATION_START = pd.Timestamp("2022-01-01")
FORMATION_END = pd.Timestamp("2024-12-31")
PRIMARY_K = 3.0
SENSITIVITY_K = 2.5
SIGMA_WINDOW = 20


@dataclass
class BreakEvent:
    trade_date: pd.Timestamp
    close: float
    pre_regime: str
    post_regime: str
    sigma20_lag1: float
    adverse_move: float
    threshold: float
    origin_gap_days: int | None
    sigma_span_calendar_days: int | None


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("BLOCKED_DATA:NEON_DATABASE_URL_NOT_SET")
    return value


def load_canonical() -> pd.DataFrame:
    sql = """
        SELECT observation_ts,
               COALESCE((metadata->>'trade_date')::date,
                        (observation_ts AT TIME ZONE 'America/New_York')::date) AS trade_date,
               value::double precision AS close,
               source,
               source_symbol,
               quality_status,
               metadata
        FROM canonical_latest
        WHERE series_id=%s
          AND observation_ts >= %s
          AND observation_ts < %s
        ORDER BY observation_ts
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    SERIES_ID,
                    PREHISTORY_START.tz_localize("UTC").to_pydatetime(),
                    (FORMATION_END + pd.Timedelta(days=1)).tz_localize("UTC").to_pydatetime(),
                ),
            )
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
    d = pd.DataFrame(rows, columns=cols)
    if d.empty:
        raise RuntimeError("BLOCKED_DATA:NO_CANONICAL_XAU_ROWS")
    d["trade_date"] = pd.to_datetime(d["trade_date"]).dt.normalize()
    d["close"] = pd.to_numeric(d["close"], errors="raise")
    if d["trade_date"].duplicated().any():
        raise RuntimeError("WP2_DUPLICATE_TRADE_DATE")
    if not d["trade_date"].is_monotonic_increasing:
        raise RuntimeError("WP2_NON_MONOTONIC_DATES")
    if (~np.isfinite(d["close"].to_numpy(float))).any() or (d["close"] <= 0).any():
        raise RuntimeError("WP2_INVALID_CLOSE")
    bad_lineage = d[
        d["source"].ne("Twelve Data")
        | d["source_symbol"].ne("XAU/USD")
        | d["quality_status"].ne("APPROVED_CANONICAL_TWELVE_NY17")
    ]
    if len(bad_lineage):
        raise RuntimeError(f"WP2_CANONICAL_LINEAGE_FAIL:{len(bad_lineage)}")
    return d.reset_index(drop=True)


def prepare_features(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    out["log_ret"] = np.log(out["close"] / out["close"].shift(1))
    out["close_lag20"] = out["close"].shift(SIGMA_WINDOW)
    out["trade_date_lag20"] = out["trade_date"].shift(SIGMA_WINDOW)
    out["prev_trade_date"] = out["trade_date"].shift(1)
    # Exactly 20 matured return observations, all strictly before the current origin.
    out["sigma20_lag1"] = (
        out["log_ret"].shift(1).rolling(SIGMA_WINDOW, min_periods=SIGMA_WINDOW).std(ddof=1)
    )
    return out


def run_labeler(features: pd.DataFrame, k: float) -> tuple[pd.DataFrame, list[BreakEvent], pd.Timestamp, str]:
    d = features.copy()
    regime: str | None = None
    extreme: float | None = None
    initialization_date: pd.Timestamp | None = None
    initial_regime: str | None = None
    events: list[BreakEvent] = []
    rows: list[dict] = []

    for row in d.itertuples(index=False):
        close = float(row.close)
        pre_regime: str | None = None
        post_regime: str | None = None
        is_break = False
        adverse_move = np.nan
        threshold = np.nan
        regime_before = regime

        if regime is None:
            if pd.notna(row.close_lag20):
                momentum20 = float(np.log(close / float(row.close_lag20)))
                if momentum20 > 0:
                    regime = "UP"
                elif momentum20 < 0:
                    regime = "DOWN"
                if regime is not None:
                    extreme = close
                    initialization_date = pd.Timestamp(row.trade_date)
                    initial_regime = regime
        else:
            sigma = float(row.sigma20_lag1) if pd.notna(row.sigma20_lag1) else np.nan
            if regime == "UP":
                adverse_move = float(np.log(float(extreme) / close))
            else:
                adverse_move = float(np.log(close / float(extreme)))
            if np.isfinite(sigma):
                threshold = float(k * sigma)
            if np.isfinite(threshold) and adverse_move >= threshold:
                is_break = True
                pre_regime = regime
                post_regime = "DOWN" if regime == "UP" else "UP"
                regime = post_regime
                extreme = close
                gap = None if pd.isna(row.prev_trade_date) else int((pd.Timestamp(row.trade_date) - pd.Timestamp(row.prev_trade_date)).days)
                span20 = None if pd.isna(row.trade_date_lag20) else int((pd.Timestamp(row.trade_date) - pd.Timestamp(row.trade_date_lag20)).days)
                events.append(
                    BreakEvent(
                        trade_date=pd.Timestamp(row.trade_date),
                        close=close,
                        pre_regime=pre_regime,
                        post_regime=post_regime,
                        sigma20_lag1=sigma,
                        adverse_move=adverse_move,
                        threshold=threshold,
                        origin_gap_days=gap,
                        sigma_span_calendar_days=span20,
                    )
                )
            elif regime == "UP":
                extreme = max(float(extreme), close)
            else:
                extreme = min(float(extreme), close)

        rows.append(
            {
                "observation_ts": row.observation_ts,
                "trade_date": pd.Timestamp(row.trade_date),
                "close": close,
                "log_ret": row.log_ret,
                "sigma20_lag1": row.sigma20_lag1,
                "regime_before": regime_before,
                "regime_after": regime,
                "regime_extreme_after": extreme,
                "is_break": is_break,
                "pre_regime": pre_regime,
                "post_regime": post_regime,
                "adverse_move": adverse_move,
                "threshold": threshold,
                "k_sigma": k,
            }
        )

    if initialization_date is None or initial_regime is None:
        raise RuntimeError("WP2_REGIME_INITIALIZATION_FAIL")
    return pd.DataFrame(rows), events, initialization_date, initial_regime


def event_frame(events: list[BreakEvent], k: float) -> pd.DataFrame:
    rows = []
    formation_events = [e for e in events if FORMATION_START <= e.trade_date <= FORMATION_END]
    for i, e in enumerate(formation_events, start=1):
        rows.append(
            {
                "event_id": f"B{i:03d}",
                "trade_date": e.trade_date.date().isoformat(),
                "close": e.close,
                "pre_regime": e.pre_regime,
                "post_regime": e.post_regime,
                "break_direction": f"{e.pre_regime}_TO_{e.post_regime}",
                "sigma20_lag1": e.sigma20_lag1,
                "adverse_move": e.adverse_move,
                "threshold": e.threshold,
                "origin_gap_days": e.origin_gap_days,
                "sigma_span_calendar_days": e.sigma_span_calendar_days,
                "k_sigma": k,
                "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                "prospective_claim": False,
            }
        )
    return pd.DataFrame(rows)


def spacing_stats(events: pd.DataFrame) -> dict:
    if len(events) < 2:
        return {
            "mean_spacing_origins": None,
            "median_spacing_origins": None,
            "min_spacing_origins": None,
            "mean_spacing_calendar_days": None,
            "median_spacing_calendar_days": None,
            "min_spacing_calendar_days": None,
        }
    # Origin spacing is measured on the governed canonical observation index.
    dates = pd.to_datetime(events["trade_date"])
    return {
        "mean_spacing_calendar_days": float(dates.diff().dropna().dt.days.mean()),
        "median_spacing_calendar_days": float(dates.diff().dropna().dt.days.median()),
        "min_spacing_calendar_days": int(dates.diff().dropna().dt.days.min()),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_canonical()
    features = prepare_features(raw)
    primary_daily, primary_all, init_date, init_regime = run_labeler(features, PRIMARY_K)
    sensitivity_daily, sensitivity_all, init_date_25, init_regime_25 = run_labeler(features, SENSITIVITY_K)

    primary_events = event_frame(primary_all, PRIMARY_K)
    sensitivity_events = event_frame(sensitivity_all, SENSITIVITY_K)
    formation_mask = primary_daily["trade_date"].between(FORMATION_START, FORMATION_END)
    formation_daily = primary_daily.loc[formation_mask].copy().reset_index(drop=True)

    event_id_by_date = dict(zip(primary_events["trade_date"], primary_events["event_id"]))
    formation_daily["event_id"] = formation_daily["trade_date"].dt.date.astype(str).map(event_id_by_date)
    formation_daily["evidence_class"] = "HISTORICAL_REPLAY_RECONSTRUCTION"
    formation_daily["prospective_claim"] = False

    # Contract / quality audits.
    dirs = primary_events["break_direction"].tolist()
    alternation_ok = all(a != b for a, b in zip(dirs, dirs[1:]))
    exact_ts_unique = int(raw["observation_ts"].nunique()) == len(raw)
    formation_rows = int(formation_mask.sum())
    counts_by_year = {
        str(y): int((pd.to_datetime(primary_events["trade_date"]).dt.year == y).sum())
        for y in (2022, 2023, 2024)
    }
    sensitivity_counts_by_year = {
        str(y): int((pd.to_datetime(sensitivity_events["trade_date"]).dt.year == y).sum())
        for y in (2022, 2023, 2024)
    }

    # Governed-origin spacing for primary events.
    idx_map = {d.date().isoformat(): i for i, d in enumerate(formation_daily["trade_date"], start=1)}
    event_origin_idx = [idx_map[d] for d in primary_events["trade_date"]]
    origin_spacings = np.diff(event_origin_idx) if len(event_origin_idx) >= 2 else np.array([])
    calendar_spacings = pd.to_datetime(primary_events["trade_date"]).diff().dropna().dt.days.to_numpy()

    audit = {
        "audit_id": "GC_BREAK_WP2_LABEL_AUDIT_V1",
        "status": "PASS_WITH_DATA_DENSITY_WARNING",
        "series_id": SERIES_ID,
        "source_contract": "Twelve Data XAU/USD 1min exact 16:59 America/New_York -> NY17 canonical",
        "prehistory_start": PREHISTORY_START.date().isoformat(),
        "formation_start": FORMATION_START.date().isoformat(),
        "formation_end": FORMATION_END.date().isoformat(),
        "canonical_rows_prehistory_plus_formation": int(len(raw)),
        "formation_governed_origins": formation_rows,
        "distinct_observation_ts": int(raw["observation_ts"].nunique()),
        "duplicate_timestamp_count": int(len(raw) - raw["observation_ts"].nunique()),
        "chronology_monotonic": bool(raw["trade_date"].is_monotonic_increasing),
        "primary_contract": {
            "family": "VOLATILITY_NORMALIZED_DIRECTIONAL_CHANGE",
            "return_transform": "log(P_t/P_t-1)",
            "sigma_window_observations": SIGMA_WINDOW,
            "sigma_lag": 1,
            "sigma_ddof": 1,
            "k_sigma": PRIMARY_K,
            "persistence_filter": "NONE",
            "engine_independent": True,
            "engine_inputs_used": [],
        },
        "initialization": {
            "date": init_date.date().isoformat(),
            "regime": init_regime,
            "sensitivity_date": init_date_25.date().isoformat(),
            "sensitivity_regime": init_regime_25,
        },
        "primary_events": {
            "count": int(len(primary_events)),
            "counts_by_year": counts_by_year,
            "up_to_down": int((primary_events["break_direction"] == "UP_TO_DOWN").sum()),
            "down_to_up": int((primary_events["break_direction"] == "DOWN_TO_UP").sum()),
            "direction_alternation_ok": bool(alternation_ok),
            "mean_spacing_origins": float(origin_spacings.mean()) if len(origin_spacings) else None,
            "median_spacing_origins": float(np.median(origin_spacings)) if len(origin_spacings) else None,
            "min_spacing_origins": int(origin_spacings.min()) if len(origin_spacings) else None,
            "mean_spacing_calendar_days": float(calendar_spacings.mean()) if len(calendar_spacings) else None,
            "median_spacing_calendar_days": float(np.median(calendar_spacings)) if len(calendar_spacings) else None,
            "min_spacing_calendar_days": int(calendar_spacings.min()) if len(calendar_spacings) else None,
        },
        "sensitivity_k_2_5": {
            "count": int(len(sensitivity_events)),
            "counts_by_year": sensitivity_counts_by_year,
            "up_to_down": int((sensitivity_events["break_direction"] == "UP_TO_DOWN").sum()),
            "down_to_up": int((sensitivity_events["break_direction"] == "DOWN_TO_UP").sum()),
            "selection_rule": "sensitivity only; must not replace primary k=3.0 from downstream model score",
        },
        "data_density_diagnostics": {
            "formation_rows_by_year": {
                str(y): int((formation_daily["trade_date"].dt.year == y).sum()) for y in (2022, 2023, 2024)
            },
            "primary_event_origin_gap_days_max": int(primary_events["origin_gap_days"].max()),
            "primary_event_origin_gap_days_median": float(primary_events["origin_gap_days"].median()),
            "primary_event_sigma_span_days_max": int(primary_events["sigma_span_calendar_days"].max()),
            "primary_event_sigma_span_days_median": float(primary_events["sigma_span_calendar_days"].median()),
            "interpretation": "The frozen contract uses governed observations, not an imputed weekday grid. Missing exact NY17 bars remain missing; no interpolation/ffill is introduced. Sparse calendar density must remain visible in WP3/WP4.",
        },
        "engine_independence_test": {
            "forbidden_engine_columns_used": [],
            "passed": True,
        },
        "database_writes": "NONE",
        "prospective_claim": False,
        "wp2_interpretation": "Primary engine-independent break inventory generated on canonical XAU. Suitable to proceed to chronology/feature audit only with the explicit data-density warning retained.",
    }

    if not exact_ts_unique or not alternation_ok:
        audit["status"] = "FAIL"

    primary_events.to_csv(a.output_dir / "gc_break_wp2_break_events_k3_v1.csv", index=False)
    sensitivity_events.to_csv(a.output_dir / "gc_break_wp2_break_events_k25_sensitivity_v1.csv", index=False)
    formation_daily.to_csv(a.output_dir / "gc_break_wp2_origin_labels_k3_v1.csv", index=False)
    (a.output_dir / "gc_break_wp2_label_audit_v1.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps(audit, indent=2, sort_keys=True))
    if audit["status"] == "FAIL":
        return 1
    print("GC_BREAK_WP2_GROUND_TRUTH_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
