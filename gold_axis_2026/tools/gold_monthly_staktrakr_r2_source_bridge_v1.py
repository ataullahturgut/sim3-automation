"""Pinned StakTrakr R1 -> R2 four-metal historical research source bridge.

No price insertion, forward-fill or provider equivalence claim. Reads two
immutable GitHub blob-verified 2026 source files. Builds recovery candidate
for Aug/Sep 2026 and a ledger of ALL retrospective revision conflicts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

METALS=("Gold","Silver","Platinum","Palladium")
OLD_BLOB="64e025fb943b31b7bc8b89c6cf521db4210f560b"
NEW_BLOB="ce0775767fad3d9d56431b5ca57c3e47a3c3a70b"
OLD_REF="ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
NEW_REF="709f31117ec0b748a6d0478bb652e086cd44e609"

def load(blob: bytes, expected_blob_sha: str) -> dict:
    computed=hashlib.sha1(f"blob {len(blob)}\0".encode()+blob).hexdigest()
    if computed != expected_blob_sha:
        raise RuntimeError(f"PINNED_SOURCE_BLOB_MISMATCH expected={expected_blob_sha} got={computed}")
    raw=json.loads(blob)
    if not isinstance(raw,list):
        raise RuntimeError("SOURCE_SCHEMA_NOT_LIST")
    panel={}
    for row in raw:
        metal=row.get("metal")
        if metal not in METALS:
            continue
        day=str(row.get("timestamp",""))[:10]
        if date.fromisoformat(day).isoformat()!=day:
            raise RuntimeError(f"BAD_DAY {day}")
        key=(day,metal)
        if key in panel:
            raise RuntimeError(f"DUPLICATE_METAL_DAY {key}")
        value=float(row["spot"])
        if not (math.isfinite(value) and value>0):
            raise RuntimeError(f"INVALID_PRICE {key}")
        panel[key]={
            "price":value,
            "source":row.get("source"),
            "provider":row.get("provider"),
            "source_timestamp":row.get("timestamp"),
        }
    return panel

def summarize(old: dict,new: dict) -> dict:
    keys_old=set(old)
    keys_new=set(new)
    deleted=sorted(keys_old-keys_new)
    added=sorted(keys_new-keys_old)
    changed=[
        {"date":d,"metal":m,"old_price":old[(d,m)]["price"],
         "new_price":new[(d,m)]["price"],
         "delta":new[(d,m)]["price"]-old[(d,m)]["price"]}
        for d,m in sorted(keys_old & keys_new)
        if old[(d,m)]["price"]!=new[(d,m)]["price"]
    ]
    same=len(keys_old&keys_new)-len(changed)
    if deleted:
        raise RuntimeError(f"OLDER_SOURCE_OBSERVATIONS_REMOVED {len(deleted)}")
    months={}
    for m in ("2026-08","2026-09"):
        days=sorted({d for d,_ in new if d.startswith(m)})
        paired=[d for d in days if all((d,metal) in new for metal in METALS)]
        weekdays=[d for d in paired if date.fromisoformat(d).isoweekday()<=5]
        weekends=[d for d in paired if date.fromisoformat(d).isoweekday()>5]
        provenance=Counter(str(new[(d,metal)]["source"] or "UNKNOWN")+"/"+str(new[(d,metal)]["provider"] or "UNKNOWN") for d in paired for metal in METALS)
        if len(weekdays)<20:
            raise RuntimeError(f"MONTH_UNDER_20_MATCHED_BUSINESS_DAYS {m}={len(weekdays)}")
        if len(paired)!=len(days):
            raise RuntimeError(f"FOUR_METAL_DATE_MISMATCH {m}")
        months[m]={
            "calendar_dates":len(days),
            "complete_four_metal_dates":len(paired),
            "complete_weekdays":len(weekdays),
            "weekend_dates":len(weekends),
            "first_observation_date":days[0],
            "last_observation_date":days[-1],
            "all_metals":list(METALS),
            "source_provider_labels":dict(provenance),
            "source_firstprint_verified":False,
            "research_sufficient_20_business_days":True,
            "eligible_for_automatic_canonical_overwrite":False,
            "reason":"spot-history daily noon seed/sqld research values are not certified LBMA single-fixing firstprint; historical revisions",
        }
    summary={
        "schema":"GOLD_MONTHLY_STAKTRAKR_R1_R2_BRIDGE_V1",
        "status":"FOUR_METALS_FOUND_AUG_SEP_PROVISIONAL_RESEARCH_NOT_AUTOMATIC_MODEL_INPUT",
        "repo":"lbruton/StakTrakr",
        "source_path":"data/spot-history-2026.json",
        "original_reference":{"commit":OLD_REF,"blob_sha1":OLD_BLOB},
        "new_reference":{"commit":NEW_REF,"blob_sha1":NEW_BLOB},
        "input_old_four_metal_rows":len(old),
        "input_new_four_metal_rows":len(new),
        "old_new_exact_common_rows":same,
        "old_new_revised_common_rows":len(changed),
        "old_new_new_rows":len(added),
        "old_new_deleted_rows":len(deleted),
        "revisions_by_month":dict(sorted(Counter(r["date"][:7] for r in changed).items())),
        "added_by_month":dict(sorted(Counter(d[:7] for d,_ in added).items())),
        "august_september":months,
        "top_revisions_by_absolute_usd":sorted(changed,key=lambda r:abs(r["delta"]),reverse=True)[:12],
        "result_guard":{
            "no_source_splice_into_R1":True,
            "new_source_version_id_required":True,
            "historical_raw_price_changes_recorded":True,
            "live_original_firstprint_proven":False,
            "real_time_asof_approved":False,
            "auto_model_promotion":False,
            "no_database_mutation":True,
            "2026_aug_sep_source_records_recovered":True,
        },
    }
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old",required=True)
    ap.add_argument("--new",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    out=summarize(load(Path(a.old).read_bytes(),OLD_BLOB),load(Path(a.new).read_bytes(),NEW_BLOB))
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("STAK_R2_AUG_SEP_SOURCE_RECOVERY_GATE=PASS")
    print(json.dumps({k:v for k,v in out.items() if k in (
        "status","old_new_exact_common_rows","old_new_revised_common_rows",
        "old_new_new_rows","old_new_deleted_rows","revisions_by_month","added_by_month",
        "august_september")},sort_keys=True))
if __name__=="__main__":
    main()
