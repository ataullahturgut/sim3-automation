from pathlib import Path
import importlib.util, json, math
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"
RTEF=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

OUT_MD=AX/"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_SUMMARY_2026-10-04.json"
OUT_GRID=AX/"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_2025_GRID_2026-10-04.csv"
OUT_ACTIONS=AX/"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_2026_ACTIONS_2026-10-04.csv"
OUT_SCORES=AX/"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_SCORES_2026-10-04.csv"

QLEVELS=[0.80,0.85,0.90,0.95]

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec); spec.loader.exec_module(hsm)

def safe_num(s): return pd.to_numeric(s,errors="coerce")

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float((up+dn)/2)}

def build_frame():
    h=hsm.load_frame().sort_values("feature_cutoff_date").reset_index(drop=True)
    rf=pd.read_csv(RTEF,parse_dates=["feature_cutoff_date"])
    dv=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"])
    add_r=["feature_cutoff_date","opposite_semivar_share","path_consistency","signed_opt_pressure",
           "signed_d_opt_pressure","opt_total_z20","gc_volume_z20","gc_volume_accel_5"]
    add_d=["feature_cutoff_date","core_confirmation","cross_dispersion"]
    z=h.merge(rf[add_r],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.merge(dv[add_d],on="feature_cutoff_date",how="left",validate="one_to_one")
    z["abs_h_ret_12"]=safe_num(z.h_ret_12).abs()
    z["reversal_target"]=(z.y_up.astype(int)!=z.momentum_up.astype(int)).astype(int)
    # trend age: consecutive origins with same momentum state
    age=[]; prev=None; run=0
    for m in z.momentum_up.astype(int):
        if prev is None or m!=prev: run=1
        else: run+=1
        age.append(run); prev=m
    z["trend_age"]=age
    # topology dynamics
    z["ndx_r60_d1"]=safe_num(z.ndx_r60)-safe_num(z.ndx_r60).shift(1)
    z["vix_r60_d1"]=safe_num(z.vix_r60)-safe_num(z.vix_r60).shift(1)
    z["topology_rotation"]=np.sqrt(z.ndx_r60_d1**2+z.vix_r60_d1**2)
    # structural deltas
    for c in ["trend_strength","adverse_excursion","path_consistency","opposite_semivar_share",
              "signed_opt_pressure","core_confirmation","cross_dispersion"]:
        z[f"{c}_d1"]=safe_num(z[c])-safe_num(z[c]).shift(1)
        z[f"{c}_d3"]=safe_num(z[c])-safe_num(z[c]).shift(3)
    z["handoff_confirm"]=(safe_num(z.leadlag_score_premax)>=.60)&(safe_num(z.internal_now)>=.60)&(safe_num(z.internal_d1)>=0)
    return z

CP_FEATURES=["abs_h_ret_12","trend_strength","adverse_excursion","path_consistency",
             "signed_opt_pressure","opt_total_z20","gc_volume_z20","core_confirmation","cross_dispersion"]

SELLR_FEATURES=[
    ("adverse_excursion",1.0),
    ("trend_strength",-1.0),
    ("trend_close_location",-1.0),
    ("session_against_trend",1.0),
    ("opposite_semivar_share",1.0),
    ("signed_opt_pressure",1.0),
    ("signed_d_opt_pressure",1.0),
    ("core_confirmation",-1.0),
    ("cross_dispersion",1.0),
    ("topology_rotation",1.0),
    ("trend_age",1.0),
]

HAZ_FEATURES=["log_trend_age","abs_h_ret_12","trend_strength","adverse_excursion","path_consistency",
              "signed_opt_pressure","opt_total_z20","core_confirmation","cross_dispersion","mcp_score"]

ANALOG_FEATURES=["abs_h_ret_12","trend_strength","adverse_excursion","path_consistency","opposite_semivar_share",
                 "session_against_trend","trend_close_location","signed_opt_pressure","signed_d_opt_pressure",
                 "opt_total_z20","gc_volume_z20","gc_volume_accel_5","core_confirmation","cross_dispersion",
                 "topology_rotation","trend_age"]

def mcp_scores(z):
    vals=z[CP_FEATURES].apply(pd.to_numeric,errors="coerce")
    out=np.full(len(z),np.nan)
    for i in range(len(z)):
        if i<45: continue
        ref=vals.iloc[max(0,i-65):i-5].copy()
        recent=vals.iloc[max(0,i-4):i+1].copy()
        if len(ref)<40 or len(recent)<3: continue
        med=ref.median()
        mad=(ref-med).abs().median()*1.4826
        mad=mad.replace(0,np.nan)
        # fallback std where MAD degenerates
        std=ref.std(ddof=0).replace(0,np.nan)
        scale=mad.fillna(std).fillna(1.0)
        rz=(recent-med)/scale
        shift=rz.mean(axis=0,skipna=True)
        if shift.notna().sum()<6: continue
        out[i]=float(np.sqrt(np.nansum(shift.to_numpy(float)**2)))
    return out

def fit_sellr(z,trainmask):
    train=z[trainmask].copy()
    spec={}
    for c,sgn in SELLR_FEATURES:
        x=safe_num(train[c])*sgn
        med=float(x.median())
        x=x.fillna(med)
        edges=np.unique(np.quantile(x,[0,.2,.4,.6,.8,1.0]))
        if len(edges)<3:
            lo=float(x.min()); hi=float(x.max())
            edges=np.array([lo-1e-9,(lo+hi)/2,hi+1e-9])
        else:
            edges[0]-=1e-9; edges[-1]+=1e-9
        bins=np.clip(np.digitize(x,edges[1:-1],right=False),0,len(edges)-2)
        y=train.reversal_target.astype(int).to_numpy()
        k=len(edges)-1
        llr=[]
        for bidx in range(k):
            nr=int(((bins==bidx)&(y==1)).sum()); nc=int(((bins==bidx)&(y==0)).sum())
            pr=(nr+1)/(int((y==1).sum())+k)
            pc=(nc+1)/(int((y==0).sum())+k)
            llr.append(float(np.log(pr/pc)))
        spec[c]={"sign":sgn,"median":med,"edges":edges.tolist(),"llr":llr}
    return spec

def apply_sellr(z,spec):
    score=np.zeros(len(z),float)
    valid=np.zeros(len(z),int)
    for c,s in spec.items():
        x=safe_num(z[c])*s["sign"]
        x=x.fillna(s["median"]).to_numpy(float)
        edges=np.asarray(s["edges"],float)
        bins=np.clip(np.digitize(x,edges[1:-1],right=False),0,len(edges)-2)
        score+=np.asarray(s["llr"])[bins]
        valid+=1
    score[valid==0]=np.nan
    return score

def prep_matrix(df,features,fit=None):
    X=df[features].apply(pd.to_numeric,errors="coerce").copy()
    if fit is None:
        med=X.median()
        X=X.fillna(med)
        scaler=StandardScaler().fit(X)
        return scaler.transform(X),{"median":med.to_dict(),"scaler":scaler}
    med=pd.Series(fit["median"])
    X=X.fillna(med)
    return fit["scaler"].transform(X)

def action_stats(df,mask):
    q=df[mask].copy()
    actions=len(q); rescue=int((~q.baseline_correct).sum()); broken=int(q.baseline_correct.sum())
    net=rescue-broken; precision=rescue/actions if actions else 0.0; rate=actions/max(len(df),1)
    monthly={}
    if actions:
        qq=q.assign(net=np.where(q.baseline_correct,-1,1),month=q.feature_cutoff_date.dt.to_period("M").astype(str))
        monthly=qq.groupby("month").net.sum().to_dict()
    nonneg=sum(v>=0 for v in monthly.values())/len(monthly) if monthly else 0.0
    worst=min(monthly.values()) if monthly else 0
    return {"actions":int(actions),"rescue":rescue,"broken":broken,"net":int(net),"precision":float(precision),
            "rate":float(rate),"nonnegative_action_month_share":float(nonneg),"worst_action_month_net":int(worst),
            "monthly_net":monthly}

def eligible(st):
    return st["actions"]>=6 and st["precision"]>=.60 and st["net"]>0 and st["rate"]<=.15 and st["nonnegative_action_month_share"]>=.70 and st["worst_action_month_net"]>=-1

def select_variant(dev,score_col,train_scores,family):
    qs={q:float(np.nanquantile(train_scores,q)) for q in QLEVELS}
    rows=[]
    for handoff in [False,True]:
        for q,thr in qs.items():
            m=dev[score_col].notna()&(dev[score_col]>=thr)&(dev.baseline_pred.astype(int)==dev.momentum_up.astype(int))
            if handoff: m=m&dev.handoff_confirm
            st=action_stats(dev,m)
            rows.append({"family":family,"quantile":q,"threshold":thr,"handoff":handoff,
                         **{k:v for k,v in st.items() if k!="monthly_net"},
                         "monthly_net_json":json.dumps(st["monthly_net"],sort_keys=True),
                         "eligible":eligible(st)})
    g=pd.DataFrame(rows)
    eg=g[g.eligible].copy()
    sel=None
    if len(eg):
        eg["handoff_pref"]=eg.handoff.astype(int)
        eg=eg.sort_values(["net","precision","actions","quantile","handoff_pref"],ascending=[False,False,True,False,False])
        sel=eg.iloc[0].to_dict()
    return g,sel

def mechanism_mask(df,score_col,sel):
    m=df[score_col].notna()&(df[score_col]>=float(sel["threshold"]))&(df.baseline_pred.astype(int)==df.momentum_up.astype(int))
    if bool(sel["handoff"]): m=m&df.handoff_confirm
    return m

def main():
    z=build_frame()
    z["mcp_score"]=mcp_scores(z)
    z["log_trend_age"]=np.log1p(z.trend_age.astype(float))

    train=(z.feature_cutoff_date.dt.year.isin([2023,2024]))
    train_valid=train & z.mcp_score.notna()
    if train_valid.sum()<300: raise RuntimeError("Insufficient 2023-24 training rows")

    # SELLR
    sellr_spec=fit_sellr(z,train)
    z["sellr_score"]=apply_sellr(z,sellr_spec)

    # Hazard
    htrain=z[train_valid].copy()
    Xh,prep_h=prep_matrix(htrain,HAZ_FEATURES)
    yh=htrain.reversal_target.astype(int).to_numpy()
    haz=LogisticRegression(C=1.0,class_weight="balanced",max_iter=5000,random_state=20261004)
    haz.fit(Xh,yh)
    z["haz_score"]=haz.predict_proba(prep_matrix(z,HAZ_FEATURES,prep_h))[:,1]

    # Analog
    atrain=z[train & z[ANALOG_FEATURES].notna().sum(axis=1).ge(8)].copy()
    Xa,prep_a=prep_matrix(atrain,ANALOG_FEATURES)
    ya=atrain.reversal_target.astype(int).to_numpy()
    nn=NearestNeighbors(n_neighbors=26,metric="euclidean").fit(Xa)
    Xall=prep_matrix(z,ANALOG_FEATURES,prep_a)
    dist,idx=nn.kneighbors(Xall,n_neighbors=26)
    scores=[]
    train_dates=set(atrain.feature_cutoff_date)
    for i,row in z.iterrows():
        inds=list(idx[i])
        # Leave self out for training-date diagnostics.
        if row.feature_cutoff_date in train_dates:
            inds=[j for j in inds if atrain.iloc[j].feature_cutoff_date!=row.feature_cutoff_date][:25]
        else:
            inds=inds[:25]
        scores.append(float(np.mean(ya[inds])) if inds else np.nan)
    z["analog_score"]=scores

    score_cols={"MCP":"mcp_score","SELLR":"sellr_score","HAZ":"haz_score","ANALOG":"analog_score"}

    dev=z[z.feature_cutoff_date.dt.year==2025].copy()
    grids=[]; selected={}
    for fam,col in score_cols.items():
        ts=z.loc[train & z[col].notna(),col].to_numpy(float)
        g,sel=select_variant(dev,col,ts,fam)
        grids.append(g)
        if sel is not None: selected[fam]=sel
    grid=pd.concat(grids,ignore_index=True)

    # Consensus2 from selected family rules, evaluated on 2025 before opening 2026.
    consensus_sel=None
    if len(selected)>=2:
        votes=np.zeros(len(dev),int)
        for fam,sel in selected.items():
            votes+=mechanism_mask(dev,score_cols[fam],sel).to_numpy(int)
        cm=pd.Series(votes>=2,index=dev.index)
        cst=action_stats(dev,cm)
        if eligible(cst):
            consensus_sel={"family":"CONSENSUS2",**{k:v for k,v in cst.items() if k!="monthly_net"},
                           "monthly_net":cst["monthly_net"],"members":list(selected.keys())}

    # Finalists and winner selected only on 2025.
    finalists=[]
    for fam,sel in selected.items():
        finalists.append({"family":fam,"net":int(sel["net"]),"precision":float(sel["precision"]),"actions":int(sel["actions"]),
                          "ba_gain":np.nan})
    if consensus_sel:
        finalists.append({"family":"CONSENSUS2","net":consensus_sel["net"],"precision":consensus_sel["precision"],
                          "actions":consensus_sel["actions"],"ba_gain":np.nan})
    winner=None
    if finalists:
        finalists=sorted(finalists,key=lambda r:(-r["net"],-r["precision"],r["actions"],r["family"]))
        winner=finalists[0]["family"]

    # Frozen 2026 stress of all 2025-eligible finalists.
    test=z[z.feature_cutoff_date.dt.year==2026].copy().reset_index(drop=True)
    if len(test)!=191: raise RuntimeError(f"Expected 191 2026 rows, got {len(test)}")
    if int(test.baseline_correct.sum())!=126: raise RuntimeError(f"Expected baseline 126/191, got {int(test.baseline_correct.sum())}")
    base=confusion(test.y_up,test.baseline_pred)
    stress={}
    masks={}
    for fam,sel in selected.items():
        masks[fam]=mechanism_mask(test,score_cols[fam],sel)
    if consensus_sel:
        votes=np.zeros(len(test),int)
        for fam in consensus_sel["members"]: votes+=masks[fam].to_numpy(int)
        masks["CONSENSUS2"]=pd.Series(votes>=2,index=test.index)

    action_rows=[]
    remaining53=(~test.baseline_correct)&test.is_reversal
    for fam,m in masks.items():
        st=action_stats(test,m)
        assisted=test.baseline_pred.to_numpy(int).copy()
        assisted[m.to_numpy()]=1-assisted[m.to_numpy()]
        ass=confusion(test.y_up,assisted)
        # episode starts among remaining reversal errors
        rr=test[remaining53].copy()
        episode=[]; ep=0; prev=None
        for d in rr.feature_cutoff_date:
            if prev is None or (d-prev).days>4: ep+=1
            episode.append(ep); prev=d
        rr["episode"]=episode
        first=set(rr.groupby("episode").feature_cutoff_date.min())
        ep_first=int((m & test.feature_cutoff_date.isin(first)).sum())
        stress[fam]={"action_stats":st,"assisted":ass,
                     "remaining53_rescued":int((m&remaining53).sum()),
                     "episode_first_rescued":ep_first,
                     "overlap_sage":int((m&test.sage_flip).sum()),
                     "overlap_ruleflow":int((m&test.ruleflow_flip).sum())}
        q=test[m].copy()
        q["family"]=fam
        q["outcome"]=np.where(q.baseline_correct,"BROKEN","RESCUE")
        action_rows.append(q)

    act=pd.concat(action_rows,ignore_index=True) if action_rows else pd.DataFrame()
    if len(act):
        cols=["family","feature_cutoff_date","forecast_issue_date","target_end_date_h3","momentum_up","y_up","target_r3",
              "baseline_pred","baseline_correct","handoff_confirm","mcp_score","sellr_score","haz_score","analog_score","outcome"]
        act[cols].to_csv(OUT_ACTIONS,index=False)
    else: pd.DataFrame().to_csv(OUT_ACTIONS,index=False)

    z[["feature_cutoff_date","y_up","momentum_up","reversal_target","baseline_pred","baseline_correct","handoff_confirm",
       "mcp_score","sellr_score","haz_score","analog_score"]].to_csv(OUT_SCORES,index=False)
    grid.to_csv(OUT_GRID,index=False)

    summary={
      "schema":"GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1",
      "status":"NO_2025_ELIGIBLE_FINALIST" if winner is None else "WINNER_FROZEN_2026_STRESSED",
      "train_2023_2024_n":int(train.sum()),
      "dev_2025_n":int(len(dev)),
      "baseline_2026":base,
      "selected_2025":selected,
      "consensus_2025":consensus_sel,
      "finalists_2025":finalists,
      "winner":winner,
      "stress_2026":stress,
      "hazard_coefficients":{f:float(c) for f,c in zip(HAZ_FEATURES,haz.coef_[0])},
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Reversal Mechanism Tournament V1 Result","",
           "**Status:** "+summary["status"],"",
           "## Design","",
           "- 2023-2024: mechanism construction / fitting",
           "- 2025: eligibility and threshold selection",
           "- 2026: frozen retrospective stress",
           "- No 2026 label enters fitting or selection.","",
           "## 2025 fixed-grid results","",
           "| Family | Q | Handoff | Actions | Rescue | Broken | Net | Precision | Eligible |",
           "|---|---:|---|---:|---:|---:|---:|---:|---|"]
    for r in grid.sort_values(["family","eligible","net","precision"],ascending=[True,False,False,False]).itertuples():
        lines.append(f"| {r.family} | {r.quantile:.2f} | {r.handoff} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% | {r.eligible} |")
    lines += ["","## 2025 selected finalists",""]
    if not finalists:
        lines.append("No mechanism passed the preregistered 2025 eligibility gate.")
    else:
        lines += ["| Finalist | Net | Precision | Actions |","|---|---:|---:|---:|"]
        for r in finalists:
            lines.append(f"| {r['family']} | {r['net']:+d} | {100*r['precision']:.1f}% | {r['actions']} |")
        lines += ["",f"Frozen tournament winner: **{winner}**","",
                  "## Frozen 2026 stress","",
                  "| Family | Actions | Rescue | Broken | Net | Precision | Remaining-53 rescued | Episode starts | Accuracy | BA |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for fam,s in stress.items():
            st=s["action_stats"]; ass=s["assisted"]
            lines.append(f"| {fam} | {st['actions']} | {st['rescue']} | {st['broken']} | {st['net']:+d} | {100*st['precision']:.1f}% | {s['remaining53_rescued']} | {s['episode_first_rescued']} | {100*ass['accuracy']:.2f}% | {100*ass['balanced_accuracy']:.2f}% |")
        if winner in stress:
            s=stress[winner]
            lines += ["",f"### Winner — {winner}","",
                      f"- combined baseline: **{base['correct']}/{base['n']} = {100*base['accuracy']:.2f}%**, BA **{100*base['balanced_accuracy']:.2f}%**",
                      f"- assisted: **{s['assisted']['correct']}/{s['assisted']['n']} = {100*s['assisted']['accuracy']:.2f}%**, BA **{100*s['assisted']['balanced_accuracy']:.2f}%**",
                      f"- net rescue: **{s['action_stats']['net']:+d}**",
                      f"- remaining-53 rescued: **{s['remaining53_rescued']}**",
                      f"- episode-first rescues: **{s['episode_first_rescued']}**"]
    lines += ["","## Hazard coefficients (standardized features)","",
              "| Feature | Coefficient |","|---|---:|"]
    for f,c in sorted(summary["hazard_coefficients"].items(),key=lambda kv:-abs(kv[1])):
        lines.append(f"| {f} | {c:+.3f} |")
    lines += ["","## Interpretation discipline","",
              "- This tournament deliberately tests multiple causal/statistical stories rather than repeatedly retuning one gate.",
              "- 2025 determines eligibility; 2026 is not used to rescue a failed mechanism.",
              "- Because the project focus arose from retrospective 2026 errors, even a positive 2026 stress remains retrospective evidence, not pristine prospective validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
