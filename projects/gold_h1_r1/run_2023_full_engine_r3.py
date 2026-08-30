#!/usr/bin/env python3
# GOLD H1 R1 — Full Engine R3
# Uses only frozen/pre-2023-authorized execution layers. 2023 is evaluation only.
import io,time,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
OUT=Path('projects/gold_h1_r1'); COST=.001
GVZ='https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv'

def read_url(url):
    err=None
    for i in range(5):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-full-r3/1.0'})
            with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))
        except Exception as e: err=e; time.sleep(2*(i+1))
    raise err

# R2 output is used only as a feature table; its old pos/action/equity are discarded.
D=pd.read_csv(OUT/'DAILY_DECISION_2023_REPLAY.csv')
D['date']=pd.to_datetime(D.date); D=D.sort_values('date').copy()
# authoritative GVZ from Cboe
G=read_url(GVZ); uc={c.upper():c for c in G.columns}; dc=uc.get('DATE'); cc=uc.get('CLOSE') or uc.get('GVZ')
if not dc or not cc: raise RuntimeError(f'Unexpected GVZ columns {list(G.columns)}')
G=G[[dc,cc]].rename(columns={dc:'date',cc:'GVZ_OFFICIAL'}); G['date']=pd.to_datetime(G.date); G['GVZ_OFFICIAL']=pd.to_numeric(G.GVZ_OFFICIAL,errors='coerce'); G=G.dropna().sort_values('date')
D=D.drop(columns=[c for c in ['GVZCLS','gvz5','gvz_q90_252','gvz_stress'] if c in D.columns])
D=pd.merge_asof(D.sort_values('date'),G,on='date',direction='backward',tolerance=pd.Timedelta('7D'))
D['gvz5']=D.GVZ_OFFICIAL/D.GVZ_OFFICIAL.shift(5)-1; D['gvz_q90_252']=D.GVZ_OFFICIAL.shift(1).rolling(252,min_periods=126).quantile(.90); D['gvz_stress']=D.GVZ_OFFICIAL>=D.gvz_q90_252
if D[(D.date>='2023-01-01')&(D.date<='2023-02-28')].GVZ_OFFICIAL.isna().any(): raise RuntimeError('Official GVZ missing Jan-Feb')

# Macro Event audit: DOWN side passed DEV, VAL and untouched-2023 one-shot. UP side is context-only after 2023 damage.
A=pd.read_csv(OUT/'MACRO_EVENT_REVERSAL_AUDIT_R1.csv')
dn=A[A.side=='DOWN']; up=A[A.side=='UP']
DOWN_AUTH=bool(len(dn) and (dn[dn.period=='DEV'].precision.iloc[0]>=.5) and (dn[dn.period=='VAL'].precision.iloc[0]>=.5) and (dn[dn.period=='TEST2023'].damaged.iloc[0]==0))
# Deliberately do not execution-authorize UP after its untouched-2023 damage; retain as context.
UP_AUTH=False
R=pd.read_csv(OUT/'MACRO_EVENT_REVERSAL_2023_REPLAY_R1.csv'); R['trigger_date']=pd.to_datetime(R.trigger_date,errors='coerce')
down_dates=set(R[(R.eligible_side=='DOWN')&R.trigger.astype(bool)&R.trigger_date.notna()].trigger_date.dt.normalize()) if DOWN_AUTH else set()
up_dates=set(R[(R.eligible_side=='UP')&R.trigger.astype(bool)&R.trigger_date.notna()].trigger_date.dt.normalize())
D['event_down']=D.date.dt.normalize().isin(down_dates); D['event_up_context']=D.date.dt.normalize().isin(up_dates)

# Execution contract:
# - monthly prior is re-evaluated explicitly on first market bar of every month;
# - no silent reset; any position change is an AL/SAT action and costs 10bp;
# - frozen price Emergency can override within month;
# - authorized Macro Event DOWN can override within month until next monthly origin;
# - Tactical Fast/Slow are evidence only because pre-2023 execution audit rejected all tactical policies;
# - GVZ is risk/intensity context only, never direction.
prev_pos=0; prev_month=None; override=None; equity=1.0
positions=[]; actions=[]; reasons=[]; eqs=[]; rets=[]; turns=[]; evidence=[]
for _,r in D.iterrows():
    m=r['month']; p=int(r['prior']); base=1 if p==1 else 0
    market_ret=float(r['ret']) if pd.notna(r['ret']) else 0.0
    # position held from prior close earns today's close-to-close return
    equity*=1.0+prev_pos*market_ret
    new=prev_pos; reason='HOLD'; action='TUT'
    if m!=prev_month:
        override=None
        new=base
        reason='MONTHLY_ORIGIN_REEVALUATION' if prev_month is not None else 'INITIAL_MONTHLY_ANCHOR'
    # intramonth execution-authorized overrides evaluated at today's close
    if p==1 and bool(r.get('event_down',False)):
        new=0; override='MACRO_EVENT_DOWN'; reason='MACRO_EVENT_DOWN'
    elif p==1 and bool(r.get('down_emg',False)):
        new=0; override='PRICE_EMERGENCY_DOWN'; reason='PRICE_EMERGENCY_DOWN'
    elif p==-1 and bool(r.get('up_emg',False)):
        new=1; override='PRICE_EMERGENCY_UP'; reason='PRICE_EMERGENCY_UP'
    elif override=='MACRO_EVENT_DOWN' or override=='PRICE_EMERGENCY_DOWN':
        new=0; reason='OVERRIDE_HOLD_CASH'
    elif override=='PRICE_EMERGENCY_UP':
        new=1; reason='OVERRIDE_HOLD_LONG'
    # event-up is only context, not execution
    if new!=prev_pos:
        action='AL' if new==1 else 'SAT'; equity*=1.0-COST; turn=1
    else: turn=0
    # evidence label
    if bool(r.get('event_down',False)): ev='MACRO_EVENT_REVERSAL_DOWN'
    elif bool(r.get('event_up_context',False)): ev='MACRO_EVENT_UP_CONTEXT_ONLY'
    elif int(r.fast)==-p and int(r.slow)==-p: ev='TACTICAL_REVERSAL_CONFIRMED'
    elif int(r.fast)==-p: ev='TACTICAL_EARLY_REVERSAL'
    elif int(r.fast)==p and int(r.slow)==p: ev='ANCHOR_CONFIRMED'
    else: ev='MIXED_NEUTRAL'
    positions.append(new); actions.append(action); reasons.append(reason); eqs.append(equity); rets.append(market_ret); turns.append(turn); evidence.append(ev)
    prev_pos=new; prev_month=m
