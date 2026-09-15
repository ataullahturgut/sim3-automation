from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import numpy as np

MIN_PRIOR = 24
MAD_NORMAL_SCALE = 1.4826
IQR_NORMAL_WIDTH = 1.3489795003921634


@dataclass(frozen=True)
class RawEvent:
    family: str
    release_ts: datetime
    components: dict[str, float]


@dataclass(frozen=True)
class ScoredEvent:
    family: str
    release_ts: datetime
    raw_components: dict[str, float]
    scales: dict[str, float] | None
    scale_methods: dict[str, str] | None
    z: dict[str, float] | None
    shock_intensity: float | None
    status: str


def linear_quantile(values: Iterable[float], p: float) -> float:
    xs = sorted(float(x) for x in values)
    if not xs:
        raise ValueError("EMPTY_QUANTILE_INPUT")
    if not 0.0 <= p <= 1.0:
        raise ValueError("INVALID_QUANTILE_PROBABILITY")
    if len(xs) == 1:
        return xs[0]
    h = (len(xs) - 1) * p
    j = math.floor(h)
    gamma = h - j
    if j >= len(xs) - 1:
        return xs[-1]
    return xs[j] + gamma * (xs[j + 1] - xs[j])


def robust_scale(values: list[float]) -> tuple[float | None, str | None]:
    if len(values) < MIN_PRIOR:
        return None, None
    med = statistics.median(values)
    mad = statistics.median(abs(float(x) - med) for x in values)
    scale = MAD_NORMAL_SCALE * mad
    if math.isfinite(scale) and scale > 0.0:
        return float(scale), "MAD_1P4826"
    q25 = linear_quantile(values, 0.25)
    q75 = linear_quantile(values, 0.75)
    scale = (q75 - q25) / IQR_NORMAL_WIDTH
    if math.isfinite(scale) and scale > 0.0:
        return float(scale), "IQR_NORMAL_FALLBACK"
    return None, None


def score_family(events: list[RawEvent]) -> list[ScoredEvent]:
    if not events:
        return []
    families = {e.family for e in events}
    if len(families) != 1:
        raise ValueError("MIXED_FAMILIES")
    events = sorted(events, key=lambda e: e.release_ts)
    component_names = tuple(sorted(events[0].components))
    for e in events:
        if tuple(sorted(e.components)) != component_names:
            raise ValueError(f"COMPONENT_SCHEMA_DRIFT:{e.release_ts.isoformat()}")

    prior = {k: [] for k in component_names}
    out: list[ScoredEvent] = []
    for e in events:
        scales: dict[str, float] = {}
        methods: dict[str, str] = {}
        for k in component_names:
            s, method = robust_scale(prior[k])
            if s is not None and method is not None:
                scales[k] = s
                methods[k] = method
        if len(scales) != len(component_names):
            out.append(
                ScoredEvent(
                    family=e.family,
                    release_ts=e.release_ts,
                    raw_components=dict(e.components),
                    scales=None,
                    scale_methods=None,
                    z=None,
                    shock_intensity=None,
                    status="INSUFFICIENT_HISTORY",
                )
            )
        else:
            z = {k: float(e.components[k]) / scales[k] for k in component_names}
            intensity = sum(abs(v) for v in z.values()) / len(z)
            out.append(
                ScoredEvent(
                    family=e.family,
                    release_ts=e.release_ts,
                    raw_components=dict(e.components),
                    scales=scales,
                    scale_methods=methods,
                    z=z,
                    shock_intensity=float(intensity),
                    status="SCORED",
                )
            )
        for k in component_names:
            prior[k].append(float(e.components[k]))
    return out


def severity_thresholds(scored_events: list[ScoredEvent]) -> dict[str, float]:
    vals = [float(e.shock_intensity) for e in scored_events if e.shock_intensity is not None]
    if not vals:
        raise ValueError("NO_SCORED_INTENSITIES")
    return {"q75": linear_quantile(vals, 0.75), "q90": linear_quantile(vals, 0.90)}


def severity(intensity: float | None, thresholds: dict[str, float]) -> str:
    if intensity is None:
        return "INSUFFICIENT_HISTORY"
    if intensity >= float(thresholds["q90"]):
        return "HIGH"
    if intensity >= float(thresholds["q75"]):
        return "ELEVATED"
    return "NORMAL"


def fit_ols(xs: list[list[float]], ys: list[float]) -> dict[str, list[float] | float]:
    if not xs or not ys or len(xs) != len(ys):
        raise ValueError("INVALID_OLS_INPUT")
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if x.ndim != 2:
        raise ValueError("OLS_X_NOT_2D")
    if len(xs) <= x.shape[1]:
        raise ValueError("INSUFFICIENT_OLS_SUPPORT")
    design = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    pred = design @ coef
    residual = y - pred
    rmse = float(np.sqrt(np.mean(residual**2)))
    return {
        "intercept": float(coef[0]),
        "coefficients": [float(v) for v in coef[1:]],
        "rmse": rmse,
    }


def predict_ols(model: dict, x: list[float]) -> float:
    coefs = [float(v) for v in model["coefficients"]]
    if len(coefs) != len(x):
        raise ValueError("PREDICT_DIMENSION_MISMATCH")
    return float(model["intercept"]) + sum(c * float(v) for c, v in zip(coefs, x))


def loo_sign_accuracy(xs: list[list[float]], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 4:
        raise ValueError("INVALID_LOO_INPUT")
    correct = 0
    used = 0
    for i in range(len(xs)):
        train_x = xs[:i] + xs[i + 1 :]
        train_y = ys[:i] + ys[i + 1 :]
        if len(train_x) <= len(train_x[0]):
            continue
        model = fit_ols(train_x, train_y)
        pred = predict_ols(model, xs[i])
        actual = float(ys[i])
        if pred == 0.0 or actual == 0.0:
            continue
        used += 1
        correct += int((pred > 0.0) == (actual > 0.0))
    if used == 0:
        raise ValueError("NO_NONZERO_LOO_CASES")
    return correct / used


def stable_float(value: float) -> float:
    return float(f"{float(value):.12g}")
