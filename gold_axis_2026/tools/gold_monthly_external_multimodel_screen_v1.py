from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_fx_h10_residual_v1 as h10

EXPECTED = {
    "ChHHO-ANFIS": (1413.0297794085, 23),
    "DE-ABC-RBFNN": (1415.8371, 25),
    "PLS1-V1-ALL4": (1420.0291, 20),
    "LMC2_RBF_M32": (1424.1711, 19),
    "FULL7-ANN": (1428.8590, 22),
    "REDUCED4-ANN": (1431.4587, 24),
    "EPSILON_RBF_DAILY12": (1449.187363, 19),
    "CATBOOST_PRICE": (1460.4339353, 20),
}
TOL_SUMAE = 0.05

OFFLINE_BLOCKS = {
    "INFLATION_HEADLINE": ["cpi_surprise_last"],
    "RATES_PIT": ["dgs10_change", "dff_change", "curve_proxy_change"],
    "FX_CNY_PIT": ["usdcny_logret"],
}
OPTIONAL_H10_BLOCKS = {
    "FX_H10_BROAD": ["broad_usd_ret"],
    "FX_H10_MAJORS": [
        "eur_usdstrength_ret", "jpy_usdstrength_ret",
        "gbp_usdstrength_ret", "chf_usdstrength_ret",
        "cny_usdstrength_ret"
    ],
}

ANN_RUNS = {
    "BATCH1": "36127630549",
    "BATCH2": "36128225062",
    "BATCH5": "36129458713",
    "BATCH8": "36130538857",
    "STAGE31": "36132219383",
    "STAGE32": "36132859342",
    "STAGE34": "36134549789",
}
FULL7 = ["VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA"]
REDUCED4 = ["VANILLA","MPA","SCA","DE_ABC"]


def read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def row_norm(r):
    return {
        "target": str(r["target"]),
        "origin": str(r.get("origin") or ""),
        "forecast": float(r["forecast"]),
        "actual": float(r["actual"]),
        "rw": float(r["rw"]),
    }


def rows_from(path: Path, route):
    d = read_json(path)
    x = d
    for k in route:
        x = x[k]
    return [row_norm(r) for r in x]


