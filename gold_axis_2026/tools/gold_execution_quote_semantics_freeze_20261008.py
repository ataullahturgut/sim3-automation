"""Freeze exact quote type of the verified one-provider research candidate.
HistData Generic ASCII one-minute bars are BID OHLC, NOT OTC mid nor bank ask.
This only corrects source metadata, not bar values, labels or old frozen files.
"""
from pathlib import Path
from datetime import datetime, timezone
import os,json,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_XAU_QUOTE_TYPE_SOURCE_CONTRACT_2026-10-08.json'
TABLE='gold_research_xau_execution_origin_quality_candidate_v1'
def main():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("SELECT to_regclass(%s)",('public.'+TABLE,))
            if not c.fetchone()[0]:raise RuntimeError('GOVERNED_CANDIDATE_TABLE_MISSING')
            c.execute(f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS source_quote_type TEXT")
            c.execute(f"""UPDATE {TABLE} SET source_quote_type='HISTDATA_GENERIC_ASCII_M1_BID_OHLC'
                     WHERE source_provider='HISTDATA' AND source_quote_type IS NULL""")
            updated=c.rowcount
            c.execute(f"""SELECT COUNT(*), COUNT(*) FILTER (
                   WHERE source_quote_type='HISTDATA_GENERIC_ASCII_M1_BID_OHLC'),
                   COUNT(*) FILTER (WHERE source_quote_type IS NULL),
                   COUNT(DISTINCT source_provider)
                FROM {TABLE}""")
            total,correct,missing,provider_n=c.fetchone()
            if int(total)!=int(correct) or int(missing)>0 or int(provider_n)!=1:
                raise RuntimeError('QUOTE_TYPE_BINDING_QC_FAIL')
        con.commit()
    r={'status':'QUOTE_SEMANTICS_BOUND_TO_PRIVATE_RESEARCH_PANEL',
      'asof':'2026-10-08',
      'provider':'HistData.com Generic ASCII M1 Bid OHLC',
      'timezone':'EST_fixed_UTCminus5_no_US_DST',
      'original_raw_M1_quote':'BID_OHLC',
      'derived_M15_price':'BID_OHLC_AGGREGATED',
      'not_midpoint':True,'not_bank_executable_bid_ask':True,
      'Twelve_Data': 'COMPOSITE_SOURCE_DIFFERENT_REFERENCE_NOT_INTERCHANGEABLE_WITH_HISTDATA_BID',
      'private_table':TABLE,'private_target_rows':int(total),'updated_source_semantics_rows':int(updated),
      'all_rows_correct_quote_identity':True,
      'model_label_returns_modified':False,'raw_price_modified':False,
      'histdata_official_spec_url':'https://www.histdata.com/f-a-q/data-files-detailed-specification/',
      'twelve_data_vendor_discrepancy_url':'https://support.twelvedata.com/en/articles/11850499-understanding-price-deviations-in-commodities-and-forex-data',
      'frozen_utc':datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
