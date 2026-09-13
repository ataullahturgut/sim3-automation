from __future__ import annotations

import copy
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from river import drift

from gold_axis_2026.v163_research import run_v163_heterogeneous_forecasters as v163
from gold_axis_2026.v164_research import run_v164_adaptive_error_memory as v164

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v165a_research/contracts/v165a_drift_detector_validation_freeze_v1.json"
V164_CONTRACT = ROOT / "v164_research/contracts/v164_adaptive_error_memory_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v165a_research"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    family: str
    params: dict


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V165A_DETECTOR_SCORING":
        raise RuntimeError("V165A_CONTRACT_NOT_FROZEN")
    e = c["evaluation_lock"]
    if e["2025_2026_loss_streams_used_for_detector_selection"] is not False:
        raise RuntimeError("V165A_FUTURE_LOSS_SELECTION_FORBIDDEN")
    if e["triggered_adaptation_in_v165a"] != "FORBIDDEN":
        raise RuntimeError("V165A_ADAPTATION_MUST_REMAIN_FORBIDDEN")
    if e["selector_scoring_in_v165a"] != "FORBIDDEN":
        raise RuntimeError("V165A_SELECTOR_MUST_REMAIN_FORBIDDEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V165A_GOVERNANCE_LOCK_FAIL")
    return c


def detector_candidates(contract: dict) -> list[Candidate]:
    out: list[Candidate] = []
    a = contract["detectors"]["ADWIN"]
    for delta in a["delta_grid"]:
        out.append(Candidate(
            candidate_id=f"ADWIN_D{float(delta):g}",
            family="ADWIN",
            params={
                "delta": float(delta),
                "clock": int(a["clock"]),
                "max_buckets": int(a["max_buckets"]),
                "min_window_length": int(a["min_window_length"]),
                "grace_period": int(a["grace_period"]),
            },
        ))
    p = contract["detectors"]["PAGE_HINKLEY"]
    for delta in p["delta_grid_standardized"]:
        for threshold in p["threshold_grid_standardized"]:
            out.append(Candidate(
                candidate_id=f"PH_D{float(delta):g}_T{float(threshold):g}",
                family="PAGE_HINKLEY",
                params={
                    "min_instances": int(p["min_instances"]),
                    "delta": float(delta),
                    "threshold": float(threshold),
                    "alpha": float(p["alpha"]),
                    "mode": str(p["mode"]),
                },
            ))
    return out


def moving_block_bootstrap(base: np.ndarray, length: int, block_length: int, rng: np.random.Generator) -> np.ndarray:
    x = np.asarray(base, dtype=float)
    if len(x) < block_length:
        raise ValueError("BASE_SHORTER_THAN_BLOCK")
    chunks: list[np.ndarray] = []
    max_start = len(x) - block_length
    while sum(len(c) for c in chunks) < length:
        start = int(rng.integers(0, max_start + 1))
        chunks.append(x[start:start + block_length])
    return np.concatenate(chunks)[:length].copy()


def inject_drift(stream: np.ndarray, start: int, shape: str, shift: float, clip: tuple[float, float]) -> np.ndarray:
    z = np.asarray(stream, dtype=float).copy()
    if shift == 0.0:
        return np.clip(z, clip[0], clip[1])
    if shape == "ABRUPT":
        z[start:] += shift
    elif shape == "GRADUAL_20":
        width = 20
        stop = min(len(z), start + width)
        if stop > start:
            ramp = np.linspace(shift / width, shift, stop - start)
            z[start:stop] += ramp
        if stop < len(z):
            z[stop:] += shift
    else:
        raise ValueError(shape)
    return np.clip(z, clip[0], clip[1])


def first_alarm(candidate: Candidate, stream: np.ndarray, baseline_mean: float, baseline_sd: float) -> int | None:
    if candidate.family == "ADWIN":
        d = drift.ADWIN(**candidate.params)
        for i, x in enumerate(np.asarray(stream, dtype=float)):
            # Excess Brier is bounded to [-1,1]; map to [0,1] for ADWIN's bounded-stream setting.
            d.update(float(np.clip((x + 1.0) / 2.0, 0.0, 1.0)))
            if d.drift_detected:
                return i
        return None
    if candidate.family == "PAGE_HINKLEY":
        d = drift.PageHinkley(**candidate.params)
        scale = baseline_sd if np.isfinite(baseline_sd) and baseline_sd > 1e-12 else 1.0
        for i, x in enumerate(np.asarray(stream, dtype=float)):
            d.update(float((x - baseline_mean) / scale))
            if d.drift_detected:
                return i
        return None
    raise ValueError(candidate.family)


