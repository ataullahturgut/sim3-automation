from pathlib import Path
import importlib.util
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist
from sklearn.mixture import GaussianMixture

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"
RTEF=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

OUT_MD=AX/"GOLD_H3_LATENT_REGIME_HANDOFF_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_LATENT_REGIME_HANDOFF_V1_SUMMARY_2026-10-04.json"
OUT_REG=AX/"GOLD_H3_LATENT_REGIME_HANDOFF_V1_REGIMES_2026-10-04.csv"
OUT_ACT=AX/"GOLD_H3_LATENT_REGIME_HANDOFF_V1_ACTIONS_2026-10-04.csv"
OUT_MODEL=AX/"GOLD_H3_LATENT_REGIME_HANDOFF_V1_MODEL_2026-10-04.json"

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec); spec.loader.exec_module(hsm)

FEATURES=[
 "abs_h_ret_12","trend_strength","adverse_excursion","path_consistency",
 "gc_volume_z20","opt_total_z20","signed_opt_pressure",
 "core_confirmation","cross_dispersion","gn_r60","gv_r60"
]

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b)
    if m.sum()<40 or np.std(a[m])<=1e-12 or np.std(b[m])<=1e-12:
        return np.nan
    return float(np.corrcoef(a[m],b[m])[0,1])

def build_regime_panel():
    rf=pd.read_csv(RTEF,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date")
    dv=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)

    gn=[]; gv=[]
    for i in range(len(dv)):
        h=dv.iloc[max(0,i-60):i]
        g=pd.to_numeric(h.gold_daily_ret1,errors="coerce")
        n=pd.to_numeric(h.ndx_ret1,errors="coerce")
        v=pd.to_numeric(h.vix_ret1,errors="coerce")
        gn.append(corr(g,n)); gv.append(corr(g,v))
    dv["gn_r60"]=gn; dv["gv_r60"]=gv

    rcols=["feature_cutoff_date","abs_h_ret_12","trend_strength","adverse_excursion","path_consistency",
           "gc_volume_z20","opt_total_z20","signed_opt_pressure"]
    dcols=["feature_cutoff_date","core_confirmation","cross_dispersion","gn_r60","gv_r60"]
    x=rf[rcols].merge(dv[dcols],on="feature_cutoff_date",how="inner",validate="one_to_one")
    return x.sort_values("feature_cutoff_date").reset_index(drop=True)

def robust_fit_transform(train, allx):
    med={}; iqr={}
    tr=np.zeros((len(train),len(FEATURES)),float)
    aa=np.zeros((len(allx),len(FEATURES)),float)
    for j,c in enumerate(FEATURES):
        s=pd.to_numeric(train[c],errors="coerce")
        m=float(s.median())
        q1=float(s.quantile(.25)); q3=float(s.quantile(.75))
        scale=float(q3-q1)
        if not np.isfinite(scale) or scale<1e-8:
            scale=float(s.std())
        if not np.isfinite(scale) or scale<1e-8:
            scale=1.0
        med[c]=m; iqr[c]=scale
        tr[:,j]=(pd.to_numeric(train[c],errors="coerce").fillna(m).to_numpy(float)-m)/scale
        aa[:,j]=(pd.to_numeric(allx[c],errors="coerce").fillna(m).to_numpy(float)-m)/scale
    return tr,aa,med,iqr

def entropy_norm(p):
    p=np.clip(np.asarray(p,float),1e-12,1)
    k=p.shape[1]
    return -np.sum(p*np.log(p),axis=1)/math.log(k)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "up_recall":float(up),"down_recall":float(dn),"balanced_accuracy":float((up+dn)/2)}

