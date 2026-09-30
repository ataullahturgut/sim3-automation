from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho
import gold_monthly_chhho_predev_backcast_v1 as predev

EXPECTED = {
    "2022-04": {"pred": -0.010986345550590273, "forecast": 1926.7157311172843, "train_rows": 145},
    "2023-08": {"pred": 0.023069926091790684, "forecast": 1996.5326234990478, "train_rows": 161},
    "2024-11": {"pred": 0.02935125952261966, "forecast": 2770.1250210570856, "train_rows": 176},
}

def main():
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    rows=[]
    for t,exp in EXPECTED.items():
        o=base.month_shift(t,-1)
        canonical=base.all_samples_at_origin(b,t,governed=True)
        helper=predev.all_samples_with_history(b,t,b.gpr_vintages[o])
        ck=sorted(canonical); hk=sorted(helper)
        assert ck==hk, (t,ck[:3],hk[:3],ck[-3:],hk[-3:])
        maxdiff=0.0
        for k in ck:
            for i in (0,1):
                maxdiff=max(maxdiff,float(np.max(np.abs(canonical[k][i]-helper[k][i]))))
        p1,n1,d1=chhho.select(canonical,t,"CHHHO")
        p2,n2,d2=chhho.select(helper,t,"CHHHO")
        pred1=float(p1[0]); pred2=float(p2[0])
        fc=float(b.core_gold[o]*math.exp(pred2))
        rows.append({
            "target":t,"origin":o,"sample_keys":len(ck),"max_sample_abs_diff":maxdiff,
            "canonical_pred":pred1,"helper_pred":pred2,"expected_pred":exp["pred"],
            "helper_forecast":fc,"expected_forecast":exp["forecast"],
            "canonical_train_rows":n1,"helper_train_rows":n2,"expected_train_rows":exp["train_rows"],
            "pred_diff_helper_vs_canonical":abs(pred2-pred1),
            "pred_diff_vs_expected":abs(pred2-exp["pred"]),
            "forecast_diff_vs_expected":abs(fc-exp["forecast"]),
            "diag_equal":d1==d2,
        })
    gate=all(
        r["max_sample_abs_diff"] < 1e-14 and
        r["pred_diff_helper_vs_canonical"] < 1e-14 and
        r["pred_diff_vs_expected"] < 1e-12 and
        r["forecast_diff_vs_expected"] < 1e-9 and
        r["canonical_train_rows"]==r["helper_train_rows"]==r["expected_train_rows"] and
        r["diag_equal"]
        for r in rows
    )
    out={"schema":"GOLD_MONTHLY_CHHHO_BACKCAST_RECONCILE_V1_2026-09-30",
         "gate":"PASS" if gate else "FAIL","rows":rows}
    Path("GOLD_MONTHLY_CHHHO_BACKCAST_RECONCILE_V1_2026-09-30.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    if not gate:
        raise SystemExit(2)

if __name__=="__main__":
    main()
