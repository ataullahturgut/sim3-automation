from __future__ import annotations
import argparse, json, math
from pathlib import Path
import pandas as pd

import gold_monthly_chhho_alarm_audit_v3 as v3
import gold_monthly_chhho_efg_alarm_audit_v1 as efg
import gold_monthly_chhho_miss_mechanism_screen_v2 as ms

APPROX_HIGH_AE=63.06
APPROX_HIGH_APE=2.96117
APPROX_HIGH_RET_PP=3.00590

H_MMNET_CHG=0.1499821
H_OI_PCT=0.149766

def load(p): return json.loads(Path(p).read_text())
def period(rows,a,b): return [r for r in rows if a<=r['target']<=b]

def combine_forecasts(pre,ch,transport,gold_map):
    rows=[]
    rows.extend(dict(r) for r in pre['rows'])
    for sec in ['dev','transport_2025','stress_2026']:
        rows.extend(dict(r) for r in ch[sec]['rows'])
    aug=[r for r in transport['rows_2026_jan_aug'] if r['target']=='2026-08']
    if len(aug)!=1: raise RuntimeError('AUG_MISSING')
    a=aug[0]
    rows.append({
        'target':'2026-08','origin':'2026-07',
        'forecast':float(a['forecast']),'actual':float(a['actual']),
        'rw':float(a['rw']),
        'pred_log_return_gold':math.log(float(a['forecast'])/float(a['rw']))
    })
    out={}
    for r in rows:
        z=dict(r)
        o=z['origin']
        rw=float(z.get('rw',gold_map[o]))
        pred=float(z['pred_log_return_gold'])
        actual=float(z['actual']); forecast=float(z['forecast'])
        ar=math.log(actual/rw)
        ae=abs(forecast-actual)
        ape=ae/actual*100.0
        re=abs(pred-ar)*100.0
        z.update({
            'rw':rw,'ae':ae,'ape_pct':ape,'return_error_pp':re
        })
        out[z['target']]=z
    return out

