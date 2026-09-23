from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import psycopg

from regime_dampener_v1 import frozen_direction_ttsm_realized_semivariance_xau_v1 as ttsm_mod
from regime_dampener_v1 import frozen_direction_bonato_qboost_realized_moments_spot_xau_v1 as bonato_mod
from regime_dampener_v1 import frozen_direction_downside_realized_moments_logit_v2 as logit_mod
from tools.regime_v1_data import Daily
from tools.regime_v1_experts import legacy_context

IDENTITY = "DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESEARCH"
TABLE = "public.xau_intraday_research_cache_5m"
TZ = "America/New_York"
MIN_BARS = 240
CUTOFF = "2026-01-02T05:00:00Z"
Z90 = 1.2815515655446004

DIRECT_UP_EXPERTS = [
    "TTSM_S2",
    "TTSM_S1",
    "BONATO_AR1_RM_QBOOST_H1",
    "AR1_RM_LOGIT",
    "RM_LOGIT",
]
ROUTER_TIE_ORDER = {name: i for i, name in enumerate(DIRECT_UP_EXPERTS)}

CANDIDATES = [
    "TTSM_S2",
    "TTSM_S1",
    "TSM",
    "BONATO_AR1_RM_QBOOST_H1",
    "BONATO_AR1_QBOOST_H1",
    "AR1_RM_LOGIT",
    "RM_LOGIT",
    "RV_LOGIT",
    "RSK_LOGIT",
    "AR1_LOGIT",
]
CANDIDATE_ORDER = {name: i for i, name in enumerate(CANDIDATES)}

EXPECTED_ROUTER = {
    2022: {"up": 22},
    2023: {"up": 19},
    2024: {"up": 42, "tp": 26, "fp": 16},
    2025: {"up": 37, "tp": 27, "fp": 10, "selected_rm": 37},
}
EXPECTED_SQRT = {2022: 11, 2023: 2, 2024: 17, 2025: 90}


@dataclass(frozen=True)
class BaseDay:
    d: object
    close: float
    n_bars: int
    m_returns: int
    rv: float
    r3: float
    rs_plus: float
    rs_minus: float


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v


def load_days() -> list[BaseDay]:
    sql = f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and observation_ts < %s::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select
        d, observation_ts, close,
        case when prev_close is not null and prev_close > 0
             then ln(close/prev_close) else null end as r
      from b
    )
    select
      d,
      count(*)::int as n_bars,
      count(r)::int as m_returns,
      (array_agg(close order by observation_ts desc))[1]::double precision as close,
      coalesce(sum(r*r),0)::double precision as rv,
      coalesce(sum(r*r*r),0)::double precision as r3,
      coalesce(sum(case when r > 0 then r*r else 0 end),0)::double precision as rs_plus,
      coalesce(sum(case when r < 0 then r*r else 0 end),0)::double precision as rs_minus
    from intr
    group by d
    having count(*) >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql, (CUTOFF,))
            raw = cur.fetchall()

    out = []
    for d, n, m, close, rv, r3, rp, rm in raw:
        vals = [float(close), float(rv), float(r3), float(rp), float(rm)]
        if not all(math.isfinite(x) for x in vals):
            raise RuntimeError(f"NONFINITE_DAY:{d}")
        if vals[0] <= 0 or vals[1] < 0 or vals[3] < 0 or vals[4] < 0:
            raise RuntimeError(f"INVALID_DAY:{d}")
        out.append(BaseDay(d, vals[0], int(n), int(m), vals[1], vals[2], vals[3], vals[4]))
    if len(out) < 1000:
        raise RuntimeError(f"INSUFFICIENT_DAYS:{len(out)}")
    return out


def rsk(x: BaseDay) -> float:
    if x.rv > 0 and x.m_returns > 0:
        z = math.sqrt(x.m_returns) * x.r3 / (x.rv ** 1.5)
        return z if math.isfinite(z) else 0.0
    return 0.0


def transformed(days: list[BaseDay]):
    tdays = [ttsm_mod.Day(x.d, x.close, x.n_bars, x.rs_plus, x.rs_minus) for x in days]
    bdays = []
    ldays = []
    daily = []
    prev = None
    for x in days:
        lag = float("nan") if prev is None else math.log(x.close / prev)
        sk = rsk(x)
        bdays.append(bonato_mod.DayRow(x.d, x.close, x.n_bars, x.rv, sk, lag))
        ldays.append(logit_mod.DayRow(x.d, x.close, x.n_bars, x.rv, math.log(max(x.rv, 1e-12)), sk, lag))
        daily.append(Daily(
            d=x.d, close=x.close, n_bars=x.n_bars, m_returns=x.m_returns,
            rv=x.rv, r3=x.r3, dr=x.rs_minus,
            rs_plus=x.rs_plus, rs_minus=x.rs_minus,
        ))
        prev = x.close
    return tdays, bdays, ldays, daily


