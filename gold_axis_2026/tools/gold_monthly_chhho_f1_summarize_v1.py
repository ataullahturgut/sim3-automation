from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np

def load_all(d):
    out={}
    for p in Path(d).glob("chhho_f1_*.json"):
        z=json.loads(p.read_text())
        out[z["variant"]]=z
    return out

def rowmap(z):
    return {r["target"]:r for r in z["dev"]["rows"]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--dir",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    z=load_all(a.dir)
    if "CURRENT8" not in z: raise RuntimeError("BASELINE_MISSING")
    base=z["CURRENT8"]; bmap=rowmap(base)
    rows=[]
    for name,q in sorted(z.items()):
        qm=rowmap(q); targets=sorted(set(bmap)&set(qm))
        bae=np.array([abs(bmap[t]["forecast"]-bmap[t]["actual"]) for t in targets],float)
        qae=np.array([abs(qm[t]["forecast"]-qm[t]["actual"]) for t in targets],float)
        delta=bae-qae
        bm=base["dev"]["metrics"]; m=q["dev"]["metrics"]
        rows.append({
          "variant":name,
          "kept_features":q["kept_features"],
          "sum_abs_error":m["sum_abs_error"],
          "direction_correct":m["direction_correct"],
          "mae":m["mae"],"rmse":m["rmse"],"mape_pct":m["mape_pct"],
          "delta_sum_abs_error_vs_current8":bm["sum_abs_error"]-m["sum_abs_error"],
          "pct_improvement_vs_current8":100*(bm["sum_abs_error"]-m["sum_abs_error"])/bm["sum_abs_error"],
          "direction_delta_vs_current8":m["direction_correct"]-bm["direction_correct"],
          "months_improved":int(np.sum(delta>1e-9)),
          "months_worsened":int(np.sum(delta<-1e-9)),
          "months_tied":int(np.sum(np.abs(delta)<=1e-9)),
          "median_paired_ae_improvement":float(np.median(delta)),
          "mean_paired_ae_improvement":float(np.mean(delta)),
          "worst_single_month_penalty_vs_current8":float(np.min(delta)),
          "best_single_month_gain_vs_current8":float(np.max(delta)),
          "yearly":q["dev"]["yearly"],
        })
    rows.sort(key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["variant"]))
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F0_F1_SUMMARY_V1_2026-09-29",
      "authority":{
        "dev":"2022-04..2024-12","2025_used":False,"2026_used":False,
        "random_split":"NONE","external_features_used":False,
        "question":"CURRENT8 necessity only; no representation/lag/external changes",
        "selection_warning":"Exploratory necessity audit; no final feature-set promotion without robustness stage",
      },
      "f0_parity":base["f0_parity"],
      "ranking_by_dev_sum_abs_error":rows,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F1_SUMMARY_GATE=PASS")
    for r in rows:
        print(json.dumps({k:r[k] for k in ["variant","sum_abs_error","direction_correct","delta_sum_abs_error_vs_current8","pct_improvement_vs_current8","months_improved","months_worsened","median_paired_ae_improvement"]},sort_keys=True))
if __name__=="__main__":main()
