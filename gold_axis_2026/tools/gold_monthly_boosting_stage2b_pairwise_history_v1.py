from __future__ import annotations
import json, os
from pathlib import Path
import psycopg
import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage1_canonical_v1 as s1
import gold_monthly_boosting_stage2_feature_representation_v1 as s2

DEV_START, DEV_END = "2022-04", "2024-12"
START_BY_REP = {
    "RAW_LEVEL_LAGS8":"2010-03",
    "DAILY_SUMMARY12":"2010-03",
    "SIMPLE_RETURNS8":"2010-05",
    "MIXED20":"2010-05",
}

def invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in targets}
    comparisons=[]
    promoted={}
    controls={}

    for name in s1.PARAMS:
        controls[name]={}
        for start in sorted(set(START_BY_REP.values())):
            s2.COMMON_TRAIN_START=start
            controls[name][start]=s2.evaluate(b,cache,name,"CURRENT8")
        promoted[name]=[]
        for rep,start in START_BY_REP.items():
            s2.COMMON_TRAIN_START=start
            cand=s2.evaluate(b,cache,name,rep)
            ctrl=controls[name][start]
            cm=cand["metrics"]; bm=ctrl["metrics"]
            row={
                "model":name,"representation":rep,"pairwise_train_start":start,
                "candidate_sum_abs_error":cm["sum_abs_error"],
                "current8_control_sum_abs_error":bm["sum_abs_error"],
                "delta_sum_abs_error_candidate_minus_current8":cm["sum_abs_error"]-bm["sum_abs_error"],
                "candidate_direction_correct":cm["direction_correct"],
                "current8_direction_correct":bm["direction_correct"],
                "delta_direction_correct":cm["direction_correct"]-bm["direction_correct"],
                "candidate_metrics":cm,"current8_control_metrics":bm
            }
            comparisons.append(row); promoted[name].append(row)

    for name in promoted:
        promoted[name].sort(key=lambda z:(z["delta_sum_abs_error_candidate_minus_current8"],-z["delta_direction_correct"],z["representation"]))

    after=invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "scope":"BOOSTING_STAGE2B_PAIRWISE_HISTORY_CONTROL_V1",
        "purpose":"Separate feature-representation effect from unequal historical-start effect.",
        "dev":f"{DEV_START}..{DEV_END}",
        "2025_2026":"NOT_OPENED_NOT_EVALUATED",
        "random_split":"NONE","database":"READ_ONLY",
        "start_by_representation":START_BY_REP,
        "comparisons":comparisons,
        "best_pairwise_feature_change_by_model":{k:v[0] for k,v in promoted.items()},
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after
    }
    Path("gold_monthly_boosting_stage2b_pairwise_history_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"best_pairwise":out["best_pairwise_feature_change_by_model"],
                      "authority_invariants_unchanged":after==b.invariants_before},sort_keys=True))

if __name__=="__main__":
    main()
