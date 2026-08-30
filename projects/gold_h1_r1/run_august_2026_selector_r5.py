#!/usr/bin/env python3
import base64,gzip,io,json,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
OUT=Path('projects/gold_h1_r1')
BRANCH_PIN='7706d68ad5a103381f1dbe717af171b7726f3eb3'
STAK_PIN='ed2e549f82ba0d1cd3ca32842b82d3888d301e01'
PRED_URL=f'https://raw.githubusercontent.com/ataullahturgut/sim3-automation/{BRANCH_PIN}/gold_axis_2026/monthly_predictions_2023_2026.csv'
CORE_URL=f'https://raw.githubusercontent.com/ataullahturgut/sim3-automation/{BRANCH_PIN}/gold_axis_2026/core5_monthly.csv.gz.b64'
METALS=['Gold','Silver','Platinum','Palladium']

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'gold-aug-selector-r5/1.0'})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def load_core():
    raw=gzip.decompress(base64.b64decode(get(CORE_URL).strip())).decode()
    return pd.read_csv(io.StringIO(raw),parse_dates=['date']).set_index('date').sort_index()

def load_wide():
    rows=[]
    for y in range(2010,2027):
        u=f'https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_PIN}/data/spot-history-{y}.json'
        z=json.loads(get(u))
        for r in z:
            if r.get('metal') in METALS:
                d=pd.to_datetime(r['timestamp']).normalize()
                if d<=pd.Timestamp('2026-07-31'): rows.append((d,r['metal'],float(r['spot'])))
    d=pd.DataFrame(rows,columns=['date','metal','spot']).sort_values(['date','metal']).drop_duplicates(['date','metal'],keep='last')
    return d.pivot(index='date',columns='metal',values='spot').sort_index()[METALS].dropna()

def features(core,wide,t):
    p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
    g=core.loc[:p,'gold_monthly'].dropna(); rets=g.pct_change().dropna(); hist=np.log(wide[METALS]).diff().dropna(); end=p+pd.offsets.MonthEnd(1); hp=hist.loc[:end]; pv=hp.loc[hp.index.to_period('M')==p.to_period('M')]
    c63=hp.iloc[-63:].corr() if len(hp)>=63 else hp.corr(); goldcorr=np.nanmean([c63.loc['Gold',m] for m in METALS if m!='Gold'])
    return {'gold_ret1':float(rets.iloc[-1]),'gold_mom3':float(g.iloc[-1]/g.iloc[-4]-1),'gold_mom6':float(g.iloc[-1]/g.iloc[-7]-1),'gold_daily_vol':float(pv['Gold'].std()*np.sqrt(21)),'cross_corr63':float(goldcorr),'cross_dispersion':float(pv.mean().std()),'gpr':float(core.loc[p,'gpr']),'fedfunds':float(core.loc[p,'fedfunds']),'nasdaq_ret1':float(np.log(core.loc[p,'nasdaq']/core.loc[pp,'nasdaq'])),'usdcny_ret1':float(np.log(core.loc[p,'usdcny']/core.loc[pp,'usdcny']))}

pred=pd.read_csv(io.BytesIO(get(PRED_URL)),parse_dates=['month']).sort_values('month').reset_index(drop=True)
core=load_core(); wide=load_wide(); rows=[]
for _,r in pred.iterrows():
    z=r.to_dict(); z.update(features(core,wide,r.month)); rows.append(z)
d=pd.DataFrame(rows)
augf=json.loads((OUT/'AUGUST_2026_FORECAST_R4.json').read_text())
aug={'month':pd.Timestamp('2026-08-01'),'actual':np.nan,'prev_actual':4073.0,'rw':float(augf['rw']),'ma3':float(augf['3m_momentum']),'vw_midas_msvr':float(augf['vw_midas_msvr']),'causal_patch_transformer':float(augf['causal_patch_transformer'])}
aug.update(features(core,wide,pd.Timestamp('2026-08-01')))
base_features=['gold_ret1','gold_mom3','gold_mom6','gold_daily_vol','cross_corr63','cross_dispersion','gpr','fedfunds','nasdaq_ret1','usdcny_ret1']
for z in [d]:
    z['f_rw_ret']=z.rw/z.prev_actual-1; z['f_mom_ret']=z.ma3/z.prev_actual-1; z['f_vw_ret']=z.vw_midas_msvr/z.prev_actual-1; z['f_patch_ret']=z.causal_patch_transformer/z.prev_actual-1; z['forecast_dispersion']=z[['rw','ma3','vw_midas_msvr','causal_patch_transformer']].std(axis=1)/z.prev_actual
