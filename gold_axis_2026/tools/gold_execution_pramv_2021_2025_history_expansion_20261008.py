"""PRAMV frozen original architecture full-history extension 2021-2025.

Found in private Neon: complete 2021 & 2022 12/12 monthly NFP/AHE/
UNEMP and CPI first-prints/consensus, 8/8 Fed FOMC decision times.
2020 NFP/AHE/UNEMP only 11, and 2020 unscheduled emergency Fed
interventions not prescheduled => 2020 candidate cannot be treated
as fully source-PIT-complete model warmup.

Build temporary private combined 2021–25 macro ledger at job runtime,
in-memory Neon's first-print/consensus. GitHub commits only aggregates
and model metrics, no 2020–22 private macro values. Record that historical
consensus 'PIT' was 2026 retrieved and release time is an assertion, not
an independently archived true pre-release expectation vintage.

Fixed PRAMV M4, RFR and gate unchanged; both 2021-22 and 2023-24
historical source labels matured before each training decision.
Separate version from frozen 2026-10-07 prospective PRAMV.
"""
from pathlib import Path
import sys,os,json,hashlib
from datetime import datetime,timezone
import pandas as pd,numpy as np,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/'tools'))
import gold_execution_pramv_repaired_full_retrain_20261008 as base
import gold_execution_2020_2025_all_existing_model_replay_20261008 as common
G=AX/'GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv'
OR=AX/'GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv'
NAME='GOLD_EXECUTION_PRAMV_ORIGINAL_FULLER_HISTORY_2021_2025_SOURCE_MACRO_RETEST_20261008'
AGG=AX/(NAME+'_MACRO_PRE2023_QC.json')
ORIGINAL=['CPI','NFP','AHE','UNEMP']
PAIRS={
 'CPI':('MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT'),
 'NFP':('MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT'),
 'AHE':('MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT'),
 'UNEMP':('MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT')}
FOMC="MACRO_EVENT_V3_FOMC_SCORE"
FED_HOURS={
 2021:['2021-01-27','2021-03-17','2021-04-28','2021-06-16','2021-07-28','2021-09-22','2021-11-03','2021-12-15'],
 2022:['2022-01-26','2022-03-16','2022-05-04','2022-06-15','2022-07-27','2022-09-21','2022-11-02','2022-12-14']}
def conn_load():
    ids=[FOMC]+[q for pair in PAIRS.values() for q in pair]
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=30) as cn:
        with cn.cursor() as cur:
            cur.execute('SET TRANSACTION READ ONLY')
            cur.execute("""SELECT series_id,observation_ts,value,available_as_of,retrieved_at,lineage_id
                 FROM observations WHERE series_id = ANY(%s)
                 AND observation_ts >= '2021-01-01' AND observation_ts<'2023-01-01'
                 ORDER BY series_id,observation_ts,retrieved_at""",(ids,))
            rows=cur.fetchall()
        cn.rollback()
    raw=pd.DataFrame(rows,columns=['series_id','event_ts','value','available_at','retrieved_at','lineage'])
    for k in ['event_ts','available_at','retrieved_at']:raw[k]=pd.to_datetime(raw[k],utc=True)
    if raw.empty:raise RuntimeError('MACRO_SOURCE_NEON_EMPTY')
    dup=raw.groupby(['series_id','event_ts'],dropna=False)
    if any(z.value.nunique(dropna=False)>1 or z.available_at.nunique(dropna=False)>1 for _,z in dup):
        raise RuntimeError('MACRO_MISMATCHED_VINTAGE')
    raw=raw.sort_values('retrieved_at').drop_duplicates(['series_id','event_ts'],keep='last')
    return raw
def raw_calendar(raw):
    rows=[];summary={}
    for year in [2021,2022]:
        sub=raw[raw.event_ts.dt.year==year]
        counts={k:int((sub.series_id==k).sum()) for k in [FOMC]+[x for v in PAIRS.values() for x in v]}
        if counts[FOMC]!=8 or any(counts[s]!=12 for pair in PAIRS.values() for s in pair):
            raise RuntimeError('2021_2022_MACRO_SOURCE_GAP_'+str(year)+'_'+str(counts))
        summary[str(year)]={kind:{'complete':12} for kind in PAIRS}
        f=sub[sub.series_id==FOMC]
        dates=sorted(f.event_ts.dt.date.astype(str).tolist())
        if dates!=FED_HOURS[year]:
            raise RuntimeError('FED_2021_22_SCHEDULE_NOT_MATCHED_'+str(year)+'_'+str(dates))
        if not all(t.tz_convert('America/New_York').hour==14 for t in f.event_ts):
            raise RuntimeError('FED_STATEMENT_WRONG_TIME')
        for typ,(act,cons) in PAIRS.items():
            a=sub[sub.series_id==act].copy();c=sub[sub.series_id==cons].copy()
            x=a.merge(c,on='event_ts',how='outer',validate='one_to_one',
                     suffixes=('_act','_cons'),indicator=True)
            if len(x)!=12 or not (x._merge=='both').all():
                raise RuntimeError('MACRO_PAIRS_NOT_SAME_RELEASE')
            for r in x.itertuples(index=False):
                if pd.isna(r.value_act) or pd.isna(r.value_cons):
                    raise RuntimeError('SOURCE_HAS_NULL_NUMERIC_MACRO')
                ready=max(r.available_at_act,r.available_at_cons)
                if ready < r.event_ts or ready > r.event_ts+pd.Timedelta(hours=1):
                    raise RuntimeError('MACRO_REPORTED_READINESS_BAD')
                rows.append({'event_type':typ,'event_ts_utc':r.event_ts,'actual':float(r.value_act),
                     'consensus':float(r.value_cons),'surprise':float(r.value_act-r.value_cons),
                     'actual_available_as_of_utc':r.available_at_act,
                     'consensus_available_as_of_utc':r.available_at_cons,
                     'surprise_ready_at_utc':ready,'pair_complete':True,
                     'actual_lineage_id':r.lineage_act,'consensus_lineage_id':r.lineage_cons,
                     'pit_use':'LEGACY_RECONSTRUCTED_RELEASE_TIME_ASOF_NOT_ARCHIVED_PREFLIGHT_CONSENSUS'})
        for r in f.itertuples(index=False):
            rows.append({'event_type':'FOMC','event_ts_utc':r.event_ts,
               'actual':np.nan,'consensus':np.nan,'surprise':np.nan,
               'actual_available_as_of_utc':pd.NaT,'consensus_available_as_of_utc':pd.NaT,
               'surprise_ready_at_utc':pd.NaT,'pair_complete':False,
               'actual_lineage_id':'FED_2021_2022_PUBLIC_REGULAR_CALENDAR_'+str(r.lineage),
               'consensus_lineage_id':None,
               'pit_use':'OFFICIAL_SCHEDULED_STATEMENT_EVENT_TIME_ONLY_NO_SURPRISE'})
        summary[str(year)]['FOMC']={'scheduled_statement_events':8}
    return pd.DataFrame(rows),summary
