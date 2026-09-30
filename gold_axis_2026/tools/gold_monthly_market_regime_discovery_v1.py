from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import ruptures as rpt
from hmmlearn.hmm import GaussianHMM
from scipy.special import logsumexp
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import gold_monthly_chhho_alarm_audit_v3 as audit
import gold_monthly_chhho_efg_alarm_audit_v1 as efg
import gold_monthly_chhho_etf_anomaly_screen_v1 as etf

START="2010-01"
TRAIN_END="2024-12"
TEST_START="2025-01"
END="2026-08"
FEATURES=[
    "Gold_r1",
    "Gold_r3",
    "Gold_level_gap",
    "Gold_rv_ratio",
    "cross_metal_dispersion",
    "gvz_ratio12",
    "cftc_mm_net_oi",
    "cftc_oi_ratio12",
    "broad_usd_logchg",
    "nom10_change",
    "real10_change",
    "etf_combined_flow",
    "etf_outflow_breadth",
]

def load_json(p):
    return json.loads(Path(p).read_text())

def mrange(a,b):
    cur=a
    while cur<=b:
        yield cur
        cur=audit.mshift(cur,1)

def build_panel(snapshot,public,external):
    monthly=efg.build_market(snapshot["payload"],public)
    gvz,gvzmeta=efg.download_gvz()
    cot,cotmeta=efg.download_cftc()
    cotm=efg.cftc_monthly_pit(cot,start=START,end=END)
    macro=audit.build_macro(external)

    gld=etf.parse_gld(etf.fetch(etf.GLD_URL))
    iau=etf.parse_iau(etf.fetch(etf.IAU_URL))
    etfm=etf.monthly_features(gld,iau)

    rows=[]
    missing=[]
    for m in mrange(START,END):
        try:
            if m not in monthly.index or m not in gvz.index or m not in cotm.index or m not in etfm.index:
                raise KeyError("market-source row missing")
            z=monthly.loc[m]
            g=gvz.loc[m]
            c=cotm.loc[m]
            e=etfm.loc[m]
            mac=macro(m)
            metals=[z["Gold_r1"],z["Silver_r1"],z["Platinum_r1"],z["Palladium_r1"]]
            vals={
                "Gold_r1":float(z["Gold_r1"]),
                "Gold_r3":float(z["Gold_r3"]),
                "Gold_level_gap":float(z["Gold_level_gap"]),
                "Gold_rv_ratio":float(z["Gold_rv_ratio"]),
                "cross_metal_dispersion":float(np.std(np.asarray(metals,float),ddof=0)),
                "gvz_ratio12":float(g["gvz_ratio12"]),
                "cftc_mm_net_oi":float(c["mm_net_oi"]),
                "cftc_oi_ratio12":float(c["oi_ratio12"]),
                "broad_usd_logchg":float(mac["broad_usd_logchg"]),
                "nom10_change":float(mac["nom10_change"]),
                "real10_change":float(mac["real10_change"]),
                "etf_combined_flow":float(e["combined_flow"]),
                "etf_outflow_breadth":float(e["outflow_breadth"]),
            }
            if not all(np.isfinite(vals[k]) for k in FEATURES):
                raise ValueError("non-finite feature")
            rows.append({"month":m,**vals})
        except Exception as exc:
            missing.append({"month":m,"error":repr(exc)})
    return pd.DataFrame(rows).set_index("month"),{
        "gvz":gvzmeta,
        "cftc":cotmeta,
        "gld":{"url":etf.GLD_URL,"rows":len(gld),"first":str(gld.date.min().date()),"last":str(gld.date.max().date())},
        "iau":{"url":etf.IAU_URL,"rows":len(iau),"first":str(iau.date.min().date()),"last":str(iau.date.max().date())},
        "missing":missing,
    }

def hmm_param_count(k,d):
    return (k-1) + k*(k-1) + k*d + k*d

def fit_best_hmm(X,k):
    best=None
    failures=[]
    for seed in range(10):
        try:
            model=GaussianHMM(
                n_components=k,
                covariance_type="diag",
                n_iter=1000,
                tol=1e-4,
                min_covar=1e-5,
                random_state=seed,
            )
            model.fit(X)
            ll=float(model.score(X))
            if not np.isfinite(ll):
                raise RuntimeError("non-finite loglik")
            if best is None or ll>best[0]:
                best=(ll,seed,model)
        except Exception as exc:
            failures.append({"seed":seed,"error":repr(exc)})
    if best is None:
        raise RuntimeError(("ALL_HMM_FITS_FAILED",k,failures))
    return best,failures

