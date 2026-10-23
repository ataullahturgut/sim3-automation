"""Neon GOLD H=1 eight-feature data adapter (research replay; no live/PIT claim).

Existing ANFIS/RBFNN mathematical solvers are unchanged. Old CORE5 gold price is
replaced by the exact aligned four-metal StakTrakr monthly means. The GPR history
for each forecast origin MUST come from that origin's own official Git vintage.
Retrospective price reconstruction is NOT certified historical as-of pricing.
"""
from __future__ import annotations

import calendar
import math
from collections import defaultdict
from datetime import date, datetime, timezone

import numpy as np
import psycopg

PRICE_COMMIT_OLD = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
PRICE_COMMIT_2026 = "02964d0324dde362099976c867f5077a369acaa5"
GPR_REPOSITORY = "iacoviel/iacoviel.github.io"
METAL_CODES = {"AU": "Gold", "AG": "Silver", "PT": "Platinum", "PD": "Palladium"}
FIRST_MONTH, LAST_MONTH = "2010-01", "2026-09"
FIRST_ORIGIN, LAST_ORIGIN = "2022-03", "2026-09"
EVIDENCE_ARCHIVE = "OFFICIAL_HISTORICAL_GIT_VINTAGE_RECONSTRUCTION"
EVIDENCE_SEPTEMBER = "OFFICIAL_SEP_2026_VINTAGE_CROSSCHECKED"

# IMPORTANT: match the authoritative monthly Neon view exactly (weekday intersection).
PRICE_SQL = """
WITH old_days AS (
 SELECT CASE o.series_id WHEN 'XAU_STAKTRAKR_RESEARCH_DAILY_R1' THEN 'AU'
 WHEN 'XAG_STAKTRAKR_RESEARCH_DAILY_R1' THEN 'AG'
 WHEN 'XPT_STAKTRAKR_RESEARCH_DAILY_R1' THEN 'PT'
 WHEN 'XPD_STAKTRAKR_RESEARCH_DAILY_R1' THEN 'PD' END AS metal,
 o.observation_ts::date AS price_date, o.value AS price_usd_oz,
 o.source AS revision
 FROM public.observations o
 WHERE o.series_id IN ('XAU_STAKTRAKR_RESEARCH_DAILY_R1',
 'XAG_STAKTRAKR_RESEARCH_DAILY_R1','XPT_STAKTRAKR_RESEARCH_DAILY_R1',
 'XPD_STAKTRAKR_RESEARCH_DAILY_R1')
 AND o.observation_ts >= DATE '2010-01-01'
 AND o.observation_ts < DATE '2026-01-01'
 AND o.source = 'lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01'
 AND o.metadata->>'payload_provider_label'='LBMA'
 AND o.metadata->>'payload_source_label'='seed'
 AND o.quality_status='APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT'
 AND EXTRACT(ISODOW FROM o.observation_ts) BETWEEN 1 AND 5
), new_days AS (
 SELECT s.metal,s.price_date,s.price_usd_oz,
 (s.source_repository || '@' || s.snapshot_commit) AS revision
 FROM gold_monthly_h1.staktrakr_2026_git_snapshot_daily_v1 s
 WHERE s.snapshot_commit = '02964d0324dde362099976c867f5077a369acaa5'
 AND s.source_repository = 'lbruton/StakTrakr'
 AND s.evidence_status = 'RESEARCH_GIT_SNAPSHOT_NOT_PIT'
 AND s.price_date >= DATE '2026-01-01'
 AND s.price_date < DATE '2026-10-01'
 AND EXTRACT(ISODOW FROM s.price_date) BETWEEN 1 AND 5
)
SELECT metal,price_date,price_usd_oz,revision FROM old_days
UNION ALL
SELECT metal,price_date,price_usd_oz,revision FROM new_days
ORDER BY price_date,metal
"""
MONTHLY_SQL = """
SELECT metal,observed_month,monthly_average_usd_oz,weekday_observations,
       source_revisions,research_only
FROM gold_monthly_h1.staktrakr_single_repository_monthly_research_v1
WHERE observed_month BETWEEN DATE '2010-01-01' AND DATE '2026-09-01'
ORDER BY observed_month,metal
"""
GPR_AUDIT_SQL = """
SELECT origin_month,gpr_observation_month,gpr_value,source_repository,
 official_source_file,official_commit_sha,official_committed_at,
 forecast_cutoff_exclusive_at,source_series_id,evidence_class,original_live_capture
FROM gold_monthly_h1.gpr_origin_safe_model_v1 ORDER BY origin_month
"""
GPR_HISTORY_SQL = """
SELECT metadata->>'origin_month' AS origin_month,observation_ts::date AS observation_month,
 value,available_as_of,metadata->>'archive_path' AS source_path,
 metadata->>'archive_commit_sha' AS source_commit
FROM public.observations WHERE series_id='GPR_OFFICIAL_GIT_PIT'
AND source='Caldara-Iacoviello official GitHub archive'
AND quality_status='APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH'
AND metadata->>'origin_month' BETWEEN '2022-03' AND '2026-08'
ORDER BY origin_month,observation_ts
"""
GPR_SEP_SQL = """
SELECT observation_month,series_value,source_revision_hash,
 COALESCE(provenance_metadata->>'original_official_git_commit',
          provenance_metadata->>'source_commit') AS source_commit,
 verified_git_commit_at
FROM gold_monthly_h1.original_source_shadow_monthly_v1
WHERE source_family='GPR_OFFICIAL_GIT' AND source_version='2026-09'
 AND series_name='GPR' AND observation_month <= DATE '2026-08-01'
 AND source_repository_or_url =
 'iacoviel/iacoviel.github.io/gpr_archive_files/data_gpr_export_202609.xls'
ORDER BY observation_month
"""


