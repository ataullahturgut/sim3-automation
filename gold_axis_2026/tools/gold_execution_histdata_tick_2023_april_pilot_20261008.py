"""Free HistData Apr-2023 raw BID/ASK TICK pilot: test missing M1 dates.
Tick ZIP is monthly even when M1 is from an incomplete yearly ZIP.
NEVER deduplicate tick timestamps: duplicate timestamps can be real quotes.
Store aggregated bid/ask 15-minute source separately, not mixed with M1 bars.
"""
from pathlib import Path
from datetime import datetime, timezone
import os,json,numpy as np,pandas as pd,psycopg
from histdata_fetcher import fetch_data
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2023_HISTDATA_TICK_BIDASK_REPAIR_PILOT_2026-10-08.json'
SOURCE_M1='HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1'
SOURCE_TICK='HISTDATA_XAUUSD_TICK_BIDASK_M15_2023_APR_PILOT_V1'
TABLE='gold_research_histdata_xau_tick_bidask15m_candidate'

def get_m1():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""SELECT bar_start_utc,close_price
                 FROM gold_research_histdata_xau15m_candidate
                 WHERE source_id=%s AND bar_start_utc>='2023-04-01' AND bar_start_utc<'2023-05-01'
                 ORDER BY bar_start_utc""",(SOURCE_M1,))
            z=pd.DataFrame(c.fetchall(),columns=['utc','m1_bid_close'])
    z.utc=pd.to_datetime(z.utc,utc=True)
    return z

def main():
    r={'status':'NOT_ACQUIRED','asof':'2026-10-08',
       'test':'April 2023 independent same-provider tick BID/ASK vs historic M1 BID, separate source identity',
       'original_vendor':'HistData.com','source_tick':SOURCE_TICK,
       'tick_timestamp':'EST_FIXED_UTC_MINUS5_UNCHANGED_US_DST',
       'original_timestamps_deduplicated':False,'paid_download_usd':0,'licensed_raw_ticks_public':False,
       'price_source_promoted':False}
    try:
        x=fetch_data('XAUUSD','2023-04-01','2023-04-30','tick',
                     output_format=None,max_workers=1)
        if not x.ok or x.failed_periods: raise RuntimeError('TICK_SOURCE_PERIOD_UNAVAILABLE')
        q=x.data[['datetime','bid','ask']].copy()
        r['downloaded_tick_rows']=int(len(q))
        r['fetched_period_labels']=list(x.fetched_periods)
        if len(q)<15000:raise RuntimeError('TICK_SAMPLE_TOO_SMALL')
        q['ts']=pd.to_datetime(q.datetime,errors='coerce')
        q['bid']=pd.to_numeric(q.bid,errors='coerce')
        q['ask']=pd.to_numeric(q.ask,errors='coerce')
        q=q.dropna(subset=['ts','bid','ask'])
        r['bad_nonpositive_or_crossed_quotes']=int(((q.bid<=0)|(q.ask<=0)|(q.ask<q.bid)).sum())
        q=q[(q.bid>0)&(q.ask>=q.bid)].copy()
        q['utc']=q.ts.dt.tz_localize('Etc/GMT+5').dt.tz_convert('UTC')
        q=q[(q.utc>='2023-04-01')&(q.utc<'2023-05-01')].copy()
        if len(q)<10000:raise RuntimeError('TICK_SAMPLE_VALID_TOO_SMALL')
        q=q.sort_values('utc',kind='mergesort')
        r['duplicate_exact_utc_tick_timestamps_preserved']=int(q.utc.duplicated().sum())
        r['valid_sample_ticks']=int(len(q))
        r['median_raw_bid_ask_spread_bps']=float(np.median((q.ask-q.bid)/((q.ask+q.bid)/2)*10000))
        r['p95_raw_bid_ask_spread_bps']=float(np.quantile((q.ask-q.bid)/((q.ask+q.bid)/2)*10000,.95))
        q=q.set_index('utc')
        q['mid']=(q.bid+q.ask)/2
        agg=q[['bid','ask','mid']].resample('15min',closed='left',label='left').agg(['first','max','min','last'])
        n=q.bid.resample('15min',closed='left',label='left').size()
        agg.columns=[a+'_'+b for a,b in agg.columns]
        agg['tick_count']=n
        agg=agg[agg.tick_count>0].reset_index().rename(columns={'utc':'bar_start_utc'})
        agg=agg[(agg.bar_start_utc>='2023-04-01')&(agg.bar_start_utc<'2023-05-01')]
        if len(agg)<800:raise RuntimeError('TICK_15MIN_AGGREGATE_TOO_THIN')
        r['candidate_m15_tick_derived_bars']=int(len(agg))
        r['pivotal_m15_from_ticks']=int(((agg.bar_start_utc.dt.hour==6)|(agg.bar_start_utc.dt.hour==13)|(agg.bar_start_utc.dt.hour==14)).sum())
        m=get_m1()
        z=agg.merge(m,left_on='bar_start_utc',right_on='utc',how='left')
        r['existing_m1_m15_april_bars']=int(len(m))
        r['new_tick_m15_intervals_absent_from_m1']=int(z.m1_bid_close.isna().sum())
        v=z.dropna(subset=['m1_bid_close'])
        r['same_timestamp_bid_close_overlap']=int(len(v))
        diff=np.abs(v.bid_last/v.m1_bid_close-1)*10000
        r['same_vendor_m1_vs_tick_bid_close_median_abs_bps']=float(diff.median())
        r['same_vendor_m1_vs_tick_bid_close_p95_abs_bps']=float(diff.quantile(.95))
        sat=((agg.bar_start_utc.dt.dayofweek==5)|
             ((agg.bar_start_utc.dt.dayofweek==6)&(agg.bar_start_utc.dt.hour<21)))
        r['hard_closed_market_bars']=int(sat.sum())
        if sat.any():raise RuntimeError('TICK_MARKET_CLOSED_BARS')
        with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
            with con.cursor() as c:
                c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE}(
                    source_id TEXT NOT NULL,
                    bar_start_utc TIMESTAMPTZ NOT NULL,
                    bid_open DOUBLE PRECISION NOT NULL,
                    bid_high DOUBLE PRECISION NOT NULL,
                    bid_low DOUBLE PRECISION NOT NULL,
                    bid_close DOUBLE PRECISION NOT NULL,
                    ask_open DOUBLE PRECISION NOT NULL,
                    ask_high DOUBLE PRECISION NOT NULL,
                    ask_low DOUBLE PRECISION NOT NULL,
                    ask_close DOUBLE PRECISION NOT NULL,
                    mid_open DOUBLE PRECISION NOT NULL,
                    mid_close DOUBLE PRECISION NOT NULL,
                    tick_count INTEGER NOT NULL,
                    data_vintage TEXT NOT NULL,
                    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY(source_id,bar_start_utc))""")
                c.execute(f"""CREATE TEMP TABLE stage(
                   source_id text,bar_start_utc timestamptz,
                   bid_open float8,bid_high float8,bid_low float8,bid_close float8,
                   ask_open float8,ask_high float8,ask_low float8,ask_close float8,
                   mid_open float8,mid_close float8,tick_count int,data_vintage text
                ) ON COMMIT DROP""")
                with c.copy("""COPY stage (source_id,bar_start_utc,bid_open,bid_high,
                    bid_low,bid_close,ask_open,ask_high,ask_low,ask_close,
                    mid_open,mid_close,tick_count,data_vintage) FROM STDIN""") as copy:
                    for x in agg.itertuples(index=False):
                        copy.write_row((SOURCE_TICK,x.bar_start_utc.to_pydatetime(),
                          float(x.bid_first),float(x.bid_max),float(x.bid_min),float(x.bid_last),
                          float(x.ask_first),float(x.ask_max),float(x.ask_min),float(x.ask_last),
                          float(x.mid_first),float(x.mid_last),int(x.tick_count),
                          'HISTORICAL_2026_10_08_NOT_POINT_IN_TIME'))
                c.execute(f"""INSERT INTO {TABLE} (
                  source_id,bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                  ask_open,ask_high,ask_low,ask_close,mid_open,mid_close,tick_count,data_vintage)
                  SELECT source_id,bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                  ask_open,ask_high,ask_low,ask_close,mid_open,mid_close,tick_count,data_vintage
                  FROM stage ON CONFLICT(source_id,bar_start_utc) DO NOTHING""")
                r['private_m15_bars_inserted']=int(c.rowcount)
            con.commit()
        r['status']='TICK_AND_M1_SAME_VENDOR_COVERAGE_COMPARE_COMPLETE'
    except Exception as ex:
        r['status']='CANDIDATE_FETCH_OR_QC_BLOCKED'
        r['error_type']=type(ex).__name__
        r['error_summary']=str(ex)[:150]
    r['completed_at_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(r,indent=2,default=str)+'\n')
    print(json.dumps(r,indent=2,default=str),flush=True)
    return 0 if r['status']=='TICK_AND_M1_SAME_VENDOR_COVERAGE_COMPARE_COMPLETE' else 1
if __name__=='__main__':raise SystemExit(main())
