import io,json,math,warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import yfinance as yf
import run_models as rm
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent
SEED=20260827

# Paper-verified market identities. GPY remains excluded: exact identity is unresolved.
BASE_TICKERS={
 'DJI':'^DJI','DXY':'DX-Y.NYB','NDX':'^NDX','US10YT':'^TNX','US500':'^GSPC','VIX':'^VIX',
 'HL_pb':'HL-PB','NEM_g':'NEM','DZZ':'DZZ','GLL':'GLL','GVZ_PROXY':'^GVZ',
 'BARRICK_TSX_PROXY':'ABX.TO'
}
RETURN_KEYS={'DJI','DXY','NDX','US500','HL_pb','NEM_g','DZZ','GLL','BARRICK_TSX_PROXY'}
LEVEL_KEYS={'US10YT','VIX','GVZ_PROXY'}
GPR_URL='https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls'


def yf_monthly(ticker):
    d=yf.download(ticker,start='2009-01-01',end='2026-08-02',auto_adjust=True,progress=False,threads=False)
    if d is None or d.empty: return None
    if isinstance(d.columns,pd.MultiIndex):
        c=d['Close'][ticker] if ticker in d['Close'].columns else d['Close'].iloc[:,0]
    else: c=d['Close']
    c=pd.Series(c).dropna(); c.index=pd.to_datetime(c.index).tz_localize(None)
    m=c.groupby(c.index.to_period('M')).last(); m.index=m.index.to_timestamp(); return m.astype(float)


def load_market():
    out={}; rep=[]
    for k,t in BASE_TICKERS.items():
        try:
            s=yf_monthly(t)
            if s is None: rep.append({'feature':k,'source':t,'status':'NOT_FOUND'}); continue
            out[k]=s; rep.append({'feature':k,'source':t,'status':'OK','start':str(s.index.min().date()),'end':str(s.index.max().date()),'n':len(s)})
        except Exception as e: rep.append({'feature':k,'source':t,'status':'ERROR_'+type(e).__name__})
    # Auditable Barrick identities. Paper identity is Barrick, but exchange/ticker is not explicit in accessible text.
    rep += [
      {'feature':'BRK_g','source':'Barrick identity verified; operational proxy ABX.TO','status':'PROXY_EXCHANGE_NOT_EXPLICIT_IN_PAPER'},
      {'feature':'GPY','source':'UNRESOLVED','status':'BLOCKED_AMBIGUOUS_IDENTIFIER'},
      {'feature':'long_term_trend','source':'UNRESOLVED_DEFINITION','status':'BLOCKED_DEFINITION_NOT_EXPLICIT'},
      {'feature':'volatility','source':'UNRESOLVED_DEFINITION','status':'BLOCKED_DEFINITION_NOT_EXPLICIT'},
      {'feature':'g_volatility','source':'^GVZ','status':'PROXY_ONLY'}]
    return out,pd.DataFrame(rep)


def load_gpr_official():
    r=requests.get(GPR_URL,timeout=60); r.raise_for_status()
    book=pd.read_excel(io.BytesIO(r.content),sheet_name=None,engine='xlrd')
    best=None
    for sh,d in book.items():
        cols={str(c).strip().upper():c for c in d.columns}
        if 'GPR' in cols and 'GPRT' in cols and 'GPRA' in cols:
            # date column can be month or date
            dc=None
            for cand in ['MONTH','DATE']:
                if cand in cols: dc=cols[cand]; break
            if dc is None: dc=d.columns[0]
            q=d[[dc,cols['GPR'],cols['GPRT'],cols['GPRA']]].copy(); q.columns=['date','GPR','GPRT','GPRA']
            q['date']=pd.to_datetime(q.date,errors='coerce'); q=q.dropna(subset=['date'])
            for c in ['GPR','GPRT','GPRA']: q[c]=pd.to_numeric(q[c],errors='coerce')
            q=q.dropna(subset=['GPR']); q['date']=q.date.dt.to_period('M').dt.to_timestamp(); q=q.drop_duplicates('date',keep='last').set_index('date').sort_index()
            if best is None or len(q)>len(best): best=q
    if best is None: raise RuntimeError('GPR/GPRT/GPRA columns not found in official workbook')
    return best


