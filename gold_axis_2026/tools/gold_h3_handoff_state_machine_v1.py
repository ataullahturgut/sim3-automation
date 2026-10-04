from pathlib import Path
import importlib.util
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
RF=AX/"GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
AUDIT=AX/"tools"/"gold_h3_remaining53_signal_audit.py"

OUT_MD=AX/"GOLD_H3_HANDOFF_STATE_MACHINE_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_STATE_MACHINE_V1_SUMMARY_2026-10-04.json"
OUT_GRID=AX/"GOLD_H3_HANDOFF_STATE_MACHINE_V1_2025_GRID_2026-10-04.csv"
OUT_ACTIONS=AX/"GOLD_H3_HANDOFF_STATE_MACHINE_V1_ACTIONS_2026-10-04.csv"

Q_EXT=[0.60,0.67,0.75]
Q_INT=[0.60,0.67,0.75]
DELTAS=[0.00,0.05,0.10,0.15]

def b(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def load_scores():
    spec=importlib.util.spec_from_file_location("audit",AUDIT)
    audit=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    s,_=audit.build_scores()
    s=s.sort_values("feature_cutoff_date").reset_index(drop=True)
    s["internal_now"]=s[["fragility_score","flow_score"]].max(axis=1)
    s["internal_lag1"]=s[["fragility_score_lag1","flow_score_lag1"]].max(axis=1)
    s["internal_d1"]=s.internal_now-s.internal_lag1
    return s

def topology_table():
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    out=[]
    for i,r in d.iterrows():
        h=d.iloc[max(0,i-60):i]
        if len(h)<40:
            out.append((r.feature_cutoff_date,np.nan,np.nan,np.nan,np.nan,False))
            continue
        g=pd.to_numeric(h.gold_daily_ret1,errors="coerce").to_numpy(float)
        n=pd.to_numeric(h.ndx_ret1,errors="coerce").to_numpy(float)
        v=pd.to_numeric(h.vix_ret1,errors="coerce").to_numpy(float)
        def cp(a,b):
            m=np.isfinite(a)&np.isfinite(b)
            if m.sum()<40 or np.std(a[m])<=1e-12 or np.std(b[m])<=1e-12:
                return np.nan,np.nan
            rr,pp=pearsonr(a[m],b[m])
            return float(rr),float(pp)
        rn,pn=cp(g,n); rv,pv=cp(g,v)
        strong=bool(np.isfinite(rn) and np.isfinite(rv) and np.isfinite(pn) and np.isfinite(pv)
                    and rn>0 and rv<0 and min(pn,pv)<0.05)
        out.append((r.feature_cutoff_date,rn,pn,rv,pv,strong))
    return pd.DataFrame(out,columns=["feature_cutoff_date","ndx_r60","ndx_p60","vix_r60","vix_p60","strong_pro_risk"])

def load_frame():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])[["feature_cutoff_date","momentum_up"]]
    z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    z["v5_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)

    s=pd.read_csv(SAGE,parse_dates=["feature_cutoff_date"])
    sdates=set(s[[b(x) for x in s.ocs_candidate]].feature_cutoff_date)
    rf=pd.read_csv(RF,parse_dates=["date"])
    rdates=set(rf[[b(x) for x in rf.v3_candidate]].date)
    z["sage_flip"]=z.feature_cutoff_date.isin(sdates)
    z["ruleflow_flip"]=z.feature_cutoff_date.isin(rdates)
    z["overlay_flip"]=z.sage_flip|z.ruleflow_flip
    z["baseline_pred"]=np.where(z.overlay_flip,1-z.v5_pred,z.v5_pred).astype(int)
    z["baseline_correct"]=z.baseline_pred.astype(int)==z.y_up.astype(int)
    z["is_reversal"]=z.y_up.astype(int)!=z.momentum_up.astype(int)

    scores=load_scores()
    topo=topology_table()
    z=z.merge(scores[["feature_cutoff_date","fragility_score","flow_score","leadlag_score",
                      "leadlag_score_lag1","leadlag_score_lag2","leadlag_score_premax",
                      "internal_now","internal_lag1","internal_d1"]],
              on="feature_cutoff_date",how="left")
    z=z.merge(topo,on="feature_cutoff_date",how="left")
    return z.sort_values("feature_cutoff_date").reset_index(drop=True)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "up_recall":float(up),"down_recall":float(dn),"balanced_accuracy":float((up+dn)/2)}

def rule_mask(df,qe,qi,delta):
    complete=(df.leadlag_score_premax.notna()&df.internal_now.notna()&df.internal_d1.notna())
    pressure=df.leadlag_score_premax>=qe
    internal=(df.internal_now>=qi)&(df.internal_d1>=delta)
    still_momentum=df.baseline_pred.astype(int)==df.momentum_up.astype(int)
    veto=df.strong_pro_risk.fillna(False).astype(bool)
    return complete & pressure & internal & still_momentum & (~veto)