def bonato_maps(days_b) -> dict[str, dict[str, dict]]:
    maps = {
        "BONATO_AR1_QBOOST_H1": {},
        "BONATO_AR1_RM_QBOOST_H1": {},
    }
    for i in range(1, len(days_b) - 1):
        if not math.isfinite(days_b[i].lag1_return):
            continue
        train_idx = list(range(1, i))
        if len(train_idx) < 250:
            continue
        y = np.array([math.log(days_b[j+1].close / days_b[j].close) for j in train_idx], dtype=float)
        ret = math.log(days_b[i+1].close / days_b[i].close)
        if ret == 0:
            continue
        for name, feats in {
            "BONATO_AR1_QBOOST_H1": ("lag1_return",),
            "BONATO_AR1_RM_QBOOST_H1": ("lag1_return", "rv", "rsk"),
        }.items():
            X = np.array([[float(getattr(days_b[j], f)) for f in feats] for j in train_idx], dtype=float)
            xn = np.array([float(getattr(days_b[i], f)) for f in feats], dtype=float)
            fc, _ = bonato_mod.fit_qboost(X, y, xn, 0.50)
            maps[name][days_b[i+1].d.isoformat()] = {
                "origin_date": days_b[i].d.isoformat(),
                "actual_up": int(ret > 0),
                "score": float(fc),
                "up": int(fc > 0),
                "down": int(fc < 0),
            }
    return maps


def logit_maps(days_l) -> dict[str, dict[str, dict]]:
    maps = {name: {} for name in logit_mod.MODELS}
    for i in range(1, len(days_l) - 1):
        origin = days_l[i]
        if not math.isfinite(origin.lag1_return):
            continue
        train_idx = list(range(1, i))
        if len(train_idx) < 250:
            continue
        y = np.array([
            1.0 if math.log(days_l[j+1].close / days_l[j].close) > 0 else 0.0
            for j in train_idx
        ], dtype=float)
        ret = math.log(days_l[i+1].close / origin.close)
        if ret == 0:
            continue
        for name, feats in logit_mod.MODELS.items():
            X = np.array([[float(getattr(days_l[j], f)) for f in feats] for j in train_idx], dtype=float)
            xn = np.array([float(getattr(origin, f)) for f in feats], dtype=float)
            p, _ = logit_mod.fit_logit_predict(X, y, xn)
            maps[name][days_l[i+1].d.isoformat()] = {
                "origin_date": origin.d.isoformat(),
                "actual_up": int(ret > 0),
                "score": float(p),
                "up": int(p >= 0.5),
                "down": int(p < 0.5),
            }
    return maps


def wilson_lcb(k: int, n: int, z: float = Z90) -> float:
    if n <= 0:
        return float("-inf")
    p = k / n
    den = 1.0 + z*z/n
    center = p + z*z/(2*n)
    rad = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (center - rad) / den


def router_stats(history: list[dict], expert: str, bucket: str) -> dict | None:
    bucket_hist = [r for r in history if r["legacy_bucket"] == bucket]
    bucket_calls = [r for r in bucket_hist if r[expert] == 1]
    use = bucket_hist if len(bucket_calls) >= 30 else history
    calls = [r for r in use if r[expert] == 1]
    n_up = len(calls)
    if n_up == 0:
        return None
    tp = sum(r["actual_up"] == 1 for r in calls)
    fp = n_up - tp
    actual_down_hist = sum(r["actual_up"] == 0 for r in use)
    precision = tp / n_up
    fpr = fp / actual_down_hist if actual_down_hist else 1.0
    return {
        "n_up": n_up,
        "tp": tp,
        "fp": fp,
        "precision": precision,
        "fpr": fpr,
        "lcb": wilson_lcb(tp, n_up),
        "scope": "BUCKET" if use is bucket_hist else "GLOBAL",
    }


