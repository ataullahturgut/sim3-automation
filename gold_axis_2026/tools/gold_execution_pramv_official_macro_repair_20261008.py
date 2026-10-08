"""Official-event calendar repair for frozen PRAMV research rerun.

Do not back-fill unrealized or canceled releases with zeros. FOMC 2025
published schedule (2024-08-09 Fed press release), actual statement at
14:00 America/New_York. 2025 BLS dates INCLUDE late and canceled releases
under US government lapse. Dec 18 CPI November two-month cumulative
measurement is not month-on-month comparable: NO invented CPI MoM surprise.
Retain historical actual/consensus pair provenance and present vintage caveat.
No legacy file/table overwritten. No forecast fitted in this script.
"""
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime,timezone
import json,hashlib,pandas as pd,numpy as np
AX=Path(__file__).resolve().parents[1]
SOURCE=AX/'GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv'
CAL=AX/'GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv'
QC=AX/'GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_QC_20261008.json'
FED='https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm'
BLS='https://www.bls.gov/schedule/2025/'
LAPSE='https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm'
CPI='https://www.bls.gov/news.release/archives/cpi_12182025.htm'
# Official 2025 FOMC regular meeting statement second days, no July/November
# fabricated move or December projection substituted for scheduled statement.
FOMC_2025=['2025-01-29','2025-03-19','2025-05-07','2025-06-18',
           '2025-07-30','2025-09-17','2025-10-29','2025-12-10']
# 2025 BLS published release dates, NOT reference month.
NFP_2025=['2025-01-10','2025-02-07','2025-03-07','2025-04-04',
          '2025-05-02','2025-06-06','2025-07-03','2025-08-01',
          '2025-09-05','2025-11-20','2025-12-16']
CPI_2025=['2025-01-15','2025-02-12','2025-03-12','2025-04-10',
          '2025-05-13','2025-06-11','2025-07-15','2025-08-12',
          '2025-09-11','2025-10-24','2025-12-18']
NFP_CANCEL=['2025-11-07']
CPI_CANCEL=['2025-11-13']
def et(d,hour,minute=0):
    x=pd.Timestamp(d).tz_localize('America/New_York')+pd.Timedelta(hours=hour,minutes=minute)
    return x.tz_convert('UTC')
