import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import run_models as rm

ROOT=Path(__file__).resolve().parent
T=pd.Timestamp('2026-08-01'); P=pd.Timestamp('2026-07-01'); PP=pd.Timestamp('2026-06-01')


def august_msvr(wide,core):
    S=rm.msvr_samples(wide,core)
    rank=rm.tune_msvr(S)  # frozen 2025 tuning, identical to 2026 replay
    _,C,ep,gm=rank[0]
    tr=[s for s in S if s[0] < T]
    X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
    # Build Aug feature strictly from Jul + Jun information.
    mavg=wide.groupby(wide.index.to_period('M')).mean(); mavg.index=mavg.index.to_timestamp()
    gz=rm.gpr_z(core,P); feat=[]
    for metal in rm.METALS:
        pm=float(np.log(mavg.loc[P,metal]/mavg.loc[PP,metal]))
        mask=wide.index.to_period('M')==P.to_period('M'); v=wide.loc[mask,metal].values
        feat.extend([pm,rm.vw_return(v,gz)])
    feat=np.array(feat,float)
    sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
    m=rm.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
    rr=float(sy.inverse_transform(m.predict(sx.transform(feat[None])))[0,0])
    return float(core.loc[P,'gold_monthly'])*math.exp(rr), rr, rank[0]


def make_patch_feature(wide,core,L):
    r=np.log(wide[rm.METALS]).diff().dropna(); hist=r.loc[:pd.Timestamp('2026-07-31')]
    x=rm.causal_decomp(hist.iloc[-L:].values.astype(np.float32),21).astype(np.float32)
    nas=float(np.log(core.loc[P,'nasdaq']/core.loc[PP,'nasdaq']))
    fx=float(np.log(core.loc[P,'usdcny']/core.loc[PP,'usdcny']))
    ma=np.array([core.loc[P,'fedfunds'],nas,fx,np.log1p(core.loc[P,'gpr']),rm.gpr_z(core,P)],np.float32)
    return (T,x,ma,0.0)


def august_patch(wide,core):
    rank=rm.tune_patch(wide,core)  # same architecture selection as 2026 replay
    _,L,PCH,D=rank[0]
    S=rm.patch_samples(wide,core,L)
    trall=[s for s in S if s[0] < T]
    cut=max(36,int(len(trall)*.85)); tr=trall[:cut]; va=trall[cut:]
    te=make_patch_feature(wide,core,L)
    preds=[]
    for off in [0,101,202]:
        mo,sc,_=rm.fit_patch(tr,va,PCH,D,rm.SEED+off+8,200)
        preds.append(rm.pred_patch(mo,sc,te))
    rr=float(np.median(preds))
    return float(core.loc[pd.Timestamp('2026-07-01'),'gold_monthly'])*math.exp(rr), rr, preds, rank[0]


def main():
    core=rm.load_core(); wide=rm.fetch_history()
    july=float(core.loc[pd.Timestamp('2026-07-01'),'gold_monthly'])
    h=core.loc[:pd.Timestamp('2026-07-01'),'gold_monthly'].pct_change().dropna()
    mom=july*(1+float(h.iloc[-3:].mean()))
    vw,vr,vsel=august_msvr(wide,core)
    pt,pr,seeds,psel=august_patch(wide,core)
    out={
      'forecast_origin':'2026-07-31',
      'target_month':'2026-08',
      'target_definition':'CORE5 monthly average gold USD/oz',
      'rw':july,
      '3m_momentum':mom,
      'vw_midas_msvr':vw,
      'causal_patch_transformer':pt,
      'vw_selected':vsel,
      'patch_selected':psel,
      'patch_seed_returns':seeds,
      'notes':'All August forecasts use only information available through 2026-07-31. No August observation is used.'
    }
    (ROOT/'forecast_august_2026.json').write_text(json.dumps(out,indent=2))
    pd.DataFrame([out]).to_csv(ROOT/'forecast_august_2026.csv',index=False)
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