def build_router_rows(trows, bmaps, lmaps, contexts) -> list[dict]:
    tmap = {r["target_date"]: r for r in trows}
    common_dates = sorted(
        set(tmap)
        & set(bmaps["BONATO_AR1_RM_QBOOST_H1"])
        & set(lmaps["AR1_RM_LOGIT"])
        & set(lmaps["RM_LOGIT"])
    )
    rows = []
    for td in common_dates:
        t = tmap[td]
        b = bmaps["BONATO_AR1_RM_QBOOST_H1"][td]
        ar = lmaps["AR1_RM_LOGIT"][td]
        rm = lmaps["RM_LOGIT"][td]
        od = t["origin_date"]
        if not (od == b["origin_date"] == ar["origin_date"] == rm["origin_date"]):
            raise RuntimeError(f"ORIGIN_MISMATCH:{td}")
        vals = [int(t["actual_up"]), int(b["actual_up"]), int(ar["actual_up"]), int(rm["actual_up"])]
        if len(set(vals)) != 1:
            raise RuntimeError(f"ACTUAL_MISMATCH:{td}:{vals}")
        ctx = contexts[od]
        row = {
            "origin_date": od,
            "target_date": td,
            "actual_up": vals[0],
            "TTSM_S2": int(t["ttsm_s2_signal"] == 1),
            "TTSM_S1": int(t["ttsm_s1_signal"] == 1),
            "BONATO_AR1_RM_QBOOST_H1": int(b["up"]),
            "AR1_RM_LOGIT": int(ar["up"]),
            "RM_LOGIT": int(rm["up"]),
            **ctx,
        }

        history = rows
        eligible = []
        for expert in DIRECT_UP_EXPERTS:
            if row[expert] != 1:
                continue
            st = router_stats(history, expert, row["legacy_bucket"])
            if st is None:
                continue
            if st["n_up"] < 30 or st["precision"] <= 0.50 or st["fpr"] >= 0.50:
                continue
            eligible.append((expert, st))

        if eligible:
            eligible.sort(key=lambda x: (
                -x[1]["lcb"],
                x[1]["fpr"],
                -x[1]["precision"],
                ROUTER_TIE_ORDER[x[0]],
            ))
            selected, st = eligible[0]
            row["router_up"] = 1
            row["selected_expert"] = selected
            row["selected_lcb"] = st["lcb"]
            row["selected_precision"] = st["precision"]
            row["selected_fpr"] = st["fpr"]
            row["selected_history_n_up"] = st["n_up"]
            row["selected_scope"] = st["scope"]
        else:
            row["router_up"] = 0
            row["selected_expert"] = ""
            row["selected_lcb"] = None
            row["selected_precision"] = None
            row["selected_fpr"] = None
            row["selected_history_n_up"] = None
            row["selected_scope"] = ""
        rows.append(row)
    return rows


def load_sqrt(path: Path) -> list[dict]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y = int(r["evaluation_year"])
            if y not in (2022, 2023, 2024, 2025):
                continue
            if int(r["sqrt_high_risk_alert"]) != 1:
                continue
            ret = float(r["target_close_return"])
            if ret == 0:
                raise RuntimeError(f"ZERO_PARENT_RETURN:{r['target_date']}")
            out.append({
                "evaluation_year": y,
                "origin_date": r["origin_date"],
                "target_date": r["target_date"],
                "actual_up": int(ret > 0),
                "sqrt_score": float(r["sqrt_normalized_risk_score"]),
                "actual_high_risk": int(r["actual_high_risk"]),
            })
    return out


def candidate_down_value(name: str, td: str, tmap, bmaps, lmaps) -> tuple[int | None, float | None]:
    if name == "TTSM_S2":
        r = tmap.get(td)
        return (None, None) if r is None else (int(r["ttsm_s2_signal"] == -1), float(r["ttsm_s2_signal"]))
    if name == "TTSM_S1":
        r = tmap.get(td)
        return (None, None) if r is None else (int(r["ttsm_s1_signal"] == -1), float(r["ttsm_s1_signal"]))
    if name == "TSM":
        r = tmap.get(td)
        return (None, None) if r is None else (int(r["tsm_signal"] == -1), float(r["tsm_signal"]))
    if name in bmaps:
        r = bmaps[name].get(td)
        return (None, None) if r is None else (int(r["down"]), float(r["score"]))
    key = name
    if key in lmaps:
        r = lmaps[key].get(td)
        return (None, None) if r is None else (int(r["down"]), float(r["score"]))
    raise KeyError(name)


