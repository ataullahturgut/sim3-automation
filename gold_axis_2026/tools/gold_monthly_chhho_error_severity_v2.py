from __future__ import annotations
import argparse, json, math
from pathlib import Path

import pandas as pd

import gold_monthly_chhho_alarm_audit_v3 as v3
import gold_monthly_chhho_efg_alarm_audit_v1 as efg
import gold_monthly_chhho_miss_mechanism_screen_v2 as ms
import gold_monthly_chhho_error_label_revision_v1 as prev

MEDIUM_LO=2.50
HIGH_LO=3.00

def load(p): return json.loads(Path(p).read_text())
def period(rows,a,b): return [r for r in rows if a<=r['target']<=b]

def severity(x):
    x=float(x)
    if x>=HIGH_LO: return 'HIGH'
    if x>=MEDIUM_LO: return 'MEDIUM'
    return 'NORMAL'

def score(rows,flag,label_pred):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in rows if label_pred(r)]
    hits=[r for r in ev if label_pred(r)]
    fps=[r for r in ev if not label_pred(r)]
    miss=[r for r in hi if not r[flag]]
    return {
        'n':len(rows),'events':len(ev),'error_n':len(hi),
        'hits':len(hits),'false_alarms':len(fps),'misses':len(miss),
        'precision':None if not ev else len(hits)/len(ev),
        'recall':None if not hi else len(hits)/len(hi),
        'alarm_targets':[r['target'] for r in ev],
        'hit_targets':[r['target'] for r in hits],
        'miss_targets':[r['target'] for r in miss],
    }

