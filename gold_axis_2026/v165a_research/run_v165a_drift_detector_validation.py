from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from river import drift

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v165a_research/contracts/v165a_r1_synthetic_drift_detector_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v165a_research"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    family: str
    params: dict


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V165A_R1_DETECTOR_SCORING":
        raise RuntimeError("V165A_R1_CONTRACT_NOT_FROZEN")
    e = c["evaluation_lock"]
    if e["2025_2026_used_for_detector_selection"] is not False:
        raise RuntimeError("V165A_R1_FUTURE_SELECTION_FORBIDDEN")
    if e["triggered_adaptation_in_v165a_r1"] != "FORBIDDEN":
        raise RuntimeError("V165A_R1_ADAPTATION_MUST_REMAIN_FORBIDDEN")
    if e["selector_scoring_in_v165a_r1"] != "FORBIDDEN":
        raise RuntimeError("V165A_R1_SELECTOR_MUST_REMAIN_FORBIDDEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V165A_R1_GOVERNANCE_LOCK_FAIL")
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


def generate_ar1_loss_stream(
    rng: np.random.Generator,
    length: int,
    rho: float,
    innovation: str,
    burn: int = 200,
) -> np.ndarray:
    n = int(length + burn)
    if innovation == "NORMAL":
        eps = rng.normal(size=n)
    elif innovation == "STUDENT_T5":
        eps = rng.standard_t(df=5, size=n) / math.sqrt(5.0 / 3.0)
    else:
        raise ValueError(innovation)
    z = np.zeros(n, dtype=float)
    scale = math.sqrt(max(1e-12, 1.0 - float(rho) ** 2))
    z[0] = eps[0]
    for i in range(1, n):
        z[i] = float(rho) * z[i - 1] + scale * eps[i]
    return z[burn:]


def inject_drift(stream: np.ndarray, start: int, shape: str, shift: float) -> np.ndarray:
    z = np.asarray(stream, dtype=float).copy()
    if shift == 0.0:
        return z
    if shape == "ABRUPT":
        z[start:] += shift
    elif shape == "GRADUAL_30":
        width = 30
        stop = min(len(z), start + width)
        if stop > start:
            z[start:stop] += np.linspace(shift / width, shift, stop - start)
        if stop < len(z):
            z[stop:] += shift
    else:
        raise ValueError(shape)
    return z


def _new_detector(candidate: Candidate):
    if candidate.family == "ADWIN":
        return drift.ADWIN(**candidate.params)
    if candidate.family == "PAGE_HINKLEY":
        return drift.PageHinkley(**candidate.params)
    raise ValueError(candidate.family)


def first_alarm_synthetic(candidate: Candidate, latent_stream: np.ndarray, clip: tuple[float, float]) -> int | None:
    d = _new_detector(candidate)
    lo, hi = clip
    for i, x in enumerate(np.asarray(latent_stream, dtype=float)):
        if candidate.family == "ADWIN":
            bounded = float(np.clip((np.clip(x, lo, hi) - lo) / (hi - lo), 0.0, 1.0))
            d.update(bounded)
        else:
            d.update(float(x))
        if d.drift_detected:
            return i
    return None


def synthetic_scenarios(contract: dict) -> list[tuple[str, str, float]]:
    s = contract["synthetic_benchmark"]
    out = [("NULL", "NULL", 0.0)]
    for shape in s["drift_shapes"]:
        for mult in s["shift_sizes_sd"]:
            out.append((f"{shape}_{float(mult):g}SD", str(shape), float(mult)))
    return out


def run_synthetic_benchmark(contract: dict, candidates: list[Candidate]) -> list[dict]:
    s = contract["synthetic_benchmark"]
    reps = int(s["replicates_per_scenario"])
    length = int(s["stream_length"])
    drift_start = int(s["pre_drift_length"])
    clip = tuple(float(x) for x in s["latent_clip"])
    rows: list[dict] = []
    seed = int(s["seed"])
    scenario_index = 0

    for innovation in s["innovation_families"]:
        for rho in [float(x) for x in s["ar1_rho"]]:
            for scenario, shape, shift in synthetic_scenarios(contract):
                scenario_index += 1
                alarms = {c.candidate_id: [] for c in candidates}
                rng = np.random.default_rng(seed + 100003 * scenario_index)
                for _ in range(reps):
                    base = generate_ar1_loss_stream(rng, length, rho, str(innovation))
                    stream = base if scenario == "NULL" else inject_drift(base, drift_start, shape, shift)
                    for cand in candidates:
                        alarms[cand.candidate_id].append(first_alarm_synthetic(cand, stream, clip))

                for cand in candidates:
                    aa = alarms[cand.candidate_id]
                    if scenario == "NULL":
                        rows.append({
                            "candidate_id": cand.candidate_id,
                            "family": cand.family,
                            "innovation": innovation,
                            "rho": rho,
                            "scenario": scenario,
                            "shift_sd": 0.0,
                            "replicates": reps,
                            "false_alarm_rate": float(np.mean([a is not None for a in aa])),
                            "pre_drift_false_alarm_rate": None,
                            "detection_rate": None,
                            "median_detection_delay": None,
                            "p90_detection_delay": None,
                        })
                    else:
                        pre_false = [a is not None and a < drift_start for a in aa]
                        delays = [int(a - drift_start) for a in aa if a is not None and a >= drift_start]
                        rows.append({
                            "candidate_id": cand.candidate_id,
                            "family": cand.family,
                            "innovation": innovation,
                            "rho": rho,
                            "scenario": scenario,
                            "shift_sd": shift,
                            "replicates": reps,
                            "false_alarm_rate": None,
                            "pre_drift_false_alarm_rate": float(np.mean(pre_false)),
                            "detection_rate": float(len(delays) / reps),
                            "median_detection_delay": float(np.median(delays)) if delays else None,
                            "p90_detection_delay": float(np.quantile(delays, 0.90)) if delays else None,
                        })
    return rows


