import json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import run_models as rm

warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent
SEED=20260827

# Paper-verified monthly variables. GPY is intentionally NOT mapped: the paper calls it
# 'platinum producer stocks (GPY)' but public Investing search maps GPY to Golden Predator,
# which is not a platinum producer. We will not guess.
YF_MAP={
    'DJI':'^DJI','DXY':'DX-Y.NYB','NDX':'^NDX','US10YT':'^TNX','US500':'^GSPC','VIX':'^VIX',
    'BRK_g':'GOLD','HL_pb':'HL-PB','NEM_g':'NEM','DZZ':'DZZ','GLL':'GLL','GVZ_PROXY':'^GVZ'
}
PRICE_RETURN_KEYS={'DJI','DXY','NDX','US500','BRK_g','HL_pb','NEM_g','DZZ','GLL'}
LEVEL_KEYS={'US10YT','VIX','GVZ_PROXY'}


def fetch_yahoo_monthly():
    import yfinance as yf
    series={}; report=[]
    for key,ticker in YF_MAP.items():
        try:
            d=yf.download(ticker,start='2009-01-01',end='2026-08-02',auto_adjust=True,progress=False,threads=False)
            if d is None or d.empty:
                report.append({'paper_name':key,'mapped_ticker':ticker,'status':'NOT_FOUND','start':None,'end':None,'n_months':0})
                continue
            if isinstance(d.columns,pd.MultiIndex):
                c=d['Close'][ticker] if ticker in d['Close'].columns else d['Close'].iloc[:,0]
            else:
                c=d['Close']
            c=pd.Series(c).dropna(); c.index=pd.to_datetime(c.index).tz_localize(None)
            m=c.groupby(c.index.to_period('M')).last(); m.index=m.index.to_timestamp()
            series[key]=m.astype(float)
            report.append({'paper_name':key,'mapped_ticker':ticker,'status':'OK','start':str(m.index.min().date()),'end':str(m.index.max().date()),'n_months':int(len(m))})
        except Exception as e:
            report.append({'paper_name':key,'mapped_ticker':ticker,'status':'ERROR:'+type(e).__name__,'start':None,'end':None,'n_months':0})
    report += [
      {'paper_name':'GPY','mapped_ticker':'UNRESOLVED','status':'BLOCKED_AMBIGUOUS_IDENTIFIER','start':None,'end':None,'n_months':0},
      {'paper_name':'long_term_trend','mapped_ticker':'UNRESOLVED_DEFINITION','status':'BLOCKED_DEFINITION_NOT_STATED','start':None,'end':None,'n_months':0},
      {'paper_name':'volatility','mapped_ticker':'UNRESOLVED_DEFINITION','status':'BLOCKED_DEFINITION_NOT_STATED','start':None,'end':None,'n_months':0},
      {'paper_name':'g_volatility','mapped_ticker':'^GVZ','status':'PROXY_ONLY_NOT_EXPLICITLY_MAPPED_IN_PAPER','start':None,'end':None,'n_months':0},
    ]
    return series,pd.DataFrame(report)


def monthly_close(wide,metal='Gold'):
    s=wide[metal].dropna(); m=s.groupby(s.index.to_period('M')).last(); m.index=m.index.to_timestamp(); return m.astype(float)


def calendar31_weighted_return(wide,core,p,metal='Gold',reverse=True):
    # Intended implementation follows the paper's text/Fig. 6: recent observations carry
    # larger weights. The printed Eq.6 has the index direction reversed; reverse=False is
    # kept for a literal-formula sensitivity test.
    s=wide[metal].sort_index().astype(float)
    p=pd.Timestamp(p)
    start=p; month_end=p+pd.offsets.MonthEnd(0)
    prev=s.loc[s.index<start]
    if prev.empty: return np.nan
    prev_close=float(prev.iloc[-1])
    cal=pd.date_range(start,month_end,freq='D')
    x=s.reindex(cal).ffill()
    if pd.isna(x.iloc[0]): x.iloc[0]=prev_close
    x=x.ffill()
    # Extend shorter months to D31 using last observed/fill value, matching paper's D1..D31 alignment.
    vals=list(x.values.astype(float))
    while len(vals)<31: vals.append(vals[-1])
    vals=np.asarray(vals[:31],float)
    dr=np.diff(np.log(np.r_[prev_close,vals]))  # 31 daily return slots
    hist=core.loc[:p,'gpr'].dropna()
    lo=float(hist.min()); hi=float(hist.max()); gnorm=.5 if hi<=lo else float((hist.iloc[-1]-lo)/(hi-lo))
    lam=.1*math.exp(-10.0*np.clip(gnorm,0,1))
    if reverse:
        age=np.arange(30,-1,-1,dtype=float)  # D31 age=0 -> highest weight
        w=np.exp(-lam*age)
    else:
        i=np.arange(1,32,dtype=float)        # literal printed Eq.6
        w=np.exp(-lam*i)
    w=w/w.sum()
    return float(w@dr)


