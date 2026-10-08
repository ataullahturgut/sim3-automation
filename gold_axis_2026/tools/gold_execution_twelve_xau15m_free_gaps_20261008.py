"""Acquire only missing Twelve Data XAU/USD 15m 2020-2021 + 2026 Oct.
Authenticated calls consume included API credits; no paid add-on. Store privately.
"""
from __future__ import annotations
import calendar, hashlib, json, os, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import psycopg
import requests

AX=Path(__file__).resolve().parents[1]
REPORT=AX/'GOLD_EXECUTION_TWELVE_XAU15M_GAP_FETCH_20261008.json'
SOURCE='TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1'
SYMBOL='XAU/USD'
URL='https://api.twelvedata.com/time_series'

def month_windows():
    for year in (2020,2021):
        for m in range(1,13):
            start=f'{year:04d}-{m:02d}-01'
            end=f'{year + (m==12):04d}-{1 if m==12 else m+1:02d}-01'
            yield (start,end)
    yield ('2026-10-01','2026-10-09')

def request_month(session,start,end,api_key):
    params={'symbol':SYMBOL,'interval':'15min','timezone':'UTC','order':'ASC',
            'start_date':start+' 00:00:00','end_date':end+' 00:00:00',
            'apikey':api_key}
    for attempt in range(1,6):
        try:
            response=session.get(URL,params=params,timeout=(10,45))
            p=response.json()
            if not isinstance(p,dict):raise ValueError('VENDOR_RESPONSE_NOT_OBJECT')
            code=int(p.get('code') or response.status_code)
            if code==429 or response.status_code==429:
                if attempt==5:raise RuntimeError('TWELVE_RATE_LIMIT_RETRY_EXHAUSTED')
                time.sleep(75)
                continue
            if code>=400 or response.status_code>=400:
                raise ValueError('VENDOR_ACCESS_OR_PLAN_ERROR_CODE_'+str(code))
            vals=p.get('values')
            if not isinstance(vals,list):raise ValueError('VENDOR_VALUES_MISSING')
            if p.get('meta',{}).get('symbol',SYMBOL)!=SYMBOL:
                raise ValueError('VENDOR_SYMBOL_MISMATCH')
            if p.get('meta',{}).get('interval','15min')!='15min':
                raise ValueError('VENDOR_INTERVAL_MISMATCH')
            return vals
        except (requests.RequestException,ValueError) as exc:
            if isinstance(exc,ValueError):raise
            if attempt==5:raise RuntimeError('TRANSPORT_RETRIES_EXHAUSTED') from exc
            time.sleep(12*attempt)
    raise RuntimeError('UNREACHABLE')

def parse(vals,start,end,ready_cutoff):
    q=pd.DataFrame(vals)
    required={'datetime','open','high','low','close'}
    if not required.issubset(q.columns):raise ValueError('VENDOR_OHLC_COLUMNS_MISSING')
    q=q[list(required)].copy()
    q['bar_start_utc']=pd.to_datetime(q['datetime'],errors='coerce',utc=True)
    q=q.dropna(subset=['bar_start_utc'])
    for c in ('open','high','low','close'):
        q[c]=pd.to_numeric(q[c],errors='coerce')
    q=q.dropna(subset=['open','high','low','close'])
    s=pd.Timestamp(start,tz='UTC');e=pd.Timestamp(end,tz='UTC')
    q=q[(q.bar_start_utc>=s)&(q.bar_start_utc<e)]
    # Never call a partial current bar 'matured'; no future bars.
    q=q[q.bar_start_utc+pd.Timedelta(minutes=15)<=ready_cutoff]
    if q.empty:raise ValueError('NO_COMPLETE_BARS_IN_CHUNK')
    if (q[['open','high','low','close']]<=0).any().any():raise ValueError('INVALID_POSITIVE_GOLD_PRICE')
    if (q.high+1e-9<q[['open','low','close']].max(axis=1)).any():raise ValueError('OHLC_HIGH_FAIL')
    if (q.low-1e-9>q[['open','high','close']].min(axis=1)).any():raise ValueError('OHLC_LOW_FAIL')
    if q.bar_start_utc.duplicated().any():raise ValueError('DUPLICATE_INTERVAL_IN_VENDOR_CHUNK')
    if ((q.bar_start_utc.dt.minute%15)!=0).any():raise ValueError('NOT_QUARTER_HOUR_ALIGNED')
    return q[['bar_start_utc','open','high','low','close']].sort_values('bar_start_utc')

