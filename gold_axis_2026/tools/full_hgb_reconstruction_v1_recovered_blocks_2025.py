from __future__ import annotations
import argparse, json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

NY = ZoneInfo('America/New_York')
FINAL = {'VALID_EXACT_BAR','PROVIDER_NO_BAR'}
TRAIN_START=pd.Timestamp('2022-01-01'); TRAIN_END=pd.Timestamp('2024-12-31')
CH_START=pd.Timestamp('2025-01-01'); CH_END=pd.Timestamp('2025-12-31')
GOLD=['gold_ret_lag1','gold_ret_lag2','gold_ret_lag3','gold_mom3','gold_mom5','gold_mom10','gold_mom20','gold_rv5','gold_rv10','gold_rv20']
DAILY_MAP={'xag':'XAG_STAKTRAKR_RESEARCH_DAILY_R1','xpt':'XPT_STAKTRAKR_RESEARCH_DAILY_R1','xpd':'XPD_STAKTRAKR_RESEARCH_DAILY_R1','nasdaq':'NASDAQ100_FRED','sp500':'SP500_FRED','djia':'DJIA_FRED'}
MONTHLY_MAP={'dgs10':'DGS10_ALFRED_PIT_ME','dff':'DFF_ALFRED_PIT_ME','fx':'DEXCHUS_ALFRED_PIT_ME'}
EVENTS={'MACRO_EVENT_V3_EMPLOYMENT_SCORE','MACRO_EVENT_V3_INFLATION_SCORE'}
CAT=['monthly_direction_3m','fast_state','slow_state','emergency_level','emergency_reversal']
NUM=GOLD+['xag_ret','xpt_ret','xpd_ret','nasdaq_ret','sp500_ret','djia_ret','dgs10_level','dff_level','fx_ret','macro_score','macro_event_count']

def load_contract(p: Path):
    c=json.loads(p.read_text())
    assert c['contract_id']=='FULL_HGB_RECONSTRUCTION_V1_RECOVERED_BLOCKS_2025'
    assert c['status']=='FROZEN_BEFORE_2025_REPLAY'
    assert c['numeric_features']==NUM and c['categorical_features']==CAT
    assert not c['split']['challenge_refit'] and not c['split']['challenge_hyperparameter_search'] and not c['split']['challenge_threshold_search']
    return c

def exact(p: Path, challenge=False):
    d=pd.read_csv(p,dtype=str,keep_default_na=False)
    if not {'trade_date','acquisition_status'}<=set(d): raise RuntimeError('EXACT_SCHEMA_FAIL')
    bad=set(d.acquisition_status)-FINAL
    if bad: raise RuntimeError(f'UNRESOLVED_EXACT:{sorted(bad)}')
    v=d[d.acquisition_status.eq('VALID_EXACT_BAR')].copy()
    if challenge:
        exp={'provider':'Twelve Data','symbol':'XAU/USD','interval':'1min','timezone':'America/New_York','accepted_source_time':'16:59:00','evidence_class':'HISTORICAL_REPLAY_RECONSTRUCTION','prospective_claim':'False'}
        for k,x in exp.items():
            if k not in v or set(v[k])!={x}: raise RuntimeError(f'CHALLENGE_LINEAGE_FAIL:{k}')
    v['date']=pd.to_datetime(v.trade_date).dt.normalize(); v['close']=pd.to_numeric(v.close,errors='raise')
    if v.date.duplicated().any() or (v.close<=0).any(): raise RuntimeError('INVALID_EXACT')
    return v[['date','close']].sort_values('date').reset_index(drop=True)

def gold_features(d):
    q=d.copy(); r=np.log(q.close).diff()
    q['gold_ret_lag1']=r; q['gold_ret_lag2']=r.shift(1); q['gold_ret_lag3']=r.shift(2)
    for k in [3,5,10,20]: q[f'gold_mom{k}']=np.log(q.close/q.close.shift(k))
    for k in [5,10,20]: q[f'gold_rv{k}']=r.rolling(k,min_periods=k).std(ddof=0)
    return q

