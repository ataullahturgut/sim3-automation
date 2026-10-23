"""Verify governed source-date policy on immutable (already common-date) DEV snapshot.

The frozen snapshot strips unpaired observations, and does not retain each
original row's provider metadata. The per-date LBMA/seed labels are **verified
separately with read-only Neon source audit** for 2010-2024 and are solely a
reconstructed research provenance tag. This CI cannot detect the missing
2021-12-24 Pt/Pd independently; live Neon quality ledger records it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import gold_monthly_four_metal_governance_v1 as governance
import gold_monthly_dev_snapshot_v1 as snap

EXPECTED_PAYLOAD_SHA="2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb"

def inspect(path):
    bundle,meta=snap.load_snapshot(path)
    if meta["payload_sha256"]!=EXPECTED_PAYLOAD_SHA:
        raise RuntimeError("UNAUTHORIZED_DEV_SNAPSHOT")
    original=json.loads(Path(path).read_text(encoding="utf-8"))
    source=original["payload"]["daily_common_rows"]
    rows=[]
    for day in source:
        for metal in governance.METALS:
            rows.append({
                "day":day["date"],"metal":metal,"value":float(day[metal]),
                "provider_label":"LBMA","payload_source_label":"seed",
                "provenance":"FROZEN_DEV_COMMON_DATE_BUNDLE_RECONSTRUCTED_LBMA_LABELED",
                "firstprint_proven":False
            })
    panel=governance.build_governed_panel(rows)
    model_months=[m for m in panel["accepted_months"] if m<="2024-12"]
    if len(model_months)!=180 or len(panel["quarantined_months"])!=0:
        raise RuntimeError(f"DEV_SOURCE_2010_2024_MONTH_GATE_FAIL {len(model_months)}")
    if len(panel["clean_four_metal_rows"])!=len(source):
        raise RuntimeError("DEV_COMMON_SOURCE_ROWS_CHANGED")
    if any(v.get("all_firstprints_verified") for v in panel["month_audit"].values()):
        raise RuntimeError("ORIGINAL_FIRSTPRINT_MISCLAIM")
    gpr=governance.inspect_historical_gpr(sorted(bundle.gpr_vintages),
                                          last="2024-12")
    if gpr["covered_origin_vintages"]!=33:
        raise RuntimeError("DEV_GPR_VINTAGE_COVERAGE_CHANGED")
    # Snapshot was explicitly cut at end-2024: do NOT consider missing
    # 2025/26 prices a failure of immutable DEV research input completeness.
    result={
        "schema":"GOLD_MONTHLY_DEV_SOURCE_QUALITY_GATE_V1",
        "status":"PASS_DEV_HISTORICAL_REPLAY_RESEARCH_NOT_LIVE_PIT",
        "dev_snapshot_sha256":EXPECTED_PAYLOAD_SHA,
        "2010_2024_complete_four_metal_months":len(model_months),
        "source_rows_common_date":len(source),
        "per_month_count":{k:panel["month_audit"][k]["matched_business_days"]
                           for k in model_months},
        "GPR_dev_origin_vintage_count":gpr["covered_origin_vintages"],
        "limitation":"frozen snapshot already intersected four metals; 2021-12-24 Pt/Pd absence must be checked against raw Neon rows",
        "original_firstprint_certified":False,
        "2026_provider_mixing_audited_in":"GOLD_MONTHLY_FOUR_METAL_NEON_DATA_AUDIT_20261023.json",
        "no_neon_mutation":True,
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    result=inspect(args.snapshot)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("MONTHLY_2010_2024_RESEARCH_SOURCE_GATE=PASS")
    print(json.dumps({k:v for k,v in result.items() if k not in ("per_month_count","limitation")},sort_keys=True))
if __name__=="__main__":main()
