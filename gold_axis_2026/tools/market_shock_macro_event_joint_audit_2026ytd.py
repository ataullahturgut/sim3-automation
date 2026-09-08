from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import fisher_exact

import market_shock_macro_event_joint_audit_v1 as base

PRIMARY_YEARS = (2026,)
START = pd.Timestamp("2026-01-01", tz="UTC")
END = pd.Timestamp("2026-09-01", tz="UTC")


def verify_cache_lineage(conn) -> dict:
    q = """
    SELECT batch_id, series_id, interval, first_ts, last_ts, retrieved_at,
           provider, symbol, evidence_class, purpose, row_count, inserted_count,
           payload_sha256, code_sha, status
    FROM xau_intraday_research_cache_batches
    WHERE interval='5min'
    ORDER BY batch_id DESC
    LIMIT 1
    """
    d = base.fetch_df(conn, q)
    if len(d) != 1:
        raise RuntimeError("XAU_5M_CACHE_BATCH_NOT_FOUND")
    r = d.iloc[0].to_dict()
    first_ts = pd.to_datetime(r["first_ts"], utc=True)
    last_ts = pd.to_datetime(r["last_ts"], utc=True)
    checks = {
        "provider": r["provider"] == "Twelve Data",
        "symbol": r["symbol"] == "XAU/USD",
        "interval": r["interval"] == "5min",
        "evidence_class": r["evidence_class"] == "HISTORICAL_RESEARCH_RETRIEVAL",
        "status": r["status"] == "COMPLETE",
        "coverage_start": first_ts <= pd.Timestamp("2020-04-06", tz="UTC"),
        "coverage_end": last_ts >= pd.Timestamp("2026-08-31 23:55", tz="UTC"),
    }
    if not all(checks.values()):
        raise RuntimeError(f"XAU_5M_CACHE_LINEAGE_FAIL:{checks}")
    out = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
    out["checks"] = checks
    return out


def load_xau(conn) -> pd.DataFrame:
    q = """
    SELECT observation_ts AS ts, close
    FROM xau_intraday_research_cache_5m
    WHERE observation_ts >= '2020-04-06 00:00:00+00'
      AND observation_ts <  '2026-09-01 00:00:00+00'
    ORDER BY observation_ts
    """
    d = base.fetch_df(conn, q)
    if d.empty:
        raise RuntimeError("XAU_5M_CACHE_EMPTY")
    d["ts"] = pd.to_datetime(d["ts"], utc=True)
    d["close"] = d["close"].astype(float)
    return d


def load_macro(conn) -> pd.DataFrame:
    q = """
    SELECT series_id, observation_ts, value, metadata
    FROM observations
    WHERE series_id = ANY(%s)
      AND observation_ts >= '2026-01-01 00:00:00+00'
      AND observation_ts <  '2026-09-01 00:00:00+00'
    ORDER BY observation_ts, series_id
    """
    d = base.fetch_df(conn, q, (base.SERIES,))
    if d.empty:
        raise RuntimeError("MACRO_V3_SCORE_SERIES_EMPTY")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["score"] = d["value"].astype(float)
    d["state"] = d["metadata"].map(lambda x: (x or {}).get("state"))
    d["family"] = d["metadata"].map(lambda x: (x or {}).get("family"))
    return d


def score_market_shock(ms, raw: pd.DataFrame):
    data = ms.build_returns(raw)
    cutoff = pd.Timestamp("2026-01-01", tz="UTC")
    train = data[data["ts"] < cutoff].copy()
    if len(train) < 100000:
        raise RuntimeError(f"MARKET_SHOCK_TRAIN_TOO_SMALL:2026:{len(train)}")
    periodicity = ms.fit_periodicity(train)
    train_scored = ms.add_scores(train, periodicity)
    evt30 = ms.fit_evt(train_scored["score30"])
    rep, seg, _ = ms.score_segment(data, 2026, periodicity, evt30)
    seg = seg[(seg["ts"] >= START) & (seg["ts"] < END)].copy()
    return seg.sort_values("ts").reset_index(drop=True), [rep]


