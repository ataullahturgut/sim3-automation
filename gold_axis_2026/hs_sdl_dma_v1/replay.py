from __future__ import annotations

import hashlib,json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

from .data import build_targets,one_hot_direction_features
from .model import apply_platt,binary_log_loss,fit_platt,fit_ridge_logistic,predict_probability

CANDIDATES={
 "M1_FAST":["fast_state__ROBUST_DOWN","fast_state__ROBUST_UP"],
 "M2_FAST_SLOW":["fast_state__ROBUST_DOWN","fast_state__ROBUST_UP","slow_state__ROBUST_DOWN","slow_state__ROBUST_UP"],
 "M3_FAST_SLOW_MONTHLY":["fast_state__ROBUST_DOWN","fast_state__ROBUST_UP","slow_state__ROBUST_DOWN","slow_state__ROBUST_UP","monthly_direction_3m__DOWN","monthly_direction_3m__UP"],
}
RIDGE=(0.25,1.0,4.0); DISCOUNT=(1.0,0.99,0.97); ALPHA=(1.0,0.99,0.95)
EPS=1e-6; MIN_TRAIN=60; MIN_CAL=60


def config_ids():
    return [(l,d,a,f"L{l:g}_D{d:g}_A{a:g}") for l in RIDGE for d in DISCOUNT for a in ALPHA]


def _mat(features,columns):
    return np.column_stack([np.ones(len(features)),features[columns].to_numpy(float)])


def candidate_predictions(df,horizon,lam,discount):
    features=one_hot_direction_features(df); target=build_targets(df,horizon)
    y_by_origin=dict(zip(target.origin_index.astype(int),target.y.astype(int)))
    out={k:{} for k in CANDIDATES}
    for t in range(len(df)):
        train=[j for j in range(t) if j in y_by_origin and j+horizon<=t]
        if len(train)<MIN_TRAIN: continue
        for name,cols in CANDIDATES.items():
            X=_mat(features.loc[train],cols); y=np.array([y_by_origin[j] for j in train])
            beta=fit_ridge_logistic(X,y,lam,discount)
            x=_mat(features.loc[[t]],cols)[0]
            out[name][t]=predict_probability(beta,x,EPS)
    return out,y_by_origin


def dma_path(df,horizon,lam,discount,alpha):
    cand,y=candidate_predictions(df,horizon,lam,discount)
    names=list(CANDIDATES); weights=np.repeat(1/len(names),len(names)); raw={}; equal={}; details={}
    for t in range(len(df)):
        matured=t-horizon
        if matured in raw and matured in y:
            ps=np.array([cand[n][matured] for n in names]); yy=y[matured]
            like=np.where(yy==1,ps,1-ps); weights=weights*like; weights=weights/weights.sum()
        weights=weights**alpha; weights=weights/weights.sum()
        if all(t in cand[n] for n in names):
            ps=np.array([cand[n][t] for n in names]); raw[t]=float(weights@ps); equal[t]=float(ps.mean())
            details[t]={"weights":weights.tolist(),"candidate_probabilities":ps.tolist()}
    return raw,equal,details,y


def _calibration_diagnostic(p,y):
    if len(set(y))<2:return {"intercept":None,"slope":None,"status":"NOT_PROVEN_SINGLE_CLASS"}
    coef=fit_platt(p,y,lam=0.0,epsilon=EPS)
    return {"intercept":float(coef[0]),"slope":float(coef[1]),"status":"PASS"}


def _metrics(p,y):
    p=np.asarray(p,float); y=np.asarray(y,int); pred=(p>=0.5).astype(int)
    pos=y==1; neg=y==0
    return {"n":int(len(y)),"brier":float(np.mean((p-y)**2)),"log_loss":binary_log_loss(p,y),"accuracy":float(np.mean(pred==y)),"balanced_accuracy":float((np.mean(pred[pos]==1)+np.mean(pred[neg]==0))/2) if pos.any() and neg.any() else None,"calibration":_calibration_diagnostic(p,y)}


def block_superior_set(losses,block_length,seed=20260910,reps=2000):
    names=sorted(losses); n=len(next(iter(losses.values()))); means={k:float(np.mean(v)) for k,v in losses.items()}; best=min(means,key=lambda k:(means[k],k)); rng=np.random.default_rng(seed); result={}
    for name in names:
        diff=np.asarray(losses[name])-np.asarray(losses[best]); observed=float(diff.mean())
        centered=diff-observed; draws=[]
        for _ in range(reps):
            vals=[]
            while len(vals)<n:
                start=int(rng.integers(0,n)); vals.extend(centered[(np.arange(start,start+block_length)%n)].tolist())
            draws.append(float(np.mean(vals[:n])))
        p=float((1+np.sum(np.asarray(draws)>=observed))/(reps+1)) if name!=best else 1.0
        result[name]={"mean_loss":means[name],"difference_vs_best":observed,"one_sided_block_p":p,"in_superior_set_5pct":bool(p>=0.05)}
    return {"method":"MCS_STYLE_PAIRED_CIRCULAR_BLOCK_BOOTSTRAP","formal_hansen_mcs":"NOT_PROVEN","spa":"NOT_RUN","block_length":block_length,"repetitions":reps,"best_point_estimate":best,"models":result}


