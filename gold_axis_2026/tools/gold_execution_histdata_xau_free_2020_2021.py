"""Fetch HistData free 2020-2021 XAUUSD M1; normalize EST-fixed to UTC M15.
Store licensed raw-derived candidate privately in Neon, never in public GitHub.
"""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import psycopg
from histdata_fetcher import fetch_data

AX=Path(__file__).resolve().parents[1]
REPORT=AX/'GOLD_EXECUTION_HISTDATA_XAU_FREE_BACKFILL_2020_2021_20261008.json'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1'

def into_utc_15m(df):
    src=df[['datetime','open','high','low','close']].copy()
    src['datetime']=pd.to_datetime(src.datetime,errors='coerce')
    src=src.dropna(subset=['datetime','open','high','low','close'])
    src=src[(src[['open','high','low','close']]>0).all(axis=1)]
    src=src.sort_values('datetime').drop_duplicates('datetime',keep='last')
    src['utc']=src.datetime.dt.tz_localize('Etc/GMT+5').dt.tz_convert('UTC')
    src=src.set_index('utc')
    m15=src[['open','high','low','close']].resample(
        '15min',label='left',closed='left').agg(
        {'open':'first','high':'max','low':'min','close':'last'})
    m15['minute_bars']=src.close.resample(
        '15min',label='left',closed='left').count()
    m15=m15.dropna(subset=['open','high','low','close'])
    valid=((m15.high>=m15[['open','close','low']].max(axis=1))&
           (m15.low<=m15[['open','close','high']].min(axis=1)))
    if not valid.all():raise ValueError('OHLC_INCONSISTENCY')
    if m15.index.duplicated().any():raise ValueError('DUPLICATE_M15_TIMESTAMP')
    return m15.reset_index().rename(columns={'utc':'bar_start_utc'})

def persist(q):
    url=os.environ.get('NEON_DATABASE_URL','').strip()
    if not url:return {'status':'BLOCKED_DB_SECRET_MISSING','inserted':0}
    with psycopg.connect(url,autocommit=False,connect_timeout=15) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS gold_research_histdata_xau15m_candidate (
                source_id TEXT NOT NULL,
                bar_start_utc TIMESTAMPTZ NOT NULL,
                open_price DOUBLE PRECISION NOT NULL,
                high_price DOUBLE PRECISION NOT NULL,
                low_price DOUBLE PRECISION NOT NULL,
                close_price DOUBLE PRECISION NOT NULL,
                native_minute_bars SMALLINT NOT NULL,
                source_timezone TEXT NOT NULL,
                retrieved_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                evidence_class TEXT NOT NULL,
                PRIMARY KEY (source_id,bar_start_utc)
            )""")
            cur.execute("""CREATE TEMP TABLE hist_xau_stage (
                source_id TEXT,bar_start_utc TIMESTAMPTZ,open_price FLOAT8,
                high_price FLOAT8,low_price FLOAT8,close_price FLOAT8,
                native_minute_bars SMALLINT,source_timezone TEXT,evidence_class TEXT
            ) ON COMMIT DROP""")
            with cur.copy("""COPY hist_xau_stage
                (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                 native_minute_bars,source_timezone,evidence_class) FROM STDIN""") as copy:
                for row in q.itertuples(index=False):
                    copy.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                        float(row.open),float(row.high),float(row.low),float(row.close),
                        int(row.minute_bars),'EST_FIXED_UTC_MINUS_05',
                        'HISTORICAL_BACKFILL_SOURCE_CANDIDATE_NOT_CANONICAL'))
            cur.execute("""INSERT INTO gold_research_histdata_xau15m_candidate
                (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                 native_minute_bars,source_timezone,evidence_class)
                SELECT source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                       native_minute_bars,source_timezone,evidence_class
                FROM hist_xau_stage ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
            inserted=cur.rowcount
            cur.execute("""SELECT COUNT(*), MIN(bar_start_utc), MAX(bar_start_utc)
                FROM gold_research_histdata_xau15m_candidate WHERE source_id=%s""",(SOURCE,))
            count,low,high=cur.fetchone()
        conn.commit()
    return {'status':'PERSISTED_PRIVATE_SOURCE_CANDIDATE','inserted':inserted,
            'total_for_source':count,
            'first_utc':low.isoformat() if low else None,
            'last_utc':high.isoformat() if high else None}

def main():
    report={'source':SOURCE,'asof':'2026-10-08','timeframe_origin':'1min',
      'normalization':'EST UTC-05 fixed, no daylight time -> UTC, then M15 left-closed',
      'source_precedence':'CANDIDATE_ONLY; NEVER overwrites Twelve Data frozen raw',
      'license':'PRIVATE_INTERNAL_RESEARCH_NO_PUBLIC_RAW_EXPORT','periods':{},
      'cost_usd_download':0,'model_retrained':False}
    frames=[]
    for year in (2020,2021):
        try:
            result=fetch_data('XAUUSD',f'{year}-01-01',f'{year}-12-31',
                '1min',output_format=None,max_workers=1)
            if not result.ok or result.failed_periods:
                raise RuntimeError('SOURCE_YEAR_INCOMPLETE_OR_FAILED_PERIOD')
            q=into_utc_15m(result.data)
            if len(q)<17500:raise RuntimeError('TOO_FEW_M15_BARS')
            canonical=q.to_csv(index=False).encode('utf-8')
            report['periods'][str(year)]={'status':'FETCH_AND_M15_QC_PASS',
                'rows_1m':len(result.data),'rows_15m':len(q),
                'full_15m_native_minutes':int((q.minute_bars==15).sum()),
                'less_than_15_native_minutes':int((q.minute_bars<15).sum()),
                'utc_first':str(q.bar_start_utc.min()),
                'utc_last':str(q.bar_start_utc.max()),
                'canonical_15m_sha256':hashlib.sha256(canonical).hexdigest(),
                'period_labels':list(result.fetched_periods)}
            frames.append(q)
        except Exception as exc:
            report['periods'][str(year)]={'status':'FETCH_OR_QC_FAILED',
                'error_type':type(exc).__name__}
    if len(frames)==2:
        q=pd.concat(frames,ignore_index=True).sort_values('bar_start_utc').drop_duplicates('bar_start_utc')
        try:report['private_storage']=persist(q)
        except Exception as exc:
            report['private_storage']={'status':'DB_WRITE_FAILED',
                'error_type':type(exc).__name__}
    else:report['private_storage']={'status':'BLOCKED_SOURCE_YEAR_INCOMPLETE'}
    report['status']='PRIVATE_CANDIDATE_SAVED' if report['private_storage']['status']=='PERSISTED_PRIVATE_SOURCE_CANDIDATE' else 'NOT_PERSISTED'
    report['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
