from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

IDENTITY = "DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESEARCH"
PRE_YEARS = (2022, 2023, 2024)
SQRT_WINDOWS = tuple(range(250, 1001, 25))
ROUTER_WINDOWS = tuple(range(30, 501, 10))
UP2_WINDOWS = tuple(range(60, 100, 5))
EPS = 1e-14


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"MODULE_LOAD_FAILED:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def yr(s: str) -> int:
    return int(str(s)[:4])


def nearest_rank(a, q: float) -> float:
    a = np.asarray(a, dtype=float)
    if len(a) == 0:
        raise RuntimeError("EMPTY_QUANTILE")
    k = max(1, min(len(a), int(math.ceil(q * len(a)))))
    return float(np.sort(a)[k - 1])


def qloss(y: float, f: float) -> float:
    yy = max(float(y), EPS)
    ff = max(float(f), EPS)
    z = yy / ff
    return z - math.log(z) - 1.0


def auc_safe(y, score):
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, score))


def build_sqrt_rows(days):
    days = sorted(days, key=lambda x: x.d)
    dr = np.asarray([float(x.dr) for x in days], dtype=float)
    close = np.asarray([float(x.close) for x in days], dtype=float)
    sd = np.sqrt(dr)
    out = []
    for i in range(21, len(days) - 1):
        t = i + 1
        if close[i] <= 0 or close[t] <= 0:
            continue
        out.append({
            "origin_date": days[i].d.isoformat(),
            "target_date": days[t].d.isoformat(),
            "sd_d": float(sd[i]),
            "sd_w": float(np.mean(sd[i-4:i+1])),
            "sd_m": float(np.mean(sd[i-21:i+1])),
            "target_dr": float(dr[t]),
            "target_return": float(math.log(close[t] / close[i])),
        })
    return out


def sqrt_eval(rows, year: int, window: int | None):
    cutoff = date(year - 1, 12, 31)
    train_all = [r for r in rows if date.fromisoformat(r["target_date"]) <= cutoff]
    test = [r for r in rows if yr(r["target_date"]) == year]
    if window is not None:
        if len(train_all) < window:
            return {"status": "INFEASIBLE_WINDOW", "train_available": len(train_all), "test_n": len(test)}
        train = train_all[-window:]
    else:
        train = train_all
    if len(train) < 250 or not test:
        return {"status": "INFEASIBLE_WINDOW", "train_available": len(train), "test_n": len(test)}
    X = np.asarray([[1.0, r["sd_d"], r["sd_w"], r["sd_m"]] for r in train], dtype=float)
    ysd = np.sqrt(np.asarray([r["target_dr"] for r in train], dtype=float))
    beta = np.linalg.lstsq(X, ysd, rcond=None)[0]
    Xt = np.asarray([[1.0, r["sd_d"], r["sd_w"], r["sd_m"]] for r in test], dtype=float)
    sp = Xt @ beta
    if np.any(~np.isfinite(sp)) or np.any(sp <= 0):
        return {"status": "NONPOSITIVE_SD_FORECAST", "train_n": len(train), "test_n": len(test)}
    pred = sp * sp
    y = np.asarray([r["target_dr"] for r in test], dtype=float)
    train_dr = np.asarray([r["target_dr"] for r in train], dtype=float)
    q80 = nearest_rank(train_dr, 0.80)
    high = (y >= q80).astype(int)
    alerts = pred >= q80
    tp = int(np.sum(alerts & (high == 1)))
    fp = int(np.sum(alerts & (high == 0)))
    fn = int(np.sum((~alerts) & (high == 1)))
    tn = int(np.sum((~alerts) & (high == 0)))
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    mean_dr = float(np.mean(train_dr))
    mse = float(np.mean((pred - y) ** 2))
    mean_mse = float(np.mean((mean_dr - y) ** 2))
    qlike = float(np.mean([qloss(a, b) for a, b in zip(y, pred)]))
    return {
        "status": "OK",
        "year": year,
        "train_n": len(train),
        "train_available": len(train_all),
        "test_n": len(test),
        "mse": mse,
        "qlike": qlike,
        "oos_r2_vs_train_mean": float(1 - mse / mean_mse) if mean_mse > 0 else None,
        "high_risk_auc": auc_sade(high, pred),
        "alert_count": int(np.sum(alerts)),
        "alert_coverage": float(np.mean(alerts)),
        "alert_precision": precision,
        "alert_recall": recall,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "q80": q80,
        "beta": [float(x) for x in beta],
    }


