from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / 'r4_1' / 'src'
if str(R4_SRC) not in sys.path: sys.path.insert(0, str(R4_SRC))
from gold_r4 import completed_weekly_closes, fast_state, slow_state  # noqa: E402

START_PREHISTORY=pd.Timestamp('2021-09-01')
FORMATION_START=pd.Timestamp('2022-01-01')
CHALLENGE_START=pd.Timestamp('2025-01-01')
CHALLENGE_END=pd.Timestamp('2025-12-31')
SIGMA_WINDOW=20
K=3.0
FINAL={'VALID_EXACT_BAR','PROVIDER_NO_BAR'}


def load_contracts():
    a=json.loads((ROOT/'gc_break_v0'/'gc_break_wp4c_structural_health_dual_lane_freeze_v1.json').read_text())
    p=json.loads((ROOT/'gc_break_v0'/'gc_break_wp4c_2025_challenge_protocol_v1.json').read_text())
    if a.get('status')!='FORMATION_INFORMED_DEVELOPMENT_LOCK_BEFORE_CHALLENGE': raise RuntimeError('ARCHITECTURE_LOCK_FAIL')
    if p.get('status')!='FROZEN_BEFORE_2025_CHALLENGE_SCORING': raise RuntimeError('CHALLENGE_PROTOCOL_NOT_FROZEN')
    if p.get('architecture_contract')!=a.get('contract_id'): raise RuntimeError('PROTOCOL_ARCH_MISMATCH')
    return a,p


def load_exact(path:Path, challenge:bool)->pd.DataFrame:
    d=pd.read_csv(path,dtype=str,keep_default_na=False)
    req={'trade_date','acquisition_status'}
    if not req<=set(d): raise RuntimeError(f'EXACT_SCHEMA_FAIL:{path}')
    bad=sorted(set(d.acquisition_status)-FINAL)
    if bad: raise RuntimeError(f'UNRESOLVED_EXACT_STATUS:{path}:{bad[:5]}')
    if challenge:
        lineage={'provider':'Twelve Data','symbol':'XAU/USD','interval':'1min','timezone':'America/New_York','accepted_source_time':'16:59:00','evidence_class':'HISTORICAL_REPLAY_RECONSTRUCTION','prospective_claim':'False'}
        for k,v in lineage.items():
            vals=set(d.loc[d.acquisition_status.eq('VALID_EXACT_BAR'),k]) if k in d else set()
            if vals!={v}: raise RuntimeError(f'CHALLENGE_LINEAGE_FAIL:{k}:{vals}')
    valid=d[d.acquisition_status.eq('VALID_EXACT_BAR')].copy()
    valid['date']=pd.to_datetime(valid.trade_date).dt.normalize(); valid['close']=pd.to_numeric(valid.close,errors='raise')
    if valid.date.duplicated().any() or (valid.close<=0).any() or not np.isfinite(valid.close.to_numpy()).all(): raise RuntimeError(f'INVALID_EXACT_ROWS:{path}')
    return valid[['date','close']].sort_values('date').reset_index(drop=True)


def label_history(d:pd.DataFrame)->pd.DataFrame:
    x=d.sort_values('date').reset_index(drop=True).copy()
    x['log_ret']=np.log(x.close/x.close.shift(1)); x['close_lag20']=x.close.shift(20)
    x['sigma20_lag1']=x.log_ret.shift(1).rolling(20,min_periods=20).std(ddof=1)
    regime=None; extreme=None; rows=[]; eid=0
    for r in x.itertuples(index=False):
        rb=regime; br=False; adverse=np.nan; threshold=np.nan
        if regime is None:
            if pd.notna(r.close_lag20):
                mom=float(np.log(float(r.close)/float(r.close_lag20)))
                if mom>0: regime='UP'
                elif mom<0: regime='DOWN'
                if regime is not None: extreme=float(r.close)
        else:
            sig=float(r.sigma20_lag1) if pd.notna(r.sigma20_lag1) else np.nan
            if regime=='UP': adverse=float(np.log(float(extreme)/float(r.close)))
            else: adverse=float(np.log(float(r.close)/float(extreme)))
            threshold=float(K*sig) if np.isfinite(sig) else np.nan
            if np.isfinite(threshold) and adverse>=threshold:
                br=True; eid+=1; regime='DOWN' if regime=='UP' else 'UP'; extreme=float(r.close)
            elif regime=='UP': extreme=max(float(extreme),float(r.close))
            else: extreme=min(float(extreme),float(r.close))
        frac=adverse/threshold if np.isfinite(adverse) and np.isfinite(threshold) and threshold>0 else np.nan
        rows.append({'date':pd.Timestamp(r.date),'close':float(r.close),'log_ret':r.log_ret,'sigma20_lag1':r.sigma20_lag1,
                     'regime_before':rb,'regime_after':regime,'adverse_move':adverse,'threshold':threshold,'adverse_fraction':frac,
                     'is_break':br,'event_seq_all':eid if br else np.nan})
    return pd.DataFrame(rows)