def aggregate_candidate(rows: list[dict], candidate: Candidate, contract: dict) -> dict:
    z = [r for r in rows if r["candidate_id"] == candidate.candidate_id]
    null = [r for r in z if r["scenario"] == "NULL"]
    one = [r for r in z if r["shift_sd"] == 1.0]
    nonnull = [r for r in z if r["scenario"] != "NULL"]
    mean_far = float(np.mean([r["false_alarm_rate"] for r in null]))
    worst_far = float(np.max([r["false_alarm_rate"] for r in null]))
    mean_det = float(np.mean([r["detection_rate"] for r in one]))

    by_arch: dict[tuple[str, float], list[float]] = {}
    for r in one:
        by_arch.setdefault((str(r["innovation"]), float(r["rho"])), []).append(float(r["detection_rate"]))
    arch_rates = [float(np.mean(v)) for v in by_arch.values()]
    worst_det = float(np.min(arch_rates))

    delays_1 = [float(r["median_detection_delay"]) for r in one if r["median_detection_delay"] is not None]
    all_delays = [float(r["median_detection_delay"]) for r in nonnull if r["median_detection_delay"] is not None]
    med_delay_1 = float(np.median(delays_1)) if delays_1 else math.inf
    mean_delay_all = float(np.mean(all_delays)) if all_delays else math.inf

    g = contract["selection_gate"]
    checks = {
        "mean_false_alarm_pass": mean_far <= float(g["mean_null_false_alarm_rate_max"]),
        "worst_false_alarm_pass": worst_far <= float(g["worst_archetype_null_false_alarm_rate_max"]),
        "mean_detection_pass": mean_det >= float(g["mean_detection_rate_at_1sd_min"]),
        "worst_detection_pass": worst_det >= float(g["worst_archetype_detection_rate_at_1sd_min"]),
    }
    return {
        "candidate_id": candidate.candidate_id,
        "family": candidate.family,
        "params": candidate.params,
        "mean_null_false_alarm_rate": mean_far,
        "worst_archetype_null_false_alarm_rate": worst_far,
        "mean_detection_rate_at_1sd": mean_det,
        "worst_archetype_detection_rate_at_1sd": worst_det,
        "median_detection_delay_at_1sd": None if not np.isfinite(med_delay_1) else med_delay_1,
        "mean_detected_delay_all_nonnull": None if not np.isfinite(mean_delay_all) else mean_delay_all,
        "checks": checks,
        "pass": bool(all(checks.values())),
    }


def select_candidate(summary: list[dict]) -> dict:
    eligible = [x for x in summary if x["pass"]]
    if not eligible:
        return {"status": "NO_DETECTOR_PASSES_FROZEN_SYNTHETIC_GATE", "selected_candidate_id": None}

    def key(x: dict):
        delay = x["median_detection_delay_at_1sd"] if x["median_detection_delay_at_1sd"] is not None else math.inf
        avg = x["mean_detected_delay_all_nonnull"] if x["mean_detected_delay_all_nonnull"] is not None else math.inf
        return (
            float(delay),
            float(x["mean_null_false_alarm_rate"]),
            -float(x["mean_detection_rate_at_1sd"]),
            float(avg),
            str(x["candidate_id"]),
        )

    best = sorted(eligible, key=key)[0]
    return {"status": "DETECTOR_SELECTED_SYNTHETIC_ONLY", "selected_candidate_id": best["candidate_id"], "selected": best}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_artifact_files(artifact_dir: Path, contract: dict) -> list[Path]:
    expected = contract["frozen_v164_artifact"]["prediction_file_sha256"]
    files: list[Path] = []
    for name, digest in sorted(expected.items()):
        p = artifact_dir / name
        if not p.exists():
            raise RuntimeError(f"V165A_R1_MISSING_FROZEN_V164_FILE:{name}")
        actual = _sha256(p)
        if actual != digest:
            raise RuntimeError(f"V165A_R1_V164_FILE_HASH_MISMATCH:{name}:{actual}")
        files.append(p)
    return files