def pooled_sqrt(year_metrics):
    oks = [m for m in year_metrics if m.get("status") == "OK"]
    if len(oks) != len(PRE_YEARS):
        return {"status": "INCOMPLETE", "years_ok": len(oks)}
    n = sum(int(m["test_n"]) for m in oks)
    return {
        "status": "OK",
        "n": n,
        "pooled_mse": float(sum(m["mse"] * m["test_n"] for m in oks) / n),
        "pooled_qlike": float(sum(m["qlike"] * m["test_n"] for m in oks) / n),
        "mean_annual_auc": float(np.mean([m["high_risk_auc"] for m in oks if m["high_risk_auc"] is not None])),
        "total_alerts": int(sum(m["alert_count"] for m in oks)),
        "mean_alert_precision": float(np.mean([m["alert_precision"] for m in oks if m["alert_precision"] is not None])),
        "mean_alert_recall": float(np.mean([m["alert_recall"] for m in oks if m["alert_recall"] is not None])),
    }


def router_base_rows(base, days):
    tdays, bdays, ldays, daily = base.transformed(days)
    trows = base.ttsm_mod.build_signal_rows(tdays)
    tmap = {r["target_date"]: r for r in trows}
    bmaps = base.bonato_maps(bdays)
    lmaps = base.logit_maps(ldays)
    contexts = base.legacy_context(daily)
    common = sorted(
        set(tmap)
        & set(bmaps["BONATO_AR1_RM_QBOOST_H1"])
        & set(lmaps["AR1_RM_LOGIT"])
        & set(lmaps["RM_LOGIT"])
    )
    rows = []
    for td in common:
        t = tmap[td]
        b = bmaps["BONATO_AR1_RM_QBOOST_H1"][td]
        ar = lmaps["AR1_RM_LOGIT"][td]
        rm = lmaps["RM_LOGIT"][td]
        od = t["origin_date"]
        vals = [int(t["actual_up"]), int(b["actual_up"]), int(ar["actual_up"]), int(rm["actual_up"])]
        if not (od == b["origin_date"] == ar["origin_date"] == rm["origin_date"]) or len(set(vals)) != 1:
            raise RuntimeError(f"ROUTER_BASE_ALIGNMENT_FAIL:{td}")
        rows.append({
            "origin_date": od,
            "target_date": td,
            "actual_up": vals[0],
            "TTSM_S2": int(t["ttsm_s2_signal"] == 1),
            "TTSM_S1": int(t["ttsm_s1_signal"] == 1),
            "BONATO_AR1_RM_QBOOST_H1": int(b["up"]),
            "AR1_RM_LOGIT": int(ar["up"]),
            "RM_LOGIT": int(rm["up"]),
            **contexts[od],
        })
    return rows


def router_score_one(base, eval_rows, initial_history, mode: str, window: int | None = None):
    hist = [dict(r) for r in sorted(initial_history, key=lambda z: z["target_date"])]
    scored = []
    for row0 in sorted(eval_rows, key=lambda z: z["target_date"]):
        if mode == "ROLLING":
            use_hist = hist[-window:] if window is not None else hist
        else:
            use_hist = hist
        candidates = []
        for expert in base.DIRECT_UP_EXPERTS:
            if int(row0[expert]) != 1:
                continue
            st = base.router_stats(use_hist, expert, row0["legacy_bucket"])
            if st is None:
                continue
            if st["n_up"] < 30 or st["precision"] <= 0.50 or st["fpr"] >= 0.50:
                continue
            candidates.append((expert, st))
        row = dict(row0)
        if candidates:
            candidates.sort(key=lambda x: (
                -x[1]["lcb"], x[1]["fpr"], -x[1]["precision"], base.ROUTER_TIE_ORDER[x[0]]
            ))
            selected, st = candidates[0]
            row["router_up"] = 1
            row["selected_expert"] = selected
        else:
            row["router_up"] = 0
            row["selected_expert"] = ""
        scored.append(row)
        hist.append(dict(row0))
    return scored


def router_metrics(rows):
    n = len(rows)
    calls = [r for r in rows if int(r["router_up"]) == 1]
    tp = sum(int(r["actual_up"]) == 1 for r in calls)
    fp = len(calls) - tp
    actual_up = sum(int(r["actual_up"]) == 1 for r in rows)
    actual_down = n - actual_up
    precision = tp / len(calls) if calls else None
    fpr = fp / actual_down if actual_down else None
    recall = tp / actual_up if actual_up else None
    return {
        "n": n,
        "calls": len(calls),
        "tp": tp,
        "fp": fp,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "precision": precision,
        "false_up_fpr": fpr,
        "actual_up_recall": recall,
        "coverage": len(calls) / n if n else None,
        "wilson90_lcb_precision": base_wilson(tp, len(calls)),
        "selected_counts": dict(Counter(r["selected_expert"] for r in calls)),
    }


