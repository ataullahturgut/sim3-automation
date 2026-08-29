#!/usr/bin/env python3
import io, urllib.request, time
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1'); PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
URL=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
def read(url):
  for k in range(5):
    try:
      req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1'})
      with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))
    except Exception:
      if k==4: raise
      time.sleep(2*(k+1))
# Daily price
D=read(URL); D['date']=pd.to_datetime(D['time']); D=D[['date','open','high','low','close']].sort_values('date').drop_duplicates('date')
D['month']=D.date.dt.to_period('M').astype(str)
D['ret']=D.close.pct_change(); D['sma20']=D.close.rolling(20).mean(); D['fast_raw']=np.sign(D.close-D.sma20)
# fast persistence 2 market days
fr=D.fast_raw.to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
  if np.isfinite(fr[i]) and fr[i]!=0 and fr[i]==fr[i-1]: fast[i]=int(fr[i])
D['fast']=fast
# Weekly bars, Sunday-Friday MT5 contract. completed-week state becomes known only after that week closes.
wd=D.copy(); wd['wk_start']=(wd.date-pd.to_timedelta((wd.date.dt.weekday+1)%7,unit='D')).dt.normalize()
W=wd.groupby('wk_start').agg(wclose=('close','last')).reset_index().sort_values('wk_start')
W['sma4']=W.wclose.rolling(4).mean(); W['raw']=np.sign(W.wclose-W.sma4); wr=W.raw.to_numpy(); slow=np.zeros(len(W),int)
for i in range(1,len(W)):
  if np.isfinite(wr[i]) and wr[i]!=0 and wr[i]==wr[i-1]: slow[i]=int(wr[i])
W['slow']=slow; W['known_date']=W.wk_start+pd.Timedelta(days=6)
D=pd.merge_asof(D.sort_values('date'),W[['known_date','slow']].rename(columns={'known_date':'date'}).sort_values('date'),on='date',direction='backward'); D['slow']=D.slow.fillna(0).astype(int)
# Monthly 3M prior history, origin-safe
M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); M['target']=pd.to_datetime(M.target).dt.to_period('M').astype(str); prior=dict(zip(M.target,M.dir3.astype(int)))
D['prior']=D.month.map(prior).fillna(0).astype(int)
# Candidate execution policies, all causal. Position is long=1/cash=0. No shorting.
# monthly: follow monthly prior throughout.
# fast: daily fast may override prior.
# slow: weekly slow may override prior.
# dual: change from prior only when fast+slow agree opposite; return to prior when fast+slow agree with prior.
# dual2: same as dual but opposite agreement must persist 2 consecutive market days.
def make_pos(df,policy):
  pos=[]; cur=None; opp_count=0
  last_month=None
  for _,r in df.iterrows():
    p=int(r.prior); f=int(r.fast); s=int(r.slow); m=r.month
    base=1 if p==1 else 0
    if m!=last_month: cur=base; opp_count=0; last_month=m
    if policy=='monthly': cur=base
    elif policy=='fast':
      if f==1: cur=1
      elif f==-1: cur=0
    elif policy=='slow':
      if s==1: cur=1
      elif s==-1: cur=0
    elif policy in ('dual','dual2'):
      opp=(f!=0 and s!=0 and f==s and f==-p)
      same=(f!=0 and s!=0 and f==s and f==p)
      if opp: opp_count+=1
      else: opp_count=0
      need=1 if policy=='dual' else 2
      if opp_count>=need: cur=1 if f==1 else 0
      elif same: cur=base
    pos.append(cur)
  return pd.Series(pos,index=df.index,dtype=int)
def eval_policy(policy,a,b,cost=.001):
  x=D[(D.date>=pd.Timestamp(a))&(D.date<=pd.Timestamp(b))].copy(); x['pos']=make_pos(x,policy); x['turn']=x.pos.diff().abs().fillna(0); x['strat_ret']=x.pos.shift(1).fillna(x.pos.iloc[0])*x.ret.fillna(0)-cost*x.turn
  eq=(1+x.strat_ret).cumprod(); net=eq.iloc[-1]-1; dd=(eq/eq.cummax()-1).min(); trades=int(x.turn.sum()); return net,dd,trades
policies=['monthly','fast','slow','dual','dual2']; rows=[]
for p in policies:
  for name,a,b in [('DEV','2010-01-01','2020-12-31'),('VAL','2021-01-01','2022-12-31'),('TEST2023','2023-01-01','2023-12-31')]:
    net,dd,tr=eval_policy(p,a,b); rows.append([p,name,net,dd,tr])
