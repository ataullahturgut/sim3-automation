from __future__ import annotations
import argparse, io, json, math, re, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

HIGH_AE = 63.06
CAL_START, CAL_END = '2010-01', '2021-12'
DEV_START, DEV_END = '2022-04', '2024-12'

CFTC_SHUTDOWN_RELEASE = {
 '2025-09-30':'2025-11-19','2025-10-07':'2025-11-21','2025-10-14':'2025-11-25',
 '2025-10-21':'2025-12-02','2025-10-28':'2025-12-05','2025-11-04':'2025-12-09',
 '2025-11-10':'2025-12-10','2025-11-18':'2025-12-12','2025-11-25':'2025-12-15',
 '2025-12-02':'2025-12-17','2025-12-09':'2025-12-19','2025-12-16':'2025-12-23',
 '2025-12-23':'2025-12-29'
}

def mshift(m,d):
 y,mo=map(int,m.split('-')); z=y*12+mo-1+d; return f'{z//12:04d}-{z%12+1:02d}'
def eom(m):
 return pd.Period(m,freq='M').end_time.normalize()

def fetch(url, timeout=60):
 h={'User-Agent':'Mozilla/5.0 GOLD_MONTHLY_RESEARCH/1.0'}
 r=requests.get(url,headers=h,timeout=timeout); r.raise_for_status(); return r

def load_inputs(a):
 snap=json.loads(Path(a.snapshot).read_text())['payload']
 pub=json.loads(Path(a.public_bundle).read_text())
 ch=json.loads(Path(a.chhho).read_text())
 vt=json.loads(Path(a.vix_transport).read_text())
 return snap,pub,ch,vt

def build_market(snap,pub):
 daily=list(snap['daily_common_rows'])+list(pub['daily_extension_rows'])
 df=pd.DataFrame(daily); df['date']=pd.to_datetime(df['date']); df=df.sort_values('date').drop_duplicates('date',keep='last')
 df['month']=df.date.dt.strftime('%Y-%m')
 monthly=df.groupby('month')[['Gold','Silver','Platinum','Palladium']].mean().sort_index()
 gold=dict((k,float(v)) for k,v in snap['core_gold'].items())
 gold.update({k:float(v) for k,v in pub['world_bank']['gold_monthly'].items()})
 for k,v in gold.items(): monthly.loc[k,'Gold']=v
 monthly=monthly.sort_index()
 for c in ['Gold','Silver','Platinum','Palladium']:
  monthly[c+'_r1']=np.log(monthly[c]/monthly[c].shift(1))
 monthly['Gold_r3']=np.log(monthly.Gold/monthly.Gold.shift(3))
 monthly['Gold_ma12_prior']=monthly.Gold.shift(1).rolling(12,min_periods=12).mean()
 monthly['Gold_level_gap']=np.log(monthly.Gold/monthly.Gold_ma12_prior)
 dr=np.log(df.Gold).diff(); d2=pd.DataFrame({'month':df.month,'r':dr})
 rv=d2.groupby('month').r.std(ddof=0)*math.sqrt(21)
 monthly['Gold_rv']=rv
 monthly['Gold_rv_med12_prior']=monthly.Gold_rv.shift(1).rolling(12,min_periods=6).median()
 monthly['Gold_rv_ratio']=monthly.Gold_rv/monthly.Gold_rv_med12_prior
 return monthly

def build_chhho(ch,vt):
 rows=[]
 for sec in ['dev','transport_2025','stress_2026']: rows.extend(ch[sec]['rows'])
 aug=[r for r in vt['rows_2026_jan_aug'] if r['target']=='2026-08'][0]
 rows.append({'target':'2026-08','origin':'2026-07','forecast':aug['forecast'],'actual':aug['actual'],'rw':aug['rw'],
              'pred_log_return_gold':math.log(aug['forecast']/aug['rw'])})
 out={}
 for r in rows:
  z=dict(r); z['ae']=abs(float(z['actual'])-float(z['forecast']))
  if 'pred_log_return_gold' not in z: z['pred_log_return_gold']=math.log(float(z['forecast'])/float(z['rw']))
  z['high_error']=z['ae']>HIGH_AE; out[z['target']]=z
 return out

