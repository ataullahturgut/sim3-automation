from __future__ import annotations
import json, os
from pathlib import Path

import numpy as np
import pandas as pd

import gold_nextday_direction_hourly_lag_v2 as v2
import gold_nextday_direction_hourly_lag_v3_selection as v3

OUT=Path(os.environ.get("OUT_DIR","gold_nextday_hourly_block_v4_out"))
OUT.mkdir(parents=True,exist_ok=True)

BASE=list(v2.V1_FEATURES)
V3_BASE=BASE+["hr_ret_lag2"]
MAX_KEEP=4
MIN_BA_GAIN=0.005
MAX_BRIER_WORSEN=0.002
MAX_ACC_DROP=0.005

BLOCKS=[]
for s in range(23):
    BLOCKS.append((f"blk2_{s}_{s+1}",[f"hr_ret_lag{s}",f"hr_ret_lag{s+1}"]))
for s in range(22):
    BLOCKS.append((f"blk3_{s}_{s+2}",[f"hr_ret_lag{s}",f"hr_ret_lag{s+1}",f"hr_ret_lag{s+2}"]))

def add_blocks(daily):
    q=daily.copy()
    for name,parts in BLOCKS:
        q[name]=q[parts].sum(axis=1)
    return q

def delta_row(name,m,base):
    return {
        "block":name,
        **m,
        "delta_accuracy":float(m["accuracy"]-base["accuracy"]),
        "delta_balanced_accuracy":float(m["balanced_accuracy"]-base["balanced_accuracy"]),
        "delta_brier":float(m["brier"]-base["brier"]),
        "delta_logloss":float(m["logloss"]-base["logloss"]),
        "delta_up_recall":float(m["up_recall"]-base["up_recall"]),
        "delta_down_recall":float(m["down_recall"]-base["down_recall"]),
    }

def oos(daily,features,year,tag):
    return v3.oos_year(daily,features,year,tag)

def compare_row(model,period,m):
    return {"model":model,"period":str(period),**m,"false_call_rate":1-m["accuracy"]}

