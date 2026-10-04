from pathlib import Path
import importlib.util
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"
V5C=AX/"GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
RF=AX/"GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"

OUT_MD=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_SUMMARY_2026-10-04.json"
OUT_TIMELINE=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"

EXPECTED_RUNS=[4,6,8,12]
A0=B0=0.5
PRED_THRESHOLD=0.60
P_GT_HALF_THRESHOLD=0.80

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec); spec.loader.exec_module(hsm)

class BetaBernoulliBOCPD:
    def __init__(self,expected_run):
        self.h=1.0/float(expected_run)
        self.r=np.array([1.0],float)
        self.a=np.array([A0],float)
        self.b=np.array([B0],float)
        self.last_map=0
        self.n_updates=0

    def predictive(self):
        means=self.a/(self.a+self.b)
        p=float(np.dot(self.r,means))
        pgt=np.array([1.0-beta_dist.cdf(0.5,aa,bb) for aa,bb in zip(self.a,self.b)],float)
        p_gt=float(np.dot(self.r,pgt))
        entropy=float(-np.sum(np.where(self.r>0,self.r*np.log(np.maximum(self.r,1e-300)),0.0)))
        return {
            "p_rescue":p,
            "p_theta_gt_half":p_gt,
            "map_run":int(np.argmax(self.r)),
            "run_entropy":entropy,
            "n_updates":int(self.n_updates),
        }

    def update(self,y):
        y=int(y)
        means=self.a/(self.a+self.b)
        like=means if y==1 else (1.0-means)
        prior_like=A0/(A0+B0) if y==1 else B0/(A0+B0)

        new=np.zeros(len(self.r)+1,float)
        new[0]=self.h*prior_like*float(self.r.sum())
        new[1:]=(1.0-self.h)*self.r*like
        ev=float(new.sum())
        if not np.isfinite(ev) or ev<=0:
            raise RuntimeError("invalid BOCPD evidence")
        new/=ev

        na=np.empty(len(self.a)+1,float)
        nb=np.empty(len(self.b)+1,float)
        na[0]=A0+y; nb[0]=B0+(1-y)
        na[1:]=self.a+y
        nb[1:]=self.b+(1-y)

        prev_map=int(np.argmax(self.r))
        cur_map=int(np.argmax(new))
        reset=cur_map < prev_map+1

        self.r,self.a,self.b=new,na,nb
        self.last_map=cur_map
        self.n_updates+=1
        return {
            "evidence":ev,
            "log_evidence":math.log(ev),
            "map_run_after":cur_map,
            "map_reset":bool(reset),
            "p_run0_after":float(new[0]),
        }