def make_target_series(core,wide,target_kind):
    if target_kind=='paper_close': return monthly_close(wide,'Gold')
    if target_kind=='core5_average': return core['gold_monthly'].dropna().astype(float)
    raise ValueError(target_kind)


def build_samples(core,wide,market,target_kind,variant='verified',weight_direction='text_recent'):
    target=make_target_series(core,wide,target_kind)
    mr=np.log(target/target.shift(1))
    rows=[]
    for t in pd.date_range('2011-06-01','2026-08-01',freq='MS'):
        p=t-pd.offsets.MonthBegin(1)
        # for Aug-2026 forecast target does not need to exist, but previous target must.
        if p not in target.index or p not in core.index: continue
        f={}
        # Paper states MR plus lag1,2,3; use four most recent known monthly returns.
        try:
            f['MR_t1']=float(mr.loc[p])
            f['MR_lag1']=float(mr.shift(1).loc[p])
            f['MR_lag2']=float(mr.shift(2).loc[p])
            f['MR_lag3']=float(mr.shift(3).loc[p])
        except Exception: continue
        if not np.isfinite(list(f.values())).all(): continue
        f['MR_abs_lag1']=abs(f['MR_t1'])
        f['weighted_DR']=calendar31_weighted_return(wide,core,p,'Gold',reverse=(weight_direction=='text_recent'))
        # GPR is explicitly in the paper feature vector; lagged one month at forecast origin.
        f['GPR']=float(core.loc[p,'gpr'])
        # seasonal features; target month's calendar is known ex ante
        m=t.month; q=(m-1)//3+1
        f['month_sin']=math.sin(2*math.pi*m/12); f['month_cos']=math.cos(2*math.pi*m/12)
        f['quarter_sin']=math.sin(2*math.pi*q/4); f['quarter_cos']=math.cos(2*math.pi*q/4)
        missing=False
        for key,s in market.items():
            if key=='GVZ_PROXY' and variant=='verified': continue
            if p not in s.index:
                missing=True; break
            if key in PRICE_RETURN_KEYS:
                pp=p-pd.offsets.MonthBegin(1)
                if pp not in s.index or s.loc[p]<=0 or s.loc[pp]<=0: missing=True; break
                f[key+'_lag1']=float(np.log(s.loc[p]/s.loc[pp]))
            elif key in LEVEL_KEYS:
                f[key+'_lag1']=float(s.loc[p])
        if missing: continue
        # Derived trend/realized-volatility definitions are not stated by paper, so only in explicit extension.
        if variant=='causal_extension':
            hist=target.loc[:p]
            if len(hist)<13: continue
            f['trend12_log_slope']=float(np.polyfit(np.arange(12),np.log(hist.iloc[-12:].values),1)[0])
            f['realized_vol_6m']=float(mr.loc[:p].iloc[-6:].std(ddof=1))
            # if available, GVZ proxy is included above
        y=float(np.log(target.loc[t]/target.loc[p])) if t in target.index else np.nan
        rows.append({'month':t,'prev_price':float(target.loc[p]),'actual':float(target.loc[t]) if t in target.index else np.nan,'y':y,**f})
    return pd.DataFrame(rows).set_index('month').sort_index()


