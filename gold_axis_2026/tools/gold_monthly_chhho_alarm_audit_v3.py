from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

HIGH_AE = 63.06
HIGH_APE = 2.96117
HIGH_RETURN_ERROR_PP = 3.00590
EXPECTED_DEV = {
    'A':['2022-11','2023-08'],
    'B':['2023-01','2023-02','2023-05'],
    'C':['2024-07'],
    'D':['2024-11'],
}

def mshift(m,d):
    y,mo=map(int,m.split('-')); z=y*12+mo-1+d
    return f'{z//12:04d}-{z%12+1:02d}'

def load_json(p): return json.loads(Path(p).read_text())

def build_markets(snapshot, public):
    snap=snapshot['payload']
    daily=list(snap['daily_common_rows'])+list(public['daily_extension_rows'])
    df=pd.DataFrame(daily)
    df['date']=pd.to_datetime(df['date'])
    df=df.sort_values('date').drop_duplicates('date',keep='last')
    df['month']=df.date.dt.strftime('%Y-%m')
    legacy=df.groupby('month')[['Gold','Silver','Platinum','Palladium']].mean().sort_index()
    corrected=legacy.copy()
    gold={k:float(v) for k,v in snap['core_gold'].items()}
    gold.update({k:float(v) for k,v in public['world_bank']['gold_monthly'].items()})
    for k,v in gold.items(): corrected.loc[k,'Gold']=v
    corrected=corrected.sort_index()
    for market in (legacy,corrected):
        for c in ['Gold','Silver','Platinum','Palladium']:
            market[c+'_r1']=np.log(market[c]/market[c].shift(1))
        market['Gold_r3']=np.log(market.Gold/market.Gold.shift(3))
        market['Gold_ma12_prior']=market.Gold.shift(1).rolling(12,min_periods=12).mean()
        market['Gold_vs_ma12']=market.Gold/market.Gold_ma12_prior-1
    return corrected,legacy,gold

def series_df(store,key):
    rows=[]
    for ds,v in store.items():
        val=v.get(key) if isinstance(v,dict) else v
        if val is not None:
            rows.append((pd.Timestamp(ds),float(val)))
    return pd.DataFrame(rows,columns=['date','value']).sort_values('date')

def mm(df,m,lag):
    p=pd.Period(m,freq='M'); cut=p.end_time.normalize()-pd.Timedelta(days=lag)
    z=df[(df.date.dt.to_period('M')==p)&(df.date<=cut)]
    if z.empty: raise RuntimeError(f'MACRO_MONTH_EMPTY {m} lag={lag}')
    return float(z.value.mean())

def build_macro(external):
    broad=series_df(external['h10_daily'],'BROAD_USD_INDEX')
    nominal=series_df(external['h15_daily'],'DGS10')
    real=series_df(external['h15_daily'],'DFII10')
    cache={}
    def state(m):
        if m in cache: return cache[m]
        pm=mshift(m,-1)
        nc,npv=mm(nominal,m,2),mm(nominal,pm,2)
        rc,rpv=mm(real,m,2),mm(real,pm,2)
        uc,upv=mm(broad,m,7),mm(broad,pm,7)
        cache[m]={
            'nom10_change':nc-npv,
            'real10_change':rc-rpv,
            'broad_usd_logchg':math.log(uc/upv),
        }
        return cache[m]
    return state

def state_row(market,origin):
    s=market.loc[origin]
    return {
        'Gold_r1':float(s.Gold_r1),
        'Silver_r1':float(s.Silver_r1),
        'Platinum_r1':float(s.Platinum_r1),
        'Palladium_r1':float(s.Palladium_r1),
        'Gold_r3':float(s.Gold_r3),
        'Gold_vs_ma12':float(s.Gold_vs_ma12),
        'Gold_level':float(s.Gold),
    }

def alarm_flags(state,pred,macro):
    g=state['Gold_r1']
    oth=[state['Silver_r1'],state['Platinum_r1'],state['Palladium_r1']]
    opposite=sum(x*g<0 for x in oth)
    A=np.sign(pred)==np.sign(g) and abs(g)<.02 and opposite>=2
    B=(g>.03 and sum(x>0 for x in oth)>=2 and macro['broad_usd_logchg']<0
       and macro['nom10_change']<0 and macro['real10_change']<0 and pred<=.01)
    C=g<0 and macro['nom10_change']<0 and macro['real10_change']<0 and abs(pred)<.01
    D=(g>.03 and macro['broad_usd_logchg']>0 and macro['nom10_change']>0
       and macro['real10_change']>0 and pred>0)
    E=state['Gold_vs_ma12']>.20 and abs(pred-g)>.05
    G=state['Gold_r3']<=-.10
    return {
        'A':bool(A),'B':bool(B),'C':bool(C),'D':bool(D),'E':bool(E),'G':bool(G),
        'hard_alarm':bool(A or C or D or E or G),
        'opposite_metals':int(opposite),
    }

