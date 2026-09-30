from __future__ import annotations
import argparse,json
from pathlib import Path

MEDIUM_LO=2.50
HIGH_LO=3.00

def load(p): return json.loads(Path(p).read_text())
def sev(x):
    x=float(x)
    if x>=HIGH_LO: return 'HIGH'
    if x>=MEDIUM_LO: return 'MEDIUM'
    return 'NORMAL'

def period(rows,a,b): return [r for r in rows if a<=r['target']<=b]

def score(rows,flag,pred):
    ev=[r for r in rows if r[flag]]
    err=[r for r in rows if pred(r)]
    hits=[r for r in ev if pred(r)]
    fps=[r for r in ev if not pred(r)]
    miss=[r for r in err if not r[flag]]
    return {
        'n':len(rows),'events':len(ev),'error_n':len(err),'hits':len(hits),
        'false_alarms':len(fps),'misses':len(miss),
        'precision':None if not ev else len(hits)/len(ev),
        'recall':None if not err else len(hits)/len(err),
        'alarm_targets':[r['target'] for r in ev],
        'hit_targets':[r['target'] for r in hits],
        'miss_targets':[r['target'] for r in miss],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    src=load(a.input)
    if src.get('schema')!='GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V2_2026-09-30':
        raise RuntimeError(('BAD_INPUT_SCHEMA',src.get('schema')))

    rows=[]
    disagreements=[]
    for x in src['rows']:
        r=dict(x)
        r['ape_severity']=sev(r['ape_pct'])
        r['return_severity']=sev(r['return_error_pp'])
        r['ape_medium']=r['ape_severity']=='MEDIUM'
        r['ape_high']=r['ape_severity']=='HIGH'
        r['ape_elevated']=r['ape_severity'] in ('MEDIUM','HIGH')
        if r['ape_severity']!=r['return_severity']:
            disagreements.append({
                'target':r['target'],'origin':r['origin'],
                'ape_pct':r['ape_pct'],'return_error_pp':r['return_error_pp'],
                'ape_severity':r['ape_severity'],'return_severity':r['return_severity'],
            })
        rows.append(r)

    periods={
        'PREDEV_VALID':('2021-11','2022-03'),
        'DEV':('2022-04','2024-12'),
        '2025':('2025-01','2025-12'),
        '2026_JAN_AUG':('2026-01','2026-08'),
        'ALL_USABLE':('2021-11','2026-08'),
    }
    flags=['A','B','C','D','H','ABCDH','E','G','GVZ_Q80','GVZ_Q90',
           'OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']
    scores={}
    sev_by_period={}
    for p,rng in periods.items():
        z=period(rows,*rng)
        scores[p]={
            'HIGH':{f:score(z,f,lambda r:r['ape_high']) for f in flags},
            'ELEVATED_MEDIUM_PLUS_HIGH':{f:score(z,f,lambda r:r['ape_elevated']) for f in flags},
        }
        sev_by_period[p]={
            'n':len(z),
            'normal_n':sum(r['ape_severity']=='NORMAL' for r in z),
            'medium_n':sum(r['ape_severity']=='MEDIUM' for r in z),
            'high_n':sum(r['ape_severity']=='HIGH' for r in z),
            'medium_targets':[r['target'] for r in z if r['ape_severity']=='MEDIUM'],
            'high_targets':[r['target'] for r in z if r['ape_severity']=='HIGH'],
        }

    high_misses=[r for r in rows if r['ape_high'] and not r['ABCDH']]
    medium_misses=[r for r in rows if r['ape_medium'] and not r['ABCDH']]

    out={
        'schema':'GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30',
        'status':'COMPLETE',
        'primary_severity_metric':'APE',
        'severity_definition':{
            'NORMAL':'APE < 2.50%',
            'MEDIUM':'2.50% <= APE < 3.00%',
            'HIGH':'APE >= 3.00%',
        },
        'robustness_metric':'ABS_LOG_RETURN_ERROR_PP',
        'severity_by_period':sev_by_period,
        'ape_high_targets':[r['target'] for r in rows if r['ape_high']],
        'ape_medium_targets':[r['target'] for r in rows if r['ape_medium']],
        'return_vs_ape_disagreements':disagreements,
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
        'rows':rows,
        'governance':{
            'model_rerun':False,
            'alarm_rules_retuned':False,
            'routing_tested':False,
            'sum_abs_error_project_metric_changed':False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('OUTPUT_GATE=PASS')
    print(json.dumps({
        'severity_by_period':sev_by_period,
        'disagreements':disagreements,
        'ABCDH_HIGH':{p:scores[p]['HIGH']['ABCDH'] for p in periods},
        'ABCDH_ELEVATED':{p:scores[p]['ELEVATED_MEDIUM_PLUS_HIGH']['ABCDH'] for p in periods},
        'individual_HIGH':{p:{f:scores[p]['HIGH'][f] for f in ['A','B','C','D','H']} for p in periods},
        'high_misses':out['high_misses_after_ABCDH'],
        'medium_misses':out['medium_misses_after_ABCDH'],
    },sort_keys=True))

if __name__=='__main__': main()