def download_gvz():
 url='https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS'
 r=fetch(url)
 x=pd.read_csv(io.BytesIO(r.content)); x.columns=['date','gvz']; x['date']=pd.to_datetime(x.date); x['gvz']=pd.to_numeric(x.gvz,errors='coerce'); x=x.dropna()
 x['month']=x.date.dt.strftime('%Y-%m')
 g=x.groupby('month').gvz.agg(['mean','max','last']).rename(columns={'mean':'gvz_mean','max':'gvz_max','last':'gvz_last'}).sort_index()
 g['gvz_mean_chg']=g.gvz_mean.diff(); g['gvz_max_chg']=g.gvz_max.diff()
 g['gvz_med12_prior']=g.gvz_mean.shift(1).rolling(12,min_periods=6).median()
 g['gvz_ratio12']=g.gvz_mean/g.gvz_med12_prior
 return g,{'url':url,'rows':len(x),'first':str(x.date.min().date()),'last':str(x.date.max().date())}

def ccol(cols,*needles):
 low={c.lower():c for c in cols}
 for n in needles:
  if n.lower() in low: return low[n.lower()]
 for c in cols:
  s=c.lower()
  if all(t.lower() in s for t in needles): return c
 raise KeyError(f'column not found {needles}; sample={list(cols)[:40]}')

def download_cftc():
 url='https://publicreporting.cftc.gov/resource/72hh-3qpy.json'
 params={'$limit':'50000', '$order':'report_date_as_yyyy_mm_dd ASC',
         '$where':"cftc_contract_market_code='088691' AND report_date_as_yyyy_mm_dd >= '2009-09-01T00:00:00.000'"}
 try:
  r=requests.get(url,params=params,headers={'User-Agent':'GOLD_MONTHLY_RESEARCH/1.0'},timeout=90); r.raise_for_status(); d=pd.DataFrame(r.json())
  source='CFTC_PUBLIC_REPORTING_SODA_72hh-3qpy'
 except Exception:
  parts=[]
  for y in range(2010,2027):
   u=f'https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip'; rr=fetch(u,90); z=zipfile.ZipFile(io.BytesIO(rr.content)); name=z.namelist()[0]; parts.append(pd.read_csv(io.BytesIO(z.read(name)),low_memory=False))
  d=pd.concat(parts,ignore_index=True); source='CFTC_OFFICIAL_ANNUAL_COMPRESSED'
 cols=d.columns
 datec=ccol(cols,'report_date_as_yyyy_mm_dd') if any(c.lower()=='report_date_as_yyyy_mm_dd' for c in cols) else ccol(cols,'report','date')
 codec=ccol(cols,'cftc_contract_market_code') if any(c.lower()=='cftc_contract_market_code' for c in cols) else ccol(cols,'cftc','contract','market','code')
 oi=ccol(cols,'open_interest_all') if any(c.lower()=='open_interest_all' for c in cols) else ccol(cols,'open','interest','all')
 ml=ccol(cols,'m_money_positions_long_all') if any(c.lower()=='m_money_positions_long_all' for c in cols) else ccol(cols,'money','long','all')
 ms=ccol(cols,'m_money_positions_short_all') if any(c.lower()=='m_money_positions_short_all' for c in cols) else ccol(cols,'money','short','all')
 msp=ccol(cols,'m_money_positions_spread_all') if any(c.lower()=='m_money_positions_spread_all' for c in cols) else ccol(cols,'money','spread','all')
 ol=ccol(cols,'other_rept_positions_long_all') if any(c.lower()=='other_rept_positions_long_all' for c in cols) else ccol(cols,'other','long','all')
 os_=ccol(cols,'other_rept_positions_short_all') if any(c.lower()=='other_rept_positions_short_all' for c in cols) else ccol(cols,'other','short','all')
 d=d[d[codec].astype(str).str.contains('088691',na=False)].copy(); d['report_date']=pd.to_datetime(d[datec])
 for c in [oi,ml,ms,msp,ol,os_]: d[c]=pd.to_numeric(d[c],errors='coerce')
 d=d.dropna(subset=[oi,ml,ms]).sort_values('report_date')
 d['oi']=d[oi]; d['mm_long']=d[ml]; d['mm_short']=d[ms]; d['mm_spread']=d[msp]; d['other_long']=d[ol]; d['other_short']=d[os_]
 d['mm_net']=d.mm_long-d.mm_short; d['mm_net_oi']=d.mm_net/d.oi; d['mm_gross_oi']=(d.mm_long+d.mm_short+d.mm_spread)/d.oi; d['other_net_oi']=(d.other_long-d.other_short)/d.oi
 def release(dt):
  k=dt.strftime('%Y-%m-%d')
  return pd.Timestamp(CFTC_SHUTDOWN_RELEASE[k]) if k in CFTC_SHUTDOWN_RELEASE else dt+pd.Timedelta(days=7)
 d['release_date']=d.report_date.map(release)
 return d[['report_date','release_date','oi','mm_net','mm_net_oi','mm_gross_oi','other_net_oi']], {'source':source,'rows':len(d),'first':str(d.report_date.min().date()),'last':str(d.report_date.max().date()),'url':url}

