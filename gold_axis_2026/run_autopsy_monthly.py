import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import run_models as rm

ROOT=Path(__file__).resolve().parent
PRED=ROOT/'monthly_predictions_2023_2026.csv'
METALS=rm.METALS
RNG=np.random.default_rng(20260827)


def load_predictions():
    d=pd.read_csv(PRED,parse_dates=['month']).sort_values('month').reset_index(drop=True)
    return d


def monthly_market_features(core,wide,t):
    p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
    if p not in core.index or pp not in core.index: return None
    g=core.loc[:p,'gold_monthly'].dropna()
    if len(g)<7: return None
    rets=g.pct_change().dropna()
    hist=np.log(wide[METALS]).diff().dropna()
    end=p+pd.offsets.MonthEnd(1)
    hp=hist.loc[:end]
    pmask=hp.index.to_period('M')==p.to_period('M')
    pv=hp.loc[pmask]
    if len(pv)<5: return None
    c63=hp.iloc[-63:].corr() if len(hp)>=63 else hp.corr()
    goldcorr=np.nanmean([c63.loc['Gold',m] for m in METALS if m!='Gold'])
    cross_disp=float(pv.mean().std())
    return {
      'origin_month':p,
      'gold_ret1':float(rets.iloc[-1]),
      'gold_mom3':float(g.iloc[-1]/g.iloc[-4]-1),
      'gold_mom6':float(g.iloc[-1]/g.iloc[-7]-1),
      'gold_daily_vol':float(pv['Gold'].std()*np.sqrt(21)),
      'cross_corr63':float(goldcorr),
      'cross_dispersion':cross_disp,
      'gpr':float(core.loc[p,'gpr']),
      'fedfunds':float(core.loc[p,'fedfunds']),
      'nasdaq_ret1':float(np.log(core.loc[p,'nasdaq']/core.loc[pp,'nasdaq'])),
      'usdcny_ret1':float(np.log(core.loc[p,'usdcny']/core.loc[pp,'usdcny'])),
    }


def attach_features(pred,core,wide):
    rows=[]
    for _,r in pred.iterrows():
        f=monthly_market_features(core,wide,r.month)
        z=r.to_dict(); z.update(f or {}); rows.append(z)
    return pd.DataFrame(rows)


def target_consistency(core,wide):
    m=wide['Gold'].groupby(wide.index.to_period('M')).mean(); m.index=m.index.to_timestamp()
    ix=sorted(set(m.index)&set(core.index)&set(pd.date_range('2023-01-01','2026-07-01',freq='MS')))
    q=pd.DataFrame({'month':ix,'core5':[core.loc[x,'gold_monthly'] for x in ix],'daily_source_mean':[m.loc[x] for x in ix]})
    q['pct_diff']=100*(q.daily_source_mean-q.core5)/q.core5
    return q, {'mean_abs_pct_diff':float(q.pct_diff.abs().mean()),'max_abs_pct_diff':float(q.pct_diff.abs().max()),'mean_signed_pct_diff':float(q.pct_diff.mean())}


def robust_shift(feat):
    cols=['gold_ret1','gold_mom3','gold_mom6','gold_daily_vol','cross_corr63','cross_dispersion','gpr','fedfunds','nasdaq_ret1','usdcny_ret1']
    # target Jan-2026 uses Dec-2025 origin, so define 2026 forecast regime by target month.
    ref=feat[(feat.month<'2026-01-01')].copy()
    cur=feat[(feat.month>='2026-01-01')].copy()
    out=[]
    for c in cols:
        med=float(ref[c].median()); mad=float((ref[c]-med).abs().median()); scale=1.4826*mad
        if scale<1e-10: scale=float(ref[c].std()+1e-10)
        rz=(cur[c]-med)/scale
        out.append({'feature':c,'reference_median':med,'robust_scale':scale,
                    '2026_mean_abs_robust_z':float(rz.abs().mean()),'2026_max_abs_robust_z':float(rz.abs().max()),
                    'months_abs_z_gt_3':int((rz.abs()>3).sum())})
    return pd.DataFrame(out).sort_values('2026_mean_abs_robust_z',ascending=False)


