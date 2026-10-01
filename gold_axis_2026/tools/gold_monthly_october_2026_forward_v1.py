from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base


TARGET = "2026-10"
ORIGIN = "2026-09"


def merge_bundle(dev_snapshot, current_bundle):
    b, meta = snap.load_snapshot(dev_snapshot)
    cur = json.loads(Path(current_bundle).read_text())

    dd = {m: {k: list(v) for k, v in b.daily_month_values[m].items()} for m in base.METALS}
    for r in cur["daily_extension_rows"]:
        mk = r["date"][:7]
        for m in base.METALS:
            dd[m].setdefault(mk, []).append(float(r[m]))

    daily = {m: {k: np.asarray(v, float) for k, v in q.items()} for m, q in dd.items()}
    monthly = {m: {k: float(v.mean()) for k, v in daily[m].items()} for m in base.METALS}

    core = dict(b.core_gold)
    core.update({k: float(v) for k, v in cur["world_bank"]["gold_monthly"].items()})

    gpr = dict(b.gpr_vintages)
    gpr.update({o: {k: float(v) for k, v in h.items()} for o, h in cur["gpr_vintages"].items()})

    checks = dict(b.source_checks)
    checks.update({
        "public_extension_last": cur["daily_extension_last"],
        "public_extension_rows": len(cur["daily_extension_rows"]),
        "world_bank_last": cur["world_bank"]["last"],
        "neon_reads": 0,
    })

    out = base.DataBundle(
        core_gold=core,
        core_gpr={},
        daily_month_values=daily,
        monthly_metal=monthly,
        gpr_vintages=gpr,
        source_checks=checks,
        invariants_before=b.invariants_before,
    )
    return out, cur, meta


def forward_x(bundle, target, gpr_history):
    p = base.month_shift(target, -1)
    pp = base.month_shift(target, -2)
    z = base.gpr_norm(gpr_history, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FORWARD_FEATURE_MONTH_MISSING {metal} {target}")
        x.extend((
            math.log(M[p] / M[pp]),
            base.weighted_daily_return(bundle, metal, p, z),
        ))
    return np.asarray(x, float)


def forward_samples(bundle):
    if ORIGIN not in bundle.gpr_vintages:
        raise RuntimeError("GPR_ORIGIN_VINTAGE_MISSING_2026_09")
    gh = bundle.gpr_vintages[ORIGIN]
    out = {}
    for t in base.month_range("2010-03", ORIGIN):
        try:
            out[t] = base.sample_for_target(bundle, t, gh, True)
        except RuntimeError:
            continue
    out[TARGET] = (forward_x(bundle, TARGET, gh), np.zeros(4, float))
    return out


def predict(model, samples):
    if model == "CHHHO":
        import vw_midas_anfis_stage3c_literature_v1 as anfis
        p, n, diag = anfis.select(samples, TARGET, "CHHHO")
        return np.asarray(p, float), {"train_rows": n, **diag}
    if model == "DE_ABC":
        import vw_midas_rbfnn_stage1_v1 as rbfnn
        p, diag = rbfnn.predict(samples, TARGET, "DE_ABC")
        return np.asarray(p, float), diag
    raise KeyError(model)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-snapshot", required=True)
    ap.add_argument("--current-bundle", required=True)
    ap.add_argument("--model", required=True, choices=["CHHHO", "DE_ABC"])
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    b, cur, meta = merge_bundle(a.dev_snapshot, a.current_bundle)

    if cur["daily_extension_last"] < "2026-09-30":
        raise RuntimeError(f"SEPTEMBER_NOT_COMPLETE last={cur['daily_extension_last']}")

    sep_dates = sorted({
        r["date"] for r in cur["daily_extension_rows"]
        if r["date"].startswith("2026-09")
    })
    if len(sep_dates) < 18:
        raise RuntimeError(f"SEPTEMBER_COMMON_DAILY_ROWS_TOO_FEW n={len(sep_dates)}")

    sep_monthly = {}
    for m in base.METALS:
        vals = b.daily_month_values[m].get(ORIGIN)
        if vals is None or len(vals) < 18:
            raise RuntimeError(f"SEPTEMBER_METAL_INCOMPLETE {m}")
        v = float(np.mean(vals))
        if not np.isfinite(v) or v <= 0:
            raise RuntimeError(f"SEPTEMBER_METAL_BAD_VALUE {m} {v}")
        sep_monthly[m] = v

    samples = forward_samples(b)

    # The September target is now complete and included in model fitting.
    if ORIGIN not in samples:
        raise RuntimeError("SEPTEMBER_TRAINING_ROW_MISSING")

    p, diag = predict(a.model, samples)

    wb_sep = b.core_gold.get(ORIGIN)
    if wb_sep is not None:
        origin_price = float(wb_sep)
        origin_price_role = "WORLD_BANK_MONTHLY_GOLD_2026_09"
        forecast_status = "CANONICAL_MONTHLY_LEVEL_ORIGIN_AVAILABLE"
        canonical_level_final = True
    else:
        origin_price = float(sep_monthly["Gold"])
        origin_price_role = "STAKTRAKR_COMPLETE_SEPTEMBER_MONTHLY_AVERAGE_PROXY"
        forecast_status = "SEPTEMBER_COMPLETE_FEATURES_FULL_MONTH_STAK_LEVEL_PROXY"
        canonical_level_final = False

    forecast = float(origin_price * math.exp(float(p[0])))

    out = {
        "schema": "GOLD_MONTHLY_OCTOBER_2026_FORWARD_V1_2026-10-01",
        "model": a.model,
        "target": TARGET,
        "origin": ORIGIN,
        "forecast_role": "SEPTEMBER_COMPLETE_ORIGIN_FORWARD",
        "train_end": ORIGIN,
        "september_training_y_used": True,
        "october_target_y_used": False,
        "pred_log_return_gold": float(p[0]),
        "origin_price": origin_price,
        "origin_price_role": origin_price_role,
        "forecast": forecast,
        "forecast_status": forecast_status,
        "canonical_level_final": canonical_level_final,
        "september_common_daily_rows": len(sep_dates),
        "september_common_daily_first": sep_dates[0],
        "september_common_daily_last": sep_dates[-1],
        "september_monthly_metals": sep_monthly,
        "daily_data_last": cur["daily_extension_last"],
        "world_bank_last": cur["world_bank"]["last"],
        "world_bank_sep_available": wb_sep is not None,
        "gpr_vintage_origin": ORIGIN,
        "gpr_meta": cur["gpr_meta"][ORIGIN],
        "neon_reads": 0,
        "dev_snapshot_payload_sha256": meta["payload_sha256"],
        "diag": diag,
        "governance": {
            "october_data_used": False,
            "model_contract_changed": False,
            "feature_contract_changed": False,
            "posthoc_level_scaling": False,
        },
    }

    Path(a.output).write_text(
        json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("OCTOBER_2026_FORWARD_GATE=PASS")
    print(json.dumps({
        "model": out["model"],
        "forecast": out["forecast"],
        "pred_log_return_gold": out["pred_log_return_gold"],
        "origin_price": out["origin_price"],
        "origin_price_role": out["origin_price_role"],
        "forecast_status": out["forecast_status"],
        "september_common_daily_rows": out["september_common_daily_rows"],
        "daily_data_last": out["daily_data_last"],
        "world_bank_last": out["world_bank_last"],
        "world_bank_sep_available": out["world_bank_sep_available"],
        "train_rows": out["diag"].get("train_rows"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