def cftc_monthly_pit(cot,start='2010-01',end='2026-08'):
 rows=[]
 for m in pd.period_range(start,end,freq='M').astype(str):
  q=cot[cot.release_date<=eom(m)]
  if q.empty: continue
  z=q.iloc[-1]; rows.append({'month':m,'report_date':z.report_date,'release_date':z.release_date,'oi':z.oi,'mm_net':z.mm_net,'mm_net_oi':z.mm_net_oi,'mm_gross_oi':z.mm_gross_oi,'other_net_oi':z.other_net_oi})
 x=pd.DataFrame(rows).set_index('month').sort_index()
 for c in ['oi','mm_net_oi','mm_gross_oi','other_net_oi']: x[c+'_chg1']=x[c].diff()
 x['oi_pct1']=x.oi.pct_change(); x['oi_med12_prior']=x.oi.shift(1).rolling(12,min_periods=6).median(); x['oi_ratio12']=x.oi/x.oi_med12_prior
 return x

def q(s,p): return float(pd.to_numeric(s,errors='coerce').dropna().quantile(p))
def thresholds(monthly,gvz,cotm):
 cal=monthly.loc[CAL_START:CAL_END]; gc=gvz.loc[CAL_START:CAL_END]; cc=cotm.loc[CAL_START:CAL_END]
 return {
  'E_level_q95':q(cal.Gold_level_gap,.95),'E_r3_q95':q(cal.Gold_r3,.95),'E_r1_q05':q(cal.Gold_r1,.05),'E_r3_q05':q(cal.Gold_r3,.05),'E_rv_ratio_q95':q(cal.Gold_rv_ratio,.95),
  'F_gvz_max_q80':q(gc.gvz_max,.80),'F_gvz_max_q90':q(gc.gvz_max,.90),'F_gvz_mean_q90':q(gc.gvz_mean,.90),'F_gvz_ratio_q90':q(gc.gvz_ratio12,.90),
  'F_cftc_abs_mmnet_chg_q90':q(cc.mm_net_oi_chg1.abs(),.90),'F_cftc_abs_oi_pct_q90':q(cc.oi_pct1.abs(),.90),'F_cftc_oi_ratio_q10':q(cc.oi_ratio12,.10),'F_cftc_mmnet_low_q10':q(cc.mm_net_oi,.10),'F_cftc_mmnet_high_q90':q(cc.mm_net_oi,.90)
 }

