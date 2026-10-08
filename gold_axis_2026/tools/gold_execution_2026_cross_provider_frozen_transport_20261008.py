"""2026 cross-provider transport (explicitly NOT direct Dukascopy 2026 source).

Train separately on already audited 2020-25 Dukascopy-derived BID or HistData BID,
then score both separately frozen sets on the SAME 2026 Jan-Sep HistData BID
complete-source origins. No raw quotes or dated predictions committed to Git.
This is a transparent domain-shift stress check, not main same-source validation.
"""
from __future__ import annotations
import sys,json,time
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2026_histdata_restricted_holdout_20261008 as hist
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as base
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as vix
import gold_execution_2020_2025_training_start_sensitivity_20261008 as spec
NAME="GOLD_EXECUTION_DUKASCOPY_TO_HISTDATA_2026_PROVIDER_TRANSPORT_20261008"
OUT=AX/(NAME+"_SUMMARY.json")
MET=AX/(NAME+"_METRICS.csv")
PAIR=AX/(NAME+"_PAIRED_PROVIDER.csv")
PRIVATE=AX/(NAME+"_DATED_PRIVATE.csv")

def provider_panel(q,t,from_year,to_year):
    x=base.features(q,t,min_year=from_year,max_year=to_year,
                    gvz_csv=spec.GVZ_FULL,require_full_2023_2025=False)
    return vix.joined(x,require_full_2023_2025=False)

def train_score(train_D,train_H,test):
    result=[]
    frozen_before=pd.Timestamp("2026-01-01")
    for target in ("DAY","OVN"):
        te=test[(test.target==target)&(test.year==2026)].sort_values("date")
        if len(te)<120:raise RuntimeError("2026_SOURCE_TARGET_MATCHED_DAYS_TOO_SPARSE")
        for train_name,panel in (("DUKASCOPY_EV_2020_25",train_D),
                                  ("HISTDATA_BID_2020_25",train_H)):
            for start in spec.HISTORIES:
                tr=panel[(panel.target==target)&(panel.year>=start)&
                         (panel.date<frozen_before)]
                if target=="OVN":tr=tr[tr.next_date<=frozen_before]
                if len(tr)<450 or tr.y.nunique()!=2:
                    raise RuntimeError("TRAINING_HISTORY_INSUFFICIENT_"+target)
                if (tr.year==2026).any():raise RuntimeError("2026_TARGET_IN_TRAINING")
                for method in spec.MODELS:
                    cols=((base.BASE_DAY if target=="DAY" else base.BASE_OVN)
                          if method=="BASE_LOGIT" else spec.COLUMNS[method])
                    if tr[cols].isna().any().any() or te[cols].isna().any().any():
                        raise RuntimeError("MISSING_CONTRACT_FEATURE")
                    fit=spec.method_fit(tr[cols].to_numpy(float),
                                            tr.y.to_numpy(int),method)
                    probs=np.clip(fit.predict_proba(te[cols].to_numpy(float))[:,1],1e-6,1-1e-6)
                    for row,p in zip(te.itertuples(index=False),probs):
                        result.append({"date":row.date.strftime("%Y-%m-%d"),
                          "year":2026,"target":target,"train_provider":train_name,
                          "train_start":start,"model":method,"n_train":len(tr),
                          "y":int(row.y),"pred":int(p>=.5),"p_up":float(p),
                          "score_provider":"HISTDATA_M1_BID_ONLY_2026_JAN_SEP",
                          "not_same_provider_backtest":train_name.startswith("DUKASCOPY")})
    return pd.DataFrame(result)

def metrics(p):
    arr=[]
    for (train_src,target,start,model),g in p.groupby(
            ["train_provider","target","train_start","model"]):
        y=g.y.to_numpy(int);a=g.pred.to_numpy(int);prob=g.p_up.to_numpy(float)
        tn=int(((y==0)&(a==0)).sum())
        fp=int(((y==0)&(a==1)).sum())
        fn=int(((y==1)&(a==0)).sum())
        tp=int(((y==1)&(a==1)).sum())
        d=tn/(tn+fp);u=tp/(fn+tp)
        arr.append({"train_provider":train_src,"score_provider":"HISTDATA_BID",
          "target":target,"train_start":start,"model":model,
          "year":2026,"n":len(g),"balanced_accuracy":.5*(d+u),
          "accuracy":float(np.mean(y==a)),"down_recall":d,"up_recall":u,
          "brier":float(np.mean((prob-y)**2)),"tn":tn,"fp":fp,"fn":fn,"tp":tp})
    return pd.DataFrame(arr)