def add_roles(lab:pd.DataFrame)->pd.DataFrame:
    out=[]
    for i,r in lab.iterrows():
        hist=lab.loc[:i,['date','close']]
        day=pd.Timestamp(r.date)
        fs=fast_state(hist.close.tolist()).value
        ss=slow_state(completed_weekly_closes(hist,day)).value
        out.append((fs,ss))
    lab=lab.copy(); lab[['fast_state','slow_state']]=pd.DataFrame(out,index=lab.index)
    return lab


def same(v:str,reg:str|None)->bool:
    return (reg=='UP' and v=='ROBUST_UP') or (reg=='DOWN' and v=='ROBUST_DOWN')
def opp(v:str,reg:str|None)->bool:
    return (reg=='UP' and v=='ROBUST_DOWN') or (reg=='DOWN' and v=='ROBUST_UP')


def add_signals(p:pd.DataFrame)->pd.DataFrame:
    q=p.copy(); valid=q.regime_before.isin(['UP','DOWN'])
    q['fast_same']=[same(str(v),r) for v,r in zip(q.fast_state,q.regime_before)]
    q['fast_conflict']=valid & ~q.fast_same
    q['fast_opposite']=[opp(str(v),r) for v,r in zip(q.fast_state,q.regime_before)]
    q['path_half']=valid & q.adverse_fraction.ge(0.50)
    return q


def state_trajectory(p:pd.DataFrame)->pd.DataFrame:
    state='STABLE'; regime=None; rows=[]
    for _,r in p.iterrows():
        rb=r.regime_before
        if rb in {'UP','DOWN'}: regime=rb
        if regime is None:
            rows.append({**r.to_dict(),'state_before':state,'state_after':state,'transition_reason':'REGIME_NOT_INITIALIZED'}); continue
        fs=str(r.fast_state); ss=str(r.slow_state); f_same=same(fs,regime); f_opp=opp(fs,regime); f_conf=not f_same
        path=bool(r.path_half); weak=path or f_conf; strong=f_opp or (path and f_conf); before=state; reason='HOLD'
        if bool(r.is_break):
            state='CONFIRMED_BREAK'; regime=str(r.regime_after); reason='FROZEN_CURRENT_ORIGIN_BREAK'
        elif state=='CONFIRMED_BREAK':
            if same(ss,regime): state='NEW_REGIME'; reason='SLOW_CONFIRMS_NEW_REGIME'
            else: reason='AWAIT_SLOW_CONFIRMATION'
        elif state=='NEW_REGIME':
            if same(fs,regime) and same(ss,regime): state='STABLE'; reason='FAST_AND_SLOW_SUPPORT_NEW_REGIME'
            else: reason='NEW_REGIME_SETTLING'
        elif state=='STABLE':
            if weak: state='WEAKENING'; reason='STRUCTURAL_HEALTH_OR_FAST_WEAKENING'
            else: reason='STABLE_EVIDENCE'
        elif state=='WEAKENING':
            if strong: state='BREAK_ALERT'; reason='FAST_OPPOSITE_OR_DUAL_LANE_CONCORDANCE'
            elif not weak: state='STABLE'; reason='RECOVERY_TO_STABLE'
            else: reason='WEAKENING_PERSISTS'
        elif state=='BREAK_ALERT':
            if strong: reason='BREAK_ALERT_PERSISTS'
            elif weak: state='WEAKENING'; reason='DEESCALATE_TO_WEAKENING'
            else: state='STABLE'; reason='RECOVERY_TO_STABLE'
        rows.append({**r.to_dict(),'state_before':before,'state_after':state,'transition_reason':reason})
    return pd.DataFrame(rows)


