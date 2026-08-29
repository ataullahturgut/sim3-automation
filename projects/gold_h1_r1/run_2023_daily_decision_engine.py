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
D=read(URL); D['date']=pd.to_datetime(D['time']); D=D[['date','open','high','low','close']].sort_values('date').drop_duplicates('date')
D['month']=D.date.dt.to_period('M').astype(str); D['ret']=D.close.pct_change(); D['sma20']=D.close.rolling(20).mean(); D['sma50']=D.close.rolling(50).mean(); D['fast_raw']=np.sign(D.close-D.sma20)
fr=D.fast_raw.to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
  if np.isfinite(fr[i]) and fr[i]!=0 and fr[i]==fr[i-1]: fast[i]=int(fr[i])
D['fast']=fast
wd=D.copy(); wd['wk_start']=(wd.date-pd.to_timedelta((wd.date.dt.weekday+1)%7,unit='D')).dt.normalize(); W=wd.groupby('wk_start').agg(wclose=('close','last')).reset_index().sort_values('wk_start'); W['sma4']=W.wclose.rolling(4).mean(); W['raw']=np.sign(W.wclose-W.sma4); wr=W.raw.to_numpy(); slow=np.zeros(len(W),int)
for i in range(1,len(W)):
  if np.isfinite(wr[i]) and wr[i]!=0 and wr[i]==wr[i-1]: slow[i]=int(wr[i])
W['slow']=slow; W['known_date']=W.wk_start+pd.Timedelta(days=6)
D=pd.merge_asof(D.sort_values('date'),W[['known_date','slow']].rename(columns={'known_date':'date'}).sort_values('date'),on='date',direction='backward'); D['slow']=D.slow.fillna(0).astype(int)
M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); M['target']=pd.to_datetime(M.target).dt.to_period('M').astype(str); M=M.sort_values('target'); M['mom1']=M.actual_dir.shift(1).fillna(0).astype(int); prior=dict(zip(M.target,M.dir3.astype(int))); mom1=dict(zip(M.target,M.mom1.astype(int)))
D['prior']=D.month.map(prior).fillna(0).astype(int); D['mom1']=D.month.map(mom1).fillna(0).astype(int)
D['mtd_peak']=D.groupby('month').close.cummax(); D['mtd_trough']=D.groupby('month').close.cummin(); D['mtd_dd']=D.close/D.mtd_peak-1; D['mtd_rally']=D.close/D.mtd_trough-1; D['ret5']=D.close.pct_change(5)
# frozen emergency rules: downside existing R1; upside pre-2023 frozen from prior audit
D['down_emg']=(D.mtd_dd<=-.03)&(D.ret5<=-.04)&(D.close<D.sma50)
D['up_emg']=(D.mtd_rally>=.03)&(D.ret5>=.02)&(D.close>D.sma50)
# candidate daily decision policies, selected only on 2010-2022
# score = opposite votes among MOM1/Fast/Slow versus monthly prior; emergency always overrides.
def run_policy(df,k=3,persist=2,release=2):
  pos=[]; decision=[]; cur=None; opp_streak=same_streak=0; lastm=None
  for _,r in df.iterrows():
    p=int(r.prior); base=1 if p==1 else 0; m=r.month
    if m!=lastm: cur=base; opp_streak=same_streak=0; lastm=m
    votes=[int(r.mom1),int(r.fast),int(r.slow)]; opp=sum(v!=0 and v==-p for v in votes); same=sum(v!=0 and v==p for v in votes)
    if p==1 and bool(r.down_emg): new=0; reason='EMERGENCY_DOWN'
    elif p==-1 and bool(r.up_emg): new=1; reason='EMERGENCY_UP'
    else:
      opp_streak=opp_streak+1 if opp>=k else 0; same_streak=same_streak+1 if same>=release else 0; new=cur; reason='HOLD'
      if opp_streak>=persist: new=1-base; reason='REVERSAL_CONSENSUS'
      elif same_streak>=persist: new=base; reason='RETURN_PRIOR'
    if cur is None: cur=base
    action='TUT' if new==cur else ('AL' if new==1 else 'SAT'); cur=new; pos.append(cur); decision.append((action,reason,opp,same))
  out=df.copy(); out['pos']=pos; out['action']=[x[0] for x in decision]; out['reason']=[x[1] for x in decision]; out['opp_votes']=[x[2] for x in decision]; out['same_votes']=[x[3] for x in decision]; out['turn']=out.pos.diff().abs().fillna(0); out['strat_ret']=out.pos.shift(1).fillna(out.pos.iloc[0])*out.ret.fillna(0)-.001*out.turn; out['equity']=(1+out.strat_ret).cumprod(); return out
