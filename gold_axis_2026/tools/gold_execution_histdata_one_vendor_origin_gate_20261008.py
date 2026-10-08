"""One-vendor origin-safe clock/quality candidate, 2020-2026 as-of 2026-10-08.

Source: HistData M1 fixed EST, normalized to UTC then 15m. The three
private HistData source IDs hold 2020-21, 2022-24, 2025-Sep2026.
NO Twelve/legacy quotes ever spliced into price or target series.
Only full 15-minute native-minute pivotal bars and full daytime paths are
eligible. Overnight consecutive weekday or Fri->Mon. No automatic holiday
substitution. Unstable move <=10bp is flagged, raw y remains.
No trading/PIT/PRAMV conclusions from this archive.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib
import numpy as np,pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_HISTDATA_ONE_VENDOR_GOVERNED_CANDIDATE_2026-10-08.json'
SOURCES={
 'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1':(2020,2021),
 'HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1':(2022,2024),
 'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026':(2025,2026)
}
COLS=['bar_start_utc','open_price','high_price','low_price','close_price','native_minute_bars','source_id']
LAYER='gold_research_xau_execution_origin_quality_candidate_v1'
def load(con):
    parts=[]
    for source,(start,end) in SOURCES.items():
        q=pd.read_sql_query("""SELECT bar_start_utc,open_price,high_price,low_price,close_price,
                      native_minute_bars,source_id
                  FROM gold_research_histdata_xau15m_candidate
                  WHERE source_id=%s AND bar_start_utc >= %s AND bar_start_utc < %s
                  ORDER BY bar_start_utc""",con,params=(
                    source,f'{start}-01-01',
                    f'{end+1}-01-01' if end<2026 else '2026-10-02'),
                  parse_dates=['bar_start_utc'])
        if q.empty:raise RuntimeError('MISSING_UPSTREAM_SOURCE_'+source)
        q.bar_start_utc=pd.to_datetime(q.bar_start_utc,utc=True)
        if q.bar_start_utc.duplicated().any():raise RuntimeError('DUPLICATE_'+source)
        parts.append(q)
    allq=pd.concat(parts,ignore_index=True).sort_values('bar_start_utc')
    if allq.bar_start_utc.duplicated().any():raise RuntimeError('DUPLICATE_BETWEEN_VENDOR_VINTAGES')
    if (allq[['open_price','high_price','low_price','close_price']]<=0).any().any():
        raise RuntimeError('NONPOSITIVE')
    if (allq.high_price<allq[['open_price','close_price','low_price']].max(axis=1)).any():
        raise RuntimeError('HIGH_OHLC_INVALID')
    if (allq.low_price>allq[['open_price','close_price','high_price']].min(axis=1)).any():
        raise RuntimeError('LOW_OHLC_INVALID')
    if ((allq.bar_start_utc.dt.minute%15)!=0).any():raise RuntimeError('BAD_QUARTER_HOUR')
    dow=allq.bar_start_utc.dt.dayofweek
    closed=(dow==5)|((dow==6)&(allq.bar_start_utc.dt.hour<21))
    if closed.any():raise RuntimeError('CLOSED_MARKET_SATURDAY_SUNDAY_M15')
    if (allq.native_minute_bars>15).any():raise RuntimeError('NATIVE_MINUTE_OVERFLOW')
    return allq

def make_labels(q):
    # Turkey fixed UTC+03 throughout 2020-2026, provider bars UTC.
    t=q.set_index('bar_start_utc',drop=False).sort_index()
    ts=t.index
    all_day=sorted({k.date() for k in ts if k.hour==6 and k.minute==0 and k.dayofweek<5})
    day_rows=[]
    def fetch(day,HHMM):
        if day is None:return None
        stamp=pd.Timestamp(day,tz='UTC')+pd.Timedelta(hours=int(HHMM[:2]),
                                                       minutes=int(HHMM[3:]))
        return t.loc[stamp] if stamp in ts else None
    for i,d in enumerate(all_day):
        next_day=all_day[i+1] if i+1<len(all_day) else None
        next_cal=(pd.Timestamp(d)+pd.Timedelta(days=3 if pd.Timestamp(d).dayofweek==4 else 1)).date()
        nxt_regular=next_day==next_cal
        o9=fetch(d,'06:00');c1645=fetch(d,'13:45')
        o17=fetch(d,'14:00'); cnext=fetch(next_day,'05:45') if nxt_regular else None
        complete_day=True
        for k in range(32):
            tstamp=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=6,minutes=15*k)
            if tstamp not in ts or int(t.loc[tstamp,'native_minute_bars'])!=15:
                complete_day=False
                break
        mature_day=bool(complete_day and o9 is not None and c1645 is not None
              and int(o9.native_minute_bars)==15 and int(c1645.native_minute_bars)==15)
        mature_ovn=bool(nxt_regular and o17 is not None and cnext is not None
              and int(o17.native_minute_bars)==15 and int(cnext.native_minute_bars)==15)
        if mature_ovn and (pd.Timestamp(d).dayofweek<4):
            # Require good bar density between 17:00 and next 09:00
            start=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=14)
            end=pd.Timestamp(next_day,tz='UTC')+pd.Timedelta(hours=6)
            g=t[(ts>=start)&(ts<end)]
            # 64 target 15m slots, legitimate daily maintenance can remove some.
            mature_ovn=bool(len(g)>=55 and (g.native_minute_bars>=12).sum()>=54)
        def lr(a,b):
            if a is None or b is None:return None
            return float(np.log(float(b)/float(a)))
        day_ret=lr(o9.open_price,c1645.close_price) if mature_day else None
        ovn_ret=lr(o17.open_price,cnext.close_price) if mature_ovn else None
        dts=pd.Timestamp(d)
        tstatus='OK' if mature_day else 'MISSING_OR_THIN_09_17_PATH'
        ostatus='OK' if mature_ovn else ('NEXT_EXPECTED_TRADING_DAY_UNAVAILABLE' if not nxt_regular
                 else 'MISSING_OR_THIN_17_TO_NEXT09')
        flags=[]
        if day_ret is not None and abs(day_ret)<=.001:flags.append('DAY_MAGNITUDE_LE_10BPS')
        if ovn_ret is not None and abs(ovn_ret)<=.001:flags.append('OVN_MAGNITUDE_LE_10BPS')
        if int(dts.dayofweek)==4:flags.append('FRIDAY_TO_MONDAY_WEEKEND_HOLD')
        rows=dict(
          issue_date=d,year=d.year,next_trading_date=next_day,
          source_provider='HISTDATA',calendar_version='TR_UTCPLUS3_2020_2026',
          data_vintage='RETRIEVED_2026-10-08_HISTORICAL_NOT_PIT',
          day_gate=tstatus,overnight_gate=ostatus,
          day_return=day_ret,overnight_return=ovn_ret,
          day_y=(int(day_ret>0) if day_ret is not None else None),
          overnight_y=(int(ovn_ret>0) if ovn_ret is not None else None),
          day_low_margin_10bp=(abs(day_ret)<=.001 if day_ret is not None else None),
          overnight_low_margin_10bp=(abs(ovn_ret)<=.001 if ovn_ret is not None else None),
          ambiguity_flags=','.join(flags))
        day_rows.append(rows)
    return pd.DataFrame(day_rows)

def persist(con, d):
    with con.cursor() as c:
        c.execute(f"""CREATE TABLE IF NOT EXISTS {LAYER}(
           issue_date DATE PRIMARY KEY,
           year INTEGER NOT NULL,
           next_trading_date DATE,
           source_provider TEXT NOT NULL,
           calendar_version TEXT NOT NULL,
           data_vintage TEXT NOT NULL,
           day_gate TEXT NOT NULL,
           overnight_gate TEXT NOT NULL,
           day_return DOUBLE PRECISION,
           overnight_return DOUBLE PRECISION,
           day_y SMALLINT,
           overnight_y SMALLINT,
           day_low_margin_10bp BOOLEAN,
           overnight_low_margin_10bp BOOLEAN,
           ambiguity_flags TEXT NOT NULL,
           retrieved_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        c.execute("""CREATE TEMP TABLE stage (
           issue_date DATE,year INTEGER,next_trading_date DATE,source_provider TEXT,
           calendar_version TEXT,data_vintage TEXT,day_gate TEXT,overnight_gate TEXT,
           day_return DOUBLE PRECISION,overnight_return DOUBLE PRECISION,
           day_y SMALLINT,overnight_y SMALLINT,day_low_margin_10bp BOOLEAN,
           overnight_low_margin_10bp BOOLEAN,ambiguity_flags TEXT) ON COMMIT DROP""")
        fields=list(d.columns)
        with c.copy("COPY stage("+','.join(fields)+") FROM STDIN") as cp:
            for item in d.itertuples(index=False):
                vals=list(item)
                if pd.isna(vals[2]):vals[2]=None
                cp.write_row(tuple(vals))
        c.execute(f"""INSERT INTO {LAYER} ({','.join(fields)})
              SELECT {','.join(fields)} FROM stage ON CONFLICT(issue_date) DO NOTHING""")
        inserted=int(c.rowcount)
        c.execute(f'SELECT COUNT(*),COUNT(*) FILTER (WHERE day_y IS NOT NULL), COUNT(*) FILTER (WHERE overnight_y IS NOT NULL) FROM {LAYER}')
        persisted=c.fetchone()
    con.commit()
    return {'inserted_new_candidate_target_origins':inserted,
       'private_total_rows':int(persisted[0]),'private_day_mature':int(persisted[1]),
       'private_ovn_mature':int(persisted[2])}

def main():
    rep={'asof':'2026-10-08','status':'INCOMPLETE',
     'physical_quote_provider':'HistData M1 normalized fixed EST->UTC M15, original source quote from single supplier',
     'historical_vintage_PIT':'NO, historical downloaded in Oct 2026',
     'price_source_policy':'single vendor within all price anchors and target; no Twelve and legacy splicing',
     'target_gate_contract':'DAY 32 fully populated native 15M candles each with 15 source minutes, OVN two full native anchors plus 55/64 overnight bar density for next weekday, Fri->Mon allowed separately flagged',
     'low_margin_threshold':'10 basis points DIAGNOSTIC FLAG ONLY, original up/down sign never replaced',
     'result_role':'ONE_VENDOR_QUALITY_GATED_RESEARCH_CANDIDATE_NOT_EXECUTABLE_BANK_TRUTH',
     'public_raw_price':False}
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=30) as con:
        q=load(con)
        df=make_labels(q)
        years={}
        for y in range(2020,2027):
            z=df[df.year==y]
            bars=q[q.bar_start_utc.dt.year==y]
            if len(z)==0:continue
            m=z.day_y.notna();n=z.overnight_y.notna()
            years[str(y)]={'observed_15m_bars':int(len(bars)),
              'incomplete_native_15m_bars':int((bars.native_minute_bars!=15).sum()),
              'observed_weekday_09_00_dates':int(len(z)),
              'day_mature_n':int(m.sum()),'day_quarantined_n':int((~m).sum()),
              'overnight_mature_n':int(n.sum()),'overnight_quarantined_n':int((~n).sum()),
              'day_low_margin_10bps_n':int((z.day_low_margin_10bp==True).sum()),
              'overnight_low_margin_10bps_n':int((z.overnight_low_margin_10bp==True).sum()),
              'day_anchor_sample_eligible_first':str(z.loc[m,'issue_date'].min()) if m.any() else None,
              'ovn_anchor_sample_eligible_last':str(z.loc[n,'issue_date'].max()) if n.any() else None,
              'month_15m_bar_counts':{str(int(k)):int(v) for k,v in
                   bars.groupby(bars.bar_start_utc.dt.month).size().items()}}
        rep['yearly']=years
        rep['2023_ref_coverage_warning']=len(q[q.bar_start_utc.dt.year==2023])<22000
        # Self-contained deterministic label identity hash, not raw prices.
        rep['candidate_target_series_sha256']=hashlib.sha256(
            df.sort_values('issue_date')[['issue_date','day_gate','overnight_gate','day_return','overnight_return']].
            to_csv(index=False).encode('utf-8')).hexdigest()
        rep['private_storage']=persist(con,df)
    rep['status']='ONE_VENDOR_QC_CANDIDATE_SAVED_NOT_CANONICAL'
    rep['calendars_not_proven']='Holiday/exchange venue hours and actual bank spread not supplied'
    rep['models_retrained']=False
    rep['completed_at_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(rep,indent=2,default=str,ensure_ascii=False)+'\n')
    print(json.dumps(rep,indent=2,default=str,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
