from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np, psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb
import vw_midas_anfis_vanilla_v2 as core

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"
MAX_EPOCHS=100; CHECK_FRAC=.20; MIN_CHECK=12

def run_epochs(X,Y,epochs,Xcheck=None,Ycheck=None):
    c,s,labels=eb.fit_antecedents(X); l=np.log(np.clip(s,core.SFLOOR,core.SCEIL))
    k=core.K0; hist=[]; best_check=(float("inf"),0)
    for ep in range(epochs):
        beta=core.lse(X,Y,c,l); loss,gc,gl=core.loss_grad(X,Y,c,l,beta); hist.append(loss)
        if Xcheck is not None:
            e=core.design(Xcheck,c,l)@beta-Ycheck; cl=float(np.mean(e*e))
            if cl<best_check[0]-1e-12: best_check=(cl,ep)
        g=np.r_[gc.ravel(),gl.ravel()]; gn=float(np.linalg.norm(g))
        if np.isfinite(gn) and gn>1e-15:
            eta=k/gn; c-=eta*gc; l-=eta*gl; l=np.clip(l,math.log(core.SFLOOR),math.log(core.SCEIL))
        if len(hist)>=5:
            d=np.diff(hist[-5:]); sg=np.sign(d)
            if np.all(d<0): k*=core.KINC
            elif np.all(sg[:-1]*sg[1:]<0): k*=core.KDEC
    beta=core.lse(X,Y,c,l)
    return c,l,beta,labels,{"train_first":hist[0],"train_last":hist[-1],"check_best_mse":best_check[0],"check_best_epoch":best_check[1]}

def predict(samples,target):
    keys=sorted(k for k in samples if k<target)
    X0=np.stack([samples[k][0] for k in keys]); Y0=np.stack([samples[k][1] for k in keys]); tx0=samples[target][0][None,:]
    ncheck=max(MIN_CHECK,int(round(CHECK_FRAC*len(keys)))); nfit=len(keys)-ncheck
    if nfit<30: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL {target} {nfit}")
    xm,xs=X0[:nfit].mean(0),X0[:nfit].std(0); ym,ys=Y0[:nfit].mean(0),Y0[:nfit].std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    X=(X0[:nfit]-xm)/xs; Y=(Y0[:nfit]-ym)/ys; Xc=(X0[nfit:]-xm)/xs; Yc=(Y0[nfit:]-ym)/ys
    _,_,_,_,sel=run_epochs(X,Y,MAX_EPOCHS,Xc,Yc)
    chosen=int(sel["check_best_epoch"])+1

    # Refit chosen complexity on all origin-safe history; no target/check leakage.
    xm,xs=X0.mean(0),X0.std(0); ym,ys=Y0.mean(0),Y0.std(0); xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    X=(X0-xm)/xs; Y=(Y0-ym)/ys; tx=(tx0-xm)/xs
    c,l,b,labels,fit=run_epochs(X,Y,chosen)
    p=(core.design(tx,c,l)@b)[0]*ys+ym
    diag={"inner_fit_rows":nfit,"inner_check_rows":ncheck,"selected_epochs":chosen,
          "best_check_mse":sel["check_best_mse"],"full_train_first":fit["train_first"],"full_train_last":fit["train_last"]}
    return p,len(keys),[int((labels==r).sum()) for r in range(core.R)],diag

def ev(bundle,cache,a,b):
    rows=[]
    for t in base.month_range(a,b):
        p,n,c,d=predict(cache[t],t); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"train_rows":n,"rule_counts":c,"anfis_diag":d,
          "pred_log_return_gold":float(p[0]),"forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def main():
    dsn=os.environ["NEON_DATABASE_URL"]; bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=ev(bundle,cache,DEV_START,DEV_END); tr=ev(bundle,cache,TR_START,TR_END); st=ev(bundle,cache,ST_START,ST_END)
    after=inv(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":"VW_MIDAS_ANFIS_VANILLA_V3_CHECKED",
      "canonical_anfis":{"base":"Jang1993_hybrid_LSE_plus_gradient","rules":5,"inputs":8,"outputs":4,
       "membership":"Gaussian","metaheuristic":"NONE","max_epochs":MAX_EPOCHS,
       "checking":"chronological_last_20pct_min12_pre_target; choose_min_check_error_epoch; refit_all_history_at_selected_epoch"},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","random_split":"NONE",
       "target_month_in_training":False,"selection_period":f"{DEV_START}..{DEV_END}",
       "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
      "dev":{"metrics":eb.active_metrics(dev),"yearly":eb.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":eb.active_metrics(tr),"rows":tr},"stress_2026":{"metrics":eb.active_metrics(st),"rows":st}}
    Path("vw_midas_anfis_vanilla_v3_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS"); print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