def main():
    raw=conn_load(); earlier,qc=raw_calendar(raw)
    old=pd.read_csv(OR);new=pd.read_csv(G)
    both_old=pd.concat([earlier,old],ignore_index=True)
    both_new=pd.concat([earlier,new],ignore_index=True)
    for name,frame in [('base',both_old),('fixed',both_new)]:
        if frame.duplicated(['event_type','event_ts_utc']).any():
            raise RuntimeError('CONFLICT_OR_DUPLICATE_MACRO_'+name)
    # Private ephemeral job paths are deliberately not added to git.
    tmp=AX/'_PRIVATE_PRAMV_NEON_MACRO_RUNTIME'
    tmp.mkdir(exist_ok=True)
    paths={name:tmp/(name+'_2021_2025_source.csv') for name in ('base','fixed')}
    both_old.to_csv(paths['base'],index=False)
    both_new.to_csv(paths['fixed'],index=False)
    base.CAL=paths['fixed']
    base.OLDMACRO=paths['base']
    base.OUT=AX/(NAME+'_SUMMARY.json')
    base.MET=AX/(NAME+'_YEARLY_METRICS.csv')
    base.PRED=AX/(NAME+'_DATED_PREDICTIONS.csv')
    base.CHECK=AX/(NAME+'_FOMC_ABLATION.csv')
    def true_source():
        p,t=common.source_load()
        p=p[p.index>=pd.Timestamp('2021-01-01',tz='UTC')]
        return p,t
    base.mkt_q=true_source
    base.main()
    z=json.loads(base.OUT.read_text())
    z.update({
      'status':'PRAMV_ARCHITECTURE_ACTUALLY_REFIT_ON_2021_2025_FULLER_OLD_MACRO_SOURCE_RESTRICTED_PIT',
      'macro_train_since_2021':True,
      '2020_prices_available':True,
      '2020_model_training_excluded':'2020 observations have only 11 of 12 NFP/AHE/UNEMP release pairs and emergency unscheduled FOMC; do not silently set missing no-event',
      'source_window':'Same accepted 2020-2025 BID15m quote universe; macro-complete 2021-2024 training, 2023-24 expanding validation and frozen 2025',
      'historical_2021_2022_events':qc,
      'model_versions':'New full-history research rerun, not frozen 2026-10-07 champion. No 2025 model tuning.',
      'm4_train_history_from_2020_22':True,
      'm4_train_history_exact_years':[2021,2022,2023,2024],
      'original_PIT_consensus_limit':'Actual+consensus source ingested retrospectively 2026; claimed released_at=event_ts, pre-release archived consensus vintage not independently verified.',
      'privacy':'2021-22 legacy historical consensus numeric observations are only ephemeral job files and private Neon source; do not commit to public repo',
      'fed_regular_calendar_validation':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
      '2020_2022_source_inventory':'GOLD_EXECUTION_PRAMV_PRE2023_MACRO_SOURCE_AVAILABILITY_AUDIT_20261008.json'})
    base.OUT.write_text(json.dumps(z,indent=2)+'\n')
    info={'status':'2021_22_RESEARCH_EVENTS_MATCHED_NEON_AND_OFFICIAL_FED_CALENDAR',
      'm4_macro_pre2023_complete_sources':qc,
      'use_2020_macro_training':False,'2020_NFP_pair_missing':True,
      'fomc_schedule_event_verification_2021_22':True,
      'retrospective_consensus_warning':z['original_PIT_consensus_limit'],
      'private_NEON_values_not_published':True,
      'macro_release_ready_join':True,
      'future_2025_target_used_in_training':False,
      'new_summary':base.OUT.name,'generated_at':datetime.now(timezone.utc).isoformat()}
    AGG.write_text(json.dumps(info,indent=2)+'\n')
    print('EXPANDED_2021_2025_PRAMV_FINISHED',json.dumps(info,indent=2),flush=True)
if __name__=='__main__':main()
