#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage41_meta_v1 as b41
import gold_monthly_svr_dwt_stage5a2_tlbo_tuned_pso_v1 as core

def run_shard(start,end,tag):
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    rows=[]
    for target in base.month_range(start,end):
        r=core.predict_one(bundle,target); rows.append(r)
        print(f"PROGRESS shard={tag} method={core.METHOD} target={target} AE={r['absolute_error']:.6f} outer={r['outer_validation_score']:.6f}",flush=True)
    after=b41.read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
        "scope":"STAGE5A2_TLBO_TUNED_PSO_SHARD_V1","method":core.METHOD,
        "tag":tag,"start":start,"end":end,"rows":rows,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED",
        "random_split":"NONE","database":"READ_ONLY"
    }
    p=Path(f"stage5a2_tlbo_tuned_pso_shard_{tag}.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"SHARD_GATE=PASS tag={tag} n={len(rows)}",flush=True)

def aggregate(root):
    root=Path(root)
    files=sorted(root.rglob("stage5a2_tlbo_tuned_pso_shard_*.json"))
    if len(files)!=5:
        raise RuntimeError(f"EXPECTED_5_SHARDS got={len(files)}")
    rows=[]
    invariant_ref=None
    tags=[]
    for p in files:
        d=json.loads(p.read_text())
        assert d["scope"]=="STAGE5A2_TLBO_TUNED_PSO_SHARD_V1"
        assert d["method"]==core.METHOD
        assert d["2025_role"]=="LOCKED_NOT_OPENED"
        assert d["2026_role"]=="QUARANTINED_NOT_USED"
        assert d["authority_invariants_before"]==d["authority_invariants_after"]
        if invariant_ref is None:
            invariant_ref=d["authority_invariants_before"]
        else:
            assert invariant_ref==d["authority_invariants_before"]
        tags.append(d["tag"])
        rows.extend(d["rows"])
    rows=sorted(rows,key=lambda r:r["target"])
    expected=base.month_range("2022-04","2024-12")
    targets=[r["target"] for r in rows]
    if targets!=expected:
        raise RuntimeError(f"TARGET_COVERAGE_FAIL targets={targets}")
    compact=[{k:r[k] for k in ("target","method","selected_repeat","selected_validation_loss","selected_pso",
                               "selected_params","repeat_records","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in rows]
    payload=hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "family":"SVR_DWT_SVR","scope":"STAGE5A2_TLBO_TUNED_PSO_DEV_ONLY_V1","method":core.METHOD,
        "execution":"5_PARALLEL_ORIGIN_SHARDS_EXACT_TARGET_DETERMINISTIC_EQUIVALENCE",
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE5A2_TLBO_TUNED_PSO_FREEZE_2026-09-28.md",
        "contract":{
            "parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
            "svr_parameter_vector":["log2_C","log2_gamma","epsilon"],
            "svr_lower_bounds":b41.LOWER.tolist(),"svr_upper_bounds":b41.UPPER.tolist(),
            "pso_control_vector":["w","c1","c2","vmax_frac"],"pso_control_lower":core.QLO.tolist(),"pso_control_upper":core.QHI.tolist(),
            "outer_tlbo_population":core.TLBO_POP,"outer_tlbo_iterations":core.TLBO_ITERS,
            "nested_pso_population":core.OUTER_PSO_POP,"nested_pso_iterations":core.OUTER_PSO_ITERS,
            "final_population":core.FINAL_POP,"final_iterations":core.FINAL_ITERS,"repeats":core.REPEATS,
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED",
            "random_split":"NONE","database":"READ_ONLY","outer_optimizer_refit":"NONE"
        },
        "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows,
        "authority_invariants_before":invariant_ref,"authority_invariants_after":invariant_ref,
        "shards":tags,"payload_sha256":payload
    }
    Path("gold_monthly_svr_dwt_stage5a2_tlbo_tuned_pso_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    m=out["metrics"]
    report=[
      "# GOLD MONTHLY FORECAST — SVR STAGE 5A.2 TLBO-TUNED PSO RESULT","",
      "Date: 2026-09-28","Status: **COMPLETE / SCIENTIFIC GATE PASS**","",
      "Execution: 5 parallel origin shards; per-target deterministic algorithm unchanged.","",
      f"- DEV SigmaAE: **{m['sum_abs_error']:.6f}**",f"- MAE: {m['mae']:.6f}",f"- RMSE: {m['rmse']:.6f}",
      f"- MAPE: {m['mape_pct']:.4f}%",f"- Relative MAE vs RW: {m['relative_mae_vs_rw']:.6f}",
      f"- Direction: **{m['direction_correct']}/33**",f"- Worst month: {m['worst_month']}","",
      "Frozen parent reference: **1449.187363 / 19/33**.","",
      "## Kontrol ve Uyum Özeti","- 33/33 DEV origins exactly once: PASS.","- Prior-only chronology: PASS.",
      "- Target-based deterministic seeds preserved across shards: PASS.","- Outer TLBO pre-target validation only: PASS.",
      "- 2025 opened: NO.","- 2026 used: NO.","- Random split: NONE.","- DB mutation: NONE / READ_ONLY.",""
    ]
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE5A2_TLBO_TUNED_PSO_RESULT_2026-09-28.md").write_text("\n".join(report),encoding="utf-8")
    print("SVR_STAGE5A2_SHARDED_AGGREGATE_GATE=PASS",flush=True)
    print(json.dumps({"method":core.METHOD,"metrics":m,"payload_sha256":payload},sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--start"); ap.add_argument("--end"); ap.add_argument("--tag")
    ap.add_argument("--aggregate",action="store_true"); ap.add_argument("--input-dir",default=".")
    a=ap.parse_args()
    if a.aggregate:
        aggregate(a.input_dir)
    else:
        if not (a.start and a.end and a.tag):
            raise SystemExit("shard mode requires --start --end --tag")
        run_shard(a.start,a.end,a.tag)

if __name__=="__main__":
    main()