def diag_logpdf(X,means,covars):
    X=np.asarray(X,float)
    means=np.asarray(means,float)
    covars=np.asarray(covars,float)
    # hmmlearn diag covars may be expanded to Kxdxd in some versions.
    if covars.ndim==3:
        covars=np.stack([np.diag(c) for c in covars],axis=0)
    covars=np.maximum(covars,1e-9)
    out=np.empty((len(X),len(means)),float)
    for j in range(len(means)):
        d=X-means[j]
        out[:,j]=-0.5*(np.sum(np.log(2*np.pi*covars[j]))+np.sum(d*d/covars[j],axis=1))
    return out

def forward_filter(model,X):
    loge=diag_logpdf(X,model.means_,model.covars_)
    posts=[]
    prev=None
    for i in range(len(X)):
        prior=np.asarray(model.startprob_,float) if prev is None else prev @ np.asarray(model.transmat_,float)
        logp=np.log(np.maximum(prior,1e-300))+loge[i]
        logp=logp-logsumexp(logp)
        post=np.exp(logp)
        posts.append(post)
        prev=post
    return np.asarray(posts),loge

def canonical_map(states,train_df):
    profiles=[]
    for s in sorted(set(states)):
        idx=np.where(states==s)[0]
        g=float(train_df.iloc[idx]["Gold_r1"].mean())
        vol=float(train_df.iloc[idx]["Gold_rv_ratio"].mean())
        profiles.append((g,vol,int(s)))
    profiles.sort()
    return {old:new for new,(_,_,old) in enumerate(profiles)}

def remap_array(a,mapping):
    return np.asarray([mapping[int(x)] for x in a],int)

def remap_matrix(M,mapping):
    k=len(mapping)
    out=np.zeros((k,k),float)
    for old_i,new_i in mapping.items():
        for old_j,new_j in mapping.items():
            out[new_i,new_j]=M[old_i,old_j]
    return out

def spells(months,states):
    out=[]
    if not len(states): return out
    start=0
    for i in range(1,len(states)+1):
        if i==len(states) or states[i]!=states[start]:
            out.append({
                "state":int(states[start]),
                "start":months[start],
                "end":months[i-1],
                "length":i-start,
            })
            start=i
    return out

def js_distance(p,q):
    p=np.asarray(p,float); q=np.asarray(q,float)
    p=p/p.sum(); q=q/q.sum(); m=(p+q)/2
    def kl(a,b):
        keep=a>0
        return float(np.sum(a[keep]*np.log(a[keep]/b[keep])))
    return float(math.sqrt(0.5*kl(p,m)+0.5*kl(q,m)))

