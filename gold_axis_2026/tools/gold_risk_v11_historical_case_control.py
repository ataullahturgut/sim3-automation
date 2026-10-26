#!/usr/bin/env python3
"""Gold risk V11: 2010-19 historical case/control price-only gate.
Research-only; no historical first-print certification, trading, Neon writes,
2020-22 training, or 2026 tuning. V8 BASE14/CFTC21 stay unchanged.
"""
from __future__ import annotations
import csv,json,hashlib,math
from pathlib import Path
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score
import gold_risk_cftc_v8 as old
from sklearn.ensemble import IsolationForest

ROOT=Path(__file__).parent
O=ROOT/'outputs';O.mkdir(exist_ok=True)
FEATURES=['ret5','ret20','ret5_minus_quarter20','rv5','rv20','ma20_gap','drawdown60','vol_expansion']
# Independent read-only Neon per-year checksums, derived from exact research lineage.
NEON_YEAR_MD5={
  '2010':'91fc887a3bc26a77fa859d80a1efa741','2011':'62ae1bdcaecc8a556373c13925256a6e',
  '2012':'644a3123b9de21971af53cb35dca9274','2013':'ba37e649d3f3ddf182420576edd28902',
  '2014':'4c33572dc7258371be87029b21730acd','2015':'eeee93d262ec1ab37188b9e5275f5092',
  '2016':'ad30c632c2187e4021d58a7f33081b31','2017':'3890b3bb93e0593a741aadd53f8b50a2',
  '2018':'40f2d6974a43b87ba9ba2d2fd26a90f0','2019':'5e274b9094ac09e7742323143505d2b4'}

def features(dates,prices,for_history=True):
    """Causal X_t uses only prices <=t; label references t+1..t+5 only."""
    p=np.asarray(prices,float); log=np.log(p);out=[]
    for i in range(60,len(p)-5):
        if not np.isfinite(p[i-60:i+6]).all() or min(p[i-60:i+6])<=0: continue
        ret5=log[i]-log[i-5];ret20=log[i]-log[i-20]
        v5=float(np.std(np.diff(log[i-5:i+1])));v20=float(np.std(np.diff(log[i-20:i+1])))
        x=[ret5,ret20,ret5-ret20/4,v5,v20,
           p[i]/np.mean(p[i-19:i+1])-1,p[i]/max(p[i-59:i+1])-1,
           v5/max(v20,0.0001)]
        nxt=min(p[i+1:i+6])/p[i]-1
        out.append({'origin':dates[i],'features':x,'future5_min':float(nxt),
                    'five':bool(nxt<=-.05),'next_day3':bool(p[i+1]/p[i]-1<=-.03),
                    'current_gold':float(p[i]),'target_mature':dates[i+5]})
    return out

def historic():
    with (ROOT/'historical_gold_daily_research_2010_2019.csv').open() as f:
        data=list(csv.DictReader(f))
    assert len(data)==2526
    dates=[r['date'] for r in data]; prices=[float(r['xau_usd_source']) for r in data]
    assert dates[0]=='2010-01-04' and dates[-1]=='2019-12-31'
    assert dates==sorted(set(dates))
    for year,expected in NEON_YEAR_MD5.items():
        text=','.join(r['date'].replace('-','')+':'+str(int(round(float(r['xau_usd_source'])*100)))
                      for r in data if r['date'].startswith(year))
        assert hashlib.md5(text.encode('utf-8')).hexdigest()==expected, 'NEON_SOURCE_YEAR_MD5_MISMATCH_'+year
    h=features(dates,prices)
    return h,data

def control_matches(h):
    """Match 3 same-year noncrash counterexamples to first origin of each event-label run."""
    positives=[i for i,r in enumerate(h) if r['five']]
    firsts=[i for i in positives if i==0 or not h[i-1]['five']]
    candidates=[]
    for first in firsts:
        ref=h[first]; y=ref['origin'][:4]
        blocked=set(range(max(0,first-20),min(len(h),first+21)))
        for q in positives:
            blocked.update(range(max(0,q-6),min(len(h),q+7)))
        clean=[i for i,r in enumerate(h) if i not in blocked and r['origin'][:4]==y and not r['five']]
        if not clean: continue
        # Match only on features known that day, not on future returns.
        dist=lambda i: abs(h[i]['features'][1]-ref['features'][1])/0.025+abs(h[i]['features'][4]-ref['features'][4])/0.007
        selected=[]
        for j in sorted(clean,key=dist):
            if all(abs(j-k)>10 for k in selected):selected.append(j)
            if len(selected)==3:break
        candidates.append({'case':ref['origin'],'case_future5_pct':round(ref['future5_min']*100,2),
            'case_ret20_pct':round(ref['features'][1]*100,2),
            'case_rv20_pct':round(ref['features'][4]*100,2),
            'controls':[(h[j]['origin'],round(h[j]['future5_min']*100,2),round(dist(j),3)) for j in selected]})
    return candidates

