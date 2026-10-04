from pathlib import Path
import importlib.util, json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"
RTEF=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

OUT_MD=AX/"GOLD_H3_HANDOFF_LATENT_REGIME_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_LATENT_REGIME_V1_SUMMARY_2026-10-04.json"
OUT_ASSIGN=AX/"GOLD_H3_HANDOFF_LATENT_REGIME_V1_ASSIGNMENTS_2026-10-04.csv"
OUT_PROFILE=AX/"GOLD_H3_HANDOFF_LATENT_REGIME_V1_PROFILES_2026-10-04.csv"
OUT_ACTIONS=AX/"GOLD_H3_HANDOFF_LATENT_REGIME_V1_ACTIONS_2026-10-04.csv"

FEATURES=[
 "abs_h_ret_12","trend_strength","adverse_excursion","path_consistency",
 "signed_opt_pressure","opt_total_z20","gc_volume_z20",
 "core_confirmation","cross_dispersion"
]

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec); spec.loader.exec_module(hsm)

def load_market():
    a=pd.read_csv(RTEF,parse_dates=["feature_cutoff_date"])
    b=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"])
    keepa=["feature_cutoff_date"]+[c for c in FEATURES if c in a.columns]
    keepb=["feature_cutoff_date"]+[c for c in FEATURES if c in b.columns and c not in keepa]
    z=a[keepa].merge(b[keepb],on="feature_cutoff_date",how="inner",validate="one_to_one")
    z["year"]=z.feature_cutoff_date.dt.year
    return z.sort_values("feature_cutoff_date").reset_index(drop=True)

def fit_preprocess(dev):
    q={}
    X=pd.DataFrame(index=dev.index)
    for c in FEATURES:
        x=pd.to_numeric(dev[c],errors="coerce")
        lo=float(x.quantile(.01)); hi=float(x.quantile(.99)); med=float(x.median())
        xc=x.clip(lo,hi).fillna(med)
        mu=float(xc.mean()); sd=float(xc.std(ddof=0))
        if not np.isfinite(sd) or sd<1e-12: sd=1.0
        q[c]={"lo":lo,"hi":hi,"median":med,"mean":mu,"std":sd}
        X[c]=(xc-mu)/sd
    return q,X.to_numpy(float)

def transform(df,p):
    X=pd.DataFrame(index=df.index)
    for c in FEATURES:
        s=p[c]
        x=pd.to_numeric(df[c],errors="coerce").clip(s["lo"],s["hi"]).fillna(s["median"])
        X[c]=(x-s["mean"])/s["std"]
    return X.to_numpy(float)

def choose_k(X):
    rows=[]
    models={}
    for k in [2,3,4,5]:
        m=KMeans(n_clusters=k,random_state=20261004,n_init=50)
        lab=m.fit_predict(X)
        sil=float(silhouette_score(X,lab))
        rows.append({"k":k,"silhouette":sil})
        models[k]=m
    rows=sorted(rows,key=lambda r:(-r["silhouette"],r["k"]))
    best=rows[0]
    for r in rows[1:]:
        if best["silhouette"]-r["silhouette"]<0.01 and r["k"]<best["k"]:
            best=r
    return best["k"],models[best["k"]],sorted(rows,key=lambda r:r["k"])

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); dn=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "balanced_accuracy":float((up+dn)/2)}

