from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
SENTRYP=AX/"tools"/"gold_session_sentry_v1_20261007.py"
DARTP=AX/"tools"/"gold_session_dart_v1_20261007.py"
OUT=AX/"SESSION_AURORA_V1_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

sentry=loadmod("session_sentry",SENTRYP)
dart=loadmod("session_dart",DARTP)

PAIR_WINDOW=63
MIN_MATURED_PAIR=42
ENTER_NET_RESCUE=3
MIN_DISAGREEMENTS=8
EXIT_PROB=.10
EXIT_Q=.40

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

def run_window(g):
    g=g.sort_values("start_utc").reset_index(drop=True)
    disagreements=dart.disagreement_events(g)
    detector=dart.BetaBernoulliBOCPD()
    processed=set()
    state="STRUCTURAL_IRIS"
    rows=[];switches=[]

    for r in g.itertuples(index=False):
        matured_pairs=g[
            (g.end_utc<=r.start_utc)&
            (g.start_utc<r.start_utc)
        ].tail(PAIR_WINDOW).copy()

        if len(matured_pairs):
            y=matured_pairs.y_up.to_numpy(int)
            sp=(matured_pairs.p_struct.to_numpy(float)>=.5).astype(int)
            pp=(matured_pairs.p_path.to_numpy(float)>=.5).astype(int)
            s_ok=sp==y;p_ok=pp==y
            adv=((~s_ok)&p_ok).astype(int)-(s_ok&(~p_ok)).astype(int)
            net=int(adv.sum())
            rescues=int(((~s_ok)&p_ok).sum())
            breaks=int((s_ok&(~p_ok)).sum())
        else:
            net=rescues=breaks=0

        matured_dis=disagreements[
            (disagreements.end_utc<=r.start_utc)&
            (disagreements.start_utc<r.start_utc)&
            (~disagreements.index.isin(processed))
        ].sort_values(["end_utc","start_utc"]).copy()

        for idx,ev in matured_dis.iterrows():
            detector.update(int(ev.x_path_win))
            processed.add(int(idx))

        ds=detector.summary()
        old=state

        if state=="STRUCTURAL_IRIS":
            if len(matured_pairs)>=MIN_MATURED_PAIR and net>=ENTER_NET_RESCUE:
                state="PATH_GLOBAL"
        else:
            if (
                ds["matured_disagreements"]>=MIN_DISAGREEMENTS
                and ds["prob_path_superior"]<=EXIT_PROB
                and ds["q_path"]<=EXIT_Q
            ):
                state="STRUCTURAL_IRIS"

        if state!=old:
            switches.append({
                "partition":r.partition,"window":r.window,
                "start_utc":str(r.start_utc),"year":int(r.year),
                "from":old,"to":state,
                "matured_pair_n":int(len(matured_pairs)),
                "net_rescue_63":net,
                "matured_disagreements":int(ds["matured_disagreements"]),
                "q_path":float(ds["q_path"]),
                "prob_path_superior":float(ds["prob_path_superior"])
            })

        pout=float(r.p_path if state=="PATH_GLOBAL" else r.p_struct)
        rows.append({
            "partition":r.partition,"window":r.window,"label_date":r.label_date,
            "start_utc":r.start_utc,"end_utc":r.end_utc,
            "year":int(r.year),"y_up":int(r.y_up),
            "p_struct":float(r.p_struct),"p_path":float(r.p_path),
            "p_aurora":pout,"active_expert":state,
            "matured_pair_n":int(len(matured_pairs)),
            "net_rescue_63":net,"rescues_63":rescues,"breaks_63":breaks,
            **ds
        })
    return pd.DataFrame(rows),pd.DataFrame(switches)

def gate(pred,switches):
    reasons=[]
    for yr in [2023,2024]:
        z=pred[pred.year.eq(yr)]
        if z.empty:continue
        ma=metric(z.y_up,z.p_aurora);mb=metric(z.y_up,z.p_struct)
        if ma["accuracy"]+0.01+1e-12<mb["accuracy"]:reasons.append(f"{yr}_ACC")
        if ma["brier"]>mb["brier"]+.003+1e-12:reasons.append(f"{yr}_BRIER")
    z=pred[pred.year.isin([2023,2024])]
    if z.empty:return {"eligible":False,"reason":"NO_DEV"}
    ma=metric(z.y_up,z.p_aurora);mb=metric(z.y_up,z.p_struct)
    if ma["balanced_accuracy"]+0.01+1e-12<mb["balanced_accuracy"]:reasons.append("DEV_BA")
    if min(ma["up_recall"],ma["down_recall"])<.30:reasons.append("RECALL_FLOOR")
    if switches.empty or switches[switches.year.le(2024)].empty:reasons.append("NO_SWITCH_BY_2024")
    return {
        "eligible":len(reasons)==0,
        "reason":"PASS" if not reasons else "|".join(reasons),
        "dev_aurora":ma,"dev_struct":mb
    }

