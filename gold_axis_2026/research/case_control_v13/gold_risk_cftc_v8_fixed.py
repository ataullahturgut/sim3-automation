#!/usr/bin/env python3
"""Gold independent risk overlay V2: adds audited weekly CFTC positioning as lagged signal.

Inputs are historical research snapshots, not guaranteed first-publication price vintages.
Training 2023-2024 for 2025 check, 2023-2025 for 2026 (unchanged 90/95th thresholds).
NO price forecast, ANN confidence, trading signal, official realtime promise, or live writes.
"""
import argparse, csv, hashlib, io, json, math, os, zipfile
from bisect import bisect_right
from datetime import date, timedelta
from pathlib import Path
from gold_risk_release_clock_v8 import next_h10_publication, h10_is_available, cftc_conservative_is_available
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest

CFTC_EXACT={'GC':'088691','SI':'084691'}
BAD_DAY='2026-02-27'
FAMILIES={
    'BASE_14':list(range(14)),
    'BASE_14_PLUS_CFTC_7':list(range(21)),
    'CFTC_7_ONLY':list(range(14,21)),
    'METAL_GVZ_10':list(range(10)),
}
FEATURES=['au_ret5','au_ret20','au_rsi14','au_ma20_gap','au_rv5','four_metals_ret5_disp',
          'gvz_level','gvz_z252','gvz_dlog5','gvz_dlog1',
          'broadusd_h10_dlog5_last_published','broadusd_h10_dlog1_last_published',
          'dgs10_h15_change_5_lagged','dgs10_h15_last_lagged',
          'cftc_gc_net_over_oi','cftc_si_net_over_oi',
          'cftc_gc_wow_change','cftc_gc_four_week_change','cftc_si_four_week_change',
          'cftc_gc_minus_si_concentration','cftc_gc_short_over_oi']


def check(b,reason):
    if not b: raise ValueError('GOLD_RISK_V2_FAIL:'+reason)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def next_monday(d):
    """Legacy name: now returns holiday-adjusted FED H10 published-date."""
    return next_h10_publication(d).date().isoformat()