def candidate_grid(n_features):
    # Includes the paper's published Au seasonal-on point (C=2.1797,gamma=10,epsilon=.1),
    # but prospective selection is performed only on pre-origin folds.
    out=[(2.1797,10.0,.10)]
    for C in [.25,.5,1.,2.,5.,10.,20.]:
        for gm in [0.01,0.05,0.1,0.5,1.0,2.0]:
            for ep in [.01,.03,.05,.10,.15]: out.append((C,gm,ep))
    # deterministic thinning for speed while covering ranges
    rng=np.random.default_rng(SEED+n_features)
    idx=rng.choice(np.arange(1,len(out)),size=min(59,len(out)-1),replace=False)
    return [out[0]]+[out[i] for i in idx]


def tune_pre_origin(df,origin,features):
    hist=df[(df.index<origin)&df.y.notna()].copy()
    if len(hist)<48: raise RuntimeError('insufficient history')
    # Last 24 months are validation; each validation month is predicted from all earlier observations.
    val_months=list(hist.index[-24:])
    scores=[]
    for C,gamma,eps in candidate_grid(len(features)):
        errs=[]
        for vt in val_months:
            tr=hist[hist.index<vt]
            if len(tr)<36: continue
            sx=StandardScaler().fit(tr[features]); sy=StandardScaler().fit(tr[['y']])
            model=SVR(kernel='rbf',C=C,gamma=gamma,epsilon=eps)
            model.fit(sx.transform(tr[features]),sy.transform(tr[['y']]).ravel())
            pr=float(sy.inverse_transform([[model.predict(sx.transform(hist.loc[[vt],features]))[0]]])[0,0])
            errs.append(abs(pr-float(hist.loc[vt,'y'])))
        if errs: scores.append((float(np.mean(errs)),C,gamma,eps))
    return min(scores)


def predict_one(df,t,features,params):
    tr=df[(df.index<t)&df.y.notna()].copy(); te=df.loc[[t]]
    _,C,gamma,eps=params
    sx=StandardScaler().fit(tr[features]); sy=StandardScaler().fit(tr[['y']])
    model=SVR(kernel='rbf',C=C,gamma=gamma,epsilon=eps)
    model.fit(sx.transform(tr[features]),sy.transform(tr[['y']]).ravel())
    rr=float(sy.inverse_transform([[model.predict(sx.transform(te[features]))[0]]])[0,0])
    return float(te.prev_price.iloc[0]*math.exp(rr)),rr


def replay(df,target_kind,variant,weight_direction):
    features=[c for c in df.columns if c not in ['prev_price','actual','y']]
    rows=[]; sels={}
    for year in [2023,2024,2025,2026]:
        origin=pd.Timestamp(f'{year}-01-01')
        sel=tune_pre_origin(df,origin,features); sels[str(year)]=sel
        end=7 if year==2026 else 12
        for m in range(1,end+1):
            t=pd.Timestamp(year=year,month=m,day=1)
            if t not in df.index or pd.isna(df.loc[t,'actual']): continue
            pred,rr=predict_one(df,t,features,sel)
            act=float(df.loc[t,'actual']); prev=float(df.loc[t,'prev_price'])
            rw=prev
            # standard 3-price moving average benchmark, matching paper naming more closely
            prior=df.loc[:t].iloc[:-1]['prev_price']
            # operational momentum benchmark retained separately for our prior work
            hist_prices=pd.concat([df.loc[:t].iloc[:-1]['prev_price'],pd.Series([prev])])
            rows.append({'target_kind':target_kind,'variant':variant,'weight_direction':weight_direction,'month':t,
                         'actual':act,'forecast':pred,'ape':abs(pred-act)/act*100,'pred_return':rr,
                         'rw':rw,'rw_ape':abs(rw-act)/act*100})
    out=pd.DataFrame(rows)
    # August 2026 prospective forecast from Jul-31 origin, tune using only <=Jul history.
    aug=pd.Timestamp('2026-08-01'); augrow=None
    if aug in df.index:
        sel_aug=tune_pre_origin(df,aug,features); pr,rr=predict_one(df,aug,features,sel_aug)
        augrow={'target_kind':target_kind,'variant':variant,'weight_direction':weight_direction,'forecast_origin':'2026-07-31',
                'target_month':'2026-08','forecast':pr,'pred_return':rr,'prev_price':float(df.loc[aug,'prev_price']),
                'selected_cv_mae_return':sel_aug[0],'C':sel_aug[1],'gamma':sel_aug[2],'epsilon':sel_aug[3]}
    return out,sels,augrow,features


