"""Check historical macro consensus/actual availability 2020–2022 in
already connected Neon source. Read only; only publish aggregated counts.
No source backfill, no 2026 values pretending to be point-in-time.
"""
from pathlib import Path
from datetime import datetime,timezone
import os,json,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_PRAMV_PRE2023_MACRO_SOURCE_AVAILABILITY_AUDIT_20261008.json'
IDS=[
'MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT',
'MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT',
'MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT',
'MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT',
'MACRO_EVENT_V3_FOMC_SCORE']
def main():
    result={'status':'UNDETERMINED','year_bounds':'2020-2025','read_only':True,
      'historical_retrieval_not_pit_by_itself':True,'values_exported':False,
      'tested_series':IDS,'counts':[]}
    try:
        with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
            with con.cursor() as c:
                c.execute('SET TRANSACTION READ ONLY')
                c.execute("""SELECT DATE_PART('year',observation_ts)::integer AS yr,series_id,
                         COUNT(*) AS n,
                         COUNT(*) FILTER (WHERE available_as_of IS NOT NULL) AS has_claimed_ready,
                         COUNT(*) FILTER (WHERE available_as_of <= observation_ts+interval '1 day') AS asof_near_release,
                         MIN(observation_ts)::date AS first_date,
                         MAX(observation_ts)::date AS last_date
                         FROM observations
                         WHERE series_id = ANY(%s)
                         AND observation_ts >= '2020-01-01' AND observation_ts < '2026-01-01'
                         GROUP BY 1,2 ORDER BY 1,2""",(IDS,))
                z=c.fetchall()
                result['counts']=[{'year':r[0],'series_id':r[1],'n':r[2],
                  'ready_notnull':r[3],'near_release_assertion':r[4],
                  'first':str(r[5]),'last':str(r[6])} for r in z]
            con.rollback()
        keys=[str(i) for i in (2020,2021,2022)]
        result['pre2023_complete_cpi_nfp_ahe_unemp_pairs']=all(
            all(sum(r['n'] for r in result['counts'] if r['year']==y and r['series_id']==k)>8
                for k in IDS[:8]) for y in (2020,2021,2022))
        result['status']='AGGREGATE_SOURCE_INVENTORY_READ_ONLY_COMPLETE'
    except Exception as e:
        result['status']='SOURCE_INVENTORY_BLOCKED'
        result['error']=type(e).__name__+': '+str(e)[:130]
    result['timestamp_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print('PRE2023_MACRO_SOURCE_INVENTORY',json.dumps(result),flush=True)
if __name__=='__main__':main()
