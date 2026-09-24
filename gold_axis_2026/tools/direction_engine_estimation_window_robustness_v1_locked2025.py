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

IDENTITY = "DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_TRANSPORT"
SQRT_WINDOWS = tuple(range(250, 1001, 25))
ROUTER_WINDOWS = tuple(range(30, 501, 10))
UP2_WINDOWS = tuple(range(60, 100, 5))


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


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            z = dict(row)
            for k, v in list(z.items()):
                if isinstance(v, (dict, list, tuple)):
                    z[k] = json.dumps(v, sort_keys=True)
            w.writerow(z)


def router_metrics(base, rows):
    m = base.router_stats(rows)
    return {
        "n": int(m["n"]),
        "calls": int(m["router_up"]),
        "tp": int(m["tp"]),
        "fp": int(m["fp"]),
        "actual_up": int(m["actual_up"]),
        "actual_down": int(m["actual_down"]),
        "precision": m["precision"],
        "false_up_fpr": m["fpr"],
        "actual_up_recall": m["recall"],
        "coverage": m["coverage"],
        "wilson90_lcb_precision": base.wilson_lcb(int(m["tp"]), int(m["router_up"])),
        "selected_counts": dict(Counter(r["selected_expert"] for r in rows if int(r["router_up"]) == 1)),
    }