def main() -> int:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    ms = base.load_market_shock_module()

    with psycopg.connect(db) as conn:
        lineage = verify_cache_lineage(conn)
        raw = load_xau(conn)
        macro = load_macro(conn)

    seg, segment_reports = score_market_shock(ms, raw)
    strong = macro[macro["state"].isin(base.STRONG_STATES)].copy()
    strong["macro_direction"] = np.sign(strong["score"]).astype(int)
    if (strong["macro_direction"] == 0).any():
        raise RuntimeError("STRONG_MACRO_ZERO_DIRECTION")

    rows = []
    event_shock_count = 0
    control_total = 0
    control_shock_count = 0
    concordant = 0
    discordant = 0
    continuation_vals: list[float] = []
    continuation_hits = 0

    for _, ev in strong.iterrows():
        t = pd.Timestamp(ev["observation_ts"])
        match = base.shock_match(seg, t)
        event_has = match is not None
        event_shock_count += int(event_has)

        macro_dir = int(ev["macro_direction"])
        shock_ts = shock_state = shock_dir = None
        is_concordant = None
        signed_cont = None
        continuation_hit = None

        if match is not None:
            shock_ts = pd.Timestamp(match["ts"])
            shock_state = str(match["shock_state"])
            shock_dir = int(np.sign(float(match["shock_direction"])))
            is_concordant = shock_dir == macro_dir and shock_dir != 0
            if is_concordant:
                concordant += 1
                shock_close = float(match["close"])
                endpoint = base.close_at_or_before(seg[seg["ts"] > shock_ts], t + pd.Timedelta(minutes=30))
                if endpoint is not None:
                    end_close, _ = endpoint
                    signed_cont = macro_dir * math.log(end_close / shock_close)
                    continuation_vals.append(signed_cont)
                    continuation_hit = signed_cont > 0
                    continuation_hits += int(continuation_hit)
            else:
                discordant += 1

        controls = []
        for d in base.CONTROL_OFFSETS_DAYS:
            if len(controls) >= 4:
                break
            ct = t + pd.Timedelta(days=d)
            if ct < START or ct >= END:
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
            control_shock_count += int(cm is not None)

        rows.append({
            "family": ev["family"],
            "series_id": ev["series_id"],
            "release_ts": t.isoformat(),
            "macro_score": float(ev["score"]),
            "macro_state": ev["state"],
            "macro_direction": macro_dir,
            "market_shock_present_0_10m": event_has,
            "market_shock_ts": shock_ts.isoformat() if shock_ts is not None else None,
            "market_shock_state": shock_state,
            "market_shock_direction": shock_dir,
            "direction_concordant": is_concordant,
            "post_confirm_signed_log_return_to_30m": signed_cont,
            "post_confirm_continuation_hit": continuation_hit,
            "controls": controls,
        })

    n_events = len(strong)
    if n_events == 0 or control_total == 0:
        raise RuntimeError(f"INSUFFICIENT_JOINT_SAMPLE:{n_events}:{control_total}")
    event_no = n_events - event_shock_count
    control_no = control_total - control_shock_count
    odds_ratio, fisher_p = fisher_exact(
        [[event_shock_count, event_no], [control_shock_count, control_no]],
        alternative="greater",
    )
    event_rate = event_shock_count / n_events
    control_rate = control_shock_count / control_total
    risk_ratio = event_rate / control_rate if control_rate > 0 else float("inf")

    overlap_n = concordant + discordant
    concordance_rate = concordant / overlap_n if overlap_n else None
    concordance_p = base.exact_binom_p(concordant, overlap_n)
    cont_n = len(continuation_vals)
    cont_median = float(np.median(continuation_vals)) if continuation_vals else None
    cont_hit_rate = continuation_hits / cont_n if cont_n else None
    cont_p = base.exact_binom_p(continuation_hits, cont_n)

    gate_a = bool(risk_ratio > 1 and fisher_p <= 0.10)
    gate_b = bool(overlap_n > 0 and concordance_rate > 0.5 and concordance_p <= 0.10)
    gate_c = bool(cont_median is not None and cont_median > 0)
    if gate_a and gate_b and gate_c:
        status = "JOINT_CONTEXT_PASS"
    elif gate_a and gate_b:
        status = "CONTEXT_ASSOCIATION_ONLY"
    else:
        status = "JOINT_VALUE_NOT_PROVEN"

    rdf = pd.DataFrame(rows)
    family = {}
    for fam, g in rdf.groupby("family", dropna=False):
        ov = g[g["market_shock_present_0_10m"] == True]
        family[str(fam)] = {
            "strong_events": int(len(g)),
            "event_window_shocks": int(g["market_shock_present_0_10m"].sum()),
            "concordant": int((ov["direction_concordant"] == True).sum()),
            "discordant": int((ov["direction_concordant"] == False).sum()),
        }

    def safe_float(x):
        if x is None:
            return None
        x = float(x)
        return "INF" if math.isinf(x) and x > 0 else "-INF" if math.isinf(x) else x

    report = {
        "audit": "GOLD_CONTROL_MARKET_SHOCK_MACRO_EVENT_JOINT_AUDIT_2026YTD",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "HISTORICAL_RESEARCH_AUDIT",
        "prospective_claim": False,
        "production_authority": False,
        "neon_write": False,
        "market_shock_identity": "MARKET_SHOCK_CHALLENGER_V3",
        "market_shock_source_sha": "12edc11e42b58d9c91fb587efdda9269cae4c91a",
        "market_shock_standalone_status_unchanged": "FAILED_RESEARCH_GATES_NOT_PROMOTED",
        "macro_identity": "MACRO_EVENT_SUCCESSOR_V3",
        "primary_period": "2026-01-01/2026-08-31",
        "cache_lineage": lineage,
        "xau_rows_loaded": int(len(raw)),
        "macro_all_events": int(len(macro)),
        "strong_macro_events": n_events,
        "market_shock_segment_reports": segment_reports,
        "primary_tests": {
            "shock_incidence_enrichment": {
                "event_shocks": event_shock_count,
                "event_windows": n_events,
                "event_rate": event_rate,
                "control_shocks": control_shock_count,
                "control_windows": control_total,
                "control_rate": control_rate,
                "risk_ratio": safe_float(risk_ratio),
                "odds_ratio": safe_float(odds_ratio),
                "fisher_exact_one_sided_p": float(fisher_p),
                "pass": gate_a,
            },
            "direction_concordance": {
                "concordant": concordant,
                "discordant": discordant,
                "overlap_n": overlap_n,
                "rate": concordance_rate,
                "binomial_one_sided_p": concordance_p,
                "pass": gate_b,
            },
            "post_confirmation_continuation": {
                "n": cont_n,
                "hits": continuation_hits,
                "hit_rate": cont_hit_rate,
                "median_signed_log_return": cont_median,
                "binomial_one_sided_p": cont_p,
                "pass": gate_c,
            },
        },
        "family_descriptive": family,
        "final_status": status,
        "interpretation_lock": "2026YTD_IS_SMALL_SAMPLE_HISTORICAL_CORROBORATION_ONLY; DOES_NOT_REHABILITATE_MARKET_SHOCK_V3_STANDALONE_OR_AUTHORIZE_PRODUCTION",
    }

    Path("market_shock_macro_event_joint_audit_2026ytd_report.json").write_text(
        json.dumps(report, indent=2, default=str, allow_nan=False), encoding="utf-8"
    )
    rdf.to_csv("market_shock_macro_event_joint_audit_2026ytd_events.csv", index=False)
    print(json.dumps(report, indent=2, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
