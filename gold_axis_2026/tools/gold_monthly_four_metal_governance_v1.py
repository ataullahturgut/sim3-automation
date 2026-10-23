"""Origin-safe, source-governed four-metal daily research panel.

Does not synthesize prices, carry-forward labels, overwrite originals, or
certify historical first-publication time. Date-only research records cannot
establish their true availability to a real-time forecaster.

Two evidence tiers:
  - homogeneous replay panel: four-metal matched business dates with known,
    mutually consistent provenance labels (still NOT live PIT verified);
  - shadow/quarantine: mixed/unknown provider, weekend or insufficient months.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

METALS = ("Gold", "Silver", "Platinum", "Palladium")
SERIES = {
    "Gold": "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
MIN_MONTH_COMMON_BUSINESS_DAYS = 15
# A source label is not evidence of a license/firstprint or benchmark equivalence.
ALLOWED_REPLAY_PROVIDER = ("LBMA", "seed")
MODEL_MONTHS_START, MODEL_MONTHS_END = "2010-01", "2026-09"

@dataclass(frozen=True)
class DailyRecord:
    day: str
    metal: str
    value: float
    provider_label: str | None
    payload_source_label: str | None
    provenance: str
    firstprint_proven: bool = False

def _month(day: str) -> str:
    return day[:7]

def _as_date(day: str) -> date:
    try:
        parsed = date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError(f"INVALID_DATE {day}") from exc
    if parsed.isoformat() != day:
        raise ValueError(f"INVALID_ISO_DATE {day}")
    return parsed

def _parse_record(row: dict) -> DailyRecord:
    metal = str(row["metal"])
    if metal not in METALS:
        raise ValueError(f"UNSUPPORTED_METAL {metal}")
    day = str(row["day"])
    _as_date(day)
    price = float(row["value"])
    if not math.isfinite(price) or price <= 0:
        raise ValueError(f"NONPOSITIVE_OR_NONFINITE_PRICE {metal} {day}")
    # The original archive is a 2026 research reconstruction; "LBMA" is a
    # *payload label* only and no original first-publication receipt exists.
    return DailyRecord(
        day=day, metal=metal, value=price,
        provider_label=row.get("provider_label"),
        payload_source_label=row.get("payload_source_label"),
        provenance=str(row.get("provenance") or "UNKNOWN_RESEARCH_ORIGIN"),
        firstprint_proven=bool(row.get("firstprint_proven", False)),
    )

def build_governed_panel(rows: list[dict]) -> dict:
    """Return immutable rows and per-month reasons: never silently fill gaps."""
    records = [_parse_record(row) for row in rows]
    if not records:
        raise RuntimeError("NO_METAL_ROWS")
    indices = {(r.day,r.metal) for r in records}
    if len(indices) != len(records):
        raise RuntimeError("DUPLICATE_DATE_METAL_IN_INPUT")
    by_day = defaultdict(dict)
    months = defaultdict(lambda: {"observed_days":set(), "weekend_days":set(),
                                  "missing_metal_days": [], "provider_labels":Counter(),
                                  "source_labels":Counter(), "all_rows":0})
    for r in records:
        by_day[r.day][r.metal] = r
        m = months[_month(r.day)]
        m["observed_days"].add(r.day)
        m["all_rows"] += 1
        m["provider_labels"][str(r.provider_label or "UNKNOWN")] += 1
        m["source_labels"][str(r.payload_source_label or "UNKNOWN")] += 1
        if _as_date(r.day).isoweekday()>5:
            m["weekend_days"].add(r.day)

    aligned = []
    month_aligned = Counter()
    for day, metals in sorted(by_day.items()):
        missing = sorted(set(METALS).difference(metals))
        if missing:
            months[_month(day)]["missing_metal_days"].append({
                "date":day,"missing_metals":missing
            })
            continue
        if _as_date(day).isoweekday()>5:
            continue
        # Keep the provenance as an immutable tuple for each metal in the row.
        aligned.append({
            "day":day,"month":_month(day),
            "prices":{m:metals[m].value for m in METALS},
            "sources":{m:{"provider":metals[m].provider_label,
                           "payload_source":metals[m].payload_source_label,
                           "firstprint_proven":metals[m].firstprint_proven,
                           "source":metals[m].provenance} for m in METALS},
        })
        month_aligned[_month(day)] += 1

    accepted=[]
    quarantined=[]
    all_months={}
    for m in sorted(months):
        x=months[m]
        reasons=[]
        provider_labels=sorted(x["provider_labels"])
        source_labels=sorted(x["source_labels"])
        common=month_aligned[m]
        if common<MIN_MONTH_COMMON_BUSINESS_DAYS:
            reasons.append("INSUFFICIENT_MATCHED_BUSINESS_DAYS")
        if x["weekend_days"]:
            reasons.append("WEEKEND_OBSERVATIONS_PRESENT")
        if (provider_labels != [ALLOWED_REPLAY_PROVIDER[0]]
                or source_labels != [ALLOWED_REPLAY_PROVIDER[1]]):
            reasons.append("MIXED_OR_UNVERIFIED_PROVIDER_PAYLOAD")
        eligible=not reasons
        # One holiday mismatch is lossless: exclude that single unpaired date,
        # never fill platinum/palladium via previous-close substitution.
        out={
            "month":m,
            "scope":"RESEARCH_REPLAY_NOT_ORIGINAL_FIRSTPRINT",
            "status":"RESEARCH_ELIGIBLE_NOT_LIVE_PIT" if eligible else "QUARANTINED_RESEARCH_ONLY",
            "matched_business_days":common,
            "raw_dates":len(x["observed_days"]),
            "raw_records":x["all_rows"],
            "weekend_dates":sorted(x["weekend_days"]),
            "missing_metal_days":x["missing_metal_days"],
            "provider_labels":dict(x["provider_labels"]),
            "source_labels":dict(x["source_labels"]),
            "reasons":reasons,
            "all_firstprints_verified":all(r.firstprint_proven for r in records
                                           if _month(r.day)==m),
        }
        all_months[m]=out
        (accepted if eligible else quarantined).append(m)
    clean=[r for r in aligned if r["month"] in accepted]
    # Report *absent entire calendar months* separately; never add synthetic
    # zero rows or mark a missing month as an observed/quarantined one.
    expected_months=[]
    y,mo=map(int,MODEL_MONTHS_START.split("-"))
    ey,em=map(int,MODEL_MONTHS_END.split("-"))
    while (y,mo)<=(ey,em):
        expected_months.append(f"{y:04d}-{mo:02d}")
        y,mo=(y+1,1) if mo==12 else (y,mo+1)
    missing_expected=[m for m in expected_months if m not in months]
    # The common-date 2010-2025 source replay is not equivalent to the
    # original GPR true-time vintage/official WB final monthly average.
    return {
        "schema":"GOLD_MONTHLY_FOUR_METAL_GOVERNED_PANEL_V1",
        "scope":"RESEARCH_ONLY_NO_PROSPECTIVE_FIRSTPRINT_CLAIM",
        "policy":{"min_common_business_days":MIN_MONTH_COMMON_BUSINESS_DAYS,
                  "required_provider_label":ALLOWED_REPLAY_PROVIDER[0],
                  "required_source_label":ALLOWED_REPLAY_PROVIDER[1],
                  "weekends_allowed":False,"imputation_allowed":False,
                  "forward_fill_allowed":False,
                  "live_pit_certified":False},
        "count_raw_records":len(records),
        "count_input_dates":len(by_day),
        "count_common_business_dates":len(aligned),
        "count_accepted_business_dates":len(clean),
        "accepted_months":accepted,"quarantined_months":quarantined,
        "expected_calendar_months":len(expected_months),
        "missing_expected_months":missing_expected,
        "month_audit":all_months,
        "clean_four_metal_rows":clean,
    }

def inspect_historical_gpr(vintage_months: list[str], start="2010-01",
                           last="2026-07") -> dict:
    """Enumerate which months have GPR vintage proof.

    Missing vintages DO NOT prohibit training on older OBSERVATION values
    included in a verified 2022+ vintage. They prohibit claims of a true
    monthly PIT replay at those older origins.
    """
    vintages=set(vintage_months)
    months=[]
    y,m=map(int,start.split("-")); ey,em=map(int,last.split("-"))
    while (y,m)<=(ey,em):
        months.append(f"{y:04d}-{m:02d}")
        y,m=(y+1,1) if m==12 else (y,m+1)
    missing=[m for m in months if m not in vintages]
    covered=[m for m in months if m in vintages]
    return {
        "model_origin_months":len(months),
        "covered_origin_vintages":len(covered),
        "unverified_origin_vintages":len(missing),
        "covered_first":min(covered) if covered else None,
        "missing_first":min(missing) if missing else None,
        "missing_last":max(missing) if missing else None,
        "older_historical_values_can_be_training_at_later_origin":True,
        "pre-vintage_original_PIT_certified":False,
    }

def load_neon_read_only(dsn: str) -> tuple[list[dict],list[str]]:
    """Opt-in source audit for all four metal rows. NEVER writes to Neon."""
    import psycopg
    rows=[]
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            cur.execute(
                "SELECT series_id,observation_ts::date,value,source,"
                "metadata->>'payload_provider_label',"
                "metadata->>'payload_source_label' FROM observations "
                "WHERE series_id=ANY(%s) AND observation_ts>='2010-01-01' "
                "AND observation_ts<'2026-10-01' ORDER BY observation_ts,series_id",
                (list(SERIES.values()),)
            )
            inverse={sid:metal for metal,sid in SERIES.items()}
            for sid,dt,value,source,provider,payload in cur:
                rows.append({
                    "day":dt.isoformat(),"metal":inverse[sid],
                    "value":float(value),"provider_label":provider,
                    "payload_source_label":payload,
                    "provenance":source,
                    "firstprint_proven":False,
                })
            cur.execute(
                "SELECT DISTINCT metadata->>'origin_month' FROM observations "
                "WHERE series_id='GPR_OFFICIAL_GIT_PIT' "
                "AND metadata ? 'origin_month'"
            )
            vintages=[x[0] for x in cur if x[0]]
    return rows,vintages

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dsn-env",default="NEON_DATABASE_URL")
    ap.add_argument("--input-json")
    ap.add_argument("--report",required=True)
    ap.add_argument("--panel-output")
    opts=ap.parse_args()
    if opts.input_json:
        doc=json.loads(Path(opts.input_json).read_text(encoding="utf-8"))
        rows=doc["rows"]
        vintages=doc["gpr_vintage_months"]
    else:
        import os
        dsn=os.environ.get(opts.dsn_env)
        if not dsn:
            raise RuntimeError("NEON_URL_REQUIRED_FOR_DATABASE_REPLAY_AUDIT")
        rows,vintages=load_neon_read_only(dsn)
    result=build_governed_panel(rows)
    result["gpr_vintage_coverage"]=inspect_historical_gpr(vintages)
    result["raw_input_sha256"]=hashlib.sha256(json.dumps(
        rows,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    clean=result.pop("clean_four_metal_rows")
    if opts.panel_output:
        Path(opts.panel_output).write_text(json.dumps({
            "schema":"GOLD_MONTHLY_CLEAN_RESEARCH_FOUR_METAL_DAILY_V1",
            "rows":clean,
            "firstprint_certified":False,
            "raw_input_sha256":result["raw_input_sha256"],
        },indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    Path(opts.report).write_text(json.dumps(result,indent=2,sort_keys=True,
        allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"gate":"RESEARCH_SOURCE_QUALITY_AUDIT_COMPLETE",
        "accepted_months":len(result["accepted_months"]),
        "quarantined_months":len(result["quarantined_months"]),
        "matched_business_days":result["count_accepted_business_dates"],
        "gpr_vintage_coverage":result["gpr_vintage_coverage"]},sort_keys=True))

if __name__=="__main__":main()
