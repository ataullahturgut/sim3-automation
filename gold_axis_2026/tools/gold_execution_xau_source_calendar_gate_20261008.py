"""2026 spot XAU/USD source-integrity gate. No raw price export, no model score.
Saturday UTC hours are indisputably outside ordinary weekday wholesale spot gold.
Sunday 00:00-20:59 UTC is also excluded under either US DST schedule.
Do not silently repair synthetic/fill prices by removing Saturday only.
"""
from __future__ import annotations
import os,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
import numpy as np
import psycopg

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_XAU_SOURCE_CALENDAR_GATE_2026-10-08.json'
PRIVATE_SRC='TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1'
ARCHIVE=AX/'GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv'

def summary(q,name):
    q=q.copy()
    q['ts']=pd.to_datetime(q['ts'],utc=True)
    q=q.sort_values('ts').drop_duplicates('ts')
    days=q.ts.dt.dayofweek
    saturday=(days==5)
    sunday_pre=(days==6)&(q.ts.dt.hour<21)
    hard_closed=saturday|sunday_pre
    weekday=(days<5)
    out={'name':name,'rows':int(len(q)),
       'first_utc':q.ts.min().isoformat() if len(q) else None,
       'last_utc':q.ts.max().isoformat() if len(q) else None,
       'saturday_bar_count':int(saturday.sum()),
       'sunday_before_21utc_count':int(sunday_pre.sum()),
       'hard_closed_interval_count':int(hard_closed.sum()),
       'hard_closed_distinct_utc_dates':int(q.loc[hard_closed,'ts'].dt.date.nunique()),
       'weekday_count':int(weekday.sum()),
       'sample_closed_dates':[str(x) for x in sorted(q.loc[hard_closed,'ts'].dt.date.unique())[:15]]}
    if 'open' in q and 'close' in q:
        o=pd.to_numeric(q['open'],errors='coerce');c=pd.to_numeric(q['close'],errors='coerce')
        out['hard_closed_distinct_close_prices']=int(c[hard_closed].nunique())
        out['hard_closed_nonzero_open_close_bars']=int(((c-o).abs()>1e-8)[hard_closed].sum())
        out['hard_closed_price_min_max_ratio']=float(c[hard_closed].max()/c[hard_closed].min()) if hard_closed.any() else None
    return out

def main():
    url=os.environ.get('NEON_DATABASE_URL')
    if not url:raise RuntimeError('PRIVATE_DB_SECRET_UNAVAILABLE')
    with psycopg.connect(url,connect_timeout=20) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT bar_start_utc,open_price,close_price
             FROM gold_research_twelve_xau15m_gap_candidate
             WHERE source_id=%s AND ((bar_start_utc>='2020-01-01' AND bar_start_utc<'2022-01-01')
             OR (bar_start_utc>='2026-09-28' AND bar_start_utc<'2026-10-09'))
             ORDER BY bar_start_utc''',(PRIVATE_SRC,))
            rows=cur.fetchall()
    q=pd.DataFrame(rows,columns=['ts','open','close'])
    if q.empty:raise RuntimeError('EMPTY_CANDIDATE')
    records=[summary(q[q.ts.dt.year==y],f'TWELVE_{y}') for y in (2020,2021,2026)]
    # Older project archive independent of current new private pull; still not a truly independent spot vendor.
    a=pd.read_csv(ARCHIVE,usecols=['dt_utc','open','close'],low_memory=False)
    a=a.rename(columns={'dt_utc':'ts'})
    a.ts=pd.to_datetime(a.ts,utc=True)
    records+=[summary(a[a.ts.dt.year==y],f'FROZEN_ARCHIVE_{y}') for y in (2023,2024,2025)]
    suspicious=[r['name'] for r in records if r['hard_closed_nonzero_open_close_bars']>5]
    result={'asof':'2026-10-08','status':'SOURCE_CALENDAR_AUDITED',
        'forbidden_market_time_definition':'ALL_SATURDAY_UTC_AND_SUNDAY_0000_2059_UTC',
        'false_positive_note':'Sunday first valid gold quote may vary with daylight savings; pre-21 UTC is a conservative impossible-market interval',
        '2026_canonical_gate':'FAIL_QUARANTINE_ALL_2026_LATE_PRICE_BARS' if
           any(r['name']=='TWELVE_2026' and r['hard_closed_nonzero_open_close_bars']>5 for r in records)
            else 'NEEDS_FURTHER_PROOF',
        'research_constraints':'no interpolation, no weekend deletion as substitute for independent source confirmation, no contaminated 2026 backtest',
        'source_suspect_in_closed_hours':suspicious,
        'records':records,
        'models_rerun':False,'raw_prices_exported':False,
        'time_generated_utc':datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
