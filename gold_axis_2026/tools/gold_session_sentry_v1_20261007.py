from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_SENTRY_V1_OUT";OUT.mkdir(exist_ok=True)

PATH_DEV=AX/"GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv"
STRUCT_DEV=AX/"GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PREDICTIONS_2026-10-07.csv"
PATH_25=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
STRUCT_25=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"

WINDOW=63
MIN_MATURED=42
ENTER_PATH=3
EXIT_PATH=0

def metric(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "up_actual":int((y==1).sum()),
        "up_correct":int(((y==1)&(pred==1)).sum()),
        "down_actual":int((y==0).sum()),
        "down_correct":int(((y==0)&(pred==0)).sum()),
    }

def norm_dates(q):
    q=q.copy()
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    if "end_utc" in q.columns:
        q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    return q

def load_ledger():
    pdv=norm_dates(pd.read_csv(PATH_DEV))
    sdv=norm_dates(pd.read_csv(STRUCT_DEV))
    sdv=sdv[sdv.model.eq("S14_A1_PLUS_1H_FULL")].copy()

    keys=["partition","window","label_date","start_utc","end_utc","year","y_up"]
    dev=pdv[keys+["p_up"]].rename(columns={"p_up":"p_path"}).merge(
        sdv[keys+["p_up"]].rename(columns={"p_up":"p_struct"}),
        on=keys,how="inner",validate="one_to_one"
    )

    p25=norm_dates(pd.read_csv(PATH_25))
    p25=p25[p25.model.eq("PATH_GLOBAL_1H")].copy()
    s25=norm_dates(pd.read_csv(STRUCT_25))
    s25=s25[s25.model.eq("S14_A1_PLUS_1H_FULL")].copy()

    keys25=["partition","window","label_date","start_utc","y_up"]
    y25=p25[keys25+["p_up"]].rename(columns={"p_up":"p_path"}).merge(
        s25[keys25+["end_utc","year","p_up"]].rename(columns={"p_up":"p_struct"}),
        on=keys25,how="inner",validate="one_to_one"
    )
    y25["year"]=2025

    q=pd.concat([
        dev[["partition","window","label_date","start_utc","end_utc","year","y_up","p_path","p_struct"]],
        y25[["partition","window","label_date","start_utc","end_utc","year","y_up","p_path","p_struct"]],
    ],ignore_index=True)
    q=q.drop_duplicates(["partition","window","start_utc"],keep="last")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def run_window(g,through_2025=True):
    g=g.sort_values("start_utc").reset_index(drop=True)
    state="STRUCTURAL_IRIS"
    rows=[];switches=[]
    for r in g.itertuples(index=False):
        if (not through_2025) and int(r.year)>2024:
            break
        matured=g[
            (g.end_utc<=r.start_utc) &
            (g.start_utc<r.start_utc)
        ].tail(WINDOW).copy()

        if len(matured):
            y=matured.y_up.to_numpy(int)
            s=(matured.p_struct.to_numpy(float)>=.5).astype(int)
            p=(matured.p_path.to_numpy(float)>=.5).astype(int)
            s_ok=s==y;p_ok=p==y
            adv=((~s_ok)&p_ok).astype(int)-(s_ok&(~p_ok)).astype(int)
            net=int(adv.sum())
            rescues=int(((~s_ok)&p_ok).sum())
            breaks=int((s_ok&(~p_ok)).sum())
        else:
            net=rescues=breaks=0

        old=state
        if len(matured)>=MIN_MATURED:
            if state=="STRUCTURAL_IRIS" and net>=ENTER_PATH:
                state="PATH_GLOBAL"
            elif state=="PATH_GLOBAL" and net<=EXIT_PATH:
                state="STRUCTURAL_IRIS"

        if state!=old:
            switches.append({
                "partition":r.partition,"window":r.window,
                "start_utc":str(r.start_utc),
                "year":int(r.year),"from":old,"to":state,
                "matured_n":int(len(matured)),
                "net_rescue_63":net,"rescues_63":rescues,"breaks_63":breaks
            })

        pout=float(r.p_path if state=="PATH_GLOBAL" else r.p_struct)
        rows.append({
            "partition":r.partition,"window":r.window,"label_date":r.label_date,
            "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),"y_up":int(r.y_up),
            "p_struct":float(r.p_struct),"p_path":float(r.p_path),
            "active_expert":state,"p_sentry":pout,
            "matured_pair_n":int(len(matured)),
            "net_rescue_63":net,"rescues_63":rescues,"breaks_63":breaks,
        })
    return pd.DataFrame(rows),pd.DataFrame(switches)