def _bool(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def build_frame():
    # 2025 formation can use the existing HSM frame.
    old=hsm.load_frame().sort_values("feature_cutoff_date").reset_index(drop=True)
    old=old[old.feature_cutoff_date.dt.year==2025].copy()
    old["eval_block"]="FORMATION_2025"

    # 2026 must preserve the authoritative 191-origin call-by-call universe.
    v=pd.read_csv(V5C,parse_dates=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])[["feature_cutoff_date","momentum_up"]]
    z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    z["v5_pred"]=(z.v5_dir.astype(str).str.upper()=="UP").astype(int)

    ss,_=import_audit_scores()
    z=z.merge(ss,on="feature_cutoff_date",how="left",validate="one_to_one")

    sg=pd.read_csv(SAGE,parse_dates=["feature_cutoff_date"])
    sdates=set(sg[(sg.feature_cutoff_date.dt.year==2026)&sg.ocs_candidate.map(_bool)].feature_cutoff_date)
    rr=pd.read_csv(RF,parse_dates=["date"])
    rdates=set(rr[(rr.date.dt.year==2026)&rr.v3_candidate.map(_bool)].date)
    flips=sdates|rdates
    z["sage_flip"]=z.feature_cutoff_date.isin(sdates)
    z["ruleflow_flip"]=z.feature_cutoff_date.isin(rdates)
    z["baseline_pred"]=np.where(z.feature_cutoff_date.isin(flips),1-z.v5_pred,z.v5_pred).astype(int)
    z["baseline_correct"]=z.baseline_pred.astype(int)==z.y_up.astype(int)
    z["is_reversal"]=z.y_up.astype(int)!=z.momentum_up.astype(int)
    z["eval_block"]="STRESS_2026"

    # Keep a common subset of fields required downstream.
    common=list(set(old.columns)&set(z.columns))
    needed=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","month","y_up","target_r3",
            "momentum_up","v5_pred","baseline_pred","baseline_correct","is_reversal",
            "leadlag_score_premax","internal_now","internal_d1","eval_block"]
    for c in needed:
        if c not in old.columns: old[c]=np.nan
        if c not in z.columns: z[c]=np.nan
    out=pd.concat([old[needed],z[needed]],ignore_index=True).sort_values("feature_cutoff_date").reset_index(drop=True)
    out["handoff_alarm"]=(pd.to_numeric(out.leadlag_score_premax,errors="coerce")>=.60)&(pd.to_numeric(out.internal_now,errors="coerce")>=.60)&(pd.to_numeric(out.internal_d1,errors="coerce")>=0)&(out.baseline_pred.astype(int)==out.momentum_up.astype(int))
    out["competence_y"]=(~out.baseline_correct).astype(int)
    return out

def import_audit_scores():
    audit_path=AX/"tools"/"gold_h3_remaining53_signal_audit.py"
    sp=importlib.util.spec_from_file_location("audit_for_competence",audit_path)
    audit=importlib.util.module_from_spec(sp); sp.loader.exec_module(audit)
    scores,_=audit.build_scores()
    scores=scores.sort_values("feature_cutoff_date").reset_index(drop=True)
    scores["internal_now"]=scores[["fragility_score","flow_score"]].max(axis=1)
    scores["internal_lag1"]=scores[["fragility_score_lag1","flow_score_lag1"]].max(axis=1)
    scores["internal_d1"]=scores.internal_now-scores.internal_lag1
    return scores[["feature_cutoff_date","leadlag_score_premax","internal_now","internal_d1"]],audit

def formation_evidence(alarms,expected_run):
    m=BetaBernoulliBOCPD(expected_run)
    le=0.0
    for r in alarms.sort_values("feature_cutoff_date").itertuples():
        u=m.update(int(r.competence_y))
        le+=u["log_evidence"]
    return le,m

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "up_recall":float(up),"down_recall":float(dn),"balanced_accuracy":float((up+dn)/2)}

