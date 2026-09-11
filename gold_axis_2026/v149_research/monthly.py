from __future__ import annotations

import base64
import gzip
import io
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .common import canonical_frame_hash, sha256_file
from .stats import circular_block_superior_set, conditional_predictive_ability, hac_mean_test

ROOT = Path(__file__).resolve().parents[1]
BASE_MODELS = ["VW", "DMA", "DMS", "IDMA", "PATCH", "MOMENTUM", "RW"]
PIT_SAFE_MODELS = ["VW", "PATCH", "MOMENTUM", "RW"]


def load_core5() -> pd.DataFrame:
    raw = gzip.decompress(base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip()))
    frame = pd.read_csv(io.BytesIO(raw), parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    return frame


def _ridge_predict(X, y, x, lam=1e-4):
    X = np.asarray(X, float); y = np.asarray(y, float); x = np.asarray(x, float)
    mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd < 1e-12] = 1.0
    z = (X - mu) / sd; zx = (x - mu) / sd
    design = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(design.shape[1]) * lam; penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return float(np.r_[1.0, zx] @ beta)


def reconstruct_dynamic_diagnostics() -> pd.DataFrame:
    """Diagnostic only: source is explicitly NOT historical PIT and cannot be promoted."""
    d = load_core5().copy()
    for c in ["gold_monthly", "fedfunds", "nasdaq", "usdcny", "gpr"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["gold_ret"] = np.log(d.gold_monthly).diff()
    for c in ["fedfunds", "nasdaq", "usdcny", "gpr"]:
        d[c + "_chg"] = np.log(d[c].clip(lower=1e-9)).diff()
    feats = ["fedfunds_chg", "nasdaq_chg", "usdcny_chg", "gpr_chg"]
    subsets = [list(s) for k in range(1, len(feats)+1) for s in itertools.combinations(feats, k)]
    weights = np.repeat(1 / len(subsets), len(subsets)); idma_weights = weights.copy()
    rows=[]; prior_model_losses=[]
    for i in range(61, len(d)-1):
        train=d.iloc[1:i+1].dropna(subset=["gold_ret"]+feats)
        if len(train)<60: continue
        preds=[]
        for ss in subsets:
            preds.append(_ridge_predict(train[ss], train.gold_ret, d.loc[i,ss]))
        preds=np.asarray(preds)
        if prior_model_losses:
            like=np.exp(-np.clip(prior_model_losses[-1],0,1)*50.0)
            weights=np.maximum(weights**0.99 * like,1e-300); weights/=weights.sum()
            alpha=0.95 if len(prior_model_losses)>=24 and np.mean(np.min(prior_model_losses[-24:],axis=1))<np.mean(np.mean(prior_model_losses[-24:],axis=1)) else 0.99
            idma_weights=np.maximum(idma_weights**alpha * like,1e-300); idma_weights/=idma_weights.sum()
        base=float(d.loc[i,"gold_monthly"])
        target_date=pd.Timestamp(d.loc[i+1,"date"])
        rows.append({"target_month":target_date.strftime("%Y-%m"),"DMA":base*np.exp(float(weights@preds)),"DMS":base*np.exp(float(preds[int(np.argmax(weights))])),"IDMA":base*np.exp(float(idma_weights@preds))})
        realized=float(d.loc[i+1,"gold_ret"])
        prior_model_losses.append((preds-realized)**2)
    return pd.DataFrame(rows)


def build_same_origin_panel() -> tuple[pd.DataFrame, dict]:
    p=pd.read_csv(ROOT/"production_closure/production_history_43.csv",dtype={"month":str})
    p=p.rename(columns={"month":"target_month","actual":"realized_target","rw":"RW","mom":"MOMENTUM","vw":"VW","patch_r1":"PATCH"})
    dyn=reconstruct_dynamic_diagnostics()
    p=p.merge(dyn,on="target_month",how="left",validate="one_to_one")
    p["origin_month"]=(pd.PeriodIndex(p.target_month,freq="M")-1).astype(str)
    records=[]
    source_hash=sha256_file(ROOT/"production_closure/production_history_43.csv")
    core_hash=sha256_file(ROOT/"core5_monthly.csv.gz.b64")
    for row in p.itertuples(index=False):
        for model in BASE_MODELS:
            pit=model in PIT_SAFE_MODELS
            forecast=getattr(row,model)
            records.append({
                "forecast_origin":row.origin_month,"target_month":row.target_month,
                "realized_target":row.realized_target,"model":model,"forecast":forecast,
                "signed_error":forecast-row.realized_target,"absolute_error":abs(forecast-row.realized_target),
                "squared_error":(forecast-row.realized_target)**2,
                "origin_cutoff":row.origin_month+"-MONTH_END",
                "source_vintage_lineage":source_hash if pit else core_hash,
                "evidence_class":"FROZEN_REPLAY" if pit else "RETROSPECTIVE_DIAGNOSTIC_NOT_PIT",
                "pit_status":"PIT_COMPATIBLE_FROZEN_ARTIFACT" if pit else "BLOCKED_PIT",
                "model_version":"CANONICAL_REPLAY" if pit else "V149_DIAGNOSTIC_RECONSTRUCTION_NOT_CANONICAL_IDENTITY",
            })
    out=pd.DataFrame(records).sort_values(["target_month","model"]).reset_index(drop=True)
    coverage={m:{"rows":int((out.model==m).sum()),"pit_rows":int(((out.model==m)&out.pit_status.str.startswith("PIT_")).sum())} for m in BASE_MODELS}
    meta={"rows":len(out),"targets":p.target_month.nunique(),"coverage":coverage,"panel_sha256":canonical_frame_hash(out),"all_seven_common_pit_origins":0,"all_seven_status":"BLOCKED_PIT"}
    return out,meta


def _metrics(frame: pd.DataFrame, col: str) -> dict:
    e=frame[col]-frame.realized_target
    return {"n":len(frame),"mae":float(np.mean(abs(e))),"rmse":float(np.sqrt(np.mean(e**2))),"median_ae":float(np.median(abs(e))),"bias":float(np.mean(e)),"mape":float(np.mean(abs(e/frame.realized_target))*100),"smape":float(np.mean(2*abs(e)/(abs(frame[col])+abs(frame.realized_target)))*100),"worst_ae":float(np.max(abs(e)))}


def monthly_audit(panel: pd.DataFrame, development_end="2024-12") -> dict:
    wide=panel.pivot(index=["forecast_origin","target_month","realized_target"],columns="model",values="forecast").reset_index()
    dev=wide[wide.target_month<=development_end].copy()
    valid=PIT_SAFE_MODELS
    f_corr=dev[valid].corr().round(8).to_dict()
    err=dev[valid].sub(dev.realized_target,axis=0)
    e_corr=err.corr().round(8).to_dict()
    dm={}
    for a,b in itertools.combinations(valid,2):
        dm[f"{a}__{b}"]=hac_mean_test(err[a]**2-err[b]**2,lag=1)
    cpa={}
    for a,b in itertools.combinations(valid,2):
        ld=(err[a]**2-err[b]**2).to_numpy()
        disagreement=abs(dev[a]-dev[b]).shift(1).fillna(0).to_numpy()
        prior_ld=pd.Series(ld).shift(1).fillna(0).to_numpy()
        z=np.column_stack([np.ones(len(dev)),disagreement,prior_ld])
        cpa[f"{a}__{b}"]=conditional_predictive_ability(ld,z,lag=1)
    losses={m:(err[m].to_numpy()**2) for m in valid}
    mcs=circular_block_superior_set(losses,block=3,seed=20260911)
    dispersion=dev[valid].std(axis=1)
    mean_abs=err.abs().mean(axis=1)
    disagreement_relation={"n":len(dev),"corr_dispersion_mean_absolute_error":float(np.corrcoef(dispersion,mean_abs)[0,1])}
    metrics={m:_metrics(dev,m) for m in valid}
    redundancy={}
    for m in valid:
        others=[x for x in valid if x!=m]
        r2=float(np.linalg.lstsq(np.column_stack([np.ones(len(dev)),dev[others]]),dev[m],rcond=None)[1].sum()) if len(dev)>len(others)+1 else float('nan')
        redundancy[m]="PARTIALLY_REDUNDANT" if max(abs(f_corr[m][o]) for o in others)>=0.95 else "NON_REDUNDANT_NOT_PROVEN"
    return {"development_window":[str(dev.target_month.min()),str(dev.target_month.max())],"development_n":len(dev),"models":valid,"excluded_blocked_models":["DMA","DMS","IDMA"],"seven_model_claim":"BLOCKED_PIT","forecast_correlation":f_corr,"error_correlation":e_corr,"dm_squared_loss":dm,"conditional_predictive_ability":cpa,"superior_set":mcs,"disagreement_relation":disagreement_relation,"metrics":metrics,"redundancy":redundancy,"integration_diagnosis":"ONLY_MANDATORY_RW_AND_SIMPLE_EQUAL_4_ELIGIBLE","complex_integration":"NOT_PROVEN"}


def evaluate_monthly_candidates(panel: pd.DataFrame, outer_start="2025-01") -> tuple[pd.DataFrame,dict]:
    wide=panel.pivot(index=["forecast_origin","target_month","realized_target"],columns="model",values="forecast").reset_index()
    out=wide[wide.target_month>=outer_start].copy()
    out["SIMPLE_EQUAL_4"]=out[PIT_SAFE_MODELS].mean(axis=1)
    metrics={m:_metrics(out,m) for m in PIT_SAFE_MODELS+["SIMPLE_EQUAL_4"]}
    rw=metrics["RW"]
    for m in metrics:
        metrics[m]["relative_mae_vs_rw"]=metrics[m]["mae"]/rw["mae"]
        metrics[m]["relative_msfe_vs_rw"]=(metrics[m]["rmse"]**2)/(rw["rmse"]**2)
        prior=out[m].shift(1)-out.realized_target.shift(1)
        current=out[m]-out.realized_target
        metrics[m]["direction_accuracy"]=float(np.mean(np.sign(out[m]-out["RW"])==np.sign(out.realized_target-out["RW"])))
        metrics[m]["first_half_mae"]=float(abs(current.iloc[:len(out)//2]).mean())
        metrics[m]["second_half_mae"]=float(abs(current.iloc[len(out)//2:]).mean())
    losses={m:(out[m]-out.realized_target).to_numpy()**2 for m in metrics}
    dm_vs_rw={m:hac_mean_test(losses[m]-losses["RW"],lag=1) for m in metrics if m!="RW"}
    dm_vs_simple={m:hac_mean_test(losses[m]-losses["SIMPLE_EQUAL_4"],lag=1) for m in metrics if m!="SIMPLE_EQUAL_4"}
    winner=pd.DataFrame({m:abs(out[m]-out.realized_target) for m in metrics}).idxmin(axis=1).value_counts().to_dict()
    disagreement=out[PIT_SAFE_MODELS].std(axis=1)
    mean_ae=pd.DataFrame({m:abs(out[m]-out.realized_target) for m in PIT_SAFE_MODELS}).mean(axis=1)
    best=min(metrics,key=lambda m:(metrics[m]["mae"],m))
    promoted=(best=="SIMPLE_EQUAL_4" and metrics[best]["relative_mae_vs_rw"]<0.95 and metrics[best]["relative_msfe_vs_rw"]<0.95)
    return out[["forecast_origin","target_month","realized_target"]+PIT_SAFE_MODELS+["SIMPLE_EQUAL_4"]],{"outer_window":[str(out.target_month.min()),str(out.target_month.max())],"n":len(out),"metrics":metrics,"best_point_estimate":best,"win_counts":winner,"dm_hac_vs_rw":dm_vs_rw,"dm_hac_vs_simple":dm_vs_simple,"superior_set":circular_block_superior_set(losses,block=3,seed=20260911),"forecast_disagreement_error_correlation":float(np.corrcoef(disagreement,mean_ae)[0,1]),"promotion":"ELIGIBLE" if promoted else "NOT_PROVEN","all_seven_architecture":"BLOCKED_PIT"}
