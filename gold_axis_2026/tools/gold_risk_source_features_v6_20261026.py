#!/usr/bin/env python3
"""V6 issuer-source feature replay, research only. No trading / Neon writes.
Decision: 17:30 America/New_York (BASE14 issue clock).
SLV and TIPS T+1 09:00 New York are hypothetical delays, not first-print proof.
Historical series revisions are not certified PIT; model promotion is blocked.
Requires sibling gold_risk_asof_audit_20261026.py and six original files.
"""
import argparse,csv,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo
from importlib.util import spec_from_file_location,module_from_spec

NY=ZoneInfo('America/New_York')
A=Path(__file__).with_name('gold_risk_asof_audit_20261026.py')
sp=spec_from_file_location('source_asof',A); source=module_from_spec(sp); sp.loader.exec_module(source)
EVENTS=['2026-01-22','2026-01-26','2026-01-29','2026-01-30','2026-02-02',
'2026-03-30','2026-03-31','2026-04-01','2026-04-02','2026-04-03',
'2026-06-03','2026-06-05','2026-06-17','2026-06-18','2026-08-11','2026-08-25','2026-08-27']

def last(rows,kind,t,key,missing_ok=False):
    a=[r for r in rows if source.earliest_time(r['date'],kind)<=t
       and (missing_ok or r[key] is not None)]
    return a[-1] if a else None

def released(rows,kind,t,key,n):
    a=[r for r in rows if source.earliest_time(r['date'],kind)<=t and r[key] is not None]
    return a[-n:] if len(a)>=n else []

def delta(q,key):
    return round(q[-1][key]-q[-6][key],8) if len(q)>=6 else None

def verified_sources(folder):
    for name,sha in source.SHA.items():
        assert source.digest(folder/name)==sha, 'SOURCE_SHA_MISMATCH: '+name
    silver,fix=source.historical_slv(folder/'slv_official_download_xml')
    nominal=source.historical_h15(folder/'fed_h15_treasury_cmt_full_history.csv')
    tips=source.historical_tips(folder)
    assert (len(silver),len(nominal),len(tips),fix)==(958,994,953,6)
    assert all(source.no_dupes(a)==0 for a in (silver,nominal,tips))
    assert sum(q['2y'] is None and q['10y'] is None for q in nominal)==42
    assert [q['date'].isoformat() for q in silver if q['shares'] is None]==['2024-03-29','2024-03-31']
    return silver,nominal,tips

def row(day,silver,nominal,tips):
    at=dt.datetime.combine(day,dt.time(17,30),NY)
    two=released(nominal,'h15',at,'2y',6)
    ten=released(nominal,'h15',at,'10y',6)
    real=released(tips,'tips',at,'real10y',6)
    all_silver=[q for q in silver if source.earliest_time(q['date'],'slv')<=at]
    last_nom=last(nominal,'h15',at,'10y')
    last_real=last(tips,'tips',at,'real10y')
    last_silver=last(silver,'slv',at,'shares',True)
    # No crossing a missing issuer-share row to generate fake share changes.
    shift1=(all_silver[-1]['shares']-all_silver[-2]['shares']
        if len(all_silver)>=2 and all(q['shares'] is not None for q in all_silver[-2:]) else None)
    shift5=(all_silver[-1]['shares']-all_silver[-6]['shares']
        if len(all_silver)>=6 and all(q['shares'] is not None for q in all_silver[-6:]) else None)
    out={
      'origin':day.isoformat(),'decision_ny':at.isoformat(),
      'nom2_day':two[-1]['date'].isoformat() if two else None,
      'nom10_day':last_nom['date'].isoformat() if last_nom else None,
      'nom_2y':two[-1]['2y'] if two else None,
      'nom_10y':ten[-1]['10y'] if ten else None,
      'slope_10y_minus_2y':round(ten[-1]['10y']-two[-1]['2y'],8)
          if two and ten and two[-1]['date']==ten[-1]['date'] else None,
      'nom_10y_delta5':delta(ten,'10y'),
      'real10y_day_proxy':last_real['date'].isoformat() if last_real else None,
      'real10y':real[-1]['real10y'] if real else None,
      'real10y_delta5':delta(real,'real10y'),
      'slv_day_proxy':last_silver['date'].isoformat() if last_silver else None,
      'slv_shares':last_silver['shares'] if last_silver else None,
      'slv_nav':last_silver['nav'] if last_silver else None,
      'slv_share_delta_one_obs':shift1,'slv_share_delta_five_obs':shift5,
      'nom_pub_rule':'H15 16:15 NY; vintage unverified',
      'real_pub_rule':'T+1 weekday 09 NY provisional proxy',
      'slv_pub_rule':'T+1 weekday 09 NY provisional proxy',
      'pit_vintage_certified':False,'model_ready':False}
    for kind,q in [('h15',last_nom),('tips',last_real),('slv',last_silver)]:
        if q: assert source.earliest_time(q['date'],kind)<=at, 'LOOKAHEAD_'+kind
    if out['nom2_day']: assert out['nom2_day']==out['nom10_day']
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--outdir',required=True,type=Path)
    a=p.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    silver,nominal,tips=verified_sources(a.input)
    days=[]
    d=dt.date(2023,1,3)
    while d<=dt.date(2026,10,23):
        if d.weekday()<5: days.append(row(d,silver,nominal,tips))
        d+=dt.timedelta(days=1)
    assert len(days)==994
    april1=next(x for x in days if x['origin']=='2024-04-01')
    april2=next(x for x in days if x['origin']=='2024-04-02')
    assert april1['slv_share_delta_one_obs'] is None
    assert april2['slv_share_delta_one_obs'] is None
    assert april2['slv_share_delta_five_obs'] is None
    assert all(x['slv_shares']!=0 for x in days if x['slv_shares'] is not None)
    assert all(any(x['origin']==e and x['real10y'] is not None for x in days) for e in EVENTS)
    for filename,records in [('asof_candidate_features_2023_2026_RESEARCH_ONLY.csv',days),
     ('key_event_source_features_RESEARCH_ONLY.csv',[x for x in days if x['origin'] in EVENTS])]:
        with (a.outdir/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(days[0]));w.writeheader();w.writerows(records)
    features=['nom_2y','nom_10y','slope_10y_minus_2y','nom_10y_delta5',
              'real10y','real10y_delta5','slv_shares','slv_share_delta_one_obs',
              'slv_share_delta_five_obs']
    report={'source_sha256_match':True,'source_rows':{'SLV':958,'H15':994,'REAL10Y':953},
      'decision_clock':'17:30 America/New_York',
      'n_weekdays_evaluated':994,
      'research_candidates_nonnull':{k:sum(x[k] is not None for x in days) for k in features},
      'release_policy':{'H15':'16:15 NY firstprint vintage unknown',
                        'SLV':'T+1 weekday 09 NY unverified proxy',
                        'REAL10Y':'T+1 weekday 09 NY unverified proxy'},
      'historical_pit_verified':False,'production_approved':False,
      'base14_reproduced':False,'cftc21_reproduced':False,'paired_model_backtest_run':False,
      'stop_reason':'Missing archived original risk-overlay-source ZIP and 398-row GC/SI quality-gated CFTC CSV.',
      'target_policy':'2023-24 fit, 2025 validation, 2026 retrospective stress; no 2026-derived threshold'}
    (a.outdir/'candidate_source_gate_v6.json').write_text(
       json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
