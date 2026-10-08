"""Origin-safe execution direction ML challenge. New scientific research identity, not a replacement for frozen prior models.
Source: identical audited Dukascopy BID M15 / governed DAY and OVN labels.
2022 history; 2023/24 monthly chronological refits; 2025 frozen-2024 retrospective.
No forecast target prices or raw quotes published. No 2025-directed selection.
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, time
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import confusion_matrix, brier_score_loss, log_loss

AX = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AX / "tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as source
BASE = "GOLD_EXECUTION_ORIGIN_SAFE_SHAPE_GVZ_ML_CHALLENGE_20261008"
SFILE = AX / (BASE + "_SUMMARY.json")
MFILE = AX / (BASE + "_METRICS.csv")
PFILE = AX / (BASE + "_PREDICTIONS_PRIVATE.csv")
GVZ_CSV = AX / "GOLD_GVZCLS_RAW_2021_2025.csv"
ORIGIN = {"DAY": 9, "OVN": 17}
PRICE = ["impulse_early", "impulse_late", "prior_overnight", "prior_day",
         "pre4h_ret", "pre2h_ret", "pre4h_rv", "pre4h_down_semivol",
         "pre4h_up_semivol", "pre4h_efficiency", "pre4h_sign_memory",
         "pre4h_jump_share"]
BASE_DAY = ["impulse_early", "impulse_late", "prior_overnight"]
BASE_OVN = ["impulse_early", "impulse_late"]
MODELS = ["BASE_LOGIT", "SHAPE_LOGIT", "SHAPE_GVZ_LOGIT", "SHAPE_GVZ_HGB"]
MIN_TRAIN = 150

def features(q, t):
    gvz = pd.read_csv(GVZ_CSV, usecols=["date","value"]).copy()
    gvz["date"] = pd.to_datetime(gvz["date"], errors="raise")
    gvz["value"] = pd.to_numeric(gvz["value"], errors="coerce")
    gvz = gvz.dropna().sort_values("date").drop_duplicates("date",keep="last")
    if gvz.empty: raise RuntimeError("NO_GVZ_FILE")
    out = []
    t = t.sort_values("date").reset_index(drop=True)
    for i, r in t.iterrows():
        if not 2022 <= int(r.year) <= 2025: continue
        d = pd.Timestamp(r.date).normalize()
        if i == 0: continue
        prev = t.iloc[i-1]
        prev_day = float(prev.ret_DAY) if np.isfinite(prev.ret_DAY) else np.nan
        prev_ovn = float(prev.ret_OVN) if (pd.Timestamp(prev.next_date)==d and np.isfinite(prev.ret_OVN)) else np.nan
        histgv = gvz[gvz.date < d]
        if histgv.empty: continue
        latest_gvz = histgv.iloc[-1]
        # The previous NY-close GVZ is observable before 09:00 TR only when it is
        # strictly dated before the current Turkish issue date. Never same-day GVZ.
        gv = float(latest_gvz.value)
        if gv <= 0: continue
        for name, hour in ORIGIN.items():
            y = getattr(r, "y_"+name)
            target_ret = getattr(r, "ret_"+name)
            gate = getattr(r, "day_gate" if name == "DAY" else "overnight_gate")
            if not (np.isfinite(y) and np.isfinite(target_ret) and gate=="COMPLETE_SINGLE_SOURCE"):
                continue
            if int(target_ret>0) != int(y):
                raise RuntimeError("FROZEN_PRICE_TARGET_SIGN_MISMATCH")
            if name=="OVN" and d.dayofweek==4:
                # Friday->Monday 64h is a different target, excluded from regular 16h challenge.
                continue
            origin = pd.Timestamp(d.date(), tz="Europe/Istanbul") + pd.Timedelta(hours=hour)
            interval_utc = pd.date_range(origin.tz_convert("UTC")-pd.Timedelta(hours=4),
                                         periods=16, freq="15min")
            bars = q.reindex(interval_utc)
            if len(bars)!=16 or bars[["open","close"]].isna().any().any():
                continue
            if (bars[["open","close"]]<=0).any().any(): continue
            lr = np.log(bars["close"].to_numpy(float)/bars["open"].to_numpy(float))
            if not np.isfinite(lr).all(): continue
            # Exactly completed previous half-hours, before the 09:00 / 17:00 origin.
            early = float(np.log(bars.close.iloc[-3] / bars.open.iloc[-4]))
            late = float(np.log(bars.close.iloc[-1] / bars.open.iloc[-2]))
            rv = float(np.sqrt(np.square(lr).sum()))
            denom = float(np.abs(lr).sum())
            if rv < 1e-12 or denom < 1e-12: continue
            pre4 = float(np.log(bars.close.iloc[-1]/bars.open.iloc[0]))
            pre2 = float(np.log(bars.close.iloc[-1]/bars.open.iloc[-8]))
            vals = {
                "impulse_early":early,
                "impulse_late":late,
                "prior_overnight":prev_ovn,
                "prior_day":prev_day,
                "pre4h_ret":pre4,
                "pre2h_ret":pre2,
                "pre4h_rv":rv,
                "pre4h_down_semivol":float(np.sqrt(np.square(np.minimum(lr,0)).sum())),
                "pre4h_up_semivol":float(np.sqrt(np.square(np.maximum(lr,0)).sum())),
                "pre4h_efficiency":abs(float(lr.sum()))/denom,
                "pre4h_sign_memory":float(np.mean(np.sign(lr[:-1])*np.sign(lr[1:]))),
                "pre4h_jump_share":float(np.max(np.abs(lr)))/denom,
                "gvz_log":float(np.log(gv)),
                "gvz_x_early":float(np.log(gv))*early,
                "gvz_x_late":float(np.log(gv))*late,
                "date":d, "year":int(r.year), "target":name, "y":int(y),
                "next_date":pd.Timestamp(r.next_date),
                "gvz_asof":pd.Timestamp(latest_gvz.date),
            }
            # No invented missing-value imputation: this challenge uses complete
            # matched rows for all candidate families, so comparisons are paired.
            if not np.isfinite(list(vals[k] for k in PRICE)).all():continue
            out.append(vals)
    z = pd.DataFrame(out).sort_values(["target","date"]).reset_index(drop=True)
    if z.empty: raise RuntimeError("NO_FEATURE_ROWS")
    if not (z.gvz_asof < z.date).all():raise RuntimeError("GVZ_PIT_VIOLATION")
    if z.duplicated(["target","date"]).any():raise RuntimeError("DUPLICATE_DAY")
    if (z.year==2025).sum()<350:raise RuntimeError("2025_MATCHED_DATA_INSUFFICIENT")
    if (z.year==2023).sum()<350:raise RuntimeError("2023_MATCHED_DATA_INSUFFICIENT")
    return z

def fit_method(model, hist, test, target, cache, refit_key):
    baseline = BASE_DAY if target=="DAY" else BASE_OVN
    cols = (baseline if model=="BASE_LOGIT" else PRICE if model=="SHAPE_LOGIT"
            else PRICE+["gvz_log","gvz_x_early","gvz_x_late"])
    if hist[cols].isna().any().any() or test[cols].isna().any().any():
        raise RuntimeError("HIDDEN_FEATURE_IMPUTATION")
    key=(target,model,refit_key)
    if key not in cache:
        x=hist[cols].to_numpy(float)
        y=hist.y.to_numpy(int)
        if model=="SHAPE_GVZ_HGB":
            f=HistGradientBoostingClassifier(max_iter=90,learning_rate=.04,max_leaf_nodes=7,
                min_samples_leaf=35,l2_regularization=10.,max_depth=3,random_state=1808)
        else:
            f=make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=1000))
        cache[key]=f.fit(x,y)
    return float(np.clip(cache[key].predict_proba(test[cols].to_numpy(float))[0,1],1e-6,1-1e-6))

def predictions(z):
    all_rows = []
    for target in ("DAY","OVN"):
        k=z[z.target==target].sort_values("date").reset_index(drop=True)
        if (k.year==2022).sum()<120: raise RuntimeError(target+":SHORT_WARMUP")
        frozen = k[(k.date<pd.Timestamp("2025-01-01")) &
                   ((k.next_date<=pd.Timestamp("2025-01-01")) if target=="OVN" else True)].copy()
        if len(frozen)<540:raise RuntimeError(target+":INSUFFICIENT_FROZEN_TRAINING")
        cache={}
        for r in k[k.year.isin([2023,2024,2025])].itertuples(index=False):
            dd=pd.Timestamp(r.date)
            row=k.loc[k.date==dd]
            # One fixed fit per development calendar month: only labels fully matured
            # at the START of that month, and never an outcome from the month itself.
            month_start=pd.Timestamp(year=dd.year,month=dd.month,day=1)
            if r.year==2025:
                train=frozen.copy()
                refit_key="FROZEN_2024"
            else:
                train=(k[(k.date<month_start) & (k.next_date<=month_start)].copy()
                       if target=="OVN" else k[k.date<month_start].copy())
                refit_key=month_start.strftime("%Y-%m")
            if len(train)<MIN_TRAIN or train.y.nunique()!=2:continue
            if not (train.date<dd).all():raise RuntimeError("FUTURE_TRAINING_ROW")
            if target=="OVN" and not (train.next_date<=month_start if r.year<2025
                                      else train.next_date<=pd.Timestamp("2025-01-01")).all():
                raise RuntimeError("OVERNIGHT_UNMATURED_LABEL")
            if r.year==2025 and train.year.max()>2024:
                raise RuntimeError("FROZEN_2025_FIT_LEAKAGE")
            for model in MODELS:
                p=fit_method(model,train,row,target,cache,refit_key)
                all_rows.append({"date":dd.strftime("%Y-%m-%d"),"year":int(r.year),
                    "target":target,"model":model,"n_train":len(train),
                    "y":int(r.y),"p_up":p,"pred":int(p>=.5),
                    "research_scope":"RETROSPECTIVE_2025_FROZEN_2024" if r.year==2025
                        else "MONTHLY_PREQUENTIAL_DEV_2023_2024"})
    return pd.DataFrame(all_rows)

def metrics(p):
    out=[]
    for (target,model,year),g in p.groupby(["target","model","year"]):
        y=g.y.to_numpy(int);pr=g.p_up.to_numpy(float);guess=g.pred.to_numpy(int)
        tn,fp,fn,tp=map(int,confusion_matrix(y,guess,labels=[0,1]).ravel())
        down=tn/(tn+fp) if tn+fp else np.nan
        up=tp/(tp+fn) if tp+fn else np.nan
        out.append({"target":target,"model":model,"year":int(year),"n":len(g),
            "accuracy":float(np.mean(guess==y)),
            "balanced_accuracy":float((up+down)/2),"up_recall":up,"down_recall":down,
            "brier":float(brier_score_loss(y,pr)),
            "logloss":float(log_loss(y,pr,labels=[0,1])),
            "pred_up_rate":float(np.mean(guess)),
            "tn":tn,"fp":fp,"fn":fn,"tp":tp})
    return pd.DataFrame(out)

def main():
    start=time.time()
    q,t=source.source_load()
    z=features(q,t)
    p=predictions(z)
    m=metrics(p)
    # Paired only: every model must score exactly the same dates for each target/year.
    for (target,year),g in p.groupby(["target","year"]):
        dates={name:set(h.date) for name,h in g.groupby("model")}
        assert len(set(map(frozenset,dates.values())))==1,("UNMATCHED",target,year)
    # Preregistered descriptive DEV eligibility. Not a winner search on 2025.
    dev=m[m.year.isin([2023,2024])].copy()
    gate={}
    for (target,model),g in dev.groupby(["target","model"]):
        years=sorted(g.year.tolist())
        gate[target+"_"+model]={"development_years":years,
          "ba_above_chance_both":bool(len(g)==2 and (g.balanced_accuracy>.5).all()),
          "down_recall_ge_0p30_both":bool(len(g)==2 and (g.down_recall>=.30).all())}
    summary={"status":"COMPLETED_ORIGIN_SAFE_SHAPE_GVZ_CHALLENGE",
      "source_id":source.SOURCE,"source_bars":len(q),"target_dates":len(t),
      "matched_rows_by_target_year":{str(k[0])+"_"+str(k[1]):int(v) for k,v in z.groupby(["target","year"]).size().items()},
      "scope":"DAY09to17 and weekday16h OVN17toNext09, no pooled 64h weekend",
      "governance":"2022 warmup, 2023/24 strictly prior matured-label monthly issue refits, 2025 frozen 2024 retrospective; no selection by 2025",
      "feature_gvz":"Observation date strictly previous local origin date, never same day; source-received publication vintage not independently verified",
      "comparison":"all fixed challengers scored on identical source/date populations",
      "candidate_features":PRICE+["gvz_log","gvz_x_early","gvz_x_late"],
      "model_names":MODELS,"2025_is_untouched":False,
      "not_yet_live_tradeable":True,"dev_gates":gate,
      "no_model_automatically_promoted":True,"research_elapsed_seconds":int(time.time()-start)}
    SFILE.write_text(json.dumps(summary,indent=2,default=str)+"\n")
    MFILE.write_text(m.to_csv(index=False))
    PFILE.write_text(p.to_csv(index=False))
    print("SUCCESS_SHAPE_GVZ",json.dumps(summary,default=str),flush=True)
    print(m.to_string(index=False),flush=True)
if __name__=="__main__":main()
