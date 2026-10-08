"""Original 2026 PRAMV M4 PIT macro readiness without exposing raw consensus.

2026 actual-consensus pairs must align on exact release timestamp, have
as-of<=decision (not inferred from retrospective value), no missing official
scheduled CPI NFP FOMC means known no release; fail closed.
"""
from pathlib import Path
import os,json
import pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_2026_PRAMV_MACRO_PIT_SOURCE_READINESS_20261008.json"
BASE="2026-10-08"
PAIRS={
 'CPI':('MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT'),
 'NFP':('MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT'),
 'AHE':('MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT'),
 'UNEMP':('MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT')}
FOMC='MACRO_EVENT_V3_FOMC_SCORE'
FED2026=['2026-01-28','2026-03-18','2026-04-29','2026-06-17',
         '2026-07-29','2026-09-16']
EXPECTED_CPI=['2026-01-13','2026-02-13','2026-03-11','2026-04-10','2026-05-12',
 '2026-06-10','2026-07-14','2026-08-12','2026-09-11']
def main():
    wanted=[FOMC]+[q for xx in PAIRS.values() for q in xx]
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=30) as conn:
      with conn.cursor() as cur:
        cur.execute('SET TRANSACTION READ ONLY')
        cur.execute("""SELECT series_id,observation_ts,available_as_of,retrieved_at,lineage_id
             FROM observations WHERE series_id = ANY(%s)
             AND observation_ts >= '2026-01-01' AND observation_ts<'2026-10-09'
             ORDER BY series_id,observation_ts,retrieved_at""",(wanted,))
        records=cur.fetchall()
    df=pd.DataFrame(records,columns=['series_id','ts','available','retrieved','lineage'])
    summary={"asof":BASE,"status":"NOT_CLEARED_FOR_2026_MACRO_M4",
      "audit":"read_only_counts_release_dates_without_publishing_numeric_consensus",
      "expected_fed_regular_scheduled_statement_dates":FED2026,
      "expected_BLS_CPI_scheduled_release_dates_through_2026_09":EXPECTED_CPI,
      "official_FOMC":"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
      "official_BLS":"https://www.bls.gov/schedule/2026/",
      "total_2026_observation_rows":len(df),
      "original_M4_original_PRAMV_can_be_scored":False}
    if df.empty:
      summary["reason"]="REQUIRED_2026_MACRO_NEON_OBSERVATIONS_EMPTY"
    else:
      for k in ('ts','available','retrieved'):df[k]=pd.to_datetime(df[k],utc=True,errors='coerce')
      counts={}
      for id in wanted:
        z=df[df.series_id==id]
        dates=sorted(set(z.ts.dt.date.dropna().astype(str)))
        counts[id]={"rows":len(z),"unique_release_UTC_dates":len(dates),
          "release_dates_UTC":dates,
          "missing_available_asof":int(z.available.isna().sum()),
          "release_available_asof_later_than_24h":int((z.available>z.ts+pd.Timedelta(hours=24)).sum()),
          "retrospectively_retrieved_after_release":int((z.retrieved>z.ts).sum())}
      summary["source_series_receipts"]=counts
      source_qc={}
      for name,(aid,cid) in PAIRS.items():
        a=df[df.series_id==aid][['ts','available']].drop_duplicates('ts')
        b=df[df.series_id==cid][['ts','available']].drop_duplicates('ts')
        merged=a.merge(b,on='ts',how='outer',indicator=True,suffixes=('_actual','_consensus'))
        source_qc[name]={"matching_release_pairs":int((merged._merge=='both').sum()),
          "unmatched":int((merged._merge!='both').sum()),
          "both_asof_present":int((merged.available_actual.notna()&merged.available_consensus.notna()).sum())}
      summary["paired_actual_consensus_qc"]=source_qc
      summary["source_has_all_FED2026_regular"] = (
         set(FED2026).issubset(set(counts[FOMC]["release_dates_UTC"])))
      summary["source_has_CPI2026_9"]=(
         set(EXPECTED_CPI).issubset(set(counts[PAIRS['CPI'][0]]["release_dates_UTC"])))
      complete=(summary["source_has_all_FED2026_regular"] and summary["source_has_CPI2026_9"]
        and all(x["matching_release_pairs"]>=8 and x["unmatched"]==0 and
               x["both_asof_present"]>=8 for x in source_qc.values()))
      summary["retrospective_macro_source_coverage_provisionally_ready"]=bool(complete)
      summary["original_M4_original_PRAMV_can_be_scored"]=False
      summary["reason"]=("COVERAGE_PROVISIONALLY_PRESENT_BUT_RELEASE_TIME_CONSENSUS_VINTAGE_REQUIRES_CERTIFICATION"
        if complete else "SOURCE_2026_FOMC_CPI_OR_ACTUAL_CONSENSUS_MISSING")
    OUT.write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print("2026_ORIGINAL_MACRO_SOURCE_PIT_READINESS",json.dumps(summary,default=str),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as err:
      import traceback
      tb=traceback.extract_tb(err.__traceback__)[-1]
      obj={"status":"MACRO_READINESS_SQL_BLOCKED","type":type(err).__name__,
           "function":tb.name,"line":tb.lineno,"no_false_zero_event":True}
      OUT.write_text(json.dumps(obj,indent=2)+"\n")
      print("MACRO_READINESS_FAILED",json.dumps(obj),flush=True)