def canonical_forecasts(chhho,transport):
    rows=[]
    for sec in ['dev','transport_2025','stress_2026']:
        rows.extend(dict(r) for r in chhho[sec]['rows'])
    aug=[r for r in transport['rows_2026_jan_aug'] if r['target']=='2026-08']
    if len(aug)!=1: raise RuntimeError('AUG_2026_TRANSPORT_ROW_MISSING')
    a=aug[0]
    rows.append({
        'target':'2026-08','origin':'2026-07','forecast':float(a['forecast']),
        'actual':float(a['actual']),'rw':float(a['rw']),
        'pred_log_return_gold':math.log(float(a['forecast'])/float(a['rw'])),
        'method':'CHHHO_FROZEN_TRANSPORT'
    })
    rows.sort(key=lambda r:r['target'])
    return rows

def evaluate_row(r,market,macro_state,gold_map):
    o,t=r['origin'],r['target']; pred=float(r['pred_log_return_gold'])
    st=state_row(market,o); mac=macro_state(o); fl=alarm_flags(st,pred,mac)
    fc=float(r['forecast']); act=float(r['actual']); rw=float(r.get('rw',gold_map[o]))
    ae=abs(fc-act); ape=ae/act*100.0
    actual_ret=math.log(act/rw); ret_err_pp=abs(pred-actual_ret)*100.0
    return {
        'target':t,'origin':o,'forecast':fc,'actual':act,'rw':rw,'pred_log_return_gold':pred,
        'actual_log_return_gold':actual_ret,'ae':ae,'ape_pct':ape,'return_error_pp':ret_err_pp,
        'high_ae':bool(ae>HIGH_AE),'high_ape':bool(ape>HIGH_APE),
        'high_return_error':bool(ret_err_pp>HIGH_RETURN_ERROR_PP),
        **st,**mac,**fl,
    }

def event_lists(rows):
    return {a:[r['target'] for r in rows if r[a]] for a in 'ABCDEG'}

def summary(rows,label):
    alarm=sum(r['hard_alarm'] for r in rows)
    hi=sum(r[label] for r in rows)
    hits=sum(r['hard_alarm'] and r[label] for r in rows)
    fp=sum(r['hard_alarm'] and not r[label] for r in rows)
    miss=sum((not r['hard_alarm']) and r[label] for r in rows)
    return {
        'n':len(rows),'high_error_n':hi,'hard_alarms':alarm,'hits':hits,'false_alarms':fp,'misses':miss,
        'precision':None if hits+fp==0 else hits/(hits+fp),
        'recall':None if hits+miss==0 else hits/(hits+miss),
        'alarm_targets':[r['target'] for r in rows if r['hard_alarm']],
        'hit_targets':[r['target'] for r in rows if r['hard_alarm'] and r[label]],
        'miss_targets':[r['target'] for r in rows if (not r['hard_alarm']) and r[label]],
    }

