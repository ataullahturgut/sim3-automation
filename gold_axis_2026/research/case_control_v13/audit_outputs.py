"""Additional evaluation only; does not fit or select models."""
import research as r
import pandas as pd,numpy as np,json,zipfile
F=pd.read_csv(r.O/'research_feature_panel.csv',parse_dates=['origin']).set_index('origin')
E=pd.read_csv(r.O/'historical_events.csv');C=pd.read_csv(r.O/'matched_controls.csv');D=pd.read_csv(r.O/'daily_all_models.csv',parse_dates=['origin']);cols=json.load(open(r.O/'feature_contract.json'))['features']
# Overlapping event context intervals: never claim these are independent shocks.
cluster=0;end=-1
for i,e in E.iterrows():
 if e.onset_i-30>end:cluster+=1
 E.loc[i,'context_cluster']=cluster;end=max(end,e.onset_i+10)
 cs=C[C.event_id==e.event_id];E.loc[i,'matched_controls']=len(cs)
 complete=F.iloc[max(0,int(e.peak_i)-3):int(e.peak_i)+1][cols].notna().all(axis=1).any()
 E.loc[i,'training_status']='MATCHED' if len(cs)>=2 else 'MISSING_FEATURES' if not complete else 'NO_TWO_NONOVERLAPPING_SAME_YEAR_CONTROLS'
E.to_csv(r.O/'historical_event_coverage.csv',index=False)
# Target horizons compared separately on the original full historical panel.
counts=[]
for year in range(2010,2023):
 f=F[F.index.year==year]
 for h in [1,3,5,10,20]:
  th=.03 if h==1 else .05
  counts.append(dict(year=year,horizon=h,threshold_pct=100*th,valid_days=int(f[f'future_min{h}'].notna().sum()),positive_origins=int((f[f'future_min{h}']<=-th).sum())))
r.csvout('historical_horizon_counts.csv',counts)
# Release ledger, records proxy rather than falsely verified first publication.
weekly=pd.read_csv(r.O/'cftc_parsed_all.csv',parse_dates=['report']);w=weekly.query('market=="GC" and kind=="disaggregated_managed_money"').sort_values('report')
ledger=[]
fred_cache={name:r.fred(name) for name in ["DGS2","DGS10","DFII10","DTWEXB","DTWEXBGS"]}
for d in F.loc['2010':'2022'].index:
 item={'origin':str(d.date()),'decision_clock':'17:30 America/New_York','first_print_verified':False,'strict_signal_allowed':False}
 for name in ['DGS2','DGS10','DFII10','DTWEXB' if d.year<2020 else 'DTWEXBGS']:
  v=fred_cache[name];delay=10 if name.startswith('DTW') else 1;v=v[v.index+pd.Timedelta(days=delay)<=d]
  if len(v):item[name+'_obs']=str(v.index[-1].date());item[name+'_proxy_available']=str((v.index[-1]+pd.Timedelta(days=delay)).date())
 v=w[w.report+pd.Timedelta(days=7)<=d]
 if len(v):
  item['cftc_obs']=str(v.iloc[-1].report.date());item['cftc_proxy_available']=str((v.iloc[-1].report+pd.Timedelta(days=7)).date());item['cftc_age_days']=(d-v.iloc[-1].report).days
 item['exceptional_cftc_quarantine']=pd.isna(F.loc[d,'GC_net'])
 ledger.append(item)
r.csvout('historical_asof_PROXY_NOT_PIT.csv',ledger)
# Comparison to untouched original V8, same 2025/2026 scoring origins.
orig=pd.read_csv(r.O/'replay/gold_risk_v2_daily_alerts.csv',parse_dates=['origin']);rows=[]
for (year,name),g in orig.groupby(['period','family']):
 if name not in ['BASE_14','BASE_14_PLUS_CFTC_7']:continue
 g=g.set_index('origin');ff=F.loc[g.index].copy();ff['y1']=g.y_nextday_drop3;ff['y5']=g.y_next5_drawdown5
 rows.append(dict(period=year,model=name,source='ORIGINAL_V8_REPRODUCTION',**r.metrics(ff,g.alert_level.eq('RED'))))
r.csvout('original_V8_metrics.csv',rows)
# Every model: one/three/five/ten-session strict-pre-onset proxy recall.
timelines=[];episodes=[]
for (year,name),g in D.groupby([D.origin.dt.year,'model']):
 g=g.set_index('origin').sort_index();es=r.events(F,f'{year}-01-01',f'{year}-09-21' if year==2026 else f'{year}-12-31')
 for e in es:
  onset=int(e['onset_i']);eval_dates=F.index[int(e['first_label_i']):int(e['window_end_i'])+1];eligible=sum(d in g.index for d in eval_dates)
  q=dict(period=int(year),model=name,event_id=e['event_id'],onset_proxy=e['onset_proxy'],peak=e['peak'],trough=e['trough'],drawdown_pct=e['drawdown_pct'],eligible=bool(eligible))
  for h in [1,3,5,10]:
   dates=F.index[max(0,onset-h):onset];ad=[d for d in dates if d in g.index and g.loc[d,'red']]
   q[f'early_{h}']=bool(ad) if eligible else None;q[f'first_alarm_{h}']=str(ad[0].date()) if ad and eligible else None
  timelines.append(q)
 red=g[g.red];current=[]
 for d,q in red.iterrows():
  if current and (F.index.get_loc(d)-F.index.get_loc(current[-1][0])!=1):
   episodes.append(dict(period=int(year),model=name,start=str(current[0][0].date()),end=str(current[-1][0].date()),days=len(current),false5_days=sum(bool(x[1].false5) for x in current)));current=[]
  current.append((d,q))
 if current:episodes.append(dict(period=int(year),model=name,start=str(current[0][0].date()),end=str(current[-1][0].date()),days=len(current),false5_days=sum(bool(x[1].false5) for x in current)))
r.csvout('pre_onset_all_models_1_3_5_10.csv',timelines);r.csvout('alarm_episodes.csv',episodes)
# Add literal source observation metadata to daily results for review.
b=pd.read_csv(r.O/'corrected_baseline_daily.csv').query('family=="BASE_14"')[['origin','first_target','target_mature','cftc_observed_position_date','cftc_available_date','cftc_publication_status']]
a=pd.read_csv(r.O/'daily_all_models.csv');a.merge(b,on='origin',how='left',validate='many_to_one').to_csv(r.O/'daily_alarms_with_source_dates.csv',index=False)
# Original source parity vs read-only live database, pinned lineage.
n=json.loads(json.load(open(r.I/'neon_prices_readonly.json'))['content'][0]['text']);nn={q['date'][:10]:q['metals'] for q in n}
s=json.loads(zipfile.ZipFile(r.I/'source.zip').read('risk-overlay-source.json'));prices={q['date']:dict(zip(['AU','AG','PT','PD'],q['metals'])) for q in s['prices'] if q['date']<'2023'}
assert all(all(float(v[k])==prices[d][k] for k in v) for d,v in nn.items() if d in prices)
r.dump('neon_parity.json',{'complete_shared_days':len(prices),'date_rows':len(nn),'value_differences':0,'source_contract':'inputs/neon_prices.sql','incomplete_metal_dates':[d for d,v in nn.items() if len(v)!=4]})
print('AUDIT_OUTPUTS_DONE',len(E),'event groups',cluster,'overlapping context clusters',len(C),'controls')
