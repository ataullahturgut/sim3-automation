"""Second strict exact-family source-migration replay, no invented new algorithms.
Rerun existing PSF price-only M0-M3, FSMR4/FSMR8 and LIT Stage3
price-only selective variants on validated 2020-25 XAU BID feed.
Macro-dependent M4 and PRAMV remain protected and NOT retrained: 2025
point-in-time macro ledger is known incomplete.
"""
from pathlib import Path
import json,time,sys,os
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/'tools'))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as common
import gold_execution_psf_ovn_20261007 as psf
import gold_execution_fsmr_stage4_20261007 as fsmr
import gold_execution_lit_stage3_selective_20261007 as l3
OUTBASE='GOLD_EXECUTION_2020_2025_EXISTING_PSF_FSMR_LIT3_SOURCE_REPLAY_20261008'
MET=AX/(OUTBASE+'_METRICS.csv')
PRED=AX/(OUTBASE+'_PREDICTIONS.csv')
SUM=AX/(OUTBASE+'_SUMMARY.json')
def install_source_target(g,t,kind):
    z=common.merge_truth(g,t)
    if kind=='psf':
        z["y"]=z.y_OVN
        z["ret_target"]=z.ret_OVN
    elif kind=='fsmr':
        z["y"]=z.y_OVN
        z["ret"]=z.ret_OVN
    elif kind=='l3':
        z["y"]=z.y_OVN
        z["ret"]=z.ret_OVN
    else:raise ValueError(kind)
    assert (z.loc[z.y.notna(),"overnight_gate"].eq("COMPLETE_SINGLE_SOURCE")).all()
    return z
def psf_run(q,t):
    no_macro={k:v for k,v in psf.FAMILIES.items() if "MACRO" not in k}
    if sorted(no_macro)!=sorted(["M0_SCALAR","M1_SIGNATURE","M2_FPCA","M3_SIG_FPCA"]):
        raise RuntimeError('ORIGINAL_PSF_MACRO_SPEC_CHANGED_UNEXPECTEDLY')
    psf.FAMILIES=no_macro
    zz=install_source_target(psf.build(q,psf.macro_table()),t,"psf")
    p=psf.predictions(zz)
    return p
def l3_run(q,t):
    zz=install_source_target(l3.build(q,l3.macro_map()),t,"l3")
    p=l3.pair_predictions(zz)
    out=[]
    approved=['PAIR_ALL','PAIR_CONF60','SNR_Q67','SNR_Q67_PAIR_SAME']
    for r in p.itertuples(index=False):
        for policy in approved:
            active,pred=l3.apply_policy(r,policy)
            out.append({"date":r.date,"year":int(r.year),"model_id":"LIT3_"+policy,
              "family":"LIT_STAGE3_SELECTIVE_ONLY_PRICE_KNOWN_BY_ORIGIN",
              "active":bool(active),"pred":int(pred),"y":int(r.y),
              "prob_up":float(r.p_pair) if policy.startswith('PAIR') else np.nan,
              "origin":"17:00","period":r.period})
    return pd.DataFrame(out)
def fsmr_run(q,t):
    zz=install_source_target(fsmr.build(q),t,"fsmr")
    # Same posterior smoothing/state threshold model; 2023 selection separate.
    return fsmr.score_states(zz)
