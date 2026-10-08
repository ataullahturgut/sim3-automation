"""Zero-cost independent spot 2025 archive recovery, 2026 Sep availability pilot.
HistData M1 (EST fixed) -> real UTC M15, private persistence only.
Existing Twelve Data and frozen 2025 price archives are never modified.
"""
from __future__ import annotations
import json, os, hashlib
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from histdata_fetcher import fetch_data
from gold_execution_histdata_xau_free_2020_2021 import into_utc_15m

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_HISTDATA_INDEPENDENT_2025_2026_SOURCE_AUDIT_2026-10-08.json'
OLD=AX/'GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026'
MIN_2025=22000

def compare(q,old):
    x=q[['bar_start_utc','close','open']].rename(columns={'bar_start_utc':'ts','close':'new_close','open':'new_open'})
    z=x.merge(old[['ts','close','open']].rename(columns={'close':'old_close','open':'old_open'}),on='ts',validate='one_to_one')
    if not len(z):return {'overlap_rows':0}
    z['diff_bps']=np.abs(z.new_close/z.old_close-1)*10000
    out={'overlap_rows':int(len(z)),'median_abs_close_bps':float(z.diff_bps.median()),
         'p95_abs_close_bps':float(z.diff_bps.quantile(.95))}
    blocks={'2025_PRE_ANOMALY':(z.ts<'2025-04-26'),
      '2025_ANOMALOUS_ARCHIVE_PERIOD':(z.ts>='2025-04-26')}
    for k,mask in blocks.items():
        g=z[mask]
        out[k]={'n':int(len(g)),'median_bps':float(g.diff_bps.median()) if len(g) else None,
           'p95_bps':float(g.diff_bps.quantile(.95)) if len(g) else None}
    return out

def save_private(q):
    url=os.environ.get('NEON_DATABASE_URL','').strip()
    if not url:raise RuntimeError('NEON_SECRET_MISSING')
    with psycopg.connect(url,autocommit=False,connect_timeout=20) as con:
        with con.cursor() as cur:
            # Schema is already present for independent 2020-21 HistData data.
            cur.execute("""SELECT to_regclass('public.gold_research_histdata_xau15m_candidate')""")
            if not cur.fetchone()[0]:raise RuntimeError('HISTDATA_CANDIDATE_TABLE_MISSING')
            cur.execute("""CREATE TEMP TABLE stage_hist (
                source_id text,bar_start_utc timestamptz,open_price float8,
                high_price float8,low_price float8,close_price float8,
                native_minute_bars smallint,source_timezone text,evidence_class text
            ) ON COMMIT DROP""")
            with cur.copy("""COPY stage_hist
               (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                native_minute_bars,source_timezone,evidence_class) FROM STDIN""") as cp:
                for row in q.itertuples(index=False):
                    cp.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                      float(row.open),float(row.high),float(row.low),float(row.close),
                      int(row.minute_bars),'EST_FIXED_UTC_MINUS_05',
                      'HISTORICAL_INDEPENDENT_SOURCE_CANDIDATE_NOT_CANONICAL'))
            cur.execute("""INSERT INTO gold_research_histdata_xau15m_candidate
                (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                 native_minute_bars,source_timezone,evidence_class)
               SELECT source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                      native_minute_bars,source_timezone,evidence_class FROM stage_hist
               ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
            n=cur.rowcount
            cur.execute("""SELECT count(*),min(bar_start_utc),max(bar_start_utc)
                FROM gold_research_histdata_xau15m_candidate WHERE source_id=%s""",(SOURCE,))
            count,first,last=cur.fetchone()
        con.commit()
    return {'status':'PRIVATE_CANDIDATE_SAVED','new_rows':n,'total_rows':count,
      'first_utc':first.isoformat() if first else None,'last_utc':last.isoformat() if last else None}

def get_window(start,end,name,min_rows):
    x=fetch_data('XAUUSD',start,end,'1min',output_format=None,max_workers=1)
    if not x.ok or x.failed_periods:raise RuntimeError('SOURCE_PARTIAL_OR_FAILED_PERIOD_'+name)
    q=into_utc_15m(x.data)
    if len(q)<min_rows:raise RuntimeError('HISTDATA_INCOMPLETE_'+name+'_'+str(len(q)))
    if q.bar_start_utc.duplicated().any():raise RuntimeError('DUPLICATE_UTC_'+name)
    bad=q[(q.bar_start_utc.dt.dayofweek==5)|((q.bar_start_utc.dt.dayofweek==6)&(q.bar_start_utc.dt.hour<21))]
    if len(bad)>5:raise RuntimeError('INDEPENDENT_SOURCE_CLOSED_MARKET_BARS_'+name+'_'+str(len(bad)))
    return q,len(x.data)

def main():
    report={'status':'NOT_ACQUIRED','asof':'2026-10-08',
       'source':SOURCE,'price_exported':False,'paid_download':False,
       'weekend_contract':'No Saturday or early Sunday spot gold bars',
       'windows':{}}
    recovered=[]
    q25=None
    try:
        q25,raw=get_window('2025-01-01','2025-12-31','2025',MIN_2025)
        old=pd.read_csv(OLD,usecols=['dt_utc','open','close']).rename(columns={'dt_utc':'ts'})
        old.ts=pd.to_datetime(old.ts,utc=True)
        comp=compare(q25,old)
        report['windows']['2025']={'status':'INDEPENDENT_FULL_YEAR_RECEIVED',
          'native_m1_rows':raw,'m15_rows':len(q25),
          'first_utc':q25.bar_start_utc.min().isoformat(),
          'last_utc':q25.bar_start_utc.max().isoformat(),
          'full_native_minute_15m_bars':int((q25.minute_bars==15).sum()),
          'bar_subset_lt15':int((q25.minute_bars<15).sum()),
          'source_comparison':comp,'source_hash':hashlib.sha256(q25.to_csv(index=False).encode()).hexdigest()}
        recovered.append(q25)
    except Exception as exc:
        report['windows']['2025']={'status':'FETCH_OR_QC_FAILED','error_type':type(exc).__name__,
                                    'error_description':str(exc)[:140]}
    # Pilot only. 2026 September monthly public release may not exist yet.
    try:
        q26,raw=get_window('2026-09-01','2026-09-30','2026_SEP',1400)
        report['windows']['2026_SEP']={'status':'INDEPENDENT_MONTH_RECEIVED',
          'native_m1_rows':raw,'m15_rows':len(q26),
          'first_utc':q26.bar_start_utc.min().isoformat(),'last_utc':q26.bar_start_utc.max().isoformat()}
        recovered.append(q26)
    except Exception as exc:
        report['windows']['2026_SEP']={'status':'NOT_PROVEN_OR_UNAVAILABLE',
          'error_type':type(exc).__name__,'error_description':str(exc)[:140]}
    if q25 is not None:
        try:
            report['private_storage']=save_private(pd.concat(recovered,ignore_index=True))
            report['status']='2025_INDEPENDENT_CANDIDATE_SAVED'
        except Exception as exc:
            report['status']='PERSIST_FAIL'
            report['private_storage']={'error_type':type(exc).__name__}
    else:report['status']='2025_NOT_RECOVERED'
    report['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False,default=str))
    return 0 if report['status']=='2025_INDEPENDENT_CANDIDATE_SAVED' else 1
if __name__=='__main__':raise SystemExit(main())
