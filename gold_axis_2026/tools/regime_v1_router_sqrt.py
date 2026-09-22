from __future__ import annotations

import math
from datetime import date

import numpy as np

from regime_v1_data import Daily

ALPHA = 0.20
DELTA = 0.10
Z90 = 1.2815515655446004
ORDER = ["TTSM_S2", "TTSM_S1", "BONATO_AR1_RM_QBOOST_H1", "AR1_RM_LOGIT", "RM_LOGIT"]


def wilson_lcb(tp: int, n: int) -> float:
    if n <= 0:
        return float("-inf")
    p = tp / n
    z = Z90
    den = 1.0 + z*z/n
    num = p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return num / den


def competence(hist: list[dict], expert: str, bucket: str) -> dict:
    same = [r for r in hist if r["legacy_bucket"] == bucket]
    same_calls = sum(int(r[expert]) for r in same)
    sub = same if same_calls >= 30 else hist
    calls = sum(int(r[expert]) for r in sub)
    tp = sum(int(r[expert]) and int(r["actual_up"]) for r in sub)
    fp = calls - tp
    down_n = sum(1 - int(r["actual_up"]) for r in sub)
    precision = tp / calls if calls else 0.0
    fpr = fp / down_n if down_n else 1.0
    return {
        "calls": calls,
        "tp": tp,
        "fp": fp,
        "down_n": down_n,
        "precision": precision,
        "fpr": fpr,
        "lcb": wilson_lcb(tp, calls),
        "source": "BUCKET" if same_calls >= 30 else "GLOBAL",
    }


def router_year(common: list[dict], year: int) -> list[dict]:
    formation = [
        dict(r) for r in common
        if date.fromisoformat(r["target_date"]).year == year - 1
    ]
    ev = [
        dict(r) for r in common
        if date.fromisoformat(r["target_date"]).year == year
    ]
    ev.sort(key=lambda r: r["target_date"])
    hist = list(formation)
    out = []

    for r in ev:
        candidates = []
        for rank, expert in enumerate(ORDER):
            if not int(r[expert]):
                continue
            c = competence(hist, expert, r["legacy_bucket"])
            eligible = (
                c["calls"] >= 30
                and c["precision"] > 0.50
                and c["fpr"] < 0.50
            )
            if eligible:
                key = (c["lcb"], -c["fpr"], c["precision"], -rank)
                candidates.append((key, expert, c))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, selected, cc = candidates[0]
            router_up = 1
        else:
            selected = ""
            cc = None
            router_up = 0

        rr = dict(r)
        rr.update({
            "router_up": router_up,
            "selected_expert": selected,
            "selected_lcb": None if cc is None else cc["lcb"],
            "selected_precision": None if cc is None else cc["precision"],
            "selected_fpr": None if cc is None else cc["fpr"],
            "selected_history_source": None if cc is None else cc["source"],
        })
        out.append(rr)

        # Current target is matured by the next row's origin on this daily target axis.
        hist.append(r)

    return out


def nearest_rank(a: np.ndarray, q: float) -> float:
    a = np.asarray(a, dtype=float)
    if len(a) == 0:
        raise RuntimeError("EMPTY_NEAREST_RANK")
    k = max(1, min(len(a), int(math.ceil(q * len(a)))))
    return float(np.sort(a)[k-1])


def sqrt_rows(days: list[Daily], year: int) -> list[dict]:
    dr = np.array([x.dr for x in days], dtype=float)
    sd = np.sqrt(dr)
    close = np.array([x.close for x in days], dtype=float)

    rows = []
    for i in range(21, len(days)-1):
        t = i + 1
        rows.append({
            "origin_date": days[i].d.isoformat(),
            "target_date": days[t].d.isoformat(),
            "dr_d": float(dr[i]),
            "dr_w": float(np.mean(dr[i-4:i+1])),
            "dr_m": float(np.mean(dr[i-21:i+1])),
            "sd_d": float(sd[i]),
            "sd_w": float(np.mean(sd[i-4:i+1])),
            "sd_m": float(np.mean(sd[i-21:i+1])),
            "target_dr": float(dr[t]),
            "target_return": float(math.log(close[t]/close[i])),
        })

    cutoff = date(year-1, 12, 31)
    train = [
        r for r in rows
        if date.fromisoformat(r["target_date"]) <= cutoff
    ]
    test = [
        r for r in rows
        if date.fromisoformat(r["target_date"]).year == year
    ]
    if len(train) < 250:
        raise RuntimeError(f"SQRT_FORMATION_TOO_SHORT:{year}:{len(train)}")

    X = np.array(
        [[1.0,r["sd_d"],r["sd_w"],r["sd_m"]] for r in train],
        dtype=float,
    )
    ysd = np.array([math.sqrt(r["target_dr"]) for r in train], dtype=float)
    beta = np.linalg.lstsq(X, ysd, rcond=None)[0]
    ydr = np.array([r["target_dr"] for r in train], dtype=float)
    q80 = nearest_rank(ydr, 0.80)
    q90 = nearest_rank(ydr, 0.90)

    out = []
    for r in test:
        xn = np.array([1.0,r["sd_d"],r["sd_w"],r["sd_m"]], dtype=float)
        sp = float(xn @ beta)
        if not math.isfinite(sp) or sp <= 0:
            raise RuntimeError(f"SQRT_NONPOSITIVE:{year}:{r['target_date']}:{sp}")
        fp = sp * sp
        rr = dict(r)
        rr.update({
            "evaluation_year": year,
            "formation_n": len(train),
            "q80": q80,
            "q90": q90,
            "sqrt_forecast": fp,
            "sqrt_normalized_risk_score": fp/q80,
            "sqrt_alarm": int(fp >= q80),
            "risk_regime": (
                "EXTREME" if fp >= q90
                else ("HIGH_NON_EXTREME" if fp >= q80 else "NO_ALARM")
            ),
        })
        out.append(rr)

    return out
