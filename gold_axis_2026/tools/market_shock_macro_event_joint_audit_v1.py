from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest, fisher_exact

SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]
STRONG_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
PRIMARY_YEARS = (2024, 2025)
CONTROL_OFFSETS_DAYS = (-7, 7, -14, 14, -21, 21, -28, 28)


def load_market_shock_module():
    module_dir = Path(os.environ["MARKET_SHOCK_MODULE_DIR"]).resolve()
    path = module_dir / "market_shock_challenger_v3.py"
    spec = importlib.util.spec_from_file_location("market_shock_challenger_v3_joint", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MARKET_SHOCK_V3_IMPORT_FAILED:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def fetch_df(conn, sql: str, params=()) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


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
    d = fetch_df(conn, q)
    if len(d) != 1:
        raise RuntimeError("XAU_5M_CACHE_BATCH_NOT_FOUND")
    r = d.iloc[0].to_dict()
    checks = {
        "provider": r["provider"] == "Twelve Data",
        "symbol": r["symbol"] == "XAU/USD",
        "interval": r["interval"] == "5min",
        "evidence_class": r["evidence_class"] == "HISTORICAL_RESEARCH_RETRIEVAL",
        "status": r["status"] == "COMPLETE",
        "coverage_start": pd.Timestamp(r["first_ts"], tz="UTC") <= pd.Timestamp("2020-04-06", tz="UTC"),
        "coverage_end": pd.Timestamp(r["last_ts"], tz="UTC") >= pd.Timestamp("2025-12-31 23:00", tz="UTC"),
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
      AND observation_ts <  '2026-01-01 00:00:00+00'
    ORDER BY observation_ts
    """
    d = fetch_df(conn, q)
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
      AND observation_ts >= '2024-01-01 00:00:00+00'
      AND observation_ts <  '2026-01-01 00:00:00+00'
    ORDER BY observation_ts, series_id
    """
    d = fetch_df(conn, q, (SERIES,))
    if d.empty:
        raise RuntimeError("MACRO_V3_SCORE_SERIES_EMPTY")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["score"] = d["value"].astype(float)
    d["state"] = d["metadata"].map(lambda x: (x or {}).get("state"))
    d["family"] = d["metadata"].map(lambda x: (x or {}).get("family"))
    return d


def score_market_shock(ms, raw: pd.DataFrame):
    data = ms.build_returns(raw)
    segments = []
    segment_reports = []
    for year in PRIMARY_YEARS:
        cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
        train = data[data["ts"] < cutoff].copy()
        if len(train) < 100000:
            raise RuntimeError(f"MARKET_SHOCK_TRAIN_TOO_SMALL:{year}:{len(train)}")
        periodicity = ms.fit_periodicity(train)
        train_scored = ms.add_scores(train, periodicity)
        evt30 = ms.fit_evt(train_scored["score30"])
        rep, seg, _ = ms.score_segment(data, year, periodicity, evt30)
        segment_reports.append(rep)
        segments.append(seg)
    out = pd.concat(segments, ignore_index=True).sort_values("ts").reset_index(drop=True)
    return out, segment_reports


def any_macro_near(all_macro: pd.DataFrame, t: pd.Timestamp, minutes: int = 60) -> bool:
    lo, hi = t - pd.Timedelta(minutes=minutes), t + pd.Timedelta(minutes=minutes)
    return bool(((all_macro["observation_ts"] >= lo) & (all_macro["observation_ts"] <= hi)).any())


def shock_match(seg: pd.DataFrame, t: pd.Timestamp):
    w = seg[(seg["ts"] >= t) & (seg["ts"] <= t + pd.Timedelta(minutes=10)) & seg["shock_sig"].fillna(False)].copy()
    if w.empty:
        return None
    return w.sort_values("ts").iloc[0]


def has_required_xau(seg: pd.DataFrame, t: pd.Timestamp) -> bool:
    w = seg[(seg["ts"] >= t) & (seg["ts"] <= t + pd.Timedelta(minutes=30))]
    return len(w) >= 4 and bool((w["ts"] <= t + pd.Timedelta(minutes=10)).any())


def close_at_or_before(seg: pd.DataFrame, t: pd.Timestamp):
    w = seg[seg["ts"] <= t]
    if w.empty:
        return None
    r = w.iloc[-1]
    return float(r["close"]), pd.Timestamp(r["ts"])


def exact_binom_p(hits: int, n: int) -> float | None:
    return float(binomtest(hits, n, p=0.5, alternative="greater").pvalue) if n else None


def main() -> int:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    ms = load_market_shock_module()

    with psycopg.connect(db) as conn:
        lineage = verify_cache_lineage(conn)
        raw = load_xau(conn)
        macro = load_macro(conn)

    seg, segment_reports = score_market_shock(ms, raw)
    strong = macro[macro["state"].isin(STRONG_STATES)].copy()
    strong["macro_direction"] = np.sign(strong["score"]).astype(int)
    if (strong["macro_direction"] == 0).any():
        raise RuntimeError("STRONG_MACRO_ZERO_DIRECTION")

    rows = []
    event_shock_count = 0
    control_total = 0
    control_shock_count = 0
    concordant = 0
    discordant = 0
    continuation_vals = []
    continuation_hits = 0

    start = pd.Timestamp("2024-01-01", tz="UTC")
    end = pd.Timestamp("2026-01-01", tz="UTC")

    for _, ev in strong.iterrows():
        t = pd.Timestamp(ev["observation_ts"])
        match = shock_match(seg, t)
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
                endpoint = close_at_or_before(seg[(seg["ts"] > shock_ts)], t + pd.Timedelta(minutes=30))
                if endpoint is not None:
                    end_close, end_ts = endpoint
                    signed_cont = macro_dir * math.log(end_close / shock_close)
                    continuation_vals.append(signed_cont)
                    continuation_hit = signed_cont > 0
                    continuation_hits += int(continuation_hit)
            else:
                discordant += 1

        controls = []
        for d in CONTROL_OFFSETS_DAYS:
            if len(controls) >= 4:
                break
            ct = t + pd.Timedelta(days=d)
            if ct < start or ct >= end:
                continue
            if any_macro_near(macro, ct, 60):
                continue
            if not has_required_xau(seg, ct):
                continue
            cm = shock_match(seg, ct)
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
    event_no = n_events - event_shock_count
    control_no = control_total - control_shock_count
    if n_events == 0 or control_total == 0:
        raise RuntimeError(f"INSUFFICIENT_JOINT_SAMPLE:{n_events}:{control_total}")

    odds_ratio, fisher_p = fisher_exact(
        [[event_shock_count, event_no], [control_shock_count, control_no]],
        alternative="greater",
    )
    event_rate = event_shock_count / n_events
    control_rate = control_shock_count / control_total
    risk_ratio = event_rate / control_rate if control_rate > 0 else float("inf")

    overlap_n = concordant + discordant
    concordance_rate = concordant / overlap_n if overlap_n else None
    concordance_p = exact_binom_p(concordant, overlap_n)
    cont_n = len(continuation_vals)
    cont_median = float(np.median(continuation_vals)) if continuation_vals else None
    cont_hit_rate = continuation_hits / cont_n if cont_n else None
    cont_p = exact_binom_p(continuation_hits, cont_n)

    gate_a = bool(risk_ratio > 1 and fisher_p <= 0.10)
    gate_b = bool(overlap_n > 0 and concordance_rate > 0.5 and concordance_p <= 0.10)
    gate_c = bool(cont_median is not None and cont_median > 0)
    if gate_a and gate_b and gate_c:
        status = "JOINT_CONTEXT_PASS"
    elif gate_a and gate_b:
        status = "CONTEXT_ASSOCIATION_ONLY"
    else:
        status = "JOINT_VALUE_NOT_PROVEN"

    family = {}
    rdf = pd.DataFrame(rows)
    for fam, g in rdf.groupby("family", dropna=False):
        ov = g[g["market_shock_present_0_10m"] == True]
        family[str(fam)] = {
            "strong_events": int(len(g)),
            "event_window_shocks": int(g["market_shock_present_0_10m"].sum()),
            "concordant": int((ov["direction_concordant"] == True).sum()),
            "discordant": int((ov["direction_concordant"] == False).sum()),
        }

    report = {
        "audit": "GOLD_CONTROL_MARKET_SHOCK_MACRO_EVENT_JOINT_AUDIT_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "HISTORICAL_RESEARCH_AUDIT",
        "prospective_claim": False,
        "production_authority": False,
        "neon_write": False,
        "market_shock_identity": "MARKET_SHOCK_CHALLENGER_V3",
        "market_shock_source_sha": "12edc11e42b58d9c91fb587efdda9269cae4c91a",
        "market_shock_standalone_status_unchanged": "FAILED_RESEARCH_GATES_NOT_PROMOTED",
        "macro_identity": "MACRO_EVENT_SUCCESSOR_V3",
        "primary_years": list(PRIMARY_YEARS),
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
                "risk_ratio": risk_ratio,
                "odds_ratio": float(odds_ratio),
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
        "interpretation_lock": "JOINT_PASS_IS_CONTEXT_CONFIRMATION_EVIDENCE_ONLY; DOES_NOT_REHABILITATE_MARKET_SHOCK_V3_STANDALONE_OR_AUTHORIZE_PRODUCTION",
    }

    Path("market_shock_macro_event_joint_audit_v1_report.json").write_text(
        json.dumps(report, indent=2, default=str, allow_nan=False), encoding="utf-8"
    )
    rdf.to_csv("market_shock_macro_event_joint_audit_v1_events.csv", index=False)
    print(json.dumps(report, indent=2, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