def error_anatomy(feat):
    models={'rw':'rw_ape','3m_momentum':'ma3_ape','vw':'vw_midas_msvr_ape','patch':'causal_patch_transformer_ape'}
    cols=['gold_ret1','gold_mom3','gold_mom6','gold_daily_vol','cross_corr63','cross_dispersion','gpr','fedfunds','nasdaq_ret1','usdcny_ret1']
    corr=[]
    for m,e in models.items():
        for c in cols:
            corr.append({'model':m,'feature':c,'spearman_error_corr':float(feat[[c,e]].corr(method='spearman').iloc[0,1])})
    corr=pd.DataFrame(corr)
    # quartile diagnostics for VW error
    q=[]
    for c in cols:
        try: b=pd.qcut(feat[c],4,duplicates='drop')
        except Exception: continue
        for lev,g in feat.groupby(b,observed=True):
            q.append({'feature':c,'quartile':str(lev),'n':len(g),'vw_mape':float(g.vw_midas_msvr_ape.mean()),'patch_mape':float(g.causal_patch_transformer_ape.mean()),'momentum_mape':float(g.ma3_ape.mean())})
    return corr,pd.DataFrame(q)


def best_change_point(series,months,min_side=8,nperm=3000):
    y=np.asarray(series,float); n=len(y)
    candidates=range(min_side,n-min_side+1)
    def score(a,k):
        return np.sum((a[:k]-a[:k].mean())**2)+np.sum((a[k:]-a[k:].mean())**2)
    base=np.sum((y-y.mean())**2)
    vals=[(score(y,k),k) for k in candidates]
    s,k=min(vals)
    improvement=base-s
    perm=[]
    for _ in range(nperm):
        a=RNG.permutation(y)
        bs=np.sum((a-a.mean())**2)
        ss=min(score(a,j) for j in candidates)
        perm.append(bs-ss)
    p=(1+sum(v>=improvement for v in perm))/(1+nperm)
    return {'break_before_month':str(pd.Timestamp(months.iloc[k]).date()),'left_n':k,'right_n':n-k,
            'left_mean':float(y[:k].mean()),'right_mean':float(y[k:].mean()),'sse_improvement':float(improvement),'permutation_p':float(p)}


def change_points(pred):
    out={}
    for name,col in [('vw_abs_ape','vw_midas_msvr_ape'),('patch_abs_ape','causal_patch_transformer_ape'),('momentum_abs_ape','ma3_ape')]:
        out[name]=best_change_point(pred[col].values,pred.month)
    # signed VW percent error: positive = underforecast
    signed=100*(pred.actual-pred.vw_midas_msvr)/pred.actual
    out['vw_signed_pct_error']=best_change_point(signed.values,pred.month)
    return out


def vw_samples_variant(wide,core,metals,mode):
    mavg=wide.groupby(wide.index.to_period('M')).mean(); mavg.index=mavg.index.to_timestamp()
    out=[]
    for t in sorted(set(mavg.index)&set(core.index)):
        p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
        if p not in mavg.index or pp not in mavg.index or p not in core.index: continue
        gz=rm.gpr_z(core,p); X=[]; Y=[]; ok=True
        for metal in metals:
            mr=float(np.log(mavg.loc[p,metal]/mavg.loc[pp,metal]))
            v=wide.loc[wide.index.to_period('M')==p.to_period('M'),metal].values
            if len(v)<5: ok=False; break
            lr=np.diff(np.log(v))
            weighted=rm.vw_return(v,gz)
            unweighted=float(np.mean(lr)) if len(lr) else 0.0
            if mode=='full': X.extend([mr,weighted])
            elif mode=='no_gpr': X.extend([mr,unweighted])
            elif mode=='monthly_only': X.append(mr)
            elif mode=='daily_only': X.append(weighted)
            else: raise ValueError(mode)
            Y.append(float(np.log(mavg.loc[t,metal]/mavg.loc[p,metal])))
        if ok: out.append((t,np.array(X,float),np.array(Y,float)))
    return out


def tune_variant(S,year):
    val0=pd.Timestamp(f'{year-2}-01-01'); val1=pd.Timestamp(f'{year-1}-12-01')
    val=[t for t,_,_ in S if val0<=t<=val1]
    ranked=[]
    for C in [.1,1.,10.]:
      for ep in [.02,.05]:
       for gm in [.5,1.]:
        errs=[]
        for t in val:
            tr=[s for s in S if s[0]<t]; te=next(s for s in S if s[0]==t)
            X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
            sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
            m=rm.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
            pr=sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0]
            errs.append(abs(pr-te[2][0]))
        ranked.append((float(np.mean(errs)),C,ep,gm))
    return min(ranked)


