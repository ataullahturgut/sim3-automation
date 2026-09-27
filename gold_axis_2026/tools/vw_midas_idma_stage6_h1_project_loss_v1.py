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

# Stage 6 only: project-specific H=1 loss alignment.
# The IDMA mechanism and candidate space remain unchanged.
# We change only the training selector loss to absolute price error (AE_PRICE),
# aligning the optimizer with the project's primary price metric ΣAE.
OBJECTIVE = "AE_PRICE"
WINDOWS = (12, None)  # W24 removed after Stage 5 weakness; no extra search dimension.

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

    # Shared expensive state paths across the two retained selector windows.
    precomputed = {}
    for target in targets:
        precomputed[target] = {}
        for lane in ("AUTHORITY_GOLD", "GOVERNED_MULTI4"):
            precomputed[target][lane] = idma.compute_outer_candidates(
                bundle, cache[target], target, lane
            )

    models = []
    for lane in ("AUTHORITY_GOLD", "GOVERNED_MULTI4"):
        for window in WINDOWS:
            models.append(
                idma.build_variant(
                    bundle, cache, lane, OBJECTIVE, window, precomputed
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
        "family": "IDMA_STAGE6_H1_PROJECT_LOSS_V1",
        "scope": "STAGE_6_ONLY",
        "authority": {
            "idma_method": "Predictors and forgetting factors are optimized within training data; revised inputs are then used by standard DMA for test prediction.",
            "gold_application": "Chen, Yang & Lan (2026) apply IDMA to monthly gold and optimize DMA inputs for forecasting performance.",
            "project_specific_change": "Selector loss only: AE_PRICE instead of Stage-4/5 MSFE_LOGRET.",
            "why_ae_price": "The project primary price criterion is cumulative absolute USD error (ΣAE), so AE_PRICE aligns training-only model selection to that criterion.",
            "direction_not_optimized": True,
            "why_no_direction_optimizer": "Direction remains a report/tie-break metric to avoid adding a custom non-authority search dimension.",
            "windows_tested": ["W12", "EXPANDING"],
            "w24_not_retested": "Stage 5 showed no price-error benefit and weaker/unstable direction; omitted to limit multiplicity.",
            "stage7_not_run": True,
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

    Path("vw_midas_idma_stage6_h1_project_loss_v1_result.json").write_text(
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
