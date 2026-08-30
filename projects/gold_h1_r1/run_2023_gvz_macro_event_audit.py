#!/usr/bin/env python3
import io,json,time,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
OUT=Path('projects/gold_h1_r1')
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
GOLD=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
GVZ='https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv'
MACRO='https://raw.githubusercontent.com/superpilot69/fred-us-macro-open-data/main/data/fred-us-macro-events.json'

def get_bytes(url,tries=5):
    err=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-event-audit/1.0'})
            with urllib.request.urlopen(req,timeout=240) as r:return r.read()
        except Exception as e: err=e; time.sleep(3*(i+1))
    raise err

def csv(url): return pd.read_csv(io.BytesIO(get_bytes(url)))

# Gold daily
D=csv(GOLD); D['date']=pd.to_datetime(D['time']); D=D[['date','open','high','low','close']].sort_values('date').drop_duplicates('date')
D['month']=D.date.dt.to_period('M').astype(str); D['ret']=D.close.pct_change(); D['sma20']=D.close.rolling(20).mean(); D['fast_raw']=np.sign(D.close-D.sma20)
fr=D.fast_raw.to_numpy(); fast=np.zeros(len(D),int)
for i in range(1,len(D)):
    if np.isfinite(fr[i]) and fr[i]!=0 and fr[i]==fr[i-1]: fast[i]=int(fr[i])
D['fast']=fast
# Slow, same contract as main engine
wd=D[['date','close']].copy(); wd['wk_start']=(wd.date-pd.to_timedelta((wd.date.dt.weekday+1)%7,unit='D')).dt.normalize()
W=wd.groupby('wk_start').agg(wclose=('close','last')).reset_index().sort_values('wk_start'); W['sma4']=W.wclose.rolling(4).mean(); W['raw']=np.sign(W.wclose-W.sma4)
wr=W.raw.to_numpy(); slow=np.zeros(len(W),int)
for i in range(1,len(W)):
    if np.isfinite(wr[i]) and wr[i]!=0 and wr[i]==wr[i-1]: slow[i]=int(wr[i])
W['slow']=slow; W['known_date']=W.wk_start+pd.Timedelta(days=6)
D=pd.merge_asof(D.sort_values('date'),W[['known_date','slow']].rename(columns={'known_date':'date'}).sort_values('date'),on='date',direction='backward'); D['slow']=D.slow.fillna(0).astype(int)
# Monthly prior
M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); M['target']=pd.to_datetime(M.target).dt.to_period('M').astype(str); M=M.sort_values('target'); M=M[~M.flat.astype(bool)].copy()
prior=dict(zip(M.target,M.dir3.astype(int))); D['prior']=D.month.map(prior).fillna(0).astype(int)

# Official Cboe GVZ history. Hard fail if missing; no silent NaN.
g=csv(GVZ); cols={c.upper():c for c in g.columns}; dc=cols.get('DATE'); cc=cols.get('CLOSE') or cols.get('GVZ')
if dc is None or cc is None: raise RuntimeError(f'Unexpected Cboe GVZ columns: {list(g.columns)}')
g=g[[dc,cc]].rename(columns={dc:'date',cc:'GVZCLS'}); g['date']=pd.to_datetime(g.date); g['GVZCLS']=pd.to_numeric(g.GVZCLS,errors='coerce'); g=g.dropna().sort_values('date')
D=pd.merge_asof(D.sort_values('date'),g,on='date',direction='backward',tolerance=pd.Timedelta('7D'))
if D.loc[(D.date>='2023-01-01')&(D.date<='2023-02-28'),'GVZCLS'].isna().any(): raise RuntimeError('GVZ missing in Jan-Feb 2023 after Cboe merge')
D['gvz5']=D.GVZCLS/D.GVZCLS.shift(5)-1; D['gvz_q90_252']=D.GVZCLS.shift(1).rolling(252,min_periods=126).quantile(.90); D['gvz_stress']=D.GVZCLS>=D.gvz_q90_252