def consensus_breaks(breaks_by_pen,months):
    candidates=[]
    labels=list(breaks_by_pen)
    for li,label in enumerate(labels):
        for idx in breaks_by_pen[label]:
            candidates.append((idx,label))
    groups=[]
    used=set()
    for i,(idx,label) in enumerate(candidates):
        if i in used: continue
        grp=[(idx,label)]; used.add(i)
        for j,(idx2,label2) in enumerate(candidates):
            if j in used: continue
            if label2==label: continue
            if abs(idx2-idx)<=2:
                grp.append((idx2,label2)); used.add(j)
        labs={x[1] for x in grp}
        if len(labs)>=2:
            mid=int(round(np.median([x[0] for x in grp])))
            mid=min(max(mid,1),len(months)-1)
            groups.append({
                "month":months[mid],
                "support_penalties":sorted(labs),
                "raw_indices":[int(x[0]) for x in grp],
            })
    # Deduplicate nearby consensus groups.
    final=[]
    for g in sorted(groups,key=lambda x:x["month"]):
        idx=months.index(g["month"])
        if final and abs(idx-months.index(final[-1]["month"]))<=2:
            prev=final[-1]
            prev["support_penalties"]=sorted(set(prev["support_penalties"])|set(g["support_penalties"]))
            prev["raw_indices"]+=g["raw_indices"]
        else:
            final.append(g)
    return final

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--public-bundle",required=True)
    ap.add_argument("--external",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    snapshot=load_json(a.snapshot)
    public=load_json(a.public_bundle)
    external=load_json(a.external)

    panel,sources=build_panel(snapshot,public,external)
    train=panel.loc[START:TRAIN_END].copy()
    test=panel.loc[TEST_START:END].copy()

    if len(train)<175:
        raise RuntimeError(("TRAIN_COVERAGE_TOO_LOW",len(train)))
    if list(test.index)!=list(mrange(TEST_START,END)):
        raise RuntimeError(("TRANSPORT_MONTHS_INCOMPLETE",list(test.index)))

    scaler=StandardScaler().fit(train[FEATURES].values)
    Ztrain=scaler.transform(train[FEATURES].values)
    Zall=scaler.transform(panel[FEATURES].values)

    pca_full=PCA().fit(Ztrain)
    cum=np.cumsum(pca_full.explained_variance_ratio_)
    npc=int(np.searchsorted(cum,.85)+1)
    npc=max(2,min(6,npc))
    pca=PCA(n_components=npc,random_state=0).fit(Ztrain)
    Xtrain=pca.transform(Ztrain)
    Xall=pca.transform(Zall)

    hmm_rows=[]
    hmm_models={}
    for k in range(1,6):
        (ll,seed,model),failures=fit_best_hmm(Xtrain,k)
        p=hmm_param_count(k,Xtrain.shape[1])
        bic=float(-2*ll+p*np.log(len(Xtrain)))
        hmm_rows.append({"k":k,"loglik":ll,"seed":seed,"params":p,"bic":bic,"fit_failures":failures})
        hmm_models[k]=model
    hmm_rows.sort(key=lambda z:z["k"])
    selected=min(hmm_rows,key=lambda z:(z["bic"],z["k"]))
    ksel=int(selected["k"])
    model=hmm_models[ksel]

    posts_all,loge_all=forward_filter(model,Xall)
    raw_states=posts_all.argmax(axis=1)
    train_n=len(train)
    mapping=canonical_map(raw_states[:train_n],train)
    states=remap_array(raw_states,mapping)
    trans=remap_matrix(np.asarray(model.transmat_,float),mapping)
    post_canon=np.zeros_like(posts_all)
    for old,new in mapping.items():
        post_canon[:,new]=posts_all[:,old]

    months=list(panel.index)
    train_states=states[:train_n]
    train_months=months[:train_n]
    spell_rows=spells(train_months,train_states)
    spell_stats={}
    for s in range(ksel):
        lens=[x["length"] for x in spell_rows if x["state"]==s]
        spell_stats[str(s)]={
            "n_spells":len(lens),
            "mean_length":None if not lens else float(np.mean(lens)),
            "median_length":None if not lens else float(np.median(lens)),
            "max_length":None if not lens else int(max(lens)),
        }

    occup=np.bincount(train_states,minlength=ksel)
    weighted_self=float(np.sum((occup/occup.sum())*np.diag(trans)))
    simple_self=float(np.mean(np.diag(trans)))

    # State profiles in original feature space.
    profiles={}
    Zdf=pd.DataFrame(Zall,index=panel.index,columns=FEATURES)
    for s in range(ksel):
        idx=[i for i,x in enumerate(states[:train_n]) if x==s]
        raw=train.iloc[idx]
        z=Zdf.iloc[idx]
        zmeans={c:float(z[c].mean()) for c in FEATURES}
        top_high=sorted(zmeans.items(),key=lambda x:-x[1])[:4]
        top_low=sorted(zmeans.items(),key=lambda x:x[1])[:4]
        profiles[str(s)]={
            "label":f"R{s}",
            "train_months":len(idx),
            "raw_feature_means":{c:float(raw[c].mean()) for c in FEATURES},
            "z_feature_means":zmeans,
            "top_high_features":[{"feature":c,"zmean":v} for c,v in top_high],
            "top_low_features":[{"feature":c,"zmean":v} for c,v in top_low],
        }

    # GMM robustness.
    gmm_rows=[]
    for k in range(1,6):
        gm=GaussianMixture(n_components=k,covariance_type="full",n_init=20,random_state=0,reg_covar=1e-5).fit(Xtrain)
        lab=gm.predict(Xtrain)
        sil=None
        if k>=2 and len(set(lab))>1:
            sil=float(silhouette_score(Xtrain,lab))
        gmm_rows.append({"k":k,"bic":float(gm.bic(Xtrain)),"aic":float(gm.aic(Xtrain)),"silhouette":sil})
    gmm_selected=min(gmm_rows,key=lambda z:(z["bic"],z["k"]))["k"]

    # Multivariate PELT on frozen PCA transform, full timeline for descriptive structural breaks.
    breaks={}
    n=len(Xall)
    for mult in (2,4,6):
        label=f"{mult}logn"
        bk=rpt.Pelt(model="rbf",min_size=3,jump=1).fit(Xall).predict(pen=float(mult*np.log(n)))
        # bk are segment end indices in 1..n; omit terminal n, map boundary to next month index.
        breaks[label]=[int(i) for i in bk if i<n]
    cons=consensus_breaks(breaks,months)
    breaks_months={k:[months[min(i,len(months)-1)] for i in v] for k,v in breaks.items()}

    # OOD by maximum state emission density, threshold from 2010-2024.
    max_emission=loge_all.max(axis=1)
    ood_threshold=float(np.quantile(max_emission[:train_n],.05))

    table=[]
    for i,m in enumerate(months):
        s=int(states[i])
        table.append({
            "month":m,
            "period":"REGIME_DEV" if m<=TRAIN_END else ("2025" if m<="2025-12" else "2026"),
            "state":f"R{s}",
            "state_id":s,
            "state_probability":float(post_canon[i,s]),
            "max_emission_logdensity":float(max_emission[i]),
            "ood_below_train_p05":bool(i>=train_n and max_emission[i]<ood_threshold),
            **{c:float(panel.loc[m,c]) for c in FEATURES},
        })

    # Occupancy / transport diagnostics.
    def occupancy(rows):
        counts=np.zeros(ksel,float)
        for r in rows: counts[r["state_id"]]+=1
        return counts/counts.sum() if counts.sum() else counts
    train_rows=[r for r in table if r["period"]=="REGIME_DEV"]
    y25=[r for r in table if r["period"]=="2025"]
    y26=[r for r in table if r["period"]=="2026"]
    p0=occupancy(train_rows); p25=occupancy(y25); p26=occupancy(y26)
    occ={
        "2010_2024":{f"R{i}":float(p0[i]) for i in range(ksel)},
        "2025":{f"R{i}":float(p25[i]) for i in range(ksel)},
        "2026_JAN_AUG":{f"R{i}":float(p26[i]) for i in range(ksel)},
        "js_distance_2025_vs_2010_2024":js_distance(p25,p0),
        "js_distance_2026_vs_2010_2024":js_distance(p26,p0),
    }

    hmm_bic_k1=next(x["bic"] for x in hmm_rows if x["k"]==1)
    delta_bic=float(hmm_bic_k1-selected["bic"])
    states_ge12=sum(int(v>=12) for v in occup)
    strong=bool(ksel>=2 and delta_bic>=10 and states_ge12>=2 and weighted_self>=.60)

    evidence={
        "selected_hmm_k":ksel,
        "hmm_delta_bic_vs_k1":delta_bic,
        "train_states_with_at_least_12_months":states_ge12,
        "weighted_self_transition":weighted_self,
        "simple_mean_self_transition":simple_self,
        "primary_regime_evidence":"STRONG" if strong else "NOT_STRONG",
        "gmm_selected_k":int(gmm_selected),
        "gmm_supports_multi_state":bool(gmm_selected>=2),
        "consensus_change_points":cons,
        "n_consensus_change_points":len(cons),
    }

    out={
        "schema":"GOLD_MONTHLY_MARKET_REGIME_DISCOVERY_V1_2026-09-30",
        "status":"COMPLETE",
        "scope":{
            "panel_start":START,"regime_development_end":TRAIN_END,
            "transport_start":TEST_START,"panel_end":END,
            "train_rows":len(train),"transport_rows":len(test),
            "feature_count":len(FEATURES),"pca_components":npc,
            "pca_explained_variance":float(pca.explained_variance_ratio_.sum()),
        },
        "features":FEATURES,
        "sources":sources,
        "hmm_model_selection":hmm_rows,
        "gmm_model_selection":gmm_rows,
        "evidence":evidence,
        "transition_matrix":trans.tolist(),
        "state_occupancy_train":{f"R{i}":int(occup[i]) for i in range(ksel)},
        "spell_stats":spell_stats,
        "state_profiles":profiles,
        "occupancy_transport":occ,
        "ood_threshold_train_p05_max_emission":ood_threshold,
        "ood_transport_months":[r["month"] for r in table if r["ood_below_train_p05"]],
        "change_points":{
            "raw_break_months":breaks_months,
            "consensus":cons,
        },
        "monthly_regimes":table,
        "governance":{
            "forecast_error_used":False,
            "alarm_labels_used":False,
            "model_forecasts_used":False,
            "2025_2026_used_to_choose_regime_model":False,
            "train_scaler_pca_only_2010_2024":True,
            "routing_tested":False,
            "alarm_selection_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "scope":out["scope"],
        "evidence":evidence,
        "hmm_model_selection":[{"k":x["k"],"bic":x["bic"],"loglik":x["loglik"]} for x in hmm_rows],
        "gmm_model_selection":gmm_rows,
        "occupancy_transport":occ,
        "ood_transport_months":out["ood_transport_months"],
        "state_profiles":profiles,
        "2025_2026":[{"month":r["month"],"state":r["state"],"p":r["state_probability"],"ood":r["ood_below_train_p05"]} for r in table if r["period"]!="REGIME_DEV"],
    },sort_keys=True))

if __name__=="__main__":
    main()
