from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True)
    ap.add_argument("--base",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    b=json.loads(Path(a.base).read_text())
    if not b.get("baseline_parity",{}).get("pass"):
        raise RuntimeError("BASE_PARITY_NOT_PASS")

    files=sorted(Path(a.dir).rglob("fx2_shard_*.json"))
    if len(files)!=6:
        raise RuntimeError(f"EXPECTED_6_SHARDS got={len(files)} {files}")

    rows=[]; auth=None; labels=[]
    for p in files:
        d=json.loads(p.read_text())
        rows.extend(d["rows"]); labels.append(d["label"])
        if auth is None: auth=d["authority"]
        else:
            for k in ("snapshot_payload_sha256","external_v2_payload_sha256","b2_gate_schema"):
                if d["authority"].get(k)!=auth.get(k):
                    raise RuntimeError(f"AUTHORITY_MISMATCH {p} {k}")

    rows=sorted(rows,key=lambda r:r["target"])
    targets=[r["target"] for r in rows]
    expected=list(base.month_range("2022-04","2024-12"))
    if targets!=expected or len(set(targets))!=33:
        raise RuntimeError("TARGET_COVERAGE_FAIL")

    m=eb.active_metrics(rows)
    yr=eb.yearly(rows)
    br={r["target"]:r for r in b["dev"]["rows"]}
    b_ae=np.array([abs(float(br[t]["forecast"])-float(br[t]["actual"])) for t in targets])
    x_ae=np.array([abs(float(r["forecast"])-float(r["actual"])) for r in rows])
    paired=b_ae-x_ae
    bsum=float(b_ae.sum()); xsum=float(x_ae.sum())

    yearly={}
    for y in ("2022","2023","2024"):
        ix=[i for i,t in enumerate(targets) if t.startswith(y)]
        bs=float(b_ae[ix].sum()); xs=float(x_ae[ix].sum())
        yearly[y]={"base_sum_abs_error":bs,"fx2_sum_abs_error":xs,"delta_base_minus_fx2":bs-xs}

    signed=np.array([float(r["forecast"])-float(r["actual"]) for r in rows])
    loo=[]
    for i,t in enumerate(targets):
        loo.append({"left_out_target":t,"base_minus_fx2_improvement":float((bsum-b_ae[i])-(xsum-x_ae[i]))})

    out={
      "schema":"GOLD_MONTHLY_F4_FX2_BROADUSD_MR1_DAILY_RMS_VOL_RESULT_V1_2026-09-29",
      "variant":"FX2_BROADUSD_MR1_PLUS_DAILY_RMS_VOL",
      "execution":{"mode":"PARALLEL_OUTER_ORIGIN_SHARDS","shards":labels},
      "authority":{
        "selection_period":"2022-04..2024-12",
        "2025_used":False,
        "2026_used":False,
        "base_parity_pass":True,
        "total_inputs":10,
        "population":30,
        "gpr_fx_weighting_used":False,
        "snapshot_payload_sha256":auth["snapshot_payload_sha256"],
        "external_v2_payload_sha256":auth["external_v2_payload_sha256"],
        "b2_gate_schema":auth["b2_gate_schema"],
      },
      "base":{
        "sum_abs_error":float(b["dev"]["metrics"]["sum_abs_error"]),
        "direction_correct":int(b["dev"]["metrics"]["direction_correct"]),
        "metrics":b["dev"]["metrics"],
      },
      "fx2":{
        "sum_abs_error":float(m["sum_abs_error"]),
        "direction_correct":int(m["direction_correct"]),
        "metrics":m,
        "yearly":yr,
        "rows":rows,
      },
      "comparison":{
        "delta_sum_abs_error_base_minus_fx2":float(bsum-xsum),
        "relative_improvement_pct":float((bsum-xsum)/bsum*100.0),
        "direction_delta_correct":int(m["direction_correct"])-int(b["dev"]["metrics"]["direction_correct"]),
        "paired_wins":int(np.sum(paired>1e-12)),
        "paired_losses":int(np.sum(paired<-1e-12)),
        "paired_ties":int(len(paired)-np.sum(paired>1e-12)-np.sum(paired<-1e-12)),
        "median_paired_abs_error_improvement":float(np.median(paired)),
        "mean_paired_abs_error_improvement":float(np.mean(paired)),
        "worst_fx2_abs_error":float(x_ae.max()),
        "worst_fx2_target":targets[int(np.argmax(x_ae))],
        "fx2_signed_bias_mean":float(signed.mean()),
        "yearly":yearly,
        "leave_one_origin":{
          "min_improvement":float(min(x["base_minus_fx2_improvement"] for x in loo)),
          "max_improvement":float(max(x["base_minus_fx2_improvement"] for x in loo)),
          "all":loo,
        },
      },
      "interpretation":{
        "dev_sum_abs_error_improved":bool(xsum<bsum),
        "direction_improved":bool(int(m["direction_correct"])>int(b["dev"]["metrics"]["direction_correct"])),
        "direction_not_worse":bool(int(m["direction_correct"])>=int(b["dev"]["metrics"]["direction_correct"])),
        "median_paired_improvement_positive":bool(float(np.median(paired))>0),
        "all_leave_one_origin_improvements_positive":bool(min(x["base_minus_fx2_improvement"] for x in loo)>0),
      },
    }

    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_FX2_SUMMARY_GATE=PASS")
    print(json.dumps({
      "base_sum_abs_error":out["base"]["sum_abs_error"],
      "base_direction":out["base"]["direction_correct"],
      "fx2_sum_abs_error":out["fx2"]["sum_abs_error"],
      "fx2_direction":out["fx2"]["direction_correct"],
      "comparison":{k:v for k,v in out["comparison"].items() if k not in {"leave_one_origin","yearly"}},
      "yearly":out["comparison"]["yearly"],
      "interpretation":out["interpretation"],
    },sort_keys=True))


if __name__=="__main__":
    main()
