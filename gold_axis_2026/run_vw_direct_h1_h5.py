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

# Direct h-step forecast contract:
# At origin month o (month-end), use only features available through o.
# Target is month t=o+h. No recursive use of forecasts. Target y=log(P_t/P_o).
# For training/tuning at an origin O, a historical sample is usable only if its TARGET month <= O,
# because only then would its outcome have been known at O.

EXCLUDE={'prev_price','actual','y'}
SEASONAL=['month_sin','month_cos','quarter_sin','quarter_cos']


def direct_frame(one_step_df, h):
    # one_step_df row t uses origin t-1 features. Therefore row o+1 contains origin-o information.
    target_price={}
    # reconstruct target monthly series from one-step rows
    for t,r in one_step_df.iterrows():
        if pd.notna(r.get('actual',np.nan)): target_price[pd.Timestamp(t)]=float(r.actual)
        # prev_price corresponds t-1
        target_price.setdefault(pd.Timestamp(t)-pd.offsets.MonthBegin(1),float(r.prev_price))
    rows=[]
    base_features=[c for c in one_step_df.columns if c not in EXCLUDE]
    for src_t,r in one_step_df.iterrows():
        origin=pd.Timestamp(src_t)-pd.offsets.MonthBegin(1)
        target=origin+pd.offsets.MonthBegin(h)
        if target not in target_price: continue
        z={c:float(r[c]) for c in base_features}
        # target-calendar seasonality is known at origin and must refer to h-step target, not origin+1.
        m=target.month; q=(m-1)//3+1
        z['month_sin']=math.sin(2*math.pi*m/12); z['month_cos']=math.cos(2*math.pi*m/12)
        z['quarter_sin']=math.sin(2*math.pi*q/4); z['quarter_cos']=math.cos(2*math.pi*q/4)
        p0=float(target_price[origin]); pt=float(target_price[target])
        rows.append({'origin':origin,'target':target,'origin_price':p0,'actual':pt,'y':math.log(pt/p0),**z})
    return pd.DataFrame(rows).set_index('target').sort_index()


def direct_live_row(one_step_df,h,target_series):
    origin=pd.Timestamp('2026-07-01'); target=origin+pd.offsets.MonthBegin(h)
    src=origin+pd.offsets.MonthBegin(1)  # Aug row contains Jul-origin features
    if src not in one_step_df.index: raise KeyError(src)
    r=one_step_df.loc[src]
    features=[c for c in one_step_df.columns if c not in EXCLUDE]
    z={c:float(r[c]) for c in features}
    m=target.month; q=(m-1)//3+1
    z['month_sin']=math.sin(2*math.pi*m/12); z['month_cos']=math.cos(2*math.pi*m/12)
    z['quarter_sin']=math.sin(2*math.pi*q/4); z['quarter_cos']=math.cos(2*math.pi*q/4)
    return pd.DataFrame([{'origin':origin,'target':target,'origin_price':float(target_series.loc[origin]),**z}]).set_index('target')


def grid(n,h):
    # compact, deterministic, broad grid + paper Au parameter point
    pts=[(2.1797,10.0,.10)]
    raw=[(C,g,e) for C in [.25,.5,1,2,5,10] for g in [.01,.05,.1,.5,1,2] for e in [.01,.03,.05,.10,.15]]
    rng=np.random.default_rng(SEED+n+100*h)
    ix=rng.choice(len(raw),size=17,replace=False)
    return pts+[raw[i] for i in ix]


def fit_predict(train,test,features,par):
    _,C,g,e=par
    sx=StandardScaler().fit(train[features]); sy=StandardScaler().fit(train[['y']])
    mo=SVR(kernel='rbf',C=C,gamma=g,epsilon=e).fit(sx.transform(train[features]),sy.transform(train[['y']]).ravel())
    rr=float(sy.inverse_transform([[mo.predict(sx.transform(test[features]))[0]]])[0,0])
    return rr


def tune_at_origin(df,origin,features,h):
    # Outcomes known at origin: target <= origin.
    known=df[(df.index<=origin)&df.y.notna()].copy()
    if len(known)<48: raise RuntimeError(f'insufficient known samples h={h} origin={origin}')
    # Last 12 historical target months as validation. Each val prediction is itself origin-safe:
    # training sample target <= validation origin (= val target - h).
    vals=list(known.index[-12:]); scores=[]
    for C,g,e in grid(len(features),h):
        errs=[]
        for vt in vals:
            vo=pd.Timestamp(vt)-pd.offsets.MonthBegin(h)
            tr=df[(df.index<=vo)&df.y.notna()]
            if len(tr)<36: continue
            te=df.loc[[vt]]
            rr=fit_predict(tr,te,features,(0,C,g,e)); errs.append(abs(rr-float(te.y.iloc[0])))
        if errs: scores.append((float(np.mean(errs)),C,g,e))
    if not scores: raise RuntimeError('no tuning scores')
    return min(scores)


def forecast_at_origin(df,origin,target,features,h,par=None):
    if par is None: par=tune_at_origin(df,origin,features,h)
    tr=df[(df.index<=origin)&df.y.notna()]
    te=df.loc[[target]]
    rr=fit_predict(tr,te,features,par)
    fc=float(te.origin_price.iloc[0]*math.exp(rr))
    return fc,rr,par


def momentum_benchmark(price,origin,h):
    s=price.loc[:origin].dropna(); rets=s.pct_change().dropna()
    mu=float(rets.iloc[-3:].mean())
    return float(s.iloc[-1]*(1+mu)**h)


