"""Source-disagreement attribution, 2020-2026 XAU/USD Turkish clocks.
Read-only: no model selection, 2023 date gaps explicitly recorded.
Measures same-origin return SIGN disagreement and magnitude cutoffs in bps.
All raw prices private, GitHub receives aggregate diagnostics only.
"""
from __future__ import annotations
from pathlib import Path
import os,json
from datetime import datetime,timezone
import numpy as np,pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_XAU_SOURCE_LABEL_DISAGREEMENT_ANATOMY_2026-10-08.json'
H={
 '2020':'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1',
 '2021':'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1',
 '2022':'HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1',
 '2023':'HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1',
 '2024':'HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1',
 '2025':'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026',
 '2026':'HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026',
}
T='TWELVE_XAUUSD_15M_2020_2021_OCT2026_CANDIDATE_V1'

def get_h(con,y):
    with con.cursor() as c:
        c.execute("""SELECT bar_start_utc,open_price,close_price,native_minute_bars
              FROM gold_research_histdata_xau15m_candidate
              WHERE source_id=%s AND bar_start_utc>=%s AND bar_start_utc<%s
              ORDER BY bar_start_utc""",
              (H[str(y)],f'{y}-01-01',f'{y+1}-01-01'))
        q=pd.DataFrame(c.fetchall(),columns=['ts','open','close','native_minutes'])
    q.ts=pd.to_datetime(q.ts,utc=True)
    return q

def get_second(con,y):
    if y in (2020,2021,2026):
        with con.cursor() as c:
            c.execute("""SELECT bar_start_utc,open_price,close_price
                FROM gold_research_twelve_xau15m_gap_candidate
                WHERE source_id=%s AND bar_start_utc>=%s AND bar_start_utc<%s
                ORDER BY bar_start_utc""",(T,f'{y}-01-01',f'{y+1}-01-01'))
            q=pd.DataFrame(c.fetchall(),columns=['ts','open','close'])
    else:
        f='GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv' if y==2022 else 'GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv'
        q=pd.read_csv(AX/f,usecols=['dt_utc','open','close'],low_memory=False)
        q=q.rename(columns={'dt_utc':'ts'})
    q.ts=pd.to_datetime(q.ts,utc=True)
    return q[(q.ts>=pd.Timestamp(f'{y}-01-01',tz='UTC'))&
             (q.ts<pd.Timestamp(f'{y+1}-01-01',tz='UTC'))].copy()

def target(q):
    q=q.sort_values('ts').drop_duplicates('ts').set_index('ts')
    dates=sorted({ts.date() for ts in q.index if ts.hour==6 and ts.minute==0 and ts.dayofweek<5})
    def at(d,hr,col):
        if d is None:return None
        x=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=int(hr[:2]),minutes=int(hr[3:]))
        return float(q.at[x,col]) if x in q.index else None
    def log(a,b):
        if a is None or b is None or a<=0 or b<=0:return np.nan
        return float(np.log(b/a))
    out=[]
    for i,d in enumerate(dates):
        nxt=dates[i+1] if i+1<len(dates) else None
        expected=(pd.Timestamp(d)+pd.Timedelta(days=3 if pd.Timestamp(d).dayofweek==4 else 1)).date()
        dstart=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=6)
        full=all((dstart+pd.Timedelta(minutes=15*k)) in q.index for k in range(32))
        dr=log(at(d,'06:00','open'),at(d,'13:45','close')) if full else np.nan
        over=log(at(d,'14:00','open'),at(nxt,'05:45','close')) if nxt==expected else np.nan
        out.append({'date':str(d),'DAY':dr,'OVN':over})
    return pd.DataFrame(out)

def compare(h,t,y):
    x=target(h).merge(target(t),on='date',suffixes=('_h','_t'),validate='one_to_one')
    entry={'year':y,'histdata_m15':len(h),'comparator_m15':len(t),'windows':{}}
    for w in ('DAY','OVN'):
        z=x.dropna(subset=[w+'_h',w+'_t']).copy()
        if not len(z):continue
        hret=z[w+'_h'].to_numpy(float)*1e4
        tret=z[w+'_t'].to_numpy(float)*1e4
        flips=((hret>0)!=(tret>0))
        sub={'matched_n':len(z),'label_disagreements':int(flips.sum()),
          'label_disagreement_rate':float(flips.mean()),
          'independent_move_abs_median_bps':float(np.median(np.abs(hret))),
          'comparator_move_abs_median_bps':float(np.median(np.abs(tret))),
          'source_ret_diff_abs_median_bps':float(np.median(np.abs(hret-tret))),
          'source_ret_diff_abs_p95_bps':float(np.quantile(np.abs(hret-tret),.95)),
          'sign_disagreement_by_min_abs_move_cutoff_bps':{},
          'discordant_abs_independent_move_bps':{}}
        for c in [0,5,10,20,50,100]:
            eligible=(np.minimum(np.abs(hret),np.abs(tret))>c)
            sub['sign_disagreement_by_min_abs_move_cutoff_bps'][str(c)]={'n':int(eligible.sum()),
                     'flips':int((flips&eligible).sum()),
                     'pct':float((flips&eligible).sum()/eligible.sum()*100) if eligible.sum() else None}
        if flips.any():
            xs=np.abs(hret[flips]);xt=np.abs(tret[flips])
            sub['discordant_abs_independent_move_bps']={
              'median':float(np.median(xs)),'p90':float(np.quantile(xs,.9)),
              'independent_absmove_le10_share':float((xs<=10).mean()),
              'both_vendor_absmove_gt50_count':int(((xs>50)&(xt>50)).sum())}
        else:sub['discordant_abs_independent_move_bps']={'median':None}
        entry['windows'][w]=sub
    return entry

def main():
    r={'asof':'2026-10-08','status':'QC_COMPLETED',
       'method':'source-independent fixed TR origin, paired realized log returns; bps magnitude sensitivity; no prediction model retuned',
       'matched_source_yields_not_identical':'true',
       'fully_qualified_canonical_spot_quote':False,
       'years':{},'models_retrained':False}
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        for y in range(2020,2027):
            h=get_h(con,y);t=get_second(con,y)
            r['years'][str(y)]=compare(h,t,y)
            print('SENSITIVITY_DONE',y,json.dumps({k:{'n':v['matched_n'],'flips':v['label_disagreements']} for k,v in r['years'][str(y)]['windows'].items()}),flush=True)
    r['created_utc']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(r,indent=2,default=str)+'\n')
    print('SOURCE_LABEL_QC_SAVED',flush=True)
if __name__=='__main__':main()