def candidate_metrics(rows: list[dict], name: str, tmap, bmaps, lmaps) -> dict:
    vals = []
    for r in rows:
        down, score = candidate_down_value(name, r["target_date"], tmap, bmaps, lmaps)
        if down is None:
            continue
        vals.append((r, down, score))
    n = len(vals)
    calls = [(r, s) for r, d, s in vals if d == 1]
    down_calls = len(calls)
    correct = sum(r["actual_up"] == 0 for r, _ in calls)
    false = sum(r["actual_up"] == 1 for r, _ in calls)
    actual_down = sum(r["actual_up"] == 0 for r, _, _ in vals)
    actual_up = sum(r["actual_up"] == 1 for r, _, _ in vals)
    precision = correct / down_calls if down_calls else None
    recall = correct / actual_down if actual_down else None
    fpr = false / actual_up if actual_up else None
    return {
        "candidate": name,
        "available_n": n,
        "subset_n": len(rows),
        "actual_down": actual_down,
        "actual_up": actual_up,
        "down_calls": down_calls,
        "correct_down": correct,
        "false_down": false,
        "down_precision": precision,
        "down_recall": recall,
        "false_down_fpr": fpr,
        "down_call_coverage": down_calls / n if n else None,
        "wilson90_lcb_down_precision": wilson_lcb(correct, down_calls) if down_calls else None,
    }


def eligible(m: dict) -> bool:
    return bool(
        m["down_calls"] >= 5
        and m["down_precision"] is not None
        and m["down_precision"] > 0.50
        and m["false_down_fpr"] is not None
        and m["false_down_fpr"] < 0.50
    )


