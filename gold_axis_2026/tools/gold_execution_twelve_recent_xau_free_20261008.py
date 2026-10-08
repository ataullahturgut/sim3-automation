from __future__ import annotations
import json,os,sys
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
import requests
import gold_execution_twelve_xau15m_free_gaps_20261008 as core

OUT=Path(__file__).resolve().parents[1]/'GOLD_EXECUTION_TWELVE_RECENT_XAU15M_GAP_20261008.json'
def main():
    now=datetime.now(timezone.utc)
    report={'asof':now.isoformat(),'source':core.SOURCE,
            'requested_range':['2026-09-28','2026-10-09'],
            'previous_15m_archive_last':'2026-09-27T23:45:00+00:00',
            'vendor_raw_public':False,'paid_download':False,
            'status':'NOT_ACQUIRED'}
    try:
        key=os.environ.get('TWELVE_DATA_API_KEY','').strip()
        if not key:raise RuntimeError('TWELVE_SECRET_MISSING')
        vals=core.request_month(requests.Session(),'2026-09-28','2026-10-09',key)
        q=core.parse(vals,'2026-09-28','2026-10-09',pd.Timestamp(now))
        report.update(vendor_returned_rows=len(vals),valid_completed_bars=len(q),
                      first_utc=q.bar_start_utc.min().isoformat(),
                      last_utc=q.bar_start_utc.max().isoformat())
        if len(q)<300:raise RuntimeError('RECENT_VENDOR_RESPONSE_INCOMPLETE')
        report['private_storage']=core.save_private(q)
        report['status']='RECENT_GAP_CANDIDATE_SAVED'
    except Exception as e:
        report.update(status='NOT_ACQUIRED',error_type=type(e).__name__,
                      error_summary=str(e)[:100])
    OUT.write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps(report,indent=2,default=str))
    return 0 if report['status']=='RECENT_GAP_CANDIDATE_SAVED' else 1
if __name__=='__main__':raise SystemExit(main())