def month(x):
    if isinstance(x, (date, datetime)):
        return x.strftime("%Y-%m")
    return str(x)[:7]


def previous(m):
    y, k = map(int, m.split("-"))
    return f"{y - 1:04d}-12" if k == 1 else f"{y:04d}-{k - 1:02d}"


def next_month(m):
    y, k = map(int, m.split("-"))
    return f"{y + 1:04d}-01" if k == 12 else f"{y:04d}-{k + 1:02d}"


def months_between(start, end):
    m = start
    while m <= end:
        yield m
        m = next_month(m)


def require(test, label):
    if not test:
        raise RuntimeError("GOLD_H1_NEON_SOURCE_" + label)


def normalize_daily(daily_rows, monthly_rows):
    """Pure source parity gate; follows four-metal weekday intersection rule."""
    by_date = defaultdict(dict)
    for metal, d, value, revision in daily_rows:
        require(metal in METAL_CODES, "BAD_METAL")
        k = month(d)
        require(FIRST_MONTH <= k <= LAST_MONTH, "FUTURE_PRICE_MONTH")
        expected = "lbruton/StakTrakr@" + (PRICE_COMMIT_OLD if k < "2026-01" else PRICE_COMMIT_2026)
        require(revision == expected, "PRICE_WRONG_PINNED_COMMIT")
        require(d.isoweekday() <= 5, "PRICE_WEEKEND")
        require(math.isfinite(float(value)) and float(value) > 0, "PRICE_NONFINITE")
        require(metal not in by_date[d], "PRICE_DUPLICATE_DATE_METAL")
        by_date[d][metal] = float(value)

    aligned = defaultdict(lambda: defaultdict(list))
    for d in sorted(by_date):
        if set(by_date[d]) != set(METAL_CODES):
            continue
        for code, name in METAL_CODES.items():
            aligned[name][month(d)].append(by_date[d][code])
    required_months = list(months_between(FIRST_MONTH, LAST_MONTH))
    daily = {}
    means = {}
    for name in METAL_CODES.values():
        require(set(aligned[name]) == set(required_months), "MONTHS_MISSING_" + name)
        for m in required_months:
            prices = aligned[name][m]
            require(len(prices) >= 15, "TOO_FEW_COMMON_DAYS_" + m)
        daily[name] = {m: np.asarray(v, dtype=float) for m, v in aligned[name].items()}
        means[name] = {m: float(np.mean(v)) for m, v in aligned[name].items()}

    seen = set()
    for metal, d, mean, n, revisions, research_only in monthly_rows:
        m = month(d)
        if metal not in METAL_CODES or not (FIRST_MONTH <= m <= LAST_MONTH):
            raise RuntimeError("GOLD_H1_NEON_SOURCE_WRONG_MONTHLY_VIEW_ROW")
        require((metal, m) not in seen, "MONTHLY_DUPLICATE")
        seen.add((metal, m))
        name = METAL_CODES[metal]
        expected = "lbruton/StakTrakr@" + (PRICE_COMMIT_OLD if m < "2026-01" else PRICE_COMMIT_2026)
        require(revisions == expected, "MONTHLY_SOURCE_MISMATCH")
        require(research_only is True, "MONTHLY_FALSE_PIT_CLAIM")
        require(int(n) == len(daily[name][m]), "DAILY_MONTHLY_COUNT_MISMATCH")
        require(abs(float(mean) - means[name][m]) < 1e-6, "DAILY_MONTHLY_PRICE_MISMATCH")
    require(len(seen) == len(required_months) * 4, "MONTHLY_PANEL_INCOMPLETE")
    return daily, means, {"aligned_days": len([d for d in by_date if len(by_date[d]) == 4]),
                          "metal_months": 4 * len(required_months),
                          "source_pit_verified": False,
                          "source_class": "PINNED_RESEARCH_GIT_NOT_ASOF_PROVEN"}


