from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

TIMELINE=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"
PHASE=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"
SELLR=AX/"GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv"

OUT_MD=AX/"GOLD_H3_DPTC_V1_RESULT_2026-10-05.md"
OUT_JSON=AX/"GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json"
OUT_CSV=AX/"GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv"

SELLR_THR=2.3677413378977423
Q99_RUN=4.0

def b(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def load():
    tl=pd.read_csv(TIMELINE,parse_dates=["feature_cutoff_date"])
    tl["target_end_date_h3"]=pd.to_datetime(tl["target_end_date_h3"],errors="coerce")
    ph=pd.read_csv(PHASE,parse_dates=["feature_cutoff_date"])
    sc=pd.read_csv(SELLR,parse_dates=["feature_cutoff_date"])[["feature_cutoff_date","sellr_score","baseline_pred","momentum_up"]]
    z=tl.merge(ph[["feature_cutoff_date","strong_pro_risk","strong_run","dep_shift95","dependence_phase"]],
               on="feature_cutoff_date",how="left")
    z=z.merge(sc,on="feature_cutoff_date",how="left",suffixes=("","_sellr"))
    z["sellr_fire"]=(pd.to_numeric(z.sellr_score,errors="coerce")>=SELLR_THR)&(
        pd.to_numeric(z.baseline_pred_sellr,errors="coerce")==pd.to_numeric(z.momentum_up_sellr,errors="coerce"))
    z["phase_q95"]=z.dependence_phase.map(b)
    z["phase_q99"]=z.strong_pro_risk.map(b)&((pd.to_numeric(z.strong_run,errors="coerce")>Q99_RUN)|z.dep_shift95.map(b))
    return z

def simulate(df,phase_col):
    trust=False;broken_streak=0;pending=[];rows=[];entry=None
    for _,r in df.sort_values("feature_cutoff_date").iterrows():
        now=r.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            if p["acted"] and trust:
                if p["y"]==1: broken_streak=0
                else:
                    broken_streak+=1
                    if broken_streak>=2:
                        trust=False;broken_streak=0
        catalyst=bool(r.sellr_fire)
        if (not trust) and catalyst:
            trust=True;broken_streak=0
            if entry is None: entry=now
        pretrust_phase=bool(r[phase_col]) if not trust else False
        acted=bool(trust or pretrust_phase)
        mode="TRUST" if trust else ("PHASE" if pretrust_phase else "KEEP")
        rows.append({
          "feature_cutoff_date":now,"target_end_date_h3":r.target_end_date_h3,
          "competence_y":int(r.competence_y),"baseline_pred":None if pd.isna(r.baseline_pred) else int(r.baseline_pred),
          "y_up":None if pd.isna(r.y_up) else int(r.y_up),"sellr_fire":catalyst,
          "phase":bool(r[phase_col]),"acted":acted,"mode":mode
        })
        pending.append({"origin":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y),"acted":acted})
    out=pd.DataFrame(rows)
    act=out[out.acted].copy()
    rescue=int(act.competence_y.sum());broken=int(len(act)-rescue)
    return out,act,entry,rescue,broken

def metrics_2026(act):
    tp,tn,fp,fn=67,59,41,24
    for r in act.itertuples():
        bp=int(r.baseline_pred);yy=int(r.y_up)
        if bp==1 and yy==0: fp-=1;tn+=1
        elif bp==0 and yy==1: fn-=1;tp+=1
        elif bp==1 and yy==1: tp-=1;fn+=1
        elif bp==0 and yy==0: tn-=1;fp+=1
    correct=tp+tn
    ba=(tp/(tp+fn)+tn/(tn+fp))/2
    return {"tp":tp,"tn":tn,"fp":fp,"fn":fn,"correct":correct,"accuracy":correct/191,"balanced_accuracy":ba}

def month_delete(act):
    if act.empty:return []
    q=act.copy();q["month"]=q.feature_cutoff_date.dt.to_period("M").astype(str)
    out=[]
    for m in sorted(q.month.unique()):
        g=q[q.month!=m];rr=int(g.competence_y.sum());bb=int(len(g)-rr)
        out.append({"deleted_month":m,"actions":int(len(g)),"rescue":rr,"broken":bb,"net":rr-bb})
    return out

