"""October 2026 genuinely past XAU/USD BID ASK daily quote recovery.
2026-10-08 source-day is NOT requested, only completed Oct1-7 UTC dates.
Dukascopy primary, private candidate table; retry transient HTTP 503.
No paid API, no holiday interpolation and no vendor-inconsistent source splice.
"""
from datetime import datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,time
import pandas as pd
import gold_execution_dukascopy_independent_xau_pilot_20261008 as src
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_DUKASCOPY_OCT2026_SOURCE_GAP_RECOVERY_20261008.json'
DATES=['2026-10-01','2026-10-02','2026-10-05','2026-10-06','2026-10-07']
def one(day):
    r={'date_utc':day,'attempts':[],'data_mature':False}
    for attempt in range(1,4):
        with ThreadPoolExecutor(max_workers=2) as pool:
            fb=pool.submit(src.pull,day,'BID')
            fa=pool.submit(src.pull,day,'ASK')
            b,bmeta=fb.result();a,ameta=fa.result()
        r['attempts'].append({'attempt':attempt,'bid':bmeta.get('result'),
             'ask':ameta.get('result'),
             'bid_http_failure':bmeta.get('causes',[])[:2],
             'ask_http_failure':ameta.get('causes',[])[:2]})
        if b is not None and a is not None:
            try:
                g,agg=src.derive(b,a)
                if len(g)<80:raise RuntimeError('SOURCE_DAY_UNDER_COVERAGE')
                if g.bar_start_utc.min()<pd.Timestamp(day,tz='UTC') or \
                   g.bar_start_utc.max()>=pd.Timestamp(day,tz='UTC')+pd.Timedelta(days=1):
                    raise RuntimeError('DATA_OUTSIDE_REQUESTED_UTC_DAY')
                r['data_mature']=True
                r['m15_bars']=len(g)
                r['full_native_M1_15min_bars']=agg['complete_15m_bars']
                r['partial_native_M1_15min_bars']=agg['partial_m15_bars']
                r['median_spread_bps']=agg['median_spread_bps']
                r['persisted_new_private_bars']=src.save_private(g)
                r['result']='SOURCE_DAY_SAVED_PRIVATE'
                return r
            except Exception as e:r['last_gate_failure']=type(e).__name__+':'+str(e)[:75]
        time.sleep(min(4*attempt,12))
    r['result']='API_UNAVAILABLE_QUARANTINED'
    return r
def main():
    rep={'asof':'2026-10-08','status':'INCOMPLETE',
      'source':'Direct Dukascopy XAU/USD native M1 BID and ASK, no current-day price',
      'private_source_id':src.SOURCE,'new_source_quotes_not_histdata_bid':True,
      'not_bank_executable_bid_ask':True,
      'paid_purchase_usd':0,'original_archives_unchanged':True,
      'closed_date_window':'2026-10-01 to 2026-10-07 incl, weekends excluded',
      'dates':[]}
    for day in DATES:
        r=one(day)
        rep['dates'].append(r)
        print('OCT26_SOURCE_RECOVERY',json.dumps(r,default=str),flush=True)
    rep['completed_source_days']=sum(z['result']=='SOURCE_DAY_SAVED_PRIVATE' for z in rep['dates'])
    rep['quarantined_source_days']=len(DATES)-rep['completed_source_days']
    rep['total_completed_m15_bars']=sum(int(z.get('m15_bars',0)) for z in rep['dates'])
    rep['status']='COMPLETE_CLOSED_WEEKDAY_OCT_SOURCE_CANDIDATE' if rep['quarantined_source_days']==0 \
        else 'PARTIAL_OCT_SOURCE_CANDIDATE_WITH_EXPLICIT_GAPS'
    rep['timestamp_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(rep,indent=2,default=str)+'\n')
    print('OCT2026_FINAL',rep['status'],rep['completed_source_days'],flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
