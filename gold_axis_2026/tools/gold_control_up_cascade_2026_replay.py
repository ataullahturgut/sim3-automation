from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

IDENTITY = "GOLD_CONTROL_FROZEN_UP_CASCADE_2026_REPLAY"
EXPECTED_PRIMARY = {
    2024: {"up": 42, "tp": 26, "fp": 16},
    2025: {"up": 37, "tp": 27, "fp": 10},
}
EXPECTED_RESIDUAL = {
    2022: (11, 5, 6),
    2023: (2, 1, 1),
    2024: (13, 7, 6),
    2025: (74, 35, 39),
}
EXPECTED_UP2 = {
    2022: (7, 4, 3),
    2023: (1, 1, 0),
    2024: (3, 3, 0),
    2025: (25, 13, 12),
}


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAIL:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_parent(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y = int(r["evaluation_year"])
            if y not in (2022, 2023, 2024, 2025, 2026):
                continue
            ret = float(r["target_close_return"])
            if ret == 0:
                continue
            rows.append({
                "evaluation_year": y,
                "origin_date": r["origin_date"],
                "target_date": r["target_date"],
                "actual_up": int(ret > 0),
                "sqrt_alert": int(r["sqrt_high_risk_alert"]),
                "sqrt_score": float(r["sqrt_normalized_risk_score"]),
                "actual_high_risk": int(r["actual_high_risk"]),
            })
    return rows


def build_all_base_rows(base, days):
    tdays, bdays, ldays, daily = base.transformed(days)
    trows = base.ttsm_mod.build_signal_rows(tdays)
    tmap = {r["target_date"]: r for r in trows}
    bmaps = base.bonato_maps(bdays)
    lmaps = base.logit_maps(ldays)
    contexts = base.legacy_context(daily)

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
        rows.append({
            "origin_date": od,
            "target_date": td,
            "actual_up": vals[0],
            "TTSM_S2": int(t["ttsm_s2_signal"] == 1),
            "TTSM_S1": int(t["ttsm_s1_signal"] == 1),
            "BONATO_AR1_RM_QBOOST_H1": int(b["up"]),
            "AR1_RM_LOGIT": int(ar["up"]),
            "RM_LOGIT": int(rm["up"]),
            **ctx,
        })
    return rows


def score_router_year(base, eval_rows, history):
    hist = [dict(r) for r in history]
    scored = []
    for raw in eval_rows:
        row = dict(raw)
        eligible = []
        for expert in base.DIRECT_UP_EXPERTS:
            if int(row[expert]) != 1:
                continue
            st = base.router_stats(hist, expert, row["legacy_bucket"])
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
                base.ROUTER_TIE_ORDER[x[0]],
            ))
            selected, st = eligible[0]
            row.update({
                "router_up": 1,
                "selected_expert": selected,
                "selected_lcb": float(st["lcb"]),
                "selected_precision": float(st["precision"]),
                "selected_fpr": float(st["fpr"]),
                "selected_history_n_up": int(st["n_up"]),
                "selected_scope": st["scope"],
            })
        else:
            row.update({
                "router_up": 0,
                "selected_expert": "",
                "selected_lcb": None,
                "selected_precision": None,
                "selected_fpr": None,
                "selected_history_n_up": None,
                "selected_scope": "",
            })
        scored.append(row)
        # Frozen algorithm updates competence causally after each matured target.
        hist.append(dict(raw))
    return scored, hist


def build_router_extension(base, days):
    base_rows = build_all_base_rows(base, days)
    by_year = defaultdict(list)
    for r in base_rows:
        by_year[int(r["target_date"][:4])].append(r)

    # Preserve frozen 2022/2023 historical extension exactly via frozen code.
    tdays, bdays, ldays, daily = base.transformed(days)
    hist_frozen = base.build_router_rows(
        base.ttsm_mod.build_signal_rows(tdays),
        base.bonato_maps(bdays),
        base.logit_maps(ldays),
        base.legacy_context(daily),
    )
    out = [r for r in hist_frozen if int(r["target_date"][:4]) in (2022, 2023)]

    # Preserve frozen 2024 -> 2025 path, then extend that same causal path into 2026.
    s24, h24 = score_router_year(base, by_year.get(2024, []), by_year.get(2023, []))
    s25, h25 = score_router_year(base, by_year.get(2025, []), h24)
    s26, _ = score_router_year(base, by_year.get(2026, []), h25)
    out += s24 + s25 + s26
    return out


