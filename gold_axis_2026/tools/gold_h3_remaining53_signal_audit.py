from pathlib import Path
import json
import math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

V5=AX/"GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
RF=AX/"GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"
IFBC=AX/"GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv"
LLRS=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
TRES=AX/"GOLD_H3_TRES_V2_PREDICTIONS_2026-10-04.csv"

OUT_MD=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_SUMMARY_2026-10-04.json"
OUT_CSV=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_ORIGINS_2026-10-04.csv"
OUT_EP=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_EPISODES_2026-10-04.csv"
OUT_FEAT=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_FEATURES_2026-10-04.csv"

THRESHOLDS=[0.60,0.67,0.75,0.80]

def b(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def pct_rank(hist,val):
    a=pd.to_numeric(pd.Series(hist),errors="coerce").to_numpy(float)
    a=a[np.isfinite(a)]
    if not np.isfinite(val) or len(a)<20: return np.nan
    return float((1+np.sum(a<=val))/(len(a)+1))

def rolling_rank(df,col,sign=1.0,window=120):
    x=pd.to_numeric(df[col],errors="coerce").to_numpy(float)*sign
    out=np.full(len(df),np.nan)
    for i in range(len(df)):
        h=x[max(0,i-window):i]
        out[i]=pct_rank(h,x[i])
    return out

def medcols(df,cols):
    a=df[cols].to_numpy(float)
    return np.nanmedian(a,axis=1)

def reaction_break(div):
    d=div.copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    regs=["silver_ret1","usd_ret1","tnx_chg1","ndx_ret1","vix_ret1"]
    y=pd.to_numeric(d.gold_daily_ret1,errors="coerce").to_numpy(float)
    X=np.column_stack([pd.to_numeric(d[c],errors="coerce").to_numpy(float) for c in regs])
    absz=np.full(len(d),np.nan); against=np.full(len(d),np.nan)
    for i in range(len(d)):
        hidx=np.arange(max(0,i-60),i)
        if len(hidx)<40: continue
        yh=y[hidx]; Xh=X[hidx]
        m=np.isfinite(yh)&np.all(np.isfinite(Xh),axis=1)
        if m.sum()<40 or not np.isfinite(y[i]) or not np.all(np.isfinite(X[i])): continue
        A=np.column_stack([np.ones(m.sum()),Xh[m]])
        beta=np.linalg.lstsq(A,yh[m],rcond=None)[0]
        fitted=A@beta
        rs=yh[m]-fitted
        sig=float(np.std(rs,ddof=max(1,A.shape[1])))
        if not np.isfinite(sig) or sig<=1e-10: continue
        pred=float(np.r_[1.0,X[i]]@beta)
        resid=(y[i]-pred)/sig
        mom=1 if int(d.loc[i,"momentum_up"])==1 else -1
        absz[i]=abs(resid)
        against[i]=-mom*resid
    d["reaction_abs_z"]=absz
    d["reaction_against_z"]=against
    d["reaction_abs_rank"]=rolling_rank(d,"reaction_abs_z",1.0,120)
    d["reaction_against_rank"]=rolling_rank(d,"reaction_against_z",1.0,120)
    d["reaction_score"]=medcols(d,["reaction_abs_rank","reaction_against_rank"])
    return d[["feature_cutoff_date","reaction_abs_z","reaction_against_z","reaction_abs_rank","reaction_against_rank","reaction_score"]]

def build_scores():
    i=pd.read_csv(IFBC,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    mom=np.where(i.momentum_up.astype(int).to_numpy()==1,1.0,-1.0)
    i["gc_flow_against_mom"]=-mom*pd.to_numeric(i.gc_flow_12,errors="coerce").to_numpy(float)
    i["si_flow_against_mom"]=-mom*pd.to_numeric(i.si_flow_12,errors="coerce").to_numpy(float)

    rank_specs={
      "r_frag_trend":("trend_strength",-1.0),
      "r_frag_session":("session_against_trend",1.0),
      "r_frag_close":("trend_close_location",-1.0),
      "r_frag_adverse":("adverse_excursion",1.0),
      "r_flow_gc_oppvol":("gc_opp_vol_share_12",1.0),
      "r_flow_si_oppvol":("si_opp_vol_share_12",1.0),
      "r_flow_joint":("joint_opposition_share12",1.0),
      "r_flow_gc_against":("gc_flow_against_mom",1.0),
      "r_flow_si_against":("si_flow_against_mom",1.0),
      "r_flow_ineff":("gc_efficiency_12",-1.0),
    }
    for out,(col,sgn) in rank_specs.items():
        i[out]=rolling_rank(i,col,sgn,120)
    i["fragility_score"]=medcols(i,["r_frag_trend","r_frag_session","r_frag_close","r_frag_adverse"])
    i["flow_score"]=medcols(i,["r_flow_gc_oppvol","r_flow_si_oppvol","r_flow_joint","r_flow_gc_against","r_flow_si_against","r_flow_ineff"])

    l=pd.read_csv(LLRS,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    l["r_llrs_pressure"]=rolling_rank(l,"llrs_pressure",1.0,120)
    l["r_llrs_incremental"]=rolling_rank(l,"llrs_incremental",1.0,120)
    l["llrs_strict"]=pd.Series([b(x) for x in l.llrs_external_opposes],index=l.index,dtype=bool) & (pd.to_numeric(l.llrs_pressure,errors="coerce")>0) & (pd.to_numeric(l.llrs_incremental,errors="coerce")>0)
    l["leadlag_score"]=medcols(l,["r_llrs_pressure","r_llrs_incremental"])
    l.loc[~l.llrs_strict,"leadlag_score"]=0.0

    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    rb=reaction_break(d)

    t=pd.read_csv(TRES,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date")
    t=t[["feature_cutoff_date","mu_reversal","mu_unresolved","mu_continuation"]].copy()
    t["tres_warning"]=pd.to_numeric(t.mu_reversal,errors="coerce")+0.5*pd.to_numeric(t.mu_unresolved,errors="coerce")

    keep_i=["feature_cutoff_date","fragility_score","flow_score"]+list(rank_specs.keys())
    z=i[keep_i].merge(l[["feature_cutoff_date","leadlag_score","llrs_strict","r_llrs_pressure","r_llrs_incremental"]],on="feature_cutoff_date",how="outer")
    z=z.merge(rb,on="feature_cutoff_date",how="outer").merge(t,on="feature_cutoff_date",how="outer")
    z=z.sort_values("feature_cutoff_date").reset_index(drop=True)

    mech=["fragility_score","flow_score","leadlag_score","reaction_score"]
    for c in mech+["tres_warning"]:
        z[f"{c}_lag1"]=z[c].shift(1)
        z[f"{c}_lag2"]=z[c].shift(2)
        z[f"{c}_premax"]=z[[f"{c}_lag1",f"{c}_lag2"]].max(axis=1)
        z[f"{c}_anymax"]=z[[c,f"{c}_lag1",f"{c}_lag2"]].max(axis=1)
    return z,rank_specs

def build_target(scores):
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    v=v[v.feature_cutoff_date.dt.year==2026].copy()
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])[["feature_cutoff_date","momentum_up"]]
    v=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    v["v5_pred"]=(pd.to_numeric(v.p_helios_v5_dce,errors="coerce")>=.5).astype(int)

    s=pd.read_csv(SAGE,parse_dates=["feature_cutoff_date"])
    sdates=set(s[(s.feature_cutoff_date.dt.year==2026)&s.ocs_candidate.astype(str).str.lower().isin(["true","1","yes"])].feature_cutoff_date)
    r=pd.read_csv(RF,parse_dates=["date"])
    rdates=set(r[(r.date.dt.year==2026)&r.v3_candidate.astype(str).str.lower().isin(["true","1","yes"])].date)
    fix=sdates|rdates
    v["combined_pred"]=v.apply(lambda x:1-int(x.v5_pred) if x.feature_cutoff_date in fix else int(x.v5_pred),axis=1)
    v["is_reversal"]=v.y_up.astype(int)!=v.momentum_up.astype(int)
    v["combined_correct"]=v.combined_pred.astype(int)==v.y_up.astype(int)
    v["missed_reversal"]=(~v.combined_correct)&v.is_reversal
    v["correct_continuation"]=v.combined_correct&(~v.is_reversal)
    z=v.merge(scores,on="feature_cutoff_date",how="left",validate="one_to_one")
    return z

def smd(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<3 or len(b)<3:return np.nan
    va=np.var(a,ddof=1); vb=np.var(b,ddof=1)
    sp=np.sqrt(((len(a)-1)*va+(len(b)-1)*vb)/(len(a)+len(b)-2))
    return float((np.mean(a)-np.mean(b))/sp) if sp>1e-12 else np.nan

def prevalence(tab, mechanism, threshold, timing):
    col={"current":mechanism,"pre":f"{mechanism}_premax","any":f"{mechanism}_anymax"}[timing]
    miss=tab[tab.missed_reversal]
    ctrl=tab[tab.correct_continuation]
    mc=float((pd.to_numeric(miss[col],errors="coerce")>=threshold).mean())
    cc=float((pd.to_numeric(ctrl[col],errors="coerce")>=threshold).mean())
    return {"mechanism":mechanism,"threshold":threshold,"timing":timing,
            "miss_coverage":mc,"control_prevalence":cc,"lift":float(mc/cc) if cc>0 else np.nan,
            "miss_n":int(len(miss)),"control_n":int(len(ctrl))}

def episodes(tab):
    q=tab[tab.missed_reversal].sort_values("feature_cutoff_date").copy()
    eid=[]; e=0; prev=None
    for d in q.feature_cutoff_date:
        if prev is None or (d-prev).days>4:e+=1
        eid.append(e); prev=d
    q["episode"]=eid
    first=q.groupby("episode",as_index=False).first()
    spans=q.groupby("episode").agg(start=("feature_cutoff_date","min"),end=("feature_cutoff_date","max"),n=("feature_cutoff_date","size"),
                                    max_abs_r3=("target_r3",lambda x:float(np.max(np.abs(pd.to_numeric(x,errors="coerce")))))).reset_index()
    first=first.merge(spans,on="episode",suffixes=("","_span"))
    return q,first

def main():
    scores,rank_specs=build_scores()
    z=build_target(scores)
    miss=z[z.missed_reversal].copy()
    ctrl=z[z.correct_continuation].copy()
    if len(miss)!=53:
        raise RuntimeError(f"Expected 53 remaining missed reversals, got {len(miss)}")

    mech=["fragility_score","flow_score","leadlag_score","reaction_score"]
    prev=[]
    for m in mech:
        for th in THRESHOLDS:
            for timing in ["current","pre","any"]:
                prev.append(prevalence(z,m,th,timing))
    prevdf=pd.DataFrame(prev)

    q,ep=episodes(z)

    for th in [0.67,0.75]:
        for timing,suf in [("current",""),("pre","_premax"),("any","_anymax")]:
            cols=[f"{m}{suf}" for m in mech]
            q[f"mechanism_count_{timing}_{str(th).replace('.','p')}"]=(q[cols]>=th).sum(axis=1)
            ep[f"mechanism_count_{timing}_{str(th).replace('.','p')}"]=(ep[cols]>=th).sum(axis=1)

    feat_rows=[]
    current_features=list(rank_specs.keys())+["r_llrs_pressure","r_llrs_incremental","reaction_abs_rank","reaction_against_rank",
                                               "fragility_score","flow_score","leadlag_score","reaction_score","tres_warning"]
    for c in current_features:
        if c not in z.columns:continue
        feat_rows.append({"feature":c,"miss_mean":float(pd.to_numeric(miss[c],errors="coerce").mean()),
                          "control_mean":float(pd.to_numeric(ctrl[c],errors="coerce").mean()),
                          "smd_miss_minus_control":smd(pd.to_numeric(miss[c],errors="coerce"),pd.to_numeric(ctrl[c],errors="coerce"))})
    featdf=pd.DataFrame(feat_rows).sort_values("smd_miss_minus_control",ascending=False)

    # Compact per-origin audit.
    outcols=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3","momentum_up","y_up","v5_pred","combined_pred",
             "fragility_score","flow_score","leadlag_score","reaction_score","tres_warning",
             "fragility_score_lag1","fragility_score_lag2","flow_score_lag1","flow_score_lag2",
             "leadlag_score_lag1","leadlag_score_lag2","reaction_score_lag1","reaction_score_lag2",
             "reaction_abs_z","reaction_against_z"]
    for c in outcols:
        if c not in q.columns:q[c]=np.nan
    q[outcols+["episode"]].to_csv(OUT_CSV,index=False)
    epcols=["episode","feature_cutoff_date","start","end","n","max_abs_r3","target_r3"]+[
        x for m in mech for x in [m,f"{m}_lag1",f"{m}_lag2",f"{m}_premax",f"{m}_anymax"]
    ]+["tres_warning","tres_warning_lag1","tres_warning_lag2","mechanism_count_current_0p67","mechanism_count_pre_0p67","mechanism_count_any_0p67",
       "mechanism_count_current_0p75","mechanism_count_pre_0p75","mechanism_count_any_0p75"]
    ep[epcols].to_csv(OUT_EP,index=False)
    featdf.to_csv(OUT_FEAT,index=False)

    summary={
      "schema":"GOLD_H3_REMAINING53_SIGNAL_AUDIT",
      "status":"RETROSPECTIVE_MECHANISM_DIAGNOSTIC",
      "remaining_missed_reversals":int(len(miss)),
      "correct_continuation_controls":int(len(ctrl)),
      "episodes":int(ep.episode.nunique()),
      "multi_origin_episodes":int((q.groupby("episode").size()>=2).sum()),
      "prevalence":prev,
      "episode_first":{
        "n":int(len(ep)),
        "at_067":{
          "pre_ge1":int((ep.mechanism_count_pre_0p67>=1).sum()),
          "pre_ge2":int((ep.mechanism_count_pre_0p67>=2).sum()),
          "any_ge1":int((ep.mechanism_count_any_0p67>=1).sum()),
          "any_ge2":int((ep.mechanism_count_any_0p67>=2).sum()),
          "current_ge1":int((ep.mechanism_count_current_0p67>=1).sum()),
          "current_ge2":int((ep.mechanism_count_current_0p67>=2).sum())
        },
        "at_075":{
          "pre_ge1":int((ep.mechanism_count_pre_0p75>=1).sum()),
          "pre_ge2":int((ep.mechanism_count_pre_0p75>=2).sum()),
          "any_ge1":int((ep.mechanism_count_any_0p75>=1).sum()),
          "any_ge2":int((ep.mechanism_count_any_0p75>=2).sum())
        }
      },
      "top_feature_smd":featdf.head(15).replace({np.nan:None}).to_dict("records")
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    def fmt(x):
        return "NA" if not np.isfinite(x) else f"{100*x:.1f}%"
    lines=["# GOLD H3 — Remaining-53 Signal Audit Result","",
           "**Status:** retrospective mechanism diagnostic; not a new model and not a promotion test.","",
           f"- Remaining missed reversals: **{len(miss)}**",
           f"- Correct-continuation controls: **{len(ctrl)}**",
           f"- Reversal episodes: **{len(ep)}**",
           f"- Multi-origin episodes: **{int((q.groupby('episode').size()>=2).sum())}**","",
           "## Mechanism coverage","",
           "| Mechanism | Threshold | Timing | Miss coverage | Control prevalence | Lift |",
           "|---|---:|---|---:|---:|---:|"]
    for r in prevdf[(prevdf.threshold.isin([.67,.75]))].itertuples():
        lift="NA" if not np.isfinite(r.lift) else f"{r.lift:.2f}x"
        lines.append(f"| {r.mechanism} | {r.threshold:.2f} | {r.timing} | {fmt(r.miss_coverage)} | {fmt(r.control_prevalence)} | {lift} |")
    lines += ["","## Episode-first early-warning coverage","",
              f"At 0.67, at least one mechanism was already elevated at t-1/t-2 in **{summary['episode_first']['at_067']['pre_ge1']}/{len(ep)}** episode starts.",
              f"At 0.67, at least two mechanisms were already elevated at t-1/t-2 in **{summary['episode_first']['at_067']['pre_ge2']}/{len(ep)}** episode starts.",
              f"Allowing same-origin evidence as well, >=1 mechanism appears in **{summary['episode_first']['at_067']['any_ge1']}/{len(ep)}**, >=2 in **{summary['episode_first']['at_067']['any_ge2']}/{len(ep)}**.",
              f"At 0.75, pre-origin >=1 mechanism: **{summary['episode_first']['at_075']['pre_ge1']}/{len(ep)}**; pre-origin >=2: **{summary['episode_first']['at_075']['pre_ge2']}/{len(ep)}**.","",
              "## Strongest current-origin discriminators","",
              "| Feature | Miss mean | Control mean | SMD |",
              "|---|---:|---:|---:|"]
    for r in featdf.head(15).itertuples():
        lines.append(f"| {r.feature} | {r.miss_mean:.3f} | {r.control_mean:.3f} | {r.smd_miss_minus_control:+.3f} |")
    lines += ["","## Episode starts","",
              "| Episode | Start | N origins | Max |H3| | Frag pre | Flow pre | LLRS pre | Reaction pre | #pre >=.67 | #any >=.67 |",
              "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in ep.itertuples():
        def fv(x): return "NA" if not np.isfinite(x) else f"{x:.2f}"
        lines.append(f"| {r.episode} | {r.feature_cutoff_date.date()} | {r.n} | {100*r.max_abs_r3:.2f}% | {fv(r.fragility_score_premax)} | {fv(r.flow_score_premax)} | {fv(r.leadlag_score_premax)} | {fv(r.reaction_score_premax)} | {int(r.mechanism_count_pre_0p67)} | {int(r.mechanism_count_any_0p67)} |")
    lines += ["","## Interpretation discipline","",
              "- A high same-origin score is detection, not necessarily advance warning.",
              "- The key evidence for a usable signal is t-1/t-2 episode-start coverage with materially lower prevalence on correct-continuation controls.",
              "- No threshold in this report is a frozen trading rule.",
              "- TRES is secondary diagnostic context only and is not counted among the four primary mechanism families."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: remaining53-audit-run