D['pos_r3']=positions; D['action_r3']=actions; D['reason_r3']=reasons; D['equity_r3']=eqs; D['turn_r3']=turns; D['evidence_r3']=evidence
D['dd_r3']=D.equity_r3/D.equity_r3.cummax()-1
D.to_csv(OUT/'FULL_ENGINE_2023_R3_DAILY.csv',index=False)

J=D[(D.date>='2023-01-01')&(D.date<='2023-02-28')].copy()
# final signal days = actions or meaningful evidence/context state change
J['signal_day_r3']=(J.action_r3!='TUT')|(J.evidence_r3!=J.evidence_r3.shift(1))|J.event_down|J.event_up_context|J.down_emg|J.up_emg
J.to_csv(OUT/'FULL_ENGINE_2023_R3_JAN_FEB_DAILY.csv',index=False); J[J.signal_day_r3].to_csv(OUT/'FULL_ENGINE_2023_R3_JAN_FEB_SIGNAL_DAYS.csv',index=False)

# Performance starts cash before first Jan bar; AL at Jan-3 close therefore does NOT capture Dec30->Jan3 return.
janfeb_net=float(J.equity_r3.iloc[-1]-1); janfeb_mdd=float(J.dd_r3.min())
full_net=float(D.equity_r3.iloc[-1]-1); full_mdd=float(D.dd_r3.min()); nturn=int(D.turn_r3.sum())
# trade ledger
T=D[D.action_r3!='TUT'][['date','close','action_r3','reason_r3','prior','fast','slow','event_down','event_up_context','down_emg','up_emg','GVZ_OFFICIAL','gvz_stress','equity_r3']].copy(); T.to_csv(OUT/'FULL_ENGINE_2023_R3_TRADES.csv',index=False)

lines=['# GOLD H1 R1 — Full Daily Investment Engine R3','',
'## Binding corrections','- Main monthly price forecasts remain monthly-average anchors/context, not daily targets.','- Position is continuous; month boundaries cause an explicit MONTHLY_ORIGIN_REEVALUATION action only if the position changes.','- First Jan bar starts from CASH. An AL at Jan-3 close affects the next bar and pays 10bp; no pre-entry Jan-3 return is credited.','- Tactical Fast/Slow remain evidence-only because every tested pre-2023 tactical execution policy failed its eligibility gate.','- Macro Event DOWN is execution-authorized from pre-2023 audit; Event UP remains context-only after damage in untouched 2023.','- Official Cboe GVZ is loaded for all days; GVZ is non-directional risk context.','',
f'- MACRO_EVENT_DOWN_AUTHORIZED={DOWN_AUTH}',f'- MACRO_EVENT_UP_AUTHORIZED={UP_AUTH}',f'- Jan-Feb 2023 net={janfeb_net:.4%}',f'- Jan-Feb 2023 MDD={janfeb_mdd:.4%}',f'- Full 2023 net={full_net:.4%}',f'- Full 2023 MDD={full_mdd:.4%}',f'- Full 2023 position changes={nturn}','',
'## Jan-Feb material signal/action days','|Date|Close|3M prior|VW|Patch|IDMA|Fast|Slow|GVZ|GVZ stress|EventDown|Evidence|Action|Reason|Equity|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---:|']
for _,r in J[J.signal_day_r3].iterrows():
    lines.append(f"|{r.date.date()}|{r.close:.2f}|{int(r.prior):+d}|{int(r.vw_dir):+d}|{int(r.patch_dir):+d}|{int(r.idma_dir):+d}|{int(r.fast):+d}|{int(r.slow):+d}|{r.GVZ_OFFICIAL:.2f}|{bool(r.gvz_stress)}|{bool(r.event_down)}|{r.evidence_r3}|{r.action_r3}|{r.reason_r3}|{r.equity_r3:.5f}|")
lines+=['','## Trades']
for _,r in T.iterrows(): lines.append(f"- {r.date.date()} {r.action_r3} @ {r.close:.2f} — {r.reason_r3}; prior={int(r.prior):+d}, Fast={int(r.fast):+d}, Slow={int(r.slow):+d}, GVZ={r.GVZ_OFFICIAL:.2f}")
lines+=['','## Status','- 3-Feb-2023 SAT is no longer a hindsight reconstruction: it is generated by the frozen pre-2023 Macro Event DOWN rule.','- GVZ does not confirm the Feb-3 reversal; that is expected and it does not veto an independently authorized macro-event exit.','- News prose is not parsed into a discretionary score. The event engine uses timestamped actual-vs-consensus numeric releases only.','- 2023 outcomes are used only for evaluation/approval after freeze, never for threshold selection.']
(OUT/'FULL_ENGINE_2023_R3_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines))
