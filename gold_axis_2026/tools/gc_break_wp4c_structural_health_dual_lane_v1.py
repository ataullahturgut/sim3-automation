from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def root() -> Path:
    here=Path(__file__).resolve()
    for p in here.parents:
        if (p/'gc_break_v0'/'gc_break_wp4c_structural_health_dual_lane_freeze_v1.json').exists(): return p
    raise RuntimeError('PROJECT_ROOT_NOT_FOUND')


def same(state:str, regime:str)->bool:
    return (regime=='UP' and state=='ROBUST_UP') or (regime=='DOWN' and state=='ROBUST_DOWN')

def opposite(state:str, regime:str)->bool:
    return (regime=='UP' and state=='ROBUST_DOWN') or (regime=='DOWN' and state=='ROBUST_UP')


def trajectory(panel:pd.DataFrame)->pd.DataFrame:
    p=panel.sort_values('date').reset_index(drop=True)
    regime=str(p.loc[0,'regime_pre'])
    if regime not in {'UP','DOWN'}: raise RuntimeError('INITIAL_REGIME_MISSING')
    state='STABLE'; rows=[]
    for _,r in p.iterrows():
        fs=str(r.fast_state); ss=str(r.slow_state) if pd.notna(r.slow_state) else 'MISSING'
        f_same=same(fs,regime); f_opp=opposite(fs,regime); f_conf=not f_same
        path=bool(r.path_half); weak=path or f_conf; strong=f_opp or (path and f_conf)
        before_state=state; before_regime=regime; br=bool(r.wp2_break_flag); reason='HOLD'
        if br:
            state='CONFIRMED_BREAK'; regime='DOWN' if regime=='UP' else 'UP'; reason='FROZEN_CURRENT_ORIGIN_BREAK'
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
        rows.append({'date':r.date,'close':r.close,'event_id':r.event_id,'wp2_break_flag':br,
                     'regime_before':before_regime,'regime_after':regime,'state_before':before_state,'state_after':state,
                     'transition_reason':reason,'path_half_structural_health':path,'fast_state':fs,'slow_state':ss,
                     'fast_same':f_same,'fast_conflict':f_conf,'fast_opposite':f_opp})
    return pd.DataFrame(rows)


def episodes(tr:pd.DataFrame, states:set[str], label:str)->pd.DataFrame:
    on=tr.state_after.isin(states).to_numpy(); out=[]; start=None
    for i,flag in enumerate(on):
        if flag and start is None: start=i
        if start is None: continue
        next_break=(i+1<len(tr) and bool(tr.loc[i+1,'wp2_break_flag']))
        end_now=(i==len(tr)-1 or not flag or next_break or (flag and i+1<len(tr) and not on[i+1]))
        if not end_now: continue
        end=i if flag else i-1
        if end>=start:
            converted=bool(end+1<len(tr) and tr.loc[end+1,'wp2_break_flag'])
            bd=pd.Timestamp(tr.loc[end+1,'date']) if converted else pd.NaT
            out.append({'episode_type':label,'episode_id':len(out)+1,'start_i':start,'end_i':end,
                        'start_date':pd.Timestamp(tr.loc[start,'date']),'end_date':pd.Timestamp(tr.loc[end,'date']),
                        'converted':converted,'break_date':bd,
                        'lead_observations':end+1-start if converted else np.nan,
                        'lead_calendar_days':(bd-pd.Timestamp(tr.loc[start,'date'])).days if converted else np.nan,
                        'recovered_to_stable':bool((not converted) and end+1<len(tr) and tr.loc[end+1,'state_after']=='STABLE')})
        start=None
    return pd.DataFrame(out)


def metrics(ep:pd.DataFrame,n_events:int,n_origins:int)->dict:
    if ep.empty:
        return {'episodes':0,'converted_episodes':0,'false_episodes':0,'prebreak_event_recall':0.0,'false_episodes_per_100_origins':0.0,'median_lead_observations':None,'median_lead_calendar_days':None,'episode_conversion_rate':None,'recovery_episode_count':0,'recovery_rate_before_break':None}
    c=ep[ep.converted]; f=ep[~ep.converted]
    return {'episodes':int(len(ep)),'converted_episodes':int(len(c)),'false_episodes':int(len(f)),
            'prebreak_event_recall':float(pd.to_datetime(c.break_date).nunique()/n_events),
            'false_episodes_per_100_origins':float(len(f)*100.0/n_origins),
            'median_lead_observations':float(c.lead_observations.median()) if len(c) else None,
            'median_lead_calendar_days':float(c.lead_calendar_days.median()) if len(c) else None,
            'episode_conversion_rate':float(len(c)/len(ep)),
            'recovery_episode_count':int(f.recovered_to_stable.fillna(False).sum()),
            'recovery_rate_before_break':float(f.recovered_to_stable.fillna(False).mean()) if len(f) else None}


