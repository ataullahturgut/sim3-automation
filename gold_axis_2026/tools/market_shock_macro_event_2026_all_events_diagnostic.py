from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest, fisher_exact, mannwhitneyu

import market_shock_macro_event_joint_audit_v1 as base
import market_shock_macro_event_joint_audit_2026ytd as ytd


def safe_float(x):
    if x is None:
        return None
    x = float(x)
    if math.isinf(x):
        return "INF" if x > 0 else "-INF"
    if math.isnan(x):
        return None
    return x


def exact_binom(hits: int, n: int):
    return float(binomtest(hits, n, p=0.5, alternative="greater").pvalue) if n else None


def main() -> int:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    ms = base.load_market_shock_module()
    with psycopg.connect(db) as conn:
        lineage = ytd.verify_cache_lineage(conn)
        raw = ytd.load_xau(conn)
        macro = ytd.load_macro(conn)

    seg, segment_reports = ytd.score_market_shock(ms, raw)
    macro = macro.copy().sort_values("observation_ts").reset_index(drop=True)
    macro["abs_score"] = macro["score"].abs()
    macro["frozen_class"] = np.where(macro["state"].isin(base.STRONG_STATES), "STRONG", "NON_STRONG")

    rows = []
    control_total = 0
    control_shocks = 0
    direction_hits = 0
    direction_n = 0
    continuation_values = []
    continuation_hits = 0

    for _, ev in macro.iterrows():
        t = pd.Timestamp(ev["observation_ts"])
        score = float(ev["score"])
        macro_dir = int(np.sign(score))
        match = base.shock_match(seg, t)
        event_has = match is not None

        shock_ts = None
        shock_state = None
        shock_dir = None
        concordant = None
        signed_cont = None
        cont_hit = None

        if match is not None:
            shock_ts = pd.Timestamp(match["ts"])
            shock_state = str(match["shock_state"])
            shock_dir = int(np.sign(float(match["shock_direction"])))
            if macro_dir != 0 and shock_dir != 0:
                direction_n += 1
                concordant = shock_dir == macro_dir
                direction_hits += int(concordant)
                shock_close = float(match["close"])
                endpoint = base.close_at_or_before(seg[seg["ts"] > shock_ts], t + pd.Timedelta(minutes=30))
                if endpoint is not None:
                    end_close, _ = endpoint
                    signed_cont = macro_dir * math.log(end_close / shock_close)
                    continuation_values.append(signed_cont)
                    cont_hit = signed_cont > 0
                    continuation_hits += int(cont_hit)

        controls = []
        for d in base.CONTROL_OFFSETS_DAYS:
            if len(controls) >= 4:
                break
            ct = t + pd.Timedelta(days=d)
            if ct < ytd.START or ct >= ytd.END:
                continue
            if base.any_macro_near(macro, ct, 60):
                continue
            if not base.has_required_xau(seg, ct):
                continue
            cm = base.shock_match(seg, ct)
            controls.append({
                "control_ts": ct.isoformat(),
                "shock": cm is not None,
                "shock_ts": pd.Timestamp(cm["ts"]).isoformat() if cm is not None else None,
            })
            control_total += 1
            control_shocks += int(cm is not None)

        rows.append({
            "release_ts": t.isoformat(),
            "series_id": ev["series_id"],
            "family": ev["family"],
            "macro_score": score,
            "abs_macro_score": abs(score),
            "macro_state": ev["state"],
            "frozen_class": ev["frozen_class"],
            "macro_direction": macro_dir,
            "market_shock_present_0_10m": event_has,
            "market_shock_ts": shock_ts.isoformat() if shock_ts is not None else None,
            "market_shock_state": shock_state,
            "market_shock_direction": shock_dir,
            "direction_concordant": concordant,
            "post_shock_signed_log_return_to_30m": signed_cont,
            "post_shock_continuation_hit": cont_hit,
            "controls": controls,
        })

    rdf = pd.DataFrame(rows)
    n_events = len(rdf)
    event_shocks = int(rdf["market_shock_present_0_10m"].sum())
    if n_events == 0 or control_total == 0:
        raise RuntimeError(f"INSUFFICIENT_SAMPLE:{n_events}:{control_total}")

    event_no = n_events - event_shocks
    control_no = control_total - control_shocks
    odds_ratio, fisher_p = fisher_exact(
        [[event_shocks, event_no], [control_shocks, control_no]], alternative="greater"
    )
    event_rate = event_shocks / n_events
    control_rate = control_shocks / control_total
    risk_ratio = event_rate / control_rate if control_rate > 0 else float("inf")

    shock_scores = rdf.loc[rdf["market_shock_present_0_10m"] == True, "abs_macro_score"].astype(float).to_numpy()
    no_shock_scores = rdf.loc[rdf["market_shock_present_0_10m"] == False, "abs_macro_score"].astype(float).to_numpy()
    if len(shock_scores) and len(no_shock_scores):
        mw = mannwhitneyu(shock_scores, no_shock_scores, alternative="greater", method="auto")
        mw_u = float(mw.statistic)
        mw_p = float(mw.pvalue)
        auc_equiv = mw_u / (len(shock_scores) * len(no_shock_scores))
    else:
        mw_u = mw_p = auc_equiv = None

    direction_rate = direction_hits / direction_n if direction_n else None
    direction_p = exact_binom(direction_hits, direction_n)
    cont_n = len(continuation_values)
    cont_rate = continuation_hits / cont_n if cont_n else None
    cont_median = float(np.median(continuation_values)) if continuation_values else None

    state_strat = {}
    for cls, g in rdf.groupby("frozen_class"):
        ov = g[g["market_shock_present_0_10m"] == True]
        valid_dir = ov[ov["direction_concordant"].notna()]
        state_strat[str(cls)] = {
            "events": int(len(g)),
            "shock_overlaps": int(g["market_shock_present_0_10m"].sum()),
            "shock_rate": float(g["market_shock_present_0_10m"].mean()),
            "median_abs_score": float(g["abs_macro_score"].median()),
            "direction_concordant": int((valid_dir["direction_concordant"] == True).sum()),
            "direction_n": int(len(valid_dir)),
        }

    family = {}
    for fam, g in rdf.groupby("family", dropna=False):
        ov = g[g["market_shock_present_0_10m"] == True]
        valid_dir = ov[ov["direction_concordant"].notna()]
        family[str(fam)] = {
            "events": int(len(g)),
            "shock_overlaps": int(g["market_shock_present_0_10m"].sum()),
            "shock_rate": float(g["market_shock_present_0_10m"].mean()),
            "median_abs_score": float(g["abs_macro_score"].median()),
            "direction_concordant": int((valid_dir["direction_concordant"] == True).sum()),
            "direction_n": int(len(valid_dir)),
        }

    all_event_enrichment_supported = bool(event_rate > control_rate and fisher_p <= 0.10)
    score_magnitude_supported = bool(
        mw_p is not None and auc_equiv is not None and auc_equiv > 0.5 and mw_p <= 0.10
    )

    report = {
        "audit": "GOLD_CONTROL_MARKET_SHOCK_MACRO_EVENT_2026_ALL_EVENTS_DIAGNOSTIC",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "HISTORICAL_RESEARCH_AUDIT",
        "prospective_claim": False,
        "production_authority": False,
        "neon_write": False,
        "threshold_changed": False,
        "threshold_selected_from_outcomes": False,
        "market_shock_identity": "MARKET_SHOCK_CHALLENGER_V3",
        "market_shock_source_sha": "12edc11e42b58d9c91fb587efdda9269cae4c91a",
        "market_shock_standalone_status_unchanged": "FAILED_RESEARCH_GATES_NOT_PROMOTED",
        "macro_identity": "MACRO_EVENT_SUCCESSOR_V3",
        "primary_period": "2026-01-01/2026-08-31",
        "cache_lineage": lineage,
        "xau_rows_loaded": int(len(raw)),
        "macro_events": n_events,
        "market_shock_segment_reports": segment_reports,
        "all_event_enrichment": {
            "event_shocks": event_shocks,
            "event_windows": n_events,
            "event_rate": event_rate,
            "control_shocks": control_shocks,
            "control_windows": control_total,
            "control_rate": control_rate,
            "risk_ratio": safe_float(risk_ratio),
            "odds_ratio": safe_float(odds_ratio),
            "fisher_exact_one_sided_p": float(fisher_p),
            "supported": all_event_enrichment_supported,
        },
        "score_magnitude_association": {
            "shock_overlap_n": int(len(shock_scores)),
            "non_overlap_n": int(len(no_shock_scores)),
            "shock_overlap_median_abs_score": float(np.median(shock_scores)) if len(shock_scores) else None,
            "non_overlap_median_abs_score": float(np.median(no_shock_scores)) if len(no_shock_scores) else None,
            "mann_whitney_u": mw_u,
            "auc_equivalent": auc_equiv,
            "one_sided_p": mw_p,
            "supported": score_magnitude_supported,
            "interpretation": "DIAGNOSTIC_ONLY_NO_THRESHOLD_SELECTION",
        },
        "direction_concordance_all_overlaps": {
            "hits": direction_hits,
            "n": direction_n,
            "rate": direction_rate,
            "binomial_one_sided_p": direction_p,
        },
        "post_shock_continuation_all_overlaps": {
            "hits": continuation_hits,
            "n": cont_n,
            "hit_rate": cont_rate,
            "median_signed_log_return": cont_median,
        },
        "frozen_state_stratification": state_strat,
        "family_descriptive": family,
        "diagnostic_flags": {
            "all_event_enrichment_supported": all_event_enrichment_supported,
            "score_magnitude_supported": score_magnitude_supported,
            "subthreshold_information_present": bool(
                state_strat.get("NON_STRONG", {}).get("shock_overlaps", 0) > 0
            ),
        },
        "interpretation_lock": "DIAGNOSTIC_ONLY; NO NEW MACRO THRESHOLD; NO MARKET_SHOCK_REHABILITATION; NO PRODUCTION AUTHORITY",
    }

    Path("market_shock_macro_event_2026_all_events_diagnostic_report.json").write_text(
        json.dumps(report, indent=2, default=str, allow_nan=False), encoding="utf-8"
    )
    rdf.to_csv("market_shock_macro_event_2026_all_events_diagnostic_events.csv", index=False)
    print(json.dumps(report, indent=2, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
