from __future__ import annotations
import json, math, os
from itertools import combinations
from pathlib import Path
import numpy as np
import psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics_mod

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"
FEATURES = ("GOLD_MR","GOLD_VW","SILVER_MR","SILVER_VW","PLATINUM_MR","PLATINUM_VW","PALLADIUM_MR","PALLADIUM_VW")
KAPPA_MONTHLY = 0.97
WARMUP = 30
C0_SCALE = 100.0
VAR_FLOOR = 1e-6
FORGETTING = (
    (0.99,0.99,"A99_L99"),
    (0.95,0.95,"A95_L95"),
    (0.99,0.95,"A99_L95"),
    (0.95,0.99,"A95_L99"),
    (1.00,1.00,"BMA_A1_L1"),
)

def logsumexp(a):
    a=np.asarray(a,float); m=float(np.max(a))
    return m+math.log(float(np.sum(np.exp(a-m))))

def norm_logweights(logw):
    z=logsumexp(logw); w=np.exp(np.asarray(logw)-z); w/=np.sum(w); return w

def masks_authority_gold():
    out=[]; optional=list(range(1,8))
    for r in range(len(optional)+1):
        for c in combinations(optional,r): out.append((0,)+tuple(c))
    return out

def masks_governed_multi4():
    out=[]; idx=list(range(8))
    for r in range(9):
        for c in combinations(idx,r): out.append(tuple(c))
    return out

def pool_indices(masks):
    return {
        "FULL":list(range(len(masks))),
        "PARSIMONIOUS_MAX3":[i for i,m in enumerate(masks) if len(m)<=3],
        "GOLD2_ONLY":[i for i,m in enumerate(masks) if all(j in (0,1) for j in m)],
    }

def scaled_data(samples,target):
    keys=sorted(k for k in samples if k<target)
    if len(keys)<WARMUP: raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X0=np.stack([samples[k][0] for k in keys]); Y0=np.stack([samples[k][1] for k in keys]); tx0=np.asarray(samples[target][0],float)
    Xw,Yw=X0[:WARMUP],Y0[:WARMUP]
    xm,xs=Xw.mean(0),Xw.std(0); ym,ys=Yw.mean(0),Yw.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return keys,(X0-xm)/xs,(Y0-ym)/ys,(tx0-xm)/xs,ym,ys

class ModelState:
    def __init__(self,mask,q):
        self.mask=tuple(mask); self.d=1+len(mask); self.q=q
        self.m=np.zeros((q,self.d),float)
        self.C=np.repeat((C0_SCALE*np.eye(self.d))[None,:,:],q,axis=0)
        self.h=np.ones(q,float)
    def row(self,x):
        return np.r_[1.0,np.asarray(x)[list(self.mask)]] if self.mask else np.ones(1,float)
    def forecast(self,x,lam):
        z=self.row(x); means=np.empty(self.q); vars_=np.empty(self.q); Rs=[]
        for j in range(self.q):
            R=self.C[j]/lam; qv=max(float(z@R@z+self.h[j]),VAR_FLOOR)
            means[j]=float(z@self.m[j]); vars_[j]=qv; Rs.append(R)
        return z,means,vars_,Rs
    def update(self,z,y,means,vars_,Rs):
        for j in range(self.q):
            R=Rs[j]; qv=vars_[j]; err=float(y[j]-means[j]); A=(R@z)/qv
            self.m[j]=self.m[j]+A*err
            C=R-np.outer(A,A)*qv; C=0.5*(C+C.T)
            ev=np.linalg.eigvalsh(C)
            if ev.min()<-1e-8: raise RuntimeError(f"STATE_COV_NOT_PSD min={ev.min()}")
            if ev.min()<0: C+=np.eye(self.d)*(-ev.min()+1e-10)
            self.C[j]=C
            self.h[j]=max(KAPPA_MONTHLY*self.h[j]+(1-KAPPA_MONTHLY)*err*err,VAR_FLOOR)

