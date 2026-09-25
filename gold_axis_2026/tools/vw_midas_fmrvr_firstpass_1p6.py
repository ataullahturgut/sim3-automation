from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
from vw_midas_fmrvr_v1 import FMRVR, arrays

WIDTH=1.6
def run_period(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        ks,X,Y,tx,ym,ys=arrays(cache[t],t)
        m=FMRVR(width=WIDTH,max_iters=300,tolerance=0.1,seed=7+sum(map(ord,t))).fit(X,Y)
        pred=m.predict(tx)[0]*ys+ym
        p=base.month_shift(t,-1)
        rows.append({"target":t,"origin":p,"forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p]),
                     "pred_log_return_gold":float(pred[0]),"relevance_vectors":len(m.used),"iterations":m.n_iters})
    return rows
def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range("2022-04","2026-07")}
    dev=run_period(b,cache,"2022-04","2024-12")
    tr=run_period(b,cache,"2025-01","2025-12")
    st=run_period(b,cache,"2026-01","2026-07")
    out={"model_id":"VW_MIDAS_FMRVR_AUTHOR_DEFAULT_1P6_FIRSTPASS",
         "kernel_width":WIDTH,"selection":"NONE_AUTHOR_DEMO_DEFAULT",
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "2025_role":"LOCKED_TRANSPORT","2026_role":"RETROSPECTIVE_STRESS"}}
    Path("vw_midas_fmrvr_firstpass_1p6.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