def run_variant(wide,core,name,metals,mode):
    S=vw_samples_variant(wide,core,metals,mode); rows=[]; selections={}
    for year in [2023,2024,2025,2026]:
        sel=tune_variant(S,year); selections[str(year)]=sel
        _,C,ep,gm=sel
        end=7 if year==2026 else 12
        for month in range(1,end+1):
            t=pd.Timestamp(year=year,month=month,day=1)
            tr=[s for s in S if s[0]<t]; te=next(s for s in S if s[0]==t)
            X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
            sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
            m=rm.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
            rr=float(sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0])
            p=t-pd.offsets.MonthBegin(1); pred=float(core.loc[p,'gold_monthly'])*math.exp(rr); act=float(core.loc[t,'gold_monthly'])
            rows.append({'variant':name,'month':t,'actual':act,'forecast':pred,'ape':abs(pred-act)/act*100})
    return pd.DataFrame(rows),selections


def ablations(wide,core):
    specs=[
      ('full_all4',METALS,'full'),
      ('gold_silver_full',['Gold','Silver'],'full'),
      ('gold_only_full',['Gold'],'full'),
      ('all4_no_gpr',['Gold','Silver','Platinum','Palladium'],'no_gpr'),
      ('all4_monthly_only',METALS,'monthly_only'),
      ('all4_daily_only',METALS,'daily_only'),
    ]
    frames=[]; sels={}
    for name,metals,mode in specs:
        print('ABLATION',name,flush=True)
        d,s=run_variant(wide,core,name,metals,mode); frames.append(d); sels[name]=s
    allr=pd.concat(frames,ignore_index=True)
    summ=allr.groupby('variant').agg(MAPE=('ape','mean'),MAE_price=('forecast',lambda x: np.nan)).reset_index()
    # yearly MAPE
    allr['year']=allr.month.dt.year
    yearly=allr.groupby(['variant','year']).ape.mean().unstack().reset_index()
    summ=summ.drop(columns=['MAE_price']).merge(yearly,on='variant')
    return allr,summ.sort_values('MAPE'),sels


