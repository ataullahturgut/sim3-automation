"""Idempotent, noncanonical Neon source staging from verified original-source files.

Only two isolated research tables are written; canonical source_registry,
observations, CORE5, GPR PIT vintages, and ChHHO forecasts are NEVER modified.
No automatic schema creation, upsert update, or mixing raw providers.
This loader requires an explicit --shadow-only opt-in and Neon DSN.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from collections import Counter
from datetime import date
from pathlib import Path

OLD_COMMIT="ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
NEW_COMMIT="02964d0324dde362099976c867f5077a369acaa5"
NEW_BLOB="ce0775767fad3d9d56431b5ca57c3e47a3c3a70b"
ALLOWED_METALS={"Gold","Silver","Platinum","Palladium"}
MODEL_SAFE=False

def build_daily(doc:dict):
    if doc.get("schema")!="GOLD_MONTHLY_STAK_FOUR_METAL_AUG_SEP_2026_SHADOW_V1":
        raise RuntimeError("UNEXPECTED_SHADOW_DAILY_SCHEMA")
    if doc.get("source_commit")!=NEW_COMMIT or doc.get("source_blob_sha")!=NEW_BLOB:
        raise RuntimeError("UNEXPECTED_STAK_SOURCE_VINTAGE")
    if doc.get("official_firstprint_certified") is not False or doc.get("neon_ingested") is not False:
        raise RuntimeError("STAGED_RECORD_CLAIMS_SOURCE_CERTIFICATION")
    rows=doc["records"]
    if len(rows)!=244:
        raise RuntimeError(f"FOUR_METAL_AUG_SEP_ROW_COUNT {len(rows)}")
    keys=set()
    counts=Counter()
    out=[]
    for x in rows:
        metal=x["metal"]
        day=date.fromisoformat(x["date"])
        ym=day.strftime("%Y-%m")
        if metal not in ALLOWED_METALS or ym not in ("2026-08","2026-09"):
            raise RuntimeError("OUT_OF_SCOPE_METAL_OR_MONTH")
        k=(x["date"],metal)
        if k in keys:raise RuntimeError("DUPLICATE_SHADOW_DAY_METAL")
        keys.add(k);counts[(ym,metal)]+=1
        price=float(x["price_usd_per_oz_source_native"])
        if not math.isfinite(price) or price<=0:raise RuntimeError("INVALID_SHADOW_PRICE")
        if x["source_type"]!="sqld" or x["provider"] is not None:
            raise RuntimeError("ORIGINAL_PAYLOAD_PROVIDER_DIFFERENT")
        if x["source_repo"]!="lbruton/StakTrakr" or x["upstream_commit"]!=NEW_COMMIT:
            raise RuntimeError("INVALID_SOURCE_COMMIT")
        if x["upstream_git_blob"]!=NEW_BLOB:raise RuntimeError("INVALID_UPSTREAM_GIT_BLOB")
        if x["provider_original_firstprint_verified"] is not False:
            raise RuntimeError("FALSE_FIRSTPRINT_CLAIM")
        if x["is_weekend"]!=(day.isoweekday()>5):
            raise RuntimeError("WEEKEND_FLAG_MISMATCH")
        out.append(("lbruton/StakTrakr","data/spot-history-2026.json",
                    NEW_COMMIT,NEW_BLOB,day,metal,price,x["original_timestamp"],
                    x["source_type"],x["provider"],x["is_weekend"],False))
    for ym,ndays in (("2026-08",31),("2026-09",30)):
        for metal in ALLOWED_METALS:
            if counts[(ym,metal)]!=ndays:
                raise RuntimeError(f"MONTH_METAL_COVERAGE {ym} {metal}")
    return out

def build_monthly(doc:dict):
    if doc.get("schema")!="GOLD_MONTHLY_OFFICIAL_GPR_WB_EXTRACT_20261023_V1":
        raise RuntimeError("UNEXPECTED_OFFICIAL_SOURCE_SCHEMA")
    out=[]
    for vint,rec in sorted(doc["gpr"].items()):
        if vint not in ("2026-09","2026-10"):
            raise RuntimeError("UNKNOWN_GPR_VINTAGE")
        published=rec["release_utc"]
        if published[:7]!=vint:raise RuntimeError("BAD_GPR_RELEASE_MONTH")
        for ym,metrics in rec["series_values"].items():
            if ym not in ("2026-07","2026-08","2026-09"):
                raise RuntimeError("OUT_OF_SCOPE_GPR_OBSERVATION")
            for metric,value in metrics.items():
                if metric not in ("GPR","GPRT","GPRA") or not math.isfinite(float(value)) or float(value)<0:
                    raise RuntimeError("INVALID_OFFICIAL_GPR_METRIC")
                out.append(("GPR_OFFICIAL_GIT",vint,
                    "iacoviel/iacoviel.github.io/"+rec["original_git_path"],
                    rec["blob"],metric,date.fromisoformat(ym+"-01"),float(value),
                    "index",published,date.fromisoformat(published[:10]),
                    json.dumps({"commit":rec["commit"],
                                "archive_vintage":vint,
                                "firstprint_system_captured":False})))
    gold=doc["world_bank"]
    if gold["published_date_note"]!="Updated on October 02, 2026":
        raise RuntimeError("UNEXPECTED_WB_OFFICIAL_RELEASE")
    if gold["unit"]!="($/troy oz)":
        raise RuntimeError("WB_GOLD_UNIT_CHANGED")
    for ym,value in gold["gold_monthly_values_usd_oz"].items():
        if ym not in ("2026-07","2026-08","2026-09"):
            raise RuntimeError("OUT_OF_SCOPE_WB_MONTH")
        if not math.isfinite(float(value)) or float(value)<=0:
            raise RuntimeError("INVALID_WB_PRICE")
        out.append(("WORLD_BANK_PINK_SHEET","2026-10-02_OCT_PINK_SHEET",
            "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx",
            "ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154",
            "GOLD_MONTHLY_USD_OZ",date.fromisoformat(ym+"-01"),
            float(value),"USD/troy_oz",None,date(2026,10,2),
            json.dumps({"sheet":"Monthly Prices","gold_column":70,"firstprint_system_captured":False})))
    if len(out)!=18:
        raise RuntimeError(f"OFFICIAL_VALUES_COUNT_WRONG {len(out)}")
    return out

def stage(daily:list,monthly:list,dsn:str):
    import psycopg
    daily_sql="""
    INSERT INTO gold_monthly_h1.original_source_shadow_daily_v1
    (source_repository,source_path,source_commit,source_git_blob,observation_day,metal,
    spot_value_source_native,observed_timestamp_text,payload_source_label,
    payload_provider_label,is_weekend,firstprint_verified)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (source_commit,observation_day,metal) DO NOTHING
    """
    monthly_sql="""
    INSERT INTO gold_monthly_h1.original_source_shadow_monthly_v1
    (source_family,source_version,source_repository_or_url,source_revision_hash,
    series_name,observation_month,series_value,unit,verified_git_commit_at,
    declared_release_day,provenance_metadata)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
    ON CONFLICT (source_family,source_version,series_name,observation_month) DO NOTHING
    """
    with psycopg.connect(dsn) as db:
        with db.cursor() as c:
            for record in daily:c.execute(daily_sql,record)
            for record in monthly:c.execute(monthly_sql,record)
            c.execute("SELECT COUNT(*) FROM gold_monthly_h1.original_source_shadow_daily_v1 WHERE source_commit=%s",(NEW_COMMIT,))
            if c.fetchone()[0]!=244:raise RuntimeError("STAGING_DAILY_DB_COUNT_MISMATCH")
            c.execute("SELECT COUNT(*) FROM gold_monthly_h1.original_source_shadow_monthly_v1 WHERE source_family IN ('GPR_OFFICIAL_GIT','WORLD_BANK_PINK_SHEET')")
            if c.fetchone()[0]<18:raise RuntimeError("STAGING_MONTHLY_DB_COUNT_MISMATCH")
        db.commit()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stak-shadow-json",required=True)
    p.add_argument("--official-monthly-json",required=True)
    p.add_argument("--shadow-only",action="store_true")
    a=p.parse_args()
    daily=build_daily(json.loads(Path(a.stak_shadow_json).read_text(encoding="utf-8")))
    monthly=build_monthly(json.loads(Path(a.official_monthly_json).read_text(encoding="utf-8")))
    print(json.dumps({"validated_daily":len(daily),"validated_official_monthly":len(monthly),
                      "only_research_shadow":True,"original_firstprint_verified":False}))
    if not a.shadow_only:return
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:raise RuntimeError("NEON_DATABASE_URL_REQUIRED_FOR_EXPLICIT_SHADOW_IMPORT")
    stage(daily,monthly,dsn)
    print("MONTHLY_SHADOW_IMPORT_COMMITTED_VERIFIED")
if __name__=="__main__":
    main()
