"""Independent calendar/anchor/concordance audit of 2022-2024 XAU/USD.
Free HistData M1, fixed EST (NOT NY DST), aggregate to UTC M15.
Private source candidates stored in Neon. Existing archives remain untouched.
Public report contains only aggregate counts, diagnostic percentages, hashes.
"""
from __future__ import annotations
import json, os, hashlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from histdata_fetcher import fetch_data
from gold_execution_histdata_xau_free_2020_2021 import into_utc_15m

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2022_2024_INDEPENDENT_SOURCE_QC_2026-10-08.json'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1'
RAW22=AX/'GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv'
RAW35=AX/'GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv'

def hardclosed(ts):
    day=ts.dt.dayofweek
    return (day==5)|((day==6)&(ts.dt.hour<21))

def persist(q):
    if not os.getenv('NEON_DATABASE_URL'):raise RuntimeError('NEON_DATABASE_URL missing')
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""CREATE TEMP TABLE stage (
            source_id text,bar_start_utc timestamptz,
            open_price float8,high_price float8,low_price float8,close_price float8,
            native_minute_bars smallint,source_timezone text,evidence_class text) ON COMMIT DROP""")
            with c.copy("""COPY stage
                (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                native_minute_bars,source_timezone,evidence_class) FROM STDIN""") as cp:
                for r in q.itertuples(index=False):
                    cp.write_row((SOURCE,r.bar_start_utc.to_pydatetime(),float(r.open),
                     float(r.high),float(r.low),float(r.close),int(r.minute_bars),
                     'EST_FIXED_UTC_MINUS_05','INDEPENDENT_XAUUSD_2022_2024_CANDIDATE_NONCANONICAL'))
            c.execute("""INSERT INTO gold_research_histdata_xau15m_candidate
               (source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                native_minute_bars,source_timezone,evidence_class)
               SELECT source_id,bar_start_utc,open_price,high_price,low_price,close_price,
                native_minute_bars,source_timezone,evidence_class FROM stage
               ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
            ins=c.rowcount
            c.execute("""SELECT count(*)
                  FROM gold_research_histdata_xau15m_candidate WHERE source_id=%s""",(SOURCE,))
            n=c.fetchone()[0]
        con.commit()
    return dict(new_rows=int(ins),private_rows=int(n))

def oldarchive(y):
    file=RAW22 if y==2022 else RAW35
    x=pd.read_csv(file,usecols=['dt_utc','open','high','low','close'],low_memory=False)
    x['ts']=pd.to_datetime(x.dt_utc,utc=True)
    x=x[x.ts.dt.year==y][['ts','open','high','low','close']]
    for col in ['open','high','low','close']:x[col]=pd.to_numeric(x[col],errors='coerce')
    if x.ts.duplicated().any(): raise RuntimeError('FROZEN_DUPLICATE_UTC_'+str(y))
    return x

def build_labels(x):
    """Only complete DAY paths, exact same-source next eligible trading dates."""
    x=x.copy();x.ts=pd.to_datetime(x.ts,utc=True)
    x=x.sort_values('ts').set_index('ts')
    days=sorted({t.date() for t in x.index if t.hour==6 and t.minute==0})
    out=[]
    def v(day,hm,col):
        hh,mm=map(int,hm.split(':'))
        t=pd.Timestamp(day,tz='UTC')+pd.Timedelta(hours=hh,minutes=mm)
        if t not in x.index:return np.nan
        return float(x.at[t,col])
    def sign(a,b):
        if not np.isfinite(a) or not np.isfinite(b) or a<=0 or b<=0:return np.nan
        return int(b>a)
    for i,d in enumerate(days):
        nxt=days[i+1] if i+1<len(days) else None
        # 09:00 to 17:00 Istanbul means UTC 06:00 open -> 13:45 close
        ds=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=6)
        daytime=all((ds+pd.Timedelta(minutes=15*j)) in x.index for j in range(32))
        dy=sign(v(d,'06:00','open'),v(d,'13:45','close')) if daytime else np.nan
        oy=sign(v(d,'14:00','open'),v(nxt,'05:45','close')) if nxt else np.nan
        out.append({'date':str(d),'next_date':str(nxt) if nxt else '',
                    'day_y':dy,'ovn_y':oy,'full_day':int(daytime)})
    return pd.DataFrame(out)