def boolean_episodes(q:pd.DataFrame,col:str,event_dates:set[pd.Timestamp])->pd.DataFrame:
    on=q[col].fillna(False).astype(bool).to_numpy(); out=[]; start=None
    for i,flag in enumerate(on):
        if flag and start is None: start=i
        if start is not None and (not flag or i==len(on)-1):
            end=i-1 if not flag else i; ds=pd.to_datetime(q.loc[start:end,'date']); ed=[d for d in ds if d in event_dates]
            # Event on an active signal origin is at-or-before detection; lead=position from episode start.
            bd=ed[0] if ed else pd.NaT; conv=pd.notna(bd)
            lead=(q.index[q.date.eq(bd)][0]-start) if conv else np.nan
            out.append({'start_i':start,'end_i':end,'start_date':q.loc[start,'date'],'end_date':q.loc[end,'date'],'converted':conv,'break_date':bd,
                        'lead_observations':lead,'lead_calendar_days':(bd-pd.Timestamp(q.loc[start,'date'])).days if conv else np.nan})
            start=None
    return pd.DataFrame(out)


def state_episodes(q:pd.DataFrame,states:set[str],event_dates:set[pd.Timestamp])->pd.DataFrame:
    on=q.state_after.isin(states).to_numpy(); out=[]; start=None
    for i,flag in enumerate(on):
        if flag and start is None: start=i
        if start is None: continue
        # current-origin break changes state to CONFIRMED_BREAK, so a warning episode converts if the next governed origin is a break.
        next_break=(i+1<len(q) and pd.Timestamp(q.loc[i+1,'date']) in event_dates)
        end_now=(i==len(q)-1 or not flag or next_break or (flag and i+1<len(q) and not on[i+1]))
        if not end_now: continue
        end=i if flag else i-1
        if end>=start:
            conv=bool(end+1<len(q) and pd.Timestamp(q.loc[end+1,'date']) in event_dates); bd=pd.Timestamp(q.loc[end+1,'date']) if conv else pd.NaT
            out.append({'start_i':start,'end_i':end,'start_date':q.loc[start,'date'],'end_date':q.loc[end,'date'],'converted':conv,'break_date':bd,
                        'lead_observations':end+1-start if conv else np.nan,'lead_calendar_days':(bd-pd.Timestamp(q.loc[start,'date'])).days if conv else np.nan,
                        'recovered_to_stable':bool((not conv) and end+1<len(q) and q.loc[end+1,'state_after']=='STABLE')})
        start=None
    return pd.DataFrame(out)


