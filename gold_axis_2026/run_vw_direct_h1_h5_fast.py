import json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import run_models as rm
import run_vw_full_rebuild_v2 as v2

warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent
SEED=20260827
EXCLUDE={'prev_price','actual','y'}


def direct_frame(one,h):
    prices={}
    for t,r in one.iterrows():
        prices[pd.Timestamp(t)]=float(r.actual) if pd.notna(r.actual) else prices.get(pd.Timestamp(t),np.nan)
        prices[pd.Timestamp(t)-pd.offsets.MonthBegin(1)]=float(r.prev_price)
    feats=[c for c in one.columns if c not in EXCLUDE]
    rows=[]
    for st,r in one.iterrows():
        origin=pd.Timestamp(st)-pd.offsets.MonthBegin(1); target=origin+pd.offsets.MonthBegin(h)
        if target not in prices or not np.isfinite(prices[target]): continue
        z={c:float(r[c]) for c in feats}
        m=target.month;q=(m-1)//3+1
        z.update(month_sin=math.sin(2*math.pi*m/12),month_cos=math.cos(2*math.pi*m/12),quarter_sin=math.sin(2*math.pi*q/4),quarter_cos=math.cos(2*math.pi*q/4))
        p0=float(prices[origin]);pt=float(prices[target])
        rows.append({'origin':origin,'target':target,'origin_price':p0,'actual':pt,'y':math.log(pt/p0),**z})
    return pd.DataFrame(rows).set_index('target').sort_index()


def grid(n,h):
    pts=[(2.1797,10.,.10)]
    raw=[(C,g,e) for C in [.25,.5,1,2,5,10] for g in [.01,.05,.1,.5,1,2] for e in [.01,.03,.05,.10,.15]]
    rng=np.random.default_rng(SEED+n+100*h); ix=rng.choice(len(raw),size=23,replace=False)
    return pts+[raw[i] for i in ix]


def fp(tr,te,features,par):
    _,C,g,e=par; sx=StandardScaler().fit(tr[features]); sy=StandardScaler().fit(tr[['y']])
    mo=SVR(kernel='rbf',C=C,gamma=g,epsilon=e).fit(sx.transform(tr[features]),sy.transform(tr[['y']]).ravel())
    return float(sy.inverse_transform([[mo.predict(sx.transform(te[features]))[0]]])[0,0])


def tune_year(df,year,features,h):
    origin=pd.Timestamp(year,1,1)-pd.offsets.MonthBegin(1)  # Dec-31 prior year represented by Dec month start
    known=df[(df.index<=origin)&df.y.notna()]
    vals=list(known.index[-18:]); scores=[]
    for par0 in grid(len(features),h):
        C,g,e=par0;er=[]
        for vt in vals:
            vo=pd.Timestamp(vt)-pd.offsets.MonthBegin(h)
            tr=df[(df.index<=vo)&df.y.notna()]
            if len(tr)<36:continue
            rr=fp(tr,df.loc[[vt]],features,(0,C,g,e));er.append(abs(rr-float(df.loc[vt,'y'])))
        if er:scores.append((float(np.mean(er)),C,g,e))
    return min(scores)


def mom(price,origin,h):
    s=price.loc[:origin];mu=float(s.pct_change().dropna().iloc[-3:].mean());return float(s.iloc[-1]*(1+mu)**h)


def replay(df,price,h):
    features=[c for c in df.columns if c not in ['origin','origin_price','actual','y']]
    pars={y:tune_year(df,y,features,h) for y in [2023,2024,2025,2026]}
    rows=[]
    for target in pd.date_range('2023-01-01','2026-07-01',freq='MS'):
        if target not in df.index:continue
        origin=target-pd.offsets.MonthBegin(h);par=pars[target.year]
        tr=df[(df.index<=origin)&df.y.notna()];rr=fp(tr,df.loc[[target]],features,par)
        fc=float(df.loc[target,'origin_price']*math.exp(rr));a=float(df.loc[target,'actual']);rw=float(df.loc[target,'origin_price']);mm=mom(price,origin,h)
        rows.append({'h':h,'origin':origin,'target':target,'actual':a,'direct_vw':fc,'direct_vw_ape':abs(fc-a)/a*100,'rw':rw,'rw_ape':abs(rw-a)/a*100,'mom3_direct':mm,'mom3_direct_ape':abs(mm-a)/a*100,'pred_return':rr,'C':par[1],'gamma':par[2],'epsilon':par[3]})
    return pd.DataFrame(rows),pars