def paired(p):
    rows=[]
    for (target,start,model),z in p.groupby(["target","train_start","model"]):
        ref=z[z.train_provider=="HISTDATA_BID_2020_25"].set_index("date").sort_index()
        alt=z[z.train_provider=="DUKASCOPY_EV_2020_25"].set_index("date").sort_index()
        if len(ref)!=len(alt) or not ref.index.equals(alt.index) or not (ref.y==alt.y).all():
            raise RuntimeError("TRAIN_PROVIDER_PAIRED_TARGET_MISMATCH")
        y=ref.y.to_numpy(int);r=ref.pred.to_numpy(int);a=alt.pred.to_numpy(int)
        sav=int(((a==y)&(r!=y)).sum());br=int(((a!=y)&(r==y)).sum())
        def BA(pred):
            return .5*(np.mean(pred[y==0]==0)+np.mean(pred[y==1]==1))
        rows.append({"target":target,"train_start":start,"model":model,
          "2026_score_source":"HISTDATA_BID_ONLY","n":len(y),
          "dukascopy_train_minus_histdata_train_BA":float(BA(a)-BA(r)),
          "dukascopy_training_rescues":sav,"dukascopy_training_breaks":br,
          "net_correct_gain":sav-br,
          "exact_mcnemar_p":float(binomtest(sav,sav+br,.5).pvalue) if sav+br else 1.,
          "exploratory_2026_already_inspected":True})
    return pd.DataFrame(rows)
def main():
    tic=time.monotonic()
    qd,td=src.source_load()
    if len(qd)!=141890 or len(td)!=1549:raise RuntimeError("2020_25_DUKASCOPY_ARCHIVE_MISMATCH")
    qh,th,quality=hist.load_q_t()
    # Compute each price-origin family inside its OWN provider, never splice
    # XAU quotes in one feature array.
    zd=provider_panel(qd,td,2020,2025)
    zh=provider_panel(qh,th,2020,2026)
    test=zh[zh.year==2026].copy()
    preds=train_score(zd,zh,test)
    m=metrics(preds);p=paired(preds)
    if len(m)!=72 or len(p)!=36:raise RuntimeError("MISSING_EXPECTED_PROVIDER_MODEL_COMPARISONS")
    output={"status":"2026_CROSS_PROVIDER_FROZEN_MODEL_TRANSPORT_EXECUTED",
       "source_train_1":"EV TRADING LABS DUKASCOPY M15 BID 2020-25",
       "source_train_2":"HISTDATA M1-derived BID 2020-25, 2023 GAP PRESERVED",
       "source_test":"HISTDATA ONLY Jan-Sep 2026 audited origin gates",
       "never_spliced_quote_source_during_features":True,
       "2026_labels_used_in_training":False,
       "matched_days_score_year":2026,
       "year2026_score_cases":{target:int(len(test[test.target==target])) for target in ("DAY","OVN")},
       "histdata_2023_source_gap_present":True,
       "models":list(spec.MODELS),"training_starts":list(spec.HISTORIES),
       "methodology":"Source-separated frozen 2020-25 model domain transport to identical HistData 2026 test",
       "same_vendor_2026_dukascopy_backtest_completed":False,
       "2026_already_inspected":"YES: this is retrospective robustness evidence NOT unseen 2026",
       "bank_tradable":False,"elapsed_seconds":int(time.monotonic()-tic)}
    OUT.write_text(json.dumps(output,indent=2)+"\n")
    MET.write_text(m.to_csv(index=False))
    PAIR.write_text(p.to_csv(index=False))
    PRIVATE.write_text(preds.to_csv(index=False))
    print("CROSS_PROVIDER_2026_ACTUAL_MODELS",json.dumps(output),flush=True)
    print(m.to_string(index=False),flush=True)
    print("EXACT_SAME_DATE_PAIRS",p.to_string(index=False),flush=True)
if __name__=="__main__":main()
