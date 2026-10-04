from pathlib import Path
import importlib.util, json
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]; AX=ROOT/"gold_axis_2026"
V1=AX/"tools"/"gold_h3_handoff_competence_bocpd_v1.py"
OUT_MD=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V3_TOPOLOGY_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V3_TOPOLOGY_SUMMARY_2026-10-04.json"
OUT_CSV=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V3_TOPOLOGY_TIMELINE_2026-10-04.csv"
EXPECTED_RUN=4; PRED_MIN=.60; PGT_MIN=.80

spec=importlib.util.spec_from_file_location("v1",V1); v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum()); fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":len(y),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),"tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float((up+dn)/2)}

def main():
    z=v1.build_frame()
    topo=v1.hsm.topology_table()[["feature_cutoff_date","strong_pro_risk"]]
    z=z.merge(topo,on="feature_cutoff_date",how="left")
    z["topology_stream"]=np.where(z.strong_pro_risk.fillna(False),"STRONG_PRO_RISK","OTHER_TOPOLOGY")

    form=z[(z.eval_block=="FORMATION_2025")&z.handoff_alarm].copy().sort_values("feature_cutoff_date")
    streams={k:v1.BetaBernoulliBOCPD(EXPECTED_RUN) for k in ["STRONG_PRO_RISK","OTHER_TOPOLOGY"]}
    init={}
    for k in streams:
        q=form[form.topology_stream==k]
        for r in q.itertuples(): streams[k].update(int(r.competence_y))
        init[k]={"alarms":int(len(q)),"rescue":int(q.competence_y.sum()),"broken":int(len(q)-q.competence_y.sum()),"state":streams[k].predictive()}

    test=z[z.eval_block=="STRESS_2026"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    if len(test)!=191 or int(test.baseline_correct.sum())!=126: raise RuntimeError("authoritative 191/126 baseline mismatch")

    pending={k:[] for k in streams}; timeline=[]; action=np.zeros(len(test),bool); first={k:None for k in streams}
    for i,row in test.iterrows():
        now=row.feature_cutoff_date
        for k in streams:
            matured=[p for p in pending[k] if p["maturity"]<=now]
            pending[k]=[p for p in pending[k] if p["maturity"]>now]
            for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])): streams[k].update(p["y"])
        if not bool(row.handoff_alarm): continue
        k=row.topology_stream; pre=streams[k].predictive()
        act=bool(pre["p_rescue"]>=PRED_MIN and pre["p_theta_gt_half"]>=PGT_MIN)
        action[i]=act
        if act and first[k] is None:first[k]=now.date().isoformat()
        timeline.append({"feature_cutoff_date":now,"target_end_date_h3":row.target_end_date_h3,"stream":k,
                         "p_rescue":pre["p_rescue"],"p_theta_gt_half":pre["p_theta_gt_half"],"map_run":pre["map_run"],
                         "act":act,"outcome":"RESCUE" if int(row.competence_y)==1 else "BROKEN","competence_y":int(row.competence_y),
                         "leadlag_score_premax":row.leadlag_score_premax,"internal_now":row.internal_now,"internal_d1":row.internal_d1})
        pending[k].append({"maturity":row.target_end_date_h3,"origin":now,"y":int(row.competence_y)})
    for k in streams:
        for p in sorted(pending[k],key=lambda x:(x["maturity"],x["origin"])): streams[k].update(p["y"])

    assisted=test.baseline_pred.to_numpy(int).copy(); assisted[action]=1-assisted[action]
    acted=test[action]; rejected=test[test.handoff_alarm&(~action)]
    rescue=int((~acted.baseline_correct).sum()); broken=int(acted.baseline_correct.sum()); remaining53=(~test.baseline_correct)&test.is_reversal
    by={}
    for k in streams:
        m=action&(test.topology_stream.to_numpy()==k); q=test[m]
        by[k]={"acted":int(m.sum()),"rescue":int((~q.baseline_correct).sum()),"broken":int(q.baseline_correct.sum()),"first_trust":first[k],"final_state":streams[k].predictive()}
    monthly={}
    if len(acted):
        aa=acted.assign(net=np.where(acted.baseline_correct,-1,1),month=acted.feature_cutoff_date.dt.to_period("M").astype(str)); monthly=aa.groupby("month").net.sum().to_dict()
    s={"schema":"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V3_TOPOLOGY","status":"POSTHOC_MECHANISTIC_STRESS","formation_2025":init,
       "fixed_expected_run":EXPECTED_RUN,"action_rule":{"p_rescue_min":PRED_MIN,"p_theta_gt_half_min":PGT_MIN},
       "stress_2026":{"handoff_alarms":int(test.handoff_alarm.sum()),"acted":int(action.sum()),"rejected":int((test.handoff_alarm&(~action)).sum()),
                      "rescue":rescue,"broken":broken,"net":rescue-broken,"precision":float(rescue/max(int(action.sum()),1)),
                      "rescued_remaining53":int((action&remaining53).sum()),"rejected_rescue":int((~rejected.baseline_correct).sum()),"rejected_broken":int(rejected.baseline_correct.sum()),
                      "baseline":confusion(test.y_up,test.baseline_pred),"assisted":confusion(test.y_up,assisted),"by_topology":by,"monthly_net":monthly}}
    OUT_JSON.write_text(json.dumps(s,indent=2,default=str)+"\n"); pd.DataFrame(timeline).to_csv(OUT_CSV,index=False)
    t=s["stress_2026"]
    lines=["# GOLD H3 — Topology-Conditioned Handoff Competence BOCPD V3","",
           "**Status:** POSTHOC_MECHANISTIC_STRESS","",
           "## 2025 initialization",""]
    for k,x in init.items(): lines.append(f"- {k}: {x['alarms']} alarms, {x['rescue']} rescue / {x['broken']} broken")
    lines += ["","## 2026 stress","",
              f"- alarms: **{t['handoff_alarms']}**; acted/rejected **{t['acted']} / {t['rejected']}**",
              f"- rescue/broken/net: **{rescue} / {broken} / {rescue-broken:+d}**",
              f"- precision: **{100*t['precision']:.2f}%**; remaining-53 rescued **{t['rescued_remaining53']}**",
              f"- baseline: **{t['baseline']['correct']}/191 = {100*t['baseline']['accuracy']:.2f}%**, BA **{100*t['baseline']['balanced_accuracy']:.2f}%**",
              f"- + topology competence: **{t['assisted']['correct']}/191 = {100*t['assisted']['accuracy']:.2f}%**, BA **{100*t['assisted']['balanced_accuracy']:.2f}%**","",
              "## Topology detail",""]
    for k,x in by.items(): lines.append(f"- {k}: acted {x['acted']}, rescue/broken {x['rescue']}/{x['broken']}, first trust {x['first_trust'] or 'NONE'}")
    lines += ["","## Chronology","",
              "| Date | Stream | P(rescue) | P(theta>.5) | Act | Outcome |",
              "|---|---|---:|---:|---|---|"]
    for r in timeline: lines.append(f"| {pd.Timestamp(r['feature_cutoff_date']).date()} | {r['stream']} | {r['p_rescue']:.3f} | {r['p_theta_gt_half']:.3f} | {r['act']} | {r['outcome']} |")
    lines += ["","## Governance","",
              "Topology definition, expected run and trust thresholds were frozen before this run. The hypothesis was motivated by already-inspected 2026 topology interaction, so this is post-hoc mechanistic research."]
    OUT_MD.write_text("\n".join(lines)+"\n"); print(OUT_MD.read_text())

if __name__=="__main__": main()
