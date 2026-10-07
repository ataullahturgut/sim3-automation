from __future__ import annotations

# workflow trigger: TWIN V1 contract unchanged

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
AURORAP=AX/"tools"/"gold_session_aurora_v1_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
OUT=AX/"SESSION_TWIN_V1_OUT";OUT.mkdir(exist_ok=True)

KNN_K=25
MIN_MEMORY=40
UP_OVERRIDE=.70
DOWN_OVERRIDE=.30
REPS=["SHAPE24","SHAPE48","SHAPE_MULTI"]

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

aur=loadmod("session_aurora",AURORAP)
m05=loadmod("m05",M05P)

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

def paa(x,blocks):
    x=np.asarray(x,float)
    if len(x)%blocks!=0:raise ValueError((len(x),blocks))
    return x.reshape(blocks,len(x)//blocks).mean(axis=1)

def norm_cum(rets):
    r=np.asarray(rets,float)
    return np.cumsum(r)/(np.sqrt(np.sum(r*r))+1e-12)

def fresh_aurora():
    ledger=aur.sentry.load_ledger()
    rows=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        pred,_=aur.run_window(g[g.year.isin([2023,2024,2025])].copy())
        if not pred.empty:rows.append(pred)
    return pd.concat(rows,ignore_index=True).sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def attach_shapes(panel):
    x15=m05.load_xau15_extended()
    h=m05.load_xau1h(x15).copy().sort_values("available_at_utc").reset_index(drop=True)
    h["logp"]=np.log(h.value.astype(float))
    av=h.available_at_utc.astype("int64").to_numpy()
    logp=h.logp.to_numpy(float)
    rows=[];missing=[]
    for r in panel.itertuples(index=False):
        t=pd.Timestamp(r.start_utc)
        j=int(np.searchsorted(av,t.value,side="left")-1)
        if j<48:
            missing.append(str(t));continue
        vals=logp[j-48:j+1]
        if len(vals)!=49 or not np.isfinite(vals).all():
            missing.append(str(t));continue
        ret48=np.diff(vals)
        s24=paa(norm_cum(ret48[-24:]),8)
        s48=paa(norm_cum(ret48),12)
        row={k:getattr(r,k) for k in panel.columns}
        row["hourly_anchor_available"]=h.iloc[j].available_at_utc
        for i,v in enumerate(s24):row[f"s24_{i}"]=float(v)
        for i,v in enumerate(s48):row[f"s48_{i}"]=float(v)
        rows.append(row)
    q=pd.DataFrame(rows)
    if q.empty:raise RuntimeError("TWIN_NO_EMBEDDINGS")
    if not (q.hourly_anchor_available<q.start_utc).all():
        raise RuntimeError("TWIN_TIME_LEAK")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True),missing

def rep_cols(rep):
    c24=[f"s24_{i}" for i in range(8)]
    c48=[f"s48_{i}" for i in range(12)]
    if rep=="SHAPE24":return c24
    if rep=="SHAPE48":return c48
    if rep=="SHAPE_MULTI":return c24+c48
    raise KeyError(rep)

def local_probability(memory,row,rep):
    if len(memory)<MIN_MEMORY:return np.nan,0,np.nan
    cols=rep_cols(rep)
    X=memory[cols].astype(float).to_numpy()
    x=row[cols].astype(float).to_numpy()
    mu=X.mean(axis=0);sd=X.std(axis=0,ddof=0);sd=np.where(sd<1e-8,1.0,sd)
    Xz=(X-mu)/sd;xz=(x-mu)/sd
    dist=np.sqrt(np.sum((Xz-xz)**2,axis=1))
    k=min(KNN_K,len(memory))
    ix=np.argsort(dist)[:k];dk=dist[ix]
    med=float(np.median(dk));tau=med if med>1e-8 else 1.0
    w=np.exp(-dk/tau)
    y=memory.iloc[ix].y_up.to_numpy(float)
    return float(np.sum(w*y)/np.sum(w)),int(k),float(np.mean(dk))

def apply_rep(g,rep):
    g=g.sort_values("start_utc").reset_index(drop=True)
    rows=[]
    for _,r in g.iterrows():
        mem=g[(g.end_utc<=r.start_utc)&(g.start_utc<r.start_utc)].copy()
        p_local,nn,md=local_probability(mem,r,rep)
        pb=float(r.p_aurora);bd=int(pb>=.5)
        rescue=False;po=pb
        if np.isfinite(p_local):
            if bd==0 and p_local>=UP_OVERRIDE:
                rescue=True;po=float(p_local)
            elif bd==1 and p_local<=DOWN_OVERRIDE:
                rescue=True;po=float(p_local)
        od=int(po>=.5);actual=int(r.y_up)
        rows.append({
            "rep":rep,"partition":r.partition,"window":r.window,
            "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
            "year":int(r.year),"y_up":actual,
            "p_aurora":pb,"p_local":p_local,"p_twin":po,
            "aurora_dir":bd,"twin_dir":od,"override":bool(rescue),
            "rescue_correct":bool(rescue and bd!=actual and od==actual),
            "rescue_broken":bool(rescue and bd==actual and od!=actual),
            "nn":nn,"mean_nn_distance":md
        })
    return pd.DataFrame(rows)

