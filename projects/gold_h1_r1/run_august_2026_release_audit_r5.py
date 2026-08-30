#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
PIN='a33d38a29cc84aa0cd641ae07bee80874a6cfb7b'
URL=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'

def read(url):
    req=urllib.request.Request(url,headers={'User-Agent':'gold-r5-release-audit/1.0'})
    with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))

D=read(URL); D['date']=pd.to_datetime(D.time); D=D[['date','close']].sort_values('date').drop_duplicates('date')
D['month']=D.date.dt.to_period('M').astype(str); D['ret']=D.close.pct_change(); D['ret5']=D.close.pct_change(5); D['sma20']=D.close.rolling(20).mean(); D['sma50']=D.close.rolling(50).mean()
raw=np.sign(D.close-D.sma20).to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
    if np.isfinite(raw[i]) and raw[i]!=0 and raw[i]==raw[i-1]: fast[i]=int(raw[i])
D['fast']=fast; D['mtd_peak']=D.groupby('month').close.cummax(); D['mtd_trough']=D.groupby('month').close.cummin(); D['mtd_dd']=D.close/D.mtd_peak-1; D['mtd_up']=D.close/D.mtd_trough-1
# exact R4 frozen price emergencies
D['down_emg']=(D.mtd_dd<=-.03)&(D.ret5<=-.04)&(D.close<D.sma50)
D['up_emg']=(D.mtd_up>=.03)&(D.ret5>=.02)&(D.close>D.sma50)

M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); M['month']=pd.to_datetime(M.target).dt.to_period('M').astype(str); hist_prior=dict(zip(M.month,M.dir3.astype(int)))
T=pd.read_csv(OUT/'tactical_origin_2026_jan_jul.csv'); p26={r.target:int(r.mom3_dir) for _,r in T.iterrows()}; p26['2026-08']=-1

def simulate(df,priors,k=None):
    x=df.copy(); x['prior']=x.month.map(priors).fillna(0).astype(int); x=x[x.prior!=0].copy()
    cur=None; lastm=None; override=False; align_streak=0; pos=[]; action=[]; reason=[]
    for _,r in x.iterrows():
        p=int(r.prior); base=1 if p==1 else 0; new=cur; rs='HOLD'
        if cur is None: new=base; rs='INITIAL_BASE'
        elif r.month!=lastm: new=base; override=False; align_streak=0; rs='MONTHLY_BASE'
        # exact emergency entry/exit against base prior
        if p==1 and bool(r.down_emg): new=0; override=True; align_streak=0; rs='EMERGENCY_DOWN'
        elif p==-1 and bool(r.up_emg): new=1; override=True; align_streak=0; rs='EMERGENCY_UP'
        elif override and k is not None:
            # state-consistent opposite emergency immediately releases to base
            opposite=(new==1 and bool(r.down_emg)) or (new==0 and bool(r.up_emg))
            if opposite:
                new=base; override=False; align_streak=0; rs='OPPOSITE_EMERGENCY_RELEASE'
            else:
                active=(p==-1 and bool(r.up_emg)) or (p==1 and bool(r.down_emg))
                aligned=(int(r.fast)==p and int(r.fast)!=0)
                align_streak=(align_streak+1) if (not active and aligned) else 0
                if align_streak>=k:
                    new=base; override=False; align_streak=0; rs=f'FAST_BASE_RELEASE_K{k}'
        a='TUT' if new==cur else ('AL' if new==1 else 'SAT')
        cur=new; lastm=r.month; pos.append(cur); action.append(a); reason.append(rs)
    x['pos']=pos; x['action']=action; x['reason']=reason; x['turn']=x.pos.diff().abs().fillna(0)
    if len(x) and x.action.iloc[0] in ('AL','SAT'): x.loc[x.index[0],'turn']=abs(float(x.pos.iloc[0]))
    x['strat_ret']=x.pos.shift(1).fillna(0)*x.ret.fillna(0)-.001*x.turn; x['eq']=(1+x.strat_ret).cumprod()
    return x

def metrics(x):
    net=float(x.eq.iloc[-1]-1); mdd=float((x.eq/x.eq.cummax()-1).min()); turns=int(x.turn.sum()); return net,mdd,turns

def period(a,b,k): return simulate(D[(D.date>=a)&(D.date<=b)],hist_prior,k)
base_dev=period('2010-01-01','2020-12-31',None); base_val=period('2021-01-01','2022-12-31',None); bd=metrics(base_dev); bv=metrics(base_val)
rows=[]
for k in [1,2,3,5]:
    dv=metrics(period('2010-01-01','2020-12-31',k)); vl=metrics(period('2021-01-01','2022-12-31',k))
    dominates=(dv[0]>=bd[0]-.02 and dv[1]>=bd[1]-.01 and vl[0]>=bv[0] and vl[1]>=bv[1])
    rows.append([k,*dv,*vl,dominates])
A=pd.DataFrame(rows,columns=['release_k','dev_net','dev_mdd','dev_turns','val_net','val_mdd','val_turns','dominates_baseline'])
A.loc[len(A)]=[0,*bd,*bv,False]; A.to_csv(OUT/'AUGUST_2026_R5_RELEASE_AUDIT.csv',index=False)
elig=A[A.dominates_baseline==True].copy(); approved=len(elig)>0
best_k=int(elig.sort_values(['val_net','val_mdd','dev_net'],ascending=False).iloc[0].release_k) if approved else None
# 2026/August challenger uses only a pre-2023-approved release; otherwise R4 state is retained.
X=simulate(D[(D.date>='2026-01-01')&(D.date<='2026-08-28')],p26,best_k if approved else None)
Aug=X[X.month=='2026-08'].copy(); Aug.to_csv(OUT/'AUGUST_2026_R5_DAY_BY_DAY.csv',index=False)
lines=['# August 2026 R5 Release Audit','',f'RELEASE_STATUS={"APPROVED" if approved else "NOT_PROVEN"}',f'SELECTED_K={best_k if approved else "NONE"}','',f'Baseline DEV net={bd[0]:.4%}, MDD={bd[1]:.4%}; VAL net={bv[0]:.4%}, MDD={bv[1]:.4%}.','', 'Candidate release is allowed only if it dominates baseline on VAL net and MDD while DEV deterioration stays within 2pp net / 1pp MDD.','', '## August decisions']
for _,r in Aug.iterrows(): lines.append(f"- {r.date.date()} close={r.close:.2f} fast={int(r.fast):+d} prior={int(r.prior):+d} up={bool(r.up_emg)} down={bool(r.down_emg)} pos={'LONG' if r.pos else 'CASH'} action={r.action} reason={r.reason}")
(OUT/'AUGUST_2026_R5_RELEASE_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