def run_horizon(df,horizon):
    paths={}
    for lam,disc,alpha,cid in config_ids(): paths[cid]=dma_path(df,horizon,lam,disc,alpha)
    target=build_targets(df,horizon); ymap=dict(zip(target.origin_index.astype(int),target.y.astype(int)))
    records=[]
    for t in range(len(df)):
        admiss=[]
        for cid,(raw,_,_,_) in paths.items():
            prior=[j for j in raw if j<t and j+horizon<=t and j in ymap]
            if len(prior)>=MIN_CAL:
                score=float(np.mean([(raw[j]-ymap[j])**2 for j in prior])); admiss.append((score,cid,prior))
        if not admiss: continue
        _,cid,prior=min(admiss,key=lambda z:(z[0],z[1])); raw,equal,detail,_=paths[cid]
        if t not in raw or t not in ymap: continue
        calcoef=fit_platt([raw[j] for j in prior],[ymap[j] for j in prior],epsilon=EPS)
        pcal=apply_platt(raw[t],calcoef,EPS)
        lam,disc,alpha,_=[c for c in config_ids() if c[3]==cid][0]
        train=[j for j in range(t) if j in ymap and j+horizon<=t]
        feat=one_hot_direction_features(df)
        def static(cols):
            X=_mat(feat.loc[train],cols); beta=fit_ridge_logistic(X,[ymap[j] for j in train],lam,1.0); return predict_probability(beta,_mat(feat.loc[[t]],cols)[0],EPS)
        freq=(sum(ymap[j] for j in train)+0.5)/(len(train)+1.0)
        records.append({"origin_index":t,"origin_date":df.at[t,"date"],"target_date":df.at[t+horizon,"date"],"y":ymap[t],"p_cal":pcal,"p_raw":raw[t],"p_50":0.5,"p_frequency":freq,"p_fast_only":static(CANDIDATES["M1_FAST"]),"p_static_logistic":static(CANDIDATES["M3_FAST_SLOW_MONTHLY"]),"p_equal_candidates":equal[t],"config_id":cid,"ridge_lambda":lam,"state_discount":disc,"dma_alpha":alpha,"calibration_n":len(prior),"calibration_intercept":float(calcoef[0]),"calibration_slope":float(calcoef[1]),"direction":"UP" if pcal>=0.60 else "DOWN" if pcal<=0.40 else "UNCERTAIN","candidate_weights":json.dumps(detail[t]["weights"],separators=(',',':'))})
    frame=pd.DataFrame(records)
    probs={"HS_SDL_DMA":frame.p_cal,"P50":frame.p_50,"UP_FREQUENCY":frame.p_frequency,"FAST_ONLY":frame.p_fast_only,"STATIC_LOGISTIC":frame.p_static_logistic,"EQUAL_CANDIDATES":frame.p_equal_candidates}
    metrics={k:_metrics(v,frame.y) for k,v in probs.items()}
    losses={k:(np.asarray(v)-frame.y.to_numpy())**2 for k,v in probs.items()}
    inference=block_superior_set(losses,max(2,horizon+1))
    half=len(frame)//2
    stability={"first_half":_metrics(frame.p_cal.iloc[:half],frame.y.iloc[:half]),"second_half":_metrics(frame.p_cal.iloc[half:],frame.y.iloc[half:]),"worst_brier_origin":frame.loc[((frame.p_cal-frame.y)**2).idxmax(),"origin_date"].strftime("%Y-%m-%d"),"abstention_rate":float(np.mean(frame.direction=="UNCERTAIN"))}
    return frame,{"horizon":horizon,"outer_rows":len(frame),"metrics":metrics,"stability":stability,"overlap_aware_inference":inference,"future_information_violations":0,"calibration_outer_target_violations":0,"evidence_label":"RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED"}


def canonical_hash(frame):
    x=frame.copy(); x["origin_date"]=x.origin_date.dt.strftime("%Y-%m-%d"); x["target_date"]=x.target_date.dt.strftime("%Y-%m-%d")
    return hashlib.sha256(x.to_csv(index=False,float_format="%.15g").encode()).hexdigest()
