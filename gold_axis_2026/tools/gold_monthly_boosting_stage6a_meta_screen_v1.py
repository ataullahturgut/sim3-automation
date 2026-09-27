from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage1_canonical_v1 as s1
import gold_monthly_boosting_stage2_feature_representation_v1 as s2

common = importlib.import_module("vw_midas_elmfis_meta_batch_1_v1")
mods = [
    common,
    importlib.import_module("vw_midas_elmfis_meta_batch_2_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_3_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_4_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_5_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_6_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_7_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_8_v1"),
    importlib.import_module("vw_midas_elmfis_meta_batch_9_v1"),
]

DEV_ANCHORS = ("2022-06","2022-12","2023-06","2023-12","2024-06","2024-12")
INNER_VAL_MONTHS = 12
POP_SIZE = 10
MAX_EVALS = 80
GENERATIONS = 20
PENALTY = 1e12

METHODS = ["VANILLA"]
PHASES = {}
SEED_BASE = {}
for m in mods:
    for k,v in getattr(m,"PHASE",{}).items():
        PHASES[k]=v
    for k,v in getattr(m,"SEED_BASE",{}).items():
        SEED_BASE[k]=int(v)
METHODS += [
    "PSO","GA","DE","MPA","ABC","SSA","GWO","WOA","HHO","ACO","BAT",
    "FA","MFO","FPA","FA_FPA","CS","SCA","SALP","SMA","GOA","ALO","TLBO",
    "JAYA","HGS","CHOA","HGSO","AOA","CPA","KRILL","CROW","DE_ABC","MULTISWARM",
    "CHHHO_PW_PM4"
]
assert len(METHODS)==34
assert set(METHODS[1:-1]) == set(PHASES)

LANES = {
    "CATBOOST": {
        "rep":"CURRENT8","start":"2010-03","model":"CATBOOST_ORDERED",
        "baseline":{"depth":6,"iterations":100,"learning_rate":0.03,
                    "l2_leaf_reg":3.0,"random_strength":1.0},
        "dim":5,
    },
    "GBRT": {
        "rep":"DAILY_SUMMARY12","start":"2010-03","model":"GBRT",
        "baseline":{"max_depth":2,"n_estimators":100,"learning_rate":0.10,
                    "min_samples_leaf":2,"subsample":1.0,"max_features":1.0},
        "dim":6,
    },
    "XGBOOST": {
        "rep":"CURRENT8","start":"2010-03","model":"XGBOOST",
        "baseline":{"max_depth":4,"n_estimators":200,"learning_rate":0.05,
                    "min_child_weight":1.0,"reg_alpha":0.01,"reg_lambda":5.0,
                    "gamma":0.001,"subsample":0.80,"colsample_bytree":0.80},
        "dim":9,
    },
    "LIGHTGBM": {
        "rep":"MIXED20","start":"2010-05","model":"LIGHTGBM",
        "baseline":{"num_leaves":31,"max_depth":6,"min_child_samples":10,
                    "n_estimators":300,"learning_rate":0.03,
                    "reg_alpha":0.0,"reg_lambda":0.0,
                    "subsample":1.0,"colsample_bytree":1.0},
        "dim":9,
    },
}

def log_interp(z, lo, hi):
    return float(math.exp(math.log(lo) + float(z)*(math.log(hi)-math.log(lo))))

def int_interp(z, lo, hi):
    return int(round(lo + float(z)*(hi-lo)))