def validate_gpr(audit_rows, history_rows, sep_rows):
    """Full per-origin GPR history needed for 8-feature VW; scalar lag is insufficient."""
    audit = {}
    for r in audit_rows:
        (origin, observed, value, repository, src, sha, released, cutoff,
         series, evidence, live) = r
        o = month(origin)
        require(FIRST_ORIGIN <= o <= LAST_ORIGIN, "GPR_WRONG_ORIGIN")
        require(o not in audit, "GPR_DUPLICATE_ORIGIN")
        require(month(observed) == previous(o), "GPR_OBSERVATION_LAG")
        require(repository == GPR_REPOSITORY and series == "GPR_OFFICIAL_GIT_PIT",
                "GPR_WRONG_SERIES")
        require(src == "gpr_archive_files/data_gpr_export_" + o.replace("-", "") + ".xls",
                "GPR_WRONG_VINTAGE_FILENAME")
        require(isinstance(sha, str) and len(sha) == 40, "GPR_BAD_SOURCE_SHA")
        require(released.tzinfo is not None and cutoff.tzinfo is not None and released < cutoff,
                "GPR_FUTURE_RELEASE")
        require(live is False, "GPR_WRONG_LIVE_EVIDENCE")
        require(evidence == (EVIDENCE_SEPTEMBER if o == LAST_ORIGIN else EVIDENCE_ARCHIVE),
                "GPR_WRONG_EVIDENCE_CLASS")
        require(math.isfinite(float(value)) and value > 0, "GPR_INVALID_VALUE")
        audit[o] = (float(value), src, sha, released, cutoff)
    require(set(audit) == set(months_between(FIRST_ORIGIN, LAST_ORIGIN)),
            "GPR_ORIGIN_COVERAGE_MISSING")

    vintages = defaultdict(dict)
    for o, d, val, available, source_path, sha in history_rows:
        require(o in audit and o != LAST_ORIGIN, "GPR_UNAPPROVED_HISTORY_ORIGIN")
        v, f, commit, released, cutoff = audit[o]
        require(source_path == f and sha == commit, "GPR_HISTORY_WRONG_VINTAGE")
        require(available is not None and available <= cutoff and available == released,
                "GPR_HISTORY_FUTURE_SOURCE")
        m = month(d)
        require(m <= previous(o), "GPR_HISTORY_FUTURE_MONTH")
        require(m not in vintages[o], "GPR_HISTORY_DUPLICATE_MONTH")
        require(math.isfinite(float(val)) and float(val) > 0, "GPR_HISTORY_INVALID")
        vintages[o][m] = float(val)

    last = audit[LAST_ORIGIN]
    for d, val, blob, commit, released in sep_rows:
        m = month(d)
        require(m <= "2026-08", "GPR_SEPTEMBER_FUTURE_MONTH")
        require(m not in vintages[LAST_ORIGIN], "GPR_SEPTEMBER_DUPLICATE")
        require(commit == last[2] and released == last[3], "GPR_SEPTEMBER_REVISION_MISMATCH")
        require(blob == "253056ac5d54881c1f3e5767087ef682e258c7a5",
                "GPR_SEPTEMBER_BLOB_MISMATCH")
        require(math.isfinite(float(val)) and float(val) > 0, "GPR_SEPTEMBER_INVALID")
        vintages[LAST_ORIGIN][m] = float(val)

    for o, (v, _, _, _, _) in audit.items():
        lag = previous(o)
        require(lag in vintages[o], "GPR_MISSING_REQUIRED_LAG_" + o)
        require(len(vintages[o]) >= 24, "GPR_TOO_SHORT_" + o)
        require(abs(vintages[o][lag] - v) < 1e-6, "GPR_LAG_VALUE_MISMATCH_" + o)
    return dict(vintages), {"gpr_origin_vintages": len(vintages),
                           "missing_required_gpr_origins": [],
                           "late_required_gpr_origins": [],
                           "missing_required_gpr_lag_month": [],
                           "gpr_history_as_of_official_archive": True,
                           "original_live_capture": False}


def load_data_neon_h1(dsn):
    """Read only. Raises on every wrong/missing input, never falls back to CORE5."""
    import vw_midas_msvr_successor_v1 as base
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            invariant = base.authority_invariants(cur)
            cur.execute(PRICE_SQL)
            price_rows = cur.fetchall()
            cur.execute(MONTHLY_SQL)
            monthly_rows = cur.fetchall()
            cur.execute(GPR_AUDIT_SQL)
            gpr_audit = cur.fetchall()
            cur.execute(GPR_HISTORY_SQL)
            gpr_rows = cur.fetchall()
            cur.execute(GPR_SEP_SQL)
            sep_rows = cur.fetchall()
    daily, monthly, price_checks = normalize_daily(price_rows, monthly_rows)
    gpr, gpr_checks = validate_gpr(gpr_audit, gpr_rows, sep_rows)
    checks = {**price_checks, **gpr_checks, "core_gold_rows": len(monthly["Gold"]),
              "model_target": "NEXT_CALENDAR_MONTH_MEAN_XAU_USD",
              "historical_replay_only": True, "original_price_as_of_verified": False}
    # core_gold is a compatibility FIELD NAME in the old solver, NOT old CORE5 data.
    return base.DataBundle(
        core_gold=dict(monthly["Gold"]),
        core_gpr={},  # intentionally forbid old rounded CORE5 GPR reconciliation
        daily_month_values=daily,
        monthly_metal=monthly,
        gpr_vintages=gpr,
        source_checks=checks,
        invariants_before=invariant,
    )
