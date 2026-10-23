"""Frozen SMA-ELMFIS V1 quarantine and chronological-inner-safe V2 science runner.

Original untouched: vw_midas_elmfis_meta_batch_5_v1.py
V1: train+validation standardized jointly before inner split (validation
statistics leakage into training).  No target-month Y leakage.
V2: reuse the SAME original sma_phase, 3 seeds, same 45/15 generations,
same ridge TSK and input features. Only repair inner-fit statistics and map
warm-start antecedents from inner-scaler coordinates to full-history scaler
before full-history refit. V2 is explicitly a distinct model.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as tsk
import vw_midas_elmfis_meta_batch_1_v1 as common
import vw_midas_elmfis_meta_batch_5_v1 as old
import gold_monthly_h1_ann_frozen_snapshot_replay_v2 as source

OLD="SMA_ELMFIS_V1_INNER_SCALER_CONTAMINATED"
NEW="SMA_ELMFIS_V2_INNER_TRAIN_ONLY_SCALING"
TGT=list(base.month_range("2022-04","2026-09"))

def need(cond,msg):
    if not cond:raise RuntimeError("SMA_ELMFIS_SCIENCE_GATE_FAIL "+msg)

def spec():
    need(tsk.N_RULES==5 and tsk.RIDGE_ALPHA==1e-3,"TSK_OR_RIDGE_CHANGED")
    need(common.INPUTS==8 and common.OUTPUTS==4 and common.PARAM_DIM==80,"ELMFIS_DIM_CHANGED")
    need(common.POP_SIZE==24 and common.SELECT_GENS==45 and common.REFIT_GENS==15
         and common.REPEATS==3,"METAOPTIMIZER_FROZEN_BUDGET_CHANGED")
    need(old.PHASE["SMA"] is old.sma_phase,"ORIGINAL_SMA_PHASE_CHANGED")
    need(old.SEED_BASE["SMA"]==208110,"SEED_CHANGED")
    return {
        "original_model":OLD,"corrected_model":NEW,
        "pretrained_lag_vintage":"ORIGIN_MONTH_END",
        "first_training_month":"2010-03",
        "input_features":"8_METAL_MR_GPR_VW",
        "n_rules":5,"num_antecedent_optimised_parameters":80,
        "tsk_order":"FIRST_ORDER","ridge_alpha":tsk.RIDGE_ALPHA,
        "optimization":"ORIGINAL_FROZEN_SLIME_MOULD_SMA_PHASE",
        "population":24,"select_generations":45,"refit_generations":15,
        "selection_repeats":3,"seed_base":208110,
        "original_implementation_changed":False,
        "original_source_sha256":hashlib.sha256(Path(old.__file__).read_bytes()).hexdigest(),
        "original_common_sha256":hashlib.sha256(Path(common.__file__).read_bytes()).hexdigest(),
        "original_tsk_sha256":hashlib.sha256(Path(tsk.__file__).read_bytes()).hexdigest(),
        "legacy_known_defect":"INNER_TRAIN_AND_VALIDATION_SCALING_STATISTICS_MIXED_BEFORE_SPLIT",
        "new_version_fix":"INNER_TRAIN_ONLY_SCALER_PLUS_EXACT_ANTECEDENT_COORDINATE_TRANSPORT",
    }

def samples_of(r):
    z={k:(np.asarray(x,float),None if y is None else np.asarray(y,float))
       for k,(x,y) in r["samples"].items()}
    need(z[r["target_month"]][1] is None,"TARGET_Y_PRESENT")
    need(list(sorted(k for k in z if k<r["target_month"]))==
         list(base.month_range("2010-03",r["origin_month"])),"HISTORY_GAP")
    return z

def extract(samples,t):
    ks=sorted(k for k in samples if k<t)
    X=np.stack([samples[k][0] for k in ks])
    Y=np.stack([samples[k][1] for k in ks])
    tx=np.asarray(samples[t][0],float)[None,:]
    need(X.shape==(len(ks),8) and Y.shape==(len(ks),4) and tx.shape==(1,8),"RAW_SHAPE")
    need(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(tx).all(),"RAW_NONFINITE")
    nval=max(common.MIN_VAL,int(round(common.VAL_FRAC*len(ks))))
    split=len(ks)-nval
    need(split>=24,"SHORT_INNER_TRAIN")
    return ks,X,Y,tx,split

def scaler(X,Y):
    xm=X.mean(0); xs=X.std(0)
    ym=Y.mean(0); ys=Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs)
    ys=np.where(ys<1e-9,1.0,ys)
    return xm,xs,ym,ys

def prepared(samples,t):
    ks,X,Y,tx,split=extract(samples,t)
    tr=scaler(X[:split],Y[:split])
    full=scaler(X,Y)
    ax,as_,ay,ays=tr
    bx,bs,by,bys=full
    inner=((X[:split]-ax)/as_,(Y[:split]-ay)/ays,
           (X[split:]-ax)/as_,(Y[split:]-ay)/ays)
    whole=((X-bx)/bs,(Y-by)/bys,(tx-bx)/bs,by,bys)
    return ks,split,inner,whole,tr,full

def map_theta_between_scalers(theta,tr,full):
    """Hold Gaussian memberships identical under two standardized coordinate frames."""
    c,s=common.decode(theta)
    mx,sx,_,_=tr
    fx,fs,_,_=full
    c_new=(c*sx[None,:]+mx[None,:]-fx[None,:])/fs[None,:]
    s_new=s*sx[None,:]/fs[None,:]
    mapped=common.encode(c_new,s_new)
    return mapped, {
       "center_clipping_max_distance":float(np.max(np.abs(
           np.clip(c_new,common.CENTER_LOW,common.CENTER_HIGH)-c_new))),
       "spread_clipping_max_distance":float(np.max(np.abs(
           np.clip(s_new,common.SPREAD_LOW,common.SPREAD_HIGH)-s_new))),
    }

def corrected(samples,t):
    ks,split,inner,full,tr,fullstat=prepared(samples,t)
    Xtr,Ytr,Xv,Yv=inner
    X,Y,tx,ym,ys=full
    start=common.initial_theta(Xtr)
    all_repeats=[]
    best,bestval,selected=None,math.inf,None
    target_seed=sum(map(ord,t))
    for rep in range(common.REPEATS):
        seed=old.SEED_BASE["SMA"]+1009*rep+target_seed
        theta,vfit=old.sma_phase(Xtr,Ytr,seed,common.SELECT_GENS,start,Xv,Yv,False)
        need(theta is not None and theta.shape==(80,) and np.isfinite(theta).all()
             and math.isfinite(vfit),"INNER_OPTIMISATION_FAILED")
        all_repeats.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(vfit)})
        if vfit<bestval:
            best=theta.copy();bestval=float(vfit);selected=rep
    need(best is not None and selected is not None,"NO_INNER_CANDIDATE")
    mapped,mapping=map_theta_between_scalers(best,tr,fullstat)
    # Original iterative SMA optimization on full past history.  The
    # Gaussian-rules warm start is transported across coordinate systems.
    refit_seed=old.SEED_BASE["SMA"]+900001+1009*selected+target_seed
    final_theta,fullfit=old.sma_phase(X,Y,refit_seed,common.REFIT_GENS,
                                     mapped,None,None,True)
    need(np.isfinite(final_theta).all() and math.isfinite(fullfit),"BAD_REFIT")
    pstd=common.predict_with_fit(final_theta,X,Y,tx)[0]
    pred=np.asarray(pstd*ys+ym,float)
    c,s=common.decode(final_theta)
    need(pred.shape==(4,) and np.isfinite(pred).all()
         and abs(float(pred[0]))<1,"PATHOLOGICAL_NEW_OUTPUT")
    need(np.isfinite(c).all() and np.isfinite(s).all() and np.min(s)>=tsk.SPREAD_FLOOR,
         "RULE_SPREAD_INVALID")
    return pred,{
        "inner_validation_fitness":bestval,
        "full_refit_fitness":float(fullfit),
        "selected_repeat":int(selected),"repeat_records":all_repeats,
        "final_min_spread":float(np.min(s)),
        "final_max_spread":float(np.max(s)),
        "max_abs_center":float(np.max(np.abs(c))),
        "inner_training_last":ks[split-1],
        "inner_validation_first":ks[split],
        "inner_validation_last":ks[-1],
        "training_first":ks[0],"training_last":ks[-1],
        "training_rows":len(ks),
        "inner_train_scaler_fitted_on":"INNER_TRAIN_ONLY",
        "full_refit_scaler_fitted_on":"FULL_ORIGIN_HISTORY_ONLY",
        "antecedent_scaler_coordinate_mapping":mapping,
        "original_sma_optimizer_function_used":True,
    }

def legacy(samples,t):
    p,n,vf,ff,rep,reps,mi,ma,mc=old.predict_target(samples,t,"SMA")
    need(np.isfinite(p).all() and abs(float(p[0]))<1,"PATHOLOGICAL_OLD_OUTPUT")
    return np.asarray(p,float),{
        "training_rows":n,"training_first":"2010-03",
        "training_last":base.month_shift(t,-1),
        "inner_validation_fitness":float(vf),"full_refit_fitness":float(ff),
        "selected_repeat":rep,"repeat_records":reps,
        "final_min_spread":mi,"final_max_spread":ma,
        "max_abs_center":mc,
        "inner_train_scaler_fitted_on":"ALL_ORIGIN_ROWS_INCLUDING_VALIDATION",
        "original_sma_optimizer_function_used":True,
    }

def period_summary(rows):
    need(rows,"EMPTY_PHASE")
    return {
        "n":len(rows),
        "sum_abs_error":sum(r["absolute_error"] for r in rows),
        "mape_pct":sum(r["absolute_percentage_error"] for r in rows)/len(rows),
        "direction_correct":sum(r["direction_correct"] for r in rows),
        "worst_month":max(rows,key=lambda x:x["absolute_error"])["target_month"],
    }

def run(mode,path,out,shard):
    snap=source.read_snapshot(path)
    attest=spec()
    need(len(snap["records"])==54 and len(TGT)==54,"MISSING_SNAPSHOT_MONTHS")
    rows=snap["records"]
    if mode=="pilot": chosen=rows[:1]
    elif mode=="audit":chosen=rows
    else:
        need(shard is not None and 0<=shard<9,"INVALID_SIX_MONTH_SHARD")
        chosen=rows[shard*6:(shard+1)*6]
        need(len(chosen)==6,"INVALID_SHARD_ROWS")
    result={
        "status":"IN_PROGRESS",
        "model":NEW if mode in ("fixed","pilot","audit") else OLD,
        "analysis_role":"CORRECTED_NEW_SCIENTIFIC_VARIANT" if mode in ("fixed","pilot","audit")
                         else "QUARANTINED_HISTORICAL_INNER_SCALER_LEAK",
        "mode":mode,"shard":shard,
        "source_snapshot_sha256":snap["snapshot_sha256"],
        "source_firstprint_certified":False,
        "data_source":"NEON_STAKTRAKR_GPR_V2",
        "database_access":"NONE","model_provenance":attest,"rows":[],
    }
    for i,r in enumerate(chosen,1):
        t=r["target_month"]
        z=samples_of(r)
        ks,X,Y,tx,split=extract(z,t)
        need(ks[0]=="2010-03" and ks[-1]==r["origin_month"]
             and len(ks)==r["training_rows"],"ROW_CHRONOLOGY")
        if mode=="audit":
            pk={k:(x.copy(),None if y is None else y.copy()) for k,(x,y) in z.items()}
            pk[t]=(pk[t][0].copy(),np.full(4,1e12))
            pk["2099-01"]=(np.full(8,1e12),np.full(4,-1e12))
            a=prepared(z,t)
            b=prepared(pk,t)
            need(a[0]==b[0] and a[1]==b[1],"POISON_INFLUENCED_KEYS")
            need(all(np.array_equal(x,y) for x,y in zip(a[2],b[2])),"POISON_CHANGED_INNER")
            need(all(np.array_equal(x,y) for x,y in zip(a[3],b[3])),"POISON_CHANGED_FULL")
            need(all(np.array_equal(x,y) for x,y in zip(a[4],b[4])),"POISON_CHANGED_TRAIN_SCALER")
            need(all(np.array_equal(x,y) for x,y in zip(a[5],b[5])),"POISON_CHANGED_FULL_SCALER")
            result["rows"].append({
                "target_month":t,"origin_month":r["origin_month"],
                "training_rows":len(ks),"inner_train_last":ks[split-1],
                "inner_validation_first":ks[split],"inner_validation_last":ks[-1],
                "target_label_and_future_2099_poison_no_effect":True,
                "source_input_sha256":r["model_input_sha256"]})
            print("SMA_ELMFIS_INPUT_LEAK_AUDIT_PASS",i,"/",len(chosen),t,flush=True)
            continue
        if mode=="legacy":
            pred,meta=legacy(z,t)
        else:
            pred,meta=corrected(z,t)
            if mode=="pilot":
                pp={k:(x.copy(),None if y is None else y.copy()) for k,(x,y) in z.items()}
                pp[t]=(pp[t][0].copy(),np.full(4,1e10))
                pp["2099-01"]=(np.full(8,1e10),np.full(4,1e10))
                pred2,_=corrected(pp,t)
                need(np.array_equal(pred,pred2),"TARGET_OR_FUTURE_POISON_ALTERS_MODEL_PRED")
        prev=float(r["origin_gold_average"])
        actual=float(r["actual_xau_average"])
        forecast=prev*math.exp(float(pred[0]))
        need(math.isfinite(forecast) and forecast>0,"INVALID_FORECAST")
        need(meta["training_rows"]==r["training_rows"]
             and meta["training_last"]==r["origin_month"],"NONCAUSAL_TRAINING")
        result["rows"].append({
            "target_month":t,"origin_month":r["origin_month"],
            "forecast_xau_average":forecast,"actual_xau_average":actual,
            "origin_gold_average":prev,
            "absolute_error":abs(forecast-actual),
            "absolute_percentage_error":100*abs(forecast-actual)/actual,
            "direction_correct":int(np.sign(forecast-prev)==np.sign(actual-prev)),
            "prediction_gold_log_return":float(pred[0]),
            "training_rows":r["training_rows"],
            "model_input_sha256":r["model_input_sha256"],
            "origin_feature_sha256":r["origin_feature_sha256"],
            "origin_gpr_commit_sha":r["gpr_source_commit_sha"],
            "source_snapshot_sha256":snap["snapshot_sha256"],
            "optimizer_diagnostics":meta,
        })
        print("SMA_ELMFIS_MONTH_COMPLETE",mode,i,"/",len(chosen),t,
              "pred=",format(forecast,".6f"),
              "actual=",format(actual,".6f"),
              "direction=",result["rows"][-1]["direction_correct"],flush=True)
    if mode=="audit":
        need(len(result["rows"])==54,"AUDIT_INCOMPLETE")
        result["status"]="SMA_ELMFIS_54_ORIGIN_TARGET_AND_FUTURE_POISON_PASS_INNER_DEFECT_FOUND"
    elif mode=="pilot":
        result["status"]="SMA_ELMFIS_CORRECTED_V2_PILOT_PASS"
    elif mode=="fixed":
        result["status"]="SMA_ELMFIS_CORRECTED_V2_SIX_MONTH_SHARD_PASS"
    else:
        result["status"]="SMA_ELMFIS_LEGACY_V1_QUARANTINED_SIX_MONTH_SHARD_PASS"
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SMA_ELMFIS_SCIENCE_GATE",result["status"],flush=True)

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--mode",choices=("audit","pilot","legacy","fixed"),required=True)
    pa.add_argument("--snapshot",required=True)
    pa.add_argument("--output",required=True)
    pa.add_argument("--shard",type=int)
    args=pa.parse_args()
    run(args.mode,args.snapshot,args.output,args.shard)
