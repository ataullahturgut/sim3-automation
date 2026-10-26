"""Executed retrospective case-control experiment. STRICT PIT signals are blocked."""
from pathlib import Path
import csv,json,zipfile,io,hashlib,sys,platform
from datetime import date,timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import gold_risk_cftc_v8_fixed as old
R=Path(__file__).parent; I=R/'inputs'; O=R/'outputs'; O.mkdir(exist_ok=True)

def dump(name,obj): (O/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str)+'\n')
def csvout(name,rows): pd.DataFrame(rows).to_csv(O/name,index=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strict_gate(first_print=False):
 if not first_print:raise ValueError('STRICT_PIT_BLOCK: original publication values and timestamps unverified')

def corrected_cftc():
 df=pd.read_csv(I/'CFTC_GC_SI_2023_2026_QUALITY_GATED.csv',dtype=str)
 # Official historical special announcements, each publication plus one day.
 releases={'2023-01-31':'2023-02-24','2023-02-07':'2023-03-03','2023-02-14':'2023-03-08','2023-02-21':'2023-03-10','2023-02-28':'2023-03-14','2023-03-07':'2023-03-16','2023-03-14':'2023-03-21'}
 changes=[]
 for idx,q in df.iterrows():
  d=q.report_date
  if d in releases:
   avail=(date.fromisoformat(releases[d])+timedelta(days=1)).isoformat()
   if avail>q.earliest_conservative_usable_date:
    changes.append({'market':q.market,'report':d,'old_proxy':q.earliest_conservative_usable_date,'official_publication':releases[d],'research_available':avail})
    df.loc[idx,'earliest_conservative_usable_date']=avail
 df.to_csv(O/'CFTC_ION_corrected.csv',index=False);csvout('CFTC_ION_date_changes.csv',changes)
 return O/'CFTC_ION_corrected.csv'

def cot_archives():
 rows=[];counts=[]
 frozen=I/'cftc_parsed_all.csv'
 if frozen.exists():
  manifest=json.loads((I/'frozen_extraction_hashes.json').read_text())
  assert sha(frozen)==manifest['cftc_parsed_all.csv']
  data=pd.read_csv(frozen,float_precision="round_trip");data.to_csv(O/'cftc_parsed_all.csv',index=False)
  pd.read_csv(I/'cftc_archive_inventory.csv').to_csv(O/'cftc_archive_inventory.csv',index=False)
  return data
 for p in sorted(I.glob('cftc_*.zip')):
  z=zipfile.ZipFile(p); n=0
  for fn in z.namelist():
   if not fn.lower().endswith(('.txt','.csv')):continue
   for q in csv.DictReader(io.StringIO(z.read(fn).decode('utf-8-sig',errors='replace'))):
    legacy='CFTC Contract Market Code' in q
    code=q.get('CFTC Contract Market Code' if legacy else 'CFTC_Contract_Market_Code','').strip().zfill(6)
    if code not in ['088691','084691']:continue
    if legacy:
     d=q['As of Date in Form YYYY-MM-DD']; oi=float(q['Open Interest (All)']);long=float(q['Noncommercial Positions-Long (All)']);short=float(q['Noncommercial Positions-Short (All)'])
    else:
     d=q.get('Report_Date_as_YYYY-MM-DD',q.get('Report_Date_as_MM_DD_YYYY'));oi=float(q['Open_Interest_All']);long=float(q['M_Money_Positions_Long_All']);short=float(q['M_Money_Positions_Short_All'])
    d=pd.Timestamp(d).strftime('%Y-%m-%d');n+=1
    rows.append(dict(report=d,market='GC' if code=='088691' else 'SI',net=(long-short)/oi,short=short/oi,oi=oi,kind='legacy_noncommercial' if legacy else 'disaggregated_managed_money',source=p.name,first_print_verified=False))
  counts.append(dict(file=p.name,rows_gc_si=n,sha256=sha(p)))
 csvout('cftc_archive_inventory.csv',counts);csvout('cftc_parsed_all.csv',rows)
 return pd.DataFrame(rows)

def fred(s):
 df=pd.read_csv(I/f'fred_{s}.csv');df.columns=['date','value'];df.value=pd.to_numeric(df.value,errors='coerce');df=df.dropna();df.date=pd.to_datetime(df.date)
 assert not df.date.duplicated().any();return df.set_index('date').value

def build_panel(source,reference,weekly,extra_lag=0):
 p=pd.DataFrame([dict(date=q['date'],**dict(zip(['AU','AG','PT','PD'],q['metals']))) for q in source['prices']]);p.date=pd.to_datetime(p.date);p=p.set_index('date');L=np.log(p);X=pd.DataFrame(index=p.index)
 for m in p:
  for h in [1,3,5,10,20]:X[f'{m}_ret{h}']=L[m].diff(h)
 X['au_vol20']=L.AU.diff().rolling(20).std(ddof=0)
 X['disp5']=L.diff(5).std(axis=1,ddof=0)
 for m in ['AG','PT','PD']:X[f'corr_AU_{m}20']=L.AU.diff().rolling(20).corr(L[m].diff())
 X['rsi14']=[np.nan]*14+[old.rsi(p.AU.iloc[i-14:i+1].values) for i in range(14,len(p))]
 X['ma20gap']=p.AU/p.AU.rolling(20).mean()-1
 X['au_vol5']=L.AU.diff().rolling(5).std(ddof=0)
 g=pd.read_csv(I/'GVZ_CBOE.csv');g.DATE=pd.to_datetime(g.DATE);g=g.set_index('DATE').GVZ.sort_index();g=g[~g.index.duplicated()]
 gs=pd.DataFrame({'gvz_level':g,'gvz_z252':(g-g.shift(1).rolling(252).mean())/g.shift(1).rolling(252).std(ddof=0),'gvz_dlog5':np.log(g).diff(5),'gvz_dlog1':np.log(g).diff()})
 def lagjoin(frame,days):
  frame=frame.copy();frame.index=frame.index+pd.Timedelta(days=days+extra_lag)
  return frame.reindex(frame.index.union(X.index)).sort_index().ffill().reindex(X.index)
 X=X.join(lagjoin(gs,0))
 for s,stem in [('DGS2','nom2'),('DGS10','nom10'),('DFII10','real10')]:
  v=fred(s);X=X.join(lagjoin(pd.DataFrame({stem:v,stem+'_delta5':v.diff(5)}),1))
 for s,stem in [('DTWEXB','usd_old'),('DTWEXBGS','usd_new')]:
  v=fred(s);X=X.join(lagjoin(pd.DataFrame({stem+'_ret5':np.log(v).diff(5),stem+'_ret1':np.log(v).diff()}),10))
 # Conservative 10 calendar day hypothetical H10 delay, NOT official release certification.
 X['usd_ret5']=X.usd_old_ret5.where(X.index<'2020-01-01',X.usd_new_ret5)
 X['usd_ret1']=X.usd_old_ret1.where(X.index<'2020-01-01',X.usd_new_ret1)
 for k in ['GC','SI']:
  w=weekly[(weekly.market==k)&(weekly.kind=='disaggregated_managed_money')].copy().sort_values('report')
  w.index=pd.to_datetime(w.report);assert not w.index.duplicated().any()
  w=w[['net','short']];w[k+'_net']=w.net;w[k+'_d1']=w.net.diff();w[k+'_d4']=w.net.diff(4);w[k+'_short']=w.short
  X=X.join(lagjoin(w[[k+'_net',k+'_d1',k+'_d4',k+'_short']],7))
 X['GC_SI_diff']=X.GC_net-X.SI_net
 # Unknown exceptional historic publication backlog: no guessed Friday release.
 bad=((X.index>='2013-10-01')&(X.index<='2013-11-15'))|((X.index>='2018-12-22')&(X.index<='2019-03-29'))
 X.loc[bad,[c for c in X if c.startswith(('GC','SI'))]]=np.nan
 names=['AU_ret5','AU_ret20','rsi14','ma20gap','au_vol5','disp5','gvz_level','gvz_z252','gvz_dlog5','gvz_dlog1','usd_ret5','usd_ret1','nom10_delta5','nom10','GC_net','SI_net','GC_d1','GC_d4','SI_d4','GC_SI_diff','GC_short']
 # For modern scoring, reuse exact incumbent inputs with corrected ION availability.
 for q in reference:
  d=pd.Timestamp(q['origin']);X.loc[d,names]=q['features']
 extra=['nom2','nom2_delta5','real10','real10_delta5','AG_ret5','PT_ret5','PD_ret5','corr_AU_AG20','corr_AU_PT20','corr_AU_PD20']
 cols=names+extra
 for h in [1,3,5,10,20]:X[f'future_min{h}']=pd.concat([p.AU.shift(-j)/p.AU-1 for j in range(1,h+1)],axis=1).min(axis=1).where(p.AU.shift(-h).notna())
 X['y1']=X.future_min1<=-.03;X['y5']=X.future_min5<=-.05;X['price']=p.AU;X['day_return_pct']=p.AU.pct_change()*100
 X['source_first_print_verified']=False
 # Never interpolate known corrupt quote. 20 sessions trailing + 20 future for label table.
 if pd.Timestamp('2026-02-27') in p.index:
  j=p.index.get_loc('2026-02-27');X.loc[p.index[j:j+21],cols]=np.nan
  X.loc[p.index[max(0,j-20):j+1],['future_min1','future_min3','future_min5','future_min10','future_min20']]=np.nan
 # Original V8 excludes only forward5; for unchanged comparison restore valid V8 features/targets.
 for q in reference:
  d=pd.Timestamp(q['origin']);X.loc[d,names]=q['features'];X.loc[d,'y1']=q['y_nextday_drop3'];X.loc[d,'y5']=q['y_next5_drawdown5']
  X.loc[d,'future_min1']=q['next_day_return_pct']/100;X.loc[d,'future_min5']=q['next5_min_return_pct']/100
 return X,cols

def events(frame,lo,hi):
 p=frame.price.values; ds=frame.index;intervals=[]
 for i,d in enumerate(ds):
  if not lo<=str(d.date())<=hi or i+20>=len(ds):continue
  if pd.isna(frame.future_min5.iloc[i]):continue
  if frame.y5.iloc[i] or frame.y1.iloc[i]:intervals.append([i,i+(5 if frame.y5.iloc[i] else 1)])
 groups=[]
 for a,b in intervals:
  if groups and a<=groups[-1][1]:groups[-1][1]=max(groups[-1][1],b)
  else:groups.append([a,b])
 out=[]
 for j,(a,b) in enumerate(groups):
  trough=a+int(np.argmin(p[a:b+1]));peak=a+int(np.argmax(p[a:trough+1]));onset=peak+1
  if trough<=peak:continue
  rec=dict(event_id=f'{lo[:4]}_{j+1:03}',first_label=str(ds[a].date()),last_window=str(ds[b].date()),peak=str(ds[peak].date()),onset_proxy=str(ds[onset].date()),trough=str(ds[trough].date()),drawdown_pct=100*(p[trough]/p[peak]-1),peak_i=peak,onset_i=onset,trough_i=trough,window_end_i=b,first_label_i=a)
  rebound=next((k for k in range(trough+1,min(len(p),trough+253)) if p[k]>=p[peak]),None)
  rec['recovery']=str(ds[rebound].date()) if rebound is not None else None
  out.append(rec)
 return out

def sample(frame,ev,cols,cut):
 good=frame[cols].notna().all(axis=1);eligible=np.flatnonzero(good & (frame.index<=cut)); matchcols=['AU_ret20','au_vol20','disp5'];sc=RobustScaler().fit(frame.loc[good&(frame.index<=cut),matchcols]);Z=sc.transform(frame[matchcols]);used=[];pairs=[];idx=[];ys=[];weights=[]
 for e in ev:
  p=e['peak_i']
  if frame.index[min(len(frame)-1,e['window_end_i']+20)]>pd.Timestamp(cut):continue
  pos=[j for j in range(max(30,p-3),p+1) if good.iloc[j]]
  if not pos:continue
  cands=[j for j in eligible if j>=30 and j+20<len(frame) and frame.index[j+20]<=pd.Timestamp(cut) and frame.index[j].year==frame.index[p].year and not frame.y1.iloc[j] and frame.future_min10.iloc[j]>-.05 and all(abs(j-v['peak_i'])>40 for v in ev) and all(abs(j-u)>40 for u in used)]
  cands=sorted(cands,key=lambda j:np.linalg.norm(Z[j]-Z[p]));controls=[]
  for j in cands:
   if all(abs(j-u)>40 for u in used+controls):controls.append(j)
   if len(controls)==3:break
  if len(controls)<2:continue
  used+=controls
  idx+=pos+controls;ys += [1]*len(pos)+[0]*len(controls);weights += [1/len(pos)]*len(pos)+[1/len(controls)]*len(controls)
  for j in controls:pairs.append(dict(event_id=e['event_id'],case_date=str(frame.index[p].date()),control_date=str(frame.index[j].date()),distance=float(np.linalg.norm(Z[j]-Z[p])),control_i=j,n_controls=len(controls)))
 return np.array(idx),np.array(ys),np.array(weights),pairs

def metrics(f,alarm):
 a=np.asarray(alarm,dtype=bool);y1=f.y1.to_numpy(bool);y5=f.y5.to_numpy(bool);g=[]
 for i in np.flatnonzero(y5):
  if g and i==g[-1][-1]+1:g[-1].append(i)
  else:g.append([i])
 false=a&~y5
 # Episodes break on unscored gaps >4 calendar days; all counts on matched origins.
 gap=np.r_[True,np.diff(f.index.values).astype('timedelta64[D]').astype(int)>4]
 episodes=lambda mask:int(np.sum(mask & (np.r_[True,~mask[:-1]]|gap)))
 return dict(n=len(f),red=int(a.sum()),hit1=int((a&y1).sum()),total1=int(y1.sum()),hit5=int((a&y5).sum()),total5=int(y5.sum()),groups_hit=sum(bool(a[q].any()) for q in g),groups=len(g),false5=int(false.sum()),false_episodes=episodes(false),alarm_episodes=episodes(a))

def main():
 source,cot,_=old.load(I/'source.zip',I/'CFTC_GC_SI_2023_2026_QUALITY_GATED.csv');original_rows=old.make_rows(source,cot)
 corrected=corrected_cftc();_,cot2,_=old.load(I/'source.zip',corrected);ref=old.make_rows(source,cot2);stats,daily=old.compute(ref);csvout('corrected_baseline_daily.csv',daily);dump('corrected_baseline_stats.json',stats)
 weekly=cot_archives();frame,cols=build_panel(source,ref,weekly);frame.to_csv(O/'research_feature_panel.csv',index_label='origin');dump('feature_contract.json',{'features':cols,'first_print_verified':False,'strict_signal_allowed':False})
 ev=events(frame,'2010-01-01','2022-12-31');csvout('historical_events.csv',ev)
 idx,y,weights,pairs=sample(frame,ev,cols,'2022-12-31');csvout('matched_controls.csv',pairs)
 csvout('training_rows.csv',[dict(origin=str(frame.index[j].date()),y=int(yy),weight=float(w)) for j,yy,w in zip(idx,y,weights)])
 windows=[]
 for kind,records in [('event',ev),('control',pairs)]:
  for e in records:
   center=e['onset_i'] if kind=='event' else e['control_i']
   for j in range(max(0,center-30),min(len(frame),center+11)):
    q={'event_id':e['event_id'],'kind':kind,'anchor':str(frame.index[center].date()),'offset':j-center,'origin':str(frame.index[j].date())}
    q.update(frame.iloc[j][cols+['price','day_return_pct','future_min1','future_min5']].to_dict());windows.append(q)
 csvout('event_control_windows_minus30_plus10.csv',windows)
 desc=[]
 for c in cols:
  pos=frame.iloc[idx[y==1]][c];neg=frame.iloc[idx[y==0]][c]
  desc.append({'feature':c,'case_median':pos.median(),'control_median':neg.median(),'case_q25':pos.quantile(.25),'case_q75':pos.quantile(.75),'control_q25':neg.quantile(.25),'control_q75':neg.quantile(.75)})
 csvout('case_control_feature_profiles.csv',desc)
 fam={'LOGIT_ALL':cols,'GBM_ALL':cols,'LOGIT_NO_CFTC':[c for c in cols if not c.startswith(('GC','SI'))], 'LOGIT_NO_USD':[c for c in cols if not c.startswith('usd')],'LOGIT_NO_RATES':[c for c in cols if not c.startswith(('nom','real'))],'LOGIT_NO_GVZ':[c for c in cols if not c.startswith('gvz')]}
 def fit(name,cc,ii,yy,ww):
  s=RobustScaler().fit(frame.iloc[ii][cc]);xx=s.transform(frame.iloc[ii][cc]);model=GradientBoostingClassifier(n_estimators=60,max_depth=2,min_samples_leaf=10,random_state=1701) if name.startswith('GBM') else LogisticRegression(C=.1,max_iter=3000,random_state=1701)
  model.fit(xx,yy,sample_weight=ww);return s,model
 dd=pd.DataFrame(daily); dd.origin=pd.to_datetime(dd.origin);dmap=dd.pivot(index='origin',columns='family',values='alert_level')
 valid=dmap.index;assert frame.loc[valid,cols].notna().all().all(),'MODERN_MISSING_INPUT'
 cand={};freeze=[];validation=[]
 for name,cc in fam.items():
  scaler,model=fit(name,cc,idx,y,weights);tr=model.predict_proba(scaler.transform(frame.iloc[idx][cc]))[:,1];pred=model.predict_proba(scaler.transform(frame.loc[valid,cc]))[:,1]
  for quant in [.1,.25,.5]:
   threshold=float(np.quantile(tr,quant));label=f'{name}_Q{int(quant*100)}';cand[label]=pd.Series(pred>=threshold,index=valid);freeze.append(dict(model=label,feature_names=cc,quantile=quant,threshold=threshold,train_end='2022-12-31'))
  pd.DataFrame({'origin':valid,'score':pred}).to_csv(O/f'scores_{name}.csv',index=False)
 cand['PASSTHROUGH']=pd.Series(True,index=valid)
 alarms={'BASE14':dmap.BASE_14.eq('RED'),'CFTC21':dmap.BASE_14_PLUS_CFTC_7.eq('RED')};union=alarms['BASE14']|alarms['CFTC21']
 for name,s in cand.items():alarms[name]=union&s
 ids2025=valid[valid.year==2025];ids2026=valid[valid.year==2026]
 for name,s in alarms.items():validation.append(dict(model=name,**metrics(frame.loc[ids2025],s.loc[ids2025])))
 csvout('validation_2025_selection.csv',validation)
 eligible=[q for q in validation if q['model'] in cand and q['hit1']==q['total1'] and q['groups_hit']==q['groups']]
 selected=min(eligible,key=lambda q:(q['false5'],q['false_episodes'],q['model']))['model'] if eligible else 'PASSTHROUGH'
 dump('FROZEN_SELECTION_2025.json',{'selected':selected,'selection_uses_2026':False,'candidates':freeze,'training_cases':int(sum(y==1)),'training_controls':int(sum(y==0)),'matched_training_event_groups':len(set(q['event_id'] for q in pairs)),'validation_gate_passed':bool(eligible),'fallback_is_not_a_new_model':not bool(eligible)})
 # Only after frozen selection, score/report 2026.
 results=[];day=[];timelines=[]
 for year,ids in [(2025,ids2025),(2026,ids2026)]:
  for name,s in alarms.items():
   results.append(dict(period=year,model=name,selected=name==selected,**metrics(frame.loc[ids],s.loc[ids])))
   for d in ids:
    f=frame.loc[d];day.append(dict(origin=str(d.date()),model=name,red=bool(s.loc[d]),price=f.price,alarm_day_return_pct=f.day_return_pct,nextday_pct=100*f.future_min1,next5_min_pct=100*f.future_min5,false5=bool(s.loc[d] and not f.y5),strict_pit_signal=False))
  es=events(frame,f'{year}-01-01',f'{year}-09-21' if year==2026 else f'{year}-12-31')
  for e in es:
   start=e['onset_i'];end=e['trough_i'];hist=frame.index[max(0,start-10):end+1]
   for name in ['BASE14','CFTC21',selected]:
    signal=alarms[name];ad=[d for d in hist if d in signal.index and bool(signal.loc[d])];first=ad[0] if ad else None
    rec=dict(period=year,model=name,**e,first_alarm=str(first.date()) if first is not None else None,lead_sessions=start-frame.index.get_loc(first) if first is not None else None)
    rec['eligible_origins_in_event']=sum(d in signal.index for d in frame.index[e['first_label_i']:e['window_end_i']+1])
    rec['timing']='NOT_EVALUABLE_QUARANTINE' if not rec['eligible_origins_in_event'] else 'MISSED' if first is None else 'EARLY_DAILY_PROXY' if first<frame.index[start] else 'ONSET_EOD_NOT_EARLY' if first==frame.index[start] else 'LATE';timelines.append(rec)
 csvout('paired_results.csv',results);csvout('daily_all_models.csv',day);csvout('event_alarm_timeline.csv',timelines)
 # Walk-forward all candidate families, only earlier events and controls; no 2026 inputs.
 wf=[]
 for cut,lo,hi in [('2016-12-31','2017-01-01','2019-12-31'),('2019-12-31','2020-01-01','2022-12-31')]:
  ii,yy,ww,_=sample(frame,ev,cols,cut)
  test=frame.loc[lo:hi].dropna(subset=cols);test=test.iloc[20:-20]
  if len(np.unique(yy))<2:continue
  for name,cc in fam.items():
   sc,mo=fit(name,cc,ii,yy,ww);tr=mo.predict_proba(sc.transform(frame.iloc[ii][cc]))[:,1];te=mo.predict_proba(sc.transform(test[cc]))[:,1]
   threshold=float(np.quantile(tr,.25));wf.append(dict(train_end=cut,test_first=lo,test_last=hi,model=name,threshold=threshold,**metrics(test,te>=threshold)))
 csvout('historical_walk_forward.csv',wf)
 # Lag sensitivity of historical training inputs; model definitions/2025 frozen thresholds unchanged.
 sensitivity=[]
 for lag in [3,7]:
  alt,_=build_panel(source,ref,weekly,extra_lag=lag)
  for name,cc in fam.items():
   ii=idx[alt.iloc[idx][cc].notna().all(axis=1).values];mask=np.isin(idx,ii);sc=RobustScaler().fit(alt.iloc[ii][cc]);model=GradientBoostingClassifier(n_estimators=60,max_depth=2,min_samples_leaf=10,random_state=1701) if name.startswith('GBM') else LogisticRegression(C=.1,max_iter=3000,random_state=1701)
   model.fit(sc.transform(alt.iloc[ii][cc]),y[mask],sample_weight=weights[mask]);te=model.predict_proba(sc.transform(alt.loc[ids2025,cc]))[:,1]
   th=next(q['threshold'] for q in freeze if q['model']==name+'_Q25');sensitivity.append(dict(lag=lag,model=name,**metrics(frame.loc[ids2025],union.loc[ids2025]&(te>=th))))
 csvout('historical_lag_sensitivity_2025.csv',sensitivity)
 # Inputs are archived current snapshots. Fail-closed strict gate is deliberately exercised.
 try:strict_gate()
 except ValueError:blocked=True
 coverage=[]
 for c in cols:
  for year in range(2000,2023):
   z=frame.loc[frame.index.year==year];coverage.append(dict(year=year,feature=c,n_nonnull=int(z[c].notna().sum()),n_days=len(z),pit_certified=0))
 csvout('coverage_by_year.csv',coverage)
 audit={'historical_requested':'2000-2022','historical_price_available':'2010-2022','events':len(ev),'matched_events':len(set(q['event_id'] for q in pairs)),'controls':len(pairs),'train_rows':len(idx),'modern_origins':len(ref),'selected':selected,'strict_pit_blocked':blocked,'source_first_print_verified':False,'intraday_onset_verified':False,'neon_writes':False,'models_promoted':False,'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},'inputs':{p.name:sha(p) for p in I.iterdir() if p.is_file()}}
 dump('audit.json',audit);print(json.dumps(audit,ensure_ascii=False));print(pd.DataFrame(results).query('model in ["BASE14","CFTC21",@selected]').to_string(index=False))
if __name__=='__main__':main()
