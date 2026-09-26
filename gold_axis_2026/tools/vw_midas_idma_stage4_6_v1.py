from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_dma_batch1_v1 as dma

HIST_START = "2019-01"
DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

SELECTOR_VARIANTS = (
    ("AE_PRICE", 12),
    ("AE_PRICE", 24),
    ("AE_PRICE", None),
    ("MSFE_LOGRET", 12),
    ("MSFE_LOGRET", 24),
    ("MSFE_LOGRET", None),
)

def candidate_rows(bundle, cache, lane):
    targets = list(base.month_range(HIST_START, ST_END))
    raw = dma.evaluate_lane(bundle, cache, targets, lane)
    # IDMA is an extension of DMA, so only DMA candidate forecasts are eligible.
    return {k: v for k, v in raw.items() if "__DMA__" in k}

def actual_log_return(bundle, target):
    p = base.month_shift(target, -1)
    return math.log(float(bundle.monthly_metal["Gold"][target]) / float(bundle.monthly_metal["Gold"][p]))

def score_rows(bundle, rows, objective):
    if not rows:
        return float("inf")
    if objective == "AE_PRICE":
        return float(sum(abs(r["forecast"] - r["actual"]) for r in rows))
    if objective == "MSFE_LOGRET":
        e = np.array([r["pred_log_return_gold"] - actual_log_return(bundle, r["target"]) for r in rows], float)
        return float(np.mean(e * e))
    raise ValueError(objective)

def history_targets(end_exclusive, window):
    xs = [t for t in base.month_range(HIST_START, base.month_shift(end_exclusive, -1))]
    if window is not None:
        xs = xs[-window:]
    return xs

def choose_config(bundle, candidates, target, objective, window):
    hist = history_targets(target, window)
    if len(hist) < 12:
        raise RuntimeError(f"IDMA_SELECTOR_HISTORY_TOO_SHORT target={target} n={len(hist)}")
    ranked = []
    for name, rows in candidates.items():
        by_t = {r["target"]: r for r in rows}
        selected = [by_t[t] for t in hist if t in by_t]
        if len(selected) != len(hist):
            raise RuntimeError(f"IDMA_CANDIDATE_HISTORY_GAP model={name} target={target} got={len(selected)} need={len(hist)}")
        s = score_rows(bundle, selected, objective)
        ranked.append((s, name))
    ranked.sort(key=lambda z: (z[0], z[1]))
    return ranked[0][1], ranked[0][0], len(hist), ranked[:5]

def copy_row(row, model_id, selection):
    z = dict(row)
    z["base_candidate_model"] = z.pop("model")
    z["model"] = model_id
    z["idma_selection"] = selection
    return z

def build_idma_variant(bundle, candidates, lane, objective, window):
    tag = "EXPANDING" if window is None else f"W{window}"
    model_id = f"IDMA_GRID__{lane}__{objective}__{tag}"
    by_model = {name: {r["target"]: r for r in rows} for name, rows in candidates.items()}

    dev = []
    selection_trace = []
    for target in base.month_range(DEV_START, DEV_END):
        name, score, n, top5 = choose_config(bundle, candidates, target, objective, window)
        selection = {
            "selector_objective": objective,
            "selector_window": tag,
            "selector_n": n,
            "selected_candidate": name,
            "selector_score": score,
            "top5": [{"score": float(s), "candidate": k} for s, k in top5],
            "uses_target_or_future_actual": False,
        }
        dev.append(copy_row(by_model[name][target], model_id, selection))
        selection_trace.append({"target": target, **selection})

    # Strict external freeze: determine one config using only history through DEV_END.
    freeze_target = "2025-01"
    frozen_name, frozen_score, frozen_n, frozen_top5 = choose_config(
        bundle, candidates, freeze_target, objective, window
    )
    frozen_selection = {
        "frozen_at": DEV_END,
        "selector_objective": objective,
        "selector_window": tag,
        "selector_n": frozen_n,
        "selected_candidate": frozen_name,
        "selector_score": frozen_score,
        "top5": [{"score": float(s), "candidate": k} for s, k in frozen_top5],
        "2025_2026_actuals_used_for_selection": False,
    }

    tr = [
        copy_row(by_model[frozen_name][t], model_id, {"external_frozen_config": frozen_selection})
        for t in base.month_range(TR_START, TR_END)
    ]
    st = [
        copy_row(by_model[frozen_name][t], model_id, {"external_frozen_config": frozen_selection})
        for t in base.month_range(ST_START, ST_END)
    ]
    return {
        "model_id": model_id,
        "lane": lane,
        "objective": objective,
        "window": tag,
        "dev": {"metrics": dma.active_metrics(dev), "yearly": dma.yearly(dev), "rows": dev},
        "transport_2025": {"metrics": dma.active_metrics(tr), "rows": tr},
        "stress_2026": {"metrics": dma.active_metrics(st), "rows": st},
        "selection_trace": selection_trace,
        "external_freeze": frozen_selection,
    }

