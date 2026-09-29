from __future__ import annotations
import argparse,json
from pathlib import Path

import gold_monthly_direct_external_store_v1 as direct
import gold_monthly_f4_fx_rates_raw_data_authority_audit_v1 as audit

def nested_date_first(d,bucket,key):
    return {dt:float(z[key]) for dt,z in d[bucket].items() if isinstance(z,dict) and key in z and z[key] is not None}

def current_date_first(d,key):
    return {dt:float(z[key]) for dt,z in d.items() if isinstance(z,dict) and key in z and z[key] is not None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    ext=json.loads(Path(a.external_v2).read_text())

    h15,h15meta=direct.fetch_h15()
    h10,h10meta=direct.fetch_fx()

    ext_s={
      "BROADUSD":nested_date_first(ext,"h10_daily","BROAD_USD_INDEX"),
      "NOM10":nested_date_first(ext,"h15_daily","DGS10"),
      "REAL10":nested_date_first(ext,"h15_daily","DFII10"),
    }
    cur_s={
      "BROADUSD":current_date_first(h10,"BROAD_USD_INDEX"),
      "NOM10":current_date_first(h15,"DGS10"),
      "REAL10":current_date_first(h15,"DFII10"),
    }

    cmp={k:audit.compare_series(k,ext_s[k],cur_s[k]) for k in ext_s}
    parity=audit.transform_parity(ext_s,cur_s)

    hash_checks={
      "h15_sha256_equal":str(ext.get("h15_meta",{}).get("sha256"))==str(h15meta.get("sha256")),
      "h10_rates_sha256_equal":str(ext.get("h10_meta",{}).get("rates_sha256"))==str(h10meta.get("rates_sha256")),
      "h10_index_sha256_equal":str(ext.get("h10_meta",{}).get("index_sha256"))==str(h10meta.get("index_sha256")),
    }

    daily_values_pass=all(v["value_mismatch_gt_1e-10_n"]==0 for v in cmp.values())
    coverage_pass=all(v["ext_only_n"]==0 and v["official_only_n"]==0 for v in cmp.values())
    transform_pass=all([
      parity["fx_max_mr1_abs_diff"]<=1e-12,
      parity["fx_max_rms_vol_abs_diff"]<=1e-12,
      parity["nom10_diff_max_abs_diff"]<=1e-12,
      parity["real10_diff_max_abs_diff"]<=1e-12,
      parity["breakeven_diff_max_abs_diff"]<=1e-12,
    ])

    out={
      "schema":"GOLD_MONTHLY_F4_FX_RATES_DIRECT_BOARD_DDP_REAUDIT_V1_2026-09-29",
      "external_v2_payload_sha256":ext.get("payload_sha256"),
      "source":"Federal Reserve Board Data Download Program direct re-fetch",
      "frozen_meta":{"h10":ext.get("h10_meta"),"h15":ext.get("h15_meta")},
      "current_meta":{"h10":h10meta,"h15":h15meta},
      "raw_package_hash_checks":hash_checks,
      "series_comparison":cmp,
      "dev_transform_recalculation":parity,
      "gates":{
        "raw_package_hashes_all_equal":all(hash_checks.values()),
        "daily_values_pass":daily_values_pass,
        "coverage_pass":coverage_pass,
        "dev_transform_pass":transform_pass,
        "pass":daily_values_pass and coverage_pass and transform_pass,
      }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_DIRECT_DDP_REAUDIT_GATE="+("PASS" if out["gates"]["pass"] else "FAIL"))
    print(json.dumps({
      "gates":out["gates"],
      "raw_package_hash_checks":hash_checks,
      "series":{k:{
        "ext_n":v["ext_n"],"official_window_n":v["official_window_n"],"common_n":v["common_n"],
        "ext_only_n":v["ext_only_n"],"official_only_n":v["official_only_n"],
        "max_abs_value_diff":v["max_abs_value_diff"],"value_mismatch_gt_1e-10_n":v["value_mismatch_gt_1e-10_n"],
      } for k,v in cmp.items()},
      "transform_max_diffs":{k:v for k,v in parity.items() if k.endswith("abs_diff")},
    },sort_keys=True))

if __name__=="__main__": main()