S=pd.DataFrame(rows,columns=['policy','period','net_return','mdd','trades']); S.to_csv(OUT/'INTRAMONTH_2023_POLICY_SCORECARD.csv',index=False)
# Choose pre-2023 only: require positive DEV and VAL improvement vs monthly in utility net + 0.5*mdd (mdd negative, so penalizes drawdown), then maximize VAL utility, tie DEV.
def util(r): return r.net_return+0.5*r.mdd
pv=S.pivot(index='policy',columns='period',values=['net_return','mdd','trades'])
base_dev=util(S[(S.policy=='monthly')&(S.period=='DEV')].iloc[0]); base_val=util(S[(S.policy=='monthly')&(S.period=='VAL')].iloc[0])
cands=[]
for p in policies:
  dr=S[(S.policy==p)&(S.period=='DEV')].iloc[0]; vr=S[(S.policy==p)&(S.period=='VAL')].iloc[0]
  if p=='monthly' or (util(dr)>=base_dev and util(vr)>=base_val): cands.append((util(vr),util(dr),-vr.trades,p))
chosen=max(cands)[-1]
# 2023 detailed replay under chosen policy
X=D[(D.date>='2023-01-01')&(D.date<='2023-12-31')].copy(); X['pos']=make_pos(X,chosen); X['turn']=X.pos.diff().abs().fillna(0); X['strat_ret']=X.pos.shift(1).fillna(X.pos.iloc[0])*X.ret.fillna(0)-.001*X.turn
X['equity']=(1+X.strat_ret).cumprod(); X.to_csv(OUT/'INTRAMONTH_2023_DAILY_REPLAY.csv',index=False)
# monthly summaries and trade actions
mrs=[]
for m,g in X.groupby('month'):
  prior0=int(g.prior.iloc[0]); pos0=int(g.pos.iloc[0]); posend=int(g.pos.iloc[-1]); net=float((1+g.strat_ret).prod()-1); bh=float(g.close.iloc[-1]/g.close.iloc[0]-1); turns=int(g.turn.sum())
  dates=g.loc[g.turn>0,['date','pos']]
  actions='; '.join(f"{d.date().isoformat()} {'AL' if p==1 else 'SAT'}" for d,p in zip(dates.date,dates.pos)) or '-'
  first_change='' if dates.empty else dates.date.iloc[0].date().isoformat()
  mrs.append([m,prior0,pos0,posend,net,bh,turns,first_change,actions])
R=pd.DataFrame(mrs,columns=['month','monthly_prior','start_pos','end_pos','strategy_return','buyhold_return','trades','first_change','actions']); R.to_csv(OUT/'INTRAMONTH_2023_MONTHLY_RESULTS.csv',index=False)
# yearly metrics
net=float(X.equity.iloc[-1]-1); mdd=float((X.equity/X.equity.cummax()-1).min()); trades=int(X.turn.sum()); bh=float(X.close.iloc[-1]/X.close.iloc[0]-1)
# baseline monthly policy 2023 exact
bn,bd,bt=eval_policy('monthly','2023-01-01','2023-12-31')
lines=['# GOLD H1 R1 — 2023 Intramonth Trading Replay','',f'Chosen policy (selected only on 2010-2022): **{chosen}**.','',f'- 2023 strategy net return (10 bp per position change): {net:.2%}',f'- 2023 max drawdown: {mdd:.2%}',f'- 2023 position changes: {trades}',f'- Buy-and-hold close-to-close: {bh:.2%}',f'- Monthly-prior-only net return: {bn:.2%}',f'- Monthly-prior-only MDD: {bd:.2%}',f'- Monthly-prior-only position changes: {bt}','','## Monthly results','|Month|Prior|End pos|Strategy|Buy&Hold|Trades|First change|Actions|','|---|---:|---:|---:|---:|---:|---|---|']
for _,r in R.iterrows(): lines.append(f"|{r.month}|{r.monthly_prior:+d}|{'LONG' if r.end_pos==1 else 'CASH'}|{r.strategy_return:.2%}|{r.buyhold_return:.2%}|{int(r.trades)}|{r.first_change or '-'}|{r.actions}|")
lines+=['','## Policy scorecard (selection periods only)','|Policy|DEV net|DEV MDD|VAL net|VAL MDD|2023 net|2023 MDD|','|---|---:|---:|---:|---:|---:|---:|']
for p in policies:
  z=S[S.policy==p].set_index('period'); lines.append(f"|{p}|{z.loc['DEV','net_return']:.2%}|{z.loc['DEV','mdd']:.2%}|{z.loc['VAL','net_return']:.2%}|{z.loc['VAL','mdd']:.2%}|{z.loc['TEST2023','net_return']:.2%}|{z.loc['TEST2023','mdd']:.2%}|")
lines+=['','## Contract','- 2023 is never used to select the execution policy.','- Monthly prior is the existing 3M direction layer.','- Fast Tactical = daily close vs SMA20 with 2-market-day persistence.','- Slow Tactical = completed Sunday-Friday weekly close vs SMA4 with 2-completed-week persistence.','- Direction takers update position only after signals are observable.','- Long/cash only; no shorting.','- Transaction cost = 10 bp per position change.']
(OUT/'INTRAMONTH_2023_REPORT.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
