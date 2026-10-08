"""Read-only 2026 candidate-source market-closure QA; aggregates only."""
from datetime import timezone, datetime
from pathlib import Path
import psycopg, os, json
AX=Path(__file__).resolve().parents[1]
out=AX/'GOLD_EXECUTION_XAU15M_2026_WEEKEND_AUDIT_2026-10-08.json'
url=os.environ['NEON_DATABASE_URL']
with psycopg.connect(url,connect_timeout=20) as conn:
    with conn.cursor() as c:
        c.execute("""
        SELECT EXTRACT(ISODOW FROM bar_start_utc)::integer dow, COUNT(*),
               COUNT(*) FILTER (WHERE ABS(close_price-open_price) < 1e-8)
        FROM gold_research_twelve_xau15m_gap_candidate
        WHERE bar_start_utc >= '2026-09-28' AND bar_start_utc < '2026-10-09'
        GROUP BY 1 ORDER BY 1
        """)
        dow=[{'iso_dow':int(d),'bars':int(n),'unchanged_open_close':int(z)} for d,n,z in c.fetchall()]
        c.execute("""
        SELECT (bar_start_utc AT TIME ZONE 'UTC')::date AS d,
               COUNT(*) AS bars,
               COUNT(DISTINCT close_price) AS distinct_closes,
               MIN(close_price)=MAX(close_price) AS all_closes_constant
        FROM gold_research_twelve_xau15m_gap_candidate
        WHERE bar_start_utc >= '2026-09-28' AND bar_start_utc < '2026-10-09'
        GROUP BY 1 ORDER BY 1
        """)
        days=[{'date_utc':str(d),'bars':int(n),'distinct_closes':int(k),
               'all_closes_constant':bool(flag)} for d,n,k,flag in c.fetchall()]
r={'source':'TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1',
   'asof':'2026-10-08','daily_counts':days,'weekday_counts':dow,
   'weekend_utc_bars':sum(x['bars'] for x in dow if x['iso_dow'] in (6,7)),
   'interpretation':'DO_NOT_TREAT_SATURDAY_SUNDAY_BARS_AS_EXECUTABLE_SPOT_HISTORY',
   'model_run_authorized':False,
   'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