def test(y,q,old):
    n15=len(q);hard=hardclosed(q.bar_start_utc)
    h_old=hardclosed(old.ts)
    if hard.any():raise RuntimeError('HISTDATA_CLOSED_HOURS_'+str(y))
    if n15<14000:raise RuntimeError('INDEPENDENT_YEAR_SEVERELY_THIN_'+str(y))
    orig=old.rename(columns={'ts':'bar_start_utc'})
    m=q.merge(orig,on='bar_start_utc',suffixes=('_ind','_frozen'),validate='one_to_one')
    if len(m)<14000: raise RuntimeError('VENDOR_OVERLAP_TOO_SMALL_'+str(y))
    v=np.abs(m.close_ind/m.close_frozen-1)*1e4
    dind=build_labels(q.rename(columns={'bar_start_utc':'ts'}))
    dfr=build_labels(old)
    dm=dfr.merge(dind,on='date',suffixes=('_frozen','_ind'),validate='one_to_one')
    diff={}
    for k in ['day','ovn']:
        s=dm.dropna(subset=[k+'_y_frozen',k+'_y_ind'])
        if k=='ovn':
            s=s[s.next_date_frozen==s.next_date_ind]
        diff[k]={'matched_origins':int(len(s)),
           'direction_disagreements':int((s[k+'_y_frozen']!=s[k+'_y_ind']).sum()),
           'disagreement_share':float((s[k+'_y_frozen']!=s[k+'_y_ind']).mean()) if len(s) else None}
    weekend_frozen=int(h_old.sum())
    return {'year':y,'histdata_1min_to_15min_rows':n15,
      'independent_year_coverage_warning':bool(n15<22000),
      'archive_original_rows':len(old),
      'histdata_complete_native_minutes':int((q.minute_bars==15).sum()),
      'histdata_incomplete_native_minutes':int((q.minute_bars<15).sum()),
      'histdata_hard_closed_bars':int(hard.sum()),
      'frozen_hard_closed_bars':weekend_frozen,
      'matched_m15_bars':int(len(m)),
      'median_abs_close_bps':float(v.median()),
      'p95_abs_close_bps':float(v.quantile(.95)),
      'p99_abs_close_bps':float(v.quantile(.99)),
      'over_50bps_share':float((v>50).mean()),
      'independent_above_frozen_share':float((m.close_ind>m.close_frozen).mean()),
      'label_concordance':diff,
      'independent_month_counts':{str(int(k)):int(n) for k,n in
         q.groupby(q.bar_start_utc.dt.month).size().items()},
      'independent_sha256':hashlib.sha256(q.to_csv(index=False).encode()).hexdigest()}

def main():
    report={'asof':'2026-10-08','status':'INCOMPLETE',
        'independent_source':SOURCE,'existing_frozen_files_unchanged':True,
        'raw_licensed_prices_exported':False,'paid_historical_price_download_usd':0,
        'est_conversion':'UTC=EST_FIXED+5, NOT America/New_York DST',
        'target_labels':'DAY 09:00 open->16:45 close TR; OVN 17:00 open->next eligible 08:45 close TR',
        'market_closure_definition':'Saturday UTC + Sunday UTC before 21:00',
        'years':{},'private_storage':None}
    qs=[]
    try:
        for y in (2022,2023,2024):
            x=fetch_data('XAUUSD',f'{y}-01-01',f'{y}-12-31',
                        '1min',output_format=None,max_workers=1)
            if not x.ok or x.failed_periods:raise RuntimeError('HISTDATA_FETCH_FAILED_'+str(y))
            q=into_utc_15m(x.data)
            q=q[q.bar_start_utc.dt.year==y].copy()
            stat=test(y,q,oldarchive(y))
            stat['native_source_m1_rows']=len(x.data)
            report['years'][str(y)]=stat
            qs.append(q)
            print('YEAR_SOURCE_QC_COMPLETE',y,json.dumps({k:stat[k] for k in
                      ['matched_m15_bars','median_abs_close_bps','p95_abs_close_bps',
                       'frozen_hard_closed_bars','label_concordance']}),flush=True)
        report['private_storage']=persist(pd.concat(qs,ignore_index=True))
        report['status']='2022_2024_SOURCE_CROSSCHECK_COMPLETE_NOT_PROMOTED'
    except Exception as e:
        report['status']='INCOMPLETE_OR_QC_FAILED'
        report['error_type']=type(e).__name__
        report['error_summary']=str(e)[:240]
    report['completed_at']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps(report,indent=2,default=str),flush=True)
    return 0 if report['status']=='2022_2024_SOURCE_CROSSCHECK_COMPLETE_NOT_PROMOTED' else 1

if __name__=='__main__':raise SystemExit(main())
