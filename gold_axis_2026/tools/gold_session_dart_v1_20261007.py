from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betainc
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_DART_V1_OUT";OUT.mkdir(exist_ok=True)

PATH_DEV=AX/"GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv"
STRUCT_DEV=AX/"GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PREDICTIONS_2026-10-07.csv"
PATH_25=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
STRUCT_25=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"

HAZARD=1.0/20.0
MAX_RUN=120
MIN_DISAGREEMENTS=8
ENTER_PROB=.90
ENTER_Q=.60
EXIT_PROB=.10
EXIT_Q=.40
A0=B0=1.0

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

def norm(q):
    q=q.copy()
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    if "end_utc" in q.columns:q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    return q

def load_ledger():
    pdv=norm(pd.read_csv(PATH_DEV))
    sdv=norm(pd.read_csv(STRUCT_DEV))
    sdv=sdv[sdv.model.eq("S14_A1_PLUS_1H_FULL")].copy()
    keys=["partition","window","label_date","start_utc","end_utc","year","y_up"]
    dev=pdv[keys+["p_up"]].rename(columns={"p_up":"p_path"}).merge(
        sdv[keys+["p_up"]].rename(columns={"p_up":"p_struct"}),
        on=keys,how="inner",validate="one_to_one"
    )

    p25=norm(pd.read_csv(PATH_25))
    p25=p25[p25.model.eq("PATH_GLOBAL_1H")].copy()
    s25=norm(pd.read_csv(STRUCT_25))
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

class BetaBernoulliBOCPD:
    def __init__(self):
        self.mass=np.array([1.0],float)
        self.alpha=np.array([A0],float)
        self.beta=np.array([B0],float)
        self.runlen=np.array([0],int)
        self.n=0

    def update(self,x):
        x=int(x)
        pred_old=np.where(
            x==1,self.alpha/(self.alpha+self.beta),self.beta/(self.alpha+self.beta)
        )
        prior_pred=.5
        growth=self.mass*(1-HAZARD)*pred_old
        cp=float(self.mass.sum()*HAZARD*prior_pred)
        mass=np.concatenate([[cp],growth])
        alpha=np.concatenate([[A0+x],self.alpha+x])
        beta=np.concatenate([[B0+(1-x)],self.beta+(1-x)])
        runlen=np.concatenate([[1],self.runlen+1])
        keep=runlen<=MAX_RUN
        mass=mass[keep];alpha=alpha[keep];beta=beta[keep];runlen=runlen[keep]
        s=float(mass.sum())
        if (not np.isfinite(s)) or s<=0:raise RuntimeError("BOCPD_MASS_COLLAPSE")
        self.mass=mass/s;self.alpha=alpha;self.beta=beta;self.runlen=runlen;self.n+=1

    def summary(self):
        means=self.alpha/(self.alpha+self.beta)
        q=float(np.sum(self.mass*means))
        prob=float(np.sum(self.mass*(1.0-betainc(self.alpha,self.beta,.5))))
        erun=float(np.sum(self.mass*self.runlen))
        cp=float(self.mass[self.runlen==1].sum()) if np.any(self.runlen==1) else 0.0
        return {
            "q_path":q,"prob_path_superior":prob,
            "expected_run_length":erun,"changepoint_mass":cp,
            "matured_disagreements":int(self.n)
        }

def disagreement_events(g):
    z=g.copy().sort_values(["end_utc","start_utc"]).reset_index(drop=True)
    s=(z.p_struct>=.5).astype(int);p=(z.p_path>=.5).astype(int)
    z["disagree"]=s.ne(p)
    d=z[z.disagree].copy()
    s2=(d.p_struct>=.5).astype(int);p2=(d.p_path>=.5).astype(int)
    d["struct_correct"]=s2.eq(d.y_up.astype(int))
    d["path_correct"]=p2.eq(d.y_up.astype(int))
    if not ((d.struct_correct.astype(int)+d.path_correct.astype(int))==1).all():
        raise RuntimeError("DISAGREEMENT_NOT_EXCLUSIVE")
    d["x_path_win"]=d.path_correct.astype(int)
    return d.reset_index(drop=True)

