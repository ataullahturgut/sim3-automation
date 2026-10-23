"""AOA-ELM V2 structural bugfix, plus quarantined exact legacy reproduction.

The frozen legacy AOA-ELM uses z=mu*(HI-LO)+LO; with LO=-2, HI=2,
mu=0.5 it is mathematically zero, making the four AOA candidate update
cases either best or zero. V2 repairs only search coordinate semantics:
normalised decision vector q∈[0,1]^144 and the original four AOA
formulas on q where z=0.5 is nonzero; model theta=-2+4*q.

A second defect in historical AOA fitness is selection-fold leakage
from computing standardizers on all prior-origin samples before splitting
chronological inner validation. V2 fits inner validation standardizers
only to the inner-training slice; final full-history refit uses a separate
full-history-only standardizer.

No target-month labels, inputs or prices are seen by predictor. This is
NEW v2 research variant, not a claim that historical v1 was valid AOA.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import vw_midas_elm_meta_batch_21_25_v1 as original
import gold_monthly_h1_ann_frozen_snapshot_replay_v2 as snaps

MODEL="AOA_ELM_FIXED_V2"
LEGACY="AOA_ELM_LEGACY_ZERO_FACTOR_V1"
HIDDEN=16
ALPHA=.001
DIM=8*HIDDEN+HIDDEN
LO=-2.0
HI=2.0
SEED_BASE=original.SEEDS["AOA"]
POP=24
GENERATIONS=35
MU=.5

def require(ok,msg):
    if not ok:raise RuntimeError("AOA_ELM_VALIDATION_FAILED "+msg)

def legacy_failure_certificate():
    factor=.5*(original.HI-original.LO)+original.LO
    require(abs(factor)<1e-15,"LEGACY_ARITHMETIC_ZERO_NOT_FOUND")
    require(original.HIDDEN==HIDDEN and original.ALPHA==ALPHA,"ARCHITECTURE_CHANGED")
    require(original.DIM==DIM and original.SEEDS["AOA"]==SEED_BASE,"LEGACY_SEED_OR_DIM_CHANGED")
    return {
        "legacy_AOA_multiplier":factor,
        "legacy_AOA_compromised":True,
        "legacy_candidate_classes":["zero","incumbent_best"],
        "legacy_score_must_not_be_certified_as_valid_AOA":True,
        "legacy_implementation_sha256":hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),
        "corrected_optimizer":"AOA_IN_UNIT_HYPERCUBE",
        "corrected_optimizer_dimension":DIM,
        "corrected_mu":MU,
        "corrected_multiplier":MU*(1.0-0.0)+0.0,
        "inner_validation_scaler_train_only":True,
        "final_full_history_scaler_train_only":True,
        "neon_price_firstprint_certified":False,
    }

def samples_for(rec):
    result={}
    for k,(x,y) in rec["samples"].items():
        result[k]=(np.asarray(x,dtype=float),None if y is None else np.asarray(y,dtype=float))
    t=rec["target_month"]
    require(result[t][1] is None,"TARGET_MONTH_LABEL_NOT_NULL")
    return result

def datasets(samples,t):
    ks=sorted(k for k in samples if k<t)
    require(ks==list(base.month_range("2010-03",base.month_shift(t,-1))),"TRAINING_SEQUENCE_GAP_OR_FUTURE")
    X=np.stack([samples[k][0] for k in ks]).astype(float)
    Y=np.stack([samples[k][1] for k in ks]).astype(float)
    tx=np.asarray(samples[t][0],dtype=float).reshape(1,-1)
    require(X.shape==(len(ks),8) and Y.shape==(len(ks),4) and tx.shape==(1,8),"WRONG_INPUT_SHAPE")
    require(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(tx).all(),"NONFINITE_MODEL_INPUT")
    n=len(X)
    nval=max(6,int(round(.2*n)))
    split=n-nval
    require(split>=30 and 0<nval<n,"BAD_VALIDATION_SPLIT")
    # Leakage-resistant scalers for INNER selection fit only X[:split],Y[:split].
    def stats(x,y):
        xm=x.mean(0); xs=x.std(0); ym=y.mean(0); ys=y.std(0)
        xs=np.where(xs<1e-9,1.0,xs)
        ys=np.where(ys<1e-9,1.0,ys)
        return xm,xs,ym,ys
    xm,xs,ym,ys=stats(X[:split],Y[:split])
    inner=((X[:split]-xm)/xs,(Y[:split]-ym)/ys,
           (X[split:]-xm)/xs,(Y[split:]-ym)/ys)
    fxm,fxs,fym,fys=stats(X,Y)
    full=((X-fxm)/fxs,(Y-fym)/fys,(tx-fxm)/fxs,fym,fys)
    return ks,split,inner,full

def fitness(q,inner):
    require(len(q)==DIM,"BAD_SEARCH_VECTOR_LENGTH")
    Xtr,Ytr,Xva,Yva=inner
    theta=LO+(HI-LO)*np.asarray(q,float)
    W,b=original.decode(theta)
    beta=original.fit_beta(Xtr,Ytr,W,b)
    pred=original.act(Xva@W+b)@beta
    result=float(.7*np.mean(abs(pred[:,0]-Yva[:,0]))+.3*np.mean(abs(pred-Yva)))
    return result if math.isfinite(result) else 1e12

def corrected_aoa(inner,seed):
    rng=np.random.default_rng(seed)
    pop=rng.uniform(0.0,1.0,(POP,DIM))
    scores=np.array([fitness(q,inner) for q in pop],dtype=float)
    require(np.isfinite(scores).all(),"NONFINITE_INITIAL_FITNESS")
    nonzero_moves=0
    unique_candidates=set()
    z=MU*(1-0)+0.0
    require(z>.1 and z<1.0,"DEGENERATE_FIXED_AOA_FACTOR")
    for step in range(GENERATIONS):
        best=pop[int(np.argmin(scores))].copy()
        moa=0.2+0.8*(step/max(1,GENERATIONS-1))
        mop=1-(step/max(1,GENERATIONS))**(1/5.0)
        for i in range(POP):
            r1,r2,r3=rng.random(),rng.random(),rng.random()
            if r1>moa:
                if r2<.5: proposal=best/(mop+1e-12)*z
                else: proposal=best*mop*z
            else:
                if r3<.5: proposal=best-mop*z
                else:proposal=best+mop*z
            cand=np.clip(np.asarray(proposal,dtype=float),0,1)
            if np.max(np.abs(cand-best))>1e-11:
                nonzero_moves+=1
            unique_candidates.add(hashlib.sha256(cand.tobytes()).hexdigest())
            score=fitness(cand,inner)
            if score<scores[i]:
                pop[i]=cand
                scores[i]=score
    require(nonzero_moves>=POP,"DEGENERATE_AOA_SEARCH_ONLY_BEST_OR_ZERO")
    require(len(unique_candidates)>=10,"AOA_SEARCH_LACKS_EXPLORATION")
    idx=int(np.argmin(scores))
    return pop[idx].copy(),float(scores[idx]),{
        "seed":int(seed),"population":POP,"generations":GENERATIONS,
        "candidate_evaluations":POP*(GENERATIONS+1),
        "nonzero_search_moves":int(nonzero_moves),
        "distinct_candidate_hashes":len(unique_candidates),
        "inner_fitness":float(scores[idx]),
        "AOA_original_kernel_equations_preserved_in_unit_cube":True,
    }

def corrected_predict(samples,target):
    ks,split,inner,full=datasets(samples,target)
    seed=SEED_BASE+sum(map(ord,target))
    q,val,diag=corrected_aoa(inner,seed)
    W,b=original.decode(LO+(HI-LO)*q)
    X,Y,tx,ym,ys=full
    beta=original.fit_beta(X,Y,W,b)
    p=np.asarray((original.act(tx@W+b)@beta)[0]*ys+ym,float)
    require(p.shape==(4,) and np.isfinite(p).all() and np.max(np.abs(p))<1,
            "INVALID_CORRECTED_FORECAST")
    return p,len(ks),{
       **diag,
       "training_first":ks[0],"training_last":ks[-1],
       "inner_train_last":ks[split-1],
       "inner_validation_first":ks[split],
       "inner_validation_last":ks[-1],
       "validation_scaler_train_only":True,
       "refit_scaler_past_history_only":True,
    }

def rep_metrics(rows):
    require(rows,"EMPTY_REPORT_ROWS")
    return {
        "n":len(rows),
        "sum_abs_error":sum(r["absolute_error"] for r in rows),
        "mape_pct":sum(r["absolute_percentage_error"] for r in rows)/len(rows),
        "directions_correct":sum(r["direction_correct"] for r in rows),
        "worst_month":max(rows,key=lambda r:r["absolute_error"])["target_month"],
    }

def execute(mode,path,output):
    source=snaps.read_snapshot(path)
    specs=legacy_failure_certificate()
    require(len(source["records"])==54,"SOURCE_PERIOD_COUNT")
    out={
        "status":"IN_PROGRESS",
        "model":MODEL if mode!="legacy" else LEGACY,
        "analysis_role":"NEW_CORRECTED_CHALLENGER" if mode!="legacy" else "QUARANTINED_ORIGINAL_BUG_REPRODUCTION",
        "contract":"NEON_STAKTRAKR_GPR_V2",
        "source_firstprint_certified":False,
        "database_access":"NONE",
        "algorithm":specs,
        "source_snapshot_sha256":source["snapshot_sha256"],
        "rows":[],
    }
    rs=source["records"][:1] if mode=="pilot" else source["records"]
    for i,r in enumerate(rs,1):
        t=r["target_month"]
        data=samples_for(r)
        if mode=="audit":
            ks,split,inner,full=datasets(data,t)
            require(ks[0]=="2010-03" and ks[-1]==r["origin_month"],"LEAKING_TRAIN_KEYS")
            poisoned=samples_for(r)
            poisoned[t]=(poisoned[t][0].copy(),np.array([1e9,-1e9,1e9,-1e9]))
            poisoned["2099-01"]=(np.full(8,1e10),np.full(4,1e10))
            pk,ps,pi,pf=datasets(poisoned,t)
            require(pk==ks and ps==split,"POISONED_KEYS_CHANGED")
            require(all(np.array_equal(x,y) for x,y in zip(inner,pi)) and
                    all(np.array_equal(x,y) for x,y in zip(full,pf)),
                    "TARGET_Y_OR_FUTURE_POISON_CHANGED_TRAIN_AND_VALIDATION")
            # verify original inner_scaler was not fitted separately from the
            # inner training subset; thus declare legacy limitation explicitly.
            require(len(ks)==r["training_rows"],"TRAIN_ROW_COUNT")
            diag={"seed":SEED_BASE+sum(map(ord,t)),"population":POP,
                  "generations":GENERATIONS,"candidate_evaluations":0,
                  "nonzero_search_moves":None,"inner_fitness":None,
                  "training_first":ks[0],"training_last":ks[-1],
                  "inner_train_last":ks[split-1],"inner_validation_first":ks[split],
                  "inner_validation_last":ks[-1]}
            pred=None
        elif mode=="legacy":
            # strictly unchanged legacy algorithm; DO NOT approve as true AOA.
            p,n,fit=original.predict(data,t,"AOA")
            pred=np.asarray(p,float)
            diag={"training_first":"2010-03","training_last":r["origin_month"],
                  "inner_fitness":float(fit),"legacy_multiplier_zero":True,
                  "candidate_evaluations":POP*(GENERATIONS+1)}
        else:
            pred,n,diag=corrected_predict(data,t)
            require(n==r["training_rows"],"CORRECTED_TRAINING_ROW_MISMATCH")
            if mode=="pilot":
                pd=samples_for(r)
                pd[t]=(pd[t][0].copy(),np.full(4,1e12))
                pd["2099-01"]=(np.full(8,1e12),np.full(4,1e12))
                pp,_,_=corrected_predict(pd,t)
                require(np.array_equal(pp,pred),"ACTUAL_FUTURE_POISON_CHANGED_CORRECTED_FORECAST")
        require(diag["training_first"]=="2010-03" and
                diag["training_last"]==r["origin_month"],"LEAKING_TRAINING_PERIOD")
        if pred is not None:
            require(np.isfinite(pred).all() and np.max(np.abs(pred))<1,"PATHOLOGICAL_ELM_OUTPUT")
            prev=float(r["origin_gold_average"])
            actual=float(r["actual_xau_average"])
            forecast=prev*math.exp(float(pred[0]))
            require(math.isfinite(forecast) and forecast>0,"BAD_PRICE_PREDICTION")
            direction=int(np.sign(forecast-prev)==np.sign(actual-prev))
            row={"target_month":t,"origin_month":r["origin_month"],
                 "forecast_xau_average":forecast,"actual_xau_average":actual,
                 "origin_gold_average":prev,
                 "absolute_error":abs(forecast-actual),
                 "absolute_percentage_error":100*abs(forecast-actual)/actual,
                 "direction_correct":direction,
                 "prediction_gold_log_return":float(pred[0]),
                 "gpr_commit_sha":r["gpr_source_commit_sha"],
                 "origin_model_input_sha256":r["model_input_sha256"],
                 "source_snapshot_sha256":source["snapshot_sha256"],
                 "training_rows":r["training_rows"],
                 "algorithm_diagnostics":diag}
        else:
            row={"target_month":t,"origin_month":r["origin_month"],
                 "training_rows":r["training_rows"],
                 "target_future_poison_changed_feature_matrices":False,
                 "origin_model_input_sha256":r["model_input_sha256"],
                 "source_snapshot_sha256":source["snapshot_sha256"],
                 "algorithm_diagnostics":diag}
        out["rows"].append(row)
        print("AOA_ELM_MONTH",mode,i,"/",len(rs),t,
              "" if pred is None else "forecast="+format(row["forecast_xau_average"],".6f"),
              flush=True)
    require(len(out["rows"])==len(rs),"INCOMPLETE")
    if mode=="audit":
        out["status"]="AOA_ELM_54_ORIGINS_PROVENANCE_AND_POISON_PASS_WITH_LEGACY_BUG_FOUND"
    elif mode=="pilot":
        out["status"]="AOA_ELM_FIXED_V2_ONE_MONTH_PILOT_PASS"
    elif mode=="legacy":
        out["status"]="AOA_ELM_LEGACY_ZERO_FACTOR_54_REPLAY_QUARANTINED"
        out["metrics"]={"DEV_2022_2024":rep_metrics(out["rows"][:33]),
                        "TEST_2025":rep_metrics(out["rows"][33:45]),
                        "STRESS_2026_01_09":rep_metrics(out["rows"][45:])}
    else:
        out["status"]="AOA_ELM_FIXED_V2_FULL_54_PASS"
        out["metrics"]={"DEV_2022_2024":rep_metrics(out["rows"][:33]),
                        "TEST_2025":rep_metrics(out["rows"][33:45]),
                        "STRESS_2026_01_09":rep_metrics(out["rows"][45:])}
        for k,v in out["metrics"].items():
            print("AOA_ELM_V2_VALIDATED_PERIOD",k,json.dumps(v,sort_keys=True),flush=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("AOA_ELM_SCIENCE_GATE",out["status"],flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--mode",choices=["audit","pilot","full","legacy"],required=True)
    a.add_argument("--snapshot",required=True)
    a.add_argument("--output",required=True)
    args=a.parse_args()
    execute(args.mode,args.snapshot,args.output)