def feature_frame(monthly,gvz,cotm,ch,th):
 idx=monthly.index.union(gvz.index).union(cotm.index).sort_values(); f=monthly.reindex(idx).join(gvz,how='left').join(cotm.add_prefix('cftc_'),how='left')
 f['E_trend_extreme']=(f.Gold_level_gap>th['E_level_q95']) | (f.Gold_r3>th['E_r3_q95'])
 f['E_vol_extreme']=f.Gold_rv_ratio>th['E_rv_ratio_q95']
 f['E_state_2of3']=((f.Gold_level_gap>th['E_level_q95']).astype(int)+(f.Gold_r3>th['E_r3_q95']).astype(int)+(f.Gold_rv_ratio>th['E_rv_ratio_q95']).astype(int))>=2
 f['G_drawdown_1m']=f.Gold_r1<th['E_r1_q05']; f['G_drawdown_3m']=f.Gold_r3<th['E_r3_q05']; f['G_postliq']=f.G_drawdown_1m|f.G_drawdown_3m
 f['F_gvz_q80']=f.gvz_max>=th['F_gvz_max_q80']; f['F_gvz_q90']=f.gvz_max>=th['F_gvz_max_q90']; f['F_gvz_dynamic']=f.gvz_ratio12>=th['F_gvz_ratio_q90']
 f['F_cftc_shift']=(f.cftc_mm_net_oi_chg1.abs()>=th['F_cftc_abs_mmnet_chg_q90']) | (f.cftc_oi_pct1.abs()>=th['F_cftc_abs_oi_pct_q90'])
 f['F_cftc_compression']=f.cftc_oi_ratio12<=th['F_cftc_oi_ratio_q10']
 f['F_position_extreme']=(f.cftc_mm_net_oi<=th['F_cftc_mmnet_low_q10']) | (f.cftc_mm_net_oi>=th['F_cftc_mmnet_high_q90'])
 f['F_flow_2of4']=((f.F_gvz_q80.astype(int)+f.F_cftc_shift.astype(int)+f.F_cftc_compression.astype(int)+f.F_position_extreme.astype(int))>=2)
 for t,r in ch.items():
  o=r['origin']
  if o in f.index:
   f.loc[o,'chhho_pred_move']=r['pred_log_return_gold']; f.loc[o,'chhho_target']=t; f.loc[o,'chhho_ae']=r['ae']; f.loc[o,'high_error']=r['high_error']
 f['E_chhho_disagree_5pp']=f.E_trend_extreme & ((f.chhho_pred_move-f.Gold_r1).abs()>=.05)
 return f

def score_flag(f,ch,flag,start,end):
 rr=[]
 for t,r in sorted(ch.items()):
  if not(start<=t<=end): continue
  o=r['origin']; alarm=bool(f.loc[o,flag]) if o in f.index and pd.notna(f.loc[o,flag]) else False
  rr.append((t,r['high_error'],alarm,r['ae']))
 tp=sum(he and al for _,he,al,_ in rr); fp=sum((not he) and al for _,he,al,_ in rr); fn=sum(he and (not al) for _,he,al,_ in rr); tn=sum((not he) and (not al) for _,he,al,_ in rr)
 return {'n':len(rr),'high_error_n':sum(x[1] for x in rr),'alarms':sum(x[2] for x in rr),'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':None if tp+fp==0 else tp/(tp+fp),'recall':None if tp+fn==0 else tp/(tp+fn),'alarm_targets':[x[0] for x in rr if x[2]],'hit_targets':[x[0] for x in rr if x[1] and x[2]]}

def analog(f,monthly,flag):
 origins=[m for m in f.loc[CAL_START:CAL_END].index if bool(f.loc[m,flag]) and mshift(m,1) in monthly.index]
 allorig=[m for m in monthly.loc[CAL_START:CAL_END].index if mshift(m,1) in monthly.index and pd.notna(monthly.loc[mshift(m,1),'Gold_r1'])]
 vals=[abs(float(monthly.loc[mshift(m,1),'Gold_r1'])) for m in origins]; base=[abs(float(monthly.loc[mshift(m,1),'Gold_r1'])) for m in allorig]
 return {'events':len(origins),'origins':origins,'next_abs_return_mean':None if not vals else float(np.mean(vals)),'next_abs_return_median':None if not vals else float(np.median(vals)),'baseline_next_abs_return_mean':float(np.mean(base)),'uplift_ratio':None if not vals else float(np.mean(vals)/np.mean(base))}

