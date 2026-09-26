from __future__ import annotations
import json, math, os
from pathlib import Path
import psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_dma_batch1_v1 as dma
import vw_midas_idma_stage4_6_v1 as idma

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

# Stage 4 only: canonical IDMA core.
# Fixed canonical selector = expanding nested training history + MSFE of gold log-return.
# Window sensitivity/adaptation belongs to Stage 5 and is intentionally not run here.
OBJECTIVE = "MSFE_LOGRET"
WINDOW = None

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
    targets = list(base.month_range(DEV_START, ST_END))
    cache = {t: base.all_samples_at_origin(bundle, t, governed=True) for t in targets}

    precomputed = {}
    for target in targets:
        precomputed[target] = {}
        for lane in ("AUTHORITY_GOLD", "GOVERNED_MULTI4"):
            precomputed[target][lane] = idma.compute_outer_candidates(
                bundle, cache[target], target, lane
            )

    models = []
    for lane in ("AUTHORITY_GOLD", "GOVERNED_MULTI4"):
        models.append(
            idma.build_variant(
                bundle, cache, lane, OBJECTIVE, WINDOW, precomputed
            )
        )

    ranking, frontier = idma.pareto(models)
    after = read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    for m in models:
        if len(m["dev"]["rows"]) != 33:
            raise RuntimeError("DEV_COUNT_GATE_FAIL")
        if len(m["transport_2025"]["rows"]) != 12:
            raise RuntimeError("TRANSPORT_COUNT_GATE_FAIL")
        if len(m["stress_2026"]["rows"]) != 7:
            raise RuntimeError("STRESS_COUNT_GATE_FAIL")
        if m["external_freeze"]["frozen_at"] != DEV_END:
            raise RuntimeError("FREEZE_GATE_FAIL")
        for r in m["dev"]["rows"] + m["transport_2025"]["rows"] + m["stress_2026"]["rows"]:
            if not math.isfinite(r["forecast"]) or not math.isfinite(r["pred_log_return_gold"]):
                raise RuntimeError(f"NONFINITE {m['model_id']} {r['target']}")
            if abs(r["pred_log_return_gold"]) >= 1:
                raise RuntimeError(f"PATHOLOGICAL_RETURN {m['model_id']} {r['target']}")

    out = {
        "family": "IDMA_STAGE4_CORE_V1",
        "scope": "STAGE_4_ONLY",
        "authority": {
            "chen_2025": "IDMA modifies DMA inputs by reselecting predictors and calibrating forgetting factors on training data before forecasting the adjacent test set.",
            "chen_yang_lan_2026_gold": "Monthly gold IDMA applies cyclic predictor selection and alpha/lambda updates; IDMA and DMA outperform benchmarks.",
            "implementation": "Exhaustive small-space realization of the same declared optimization target: 7 optional frozen predictors -> all 2^7 predictor sets; forgetting configs inherited from Stage 2.",
            "canonical_stage4_selector": "EXPANDING_NESTED_MSFE_LOGRET",
            "stage5_not_run": True,
            "stage6_not_run": True,
        },
        "contract": {
            "target": "H=1 next-calendar-month average XAU/USD",
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "predictor_sets": 128,
            "forgetting_configs": len(dma.FORGETTING),
            "candidate_configs_per_outer_lane": 128 * len(dma.FORGETTING),
            "dev_selection": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "database": "READ_ONLY",
            "random_split": "NONE",
            "target_month_leakage": False,
        },
        "source_checks": bundle.source_checks,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "models": models,
        "dev_ranking": ranking,
        "dev_pareto_frontier": frontier,
    }

    Path("vw_midas_idma_stage4_core_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "scope": out["scope"],
        "models": ranking,
        "pareto": frontier,
        "external_freezes": {m["model_id"]: m["external_freeze"] for m in models},
        "authority_invariants_unchanged": after == bundle.invariants_before,
        "source_checks": bundle.source_checks,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
