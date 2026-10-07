from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
LED=AX/"GOLD_SESSION_WINDOW_EVIDENCE_EVALUATION_LEDGER_2026-10-07.csv.gz"
RFR=AX/"GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv"
OUTR=AX/"GOLD_EXECUTION_RFR_SESSION_RESCUE_RESULT_2026-10-07.md"
OUTJ=AX/"GOLD_EXECUTION_RFR_SESSION_RESCUE_SUMMARY_2026-10-07.json"
OUTC=AX/"GOLD_EXECUTION_RFR_SESSION_RESCUE_ROWS_2026-10-07.csv"

MODELS=["PATH_GLOBAL_1H","STRUCTURAL_IRIS_1H"]
SESSIONS=[("WGC_2026_NY3","US","WGC_US"),("SOBTI_5_ET","NY_LONDON_LIT","SOBTI_NYL")]
GATES=["RFR_ALWAYS","WGC_BOTH_RFR","SOBTI_BOTH_RFR","ANY_SESSION_BOTH_RFR","THREE_OF_FOUR_RFR"]

def metric(y,p):
    y=np.asarray(y,int);p=np.asarray(p,int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    return dict(n=len(y),accuracy=float(accuracy_score(y,p)),ba=float(balanced_accuracy_score(y,p)),
                up_recall=float(recall_score(y,p,pos_label=1,zero_division=0)),
                down_recall=float(recall_score(y,p,pos_label=0,zero_division=0)),
                tn=tn,fp=fp,fn=fn,tp=tp)

def make_context():
    l=pd.read_csv(LED,compression="gzip")
    l["start_utc"]=pd.to_datetime(l.start_utc,utc=True)
    l=l[l.model.isin(MODELS)].copy()
    l["tr_date"]=(l.start_utc+pd.Timedelta(hours=3)).dt.date
    keep=[]
    for part,win,label in SESSIONS:
        z=l[(l.partition==part)&(l.window==win)].copy()
        # 17:00 TRT == 14:00 UTC. Both chosen session origins must be known by then.
        secs=z.start_utc.dt.hour*60+z.start_utc.dt.minute
        assert (secs<=14*60).all(), f"LATE_SESSION_ORIGIN:{part}:{win}"
        for model in MODELS:
            g=z[z.model==model][["tr_date","p_up"]].copy()
            g["ctx"] = label+"_"+("PATH" if model=="PATH_GLOBAL_1H" else "STRUCT")
            keep.append(g)
    q=pd.concat(keep,ignore_index=True)
    if q.duplicated(["tr_date","ctx"]).any():
        raise RuntimeError("DUP_CONTEXT")
    return q.pivot(index="tr_date",columns="ctx",values="p_up").reset_index()

def decision(row,gate):
    rfr=int(row.rule_pred); pair=int(row.pair_pred)
    if pair==rfr: return pair,False
    signs={}
    for c in ["WGC_US_PATH","WGC_US_STRUCT","SOBTI_NYL_PATH","SOBTI_NYL_STRUCT"]:
        v=row.get(c,np.nan)
        signs[c]=None if pd.isna(v) else int(float(v)>=.5)
    def both(prefix):
        a=signs.get(prefix+"_PATH");b=signs.get(prefix+"_STRUCT")
        return a is not None and b is not None and a==rfr and b==rfr
    support=sum(v==rfr for v in signs.values() if v is not None)
    avail=sum(v is not None for v in signs.values())
    use=False
    if gate=="RFR_ALWAYS": use=True
    elif gate=="WGC_BOTH_RFR": use=both("WGC_US")
    elif gate=="SOBTI_BOTH_RFR": use=both("SOBTI_NYL")
    elif gate=="ANY_SESSION_BOTH_RFR": use=both("WGC_US") or both("SOBTI_NYL")
    elif gate=="THREE_OF_FOUR_RFR": use=(avail>=3 and support>=3)
    else: raise KeyError(gate)
    return (rfr if use else pair),use

def evaluate(g,gate):
    x=g.copy()
    tmp=x.apply(lambda r:decision(r,gate),axis=1,result_type="expand")
    x["final_pred"]=tmp[0].astype(int);x["override"]=tmp[1].astype(bool)
    x["pair_correct"]=x.pair_pred.astype(int).eq(x.y.astype(int))
    x["final_correct"]=x.final_pred.astype(int).eq(x.y.astype(int))
    active=x[x.override]
    rescue=int((~active.pair_correct & active.final_correct).sum())
    brk=int((active.pair_correct & ~active.final_correct).sum())
    m=metric(x.y,x.final_pred)
    base=metric(x.y,x.pair_pred)
    return x,dict(**m,base_accuracy=base["accuracy"],base_ba=base["ba"],
                  overrides=int(x.override.sum()),rescue=rescue,breaks=brk,net_rescue=rescue-brk,
                  exact_override_p=float(binomtest(rescue,rescue+brk,.5).pvalue) if rescue+brk else 1.0)

def main():
    r=pd.read_csv(RFR,parse_dates=["date"])
    r=r[r.eligible_nomacro.astype(str).str.lower().eq("true")].copy()
    r["tr_date"]=r.date.dt.date
    ctx=make_context()
    q=r.merge(ctx,on="tr_date",how="left",validate="one_to_one")
    # only RFR eligible rows; missing session contexts simply cannot activate context-specific gates.
    rows=[];detail=[]
    for gate in GATES:
        for label,mask in [("2023",q.year.eq(2023)),("2024",q.year.eq(2024)),
                           ("DEV",q.year.isin([2023,2024])),("2025",q.year.eq(2025))]:
            x,z=evaluate(q[mask],gate)
            rows.append({"gate":gate,"period":label,**z})
            if label in ["DEV","2025"]:
                y=x.copy();y["gate"]=gate;y["period_eval"]=label;detail.append(y)
    met=pd.DataFrame(rows)

    # Development-only selector: require nonnegative net rescue in each dev year,
    # >=5 overrides pooled DEV, then maximize minimum yearly net rescue, pooled BA gain, then fewer overrides.
    ranks=[]
    for gate in GATES:
        a=met[(met.gate==gate)&(met.period=="2023")].iloc[0]
        b=met[(met.gate==gate)&(met.period=="2024")].iloc[0]
        d=met[(met.gate==gate)&(met.period=="DEV")].iloc[0]
        elig=bool(a.net_rescue>=0 and b.net_rescue>=0 and d.overrides>=5)
        score=min(int(a.net_rescue),int(b.net_rescue)) if elig else -999
        bagain=float(d.ba-d.base_ba)
        ranks.append(dict(gate=gate,eligible=elig,min_year_net=score,dev_net=int(d.net_rescue),
                          dev_ba_gain=bagain,dev_overrides=int(d.overrides)))
    ranks=sorted(ranks,key=lambda x:(x["min_year_net"],x["dev_ba_gain"],-x["dev_overrides"]),reverse=True)
    chosen=ranks[0]["gate"]
    if not ranks[0]["eligible"]: chosen="NONE"

    summary={"status":"COMPLETE","selection_uses_2025":False,
             "context_contract":"Only WGC US and Sobti NY/London PATH_GLOBAL_1H / STRUCTURAL_IRIS_1H predictions whose session origin is <=17:00 Europe/Istanbul.",
             "base":"PAIR prediction on RFR-NOMACRO eligible rows",
             "intervention":"Only when PAIR and RFR disagree; gate may replace PAIR with RFR.",
             "ranking":ranks,"chosen_dev_gate":chosen,
             "metrics":met.to_dict(orient="records")}
    pd.concat(detail,ignore_index=True).to_csv(OUTC,index=False)
    OUTJ.write_text(json.dumps(summary,indent=2)+"\n")

    def pct(v): return f"{100*float(v):.2f}%"
    lines=["# GOLD EXECUTION RFR + SESSION EXPERT RESCUE RESULT — 2026-10-07","",
           "**Status:** COMPLETE / DEVELOPMENT-ONLY RESCUE-GATE AUDIT","",
           "Base is PAIR on RFR-NOMACRO eligible days. A gate can override PAIR with RFR only when PAIR and RFR disagree. Session signals are state evidence, not relabeled overnight targets.","",
           "| Gate | DEV overrides | DEV rescue | DEV break | DEV net | DEV BA | Base BA | 2025 overrides | 2025 rescue | 2025 break | 2025 net | 2025 BA | Base BA |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for gate in GATES:
        d=met[(met.gate==gate)&(met.period=="DEV")].iloc[0];t=met[(met.gate==gate)&(met.period=="2025")].iloc[0]
        lines.append(f"| {gate} | {int(d.overrides)} | {int(d.rescue)} | {int(d.breaks)} | {int(d.net_rescue):+d} | {pct(d.ba)} | {pct(d.base_ba)} | {int(t.overrides)} | {int(t.rescue)} | {int(t.breaks)} | {int(t.net_rescue):+d} | {pct(t.ba)} | {pct(t.base_ba)} |")
    lines += ["",f"Development-only selected gate: **{chosen}**.",
              "Selection requires nonnegative net rescue in both 2023 and 2024 and at least five development overrides. 2025 is transport evidence only.",
              "If no gate passes, session expert-state gating is rejected at this stage."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