def pareto(models):
    rows = []
    for m in models:
        z = m["dev"]["metrics"]
        rows.append({
            "model": m["model_id"],
            "sum_abs_error": z["sum_abs_error"],
            "direction_correct": z["direction_correct"],
            "direction_accuracy_pct": z["direction_accuracy_pct"],
            "mae": z["mae"],
            "mape_pct": z["mape_pct"],
            "rmse": z["rmse"],
        })
    front = []
    for a in rows:
        dominated = False
        for b in rows:
            if b is a:
                continue
            if (b["sum_abs_error"] <= a["sum_abs_error"] and
                b["direction_correct"] >= a["direction_correct"] and
                (b["sum_abs_error"] < a["sum_abs_error"] or b["direction_correct"] > a["direction_correct"])):
                dominated = True
                break
        if not dominated:
            front.append(a)
    rows.sort(key=lambda x: (x["sum_abs_error"], -x["direction_correct"], x["model"]))
    front.sort(key=lambda x: (x["sum_abs_error"], -x["direction_correct"], x["model"]))
    return rows, front

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle = base.load_data(dsn)
    all_targets = list(base.month_range(HIST_START, ST_END))
    cache = {t: base.all_samples_at_origin(bundle, t, governed=True) for t in all_targets}

    lane_candidates = {}
    for lane in ("AUTHORITY_GOLD", "GOVERNED_MULTI4"):
        lane_candidates[lane] = candidate_rows(bundle, cache, lane)

    models = []
    for lane, candidates in lane_candidates.items():
        for objective, window in SELECTOR_VARIANTS:
            models.append(build_idma_variant(bundle, candidates, lane, objective, window))

    ranking, frontier = pareto(models)
    after = read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    # Scientific / governance gates
    for m in models:
        assert len(m["dev"]["rows"]) == 33
        assert len(m["transport_2025"]["rows"]) == 12
        assert len(m["stress_2026"]["rows"]) == 7
        for r in m["dev"]["rows"] + m["transport_2025"]["rows"] + m["stress_2026"]["rows"]:
            if not math.isfinite(r["forecast"]) or not math.isfinite(r["pred_log_return_gold"]):
                raise RuntimeError(f"NONFINITE {m['model_id']} {r['target']}")
            if abs(r["pred_log_return_gold"]) >= 1:
                raise RuntimeError(f"PATHOLOGICAL_RETURN {m['model_id']} {r['target']}")
        if m["external_freeze"]["frozen_at"] != DEV_END:
            raise RuntimeError("EXTERNAL_FREEZE_NOT_AT_DEV_END")

    out = {
        "family": "IDMA_STAGE4_6_V1",
        "scope": "STAGE_4_TO_6",
        "method_identity": {
            "published_idma": "Chen et al. 2025: cyclic predictor reselection + forgetting-factor calibration within DMA training/test windows.",
            "gold_authority": "Chen, Yang & Lan 2026 Economics Letters: monthly gold IDMA; horizon-specific predictor selection; IDMA and DMA outperform benchmarks.",
            "implementation_status": "PAPER_STRUCTURED_DISCRETE_IDMA_ADAPTATION",
            "important_limitation": "This governed implementation iteratively/dynamically selects among predeclared DMA predictor-pool and alpha/lambda candidates from Stage 0-3; it does not claim byte-for-byte replication of the authors' unpublished software.",
            "candidate_dimensions": ["predictor_pool", "alpha", "lambda"],
            "selector_objectives": ["AE_PRICE", "MSFE_LOGRET"],
            "selector_windows": ["W12", "W24", "EXPANDING"],
            "horizon": "H=1 only; project contract forbids silently adding h=3/6/12.",
        },
        "governance": {
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "selection_authority": f"{DEV_START}..{DEV_END}",
            "history_for_selector_starts": HIST_START,
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "external_config_frozen_at": DEV_END,
            "database": "READ_ONLY",
            "random_split": "NONE",
            "target_month_leakage": False,
        },
        "source_checks": bundle.source_checks,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "candidate_counts": {lane: len(cands) for lane, cands in lane_candidates.items()},
        "models": models,
        "dev_ranking": ranking,
        "dev_pareto_frontier": frontier,
    }
    Path("vw_midas_idma_stage4_6_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "candidate_counts": out["candidate_counts"],
        "model_count": len(models),
        "best_dev_12": ranking[:12],
        "pareto": frontier,
        "external_freezes": {m["model_id"]: m["external_freeze"] for m in models},
        "authority_invariants_unchanged": after == bundle.invariants_before,
        "source_checks": bundle.source_checks,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