def decode(lane_name, theta):
    z=np.clip(np.asarray(theta,float),0.0,1.0)
    if lane_name=="CATBOOST":
        return {
            "depth":int_interp(z[0],4,9),
            "iterations":int_interp(z[1],60,400),
            "learning_rate":log_interp(z[2],0.01,0.12),
            "l2_leaf_reg":log_interp(z[3],1.0,20.0),
            "random_strength":float(3.0*z[4]),
        }
    if lane_name=="GBRT":
        return {
            "max_depth":int_interp(z[0],1,4),
            "n_estimators":int_interp(z[1],60,350),
            "learning_rate":log_interp(z[2],0.02,0.18),
            "min_samples_leaf":int_interp(z[3],1,8),
            "subsample":float(0.70+0.30*z[4]),
            "max_features":float(0.60+0.40*z[5]),
        }
    if lane_name=="XGBOOST":
        return {
            "max_depth":int_interp(z[0],1,6),
            "n_estimators":int_interp(z[1],80,400),
            "learning_rate":log_interp(z[2],0.01,0.15),
            "min_child_weight":float(1.0+7.0*z[3]),
            "reg_alpha":float(z[4]),
            "reg_lambda":log_interp(z[5],0.5,10.0),
            "gamma":float(0.10*z[6]),
            "subsample":float(0.70+0.30*z[7]),
            "colsample_bytree":float(0.70+0.30*z[8]),
        }
    if lane_name=="LIGHTGBM":
        return {
            "num_leaves":int_interp(z[0],7,48),
            "max_depth":int_interp(z[1],3,8),
            "min_child_samples":int_interp(z[2],5,30),
            "n_estimators":int_interp(z[3],100,450),
            "learning_rate":log_interp(z[4],0.01,0.10),
            "reg_alpha":float(z[5]),
            "reg_lambda":float(5.0*z[6]),
            "subsample":float(0.70+0.30*z[7]),
            "colsample_bytree":float(0.70+0.30*z[8]),
        }
    raise KeyError(lane_name)

def encode_baseline(lane_name):
    b=LANES[lane_name]["baseline"]
    if lane_name=="CATBOOST":
        vals=[
            (b["depth"]-4)/(9-4),
            (b["iterations"]-60)/(400-60),
            (math.log(b["learning_rate"])-math.log(0.01))/(math.log(0.12)-math.log(0.01)),
            (math.log(b["l2_leaf_reg"])-math.log(1))/(math.log(20)-math.log(1)),
            b["random_strength"]/3,
        ]
    elif lane_name=="GBRT":
        vals=[
            (b["max_depth"]-1)/3,
            (b["n_estimators"]-60)/(350-60),
            (math.log(b["learning_rate"])-math.log(0.02))/(math.log(0.18)-math.log(0.02)),
            (b["min_samples_leaf"]-1)/7,
            (b["subsample"]-.70)/.30,
            (b["max_features"]-.60)/.40,
        ]
    elif lane_name=="XGBOOST":
        vals=[
            (b["max_depth"]-1)/5,
            (b["n_estimators"]-80)/(400-80),
            (math.log(b["learning_rate"])-math.log(.01))/(math.log(.15)-math.log(.01)),
            (b["min_child_weight"]-1)/7,
            b["reg_alpha"],
            (math.log(b["reg_lambda"])-math.log(.5))/(math.log(10)-math.log(.5)),
            b["gamma"]/.10,
            (b["subsample"]-.70)/.30,
            (b["colsample_bytree"]-.70)/.30,
        ]
    elif lane_name=="LIGHTGBM":
        vals=[
            (b["num_leaves"]-7)/(48-7),
            (b["max_depth"]-3)/5,
            (b["min_child_samples"]-5)/25,
            (b["n_estimators"]-100)/(450-100),
            (math.log(b["learning_rate"])-math.log(.01))/(math.log(.10)-math.log(.01)),
            b["reg_alpha"],
            b["reg_lambda"]/5,
            (b["subsample"]-.70)/.30,
            (b["colsample_bytree"]-.70)/.30,
        ]
    else:
        raise KeyError(lane_name)
    return np.clip(np.asarray(vals,float),0,1)