def fit_hist(rows):
    X=np.array([r['features'] for r in rows]); y=np.array([int(r['five']) for r in rows]);
    assert y.sum()>35 and len(y)>2300
    # Historical 2015-19 forward holdout: no hyperparameter selection on 2025/26.
    train=[i for i,r in enumerate(rows) if r['origin']<'2015-01-01' and r['target_mature']<'2015-01-01']
    hold=[i for i,r in enumerate(rows) if r['origin']>='2015-01-01']
    def f(t):
        sc=RobustScaler().fit(X[t]); mdl=LogisticRegression(C=.25,class_weight='balanced',max_iter=5000,random_state=1701).fit(sc.transform(X[t]),y[t]);
        return sc,mdl
    sc0,m0=f(train);ph=m0.predict_proba(sc0.transform(X[hold]))[:,1]
    year_out=[]
    for yr in range(2015,2020):
        ix=[j for j,i in enumerate(hold) if rows[i]['origin'][:4]==str(yr)];yf=y[np.array(hold)[ix]];ps=ph[ix]
        year_out.append({'year':yr,'n':len(ix),'positive_days':int(yf.sum()),'pred_p_ge_0_5':int((ps>=.5).sum()),
                         'false_p_ge_0_5':int(((ps>=.5)&(yf==0)).sum()),
                         'hit_p_ge_0_5':int(((ps>=.5)&(yf==1)).sum())})
    diagnostics={'train2010_14_days':len(train),'train2010_14_event_origins':int(y[train].sum()),
                 'heldout2015_19_days':len(hold),'heldout_event_origins':int(y[hold].sum()),
                 'heldout_auprc':float(average_precision_score(y[hold],ph)),'heldout_roc_auc':float(roc_auc_score(y[hold],ph)),
                 'heldout_by_year':year_out}
    sc,mdl=f(list(range(len(rows))))
    # Only historical-score quantile thresholds. No 2025/26 label-based selection.
    hist_scores=mdl.predict_proba(sc.transform(X))[:,1]
    thresholds={str(q):float(np.quantile(hist_scores,q)) for q in (.35,.5,.65,.8)}
    return sc,mdl,diagnostics,thresholds

def episode_groups(test,label='y_next5_drawdown5'):
    groups=[];cur=[]
    for j,r in enumerate(test):
        if r[label]:
            if cur and j>cur[-1]+1:groups.append(cur);cur=[]
            cur.append(j)
        elif cur:groups.append(cur);cur=[]
    if cur:groups.append(cur)
    return groups

def metrics(test,alarms):
    groups=episode_groups(test)
    d1=np.array([r['y_nextday_drop3'] for r in test],bool)
    d5=np.array([r['y_next5_drawdown5'] for r in test],bool)
    hits=int((alarms&d5).sum());false=int((alarms&~d5).sum())
    false_runs=[]; active=[]
    for i,r in enumerate(test):
        if alarms[i] and not d5[i]:active.append(i)
        elif active:false_runs.append(active);active=[]
    if active:false_runs.append(active)
    return {'alerts':int(alarms.sum()),'nextday3_hit':int((alarms&d1).sum()),'nextday3_total':int(d1.sum()),
         'next5_origin_hit':hits,'next5_origin_total':int(d5.sum()),'false5_days':false,
         'false5_episodes':len(false_runs),'five_label_groups_hit':sum(bool(alarms[g].any()) for g in groups),
         'five_label_groups_total':len(groups),'prior5_origin_groups':sum(bool(alarms[max(0,g[0]-5):g[0]].any()) for g in groups)}