def base_wilson(k, n):
    if n <= 0:
        return None
    z = 1.2815515655446004
    p = k / n
    den = 1 + z*z/n
    center = p + z*z/(2*n)
    rad = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (center-rad)/den


def score_router_policy(base, ext_rows, gov_rows, policy: str, window: int | None):
    out = []
    for year in PRE_YEARS:
        ev = [r for r in gov_rows if yr(r["target_date"]) == year]
        if policy == "FROZEN_YEAR_RESET":
            hist = [r for r in gov_rows if yr(r["target_date"]) == year - 1]
            scored = router_score_one(base, ev, hist, "EXPANDING")
        else:
            hist = [r for r in ext_rows if yr(r["target_date"]) in (2020, 2021)]
            hist += [r for r in gov_rows if yr(r["target_date"]) < year and yr(r["target_date"]) >= 2022]
            scored = router_score_one(base, ev, hist, "ROLLING" if policy == "ROLLING" else "EXPANDING", window)
        m = router_metrics(scored)
        m["year"] = year
        out.append(m)
    pooled_rows = []
    # Re-score to retain exact policy chronology separately by year, matching frozen historical-study semantics.
    for year in PRE_YEARS:
        ev = [r for r in gov_rows if yr(r["target_date"]) == year]
        if policy == "FROZEN_YEAR_RESET":
            hist = [r for r in gov_rows if yr(r["target_date"]) == year - 1]
            pooled_rows.extend(router_score_one(base, ev, hist, "EXPANDING"))
        else:
            hist = [r for r in ext_rows if yr(r["target_date"]) in (2020, 2021)]
            hist += [r for r in gov_rows if yr(r["target_date"]) < year and yr(r["target_date"]) >= 2022]
            pooled_rows.extend(router_score_one(base, ev, hist, "ROLLING" if policy == "ROLLING" else "EXPANDING", window))
    return out, router_metrics(pooled_rows)


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k); keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            z = dict(r)
            for k, v in list(z.items()):
                if isinstance(v, (dict, list, tuple)):
                    z[k] = json.dumps(v, sort_keys=True)
            w.writerow(z)


