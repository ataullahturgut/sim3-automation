#!/usr/bin/env python3
# GOLD H1 R1 — unified 2023 daily investment replay.
# Contract: no 2023 outcome is used for tuning. Continuous state across month boundaries.
# Monthly level forecasts are TARGET-MONTH AVERAGE anchors, never treated as daily-price targets.
import io, urllib.request, time
from pathlib import Path
import numpy as np, pandas as pd

OUT=Path('projects/gold_h1_r1')
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
GOLD=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'

def read_url(url):
    err=None
    for k in range(5):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-unified/2.0'})
            with urllib.request.urlopen(req,timeout=180) as r:
                return pd.read_csv(io.BytesIO(r.read()))
        except Exception as e:
            err=e; time.sleep(2*(k+1))
    raise err

def fred(series):
    d=read_url(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2009-01-01&coed=2023-12-31')
    d.columns=['date',series]; d['date']=pd.to_datetime(d.date); d[series]=pd.to_numeric(d[series],errors='coerce')
    return d.dropna()

# ---------- Daily gold + origin-safe market/risk context ----------
D=read_url(GOLD)
D['date']=pd.to_datetime(D['time'])
D=D[['date','open','high','low','close']].sort_values('date').drop_duplicates('date')
for s in ['VIXCLS','DTWEXBGS','DFII10','GVZCLS']:
    try:
        D=pd.merge_asof(D.sort_values('date'),fred(s).sort_values('date'),on='date',direction='backward',tolerance=pd.Timedelta('7D'))
    except Exception:
        D[s]=np.nan
D['month']=D.date.dt.to_period('M').astype(str)
D['ret']=D.close.pct_change(); D['ret5']=D.close.pct_change(5)
D['sma20']=D.close.rolling(20).mean(); D['sma50']=D.close.rolling(50).mean()
D['fast_raw']=np.sign(D.close-D.sma20)
fr=D.fast_raw.to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
    if np.isfinite(fr[i]) and fr[i]!=0 and fr[i]==fr[i-1]: fast[i]=int(fr[i])
D['fast']=fast

# Tactical Slow: completed Sunday-Friday week, persistent two completed weeks.
wd=D[['date','close']].copy()
wd['wk_start']=(wd.date-pd.to_timedelta((wd.date.dt.weekday+1)%7,unit='D')).dt.normalize()
W=wd.groupby('wk_start').agg(wclose=('close','last')).reset_index().sort_values('wk_start')
W['sma4']=W.wclose.rolling(4).mean(); W['raw']=np.sign(W.wclose-W.sma4)
wr=W.raw.to_numpy(); slow=np.zeros(len(W),int)
for i in range(1,len(W)):
    if np.isfinite(wr[i]) and wr[i]!=0 and wr[i]==wr[i-1]: slow[i]=int(wr[i])
W['slow']=slow; W['known_date']=W.wk_start+pd.Timedelta(days=6)
D=pd.merge_asof(D.sort_values('date'),W[['known_date','slow']].rename(columns={'known_date':'date'}).sort_values('date'),on='date',direction='backward')
D['slow']=D.slow.fillna(0).astype(int)

# ---------- Monthly direction prior and MOM1 ----------
M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv')
M['target']=pd.to_datetime(M.target).dt.to_period('M').astype(str); M=M.sort_values('target')
M['mom1']=M.actual_dir.shift(1).fillna(0).astype(int)
prior=dict(zip(M.target,M.dir3.astype(int))); mom1=dict(zip(M.target,M.mom1.astype(int)))
D['prior']=D.month.map(prior).fillna(0).astype(int); D['mom1']=D.month.map(mom1).fillna(0).astype(int)

# ---------- Monthly price-level forecast anchors (2023 archived, origin-safe) ----------
A=pd.read_csv(OUT/'autopsy_2023_direction.csv')
A=A[['month','origin_gold','mom3_forecast','vw_forecast','patch_forecast','idma_forecast','vw_dir','patch_dir','idma_dir']].copy()
D=D.merge(A,on='month',how='left')
D['level_median']=D[['mom3_forecast','vw_forecast','patch_forecast','idma_forecast']].median(axis=1)
# Diagnostic only. Monthly-average forecasts must NOT generate a daily trade by themselves.
D['level_gap_pct']=D.close/D.level_median-1

# ---------- Intramonth fracture features ----------
D['mtd_peak']=D.groupby('month').close.cummax(); D['mtd_trough']=D.groupby('month').close.cummin()
D['mtd_dd']=D.close/D.mtd_peak-1; D['mtd_up']=D.close/D.mtd_trough-1
D['vix5']=D.VIXCLS/D.VIXCLS.shift(5)-1
D['usd5']=D.DTWEXBGS/D.DTWEXBGS.shift(5)-1
D['ry5']=D.DFII10-D.DFII10.shift(5)
D['gvz5']=D.GVZCLS/D.GVZCLS.shift(5)-1
# GVZ is non-directional volatility context. Stress threshold is trailing-history percentile, not 2023-tuned.
D['gvz_q90_252']=D.GVZCLS.shift(1).rolling(252,min_periods=126).quantile(.90)
D['gvz_stress']=(D.GVZCLS>=D.gvz_q90_252).fillna(False)

# ---------- Bidirectional emergency: select/freeze ONLY on DEV 2010-20 + VAL 2021-22 ----------
def shock_signal(d,side,move,r5,stress):
    if side=='DOWN':
        base=(d.mtd_dd<=-move)&(d.ret5<=-r5)&(d.close<d.sma50)
        macro=(d.usd5>0)|(d.ry5>0)
    else:
        base=(d.mtd_up>=move)&(d.ret5>=r5)&(d.close>d.sma50)
        macro=(d.usd5<0)|(d.ry5<0)
    if stress=='NONE': return base
    if stress=='MACRO': return base&macro
    if stress=='VIX_OR_MACRO': return base&((d.vix5>=.10)|macro)
    return base
CANDS=[(mv,r5,st) for mv in [.03,.05,.07] for r5 in [.02,.04,.06] for st in ['NONE','MACRO','VIX_OR_MACRO']]
MM=M[~M.flat.astype(bool)].copy()
def evaluate_shock(side,rule,a,b):
    p=1 if side=='DOWN' else -1; target=-p
    x=MM[(MM.target>=a)&(MM.target<=b)&(MM.dir3==p)]
    corr=dmg=trig=0
    for _,r in x.iterrows():
        q=D[D.month==r.target]; hit=bool(shock_signal(q,side,*rule).any())
        trig+=int(hit); corr+=int(hit and r.actual_dir==target); dmg+=int(hit and r.actual_dir==p)
    need=int((x.actual_dir==target).sum()); prec=corr/trig if trig else np.nan
    return len(x),need,trig,corr,dmg,prec,corr-dmg

def choose_shock(side):
    eligible=[]
    for rule in CANDS:
        dev=evaluate_shock(side,rule,'2010-01','2020-12'); val=evaluate_shock(side,rule,'2021-01','2022-12')
        if dev[2] and dev[5]>=.50 and dev[6]>=0:
            eligible.append((val[6],val[5] if np.isfinite(val[5]) else -1,-val[4],dev[6],rule))
    return max(eligible)[-1] if eligible else None
FROZEN_DOWN=choose_shock('DOWN'); FROZEN_UP=choose_shock('UP')
D['down_emg']=False if FROZEN_DOWN is None else shock_signal(D,'DOWN',*FROZEN_DOWN)
D['up_emg']=False if FROZEN_UP is None else shock_signal(D,'UP',*FROZEN_UP)

# ---------- Tactical risk-overlay candidate ----------
# Not a monthly direction flip. It only controls LONG/CASH exposure intramonth.
# Candidate persistence/release is selected before 2023. No MOM1 equal-vote policy.
def simulate(df,persist=1,release=1,allow_tactical=True):
    x=df.copy().sort_values('date'); cur=None; p_streak=r_streak=0; last_prior=None
    pos=[]; acts=[]; reasons=[]; evidence=[]
    for _,r in x.iterrows():
        p=int(r.prior); base=1 if p==1 else 0
        # Explicit monthly-anchor change; never silently reset at a month boundary.
        if cur is None:
            cur=base; reason='INITIAL_MONTHLY_ANCHOR'; action='AL' if cur==1 else 'TUT'
        elif last_prior is not None and p!=last_prior:
            new=base; action='TUT' if new==cur else ('AL' if new else 'SAT'); cur=new
            reason='MONTHLY_PRIOR_CHANGE'; p_streak=r_streak=0
        else:
            action='TUT'; reason='HOLD'
        last_prior=p
        # Emergency is a frozen intramonth override.
        if p==1 and bool(r.down_emg):
            new=0; reason='FROZEN_EMERGENCY_DOWN'
        elif p==-1 and bool(r.up_emg):
            new=1; reason='FROZEN_EMERGENCY_UP'
        else:
            new=cur
            if allow_tactical:
                opposite=(r.fast!=0 and r.slow!=0 and int(r.fast)==-p and int(r.slow)==-p)
                aligned=(r.fast!=0 and r.slow!=0 and int(r.fast)==p and int(r.slow)==p)
                p_streak=p_streak+1 if opposite else 0
                r_streak=r_streak+1 if aligned else 0
                if p==1 and cur==1 and p_streak>=persist:
                    new=0; reason='TACTICAL_RISK_EXIT'
                elif p==1 and cur==0 and r_streak>=release:
                    new=1; reason='TACTICAL_REENTRY'
                elif p==-1 and cur==0 and r_streak>=release:
                    new=1; reason='TACTICAL_UPSIDE_ENTRY'
                elif p==-1 and cur==1 and p_streak>=persist:
                    new=0; reason='TACTICAL_RETURN_CASH'
        if new!=cur:
            action='AL' if new==1 else 'SAT'
        cur=new
        # Evidence label is informational and can change without trading.
        if int(r.fast)==-p and int(r.slow)==-p and p!=0: ev='REVERSAL_CONFIRMED_FAST_SLOW'
        elif int(r.fast)==-p and p!=0: ev='EARLY_REVERSAL_FAST'
        elif int(r.slow)==-p and p!=0: ev='REVERSAL_CONFLICT_SLOW'
        elif int(r.fast)==p and int(r.slow)==p and p!=0: ev='ANCHOR_CONFIRMED'
        else: ev='MIXED_NEUTRAL'
        pos.append(cur); acts.append(action); reasons.append(reason); evidence.append(ev)
    x['pos']=pos; x['action']=acts; x['reason']=reasons; x['evidence_state']=evidence
    x['turn']=x.pos.diff().abs().fillna(0)
    # close-t action affects next bar: position shifted by one. Cost at action close.
    x['strat_ret']=x.pos.shift(1).fillna(x.pos.iloc[0])*x.ret.fillna(0)-.001*x.turn
    x['equity']=(1+x.strat_ret).cumprod()
    return x

def metrics(x):
    net=float(x.equity.iloc[-1]-1); mdd=float((x.equity/x.equity.cummax()-1).min()); trades=int(x.turn.sum())
    return net,mdd,trades

# Baseline and tactical candidates trained/validated strictly pre-2023.
def slice_period(a,b): return D[(D.date>=a)&(D.date<=b)].copy()
base_dev=simulate(slice_period('2010-01-01','2020-12-31'),allow_tactical=False); base_val=simulate(slice_period('2021-01-01','2022-12-31'),allow_tactical=False)
bdn,bdd,_=metrics(base_dev); bvn,bvd,_=metrics(base_val)
rows=[]
for p in [1,2,3]:
    for r in [1,2,3]:
        dev=simulate(slice_period('2010-01-01','2020-12-31'),p,r,True); val=simulate(slice_period('2021-01-01','2022-12-31'),p,r,True)
        dn,dd,dt=metrics(dev); vn,vd,vt=metrics(val)
        # Robust gate: no validation MDD deterioration >2pp and no DEV net collapse >10pp.
        eligible=(vd>=bvd-.02) and (dn>=bdn-.10)
        rows.append([p,r,eligible,dn,dd,dt,vn,vd,vt,vn+0.5*vd])
AUD=pd.DataFrame(rows,columns=['persist','release','eligible','dev_net','dev_mdd','dev_turns','val_net','val_mdd','val_turns','val_utility'])
elig=AUD[AUD.eligible].copy()
if len(elig):
    best=elig.sort_values(['val_utility','val_net','dev_net'],ascending=False).iloc[0]
    PERSIST=int(best.persist); RELEASE=int(best.release); TACTICAL_ENABLED=True
else:
    PERSIST=99; RELEASE=99; TACTICAL_ENABLED=False
AUD.to_csv(OUT/'DAILY_DECISION_2023_PRE2023_TACTICAL_AUDIT.csv',index=False)

# ---------- Untouched 2023 replay; focus outputs include Jan-Feb ----------
X=simulate(D[(D.date>='2023-01-01')&(D.date<='2023-12-31')],PERSIST,RELEASE,TACTICAL_ENABLED)
# Flag exact days that genuinely change directional evidence or position.
X['signal_day']=(X.action!='TUT')|(X.evidence_state!=X.evidence_state.shift(1))|(X.down_emg)|(X.up_emg)
X.to_csv(OUT/'DAILY_DECISION_2023_REPLAY.csv',index=False)
X[X.action!='TUT'].to_csv(OUT/'DAILY_DECISION_2023_ACTIONS.csv',index=False)
J=X[(X.date>='2023-01-01')&(X.date<='2023-02-28')].copy()
J.to_csv(OUT/'DAILY_DECISION_2023_JAN_FEB_UNIFIED.csv',index=False)
J[J.signal_day].to_csv(OUT/'DAILY_DECISION_2023_JAN_FEB_SIGNAL_DAYS.csv',index=False)

# Month summary.
mr=[]
for m,g in X.groupby('month'):
    ev=g[g.action!='TUT']; acts='; '.join(f"{r.date.date()} {r.action}({r.reason})" for _,r in ev.iterrows()) or '-'
    mr.append([m,int(g.prior.iloc[0]),int(g.pos.iloc[-1]),float((1+g.strat_ret).prod()-1),float(g.close.iloc[-1]/g.close.iloc[0]-1),int(g.turn.sum()),acts])
R=pd.DataFrame(mr,columns=['month','prior','end_pos','strategy_return','buyhold_return','turns','actions'])
R.to_csv(OUT/'DAILY_DECISION_2023_MONTHLY.csv',index=False)

net,mdd,tr=metrics(X); jnet=float((1+J.strat_ret).prod()-1); jmdd=float(((1+J.strat_ret).cumprod()/((1+J.strat_ret).cumprod().cummax())-1).min())
lines=['# GOLD H1 R1 — Unified 2023 Daily Investment Engine R2','',
'## Corrections','- Continuous position state: NO month-boundary reset. A changed monthly prior creates an explicit AL/SAT event.','- Removed ad-hoc MOM1/Fast/Slow equal voting.','- Restored 2026 hierarchy: 3M monthly prior; MOM1/VW/Patch/IDMA as origin context; Fast/Slow as tactical evidence; frozen bidirectional Emergency; BOCPD/CFTC remain risk/context outside daily vote.','- Added GVZCLS as non-directional gold-volatility context; GVZ never votes UP/DOWN.','- Monthly VW/Patch/IDMA/3M price forecasts are target-month-average anchors, not daily-price targets. Daily close-vs-forecast gap is diagnostic only.','- News/Event emergency execution remains BLOCKED_CONSENSUS_HISTORY: no invented surprise threshold or hindsight rule is allowed.','',
f'- Frozen DOWN emergency rule: {FROZEN_DOWN}',f'- Frozen UP emergency rule: {FROZEN_UP}',f'- Tactical risk overlay enabled: {TACTICAL_ENABLED}; persistence={PERSIST}; release={RELEASE}',
f'- 2023 net (10bp/change): {net:.2%}; MDD: {mdd:.2%}; turns={tr}',f'- Jan-Feb 2023 net: {jnet:.2%}; MDD: {jmdd:.2%}','',
'## Jan-Feb direction-changing / action days','|Date|Close|Prior|MOM1|VW|Patch|IDMA|Fast|Slow|GVZ|GVZ stress|Emergency|Evidence|Action|Reason|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|']
for _,r in J[J.signal_day].iterrows():
    em='DOWN' if r.down_emg else ('UP' if r.up_emg else '-')
    lines.append(f"|{r.date.date()}|{r.close:.2f}|{int(r.prior):+d}|{int(r.mom1):+d}|{int(r.vw_dir) if pd.notna(r.vw_dir) else 0:+d}|{int(r.patch_dir) if pd.notna(r.patch_dir) else 0:+d}|{int(r.idma_dir) if pd.notna(r.idma_dir) else 0:+d}|{int(r.fast):+d}|{int(r.slow):+d}|{r.GVZCLS:.2f}|{bool(r.gvz_stress)}|{em}|{r.evidence_state}|{r.action}|{r.reason}|")
lines+=['','## Status','- Price-level engine: INCLUDED as monthly anchor/context.','- Direction engine: INCLUDED.','- Fast/Slow tactical: INCLUDED with pre-2023 risk-overlay audit.','- Bidirectional price/macro Emergency: INCLUDED and pre-2023 frozen.','- GVZ: INCLUDED correctly as volatility/risk context.','- VIX/USD/real-yield: INCLUDED in Emergency/context.','- News/Event surprise engine: BLOCKED_CONSENSUS_HISTORY; no exact point-in-time consensus dataset is source-locked, so it is NOT allowed to manufacture a 3-Feb SAT.','- BOCPD: monthly structural risk context only; not a same-day direction vote.','- CFTC: weekly positioning context only; no automatic flip.','- 2023 actuals: evaluation only, never used for threshold/persistence/rule selection.']
(OUT/'DAILY_DECISION_2023_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
