"""Private XAU 2020-21 09/17 Istanbul target anchor and per-session slot QC.
Never infer missing pivots, never publish licensed historical prices.
"""
from __future__ import annotations
import json,os
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pandas as pd
import psycopg

OUT=Path(__file__).resolve().parents[1]/'GOLD_EXECUTION_HISTDATA_2020_2021_DAY_OVN_ANCHOR_QC_20261008.json'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1'

def main():
    url=os.environ.get('NEON_DATABASE_URL','')
    if not url:raise RuntimeError('NEON_SECRET_REQUIRED')
    with psycopg.connect(url,connect_timeout=20) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT bar_start_utc,native_minute_bars
                  FROM gold_research_histdata_xau15m_candidate
                  WHERE source_id=%s ORDER BY bar_start_utc""",(SOURCE,))
            rows=cur.fetchall()
    if len(rows)<45000:raise RuntimeError('SOURCE_M15_NOT_COMPLETE')
    index=pd.DatetimeIndex([r[0] for r in rows]).tz_convert('Europe/Istanbul')
    stamps={x for x in index}
    minute_map={ts:int(row[1]) for ts,row in zip(index,rows)}
    records=[]
    for year in (2020,2021):
        days=pd.date_range(f'{year}-01-01',f'{year}-12-31',freq='B',
                           tz='Europe/Istanbul')
        expected=0;day_complete=0;day_anchor=0;overnight_ready=0;thin=0
        missing_day_anchors=[];missing_day_interior=[];thin_pivot_dates=[]
        for day in days:
            expected+=1
            start=day+pd.Timedelta(hours=9)
            end=day+pd.Timedelta(hours=16,minutes=45)
            origin_17=day+pd.Timedelta(hours=17)
            slots=pd.date_range(start,end,freq='15min')
            anchor_ok=start in stamps and end in stamps and origin_17 in stamps
            isfull=all(s in stamps for s in slots)
            anchors_native_complete=anchor_ok and all(minute_map.get(s,0)==15
                                  for s in (start,end,origin_17))
            day_anchor+=int(anchor_ok)
            day_complete+=int(isfull and anchors_native_complete)
            if not anchor_ok:missing_day_anchors.append(str(day.date()))
            elif not isfull:missing_day_interior.append(str(day.date()))
            if anchor_ok and not anchors_native_complete:
                thin+=1
                thin_pivot_dates.append(str(day.date()))
            next_weekday=day+pd.offsets.BDay(1)
            night_end=next_weekday+pd.Timedelta(hours=8,minutes=45)
            overnight_ready+=int(origin_17 in stamps and night_end in stamps
                                and minute_map.get(origin_17,0)==15
                                and minute_map.get(night_end,0)==15)
        records.append({'year':year,'weekdays_not_trading_calendar_adjusted':expected,
                  'day_09_1645_and_17_anchors_present':day_anchor,
                  'day_full_32_bars_and_3_anchors_complete':day_complete,
                  'overnight_17_to_next_BDay_0845_anchors_ready':overnight_ready,
                  'days_with_thin_pivot_native_minutes':thin,
                  'thin_pivot_dates':thin_pivot_dates,
                  'missing_day_anchors_first30':missing_day_anchors[:30],
                  'missing_interior_first30':missing_day_interior[:30]})
    result={'source_id':SOURCE,'records_15m':len(rows),
        'source_timezone':'EST_FIXED_UTC_MINUS_05_NORMALIZED_TO_UTC',
        'target_clocks':'Europe/Istanbul 09 open; 16:45 close; 17 open; next weekday 08:45 close',
        'calendar_note':'Naive Monday-Friday counts are NOT exchange-calendar-filtered, holidays may be legitimate; no labels issued.',
        'years':records,'model_labels_issued':False,'source_promotion':False,
        'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