def make_model(lane_name, params):
    p=dict(s1.PARAMS[LANES[lane_name]["model"]])
    p.update(params)
    if lane_name=="CATBOOST":
        p["loss_function"]="RMSE"
        p["boosting_type"]="Ordered"
        p["random_seed"]=1701
        p["allow_writing_files"]=False
        p["verbose"]=False
        p["thread_count"]=1
        return CatBoostRegressor(**p)
    if lane_name=="GBRT":
        p["loss"]="absolute_error"
        p["random_state"]=1701
        return GradientBoostingRegressor(**p)
    if lane_name=="XGBOOST":
        p["objective"]="reg:squarederror"
        p["tree_method"]="hist"
        p["random_state"]=1701
        p["n_jobs"]=1
        p["verbosity"]=0
        return XGBRegressor(**p)
    if lane_name=="LIGHTGBM":
        p["objective"]="regression_l1"
        p["random_state"]=1701
        p["n_jobs"]=1
        p["verbosity"]=-1
        p["deterministic"]=True
        p["force_col_wise"]=True
        p["subsample_freq"]=1 if float(p.get("subsample",1.0)) < .999999 else 0
        return LGBMRegressor(**p)
    raise KeyError(lane_name)

def prepare_anchor(bundle,samples,target,lane_name):
    lane=LANES[lane_name]
    keys=sorted(k for k in samples if lane["start"] <= k < target)
    if len(keys) < INNER_VAL_MONTHS + 36:
        raise RuntimeError(f"INNER_HISTORY_TOO_SMALL lane={lane_name} target={target} n={len(keys)}")
    split=len(keys)-INNER_VAL_MONTHS
    tr=keys[:split]; va=keys[split:]
    Xtr=np.stack([s2.rep_feature(bundle,samples,k,lane["rep"]) for k in tr])
    ytr=np.asarray([float(samples[k][1][0]) for k in tr],float)
    Xv=np.stack([s2.rep_feature(bundle,samples,k,lane["rep"]) for k in va])
    actual=np.asarray([float(bundle.core_gold[k]) for k in va],float)
    prev=np.asarray([float(bundle.core_gold[base.month_shift(k,-1)]) for k in va],float)
    rw_ae=float(np.abs(prev-actual).sum())
    Xa=np.stack([s2.rep_feature(bundle,samples,k,lane["rep"]) for k in keys])
    ya=np.asarray([float(samples[k][1][0]) for k in keys],float)
    xt=s2.rep_feature(bundle,samples,target,lane["rep"]).reshape(1,-1)
    return {
        "keys":keys,"inner_train_keys":tr,"inner_val_keys":va,
        "Xtr":Xtr,"ytr":ytr,"Xv":Xv,"actual_v":actual,"prev_v":prev,
        "rw_ae":rw_ae,"Xall":Xa,"yall":ya,"xt":xt,
        "anchor_prev":float(bundle.core_gold[base.month_shift(target,-1)]),
        "anchor_actual":float(bundle.core_gold[target]),
    }

def params_key(params):
    out=[]
    for k in sorted(params):
        v=params[k]
        if isinstance(v,float):
            v=round(v,10)
        out.append((k,v))
    return tuple(out)

class BudgetObjective:
    def __init__(self,lane_name,data,max_evals):
        self.lane_name=lane_name; self.data=data; self.max_evals=max_evals
        self.calls=0; self.cache={}; self.best_loss=math.inf; self.best_theta=None
    def __call__(self,theta):
        self.calls += 1
        if self.calls > self.max_evals:
            return PENALTY
        z=np.clip(np.asarray(theta,float),0,1)
        params=decode(self.lane_name,z)
        key=params_key(params)
        if key in self.cache:
            loss=self.cache[key]
        else:
            try:
                model=make_model(self.lane_name,params)
                model.fit(self.data["Xtr"],self.data["ytr"])
                pred=np.asarray(model.predict(self.data["Xv"]),float).reshape(-1)
                if not np.isfinite(pred).all() or np.any(np.abs(pred)>=1.0):
                    loss=PENALTY
                else:
                    fc=self.data["prev_v"]*np.exp(pred)
                    ae=float(np.abs(fc-self.data["actual_v"]).sum())
                    loss=float(ae/max(self.data["rw_ae"],1e-12))
            except Exception:
                loss=PENALTY
            self.cache[key]=loss
        if loss < self.best_loss:
            self.best_loss=float(loss); self.best_theta=z.copy()
        return float(loss)