def actual_alarm_dates(candidate: Candidate, excess: np.ndarray, dates: list[str], contract: dict) -> list[str]:
    d = _new_detector(candidate)
    cfg = contract["actual_timeline_diagnostic"]
    baseline_n = int(cfg["page_hinkley_standardization_baseline_n"])
    x = np.asarray(excess, dtype=float)
    if candidate.family == "PAGE_HINKLEY":
        if len(x) < baseline_n:
            raise RuntimeError("V165A_R1_ACTUAL_BASELINE_TOO_SHORT")
        mu = float(np.mean(x[:baseline_n]))
        sd = float(np.std(x[:baseline_n], ddof=0))
        if not np.isfinite(sd) or sd <= 1e-12:
            sd = 1.0
    else:
        mu, sd = 0.0, 1.0

    alarms: list[str] = []
    for i, val in enumerate(x):
        if candidate.family == "ADWIN":
            d.update(float(np.clip((val + 1.0) / 2.0, 0.0, 1.0)))
        else:
            d.update(float((val - mu) / sd))
        if d.drift_detected:
            alarms.append(str(dates[i]))
    return alarms


def run_actual_timeline(selected: Candidate, artifact_dir: Path, contract: dict) -> dict:
    files = validate_artifact_files(artifact_dir, contract)
    out: dict = {}
    for p in files:
        df = pd.read_csv(p)
        raw = np.square(df["y"].to_numpy(float) - df["STATIC"].to_numpy(float))
        freq = np.square(df["y"].to_numpy(float) - df["FREQ"].to_numpy(float))
        excess = raw - freq
        dates = df["target_date"].astype(str).tolist()
        alarms = actual_alarm_dates(selected, excess, dates, contract)
        by_year: dict[str, int] = {}
        for x in alarms:
            year = str(pd.Timestamp(x).year)
            by_year[year] = by_year.get(year, 0) + 1
        out[p.name] = {
            "n": int(len(df)),
            "first_target_date": dates[0],
            "last_target_date": dates[-1],
            "first_alarm_date": alarms[0] if alarms else None,
            "alarm_dates": alarms,
            "alarms_by_calendar_year": by_year,
            "pre_2025_alarm_flag": bool(any(pd.Timestamp(x) < pd.Timestamp("2025-01-01") for x in alarms)),
            "mean_excess_brier_2024": float(np.mean(excess[pd.to_datetime(df["target_date"]) < pd.Timestamp("2025-01-01")])) if np.any(pd.to_datetime(df["target_date"]) < pd.Timestamp("2025-01-01")) else None,
            "mean_excess_brier_2025": float(np.mean(excess[pd.to_datetime(df["target_date"]).dt.year == 2025])) if np.any(pd.to_datetime(df["target_date"]).dt.year == 2025) else None,
            "mean_excess_brier_2026": float(np.mean(excess[pd.to_datetime(df["target_date"]).dt.year == 2026])) if np.any(pd.to_datetime(df["target_date"]).dt.year == 2026) else None,
        }
    return out


def main() -> int:
    contract = load_contract()
    candidates = detector_candidates(contract)
    rows = run_synthetic_benchmark(contract, candidates)
    summary = [aggregate_candidate(rows, c, contract) for c in candidates]
    selection = select_candidate(summary)

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "v165a_r1_synthetic_detector_detail.csv", index=False)

    actual_timeline = None
    if selection["selected_candidate_id"] is not None:
        selected = next(c for c in candidates if c.candidate_id == selection["selected_candidate_id"])
        artifact_dir_raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
        if not artifact_dir_raw:
            raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED_AFTER_SYNTHETIC_SELECTION")
        actual_timeline = run_actual_timeline(selected, Path(artifact_dir_raw), contract)

    result = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "r0_superseded_before_scoring": True,
        "synthetic_candidate_summary": summary,
        "synthetic_selection": selection,
        "actual_v164_timeline_diagnostic": actual_timeline,
        "scientific_interpretation_lock": {
            "2025_2026_used_for_detector_selection": False,
            "actual_timeline_can_change_selected_detector": False,
            "actual_timeline_can_change_detector_parameters": False,
            "triggered_adaptation_performed": False,
            "selector_scoring_performed": False,
            "abstention_tuning_performed": False,
            "post_score_grid_expansion_performed": False,
            "prospective_claim": False,
        },
        "next_step_lock": (
            "V165B_TRIGGERED_ADAPTATION_METHOD_DEVELOPMENT_ELIGIBLE_WITH_FROZEN_DETECTOR"
            if selection["selected_candidate_id"] is not None
            else "STOP_TRIGGERED_ADAPTATION_BLOCKED_NO_DETECTOR_PASSED"
        ),
        "governance": {
            "AUTO_SELECTOR": "OFF",
            "AUTO_ENSEMBLE": "OFF",
            "production_authority": False,
            "production_writes": "NONE",
        },
    }
    (OUT / "v165a_r1_drift_detector_validation_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
