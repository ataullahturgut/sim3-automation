import os, io, json, math, hashlib, zipfile, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, average_precision_score, roc_auc_score

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
OUT=Path(os.environ.get("OUT_DIR","stage4_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001

ART={
    "stage2":11161358194,
    "stage3":11163151830,
    "hist":11088508878,
    "router":11124892942,
    "regime":11101827380,
    "transition":11114806383,
    "extreme":11115570221,
}
G_ONLY=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21",
    "sigma20","rv20","absret20","dd_high21","dist_low21","reversal_1_vs_5"
]
BLOCK_MIN_REL=60

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def get_zip(artifact_id):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{artifact_id}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"gold-intramonth-stage4"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv_from(z,endswith):
    names=[n for n in z.namelist() if n.endswith(endswith)]
    if len(names)!=1: raise RuntimeError((endswith,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def read_json_from(z):
    names=[n for n in z.namelist() if n.endswith(".json")]
    if len(names)!=1: raise RuntimeError(names)
    return json.loads(z.read(names[0]))

def load_all():
    z2=get_zip(ART["stage2"])
    df=read_csv_from(z2,"intramonth_opportunity_stage2_dataset.csv")
    df["origin_date"]=pd.to_datetime(df["origin_date"])
    df["signal_date"]=pd.to_datetime(df["signal_date"])
    df=df.sort_values("origin_date").reset_index(drop=True)
    df["label_end_date"]=df["origin_date"].shift(-5)

    z3=get_zip(ART["stage3"])
    p3=read_csv_from(z3,"stage3_dev_predictions_long.csv")
    p3["origin_date"]=pd.to_datetime(p3["origin_date"])
    p3["signal_date"]=pd.to_datetime(p3["signal_date"])
    core=p3[
        (p3["kind"]=="cls") &
        (p3["feature_block"]=="G_ONLY") &
        (p3["target"]=="opp5_k100") &
        (p3["model"]=="HGB_CLASS")
    ].copy()
    if len(core)!=749: raise RuntimeError(f"core rows {len(core)}")

    hist=read_json_from(get_zip(ART["hist"]))
    router=read_json_from(get_zip(ART["router"]))
    regime=read_json_from(get_zip(ART["regime"]))
    transition=read_json_from(get_zip(ART["transition"]))
    extreme=read_json_from(get_zip(ART["extreme"]))
    return df,core,hist,router,regime,transition,extreme

def make_core():
    return HistGradientBoostingClassifier(
        learning_rate=0.05,max_iter=100,max_leaf_nodes=7,max_depth=3,
        min_samples_leaf=40,l2_regularization=1.0,random_state=SEED
    )

def fill(train,test,features):
    a=train[features].copy(); b=test[features].copy()
    for c in features:
        med=a[c].median(skipna=True)
        v=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(v); b[c]=b[c].fillna(v)
    return a,b

def predev_core(df, monthly_valid):
    # valid same-method H2 target months only: 2021-11..2022-03
    ev=df[df["signal_month"].isin(monthly_valid)].copy()
    ev=ev[ev["signal_date"]<pd.Timestamp("2022-04-01")].copy()
    rows=[]
    inds=list(ev.index)
    for j in range(0,len(inds),5):
        bi=inds[j:j+5]
        te=df.loc[bi].copy()
        start=te["origin_date"].min()
        tr=df[
            df["label_end_date"].notna() &
            (df["label_end_date"]<=start) &
            df["opp5_k100"].notna() &
            (df["signal_date"]<pd.Timestamp("2025-01-01"))
        ].copy()
        Xtr,Xte=fill(tr,te,G_ONLY)
        m=make_core()
        m.fit(Xtr,tr["opp5_k100"].astype(int))
        pp=m.predict_proba(Xte)[:,1]
        for ix,p in zip(bi,pp):
            rows.append({
                "row_index":int(ix),"origin_date":df.at[ix,"origin_date"],
                "signal_date":df.at[ix,"signal_date"],"signal_month":df.at[ix,"signal_month"],
                "y":float(df.at[ix,"opp5_k100"]),"core_p":float(p),
                "block_start_origin":start
            })
    return pd.DataFrame(rows)

def monthly_forecast_context(df,hist):
    # H2 valid same-method preDEV
    rows=[]
    for r in hist["all_rows"]:
        if r.get("source")=="H2_VALID_SAME_METHOD_PREDEV":
            rows.append({
                "target_month":r["target"],"origin_month":r["origin"],
                "monthly_pred_log_return":float(r["pred_log_return_gold"]),
                "monthly_down":1 if float(r["pred_log_return_gold"])<0 else 0,
                "monthly_forecast":float(r["forecast"]),"monthly_origin_level":float(r["rw"]),
                "monthly_source":"H2_VALID_SAME_METHOD_PREDEV"
            })
    # H3 from stage2 dataset unique monthly context columns
    q=df[(df["block"]=="dev") & df["target_month"].notna()].copy()
    q=q.sort_values("signal_date").drop_duplicates("target_month")
    for _,r in q.iterrows():
        rows.append({
            "target_month":r["target_month"],"origin_month":r["origin_month"],
            "monthly_pred_log_return":float(r["pred_log_return_gold"]),
            "monthly_down":1 if r["monthly_direction"]=="DOWN" else 0,
            "monthly_forecast":float(r["monthly_forecast"]),
            "monthly_origin_level":float(r["monthly_rw"]),
            "monthly_source":"H3_CANONICAL_DEV"
        })
    c=pd.DataFrame(rows).drop_duplicates("target_month",keep="last").sort_values("target_month")
    c["monthly_abs_pred_log_return"]=c["monthly_pred_log_return"].abs()
    return c

def router_context(router):
    rows=router["periods"]["DEV_2022_04_2024_12"]["rows"]
    return pd.DataFrame([{
        "target_month":r["target"],
        "raw_t0_standard":int(bool(r["raw_T0_STANDARD"])),
        "router_context_available":1
    } for r in rows])

def state_context(regime,transition,extreme,months):
    rg={r["month"]:r for r in regime["walkforward_months"]}
    tr={r["month"]:r for r in transition["rows"]["EXPANDING_REFIT"]}
    ex={r["month"]:r for r in extreme["rows"]["EXPANDING_REFIT"]}
    rows=[]
    for origin_month in sorted(set(months)):
        rr=rg.get(origin_month); tt=tr.get(origin_month); ee=ex.get(origin_month)
        if rr is None: continue
        label=rr.get("live_label") or rr.get("live_display_label")
        x={
            "origin_month":origin_month,
            "state_R0":int(label=="R0"),"state_R1":int(label=="R1"),
            "state_R2":int(label=="R2"),"state_BELIRSIZ":int(label=="BELIRSIZ"),
            "state_probability":float(rr.get("live_probability",np.nan)),
            "state_ood":int(bool(rr.get("live_ood",False))),
            "state_transition":int(bool(tt.get("transition_flag",False))) if tt else 0,
            "state_extreme":int((ee or {}).get("extreme_status")=="EXTREME"),
            "state_defer":int((ee or {}).get("extreme_status")=="DEFER"),
        }
        rows.append(x)
    return pd.DataFrame(rows)

def logit(p):
    p=np.clip(np.asarray(p,float),1e-5,1-1e-5)
    return np.log(p/(1-p))

def overlay_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,l1_ratio=0.0,solver="lbfgs",max_iter=1000,random_state=SEED))
    ])