def probe_vintages():
    rows=[]
    for stamp in ['202501','202601','202607']:
        u=f'https://www.matteoiacoviello.com/gpr_files/data_gpr_export_{stamp}.xls'
        try:
            r=requests.get(u,timeout=30)
            rows.append({'vintage':stamp,'url':u,'http_status':r.status_code,'bytes':len(r.content),'accessible':bool(r.ok and len(r.content)>1000)})
        except Exception as e: rows.append({'vintage':stamp,'url':u,'http_status':None,'bytes':0,'accessible':False,'error':type(e).__name__})
    return pd.DataFrame(rows)


def gold_close(wide):
    s=wide['Gold'].dropna(); m=s.groupby(s.index.to_period('M')).last(); m.index=m.index.to_timestamp(); return m.astype(float)


def weighted_daily_gold(wide,p,gpr_value):
    s=wide['Gold'].sort_index().astype(float); p=pd.Timestamp(p); end=p+pd.offsets.MonthEnd(0)
    prev=s.loc[s.index<p]
    if prev.empty: return np.nan
    prev_close=float(prev.iloc[-1]); cal=pd.date_range(p,end,freq='D')
    x=s.reindex(cal).ffill(); x.iloc[0]=prev_close if pd.isna(x.iloc[0]) else x.iloc[0]; x=x.ffill()
    vals=list(x.values.astype(float))
    while len(vals)<31: vals.append(vals[-1])
    vals=np.asarray(vals[:31]); dr=np.diff(np.log(np.r_[prev_close,vals]))
    # normalize using only GPR values up through the value's own month, supplied by caller
    # caller passes an origin-safe scalar and corresponding historical series separately is not required for ranking; use fixed paper scaling relative to 0..max via caller's z.
    gz=float(np.clip(gpr_value,0,1))
    lam=.1*math.exp(-10.0*gz)
    age=np.arange(30,-1,-1,dtype=float); w=np.exp(-lam*age); w/=w.sum()
    return float(w@dr)


def gpr_norm_hist(gpr,month):
    h=gpr.loc[:month,'GPR'].dropna(); lo=float(h.min()); hi=float(h.max())
    return .5 if hi<=lo else float((h.iloc[-1]-lo)/(hi-lo))


def build(core,wide,market,gpr,target_kind,gpr_mode,proxy_ext=False):
    target=gold_close(wide) if target_kind=='paper_close' else core['gold_monthly'].dropna().astype(float)
    mr=np.log(target/target.shift(1)); rows=[]
    for t in pd.date_range('2011-07-01','2026-08-01',freq='MS'):
        p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
        if p not in target.index: continue
        # Paper-calendar mode uses p-month GPR; publication-safe mode uses p-1 month because p-month monthly GPR is released after p ends.
        gm=p if gpr_mode=='paper_calendar' else pp
        if gm not in gpr.index: continue
        vals=mr.loc[:p].dropna()
        if len(vals)<7: continue
        f={
          'MR_lag1':float(vals.iloc[-1]),'MR_lag2':float(vals.iloc[-2]),'MR_lag3':float(vals.iloc[-3]),
          'MR_abs_lag1':abs(float(vals.iloc[-1])),'MR_MA_3':float(vals.iloc[-3:].mean()),'MR_MA_6':float(vals.iloc[-6:].mean()),
          'MR_sign_lag1':float(np.sign(vals.iloc[-1])),
          'GPR_lag1':float(gpr.loc[gm,'GPR']),'GPRT_lag1':float(gpr.loc[gm,'GPRT']),'GPRA_lag1':float(gpr.loc[gm,'GPRA'])
        }
        gz=gpr_norm_hist(gpr,gm); f['weighted_DR']=weighted_daily_gold(wide,p,gz)
        m=t.month; q=(m-1)//3+1
        f.update({'month_sin':math.sin(2*math.pi*m/12),'month_cos':math.cos(2*math.pi*m/12),
                  'quarter_sin':math.sin(2*math.pi*q/4),'quarter_cos':math.cos(2*math.pi*q/4)})
        bad=False
        for k,s in market.items():
            if k=='GVZ_PROXY' and not proxy_ext: continue
            if p not in s.index: bad=True; break
            if k in RETURN_KEYS:
                if pp not in s.index or s.loc[p]<=0 or s.loc[pp]<=0: bad=True; break
                name='BRK_g_lag1' if k=='BARRICK_TSX_PROXY' else k+'_lag1'; f[name]=float(np.log(s.loc[p]/s.loc[pp]))
            elif k in LEVEL_KEYS:
                name='g_volatility_proxy_lag1' if k=='GVZ_PROXY' else k+'_lag1'; f[name]=float(s.loc[p])
        if bad: continue
        if proxy_ext:
            hist=target.loc[:p]
            f['long_term_trend_proxy']=float(np.polyfit(np.arange(12),np.log(hist.iloc[-12:].values),1)[0]) if len(hist)>=12 else np.nan
            f['volatility_proxy']=float(vals.iloc[-6:].std(ddof=1))
        if not np.isfinite(np.array(list(f.values()),dtype=float)).all(): continue
        y=float(np.log(target.loc[t]/target.loc[p])) if t in target.index else np.nan
        rows.append({'month':t,'prev_price':float(target.loc[p]),'actual':float(target.loc[t]) if t in target.index else np.nan,'y':y,**f})
    return pd.DataFrame(rows).set_index('month').sort_index()