def all_score(*families):
    parts=[];s=[]
    for tag,frame in families:
        if frame.empty:continue
        if tag=='PSF':
            for r in frame.itertuples(index=False):
                s.append({"date":r.date,"year":int(r.year),"model_id":str(r.family),
                    "family":"PSF_PRICE_ONLY","pred":int(r.pred),"y":int(r.y),
                    "prob_up":float(r.p_up),"active":True,"origin":"17:00","period":r.period})
        elif tag=='FSMR':
            for r in frame.itertuples(index=False):
                s.append({"date":r.date,"year":int(r.year),"model_id":str(r.model),
                    "family":"FSMR","pred":int(r.pred),"y":int(r.y),
                    "prob_up":float(r.p_state),"active":True,"origin":"17:00",
                    "period":"PREQUENTIAL_2023_2025"})
        else: s.extend(frame.to_dict('records'))
    full=pd.DataFrame(s)
    full['date']=pd.to_datetime(full.date)
    full=full[full.year.isin([2023,2024,2025])].copy()
    full["venue_scope"]=common.derive_weekend(full)
    full["target"]="OVN"
    full["source_role"]="REFIT_EXACT_PRICE_ONLY_FAMILY" 
    if full.duplicated(["date","model_id"]).any():raise RuntimeError("DUPLICATE_PREDICTIONS_PER_MODEL_DATE")
    # Do not publish actual quote levels; only binary labels, return-free probability and quality state.
    full.to_csv(PRED,index=False)
    rows=[]
    for (fam,model,year,weekend),g in full.groupby(["family","model_id","year","venue_scope"]):
        v=g[g.active.astype(bool)]
        if v.empty:continue
        sc=v.rename(columns={"y":"actual_y"}).copy()
        m=common.score_df(sc,model,year,"pred","prob_up" if sc.prob_up.notna().all() else None,
            "OVN","17:00","REFIT_SOURCE_ALIGNED_PRICE_ONLY_FROZEN_SPEC")
        m["family"]=fam
        m["coverage_in_subgroup"]=len(v)/len(g)
        m["eligible_dates_graded"]=len(g)
        rows.append(m)
    return full,pd.DataFrame(rows)
def main():
    start=time.time()
    q,t=common.source_load()
    print("LOAD_ACCEPTED_SOURCE",len(q),len(t),flush=True)
    pf=psf_run(q,t)
    print("PSF_FROZEN_ARCHITECTURES_RETRAINED",len(pf),pf.family.unique().tolist(),flush=True)
    fs=fsmr_run(q,t)
    print("FSMR_FROZEN_ARCHITECTURES_RETRAINED",len(fs),fs.model.unique().tolist(),flush=True)
    lp=l3_run(q,t)
    print("LIT3_PRICE_ONLY_POLICIES_RECONSTRUCTED",len(lp),flush=True)
    preds,metrics=all_score(("PSF",pf),("FSMR",fs),("LIT3",lp))
    metrics.to_csv(MET,index=False)
    summary={
      "status":"SECOND_LEGACY_FAMILY_SOURCE_REPLAY_COMPLETE",
      "source":common.SOURCE,
      "all_architectures_same_as_2026_10_07":True,
      "source_reconstructed":"Price-only PSF M0-M3; original FSMR4/FSMR8; same LIT3 preorigin price pair with four original selective policies",
      "trained_architecture_names":sorted(preds.model_id.unique().tolist()),
      "trained_architecture_count":len(preds.model_id.unique()),
      "price_bars":len(q),"target_dates":len(t),
      "old_macro_M4":"BLOCKED_2025_MISSING_PIT_MACRO_EVENT_LEDGER",
      "old_PRAMV_V1":"BLOCKED_MACRO_LEDGER_AND_LOCKED_PROSPECTIVE_SPEC; ARCHIVE_SOURCE_TRANSFER_SEPARATELY SCORED",
      "meta_selection":"No new winner selection in this run. All fixed prices/thresholds from 2026-10-07 originals.",
      "2025_status":"RETROSPECTIVE_TRANSPORT_NOT_UNTOUCHED",
      "2020_2022":"TRAINING_WARMUP",
      "2023_2024":"CHRONOLOGICAL_EXPANDING_FIT",
      "2025":"FROZEN_2024_PARAMETERS_FOR_PSF_AND_LIT3; FSMR_IS_ORIGINAL_PREQUENTIAL_STATE_MODEL",
      "origin":"17:00_TR_exact_16:45_17:00_completed_bar; vendor lag not certified",
      "weekend":"FRI_TO_MON_64H separate metric partition",
      "n_newsource_prediction_records":len(preds),
      "n_metric_rows":len(metrics),
      "observed_errors_tuned_on_2025":False,
      "model_predictions_artifact":PRED.name,
      "source_consistency_validated":True,
      "runtime_seconds":int(time.time()-start)}
    SUM.write_text(json.dumps(summary,indent=2)+"\n")
    print("SECOND_REPLAY_SUMMARY",json.dumps(summary,indent=2),flush=True)
    for (year,scope),z in metrics.groupby(["year","venue_scope"]):
        print("SECOND_REPLAY_LEAD",year,scope,
             z.sort_values("balanced_accuracy",ascending=False).head(7)
               [["model","n","balanced_accuracy","down_recall","up_recall","coverage_in_subgroup"]].to_json(orient="records"),flush=True)
if __name__=="__main__":main()
