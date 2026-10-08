"""V2 read-only source-aware target grading, separate from v1.
Only create a NEW private table, never overwrite legacy prices, labels, forecasts.
Guarded by 2020–2025 independent forensic acceptance receipt.
Mark 64-hour Fri->Mon bank HOLD distinct from 16-hour Tue-Friday overnight.
Low margin, BID/ASK sign disagreements and wide broker spread are data QC
caveats, not retroactively optimized prediction filters.
"""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib
import pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
AUDIT=AX/'GOLD_EXECUTION_2020_2025_PRICE_LABEL_FORENSIC_AUDIT_20261008.json'
OUT=AX/'GOLD_EXECUTION_2020_2025_SESSION_TARGET_V2_PROVENANCE_QC_20261008.json'
S='EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1'
T1='gold_research_evduka_xau_session_target_candidate_v1'
T2='gold_research_evduka_xau_session_quality_gate_v2'
def main():
    report={'status':'FAIL','asof':'2026-10-08','old_target_immutable':True,
      'private_v2_new_table':T2,'model_retrained':False,'threshold_not_tuned_on_2025':True,
      'session_breakdown':'DAY 09->17 same TR date; OVN weekday 17->next 09 (16 hours); FRI_OVN 17->Monday09 (64 hours)',
      'no_fabricated_prices':True,'no_source_blending':True}
    a=json.loads(AUDIT.read_text())
    if a['status']!='SIX_YEAR_PRICE_AND_INDEPENDENT_TARGET_RECOMPUTE_QC_PASSED' or \
       a['record_count']!=141890 or a['issue_dates']!=1549:
        raise RuntimeError('FORENSIC_RECEIPT_NOT_ACCEPTED')
    if not all(x['target_recompute']['wrong_persisted_direction']['day_y']==0 and
               x['target_recompute']['wrong_persisted_direction']['overnight_y']==0
               for x in a['years'].values()):raise RuntimeError('FORENSIC_HAS_LABEL_ERRORS')
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute(f"""SELECT issue_date,year,next_expected_date,day_y,overnight_y,
                    day_gate,overnight_gate,day_bid_logret,overnight_bid_logret,
                    day_bidask_sign_disagreement,ovn_bidask_sign_disagreement,
                    low_margin_day_10bps,low_margin_ovn_10bps,spread_09_bps,spread_17_bps
                 FROM {T1} WHERE source_id=%s ORDER BY issue_date""",(S,))
            vals=c.fetchall()
        fields=['issue_date','year','next_expected_date','day_y','overnight_y',
            'day_gate','overnight_gate','day_bid_logret','overnight_bid_logret',
            'day_bidask_sign_disagreement','ovn_bidask_sign_disagreement',
            'low_margin_day_10bps','low_margin_ovn_10bps','spread_09_bps','spread_17_bps']
        d=pd.DataFrame(vals,columns=fields)
        if len(d)!=1549 or d.issue_date.duplicated().any():raise RuntimeError('T1_CHANGED')
        d['origin_weekday']=pd.to_datetime(d.issue_date).dt.dayofweek
        d['overnight_span_type']=d.origin_weekday.map(
             lambda k:'FRI_TO_MON_WEEKEND_64H' if k==4 else 'REGULAR_NEXT_WEEKDAY_16H')
        d['overnight_elapsed_hours']=d.origin_weekday.map(lambda k:64 if k==4 else 16)
        def quality(y,conflict,low,spread):
            if pd.isna(y):return 'NO_VALID_SOURCE_LABEL'
            if bool(conflict) if pd.notna(conflict) else False:return 'BID_ASK_DIRECTION_CONFLICT'
            if bool(low) if pd.notna(low) else False:return 'LOW_MOVE_ABS_LE_10BPS'
            if pd.notna(spread) and float(spread)>30:return 'SOURCE_SPREAD_GT_30BPS'
            return 'STRUCTURALLY_CONSISTENT_BID_RESEARCH_LABEL'
        d['day_quality_class']=[quality(r.day_y,r.day_bidask_sign_disagreement,
                                    r.low_margin_day_10bps,r.spread_09_bps)
            for r in d.itertuples(index=False)]
        d['overnight_quality_class']=[quality(r.overnight_y,r.ovn_bidask_sign_disagreement,
                                    r.low_margin_ovn_10bps,r.spread_17_bps)
            for r in d.itertuples(index=False)]
        d['source_id']=S
        d['quote_semantics']='DUKASCOPY_DERIVED_BROKER_BID_RETURN_LABEL_WITH_SEPARATE_ASK'
        d['research_vintage']='HISTORICAL_RECOVERED_2026-10-08_NOT_PIT'
        d['original_issue_date']=d.issue_date
        with con.cursor() as c:
            c.execute(f"""CREATE TABLE IF NOT EXISTS {T2} (
              issue_date DATE PRIMARY KEY,year INTEGER NOT NULL,
              next_expected_date DATE,day_y SMALLINT,overnight_y SMALLINT,
              day_quality_class TEXT NOT NULL,overnight_quality_class TEXT NOT NULL,
              overnight_span_type TEXT NOT NULL,overnight_elapsed_hours SMALLINT NOT NULL,
              source_id TEXT NOT NULL,quote_semantics TEXT NOT NULL,
              research_vintage TEXT NOT NULL,
              generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            cols=['issue_date','year','next_expected_date','day_y','overnight_y',
                  'day_quality_class','overnight_quality_class',
                  'overnight_span_type','overnight_elapsed_hours',
                  'source_id','quote_semantics','research_vintage']
            c.execute("""CREATE TEMP TABLE stage(
                issue_date DATE,year INTEGER,next_expected_date DATE,
                day_y SMALLINT,overnight_y SMALLINT,
                day_quality_class TEXT,overnight_quality_class TEXT,
                overnight_span_type TEXT,overnight_elapsed_hours SMALLINT,
                source_id TEXT,quote_semantics TEXT,research_vintage TEXT
            ) ON COMMIT DROP""")
            with c.copy('COPY stage ('+','.join(cols)+') FROM STDIN') as cp:
                for r in d.itertuples(index=False):
                    cp.write_row((r.issue_date,int(r.year),r.next_expected_date,
                        int(r.day_y) if pd.notna(r.day_y) else None,
                        int(r.overnight_y) if pd.notna(r.overnight_y) else None,
                        r.day_quality_class,r.overnight_quality_class,
                        r.overnight_span_type,int(r.overnight_elapsed_hours),
                        S,r.quote_semantics,r.research_vintage))
            c.execute(f"""INSERT INTO {T2} ({','.join(cols)})
              SELECT {','.join(cols)} FROM stage
              ON CONFLICT(issue_date) DO NOTHING""")
            inserted=c.rowcount
        con.commit()
        years={}
        for y,z in d.groupby('year'):
            years[str(y)]={'origins':len(z),
              'DAY':{str(k):int(v) for k,v in z.day_quality_class.value_counts().items()},
              'OVERNIGHT':{str(k):int(v) for k,v in z.overnight_quality_class.value_counts().items()},
              'overnight_weekend_holds_n':int((z.overnight_span_type=='FRI_TO_MON_WEEKEND_64H').sum()),
              'weekend_valid_overnight_n':int(((z.overnight_span_type=='FRI_TO_MON_WEEKEND_64H')&z.overnight_y.notna()).sum()),
              'weekday_valid_overnight_n':int(((z.overnight_span_type=='REGULAR_NEXT_WEEKDAY_16H')&z.overnight_y.notna()).sum())}
        report['years']=years
        report['private_inserted_v2_rows']=int(inserted)
        report['private_target_count']=len(d)
        report['weekend_issue_date_count']=int((d.overnight_span_type=='FRI_TO_MON_WEEKEND_64H').sum())
        report['weekend_valid_n']=int(((d.overnight_span_type=='FRI_TO_MON_WEEKEND_64H')&d.overnight_y.notna()).sum())
        report['status']='SOURCE_AUDIT_GATED_V2_TARGET_SCOPE_SAVED_NOT_MODEL_APPROVED'
    report['finished_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