def descriptive_surface_summary(sqrt_surface, router_surface, up2_surface):
    sqrt_pool = [r for r in sqrt_surface if r.get("year") == "POOLED_2022_2024" and r.get("status") == "OK"]
    router_pool = [r for r in router_surface if r.get("year") == "POOLED_2022_2024"]
    up2_pool = [r for r in up2_surface if r.get("year") == "POOLED_2022_2024" and r.get("status") == "OK"]

    def pick(rows, key, reverse=False):
        vals = [r for r in rows if r.get(key) is not None]
        if not vals:
            return None
        z = max(vals, key=lambda r: float(r[key])) if reverse else min(vals, key=lambda r: float(r[key]))
        return {"policy": z.get("policy"), "window": z.get("window"), key: z.get(key)}

    supportive = [
        {"policy": r.get("policy"), "window": r.get("window"),
         "precision": r.get("up_precision"), "fpr": r.get("false_up_fpr"),
         "coverage": r.get("coverage"), "lcb": r.get("wilson90_lcb_up_precision")}
        for r in up2_pool if bool(r.get("pre2025_supportive"))
    ]
    return {
        "sqrt_descriptive_extrema_not_selection": {
            "lowest_pooled_mse": pick(sqrt_pool, "pooled_mse"),
            "lowest_pooled_qlike": pick(sqrt_pool, "pooled_qlike"),
            "highest_mean_annual_auc": pick(sqrt_pool, "mean_annual_auc", reverse=True),
            "eligible_policy_count": len(sqrt_pool),
        },
        "router_descriptive_extrema_not_selection": {
            "highest_precision": pick(router_pool, "precision", reverse=True),
            "lowest_false_up_fpr": pick(router_pool, "false_up_fpr"),
            "highest_wilson90_lcb": pick(router_pool, "wilson90_lcb_precision", reverse=True),
            "eligible_policy_count": len(router_pool),
        },
        "up2_existing_gate": {
            "supportive_policy_count": len(supportive),
            "supportive_policies": supportive,
            "eligible_policy_count": len(up2_pool),
        },
        "warning": "Extrema are descriptive only. V1 does not promote a history policy or use 2025/2026.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--external-spine", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--sqrt-code", type=Path, required=True)
    ap.add_argument("--route-module", type=Path, required=True)
    ap.add_argument("--base-module", type=Path, required=True)
    ap.add_argument("--cbr-code", type=Path, required=True)
    ap.add_argument("--up2-code", type=Path, required=True)
    ap.add_argument("--sqrt-parent", type=Path, required=True)
    ap.add_argument("--pre-ledger", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    route = load_mod("route_authority", args.route_module)
    base = load_mod("base_authority", args.base_module)
    cbr = load_mod("cbr_authority", args.cbr_code)
    sqrt_mod = load_mod("sqrt_authority", args.sqrt_code)
    up2 = load_mod("up2_authority", args.up2_code)

    ext_spine = route.load_external_spine(args.external_spine)
    ext_days = route.load_external_daily_for_sqrt(ext_spine)
    gov_base_days = base.load_days()
    _, _, _, gov_daily = base.transformed(gov_base_days)

    integrity = []

    # Frozen governed SQRT reproduction gate.
    frozen_sqrt_counts = {}
    for y, expected in {2022: 11, 2023: 2, 2024: 17}.items():
        rr = sqrt_mod.sqrt_rows(gov_daily, y)
        n = sum(int(r["sqrt_alarm"]) == 1 for r in rr)
        frozen_sqrt_counts[str(y)] = n
        if n != expected:
            integrity.append(f"SQRT_{y}:{n}!={expected}")

    # SQRT robustness surface. Keep the exact governed expanding baseline beside
    # the extended-source policies so source extension and window memory are not conflated.
    governed_rows = build_sqrt_rows(gov_daily)
    sqrt_surface = []
    governed_annual = [sqrt_eval(governed_rows, y, None) for y in PRE_YEARS]
    governed_pooled = pooled_sqrt(governed_annual)
    for m in governed_annual:
        sqrt_surface.append({"policy": "GOVERNED_FROZEN_EXPANDING", "window": "EXPANDING", **m})
    sqrt_surface.append({"policy": "GOVERNED_FROZEN_EXPANDING", "window": "EXPANDING",
                         "year": "POOLED_2022_2024", **governed_pooled})

    ext_pre = [d for d in ext_days if d.d <= date(2021, 12, 31)]
    gov_post = [d for d in gov_daily if d.d >= date(2022, 1, 1)]
    combined_days = ext_pre + gov_post
    combined_rows = build_sqrt_rows(combined_days)
    for label, window in [("EXTENDED_EXPANDING", None)] + [(f"EXTENDED_ROLLING_{w}", w) for w in SQRT_WINDOWS]:
        annual = [sqrt_eval(combined_rows, y, window) for y in PRE_YEARS]
        pooled = pooled_sqrt(annual)
        for m in annual:
            sqrt_surface.append({"policy": label, "window": "EXPANDING" if window is None else window, **m})
        sqrt_surface.append({"policy": label, "window": "EXPANDING" if window is None else window, "year": "POOLED_2022_2024", **pooled})

    # Router base rows and frozen reproduction gate.
    ext_base_days = route.external_base_days(base, ext_spine)
    ext_router_base = router_base_rows(base, ext_base_days)
    gov_router_base = router_base_rows(base, gov_base_days)
    frozen_router = []
    router_surface = []
    frozen_expected = {2022:(22,12,10), 2023:(19,5,14), 2024:(42,26,16)}
    annual, pooled = score_router_policy(base, ext_router_base, gov_router_base, "FROZEN_YEAR_RESET", None)
    for m in annual:
        frozen_router.append(m)
        exp = frozen_expected[m["year"]]
        if m["calls"] != exp[0]: integrity.append(f"ROUTER_CALLS_{m['year']}:{m['calls']}!={exp[0]}")
        if exp[1] is not None and m["tp"] != exp[1]: integrity.append(f"ROUTER_TP_{m['year']}:{m['tp']}!={exp[1]}")
        if exp[2] is not None and m["fp"] != exp[2]: integrity.append(f"ROUTER_FP_{m['year']}:{m['fp']}!={exp[2]}")
        router_surface.append({"policy":"FROZEN_YEAR_RESET","window":"YEAR_RESET",**m})
    router_surface.append({"policy":"FROZEN_YEAR_RESET","window":"YEAR_RESET","year":"POOLED_2022_2024",**pooled})

    for policy, window in [("EXPANDING", None)] + [("ROLLING", w) for w in ROUTER_WINDOWS]:
        annual, pooled = score_router_policy(base, ext_router_base, gov_router_base, policy, window)
        label = "EXPANDING" if window is None else f"ROLLING_{window}"
        for m in annual:
            router_surface.append({"policy":label,"window":"EXPANDING" if window is None else window,**m})
        router_surface.append({"policy":label,"window":"EXPANDING" if window is None else window,"year":"POOLED_2022_2024",**pooled})

    # UP2 exact formation / route reconstruction.
    ext_raw = route.build_external_5m(args.raw_root)
    ext_audit = route.external_reconstruction_audit(ext_raw, ext_spine)
    if not ext_audit.get("passed"):
        integrity.append("EXTERNAL_RECONSTRUCTION_FAIL")
    ext_sqrt, ext_sqrt_summary = route.external_sqrt_cases(sqrt_mod, ext_days)
    ext_router_scored, ext_router_summary = route.external_router_rows(base, ext_spine)
    ext_unresolved, ext_route_summary = route.route_external_sqrt_cases(ext_sqrt, ext_router_scored)
    ext_router_map = {(r["origin_date"], r["target_date"]): r for r in ext_router_scored}
    ext_sqrt_map = {(r["origin_date"], r["target_date"]): r for r in ext_sqrt}
    ext_lag = up2.lag_map_from_spine(ext_spine)
    external_cases = []
    for r in ext_unresolved:
        key = (r["origin_date"], r["target_date"])
        rr = ext_router_map[key]; sr = ext_sqrt_map[key]
        external_cases.append(up2.enrich_case(
            r, sr["sqrt_normalized_risk_score"], rr, ext_lag[r["origin_date"]],
            ext_raw[r["origin_date"]]["rets"], "EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
        ))
    if len(external_cases) != 98 or sum(r["actual_up"] for r in external_cases) != 46:
        integrity.append(f"UP2_EXTERNAL_FORMATION:{len(external_cases)}/{sum(r['actual_up'] for r in external_cases)}")

    gov_raw = cbr.load_paths(["2020-01-02", "2025-12-31"])
    parent = up2.load_parent(args.sqrt_parent)
    parent_map = {(r["origin_date"], r["target_date"]): r for r in parent}
    gov_router_scored = up2.build_governed_router_rows(base, gov_base_days)
    gov_router_map = {(r["origin_date"], r["target_date"]): r for r in gov_router_scored}
    gov_lag = up2.lag_map_from_base_days(gov_base_days)
    pre = route.load_pre_unresolved(args.pre_ledger)
    expected_pre = {2022:(11,5), 2023:(2,1), 2024:(13,7)}
    pre_cases = []
    for y, (n,u) in expected_pre.items():
        sub = [r for r in pre if int(r["evaluation_year"]) == y]
        if len(sub) != n or sum(int(r["actual_up"]) for r in sub) != u:
            integrity.append(f"UP2_PRE_ROUTE_{y}:{len(sub)}/{sum(int(r['actual_up']) for r in sub)}")
    for r in pre:
        key = (r["origin_date"], r["target_date"])
        pr = parent_map.get(key); rr = gov_router_map.get(key)
        if pr is None or rr is None:
            integrity.append(f"UP2_FEATURE_JOIN:{key}"); continue
        pre_cases.append(up2.enrich_case(
            r, pr["sqrt_score"], rr, gov_lag[r["origin_date"]], gov_raw[r["origin_date"]],
            "GOVERNED_ROUTER_ABSTAIN"
        ))

    up2_surface = []
    all_hist = external_cases + pre_cases
    def run_up2_policy(label, window):
        scored_all = []
        annual = []
        blocked = False
        for y in PRE_YEARS:
            train = [r for r in all_hist if int(r["evaluation_year"]) < y]
            train.sort(key=lambda z:z["target_date"])
            if window is not None:
                if len(train) < window:
                    annual.append({"year":y,"status":"INFEASIBLE_WINDOW","train_available":len(train)})
                    blocked = True; continue
                train = train[-window:]
            test = [r for r in pre_cases if int(r["evaluation_year"]) == y]
            scored, m = up2.score_year(train, test, y)
            annual.append(m); scored_all.extend(scored)
            if m.get("status") != "OK": blocked = True
        for m in annual:
            up2_surface.append({"policy":label,"window":"EXPANDING" if window is None else window,**m})
        if not blocked and len(scored_all) == 26:
            pooled = up2.pooled_metrics(scored_all)
            support = bool(
                pooled["n"] == 26 and pooled["up2_calls"] >= 4
                and pooled["up_precision"] is not None and pooled["up_precision"] > 0.50
                and pooled["wilson90_lcb_up_precision"] is not None and pooled["wilson90_lcb_up_precision"] > 0.50
                and pooled["false_up_fpr"] is not None and pooled["false_up_fpr"] <= 0.25
            )
            up2_surface.append({"policy":label,"window":"EXPANDING" if window is None else window,"year":"POOLED_2022_2024","status":"OK","pre2025_supportive":support,**pooled})
            return pooled, support
        up2_surface.append({"policy":label,"window":"EXPANDING" if window is None else window,"year":"POOLED_2022_2024","status":"BLOCKED_OR_INCOMPLETE"})
        return None, False

    frozen_pooled, frozen_support = run_up2_policy("EXPANDING_FROZEN", None)
    if frozen_pooled is None or frozen_pooled.get("up2_calls") != 11 or frozen_pooled.get("true_up") != 8 or frozen_pooled.get("false_up") != 3:
        integrity.append(f"UP2_FROZEN_POOLED:{frozen_pooled}")
    for w in UP2_WINDOWS:
        run_up2_policy(f"ROLLING_{w}", w)

    status = "ROBUSTNESS_SURFACE_COMPLETE" if not integrity else "BLOCKED_BASELINE_REPRODUCTION"

    write_csv(args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_SQRT_SURFACE_2026-09-24.csv", sqrt_surface)
    write_csv(args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_ROUTER_SURFACE_2026-09-24.csv", router_surface)
    write_csv(args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_UP2_SURFACE_2026-09-24.csv", up2_surface)

    surface_summary = descriptive_surface_summary(sqrt_surface, router_surface, up2_surface)

    result = {
        "identity": IDENTITY,
        "status": status,
        "integrity_errors": integrity,
        "governance": {
            "2025_used": False,
            "2026_used": False,
            "random_split": False,
            "runtime_write": False,
            "production_write": False,
            "model_feature_changes": False,
        },
        "baseline_reproduction": {
            "sqrt_alarm_counts": frozen_sqrt_counts,
            "router": frozen_router,
            "up2_external_n": len(external_cases),
            "up2_external_up": sum(r["actual_up"] for r in external_cases),
            "up2_frozen_pooled": frozen_pooled,
            "up2_frozen_supportive": frozen_support,
        },
        "source": {
            "external_reconstruction": ext_audit,
            "external_sqrt_summary": ext_sqrt_summary,
            "external_router_summary": ext_router_summary,
            "external_route_summary": ext_route_summary,
        },
        "surface_counts": {
            "sqrt_rows": len(sqrt_surface),
            "router_rows": len(router_surface),
            "up2_rows": len(up2_surface),
        },
        "descriptive_surface_summary": surface_summary,
        "interpretation_rule": "V1 maps the pre-2025 surface only; it does not select an optimal window or replay 2025.",
    }
    (args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESULT_2026-09-24.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# GOLD CONTROL — Direction Engine Estimation-Window Robustness V1", "",
        f"**Status:** `{status}`", "",
        "This V1 maps pre-2025 history-window sensitivity only. 2025/2026 were not loaded for scoring or selection.", "",
        "## Baseline reproduction", "",
        f"- SQRT alarms 2022/2023/2024: {frozen_sqrt_counts}",
        f"- Router frozen yearly summaries: {json.dumps(frozen_router, sort_keys=True)}",
        f"- UP-2 external formation: n={len(external_cases)}, UP={sum(r['actual_up'] for r in external_cases)}",
        f"- UP-2 pooled frozen: {json.dumps(frozen_pooled, sort_keys=True) if frozen_pooled else 'BLOCKED'}", "",
        "## Interpretation", "",
        "No best window is declared by this run. Use the CSV surfaces to assess broad neighboring stability versus isolated spikes. Structural-break-conditioned estimation is reserved for a separately preregistered follow-up.", "",
        "## Governance", "",
        "No random split, no 2025/2026 selection, no DB write, no runtime promotion, no model feature or threshold rule change.",
    ]
    if integrity:
        md += ["", "## Integrity errors", ""] + [f"- {x}" for x in integrity]
    (args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESULT_2026-09-24.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "integrity_errors": integrity, "surface_counts": result["surface_counts"]}, sort_keys=True))
    return 0 if not integrity else 2


if __name__ == "__main__":
    raise SystemExit(main())
