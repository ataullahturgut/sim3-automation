"""Repair-test HistData 2023 Jan-Jul only, source-consistent and free.
Fetch each month separately, compare with existing vendor candidate, and
insert ONLY timestamp-absent bars with same upstream source, never overwrite.
Any existing quote revision is counted, not silently accepted.
"""
from pathlib import Path
from datetime import datetime, timezone
import json,os,hashlib
import numpy as np, pandas as pd, psycopg
from histdata_fetcher import fetch_data
from gold_execution_histdata_xau_free_2020_2021 import into_utc_15m
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2023_HISTDATA_MONTHLY_REPAIR_QC_2026-10-08.json'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1'
def scan():
    report={'asof':'2026-10-08','status':'INCOMPLETE',
            'source':SOURCE,'model_run':False,'paid_download_usd':0,
            'raw_prices_public':False,'months':[]}
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            for month in range(1,8):
                a=f'2023-{month:02d}-01'
                nxt=f'2023-{month+1:02d}-01'
                last=(pd.Timestamp(nxt)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                row={'month':a,'end_inclusive':last}
                c.execute("""SELECT bar_start_utc,open_price,close_price
                  FROM gold_research_histdata_xau15m_candidate
                  WHERE source_id=%s AND bar_start_utc >= %s AND bar_start_utc < %s
                  ORDER BY bar_start_utc""",(SOURCE,a,nxt))
                pre=pd.DataFrame(c.fetchall(),columns=['bar_start_utc','pre_open','pre_close'])
                row['existing_rows_before']=len(pre)
                try:
                    payload=fetch_data('XAUUSD',a,last,'1min',
                                       output_format=None,max_workers=1)
                    if not payload.ok or payload.failed_periods:
                        raise RuntimeError('HISTDATA_MONTH_FETCH_PARTIAL')
                    q=into_utc_15m(payload.data)
                    q=q[(q.bar_start_utc>=pd.Timestamp(a,tz='UTC'))&
                         (q.bar_start_utc<pd.Timestamp(nxt,tz='UTC'))].copy()
                    q=q.sort_values('bar_start_utc')
                    if q.bar_start_utc.duplicated().any():raise RuntimeError('DUPLICATES')
                    if len(q)<500:raise RuntimeError('THIN_MONTH_SOURCE')
                    row['new_month_fetch_count']=len(q)
                    row['minute_input_count']=int(len(payload.data))
                    match=q.merge(pre,on='bar_start_utc',how='inner',validate='one_to_one')
                    row['overlap_bars']=len(match)
                    row['overlap_changed_close_gt_1e8']=int((abs(match.close-match.pre_close)>1e-8).sum())
                    if row['overlap_changed_close_gt_1e8']>0:
                        row['overlap_max_close_bps']=float((abs(match.close/match.pre_close-1)*10000).max())
                    missing=q[~q.bar_start_utc.isin(pre.bar_start_utc)]
                    row['new_missing_bar_candidates']=len(missing)
                    weekend=((missing.bar_start_utc.dt.dayofweek==5)|
                       ((missing.bar_start_utc.dt.dayofweek==6)&(missing.bar_start_utc.dt.hour<21)))
                    if weekend.any():raise RuntimeError('WEEKEND_SOURCE_QC')
                    if len(missing):
                        c.execute("""CREATE TEMP TABLE IF NOT EXISTS qc_stage_2023 (
                            source_id text,bar_start_utc timestamptz,open_price float8,
                            high_price float8,low_price float8,close_price float8,
                            native_minute_bars smallint,source_timezone text,evidence_class text
                        ) ON COMMIT DROP""")
                        with c.copy("""COPY qc_stage_2023 (
                            source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                            native_minute_bars,source_timezone,evidence_class
                        ) FROM STDIN""") as cp:
                            for r in missing.itertuples(index=False):
                                cp.write_row((SOURCE,r.bar_start_utc.to_pydatetime(),
                                    float(r.open),float(r.high),float(r.low),float(r.close),
                                    int(r.minute_bars),'EST_FIXED_UTC_MINUS_05',
                                    '2023_MONTHLY_SOURCE_RECHECK_CANDIDATE_NOT_PROMOTED'))
                        c.execute("""INSERT INTO gold_research_histdata_xau15m_candidate (
                           source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                           native_minute_bars,source_timezone,evidence_class)
                           SELECT source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                           native_minute_bars,source_timezone,evidence_class FROM qc_stage_2023
                           ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
                        row['inserted_new_bars']=int(c.rowcount)
                        c.execute('TRUNCATE qc_stage_2023')
                    else: row['inserted_new_bars']=0
                    con.commit()
                    row['status']='MONTH_FETCH_CHECKED'
                except Exception as ex:
                    con.rollback()
                    row['status']='MONTH_FAILED_NO_INSERT'
                    row['error_type']=type(ex).__name__
                    row['error_summary']=str(ex)[:100]
                report['months'].append(row)
                print('MONTH_QC',json.dumps(row),flush=True)
            c.execute("""SELECT date_trunc('month',bar_start_utc)::date,COUNT(*)
             FROM gold_research_histdata_xau15m_candidate
             WHERE source_id=%s AND bar_start_utc>='2023-01-01' AND bar_start_utc<'2024-01-01'
             GROUP BY 1 ORDER BY 1""",(SOURCE,))
            report['after_monthly_bar_counts']={str(m):int(n) for m,n in c.fetchall()}
    report['status']='COMPLETED_MONTHLY_RECOVERY_AUDIT'
    report['source_2023_coverage_pass']=all(x['status']=='MONTH_FETCH_CHECKED' for x in report['months']) and all(v>=1750 for v in report['after_monthly_bar_counts'].values())
    report['completed_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT',json.dumps(report,indent=2),flush=True)
if __name__=='__main__':scan()
