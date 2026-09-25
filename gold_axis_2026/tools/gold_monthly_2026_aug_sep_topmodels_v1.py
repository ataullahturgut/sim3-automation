from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_shallow_mlp_v1 as vanilla
import vw_midas_ann_meta_batch_2_v1 as ann2
import vw_midas_ann_meta_batch_5_v1 as ann5
import vw_midas_ann_meta_batch_8_v1 as ann8
import vw_midas_ann_stage3_batch31_v1 as ann31
import vw_midas_ann_stage3_batch32_v1 as ann32
import vw_midas_ann_stage3_batch34_v1 as ann34
import vw_midas_elmfis_meta_batch_5_v1 as ef5
import vw_midas_elm_meta_batch_21_25_v1 as elm2125

TARGETS=("2026-08",)

def forward_x(bundle,target,gpr_history):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    z=base.gpr_norm(gpr_history,pp)
    x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FORWARD_FEATURE_MONTH_MISSING {metal} {target} p={p} pp={pp}")
        x.extend((math.log(M[p]/M[pp]),base.weighted_daily_return(bundle,metal,p,z)))
    return np.asarray(x,float)

def forward_samples(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]
    out={}
    for t in base.month_range("2010-03",origin):
        try:
            out[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:
            continue
    x=forward_x(bundle,target,gh)
    out[target]=(x,np.zeros(4,float))
    return out

def pred_component(samples,target,component):
    if component=="VANILLA":
        p,n,it=vanilla.fit_predict(samples,target,((4,),1.0,"tanh"))
        return p,{"train_rows":n,"iterations":it}
    if component=="MPA":
        p,n,val,full,rep,reps=ann2.predict_target(samples,target,"MPA")
        return p,{"train_rows":n,"selected_repeat":rep,"inner_validation_fitness":val,"full_history_refit_fitness":full}
    if component=="SCA":
        p,n,val,full,rep,reps=ann5.predict_target(samples,target,"SCA")
        return p,{"train_rows":n,"selected_repeat":rep,"inner_validation_fitness":val,"full_history_refit_fitness":full}
    if component=="DE_ABC":
        p,n,val,full,rep,reps=ann8.predict_target(samples,target,"DE_ABC")
        return p,{"train_rows":n,"selected_repeat":rep,"inner_validation_fitness":val,"full_history_refit_fitness":full}
    if component=="ADAPTIVE_TLBO":
        p,n,meta=ann31.predict_target(samples,target,"ADAPTIVE_TLBO")
        return p,{"train_rows":n,**meta}
    if component=="TLBO_TUNED_PSO":
        p,n,meta=ann32.predict_target(samples,target,"TLBO")
        return p,{"train_rows":n,**meta}
    if component=="MPA_SCA":
        p,n,meta=ann34.predict_target(samples,target,"MPA_SCA")
        return p,{"train_rows":n,**meta}
    if component=="SMA_ELMFIS":
        p,n,val,full,rep,reps,mins,maxs,maxc=ef5.predict_target(samples,target,"SMA")
        return p,{"train_rows":n,"selected_repeat":rep,"inner_validation_fitness":val,"full_history_refit_fitness":full}
    if component=="AOA_ELM":
        p,n,fit=elm2125.predict(samples,target,"AOA")
        return p,{"train_rows":n,"inner_fitness":fit}
    raise ValueError(component)

def actual_info(bundle,target):
    vals=bundle.daily_month_values["Gold"].get(target)
    return {
        "available": vals is not None and len(vals)>0,
        "observations": 0 if vals is None else int(len(vals)),
        "average": None if vals is None or len(vals)==0 else float(np.mean(vals)),
        "core_gold": None if target not in bundle.core_gold else float(bundle.core_gold[target]),
        "common_daily_last": bundle.source_checks.get("common_daily_last"),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--component",required=True,choices=[
        "VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA",
        "SMA_ELMFIS","AOA_ELM"])
    args=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)

    rows=[]
    for target in TARGETS:
        origin=base.month_shift(target,-1)
        samples=forward_samples(b,target)
        p,meta=pred_component(samples,target,args.component)
        if origin not in b.core_gold:
            raise RuntimeError(f"CORE_GOLD_ORIGIN_MISSING {origin}")
        origin_price=float(b.core_gold[origin])
        forecast=float(origin_price*math.exp(float(p[0])))
        rows.append({
            "component":args.component,
            "target":target,
            "origin":origin,
            "origin_price":origin_price,
            "pred_log_return_gold":float(p[0]),
            "forecast":forecast,
            "actual_info":actual_info(b,target),
            **meta
        })

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "component":args.component,
        "targets":list(TARGETS),
        "forward_feature_contract":"target X built only from origin p and p-1 months; target-month Y not read for forecasting",
        "database_access":"READ_ONLY",
        "rows":rows,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":inv
    }
    p=Path(f"gold_monthly_2026_aug_sep_{args.component.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
