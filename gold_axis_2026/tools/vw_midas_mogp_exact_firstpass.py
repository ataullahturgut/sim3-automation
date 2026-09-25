from __future__ import annotations
import json,math,os
from pathlib import Path
import vw_midas_msvr_successor_v1 as base
from vw_midas_mogp_lcm_v1 import fit_predict

SPEC=(1,1,"RBF",30,0.05)
def runp(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        pred,n,loss=fit_predict(cache[t],t,SPEC)
        p=base.month_shift(t,-1)
        rows.append({"target":t,"origin":p,"forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p]),
                     "pred_log_return_gold":float(pred[0]),"train_rows":n,"loss":loss})
    return rows
def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range("2022-04","2026-07")}
    dev=runp(b,cache,"2022-04","2024-12"); tr=runp(b,cache,"2025-01","2025-12"); st=runp(b,cache,"2026-01","2026-07")
    out={"model_id":"VW_MIDAS_MOGP_EXACT_ICM_R1_FIRSTPASS","spec":SPEC,
         "selection":"NONE_FIXED_STRUCTURAL_FIRSTPASS",
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_mogp_exact_firstpass.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__":main()