def utc(d):return pd.to_datetime(d,utc=True)
def main():
    old=pd.read_csv(SOURCE)
    for key in ('event_ts_utc','surprise_ready_at_utc',
                'actual_available_as_of_utc','consensus_available_as_of_utc'):
        old[key]=pd.to_datetime(old[key],utc=True,errors='coerce')
    before={k:set(old[(old.event_type==k)&(old.event_ts_utc.dt.year==2025)].event_ts_utc.dt.date.astype(str))
            for k in ('NFP','CPI','FOMC')}
    oN=set(NFP_2025);oC=set(CPI_2025)
    # A released but measurement-incompatible CPI cannot become a numerical
    # surprise in the frozen CPI MoM model; record event and block that origin.
    missing_n=sorted(oN-before['NFP'])
    missing_c=sorted(oC-before['CPI'])
    if missing_n:raise RuntimeError('NFP_2025_RELEVANT_SOURCE_MISSING '+str(missing_n))
    if missing_c!=['2025-12-18']:raise RuntimeError('CPI_UNEXPECTED_2025_GAP '+str(missing_c))
    if before['FOMC']:raise RuntimeError('UNEXPECTED_2025_FOMC_ALREADY_EXISTS')
    if set(NFP_CANCEL)&before['NFP'] or set(CPI_CANCEL)&before['CPI']:
        raise RuntimeError('CANCELED_MACRO_TREATED_AS_PUBLISHED')
    additions=[]
    for d in FOMC_2025:
        x=et(d,14)
        additions.append({'event_type':'FOMC','event_ts_utc':x,
            'actual':np.nan,'consensus':np.nan,'surprise':np.nan,
            'actual_available_as_of_utc':pd.NaT,
            'consensus_available_as_of_utc':pd.NaT,'surprise_ready_at_utc':pd.NaT,
            'pair_complete':False,'actual_lineage_id':'OFFICIAL_FED_SCHEDULE_RELEASE_2024_08_09',
            'consensus_lineage_id':None,
            'pit_use':'OFFICIAL_ADVANCE_SCHEDULE_ONLY_NO_POSTEVENT_SURPRISE'})
    bad=et('2025-12-18',8,30)
    additions.append({'event_type':'CPI','event_ts_utc':bad,
            'actual':np.nan,'consensus':np.nan,'surprise':np.nan,
            'actual_available_as_of_utc':bad,
            'consensus_available_as_of_utc':pd.NaT,
            'surprise_ready_at_utc':pd.NaT,
            'pair_complete':False,
            'actual_lineage_id':'BLS_2025_12_18_TWO_MONTH_CUMULATIVE_NOT_MOM',
            'consensus_lineage_id':None,
            'pit_use':'PUBLISHED_UNPAIRED_CPI_TWO_MONTH_CUMULATIVE_NOT_COMPARABLE'})
    m=pd.concat([old,pd.DataFrame(additions)],ignore_index=True)
    m=m.sort_values(['event_ts_utc','event_type']).reset_index(drop=True)
    if m.duplicated(['event_type','event_ts_utc']).any():
        raise RuntimeError('DUPLICATE_EVENT')
    checks={}
    for y in (2023,2024,2025):
        g=m[m.event_ts_utc.dt.year==y]
        checks[str(y)]={k:int((g.event_type==k).sum()) for k in ('FOMC','NFP','AHE','UNEMP','CPI')}
    assert checks['2025']['FOMC']==8
    assert checks['2025']['NFP']==11 and checks['2025']['CPI']==11
    # No future inflation surprise at 17:00 on 2025-12-18.
    z=m[(m.event_ts_utc.dt.date.astype(str)=='2025-12-18')&(m.event_type=='CPI')]
    assert len(z)==1 and z.surprise_ready_at_utc.isna().all()
    # Check scheduled times fit NY daylight saving in actual year.
    assert et('2025-01-29',14).hour==19 and et('2025-09-17',14).hour==18
    # 'Available_as_of' CPI/NFP is an asserted date from data supplied in 2026:
    # NOT independent confirmation of 2025 frozen consensus-vintage integrity.
    m.to_csv(CAL,index=False)
    report={'status':'OFFICIAL_2025_EVENT_CALENDAR_REPAIRED_WITH_RESTRICTED_SURPRISE_VINTAGE',
        'source_urls':{'FOMC_schedule_published_2024':FED,
                       'BLS_original_2025_release_list':BLS,
                       'BLS_shutdown_and_cancellations':LAPSE,
                       'BLS_2025_12_18_two_month_CPI':CPI},
        'year_event_counts':checks,'2025_fomc_inserted':len(FOMC_2025),
        '2025_cpi_calendar_new_unpaired_not_mom':1,
        '2025_fomc_dates':FOMC_2025,'cpi_missing_pair_date':['2025-12-18'],
        'nfp_canceled_no_event':NFP_CANCEL,'cpi_canceled_no_event':CPI_CANCEL,
        'fomc_research_pit':'Published in Fed 2024 Aug schedule; decision 14 ET is after 17 TRT so upcoming flag known at 17',
        'consensus_pit_caution':'Legacy 2023-25 CPI/NFP/AHE/UNEMP consensus reconstructed/loaded 2026 with reported available_as_of at release; not independently verifiable at pre-release origin; restricted retrospective model only.',
        'unpaired_release_pit':'EXCLUDE 2025-12-18 from exact M4/PRAMV retest; no synthetic MoM or no-event',
        'canceled_releases_never_fabricated':True,
        'source_file':CAL.name,
        'calendar_sha256':hashlib.sha256(CAL.read_bytes()).hexdigest(),
        'legacy_file_unchanged':True,'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    QC.write_text(json.dumps(report,indent=2)+'\n')
    print('MACRO_OFFICIAL_QC',json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