def gate_test(feat):
    d=feat.copy().reset_index(drop=True)
    model_cols={'rw':'rw','momentum':'ma3','vw':'vw_midas_msvr','patch':'causal_patch_transformer'}
    ape_cols={k:(k if k=='rw' else None) for k in []}
    base_features=['gold_ret1','gold_mom3','gold_mom6','gold_daily_vol','cross_corr63','cross_dispersion','gpr','fedfunds','nasdaq_ret1','usdcny_ret1']
    rows=[]
    for i in range(12,len(d)):
        train=d.iloc[:i].copy(); test=d.iloc[[i]].copy()
        # current forecasts/disagreement and lagged model performance are known at origin
        for z in [train,test]:
            z['f_rw_ret']=z.rw/z.prev_actual-1
            z['f_mom_ret']=z.ma3/z.prev_actual-1
            z['f_vw_ret']=z.vw_midas_msvr/z.prev_actual-1
            z['f_patch_ret']=z.causal_patch_transformer/z.prev_actual-1
            z['forecast_dispersion']=z[['rw','ma3','vw_midas_msvr','causal_patch_transformer']].std(axis=1)/z.prev_actual
        # rolling past error means, constructed rowwise from prior known outcomes only
        past_err_features=[]
        for m,ec in [('rw','rw_ape'),('momentum','ma3_ape'),('vw','vw_midas_msvr_ape'),('patch','causal_patch_transformer_ape')]:
            vals=[]
            for j in range(len(train)):
                vals.append(float(train.iloc[max(0,j-3):j][ec].mean()) if j>0 else float(train[ec].iloc[:1].mean()))
            train[f'past3_{m}_ape']=vals
            test[f'past3_{m}_ape']=float(d.iloc[max(0,i-3):i][ec].mean())
            past_err_features.append(f'past3_{m}_ape')
        features=base_features+['f_rw_ret','f_mom_ret','f_vw_ret','f_patch_ret','forecast_dispersion']+past_err_features
        # winner label only from historical rows
        train['winner']=train[['rw_ape','ma3_ape','vw_midas_msvr_ape','causal_patch_transformer_ape']].idxmin(axis=1).map({'rw_ape':'rw','ma3_ape':'momentum','vw_midas_msvr_ape':'vw','causal_patch_transformer_ape':'patch'})
        sx=StandardScaler().fit(train[features]); X=sx.transform(train[features]); xt=sx.transform(test[features])
        if train.winner.nunique()>=2:
            clf=LogisticRegression(C=.1,max_iter=2000,class_weight='balanced',multi_class='auto',random_state=20260827).fit(X,train.winner)
            pick=str(clf.predict(xt)[0])
        else: pick=str(train.winner.iloc[-1])
        # simple selector: lowest expanding past MAPE
        pmeans={'rw':train.rw_ape.mean(),'momentum':train.ma3_ape.mean(),'vw':train.vw_midas_msvr_ape.mean(),'patch':train.causal_patch_transformer_ape.mean()}
        past_pick=min(pmeans,key=pmeans.get)
        r=test.iloc[0]
        actual=float(r.actual)
        def pred_of(k): return float(r[model_cols[k]])
        oracle=min(model_cols,key=lambda k:abs(pred_of(k)-actual))
        eq=float(np.mean([pred_of(k) for k in model_cols]))
        rows.append({'month':r.month,'gate_pick':pick,'gate_forecast':pred_of(pick),'gate_ape':abs(pred_of(pick)-actual)/actual*100,
                     'past_mape_pick':past_pick,'past_mape_forecast':pred_of(past_pick),'past_mape_ape':abs(pred_of(past_pick)-actual)/actual*100,
                     'equal_ensemble':eq,'equal_ensemble_ape':abs(eq-actual)/actual*100,
                     'always_vw_ape':float(r.vw_midas_msvr_ape),'oracle_pick':oracle,'oracle_ape':abs(pred_of(oracle)-actual)/actual*100,
                     'gate_hit':int(pick==oracle)})
    q=pd.DataFrame(rows)
    summary={'test_start':str(q.month.min().date()),'test_end':str(q.month.max().date()),'n':len(q),
             'gate_MAPE':float(q.gate_ape.mean()),'past_mape_selector_MAPE':float(q.past_mape_ape.mean()),
             'equal_ensemble_MAPE':float(q.equal_ensemble_ape.mean()),'always_vw_MAPE':float(q.always_vw_ape.mean()),
             'oracle_MAPE':float(q.oracle_ape.mean()),'gate_winner_hit_rate':float(q.gate_hit.mean())}
    return q,summary


def main():
    core=rm.load_core(); wide=rm.fetch_history(); pred=load_predictions(); feat=attach_features(pred,core,wide)
    cons,cons_s=target_consistency(core,wide); shift=robust_shift(feat); corr,quart=error_anatomy(feat); cp=change_points(pred)
    print('Starting ablations',flush=True); abl,abl_s,abl_sel=ablations(wide,core)
    gate,gate_s=gate_test(feat)
    cons.to_csv(ROOT/'autopsy_target_consistency.csv',index=False); feat.to_csv(ROOT/'autopsy_monthly_features_errors.csv',index=False)
    shift.to_csv(ROOT/'autopsy_covariate_shift.csv',index=False); corr.to_csv(ROOT/'autopsy_error_correlations.csv',index=False)
    quart.to_csv(ROOT/'autopsy_error_quartiles.csv',index=False); abl.to_csv(ROOT/'autopsy_vw_ablation_monthly.csv',index=False)
    abl_s.to_csv(ROOT/'autopsy_vw_ablation_summary.csv',index=False); gate.to_csv(ROOT/'autopsy_regime_gate.csv',index=False)
    summary={'target_consistency':cons_s,'change_points':cp,'gate':gate_s,'ablation_summary':abl_s.to_dict('records'),
             'ablation_selections':abl_sel,'top_covariate_shifts':shift.head(5).to_dict('records'),
             'top_abs_vw_error_correlations':corr[corr.model=='vw'].assign(a=lambda x:x.spearman_error_corr.abs()).sort_values('a',ascending=False).drop(columns='a').head(5).to_dict('records')}
    (ROOT/'autopsy_monthly_summary.json').write_text(json.dumps(summary,indent=2,default=str))
    print(json.dumps(summary,indent=2,default=str),flush=True)

if __name__=='__main__': main()