def main():
    ap=argparse.ArgumentParser()
    for x in ['snapshot','public_bundle','chhho','transport','predev','external','output']:
        ap.add_argument('--'+x.replace('_','-'),required=True)
    a=ap.parse_args()

    snapshot=load(a.snapshot); public=load(a.public_bundle); ch=load(a.chhho)
    transport=load(a.transport); pre=load(a.predev); external=load(a.external)

    market,_,gold_map=v3.build_markets(snapshot,public)
    macro=v3.build_macro(external)
    forecasts=prev.combine_forecasts(pre,ch,transport,gold_map)

    monthly=efg.build_market(snapshot['payload'],public)
    gvz,gvzmeta=efg.download_gvz()
    cot,cotmeta=efg.download_cftc()
    cotm=efg.cftc_monthly_pit(cot,start='2010-01',end='2026-08')
    th=ms.thresholds_2010_2020(monthly,gvz,cotm)
    ft=ms.feature_table(monthly,gvz,cotm,th)

    rows=[]
    for t in sorted(forecasts):
        if not ('2021-11'<=t<='2026-08'): continue
        r=forecasts[t]; o=r['origin']; pred=float(r['pred_log_return_gold'])
        st=v3.state_row(market,o); mac=macro(o); fl=v3.alarm_flags(st,pred,mac)
        x=ft.loc[o]
        H=bool(x.CFTC_SHIFT)
        sev=severity(r['return_error_pp'])
        rows.append({
            'target':t,'origin':o,
            'forecast':float(r['forecast']),'actual':float(r['actual']),'rw':float(r['rw']),
            'ae':float(r['ae']),'ape_pct':float(r['ape_pct']),
            'return_error_pp':float(r['return_error_pp']),
            'severity':sev,
            'medium_error':bool(sev=='MEDIUM'),
            'high_error':bool(sev=='HIGH'),
            'elevated_error':bool(sev in ('MEDIUM','HIGH')),
            'A':fl['A'],'B':fl['B'],'C':fl['C'],'D':fl['D'],'E':fl['E'],'G':fl['G'],
            'H':H,
            'ACD':bool(fl['A'] or fl['C'] or fl['D']),
            'ABCD':bool(fl['A'] or fl['B'] or fl['C'] or fl['D']),
            'ABCDH':bool(fl['A'] or fl['B'] or fl['C'] or fl['D'] or H),
            'GVZ_Q80':bool(x.GVZ_Q80),'GVZ_Q90':bool(x.GVZ_Q90),
            'OI_COMPRESSION':bool(x.OI_COMPRESSION),
            'POSITION_EXTREME':bool(x.POSITION_EXTREME),
            'FLOW_2OF4':bool(x.FLOW_2OF4),
        })

    dev=period(rows,'2022-04','2024-12')
    dev_q3=float(pd.Series([r['return_error_pp'] for r in dev]).quantile(.75))

    periods={
        'PREDEV_VALID':('2021-11','2022-03'),
        'DEV':('2022-04','2024-12'),
        '2025':('2025-01','2025-12'),
        '2026_JAN_AUG':('2026-01','2026-08'),
        'ALL_USABLE':('2021-11','2026-08'),
    }
    flags=['A','B','C','D','H','ABCDH','E','G','GVZ_Q80','GVZ_Q90',
           'OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']

    def is_high(r): return r['high_error']
    def is_elevated(r): return r['elevated_error']

    scores={
        p:{
            'HIGH':{f:score(period(rows,*rng),f,is_high) for f in flags},
            'ELEVATED_MEDIUM_PLUS_HIGH':{f:score(period(rows,*rng),f,is_elevated) for f in flags},
        }
        for p,rng in periods.items()
    }

    severity_targets={
        'NORMAL':[r['target'] for r in rows if r['severity']=='NORMAL'],
        'MEDIUM':[r['target'] for r in rows if r['severity']=='MEDIUM'],
        'HIGH':[r['target'] for r in rows if r['severity']=='HIGH'],
    }
    severity_by_period={}
    for p,rng in periods.items():
        z=period(rows,*rng)
        severity_by_period[p]={
            'n':len(z),
            'normal_n':sum(r['severity']=='NORMAL' for r in z),
            'medium_n':sum(r['severity']=='MEDIUM' for r in z),
            'high_n':sum(r['severity']=='HIGH' for r in z),
            'medium_targets':[r['target'] for r in z if r['severity']=='MEDIUM'],
            'high_targets':[r['target'] for r in z if r['severity']=='HIGH'],
        }

    high_misses=[r for r in rows if r['high_error'] and not r['ABCDH']]
    medium_misses=[r for r in rows if r['medium_error'] and not r['ABCDH']]

    # Compare against superseded DEV-Q3 rule.
    q3_targets=[r['target'] for r in rows if r['return_error_pp']>dev_q3]
    high_targets=severity_targets['HIGH']
    q3_only=sorted(set(q3_targets)-set(high_targets))
    high_only=sorted(set(high_targets)-set(q3_targets))

    out={
        'schema':'GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V2_2026-09-30',
        'status':'COMPLETE',
        'severity_definition':{
            'NORMAL':'return_error_pp < 2.50',
            'MEDIUM':'2.50 <= return_error_pp < 3.00',
            'HIGH':'return_error_pp >= 3.00',
        },
        'thresholds':{'medium_pp':MEDIUM_LO,'high_pp':HIGH_LO,'superseded_dev_q3_pp':dev_q3},
        'severity_targets':severity_targets,
        'severity_by_period':severity_by_period,
        'scores':scores,
        'high_misses_after_ABCDH':[
            {k:r[k] for k in ['target','origin','ae','ape_pct','return_error_pp','A','B','C','D','H',
                              'E','G','GVZ_Q80','GVZ_Q90','OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']}
            for r in high_misses
        ],
        'medium_misses_after_ABCDH':[
            {k:r[k] for k in ['target','origin','ae','ape_pct','return_error_pp','A','B','C','D','H',
                              'E','G','GVZ_Q80','GVZ_Q90','OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']}
            for r in medium_misses
        ],
        'comparison_to_superseded_q3':{
            'q3_targets':q3_targets,
            'high_3pct_targets':high_targets,
            'q3_only_targets':q3_only,
            'high_3pct_only_targets':high_only,
        },
        'rows':rows,
        'sources':{'gvz':gvzmeta,'cftc':cotmeta},
        'governance':{
            'fixed_human_readable_thresholds':True,
            'thresholds_retuned_from_outcomes':False,
            'model_selection_metric_changed':False,
            'sum_abs_error_remains_project_metric':True,
            'routing_tested':False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('OUTPUT_GATE=PASS')
    print(json.dumps({
        'severity_by_period':severity_by_period,
        'medium_targets':severity_targets['MEDIUM'],
        'high_targets':severity_targets['HIGH'],
        'ABCDH_HIGH':{p:scores[p]['HIGH']['ABCDH'] for p in periods},
        'ABCDH_ELEVATED':{p:scores[p]['ELEVATED_MEDIUM_PLUS_HIGH']['ABCDH'] for p in periods},
        'individual_HIGH':{p:{f:scores[p]['HIGH'][f] for f in ['A','B','C','D','H']} for p in periods},
        'high_misses':out['high_misses_after_ABCDH'],
        'medium_misses':out['medium_misses_after_ABCDH'],
        'q3_compare':out['comparison_to_superseded_q3'],
    },sort_keys=True))

if __name__=='__main__': main()
