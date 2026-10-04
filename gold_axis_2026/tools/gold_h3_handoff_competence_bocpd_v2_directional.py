from pathlib import Path
import importlib.util, json, math
import numpy as np, pandas as pd
from scipy.stats import beta as beta_dist

ROOT=Path(__file__).resolve().parents[2]; AX=ROOT/"gold_axis_2026"
V1=AX/"tools"/"gold_h3_handoff_competence_bocpd_v1.py"
OUT_MD=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V2_DIRECTIONAL_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V2_DIRECTIONAL_SUMMARY_2026-10-04.json"
OUT_CSV=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V2_DIRECTIONAL_TIMELINE_2026-10-04.csv"

EXPECTED_RUN=4; PRED_MIN=.60; PGT_MIN=.80
spec=importlib.util.spec_from_file_location("v1",V1); v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum()); fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":len(y),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),"tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float((up+dn)/2)}

def main():
    z=v1.build_frame()
    form=z[(z.eval_block=="FORMATION_2025")&z.handoff_alarm].copy().sort_values("feature_cutoff_date")
    streams={0:v1.BetaBernoulliBOCPD(EXPECTED_RUN),1:v1.BetaBernoulliBOCPD(EXPECTED_RUN)}
    form_stats={}
    for d in [0,1]:
        q=form[form.momentum_up.astype(int)==d]
        for r in q.itertuples(): streams[d].update(int(r.competence_y))
        form_stats[str(d)]={"alarms":int(len(q)),"rescue":int(q.competence_y.sum()),"broken":int(len(q)-q.competence_y.sum()),"state":streams[d].predictive()}

    test=z[z.eval_block=="STRESS_2026"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    if len(test)!=191 or int(test.baseline_correct.sum())!=126: raise RuntimeError("authoritative 191/126 baseline mismatch")

    pending={0:[],1:[]}; timeline=[]; action=np.zeros(len(test),bool); first={0:None,1:None}
    for i,row in test.iterrows():
        now=row.feature_cutoff_date
        for d in [0,1]:
            matured=[p for p in pending[d] if p["maturity"]<=now]
            pending[d]=[p for p in pending[d] if p["maturity"]>now]
            for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])): streams[d].update(p["y"])
        if not bool(row.handoff_alarm): continue
        d=int(row.momentum_up); pre=streams[d].predictive()
        act=bool(pre["p_rescue"]>=PRED_MIN and pre["p_theta_gt_half"]>=PGT_MIN)
        action[i]=act
        if act and first[d] is None:first[d]=now.date().isoformat()
        timeline.append({"feature_cutoff_date":now,"target_end_date_h3":row.target_end_date_h3,"direction":"UP" if d else "DOWN",
                         "p_rescue":pre["p_rescue"],"p_theta_gt_half":pre["p_theta_gt_half"],"map_run":pre["map_run"],"act":act,
                         "outcome":"RESCUE" if int(row.competence_y)==1 else "BROKEN","competence_y":int(row.competence_y),
                         "leadlag_score_premax":row.leadlag_score_premax,"internal_now":row.internal_now,"internal_d1":row.internal_d1})
        pending[d].append({"maturity":row.target_end_date_h3,"origin":now,"y":int(row.competence_y)})
    for d in [0,1]:
        for p in sorted(pending[d],key=lambda x:(x["maturity"],x["origin"])): streams[d].update(p["y"])

    assisted=test.baseline_pred.to_numpy(int).copy(); assisted[action]=1-assisted[action]
    acted=test[action]; rejected=test[test.handoff_alarm & (~action)]
    rescue=int((~acted.baseline_correct).sum()); broken=int(acted.baseline_correct.sum())
    monthly={}
    if len(acted):
        aa=acted.assign(net=np.where(acted.baseline_correct,-1,1),month=acted.feature_cutoff_date.dt.to_period("M").astype(str))
        monthly=aa.groupby("month").net.sum().to_dict()
    remaining53=(~test.baseline_correct)&test.is_reversal
    bydir={}
    for d in [0,1]:
        m=action & (test.momentum_up.astype(int).to_numpy()==d)
        q=test[m]
        bydir["UP" if d else "DOWN"]={"acted":int(m.sum()),"rescue":int((~q.baseline_correct).sum()),"broken":int(q.baseline_correct.sum()),"first_trust":first[d],"final_state":streams[d].predictive()}
    summary={"schema":"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V2_DIRECTIONAL","status":"POSTHOC_MECHANISTIC_STRESS",
             "formation_2025":form_stats,"fixed_expected_run":EXPECTED_RUN,"action_rule":{"p_rescue_min":PRED_MIN,"p_theta_gt_half_min":PGT_MIN},
             "stress_2026":{"handoff_alarms":int(test.handoff_alarm.sum()),"acted":int(action.sum()),"rejected":int((test.handoff_alarm&(~action)).sum()),
                            "rescue":rescue,"broken":broken,"net":rescue-broken,"precision":float(rescue/max(int(action.sum()),1)),
                            "rescued_remaining53":int((action&remaining53).sum()),"rejected_rescue":int((~rejected.baseline_correct).sum()),"rejected_broken":int(rejected.baseline_correct.sum()),
                            "baseline":confusion(test.y_up,test.baseline_pred),"assisted":confusion(test.y_up,assisted),"by_direction":bydir,"monthly_net":monthly}}
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")
    pd.DataFrame(timeline).to_csv(OUT_CSV,index=False)
    s=summary["stress_2026"]
    lines=["# GOLD H3 — Direction-Conditioned Handoff Competence BOCPD V2","",
           "**Status:** POSTHOC_MECHANISTIC_STRESS","",
           "## Frozen mechanics","",
           "- two independent competence streams: UP-momentum and DOWN-momentum",
           f"- expected run: **{EXPECTED_RUN} alarms** (frozen from V1)",
           f"- ACT: P(rescue)>={PRED_MIN:.2f} and P(theta>.5)>={PGT_MIN:.2f}","",
           "## 2025 initialization",""]
    for d in ["UP","DOWN"]:
        k="1" if d=="UP" else "0"; x=form_stats[k]
        lines.append(f"- {d}: {x['alarms']} alarms, {x['rescue']} rescue / {x['broken']} broken")
    lines += ["","## 2026 stress","",
              f"- Handoff alarms: **{s['handoff_alarms']}**; acted/rejected **{s['acted']} / {s['rejected']}**",
              f"- rescue/broken/net: **{s['rescue']} / {s['broken']} / {s['net']:+d}**",
              f"- precision: **{100*s['precision']:.2f}%**",
              f"- remaining-53 rescued: **{s['rescued_remaining53']}**",
              f"- baseline: **{s['baseline']['correct']}/191 = {100*s['baseline']['accuracy']:.2f}%**, BA **{100*s['baseline']['balanced_accuracy']:.2f}%**",
              f"- + directional competence: **{s['assisted']['correct']}/191 = {100*s['assisted']['accuracy']:.2f}%**, BA **{100*s['assisted']['balanced_accuracy']:.2f}%**","",
              "## Direction detail",""]
    for d,x in bydir.items():lines.append(f"- {d}: acted {x['acted']}, rescue/broken {x['rescue']}/{x['broken']}, first trust {x['first_trust'] or 'NONE'}")
    lines += ["","## Chronology","",
              "| Date | Stream | P(rescue) | P(theta>.5) | Act | Outcome |",
              "|---|---|---:|---:|---|---|"]
    for r in timeline:lines.append(f"| {pd.Timestamp(r['feature_cutoff_date']).date()} | {r['direction']} | {r['p_rescue']:.3f} | {r['p_theta_gt_half']:.3f} | {r['act']} | {r['outcome']} |")
    lines += ["","## Governance","",
              "This successor was motivated by the observed 2026 directional asymmetry, so the replay is explicitly post-hoc mechanistic research. No threshold or hazard was changed after preregistration."]
    OUT_MD.write_text("\n".join(lines)+"\n"); print(OUT_MD.read_text())

if __name__=="__main__": main()
