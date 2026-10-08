"""Chronological directional-expert test on a separate tail-risk population.

Inputs: frozen M4 and PAIR probabilities and vol-only risk score.
No post-origin returns are model inputs. Risk and actual tail cohorts are
separate; actual-tail selection is an EX POST diagnostic, not a policy.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, accuracy_score

AX=Path(__file__).resolve().parents[1]
PSF=AX/"GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
RISK=AX/"GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv"
OUT=AX/"GOLD_EXECUTION_TAIL_DIRECTION_EXPERT_METRICS_2026-10-08.csv"

def sigmoid(v):
    return 1/(1+np.exp(-np.clip(v,-30,30)))

def main():
    p=pd.read_csv(PSF)
    p=p[p.family.eq("M4_SIG_FPCA_MACRO")][["date","year","p_up","ret_target","y"]].rename(columns={"p_up":"m4"})
    b=pd.read_csv(PAIR)
    b=b[b.policy.eq("PAIR_ALL")][["date","p_pair"]].rename(columns={"p_pair":"pair"})
    s=pd.read_csv(RISK)[["date","vol_alert","tail1"]]
    a=p.merge(b,on="date",validate="one_to_one").merge(s,on="date",validate="one_to_one")
    a=a.sort_values("date").reset_index(drop=True)
    assert a.groupby("year").size().to_dict()=={2023:195,2024:259,2025:253}
    original=a.copy()
    a["p_M4"]=a.m4
    a["p_PAIR"]=a.pair
    a["p_EQUAL"]=(a.m4+a.pair)/2
    prob_hedge=[]
    prob_hedge_risk=[]
    for i,row in a.iterrows():
        hist=a.iloc[:i]
        recent=hist.tail(60)
        loss_m4=float(((recent.m4-recent.y)**2).sum())
        loss_pair=float(((recent.pair-recent.y)**2).sum())
        w=float(sigmoid(10*(loss_pair-loss_m4)))
        prob_hedge.append(w*float(row.m4)+(1-w)*float(row.pair))
        statehist=hist[hist.vol_alert.eq(row.vol_alert)].tail(60)
        if len(statehist)<15:
            w2=.5
        else:
            l_m4=float(((statehist.m4-statehist.y)**2).sum())
            l_pair=float(((statehist.pair-statehist.y)**2).sum())
            w2=float(sigmoid(10*(l_pair-l_m4)))
        prob_hedge_risk.append(w2*float(row.m4)+(1-w2)*float(row.pair))
    a["p_HEDGE60"]=prob_hedge
    a["p_RISK_HEDGE60"]=prob_hedge_risk
    rows=[]
    for year in (2023,2024,2025):
        g=a[a.year.eq(year)]
        for context, mask in [("ALL",np.ones(len(g),bool)),("RISK",g.vol_alert.to_numpy(bool)),
                              ("TAIL1_EX_POST",g.tail1.to_numpy(bool))]:
            e=g.loc[mask]
            for method in ("M4","PAIR","EQUAL","HEDGE60","RISK_HEDGE60"):
                probs=e["p_"+method].to_numpy(float)
                actual=e.y.to_numpy(int)
                pred=(probs>=.5).astype(int)
                rows.append(dict(year=year,cohort=context,model=method,n=len(e),
                                 correct=int((actual==pred).sum()),
                                 accuracy=float(accuracy_score(actual,pred)),
                                 BA=float(balanced_accuracy_score(actual,pred)),
                                 brier=float(np.mean((probs-actual)**2)),
                                 up_recall=float(np.mean(pred[actual==1]==1)) if np.any(actual==1) else np.nan,
                                 down_recall=float(np.mean(pred[actual==0]==0)) if np.any(actual==0) else np.nan))
    result=pd.DataFrame(rows)
    result.to_csv(OUT,index=False)
    m4=result[(result.year.eq(2025))&(result.cohort.eq("RISK"))&(result.model.eq("M4"))].iloc[0]
    assert (int(m4.n),int(m4.correct))==(95,53)
    print(result.to_string(index=False))
    print("Saved",OUT)

if __name__=="__main__":
    main()
