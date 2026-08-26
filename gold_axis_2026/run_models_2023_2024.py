import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import run_models as rm

ROOT=Path(__file__).resolve().parent
YEARS=[2023,2024]


def tune_msvr_for_year(S, year):
    # Freeze model choice before target year. Use the immediately preceding
    # two calendar years as chronological validation; each validation origin
    # is itself trained only on earlier observations.
    v0=pd.Timestamp(f'{year-2}-01-01'); v1=pd.Timestamp(f'{year-1}-12-01')
    val=[t for t,_,_ in S if v0<=t<=v1]
    ranked=[]
    for C in [.1,1.,10.]:
        for ep in [.02,.05]:
            for gm in [.5,1.]:
                errs=[]
                for t in val:
                    tr=[s for s in S if s[0]<t]
                    te=[s for s in S if s[0]==t][0]
                    X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
                    sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
                    m=rm.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
                    pr=sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0]
                    errs.append(abs(pr-te[2][0]))
                ranked.append((float(np.mean(errs)),C,ep,gm))
    return sorted(ranked)


def run_msvr_year(wide,core,year):
    S=rm.msvr_samples(wide,core)
    rank=tune_msvr_for_year(S,year)
    _,C,ep,gm=rank[0]
    out={}
    for t in pd.date_range(f'{year}-01-01',f'{year}-12-01',freq='MS'):
        tr=[s for s in S if s[0]<t]
        te=[s for s in S if s[0]==t][0]
        X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
        sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
        m=rm.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
        rr=float(sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0])
        p=t-pd.offsets.MonthBegin(1)
        out[t]=(float(core.loc[p,'gold_monthly'])*math.exp(rr),rr)
    return out,rank


def tune_patch_for_year(wide,core,year):
    # Architecture choice frozen before target year. Train strictly before
    # the two-year validation window and validate on those prior two years.
    cfg=[(126,7,24),(126,14,32),(252,7,24),(252,14,32),(252,21,32)]
    v0=pd.Timestamp(f'{year-2}-01-01'); v1=pd.Timestamp(f'{year-1}-12-01')
    train_end=v0-pd.offsets.MonthBegin(1)
    rank=[]
    for L,P,D in cfg:
        S=rm.patch_samples(wide,core,L)
        tr=[s for s in S if s[0]<=train_end]
        va=[s for s in S if v0<=s[0]<=v1]
        mo,sc,_=rm.fit_patch(tr,va,P,D,rm.SEED+year+L+P,160)
        pr=np.array([rm.pred_patch(mo,sc,s) for s in va]); yy=np.array([s[3] for s in va])
        rank.append((float(np.mean(np.abs(pr-yy))),L,P,D))
    return sorted(rank)


def run_patch_year(wide,core,year):
    rank=tune_patch_for_year(wide,core,year)
    _,L,P,D=rank[0]
    S=rm.patch_samples(wide,core,L)
    out={}
    for t in pd.date_range(f'{year}-01-01',f'{year}-12-01',freq='MS'):
        trall=[s for s in S if s[0]<t]
        te=[s for s in S if s[0]==t][0]
        cut=max(36,int(len(trall)*.85)); tr=trall[:cut]; va=trall[cut:]
        pp=[]
        for off in [0,101,202]:
            mo,sc,_=rm.fit_patch(tr,va,P,D,rm.SEED+year*10+off+t.month,200)
            pp.append(rm.pred_patch(mo,sc,te))
        rr=float(np.median(pp)); p=t-pd.offsets.MonthBegin(1)
        out[t]=(float(core.loc[p,'gold_monthly'])*math.exp(rr),rr,pp)
    return out,rank


def metric(res,col):
    e=res[col]-res.actual
    return {'MAPE':float(np.mean(np.abs(e)/res.actual)*100),
            'MAE':float(np.mean(np.abs(e))),
            'RMSE':float(np.sqrt(np.mean(e*e)))}


def direction_accuracy(res,col):
    return float(np.mean(np.sign(res[col]-res.prev_actual)==np.sign(res.actual-res.prev_actual))*100)


def run_year(wide,core,year):
    ms,msrank=run_msvr_year(wide,core,year)
    pt,ptrank=run_patch_year(wide,core,year)
    rows=[]
    for t in pd.date_range(f'{year}-01-01',f'{year}-12-01',freq='MS'):
        p=t-pd.offsets.MonthBegin(1)
        act=float(core.loc[t,'gold_monthly']); rw=float(core.loc[p,'gold_monthly'])
        h=core.loc[:p,'gold_monthly'].pct_change().dropna()
        ma3=rw*(1+h.iloc[-3:].mean())
        mp=ms[t][0]; tp=pt[t][0]
        rows.append({'month':t.strftime('%Y-%m'),'actual':act,'prev_actual':rw,
                     'rw':rw,'rw_ape':abs(rw-act)/act*100,
                     'ma3':ma3,'ma3_ape':abs(ma3-act)/act*100,
                     'vw_midas_msvr':mp,'vw_midas_msvr_ape':abs(mp-act)/act*100,
                     'causal_patch_transformer':tp,'causal_patch_transformer_ape':abs(tp-act)/act*100})
    res=pd.DataFrame(rows)
    summary={'year':year,
             'contract':'rolling one-month-ahead; target year excluded from hyperparameter/architecture selection; each month uses only data available through end of prior month',
             'target':'CORE5 gold_monthly monthly average USD/oz',
             'metrics':{c:metric(res,c) for c in ['rw','ma3','vw_midas_msvr','causal_patch_transformer']},
             'direction_accuracy_pct':{c:direction_accuracy(res,c) for c in ['ma3','vw_midas_msvr','causal_patch_transformer']},
             'msvr_best_pre_year':msrank[0],
             'patch_best_pre_year':ptrank[0]}
    res.to_csv(ROOT/f'results_{year}.csv',index=False)
    return summary


def main():
    core=rm.load_core(); wide=rm.fetch_history()
    summaries={}
    for year in YEARS:
        summaries[str(year)]=run_year(wide,core,year)
        print('\nYEAR',year)
        print(pd.read_csv(ROOT/f'results_{year}.csv').to_string(index=False))
        print(json.dumps(summaries[str(year)],indent=2))
    (ROOT/'summary_2023_2024.json').write_text(json.dumps(summaries,indent=2))

if __name__=='__main__':
    main()