def grid(n):
    pts=[(2.1797,10.0,.10)]
    raw=[(C,g,e) for C in [.25,.5,1,2,5,10] for g in [.01,.05,.1,.5,1,2] for e in [.01,.03,.05,.10,.15]]
    rng=np.random.default_rng(SEED+n); ix=rng.choice(len(raw),size=35,replace=False); pts += [raw[i] for i in ix]
    return pts


def tune(df,t,features):
    hist=df[(df.index<t)&df.y.notna()]
    if len(hist)<48: raise RuntimeError('insufficient historical samples')
    val=list(hist.index[-24:]); scores=[]
    for C,g,e in grid(len(features)):
        er=[]
        for vt in val:
            tr=hist[hist.index<vt]
            if len(tr)<36: continue
            sx=StandardScaler().fit(tr[features]); sy=StandardScaler().fit(tr[['y']])
            mo=SVR(kernel='rbf',C=C,gamma=g,epsilon=e).fit(sx.transform(tr[features]),sy.transform(tr[['y']]).ravel())
            rr=float(sy.inverse_transform([[mo.predict(sx.transform(hist.loc[[vt],features]))[0]]])[0,0]); er.append(abs(rr-float(hist.loc[vt,'y'])))
        if er: scores.append((float(np.mean(er)),C,g,e))
    return min(scores)


def pred(df,t,features,par):
    tr=df[(df.index<t)&df.y.notna()]; te=df.loc[[t]]; _,C,g,e=par
    sx=StandardScaler().fit(tr[features]); sy=StandardScaler().fit(tr[['y']])
    mo=SVR(kernel='rbf',C=C,gamma=g,epsilon=e).fit(sx.transform(tr[features]),sy.transform(tr[['y']]).ravel())
    rr=float(sy.inverse_transform([[mo.predict(sx.transform(te[features]))[0]]])[0,0]); return float(te.prev_price.iloc[0]*math.exp(rr)),rr


def replay(df,label):
    features=[c for c in df.columns if c not in ['prev_price','actual','y']]; rows=[]; sels={}
    for year in [2023,2024,2025,2026]:
        par=tune(df,pd.Timestamp(year,1,1),features); sels[str(year)]=par
        for m in range(1,8 if year==2026 else 13):
            t=pd.Timestamp(year,m,1)
            if t not in df.index or pd.isna(df.loc[t,'actual']): continue
            fc,rr=pred(df,t,features,par); a=float(df.loc[t,'actual']); rw=float(df.loc[t,'prev_price'])
            rows.append({'spec':label,'month':t,'actual':a,'forecast':fc,'ape':abs(fc-a)/a*100,'rw':rw,'rw_ape':abs(rw-a)/a*100,'pred_return':rr})
    aug=pd.Timestamp('2026-08-01'); ar=None
    if aug in df.index:
        par=tune(df,aug,features); fc,rr=pred(df,aug,features,par)
        ar={'spec':label,'forecast_origin':'2026-07-31','target_month':'2026-08','forecast':fc,'prev_price':float(df.loc[aug,'prev_price']),'pred_return':rr,'cv_mae_return':par[0],'C':par[1],'gamma':par[2],'epsilon':par[3]}
    return pd.DataFrame(rows),ar,features,sels