def main():
    z=load()
    form=z[z.period=="2025_FORMATION"].copy()
    test=z[z.period=="2026_STRESS"].copy()
    results={}
    allacts=[]
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _,a25,e25,r25,b25=simulate(form,col)
        _,a26,e26,r26,b26=simulate(test,col)
        met=metrics_2026(a26)
        loo=month_delete(a26)
        results[name]={
          "formation_2025":{"actions":int(len(a25)),"rescue":r25,"broken":b25,"net":r25-b25,
                            "sellr_entry":None if e25 is None else e25.date().isoformat()},
          "stress_2026":{"entry":None if e26 is None else e26.date().isoformat(),
                         "actions":int(len(a26)),"rescue":r26,"broken":b26,"net":r26-b26,
                         "precision":r26/max(len(a26),1),"metrics":met,
                         "leave_one_month_out":loo,
                         "worst_leave_one_month_out_net":min([x["net"] for x in loo]) if loo else 0,
                         "phase_actions":int((a26["mode"]=="PHASE").sum()),
                         "trust_actions":int((a26["mode"]=="TRUST").sum())}
        }
        if len(a26):
            q=a26.copy();q["variant"]=name;allacts.append(q)
    if allacts: pd.concat(allacts,ignore_index=True).to_csv(OUT_CSV,index=False)
    else: pd.DataFrame().to_csv(OUT_CSV,index=False)
    summary={"schema":"GOLD_H3_DPTC_V1","status":"POSTHOC_DEVELOPMENT_CHALLENGER","variants":results}
    OUT_JSON.write_text(json.dumps(summary,indent=2)+"\n")

    lines=["# GOLD H3 — DPTC V1 Result","",
           "**Status:** POSTHOC_DEVELOPMENT_CHALLENGER — frozen for prospective shadow after 2026-10-05.","",
           "Combined baseline reference: **126/191 = 65.97%**, BA **66.31%**.","",
           "## Variant summary","",
           "| Variant | 2025 actions R/B/net | 2026 entry | 2026 actions | Rescue | Broken | Net | Precision | Accuracy | BA | Worst leave-one-month-out |",
           "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name in ["Q95","Q99"]:
        a=results[name]["formation_2025"];s=results[name]["stress_2026"];m=s["metrics"]
        lines.append(f"| {name} | {a['actions']} ({a['rescue']}/{a['broken']}/{a['net']:+d}) | {s['entry']} | {s['actions']} | {s['rescue']} | {s['broken']} | {s['net']:+d} | {100*s['precision']:.1f}% | {100*m['accuracy']:.2f}% | {100*m['balanced_accuracy']:.2f}% | {s['worst_leave_one_month_out_net']:+d} |")
    lines += ["","## Q95 action chronology","",
              "| Date | Mode | Outcome | SELLR catalyst |",
              "|---|---|---|---|"]
    q=pd.concat(allacts,ignore_index=True) if allacts else pd.DataFrame()
    if len(q):
        for r in q[q.variant=="Q95"].itertuples():
            lines.append(f"| {r.feature_cutoff_date.date()} | {r.mode} | {'RESCUE' if r.competence_y==1 else 'BROKEN'} | {r.sellr_fire} |")
    lines += ["","## Scientific interpretation","",
              "- Q95 and Q99 were both frozen; future data may not be used to choose between them.",
              "- Pre-trust actions come from label-free dependence topology; TRUST entry comes from the already-frozen SELLR threshold.",
              "- Hysteresis handles delayed expert feedback after TRUST.",
              "- The synthesis was designed after inspecting 2026 development evidence, so 2026 accuracy is development evidence, not independent validation.",
              "- The value of DPTC is mechanistic separation: dependence state detects the competence phase, SELLR confirms a structural transition, and hysteresis preserves expert trust through noisy individual alarms."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
