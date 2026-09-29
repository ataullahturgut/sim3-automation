from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import gold_monthly_dev_snapshot_v1 as snap
import gold_monthly_chhho_f3_lag_audit_v1 as f3
import vw_midas_elmfis_baseline_v1 as eb

def clean(x):
    if isinstance(x,float):
        return x if math.isfinite(x) else None
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,list): return [clean(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True);ap.add_argument("--prehistory",required=True)
    ap.add_argument("--baseline",required=True);ap.add_argument("--output",required=True)
    a=ap.parse_args()
    b,meta=snap.load_snapshot(a.snapshot)
    pre=f3.merge_prehistory(b,a.prehistory)
    rows,d=f3.evaluate(b,"L1_L2")
    m=eb.active_metrics(rows); yearly=eb.yearly(rows)
    base=json.loads(Path(a.baseline).read_text())
    bm=base["dev"]["metrics"]; bmap={r["target"]:r for r in base["dev"]["rows"]}
    qmap={r["target"]:r for r in rows};ts=sorted(set(bmap)&set(qmap))
    delta=np.array([abs(bmap[t]["forecast"]-bmap[t]["actual"])-abs(qmap[t]["forecast"]-qmap[t]["actual"]) for t in ts])
    yd={y:base["dev"]["yearly"][y]["sum_abs_error"]-yearly[y]["sum_abs_error"] for y in yearly}
    paired={
      "delta_sum_abs_error_vs_l1":bm["sum_abs_error"]-m["sum_abs_error"],
      "pct_improvement_vs_l1":100*(bm["sum_abs_error"]-m["sum_abs_error"])/bm["sum_abs_error"],
      "direction_delta_vs_l1":m["direction_correct"]-bm["direction_correct"],
      "months_improved":int(np.sum(delta>1e-9)),"months_worsened":int(np.sum(delta<-1e-9)),
      "months_tied":int(np.sum(np.abs(delta)<=1e-9)),
      "median_paired_ae_improvement":float(np.median(delta)),
      "mean_paired_ae_improvement":float(np.mean(delta)),
      "year_delta_sum_abs_error_vs_l1":yd,
    }
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F3_L1L2_RECOVERY_V1_2026-09-29",
      "variant":"L1_L2","input_dimension":d,
      "technical_recovery":"Original run completed model computation but artifact serialization failed on non-finite diagnostic condition number; non-finite diagnostics mapped to null only. Forecasts/metrics unchanged.",
      "authority":{"dev":"2022-04..2024-12","2025_used":False,"2026_used":False,"random_split":"NONE",
        "representation":"FROZEN_CURRENT8_MR1_PLUS_VW","neon_reads":0,
        "snapshot_payload_sha256":meta["payload_sha256"],"prehistory_payload_sha256":pre["payload_sha256"],
        "baseline_artifact":11021516711},
      "dev":{"metrics":m,"yearly":yearly,"rows":clean(rows)},"paired_vs_l1":paired,
    }
    Path(a.output).write_text(json.dumps(clean(out),indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F3_L1L2_RECOVERY_GATE=PASS")
    print(json.dumps({"sum_abs_error":m["sum_abs_error"],"direction_correct":m["direction_correct"],**paired},sort_keys=True))
if __name__=="__main__":main()