def attach_external(d,p):
    o=pd.read_csv(p)
    req={'series_id','observation_ts','value','available_as_of'}
    if not req<=set(o): raise RuntimeError('EXTERNAL_SCHEMA_FAIL')
    o['observation_ts']=pd.to_datetime(o.observation_ts,format='mixed',utc=True)
    o['available_as_of']=pd.to_datetime(o.available_as_of,format='mixed',utc=True)
    o['value']=pd.to_numeric(o.value,errors='coerce'); o=o.dropna(subset=['value'])
    out=d.sort_values('date').copy(); out['origin_utc']=(out.date.dt.tz_localize(NY)+pd.Timedelta(hours=17)).dt.tz_convert('UTC')
    for name,sid in DAILY_MAP.items():
        z=o[o.series_id.eq(sid)][['observation_ts','value']].copy()
        z['source_date']=z.observation_ts.dt.tz_localize(None).dt.normalize(); z=z.sort_values('source_date').drop_duplicates('source_date',keep='last')
        z[f'{name}_ret']=np.log(z.value).diff(); z=z[['source_date',f'{name}_ret']].rename(columns={'source_date':f'{name}_source_date'})
        out=pd.merge_asof(out.sort_values('date'),z.sort_values(f'{name}_source_date'),left_on='date',right_on=f'{name}_source_date',direction='backward',allow_exact_matches=False)
        if (out[f'{name}_source_date'].notna() & (out[f'{name}_source_date']>=out.date)).any(): raise RuntimeError(f'FUTURE_DAILY:{name}')
    for name,sid in MONTHLY_MAP.items():
        z=o[o.series_id.eq(sid)][['available_as_of','value']].copy().sort_values('available_as_of').drop_duplicates('available_as_of',keep='last')
        if name=='fx': z['fx_ret']=np.log(z.value).diff(); cols=['available_as_of','fx_ret']
        else: z[f'{name}_level']=z.value; cols=['available_as_of',f'{name}_level']
        z=z[cols].rename(columns={'available_as_of':f'{name}_available'})
        out=pd.merge_asof(out.sort_values('origin_utc'),z.sort_values(f'{name}_available'),left_on='origin_utc',right_on=f'{name}_available',direction='backward',allow_exact_matches=True).sort_values('date')
        if (out[f'{name}_available'].notna() & (out[f'{name}_available']>out.origin_utc)).any(): raise RuntimeError(f'FUTURE_MACRO:{name}')
    ev=o[o.series_id.isin(EVENTS)].copy(); ev['event_date']=ev.observation_ts.dt.tz_convert(NY).dt.tz_localize(None).dt.normalize()
    e=ev.groupby('event_date').agg(macro_score=('value','sum'),macro_event_count=('value','size'),macro_available=('available_as_of','max')).reset_index()
    out=out.merge(e,left_on='date',right_on='event_date',how='left'); bad=out.macro_available.notna()&(out.macro_available>out.origin_utc)
    out.loc[bad,['macro_score','macro_event_count']]=np.nan
    out['macro_score']=out.macro_score.fillna(0.0); out['macro_event_count']=out.macro_event_count.fillna(0.0)
    return out