def main():
    reg=build_regime_panel()
    train=reg[(reg.feature_cutoff_date>="2023-01-01")&(reg.feature_cutoff_date<="2024-12-31")].copy()
    if len(train)<300:
        raise RuntimeError(f"Too few 2023-24 regime-training rows: {len(train)}")
    Xtr,Xall,med,iqr=robust_fit_transform(train,reg)

    models=[]
    for k in [2,3,4]:
        gm=GaussianMixture(n_components=k,covariance_type="full",random_state=20261004,n_init=50,reg_covar=1e-5)
        gm.fit(Xtr)
        models.append((float(gm.bic(Xtr)),k,gm))
    models.sort(key=lambda x:x[0])
    bic,k,gm=models[0]

    probs=gm.predict_proba(Xall)
    reg["regime"]=np.argmax(probs,axis=1)
    reg["regime_confidence"]=np.max(probs,axis=1)
    reg["regime_entropy"]=entropy_norm(probs)

    # Deterministic readable regime label by frozen component centroid properties.
    centers=gm.means_
    labels={}
    for comp in range(k):
        vals={FEATURES[j]:float(centers[comp,j]) for j in range(len(FEATURES))}
        score_risk=vals["abs_h_ret_12"]+vals["cross_dispersion"]+vals["adverse_excursion"]
        score_trend=vals["trend_strength"]+vals["path_consistency"]
        topo=vals["gn_r60"]-vals["gv_r60"]
        labels[comp]=f"R{comp}_risk{score_risk:+.2f}_trend{score_trend:+.2f}_topo{topo:+.2f}"
    reg["regime_label"]=reg.regime.map(labels)

    h=hsm.load_frame().merge(reg[["feature_cutoff_date","regime","regime_label","regime_confidence","regime_entropy"]],
                             on="feature_cutoff_date",how="left",validate="one_to_one")
    h["handoff_alarm"]=(pd.to_numeric(h.leadlag_score_premax,errors="coerce")>=.60)&(pd.to_numeric(h.internal_now,errors="coerce")>=.60)&(pd.to_numeric(h.internal_d1,errors="coerce")>=0)&(h.baseline_pred.astype(int)==h.momentum_up.astype(int))
    h["alarm_rescue"]=(~h.baseline_correct).astype(int)

    cal=h[(h.feature_cutoff_date.dt.year==2025)&h.handoff_alarm&(h.regime_confidence>=.60)].copy()
    rows=[]
    eligible=[]
    for r in sorted(cal.regime.dropna().astype(int).unique()):
        q=cal[cal.regime.astype("Int64")==r]
        R=int(q.alarm_rescue.sum()); B=int(len(q)-R)
        a=R+.5; bb=B+.5
        post_mean=float(a/(a+bb))
        pgt=float(1-beta_dist.cdf(.5,a,bb))
        ok=bool(len(q)>=3 and pgt>=.80 and post_mean>.50)
        if ok:eligible.append(int(r))
        rows.append({"regime":int(r),"regime_label":labels[int(r)],"alarms":int(len(q)),"rescue":R,"broken":B,
                     "raw_precision":float(R/len(q)) if len(q) else np.nan,"posterior_mean":post_mean,
                     "p_precision_gt_0p5":pgt,"eligible":ok})
    caltab=pd.DataFrame(rows)

    summary={
      "schema":"GOLD_H3_LATENT_REGIME_HANDOFF_V1",
      "status":"NO_ELIGIBLE_2025_REGIME" if not eligible else "FROZEN_2026_STRESS_COMPLETE",
      "regime_training":{"start":"2023-01-01","end":"2024-12-31","n":int(len(train)),
                         "selected_k":int(k),"bic":float(bic),
                         "bic_candidates":{str(kk):float(bb) for bb,kk,_ in models},
                         "features":FEATURES},
      "2025_calibration":{"alarms_confident":int(len(cal)),"eligible_regimes":eligible,
                          "regimes":rows},
      "2026":None
    }

    actions=pd.DataFrame()
    if eligible:
        test=h[h.feature_cutoff_date.dt.year==2026].copy().reset_index(drop=True)
        if len(test)!=191: raise RuntimeError(f"Expected 191 2026 rows; got {len(test)}")
        if int(test.baseline_correct.sum())!=126: raise RuntimeError(f"Expected 126 baseline correct; got {int(test.baseline_correct.sum())}")
        mask=test.handoff_alarm & (test.regime_confidence>=.60) & test.regime.isin(eligible)
        assisted=test.baseline_pred.to_numpy(int).copy()
        assisted[mask.to_numpy()]=1-assisted[mask.to_numpy()]
        actions=test[mask].copy()
        actions["outcome"]=np.where(actions.baseline_correct,"BROKEN","RESCUE")
        actions["assisted_pred"]=1-actions.baseline_pred
        rescue=int((~actions.baseline_correct).sum()); broken=int(actions.baseline_correct.sum())
        remaining53=(~test.baseline_correct)&test.is_reversal
        monthly={}
        if len(actions):
            aa=actions.assign(net=np.where(actions.baseline_correct,-1,1),month=actions.feature_cutoff_date.dt.to_period("M").astype(str))
            monthly=aa.groupby("month").net.sum().to_dict()
        rejected=test[test.handoff_alarm & ~mask].copy()
        summary["2026"]={
          "handoff_alarms":int(test.handoff_alarm.sum()),
          "acted":int(mask.sum()),"rescue":rescue,"broken":broken,"net":rescue-broken,
          "precision":float(rescue/max(int(mask.sum()),1)),
          "rescued_remaining53":int((mask&remaining53).sum()),
          "baseline":confusion(test.y_up,test.baseline_pred),
          "assisted":confusion(test.y_up,assisted),
          "monthly_net":monthly,
          "rejected_handoff_alarms":int(len(rejected)),
          "rejected_rescue":int((~rejected.baseline_correct).sum()),
          "rejected_broken":int(rejected.baseline_correct.sum())
        }

    reg.to_csv(OUT_REG,index=False)
    if len(actions):
        cols=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","momentum_up","y_up","target_r3",
              "baseline_pred","baseline_correct","leadlag_score_premax","internal_now","internal_d1",
              "regime","regime_label","regime_confidence","regime_entropy","assisted_pred","outcome"]
        actions[cols].to_csv(OUT_ACT,index=False)
    else:
        pd.DataFrame().to_csv(OUT_ACT,index=False)

    model_export={
      "selected_k":int(k),"bic_candidates":{str(kk):float(bb) for bb,kk,_ in models},
      "train_median":med,"train_iqr":iqr,"features":FEATURES,"labels":{str(a):b for a,b in labels.items()},
      "weights":gm.weights_.tolist(),"means":gm.means_.tolist(),"covariances":gm.covariances_.tolist(),
      "precisions_cholesky":gm.precisions_cholesky_.tolist()
    }
    OUT_MODEL.write_text(json.dumps(model_export,indent=2)+"\n")
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Latent-Regime Handoff V1 Result","",
           "**Status:** "+summary["status"],"",
           "## Unsupervised regime fit — 2023-2024 only","",
           f"- training rows: **{len(train)}**",
           f"- selected K by BIC: **{k}**",
           "- BIC: "+", ".join(f"K={kk}: {bb:.1f}" for bb,kk,_ in models),"",
           "## 2025 Handoff reliability by frozen regime","",
           "| Regime | Alarms | Rescue | Broken | Raw precision | Posterior mean | P(precision>50%) | Eligible |",
           "|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| {r['regime_label']} | {r['alarms']} | {r['rescue']} | {r['broken']} | {100*r['raw_precision']:.1f}% | {100*r['posterior_mean']:.1f}% | {100*r['p_precision_gt_0p5']:.1f}% | {r['eligible']} |")
    if not eligible:
        lines += ["","## Decision","","No frozen latent regime passed the 2025 Bayesian reliability gate. V1 closes without using 2026 to manufacture a rule."]
    else:
        s=summary["2026"]
        lines += ["","## Frozen 2026 stress","",
                  f"- total broad Handoff alarms: **{s['handoff_alarms']}**",
                  f"- acted alarms: **{s['acted']}**; rejected alarms: **{s['rejected_handoff_alarms']}**",
                  f"- rescue / broken / net: **{s['rescue']} / {s['broken']} / {s['net']:+d}**",
                  f"- action precision: **{100*s['precision']:.2f}%**",
                  f"- remaining-53 reversals rescued: **{s['rescued_remaining53']}**",
                  f"- rejected alarms contained rescue/broken: **{s['rejected_rescue']} / {s['rejected_broken']}**","",
                  f"- baseline: **{s['baseline']['correct']}/{s['baseline']['n']} = {100*s['baseline']['accuracy']:.2f}%**, BA **{100*s['baseline']['balanced_accuracy']:.2f}%**",
                  f"- + latent-regime Handoff: **{s['assisted']['correct']}/{s['assisted']['n']} = {100*s['assisted']['accuracy']:.2f}%**, BA **{100*s['assisted']['balanced_accuracy']:.2f}%**","",
                  "## 2026 action dates","",
                  "| Date | Regime | Conf | Ext pre | Internal | d1 | Baseline | Actual | Outcome |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for r in actions.itertuples():
            lines.append(f"| {r.feature_cutoff_date.date()} | {r.regime_label} | {r.regime_confidence:.2f} | {r.leadlag_score_premax:.2f} | {r.internal_now:.2f} | {r.internal_d1:+.2f} | {r.baseline_pred} | {r.y_up} | {r.outcome} |")
        lines += ["","## Monthly net",""]
        for m,n in s["monthly_net"].items():
            lines.append(f"- {m}: **{n:+d}**")
    lines += ["","## Governance","","Regimes were fit without 2025/2026 labels. 2025 was used only for Bayesian regime reliability. 2026 did not choose K, features, scaling, confidence threshold, or reliability threshold. Because the Handoff hypothesis itself arose from 2026 diagnostics, this remains strict retrospective stress evidence rather than pristine prospective OOS validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