# Public replay macro data: FRED actual/release timing + Investing.com consensus enrichment.
obj=json.loads(get_bytes(MACRO)); events=obj['events'] if isinstance(obj,dict) and 'events' in obj else obj
# Short-run gold sign: positive score supportive gold; negative adverse gold.
# Focus high-impact US labor/growth/inflation where positive economic/hawkish surprise normally raises opportunity cost/USD.
series_sign={'PAYEMS':-1,'UNRATE':1,'CES0500000003':-1,'RSAFS':-1,'CPIAUCNS':-1,'CPILFENS':-1,'PPIACO':-1,'PCEPILFE':-1}
rows=[]
for e in events:
    md=e.get('metadata') or {}; sid=md.get('seriesId'); con=md.get('consensus') or {}
    if sid not in series_sign or con.get('forecast') is None or con.get('actual') is None: continue
    # Strict timing: reject approximate release timestamps.
    if md.get('releaseDateApproximate') is True: continue
    try: actual=float(con.get('actual')); forecast=float(con.get('forecast'))
    except Exception: continue
    diff=actual-forecast
    s=0 if diff==0 else int(np.sign(diff))*series_sign[sid]
    dt=md.get('releaseDate') or e.get('createdAt')
    if not dt: continue
    d=pd.to_datetime(dt,utc=True).tz_convert(None).normalize()
    rows.append([d,sid,actual,forecast,diff,s,con.get('sourceId'),con.get('sourceUrl')])
E=pd.DataFrame(rows,columns=['date','series','actual','forecast','surprise','gold_sign','consensus_source','source_url'])
if E.empty: raise RuntimeError('No exact-timestamp consensus macro events loaded')
# aggregate all high-impact releases known before close on release day
A=E.groupby('date').agg(macro_gold_score=('gold_sign','sum'),macro_event_count=('gold_sign','size'),macro_series=('series',lambda x:';'.join(x))).reset_index()
D=D.merge(A,on='date',how='left'); D['macro_gold_score']=D.macro_gold_score.fillna(0).astype(int); D['macro_event_count']=D.macro_event_count.fillna(0).astype(int); D['macro_series']=D.macro_series.fillna('')

# Candidate same-day event reversal. Decision at that day's close applies next bar.
# No 2023 tuning. Monthly override holds until next monthly origin.
CANDS=[(score,ret) for score in [1,2,3] for ret in [.0,.005,.01,.02]]
def hit_day(q,side,rule):
    score,rt=rule
    if side=='DOWN': return (q.macro_gold_score<=-score)&(q.fast==-1)&(q['ret']<=-rt)
    return (q.macro_gold_score>=score)&(q.fast==1)&(q['ret']>=rt)
def evaluate(side,rule,a,b):
    p=1 if side=='DOWN' else -1; target=-p; x=M[(M.target>=a)&(M.target<=b)&(M.dir3==p)]
    trig=corr=dmg=0
    for _,r in x.iterrows():
        q=D[D.month==r.target]; hit=bool(hit_day(q,side,rule).any()); trig+=hit; corr+=int(hit and r.actual_dir==target); dmg+=int(hit and r.actual_dir==p)
    need=int((x.actual_dir==target).sum()); prec=corr/trig if trig else np.nan
    return len(x),need,trig,corr,dmg,prec,corr-dmg

def choose(side):
    elig=[]; allrows=[]
    for rule in CANDS:
        dev=evaluate(side,rule,'2010-01','2020-12'); val=evaluate(side,rule,'2021-01','2022-12'); allrows.append((rule,dev,val))
        if dev[2]>0 and dev[5]>=.50 and dev[6]>=0:
            elig.append((val[6],val[5] if np.isfinite(val[5]) else -1,-val[4],dev[6],rule))
    return (max(elig)[-1] if elig else None),allrows

out=[]; frozen={}
for side in ['DOWN','UP']:
    rule,allrows=choose(side); frozen[side]=rule
    if rule:
        for period,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12')]:
            out.append([side,rule[0],rule[1],period,*evaluate(side,rule,a,b)])