def try_wgc():
 page='https://www.gold.org/goldhub/data/gold-etfs-holdings-and-flows'; out={'page':page,'status':'NOT_USED_IN_ALARM_SCORE'}
 try:
  r=fetch(page); m=re.search(r'href=["\']([^"\']+\.xlsx[^"\']*)',r.text,re.I)
  if not m: out.update(status='DOWNLOAD_LINK_NOT_FOUND'); return out
  u=m.group(1); u='https://www.gold.org'+u if u.startswith('/') else u; out['download_url']=u
  rr=fetch(u); out.update(status='DOWNLOADED',bytes=len(rr.content)); Path('wgc_gold_etf_flows.xlsx').write_bytes(rr.content)
  try:
   xl=pd.ExcelFile(io.BytesIO(rr.content)); out['sheets']=xl.sheet_names
  except Exception as e: out['parse_error']=str(e)
 except Exception as e: out.update(status='BLOCKED_OR_FAILED',error=str(e))
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--snapshot',required=True); ap.add_argument('--public-bundle',required=True); ap.add_argument('--chhho',required=True); ap.add_argument('--vix-transport',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
 snap,pub,chj,vt=load_inputs(a); monthly=build_market(snap,pub); ch=build_chhho(chj,vt)
 gvzm,gvzmeta=download_gvz(); cot,cotmeta=download_cftc(); cotm=cftc_monthly_pit(cot); th=thresholds(monthly,gvzm,cotm); f=feature_frame(monthly,gvzm,cotm,ch,th)
 flags=['E_trend_extreme','E_vol_extreme','E_state_2of3','E_chhho_disagree_5pp','F_gvz_q80','F_gvz_q90','F_gvz_dynamic','F_cftc_shift','F_cftc_compression','F_position_extreme','F_flow_2of4','G_drawdown_1m','G_drawdown_3m','G_postliq']
 periods={'DEV':[DEV_START,DEV_END],'2025':['2025-01','2025-12'],'2026_JAN_AUG':['2026-01','2026-08'],'POST':['2025-01','2026-08'],'ALL_CHHHO':['2022-04','2026-08']}
 scores={fl:{p:score_flag(f,ch,fl,*b) for p,b in periods.items()} for fl in flags}
 analogs={fl:analog(f,monthly,fl) for fl in ['E_trend_extreme','E_vol_extreme','E_state_2of3','F_gvz_q80','F_gvz_q90','F_gvz_dynamic','F_cftc_shift','F_cftc_compression','F_position_extreme','F_flow_2of4','G_drawdown_1m','G_drawdown_3m','G_postliq']}
 rows=[]
 for t,r in sorted(ch.items()):
  o=r['origin']; z={'target':t,'origin':o,'ae':r['ae'],'high_error':r['high_error'],'pred_move':r['pred_log_return_gold']}
  if o in f.index:
   for c in ['Gold_r1','Gold_r3','Gold_level_gap','Gold_rv_ratio','gvz_mean','gvz_max','gvz_last','gvz_ratio12','cftc_oi','cftc_mm_net','cftc_mm_net_oi','cftc_mm_net_oi_chg1','cftc_oi_pct1','cftc_oi_ratio12']+flags:
    v=f.loc[o,c] if c in f.columns else np.nan; z[c]=None if pd.isna(v) else (bool(v) if isinstance(v,(bool,np.bool_)) else float(v))
  rows.append(z)
 wgc=try_wgc()
 out={'schema':'GOLD_MONTHLY_CHHHO_EFG_ALARM_AUDIT_V1_2026-09-29','scope':'ALARM_DETECTION_ONLY_NO_ROUTING_NO_SWITCHING','high_error_threshold_usd':HIGH_AE,'calibration_reference':f'{CAL_START}..{CAL_END}_MARKET_STATE_ONLY','thresholds':th,'sources':{'gvz':gvzmeta,'cftc':cotmeta,'wgc_etf':wgc},'governance':{'A_D_frozen_untouched':True,'2025_2026_used_to_fit_thresholds':False,'E_chhho_disagree_5pp_posthoc_not_validated':True,'cftc_release_timing':'CONSERVATIVE 7-calendar-day safety lag after report date; explicit official 2025 shutdown catch-up overrides','routing_tested':False},'scores':scores,'historical_analogs_2010_2021':analogs,'chhho_rows':rows}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
 print('OUTPUT_GATE=PASS'); print(json.dumps({'thresholds':th,'POST':{k:v['POST'] for k,v in scores.items()},'DEV':{k:v['DEV'] for k,v in scores.items()},'wgc':wgc,'gvz':gvzmeta,'cftc':cotmeta},sort_keys=True))
if __name__=='__main__': main()

# workflow trigger checkpoint 2026-09-29