def confirmation(tr:pd.DataFrame,events:pd.DataFrame)->dict:
    pos={pd.Timestamp(d):i for i,d in enumerate(pd.to_datetime(tr.date))}; rows=[]
    for j,ev in events.reset_index(drop=True).iterrows():
        b=pd.Timestamp(ev.break_date); bi=pos[b]; ni=pos[pd.Timestamp(events.iloc[j+1].break_date)] if j+1<len(events) else len(tr)
        fi=next((i for i in range(bi+1,ni) if tr.loc[i,'state_after']=='NEW_REGIME'),None)
        rows.append({'event_id':ev.event_id,'break_date':b,'confirmed_before_next_break':fi is not None,
                     'confirmation_date':pd.Timestamp(tr.loc[fi,'date']) if fi is not None else pd.NaT,
                     'delay_observations':fi-bi if fi is not None else np.nan,
                     'delay_calendar_days':(pd.Timestamp(tr.loc[fi,'date'])-b).days if fi is not None else np.nan})
    d=pd.DataFrame(rows); v=d[d.confirmed_before_next_break]
    return {'rows':d,'metrics':{'events':int(len(d)),'confirmed_before_next_break':int(len(v)),
            'confirmation_rate_before_next_break':float(len(v)/len(d)),
            'median_confirmation_delay_observations':float(v.delay_observations.median()) if len(v) else None,
            'median_confirmation_delay_calendar_days':float(v.delay_calendar_days.median()) if len(v) else None}}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--panel',type=Path,required=True); ap.add_argument('--events',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True)
    a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    c=json.loads((root()/'gc_break_v0'/'gc_break_wp4c_structural_health_dual_lane_freeze_v1.json').read_text())
    if c.get('status')!='FORMATION_INFORMED_DEVELOPMENT_LOCK_BEFORE_CHALLENGE': raise RuntimeError('WP4C_LOCK_STATUS_FAIL')
    p=pd.read_csv(a.panel,parse_dates=['date']); e=pd.read_csv(a.events,parse_dates=['trade_date']).rename(columns={'trade_date':'break_date'})
    if len(p)!=351 or len(e)!=21: raise RuntimeError(f'FORMATION_SUPPORT_FAIL:{len(p)}:{len(e)}')
    tr=trajectory(p); w=episodes(tr,{'WEAKENING','BREAK_ALERT'},'WEAKENING_OR_HIGHER'); ba=episodes(tr,{'BREAK_ALERT'},'BREAK_ALERT'); conf=confirmation(tr,e)
    wm=metrics(w,len(e),len(tr)); bm=metrics(ba,len(e),len(tr))
    ref=c['formation_development_reference']['FAST_CONFLICT']; ceiling=c['formation_development_reference']['PATH_HALF_ANATOMY']['false_episodes_per_100_origins']
    pos=wm['prebreak_event_recall']>=ref['prebreak_event_recall'] and wm['median_lead_observations']>ref['median_lead_observations'] and wm['false_episodes_per_100_origins']<=ceiling
    status='FORMATION_MONITORING_SIGNAL_REPRODUCED_CHALLENGE_REQUIRED' if pos else 'FORMATION_FEASIBILITY_NOT_REPRODUCED'
    out={'audit_id':'GC_BREAK_WP4C_STRUCTURAL_HEALTH_DUAL_LANE_FORMATION_REPRO_V1','contract_id':c['contract_id'],'contract_status':c['status'],
         'status':status,'formation_origins':len(p),'formation_break_events':len(e),'weakening':wm,'break_alert':bm,'confirmation':conf['metrics'],
         'reference_fast_conflict':ref,'anatomy_false_warning_ceiling':ceiling,
         'interpretation':'Monitoring performance may legitimately use the causal structural-health lane, but any improvement attributable to PATH_HALF is anatomy/condition-monitoring evidence, not an independent predictive claim. 2025 challenge is required before promotion.',
         'challenge_2025_accessed':False,'stress_2026_accessed':False,'database_write':'NONE','production_authority':False,'prospective_claim':False}
    tr.to_csv(a.output_dir/'gc_break_wp4c_state_trajectory_formation_v1.csv',index=False); w.to_csv(a.output_dir/'gc_break_wp4c_weakening_episodes_formation_v1.csv',index=False); ba.to_csv(a.output_dir/'gc_break_wp4c_break_alert_episodes_formation_v1.csv',index=False); conf['rows'].to_csv(a.output_dir/'gc_break_wp4c_confirmation_formation_v1.csv',index=False)
    (a.output_dir/'gc_break_wp4c_formation_reproduction_v1_summary.json').write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)); return 0

if __name__=='__main__': raise SystemExit(main())
