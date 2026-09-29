from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np

def load_all(d):
    out={}
    for p in Path(d).glob("chhho_f2_*.json"):
        z=json.loads(p.read_text())
        out[z["variant"]]=z
    return out

def rowmap(z): return {r["target"]:r for r in z["dev"]["rows"]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--dir",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    z=load_all(a.dir)
    if "CURRENT8" not in z: raise RuntimeError("CURRENT8_MISSING")
    base=z["CURRENT8"]; bmap=rowmap(base); bm=base["dev"]["metrics"]
    rows=[]
    for name,q in sorted(z.items()):
        qm=rowmap(q); targets=sorted(set(bmap)&set(qm))
        bae=np.array([abs(bmap[t]["forecast"]-bmap[t]["actual"]) for t in targets],float)
        qae=np.array([abs(qm[t]["forecast"]-qm[t]["actual"]) for t in targets],float)
        d=bae-qae
        m=q["dev"]["metrics"]
        yearly=q["dev"]["yearly"]
        year_deltas={}
        for y in sorted(yearly):
            if y in base["dev"]["yearly"]:
                year_deltas[y]=base["dev"]["yearly"][y]["sum_abs_error"]-yearly[y]["sum_abs_error"]
        rows.append({
          "variant":name,"spec":q["spec"],
          "sum_abs_error":m["sum_abs_error"],"direction_correct":m["direction_correct"],
          "mae":m["mae"],"rmse":m["rmse"],"mape_pct":m["mape_pct"],
          "delta_sum_abs_error_vs_current8":bm["sum_abs_error"]-m["sum_abs_error"],
          "pct_improvement_vs_current8":100*(bm["sum_abs_error"]-m["sum_abs_error"])/bm["sum_abs_error"],
          "direction_delta_vs_current8":m["direction_correct"]-bm["direction_correct"],
          "months_improved":int(np.sum(d>1e-9)),"months_worsened":int(np.sum(d<-1e-9)),
          "months_tied":int(np.sum(np.abs(d)<=1e-9)),
          "median_paired_ae_improvement":float(np.median(d)),
          "mean_paired_ae_improvement":float(np.mean(d)),
          "worst_single_month_penalty_vs_current8":float(np.min(d)),
          "best_single_month_gain_vs_current8":float(np.max(d)),
          "year_delta_sum_abs_error_vs_current8":year_deltas,
          "yearly":yearly,
        })
    rows.sort(key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["variant"]))
    robust=[]
    for r in rows:
        if r["variant"]=="CURRENT8": continue
        y=list(r["year_delta_sum_abs_error_vs_current8"].values())
        # Exploratory robustness: aggregate better, majority of months not worse,
        # positive median paired effect, and improvement in >=2 of 3 DEV years.
        pass_gate=(r["delta_sum_abs_error_vs_current8"]>0 and
                   r["months_improved"]>=r["months_worsened"] and
                   r["median_paired_ae_improvement"]>0 and
                   sum(v>0 for v in y)>=2)
        robust.append({"variant":r["variant"],"pass":bool(pass_gate),
                       "positive_years":sum(v>0 for v in y),"year_deltas":r["year_delta_sum_abs_error_vs_current8"]})
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F2_REPRESENTATION_SUMMARY_V1_2026-09-29",
      "authority":{
        "dev":"2022-04..2024-12","2025_used":False,"2026_used":False,
        "random_split":"NONE","external_features_used":False,"lag_search_used":False,
        "question":"representation only; same feature families/count and same ChHHO architecture", "canonical_training_sample_start":"2010-03",
        "robustness_gate":"aggregate improvement + months improved>=worsened + positive median paired AE + >=2 positive DEV years",
      },
      "baseline_parity":base["f2_baseline_parity"],
      "ranking_by_dev_sum_abs_error":rows,
      "robustness":robust,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F2_SUMMARY_GATE=PASS")
    for r in rows:
        print(json.dumps({k:r[k] for k in ["variant","sum_abs_error","direction_correct","delta_sum_abs_error_vs_current8","pct_improvement_vs_current8","months_improved","months_worsened","median_paired_ae_improvement","year_delta_sum_abs_error_vs_current8"]},sort_keys=True))
    print("ROBUST_PASS="+json.dumps([x["variant"] for x in robust if x["pass"]]))
if __name__=="__main__":main()