def build_up2_cases(route, cbr, up2, base, sqrt_mod, ext_spine, raw_root, sqrt_parent, pre_ledger, gov_days):
    ext_raw = route.build_external_5m(raw_root)
    ext_audit = route.external_reconstruction_audit(ext_raw, ext_spine)
    if not ext_audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    ext_daily = route.load_external_daily_for_sqrt(ext_spine)
    ext_sqrt, ext_sqrt_summary = route.external_sqrt_cases(sqrt_mod, ext_daily)
    ext_router, ext_router_summary = route.external_router_rows(base, ext_spine)
    ext_unresolved, ext_route_summary = route.route_external_sqrt_cases(ext_sqrt, ext_router)

    ext_router_map = {(r["origin_date"], r["target_date"]): r for r in ext_router}
    ext_sqrt_map = {(r["origin_date"], r["target_date"]): r for r in ext_sqrt}
    ext_lag = up2.lag_map_from_spine(ext_spine)
    external_cases = []
    for r in ext_unresolved:
        key = (r["origin_date"], r["target_date"])
        rr = ext_router_map[key]
        sr = ext_sqrt_map[key]
        external_cases.append(up2.enrich_case(
            r, sr["sqrt_normalized_risk_score"], rr, ext_lag[r["origin_date"]],
            ext_raw[r["origin_date"]]["rets"], "EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
        ))
    if len(external_cases) != 98 or sum(int(r["actual_up"]) for r in external_cases) != 46:
        raise RuntimeError("EXTERNAL_RESIDUAL_FORMATION_MISMATCH")

    gov_raw = cbr.load_paths(["2020-01-02", "2025-12-31"])
    parent = up2.load_parent(sqrt_parent)
    parent_map = {(r["origin_date"], r["target_date"]): r for r in parent}
    gov_router = up2.build_governed_router_rows(base, gov_days)
    gov_router_map = {(r["origin_date"], r["target_date"]): r for r in gov_router}
    gov_lag = up2.lag_map_from_base_days(gov_days)

    pre = route.load_pre_unresolved(pre_ledger)
    pre_cases = []
    for r in pre:
        key = (r["origin_date"], r["target_date"])
        pr = parent_map.get(key)
        rr = gov_router_map.get(key)
        if pr is None or rr is None or int(rr["router_up"]) != 0:
            raise RuntimeError(f"UP2_PRE_FEATURE_JOIN_OR_ROUTE_FAIL:{key}")
        pre_cases.append(up2.enrich_case(
            r, pr["sqrt_score"], rr, gov_lag[r["origin_date"]],
            gov_raw[r["origin_date"]], "GOVERNED_ROUTER_ABSTAIN"
        ))
    if len(pre_cases) != 26 or sum(int(r["actual_up"]) for r in pre_cases) != 13:
        raise RuntimeError("UP2_PRE2025_ROUTE_MISMATCH")

    stress25 = route.reconstruct_2025(base, sqrt_parent)
    if len(stress25) != 74 or sum(int(r["actual_up"]) for r in stress25) != 35:
        raise RuntimeError("UP2_LOCKED2025_ROUTE_MISMATCH")
    stress_cases = []
    for r in stress25:
        key = (r["origin_date"], r["target_date"])
        pr = parent_map.get(key)
        rr = gov_router_map.get(key)
        if pr is None or rr is None or int(rr["router_up"]) != 0:
            raise RuntimeError(f"UP2_2025_FEATURE_JOIN_OR_ROUTE_FAIL:{key}")
        stress_cases.append(up2.enrich_case(
            r, pr["sqrt_score"], rr, gov_lag[r["origin_date"]],
            gov_raw[r["origin_date"]], "GOVERNED_ROUTER_ABSTAIN"
        ))

    return {
        "external_cases": external_cases,
        "pre_cases": pre_cases,
        "stress_cases": stress_cases,
        "source": {
            "external_reconstruction": ext_audit,
            "external_sqrt_summary": ext_sqrt_summary,
            "external_router_summary": ext_router_summary,
            "external_route_summary": ext_route_summary,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1-code", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--external-spine", type=Path, required=True)
    ap.add_argument("--sqrt-code", type=Path, required=True)
    ap.add_argument("--route-module", type=Path, required=True)
    ap.add_argument("--base-module", type=Path, required=True)
    ap.add_argument("--cbr-code", type=Path, required=True)
    ap.add_argument("--up2-code", type=Path, required=True)
    ap.add_argument("--sqrt-parent", type=Path, required=True)
    ap.add_argument("--pre-ledger", type=Path, required=True)
    ap.add_argument("--v1-up2-surface", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    v1 = load_mod("history_v1_authority", args.v1_code)
    route = load_mod("route_authority_transport", args.route_module)
    base = load_mod("base_authority_transport", args.base_module)
    cbr = load_mod("cbr_authority_transport", args.cbr_code)
    up2 = load_mod("up2_authority_transport", args.up2_code)
    sqrt_mod = route.load_sqrt_mod(args.sqrt_code)

    integrity = []
    ext_spine = route.load_external_spine(args.external_spine)
    ext_days = route.load_external_daily_for_sqrt(ext_spine)
    gov_base_days = base.load_days()
    _, _, _, gov_daily = base.transformed(gov_base_days)

    # SQRT 2025 full frozen grid transport.
    governed_rows = v1.build_sqrt_rows(gov_daily)
    sq_baseline = v1.sqrt_eval(governed_rows, 2025, None)
    if sq_baseline.get("status") != "OK" or int(sq_baseline.get("alert_count", -1)) != 90:
        integrity.append(f"SQRT_LOCKED2025_BASELINE:{sq_baseline}")

    ext_pre = [d for d in ext_days if d.d <= date(2021, 12, 31)]
    gov_post = [d for d in gov_daily if d.d >= date(2022, 1, 1)]
    combined_rows = v1.build_sqrt_rows(ext_pre + gov_post)

    sqrt_surface = []
    sqrt_surface.append({"policy": "GOVERNED_FROZEN_EXPANDING", "window": "EXPANDING", **sq_baseline})
    ext_exp = v1.sqrt_eval(combined_rows, 2025, None)
    sqrt_surface.append({"policy": "EXTENDED_EXPANDING", "window": "EXPANDING", **ext_exp})
    for w in SQRT_WINDOWS:
        m = v1.sqrt_eval(combined_rows, 2025, w)
        sqrt_surface.append({"policy": f"EXTENDED_ROLLING_{w}", "window": w, **m})

    # Router 2025 full frozen grid transport.
    ext_base_days = route.external_base_days(base, ext_spine)
    ext_router_base = v1.router_base_rows(base, ext_base_days)
    gov_router_base = v1.router_base_rows(base, gov_base_days)
    ev24 = [r for r in gov_router_base if yr(r["target_date"]) == 2024]
    ev25 = [r for r in gov_router_base if yr(r["target_date"]) == 2025]
    hist23 = [r for r in gov_router_base if yr(r["target_date"]) == 2023]
    frozen_path = v1.router_score_one(base, ev24 + ev25, hist23, "EXPANDING")
    frozen25 = [r for r in frozen_path if yr(r["target_date"]) == 2025]
    frozen_m = router_metrics(base, frozen25)
    if (frozen_m["calls"], frozen_m["tp"], frozen_m["fp"]) != (37, 27, 10):
        integrity.append(f"ROUTER_LOCKED2025_BASELINE:{frozen_m}")

    pre_hist = [r for r in ext_router_base if yr(r["target_date"]) in (2020, 2021)]
    pre_hist += [r for r in gov_router_base if 2022 <= yr(r["target_date"]) <= 2024]

    router_surface = [{"policy": "FROZEN_V2_CONTINUATION", "window": "FROZEN", **frozen_m}]
    scored = v1.router_score_one(base, ev25, pre_hist, "EXPANDING")
    router_surface.append({"policy": "EXPANDING", "window": "EXPANDING", **router_metrics(base, scored)})
    for w in ROUTER_WINDOWS:
        scored = v1.router_score_one(base, ev25, pre_hist, "ROLLING", w)
        router_surface.append({"policy": f"ROLLING_{w}", "window": w, **router_metrics(base, scored)})

    # UP2 2025 transport on exact frozen residual route.
    cases = build_up2_cases(
        route, cbr, up2, base, sqrt_mod, ext_spine, args.raw_root,
        args.sqrt_parent, args.pre_ledger, gov_base_days
    )
    all_hist = cases["external_cases"] + cases["pre_cases"]
    stress25 = cases["stress_cases"]

    pre_support = {}
    with args.v1_up2_surface.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("year") == "POOLED_2022_2024":
                pre_support[r["policy"]] = (r.get("pre2025_supportive") == "True")

    up2_surface = []
    policies = [("EXPANDING_FROZEN", None)] + [(f"ROLLING_{w}", w) for w in UP2_WINDOWS]
    for label, w in policies:
        train = sorted(all_hist, key=lambda r: r["target_date"])
        if w is not None:
            if len(train) < w:
                up2_surface.append({
                    "policy": label, "window": w, "status": "INFEASIBLE_WINDOW",
                    "train_available": len(train), "pre2025_supportive": pre_support.get(label, False)
                })
                continue
            train = train[-w:]
        scored25, m = up2.score_year(train, stress25, 2025)
        row = {
            "policy": label,
            "window": "EXPANDING" if w is None else w,
            "pre2025_supportive": pre_support.get(label, False),
            **m,
        }
        if m.get("status") == "OK":
            row["residual_up_base_rate"] = 35 / 74
            row["locked2025_transport_gate"] = bool(
                m["up2_calls"] >= 5
                and m["up_precision"] is not None and m["up_precision"] > (35 / 74)
                and m["false_up_fpr"] is not None and m["false_up_fpr"] < 0.50
            )
            row["eligible_for_any_future_policy_claim"] = bool(
                row["pre2025_supportive"] and row["locked2025_transport_gate"]
            )
        up2_surface.append(row)

    base_up2 = next(r for r in up2_surface if r["policy"] == "EXPANDING_FROZEN")
    if base_up2.get("status") != "OK" or (
        int(base_up2.get("n", -1)), int(base_up2.get("up2_calls", -1)),
        int(base_up2.get("true_up", -1)), int(base_up2.get("false_up", -1))
    ) != (74, 25, 13, 12):
        integrity.append(f"UP2_LOCKED2025_BASELINE:{base_up2}")

    status = "LOCKED2025_TRANSPORT_SURFACE_COMPLETE" if not integrity else "BLOCKED_BASELINE_REPRODUCTION"

    write_csv(
        args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_SQRT_2025_SURFACE_2026-09-24.csv",
        sqrt_surface,
    )
    write_csv(
        args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_ROUTER_2025_SURFACE_2026-09-24.csv",
        router_surface,
    )
    write_csv(
        args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_UP2_2025_SURFACE_2026-09-24.csv",
        up2_surface,
    )

    result = {
        "identity": IDENTITY,
        "status": status,
        "integrity_errors": integrity,
        "parent_v1_result_commit": "19b815289469b0354b6edc502b5831253b4bc162",
        "governance": {
            "2025_role": "LOCKED_RETROSPECTIVE_TRANSPORT_ONLY",
            "2025_used_to_change_grid": False,
            "2025_used_to_tune": False,
            "2026_used": False,
            "random_split": False,
            "runtime_write": False,
            "production_write": False,
            "model_feature_changes": False,
        },
        "baseline_reproduction": {
            "sqrt_2025": sq_baseline,
            "router_2025": frozen_m,
            "up2_2025": base_up2,
        },
        "surface_counts": {
            "sqrt": len(sqrt_surface),
            "router": len(router_surface),
            "up2": len(up2_surface),
        },
        "up2_source": cases["source"],
        "interpretation_rule": "2025 transports the entire preregistered V1 surface; it cannot select or rescue a history policy.",
    }
    (args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_RESULT_2026-09-24.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md = [
        "# GOLD CONTROL — Direction Engine Estimation-Window Robustness V1 Locked-2025 Transport",
        "",
        f"**Status:** `{status}`",
        "",
        "The entire V1 history-window grid was carried to locked retrospective 2025 without any grid, threshold, feature or model change.",
        "",
        f"- SQRT frozen baseline alarms: {sq_baseline.get('alert_count')}",
        f"- Router frozen baseline: {frozen_m.get('calls')} calls = {frozen_m.get('tp')} TP + {frozen_m.get('fp')} FP",
        f"- UP-2 frozen baseline: {base_up2.get('up2_calls')} calls = {base_up2.get('true_up')} true UP + {base_up2.get('false_up')} false UP",
        "",
        "No history policy is selected by this transport run. Joint interpretation requires the pre-2025 V1 surface plus this locked-2025 surface.",
        "",
        "2026 was not used. No DB/runtime/production write occurred.",
    ]
    if integrity:
        md += ["", "## Integrity errors", ""] + [f"- {x}" for x in integrity]
    (args.out / "GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_RESULT_2026-09-24.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8"
    )

    print(json.dumps({"status": status, "integrity_errors": integrity, "surface_counts": result["surface_counts"]}, sort_keys=True))
    return 0 if not integrity else 2


if __name__ == "__main__":
    raise SystemExit(main())