def run_one(samples,target,alpha,lam,lane):
    keys,X,Y,tx,ym,ys=scaled_data(samples,target)
    if lane=="AUTHORITY_GOLD":
        masks=masks_authority_gold(); q=1; Yuse=Y[:,:1]
    elif lane=="GOVERNED_MULTI4":
        masks=masks_governed_multi4(); q=4; Yuse=Y
    else: raise ValueError(lane)
    states=[ModelState(m,q) for m in masks]; K=len(states)
    log_post=np.full(K,-math.log(K),float); pools=pool_indices(masks)
    for t in range(len(keys)):
        log_prior=alpha*log_post; log_prior-=logsumexp(log_prior)
        ll=np.empty(K,float); cached=[]
        for k,st in enumerate(states):
            z,mu,var,Rs=st.forecast(X[t],lam); e=Yuse[t]-mu
            ll[k]=float(np.sum(-0.5*(np.log(2*np.pi*var)+(e*e)/var)))
            cached.append((z,mu,var,Rs))
        log_post=log_prior+ll; log_post-=logsumexp(log_post)
        for st,c in zip(states,cached): st.update(c[0],Yuse[t],c[1],c[2],c[3])
    log_prior=alpha*log_post; log_prior-=logsumexp(log_prior)
    means=np.empty((K,q))
    for k,st in enumerate(states): means[k]=st.forecast(tx,lam)[1]
    out={}
    for pool_name,idx in pools.items():
        idx=np.asarray(idx,int); w=norm_logweights(log_prior[idx]); pmeans=means[idx]
        dma_std=w@pmeans; best_local=int(np.argmax(w)); best_global=int(idx[best_local]); dms_std=means[best_global]
        pip={}
        for j,name in enumerate(FEATURES):
            pip[name]=float(np.sum([w[a] for a,gi in enumerate(idx) if j in masks[int(gi)]]))
        out[pool_name]={
            "dma_pred_log_return_gold":float(dma_std[0]*ys[0]+ym[0]),
            "dms_pred_log_return_gold":float(dms_std[0]*ys[0]+ym[0]),
            "dms_mask":[FEATURES[j] for j in masks[best_global]],
            "dms_weight":float(w[best_local]),
            "expected_predictors":float(sum(w[a]*len(masks[int(gi)]) for a,gi in enumerate(idx))),
            "posterior_inclusion_probabilities":pip,
            "model_count":int(len(idx)),
            "max_model_weight":float(np.max(w)),
            "effective_models":float(1.0/np.sum(w*w)),
        }
    return out