def main():
    mkt=load_market()
    dev=mkt[mkt.year.isin([2023,2024])].copy().reset_index(drop=True)
    prep,X=fit_preprocess(dev)
    k,model,ks=choose_k(X)

    mkt["regime"]=model.predict(transform(mkt,prep)).astype(int)

    # Stable semantic ordering solely for readability: sort clusters by centroid trend impulse + dispersion.
    # This does not affect trust selection.
    profiles=mkt[mkt.year.isin([2023,2024])].groupby("regime")[FEATURES].mean()
    profiles["dev_n"]=mkt[mkt.year.isin([2023,2024])].groupby("regime").size()
    profiles=profiles.reset_index()
    profiles.to_csv(OUT_PROFILE,index=False)

    h=hsm.load_frame().sort_values("feature_cutoff_date").reset_index(drop=True)
    h=h.merge(mkt[["feature_cutoff_date","regime"]],on="feature_cutoff_date",how="left")
    h["handoff_alarm"]=(pd.to_numeric(h.leadlag_score_premax,errors="coerce")>=.60)&\
                       (pd.to_numeric(h.internal_now,errors="coerce")>=.60)&\
                       (pd.to_numeric(h.internal_d1,errors="coerce")>=0.0)&\
                       (h.baseline_pred.astype(int)==h.momentum_up.astype(int))
    h["rescue_if_flip"]=~h.baseline_correct

    # occupancy
    occ={}
    for y in [2023,2024,2025,2026]:
        yy=mkt[mkt.year==y]
        occ[str(y)]={str(int(r)):int(n) for r,n in yy.groupby("regime").size().items()}

    q25=h[(h.feature_cutoff_date.dt.year==2025)&h.handoff_alarm&h.regime.notna()].copy()
    qual=[]
    trusted=[]
    for r in sorted(q25.regime.astype(int).unique()):
        q=q25[q25.regime.astype(int)==r]
        actions=int(len(q)); rescue=int(q.rescue_if_flip.sum()); broken=actions-rescue
        net=rescue-broken; precision=float(rescue/actions) if actions else 0.0
        ok=bool(actions>=3 and rescue>=2 and precision>=.60 and net>0)
        qual.append({"regime":int(r),"actions":actions,"rescue":rescue,"broken":broken,"net":net,
                     "precision":precision,"trusted":ok})
        if ok: trusted.append(int(r))

    summary={
      "schema":"GOLD_H3_HANDOFF_LATENT_REGIME_V1",
      "status":"NO_TRUSTED_REGIME" if not trusted else "TRUSTED_REGIME_2026_STRESSED",
      "dev_2023_2024":{"n":int(len(dev)),"selected_k":int(k),"k_silhouette":ks},
      "regime_occupancy":occ,
      "qualification_2025":qual,
      "trusted_regimes":trusted,
      "stress_2026":None
    }

    action_df=pd.DataFrame()
    if trusted:
        t=h[h.feature_cutoff_date.dt.year==2026].copy().reset_index(drop=True)
        if len(t)!=191: raise RuntimeError(f"Expected 191 origins, got {len(t)}")
        if int(t.baseline_correct.sum())!=126: raise RuntimeError(f"Expected baseline 126 correct, got {int(t.baseline_correct.sum())}")
        act=t.handoff_alarm & t.regime.fillna(-1).astype(int).isin(trusted)
        assisted=t.baseline_pred.to_numpy(int).copy()
        assisted[act.to_numpy()]=1-assisted[act.to_numpy()]
        base=confusion(t.y_up,t.baseline_pred)
        ass=confusion(t.y_up,assisted)
        q=t[act].copy()
        q["outcome"]=np.where(q.baseline_correct,"BROKEN","RESCUE")
        q["assisted_pred"]=1-q.baseline_pred
        rescue=int((~q.baseline_correct).sum()); broken=int(q.baseline_correct.sum())
        remaining53=(~t.baseline_correct)&t.is_reversal
        summary["stress_2026"]={
          "actions":int(len(q)),"rescue":rescue,"broken":broken,"net":rescue-broken,
          "precision":float(rescue/len(q)) if len(q) else 0.0,
          "remaining53_rescued":int((act&remaining53).sum()),
          "baseline":base,"assisted":ass,
          "by_regime":[
            {"regime":int(r),
             "actions":int(len(g)),
             "rescue":int((~g.baseline_correct).sum()),
             "broken":int(g.baseline_correct.sum()),
             "precision":float((~g.baseline_correct).mean())}
            for r,g in q.groupby("regime")
          ]
        }
        action_df=q[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","regime",
                     "momentum_up","y_up","target_r3","baseline_pred","baseline_correct",
                     "leadlag_score_premax","internal_now","internal_d1","outcome"]]
    action_df.to_csv(OUT_ACTIONS,index=False)

    h[["feature_cutoff_date","regime","handoff_alarm","baseline_correct","rescue_if_flip"]].to_csv(OUT_ASSIGN,index=False)
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Handoff Latent Regime V1 Result","",
           "**Status:** "+summary["status"],"",
           "## Unsupervised 2023-2024 regime discovery","",
           f"- development origins: **{len(dev)}**",
           f"- selected K: **{k}**","",
           "| K | Silhouette |","|---:|---:|"]
    for r in ks: lines.append(f"| {r['k']} | {r['silhouette']:.4f} |")
    lines += ["","## 2025 Handoff reliability by latent regime","",
              "| Regime | Actions | Rescue | Broken | Net | Precision | Trusted |",
              "|---:|---:|---:|---:|---:|---:|---|"]
    for r in qual:
        lines.append(f"| {r['regime']} | {r['actions']} | {r['rescue']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.1f}% | {r['trusted']} |")
    lines += ["",f"Trusted regimes frozen from 2025: **{trusted if trusted else 'none'}**",""]
    if not trusted:
        lines += ["## Decision","","No latent regime met the frozen 2025 Handoff trust gate. V1 closes without a 2026 assisted claim."]
    else:
        s=summary["stress_2026"]
        lines += ["## Frozen 2026 stress","",
                  f"- actions: **{s['actions']}**",
                  f"- rescue / broken / net: **{s['rescue']} / {s['broken']} / {s['net']:+d}**",
                  f"- precision: **{100*s['precision']:.1f}%**",
                  f"- remaining-53 rescued: **{s['remaining53_rescued']}**",
                  f"- baseline: **{s['baseline']['correct']}/{s['baseline']['n']} = {100*s['baseline']['accuracy']:.2f}%**, BA **{100*s['baseline']['balanced_accuracy']:.2f}%**",
                  f"- assisted: **{s['assisted']['correct']}/{s['assisted']['n']} = {100*s['assisted']['accuracy']:.2f}%**, BA **{100*s['assisted']['balanced_accuracy']:.2f}%**","",
                  "## 2026 action dates","",
                  "| Date | Regime | Baseline | Actual | H3 return | Ext pre | Internal | d1 | Outcome |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for r in action_df.itertuples():
            lines.append(f"| {r.feature_cutoff_date.date()} | {int(r.regime)} | {r.baseline_pred} | {r.y_up} | {100*r.target_r3:+.2f}% | {r.leadlag_score_premax:.2f} | {r.internal_now:.2f} | {r.internal_d1:+.2f} | {r.outcome} |")
    lines += ["","## Interpretation discipline","",
              "- Regime labels were learned without Handoff outcomes or reversal labels.",
              "- 2025 alone determined which regimes, if any, were trusted.",
              "- 2026 did not choose K, centroids, preprocessing, thresholds, or trusted regimes.",
              "- Because the Handoff hypothesis itself originated from retrospective 2026 research, this remains a strict retrospective stress rather than pristine prospective OOS validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