def period(rows,a,b): return [r for r in rows if a<=r['target']<=b]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',required=True)
    ap.add_argument('--public-bundle',required=True)
    ap.add_argument('--chhho',required=True)
    ap.add_argument('--transport',required=True)
    ap.add_argument('--external',required=True)
    ap.add_argument('--predev',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args()

    snapshot,public,chhho,transport,external,predev=[load_json(p) for p in
        [a.snapshot,a.public_bundle,a.chhho,a.transport,a.external,a.predev]]
    corrected,legacy,gold_map=build_markets(snapshot,public)
    macro_state=build_macro(external)

    canonical=canonical_forecasts(chhho,transport)
    corr_rows=[evaluate_row(r,corrected,macro_state,gold_map) for r in canonical]
    legacy_rows=[evaluate_row(r,legacy,macro_state,gold_map) for r in canonical]

    corr_events=event_lists(corr_rows); legacy_events=event_lists(legacy_rows)
    dev_corr=period(corr_rows,'2022-04','2024-12')
    dev_events=event_lists(dev_corr)
    dev_gate={k:(dev_events[k]==v) for k,v in EXPECTED_DEV.items()}

    changed=[]
    legacy_by={r['target']:r for r in legacy_rows}
    for r in corr_rows:
        q=legacy_by[r['target']]
        diff=[x for x in 'ABCDEG' if r[x]!=q[x]]
        if diff:
            changed.append({
                'target':r['target'],'origin':r['origin'],'changed_flags':diff,
                'corrected':{x:r[x] for x in 'ABCDEG'},'legacy':{x:q[x] for x in 'ABCDEG'},
                'corrected_gold_r1':r['Gold_r1'],'legacy_gold_r1':q['Gold_r1'],
                'pred_log_return_gold':r['pred_log_return_gold'],
            })

    pre_rows=[evaluate_row(r,corrected,macro_state,gold_map) for r in predev['rows']]
    pre_legacy=[evaluate_row(r,legacy,macro_state,gold_map) for r in predev['rows']]

    macro_diffs=[]
    for old,new in zip(predev['rows'],pre_rows):
        macro_diffs.append({
            'target':new['target'],
            'nom10_change_abs_diff':abs(float(old['nom10_change'])-new['nom10_change']),
            'real10_change_abs_diff':abs(float(old['real10_change'])-new['real10_change']),
            'broad_usd_logchg_abs_diff':abs(float(old['broad_usd_logchg'])-new['broad_usd_logchg']),
        })
    macro_max={k:max(x[k] for x in macro_diffs) for k in
               ['nom10_change_abs_diff','real10_change_abs_diff','broad_usd_logchg_abs_diff']}
    macro_gate=max(macro_max.values())<1e-12

    legacy_reproduces_old_A = legacy_events['A']==['2022-11','2023-08','2025-09','2025-12','2026-05']
    gold_source_change_isolated = (
        len(changed)==1 and changed[0]['target']=='2026-05' and
        changed[0]['origin']=='2026-04' and changed[0]['changed_flags']==['A'] and
        changed[0]['legacy']['A'] is True and changed[0]['corrected']['A'] is False
    )

    gates={
        'dev_A_replay_exact':dev_gate['A'],
        'dev_B_replay_exact':dev_gate['B'],
        'dev_C_replay_exact':dev_gate['C'],
        'dev_D_replay_exact':dev_gate['D'],
        'predev_macro_external_authority_equivalence':macro_gate,
        'predev_rows_exactly_five':len(pre_rows)==5,
        'legacy_A_reproduces_prior_transport_event_set':legacy_reproduces_old_A,
        'canonical_gold_source_changes_only_2026_05_A_in_2022_2026':gold_source_change_isolated,
    }
    gate='PASS' if all(gates.values()) else 'FAIL'

    labels={'HIGH_AE':'high_ae','HIGH_APE':'high_ape','HIGH_RETURN_ERROR':'high_return_error'}
    summaries={}
    for pname,bounds in {
        'PREDEV_V2_VALID_WINDOW':('2021-11','2022-03'),
        'DEV':('2022-04','2024-12'),
        '2025':('2025-01','2025-12'),
        '2026_JAN_AUG':('2026-01','2026-08'),
    }.items():
        src=pre_rows if pname.startswith('PREDEV') else corr_rows
        z=period(src,*bounds)
        summaries[pname]={name:summary(z,key) for name,key in labels.items()}

    out={
        'schema':'GOLD_MONTHLY_CHHHO_ALARM_AUDIT_V3_2026-09-30',
        'gate':gate,
        'gates':gates,
        'thresholds':{
            'high_ae_usd_gt':HIGH_AE,'high_ape_pct_gt':HIGH_APE,
            'high_return_error_pp_gt':HIGH_RETURN_ERROR_PP,
        },
        'authority':{
            'snapshot_artifact':10985453248,'public_bundle_artifact':11015874673,
            'chhho_artifact':10989389723,'transport_artifact':11042740289,
            'external_authority_v2_artifact':11028494060,'predev_v2_artifact':11084467079,
            'gold_state_source':'CORE5/WorldBank canonical monthly Gold',
            'other_metals_source':'governed common-daily monthly means',
            'macro_source':'External Authority V2 H10/H15',
            'model_rerun':False,'threshold_retuning':False,'routing_tested':False,
        },
        'dev_replay':{'expected':EXPECTED_DEV,'actual':{k:dev_events[k] for k in 'ABCD'}},
        'corrected_event_lists':corr_events,
        'legacy_common_daily_gold_event_lists':legacy_events,
        'gold_source_changed_alarm_events':changed,
        'predev_macro_equivalence':{'rows':macro_diffs,'max_abs_diff':macro_max},
        'predev_corrected_event_lists':event_lists(pre_rows),
        'predev_legacy_event_lists':event_lists(pre_legacy),
        'predev_rows':pre_rows,
        'summaries':summaries,
        'governance':{
            'v1_old_gpr_invalid':True,
            'v2_forecasts_retained_alarm_booleans_superseded':True,
            'B_warning_only':True,
            'hard_alarm_definition':'A_OR_C_OR_D_OR_E_OR_G',
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V3_GATE='+gate)
    print(json.dumps({
        'gates':gates,'changed':changed,'predev_events':event_lists(pre_rows),
        'predev_summaries':summaries['PREDEV_V2_VALID_WINDOW'],
        'corrected_events':corr_events,
    },sort_keys=True))
    if gate!='PASS': raise SystemExit(2)

if __name__=='__main__': main()