def select_candidate(metrics: list[dict]) -> str | None:
    em = [m for m in metrics if eligible(m)]
    if not em:
        return None
    em.sort(key=lambda m: (
        -m["wilson90_lcb_down_precision"],
        m["false_down_fpr"],
        -m["down_precision"],
        -m["down_recall"],
        CANDIDATE_ORDER[m["candidate"]],
    ))
    return em[0]["candidate"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqrt-parent", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    days = load_days()
    tdays, bdays, ldays, daily = transformed(days)
    trows = ttsm_mod.build_signal_rows(tdays)
    tmap = {r["target_date"]: r for r in trows}
    bmaps = bonato_maps(bdays)
    lmaps = logit_maps(ldays)
    contexts = legacy_context(daily)
    router = build_router_rows(trows, bmaps, lmaps, contexts)
    router_map = {(r["origin_date"], r["target_date"]): r for r in router}

    integrity = []

    # Frozen Router V2 reproduction.
    router_summary = {}
    for y in (2022, 2023, 2024, 2025):
        rr = [r for r in router if int(r["target_date"][:4]) == y]
        up = [r for r in rr if r["router_up"] == 1]
        tp = sum(r["actual_up"] == 1 for r in up)
        fp = sum(r["actual_up"] == 0 for r in up)
        selected = Counter(r["selected_expert"] for r in up)
        router_summary[str(y)] = {
            "n": len(rr), "router_up": len(up), "tp": tp, "fp": fp,
            "selected_counts": dict(selected),
        }
        exp = EXPECTED_ROUTER[y]
        if len(up) != exp["up"]:
            integrity.append(f"ROUTER_UP_{y}:{len(up)}!={exp['up']}")
        if "tp" in exp and tp != exp["tp"]:
            integrity.append(f"ROUTER_TP_{y}:{tp}!={exp['tp']}")
        if "fp" in exp and fp != exp["fp"]:
            integrity.append(f"ROUTER_FP_{y}:{fp}!={exp['fp']}")
        if y == 2025 and selected.get("RM_LOGIT", 0) != exp["selected_rm"]:
            integrity.append(f"ROUTER_2025_RM_SELECTED:{selected.get('RM_LOGIT',0)}!={exp['selected_rm']}")

    sqrt = load_sqrt(args.sqrt_parent)
    for y, expected in EXPECTED_SQRT.items():
        n = sum(r["evaluation_year"] == y for r in sqrt)
        if n != expected:
            integrity.append(f"SQRT_ALARM_{y}:{n}!={expected}")

    aligned = []
    for s in sqrt:
        rr = router_map.get((s["origin_date"], s["target_date"]))
        if rr is None:
            integrity.append(f"ROUTER_ROW_NOT_FOUND:{s['origin_date']}->{s['target_date']}")
            continue
        if int(rr["actual_up"]) != int(s["actual_up"]):
            integrity.append(f"ACTUAL_SIGN_MISMATCH:{s['target_date']}")
            continue
        z = dict(s)
        z["router_up"] = int(rr["router_up"])
        z["router_selected_expert"] = rr["selected_expert"]
        aligned.append(z)

    overlap_expected = {
        2022: (0, 0, 0),
        2023: (0, 0, 0),
        2024: (4, 3, 1),
    }
    for y, (nexp, upexp, dnexp) in overlap_expected.items():
        ar = [r for r in aligned if r["evaluation_year"] == y and r["router_up"] == 1]
        au = sum(r["actual_up"] == 1 for r in ar)
        ad = sum(r["actual_up"] == 0 for r in ar)
        if (len(ar), au, ad) != (nexp, upexp, dnexp):
            integrity.append(f"SQRT_ROUTER_OVERLAP_{y}:{len(ar)}/{au}/{ad}!={nexp}/{upexp}/{dnexp}")

    # 2025 exact intersection aggregate from frozen countersign result.
    r25 = [r for r in aligned if r["evaluation_year"] == 2025 and r["router_up"] == 1]
    if len(r25) != 16 or sum(r["actual_up"] == 1 for r in r25) != 10 or sum(r["actual_up"] == 0 for r in r25) != 6:
        integrity.append("SQRT_ROUTER_OVERLAP_2025_MISMATCH")

    pre = [
        r for r in aligned
        if r["evaluation_year"] in (2022, 2023, 2024) and r["router_up"] == 0
    ]
    if len(pre) != 26:
        integrity.append(f"PRE2025_ABSTAIN_N:{len(pre)}!=26")
    pre_down = sum(r["actual_up"] == 0 for r in pre)
    pre_up = sum(r["actual_up"] == 1 for r in pre)
    if (pre_down, pre_up) != (13, 13):
        integrity.append(f"PRE2025_ABSTAIN_DIR:{pre_down}/{pre_up}!=13/13")

    pre_metrics = [candidate_metrics(pre, c, tmap, bmaps, lmaps) for c in CANDIDATES]
    selected = None if integrity else select_candidate(pre_metrics)

    stress25 = [r for r in aligned if r["evaluation_year"] == 2025 and r["router_up"] == 0]
    if len(stress25) != 74:
        integrity.append(f"LOCKED2025_ABSTAIN_N:{len(stress25)}!=74")

    transport = None
    if selected is not None and not integrity:
        transport = candidate_metrics(stress25, selected, tmap, bmaps, lmaps)
        baseline25 = (
            sum(r["actual_up"] == 0 for r in stress25) / len(stress25)
            if stress25 else None
        )
        transport["abstain_subset_down_prevalence"] = baseline25
        transport["precision_lift_vs_down_prevalence"] = (
            transport["down_precision"] - baseline25
            if transport["down_precision"] is not None and baseline25 is not None
            else None
        )
        supportive = bool(
            transport["down_calls"] >= 5
            and transport["down_precision"] is not None
            and baseline25 is not None
            and transport["down_precision"] > baseline25
            and transport["false_down_fpr"] is not None
            and transport["false_down_fpr"] < 0.50
        )
    else:
        supportive = False

    if integrity:
        status = "BLOCKED_INTEGRITY_MISMATCH"
    elif selected is None:
        status = "NO_EXISTING_DOWN_CANDIDATE_ELIGIBLE"
    elif supportive:
        status = "PRE2025_DOWN_CANDIDATE_SELECTED_2025_TRANSPORT_SUPPORTIVE"
    else:
        status = "PRE2025_DOWN_CANDIDATE_SELECTED_2025_TRANSPORT_WEAK"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-23",
        "status": status,
        "candidate_pool": CANDIDATES,
        "candidate_selection_rule": {
            "min_down_calls": 5,
            "down_precision_gt": 0.50,
            "false_down_fpr_lt": 0.50,
            "rank": [
                "higher one-sided 90% Wilson LCB DOWN precision",
                "lower false-DOWN FPR",
                "higher raw DOWN precision",
                "higher DOWN recall",
                "fixed candidate order",
            ],
        },
        "integrity_errors": integrity,
        "router_reconstruction": router_summary,
        "primary_2022_2024_abstain_subset": {
            "n": len(pre),
            "actual_down": pre_down,
            "actual_up": pre_up,
            "baseline_down_prevalence": pre_down / len(pre) if pre else None,
            "candidate_metrics": pre_metrics,
            "selected_candidate": selected,
        },
        "locked_2025_selected_candidate_transport": transport,
        "governance": {
            "random_split": False,
            "threshold_tuning": False,
            "2025_used_for_selection": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
        },
    }

    result_path = args.out / "GOLD_CONTROL_DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESULT_2026-09-23.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Pre-2025 row-level candidate ledger.
    pre_fields = [
        "evaluation_year", "origin_date", "target_date", "actual_up",
        "actual_high_risk", "sqrt_score", "router_up", "router_selected_expert",
    ]
    for c in CANDIDATES:
        pre_fields += [f"{c}_down", f"{c}_score"]
    with (args.out / "GOLD_CONTROL_DOWN_VERIFIER_CANDIDATE_AUDIT_V1_PRE2025_LEDGER_2026-09-23.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=pre_fields)
        w.writeheader()
        for r in pre:
            z = {k: r.get(k, "") for k in pre_fields[:8]}
            for c in CANDIDATES:
                d, s = candidate_down_value(c, r["target_date"], tmap, bmaps, lmaps)
                z[f"{c}_down"] = "" if d is None else d
                z[f"{c}_score"] = "" if s is None else s
            w.writerow(z)

    # Locked 2025 ledger exposes only the pre-2025-selected candidate.
    if selected is not None and not integrity:
        fields25 = [
            "evaluation_year", "origin_date", "target_date", "actual_up",
            "actual_high_risk", "sqrt_score", "router_up", "router_selected_expert",
            "selected_down_candidate", "selected_candidate_down", "selected_candidate_score",
        ]
        with (args.out / "GOLD_CONTROL_DOWN_VERIFIER_CANDIDATE_AUDIT_V1_LOCKED2025_LEDGER_2026-09-23.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields25)
            w.writeheader()
            for r in stress25:
                d, s = candidate_down_value(selected, r["target_date"], tmap, bmaps, lmaps)
                z = {k: r.get(k, "") for k in fields25[:8]}
                z.update({
                    "selected_down_candidate": selected,
                    "selected_candidate_down": "" if d is None else d,
                    "selected_candidate_score": "" if s is None else s,
                })
                w.writerow(z)

    lines = [
        "# GOLD CONTROL — DOWN VERIFIER CANDIDATE AUDIT V1 RESULT",
        "",
        f"**Status:** `{status}`",
        f"**Integrity errors:** {integrity if integrity else 'none'}",
        "",
        "## Primary 2022–2024 SQRT alarm + Router V2 ABSTAIN subset",
        "",
        f"- n={len(pre)}; actual DOWN={pre_down}; actual UP={pre_up}.",
        "",
        "| Candidate | DOWN calls | Correct | False | Precision | DOWN recall | False-DOWN FPR | Wilson90 LCB | Eligible |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for m in pre_metrics:
        lines.append(
            f"| {m['candidate']} | {m['down_calls']} | {m['correct_down']} | {m['false_down']} | "
            f"{m['down_precision']} | {m['down_recall']} | {m['false_down_fpr']} | "
            f"{m['wilson90_lcb_down_precision']} | {eligible(m)} |"
        )
    lines += ["", f"**Selected pre-2025 candidate:** {selected or 'NONE'}", ""]
    if transport is not None:
        lines += [
            "## Locked 2025 transport of selected candidate",
            "",
            f"- Candidate: {selected}",
            f"- Subset n: {transport['subset_n']}",
            f"- DOWN calls: {transport['down_calls']}",
            f"- Correct / false DOWN: {transport['correct_down']} / {transport['false_down']}",
            f"- DOWN precision: {transport['down_precision']}",
            f"- DOWN recall: {transport['down_recall']}",
            f"- False-DOWN FPR: {transport['false_down_fpr']}",
            f"- Abstain-subset DOWN prevalence: {transport['abstain_subset_down_prevalence']}",
            f"- Precision lift vs prevalence: {transport['precision_lift_vs_down_prevalence']}",
            "",
        ]
    lines += [
        "No threshold was changed and 2025 did not participate in candidate selection.",
        "No runtime or production authority is created.",
    ]
    (args.out / "GOLD_CONTROL_DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESULT_2026-09-23.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "integrity_errors": integrity,
        "selected_candidate": selected,
        "pre2025_metrics": pre_metrics,
        "locked_2025_transport": transport,
    }, indent=2))
    return 0 if not integrity else 2


if __name__ == "__main__":
    raise SystemExit(main())