def metrics(x):
  net=float(x.equity.iloc[-1]-1); mdd=float((x.equity/x.equity.cummax()-1).min()); trades=int(x.turn.sum()); return net,mdd,trades
cands=[]
for k in [2,3]:
  for persist in [1,2,3]:
    for release in [2,3]:
      a=run_policy(D[(D.date>='2010-01-01')&(D.date<='2020-12-31')],k,persist,release); b=run_policy(D[(D.date>='2021-01-01')&(D.date<='2022-12-31')],k,persist,release); dn,dd,dt=metrics(a); vn,vd,vt=metrics(b); utilv=vn+0.5*vd; utild=dn+0.5*dd; cands.append((utilv,utild,-vt,k,persist,release,dn,dd,vn,vd))
# monthly baseline candidate included implicitly by impossible threshold via k=4
a=run_policy(D[(D.date>='2010-01-01')&(D.date<='2020-12-31')],4,99,3); b=run_policy(D[(D.date>='2021-01-01')&(D.date<='2022-12-31')],4,99,3); dn,dd,dt=metrics(a); vn,vd,vt=metrics(b); cands.append((vn+0.5*vd,dn+0.5*dd,-vt,4,99,3,dn,dd,vn,vd))
chosen=max(cands); _,_,_,k,persist,release,*_=chosen
X=run_policy(D[(D.date>='2023-01-01')&(D.date<='2023-12-31')],k,persist,release); X.to_csv(OUT/'DAILY_DECISION_2023_REPLAY.csv',index=False)
# summarize action events and monthly stats
E=X[X.action!='TUT'][['date','month','close','prior','mom1','fast','slow','opp_votes','same_votes','action','reason']].copy(); E.to_csv(OUT/'DAILY_DECISION_2023_ACTIONS.csv',index=False)
rows=[]
for m,g in X.groupby('month'):
  net=float((1+g.strat_ret).prod()-1); bh=float(g.close.iloc[-1]/g.close.iloc[0]-1); events=g[g.action!='TUT']; actions='; '.join(f"{r.date.date()} {r.action}({r.reason})" for _,r in events.iterrows()) or '-'; rows.append([m,int(g.prior.iloc[0]),int(g.pos.iloc[-1]),net,bh,int(g.turn.sum()),actions])
R=pd.DataFrame(rows,columns=['month','prior','end_pos','strategy_return','buyhold_return','trades','actions']); R.to_csv(OUT/'DAILY_DECISION_2023_MONTHLY.csv',index=False)
net,mdd,tr=metrics(X); bh=float(X.close.iloc[-1]/X.close.iloc[0]-1)
lines=['# GOLD H1 R1 — 2023 Full Daily Decision Engine','',f'Frozen policy selected only on 2010-2022: opposite-vote threshold={k}, persistence={persist}, release={release}.','Daily engine evaluates every available D1 bar and emits AL/TUT/SAT. Monthly prior is not recomputed intramonth; Tactical and Emergency are.','',f'- 2023 net return (10 bp/change): {net:.2%}',f'- 2023 MDD: {mdd:.2%}',f'- Position changes: {tr}',f'- Buy&Hold close-to-close: {bh:.2%}','','## Action events','|Date|Action|Reason|Prior|MOM1|Fast|Slow|','|---|---|---|---:|---:|---:|---:|']
for _,r in E.iterrows(): lines.append(f"|{r.date.date()}|{r.action}|{r.reason}|{r.prior:+d}|{r.mom1:+d}|{r.fast:+d}|{r.slow:+d}|")
lines+=['','## Monthly','|Month|Prior|End|Strategy|BuyHold|Trades|Actions|','|---|---:|---|---:|---:|---:|---|']
for _,r in R.iterrows(): lines.append(f"|{r.month}|{r.prior:+d}|{'LONG' if r.end_pos==1 else 'CASH'}|{r.strategy_return:.2%}|{r.buyhold_return:.2%}|{int(r.trades)}|{r.actions}|")
lines+=['','## Contract','- 2023 outcomes are not used for policy selection.','- Daily Fast Tactical is recomputed every D1 bar; Slow Tactical updates only after a completed Sunday-Friday week.','- MOM1 is known at month origin from prior completed month.','- Emergency rules are frozen pre-2023.','- Long/cash only; 10 bp per position change.','- VW remains level/secondary monthly context; exact pre-2023 VW execution history is not reproducible, so it is not used to tune the daily state machine.']
(OUT/'DAILY_DECISION_2023_REPORT.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