pd.DataFrame(out,columns=['side','score_thr','ret_thr','period','eligible_months','needs','triggers','corrected','damaged','precision','utility']).to_csv(OUT/'MACRO_EVENT_REVERSAL_AUDIT_R1.csv',index=False)

# 2023 event replay and Jan-Feb focus
replay=[]
for _,r in M[(M.target>='2023-01')&(M.target<='2023-12')].iterrows():
    side='DOWN' if r.dir3==1 else 'UP'; rule=frozen.get(side); q=D[D.month==r.target]
    sig=pd.Series(False,index=q.index) if rule is None else hit_day(q,side,rule)
    hit=bool(sig.any()); first=q.loc[sig].iloc[0] if hit else None
    replay.append([r.target,int(r.actual_dir),int(r.dir3),side,hit,'' if first is None else first.date.date().isoformat(),np.nan if first is None else first.close,np.nan if first is None else first.macro_gold_score,'' if first is None else first.macro_series,np.nan if first is None else first.GVZCLS,False if first is None else bool(first.gvz_stress)])
R=pd.DataFrame(replay,columns=['target','actual_dir','prior_dir','eligible_side','trigger','trigger_date','close','macro_gold_score','macro_series','GVZCLS','gvz_stress']); R.to_csv(OUT/'MACRO_EVENT_REVERSAL_2023_REPLAY_R1.csv',index=False)
# exact Jan-Feb signal/context table
J=D[(D.date>='2023-01-01')&(D.date<='2023-02-28')].copy(); J['event_down']=False if frozen['DOWN'] is None else hit_day(J,'DOWN',frozen['DOWN']); J['event_up']=False if frozen['UP'] is None else hit_day(J,'UP',frozen['UP'])
focus=J[(J.macro_event_count>0)|(J.event_down)|(J.event_up)|(J.fast!=J.fast.shift(1))|(J.slow!=J.slow.shift(1))][['date','close','ret','prior','fast','slow','macro_gold_score','macro_event_count','macro_series','event_down','event_up','GVZCLS','gvz5','gvz_q90_252','gvz_stress']]
focus.to_csv(OUT/'JAN_FEB_2023_GVZ_MACRO_SIGNAL_DAYS_R1.csv',index=False)

# independent exact Feb-3 NFP row for audit
nfp=E[(E.series=='PAYEMS')&(E.date>='2023-02-01')&(E.date<='2023-02-07')]
lines=['# GVZ + Macro Event Reversal Audit R1','',
'Sources: pinned XAUUSD D1; official Cboe GVZ_History.csv; FRED release/actual enriched with Investing.com consensus from superpilot69/fred-us-macro-open-data.','2023 is untouched test. Approximate release timestamps are excluded. Event decisions are close-of-release-day and apply to the next D1 bar.','',
f'Frozen DOWN event rule: {frozen["DOWN"]}',f'Frozen UP event rule: {frozen["UP"]}','',
'## NFP around 3-Feb-2023']
if nfp.empty: lines.append('- NOT_FOUND in exact-timestamp macro dataset')
else:
    for _,r in nfp.iterrows(): lines.append(f'- {r.date.date()}: actual={r.actual}, forecast={r.forecast}, surprise={r.surprise}, gold_sign={r.gold_sign}, source={r.consensus_source}')
lines+=['','## 2023 event triggers']
for _,r in R.iterrows(): lines.append(f'- {r.target}: prior={r.prior_dir:+d}, actual={r.actual_dir:+d}, trigger={r.trigger}, date={r.trigger_date or "-"}, macro_score={r.macro_gold_score}, GVZ={r.GVZCLS}, GVZ_stress={r.gvz_stress}')
lines+=['','## Interpretation','- GVZ is non-directional risk/intensity context and never creates UP/DOWN by itself.','- Macro Event is execution-authorized only if a pre-2023 rule is selected and 2023 is then replayed untouched.','- If no pre-2023 eligible rule exists, EVENT_EXECUTION=REJECT and the layer remains context-only.']
(OUT/'GVZ_MACRO_EVENT_AUDIT_R1.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines))
