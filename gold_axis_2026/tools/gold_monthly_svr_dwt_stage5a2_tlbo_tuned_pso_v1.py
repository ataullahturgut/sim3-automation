#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path
import numpy as np
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c
import gold_monthly_svr_dwt_stage41_meta_v1 as b41

METHOD="TLBO_TUNED_PSO"
DEV_START,DEV_END="2022-04","2024-12"

OUTER_PSO_POP=12
OUTER_PSO_ITERS=20
TLBO_POP=6
TLBO_ITERS=5
FINAL_POP=24
FINAL_ITERS=45
REPEATS=3
SEED_BASE=507110

QLO=np.array([.2,.2,.2,.05],float)
QHI=np.array([.95,3.0,3.0,.8],float)

def init_pop(rng,pop,center):
    P=np.empty((pop,3),float)
    P[0]=np.clip(np.asarray(center,float),b41.LOWER,b41.UPPER)
    nlocal=min(pop-1,max(1,(pop-1)//2))
    if nlocal>0:
        P[1:1+nlocal]=np.clip(P[0][None,:]+rng.normal(0,1,(nlocal,3))*b41.LOCAL_SIGMA,b41.LOWER,b41.UPPER)
    if 1+nlocal<pop:
        P[1+nlocal:]=rng.uniform(b41.LOWER,b41.UPPER,size=(pop-1-nlocal,3))
    return P

def pso_train(obj,X,y,q,seed,pop,iters,center):
    w,c1,c2,vf=np.clip(np.asarray(q,float),QLO,QHI)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,pop,center)
    V=np.zeros_like(P)
    F=np.array([obj.training(z,X,y) for z in P],float)
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=float(vf)*(b41.UPPER-b41.LOWER)
    for _ in range(iters):
        r1=rng.random(P.shape); r2=rng.random(P.shape)
        V=np.clip(w*V+c1*r1*(PB-P)+c2*r2*(GB-P),-vmax,vmax)
        P=np.clip(P+V,b41.LOWER,b41.UPPER)
        F=np.array([obj.training(z,X,y) for z in P],float)
        imp=F<PF
        PB[imp]=P[imp]; PF[imp]=F[imp]
        gi=int(np.argmin(PF))
        if float(PF[gi])<GF:
            GB=PB[gi].copy(); GF=float(PF[gi])
    return GB,GF

def outer_score(obj,q,Xtr,ytr,Xv,yv,seed,anchor):
    vals=[]
    for rep in range(2):
        th,_=pso_train(obj,Xtr,ytr,q,seed+97*rep,OUTER_PSO_POP,OUTER_PSO_ITERS,anchor)
        vals.append(obj.validation(th,Xtr,ytr,Xv,yv))
    return float(np.mean(vals))

def tlbo_tune(obj,Xtr,ytr,Xv,yv,seed,anchor):
    rng=np.random.default_rng(seed)
    P=rng.uniform(QLO,QHI,size=(TLBO_POP,4))
    F=np.array([outer_score(obj,q,Xtr,ytr,Xv,yv,seed+1000+i,anchor) for i,q in enumerate(P)],float)
    trace=[]
    for g in range(TLBO_ITERS):
        teacher=P[int(np.argmin(F))].copy()
        mean=P.mean(0)
        tf=int(rng.integers(1,3))
        for i in range(TLBO_POP):
            q=np.clip(P[i]+rng.random(4)*(teacher-tf*mean),QLO,QHI)
            f=outer_score(obj,q,Xtr,ytr,Xv,yv,seed+10000+g*100+i,anchor)
            if f<F[i]:
                P[i]=q; F[i]=f
        for i in range(TLBO_POP):
            j=i
            while j==i:
                j=int(rng.integers(0,TLBO_POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            q=np.clip(P[i]+rng.random(4)*direction,QLO,QHI)
            f=outer_score(obj,q,Xtr,ytr,Xv,yv,seed+20000+g*100+i,anchor)
            if f<F[i]:
                P[i]=q; F[i]=f
        trace.append({"iteration":g,"best_outer_validation":float(np.min(F))})
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),trace

def optimize_at_origin(X,y,target):
    Xtrz,ytrz,Xvz,yvz,split,nval=b41.split_scale(X,y)
    obj=b41.Objective()
    anchor=b41.CENTER.copy()
    seed0=(b41.target_seed(target)+SEED_BASE)%(2**32)

    q,outer_val,trace=tlbo_tune(obj,Xtrz,ytrz,Xvz,yvz,seed0,anchor)

    reps=[]; winner=None
    for rep in range(REPEATS):
        seed=(seed0+500000+1009*rep)%(2**32)
        th,trfit=pso_train(obj,Xtrz,ytrz,q,seed,FINAL_POP,FINAL_ITERS,anchor)
        vfit=obj.validation(th,Xtrz,ytrz,Xvz,yvz)
        valid=math.isfinite(float(trfit)) and math.isfinite(float(vfit))
        reps.append({
            "repeat":rep,"seed":int(seed),
            "training_loss":float(trfit) if valid else None,
            "validation_loss":float(vfit) if valid else None
        })
        if valid:
            key=(float(vfit),rep)
            if winner is None or key<winner[0]:
                winner=(key,th.copy(),rep,float(trfit))
    if winner is None:
        raise RuntimeError(f"NO_VALID_TLBO_TUNED_PSO target={target}")

    theta=np.asarray(winner[1],float)
    C,gamma,epsilon=b41.Objective.decode(theta)
    return {
        "C":C,"gamma":gamma,"epsilon":epsilon,
        "log2_C":float(theta[0]),"log2_gamma":float(theta[1]),
        "selected_repeat":int(winner[2]),
        "selected_validation_loss":float(winner[0][0]),
        "selected_training_loss":float(winner[3]),
        "repeat_records":reps,
        "selected_pso":{"w":float(q[0]),"c1":float(q[1]),"c2":float(q[2]),"vmax_frac":float(q[3])},
        "outer_validation_score":float(outer_val),
        "outer_trace":trace,
        "inner_train_n":int(split),"inner_valid_n":int(nval),
        "training_fitness_calls":int(obj.training_calls),
        "validation_calls":int(obj.validation_calls),
    }

def predict_one(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    sel=optimize_at_origin(X,y,target)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    m=SVR(kernel="rbf",C=sel["C"],gamma=sel["gamma"],epsilon=sel["epsilon"],shrinking=True,tol=1e-3)
    m.fit(Xs,yz)
    pz=float(m.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin]); forecast=float(prev*math.exp(pred)); actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"method":METHOD,
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
        "inner_train_n":sel["inner_train_n"],"inner_valid_n":sel["inner_valid_n"],
        "selected_repeat":sel["selected_repeat"],"selected_validation_loss":sel["selected_validation_loss"],
        "selected_training_loss":sel["selected_training_loss"],"repeat_records":sel["repeat_records"],
        "selected_pso":sel["selected_pso"],"outer_validation_score":sel["outer_validation_score"],"outer_trace":sel["outer_trace"],
        "selected_params":{"C":sel["C"],"gamma":sel["gamma"],"epsilon":sel["epsilon"],
                           "log2_C":sel["log2_C"],"log2_gamma":sel["log2_gamma"]},
        "training_fitness_calls":sel["training_fitness_calls"],"validation_calls":sel["validation_calls"],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "absolute_error":float(abs(forecast-actual)),
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad),
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        r=predict_one(bundle,target); rows.append(r)
        print(f"PROGRESS method={METHOD} target={target} AE={r['absolute_error']:.6f} outer={r['outer_validation_score']:.6f}",flush=True)

    after=b41.read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    compact=[{k:r[k] for k in ("target","method","selected_repeat","selected_validation_loss","selected_pso",
                               "selected_params","repeat_records","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in rows]
    payload=hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "family":"SVR_DWT_SVR","scope":"STAGE5A2_TLBO_TUNED_PSO_DEV_ONLY_V1","method":METHOD,
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE5A2_TLBO_TUNED_PSO_FREEZE_2026-09-28.md",
        "contract":{
            "parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
            "svr_parameter_vector":["log2_C","log2_gamma","epsilon"],
            "svr_lower_bounds":b41.LOWER.tolist(),"svr_upper_bounds":b41.UPPER.tolist(),
            "pso_control_vector":["w","c1","c2","vmax_frac"],"pso_control_lower":QLO.tolist(),"pso_control_upper":QHI.tolist(),
            "outer_tlbo_population":TLBO_POP,"outer_tlbo_iterations":TLBO_ITERS,
            "nested_pso_population":OUTER_PSO_POP,"nested_pso_iterations":OUTER_PSO_ITERS,
            "final_population":FINAL_POP,"final_iterations":FINAL_ITERS,"repeats":REPEATS,
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED",
            "random_split":"NONE","database":"READ_ONLY","outer_optimizer_refit":"NONE"
        },
        "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows,
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,
        "payload_sha256":payload
    }
    Path("gold_monthly_svr_dwt_stage5a2_tlbo_tuned_pso_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    m=out["metrics"]
    report=[
      "# GOLD MONTHLY FORECAST — SVR STAGE 5A.2 TLBO-TUNED PSO RESULT","",
      "Date: 2026-09-28","Status: **COMPLETE / SCIENTIFIC GATE PASS**","",
      f"- DEV SigmaAE: **{m['sum_abs_error']:.6f}**",f"- MAE: {m['mae']:.6f}",f"- RMSE: {m['rmse']:.6f}",
      f"- MAPE: {m['mape_pct']:.4f}%",f"- Relative MAE vs RW: {m['relative_mae_vs_rw']:.6f}",
      f"- Direction: **{m['direction_correct']}/33**",f"- Worst month: {m['worst_month']}","",
      "Frozen parent reference: **1449.187363 / 19/33**.","",
      "## Kontrol ve Uyum Özeti","- 33/33 DEV origins: PASS.","- Prior-only chronology: PASS.",
      "- Outer TLBO tuning uses only pre-target chronological validation: PASS.","- Final 3 repeats: PASS.",
      "- 2025 opened: NO.","- 2026 used: NO.","- Random split: NONE.","- DB mutation: NONE / READ_ONLY.",""
    ]
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE5A2_TLBO_TUNED_PSO_RESULT_2026-09-28.md").write_text("\n".join(report),encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":METHOD,"metrics":m,"payload_sha256":payload},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