aug['f_rw_ret']=aug['rw']/aug['prev_actual']-1; aug['f_mom_ret']=aug['ma3']/aug['prev_actual']-1; aug['f_vw_ret']=aug['vw_midas_msvr']/aug['prev_actual']-1; aug['f_patch_ret']=aug['causal_patch_transformer']/aug['prev_actual']-1; aug['forecast_dispersion']=float(np.std([aug['rw'],aug['ma3'],aug['vw_midas_msvr'],aug['causal_patch_transformer']],ddof=1)/aug['prev_actual'])
for m,ec in [('rw','rw_ape'),('momentum','ma3_ape'),('vw','vw_midas_msvr_ape'),('patch','causal_patch_transformer_ape')]:
    vals=[]
    for j in range(len(d)): vals.append(float(d.iloc[max(0,j-3):j][ec].mean()) if j>0 else float(d[ec].iloc[:1].mean()))
    d[f'past3_{m}_ape']=vals; aug[f'past3_{m}_ape']=float(d.iloc[-3:][ec].mean())
features_cols=base_features+['f_rw_ret','f_mom_ret','f_vw_ret','f_patch_ret','forecast_dispersion']+[f'past3_{m}_ape' for m in ['rw','momentum','vw','patch']]
d['winner']=d[['rw_ape','ma3_ape','vw_midas_msvr_ape','causal_patch_transformer_ape']].idxmin(axis=1).map({'rw_ape':'rw','ma3_ape':'momentum','vw_midas_msvr_ape':'vw','causal_patch_transformer_ape':'patch'})
sx=StandardScaler().fit(d[features_cols]); X=sx.transform(d[features_cols]); xt=sx.transform(pd.DataFrame([aug])[features_cols]); clf=LogisticRegression(C=.1,max_iter=2000,class_weight='balanced',random_state=20260827).fit(X,d.winner); pick=str(clf.predict(xt)[0]); probs={c:float(p) for c,p in zip(clf.classes_,clf.predict_proba(xt)[0])}
exp_mape={'rw':float(d.rw_ape.mean()),'momentum':float(d.ma3_ape.mean()),'vw':float(d.vw_midas_msvr_ape.mean()),'patch':float(d.causal_patch_transformer_ape.mean())}; past_pick=min(exp_mape,key=exp_mape.get)
forecast_map={'rw':aug['rw'],'momentum':aug['ma3'],'vw':aug['vw_midas_msvr'],'patch':aug['causal_patch_transformer']}
out={'forecast_origin':'2026-07-31','target_month':'2026-08','gate_pick':pick,'gate_forecast':forecast_map[pick],'gate_probabilities':probs,'past_mape_pick':past_pick,'past_mape_forecast':forecast_map[past_pick],'expanding_mape_through_2026_07':exp_mape,'forecast_returns_vs_july':{'rw':aug['f_rw_ret'],'momentum':aug['f_mom_ret'],'vw':aug['f_vw_ret'],'patch':aug['f_patch_ret']},'forecast_dispersion':aug['forecast_dispersion'],'notes':'All selector inputs use information available through 2026-07-31. August actual is not used.'}
(OUT/'AUGUST_2026_SELECTOR_R5.json').write_text(json.dumps(out,indent=2)); pd.DataFrame([{'gate_pick':pick,'gate_forecast':forecast_map[pick],'past_mape_pick':past_pick,'past_mape_forecast':forecast_map[past_pick],'forecast_dispersion':aug['forecast_dispersion']}]).to_csv(OUT/'AUGUST_2026_SELECTOR_R5.csv',index=False); print(json.dumps(out,indent=2))
