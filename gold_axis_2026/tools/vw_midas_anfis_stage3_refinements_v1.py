from __future__ import annotations
import argparse,json,math,os
from pathlib import Path
import numpy as np, psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb
import vw_midas_elmfis_meta_batch_1_v1 as common
import vw_midas_anfis_vanilla_v2 as acore
import vw_midas_anfis_meta_screen_v6 as av6

# ANFIS objective: premise search + truncated-SVD LSE consequents.
common.predict_with_fit=av6.ols_predict
common.training_loss=av6.train_loss
common.validation_loss=av6.val_loss
common.population_fit=av6.pop_fit
common.validation_pick=av6.val_pick

DEV_START,DEV_END=av6.DEV_START,av6.DEV_END
TR_START,TR_END=av6.TR_START,av6.TR_END
ST_START,ST_END=av6.ST_START,av6.ST_END

METHODS=["ADAPTIVE_PSO","ADAPTIVE_TLBO","TLBO_TUNED_PSO","DE_TUNED_PSO","ADAPTIVE_CROW","PSO_TLBO_HYBRID","MPA_SCA","MPA_GA","MPA_CPA"]

def safe_arrays(samples,target):
    keys,Xr,Yr,txr,split=av6.raw_arrays(samples,target)
    xm,xs,ym,ys=av6.scale_fit(Xr[:split],Yr[:split])
    return keys,(Xr-xm)/xs,(Yr-ym)/ys,(txr-xm)/xs,ym,ys,split

def select_theta(X,Y,split,target,method):
    if method in ("ADAPTIVE_PSO","ADAPTIVE_TLBO"):
        import vw_midas_elmfis_stage3_batch31_v1 as m
        return m.adaptive_pso_select(X,Y,target) if method=="ADAPTIVE_PSO" else m.adaptive_tlbo_select(X,Y,target)
    if method in ("TLBO_TUNED_PSO","DE_TUNED_PSO"):
        import vw_midas_elmfis_stage3_batch32_v1 as m
        return m.select_and_refit(X,Y,target,"TLBO" if method.startswith("TLBO") else "DE")
    if method in ("ADAPTIVE_CROW","PSO_TLBO_HYBRID"):
        import vw_midas_elmfis_stage3_batch33_v1 as m
        return m.select_and_refit(X,Y,target,method)
    import vw_midas_elmfis_stage3b_v1 as m
    th,val,full,rep,reps,ss,rs=m.select_refit(X,Y,split,target,method)
    return th,{"selected_repeat":rep,"inner_validation_fitness":val,"full_history_refit_fitness":full,
               "repeat_validation":reps,"selected_repeat_survivor_shares":ss,"refit_survivor_shares":rs}

def predict(samples,target,method):
    keys,X,Y,tx,ym,ys,split=safe_arrays(samples,target)
    th,meta=select_theta(X,Y,split,target,method)
    pred=av6.ols_predict(th,X,Y,tx)[0]*ys+ym
    return pred,len(keys),meta

def evaluate(bundle,cache,method,a,b):
    rows=[]
    for t in base.month_range(a,b):
        p,n,d=predict(cache[t],t,method); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"method":method,"train_rows":n,"refinement_diag":d,
          "pred_log_return_gold":float(p[0]),"forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def run(method):
    dsn=os.environ["NEON_DATABASE_URL"]; b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(b,cache,method,DEV_START,DEV_END); tr=evaluate(b,cache,method,TR_START,TR_END); st=evaluate(b,cache,method,ST_START,ST_END)
    after=inv(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":f"VW_MIDAS_ANFIS_STAGE3_{method}_V1","method":method,
      "training_contract":{"premise_optimizer":method,"consequents":"truncated_SVD_LSE_per_candidate",
        "post_meta_gradient":"NONE","validation":"chronological_last20pct_min12_pre_target",
        "scaling":"fit_inner_train_only","lstsq_rcond":av6.LSTSQ_RCOND},
      "authority":{"database_access":"READ_ONLY","random_split":"NONE","target_month_in_training":False,
        "selection_period":f"{DEV_START}..{DEV_END}","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
      "dev":{"metrics":eb.active_metrics(dev),"yearly":eb.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":eb.active_metrics(tr),"rows":tr},"stress_2026":{"metrics":eb.active_metrics(st),"rows":st}}
    Path(f"anfis_stage3_{method.lower()}_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS"); print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--method",required=True,choices=METHODS); run(ap.parse_args().method)