def load(rawzip,cftc_csv):
    with zipfile.ZipFile(rawzip) as z:
        o=json.loads(z.read('risk-overlay-source.json'))
    expected=o.pop('source_sha256')
    check(digest(o)==expected,'EXOGENOUS_SOURCE_HASH_MISMATCH')
    o['source_sha256']=expected
    check(not o.get('price_firstprint_certified',True),'RESEARCH_SOURCE_VINTAGE_UNCERTAINTY_REQUIRED')
    with open(cftc_csv,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        cr=list(reader)
    check(len(cr)==398,'CFTC_EXPECTED_398_WRONG_CONTRACT_COVERAGE')
    cftc={name:[] for name in CFTC_EXACT}
    seen=set()
    for r in cr:
        k=r['market']; d=r['report_date']; avail=r['earliest_conservative_usable_date']
        check(r['contract_code'].zfill(6)==CFTC_EXACT[k],'INCORRECT_COMEX_CONTRACT')
        check((d,k) not in seen,'CFTC_WEEK_DUPLICATED');seen.add((d,k))
        check(avail>d,'CFTC_PUBLICATION_LOOKAHEAD')
        check(r['release_status'] in ('UNVERIFIED_NORMAL_WEEK_7D_LAG_PROXY','PUBLISHED_CFTC_9147_25_PUB_PLUS1D'), 'UNKNOWN_PUBLICATION_STATUS')
        values={v:float(r[v]) for v in ('mm_net_fraction_oi','open_interest','managed_money_net','managed_money_short')}
        check(values['open_interest']>0,'CFTC_OI_NONPOSITIVE')
        cftc[k].append({'date':d,'available':avail,'quality':r['release_status'],**values})
    for k in cftc:
        cftc[k].sort(key=lambda x:x['date'])
        check(len(cftc[k])==199,f'CFTC_EXPECTED_199_WEEKLY_{k}')
        check(all(cftc[k][i]['date']<cftc[k][i+1]['date'] for i in range(len(cftc[k])-1)), 'CFTC_DATE_SEQUENCE')
    check(cftc['GC'][-1]['date']==cftc['SI'][-1]['date'],'DIFFERING_CFTC_MAX_DATE')
    return o,cftc,hashlib.sha256(Path(cftc_csv).read_bytes()).hexdigest()


def rsi(p):
    dr=np.diff(np.log(p[-15:])); up=np.maximum(0,dr).mean();dn=np.maximum(0,-dr).mean()
    return (100 if dn<1e-12 else 100*up/(up+dn))/100


def make_rows(o,cot):
    days=[x['date'] for x in o['prices']]
    px=np.array([x['metals'] for x in o['prices']],float); logs=np.log(px)
    gvz=o['gvz'];gdays=sorted(gvz)
    usd=o['macro']['DTWEXBGS_FRB_H10'];udays=sorted(usd)
    yld=o['macro']['DGS10_FRB_H15'];rdays=sorted(yld)
    cdays=[x['date'] for x in cot['GC']]
    check([x['date'] for x in cot['SI']]==cdays,'CFTC_GC_SI_MISMATCH')
    out=[]
    for i in range(260,len(days)-5):
        d=days[i]
        if not '2023-01-01'<=d<='2026-09-21':continue
        # The known corrupt gold quote cannot affect feature trailing lookback
        # nor any forward five-target day. Fail-closed quarantine until window clears.
        if BAD_DAY in days[i-20:i+6]:continue
        gi=bisect_right(gdays,d)
        if gi<253:continue
        gd=gdays[gi-1]
        if (date.fromisoformat(d)-date.fromisoformat(gd)).days>4:continue
        g=np.array([gvz[v] for v in gdays[gi-253:gi]],float)
        # H10 previous-week observation: released following Monday 16:15 NY;
        # choose only macro rows whose official-cycle date <= origin.
        valid_u=[k for k in udays if h10_is_available(k,d)]
        valid_r=[k for k in rdays if (date.fromisoformat(k)+timedelta(days=1)).isoformat()<=d]
        if len(valid_u)<6 or len(valid_r)<6:continue
        valid_c=[j for j,v in enumerate(cot['GC']) if cftc_conservative_is_available(v['available'],d)]
        if len(valid_c)<5:continue
        ci=valid_c[-1]
        # fail closed when old report >21 calendar days since effective availability
        age=(date.fromisoformat(d)-date.fromisoformat(cot['GC'][ci]['available'])).days
        if age>21:continue
        curr_c=cot['GC'][ci];curr_s=cot['SI'][ci]
        check(cftc_conservative_is_available(curr_s['available'],d) and cftc_conservative_is_available(curr_c['available'],d),'CFTC_FUTURE_RELEASE')
        check(curr_c['date']==curr_s['date'],'CFTC_REPORT_DATE_ALIGNMENT')
        u=np.array([usd[k] for k in valid_u[-6:]],float)
        y=np.array([yld[k] for k in valid_r[-6:]],float)
        gc=lambda j:cot['GC'][j]['mm_net_fraction_oi']
        si=lambda j:cot['SI'][j]['mm_net_fraction_oi']
        features=[
            logs[i,0]-logs[i-5,0],logs[i,0]-logs[i-20,0],
            rsi(px[i-14:i+1,0]),px[i,0]/px[i-19:i+1,0].mean()-1,
            np.std(np.diff(logs[i-5:i+1,0])),np.std(logs[i]-logs[i-5]),
            g[-1],(g[-1]-g[:-1].mean())/max(g[:-1].std(),.001),
            math.log(g[-1]/g[-6]),math.log(g[-1]/g[-2]),
            math.log(u[-1]/u[-6]),math.log(u[-1]/u[-2]),
            y[-1]-y[-6],y[-1],
            gc(ci),si(ci),gc(ci)-gc(ci-1),gc(ci)-gc(ci-4),
            si(ci)-si(ci-4),gc(ci)-si(ci),
            curr_c['managed_money_short']/curr_c['open_interest']
        ]
        check(len(features)==21 and np.isfinite(features).all(),'INVALID_FEATURES')
        next_day=px[i+1,0]/px[i,0]-1
        m5=float(np.min(px[i+1:i+6,0]/px[i,0]-1))
        out.append({
            'origin':d, 'first_target':days[i+1],'target_mature':days[i+5],
            'features':[float(x) for x in features],
            'gold_price_usd_oz':float(px[i,0]),
            'cftc_observed_position_date':curr_c['date'],
            'cftc_available_date':curr_c['available'],
            'cftc_publication_status':curr_c['quality'],
            'cftc_staleness_days':age,
            'usd_observation_date':valid_u[-1],
            'usd_release_eligible':next_monday(valid_u[-1]),
            'rate_observation_date':valid_r[-1],
            'next_day_return_pct':100*float(next_day),
            'next5_min_return_pct':100*m5,
            'y_nextday_drop3':bool(next_day<=-.03),
            'y_next5_drawdown5':bool(m5<=-.05),
            'y_next5_abs5':bool(np.max(abs(px[i+1:i+6,0]/px[i,0]-1))>=.05)
        })
    check(all(cftc_conservative_is_available(x['cftc_available_date'],x['origin']) for x in out),'CFTC_ORIGIN_LEAK')
    check(all(x['usd_release_eligible']<=x['origin'] and x['rate_observation_date']<x['origin'] for x in out),'MACRO_ORIGIN_LEAK')
    check(len(out)>650,'NOT_ENOUGH_ALIGNED_ROWS')
    return out


def compute(rows):
    thresholds={'yellow_quantile':.9,'red_quantile':.95}
    phases=[('2025','2024-12-31','2025-01-01','2025-12-31'),
            ('2026','2025-12-31','2026-01-01','2026-09-21')]
    results={};daily=[]
    for name,cut,lo,hi in phases:
        # 5-day labels are not input; fit limited to training origins before cut.
        train=[v for v in rows if v['target_mature']<=cut]
        score=[v for v in rows if lo<=v['origin']<=hi]
        check(len(train)>=400 and len(score)>=130,'INSUFFICIENT_TRAIN_VALIDATION_'+name)
        results[name]={}
        for fam,indices in FAMILIES.items():
            x=np.array([v['features'] for v in train],float)[:,indices]
            y=np.array([v['features'] for v in score],float)[:,indices]
            scaler=RobustScaler().fit(x)
            model=IsolationForest(n_estimators=200,max_samples=min(256,len(train)),
                                  contamination='auto',random_state=1701,n_jobs=1).fit(scaler.transform(x))
            fit_risk=-model.score_samples(scaler.transform(x))
            risks=-model.score_samples(scaler.transform(y))
            ycut,rcut=np.quantile(fit_risk,[thresholds['yellow_quantile'],thresholds['red_quantile']])
            score_rows=[]
            for r,risk in zip(score,risks):
                level='RED' if risk>=rcut else ('YELLOW' if risk>=ycut else 'NORMAL')
                item={k:r[k] for k in ['origin','first_target','target_mature','gold_price_usd_oz',
                   'cftc_observed_position_date','cftc_available_date','cftc_publication_status',
                   'cftc_staleness_days','next_day_return_pct','next5_min_return_pct',
                   'y_nextday_drop3','y_next5_drawdown5','y_next5_abs5']}
                item.update({'period':name,'family':fam,'risk_score':float(risk),'alert_level':level,
                             'train_threshold_yellow':float(ycut),'train_threshold_red':float(rcut)})
                daily.append(item);score_rows.append(item)
            m={'train_origins':len(train),'score_origins':len(score),
               'red_threshold':float(rcut),'yellow_threshold':float(ycut),
               'count_red':sum(t['alert_level']=='RED' for t in score_rows),
               'count_yellow':sum(t['alert_level']=='YELLOW' for t in score_rows)}
            for lab in ('y_nextday_drop3','y_next5_drawdown5','y_next5_abs5'):
                e=[x for x in score_rows if x[lab]]
                for al,levels in [('red',{'RED'}),('red_or_yellow',{'RED','YELLOW'})]:
                    alerted=[x for x in score_rows if x['alert_level'] in levels]
                    hits=[x for x in alerted if x[lab]]
                    m[lab+'_'+al]={'positive_origin_days':len(e),'alert_origin_days':len(alerted),
                     'hit_origin_days':len(hits),'miss_origin_days':len(e)-len(hits),
                     'false_alert_origin_days':len(alerted)-len(hits),
                     'precision':len(hits)/len(alerted) if alerted else None,
                     'recall':len(hits)/len(e) if e else None}
            results[name][fam]=m
    return results,daily


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-zip',required=True)
    p.add_argument('--cftc-csv',required=True)
    p.add_argument('--outdir',required=True)
    a=p.parse_args();Path(a.outdir).mkdir(parents=True,exist_ok=True)
    o,c,h=load(a.source_zip,a.cftc_csv)
    rows=make_rows(o,c)
    scores,day=compute(rows)
    key=['origin','first_target','target_mature','period','family','risk_score','alert_level',
         'cftc_observed_position_date','cftc_available_date','cftc_publication_status',
         'cftc_staleness_days','gold_price_usd_oz','next_day_return_pct','next5_min_return_pct',
         'y_nextday_drop3','y_next5_drawdown5','y_next5_abs5','train_threshold_yellow','train_threshold_red']
    with open(Path(a.outdir)/'gold_risk_v2_daily_alerts.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=key);w.writeheader();w.writerows(day)
    examples={date:{fam:{'level':x['alert_level'],'score':round(x['risk_score'],4),
                             'cftc_asof':x['cftc_available_date'],
                             'next5_drawdown_pct':round(x['next5_min_return_pct'],2)}
                             for x in day if x['origin']==date for fam in [x['family']]}
              for date in ['2026-01-22','2026-01-26','2026-01-27','2026-01-28','2026-01-29','2026-01-30','2026-02-02','2026-06-05','2026-09-01']}
    report={'version':'GOLD_RISK_CFTC_V8_RESEARCH_ONLY_H10_DATE_FIXED_20261026',
       'not_promoted_to_production':True,'original_forecast_models_changed':False,
       'next_day_crash_probability_calibrated':False,'ann_residual_error_probability_calibrated':False,
       'source_pit_vintage_certified':False,
       'source_gvz_metals_usd_rates_sha256':o['source_sha256'],
       'source_cftc_csv_sha256':h,
       'family_feature_index':FAMILIES,'feature_names':FEATURES,
       'model':'RobustScaler+IsolationForest(200,random_state=1701); 90% YELLOW 95% RED on fit-only origin anomaly score',
       'training_2025_diag':'2023-2024 only',
       'training_2026_stress':'2023-2025 only',
       'special_cftc_2025_shutdown':'publication day + 1 day per CFTC 9147-25',
       'ordinary_cftc_weeks':'position report day+7 days research proxy not official PIT proof',
       'cftc_contract_filter':CFTC_EXACT,
       'quarantined_invalid_daily_quote':BAD_DAY,
       'cutoff_2026':'2026-09-21 to allow mature five-day targets',
       'research_caveat':'2026 stress not feature-design blind, CFTC annual historical snapshots not release-by-release archived',
       'score_summary':scores,'examples_2026':examples,
       'raw_aligned_origins':len(rows)}
    (Path(a.outdir)/'gold_risk_v2_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('RISK_V2_SOURCE_AND_TIME_GATES_PASS',len(rows),h,o['source_sha256'])
    for year in ('2025','2026'):
        for fam in FAMILIES:
            t=scores[year][fam]
            print('RISK_V2_REPORT',year,fam,'red',t['count_red'],'yellow',t['count_yellow'],
                  '1D',t['y_nextday_drop3_red'],'5D',t['y_next5_drawdown5_red'])
    for d,r in examples.items():
        if r:print('RISK_V2_EXAMPLE',d,json.dumps(r,ensure_ascii=False,sort_keys=True))
    print('RISK_V2_RESEARCH_COMPLETED_NO_MODEL_OR_DB_WRITE')

if __name__=='__main__':main()