def patch_meta(dim,obj):
    lo=np.zeros(dim,float); hi=np.ones(dim,float); span=hi-lo
    common.PARAM_DIM=dim; common.LOWER=lo; common.UPPER=hi; common.POP_SIZE=POP_SIZE
    common.LOCAL_SIGMA=np.full(dim,0.15,float)
    common.REFIT_SIGMA=np.full(dim,0.05,float)

    def init_population(rng,center,refit=False):
        center=np.clip(np.asarray(center,float),lo,hi)
        pop=np.empty((POP_SIZE,dim),float); pop[0]=center
        nlocal=(POP_SIZE-1)//2
        sigma=.05 if refit else .15
        if nlocal:
            pop[1:1+nlocal]=np.clip(center+rng.normal(0,1,(nlocal,dim))*sigma,lo,hi)
        st=1+nlocal
        if st<POP_SIZE:
            pop[st:]=rng.uniform(lo,hi,size=(POP_SIZE-st,dim))
        return pop

    common.init_population=init_population
    common.training_loss=lambda theta,X=None,Y=None: obj(theta)
    common.population_fit=lambda pop,X=None,Y=None: np.asarray([obj(x) for x in pop],float)

    def validation_pick(pop,fit,Xtr=None,Ytr=None,Xv=None,Yv=None,incumbent_theta=None,incumbent_val=math.inf):
        i=int(np.argmin(fit)); v=float(fit[i])
        if v<incumbent_val:
            return pop[i].copy(),v
        return incumbent_theta,incumbent_val
    common.validation_pick=validation_pick

    for m in mods:
        for name,val in (
            ("PARAM_DIM",dim),("LOWER",lo),("UPPER",hi),("SPAN",span),("POP_SIZE",POP_SIZE)
        ):
            if hasattr(m,name):
                setattr(m,name,val)

def piecewise_next(x,p=.4):
    x=float(np.clip(x,1e-12,1-1e-12))
    if x<p:
        y=x/p
    elif x<.5:
        y=(x-p)/(.5-p)
    elif x<1-p:
        y=(1-p-x)/(.5-p)
    else:
        y=(1-x)/p
    return float(np.clip(y,1e-12,1-1e-12))