def formation_loss_streams(panel: pd.DataFrame, contract: dict) -> tuple[dict, list[dict]]:
    parent_contract = json.loads(V164_CONTRACT.read_text(encoding="utf-8"))
    formation_end = pd.Timestamp(contract["formation_only_end"])
    d = panel[pd.to_datetime(panel["date"]) <= formation_end].copy().reset_index(drop=True)
    streams: dict = {}
    diagnostics: list[dict] = []
    for h in [int(x) for x in contract["horizons"]]:
        streams[h] = {}
        for parent, (kind, features) in v163.EXPERTS.items():
            pred = v164.sequential_parent(d, h, parent, kind, list(features), parent_contract)
            if pred.empty:
                raise RuntimeError(f"V165A_EMPTY_FORMATION_PREDICTIONS:{h}:{parent}")
            pred = pred[
                (pd.to_datetime(pred["origin_date"]) <= formation_end)
                & (pd.to_datetime(pred["target_date"]) <= formation_end)
            ].copy()
            if pred.empty:
                raise RuntimeError(f"V165A_EMPTY_FORMATION_SLICE:{h}:{parent}")
            if pd.to_datetime(pred["origin_date"]).max() > formation_end or pd.to_datetime(pred["target_date"]).max() > formation_end:
                raise RuntimeError("V165A_FUTURE_LOSS_LEAKAGE")
            raw = np.square(pred["y"].to_numpy(float) - pred["STATIC"].to_numpy(float))
            freq = np.square(pred["y"].to_numpy(float) - pred["FREQ"].to_numpy(float))
            excess = raw - freq
            streams[h][parent] = excess.astype(float)
            diagnostics.append({
                "horizon": h,
                "parent": parent,
                "n": int(len(excess)),
                "raw_brier_mean": float(np.mean(raw)),
                "frequency_brier_mean": float(np.mean(freq)),
                "excess_brier_mean": float(np.mean(excess)),
                "excess_brier_sd": float(np.std(excess, ddof=0)),
                "max_origin_date": str(pd.to_datetime(pred["origin_date"]).max().date()),
                "max_target_date": str(pd.to_datetime(pred["target_date"]).max().date()),
            })
    return streams, diagnostics


def scenario_specs(contract: dict) -> list[tuple[str, str, float]]:
    out = [("NULL", "NULL", 0.0)]
    s = contract["synthetic_validation"]
    for shape in s["drift_shapes"]:
        for mult in s["shift_sizes_in_formation_sd"]:
            out.append((f"{shape}_{float(mult):g}SD", str(shape), float(mult)))
    return out


def evaluate_one(
    base: np.ndarray,
    horizon: int,
    candidate: Candidate,
    scenario_name: str,
    shape: str,
    shift_mult: float,
    contract: dict,
    seed_offset: int,
) -> dict:
    cfg = contract["synthetic_validation"]
    reps = int(cfg["replicates_per_scenario"])
    length = int(cfg["stream_length"])
    drift_start = int(cfg["pre_drift_length"])
    block_length = max(5, int(horizon))
    lo, hi = [float(x) for x in cfg["clip_excess_brier"]]
    mu = float(np.mean(base))
    sd = float(np.std(base, ddof=0))
    if not np.isfinite(sd) or sd <= 1e-12:
        raise RuntimeError("V165A_ZERO_FORMATION_LOSS_SD")

    rng = np.random.default_rng(int(cfg["seed"]) + int(seed_offset))
    alarms: list[int | None] = []
    for _ in range(reps):
        stream = moving_block_bootstrap(base, length, block_length, rng)
        if scenario_name != "NULL":
            stream = inject_drift(stream, drift_start, shape, shift_mult * sd, (lo, hi))
        alarm = first_alarm(candidate, stream, mu, sd)
        alarms.append(alarm)

    any_alarm = np.asarray([a is not None for a in alarms], dtype=bool)
    if scenario_name == "NULL":
        return {
            "scenario": scenario_name,
            "replicates": reps,
            "false_alarm_rate": float(np.mean(any_alarm)),
            "detection_rate": None,
            "pre_drift_false_alarm_rate": None,
            "median_detection_delay": None,
            "p90_detection_delay": None,
        }

    pre_false = np.asarray([(a is not None and a < drift_start) for a in alarms], dtype=bool)
    valid = [int(a - drift_start) for a in alarms if a is not None and a >= drift_start]
    detection_rate = float(len(valid) / reps)
    return {
        "scenario": scenario_name,
        "replicates": reps,
        "false_alarm_rate": None,
        "detection_rate": detection_rate,
        "pre_drift_false_alarm_rate": float(np.mean(pre_false)),
        "median_detection_delay": float(np.median(valid)) if valid else None,
        "p90_detection_delay": float(np.quantile(valid, 0.90)) if valid else None,
    }