def primary_metrics(rows):
    calls = [r for r in rows if int(r["router_up"]) == 1]
    tp = sum(int(r["actual_up"]) == 1 for r in calls)
    fp = len(calls) - tp
    actual_up = sum(int(r["actual_up"]) == 1 for r in rows)
    actual_down = len(rows) - actual_up
    return {
        "n": len(rows),
        "up_outputs": len(calls),
        "coverage": len(calls) / len(rows) if rows else None,
        "true_up": tp,
        "false_up": fp,
        "up_precision": tp / len(calls) if calls else None,
        "up_alarm_error": fp / len(calls) if calls else None,
        "false_up_fpr": fp / actual_down if actual_down else None,
        "actual_up_recall": tp / actual_up if actual_up else None,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "abstain": len(rows) - len(calls),
        "selected_counts": dict(Counter(r["selected_expert"] for r in calls)),
        "legacy_bucket_counts": dict(Counter(r["legacy_bucket"] for r in calls)),
    }


def build_external_cases(route, up2, base, sqrt_mod, raw_root, external_spine):
    ext_raw = route.build_external_5m(raw_root)
    ext_spine = route.load_external_spine(external_spine)
    audit = route.external_reconstruction_audit(ext_raw, ext_spine)
    if not audit["passed"]:
        raise RuntimeError(f"EXTERNAL_RECON_FAIL:{audit}")

    ext_daily = route.load_external_daily_for_sqrt(ext_spine)
    ext_sqrt, ext_sqrt_summary = route.external_sqrt_cases(sqrt_mod, ext_daily)
    ext_router, ext_router_summary = route.external_router_rows(base, ext_spine)
    ext_unresolved, ext_route_summary = route.route_external_sqrt_cases(ext_sqrt, ext_router)

    expected_sqrt = {
        "2020": {"alarms": 212, "down": 97, "up": 115},
        "2021": {"alarms": 28, "down": 16, "up": 12},
    }
    expected_route = {
        "2020": {"sqrt_alarms": 212, "router_up_overlap": 140, "overlap_actual_up": 80,
                 "overlap_actual_down": 60, "router_abstain": 72,
                 "abstain_actual_down": 37, "abstain_actual_up": 35},
        "2021": {"sqrt_alarms": 28, "router_up_overlap": 2, "overlap_actual_up": 1,
                 "overlap_actual_down": 1, "router_abstain": 26,
                 "abstain_actual_down": 15, "abstain_actual_up": 11},
    }
    if ext_sqrt_summary != expected_sqrt:
        raise RuntimeError(f"EXTERNAL_SQRT_MISMATCH:{ext_sqrt_summary}")
    if ext_route_summary != expected_route:
        raise RuntimeError(f"EXTERNAL_ROUTE_MISMATCH:{ext_route_summary}")

    ext_router_map = {(r["origin_date"], r["target_date"]): r for r in ext_router}
    ext_sqrt_map = {(r["origin_date"], r["target_date"]): r for r in ext_sqrt}
    ext_lag = up2.lag_map_from_spine(ext_spine)

    cases = []
    for r in ext_unresolved:
        key = (r["origin_date"], r["target_date"])
        rr = ext_router_map[key]
        sr = ext_sqrt_map[key]
        cases.append(up2.enrich_case(
            r,
            sr["sqrt_normalized_risk_score"],
            rr,
            ext_lag[r["origin_date"]],
            ext_raw[r["origin_date"]]["rets"],
            "EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN",
        ))
    if len(cases) != 98 or sum(int(r["actual_up"]) for r in cases) != 46:
        raise RuntimeError("EXTERNAL_CASE_COUNT_FAIL")
    return cases, audit, ext_sqrt_summary, ext_router_summary, ext_route_summary