def attach_context(d, formation_panel: Path, challenge_context: Path, missing_token: str):
    f=pd.read_csv(formation_panel,dtype=str,keep_default_na=False)
    if not {'date',*CAT}<=set(f): raise RuntimeError('FORMATION_CONTEXT_SCHEMA_FAIL')
    f['date']=pd.to_datetime(f.date).dt.normalize(); f=f[['date',*CAT]].drop_duplicates('date',keep=False)
    c=pd.read_csv(challenge_context,dtype=str,keep_default_na=False)
    if not {'date',*CAT}<=set(c): raise RuntimeError('CHALLENGE_CONTEXT_SCHEMA_FAIL')
    c['date']=pd.to_datetime(c.date).dt.normalize(); c=c[['date',*CAT]].drop_duplicates('date',keep=False)
    ctx=pd.concat([f[f.date.between(TRAIN_START,TRAIN_END)],c[c.date.between(CH_START,CH_END)]],ignore_index=True).drop_duplicates('date',keep=False)
    out=d.merge(ctx,on='date',how='left',validate='one_to_one')
    for col in CAT:
        out[col]=out[col].replace('',np.nan).fillna(missing_token).astype(str)
    return out

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-12,1-1e-12); pr=p>=.5
    return {'n':int(len(y)),'up_rate':float(y.mean()),'mean_p_up':float(p.mean()),'accuracy':float(np.mean(pr==y)),'balanced_accuracy':float(balanced_accuracy_score(y,pr)),'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--historical-exact',type=Path,required=True); ap.add_argument('--challenge-exact',type=Path,required=True); ap.add_argument('--formation-context',type=Path,required=True); ap.add_argument('--challenge-context',type=Path,required=True); ap.add_argument('--external-csv',type=Path,required=True); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); c=load_contract(a.contract)
    h=exact(a.historical_exact); h=h[h.date<=TRAIN_END]; ch=exact(a.challenge_exact,True)
    d=pd.concat([h,ch]).sort_values('date').drop_duplicates('date',keep='last').reset_index(drop=True)
    d=attach_context(attach_external(gold_features(d),a.external_csv),a.formation_context,a.challenge_context,c['categorical_missing_token'])
    d['next_date']=d.date.shift(-1); d['next_return']=np.log(d.close.shift(-1)/d.close); d['y_up_next']=(d.next_return>0).astype(float); d.loc[d.next_return.isna(),'y_up_next']=np.nan
    train_mask=d.date.between(TRAIN_START,TRAIN_END)&d.next_date.le(TRAIN_END)&d[NUM].notna().all(axis=1)&d.y_up_next.notna(); tr=d.loc[train_mask].copy()
    if len(tr)<250 or tr.y_up_next.nunique()<2: raise RuntimeError(f'INSUFFICIENT_TRAIN:{len(tr)}')
    pre=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CAT),('num','passthrough',NUM)],remainder='drop')
    clf=HistGradientBoostingClassifier(max_depth=2,max_iter=80,learning_rate=.05,l2_regularization=1,random_state=20260911)
    model=make_pipeline(pre,clf); model.fit(tr[CAT+NUM],tr.y_up_next.astype(int))
    all_ch=d[d.date.between(CH_START,CH_END)].copy(); score_mask=all_ch[NUM].notna().all(axis=1); sc=all_ch.loc[score_mask,['date','close','next_date','next_return','y_up_next',*CAT,*NUM]].copy()
    if len(sc)<180: raise RuntimeError(f'INSUFFICIENT_CHALLENGE:{len(sc)}')
    sc['p_up_next_governed_origin']=model.predict_proba(sc[CAT+NUM])[:,1]; sc['edge_up_minus_down']=2*sc.p_up_next_governed_origin-1; sc['implied_direction']=np.where(sc.p_up_next_governed_origin>=.5,'UP','DOWN'); sc['research_identity']=c['research_identity']; sc['evidence_class']='HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PROSPECTIVE'; sc['challenge_refit']=False
    ev=sc[sc.next_date.le(CH_END)&sc.y_up_next.notna()]; met=metrics(ev.y_up_next.astype(int),ev.p_up_next_governed_origin)
    context_missing={k:int((all_ch[k]==c['categorical_missing_token']).sum()) for k in CAT}
    summary={'audit_id':'FULL_HGB_RECONSTRUCTION_V1_RECOVERED_BLOCKS_2025_REPLAY','status':'PASS','research_identity':c['research_identity'],'manifest_channel_being_reconstructed':'FULL_HGB','original_identity_recovered':False,'identity_claim':c['identity_claim'],'train_rows':int(len(tr)),'challenge_exact_rows':int(len(ch)),'challenge_feature_complete_rows':int(len(sc)),'challenge_feature_coverage':float(len(sc)/len(all_ch)),'challenge_auxiliary_metrics':met,'probability_min':float(sc.p_up_next_governed_origin.min()),'probability_max':float(sc.p_up_next_governed_origin.max()),'probability_mean':float(sc.p_up_next_governed_origin.mean()),'implied_direction_counts':{str(k):int(v) for k,v in sc.implied_direction.value_counts().items()},'numeric_features':NUM,'categorical_features':CAT,'challenge_context_missing_counts':context_missing,'excluded_blocks':c['excluded_blocks'],'model':'OneHotEncoder+HistGradientBoostingClassifier(max_depth=2,max_iter=80,learning_rate=0.05,l2_regularization=1,random_state=20260911)','challenge_refit':False,'hyperparameter_search':False,'threshold_search':False,'post_challenge_tuning':False,'current_gc_break_primary_target':False,'auxiliary_target_only':True,'production_database_write':'NONE','production_authority':False}
    sc.to_csv(a.output_dir/'full_hgb_reconstruction_v1_recovered_blocks_2025_daily.csv',index=False); (a.output_dir/'full_hgb_reconstruction_v1_recovered_blocks_2025_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); print(json.dumps(summary,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
