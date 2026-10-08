"""2020-2021 XAU independent vendor agreement on target labels (no model training).
Public output consists of aggregates only, market quotes remain private.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os
import pandas as pd
import numpy as np
import psycopg
from gold_execution_2022_2024_independent_source_qc_20261008 import build_labels,hardclosed

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2020_2021_SOURCE_TARGET_CONCORDANCE_2026-10-08.json'
H='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1'
T='TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1'
def fetch():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""SELECT source_id,bar_start_utc,open_price,close_price
              FROM gold_research_histdata_xau15m_candidate
              WHERE source_id=%s AND bar_start_utc >= '2020-01-01' AND bar_start_utc<'2022-01-01'
              ORDER BY bar_start_utc""",(H,))
            h=pd.DataFrame(c.fetchall(),columns=['source','ts','open','close'])
            c.execute("""SELECT source_id,bar_start_utc,open_price,close_price
              FROM gold_research_twelve_xau15m_gap_candidate
              WHERE source_id=%s AND bar_start_utc >= '2020-01-01' AND bar_start_utc<'2022-01-01'
              ORDER BY bar_start_utc""",(T,))
            t=pd.DataFrame(c.fetchall(),columns=['source','ts','open','close'])
    for df in (h,t):
        df.ts=pd.to_datetime(df.ts,utc=True)
        if df.ts.duplicated().any():raise RuntimeError('SOURCE_DUPLICATE_UTC')
    if len(h)<45000 or len(t)<45000:raise RuntimeError('INCOMPLETE_EITHER_SOURCE')
    return h,t

def study(y,h,t):
    h=h[h.ts.dt.year==y].copy()
    t=t[t.ts.dt.year==y].copy()
    a=build_labels(h[['ts','open','close']])
    b=build_labels(t[['ts','open','close']])
    m=a.merge(b,on='date',suffixes=('_hist','_twelve'),validate='one_to_one')
    directions={}
    for k in ['day','ovn']:
        d=m.dropna(subset=[k+'_y_hist',k+'_y_twelve'])
        if k=='ovn':d=d[d.next_date_hist==d.next_date_twelve]
        n=len(d)
        directions[k]={'same_date_matched_n':n,'direction_disagreement_n':int((d[k+'_y_hist']!=d[k+'_y_twelve']).sum()),
          'direction_disagreement_pct':float(100*(d[k+'_y_hist']!=d[k+'_y_twelve']).mean()) if n else None}
    x=h.merge(t,on='ts',suffixes=('_hist','_twelve'),validate='one_to_one')
    diff=np.abs(x.close_hist/x.close_twelve-1)*10000
    return {'year':y,'histdata_rows':int(len(h)),'twelve_rows':int(len(t)),
      'histdata_hard_closed_market_bars':int(hardclosed(h.ts).sum()),
      'twelve_hard_closed_market_bars':int(hardclosed(t.ts).sum()),
      'matched_15m_prices':int(len(x)),
      'close_abs_median_bps':float(diff.median()),
      'close_abs_p95_bps':float(diff.quantile(.95)),
      'target_agreement':directions,
      'twelve_january_early_unavailable':y==2020}
def main():
    h,t=fetch()
    result={'status':'COMPLETED_SOURCE_LEVEL_CONCORDANCE_NOT_CANONICAL',
      'asof':'2026-10-08','histdata_source':H,'twelve_source':T,
      'price_level_vendors_must_not_be_spliced':True,'year_results':{},
      'price_raw_exported':False,'model_retrained':False}
    for year in (2020,2021):result['year_results'][str(year)]=study(year,h,t)
    result['completed_at']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