def governed_residual_cases(up2, cbr, days, router_rows, parent_rows):
    rmap = {(r["origin_date"], r["target_date"]): r for r in router_rows}
    high = [r for r in parent_rows if int(r["sqrt_alert"]) == 1]
    origin_dates = sorted({r["origin_date"] for r in high})
    raw_paths = cbr.load_paths(origin_dates)
    lag = up2.lag_map_from_base_days(days)

    cases = []
    for s in high:
        key = (s["origin_date"], s["target_date"])
        rr = rmap.get(key)
        if rr is None:
            raise RuntimeError(f"ROUTER_ROW_NOT_FOUND:{key}")
        if int(rr["actual_up"]) != int(s["actual_up"]):
            raise RuntimeError(f"ROUTER_PARENT_LABEL_MISMATCH:{key}")
        if int(rr["router_up"]) == 1:
            continue
        if s["origin_date"] not in raw_paths:
            raise RuntimeError(f"RAW_PATH_NOT_FOUND:{s['origin_date']}")
        if s["origin_date"] not in lag:
            raise RuntimeError(f"LAG_NOT_FOUND:{s['origin_date']}")
        case = {
            "evaluation_year": int(s["evaluation_year"]),
            "origin_date": s["origin_date"],
            "target_date": s["target_date"],
            "actual_up": int(s["actual_up"]),
        }
        cases.append(up2.enrich_case(
            case,
            s["sqrt_score"],
            rr,
            lag[s["origin_date"]],
            raw_paths[s["origin_date"]],
            "GOVERNED_ROUTER_ABSTAIN",
        ))
    return cases


def residual_summary(cases, year):
    q = [r for r in cases if int(r["evaluation_year"]) == year]
    u = sum(int(r["actual_up"]) for r in q)
    return {"n": len(q), "actual_up": u, "actual_down": len(q) - u}


