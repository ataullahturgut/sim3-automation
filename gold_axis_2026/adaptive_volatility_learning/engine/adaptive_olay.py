"""OLAY-02 / OGREN-03 adaptive research engine (stdlib; no trading actions).

Two independent modules: (1) macro release probability with strict outcome
maturity, (2) chronological market state and verified-firstprint event overlay.
Research candidate ORGs are NOT causal claims. No model uses future labels.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC = timezone.utc

def instant(s: str) -> datetime:
    t = datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
    if t.tzinfo is None:
        raise ValueError('Timezone-offset required: ' + s)
    return t.astimezone(UTC)

def read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f)

def number(s):
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None

def candidate(kind, surprise):
    """Tentative CPI/NFP headline-sign hypothesis; wage/revision omitted."""
    if kind not in ('CPI', 'NFP') or surprise is None or surprise == 0:
        return None
    return 'ORG01' if surprise < 0 else 'ORG02'

def load_macro(path):
    records=[]
    for r in read_csv(path):
        if str(r.get('arm_week_lag'))!='0' or str(r.get('overlap_other_macro_release')).lower()!='false':
            continue  # placebo and overlapping releases never counted as real
        group=candidate(r.get('kind'),number(r.get('macro_surprise')))
        if group is None: continue
        records.append(dict(id=r['release_key'],
            time=instant(r['scheduled_utc_or_placebo_utc']),group=group,
            kind=r['kind'],surprise=number(r['macro_surprise']),
            outcomes={h:number(r.get('xau_logret_post%d_pct'%h)) for h in (60,240)}))
    return sorted(records,key=lambda x:(x['time'],x['id']))

def learn_prior(history,group,horizon,alpha=4.0,min_group=8,min_total=20):
    valid=[x for x in history if x['outcomes'].get(horizon) is not None]
    cohort=[x for x in valid if x['group']==group]
    base=sum(x['outcomes'][horizon]>0 for x in valid)/len(valid) if valid else .5
    probability=(sum(x['outcomes'][horizon]>0 for x in cohort)+alpha*base)/(len(cohort)+alpha)
    values=sorted(x['outcomes'][horizon] for x in cohort)
    def quantile(p):
        return values[min(len(values)-1,round((len(values)-1)*p))] if values else None
    return dict(p_up=probability,baseline_p_up=base,n_group=len(cohort),
        n_total=len(valid),q10=quantile(.1),q50=quantile(.5),q90=quantile(.9),
        eligible=len(cohort)>=min_group and len(valid)>=min_total)

def evaluate_macro(records,holdout_year=2025,horizon=60,mode='prequential'):
    rows=[]
    for item in records:
        if item['time'].year!=holdout_year or item['outcomes'][horizon] is None: continue
        if mode=='frozen':
            hist=[r for r in records if r['time'].year<holdout_year and
                  r['time']+timedelta(minutes=horizon)<=item['time']]
        elif mode=='prequential':
            hist=[r for r in records if r['time']<item['time'] and
                  r['time']+timedelta(minutes=horizon)<=item['time']]
        else: raise ValueError('bad mode')
        pred=learn_prior(hist,item['group'],horizon)
        rows.append(dict(id=item['id'],at_utc=item['time'].isoformat(),
            group=item['group'],actual_return_log_pct=item['outcomes'][horizon],
            actual_up=item['outcomes'][horizon]>0,**pred))
    def quality(arr):
        if not arr: return dict(n=0,correct=0,brier=None,baseline_correct=0,baseline_brier=None)
        n=len(arr)
        return dict(n=n,
            correct=sum((x['p_up']>=.5)==x['actual_up'] for x in arr),
            brier=round(sum((x['p_up']-float(x['actual_up']))**2 for x in arr)/n,6),
            baseline_correct=sum((x['baseline_p_up']>=.5)==x['actual_up'] for x in arr),
            baseline_brier=round(sum((x['baseline_p_up']-float(x['actual_up']))**2 for x in arr)/n,6))
    return dict(mode=mode,year=holdout_year,horizon_minutes=horizon,
        all=quality(rows),covered=quality([x for x in rows if x['eligible']]),
        predictions=rows,
        interpretation='RETROSPECTIVE_HEADLINE_SURPRISE_PROXY__NOT_CAUSAL_NOT_EXECUTABLE')

def load_bars(path):
    bars=[]
    for r in read_csv(path):
        if str(r.get('native_minute_bars','15'))!='15': continue
        at=instant(r.get('bar_start_utc',''))
        o,hi,lo,close=[number(r.get(k)) for k in
                        ('open_price','high_price','low_price','close_price')]
        if None in (o,hi,lo,close) or lo<=0 or not (lo<=o<=hi and lo<=close<=hi):
            continue
        bars.append(dict(start=at,end=at+timedelta(minutes=15),
                         open=o,high=hi,low=lo,close=close))
    bars.sort(key=lambda r:r['end'])
    if any(a['end']==b['end'] for a,b in zip(bars,bars[1:])):
        raise ValueError('Duplicate bar timestamps')
    return bars

def load_events(path):
    events=[]
    orgs={'ORG%02d'%i for i in range(1,13)}
    for r in read_csv(path):
        first=r.get('firstprint_utc','').strip()
        available=r.get('available_at_utc','').strip()
        if not first or not available: continue  # NO guessed news clock
        at,published=instant(available),instant(first)
        if at<published: raise ValueError('Available before published: '+r.get('event_id',''))
        groups=[g.strip() for g in r.get('org_candidates','').split('|') if g.strip() in orgs]
        events.append(dict(id=r['event_id'],at=at,firstprint=published,
            groups=groups,status=r.get('firstprint_status','UNVERIFIED'),
            kind=r.get('kind','OTHER'),surprise=number(r.get('macro_surprise',''))))
    return sorted(events,key=lambda e:(e['at'],e['id']))

def feature(window):
    if len(window)!=17 or any(b['end']-a['end']!=timedelta(minutes=15)
                               for a,b in zip(window,window[1:])):
        return dict(state='MISSING',r1=None,r4=None,rv4=None,eff=None,down=None)
    price=[b['close'] for b in window]
    ret=[math.log(y/x) for x,y in zip(price,price[1:])]
    rv=100*math.sqrt(sum(v*v for v in ret))
    net=100*(price[-1]/price[0]-1)
    eff=abs(math.log(price[-1]/price[0]))/max(1e-12,sum(abs(v) for v in ret))
    down=sum(v*v for v in ret if v<0)/max(1e-12,sum(v*v for v in ret))
    # Descriptive fixed bins, not optimised statistical regime classifier.
    if rv>=1: state='HIGH_VOL'
    elif abs(net)<.25 and eff<.25: state='CHOP'
    elif net>.45 and eff>.35: state='UP_FLOW'
    elif net<-.45 and eff>.35: state='DOWN_FLOW'
    else: state='MIXED'
    return dict(state=state,r1=round(100*(price[-1]/price[-5]-1),4),
        r4=round(net,4),rv4=round(rv,4),eff=round(eff,4),down=round(down,4))

def walk(bars,events,prior_records=(),start=None,stop=None):
    """Aged data only; non-overlapping 4h samples mature after the future closes."""
    transitions=Counter()
    previous=None
    matured=[]
    pending=[]  # (due, starting price, prior price-only state)
    for i,b in enumerate(bars):
        now=b['end']
        if stop and now>stop: break
        obs=feature(bars[max(0,i-16):i+1])
        for due,old_price,old_state in pending:
            if now==due and obs['state']!='MISSING':
                matured.append(dict(state=old_state,return_pct=100*(b['close']/old_price-1)))
        pending=[x for x in pending if x[0]>now]
        same=[x for x in matured if x['state']==obs['state']]
        baseline=sum(x['return_pct']>0 for x in matured)/len(matured) if matured else .5
        probability=(sum(x['return_pct']>0 for x in same)+8*baseline)/(len(same)+8)
        vals=sorted(x['return_pct'] for x in same)
        distribution=dict(n_state=len(same),n_total=len(matured),
            p_up_next_4h=round(probability,4) if len(matured)>=40 and len(same)>=12 else None,
            range_min_max=[round(vals[0],4),round(vals[-1],4)] if len(same)>=12 else None,
            quality='RESEARCH_BLOCK_SAMPLED' if len(matured)>=40 and len(same)>=12 else 'ABSTAIN_INSUFFICIENT_BLOCKS')
        if obs['state']!='MISSING' and i%16==0:
            pending.append((now+timedelta(hours=4),b['close'],obs['state']))
        if previous and previous!=obs['state'] and obs['state']!='MISSING':
            transitions[(previous,obs['state'])]+=1
        if obs['state']!='MISSING': previous=obs['state']
        visible=[e for e in events if now-timedelta(hours=72)<=e['at']<=now]
        verified=[e for e in visible if e['status']=='VERIFIED']
        groups=sorted({g for e in verified for g in e['groups']})
        fresh=[e for e in verified if now-timedelta(minutes=15)<e['at']<=now]
        predictions=[]
        for e in fresh:
            g=candidate(e['kind'],e['surprise'])
            if not g or g not in e['groups']: continue
            hist=[r for r in prior_records if r['time']+timedelta(minutes=60)<=now]
            prior=learn_prior(hist,g,60)
            predictions.append(dict(event=e['id'],provisional_group=g,
                status='RESEARCH_ONLY' if prior['eligible'] else 'ABSTAIN_INSUFFICIENT_HISTORY',
                distribution=prior))
        if start and now<start: continue
        yield dict(at_utc=now.isoformat(),price=b['close'],features=obs,
            event_ids=[e['id'] for e in visible],verified_groups=groups,
            evidence_state='SOURCE_VERIFIED_CAUSAL_UNPROVEN' if verified else 'UNKNOWN',
            preliminary_predictions=predictions,price_state_distribution=distribution,
            transitions_observed={'%s>%s'%k:v for k,v in transitions.items()},
            trade='DISABLED_NO_BANK_QUOTES_OR_CAUSAL_VALIDATION')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('macro-audit')
    a.add_argument('--study',required=True)
    a.add_argument('--year',type=int,default=2025)
    a.add_argument('--mode',choices=['frozen','prequential'],default='prequential')
    a.add_argument('--horizon',type=int,choices=[60,240],default=60)
    a.add_argument('--out')
    w=sub.add_parser('walk')
    w.add_argument('--bars',required=True)
    w.add_argument('--events',required=True)
    w.add_argument('--study')
    w.add_argument('--start')
    w.add_argument('--stop')
    w.add_argument('--out',required=True)
    args=p.parse_args()
    if args.action=='macro-audit':
        result=evaluate_macro(load_macro(args.study),args.year,args.horizon,args.mode)
        print(json.dumps({k:v for k,v in result.items() if k!='predictions'},indent=2))
        if args.out:
            Path(args.out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        bars=load_bars(args.bars)
        events=load_events(args.events)
        hist=load_macro(args.study) if args.study else []
        start=instant(args.start) if args.start else None
        stop=instant(args.stop) if args.stop else None
        with open(args.out,'w',encoding='utf-8') as f:
            for row in walk(bars,events,hist,start,stop):
                f.write(json.dumps(row,ensure_ascii=False)+'\n')
        print('Wrote',args.out)

if __name__=='__main__': main()
