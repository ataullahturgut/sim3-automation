from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
FSMR=AX/"GOLD_EXECUTION_FSMR_STAGE4_PREDICTIONS_2026-10-07.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
MET=AX/"GOLD_EXECUTION_FSMR_STAGE4_METRICS_2026-10-07.csv"
OUTS=AX/"GOLD_EXECUTION_FSMR_STABILITY_RECONCILIATION_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_FSMR_STABILITY_RECONCILIATION_RESULT_2026-10-07.md"
OUTC=AX/"GOLD_EXECUTION_FSMR_STABILITY_COMMON_ROWS_2026-10-07.csv"

MIN_N=100
MIN_COV=.35
MAX_COV=.80

def metric(y,p):
    y=np.asarray(y,int);p=np.asarray(p,int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    return {"n":len(y),"accuracy":float(accuracy_score(y,p)),"ba":float(balanced_accuracy_score(y,p)),
            "up_recall":float(recall_score(y,p,pos_label=1,zero_division=0)),
            "down_recall":float(recall_score(y,p,pos_label=0,zero_division=0)),
            "tn":tn,"fp":fp,"fn":fn,"tp":tp}

def choose(m):
    rows=[]
    for (model,delta),g in m[m.year.isin([2023,2024])].groupby(["model","delta"]):
        if set(g.year)!=set([2023,2024]):continue
        y3=g[g.year==2023].iloc[0];y4=g[g.year==2024].iloc[0]
        eligible=bool(y3.n>=MIN_N and y4.n>=MIN_N and y3.coverage>=MIN_COV and y4.coverage>=MIN_COV and y3.coverage<=MAX_COV and y4.coverage<=MAX_COV and .1<=y3.pred_up_rate<=.9 and .1<=y4.pred_up_rate<=.9)
        score=min(float(y3.ba),float(y4.ba)) if eligible else -1
        meanba=(float(y3.ba)+float(y4.ba))/2
        rows.append({"model":model,"delta":float(delta),"eligible":eligible,"min_year_ba":score,"mean_ba":meanba,
                     "ba_2023":float(y3.ba),"ba_2024":float(y4.ba),"n_2023":int(y3.n),"n_2024":int(y4.n),
                     "coverage_2023":float(y3.coverage),"coverage_2024":float(y4.coverage)})
    rows=sorted(rows,key=lambda x:(x["min_year_ba"],x["mean_ba"],min(x["coverage_2023"],x["coverage_2024"])),reverse=True)
    return rows[0],rows

def main():
    f=pd.read_csv(FSMR,parse_dates=["date"])
    p=pd.read_csv(PAIR,parse_dates=["date"])
    m=pd.read_csv(MET)
    chosen,ranking=choose(m)
    model=chosen["model"];delta=chosen["delta"]

    q=f[(f.model==model)&(f.confidence>=delta)].copy()
    pair=p[p.policy=="PAIR_ALL"][["date","year","period","pred","y"]].rename(columns={"pred":"pair_pred","y":"pair_y"})
    q=q.merge(pair,on=["date","year"],how="left",validate="one_to_one")
    if not q.pair_pred.notna().all():raise RuntimeError("PAIR_MATCH_FAIL")
    q["fsmr_correct"]=q.pred.astype(int).eq(q.y.astype(int))
    q["pair_correct"]=q.pair_pred.astype(int).eq(q.y.astype(int))
    q["rescue"]=~q.pair_correct & q.fsmr_correct
    q["break"]=q.pair_correct & ~q.fsmr_correct
    rows={}
    for year in [2023,2024,2025]:
        g=q[q.year==year]
        a=metric(g.y,g.pred);b=metric(g.y,g.pair_pred)
        majority=max(float(g.y.mean()),1-float(g.y.mean()))
        rows[str(year)]={"fsmr":a,"pair_same_rows":b,"majority_accuracy":majority,
                         "rescue":int(g.rescue.sum()),"break":int(g['break'].sum()),"net_rescue":int(g.rescue.sum()-g['break'].sum())}
    dev=q[q.year.isin([2023,2024])]
    rows["DEV"]={"fsmr":metric(dev.y,dev.pred),"pair_same_rows":metric(dev.y,dev.pair_pred),
                 "majority_accuracy":max(float(dev.y.mean()),1-float(dev.y.mean())),
                 "rescue":int(dev.rescue.sum()),"break":int(dev['break'].sum()),"net_rescue":int(dev.rescue.sum()-dev['break'].sum())}
    summary={"status":"COMPLETE","selector":"maximize minimum BA across 2023 and 2024 among preregistered FSMR candidates; require N>=100/year, 35%-80% coverage/year and noncollapsed predictions",
             "selection_uses_2025":False,"chosen":chosen,"ranking":ranking,"common_row_comparison":rows,
             "interpretation":"development-stable selective overnight specialist; 2025 is retrospective transport, not untouched prospective evidence"}
    q.to_csv(OUTC,index=False);OUTS.write_text(json.dumps(summary,indent=2)+"\n")
    def pct(x):return f"{100*float(x):.2f}%"
    lines=["# GOLD EXECUTION FSMR STABILITY RECONCILIATION — 2026-10-07","",
           "**Status:** COMPLETE / DEVELOPMENT-STABILITY SELECTOR","",
           "Selection uses 2023-2024 only and ignores 2025 outcomes.","",
           f"Chosen candidate: **{model} / delta {delta:.2f}**.","",
           "| Period | N | FSMR Acc | FSMR BA | Pair Acc same rows | Pair BA same rows | Majority Acc | Rescue | Break | Net |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for year in ["2023","2024","DEV","2025"]:
        z=rows[year]
        lines.append(f"| {year} | {z['fsmr']['n']} | {pct(z['fsmr']['accuracy'])} | {pct(z['fsmr']['ba'])} | {pct(z['pair_same_rows']['accuracy'])} | {pct(z['pair_same_rows']['ba'])} | {pct(z['majority_accuracy'])} | {z['rescue']} | {z['break']} | {z['net_rescue']:+d} |")
    lines += ["","This result is stronger than the 2023-only FSMR8 choice because the selector explicitly requires cross-year development stability before opening 2025.",
              "The 2025 row remains retrospective transport evidence; it was not used to choose model, delta, coverage or state definition."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
