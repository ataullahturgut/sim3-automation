"""2026 origin-safe gold next-session absolute-move and DOWN-tail risk study."""
from __future__ import annotations
import os,sys,json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from scipy.stats import spearmanr
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2020_2025_training_start_sensitivity_20261008 as old
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as direct
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_primary_native_restricted_diagnostic_20261008 as primary
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
NAME="GOLD_EXECUTION_2026_ABSOLUTE_SESSION_RISK_TEST_20261008"
def panel(q,t,q26,t26):
    bars=pd.concat([q,q26]).sort_index()
    labels=pd.concat([t,t26],ignore_index=True).sort_values("date")
    z=b.features(bars,labels,min_year=2020,max_year=2026,gvz_csv=old.GVZ_FULL)
    z=v.joined(z)
    z=z[z.target=="OVN"].copy()
    r=labels[["date","ret_OVN"]].rename(columns={"ret_OVN":"realized_return"})
    z=z.merge(r,on="date",how="left",validate="many_to_one")
    if z.realized_return.isna().any():raise RuntimeError("MISSING_RETURNS")
    z["x_rv"]=np.log(np.maximum(1e-8,z.pre4h_rv))
    z["x_prevday"]=np.log(np.maximum(1e-8,z.prior_day.abs()))
    z["x_gvz"]=z.gvz_log
    z["x_jump"]=z.pre4h_jump_share
    z["x_semidown"]=z.pre4h_down_semivol/np.maximum(1e-8,z.pre4h_rv)
    z["abs_move"]=z.realized_return.abs()
    if not (z.abs_move>=0).all():raise RuntimeError("INVALID_ABS_MOVE")
    return z
FEATURES=["x_rv","x_prevday","x_gvz","x_jump","x_semidown"]

def produce_predictions(z,tag):
    out=[]
    for year in (2023,2024,2025,2026):
        sub=z[z.year==year].sort_values("date")
        cache={}
        for period,now in sub.groupby(sub.date.dt.to_period("M")):
            month=period.to_timestamp()
            freeze=month if year<=2024 else pd.Timestamp(f"{year}-01-01")
            if freeze not in cache:
                tr=z[(z.date<freeze)&(z.next_date<=freeze)].copy()
                if len(tr)<175:raise RuntimeError("RISK_HISTORY_TOO_SHORT")
                m=Pipeline([("scale",StandardScaler()),("ridge",Ridge(alpha=20.))])
                m.fit(tr[FEATURES].to_numpy(float),np.log(tr.abs_move.to_numpy(float)+1e-5))
                risks=np.maximum(0,np.exp(m.predict(tr[FEATURES].to_numpy(float)))-1e-5)
                cache[freeze]=(m,float(np.quantile(risks,.75)),
                     float(np.quantile(tr.abs_move,.75)),
                     float(np.quantile(tr.realized_return,.10)),
                     float(tr.abs_move.median()))

            m,cut,tail,down,naive=cache[freeze]
            pred=np.maximum(0,np.exp(m.predict(now[FEATURES].to_numpy(float)))-1e-5)
            for j,r in enumerate(now.itertuples(index=False)):
                out.append({"source_test":tag,"year":year,"date":r.date.strftime("%Y-%m-%d"),
                    "actual_abs":float(r.abs_move),"ret":float(r.realized_return),
                    "risk_pred":float(pred[j]),"naive":naive,
                    "alarm":bool(pred[j]>=cut),
                    "large_event":bool(r.abs_move>=tail),
                    "down_tail":bool(r.realized_return<=down),
                    "train_freeze":str(freeze)})
    return pd.DataFrame(out)

def score(p):
    rows=[]
    for (source,year),g in p.groupby(["source_test","year"]):
        pred=g.risk_pred.to_numpy(float);actual=g.actual_abs.to_numpy(float)
        baseline=g.naive.to_numpy(float)
        alarm=g.alarm.to_numpy(bool)
        big=g.large_event.to_numpy(bool);down=g.down_tail.to_numpy(bool)
        def capture(ev):
            return float((alarm&ev).sum()/ev.sum()) if ev.sum() else None
        def lift(ev):
            return float((alarm&ev).sum()/alarm.sum()/ev.mean()) if alarm.sum() and ev.mean() else None
        rho,pv=spearmanr(pred,actual)
        mae=float(np.mean(abs(pred-actual)));base=float(np.mean(abs(baseline-actual)))
        rows.append({"source_test":source,"year":int(year),"n":len(g),
            "MAE_ridge_bps":mae*10000,"MAE_naive_bps":base*10000,
            "MAE_improvement":(base-mae)/base,
            "rank_spearman":float(rho),"rank_p_unadjusted":float(pv),
            "risk_alarm_rate":float(alarm.mean()),
            "large_event_rate":float(big.mean()),"large_event_capture":capture(big),
            "large_event_precision_lift":lift(big),"down_tail_rate":float(down.mean()),
            "down_tail_capture":capture(down),"down_tail_precision_lift":lift(down)})
    return pd.DataFrame(rows)

def main():
    q,t=src.source_load()
    mirror_bars,proof=mirror.load_approved()
    qm=mirror_bars.set_index("bar_start_utc")[["bid_open","bid_close"]]
    qm=qm.rename(columns={"bid_open":"open","bid_close":"close"})
    tm,_=direct.candidate_targets(t,qm)
    qhist,thist,qn,tn,qc=primary.load()
    if len(qhist)!=len(q):raise RuntimeError("SOURCE_TRAINING_NOT_SAME")
    sets=(("MIRROR_SAME_UPSTREAM_JAN_AUG20",qm,tm),
          ("DIRECT_PRIMARY_NATIVE_THROUGH_OCT07",qn,tn))
    allpred=[]
    for name,bar,labels in sets:
        z=panel(q,t,bar,labels)
        allpred.append(produce_predictions(z,name))
    p=pd.concat(allpred,ignore_index=True)
    results=score(p)
    base="GOLD_EXECUTION_2026_ABSOLUTE_SESSION_RISK_TEST_20261008"
    results.to_csv(AX/(base+"_METRICS.csv"),index=False)
    p.to_csv(AX/(base+"_PRIVATE_DATED.csv"),index=False)
    state={"status":"ORIGIN_SAFE_ABSOLUTE_MOVE_RISK_ACTUALLY_TESTED",
           "historical_source":"EV Dukascopy BID 2020-25",
           "two_2026_sources":[z[0] for z in sets],
           "ridge_alpha":20,"features":FEATURES,"freeze":"Jan 1 for 2025 and 2026",
           "no_2026_labels_in_model_fit":True,"bank_PnL":False,
           "2026_is_retrospective_not_unseen":True}
    (AX/(base+"_SUMMARY.json")).write_text(json.dumps(state,indent=2)+"\n")
    print("RISK_TEST_ACTUAL_RESULTS",results.to_string(index=False),flush=True)
    print("RISK_TEST_STATE",json.dumps(state),flush=True)
if __name__=="__main__":main()
