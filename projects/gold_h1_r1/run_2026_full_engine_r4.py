#!/usr/bin/env python3
import io,json,math,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
OUT=Path('projects/gold_h1_r1')
D1_PIN='a33d38a29cc84aa0cd641ae07bee80874a6cfb7b'
D1=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{D1_PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
GVZ='https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv'
MACRO_PIN='c3e2d4c79868ee516dc0ed111e1e4a28608a3a8b'
MACRO=f'https://raw.githubusercontent.com/superpilot69/fred-us-macro-open-data/{MACRO_PIN}/data/fred-us-macro-events.json'
CUTOFF=pd.Timestamp('2026-08-28')

def b(url):
    req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-2026-r4/1.0'})
    with urllib.request.urlopen(req,timeout=240) as r:return r.read()
def csv(url): return pd.read_csv(io.BytesIO(b(url)))

# daily gold, source locked through latest completed market day
D=csv(D1); D['date']=pd.to_datetime(D['time']); D=D[['date','open','high','low','close']].sort_values('date').drop_duplicates('date'); D=D[D.date<=CUTOFF].copy()
D['month']=D.date.dt.to_period('M').astype(str); D['ret']=D.close.pct_change(); D['ret5']=D.close.pct_change(5); D['sma20']=D.close.rolling(20).mean(); D['sma50']=D.close.rolling(50).mean()
fr=np.sign(D.close-D.sma20).to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
    if np.isfinite(fr[i]) and fr[i]!=0 and fr[i]==fr[i-1]: fast[i]=int(fr[i])
D['fast']=fast
# completed Sunday-Friday week; two completed weeks persistence
wd=D[['date','close']].copy(); wd['wk_start']=(wd.date-pd.to_timedelta((wd.date.dt.weekday+1)%7,unit='D')).dt.normalize()
W=wd.groupby('wk_start').agg(wclose=('close','last')).reset_index().sort_values('wk_start'); W['sma4']=W.wclose.rolling(4).mean(); wr=np.sign(W.wclose-W.sma4).to_numpy(); slow=np.zeros(len(W),int)
for i in range(1,len(W)):
    if np.isfinite(wr[i]) and wr[i]!=0 and wr[i]==wr[i-1]: slow[i]=int(wr[i])
W['slow']=slow; W['known_date']=W.wk_start+pd.Timedelta(days=6)
D=pd.merge_asof(D.sort_values('date'),W[['known_date','slow']].rename(columns={'known_date':'date'}).sort_values('date'),on='date',direction='backward'); D['slow']=D.slow.fillna(0).astype(int)

# monthly origin-safe directions Jan-Jul from frozen project artifact; Aug from completed Apr-Jul monthly averages only
T=pd.read_csv(OUT/'tactical_origin_2026_jan_jul.csv'); prior={r.target:int(r.mom3_dir) for _,r in T.iterrows()}; mom1={r.target:int(r.mom1_dir) for _,r in T.iterrows()}; origin_actual={r.target:int(r.actual_dir) for _,r in T.iterrows()}
# exact project monthly averages: Apr=4721, May=4587, Jun=4228, Jul=4073
rets=np.array([4587/4721-1,4228/4587-1,4073/4228-1]); aug_mom=4073*(1+rets.mean()); prior['2026-08']=1 if aug_mom>4073 else -1; mom1['2026-08']=-1
D['prior']=D.month.map(prior).fillna(0).astype(int); D['mom1']=D.month.map(mom1).fillna(0).astype(int)

# monthly main price-engine context Jan-Jul selector artifact; Aug full expert file produced separately by workflow
G=pd.read_csv(OUT/'model_selector_gate_2024_2026.csv'); G['month']=pd.to_datetime(G.month).dt.to_period('M').astype(str); gate_pick=dict(zip(G.month,G.gate_pick)); gate_fc=dict(zip(G.month,G.gate_forecast))
aug={}
augp=OUT/'AUGUST_2026_FORECAST_R4.json'
if augp.exists(): aug=json.loads(augp.read_text())
D['gate_pick']=D.month.map(gate_pick).fillna(''); D['gate_forecast']=D.month.map(gate_fc)

# official Cboe GVZ; hard fail if current period missing
g=csv(GVZ); cols={c.upper():c for c in g.columns}; dc=cols.get('DATE'); cc=cols.get('CLOSE') or cols.get('GVZ');
if not dc or not cc: raise RuntimeError(f'Unexpected GVZ columns {list(g.columns)}')
g=g[[dc,cc]].rename(columns={dc:'date',cc:'GVZ'}); g['date']=pd.to_datetime(g.date); g['GVZ']=pd.to_numeric(g.GVZ,errors='coerce'); g=g.dropna().sort_values('date')
D=pd.merge_asof(D.sort_values('date'),g,on='date',direction='backward',tolerance=pd.Timedelta('7D')); assert not D[(D.date>='2026-01-01')].GVZ.isna().any()
D['gvz_q90_252']=D.GVZ.shift(1).rolling(252,min_periods=126).quantile(.90); D['gvz_stress']=D.GVZ>=D.gvz_q90_252

# frozen price emergency rules selected before 2023
D['mtd_peak']=D.groupby('month').close.cummax(); D['mtd_trough']=D.groupby('month').close.cummin(); D['mtd_dd']=D.close/D.mtd_peak-1; D['mtd_up']=D.close/D.mtd_trough-1
D['price_emg_down']=(D.mtd_dd<=-.03)&(D.ret5<=-.04)&(D.close<D.sma50)
D['price_emg_up']=(D.mtd_up>=.03)&(D.ret5>=.02)&(D.close>D.sma50)

# frozen pre-2023 Macro Event DOWN rule: score<=-1, Fast DOWN, same-day return<=-0.5%.
# Pinned replay source covers releases through Apr-2026; append Apr-30 core PCE from timestamped calendar evidence.
obj=json.loads(b(MACRO)); events=obj['events'] if isinstance(obj,dict) and 'events' in obj else obj
sgn={'PAYEMS':-1,'UNRATE':1,'CES0500000003':-1,'RSAFS':-1,'CPIAUCNS':-1,'CPILFENS':-1,'PPIACO':-1,'PCEPILFE':-1}; er=[]
for e in events:
    md=e.get('metadata') or {}; sid=md.get('seriesId'); con=md.get('consensus') or {}
    if sid not in sgn or con.get('forecast') is None or con.get('actual') is None or md.get('releaseDateApproximate') is True: continue
    try: a=float(con['actual']); f=float(con['forecast'])
    except: continue
    dt=md.get('releaseDate') or e.get('createdAt');
    if not dt: continue
    d=pd.to_datetime(dt,utc=True).tz_convert(None).normalize(); diff=a-f; sign=0 if diff==0 else int(np.sign(diff))*sgn[sid]; er.append([d,sid,a,f,sign,'fred-us-macro-open-data'])
# exact 2026-04-30 Core PCE YoY: 3.2 actual vs 3.15 consensus; adverse-gold surprise.
er.append([pd.Timestamp('2026-04-30'),'PCEPILFE',3.2,3.15,-1,'forex.tradingcharts.com/economic_calendar/2026-04-30'])
E=pd.DataFrame(er,columns=['date','series','actual','forecast','gold_sign','source']).drop_duplicates(['date','series'],keep='last'); A=E.groupby('date').agg(macro_score=('gold_sign','sum'),macro_series=('series',lambda x:';'.join(x))).reset_index()
D=D.merge(A,on='date',how='left'); D['macro_score']=D.macro_score.fillna(0).astype(int); D['macro_series']=D.macro_series.fillna('')
D['event_down']=(D.macro_score<=-1)&(D.fast==-1)&(D.ret<=-.005)

# locked BOCPD-return alarms, risk context only (no execution authority)
BOCPD_ALARMS={'2026-03','2026-04','2026-06'}
D['bocpd_alarm_month']=D.month.isin(BOCPD_ALARMS)

# continuous LONG/CASH state. Close-t action affects next bar. Tactical/GVZ/BOCPD are evidence only.
X=D[(D.date>='2026-01-01')&(D.date<=CUTOFF)].copy(); cur=0; last_month=None; pos=[]; acts=[]; reasons=[]; evidence=[]
for _,r in X.iterrows():
    p=int(r.prior); m=r.month; new=cur; reason='HOLD'
    if last_month is None:
        new=1 if p==1 else 0; reason='INITIAL_MONTHLY_ANCHOR'
    elif m!=last_month:
        base=1 if p==1 else 0
        if base!=cur: new=base; reason='MONTHLY_ORIGIN_REEVALUATION'
    # frozen intramonth overrides have priority after monthly origin evaluation
    if p==1 and bool(r.event_down): new=0; reason='MACRO_EVENT_DOWN'
    elif p==1 and bool(r.price_emg_down): new=0; reason='PRICE_EMERGENCY_DOWN'
    elif p==-1 and bool(r.price_emg_up): new=1; reason='PRICE_EMERGENCY_UP'
    action='TUT' if new==cur else ('AL' if new else 'SAT'); cur=new; last_month=m
    if bool(r.event_down): ev='MACRO_EVENT_REVERSAL_DOWN'
    elif bool(r.price_emg_down): ev='PRICE_SHOCK_DOWN'
    elif bool(r.price_emg_up): ev='PRICE_SHOCK_UP'
    elif r.fast==-p and r.slow==-p and p!=0: ev='TACTICAL_REVERSAL_CONFIRMED'
    elif r.fast==-p and p!=0: ev='TACTICAL_EARLY_REVERSAL'
    elif r.fast==p and r.slow==p and p!=0: ev='ANCHOR_CONFIRMED'
    else: ev='MIXED_NEUTRAL'
    pos.append(cur); acts.append(action); reasons.append(reason); evidence.append(ev)
X['pos']=pos; X['action']=acts; X['reason']=reasons; X['evidence']=evidence; X['turn']=X.pos.diff().abs().fillna(0)
# initial AL is a real position change from CASH and pays 10bp
if len(X) and X.action.iloc[0]=='AL': X.loc[X.index[0],'turn']=1
X['strat_ret']=X.pos.shift(1).fillna(0)*X.ret.fillna(0)-.001*X.turn; X['equity']=(1+X.strat_ret).cumprod(); X['bh_ret']=X.ret.fillna(0); X['bh_equity']=(1+X.bh_ret).cumprod()
X.to_csv(OUT/'FULL_ENGINE_2026_R4_DAILY.csv',index=False); X[X.action!='TUT'].to_csv(OUT/'FULL_ENGINE_2026_R4_TRADES.csv',index=False)
# material signal changes
X['material']=(X.action!='TUT')|(X.evidence!=X.evidence.shift(1))|X.event_down|X.price_emg_down|X.price_emg_up|X.gvz_stress
X[X.material].to_csv(OUT/'FULL_ENGINE_2026_R4_SIGNAL_DAYS.csv',index=False)
X[['date','GVZ','gvz_q90_252','gvz_stress']].to_csv(OUT/'GVZ_2026_R4_SNAPSHOT.csv',index=False); E[(E.date>='2026-01-01')&(E.date<='2026-04-30')].to_csv(OUT/'MACRO_EVENT_2026_R4_SNAPSHOT.csv',index=False)

# metrics and monthly table
net=float(X.equity.iloc[-1]-1); mdd=float((X.equity/X.equity.cummax()-1).min()); turns=int(X.turn.sum()); bh=float(X.close.iloc[-1]/X.close.iloc[0]-1)
monthly=[]
for m,q in X.groupby('month'):
    tr='; '.join(f"{r.date.date()} {r.action}({r.reason})" for _,r in q[q.action!='TUT'].iterrows()) or '-'
    actual=origin_actual.get(m,np.nan); monthly.append([m,int(q.prior.iloc[0]),actual,gate_pick.get(m,'AUG_CONTEXT'),gate_fc.get(m,np.nan),float(q.close.iloc[-1]),int(q.pos.iloc[-1]),tr])
M=pd.DataFrame(monthly,columns=['month','mom3_prior','actual_dir_completed','main_model_context','monthly_forecast','last_daily_close','end_pos','actions']); M.to_csv(OUT/'FULL_ENGINE_2026_R4_MONTHLY.csv',index=False)

lines=['# GOLD H1 R1 — Full Daily Investment Engine 2026 R4','',
'## Contract','- Replay window: 2026-01-01 through latest completed D1 bar 2026-08-28; Aug-30 is Sunday, so no synthetic weekend price is created.','- D1 source lock: simom1/XAUUSD-history@'+D1_PIN+'.','- Position is continuous LONG/CASH; 10bp per position change; close-t action applies from next bar.','- Monthly price forecasts are monthly-average anchors/context, never daily targets.','- 2026 outcomes are NOT used to select/tune any execution threshold.','- Fast/Slow, GVZ and BOCPD remain evidence/risk context only.','- Execution-authorized intramonth rules were frozen pre-2023: Price Emergency DOWN/UP and Macro Event DOWN.','- Macro Event UP remains context-only/rejected.','',
f'- YTD net return: {net:.4%}',f'- YTD MDD: {mdd:.4%}',f'- Position changes: {turns}',f'- D1 close-to-close buy&hold comparator: {bh:.4%}',f'- Current position at 2026-08-28 close: {"LONG" if X.pos.iloc[-1] else "CASH"}',f'- Current close: {X.close.iloc[-1]:.2f}',f'- August 3M monthly-average forecast: {aug_mom:.2f} (DOWN from July 4073)','',
'## August main price experts']
if aug:
    for k in ['rw','3m_momentum','vw_midas_msvr','causal_patch_transformer']: lines.append(f'- {k}: {aug.get(k)}')
else: lines.append('- AUGUST_FULL_EXPERT_FORECAST=BLOCKED_NOT_GENERATED')
lines+=['','## Trades','|Date|Close|Action|Reason|Prior|Fast|Slow|GVZ|Evidence|','|---|---:|---|---|---:|---:|---:|---:|---|']
for _,r in X[X.action!='TUT'].iterrows(): lines.append(f'|{r.date.date()}|{r.close:.2f}|{r.action}|{r.reason}|{int(r.prior):+d}|{int(r.fast):+d}|{int(r.slow):+d}|{r.GVZ:.2f}|{r.evidence}|')
lines+=['','## Monthly','|Month|3M prior|Actual completed|Main forecast context|Forecast|End pos|Actions|','|---|---:|---:|---|---:|---|---|']
for _,r in M.iterrows(): lines.append(f'|{r.month}|{int(r.mom3_prior):+d}|{r.actual_dir_completed if pd.notna(r.actual_dir_completed) else "PARTIAL"}|{r.main_model_context}|{r.monthly_forecast if pd.notna(r.monthly_forecast) else "see expert block"}|{"LONG" if r.end_pos else "CASH"}|{r.actions}|')
lines+=['','## Source/authority status','- GVZ: official Cboe daily history; non-directional.','- Macro actual/consensus through Apr-26: pinned fred-us-macro-open-data@'+MACRO_PIN+'; Apr-30 Core PCE exact calendar evidence appended. After May-1 the monthly prior is DOWN, so the authorized Macro Event DOWN rule is not execution-eligible; missing later consensus history therefore cannot change R4 execution.','- August target month is incomplete. August actual monthly direction is NOT scored. Daily execution through Aug-28 is current-state replay.','- 2026 hierarchy that fixed Apr diagnostically remains DIAGNOSTIC_ONLY and is not granted execution authority after seeing 2026.']
(OUT/'FULL_ENGINE_2026_R4_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines))