def save_private(q):
    db=os.environ.get('NEON_DATABASE_URL','').strip()
    if not db:raise RuntimeError('PRIVATE_NEON_DATABASE_REQUIRED')
    with psycopg.connect(db,autocommit=False,connect_timeout=15) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS gold_research_twelve_xau15m_gap_candidate (
                  source_id TEXT NOT NULL, bar_start_utc TIMESTAMPTZ NOT NULL,
                  open_price DOUBLE PRECISION NOT NULL,high_price DOUBLE PRECISION NOT NULL,
                  low_price DOUBLE PRECISION NOT NULL,close_price DOUBLE PRECISION NOT NULL,
                  source_timezone TEXT NOT NULL, evidence_class TEXT NOT NULL,
                  retrieved_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                  PRIMARY KEY(source_id,bar_start_utc))""")
            cur.execute("""CREATE TEMP TABLE twelve_xau_stage (
                  source_id TEXT,bar_start_utc TIMESTAMPTZ,open_price FLOAT8,
                  high_price FLOAT8,low_price FLOAT8,close_price FLOAT8,
                  source_timezone TEXT,evidence_class TEXT) ON COMMIT DROP""")
            with cur.copy("""COPY twelve_xau_stage
                 (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                  source_timezone,evidence_class) FROM STDIN""") as cp:
                for row in q.itertuples(index=False):
                    cp.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                                 float(row.open),float(row.high),float(row.low),float(row.close),
                                 'UTC','CURRENTLY_RETRIEVED_VENDOR_HISTORICAL_CANDIDATE'))
            cur.execute("""INSERT INTO gold_research_twelve_xau15m_gap_candidate
                (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                 source_timezone,evidence_class)
                SELECT source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                       source_timezone,evidence_class FROM twelve_xau_stage
                ON CONFLICT(source_id,bar_start_utc) DO NOTHING""")
            inserted=cur.rowcount
            cur.execute("""SELECT EXTRACT(YEAR FROM bar_start_utc)::INT AS year,COUNT(*)
                FROM gold_research_twelve_xau15m_gap_candidate WHERE source_id=%s
                GROUP BY 1 ORDER BY 1""",(SOURCE,))
            annual=dict((str(int(y)),int(n)) for y,n in cur.fetchall())
            cur.execute("""SELECT COUNT(*),
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS((t.close_price/h.close_price-1)*10000)),
                   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ABS((t.close_price/h.close_price-1)*10000)),
                   AVG(CASE WHEN t.close_price>h.close_price THEN 1.0 ELSE 0 END)
                FROM gold_research_twelve_xau15m_gap_candidate t
                JOIN gold_research_histdata_xau15m_candidate h ON t.bar_start_utc=h.bar_start_utc
                WHERE t.source_id=%s AND EXTRACT(YEAR FROM t.bar_start_utc) IN (2020,2021)""",(SOURCE,))
            overlap_n,median_bps,p95_bps,positive_share=cur.fetchone()
        conn.commit()
    return {'status':'SAVED_PRIVATE_ONLY','new_rows':inserted,'annual_persisted':annual,
            'histdata_same_utc_overlap_rows':overlap_n,'histdata_close_abs_median_bps':median_bps,
            'histdata_close_abs_p95_bps':p95_bps,'twelve_price_above_histdata_share':positive_share,
            'candidate_promotion':'BLOCKED_UNTIL_SOURCE_IDENTITY_AND_ANCHOR_VALIDATION'}

def main():
    api_key=os.environ.get('TWELVE_DATA_API_KEY','').strip()
    if not api_key:raise RuntimeError('TWELVE_DATA_API_KEY_SECRET_REQUIRED')
    if not os.environ.get('NEON_DATABASE_URL','').strip():raise RuntimeError('PRIVATE_NEON_DATABASE_REQUIRED')
    now=datetime.now(timezone.utc)
    if now.date().isoformat() != '2026-10-08':
        # Not safe to replay a pinned current-day job with a later clock.
        raise RuntimeError('ASOF_DAY_DRIFT_REQUIRES_NEW_FREEZE')
    cutoff=pd.Timestamp(now).floor('min')
    reports=[]
    frames=[]
    session=requests.Session()
    report={'retrieved_at_utc':now.isoformat(),'source_id':SOURCE,
       'price_raw_public_export':False,'paid_addon_purchase':False,
       'free_existing_api_credits_only':True,'model_retrained':False,
       'asof':'2026-10-08','monthly_receipts':reports}
    try:
        for start,end in month_windows():
            vals=request_month(session,start,end,api_key)
            q=parse(vals,start,end,cutoff)
            if len(vals)>=5000:raise ValueError('VENDOR_RESPONSE_TRUNCATION_RISK')
            # Each complete calendar month should contain >1800 bars in normal FX weekly trading.
            if start[:4] in ('2020','2021') and len(q)<1700:
                reports.append({'start':start,'end_exclusive':end,
                  'vendor_returned_rows':len(vals),'filtered_complete_rows':len(q),
                  'first_utc':q.bar_start_utc.min().isoformat(),
                  'last_utc':q.bar_start_utc.max().isoformat(),
                  'diagnosis':'MONTH_RESPONSE_INSUFFICIENT_DO_NOT_PROMOTE'})
                raise RuntimeError('HISTORICAL_MONTH_INSUFFICIENT_15M_'+start)
            reports.append({'start':start,'end_exclusive':end,'rows':len(q),
                'first_utc':q.bar_start_utc.min().isoformat(),
                'last_utc':q.bar_start_utc.max().isoformat()})
            frames.append(q)
            print('COMPLETE_MONTH',start,'count',len(q),flush=True)
            time.sleep(9)
        joined=pd.concat(frames,ignore_index=True).sort_values('bar_start_utc')
        if joined.bar_start_utc.duplicated().any():raise ValueError('CROSS_MONTH_DUPLICATE')
        annual={str(int(y)):int(len(g)) for y,g in joined.groupby(joined.bar_start_utc.dt.year)}
        if annual.get('2020',0)<17000 or annual.get('2021',0)<17000:raise RuntimeError('YEAR_COVERAGE_TOO_SMALL')
        report['candidate_rows']=len(joined)
        report['annual_candidate']=annual
        report['first_utc']=joined.bar_start_utc.min().isoformat()
        report['last_utc']=joined.bar_start_utc.max().isoformat()
        report['canonical_vendor_source_hash']=hashlib.sha256(joined.to_csv(index=False).encode('utf-8')).hexdigest()
        report['neon']=save_private(joined)
        report['status']='PRIVATE_HISTORY_BACKFILL_COMPLETE'
    except Exception as e:
        report['status']='BLOCKED_NO_SOURCE_PROMOTION'
        report['error_type']=type(e).__name__
        report['error_summary']=str(e)[:120] if 'API_KEY' not in str(e) else 'ACCESS_FAILURE'
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='monthly_receipts'},indent=2,default=str))
    return 0 if report['status']=='PRIVATE_HISTORY_BACKFILL_COMPLETE' else 1
if __name__=='__main__':raise SystemExit(main())