def rule_stats(df,mask):
    q=df[mask].copy()
    rescue=int((~q.baseline_correct).sum())
    broken=int(q.baseline_correct.sum())
    actions=int(len(q)); net=rescue-broken
    precision=float(rescue/actions) if actions else 0.0
    rate=float(actions/max(len(df),1))
    if actions:
        qm=q.assign(action_net=np.where(q.baseline_correct,-1,1),
                    month=q.feature_cutoff_date.dt.to_period("M").astype(str))
        monthly=qm.groupby("month").action_net.sum().to_dict()
        nonneg=sum(v>=0 for v in monthly.values())
        nonneg_share=float(nonneg/len(monthly))
        worst=int(min(monthly.values()))
    else:
        monthly={}; nonneg_share=0.0; worst=0
    return {"actions":actions,"rescue":rescue,"broken":broken,"net":net,"precision":precision,
            "rate":rate,"monthly_net":monthly,"nonnegative_action_month_share":nonneg_share,"worst_action_month_net":worst}

def eligible(st):
    return bool(st["actions"]>=6 and st["precision"]>=0.60 and st["net"]>0 and st["rate"]<=0.15
                and st["nonnegative_action_month_share"]>=0.70 and st["worst_action_month_net"]>=-1)

def main():
    z=load_frame()

    dev=z[(z.feature_cutoff_date.dt.year==2025)&z.leadlag_score_premax.notna()&
          z.internal_now.notna()&z.internal_d1.notna()].copy()
    rows=[]
    for qe in Q_EXT:
        for qi in Q_INT:
            for d in DELTAS:
                m=rule_mask(dev,qe,qi,d)
                st=rule_stats(dev,m)
                rows.append({"q_external":qe,"q_internal":qi,"delta":d,**{k:v for k,v in st.items() if k!="monthly_net"},
                             "monthly_net_json":json.dumps(st["monthly_net"],sort_keys=True),"eligible":eligible(st)})
    grid=pd.DataFrame(rows)
    grid.to_csv(OUT_GRID,index=False)

    eg=grid[grid.eligible].copy()
    selected=None
    if len(eg):
        eg=eg.sort_values(["net","precision","actions","q_external","q_internal","delta"],
                          ascending=[False,False,True,False,False,False])
        selected=eg.iloc[0].to_dict()

    summary={
      "schema":"GOLD_H3_HANDOFF_STATE_MACHINE_V1",
      "status":"NO_2025_ELIGIBLE_RULE" if selected is None else "2025_SELECTED_2026_OPENED",
      "dev_2025":{"first":dev.feature_cutoff_date.min().date().isoformat() if len(dev) else None,
                  "last":dev.feature_cutoff_date.max().date().isoformat() if len(dev) else None,
                  "n":int(len(dev)),
                  "baseline":confusion(dev.y_up,dev.baseline_pred)},
      "selected_rule":None,
      "stress_2026":None,
    }

    action_frames=[]
    if selected is not None:
        qe=float(selected["q_external"]); qi=float(selected["q_internal"]); delta=float(selected["delta"])
        md=rule_mask(dev,qe,qi,delta)
        sd=rule_stats(dev,md)
        summary["selected_rule"]={"q_external":qe,"q_internal":qi,"delta":delta,"dev_stats":sd}

        test=z[z.feature_cutoff_date.dt.year==2026].copy()
        if len(test)!=191:
            raise RuntimeError(f"Expected 191 2026 origins, got {len(test)}")
        if int(test.baseline_correct.sum())!=126:
            raise RuntimeError(f"Expected combined baseline 126/191, got {int(test.baseline_correct.sum())}")

        mt=rule_mask(test,qe,qi,delta)
        st=rule_stats(test,mt)
        assisted=test.baseline_pred.to_numpy(int).copy()
        assisted[mt.to_numpy()]=1-assisted[mt.to_numpy()]
        base_metrics=confusion(test.y_up,test.baseline_pred)
        assisted_metrics=confusion(test.y_up,assisted)

        remaining53=(~test.baseline_correct)&test.is_reversal
        rescued_remaining53=int((mt & remaining53).sum())
        broken_correct_cont=int((mt & test.baseline_correct & (~test.is_reversal)).sum())
        broken_correct_rev=int((mt & test.baseline_correct & test.is_reversal).sum())

        overlap_sage=int((mt & test.sage_flip).sum())
        overlap_rf=int((mt & test.ruleflow_flip).sum())
        q=test[mt].copy()
        q["handoff_pred"]=1-q.baseline_pred
        q["handoff_outcome"]=np.where(q.baseline_correct,"BROKEN","RESCUE")
        q["year"]=2026
        action_frames.append(q)

        summary["stress_2026"]={
          "actions":st,
          "baseline_metrics":base_metrics,
          "assisted_metrics":assisted_metrics,
          "rescued_remaining53":rescued_remaining53,
          "broken_correct_continuations":broken_correct_cont,
          "broken_correct_reversals":broken_correct_rev,
          "overlap_sage":overlap_sage,
          "overlap_ruleflow":overlap_rf,
        }

        qd=dev[md].copy()
        qd["handoff_pred"]=1-qd.baseline_pred
        qd["handoff_outcome"]=np.where(qd.baseline_correct,"BROKEN","RESCUE")
        qd["year"]=2025
        action_frames.insert(0,qd)

    if action_frames:
        act=pd.concat(action_frames,ignore_index=True)
        cols=["year","feature_cutoff_date","forecast_issue_date","target_end_date_h3","momentum_up","y_up",
              "v5_pred","sage_flip","ruleflow_flip","baseline_pred","baseline_correct",
              "leadlag_score_premax","internal_now","internal_d1","fragility_score","flow_score",
              "strong_pro_risk","ndx_r60","vix_r60","handoff_pred","handoff_outcome"]
        act[cols].to_csv(OUT_ACTIONS,index=False)
    else:
        pd.DataFrame().to_csv(OUT_ACTIONS,index=False)

    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Handoff State Machine V1 Result","",
           "**Status:** "+summary["status"],"",
           "## 2025 selection universe","",
           f"- origins with complete Handoff state: **{summary['dev_2025']['n']}**",
           f"- coverage: **{summary['dev_2025']['first']} .. {summary['dev_2025']['last']}**",
           f"- combined baseline: **{summary['dev_2025']['baseline']['correct']}/{summary['dev_2025']['baseline']['n']} = {100*summary['dev_2025']['baseline']['accuracy']:.2f}%**","",
           "## 2025 grid","",
           "| qExt | qInt | delta | Act | Rescue | Broken | Net | Precision | Rate | Nonneg action months | Worst month | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.sort_values(["eligible","net","precision"],ascending=[False,False,False]).itertuples():
        lines.append(f"| {r.q_external:.2f} | {r.q_internal:.2f} | {r.delta:.2f} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% | {100*r.rate:.1f}% | {100*r.nonnegative_action_month_share:.1f}% | {r.worst_action_month_net:+d} | {r.eligible} |")
    if selected is None:
        lines += ["","## Decision","","No 2025 rule passed the preregistered eligibility gate. HSM V1 is closed and 2026 is not used for rule selection."]
    else:
        sr=summary["selected_rule"]; s26=summary["stress_2026"]
        lines += ["","## Selected rule from 2025","",
                  f"- external pressure threshold: **{sr['q_external']:.2f}**",
                  f"- internal state threshold: **{sr['q_internal']:.2f}**",
                  f"- internal acceleration minimum: **{sr['delta']:.2f}**",
                  f"- 2025 actions/rescue/broken/net: **{sr['dev_stats']['actions']} / {sr['dev_stats']['rescue']} / {sr['dev_stats']['broken']} / {sr['dev_stats']['net']:+d}**",
                  f"- 2025 precision: **{100*sr['dev_stats']['precision']:.2f}%**","",
                  "## Frozen 2026 stress","",
                  f"- Handoff actions: **{s26['actions']['actions']}**",
                  f"- rescue / broken / net: **{s26['actions']['rescue']} / {s26['actions']['broken']} / {s26['actions']['net']:+d}**",
                  f"- action precision: **{100*s26['actions']['precision']:.2f}%**",
                  f"- remaining-53 reversals rescued: **{s26['rescued_remaining53']}**",
                  f"- broken correct continuations: **{s26['broken_correct_continuations']}**",
                  f"- overlap with SAGE actions: **{s26['overlap_sage']}**; RuleFlow actions: **{s26['overlap_ruleflow']}**","",
                  f"- baseline: **{s26['baseline_metrics']['correct']}/{s26['baseline_metrics']['n']} = {100*s26['baseline_metrics']['accuracy']:.2f}%**, BA **{100*s26['baseline_metrics']['balanced_accuracy']:.2f}%**",
                  f"- + HSM V1: **{s26['assisted_metrics']['correct']}/{s26['assisted_metrics']['n']} = {100*s26['assisted_metrics']['accuracy']:.2f}%**, BA **{100*s26['assisted_metrics']['balanced_accuracy']:.2f}%**","",
                  "## 2026 action dates","",
                  "| Date | Momentum | Baseline | Actual | Ext pre | Internal | d1 | Topology veto | Outcome |",
                  "|---|---:|---:|---:|---:|---:|---:|---|---|"]
        for r in action_frames[-1].itertuples():
            lines.append(f"| {r.feature_cutoff_date.date()} | {r.momentum_up} | {r.baseline_pred} | {r.y_up} | {r.leadlag_score_premax:.2f} | {r.internal_now:.2f} | {r.internal_d1:+.2f} | {r.strong_pro_risk} | {r.handoff_outcome} |")
        lines += ["","## Interpretation","",
                  "- The rule was selected without looking at its 2026 rescue/broken result.",
                  "- The topology veto is the previously frozen strong-pro-risk condition, recomputed origin-safely for all origins.",
                  "- Because the Handoff concept was motivated by retrospective 2026 diagnostics, the 2026 stress is stricter retrospective evidence, not pristine prospective OOS validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