def historical_replay(df,price,h):
    features=[c for c in df.columns if c not in ['origin','origin_price','actual','y']]
    rows=[]
    # Target window 2023-01 through 2026-07. Each target has its own earlier origin.
    for target in pd.date_range('2023-01-01','2026-07-01',freq='MS'):
        if target not in df.index: continue
        origin=target-pd.offsets.MonthBegin(h)
        if origin < pd.Timestamp('2012-01-01'): continue
        try:
            par=tune_at_origin(df,origin,features,h)
            fc,rr,_=forecast_at_origin(df,origin,target,features,h,par)
        except Exception as e:
            rows.append({'h':h,'origin':origin,'target':target,'status':'ERROR_'+type(e).__name__})
            continue
        act=float(df.loc[target,'actual']); rw=float(df.loc[target,'origin_price']); mom=momentum_benchmark(price,origin,h)
        rows.append({'h':h,'origin':origin,'target':target,'status':'OK','actual':act,'direct_vw':fc,
                     'direct_vw_ape':abs(fc-act)/act*100,'rw':rw,'rw_ape':abs(rw-act)/act*100,
                     'mom3_direct':mom,'mom3_direct_ape':abs(mom-act)/act*100,'pred_return':rr,
                     'cv_mae_return':par[0],'C':par[1],'gamma':par[2],'epsilon':par[3]})
    return pd.DataFrame(rows)


def summarize(allr):
    ok=allr[allr.status=='OK'].copy()
    s=ok.groupby('h').agg(N=('direct_vw_ape','size'),VW_MAPE=('direct_vw_ape','mean'),RW_MAPE=('rw_ape','mean'),MOM3_MAPE=('mom3_direct_ape','mean')).reset_index()
    s['VW_vs_RW_improvement_pct']=100*(s.RW_MAPE-s.VW_MAPE)/s.RW_MAPE
    s['VW_vs_MOM3_improvement_pct']=100*(s.MOM3_MAPE-s.VW_MAPE)/s.MOM3_MAPE
    # non-overlapping subset: retain targets spaced at least h months, anchored to first target
    non=[]
    for h,g in ok.groupby('h'):
        g=g.sort_values('target').reset_index(drop=True); keep=[]; last=None
        for _,r in g.iterrows():
            if last is None or ((r.target.year-last.year)*12+r.target.month-last.month)>=h:
                keep.append(r); last=r.target
        q=pd.DataFrame(keep)
        non.append({'h':h,'N_nonoverlap':len(q),'VW_MAPE_nonoverlap':float(q.direct_vw_ape.mean()),
                    'RW_MAPE_nonoverlap':float(q.rw_ape.mean()),'MOM3_MAPE_nonoverlap':float(q.mom3_direct_ape.mean())})
    return s,pd.DataFrame(non)


def live_path(one_step_df,price,horizons=range(1,6)):
    rows=[]
    for h in horizons:
        d=direct_frame(one_step_df,h); features=[c for c in d.columns if c not in ['origin','origin_price','actual','y']]
        origin=pd.Timestamp('2026-07-01'); target=origin+pd.offsets.MonthBegin(h)
        live=direct_live_row(one_step_df,h,price)
        # append target row with unknown y/actual for prediction
        te=live.copy(); te['actual']=np.nan; te['y']=np.nan
        # align cols and inject into a temporary frame
        tmp=d.copy();
        for c in tmp.columns:
            if c not in te.columns: te[c]=np.nan
        te=te[tmp.columns]
        tmp=pd.concat([tmp,te])
        par=tune_at_origin(tmp,origin,features,h)
        tr=tmp[(tmp.index<=origin)&tmp.y.notna()]
        rr=fit_predict(tr,tmp.loc[[target]],features,par)
        fc=float(price.loc[origin]*math.exp(rr)); rw=float(price.loc[origin]); mom=momentum_benchmark(price,origin,h)
        rows.append({'forecast_origin':'2026-07-31','h':h,'target_month':target,'direct_vw':fc,'rw':rw,'mom3_direct':mom,
                     'pred_return':rr,'cv_mae_return':par[0],'C':par[1],'gamma':par[2],'epsilon':par[3]})
    return pd.DataFrame(rows)


def main():
    core=rm.load_core(); wide=rm.fetch_history(); market,_=v2.load_market(); gpr=v2.load_gpr_official()
    # Main specification is the frozen operational preferred audited V2 model.
    base=v2.build(core,wide,market,gpr,'core5_average','publication_lag_safe',False)
    price=core['gold_monthly'].dropna().astype(float)
    frames=[]
    for h in range(1,6):
        print('DIRECT H',h,flush=True)
        d=direct_frame(base,h); frames.append(historical_replay(d,price,h))
    allr=pd.concat(frames,ignore_index=True); allr.to_csv(ROOT/'direct_h1_h5_replay.csv',index=False)
    summ,non=summarize(allr); summ.to_csv(ROOT/'direct_h1_h5_summary.csv',index=False); non.to_csv(ROOT/'direct_h1_h5_nonoverlap.csv',index=False)
    live=live_path(base,price); live.to_csv(ROOT/'direct_aug_dec_2026.csv',index=False)
    meta={'contract':'direct horizon-specific models; no recursive forecast inputs; training outcomes usable only when target month <= forecast origin',
          'spec':'core5_average|publication_lag_safe|verified_only','target':'monthly average gold USD/oz',
          'historical_target_window':'2023-01 through 2026-07','summary':summ.to_dict(orient='records'),
          'nonoverlap':non.to_dict(orient='records'),'live_aug_dec':live.assign(target_month=live.target_month.astype(str)).to_dict(orient='records')}
    (ROOT/'direct_h1_h5_meta.json').write_text(json.dumps(meta,indent=2,default=str))
    print('\nSUMMARY\n',summ.to_string(index=False),flush=True)
    print('\nNONOVERLAP\n',non.to_string(index=False),flush=True)
    print('\nAUG-DEC\n',live.to_string(index=False),flush=True)

if __name__=='__main__': main()