def combined_sqrt_positive_metrics(parent_rows, router_rows, scored26):
    rmap = {(r["origin_date"], r["target_date"]): r for r in router_rows}
    u2map = {(r["origin_date"], r["target_date"]): r for r in scored26}
    alarms = [r for r in parent_rows if r["evaluation_year"] == 2026 and int(r["sqrt_alert"]) == 1]
    emitted = []
    for s in alarms:
        rr = rmap[(s["origin_date"], s["target_date"])]
        source = None
        if int(rr["router_up"]) == 1:
            source = "PRIMARY_UP"
        else:
            u = u2map.get((s["origin_date"], s["target_date"]))
            if u is not None and int(u["up2_call"]) == 1:
                source = "UP2"
        if source:
            emitted.append({**s, "source": source})
    tp = sum(r["actual_up"] == 1 for r in emitted)
    fp = len(emitted) - tp
    actual_down = sum(r["actual_up"] == 0 for r in alarms)
    actual_up = sum(r["actual_up"] == 1 for r in alarms)
    return {
        "sqrt_alarm_n": len(alarms),
        "sqrt_actual_up": actual_up,
        "sqrt_actual_down": actual_down,
        "positive_up_outputs": len(emitted),
        "true_up": tp,
        "false_up": fp,
        "precision": tp / len(emitted) if emitted else None,
        "call_error_rate": fp / len(emitted) if emitted else None,
        "false_up_fpr_on_sqrt_actual_down": fp / actual_down if actual_down else None,
        "up_recall_within_sqrt": tp / actual_up if actual_up else None,
        "source_counts": dict(Counter(r["source"] for r in emitted)),
    }, emitted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-module", type=Path, required=True)
    ap.add_argument("--route-module", type=Path, required=True)
    ap.add_argument("--up2-module", type=Path, required=True)
    ap.add_argument("--cbr-module", type=Path, required=True)
    ap.add_argument("--sqrt-code", type=Path, required=True)
    ap.add_argument("--sqrt-parent", type=Path, required=True)
    ap.add_argument("--external-spine", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    base = load_mod("frozen_base_2026_replay", args.base_module)
    route = load_mod("frozen_route_2026_replay", args.route_module)
    up2 = load_mod("frozen_up2_2026_replay", args.up2_module)
    cbr = load_mod("frozen_cbr_2026_replay", args.cbr_module)
    sqrt_mod = route.load_sqrt_mod(args.sqrt_code)

    # Extend only the data horizon. Model/routing rules remain frozen.
    base.CUTOFF = "2026-09-01T05:00:00Z"
    days = base.load_days()
    if not days or days[-1].d.isoformat() < "2026-08-31":
        raise RuntimeError(f"GOVERNED_DATA_HORIZON_SHORT:{days[-1].d if days else None}")

    parent = load_parent(args.sqrt_parent)
    last_2026_target = max(r["target_date"] for r in parent if r["evaluation_year"] == 2026)

    router = build_router_extension(base, days)
    router26 = [r for r in router if int(r["target_date"][:4]) == 2026 and r["target_date"] <= last_2026_target]

    integrity = []

    # Historical Primary reproduction.
    for y, exp in EXPECTED_PRIMARY.items():
        q = [r for r in router if int(r["target_date"][:4]) == y]
        m = primary_metrics(q)
        if (m["up_outputs"], m["true_up"], m["false_up"]) != (exp["up"], exp["tp"], exp["fp"]):
            integrity.append(
                f"PRIMARY_{y}:{m['up_outputs']}/{m['true_up']}/{m['false_up']}!="
                f"{exp['up']}/{exp['tp']}/{exp['fp']}"
            )

    external_cases, ext_audit, ext_sqrt_summary, ext_router_summary, ext_route_summary = build_external_cases(
        route, up2, base, sqrt_mod, args.raw_root, args.external_spine
    )
    governed_cases = governed_residual_cases(up2, cbr, days, router, parent)

    # Exact route-count integrity.
    for y, (n, u, d) in EXPECTED_RESIDUAL.items():
        s = residual_summary(governed_cases, y)
        if (s["n"], s["actual_up"], s["actual_down"]) != (n, u, d):
            integrity.append(
                f"RESIDUAL_{y}:{s['n']}/{s['actual_up']}/{s['actual_down']}!={n}/{u}/{d}"
            )

    # Reproduce frozen UP2 chronology before scoring 2026.
    historical_by_year = {y: [r for r in governed_cases if r["evaluation_year"] == y] for y in (2022, 2023, 2024, 2025)}
    scored_hist = {}
    all_hist = list(external_cases)
    for y in (2022, 2023, 2024, 2025):
        scored, met = up2.score_year(all_hist, historical_by_year[y], y)
        scored_hist[y] = met
        exp = EXPECTED_UP2[y]
        got = (met.get("up2_calls"), met.get("true_up"), met.get("false_up"))
        if got != exp:
            integrity.append(f"UP2_{y}:{got}!={exp}")
        all_hist += historical_by_year[y]

    test26 = [r for r in governed_cases if r["evaluation_year"] == 2026]
    scored26, up2_2026 = up2.score_year(all_hist, test26, 2026)
    if up2_2026.get("status") != "OK":
        integrity.append(f"UP2_2026_STATUS:{up2_2026.get('status')}")

    primary_2026 = primary_metrics(router26)
    residual_2026 = residual_summary(governed_cases, 2026)
    combined_2026, combined_rows = combined_sqrt_positive_metrics(parent, router, scored26)

    status = "PASS" if not integrity else "BLOCKED_INTEGRITY_MISMATCH"

    result = {
        "identity": IDENTITY,
        "date": "2026-10-02",
        "status": status,
        "evidence_role": "2026_RETROSPECTIVE_STRESS_ONLY",
        "last_2026_target_date": last_2026_target,
        "integrity_errors": integrity,
        "primary_up_v2_2026": primary_2026,
        "sqrt_primary_residual_2026": residual_2026,
        "up2_2026": up2_2026,
        "combined_positive_up_inside_sqrt_2026": combined_2026,
        "historical_reproduction": {
            "up2": scored_hist,
            "external_reconstruction": ext_audit,
            "external_sqrt_summary": ext_sqrt_summary,
            "external_router_summary": ext_router_summary,
            "external_route_summary": ext_route_summary,
        },
        "governance": {
            "model_changes": False,
            "threshold_changes": False,
            "expert_membership_changes": False,
            "2026_used_for_selection": False,
            "production_writes": False,
            "runtime_promotion": False,
        },
    }
    (args.out / "GOLD_CONTROL_UP_CASCADE_2026_REPLAY_RESULT_2026-10-02.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Primary standalone ledger.
    with (args.out / "GOLD_CONTROL_PRIMARY_UP_V2_2026_LEDGER_2026-10-02.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        fields = [
            "origin_date","target_date","actual_up","router_up","selected_expert",
            "selected_lcb","selected_precision","selected_fpr","selected_history_n_up",
            "selected_scope","legacy_bucket","legacy_up_count",
            *base.DIRECT_UP_EXPERTS,
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in router26:
            w.writerow({k: r.get(k, "") for k in fields})

    # 2026 UP2 residual ledger.
    if scored26:
        fields = [
            "evaluation_year","origin_date","target_date","actual_up","source",
            *up2.FEATURES,"p_up","tau","up2_call",
        ]
        with (args.out / "GOLD_CONTROL_UP2_2026_LEDGER_2026-10-02.csv").open(
            "w", newline="", encoding="utf-8"
        ) as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in scored26:
                w.writerow({k: r.get(k, "") for k in fields})

    # Combined emitted UP ledger inside SQRT.
    with (args.out / "GOLD_CONTROL_UP_CASCADE_2026_EMITTED_UP_LEDGER_2026-10-02.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        fields = ["evaluation_year","origin_date","target_date","actual_up","sqrt_score","source"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in combined_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    def pct(x):
        return "NA" if x is None else f"{100*x:.2f}%"

    lines = [
        "# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY",
        "",
        f"**Status:** \`{status}\`",
        f"**Evaluated through target:** **{last_2026_target}**",
        "",
        "No model, threshold or expert-membership rule was changed.",
        "",
        "## Primary UP Verifier V2 — standalone 2026",
        "",
        f"- eligible timeline n: **{primary_2026['n']}**",
        f"- UP outputs: **{primary_2026['up_outputs']}**",
        f"- true / false UP: **{primary_2026['true_up']} / {primary_2026['false_up']}**",
        f"- precision: **{pct(primary_2026['up_precision'])}**",
        f"- call-level false alarm: **{pct(primary_2026['up_alarm_error'])}**",
        f"- false-UP FPR: **{pct(primary_2026['false_up_fpr'])}**",
        f"- actual-UP recall: **{pct(primary_2026['actual_up_recall'])}**",
        f"- coverage: **{pct(primary_2026['coverage'])}**",
        f"- selected experts: \`{json.dumps(primary_2026['selected_counts'], sort_keys=True)}\`",
        "",
        "## SQRT high-risk residual after Primary UP",
        "",
        f"- residual n: **{residual_2026['n']}**",
        f"- actual UP / DOWN: **{residual_2026['actual_up']} / {residual_2026['actual_down']}**",
        "",
        "## One-Sided UP-2 — 2026 residual",
        "",
        f"- UP2 calls: **{up2_2026.get('up2_calls')}**",
        f"- true / false UP: **{up2_2026.get('true_up')} / {up2_2026.get('false_up')}**",
        f"- precision: **{pct(up2_2026.get('up_precision'))}**",
        f"- call-level false alarm: **{pct(None if up2_2026.get('up_precision') is None else 1-up2_2026.get('up_precision'))}**",
        f"- missed-UP recall: **{pct(up2_2026.get('missed_up_recall'))}**",
        f"- false-UP FPR: **{pct(up2_2026.get('false_up_fpr'))}**",
        f"- coverage: **{pct(up2_2026.get('coverage'))}**",
        f"- AUC: **{up2_2026.get('auc')}**",
        f"- Brier: **{up2_2026.get('brier')}**",
        f"- tau_2026: **{up2_2026.get('tau')}**",
        "",
        "## Combined positive-UP evidence inside SQRT route",
        "",
        f"- emitted UP: **{combined_2026['positive_up_outputs']}**",
        f"- true / false UP: **{combined_2026['true_up']} / {combined_2026['false_up']}**",
        f"- precision: **{pct(combined_2026['precision'])}**",
        f"- call-level false alarm: **{pct(combined_2026['call_error_rate'])}**",
        f"- false-UP FPR on actual-DOWN SQRT rows: **{pct(combined_2026['false_up_fpr_on_sqrt_actual_down'])}**",
        f"- UP recall inside SQRT route: **{pct(combined_2026['up_recall_within_sqrt'])}**",
        f"- source counts: \`{json.dumps(combined_2026['source_counts'], sort_keys=True)}\`",
        "",
        "2026 is retrospective stress and was not used to alter the frozen algorithms.",
    ]
    if integrity:
        lines += ["", "## Integrity errors", "", *[f"- {x}" for x in integrity]]
    (args.out / "GOLD_CONTROL_UP_CASCADE_2026_REPLAY_RESULT_2026-10-02.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not integrity else 2


if __name__ == "__main__":
    raise SystemExit(main())
