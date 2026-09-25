from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    rows=[]
    for t in base.month_range("2023-01","2026-07"):
        if t not in b.monthly_metal["Gold"] or t not in b.core_gold: continue
        p=base.month_shift(t,-1)
        if p not in b.monthly_metal["Gold"] or p not in b.core_gold: continue
        st=float(b.monthly_metal["Gold"][t]); core=float(b.core_gold[t])
        stp=float(b.monthly_metal["Gold"][p]); corep=float(b.core_gold[p])
        rs=math.log(st/stp); rc=math.log(core/corep)
        rows.append({
            "month":t,
            "stak_gold":st,
            "core5_gold":core,
            "level_diff_usd":st-core,
            "level_diff_pct":100*(st-core)/core,
            "stak_logret":rs,
            "core5_logret":rc,
            "return_diff_pp":100*(rs-rc),
            "return_sign_same":int(np.sign(rs)==np.sign(rc)),
        })
    def summ(a,z):
        q=[r for r in rows if a<=r["month"]<=z]
        return {
            "n":len(q),
            "mean_abs_level_diff_pct":float(np.mean([abs(r["level_diff_pct"]) for r in q])),
            "max_abs_level_diff_pct":float(np.max([abs(r["level_diff_pct"]) for r in q])),
            "mean_abs_return_diff_pp":float(np.mean([abs(r["return_diff_pp"]) for r in q])),
            "return_sign_agreement_pct":100*float(np.mean([r["return_sign_same"] for r in q])),
        }
    out={"model_id":"VW_MIDAS_TARGET_ANCHOR_BRIDGE_AUDIT_V1","database_access":"READ_ONLY",
         "definition":{"training_gold_target":"monthly_metal Gold / StakTrakr R1",
                       "price_level_anchor_and_score":"CORE5_GOLD_USD_OZ_RESEARCH_R1"},
         "summary":{"2023":summ("2023-01","2023-12"),"2024":summ("2024-01","2024-12"),
                    "2025":summ("2025-01","2025-12"),"2026":summ("2026-01","2026-07")},
         "rows":rows}
    Path("vw_midas_target_anchor_bridge_audit_v1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out["summary"],sort_keys=True))
    print("2026_ROWS="+json.dumps([r for r in rows if r["month"].startswith("2026-")],sort_keys=True))
if __name__=="__main__":main()