def ann_components(root: Path):
    out = {}
    d = read_json(root / ANN_RUNS["BATCH1"] / "vw_midas_shallow_mlp_v1_result.json")
    out["VANILLA"] = [row_norm(r) for r in d["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["BATCH2"] / "vw_midas_ann_meta_batch_2_v1_result.json")
    out["MPA"] = [row_norm(r) for r in d["models"]["MPA"]["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["BATCH5"] / "vw_midas_ann_meta_batch_5_v1_result.json")
    out["SCA"] = [row_norm(r) for r in d["models"]["SCA"]["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["BATCH8"] / "vw_midas_ann_meta_batch_8_v1_result.json")
    out["DE_ABC"] = [row_norm(r) for r in d["models"]["DE_ABC"]["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["STAGE31"] / "vw_midas_ann_stage3_batch31_v1_result.json")
    out["ADAPTIVE_TLBO"] = [row_norm(r) for r in d["models"]["ADAPTIVE_TLBO"]["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["STAGE32"] / "vw_midas_ann_stage3_batch32_v1_result.json")
    out["TLBO_TUNED_PSO"] = [row_norm(r) for r in d["models"]["TLBO_TUNED_PSO"]["dev"]["rows"]]

    d = read_json(root / ANN_RUNS["STAGE34"] / "vw_midas_ann_stage3_batch34_v1_result.json")
    out["MPA_SCA"] = [row_norm(r) for r in d["models"]["MPA_SCA"]["dev"]["rows"]]
    return out


def ensemble_rows(comp, names):
    targets = [r["target"] for r in comp[names[0]]]
    for n in names:
        if [r["target"] for r in comp[n]] != targets:
            raise RuntimeError(f"ANN_ALIGNMENT_FAIL {n}")
    out = []
    for i, t in enumerate(targets):
        base = comp[names[0]][i]
        out.append({
            "target": t,
            "origin": base["origin"],
            "forecast": float(np.mean([comp[n][i]["forecast"] for n in names])),
            "actual": base["actual"],
            "rw": base["rw"],
        })
    return out


def load_models(root: Path):
    models = {}
    models["ChHHO-ANFIS"] = rows_from(
        root / "chhho" / "anfis_stage3c_chhho_result.json", ["dev","rows"]
    )
    models["DE-ABC-RBFNN"] = rows_from(
        root / "deabc" / "rbfnn_stage1_de_abc_result.json", ["dev","rows"]
    )
    models["PLS1-V1-ALL4"] = rows_from(
        root / "pls1" / "gold_monthly_challenger_b_pls1_v1_result.json", ["dev","rows"]
    )
    models["LMC2_RBF_M32"] = rows_from(
        root / "gpr" / "gpr_lmc2_rbf_m32_result.json", ["dev","rows"]
    )

    comp = ann_components(root / "ann")
    models["FULL7-ANN"] = ensemble_rows(comp, FULL7)
    models["REDUCED4-ANN"] = ensemble_rows(comp, REDUCED4)

    models["EPSILON_RBF_DAILY12"] = rows_from(
        root / "svr" / "gold_monthly_svr_dwt_stage2b_representation_v1_result.json",
        ["results","DAILY_SUMMARY12","rows"]
    )
    models["CATBOOST_PRICE"] = rows_from(
        root / "catboost" / "gold_monthly_boosting_stage6b_catboost_vanilla_result.json",
        ["rows"]
    )
    return models


def load_snapshot(path: Path):
    d = read_json(path)
    out = {}
    for r in d["rows"]:
        out[str(r["origin_month"])] = {
            k: float(v) for k,v in r.items()
            if k != "origin_month" and v is not None
        }
    return d, out


def merge_ext(*parts):
    keys = set()
    for p in parts:
        keys.update(p)
    out = {}
    for k in sorted(keys):
        z = {}
        for p in parts:
            z.update(p.get(k, {}))
        out[k] = z
    return out


def validate_base(name, rows):
    if len(rows) != 33:
        raise RuntimeError(f"BASE_ROW_COUNT_FAIL {name} n={len(rows)}")
    got = core.metrics(rows)
    exp_sae, exp_dir = EXPECTED[name]
    if abs(got["sum_ae"] - exp_sae) > TOL_SUMAE:
        raise RuntimeError(
            f"BASE_REPRO_FAIL {name} expected={exp_sae} got={got['sum_ae']}"
        )
    if got["direction_correct"] != exp_dir:
        raise RuntimeError(
            f"BASE_DIRECTION_FAIL {name} expected={exp_dir} got={got['direction_correct']}"
        )
    return got


def block_result(rows, ext, cols):
    corrected = core.prequential(rows, ext, cols)
    gate = core.stability_gate(rows, corrected)
    full = core.metrics(corrected, "corrected_forecast")
    base = core.metrics(rows)
    full_delta = float(base["sum_ae"] - full["sum_ae"])
    improved = 0
    worsened = 0
    unchanged = 0
    for b, c in zip(rows, corrected):
        be = abs(b["forecast"] - b["actual"])
        ce = abs(c["corrected_forecast"] - c["actual"])
        if ce < be - 1e-12:
            improved += 1
        elif ce > be + 1e-12:
            worsened += 1
        else:
            unchanged += 1
    return {
        "columns": cols,
        "full_metrics": full,
        "full_dev_sum_ae_improvement": full_delta,
        "full_dev_improvement_pct": 100.0 * full_delta / base["sum_ae"],
        "months_improved": improved,
        "months_worsened": worsened,
        "months_unchanged": unchanged,
        "gate": gate,
        "rows": corrected,
    }


def run(args):
    root = Path(args.artifact_root)
    models = load_models(root)

    pit_doc, pit = load_snapshot(Path(args.pit))
    inf_doc, inf = load_snapshot(Path(args.inflation))
    h10_status = "AVAILABLE"
    h10_error = None
    h10_src = None
    try:
        h10_ext, _, h10_src = h10.build()
    except Exception as e:
        h10_status = "SOURCE_UNAVAILABLE"
        h10_error = f"{type(e).__name__}: {e}"
        h10_ext = {}
    ext = merge_ext(pit, inf, h10_ext)
    active_blocks = dict(OFFLINE_BLOCKS)
    if h10_status == "AVAILABLE":
        active_blocks.update(OPTIONAL_H10_BLOCKS)

    result = {
        "schema": "GOLD_MONTHLY_EXTERNAL_MULTIMODEL_SCREEN_V1_2026-09-29",
        "scope": "ARTIFACT_ONLY_EXTERNAL_INFORMATION_SCREEN_NO_NATIVE_RETRAIN",
        "authority": {
            "neon_reads": 0,
            "neon_connection_required": False,
            "base_forecasts": "FROZEN_AUTHORITY_ARTIFACTS",
            "selection_period": "DEV_2022-04..2024-12",
            "random_split": False,
            "target_month_external_data": False,
            "correction_method": "PREQUENTIAL_RIDGE_ON_PRIOR_DEV_RESIDUALS",
            "ridge_alpha": core.RIDGE_ALPHA,
            "min_prior_residuals": core.MIN_HISTORY,
            "correction_cap_mult": core.CAP_MULT,
            "native_integration": "NOT_RUN_IN_THIS_STAGE_REQUIRES_LONG_HISTORY_EXTERNAL_BACKFILL",
        },
        "external_sources": {
            "pit_schema": pit_doc["schema"],
            "inflation_schema": inf_doc["schema"],
            "h10_source": "Federal Reserve Board H.10 DDP",
            "h10_release_lag_days": h10.LAG_DAYS,
            "h10_status": h10_status,
            "h10_error": h10_error,
            "h10_source_hashes": h10_src,
        },
        "blocks": active_blocks,
        "offline_required_blocks": OFFLINE_BLOCKS,
        "optional_h10_blocks": OPTIONAL_H10_BLOCKS,
        "models": {},
    }

    summary = []
    for name, rows in models.items():
        base = validate_base(name, rows)
        rec = {"base": base, "blocks": {}}
        candidates = []
        for b, cols in active_blocks.items():
            br = block_result(rows, ext, cols)
            rec["blocks"][b] = br
            if br["gate"].get("pass"):
                candidates.append((br["full_metrics"]["sum_ae"], b))
        candidates.sort()
        rec["best_pass_block"] = candidates[0][1] if candidates else "BASE"
        rec["best_pass_metrics"] = (
            rec["blocks"][rec["best_pass_block"]]["full_metrics"]
            if rec["best_pass_block"] != "BASE" else base
        )
        result["models"][name] = rec
        summary.append({
            "model": name,
            "base_sum_ae": base["sum_ae"],
            "base_direction": base["direction_correct"],
            "best_block": rec["best_pass_block"],
            "best_sum_ae": rec["best_pass_metrics"]["sum_ae"],
            "best_direction": rec["best_pass_metrics"]["direction_correct"],
            "delta_sum_ae": base["sum_ae"] - rec["best_pass_metrics"]["sum_ae"],
        })

    result["summary"] = sorted(summary, key=lambda z: z["best_sum_ae"])
    result["result_sha256"] = core.sha({
        k:v for k,v in result.items() if k != "result_sha256"
    })

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "gold_monthly_external_multimodel_screen_v1_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8"
    )

    lines = [
        "# GOLD MONTHLY — EXTERNAL INFORMATION MULTI-MODEL SCREEN V1",
        "",
        "**Status:** COMPLETE / ARTIFACT-ONLY / ZERO NEON READS",
        "",
        "This stage measures incremental external information on eight frozen strong models using the same prequential residual-correction protocol. It is not native architecture retraining.",
        "",
        "| Model | Base ΣAE | Base dir | Best external block | Corrected ΣAE | Corrected dir | ΔΣAE |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for z in result["summary"]:
        lines.append(
            f"| {z['model']} | {z['base_sum_ae']:.4f} | {z['base_direction']}/33 | "
            f"{z['best_block']} | {z['best_sum_ae']:.4f} | {z['best_direction']}/33 | "
            f"{z['delta_sum_ae']:.4f} |"
        )

    lines += ["", "## Block detail", ""]
    for name, rec in result["models"].items():
        lines += [
            f"### {name}",
            "",
            "| Block | Corrected ΣAE | ΔΣAE | Δ% | Direction | Improved months | Worsened months | Gate |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for b in active_blocks:
            x = rec["blocks"][b]
            lines.append(
                f"| {b} | {x['full_metrics']['sum_ae']:.4f} | "
                f"{x['full_dev_sum_ae_improvement']:.4f} | "
                f"{x['full_dev_improvement_pct']:.2f}% | "
                f"{x['full_metrics']['direction_correct']}/33 | "
                f"{x['months_improved']} | {x['months_worsened']} | "
                f"{'PASS' if x['gate'].get('pass') else 'FAIL'} |"
            )
        lines.append("")

    lines += [
        "## Interpretation boundary",
        "",
        "- This screen answers whether external information can improve each frozen model's forecast errors.",
        "- It does not yet claim native feature integration performance.",
        "- Native retraining requires origin-safe external history extending through the historical training window; that backfill must be governed before native experiments.",
        "- 2025 is not used in this screen.",
        "- Neon reads: 0.",
    ]
    (outdir / "GOLD_MONTHLY_EXTERNAL_MULTIMODEL_SCREEN_V1_2026-09-29.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print("OUTPUT_GATE=PASS")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-root", required=True)
    ap.add_argument("--pit", required=True)
    ap.add_argument("--inflation", required=True)
    ap.add_argument("--outdir", default="external_multimodel_out")
    run(ap.parse_args())
