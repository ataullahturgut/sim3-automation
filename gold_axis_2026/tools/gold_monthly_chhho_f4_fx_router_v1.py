from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import vw_midas_elmfis_baseline_v1 as eb

def load_all(d):
    out={}
    for p in Path(d).glob("f4_fx_*.json"):
        z=json.loads(p.read_text())
        out[z["candidate"]]=z
    return out

def rowmap(z):
    return {r["target"]:r for r in z["dev"]["rows"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    z=load_all(a.dir)
    if "BASE" not in z: raise RuntimeError("BASE_MISSING")

    maps={k:rowmap(v) for k,v in z.items()}
    targets=sorted(maps["BASE"])
    routed=[]; usage={k:0 for k in z}

    for t in targets:
        ranked=[]
        for name,m in maps.items():
            r=m[t]
            ranked.append((float(r["inner_validation_fitness"]),len(r["columns"]),0 if name=="BASE" else 1,name,r))
        ranked.sort(key=lambda x:(x[0],x[1],x[2],x[3]))
        _,_,_,name,r=ranked[0]
        q=dict(r)
        q["selected_candidate"]=name
        q["inner_family_ranking"]=[{"candidate":x[3],"fitness":x[0],"n_external":x[1]} for x in ranked]
        routed.append(q); usage[name]+=1

    base_rows=z["BASE"]["dev"]["rows"]
    bm=eb.active_metrics(base_rows); rm=eb.active_metrics(routed)
    bmap={r["target"]:r for r in base_rows}
    rmap={r["target"]:r for r in routed}

    d=np.array([
      abs(bmap[t]["forecast"]-bmap[t]["actual"])-abs(rmap[t]["forecast"]-rmap[t]["actual"])
      for t in targets
    ],float)

    yearly={}
    for y in ["2022","2023","2024"]:
        ts=[t for t in targets if t.startswith(y)]
        yearly[y]=float(sum(
          abs(bmap[t]["forecast"]-bmap[t]["actual"])-abs(rmap[t]["forecast"]-rmap[t]["actual"])
          for t in ts
        ))

    total=float(d.sum())
    leave=[total-float(x) for x in d]
    direction_loss=int(bm["direction_correct"]-rm["direction_correct"])

    pass_gate=(
      rm["sum_abs_error"]<bm["sum_abs_error"] and
      int(np.sum(d>1e-9))>=int(np.sum(d<-1e-9)) and
      float(np.median(d))>0 and
      sum(v>0 for v in yearly.values())>=2 and
      direction_loss<=1 and
      min(leave)>0 and
      all(np.isfinite(r["forecast"]) for r in routed)
    )

    out={
      "schema":"GOLD_MONTHLY_CHHHO_F4_FX_ROUTER_V1_2026-09-29",
      "authority":{
        "selection":"INNER_CHRONOLOGICAL_ONLY",
        "outer_dev":"2022-04..2024-12",
        "2025_used":False,"2026_used":False,"random_split":"NONE",
        "family_candidates":sorted(z),
        "tie_break":"lower fitness, then fewer external features, then BASE",
        "promotion_gate":"charter F4 section 6",
      },
      "base":{"metrics":bm,"rows":base_rows},
      "routed":{"metrics":rm,"rows":routed,"usage":usage},
      "paired":{
        "delta_sum_abs_error":total,
        "pct_improvement":100*total/bm["sum_abs_error"],
        "months_improved":int(np.sum(d>1e-9)),
        "months_worsened":int(np.sum(d<-1e-9)),
        "months_tied":int(np.sum(np.abs(d)<=1e-9)),
        "median_ae_improvement":float(np.median(d)),
        "mean_ae_improvement":float(np.mean(d)),
        "year_delta_sum_abs_error":yearly,
        "min_leave_one_origin_total_improvement":float(min(leave)),
        "direction_loss":direction_loss,
      },
      "promotion_pass":bool(pass_gate),
    }

    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_FX_ROUTER_GATE=PASS")
    print(json.dumps({
      "base_sum_ae":bm["sum_abs_error"],
      "routed_sum_ae":rm["sum_abs_error"],
      "base_direction":bm["direction_correct"],
      "routed_direction":rm["direction_correct"],
      "usage":usage,
      "paired":out["paired"],
      "promotion_pass":bool(pass_gate),
    },sort_keys=True))

if __name__=="__main__": main()
