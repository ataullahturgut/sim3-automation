from __future__ import annotations
import json, os
from pathlib import Path
import pandas as pd

import gold_nextday_direction_hourly_lag_v2 as v2
import gold_nextday_direction_hourly_lag_v3_selection as v3

OUT=Path(os.environ.get("OUT_DIR","gold_nextday_hourly_block_v4b_out"))
OUT.mkdir(parents=True,exist_ok=True)

BASE=list(v2.V1_FEATURES)
LAG2="hr_ret_lag2"
BLOCK="blk3_19_21"

def add_block(d):
    q=d.copy()
    q[BLOCK]=q[["hr_ret_lag19","hr_ret_lag20","hr_ret_lag21"]].sum(axis=1)
    return q

def cmp(model,period,m):
    return {"model":model,"period":str(period),**m,"false_call_rate":1-m["accuracy"]}

def main():
    hourly=v2.load_hourly()
    daily=add_block(v2.build_daily(hourly))

    specs={
        "V1":BASE,
        "V3_LAG2":BASE+[LAG2],
        "BLOCK_ONLY":BASE+[BLOCK],
        "V3_PLUS_BLOCK":BASE+[LAG2,BLOCK],
    }

    ledgers=[]; fitlogs=[]; rows=[]
    for year in [2023,2024]:
        for name,features in specs.items():
            m,led,fit=v3.oos_year(daily,features,year,name)
            rows.append(cmp(name,year,m))
            ledgers.append(led)
            fitlogs.append(fit)

    led=pd.concat(ledgers,ignore_index=True)
    for name in specs:
        g=led[led.tag==name].copy()
        y=(g.actual_direction=="UP").astype(int).to_numpy()
        m=v3.metric(y,g.p_up.to_numpy(float))
        rows.append(cmp(name,"2023-2024",m))

    mdf=pd.DataFrame(rows)
    mdf.to_csv(OUT/"block_v4b_metrics.csv",index=False)
    led.to_csv(OUT/"block_v4b_predictions.csv",index=False)
    pd.concat(fitlogs,ignore_index=True).to_csv(OUT/"block_v4b_fitlog.csv",index=False)

    result={
        "schema":"GOLD_NEXTDAY_DIRECTION_HOURLY_BLOCK_V4B_CONFIRM",
        "frozen_block":BLOCK,
        "specifications":{k:v for k,v in specs.items()},
        "metrics":mdf.to_dict(orient="records"),
    }
    (OUT/"block_v4b_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD NEXT-DAY DIRECTION — HOURLY BLOCK V4B CONFIRMATION","",
        "Frozen 2023 winner: **blk3_19_21 = hr_ret_lag19 + hr_ret_lag20 + hr_ret_lag21**.","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for period in ["2023","2024","2023-2024"]:
        for name in ["V1","V3_LAG2","BLOCK_ONLY","V3_PLUS_BLOCK"]:
            r=mdf[(mdf.model==name)&(mdf.period==period)].iloc[0]
            lines.append(
                f"| {name} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.false_call_rate:.2f}% |"
            )
    lines += ["","No 2024 outcome altered the frozen block identity or model specifications."]
    (OUT/"HOURLY_BLOCK_V4B_RESULT.md").write_text("\n".join(lines)+"\n")
    print("BLOCK_V4B_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"HOURLY_BLOCK_V4B_RESULT.md").read_text())

if __name__=="__main__":
    main()