def metrics(z,pcol):
    y=z["y"].to_numpy(float); p=np.clip(z[pcol].to_numpy(float),1e-6,1-1e-6)
    out={
        "n":int(len(z)),"prevalence":float(np.mean(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "prediction_mean":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
    }
    try: out["pr_auc"]=float(average_precision_score(y,p))
    except: out["pr_auc"]=None
    try: out["roc_auc"]=float(roc_auc_score(y,p))
    except: out["roc_auc"]=None
    return out

def overlay_predict(context, dev, feature_cols, require_router=False):
    out=[]
    # preserve original Stage3 block boundaries
    for block_id in sorted(dev["block_id"].unique()):
        te=dev[dev["block_id"]==block_id].copy()
        if te.empty: continue
        start=pd.to_datetime(te["block_start_origin"].iloc[0])
        tr=context[
            (context["label_end_date"].notna()) &
            (context["label_end_date"]<=start) &
            context["y"].notna()
        ].copy()
        if require_router:
            tr=tr[tr["router_context_available"]==1].copy()
            if len(tr)<BLOCK_MIN_REL:
                q=te.copy(); q["overlay_p"]=q["core_p"]; q["overlay_fallback"]=1
                out.append(q); continue
        # context rows missing needed features are excluded, not future-imputed
        tr=tr.dropna(subset=feature_cols)
        if len(tr)<60 or tr["y"].nunique()<2:
            q=te.copy(); q["overlay_p"]=q["core_p"]; q["overlay_fallback"]=1
            out.append(q); continue
        Xtr=tr[feature_cols].astype(float)
        Xte=te[feature_cols].astype(float)
        m=overlay_model(); m.fit(Xtr,tr["y"].astype(int))
        pp=m.predict_proba(Xte)[:,1]
        q=te.copy(); q["overlay_p"]=pp; q["overlay_fallback"]=0
        out.append(q)
    return pd.concat(out,ignore_index=True)

def main():
    df,core,hist,router,regime,transition,extreme=load_all()
    mf=monthly_forecast_context(df,hist)
    rt=router_context(router)
    st=state_context(regime,transition,extreme,mf["origin_month"].tolist())

    # Build exact Stage4 DEV using frozen Stage3 predictions and monthly target context.
    core=core.merge(df[["origin_date","label_end_date"]],on="origin_date",how="left")
    core=core.rename(columns={"prediction":"core_p"})
    core["target_month"]=core["signal_date"].dt.to_period("M").astype(str)
    dev=core.merge(mf,on="target_month",how="left")
    dev=dev[dev["target_month"].between("2022-04","2024-12")].copy()
    if len(dev)!=685: raise RuntimeError(f"Stage4 dev expected 685 got {len(dev)}")
    dev=dev.merge(rt,on="target_month",how="left")
    dev=dev.merge(st,on="origin_month",how="left")

    # PreDEV core/context H2
    h2months=mf[mf["monthly_source"]=="H2_VALID_SAME_METHOD_PREDEV"]["target_month"].tolist()
    pre=predev_core(df,h2months)
    pre=pre.merge(df[["origin_date","label_end_date"]],on="origin_date",how="left")
    pre["target_month"]=pre["signal_month"]
    pre=pre.merge(mf,on="target_month",how="left")
    pre["raw_t0_standard"]=np.nan
    pre["router_context_available"]=0
    pre=pre.merge(st,on="origin_month",how="left")

    # Normalize y/block fields in DEV
    dev["y"]=dev["y"].astype(float)
    dev["core_p"]=dev["core_p"].astype(float)
    dev["block_start_origin"]=pd.to_datetime(dev["block_start_origin"])
    pre["block_id"]=-1
    pre["block_start_origin"]=pd.to_datetime(pre["block_start_origin"])
    context=pd.concat([pre,dev],ignore_index=True,sort=False)
    context["core_logit"]=logit(context["core_p"])
    dev["core_logit"]=logit(dev["core_p"])

    context.to_csv(OUT/"stage4_context_audit_table.csv",index=False)

    blocks={
        "CORE_DIR":["core_logit","monthly_down"],
        "CORE_MAG":["core_logit","monthly_pred_log_return","monthly_abs_pred_log_return"],
        "CORE_DIR_MAG":["core_logit","monthly_down","monthly_pred_log_return","monthly_abs_pred_log_return"],
        "CORE_DIR_MAG_T0REL":["core_logit","monthly_down","monthly_pred_log_return","monthly_abs_pred_log_return","raw_t0_standard"],
        "CORE_DIR_MAG_STATE":["core_logit","monthly_down","monthly_pred_log_return","monthly_abs_pred_log_return",
                              "state_R0","state_R1","state_R2","state_BELIRSIZ","state_probability","state_ood",
                              "state_transition","state_extreme","state_defer"],
        "CORE_ALL_SAFE":["core_logit","monthly_down","monthly_pred_log_return","monthly_abs_pred_log_return","raw_t0_standard",
                         "state_R0","state_R1","state_R2","state_BELIRSIZ","state_probability","state_ood",
                         "state_transition","state_extreme","state_defer"],
    }
    preds=[dev.assign(context_block="CORE_ONLY",overlay_p=dev["core_p"],overlay_fallback=0)]
    for name,cols in blocks.items():
        print("RUN",name,flush=True)
        z=overlay_predict(context,dev,cols,require_router=("T0REL" in name or name=="CORE_ALL_SAFE"))
        z["context_block"]=name
        preds.append(z)
    allp=pd.concat(preds,ignore_index=True)
    allp.to_csv(OUT/"stage4_dev_predictions.csv",index=False)

    corem=metrics(dev,"core_p")
    rows=[]
    slice_rows=[]
    year_rows=[]
    for name,z in allp.groupby("context_block"):
        mm=metrics(z,"overlay_p")
        rb=(corem["brier"]-mm["brier"])/corem["brier"]
        rll=(corem["logloss"]-mm["logloss"])/corem["logloss"]
        # DOWN/UP
        downs=z[z["monthly_down"]==1]; ups=z[z["monthly_down"]==0]
        dm=metrics(downs,"overlay_p"); um=metrics(ups,"overlay_p")
        core_down=metrics(dev[dev["monthly_down"]==1],"core_p")
        down_rel=(core_down["brier"]-dm["brier"])/core_down["brier"]
        gate=(name!="CORE_ONLY" and rb>=0.01 and mm["logloss"]<=corem["logloss"] and down_rel>=-0.01)
        rows.append({
            "context_block":name,**mm,
            "relative_brier_improvement_vs_core":rb,
            "relative_logloss_improvement_vs_core":rll,
            "down_relative_brier_improvement_vs_core":down_rel,
            "fallback_rows":int(z["overlay_fallback"].sum()),
            "scientific_gate":"PASS" if gate else ("BASE" if name=="CORE_ONLY" else "FAIL")
        })
        for lab,zz in [("DOWN",downs),("UP",ups)]:
            sm=metrics(zz,"overlay_p")
            cb=metrics(dev[dev["monthly_down"]==(1 if lab=="DOWN" else 0)],"core_p")
            slice_rows.append({
                "context_block":name,"slice":lab,**sm,
                "relative_brier_improvement_vs_core":(cb["brier"]-sm["brier"])/cb["brier"],
                "relative_logloss_improvement_vs_core":(cb["logloss"]-sm["logloss"])/cb["logloss"],
            })
        z2=z.copy(); z2["year"]=pd.to_datetime(z2["signal_date"]).dt.year
        for yr,zz in z2.groupby("year"):
            ym=metrics(zz,"overlay_p")
            cb=metrics(dev[pd.to_datetime(dev["signal_date"]).dt.year==yr],"core_p")
            year_rows.append({
                "context_block":name,"year":int(yr),**ym,
                "relative_brier_improvement_vs_core":(cb["brier"]-ym["brier"])/cb["brier"]
            })

    met=pd.DataFrame(rows).sort_values("relative_brier_improvement_vs_core",ascending=False)
    sl=pd.DataFrame(slice_rows)
    yr=pd.DataFrame(year_rows)
    met.to_csv(OUT/"stage4_metrics.csv",index=False)
    sl.to_csv(OUT/"stage4_slice_metrics.csv",index=False)
    yr.to_csv(OUT/"stage4_year_metrics.csv",index=False)

    passing=met[met["scientific_gate"]=="PASS"].copy()
    if len(passing):
        best_imp=passing["relative_brier_improvement_vs_core"].max()
        simple_order=["CORE_DIR","CORE_MAG","CORE_DIR_MAG","CORE_DIR_MAG_T0REL","CORE_DIR_MAG_STATE","CORE_ALL_SAFE"]
        near=passing[passing["relative_brier_improvement_vs_core"]>=best_imp-0.0025].copy()
        near["simplicity"]=near["context_block"].map({x:i for i,x in enumerate(simple_order)})
        sel=near.sort_values(["simplicity","relative_brier_improvement_vs_core"],ascending=[True,False]).iloc[0]
        decision="PASS"
        selected=sel["context_block"]
    else:
        decision="NO_CONTEXT_PASS"
        selected="CORE_ONLY"

    summary={
        "status":decision,
        "selected":selected,
        "dev_n":int(len(dev)),
        "down_n":int((dev["monthly_down"]==1).sum()),
        "up_n":int((dev["monthly_down"]==0).sum()),
        "core":corem,
        "context_blocks":met.to_dict(orient="records"),
        "artifact_inputs":ART,
    }

    lines=[
        "# GOLD INTRAMONTH OPPORTUNITY — Stage 4 Monthly Context Incremental Test Result","",
        f"**Status:** **{decision}**","",
        f"**Selected:** **{selected}**","",
        "## Evaluation",
        f"- DEV daily origins: {len(dev)}",
        f"- monthly-DOWN: {(dev['monthly_down']==1).sum()}",
        f"- monthly-UP: {(dev['monthly_down']==0).sum()}",
        "- target: K100",
        "- frozen core: Stage-3 G_ONLY / HGB_CLASS",
        "- no 2025/2026 use",
        "",
        "## Context metrics","",
        "| Block | Brier | Rel vs core | Log loss | DOWN rel vs core | Fallback rows | Gate |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for _,r in met.iterrows():
        lines.append(
            f"| {r['context_block']} | {r['brier']:.5f} | {100*r['relative_brier_improvement_vs_core']:.2f}% | "
            f"{r['logloss']:.5f} | {100*r['down_relative_brier_improvement_vs_core']:.2f}% | "
            f"{int(r['fallback_rows'])} | {r['scientific_gate']} |"
        )
    lines += ["","## Binding decision"]
    if decision=="PASS":
        lines.append(f"Monthly context adds pre-2025 incremental predictive value. Freeze **{selected}** as the Stage-4 context model for the next robustness/transport stage.")
    else:
        lines.append("No monthly-context overlay clears the preregistered global gate. Retain Stage-3 CORE_ONLY; monthly context remains descriptive.")
    (OUT/"STAGE4_RESULT.md").write_text("\n".join(lines),encoding="utf-8")

    files=[OUT/"stage4_context_audit_table.csv",OUT/"stage4_dev_predictions.csv",OUT/"stage4_metrics.csv",
           OUT/"stage4_slice_metrics.csv",OUT/"stage4_year_metrics.csv",OUT/"STAGE4_RESULT.md"]
    summary["hashes"]={p.name:sha256_file(p) for p in files}
    (OUT/"stage4_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    print("STAGE4_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE4_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
