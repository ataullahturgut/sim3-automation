from __future__ import annotations

import io, json, os, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

import gold_short_horizon_global_xau_stage1_r2 as s1

OUT=Path(os.environ.get("OUT_DIR","gold_h3_error_anatomy_out"))
OUT.mkdir(parents=True,exist_ok=True)

REPO="ataullahturgut/sim3-automation"
VANILLA_ARTIFACT=11218958789
CHHHO_ARTIFACT=11219164514
BLOCK=5

CORE3=s1.CORE3
STATE_FEATURES=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21",
    "platinum_r1","platinum_r5","platinum_r21",
]
MODELS=[
    "LOGIT_L2_CORE3",
    "LGBM_CORE3",
    "XGB_CORE3",
    "VANILLA_ANFIS",
    "CHHHO_ANFIS",
]

def artifact_zip(aid:int):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={
        "Authorization":f"Bearer {tok}",
        "Accept":"application/vnd.github+json",
        "User-Agent":"gold-h3-error-anatomy-v1",
    },timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def csv_from_artifact(aid:int,suffix:str)->pd.DataFrame:
    z=artifact_zip(aid)
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1:
        raise RuntimeError((aid,suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def prep_panel():
    df=s1.load_panel()
    for c in CORE3:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    return df

def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "false_call_rate":float(np.mean(pred!=y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "mean_p_up":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
    }

def classical_dev(df):
    dev=df[(df.role=="DEV") & df.target_r3.notna()].copy().reset_index(drop=True)
    rows=[]
    for start in range(0,len(dev),BLOCK):
        te=dev.iloc[start:start+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        mm=s1.mature_mask(df,cutoff,3) & df.target_r3.notna()
        tr=df[mm].copy()
        uptr=(tr.target_r3.astype(float)>0).astype(int)
        upte=(te.target_r3.astype(float)>0).astype(int).to_numpy()
        Xtr,Xte=s1.fill_train_test(tr,te,CORE3)
        for rawname,outname in [
            ("LOGIT_L2","LOGIT_L2_CORE3"),
            ("LGBM_CLASS","LGBM_CORE3"),
            ("XGB_CLASS","XGB_CORE3"),
        ]:
            m=s1.cls_model(rawname)
            m.fit(Xtr,uptr)
            p=m.predict_proba(Xte)[:,1]
            for r,y,pp in zip(te.itertuples(),upte,p):
                rows.append({
                    "forecast_issue_date":str(r.forecast_issue_date.date()),
                    "target_end_date_h3":str(r.target_end_date_h3.date()),
                    "period":"DEV_2022_2024",
                    "year":int(r.forecast_issue_date.year),
                    "model":outname,
                    "y_up":int(y),
                    "p_up":float(pp),
                })
    return pd.DataFrame(rows)

def classical_transport(df):
    eligible=df[df.target_r3.notna() & df.target_end_date_h3.notna()].copy()
    tr=eligible[eligible.target_end_date_h3<=pd.Timestamp("2024-12-31")].copy()
    te=eligible[
        eligible.forecast_issue_date.dt.year.isin([2025,2026]) &
        (eligible.target_end_date_h3<=pd.Timestamp("2026-09-30"))
    ].copy().reset_index(drop=True)
    uptr=(tr.target_r3.astype(float)>0).astype(int)
    upte=(te.target_r3.astype(float)>0).astype(int).to_numpy()
    Xtr,Xte=s1.fill_train_test(tr,te,CORE3)
    rows=[]
    for rawname,outname in [
        ("LOGIT_L2","LOGIT_L2_CORE3"),
        ("LGBM_CLASS","LGBM_CORE3"),
        ("XGB_CLASS","XGB_CORE3"),
    ]:
        m=s1.cls_model(rawname)
        m.fit(Xtr,uptr)
        p=m.predict_proba(Xte)[:,1]
        for r,y,pp in zip(te.itertuples(),upte,p):
            rows.append({
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "period":str(int(r.forecast_issue_date.year)),
                "year":int(r.forecast_issue_date.year),
                "model":outname,
                "y_up":int(y),
                "p_up":float(pp),
            })
    return pd.DataFrame(rows)

def anfis_dev():
    va=csv_from_artifact(VANILLA_ARTIFACT,"anfis_vanilla_dev_predictions.csv")
    ch=csv_from_artifact(CHHHO_ARTIFACT,"anfis_chhho_dev_predictions.csv")
    rows=[]
    for g,pcol,name in [
        (va,"p_anfis","VANILLA_ANFIS"),
        (ch,"p_chhho_anfis","CHHHO_ANFIS"),
    ]:
        for r in g.itertuples():
            rows.append({
                "forecast_issue_date":str(r.forecast_issue_date),
                "target_end_date_h3":str(r.target_end_date_h3),
                "period":"DEV_2022_2024",
                "year":int(str(r.forecast_issue_date)[:4]),
                "model":name,
                "y_up":int(r.y_up),
                "p_up":float(getattr(r,pcol)),
            })
    return pd.DataFrame(rows)

def anfis_transport():
    p=Path("gold_axis_2026/GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_TRANSPORT_PREDICTIONS_2026-10-02.csv")
    g=pd.read_csv(p)
    g=g[g.model.isin(["VANILLA_ANFIS","CHHHO_ANFIS"])].copy()
    g["y_up"]=(g.actual_direction=="UP").astype(int)
    return pd.DataFrame({
        "forecast_issue_date":g.forecast_issue_date.astype(str),
        "target_end_date_h3":g.target_end_date_h3.astype(str),
        "period":g.year.astype(int).astype(str),
        "year":g.year.astype(int),
        "model":g.model.astype(str),
        "y_up":g.y_up.astype(int),
        "p_up":g.p_up.astype(float),
    })

def wide_ledger(long_df,panel):
    w=long_df.pivot_table(
        index=["forecast_issue_date","target_end_date_h3","period","year","y_up"],
        columns="model",values="p_up",aggfunc="first"
    ).reset_index()
    if any(m not in w.columns for m in MODELS):
        raise RuntimeError("MISSING_MODEL_COLUMNS "+str([m for m in MODELS if m not in w.columns]))
    # attach origin-known state
    st=panel.copy()
    st["forecast_issue_date"]=st.forecast_issue_date.dt.strftime("%Y-%m-%d")
    cols=["forecast_issue_date"]+CORE3
    w=w.merge(st[cols],on="forecast_issue_date",how="left",validate="one_to_one")
    for m in MODELS:
        w[f"pred_{m}"]=(w[m]>=.5).astype(int)
        w[f"correct_{m}"]=(w[f"pred_{m}"]==w.y_up)
    preds=np.column_stack([w[f"pred_{m}"].to_numpy(int) for m in MODELS])
    probs=np.column_stack([w[m].to_numpy(float) for m in MODELS])
    w["up_votes"]=preds.sum(axis=1)
    w["up_vote_fraction"]=w.up_votes/len(MODELS)
    w["majority_pred_up"]=(w.up_votes>=3).astype(int)
    w["majority_correct"]=(w.majority_pred_up==w.y_up)
    w["unanimous"]=(w.up_votes.isin([0,len(MODELS)]))
    w["strong_agreement"]=(w.up_votes.isin([0,1,4,5]))
    w["probability_spread"]=np.max(probs,axis=1)-np.min(probs,axis=1)
    w["correct_count"]=np.column_stack([w[f"correct_{m}"] for m in MODELS]).sum(axis=1)
    w["all_wrong"]=(w.correct_count==0)
    w["only_one_correct"]=(w.correct_count==1)
    w["only_one_wrong"]=(w.correct_count==len(MODELS)-1)
    return w

def period_model_metrics(long_df):
    rows=[]
    for period in ["DEV_2022_2024","2025","2026"]:
        q=long_df[long_df.period==period]
        for m,g in q.groupby("model"):
            rows.append({"period":period,"model":m,**metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def consensus_metrics(w):
    rows=[]
    for period in ["DEV_2022_2024","2025","2026"]:
        g=w[w.period==period].copy()
        y=g.y_up.to_numpy(int)
        pmaj=g.up_vote_fraction.to_numpy(float)
        rows.append({"period":period,"scope":"MAJORITY","coverage":1.0,**metrics(y,pmaj)})
        for label,mask in [
            ("UNANIMOUS",g.unanimous.to_numpy(bool)),
            ("STRONG_4_OF_5",g.strong_agreement.to_numpy(bool)),
            ("DISAGREEMENT",(~g.unanimous).to_numpy(bool)),
        ]:
            if mask.sum()==0: continue
            rows.append({
                "period":period,"scope":label,"coverage":float(mask.mean()),
                **metrics(y[mask],pmaj[mask])
            })
    return pd.DataFrame(rows)

def rescue_matrix(w):
    rows=[]
    for period in ["DEV_2022_2024","2025","2026"]:
        g=w[w.period==period]
        for a in MODELS:
            wrong=~g[f"correct_{a}"].to_numpy(bool)
            for b in MODELS:
                if a==b: continue
                if wrong.sum()==0: continue
                gb=g.loc[wrong]
                row={
                    "period":period,"failed_model":a,"rescuer_model":b,
                    "failed_n":int(len(gb)),
                    "rescuer_correct_rate":float(gb[f"correct_{b}"].mean()),
                }
                for side,label in [(1,"actual_up"),(0,"actual_down")]:
                    s=gb[gb.y_up==side]
                    row[f"{label}_n"]=int(len(s))
                    row[f"{label}_rescue_rate"]=None if len(s)==0 else float(s[f"correct_{b}"].mean())
                rows.append(row)
    return pd.DataFrame(rows)

def special_cases(w):
    rows=[]
    for period in ["DEV_2022_2024","2025","2026"]:
        g=w[w.period==period]
        for kind,mask in [
            ("ALL_WRONG",g.all_wrong),
            ("ONLY_ONE_CORRECT",g.only_one_correct),
            ("ONLY_ONE_WRONG",g.only_one_wrong),
        ]:
            for _,r in g[mask].iterrows():
                rec={
                    "period":period,"case":kind,
                    "forecast_issue_date":r.forecast_issue_date,
                    "target_end_date_h3":r.target_end_date_h3,
                    "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                    "up_votes":int(r.up_votes),
                    "probability_spread":float(r.probability_spread),
                }
                if kind=="ONLY_ONE_CORRECT":
                    winners=[m for m in MODELS if bool(r[f"correct_{m}"])]
                    rec["unique_model"]=";".join(winners)
                elif kind=="ONLY_ONE_WRONG":
                    losers=[m for m in MODELS if not bool(r[f"correct_{m}"])]
                    rec["unique_model"]=";".join(losers)
                else:
                    rec["unique_model"]=""
                rows.append(rec)
    return pd.DataFrame(rows)

def standardized_shifts(w):
    rows=[]
    dev=w[w.period=="DEV_2022_2024"].copy()
    mu=dev[STATE_FEATURES].mean()
    sd=dev[STATE_FEATURES].std(ddof=0).replace(0,np.nan)

    groups=[
        ("DEV_ALL_WRONG",dev.all_wrong),
        ("DEV_ONLY_ONE_CORRECT",dev.only_one_correct),
    ]
    # For 2026, compare errors to DEV state reference.
    y26=w[w.period=="2026"].copy()
    groups += [
        ("Y2026_ALL_ROWS",pd.Series(True,index=y26.index)),
        ("Y2026_MAJORITY_WRONG",~y26.majority_correct),
    ]
    for name,mask in groups:
        src=dev if name.startswith("DEV_") else y26
        gg=src.loc[mask]
        if len(gg)==0: continue
        z=(gg[STATE_FEATURES].mean()-mu)/sd
        for f,v in z.items():
            rows.append({
                "group":name,"n":int(len(gg)),"feature":f,
                "standardized_mean_shift_vs_dev":None if pd.isna(v) else float(v),
                "group_mean":float(gg[f].mean()),
                "dev_mean":float(mu[f]),
                "dev_sd":float(sd[f]) if pd.notna(sd[f]) else None,
            })

    # model-specific rescue states on DEV
    for failed in MODELS:
        bad=dev[~dev[f"correct_{failed}"]].copy()
        for rescuer in MODELS:
            if rescuer==failed: continue
            gg=bad[bad[f"correct_{rescuer}"]].copy()
            if len(gg)<10: continue
            z=(gg[STATE_FEATURES].mean()-mu)/sd
            for f,v in z.items():
                rows.append({
                    "group":f"DEV_RESCUE_{failed}_BY_{rescuer}",
                    "n":int(len(gg)),"feature":f,
                    "standardized_mean_shift_vs_dev":None if pd.isna(v) else float(v),
                    "group_mean":float(gg[f].mean()),
                    "dev_mean":float(mu[f]),
                    "dev_sd":float(sd[f]) if pd.notna(sd[f]) else None,
                })
    return pd.DataFrame(rows)

def main():
    panel=prep_panel()

    long=pd.concat([
        classical_dev(panel),
        anfis_dev(),
        classical_transport(panel),
        anfis_transport(),
    ],ignore_index=True)

    # strict duplicate / alignment checks
    counts=long.groupby(["period","model"]).size().unstack(fill_value=0)
    print("COUNTS",counts.to_dict(),flush=True)

    w=wide_ledger(long,panel)
    pm=period_model_metrics(long)
    cm=consensus_metrics(w)
    rm=rescue_matrix(w)
    sc=special_cases(w)
    sh=standardized_shifts(w)

    long.to_csv(OUT/"h3_cross_family_long_predictions.csv",index=False)
    w.to_csv(OUT/"h3_cross_family_wide_ledger.csv",index=False)
    pm.to_csv(OUT/"h3_cross_family_model_metrics.csv",index=False)
    cm.to_csv(OUT/"h3_cross_family_consensus_metrics.csv",index=False)
    rm.to_csv(OUT/"h3_cross_family_rescue_matrix.csv",index=False)
    sc.to_csv(OUT/"h3_cross_family_special_cases.csv",index=False)
    sh.to_csv(OUT/"h3_cross_family_state_shifts.csv",index=False)

    # Compact headline facts.
    devm=pm[pm.period=="DEV_2022_2024"].copy()
    devc=cm[cm.period=="DEV_2022_2024"].copy()
    top_up=devm.sort_values(["up_recall","balanced_accuracy"],ascending=False).iloc[0]
    top_down=devm.sort_values(["down_recall","balanced_accuracy"],ascending=False).iloc[0]
    unanimous=devc[devc.scope=="UNANIMOUS"].iloc[0]
    strong=devc[devc.scope=="STRONG_4_OF_5"].iloc[0]
    majority=devc[devc.scope=="MAJORITY"].iloc[0]

    dev=w[w.period=="DEV_2022_2024"]
    single=sc[(sc.period=="DEV_2022_2024")&(sc.case=="ONLY_ONE_CORRECT")]
    unique_counts=single.unique_model.value_counts().to_dict()
    allwrong=sc[(sc.period=="DEV_2022_2024")&(sc.case=="ALL_WRONG")]

    result={
        "schema":"GOLD_H3_CROSS_FAMILY_ERROR_ANATOMY_V1",
        "models":MODELS,
        "dev_n":int(len(dev)),
        "top_up_specialist":{
            "model":str(top_up.model),
            "up_recall":float(top_up.up_recall),
            "down_recall":float(top_up.down_recall),
            "balanced_accuracy":float(top_up.balanced_accuracy),
        },
        "top_down_specialist":{
            "model":str(top_down.model),
            "up_recall":float(top_down.up_recall),
            "down_recall":float(top_down.down_recall),
            "balanced_accuracy":float(top_down.balanced_accuracy),
        },
        "majority_dev":{
            "accuracy":float(majority.accuracy),
            "balanced_accuracy":float(majority.balanced_accuracy),
        },
        "unanimous_dev":{
            "coverage":float(unanimous.coverage),
            "accuracy":float(unanimous.accuracy),
            "balanced_accuracy":float(unanimous.balanced_accuracy),
        },
        "strong_4_of_5_dev":{
            "coverage":float(strong.coverage),
            "accuracy":float(strong.accuracy),
            "balanced_accuracy":float(strong.balanced_accuracy),
        },
        "dev_common_failure_n":int(dev.all_wrong.sum()),
        "dev_only_one_correct_n":int(dev.only_one_correct.sum()),
        "dev_unique_rescuer_counts":unique_counts,
        "dev_common_failure_dates":allwrong.forecast_issue_date.tolist(),
    }
    (OUT/"h3_cross_family_error_anatomy_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD H3 — CROSS-FAMILY ERROR ANATOMY V1","",
        "Diagnostic only. No router was fit in this stage.","",
        "## DEV side-specific anatomy (2022-2024)","",
        "| Model | Accuracy | Balanced acc | UP recall | DOWN recall | Brier |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _,r in devm.sort_values("balanced_accuracy",ascending=False).iterrows():
        lines.append(
            f"| {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    lines += [
        "",
        f"UP specialist: **{top_up.model}** ({100*top_up.up_recall:.2f}% UP recall).",
        f"DOWN specialist: **{top_down.model}** ({100*top_down.down_recall:.2f}% DOWN recall).",
        "",
        "## Consensus",
        "",
        "| Scope | Coverage | Accuracy | Balanced acc |",
        "|---|---:|---:|---:|",
    ]
    for scope in ["MAJORITY","STRONG_4_OF_5","UNANIMOUS","DISAGREEMENT"]:
        r=devc[devc.scope==scope].iloc[0]
        lines.append(f"| {scope} | {100*r.coverage:.2f}% | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% |")
    lines += [
        "",
        f"DEV all-five-wrong rows: **{int(dev.all_wrong.sum())}**.",
        f"DEV exactly-one-correct rows: **{int(dev.only_one_correct.sum())}**.",
        f"Unique rescuer counts: \`{json.dumps(unique_counts,sort_keys=True)}\`.",
        "",
        "## Transport headline",
        "",
        "| Period | Model | Accuracy | Balanced acc | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for period in ["2025","2026"]:
        for _,r in pm[pm.period==period].sort_values("balanced_accuracy",ascending=False).iterrows():
            lines.append(
                f"| {period} | {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )
    lines += [
        "",
        "State-shift, rescue-matrix and exact special-case ledgers are written to separate CSV files.",
        "No model architecture is changed by this diagnostic.",
    ]
    (OUT/"H3_CROSS_FAMILY_ERROR_ANATOMY_RESULT.md").write_text("\n".join(lines)+"\n")
    print("H3_ERROR_ANATOMY_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"H3_CROSS_FAMILY_ERROR_ANATOMY_RESULT.md").read_text())

if __name__=="__main__":
    main()