def main():
    core=rm.load_core(); wide=rm.fetch_history(); market,mrep=load_market(); gpr=load_gpr_official(); vint=probe_vintages()
    mrep.to_csv(ROOT/'v2_data_availability.csv',index=False); gpr.reset_index().to_csv(ROOT/'v2_gpr_official.csv',index=False); vint.to_csv(ROOT/'v2_vintage_probe.csv',index=False)
    specs=[]; allr=[]; augs=[]; manifests=[]; sels={}
    for target in ['paper_close','core5_average']:
      for gm in ['paper_calendar','publication_lag_safe']:
       for ext in [False,True]:
        label=f'{target}|{gm}|'+('proxy_extension' if ext else 'verified_only')
        print('RUN',label,flush=True)
        d=build(core,wide,market,gpr,target,gm,ext); r,a,ff,ss=replay(d,label); allr.append(r); sels[label]=ss
        if a: augs.append(a)
        manifests.extend([{'spec':label,'feature':x} for x in ff])
    res=pd.concat(allr,ignore_index=True); res.to_csv(ROOT/'v2_results_2023_2026.csv',index=False)
    res['year']=pd.to_datetime(res.month).dt.year
    summ=res.groupby('spec').agg(MAPE=('ape','mean'),RW_MAPE=('rw_ape','mean'),N=('ape','size')).reset_index().sort_values('MAPE'); summ.to_csv(ROOT/'v2_summary.csv',index=False)
    yy=res.groupby(['spec','year']).agg(MAPE=('ape','mean'),RW_MAPE=('rw_ape','mean'),N=('ape','size')).reset_index(); yy.to_csv(ROOT/'v2_yearly.csv',index=False)
    pd.DataFrame(augs).to_csv(ROOT/'v2_august_2026.csv',index=False); pd.DataFrame(manifests).to_csv(ROOT/'v2_feature_manifest.csv',index=False)
    meta={
      'exact_replication':'BLOCKED',
      'operational_preferred_spec':'core5_average|publication_lag_safe|verified_only',
      'publication_timing_note':'Monthly GPR is updated at the beginning of each month; publication_lag_safe therefore uses p-1 GPR/GPRT/GPRA at a p-month-end forecast origin.',
      'vintage_status':'Point-in-time vintage reconstruction is only claimed if vintage_probe reports accessible; model training here uses current official history with publication lag, so revision-safe status is NOT_PROVEN.',
      'barrick_status':'Paper identity Barrick is verified. Exact exchange/ticker in accessible paper text is not; ABX.TO continuous series is used as an explicitly labeled proxy. NYSE ticker changed GOLD to B on 2025-05-09.',
      'blocked':['GPY identity unresolved','long_term_trend exact definition unresolved','volatility exact definition unresolved','g_volatility exact identity unresolved; GVZ only proxy extension','authors processed Investing.com dataset unavailable'],
      'engineered_features_interpreted_from_paper_names':['MR_abs_lag1=abs(MR_lag1)','MR_MA_3=mean(last 3 monthly returns)','MR_MA_6=mean(last 6 monthly returns)','MR_sign_lag1=sign(MR_lag1)'],
      'selections':sels,'summary':summ.to_dict('records'),'yearly':yy.to_dict('records'),'august':augs
    }
    (ROOT/'v2_meta.json').write_text(json.dumps(meta,indent=2,default=str))
    print('\nSUMMARY\n'+summ.to_string(index=False),flush=True); print('\nAUG\n'+pd.DataFrame(augs).to_string(index=False),flush=True); print('\nVINTAGES\n'+vint.to_string(index=False),flush=True)

if __name__=='__main__': main()
