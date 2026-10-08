"""Read-only six historical >1.5% in consecutive 15m XAUUSD BID closes.
Compare on EXACT SAME UTC price-bar interval with separately sourced
HistData BID, then report only aggregate bps and anchored UTC timestamps.
A giant move is not declared corrupt without independent evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os
import numpy as np,pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2020_2025_XAU_EXTREME_BAR_CROSS_VENDOR_QC_20261008.json'
EV='EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1'
H=lambda y:'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1' if y<=2021 else (
   'HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1' if y<=2024 else
   'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026')
def read(con):
    with con.cursor() as c:
        c.execute("""SELECT bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                   ask_close
                FROM gold_research_evduka_xau15m_bidask_candidate
                WHERE source_id=%s ORDER BY bar_start_utc""",(EV,))
        q=pd.DataFrame(c.fetchall(),columns=['ts','o','h','l','c','ask'])
    q.ts=pd.to_datetime(q.ts,utc=True)
    if len(q)!=141890:raise RuntimeError('PRICE_ARCHIVE_CHANGED')
    return q.sort_values('ts')
def read_h(con,dates):
    if not dates:return pd.DataFrame(columns=['ts','hclose'])
    start=min(dates)-pd.Timedelta(minutes=20)
    end=max(dates)+pd.Timedelta(minutes=20)
    years=sorted(set(x.year for x in dates))
    frames=[]
    seen_source_ids=set()
    for year in years:
        if H(year) in seen_source_ids:
            continue
        seen_source_ids.add(H(year))
        with con.cursor() as c:
            c.execute("""SELECT bar_start_utc,close_price FROM gold_research_histdata_xau15m_candidate
                        WHERE source_id=%s AND bar_start_utc>=%s AND bar_start_utc<=%s
                        ORDER BY bar_start_utc""",(H(year),start.to_pydatetime(),end.to_pydatetime()))
            rows=c.fetchall()
        frames.extend(rows)
    ans=pd.DataFrame(frames,columns=['ts','hclose'])
    if len(ans):ans.ts=pd.to_datetime(ans.ts,utc=True)
    return ans.set_index('ts') if len(ans) else ans
def main():
    rep={'status':'READ_ONLY_CROSS_VENDOR_QC_COMPLETE','asof':'2026-10-08',
       'test':'absolute concurrent quarter-hour BID close-to-close jump >1.5%',
       'primary_reference':'Dukascopy-derived independent EV 15m BID ASK',
       'separate_vendor':'HistData fixed EST timestamp-normalized BID M1->15m',
       'comparison_policy':'Same UTC 15m timestamp at both t and t-15 only; do not fill missing anchor with another time',
       'price_rows_modified':False,'labels_modified':False,'models_retrained':False,'rows':[]}
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        q=read(con)
        q['prev_ts']=q.ts.shift(1)
        q['prev_c']=q.c.shift(1)
        q['ret']=q.c/q.prev_c-1
        x=q[((q.ts-q.prev_ts)==pd.Timedelta(minutes=15))&(q.ret.abs()>.015)]
        keys=list(x.ts)+[t-pd.Timedelta(minutes=15) for t in x.ts]
        h=read_h(con,keys)
        for r in x.itertuples(index=False):
            a=r.ts-pd.Timedelta(minutes=15)
            v={'ts_utc':r.ts.isoformat(),'year':int(r.ts.year),
                'absolute_15m_bid_return_pct':float(abs(r.ret)*100),
                'direction':'UP' if r.ret>0 else 'DOWN',
                'source_bid_ask_close_spread_bps':float((r.ask/r.c-1)*10000),
                'histdata_same_utc_both_bars':False,'cross_vendor_direction_match':None,
                'histdata_absolute_same_utc_15m_move_pct':None,
                'absolute_bps_difference_of_15m_return':None}
            if len(h) and r.ts in h.index and a in h.index:
                ho=float(h.at[a,'hclose']); hc=float(h.at[r.ts,'hclose'])
                if ho>0 and hc>0:
                    other=hc/ho-1
                    v['histdata_same_utc_both_bars']=True
                    v['histdata_absolute_same_utc_15m_move_pct']=float(abs(other)*100)
                    v['cross_vendor_direction_match']=bool((other>0)==(r.ret>0))
                    v['absolute_bps_difference_of_15m_return']=float(abs(other-r.ret)*10000)
            rep['rows'].append(v)
    rep['flagged_15m_events']=len(rep['rows'])
    rep['independent_double_anchored_cross_source_events']=sum(x['histdata_same_utc_both_bars'] for x in rep['rows'])
    rep['independent_direction_consistent_events']=sum(x['cross_vendor_direction_match']==True for x in rep['rows'])
    rep['missing_independent_anchor_events']=[v['ts_utc'] for v in rep['rows'] if not v['histdata_same_utc_both_bars']]
    rep['source_limit']='World Gold Council validates Aug 9 2021 gold flash crash; Reuters documents Dec 4 2023 opening spike. Macro event support does NOT prove exact tick price.'
    rep['completed_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(rep,indent=2)+'\n')
    print('INDEPENDENT_SOURCE_EXTREME_QC',json.dumps(rep,indent=2),flush=True)
if __name__=='__main__':main()