def main():
    hourly=v2.load_hourly()
    daily=add_blocks(v2.build_daily(hourly))

    base23,base23_led,base23_fit=oos(daily,BASE,2023,"V1")
    v3_23,v3_23_led,v3_23_fit=oos(daily,V3_BASE,2023,"V3_LAG2")

    # Stage A: standalone blocks relative to V1.
    standalone=[]
    for name,_ in BLOCKS:
        m,_,_=oos(daily,BASE+[name],2023,f"STANDALONE_{name}")
        standalone.append(delta_row(name,m,base23))
    sadf=pd.DataFrame(standalone).sort_values(
        ["delta_balanced_accuracy","delta_accuracy","delta_brier"],
        ascending=[False,False,True]
    )
    sadf.to_csv(OUT/"block_v4_standalone_2023.csv",index=False)

    # Stage B: each block beyond V3 lag2.
    incremental=[]
    for name,_ in BLOCKS:
        m,_,_=oos(daily,V3_BASE+[name],2023,f"V3_PLUS_{name}")
        incremental.append(delta_row(name,m,v3_23))
    iadf=pd.DataFrame(incremental).sort_values(
        ["delta_balanced_accuracy","delta_accuracy","delta_brier"],
        ascending=[False,False,True]
    )
    iadf.to_csv(OUT/"block_v4_incremental_over_v3_2023.csv",index=False)

    # Stage C: greedy forward selection from V3, 2023 only.
    kept=[]
    remaining=[x[0] for x in BLOCKS]
    current_features=V3_BASE.copy()
    current_metrics=v3_23
    steps=[]
    while remaining and len(kept)<MAX_KEEP:
        cand=[]
        for name in remaining:
            m,_,_=oos(daily,current_features+[name],2023,f"GREEDY_{len(kept)+1}_{name}")
            cand.append((name,m))
        cand.sort(
            key=lambda x:(x[1]["balanced_accuracy"],x[1]["accuracy"],-x[1]["brier"]),
            reverse=True
        )
        best,bm=cand[0]
        dba=bm["balanced_accuracy"]-current_metrics["balanced_accuracy"]
        dacc=bm["accuracy"]-current_metrics["accuracy"]
        db=bm["brier"]-current_metrics["brier"]
        accept=(dba>=MIN_BA_GAIN and db<=MAX_BRIER_WORSEN and dacc>=-MAX_ACC_DROP)
        steps.append({
            "step":len(kept)+1,
            "candidate":best,
            "accepted":bool(accept),
            "before_accuracy":current_metrics["accuracy"],
            "after_accuracy":bm["accuracy"],
            "delta_accuracy":dacc,
            "before_balanced_accuracy":current_metrics["balanced_accuracy"],
            "after_balanced_accuracy":bm["balanced_accuracy"],
            "delta_balanced_accuracy":dba,
            "before_brier":current_metrics["brier"],
            "after_brier":bm["brier"],
            "delta_brier":db,
            "after_logloss":bm["logloss"],
        })
        if not accept:
            break
        kept.append(best)
        remaining.remove(best)
        current_features=V3_BASE+kept
        current_metrics=bm
    pd.DataFrame(steps).to_csv(OUT/"block_v4_selection_steps.csv",index=False)

    # Frozen 2023/2024 comparisons.
    v4_23,v4_23_led,v4_23_fit=oos(daily,V3_BASE+kept,2023,"V4_SELECTED")
    base24,base24_led,base24_fit=oos(daily,BASE,2024,"V1")
    v3_24,v3_24_led,v3_24_fit=oos(daily,V3_BASE,2024,"V3_LAG2")
    v4_24,v4_24_led,v4_24_fit=oos(daily,V3_BASE+kept,2024,"V4_SELECTED")

    comp=[
        compare_row("V1","2023",base23),
        compare_row("V3_LAG2","2023",v3_23),
        compare_row("V4_SELECTED","2023",v4_23),
        compare_row("V1","2024",base24),
        compare_row("V3_LAG2","2024",v3_24),
        compare_row("V4_SELECTED","2024",v4_24),
    ]
    led=pd.concat([
        base23_led,v3_23_led,v4_23_led,
        base24_led,v3_24_led,v4_24_led
    ],ignore_index=True)
    led.to_csv(OUT/"block_v4_predictions.csv",index=False)
    pd.concat([
        base23_fit,v3_23_fit,v4_23_fit,
        base24_fit,v3_24_fit,v4_24_fit
    ],ignore_index=True).to_csv(OUT/"block_v4_fitlog.csv",index=False)

    for label,tags in [
        ("V1",["V1"]),
        ("V3_LAG2",["V3_LAG2"]),
        ("V4_SELECTED",["V4_SELECTED"]),
    ]:
        g=led[led.tag.isin(tags)].copy()
        y=(g.actual_direction=="UP").astype(int).to_numpy()
        m=v3.metric(y,g.p_up.to_numpy(float))
        comp.append(compare_row(label,"2023-2024",m))
    cdf=pd.DataFrame(comp)
    cdf.to_csv(OUT/"block_v4_metrics.csv",index=False)

    coeff=v3.final_coefficients(daily,V3_BASE+kept,2023)
    coeff.to_csv(OUT/"block_v4_coefficients_through_2023.csv",index=False)

    result={
        "schema":"GOLD_NEXTDAY_DIRECTION_HOURLY_SMALL_BLOCK_V4",
        "candidate_block_count":len(BLOCKS),
        "selected_blocks":kept,
        "selected_count":len(kept),
        "selection_steps":steps,
        "top_standalone_2023":sadf.head(15)[[
            "block","delta_accuracy","delta_balanced_accuracy","delta_brier","delta_logloss"
        ]].to_dict(orient="records"),
        "top_incremental_over_v3_2023":iadf.head(15)[[
            "block","delta_accuracy","delta_balanced_accuracy","delta_brier","delta_logloss"
        ]].to_dict(orient="records"),
        "metrics":cdf.to_dict(orient="records"),
        "governance_note":"2023 selection only; 2024 frozen confirmation in already-opened research history."
    }
    (OUT/"block_v4_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    def row(model,period):
        r=cdf[(cdf.model==model)&(cdf.period==period)].iloc[0]
        return (
            f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.false_call_rate:.2f}% |"
        )

    lines=[
        "# GOLD NEXT-DAY DIRECTION — HOURLY SMALL-BLOCK V4","",
        "45 contiguous 2h/3h blocks tested. 2023 selection; 2024 frozen confirmation.","",
        f"Selected blocks: **{', '.join(kept) if kept else 'NONE'}**.","",
        "## Best standalone blocks vs V1 on 2023","",
        "| Block | Δ accuracy | Δ balanced acc | Δ Brier | Δ log loss |",
        "|---|---:|---:|---:|---:|"
    ]
    for r in sadf.head(10).itertuples():
        lines.append(
            f"| {r.block} | {100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.delta_brier:+.4f} | {r.delta_logloss:+.4f} |"
        )
    lines += ["","## Best incremental blocks over frozen V3 (V1 + lag2) on 2023","",
              "| Block | Δ accuracy | Δ balanced acc | Δ Brier | Δ log loss |",
              "|---|---:|---:|---:|---:|"]
    for r in iadf.head(10).itertuples():
        lines.append(
            f"| {r.block} | {100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.delta_brier:+.4f} | {r.delta_logloss:+.4f} |"
        )
    lines += ["","## Frozen comparison","",
              "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["2023","2024","2023-2024"]:
        for model in ["V1","V3_LAG2","V4_SELECTED"]:
            lines.append(row(model,period))
    lines += ["","All selections were made from 2023 only. 2024 did not alter the selected block set."]
    (OUT/"HOURLY_BLOCK_V4_RESULT.md").write_text("\n".join(lines)+"\n")
    print("BLOCK_V4_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"HOURLY_BLOCK_V4_RESULT.md").read_text())

if __name__=="__main__":
    main()