def row_from_pred(bundle,target,pred_ret,model,extra):
    origin=base.month_shift(target,-1)
    return {"target":target,"origin":origin,"model":model,"pred_log_return_gold":float(pred_ret),
            "forecast":float(bundle.core_gold[origin]*math.exp(float(pred_ret))),
            "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[origin]),**extra}

def active_metrics(rows): return metrics_mod.active_metrics(rows)
def yearly(rows): return metrics_mod.yearly(rows)

def evaluate_lane(bundle,cache,targets,lane):
    variants={}
    for a,l,tag in FORGETTING:
        for pool in ("FULL","PARSIMONIOUS_MAX3","GOLD2_ONLY"):
            for method in ("DMA","DMS"): variants[f"{lane}__{method}__{tag}__{pool}"]=[]
    for target in targets:
        samples=cache[target]
        for a,l,tag in FORGETTING:
            res=run_one(samples,target,a,l,lane)
            for pool,rr in res.items():
                common={"lane":lane,"alpha":a,"lambda":l,"pool":pool,"model_count":rr["model_count"],
                        "dms_mask":rr["dms_mask"],"dms_weight":rr["dms_weight"],
                        "expected_predictors":rr["expected_predictors"],
                        "max_model_weight":rr["max_model_weight"],"effective_models":rr["effective_models"],
                        "posterior_inclusion_probabilities":rr["posterior_inclusion_probabilities"]}
                k1=f"{lane}__DMA__{tag}__{pool}"; k2=f"{lane}__DMS__{tag}__{pool}"
                variants[k1].append(row_from_pred(bundle,target,rr["dma_pred_log_return_gold"],k1,common))
                variants[k2].append(row_from_pred(bundle,target,rr["dms_pred_log_return_gold"],k2,common))
    return variants

def rw_rows(bundle,targets):
    rows=[]
    for target in targets:
        origin=base.month_shift(target,-1); a=float(bundle.core_gold[target]); rw=float(bundle.core_gold[origin])
        rows.append({"target":target,"origin":origin,"model":"RANDOM_WALK","pred_log_return_gold":0.0,"forecast":rw,"actual":a,"rw":rw})
    return rows

def summarize_variant(rows): return {"metrics":active_metrics(rows),"yearly":yearly(rows),"rows":rows}

def finite_gate(all_rows):
    for r in all_rows:
        if not math.isfinite(r["forecast"]) or not math.isfinite(r["pred_log_return_gold"]): raise RuntimeError(f"NONFINITE {r['model']} {r['target']}")
        if abs(r["pred_log_return_gold"])>=1: raise RuntimeError(f"PATHOLOGICAL_RETURN {r['model']} {r['target']} {r['pred_log_return_gold']}")

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def rank_dev(summary):
    rows=[]
    for name,d in summary.items():
        m=d["metrics"]
        rows.append({"model":name,"sum_abs_error":m["sum_abs_error"],"direction_correct":m["direction_correct"],
                     "direction_total":m["n"],"direction_accuracy_pct":m["direction_accuracy_pct"],
                     "mae":m["mae"],"mape_pct":m["mape_pct"],"rmse":m["rmse"],"relative_mae_vs_rw":m["relative_mae_vs_rw"]})
    rows.sort(key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"])); return rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    all_targets=list(base.month_range(DEV_START,ST_END))
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in all_targets}
    period_targets={"dev":list(base.month_range(DEV_START,DEV_END)),
                    "transport_2025":list(base.month_range(TR_START,TR_END)),
                    "stress_2026":list(base.month_range(ST_START,ST_END))}
    raw={p:{} for p in period_targets}
    for lane in ("AUTHORITY_GOLD","GOVERNED_MULTI4"):
        for period,targets in period_targets.items(): raw[period].update(evaluate_lane(bundle,cache,targets,lane))
    summary={p:{k:summarize_variant(v) for k,v in raw[p].items()} for p in raw}
    finite_gate([r for p in raw.values() for v in p.values() for r in v])
    after=read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    dev_rank=rank_dev(summary["dev"])
    out={
        "model_family":"DMA_DMS_BATCH1_V1","stage_scope":"STAGE_0_TO_3_BATCH1",
        "method_authority":{
            "koop_korobilis_2012":"DMA/DMS via Kalman filtering; alpha/lambda forgetting factors; equal model prior; diffuse state prior; EWMA observation variance",
            "aye_et_al_2015":"gold-specific DMA/DMS evidence",
            "monthly_ewma_kappa":KAPPA_MONTHLY,
            "forgetting_grid":[{"alpha":a,"lambda":l,"tag":t} for a,l,t in FORGETTING],
            "bma_limit":"alpha=lambda=1"},
        "project_contract":{"target":"H=1 next-calendar-month average XAU/USD","features":list(FEATURES),
            "feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","dev_selection_authority":f"{DEV_START}..{DEV_END}",
            "2025_role":"LOCKED_TRANSPORT_REPORT_ONLY","2026_role":"RETROSPECTIVE_STRESS_REPORT_ONLY",
            "database":"READ_ONLY","random_split":"NONE","target_month_in_training":False},
        "lanes":{"AUTHORITY_GOLD":"Gold-only authority reference: intercept + Gold MR mandatory, remaining frozen features uncertain.",
                 "GOVERNED_MULTI4":"Project-parity extension: four metal returns updated jointly via product of task predictive densities; same subset across tasks."},
        "pools":{"FULL":"All candidate model masks in the lane.",
                 "PARSIMONIOUS_MAX3":"Only models using <=3 uncertain predictors; motivated by short-horizon DMA parsimony evidence.",
                 "GOLD2_ONLY":"Only Gold MR/VW candidate predictors (and intercept)."},
        "source_checks":bundle.source_checks,"authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "benchmarks":{p:{"random_walk":summarize_variant(rw_rows(bundle,targets))} for p,targets in period_targets.items()},
        "dev_ranking":dev_rank,"dev":summary["dev"],"transport_2025":summary["transport_2025"],"stress_2026":summary["stress_2026"],
        "selection_guard":"ONLY dev_ranking may inform later IDMA/refinement; 2025/2026 prohibited from selection."}
    Path("vw_midas_dma_batch1_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"best_dev_10":dev_rank[:10],"source_checks":bundle.source_checks,
                      "authority_invariants_unchanged":after==bundle.invariants_before,"variants":len(dev_rank)},sort_keys=True))

if __name__=="__main__": main()
