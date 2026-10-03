from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss

import gold_h3_iris_v1 as iris
import gold_h3_twin_v1 as twin
import gold_h3_prism_v1 as prism

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_recent_clean_sweep_out"))
OUT.mkdir(parents=True,exist_ok=True)
CLEAN_AURORA=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"

EXISTING={
 "RIFT":("GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv","p_rift"),
 "TURN":("GOLD_H3_CLEAN_TURN_PREDICTIONS_2026-10-03.csv","p_turn"),
 "VEGA":("GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv","p_vega"),
 "OPAL":("GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv","p_opal"),
 "HELIOS_V1_HARD":("GOLD_H3_CLEAN_HELIOS_V1_PREDICTIONS_2026-10-03.csv","p_helios_hard"),
 "HELIOS_V1_SOFT":("GOLD_H3_CLEAN_HELIOS_V1_PREDICTIONS_2026-10-03.csv","p_helios_soft"),
 "HELIOS_V2":("GOLD_H3_CLEAN_HELIOS_V2_PREDICTIONS_2026-10-03.csv","p_helios_v2"),
 "HELIOS_V3_GT":("GOLD_H3_CLEAN_HELIOS_V3_GT_PREDICTIONS_2026-10-03.csv","p_helios_v3_gt"),
 "HELIOS_V4_RGE":("GOLD_H3_CLEAN_HELIOS_V4_RGE_PREDICTIONS_2026-10-03.csv","p_helios_v4_rge"),
 "HELIOS_V5_DCE":("GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv","p_helios_v5_dce"),
}

def metric(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); d=(p>=.5).astype(int)
    pos=y==1; neg=y==0
    return {
      "n":len(y),"accuracy":float((d==y).mean()),
      "balanced_accuracy":float(.5*((d[pos]==1).mean()+(d[neg]==0).mean())),
      "brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1]))
    }

def rows_for(df,col,name):
    out=[]
    for label,years in [("2023",[2023]),("2024",[2024]),("2025",[2025]),("2026",[2026]),("2025-2026",[2025,2026])]:
        z=df[df.year.isin(years)]
        if len(z): out.append({"model":name,"period":label,**metric(z.y_up,z[col])})
    return out

def cache_hourly():
    hist=iris.load_neon_hourly(); succ,calls=iris.fetch_extension()
    _,bridge=iris.bridge_metrics(hist,succ)
    if not bridge["pass"]: raise RuntimeError(bridge)
    iris.load_neon_hourly=lambda:hist.copy()
    iris.fetch_extension=lambda:(succ.copy(),calls)
    return bridge,calls

def run_twin():
    twin.AURORA=CLEAN_AURORA
    base=pd.read_csv(CLEAN_AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]: base[c]=pd.to_datetime(base[c])
    hourly,bridge,calls=twin.fetch_hourly()
    emb=twin.build_shape_embeddings(hourly,base.feature_cutoff_date.unique())
    panel=base.merge(emb,on="feature_cutoff_date",how="inner",validate="one_to_one")
    ledgers={rep:twin.apply_rep(panel,rep) for rep in twin.REPS}
    grid,sel=twin.selection(ledgers); grid.to_csv(OUT/"clean_twin_selection.csv",index=False)
    if sel is None: return [],{"status":"NO_ELIGIBLE_REP","selected":None}
    led=ledgers[sel]; led.to_csv(OUT/"clean_twin_predictions.csv",index=False)
    full=twin.period_rows(led); ok,checks,agg,res=twin.confirmation(full)
    return rows_for(led,"p_twin","TWIN"),{"status":"MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL","selected":sel,"checks":checks}

def run_prism():
    prism.AURORA=CLEAN_AURORA
    panel,bridge,calls=prism.build_panel()
    preds={lam:prism.walk_forward(panel,lam) for lam in prism.LAMBDA_GRID}
    grid,sel=prism.select_model(preds); grid.to_csv(OUT/"clean_prism_selection.csv",index=False)
    if sel is None: return [],{"status":"NO_ELIGIBLE_LAMBDA","selected_lambda":None}
    led=preds[sel]; led.to_csv(OUT/"clean_prism_predictions.csv",index=False)
    full=prism.score_periods(led); ok,checks,agg=prism.confirmation(full)
    return rows_for(led,"p_prism","PRISM"),{"status":"MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL","selected_lambda":sel,"checks":checks}

def main():
    bridge,calls=cache_hourly()
    rows=[]
    aur=pd.read_csv(CLEAN_AURORA); rows+=rows_for(aur,"p_aurora","AURORA")
    tr,tmeta=run_twin(); rows+=tr
    pr,pmeta=run_prism(); rows+=pr
    for name,(fn,col) in EXISTING.items():
        g=pd.read_csv(ROOT/"gold_axis_2026"/fn); rows+=rows_for(g,col,name)
    tab=pd.DataFrame(rows); tab.to_csv(OUT/"recent_clean_sweep_metrics.csv",index=False)
    r26=tab[tab.period=="2026"].sort_values(["accuracy","balanced_accuracy","brier","logloss"],ascending=[False,False,True,True]).reset_index(drop=True)
    r26.insert(0,"rank",np.arange(1,len(r26)+1)); r26.to_csv(OUT/"recent_clean_2026_ranking.csv",index=False)
    r2526=tab[tab.period=="2025-2026"].sort_values(["accuracy","balanced_accuracy","brier","logloss"],ascending=[False,False,True,True]).reset_index(drop=True)
    r2526.insert(0,"rank",np.arange(1,len(r2526)+1)); r2526.to_csv(OUT/"recent_clean_2025_2026_ranking.csv",index=False)
    summ={"schema":"GOLD_H3_RECENT_CLEAN_SWEEP_V1","scope":"AURORA and post-AURORA improvement lineage","hourly_bridge":bridge,"api_calls":calls,"twin":tmeta,"prism":pmeta,"ranking_2026":r26.to_dict("records"),"ranking_2025_2026":r2526.to_dict("records")}
    (OUT/"summary.json").write_text(json.dumps(summ,indent=2,default=str)+"\n")
    lines=["# GOLD H3 RECENT CLEAN SWEEP — RESULT","",f"**TWIN:** {tmeta}",f"**PRISM:** {pmeta}","","## 2026","",
      "| Rank | Model | Acc | BA | Brier | Logloss |","|---:|---|---:|---:|---:|---:|"]
    for r in r26.itertuples(): lines.append(f"| {r.rank} | {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    lines+=["","## 2025-2026","","| Rank | Model | Acc | BA | Brier | Logloss |","|---:|---|---:|---:|---:|---:|"]
    for r in r2526.itertuples(): lines.append(f"| {r.rank} | {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    (OUT/"RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"RESULT.md").read_text())
if __name__=="__main__": main()