def summarize(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        for m,c in [("STRUCTURAL_IRIS","p_struct"),("PATH_GLOBAL","p_path"),("AURORA","p_aurora")]:
            rows.append({"period":period,"partition":part,"window":win,"model":m,**metric(g.y_up,g[c])})
    return pd.DataFrame(rows)

def main():
    ledger=sentry.load_ledger()
    dev_rows=[];dev_sw=[];gates=[]

    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        pred,sw=run_window(g[g.year.isin([2023,2024])].copy())
        dev_rows.append(pred)
        if not sw.empty:dev_sw.append(sw)
        gt=gate(pred,sw)
        gates.append({
            "partition":part,"window":win,
            "eligible":gt["eligible"],"reason":gt["reason"],
            "dev_n":gt.get("dev_aurora",{}).get("n",0),
            "aurora_ba":gt.get("dev_aurora",{}).get("balanced_accuracy",np.nan),
            "struct_ba":gt.get("dev_struct",{}).get("balanced_accuracy",np.nan),
            "aurora_up_recall":gt.get("dev_aurora",{}).get("up_recall",np.nan),
            "aurora_down_recall":gt.get("dev_aurora",{}).get("down_recall",np.nan),
            "switches_by_2024":int(0 if sw.empty else sw.year.le(2024).sum())
        })

    dev=pd.concat(dev_rows,ignore_index=True)
    switches=pd.concat(dev_sw,ignore_index=True) if dev_sw else pd.DataFrame()
    gate_df=pd.DataFrame(gates)
    eligible={(r.partition,r.window) for r in gate_df.itertuples(index=False) if bool(r.eligible)}

    tr_rows=[];tr_sw=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        if (part,win) not in eligible:continue
        pred,sw=run_window(g[g.year.isin([2023,2024,2025])].copy())
        z=pred[pred.year.eq(2025)].copy()
        if not z.empty:tr_rows.append(z)
        if not sw.empty:tr_sw.append(sw)

    tr=pd.concat(tr_rows,ignore_index=True) if tr_rows else pd.DataFrame(columns=dev.columns)
    trswitch=pd.concat(tr_sw,ignore_index=True) if tr_sw else pd.DataFrame()

    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    gate_df.to_csv(OUT/"eligibility.csv",index=False)
    switches.to_csv(OUT/"dev_switches.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)
    trswitch.to_csv(OUT/"switches_through_2025.csv",index=False)

    summary={
        "status":"SESSION_AURORA_V1_COMPLETE",
        "rule":{
            "fast_entry":{"pair_window":PAIR_WINDOW,"min_matured_pair":MIN_MATURED_PAIR,"net_rescue_threshold":ENTER_NET_RESCUE},
            "slow_exit":{"min_disagreements":MIN_DISAGREEMENTS,"prob_path_superior_max":EXIT_PROB,"q_path_max":EXIT_Q}
        },
        "experts":{"structural":"S14_A1_PLUS_1H_FULL","path":"PATH_GLOBAL_1H"},
        "development_gate":gate_df.to_dict("records"),
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "guardrails":[
            "AURORA introduces no new fitted threshold.",
            "Fast entry is frozen SENTRY evidence; slow exit is frozen DART evidence.",
            "All evidence is recomputed causally from corrected session expert rows.",
            "2025 opened only for heads passing the frozen pre-2025 gate.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION AURORA V1 — RESULT","",
           "## Pre-2025 eligibility","",
           "| Partition | Window | N | AURORA BA | Structural BA | UP recall | DOWN recall | Switches | Eligible | Reason |",
           "|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate_df.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
                     f"{100*r.aurora_ba:.2f}% | {100*r.struct_ba:.2f}% | "
                     f"{100*r.aurora_up_recall:.2f}% | {100*r.aurora_down_recall:.2f}% | "
                     f"{int(r.switches_by_2024)} | {r.eligible} | {r.reason} |")
    lines += ["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No AURORA head passed the pre-2025 gate; 2025 remained closed.")
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