def ep_metrics(ep:pd.DataFrame,n_events:int,n_origins:int)->dict:
    if ep.empty: return {'episodes':0,'converted_episodes':0,'false_episodes':0,'prebreak_event_recall':0.0,'at_or_before_event_recall':0.0,'false_episodes_per_100_origins':0.0,'median_lead_observations':None,'median_lead_calendar_days':None}
    c=ep[ep.converted]; leads=c.lead_observations.dropna(); pre=c[c.lead_observations>0]
    return {'episodes':int(len(ep)),'converted_episodes':int(len(c)),'false_episodes':int((~ep.converted).sum()),
            'prebreak_event_recall':float(pd.to_datetime(pre.break_date).nunique()/n_events) if n_events else None,
            'at_or_before_event_recall':float(pd.to_datetime(c.break_date).nunique()/n_events) if n_events else None,
            'false_episodes_per_100_origins':float((~ep.converted).sum()*100.0/n_origins),
            'median_lead_observations':float(leads.median()) if len(leads) else None,
            'median_lead_calendar_days':float(c.lead_calendar_days.dropna().median()) if len(c) else None}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--historical-exact',type=Path,required=True); ap.add_argument('--challenge-exact',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True)
    a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); arch,protocol=load_contracts()
    hist=load_exact(a.historical_exact,False); ch=load_exact(a.challenge_exact,True)
    if ch.empty or ch.date.min()<CHALLENGE_START or ch.date.max()>CHALLENGE_END: raise RuntimeError('CHALLENGE_DATE_RANGE_FAIL')
    allx=pd.concat([hist[hist.date<CHALLENGE_START],ch],ignore_index=True).sort_values('date').drop_duplicates('date',keep='last').reset_index(drop=True)
    allx=allx[allx.date>=START_PREHISTORY].reset_index(drop=True)
    lab=add_roles(label_history(allx)); lab=add_signals(lab)
    # state machine is allowed to carry pre-2025 state, but challenge episode metrics clip at first governed 2025 origin by subsetting here.
    full=state_trajectory(lab[lab.date>=FORMATION_START].reset_index(drop=True))
    q=full[full.date.between(CHALLENGE_START,CHALLENGE_END)].reset_index(drop=True)
    ev=q[q.is_break].copy().reset_index(drop=True); ev['event_id']=[f'C{i:03d}' for i in range(1,len(ev)+1)]
    event_dates=set(pd.to_datetime(ev.date))
    if not len(ev): raise RuntimeError('NO_2025_CHALLENGE_EVENTS')
    fast_ep=boolean_episodes(q,'fast_conflict',event_dates); path_ep=boolean_episodes(q,'path_half',event_dates)
    weak_ep=state_episodes(q,{'WEAKENING','BREAK_ALERT'},event_dates); alert_ep=state_episodes(q,{'BREAK_ALERT'},event_dates)
    fast=ep_metrics(fast_ep,len(ev),len(q)); path=ep_metrics(path_ep,len(ev),len(q)); weak=ep_metrics(weak_ep,len(ev),len(q)); alert=ep_metrics(alert_ep,len(ev),len(q))
    ceiling=float(protocol['primary_gate']['dual_lane_false_warning_episodes_per_100_max'])
    fast_lead=fast['median_lead_observations'] if fast['median_lead_observations'] is not None else -1.0
    weak_lead=weak['median_lead_observations'] if weak['median_lead_observations'] is not None else -1.0
    passed=weak['prebreak_event_recall']>=fast['prebreak_event_recall'] and weak_lead>fast_lead and weak['false_episodes_per_100_origins']<=ceiling
    status='CHALLENGE_MONITORING_SIGNAL_SUPPORTED' if passed else 'CHALLENGE_NOT_SUPPORTED'
    summary={'audit_id':'GC_BREAK_WP4C_2025_CHALLENGE_V1','status':status,'architecture_contract':arch['contract_id'],'challenge_protocol':protocol['protocol_id'],
             'challenge_origins':int(len(q)),'challenge_break_events':int(len(ev)),'challenge_origin_min':q.date.min().date().isoformat(),'challenge_origin_max':q.date.max().date().isoformat(),
             'FAST_CONFLICT':fast,'PATH_HALF_ANATOMY_REFERENCE':path,'WP4C_DUAL_LANE_WEAKENING':weak,'WP4C_DUAL_LANE_BREAK_ALERT':alert,
             'primary_gate':{'passed':bool(passed),'false_warning_ceiling':ceiling,'dual_recall_at_least_fast':bool(weak['prebreak_event_recall']>=fast['prebreak_event_recall']),
                             'dual_lead_strictly_greater_fast':bool(weak_lead>fast_lead),'dual_false_burden_within_ceiling':bool(weak['false_episodes_per_100_origins']<=ceiling)},
             'claim_separation':'Any gain from PATH_HALF is structural health/condition monitoring, not independent predictive evidence. FAST remains the independent tactical evidence lane; SLOW remains confirmation.',
             'post_challenge_tuning_performed':False,'stress_2026_accessed':False,'database_write':'NONE','production_authority':False,'prospective_claim':False}
    q.to_csv(a.output_dir/'gc_break_wp4c_2025_challenge_panel_v1.csv',index=False); ev.to_csv(a.output_dir/'gc_break_wp4c_2025_challenge_events_v1.csv',index=False)
    fast_ep.to_csv(a.output_dir/'gc_break_wp4c_2025_fast_conflict_episodes_v1.csv',index=False); path_ep.to_csv(a.output_dir/'gc_break_wp4c_2025_path_half_episodes_v1.csv',index=False); weak_ep.to_csv(a.output_dir/'gc_break_wp4c_2025_dual_lane_weakening_episodes_v1.csv',index=False); alert_ep.to_csv(a.output_dir/'gc_break_wp4c_2025_dual_lane_break_alert_episodes_v1.csv',index=False)
    (a.output_dir/'gc_break_wp4c_2025_challenge_v1_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)); return 0

if __name__=='__main__': raise SystemExit(main())
