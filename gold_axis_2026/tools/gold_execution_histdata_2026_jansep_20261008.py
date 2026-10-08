"""FREE additional 2026 Jan-Aug independent M1 source, plus source concordance.
Never load falsified weekend-inclusive Twelve Data as canonical.
"""
from __future__ import annotations
import os,json, hashlib
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
import psycopg
from gold_execution_histdata_independent_2025_2026_20261008 import get_window,save_private,SOURCE

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_HISTDATA_2026_JAN_SEP_BACKFILL_2026-10-08.json'
def cmp_private():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""SELECT COUNT(*),
              percentile_cont(.5) WITHIN GROUP (ORDER BY abs((t.close_price/h.close_price-1)*10000)),
              percentile_cont(.95) WITHIN GROUP (ORDER BY abs((t.close_price/h.close_price-1)*10000)),
              count(*) FILTER (WHERE extract(isodow FROM t.bar_start_utc)=6)
              FROM gold_research_histdata_xau15m_candidate h
              JOIN gold_research_twelve_xau15m_gap_candidate t
               ON h.bar_start_utc=t.bar_start_utc
              WHERE h.source_id=%s AND t.source_id='TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1'
              AND h.bar_start_utc >= '2026-09-28' AND h.bar_start_utc<'2026-10-01'""",(SOURCE,))
            n,med,p95,sat=c.fetchone()
            c.execute("""SELECT EXTRACT(YEAR FROM bar_start_utc)::INT,EXTRACT(MONTH FROM bar_start_utc)::INT,count(*)
             FROM gold_research_histdata_xau15m_candidate WHERE source_id=%s
             GROUP BY 1,2 ORDER BY 1,2""",(SOURCE,))
            months=[{'year':int(y),'month':int(m),'rows':int(n)} for y,m,n in c.fetchall()]
    return {'overlap_2026_sep28_sep30':int(n),
       'median_abs_bps':float(med) if med is not None else None,
       'p95_abs_bps':float(p95) if p95 is not None else None,
       'matched_saturday_bar_count':int(sat),'independent_source_months':months}
def main():
    report={'asof':'2026-10-08','source':SOURCE,'paid_download':False,
            'year_2026_label_status':'HISTORICAL_INDEPENDENT_CANDIDATE_ONLY',
            'weekend_market_closed_QC_required':True,'status':'BLOCKED'}
    try:
        q,raw=get_window('2026-01-01','2026-08-31','2026_JAN_AUG',12500)
        report['jan_aug']={'native_m1_rows':int(raw),'m15_rows':len(q),
           'full_15_native_minutes':int((q.minute_bars==15).sum()),
           'thin_15m_bars':int((q.minute_bars<15).sum()),
           'first_utc':q.bar_start_utc.min().isoformat(),
           'last_utc':q.bar_start_utc.max().isoformat(),
           'source_hash':hashlib.sha256(q.to_csv(index=False).encode()).hexdigest()}
        report['private_storage']=save_private(q)
        report['concordance']=cmp_private()
        coverage=report['concordance']['independent_source_months']
        for m in range(1,10):
            if not any(int(k['year'])==2026 and int(k['month'])==m and k['rows']>=1400 for k in coverage):
                raise RuntimeError('2026_MONTH_UNDER_COVERAGE_'+str(m))
        report['status']='JAN_SEP_2026_PRIVATE_CANDIDATE_COMPLETE'
    except Exception as exc:
        report['status']='INCOMPLETE_OR_QC_FAILED'
        report['error_type']=type(exc).__name__;report['error_info']=str(exc)[:110]
    report['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps(report,indent=2,default=str))
    return 0 if report['status']=='JAN_SEP_2026_PRIVATE_CANDIDATE_COMPLETE' else 1
if __name__=='__main__':raise SystemExit(main())