def aggregate_candidates(rows: list[dict], candidates: list[Candidate], horizon: int, contract: dict) -> list[dict]:
    cfg = contract["detector_selection"]
    out: list[dict] = []
    for cand in candidates:
        z = [r for r in rows if r["horizon"] == horizon and r["candidate_id"] == cand.candidate_id]
        null = [r for r in z if r["scenario"] == "NULL"]
        one_sd = [r for r in z if r["scenario"].endswith("_1SD")]
        nonnull = [r for r in z if r["scenario"] != "NULL"]
        far = float(np.mean([r["false_alarm_rate"] for r in null])) if null else math.nan
        det1 = float(np.mean([r["detection_rate"] for r in one_sd])) if one_sd else math.nan
        delays1 = [r["median_detection_delay"] for r in one_sd if r["median_detection_delay"] is not None]
        all_delays = [r["median_detection_delay"] for r in nonnull if r["median_detection_delay"] is not None]
        med1 = float(np.median(delays1)) if delays1 else math.inf
        avg_delay = float(np.mean(all_delays)) if all_delays else math.inf
        pass_far = bool(np.isfinite(far) and far <= float(cfg["minimum_null_false_alarm_requirement"]))
        pass_det = bool(np.isfinite(det1) and det1 >= float(cfg["minimum_detection_rate_at_1sd"]))
        out.append({
            "horizon": horizon,
            "candidate_id": cand.candidate_id,
            "family": cand.family,
            "params": cand.params,
            "mean_null_false_alarm_rate": far,
            "mean_detection_rate_at_1sd": det1,
            "median_delay_at_1sd": None if not np.isfinite(med1) else med1,
            "mean_median_delay_across_nonnull": None if not np.isfinite(avg_delay) else avg_delay,
            "false_alarm_gate_pass": pass_far,
            "detection_gate_pass": pass_det,
            "pass": bool(pass_far and pass_det),
        })
    return out


def select_candidate(summary: list[dict]) -> dict:
    eligible = [r for r in summary if r["pass"]]
    if not eligible:
        return {"status": "NO_DETECTOR_PASSES_FROZEN_GATE", "selected_candidate_id": None}
    def key(r: dict):
        delay = r["median_delay_at_1sd"] if r["median_delay_at_1sd"] is not None else math.inf
        avg = r["mean_median_delay_across_nonnull"] if r["mean_median_delay_across_nonnull"] is not None else math.inf
        return (float(delay), float(r["mean_null_false_alarm_rate"]), float(avg), str(r["candidate_id"]))
    best = sorted(eligible, key=key)[0]
    return {"status": "DETECTOR_SELECTED_FORMATION_SYNTHETIC_ONLY", "selected_candidate_id": best["candidate_id"], "selected": best}


def main() -> int:
    contract = load_contract()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    parent_contract = json.loads(V164_CONTRACT.read_text(encoding="utf-8"))
    data_contract = copy.deepcopy(parent_contract)
    data_contract["windows"]["test_end"] = contract["formation_only_end"]

    OUT.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, source_evidence = v163.build_panel(conn, data_contract)

    formation_end = pd.Timestamp(contract["formation_only_end"])
    panel = panel[pd.to_datetime(panel["date"]) <= formation_end].copy().reset_index(drop=True)
    streams, formation_diag = formation_loss_streams(panel, contract)
    candidates = detector_candidates(contract)
    specs = scenario_specs(contract)

    rows: list[dict] = []
    seed_offset = 0
    for h in [int(x) for x in contract["horizons"]]:
        for parent in contract["forecasters"]:
            base = streams[h][parent]
            for cand in candidates:
                for scenario_name, shape, shift_mult in specs:
                    seed_offset += 1009
                    m = evaluate_one(base, h, cand, scenario_name, shape, shift_mult, contract, seed_offset)
                    m.update({
                        "horizon": h,
                        "parent": parent,
                        "candidate_id": cand.candidate_id,
                        "family": cand.family,
                        "shift_mult_sd": shift_mult,
                    })
                    rows.append(m)

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "v165a_detector_synthetic_detail.csv", index=False)
    pd.DataFrame(formation_diag).to_csv(OUT / "v165a_formation_loss_diagnostics.csv", index=False)

    result = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "source_evidence": source_evidence,
        "formation_only_end": contract["formation_only_end"],
        "formation_loss_diagnostics": formation_diag,
        "horizons": {},
        "scientific_interpretation_lock": {
            "2025_2026_loss_streams_used_for_detector_selection": False,
            "triggered_adaptation_performed": False,
            "selector_scoring_performed": False,
            "abstention_tuning_performed": False,
            "post_score_grid_expansion_performed": False,
            "prospective_claim": False,
        },
        "governance": {
            "AUTO_SELECTOR": "OFF",
            "AUTO_ENSEMBLE": "OFF",
            "production_authority": False,
            "production_writes": "NONE",
        },
    }

    any_selected = False
    for h in [int(x) for x in contract["horizons"]]:
        summary = aggregate_candidates(rows, candidates, h, contract)
        selection = select_candidate(summary)
        any_selected = any_selected or selection["selected_candidate_id"] is not None
        result["horizons"][f"{h}D"] = {
            "candidate_summary": summary,
            "formation_synthetic_selection": selection,
        }

    result["any_detector_selected"] = bool(any_selected)
    result["next_step_lock"] = (
        "V165B_TRIGGERED_ADAPTATION_ELIGIBLE_ONLY_FOR_HORIZONS_WITH_SELECTED_DETECTOR"
        if any_selected else
        "STOP_NO_TRIGGERED_ADAPTATION_DETECTOR_GATE_FAILED"
    )

    (OUT / "v165a_drift_detector_validation_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