def run_window(g):
    g=g.sort_values("start_utc").reset_index(drop=True)
    d=disagreement_events(g)
    detector=BetaBernoulliBOCPD()
    state="STRUCTURAL_IRIS"
    processed=set()
    rows=[];switches=[]

    for r in g.itertuples(index=False):
        matured=d[
            (d.end_utc<=r.start_utc) &
            (d.start_utc<r.start_utc) &
            (~d.index.isin(processed))
        ].sort_values(["end_utc","start_utc"]).copy()

        for idx,ev in matured.iterrows():
            detector.update(int(ev.x_path_win))
            processed.add(int(idx))

        sm=detector.summary()
        old=state
        if sm["matured_disagreements"]>=MIN_DISAGREEMENTS:
            if state=="STRUCTURAL_IRIS" and sm["prob_path_superior"]>=ENTER_PROB and sm["q_path"]>=ENTER_Q:
                state="PATH_GLOBAL"
            elif state=="PATH_GLOBAL" and sm["prob_path_superior"]<=EXIT_PROB and sm["q_path"]<=EXIT_Q:
                state="STRUCTURAL_IRIS"

        if state!=old:
            switches.append({
                "partition":r.partition,"window":r.window,
                "start_utc":str(r.start_utc),"year":int(r.year),
                "from":old,"to":state,**sm
            })

        pout=float(r.p_path if state=="PATH_GLOBAL" else r.p_struct)
        rows.append({
            "partition":r.partition,"window":r.window,"label_date":r.label_date,
            "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),"y_up":int(r.y_up),
            "p_struct":float(r.p_struct),"p_path":float(r.p_path),
            "active_expert":state,"p_dart":pout,**sm
        })
    return pd.DataFrame(rows),pd.DataFrame(switches),d

def gate(pred,switches):
    reasons=[]
    for yr in [2023,2024]:
        z=pred[pred.year.eq(yr)]
        if z.empty:continue
        md=metric(z.y_up,z.p_dart);mb=metric(z.y_up,z.p_struct)
        if md["accuracy"]+0.01+1e-12<mb["accuracy"]:reasons.append(f"{yr}_ACC")
        if md["brier"]>mb["brier"]+.003+1e-12:reasons.append(f"{yr}_BRIER")
    z=pred[pred.year.isin([2023,2024])]
    if z.empty:return {"eligible":False,"reason":"NO_DEV"}
    md=metric(z.y_up,z.p_dart);mb=metric(z.y_up,z.p_struct)
    if md["balanced_accuracy"]+0.01+1e-12<mb["balanced_accuracy"]:reasons.append("DEV_BA")
    if min(md["up_recall"],md["down_recall"])<.30:reasons.append("RECALL_FLOOR")
    if switches.empty or switches[switches.year.le(2024)].empty:reasons.append("NO_SWITCH_BY_2024")
    return {
        "eligible":len(reasons)==0,
        "reason":"PASS" if not reasons else "|".join(reasons),
        "dev_dart":md,"dev_struct":mb
    }

