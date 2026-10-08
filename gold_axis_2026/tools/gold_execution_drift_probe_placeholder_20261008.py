"""Causal 2026 XAU/USD research experiment."""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def weighted_logit(x,y,ages):
    weights=np.exp(-np.log(2)*ages/252)
    model=Pipeline([("scale",StandardScaler()),("reg",LogisticRegression(C=.3))])
    for cls in (0,1):
        if (y==cls).mean()<.10:raise ValueError("TRAIN_CLASS_RARE")
        weights[y==cls]*=.5/(y==cls).mean()
    weights/=weights.mean()
    model.fit(x,y,reg__sample_weight=weights)
    return model

from pathlib import Path
import sys,json
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as direct
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
import gold_execution_2020_2025_training_start_sensitivity_20261008 as old
GVZ=b.PRICE+["gvz_log","gvz_x_early","gvz_x_late"]
VIX=v.COLS
def build_features():
    q,t=src.source_load()
    z,audit=mirror.load_approved()
    f=z.set_index("bar_start_utc")[["bid_open","bid_close"]]
    f=f.rename(columns={"bid_open":"open","bid_close":"close"})
    targets,_=direct.candidate_targets(t,f)
    both=pd.concat([q,f]).sort_index()
    dates=pd.concat([t,targets],ignore_index=True).sort_values("date")
    x=b.features(both,dates,min_year=2020,max_year=2026,gvz_csv=old.GVZ_FULL)
    return v.joined(x)

from sklearn.ensemble import HistGradientBoostingClassifier
from scipy.stats import binomtest, ks_2samp
METHODS=("EW_GVZ","EW_VIX","ROLL504_GVZ","EQUAL_GVZ_VIX","FROZEN_HGB")
def hgb(tr):
    m=HistGradientBoostingClassifier(max_iter=90,learning_rate=.04,max_leaf_nodes=7,
       min_samples_leaf=35,max_depth=3,l2_regularization=10.,random_state=1808)
    return m.fit(tr[GVZ].to_numpy(float),tr.y.to_numpy(int))
def fit_month(tr,month):
    y=tr.y.to_numpy(int)
    age=(month-tr.date).dt.days.to_numpy(float)
    rolled=tr[tr.date>=month-pd.Timedelta(days=504)]
    if len(rolled)<150 or rolled.y.nunique()!=2:raise ValueError("ROLL_WINDOW_TOO_THIN")
    return {
      "EW_GVZ":(weighted_logit(tr[GVZ].to_numpy(float),y,age),GVZ),
      "EW_VIX":(weighted_logit(tr[VIX].to_numpy(float),y,age),VIX),
      "ROLL504_GVZ":(weighted_logit(rolled[GVZ].to_numpy(float),
            rolled.y.to_numpy(int),np.zeros(len(rolled))),GVZ)}

def evaluate(z):
    rows=[]
    for target in ("DAY","OVN"):
      k=z[z.target==target].sort_values("date")
      old_cache={}
      for period,now in k[k.year>=2023].groupby(k.date.dt.to_period("M")):
        dt=period.to_timestamp()
        tr=k[k.date<dt]
        if target=="OVN":tr=tr[tr.next_date<=dt]
        if len(tr)<260:continue
        specialized=fit_month(tr,dt)
        frozen_at=pd.Timestamp("2025-01-01" if period.year==2025 else "2026-01-01")
        if period.year<=2024:baseline=tr[tr.year>=2021]
        else:
            baseline=k[(k.year>=2021)&(k.date<frozen_at)]
            if target=="OVN":baseline=baseline[baseline.next_date<=frozen_at]
        key=(target,period.year, str(dt) if period.year<=2024 else "frozen")
        if key not in old_cache:old_cache[key]=hgb(baseline)
        p={}
        for name,(model,cols) in specialized.items():
            p[name]=model.predict_proba(now[cols].to_numpy(float))[:,1]
        p["EQUAL_GVZ_VIX"]=(p["EW_GVZ"]+p["EW_VIX"])/2
        p["FROZEN_HGB"]=old_cache[key].predict_proba(now[GVZ].to_numpy(float))[:,1]
        for name,prob in p.items():
            for i,r in enumerate(now.itertuples(index=False)):
                rows.append({"target":target,"date":r.date.strftime("%Y-%m-%d"),
                "year":int(r.year),"month":str(period),"method":name,"y":int(r.y),
                "p":float(prob[i]),"pred":int(prob[i]>=.5)})
    out=pd.DataFrame(rows)
    if out.empty or out.duplicated(["target","date","method"]).any():
        raise ValueError("DUPLICATE_OR_EMPTY")
    return out

def summary_metrics(p):
    results=[]
    for (target,year,method),g in p.groupby(["target","year","method"]):
        y=g.y.to_numpy(int);q=g.pred.to_numpy(int)
        d=float(np.mean(q[y==0]==0));u=float(np.mean(q[y==1]==1))
        results.append({"target":target,"year":int(year),"method":method,
            "n":len(g),"BA":.5*(d+u),"DOWN_recall":d,"UP_recall":u,
            "accuracy":float(np.mean(q==y)),"Brier":float(np.mean((g.p-y)**2))})
    return pd.DataFrame(results)
def matched(p):
    out=[]
    for (target,year),g in p.groupby(["target","year"]):
        ref=g[g.method=="FROZEN_HGB"].set_index("date")
        for name in METHODS[:4]:
            a=g[g.method==name].set_index("date")
            if set(a.index)!=set(ref.index):raise ValueError("MATCHED_DATES_NOT_EQUAL")
            a=a.loc[ref.index]
            yy=ref.y.to_numpy(int);q=a.pred.to_numpy(int);r=ref.pred.to_numpy(int)
            save=int(np.sum((q==yy)&(r!=yy)))
            brk=int(np.sum((q!=yy)&(r==yy)))
            out.append({"target":target,"year":int(year),"method":name,
                "n":len(a),"rescues":save,"breaks":brk,"net":save-brk,
                "mcnemar_p":float(binomtest(save,save+brk,.5).pvalue) if save+brk else 1.})
    return pd.DataFrame(out)
def run():
    panel=build_features()
    predictions=evaluate(panel)
    m=summary_metrics(predictions);pairs=matched(predictions)
    name="GOLD_EXECUTION_2026_PREREG_CAUSAL_EW_CLASSBALANCED_20261008"
    m.to_csv(AX/(name+"_YEAR_METRICS.csv"),index=False)
    pairs.to_csv(AX/(name+"_PAIRED.csv"),index=False)
    predictions.to_csv(AX/(name+"_PRIVATE_DATED.csv"),index=False)
    result={"status":"ACTUAL_CAUSAL_MONTHLY_TEST","candidate_models":list(METHODS[:4]),
        "2025_2026":"retrospective, already examined",
        "asof_refit":"beginning of each month, only preceding matured labels",
        "sources":"EVTradingLabs Dukascopy historical 2020-25; gated 2026 Dukascopy-node mirror Jan-Aug20",
        "2026_prior_month_labels_may_legitimately_enter_2026_later_refit":True,
        "not_2026_untouched_holdout":True,
        "not_bank_executable":True}
    (AX/(name+"_SUMMARY.json")).write_text(json.dumps(result,indent=2)+"\n")
    print("ADAPT_RESULTS",m.to_string(index=False),flush=True)
    print("ADAPT_PAIRED",pairs.to_string(index=False),flush=True)
    print("ADAPT_STATUS",json.dumps(result),flush=True)
if __name__=="__main__":run()