def gate_window(pred,switches):
    out={"eligible":True,"reasons":[]}
    for yr in [2023,2024]:
        z=pred[pred.year.eq(yr)]
        if z.empty:
            continue
        ms=metric(z.y_up,z.p_sentry);mb=metric(z.y_up,z.p_struct)
        if ms["accuracy"]+0.01+1e-12<mb["accuracy"]:
            out["eligible"]=False;out["reasons"].append(f"{yr}_ACC")
        if ms["brier"]>mb["brier"]+0.003+1e-12:
            out["eligible"]=False;out["reasons"].append(f"{yr}_BRIER")
    z=pred[pred.year.isin([2023,2024])]
    if z.empty:
        out["eligible"]=False;out["reasons"].append("NO_DEV")
        return out
    ms=metric(z.y_up,z.p_sentry);mb=metric(z.y_up,z.p_struct)
    if ms["balanced_accuracy"]+0.01+1e-12<mb["balanced_accuracy"]:
        out["eligible"]=False;out["reasons"].append("DEV_BA")
    if min(ms["up_recall"],ms["down_recall"])<.30:
        out["eligible"]=False;out["reasons"].append("RECALL_FLOOR")
    if switches[switches.year.le(2024)].empty:
        out["eligible"]=False;out["reasons"].append("NO_SWITCH_BY_2024")
    out["reasons"]="PASS" if out["eligible"] else "|".join(out["reasons"])
    out["dev_sentry"]=ms;out["dev_struct"]=mb
    return out

def summarize(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        for model,col in [("STRUCTURAL_IRIS","p_struct"),("PATH_GLOBAL","p_path"),("SENTRY","p_sentry")]:
            m=metric(g.y_up,g[col])
            rows.append({"period":period,"partition":part,"window":win,"model":model,**m})
    return pd.DataFrame(rows)

def main():
    ledger=load_ledger()
    all_dev=[];all_sw=[];gates=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        dev,sw=run_window(g[g.year.isin([2023,2024])],through_2025=False)
        if not dev.empty:all_dev.append(dev)
        if not sw.empty:all_sw.append(sw)
        gt=gate_window(dev,sw if not sw.empty else pd.DataFrame(columns=["year"]))
        gates.append({
            "partition":part,"window":win,"eligible":gt["eligible"],"reason":gt["reasons"],
            "dev_n":gt.get("dev_sentry",{}).get("n",0),
            "sentry_ba":gt.get("dev_sentry",{}).get("balanced_accuracy",np.nan),
            "struct_ba":gt.get("dev_struct",{}).get("balanced_accuracy",np.nan),
            "sentry_up_recall":gt.get("dev_sentry",{}).get("up_recall",np.nan),
            "sentry_down_recall":gt.get("dev_sentry",{}).get("down_recall",np.nan),
            "switches_by_2024":int(0 if sw.empty else sw.year.le(2024).sum()),
        })

    dev=pd.concat(all_dev,ignore_index=True)
    switches=pd.concat(all_sw,ignore_index=True) if all_sw else pd.DataFrame()
    gate=pd.DataFrame(gates)

    transport=[];transport_sw=[]
    eligible={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        if (part,win) not in eligible:continue
        run,sw=run_window(g[g.year.isin([2023,2024,2025])],through_2025=True)
        z=run[run.year.eq(2025)].copy()
        if not z.empty:transport.append(z)
        if not sw.empty:transport_sw.append(sw)

    tr=pd.concat(transport,ignore_index=True) if transport else pd.DataFrame(columns=dev.columns)
    trsw=pd.concat(transport_sw,ignore_index=True) if transport_sw else pd.DataFrame()

    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    gate.to_csv(OUT/"eligibility.csv",index=False)
    switches.to_csv(OUT/"dev_switches.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)
    trsw.to_csv(OUT/"continuous_switches_through_2025.csv",index=False)

    summary={
        "status":"SESSION_SENTRY_V1_COMPLETE",
        "rule":{"window":WINDOW,"min_matured":MIN_MATURED,"enter_path":ENTER_PATH,"exit_path":EXIT_PATH},
        "experts":{"structural":"S14_A1_PLUS_1H_FULL","path":"PATH_GLOBAL_1H"},
        "development_gate":gate.to_dict("records"),
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "transport_2025_metrics":(
            summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else []
        ),
        "guardrails":[
            "State is independent by partition/window.",
            "Only exact common expert rows are used.",
            "Paired correctness uses only rows with end_utc <= current start_utc.",
            "SENTRY thresholds are copied unchanged from H3 authority; no session threshold search.",
            "2025 is opened only for heads passing the frozen 2023-2024 gate.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION SENTRY V1 — RESULT","",
           "## Pre-2025 eligibility","",
           "| Partition | Window | N | SENTRY BA | Structural BA | UP recall | DOWN recall | Switches | Eligible | Reason |",
           "|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
                     f"{100*r.sentry_ba:.2f}% | {100*r.struct_ba:.2f}% | "
                     f"{100*r.sentry_up_recall:.2f}% | {100*r.sentry_down_recall:.2f}% | "
                     f"{int(r.switches_by_2024)} | {r.eligible} | {r.reason} |")
    lines += ["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No SENTRY head passed the pre-2025 gate; 2025 remained closed.")
    else:
        tm=summarize(tr,"FROZEN_2025")
        lines += ["| Model | Partition | Window | N | Accuracy | BA | UP correct/actual | DOWN correct/actual | Brier |",
                  "|---|---|---|---:|---:|---:|---:|---:|---:|"]
        for r in tm.sort_values(["partition","window","model"]).itertuples(index=False):
            lines.append(f"| {r.model} | {r.partition} | {r.window} | {int(r.n)} | "
                         f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                         f"{int(r.up_correct)}/{int(r.up_actual)} | "
                         f"{int(r.down_correct)}/{int(r.down_actual)} | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