def summarize(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        for m,c in [("STRUCTURAL_IRIS","p_struct"),("PATH_GLOBAL","p_path"),("DART","p_dart")]:
            rows.append({"period":period,"partition":part,"window":win,"model":m,**metric(g.y_up,g[c])})
    return pd.DataFrame(rows)

def main():
    ledger=load_ledger()
    dev_rows=[];dev_sw=[];dis_rows=[];gate_rows=[]

    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        dset=g[g.year.isin([2023,2024])].copy()
        pred,sw,dis=run_window(dset)
        dev_rows.append(pred)
        if not sw.empty:dev_sw.append(sw)
        if not dis.empty:
            dis=dis.copy();dis["partition_key"]=part;dis["window_key"]=win
            dis_rows.append(dis)
        gt=gate(pred,sw)
        gate_rows.append({
            "partition":part,"window":win,"eligible":gt["eligible"],"reason":gt["reason"],
            "dev_n":gt.get("dev_dart",{}).get("n",0),
            "dart_ba":gt.get("dev_dart",{}).get("balanced_accuracy",np.nan),
            "struct_ba":gt.get("dev_struct",{}).get("balanced_accuracy",np.nan),
            "dart_up_recall":gt.get("dev_dart",{}).get("up_recall",np.nan),
            "dart_down_recall":gt.get("dev_dart",{}).get("down_recall",np.nan),
            "switches_by_2024":int(0 if sw.empty else sw.year.le(2024).sum()),
            "matured_disagreements_end_2024":int(pred.matured_disagreements.iloc[-1]) if not pred.empty else 0,
        })

    dev=pd.concat(dev_rows,ignore_index=True)
    switches=pd.concat(dev_sw,ignore_index=True) if dev_sw else pd.DataFrame()
    disagreements=pd.concat(dis_rows,ignore_index=True) if dis_rows else pd.DataFrame()
    gate_df=pd.DataFrame(gate_rows)

    eligible={(r.partition,r.window) for r in gate_df.itertuples(index=False) if bool(r.eligible)}
    tr_rows=[];tr_sw=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        if (part,win) not in eligible:continue
        pred,sw,_=run_window(g[g.year.isin([2023,2024,2025])].copy())
        z=pred[pred.year.eq(2025)].copy()
        if not z.empty:tr_rows.append(z)
        if not sw.empty:tr_sw.append(sw)

    tr=pd.concat(tr_rows,ignore_index=True) if tr_rows else pd.DataFrame(columns=dev.columns)
    trswitch=pd.concat(tr_sw,ignore_index=True) if tr_sw else pd.DataFrame()

    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    gate_df.to_csv(OUT/"eligibility.csv",index=False)
    switches.to_csv(OUT/"dev_switches.csv",index=False)
    disagreements.to_csv(OUT/"dev_disagreements.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)
    trswitch.to_csv(OUT/"switches_through_2025.csv",index=False)

    summary={
        "status":"SESSION_DART_V1_COMPLETE",
        "rule":{
            "hazard":HAZARD,"max_run":MAX_RUN,"min_disagreements":MIN_DISAGREEMENTS,
            "enter_prob":ENTER_PROB,"enter_q":ENTER_Q,"exit_prob":EXIT_PROB,"exit_q":EXIT_Q
        },
        "experts":{"structural":"S14_A1_PLUS_1H_FULL","path":"PATH_GLOBAL_1H"},
        "development_gate":gate_df.to_dict("records"),
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "guardrails":[
            "State independent by partition/window.",
            "Detector updates only on matured exact-common expert disagreement rows.",
            "Only disagreement rows with end_utc <= current start_utc update BOCPD.",
            "Hazard and thresholds copied unchanged from H3 DART authority.",
            "2025 opened only for heads passing frozen pre-2025 gate.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION DART V1 — RESULT","",
           "## Pre-2025 eligibility","",
           "| Partition | Window | N | DART BA | Structural BA | UP recall | DOWN recall | Disagreements | Switches | Eligible | Reason |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate_df.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
                     f"{100*r.dart_ba:.2f}% | {100*r.struct_ba:.2f}% | "
                     f"{100*r.dart_up_recall:.2f}% | {100*r.dart_down_recall:.2f}% | "
                     f"{int(r.matured_disagreements_end_2024)} | {int(r.switches_by_2024)} | "
                     f"{r.eligible} | {r.reason} |")
    lines += ["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No DART head passed the pre-2025 gate; 2025 remained closed.")
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
