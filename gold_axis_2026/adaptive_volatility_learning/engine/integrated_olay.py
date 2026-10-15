"""Integrated, evidence-gated OLAY-02 / OGREN-03 / METRIK research engine.

Only one outcome: four-hour XAU close-to-close direction.  Historical 2023-25
macro-case snapshots from Neon, with as-of prior-four-hour XAU data, are read
from CSV. News sources and availability must be independently authenticated.
Trade execution: DISABLED. No 2026 future outcomes are imported.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from adaptive_olay import load_bars, load_events, walk, instant

ORG_IDS = tuple('ORG%02d' % i for i in range(1, 13))
HORIZON = timedelta(hours=4)
EXPERTS = ('macro', 'price', 'joint')
REQUIRED_BEFORE = 17
REQUIRED_AFTER = 16

def num(v):
    try:
        val = float(v)
        return val if math.isfinite(val) else None
    except (TypeError, ValueError):
        return None

def load_cases(path):
    results = []
    with open(path, encoding='utf-8-sig', newline='') as file:
        for r in csv.DictReader(file):
            t = instant(r['time_utc'])
            surp, before, after = (num(r.get(k)) for k in
                ('surprise', 'pre_ret4h_pct', 'future_ret4h_pct'))
            if (r['kind'] not in ('CPI', 'NFP') or surp is None or surp == 0
                or before is None or after is None
                or int(r['n_pre']) != REQUIRED_BEFORE
                or int(r['n_after']) != REQUIRED_AFTER):
                continue
            results.append(dict(id=r['event_id'],time=t,kind=r['kind'],
                candidate='ORG01' if surp < 0 else 'ORG02',
                state='UP' if before >= 0 else 'DOWN',
                pre4h=before,ret4h=after,y=int(after>0),due=t+HORIZON))
    results.sort(key=lambda x:(x['time'],x['id']))
    return results

def smoothed(items, weight, prior):
    return (sum(x['y'] for x in items) + weight*prior)/(len(items)+weight)

def experts(history, group, pre4h):
    """All inputs precede t; only matured labels are present in history."""
    baseline = smoothed(history, 4, 0.5)
    state = 'UP' if pre4h>=0 else 'DOWN'
    macro=[x for x in history if x['candidate']==group]
    price=[x for x in history if x['state']==state]
    joint=[x for x in macro if x['state']==state]
    pm=smoothed(macro,6,baseline)
    pp=smoothed(price,6,baseline)
    pj=smoothed(joint,12,(pm+pp)/2)
    return dict(base=baseline,macro=pm,price=pp,joint=pj,
                n_history=len(history),n_macro=len(macro),
                n_price=len(price),n_joint=len(joint))

def performance(rows):
    def metric(col):
        if not rows: return {'correct':0,'n':0,'brier':None}
        return {'n':len(rows),
            'correct':sum(int((r[col]>=.5)==bool(r['y'])) for r in rows),
            'brier':round(sum((r[col]-r['y'])**2 for r in rows)/len(rows),6)}
    return {col:metric(col) for col in ('base','macro','price','joint','ensemble')}

def weights(past_scored, strength=30.0):
    """Exponential online expert weighting; uses *past* out-of-sample errors."""
    if not past_scored: return {k:1/3 for k in EXPERTS}
    risk={k:sum((r[k]-r['y'])**2 for r in past_scored)/len(past_scored)
          for k in EXPERTS}
    raw={k:math.exp(-strength*risk[k]) for k in EXPERTS}
    total=sum(raw.values())
    return {k:raw[k]/total for k in EXPERTS}

def crossvalidated_history(train, warmup=8):
    score=[]
    for i in range(warmup,len(train)):
        x=train[i]
        h=[r for r in train[:i] if r['due']<=x['time']]
        score.append(dict(y=x['y'],**experts(h,x['candidate'],x['pre4h'])))
    return score

def predict(history,group,pre4h,prior_scored=(),min_total=20,min_group=8):
    p=experts(history,group,pre4h)
    w=weights(prior_scored)
    mix=sum(w[k]*p[k] for k in EXPERTS)
    p['ensemble']=mix
    p['weights']=w
    p['evidence_gate']='RESEARCH_ELIGIBLE' if (
        p['n_history']>=min_total and p['n_macro']>=min_group) else 'ABSTAIN_FEW_CASES'
    p['action']='DISABLED'
    return p

def audit(cases,year=2025,mode='frozen'):
    train=[r for r in cases if r['time'].year<year]
    earlier_cv=crossvalidated_history(train)
    collected=[]
    for x in [r for r in cases if r['time'].year==year]:
        past=[r for r in train if r['due']<=x['time']]
        scored=earlier_cv
        if mode=='prequential':
            past += [r for r in cases if r['time'].year==year
                     and r['due']<=x['time'] and r['time']<x['time']]
            scored=earlier_cv+[r for r in collected if r['due']<=x['time']]
        elif mode!='frozen': raise ValueError('Unsupported audit mode')
        p=predict(past,x['candidate'],x['pre4h'],scored)
        collected.append(dict(event_id=x['id'],at_utc=x['time'].isoformat(),
            due=x['due'],kind=x['kind'],candidate=x['candidate'],
            pre_ret4h_pct=x['pre4h'],future_ret4h_pct=x['ret4h'],
            y=x['y'],**p))
    serial=[]
    for row in collected:
        z=dict(row)
        z['due']=z['due'].isoformat()
        serial.append(z)
    return dict(year=year,mode=mode,source='NEON_XAU_M15_EVENT_SNAPSHOTS',
        target='XAU_FOUR_HOUR_FORWARD_RETURN_FROM_RELEASE_TIME',
        n_training=len(train),n_train_cv=len(earlier_cv),
        train_cv={k:performance([dict(r,ensemble=r.get('joint')) for r in earlier_cv])[k]
                  for k in ('base','macro','price','joint')},
        test=performance(collected),
        test_eligible=performance([r for r in collected if r['evidence_gate']=='RESEARCH_ELIGIBLE']),
        records=serial,
        claim='EXPLORATORY_NOT_BLIND_NOT_LIVE_NO_CAUSAL_CERTIFICATION')

def checked_source_events(event_csv):
    """Verified reporting time is a hard requirement. Do not infer one."""
    return load_events(event_csv)

def overlay_groups(events,asof,half_life_hours=24):
    """A time-decayed evidence display. These weights are NOT probabilities."""
    val={g:0.0 for g in ORG_IDS}
    proof=[]
    for e in events:
        if e['status']!='VERIFIED' or e['at']>asof: continue
        age=(asof-e['at']).total_seconds()/3600
        if age>72: continue
        strength=2**(-age/half_life_hours)
        for group in e['groups']:
            if group in val: val[group]+=strength/max(1,len(e['groups']))
        proof.append(e['id'])
    ranked=sorted(((k,round(v,5)) for k,v in val.items() if v>0),
                  key=lambda t:(-t[1],t[0]))
    return dict(active_candidates=ranked[:3],evidence_ids=proof,
        org_decision='CANDIDATE_ONLY' if ranked else 'UNKNOWN',
        weight_meaning='DECAYED_EVIDENCE_NOT_PROBABILITY')

def explain_walk(bars,events,cases,start=None,stop=None):
    """Single chronological walk: validated news AND metrics at same clock."""
    for row in walk(bars,events,cases,start=start,stop=stop):
        t=instant(row['at_utc'])
        og=overlay_groups(events,t)
        feats=row['features']
        combined=[]
        for e in events:
            if not (t-timedelta(minutes=15)<e['at']<=t): continue
            if e['status']!='VERIFIED' or e['at']!=t: continue
            g=('ORG01' if e['surprise']<0 else 'ORG02') if (
                e['kind'] in ('CPI','NFP') and e['surprise'] not in (None,0)) else None
            if not g or g not in e['groups']: continue
            # Event-based feature snapshot must use 17 contiguous pre-event bars.
            # The surrounding walk() at t has a 17-bar history ending at t.
            if feats['state']=='MISSING' or feats['r4'] is None: continue
            history=[c for c in cases if c['due']<=t]
            cv=crossvalidated_history(history)
            pred=predict(history,g,feats['r4'],cv)
            combined.append(dict(event_id=e['id'],candidate=g,
                p_up_4h_exploratory=round(pred['ensemble'],6)
                    if pred['evidence_gate']=='RESEARCH_ELIGIBLE' else None,
                expert_probs={k:round(pred[k],6) for k in ('base',)+EXPERTS},
                status=pred['evidence_gate'],
                mandatory_warning='NOT_CERTIFIED_PIT_NO_CAUSAL_VALIDATION'))
        row['integration']=dict(**og,matched_event_forecasts=combined,
            trade='DISABLED',source_requirements='FIRSTPRINT_AND_AVAILABLE_AT_VERIFIED')
        yield row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',required=True)
    sub=parser.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('audit')
    a.add_argument('--year',type=int,default=2025)
    a.add_argument('--mode',choices=('frozen','prequential'),default='frozen')
    a.add_argument('--out')
    w=sub.add_parser('walk')
    w.add_argument('--bars',required=True)
    w.add_argument('--events',required=True)
    w.add_argument('--start')
    w.add_argument('--stop')
    w.add_argument('--out',required=True)
    args=parser.parse_args()
    cases=load_cases(args.cases)
    if args.cmd=='audit':
        result=audit(cases,year=args.year,mode=args.mode)
        report=json.dumps(result,ensure_ascii=False,indent=2)
        if args.out: Path(args.out).write_text(report+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k!='records'},
                         ensure_ascii=False,indent=2))
    else:
        bars=load_bars(args.bars)
        events=checked_source_events(args.events)
        start=instant(args.start) if args.start else None
        stop=instant(args.stop) if args.stop else None
        with open(args.out,'w',encoding='utf-8') as file:
            for entry in explain_walk(bars,events,cases,start=start,stop=stop):
                file.write(json.dumps(entry,ensure_ascii=False)+'\n')
        print('Wrote',args.out)

if __name__=='__main__': main()