def score(rows,flag,label='high_return_error'):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in rows if r[label]]
    hits=[r for r in ev if r[label]]
    fps=[r for r in ev if not r[label]]
    miss=[r for r in hi if not r[flag]]
    return {
        'n':len(rows),'events':len(ev),'high_error_n':len(hi),
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
    forecasts=combine_forecasts(pre,ch,transport,gold_map)

    monthly=efg.build_market(snapshot['payload'],public)
    gvz,gvzmeta=efg.download_gvz()
    cot,cotmeta=efg.download_cftc()
    cotm=efg.cftc_monthly_pit(cot,start='2010-01',end='2026-08')
    th=ms.thresholds_2010_2020(monthly,gvz,cotm)

    # Scientific replay guard for frozen H.
    if abs(th['cftc_abs_mmnet_chg_q90']-H_MMNET_CHG)>5e-7:
        raise RuntimeError(('H_MMNET_THRESHOLD_DRIFT',th['cftc_abs_mmnet_chg_q90']))
    if abs(th['cftc_abs_oi_pct_q90']-H_OI_PCT)>5e-7:
        raise RuntimeError(('H_OI_THRESHOLD_DRIFT',th['cftc_abs_oi_pct_q90']))

    ft=ms.feature_table(monthly,gvz,cotm,th)

    rows=[]
    for t in sorted(forecasts):
        if not ('2021-11'<=t<='2026-08'): continue
        r=forecasts[t]; o=r['origin']; pred=float(r['pred_log_return_gold'])
        st=v3.state_row(market,o); mac=macro(o); fl=v3.alarm_flags(st,pred,mac)
        x=ft.loc[o]
        H=bool(x.CFTC_SHIFT)
        row={
            'target':t,'origin':o,
            'forecast':float(r['forecast']),'actual':float(r['actual']),'rw':float(r['rw']),
            'ae':float(r['ae']),'ape_pct':float(r['ape_pct']),
            'return_error_pp':float(r['return_error_pp']),
            'A':fl['A'],'B':fl['B'],'C':fl['C'],'D':fl['D'],'E':fl['E'],'G':fl['G'],
            'H':H,
            'ACD':bool(fl['A'] or fl['C'] or fl['D']),
            'ABCD':bool(fl['A'] or fl['B'] or fl['C'] or fl['D']),
            'ABCDH':bool(fl['A'] or fl['B'] or fl['C'] or fl['D'] or H),
            'GVZ_Q80':bool(x.GVZ_Q80),'GVZ_Q90':bool(x.GVZ_Q90),
            'OI_COMPRESSION':bool(x.OI_COMPRESSION),
            'POSITION_EXTREME':bool(x.POSITION_EXTREME),
            'FLOW_2OF4':bool(x.FLOW_2OF4),
        }
        rows.append(row)

    # Freeze exact DEV Q3 thresholds from the authoritative 33-row DEV distribution.
    # This avoids boundary changes caused only by rounded display constants.
    dev_rows=[r for r in rows if '2022-04'<=r['target']<='2024-12']
    if len(dev_rows)!=33:
        raise RuntimeError(('DEV_ROW_COUNT',len(dev_rows)))
    exact_high_ae=float(pd.Series([r['ae'] for r in dev_rows]).quantile(.75))
    exact_high_ape=float(pd.Series([r['ape_pct'] for r in dev_rows]).quantile(.75))
    exact_high_ret=float(pd.Series([r['return_error_pp'] for r in dev_rows]).quantile(.75))
    if abs(exact_high_ae-APPROX_HIGH_AE)>.05:
        raise RuntimeError(('AE_Q3_DRIFT',exact_high_ae))
    if abs(exact_high_ape-APPROX_HIGH_APE)>.001:
        raise RuntimeError(('APE_Q3_DRIFT',exact_high_ape))
    if abs(exact_high_ret-APPROX_HIGH_RET_PP)>.001:
        raise RuntimeError(('RETURN_Q3_DRIFT',exact_high_ret))
    for r in rows:
        r['high_ae']=bool(r['ae']>exact_high_ae)
        r['high_ape']=bool(r['ape_pct']>exact_high_ape)
        r['high_return_error']=bool(r['return_error_pp']>exact_high_ret)

    periods={
        'PREDEV_VALID':('2021-11','2022-03'),
        'DEV':('2022-04','2024-12'),
        '2025':('2025-01','2025-12'),
        '2026_JAN_AUG':('2026-01','2026-08'),
        'ALL_USABLE':('2021-11','2026-08'),
    }
    flags=['A','B','C','D','H','ACD','ABCD','ABCDH','E','G','GVZ_Q80','GVZ_Q90',
           'OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']
    scores={p:{f:score(period(rows,*rng),f,'high_return_error') for f in flags}
            for p,rng in periods.items()}

    labels=['high_ae','high_ape','high_return_error']
    label_targets={lab:[r['target'] for r in rows if r[lab]] for lab in labels}
    disagreements=[]
    for r in rows:
        vals=(r['high_ae'],r['high_ape'],r['high_return_error'])
        if len(set(vals))>1:
            disagreements.append({
                'target':r['target'],'origin':r['origin'],
                'ae':r['ae'],'ape_pct':r['ape_pct'],'return_error_pp':r['return_error_pp'],
                'high_ae':r['high_ae'],'high_ape':r['high_ape'],
                'high_return_error':r['high_return_error'],
                'A':r['A'],'B':r['B'],'C':r['C'],'D':r['D'],'H':r['H'],
            })

    # New primary-error misses after all currently repeated/frozen A/B/C/D/H mechanisms.
    primary_misses=[r for r in rows if r['high_return_error'] and not r['ABCDH']]

    out={
        'schema':'GOLD_MONTHLY_CHHHO_ERROR_LABEL_REVISION_V1_2026-09-30',
        'status':'COMPLETE',
        'primary_alarm_error_label':'HIGH_RETURN_ERROR',
        'thresholds':{
            'high_return_error_pp_gt_exact_dev_q3':exact_high_ret,
            'high_ape_pct_gt_exact_dev_q3':exact_high_ape,
            'high_ae_usd_gt_exact_dev_q3':exact_high_ae,
            'display_reference_return_error_pp':APPROX_HIGH_RET_PP,
            'display_reference_ape_pct':APPROX_HIGH_APE,
            'display_reference_ae_usd':APPROX_HIGH_AE,
            'H_mmnet_oi_monthly_abs_change_ge':H_MMNET_CHG,
            'H_oi_monthly_abs_pct_change_ge':H_OI_PCT,
        },
        'label_targets':label_targets,
        'label_counts':{k:len(v) for k,v in label_targets.items()},
        'label_disagreements':disagreements,
        'scores_primary_return_error':scores,
        'primary_return_error_misses_after_ABCDH':[
            {k:r[k] for k in ['target','origin','ae','ape_pct','return_error_pp','A','B','C','D','H',
                              'E','G','GVZ_Q80','GVZ_Q90','OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']}
            for r in primary_misses
        ],
        'rows':rows,
        'sources':{'gvz':gvzmeta,'cftc':cotmeta},
        'governance':{
            'model_selection_metric_changed':False,
            'project_primary_economic_metric_remains_sum_abs_error':True,
            'alarm_primary_label_changed_from_ae_to_return_error':True,
            'thresholds_retuned':False,
            'routing_tested':False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('OUTPUT_GATE=PASS')
    print(json.dumps({
        'label_counts':out['label_counts'],
        'label_targets':label_targets,
        'disagreements':disagreements,
        'ABCDH':{p:scores[p]['ABCDH'] for p in periods},
        'individual':{p:{f:scores[p][f] for f in ['A','B','C','D','H']} for p in periods},
        'primary_misses':out['primary_return_error_misses_after_ABCDH'],
    },sort_keys=True))

if __name__=='__main__': main()