def main():
    z=build_frame()

    form=z[(z.eval_block=="FORMATION_2025")&z.handoff_alarm].copy()
    if len(form)!=13:
        raise RuntimeError(f"Expected 13 2025 broad Handoff alarms, got {len(form)}")

    ev={}
    for er in EXPECTED_RUNS:
        le,_=formation_evidence(form,er)
        ev[er]=float(le)
    selected=max(ev,key=ev.get)

    # Build posterior from all 2025 alarm outcomes in alarm order. They are all matured before 2026 replay.
    model=BetaBernoulliBOCPD(selected)
    formation_rows=[]
    for r in form.sort_values("feature_cutoff_date").itertuples():
        pre=model.predictive()
        act=bool(pre["p_rescue"]>=PRED_THRESHOLD and pre["p_theta_gt_half"]>=P_GT_HALF_THRESHOLD)
        upd=model.update(int(r.competence_y))
        formation_rows.append({
            "period":"2025_FORMATION","feature_cutoff_date":r.feature_cutoff_date,
            "target_end_date_h3":r.target_end_date_h3,"competence_y":int(r.competence_y),
            **pre,"act":act,**upd
        })

    # 2026 replay: decisions at feature cutoff; updates only when prior alarm targets have matured.
    test=z[z.eval_block=="STRESS_2026"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    if len(test)!=191:
        raise RuntimeError(f"Expected 191 2026 origins, got {len(test)}")
    if int(test.baseline_correct.sum())!=126:
        raise RuntimeError(f"Expected 126 combined baseline correct, got {int(test.baseline_correct.sum())}")

    pending=[]
    timeline=[]
    action_mask=np.zeros(len(test),dtype=bool)

    for i,row in test.iterrows():
        now=row.feature_cutoff_date
        # Mature only information that would have been available by this origin.
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        matured.sort(key=lambda x:(x["maturity"],x["origin"]))
        matured_updates=[]
        for p in matured:
            u=model.update(p["y"])
            matured_updates.append({"origin":p["origin"].date().isoformat(),"maturity":p["maturity"].date().isoformat(),"y":p["y"],"map_reset":u["map_reset"]})

        if not bool(row.handoff_alarm):
            continue

        pre=model.predictive()
        act=bool(pre["p_rescue"]>=PRED_THRESHOLD and pre["p_theta_gt_half"]>=P_GT_HALF_THRESHOLD)
        action_mask[i]=act
        outcome="RESCUE" if int(row.competence_y)==1 else "BROKEN"
        timeline.append({
            "period":"2026_STRESS",
            "feature_cutoff_date":now,
            "forecast_issue_date":row.forecast_issue_date,
            "target_end_date_h3":row.target_end_date_h3,
            "momentum_up":int(row.momentum_up),"y_up":int(row.y_up),
            "baseline_pred":int(row.baseline_pred),"competence_y":int(row.competence_y),
            "outcome":outcome,
            "leadlag_score_premax":float(row.leadlag_score_premax),
            "internal_now":float(row.internal_now),"internal_d1":float(row.internal_d1),
            **pre,"act":act,
            "matured_updates_before_decision":json.dumps(matured_updates,separators=(",",":"))
        })
        pending.append({"maturity":row.target_end_date_h3,"origin":now,"y":int(row.competence_y)})

    # Retrospective scoring; queued final outcomes need not alter decisions but can update final state for reporting.
    for p in sorted(pending,key=lambda x:(x["maturity"],x["origin"])):
        model.update(p["y"])

    assisted=test.baseline_pred.to_numpy(int).copy()
    assisted[action_mask]=1-assisted[action_mask]

    acted=test[action_mask].copy()
    rescue=int((~acted.baseline_correct).sum())
    broken=int(acted.baseline_correct.sum())
    remaining53=(~test.baseline_correct)&test.is_reversal

    rejected=test[test.handoff_alarm & (~action_mask)].copy()
    first_trust=None
    for r in timeline:
        if r["act"]:
            first_trust=pd.Timestamp(r["feature_cutoff_date"]).date().isoformat()
            break

    monthly={}
    if len(acted):
        aa=acted.assign(net=np.where(acted.baseline_correct,-1,1),month=acted.feature_cutoff_date.dt.to_period("M").astype(str))
        monthly=aa.groupby("month").net.sum().to_dict()

    summary={
      "schema":"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1",
      "status":"FROZEN_2026_STRESS_COMPLETE",
      "formation_2025":{
        "alarms":int(len(form)),
        "rescue":int(form.competence_y.sum()),
        "broken":int(len(form)-form.competence_y.sum()),
        "expected_run_log_evidence":{str(k):v for k,v in ev.items()},
        "selected_expected_run":int(selected),
      },
      "action_rule":{"p_rescue_min":PRED_THRESHOLD,"p_theta_gt_half_min":P_GT_HALF_THRESHOLD},
      "stress_2026":{
        "handoff_alarms":int(test.handoff_alarm.sum()),
        "acted":int(action_mask.sum()),
        "rejected":int((test.handoff_alarm & (~action_mask)).sum()),
        "rescue":rescue,"broken":broken,"net":rescue-broken,
        "precision":float(rescue/max(int(action_mask.sum()),1)),
        "rescued_remaining53":int((action_mask&remaining53).sum()),
        "rejected_rescue":int((~rejected.baseline_correct).sum()),
        "rejected_broken":int(rejected.baseline_correct.sum()),
        "baseline":confusion(test.y_up,test.baseline_pred),
        "assisted":confusion(test.y_up,assisted),
        "monthly_net":monthly,
        "first_trusted_handoff_origin":first_trust,
        "final_competence_state":model.predictive(),
      }
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    pd.DataFrame(formation_rows+timeline).to_csv(OUT_TIMELINE,index=False)

    lines=["# GOLD H3 — Handoff Competence BOCPD V1 Result","",
           "**Status:** FROZEN_2026_STRESS_COMPLETE","",
           "## Formation — 2025 Handoff competence only","",
           f"- alarms: **{len(form)}**; rescue/broken = **{int(form.competence_y.sum())} / {int(len(form)-form.competence_y.sum())}**",
           "- sequential log evidence: "+", ".join(f"E[run]={k}: {v:.4f}" for k,v in sorted(ev.items())),
           f"- selected expected competence run: **{selected} Handoff alarms**","",
           "## Frozen trust rule","",
           f"- ACT only if predictive P(rescue) >= **{PRED_THRESHOLD:.2f}**",
           f"- and mixture P(theta>0.50) >= **{P_GT_HALF_THRESHOLD:.2f}**",
           "- otherwise reject Handoff and keep the combined baseline.","",
           "## 2026 causal sequential stress","",
           f"- broad Handoff alarms: **{summary['stress_2026']['handoff_alarms']}**",
           f"- acted / rejected: **{summary['stress_2026']['acted']} / {summary['stress_2026']['rejected']}**",
           f"- action rescue / broken / net: **{rescue} / {broken} / {rescue-broken:+d}**",
           f"- action precision: **{100*summary['stress_2026']['precision']:.2f}%**",
           f"- remaining-53 reversals rescued: **{summary['stress_2026']['rescued_remaining53']}**",
           f"- rejected Handoff alarms contained rescue/broken: **{summary['stress_2026']['rejected_rescue']} / {summary['stress_2026']['rejected_broken']}**",
           f"- first trusted Handoff origin: **{first_trust or 'NONE'}**","",
           f"- baseline: **{summary['stress_2026']['baseline']['correct']}/{summary['stress_2026']['baseline']['n']} = {100*summary['stress_2026']['baseline']['accuracy']:.2f}%**, BA **{100*summary['stress_2026']['baseline']['balanced_accuracy']:.2f}%**",
           f"- + competence BOCPD: **{summary['stress_2026']['assisted']['correct']}/{summary['stress_2026']['assisted']['n']} = {100*summary['stress_2026']['assisted']['accuracy']:.2f}%**, BA **{100*summary['stress_2026']['assisted']['balanced_accuracy']:.2f}%**","",
           "## Handoff alarm chronology","",
           "| Date | P(rescue) | P(theta>.5) | MAP run | Act | Actual Handoff outcome |",
           "|---|---:|---:|---:|---|---|"]
    for r in timeline:
        lines.append(f"| {pd.Timestamp(r['feature_cutoff_date']).date()} | {r['p_rescue']:.3f} | {r['p_theta_gt_half']:.3f} | {r['map_run']} | {r['act']} | {r['outcome']} |")
    lines += ["","## Monthly acted net",""]
    if monthly:
        for m,n in monthly.items():lines.append(f"- {m}: **{n:+d}**")
    else:
        lines.append("- no actions")
    lines += ["","## Scientific interpretation","",
              "- The engine estimates the time-varying competence of the Handoff expert, not Gold direction directly.",
              "- Each 2026 decision uses only Handoff outcomes whose H3 targets had already matured by that feature cutoff.",
              "- 2026 did not select the BOCPD hazard or trust thresholds.",
              "- Because the Handoff family itself was motivated by retrospective 2026 analysis, this is stringent retrospective stress evidence, not pristine prospective validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