class PiecewiseChaos:
    def __init__(self,seed):
        rng=np.random.default_rng(seed)
        self.x=float(rng.uniform(.013,.987))
    def rand(self,shape=None):
        n=1 if shape is None else int(np.prod(shape))
        a=np.empty(n,float)
        for i in range(n):
            self.x=piecewise_next(self.x,.4); a[i]=self.x
        if shape is None: return float(a[0])
        return a.reshape(shape)

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/
           (math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,shape); v=rng.normal(0,1,shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def chhho_pw_pm4_phase(seed,generations,center,obj):
    dim=len(center); lo=np.zeros(dim); hi=np.ones(dim); span=hi-lo
    chaos=PiecewiseChaos(seed)
    rng=np.random.default_rng(seed+991)
    pop=lo+chaos.rand((POP_SIZE,dim))*span
    pop[0]=np.clip(center,lo,hi)
    fit=np.asarray([obj(x) for x in pop],float)
    best=pop[int(np.argmin(fit))].copy(); bestf=float(np.min(fit))
    for t in range(generations):
        if obj.calls>=obj.max_evals: break
        rabbit=pop[int(np.argmin(fit))].copy()
        E1=2*(1-(t+1)/max(1,generations))
        mean=pop.mean(0)
        new=pop.copy()
        for i in range(POP_SIZE):
            if obj.calls>=obj.max_evals: break
            E0=2*chaos.rand()-1; E=E1*E0
            q=chaos.rand(); J=2*(1-chaos.rand())
            if abs(E)>=1:
                if q>=.5:
                    j=min(POP_SIZE-1,int(chaos.rand()*POP_SIZE))
                    xr=pop[j]
                    r1=chaos.rand((dim,)); r2=chaos.rand((dim,))
                    cand=xr-r1*np.abs(xr-2*r2*pop[i])
                else:
                    r3=chaos.rand((dim,)); r4=chaos.rand((dim,))
                    cand=(rabbit-mean)-r3*(lo+r4*span)
            else:
                r=chaos.rand()
                if r>=.5:
                    cand=rabbit-E*np.abs(J*rabbit-pop[i])
                else:
                    y=rabbit-E*np.abs(J*rabbit-pop[i])
                    y=np.clip(y,lo,hi)
                    z=y+chaos.rand((dim,))*levy(rng,(dim,))*(.05*span)
                    z=np.clip(z,lo,hi)
                    fy=obj(y)
                    if obj.calls>=obj.max_evals:
                        cand=y
                    else:
                        fz=obj(z)
                        cand=y if fy<=fz else z
            new[i]=np.clip(cand,lo,hi)
        nf=np.asarray([obj(x) for x in new],float)
        imp=nf<fit
        pop[imp]=new[imp]; fit[imp]=nf[imp]
        i=int(np.argmin(fit))
        if float(fit[i])<bestf:
            best=pop[i].copy(); bestf=float(fit[i])
    if obj.best_theta is not None and obj.best_loss<bestf:
        best=obj.best_theta.copy(); bestf=float(obj.best_loss)
    return best,bestf

def run_optimizer(method,lane_name,target,data):
    center=encode_baseline(lane_name)
    if method=="VANILLA":
        obj=BudgetObjective(lane_name,data,1)
        loss=obj(center)
        return center,float(loss),obj.calls
    obj=BudgetObjective(lane_name,data,MAX_EVALS)
    patch_meta(LANES[lane_name]["dim"],obj)
    seed=(SEED_BASE.get(method,771100) + 1009*sum(map(ord,lane_name)) + sum(map(ord,target))) % 2147483000
    if method=="CHHHO_PW_PM4":
        theta,fit=chhho_pw_pm4_phase(seed,GENERATIONS,center,obj)
    else:
        fn=PHASES[method]
        dummy=np.zeros((1,1),float)
        theta,fit=fn(dummy,dummy,seed,GENERATIONS,center,Xv=dummy,Yv=dummy,refit=False)
        if theta is None and obj.best_theta is not None:
            theta=obj.best_theta.copy(); fit=obj.best_loss
    if obj.best_theta is not None and obj.best_loss<float(fit):
        theta=obj.best_theta.copy(); fit=obj.best_loss
    return np.clip(np.asarray(theta,float),0,1),float(fit),int(min(obj.calls,MAX_EVALS))

def outer_diag(lane_name,data,theta):
    params=decode(lane_name,theta)
    model=make_model(lane_name,params)
    model.fit(data["Xall"],data["yall"])
    pred=float(np.asarray(model.predict(data["xt"])).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1:
        return {"params":params,"pred_log_return_gold":pred,"forecast":None,"absolute_error":PENALTY,
                "direction_correct":False}
    fc=float(data["anchor_prev"]*math.exp(pred))
    ae=float(abs(fc-data["anchor_actual"]))
    dc=bool(int(np.sign(fc-data["anchor_prev"]))==int(np.sign(data["anchor_actual"]-data["anchor_prev"])))
    return {"params":params,"pred_log_return_gold":pred,"forecast":fc,"absolute_error":ae,"direction_correct":dc}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
        with cn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def run_lane(lane_name):
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in DEV_ANCHORS}
    rows=[]
    vanilla_by_anchor={}
    for target in DEV_ANCHORS:
        data=prepare_anchor(b,cache[target],target,lane_name)
        vtheta,vloss,vcalls=run_optimizer("VANILLA",lane_name,target,data)
        vdiag=outer_diag(lane_name,data,vtheta)
        vanilla_by_anchor[target]=float(vloss)
        rows.append({"lane":lane_name,"method":"VANILLA","anchor":target,
                     "inner_relative_sum_abs_error":float(vloss),
                     "ratio_vs_vanilla":1.0,"objective_calls":vcalls,
                     "outer_diagnostic":vdiag})
        for method in METHODS[1:]:
            theta,loss,calls=run_optimizer(method,lane_name,target,data)
            diag=outer_diag(lane_name,data,theta)
            rows.append({"lane":lane_name,"method":method,"anchor":target,
                         "inner_relative_sum_abs_error":float(loss),
                         "ratio_vs_vanilla":float(loss/max(vloss,1e-12)),
                         "objective_calls":calls,"outer_diagnostic":diag})

    summary=[]
    for method in METHODS:
        rr=[r for r in rows if r["method"]==method]
        ratios=np.asarray([r["ratio_vs_vanilla"] for r in rr],float)
        outer_ae=np.asarray([r["outer_diagnostic"]["absolute_error"] for r in rr],float)
        dirs=np.asarray([r["outer_diagnostic"]["direction_correct"] for r in rr],bool)
        summary.append({
            "method":method,
            "anchors":len(rr),
            "mean_ratio_vs_vanilla":float(np.mean(ratios)),
            "median_ratio_vs_vanilla":float(np.median(ratios)),
            "worst_ratio_vs_vanilla":float(np.max(ratios)),
            "anchors_better_than_vanilla":int(np.sum(ratios<1.0-1e-12)),
            "outer_anchor_sum_abs_error_diagnostic":float(np.sum(outer_ae)),
            "outer_anchor_direction_correct_diagnostic":int(np.sum(dirs)),
        })
    ranking=sorted(summary,key=lambda z:(z["mean_ratio_vs_vanilla"],z["median_ratio_vs_vanilla"],
                                          z["worst_ratio_vs_vanilla"],z["method"]))
    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    payload={
        "scope":"BOOSTING_STAGE6A_METAHEURISTIC_BROAD_SCREEN_V1",
        "lane":lane_name,
        "model_contract":LANES[lane_name],
        "anchors":list(DEV_ANCHORS),
        "methods":METHODS,
        "budget":{"population_reference":POP_SIZE,"hard_objective_calls":MAX_EVALS,
                  "generations_ceiling":GENERATIONS,"repeats_per_anchor":1},
        "inner_validation":{"months":INNER_VAL_MONTHS,"objective":"price_SigmaAE / random_walk_SigmaAE",
                            "anchor_target_in_fitness":False},
        "authority":{"database":"READ_ONLY","random_split":"NONE",
                     "2025_role":"NOT_OPENED_NOT_EVALUATED","2026_role":"NOT_OPENED_NOT_EVALUATED",
                     "chhho":"Piecewise C6 p=0.4, PM4-style chaotic HHO random-control replacement"},
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "rows":rows,"summary":summary,"ranking":ranking,
    }
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    payload["payload_sha256"]=digest
    out=Path(f"gold_monthly_boosting_stage6a_{lane_name.lower()}_result.json")
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"lane":lane_name,"top10":ranking[:10],
                      "vanilla":next(x for x in summary if x["method"]=="VANILLA"),
                      "payload_sha256":digest,
                      "authority_invariants_unchanged":after==b.invariants_before},sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lane",required=True,choices=sorted(LANES))
    args=ap.parse_args()
    run_lane(args.lane)

if __name__=="__main__":
    main()