def summarize(res):
    g=res.groupby(['target_kind','variant','weight_direction']).agg(MAPE=('ape','mean'),RW_MAPE=('rw_ape','mean'),N=('ape','size')).reset_index()
    y=res.copy(); y['year']=pd.to_datetime(y.month).dt.year
    yy=y.groupby(['target_kind','variant','weight_direction','year']).agg(MAPE=('ape','mean'),RW_MAPE=('rw_ape','mean'),N=('ape','size')).reset_index()
    return g,yy


def main():
    core=rm.load_core(); wide=rm.fetch_history()
    market,availability=fetch_yahoo_monthly()
    availability.to_csv(ROOT/'full_rebuild_data_availability.csv',index=False)
    ok={k:v for k,v in market.items() if len(v)>=120}
    # Need a common monthly feature set. Features with inadequate history are dropped and recorded, never imputed from invented values.
    results=[]; aug=[]; manifests=[]; selections={}
    specs=[
      ('paper_close','verified','text_recent'),
      ('paper_close','verified','formula_literal'),
      ('paper_close','causal_extension','text_recent'),
      ('core5_average','verified','text_recent'),
      ('core5_average','causal_extension','text_recent'),
    ]
    for target_kind,variant,wd in specs:
        print('BUILD',target_kind,variant,wd,flush=True)
        d=build_samples(core,wide,ok,target_kind,variant,wd)
        # Require complete features across replay; columns that are mostly missing were already excluded at source.
        r,s,a,features=replay(d,target_kind,variant,wd)
        results.append(r); selections[f'{target_kind}|{variant}|{wd}']=s
        if a: aug.append(a)
        for f in features: manifests.append({'target_kind':target_kind,'variant':variant,'weight_direction':wd,'feature':f})
    res=pd.concat(results,ignore_index=True); res.to_csv(ROOT/'full_rebuild_results_2023_2026.csv',index=False)
    pd.DataFrame(aug).to_csv(ROOT/'full_rebuild_august_2026.csv',index=False)
    pd.DataFrame(manifests).to_csv(ROOT/'full_rebuild_feature_manifest.csv',index=False)
    summ,yearly=summarize(res); summ.to_csv(ROOT/'full_rebuild_summary.csv',index=False); yearly.to_csv(ROOT/'full_rebuild_yearly.csv',index=False)
    meta={
      'exact_replication_status':'BLOCKED',
      'blocked_reasons':[
        'Authors processed dataset is not public.',
        'Paper identifier GPY is ambiguous: Investing public GPY resolves to Golden Predator, not a verified platinum producer; excluded.',
        'Exact definitions of long-term trend and generic volatility are not stated in accessible paper text; excluded from verified variant.',
        'g_volatility exact mapping is not explicitly stated; ^GVZ is used only in causal_extension as a labeled proxy.',
        'Paper uses Investing.com monthly/daily closing prices; this rebuild uses public Yahoo market series plus LBMA/StakTrakr metals, so it is a close replication, not exact.',
        'Printed Eq.6 weighting direction conflicts with paper text/Fig.6; both directions are tested.'
      ],
      'paper_published_Au_params_seasonal_on':{'C':2.1797,'gamma':10.0,'epsilon':0.1,'kernel':'rbf'},
      'selection_contract':'For prospective replay, hyperparameters are selected only from pre-origin rolling validation; published full-sample paper parameters are not forced into 2023-2026 replay.',
      'available_market_keys':sorted(ok.keys()),
      'selections':selections,
      'summary':summ.to_dict(orient='records'),
      'yearly':yearly.to_dict(orient='records')
    }
    (ROOT/'full_rebuild_meta.json').write_text(json.dumps(meta,indent=2,default=str))
    print('\nSUMMARY\n',summ.to_string(index=False),flush=True)
    print('\nAUGUST\n',pd.DataFrame(aug).to_string(index=False),flush=True)
    print('\nAVAILABILITY\n',availability.to_string(index=False),flush=True)

if __name__=='__main__': main()