def main():
    h,raw=historic(); matches=control_matches(h)
    assert len(matches)==16,('expected16_post_60day_warmup',len(matches))
    assert sum(r['five'] for r in h)==43,('positive_post_warmup',sum(r['five'] for r in h))
    sc,mdl,diag,thresholds=fit_hist(h)
    with (O/'historical_case_control_matches.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['case_date','case_future5_pct','case_ret20_pct','matched_control_date','matched_control_future5_pct','similarity_distance'])
        for r in matches:
            for d,fall,dist in r['controls']:writer.writerow([r['case'],r['case_future5_pct'],r['case_ret20_pct'],d,fall,dist])
    src,cftc,sha=old.load(ROOT/'gold-risk-overlay-2023-2026-source-artifact.zip',ROOT/'CFTC_GC_SI_2023_2026_QUALITY_GATED.csv')
    rows=old.make_rows(src,cftc)
    print('aligned_v8_origins',len(rows))
    by_date={r['origin']:r for r in rows};
    all_dates=[r['date'] for r in src['prices']];price=[r['metals'][0] for r in src['prices']]
    # Causal historical-price features independently recomputed from the SAME V8 full price panel.
    short_feats={r['origin']:r for r in features(all_dates,price)}
    assert all(d in short_feats for d in by_date)
    pairs={};daily=[]
    for year,cut,lo,hi in [('2025','2024-12-31','2025-01-01','2025-12-31'),('2026','2025-12-31','2026-01-01','2026-09-21')]:
        train=[r for r in rows if r['target_mature']<=cut]
        test=[r for r in rows if lo<=r['origin']<=hi]
        assert len(test)==(232 if year=='2025' else 161)
        x=np.array([r['features'] for r in train]);v=np.array([r['features'] for r in test]);
        alert={}
        for name,cols in [('BASE14',list(range(14))),('CFTC21',list(range(21))),('MGVZ10',list(range(10)))]:
            scaler=RobustScaler().fit(x[:,cols]);mod=IsolationForest(n_estimators=200,max_samples=min(256,len(train)),random_state=1701,n_jobs=1).fit(scaler.transform(x[:,cols]));
            cutp=np.quantile(-mod.score_samples(scaler.transform(x[:,cols])),.95)
            alert[name]=-mod.score_samples(scaler.transform(v[:,cols]))>=cutp
        P=mdl.predict_proba(sc.transform(np.array([short_feats[r['origin']]['features'] for r in test])))[:,1]
        candidates={'BASE14':alert['BASE14'],'CFTC21':alert['CFTC21'],
              'V10_BASE_AND_MGVZ':alert['BASE14']&alert['MGVZ10']}
        for q in ('0.35','0.5','0.65','0.8'):
            hh=P>=thresholds[q]
            candidates['BASE14_HIST_'+q]=alert['BASE14']&hh
            candidates['CFTC_OR_BASE_HIST_'+q]=alert['CFTC21']|(alert['BASE14']&hh)
            candidates['BASE_MGVZ_OR_HIST_'+q]=alert['BASE14']&(alert['MGVZ10']|hh)
        pairs[year]={name:metrics(test,flags) for name,flags in candidates.items()}
        for i,r in enumerate(test):
            d={'period':year,'origin':r['origin'],'gold_price':r['gold_price_usd_oz'],
               'y_nextday_drop3':int(r['y_nextday_drop3']),'y_next5_drop5':int(r['y_next5_drawdown5']),
               'historical_risk_score':round(float(P[i]),7)}
            d.update({name:int(flags[i]) for name,flags in candidates.items()})
            daily.append(d)
        if year=='2025':
            # Pre-declared 2025-only preference: do not miss CFTC21's 3/3 day events or groups.
            must=pairs['2025']['CFTC21']
            valid=[(p['false5_days'],p['alerts'],name) for name,p in pairs['2025'].items() if
              p['nextday3_hit']>=must['nextday3_hit'] and p['five_label_groups_hit']>=must['five_label_groups_hit']
              and p['prior5_origin_groups']>=must['prior5_origin_groups']]
            selected=sorted(valid)[0][2]
    with (O/'v11_daily_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=daily[0].keys());w.writeheader();w.writerows(daily)
    result={'research_only':True,'historical_price_first_print_verified':False,'historical_raw_input_days':len(raw),'historical_price_csv_sha256':hashlib.sha256((ROOT/'historical_gold_daily_research_2010_2019.csv').read_bytes()).hexdigest(),
      'historic_labeled_rows':len(h),'historical_source_year_md5_verified':True,'historic_5day_positive_origin_days':sum(r['five'] for r in h),
      'historic_episode_groups':len(matches),'historic_negative_matched_controls':sum(len(r['controls']) for r in matches),
      'historic_times':'2010-2019 only; 2020-2022 not used','historic_validation':diag,
      'research_only_historical_thresholds':thresholds,'model':'RobustScaler + L2 LogisticRegression(C=0.25,class_weight=balanced) PRICE-ONLY; fixed historic quantiles',
      'v8_inputs_source_hash':src['source_sha256'],'cftc_hash':sha,'paired_metrics':pairs,
      'selected_from_2025_only':selected, 'not_promoted':True,'not_live_pit_certified':True,
      'tuned_on_2026':False,'physical_first_selling_onset_verified':False,
      'v11_supervised_model_is_probability_calibrated':False}
    (O/'v11_result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('Historical fit',json.dumps(diag))
    print('2025-selected',selected,'2025',pairs['2025'][selected],'2026',pairs['2026'][selected])
    print('2026 all',json.dumps({name:[m['alerts'],m['false5_days'],m['five_label_groups_hit'],m['nextday3_hit']] for name,m in pairs['2026'].items()}))
    print('V11_RESEARCH_ONLY_NO_PIT_OR_DEPLOYMENT')

if __name__=='__main__':main()