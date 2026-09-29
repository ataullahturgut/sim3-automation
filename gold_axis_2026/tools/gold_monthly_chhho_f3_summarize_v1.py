from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np

def load_all(d):
    out={}
    for p in Path(d).glob("chhho_f3_*.json"):
        z=json.loads(p.read_text())
        out[z["variant"]]=z
    return out
def rowmap(z): return {r["target"]:r for r in z["dev"]["rows"]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--dir",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    z=load_all(a.dir)
    if "L1" not in z: raise RuntimeError("L1_BASELINE_MISSING")
    base=z["L1"]; bm=base["dev"]["metrics"]; bmap=rowmap(base)
    rows=[]
    for name,q in sorted(z.items()):
        qm=rowmap(q); ts=sorted(set(bmap)&set(qm))
        bae=np.array([abs(bmap[t]["forecast"]-bmap[t]["actual"]) for t in ts],float)
        qae=np.array([abs(qm[t]["forecast"]-qm[t]["actual"]) for t in ts],float)
        d=bae-qae; m=q["dev"]["metrics"]
        yd={}
        for y,yr in q["dev"]["yearly"].items():
            yd[y]=base["dev"]["yearly"][y]["sum_abs_error"]-yr["sum_abs_error"]
        rows.append({
          "variant":name,"spec":q["spec"],"input_dimension":q["input_dimension"],
          "sum_abs_error":m["sum_abs_error"],"direction_correct":m["direction_correct"],
          "mae":m["mae"],"rmse":m["rmse"],"mape_pct":m["mape_pct"],
          "delta_sum_abs_error_vs_l1":bm["sum_abs_error"]-m["sum_abs_error"],
          "pct_improvement_vs_l1":100*(bm["sum_abs_error"]-m["sum_abs_error"])/bm["sum_abs_error"],
          "direction_delta_vs_l1":m["direction_correct"]-bm["direction_correct"],
          "months_improved":int(np.sum(d>1e-9)),"months_worsened":int(np.sum(d<-1e-9)),
          "months_tied":int(np.sum(np.abs(d)<=1e-9)),
          "median_paired_ae_improvement":float(np.median(d)),
          "mean_paired_ae_improvement":float(np.mean(d)),
          "year_delta_sum_abs_error_vs_l1":yd,
        })
    rows.sort(key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["variant"]))
    robust=[]
    for r in rows:
        if r["variant"]=="L1": continue
        y=list(r["year_delta_sum_abs_error_vs_l1"].values())
        ok=(r["delta_sum_abs_error_vs_l1"]>0 and r["months_improved"]>=r["months_worsened"] and
            r["median_paired_ae_improvement"]>0 and sum(v>0 for v in y)>=2 and
            r["direction_correct"]>=bm["direction_correct"]-1)
        robust.append({"variant":r["variant"],"pass":bool(ok),"positive_years":sum(v>0 for v in y)})
    out={"schema":"GOLD_MONTHLY_CHHHO_F3_LAG_SUMMARY_V1_2026-09-29",
      "authority":{"dev":"2022-04..2024-12","2025_used":False,"2026_used":False,"random_split":"NONE",
        "representation":"FROZEN_CURRENT8_MR1_PLUS_VW","external_features_used":False,
        "robustness_gate":"aggregate better + months improved>=worsened + positive median paired AE + >=2 positive DEV years + direction loss <=1"},
      "baseline_parity":base["f3_baseline_parity"],"ranking_by_dev_sum_abs_error":rows,"robustness":robust}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F3_SUMMARY_GATE=PASS")
    for r in rows:
        print(json.dumps({k:r[k] for k in ["variant","input_dimension","sum_abs_error","direction_correct","delta_sum_abs_error_vs_l1","pct_improvement_vs_l1","months_improved","months_worsened","median_paired_ae_improvement","year_delta_sum_abs_error_vs_l1"]},sort_keys=True))
    print("ROBUST_PASS="+json.dumps([x["variant"] for x in robust if x["pass"]]))
if __name__=="__main__":main()