def live(base,price,h,par):
    origin=pd.Timestamp('2026-07-01'); target=origin+pd.offsets.MonthBegin(h); src=pd.Timestamp('2026-08-01')
    r=base.loc[src]; features=[c for c in base.columns if c not in EXCLUDE]
    z={c:float(r[c]) for c in features};m=target.month;q=(m-1)//3+1
    z.update(month_sin=math.sin(2*math.pi*m/12),month_cos=math.cos(2*math.pi*m/12),quarter_sin=math.sin(2*math.pi*q/4),quarter_cos=math.cos(2*math.pi*q/4))
    df=direct_frame(base,h);te=pd.DataFrame([{'origin':origin,'origin_price':float(price.loc[origin]),'actual':np.nan,'y':np.nan,**z}],index=[target]);te.index.name='target'
    for c in df.columns:
        if c not in te:te[c]=np.nan
    tr=df[(df.index<=origin)&df.y.notna()];rr=fp(tr,te[df.columns], [c for c in df.columns if c not in ['origin','origin_price','actual','y']],par)
    return {'forecast_origin':'2026-07-31','h':h,'target_month':target,'direct_vw':float(price.loc[origin]*math.exp(rr)),'rw':float(price.loc[origin]),'mom3_direct':mom(price,origin,h),'pred_return':rr,'C':par[1],'gamma':par[2],'epsilon':par[3]}


def main():
    core=rm.load_core();wide=rm.fetch_history();market,_=v2.load_market();gpr=v2.load_gpr_official();base=v2.build(core,wide,market,gpr,'core5_average','publication_lag_safe',False);price=core.gold_monthly.dropna().astype(float)
    allr=[];live_rows=[];sels={}
    for h in range(1,6):
        print('H',h,flush=True);d=direct_frame(base,h);r,p=replay(d,price,h);allr.append(r);sels[str(h)]={str(k):v for k,v in p.items()};live_rows.append(live(base,price,h,p[2026]))
    res=pd.concat(allr);res.to_csv(ROOT/'direct_fast_replay.csv',index=False)
    s=res.groupby('h').agg(N=('direct_vw_ape','size'),VW_MAPE=('direct_vw_ape','mean'),RW_MAPE=('rw_ape','mean'),MOM3_MAPE=('mom3_direct_ape','mean')).reset_index();s['VW_vs_RW_pct']=100*(s.RW_MAPE-s.VW_MAPE)/s.RW_MAPE;s['VW_vs_MOM3_pct']=100*(s.MOM3_MAPE-s.VW_MAPE)/s.MOM3_MAPE;s.to_csv(ROOT/'direct_fast_summary.csv',index=False)
    non=[]
    for h,g in res.groupby('h'):
        q=g.iloc[::h];non.append({'h':h,'N':len(q),'VW_MAPE':q.direct_vw_ape.mean(),'RW_MAPE':q.rw_ape.mean(),'MOM3_MAPE':q.mom3_direct_ape.mean()})
    pd.DataFrame(non).to_csv(ROOT/'direct_fast_nonoverlap.csv',index=False)
    lv=pd.DataFrame(live_rows);lv.to_csv(ROOT/'direct_fast_aug_dec_2026.csv',index=False)
    (ROOT/'direct_fast_meta.json').write_text(json.dumps({'contract':'year-frozen tuning, direct horizon-specific, outcome-known-only training','summary':s.to_dict('records'),'nonoverlap':non,'live':lv.assign(target_month=lv.target_month.astype(str)).to_dict('records'),'selections':sels},indent=2,default=str))
    print('\n',s.to_string(index=False));print('\nLIVE\n',lv.to_string(index=False))
if __name__=='__main__':main()
