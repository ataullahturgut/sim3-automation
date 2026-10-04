from pathlib import Path
import importlib.util, json
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]; AX=ROOT/"gold_axis_2026"
V1=AX/"tools"/"gold_h3_handoff_competence_bocpd_v1.py"
OUT_MD=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_SUMMARY_2026-10-04.json"
OUT_CSV=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_TIMELINE_2026-10-04.csv"

EXPECTED_RUN=4; PRED_MIN=.60; PGT_MIN=.80; EXIT_STREAK=2
spec=importlib.util.spec_from_file_location("v1",V1); v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum()); fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":len(y),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),"tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float((up+dn)/2)}

def main():
    z=v1.build_frame()
    form=z[(z.eval_block=="FORMATION_2025")&z.handoff_alarm].copy().sort_values("feature_cutoff_date")
    model=v1.BetaBernoulliBOCPD(EXPECTED_RUN)
    for r in form.itertuples(): model.update(int(r.competence_y))

    test=z[z.eval_block=="STRESS_2026"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    if len(test)!=191 or int(test.baseline_correct.sum())!=126: raise RuntimeError("authoritative 191/126 baseline mismatch")

    trust=False; failure_streak=0; pending=[]; timeline=[]; actions=np.zeros(len(test),bool); state_events=[]
    for i,row in test.iterrows():
        now=row.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        matured_updates=[]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            upd=model.update(p["y"])
            before=trust
            if p["acted"] and trust:
                if p["y"]==1:
                    failure_streak=0
                else:
                    failure_streak+=1
                    if failure_streak>=EXIT_STREAK:
                        trust=False
                        failure_streak=0
                        state_events.append({"date":now.date().isoformat(),"event":"TRUST_EXIT","trigger_origin":p["origin"].date().isoformat()})
            matured_updates.append({"origin":p["origin"].date().isoformat(),"y":p["y"],"acted":p["acted"],"trust_before":before,"trust_after":trust,"map_reset":upd["map_reset"]})

        if not bool(row.handoff_alarm): continue
        pre=model.predictive()
        entry=False
        if not trust and pre["p_rescue"]>=PRED_MIN and pre["p_theta_gt_half"]>=PGT_MIN:
            trust=True; failure_streak=0; entry=True
            state_events.append({"date":now.date().isoformat(),"event":"TRUST_ENTRY","trigger_origin":now.date().isoformat()})
        act=bool(trust)
        actions[i]=act
        timeline.append({"feature_cutoff_date":now,"target_end_date_h3":row.target_end_date_h3,
                         "p_rescue":pre["p_rescue"],"p_theta_gt_half":pre["p_theta_gt_half"],"map_run":pre["map_run"],
                         "entry_now":entry,"trust_state":trust,"failure_streak_before_decision":failure_streak,
                         "act":act,"outcome":"RESCUE" if int(row.competence_y)==1 else "BROKEN","competence_y":int(row.competence_y),
                         "leadlag_score_premax":row.leadlag_score_premax,"internal_now":row.internal_now,"internal_d1":row.internal_d1,
                         "matured_updates_before_decision":json.dumps(matured_updates,separators=(",",":"))})
        pending.append({"maturity":row.target_end_date_h3,"origin":now,"y":int(row.competence_y),"acted":act})

    # final maturation is reporting only
    for p in sorted(pending,key=lambda x:(x["maturity"],x["origin"])):
        model.update(p["y"])

    assisted=test.baseline_pred.to_numpy(int).copy(); assisted[actions]=1-assisted[actions]
    acted=test[actions]; rejected=test[test.handoff_alarm&(~actions)]
    rescue=int((~acted.baseline_correct).sum()); broken=int(acted.baseline_correct.sum()); remaining53=(~test.baseline_correct)&test.is_reversal
    monthly={}
    if len(acted):
        aa=acted.assign(net=np.where(acted.baseline_correct,-1,1),month=acted.feature_cutoff_date.dt.to_period("M").astype(str)); monthly=aa.groupby("month").net.sum().to_dict()

    s={"schema":"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS","status":"POSTHOC_DEVELOPMENT_DIAGNOSTIC",
       "formation_2025":{"alarms":int(len(form)),"rescue":int(form.competence_y.sum()),"broken":int(len(form)-form.competence_y.sum())},
       "fixed":{"expected_run":EXPECTED_RUN,"entry_p_rescue":PRED_MIN,"entry_p_theta_gt_half":PGT_MIN,"exit_consecutive_broken":EXIT_STREAK},
       "stress_2026":{"handoff_alarms":int(test.handoff_alarm.sum()),"acted":int(actions.sum()),"rejected":int((test.handoff_alarm&(~actions)).sum()),
                      "rescue":rescue,"broken":broken,"net":rescue-broken,"precision":float(rescue/max(int(actions.sum()),1)),
                      "rescued_remaining53":int((actions&remaining53).sum()),"rejected_rescue":int((~rejected.baseline_correct).sum()),"rejected_broken":int(rejected.baseline_correct.sum()),
                      "baseline":confusion(test.y_up,test.baseline_pred),"assisted":confusion(test.y_up,assisted),"monthly_net":monthly,"state_events":state_events}}
    OUT_JSON.write_text(json.dumps(s,indent=2,default=str)+"\n"); pd.DataFrame(timeline).to_csv(OUT_CSV,index=False)
    t=s["stress_2026"]
    lines=["# GOLD H3 — Handoff Competence BOCPD V4 Hysteresis","",
           "**Status:** POSTHOC_DEVELOPMENT_DIAGNOSTIC","",
           "## Frozen state machine","",
           f"- enter trust: P(rescue)>={PRED_MIN:.2f} and P(theta>.5)>={PGT_MIN:.2f}",
           f"- once ON, act on every Handoff alarm",
           f"- exit only after **{EXIT_STREAK} consecutive matured BROKEN outcomes from acted Handoff alarms**","",
           "## 2026 replay","",
           f"- Handoff alarms: **{t['handoff_alarms']}**; acted/rejected **{t['acted']} / {t['rejected']}**",
           f"- rescue/broken/net: **{rescue} / {broken} / {rescue-broken:+d}**",
           f"- precision: **{100*t['precision']:.2f}%**",
           f"- remaining-53 rescued: **{t['rescued_remaining53']}**",
           f"- baseline: **{t['baseline']['correct']}/191 = {100*t['baseline']['accuracy']:.2f}%**, BA **{100*t['baseline']['balanced_accuracy']:.2f}%**",
           f"- + hysteretic competence: **{t['assisted']['correct']}/191 = {100*t['assisted']['accuracy']:.2f}%**, BA **{100*t['assisted']['balanced_accuracy']:.2f}%**","",
           "## Trust-state events",""]
    if state_events:
        for e in state_events:lines.append(f"- {e['date']}: **{e['event']}**")
    else:lines.append("- none")
    lines += ["","## Chronology","",
              "| Date | P(rescue) | P(theta>.5) | Entry | Trust | Fail streak | Act | Outcome |",
              "|---|---:|---:|---|---|---:|---|---|"]
    for r in timeline:lines.append(f"| {pd.Timestamp(r['feature_cutoff_date']).date()} | {r['p_rescue']:.3f} | {r['p_theta_gt_half']:.3f} | {r['entry_now']} | {r['trust_state']} | {r['failure_streak_before_decision']} | {r['act']} | {r['outcome']} |")
    lines += ["","## Governance","",
              "V4 was designed after inspecting V1 chronology. Its 2026 result is therefore development evidence, not validation. Entry thresholds, BOCPD hazard and the two-strike exit were frozen before this run."]
    OUT_MD.write_text("\n".join(lines)+"\n"); print(OUT_MD.read_text())

if __name__=="__main__": main()
