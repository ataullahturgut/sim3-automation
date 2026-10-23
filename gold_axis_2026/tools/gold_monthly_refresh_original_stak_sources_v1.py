"""Compare and stage immutable same-origin StakTrakr daily metal price vintages.

Inputs are actual historical source files downloaded from public GitHub repo
lbruton/StakTrakr, NOT prices manufactured in our database. Original and latest
commits stay immutable; historical revisions MUST NOT silently overwrite existing
observations or relabel unverified sqld rows as LBMA firstprints.
"""
from __future__ import annotations
import argparse, calendar, hashlib, json, math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

UPSTREAM_REPO="lbruton/StakTrakr"
UPSTREAM_PATH="data/spot-history-2026.json"
OLD_COMMIT="ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
NEW_COMMIT="02964d0324dde362099976c867f5077a369acaa5"
OLD_BLOB="64e025fb943b31b7bc8b89c6cf521db4210f560b"
NEW_BLOB="ce0775767fad3d9d56431b5ca57c3e47a3c3a70b"
METALS=("Gold","Silver","Platinum","Palladium")
STAGE_MONTHS=("2026-08","2026-09")

def git_blob_hash(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def read_snapshot(path:str,expected_blob:str)->tuple[list[dict],str]:
    raw=Path(path).read_bytes()
    sha=git_blob_hash(raw)
    if sha!=expected_blob:
        raise RuntimeError(f"UPSTREAM_GIT_BLOB_MISMATCH expected={expected_blob} actual={sha}")
    parsed=json.loads(raw)
    if not isinstance(parsed,list):
        raise RuntimeError("NOT_ARRAY_OF_SPOT_HISTORY")
    result=[]
    seen=set()
    for x in parsed:
        if x.get("metal") not in (*METALS,"Copper"):raise RuntimeError("UNKNOWN_METAL")
        d=x.get("timestamp","")[:10]
        dt=date.fromisoformat(d)
        if dt.isoformat()!=d:raise RuntimeError("INVALID_DATE")
        price=float(x.get("spot",float("nan")))
        if not math.isfinite(price) or price<=0:raise RuntimeError(f"BAD_PRICE {x}")
        key=(x["metal"],d)
        if key in seen:raise RuntimeError(f"DUPLICATE_SPOT {key}")
        seen.add(key)
        result.append({
            "metal":x["metal"],"date":d,"price_usd_per_oz_source_native":price,
            "source_type":x.get("source"),"provider":x.get("provider"),
            "original_timestamp":x["timestamp"],
        })
    return result,sha

def compare(old:list[dict],new:list[dict],old_sha:str,new_sha:str):
    a={(x["metal"],x["date"]):x for x in old}
    b={(x["metal"],x["date"]):x for x in new}
    changed=[]
    for key,x in a.items():
        y=b.get(key)
        if y and (x["price_usd_per_oz_source_native"]!=y["price_usd_per_oz_source_native"]
                  or x["source_type"]!=y["source_type"] or x["provider"]!=y["provider"]):
            changed.append({"date":key[1],"metal":key[0],
                "old_price":x["price_usd_per_oz_source_native"],
                "new_price":y["price_usd_per_oz_source_native"],
                "old_provider":x["provider"],"new_provider":y["provider"]})
    deletions=[x for key,x in a.items() if key not in b]
    additions=[x for key,x in b.items() if key not in a]
    if deletions:raise RuntimeError(f"HISTORICAL_UPSTREAM_RECORDS_REMOVED count={len(deletions)}")
    by_month={}
    for m in STAGE_MONTHS:
        stage=[x for x in new if x["date"][:7]==m and x["metal"] in METALS]
        calendar_days=calendar.monthrange(int(m[:4]),int(m[5:]))[1]
        # Full daily availability (incl. weekend records) is a *source*
        # completeness fact, NOT a benchmark/fixing uniformity certificate.
        days=sorted(set(x["date"] for x in stage))
        expected=[f"{m}-{d:02d}" for d in range(1,calendar_days+1)]
        if days!=expected:
            raise RuntimeError(f"INCOMPLETE_STAK_UPSTREAM_{m} actual={len(days)}")
        counts={metal:sum(x["metal"]==metal for x in stage) for metal in METALS}
        if any(n!=calendar_days for n in counts.values()):
            raise RuntimeError(f"INCOMPLETE_FOUR_METAL_COVERAGE_{m} {counts}")
        provider=set(x["provider"] for x in stage)
        types=set(x["source_type"] for x in stage)
        if types!={"sqld"} or provider!={None}:
            raise RuntimeError(f"UPSTREAM_PROVIDER_CONTRACT_CHANGED_{m} providers={provider} types={types}")
        business_days=sum(date.fromisoformat(d).isoweekday()<=5 for d in days)
        by_month[m]={"days":len(days),"business_days":business_days,
            "weekend_days":len(days)-business_days,
            "rows_by_metal":counts,"upstream_payload_source":"sqld",
            "upstream_provider_id":"MISSING","real_market_fixing_certified":False}
    new_rows=[x for x in new if x["date"][:7] in STAGE_MONTHS and x["metal"] in METALS]
    staged=[]
    for x in sorted(new_rows,key=lambda v:(v["date"],v["metal"])):
        staged.append({**x,
            "source_repo":UPSTREAM_REPO,"source_path":UPSTREAM_PATH,
            "upstream_commit":NEW_COMMIT,"upstream_git_blob":new_sha,
            "ingestion_role":"SHADOW_ONLY_NO_CANONICAL_OVERWRITE",
            "provider_original_firstprint_verified":False,
            "date_only_not_real_published_timestamp":True,
            "is_weekend":date.fromisoformat(x["date"]).isoweekday()>5,
            "eligible_for_original_lbma_homogeneous_model":False})
    revisions_month=Counter(x["date"][:7] for x in changed)
    report={
        "schema":"GOLD_MONTHLY_STAK_ORIGINAL_SOURCE_REFRESH_AUDIT_20261023_V1",
        "scope":"RESEARCH_SOURCE_STAGING_NOT_OFFICIAL_FOUR_METAL_FIRSTPRINT",
        "upstream_repo":UPSTREAM_REPO,"upstream_path":UPSTREAM_PATH,
        "old_commit":OLD_COMMIT,"old_blob_verified":old_sha,
        "new_commit":NEW_COMMIT,"new_blob_verified":new_sha,
        "original_rows":len(old),"latest_rows":len(new),
        "added_records_all_metals":len(additions),
        "changed_overlap_records_all_metals":len(changed),
        "changed_overlap_by_month":dict(sorted(revisions_month.items())),
        "removed_overlap_records":len(deletions),
        "stage_months":by_month,
        "stage_row_count":len(staged),
        "revision_samples":changed[:16],
        "original_firstprint_verified":False,
        "upstream_missing_provider_label":True,
        "old_database_rows_safe_unchanged":True,
        "weekends_not_automatically_considered_valid_fixings":True,
        "gold_monthly_model_auto_promoted":False,
        "neon_database_written":False,
    }
    return report,staged

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--old-json",required=True);p.add_argument("--new-json",required=True)
    p.add_argument("--report",required=True);p.add_argument("--stage",required=True)
    args=p.parse_args()
    old,osh=read_snapshot(args.old_json,OLD_BLOB)
    new,nsh=read_snapshot(args.new_json,NEW_BLOB)
    report,stage=compare(old,new,osh,nsh)
    Path(args.report).write_text(json.dumps(report,indent=2,sort_keys=True)+chr(10))
    Path(args.stage).write_text(json.dumps({
        "schema":"GOLD_MONTHLY_STAK_FOUR_METAL_AUG_SEP_2026_SHADOW_V1",
        "source_repo":UPSTREAM_REPO,"source_commit":NEW_COMMIT,
        "source_blob_sha":nsh,"records":stage,
        "official_firstprint_certified":False,
        "eligible_for_canonical_LBMA_fixer":False,
        "neon_ingested":False,
    },indent=2,sort_keys=True)+chr(10))
    print("SAME_UPSTREAM_SOURCE_STAGING_GATE=PASS")
    print(json.dumps({k:v for k,v in report.items()
                       if k in ("old_commit","new_commit","stage_months",
                                "stage_row_count","changed_overlap_records_all_metals",
                                "added_records_all_metals","removed_overlap_records")},sort_keys=True))
if __name__=="__main__":main()