def paired(z):
    ma=metric(z.y_up,z.p_aurora);mt=metric(z.y_up,z.p_twin)
    return ma,mt,{
        "override_n":int(z.override.sum()),
        "rescued":int(z.rescue_correct.sum()),
        "broken":int(z.rescue_broken.sum()),
        "net_rescue":int(z.rescue_correct.sum()-z.rescue_broken.sum())
    }

def select_rep(g):
    rows=[];ledgers={}
    for rep in REPS:
        led=apply_rep(g,rep);dev=led[led.year.isin([2023,2024])].copy()
        ledgers[rep]=led
        ma,mt,x=paired(dev)
        eligible=bool(
            x["override_n"]>=3 and x["net_rescue"]>0 and
            mt["balanced_accuracy"]+1e-12>=ma["balanced_accuracy"] and
            mt["accuracy"]+.005+1e-12>=ma["accuracy"] and
            mt["brier"]<=ma["brier"]+.0025+1e-12
        )
        rows.append({
            "rep":rep,"eligible":eligible,"dev_n":len(dev),
            "aurora_accuracy":ma["accuracy"],"twin_accuracy":mt["accuracy"],
            "aurora_ba":ma["balanced_accuracy"],"twin_ba":mt["balanced_accuracy"],
            "aurora_brier":ma["brier"],"twin_brier":mt["brier"],
            "twin_up_recall":mt["up_recall"],"twin_down_recall":mt["down_recall"],
            **x
        })
    tab=pd.DataFrame(rows)
    elig=tab[tab.eligible].copy()
    if elig.empty:return tab,None,ledgers
    order={"SHAPE24":0,"SHAPE48":1,"SHAPE_MULTI":2}
    elig["simplicity"]=elig.rep.map(order)
    elig=elig.sort_values(["twin_ba","twin_accuracy","twin_brier","simplicity"],
                          ascending=[False,False,True,True])
    return tab,str(elig.iloc[0].rep),ledgers

def summarize(z,period):
    rows=[]
    for (part,win),g in z.groupby(["partition","window"],sort=True):
        ma,mt,x=paired(g)
        rows.append({
            "period":period,"partition":part,"window":win,"rep":g.rep.iloc[0],**x,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"twin_{k}":v for k,v in mt.items()}
        })
    return pd.DataFrame(rows)

def main():
    panel,missing=attach_shapes(fresh_aurora())
    selections=[];chosen={};dev_parts=[];tr_parts=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        tab,rep,ledgers=select_rep(g)
        for r in tab.to_dict("records"):selections.append({"partition":part,"window":win,**r})
        if rep is None:continue
        chosen[(part,win)]=rep
        led=ledgers[rep]
        dev_parts.append(led[led.year.isin([2023,2024])].copy())
        tr_parts.append(led[led.year.eq(2025)].copy())

    sel=pd.DataFrame(selections)
    dev=pd.concat(dev_parts,ignore_index=True) if dev_parts else pd.DataFrame()
    tr=pd.concat(tr_parts,ignore_index=True) if tr_parts else pd.DataFrame()

    panel.to_csv(OUT/"shape_panel.csv",index=False)
    sel.to_csv(OUT/"selection_grid.csv",index=False)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    if not dev.empty:summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"dev_metrics.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_TWIN_V1_COMPLETE",
        "rule":{"k":KNN_K,"min_memory":MIN_MEMORY,"up_override":UP_OVERRIDE,"down_override":DOWN_OVERRIDE},
        "selected_heads":[{"partition":p,"window":w,"rep":rep} for (p,w),rep in sorted(chosen.items())],
        "selection_grid":sel.to_dict("records"),
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "embedding_missing_rows":len(missing),
        "guardrails":[
            "Same-window matured analogue memory only.",
            "Hourly path strictly available before session start.",
            "Representation selected only on 2023-2024.",
            "k and 0.70/0.30 thresholds frozen.",
            "2025 transport only; no retuning.",
            "2026 unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION TWIN V1 — RESULT","",
           "## Development representation selection","",
           "| Partition | Window | Rep | N | AURORA BA | TWIN BA | TWIN UP | TWIN DOWN | Overrides | Rescue | Break | Net | Eligible |",
           "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in sel.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {r.rep} | {int(r.dev_n)} | "
            f"{100*r.aurora_ba:.2f}% | {100*r.twin_ba:.2f}% | "
            f"{100*r.twin_up_recall:.2f}% | {100*r.twin_down_recall:.2f}% | "
            f"{int(r.override_n)} | {int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} | {r.eligible} |"
        )
    lines+=["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No TWIN head passed development; 2025 remained closed.")
    else:
        tm=summarize(tr,"FROZEN_2025")
        lines+=["| Partition | Window | Rep | N | AURORA BA | TWIN BA | TWIN UP | TWIN DOWN | AURORA Brier | TWIN Brier | Overrides | Net rescue |",
                "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {r.rep} | {int(r.twin_n)} | "
                f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.twin_balanced_accuracy:.2f}% | "
                f"{100*r.twin_up_recall:.2f}% | {100*r.twin_down_recall:.2f}% | "
                f"{r.aurora_brier:.4f} | {r.twin_brier:.4f} | "
                f"{int(r.override_n)} | {int(r.net_rescue):+d} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
