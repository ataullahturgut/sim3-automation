"""Fixed-calendar vendor concordance probe: Twelve Data historical XAU 15m vs HistData M15.
Eight one-week samples by quarter, independent of observed gold returns; private DB only.
"""
from __future__ import annotations
import hashlib,json,os,time
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
import requests
import gold_execution_twelve_xau15m_free_gaps_20261008 as core

OUT=Path(__file__).resolve().parents[1]/'GOLD_EXECUTION_XAU15M_HISTDATA_TWELVE_CONCORDANCE_20261008.json'
WEEKS=[('2020-01-06','2020-01-13'),('2020-04-06','2020-04-13'),
('2020-07-06','2020-07-13'),('2020-10-05','2020-10-12'),
('2021-01-04','2021-01-11'),('2021-04-05','2021-04-12'),
('2021-07-05','2021-07-12'),('2021-10-04','2021-10-11')]

def main():
    report={'source_1':'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1',
        'source_2':core.SOURCE,
        'sample_design':'First full calendar week of Jan/Apr/Jul/Oct for each year, fixed prior to reading returns',
        'windows':[],'asof':'2026-10-08','paid_download':False,
        'raw_prices_public':False,'status':'BLOCKED'}
    try:
        key=os.environ.get('TWELVE_DATA_API_KEY','').strip()
        if not key:raise RuntimeError('API_SECRET_MISSING')
        qframes=[]
        s=requests.Session()
        for start,end in WEEKS:
            vals=core.request_month(s,start,end,key)
            q=core.parse(vals,start,end,pd.Timestamp(datetime.now(timezone.utc)))
            if len(q)<150:raise ValueError('INCOMPLETE_WEEK_'+start)
            report['windows'].append({'start':start,'end_exclusive':end,
                'vendor_rows':len(vals),'filtered_rows':len(q),
                'first_utc':q.bar_start_utc.min().isoformat(),
                'last_utc':q.bar_start_utc.max().isoformat()})
            qframes.append(q)
            time.sleep(9)
        q=pd.concat(qframes,ignore_index=True)
        if q.bar_start_utc.duplicated().any():raise ValueError('DUPLICATE_ACROSS_WEEKS')
        report['twelve_rows']=len(q)
        report['twelve_candidate_hash']=hashlib.sha256(q.to_csv(index=False).encode()).hexdigest()
        report['private_storage_and_match']=core.save_private(q)
        if report['private_storage_and_match']['histdata_same_utc_overlap_rows']<1000:
            raise RuntimeError('INSUFFICIENT_MATCHED_SAMPLE')
        report['status']='WEEKLY_SAMPLES_SAVED_AND_COMPARED'
    except Exception as e:
        report['error_type']=type(e).__name__;report['error_summary']=str(e)[:110]
    report['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps(report,indent=2,default=str))
    return 0 if report['status']=='WEEKLY_SAMPLES_SAVED_AND_COMPARED' else 1
if __name__=='__main__':raise SystemExit(main())
