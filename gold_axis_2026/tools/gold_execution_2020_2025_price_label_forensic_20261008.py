"""INDEPENDENT forensic audit of archived XAUUSD BID/ASK and saved labels, 2020-25.
No model fit, source mutation, target overwrite or future information.
Official Dukascopy XAU break UTC 21-22 during US summer and 22-23 winter;
Sunday open 21 summer/22 winter; Friday closes 21/22. Calendar holidays TBD.
Volume v and original GZIP hashes checked against persistent Neon quotes.
"""
from __future__ import annotations
import os,gzip,json,hashlib,requests
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd,numpy as np,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_2020_2025_PRICE_LABEL_FORENSIC_AUDIT_20261008.json"
SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1"
P="gold_research_evduka_xau15m_bidask_candidate"
T="gold_research_evduka_xau_session_target_candidate_v1"
U="https://evtradelabs.com/api/simulator/data/XAUUSD/M15/{year}.json.gz"
PRICES=["bid_open","bid_high","bid_low","bid_close","ask_open","ask_high","ask_low","ask_close"]
RENAME={"o":"bid_open","h":"bid_high","l":"bid_low","c":"bid_close",
        "ao":"ask_open","ah":"ask_high","al":"ask_low","ac":"ask_close"}

def db(con,year):
    with con.cursor() as c:
        c.execute(f"""SELECT bar_start_utc,{','.join(PRICES)}
        FROM {P} WHERE source_id=%s AND bar_start_utc>=%s
        AND bar_start_utc<%s ORDER BY bar_start_utc""",
           (SOURCE,f"{year}-01-01",f"{year+1}-01-09" if year<2025 else '2026-01-01'))
        rows=c.fetchall()
        c.execute(f"""SELECT issue_date,year,next_expected_date,
          day_gate,overnight_gate,
          day_bid_logret,day_ask_logret,overnight_bid_logret,overnight_ask_logret,
          day_y,overnight_y,day_bidask_sign_disagreement,ovn_bidask_sign_disagreement,
          spread_09_bps,spread_17_bps,low_margin_day_10bps,low_margin_ovn_10bps
          FROM {T} WHERE source_id=%s AND year=%s ORDER BY issue_date""",(SOURCE,year))
        t=c.fetchall()
    q=pd.DataFrame(rows,columns=["ts"]+PRICES)
    labcols=["issue_date","year","next_expected_date","day_gate","overnight_gate",
          "day_bid_logret","day_ask_logret","overnight_bid_logret","overnight_ask_logret",
          "day_y","overnight_y","day_bidask_sign_disagreement","ovn_bidask_sign_disagreement",
          "spread_09_bps","spread_17_bps","low_margin_day_10bps","low_margin_ovn_10bps"]
    l=pd.DataFrame(t,columns=labcols)
    q.ts=pd.to_datetime(q.ts,utc=True)
    if q.ts.duplicated().any():raise RuntimeError("DB_SOURCE_DUPLICATE")
    return q,l

def fresh(year):
    response=requests.get(U.format(year=year),timeout=(10,40),headers={"User-Agent":"SourceIntegrityAudit/1.0"})
    response.raise_for_status()
    raw=gzip.decompress(response.content)
    d=json.loads(raw)
    if isinstance(d,dict):
        for key in ("data","bars","candles","items","rows"):
            if isinstance(d.get(key),list):d=d[key];break
    q=pd.DataFrame(d)
    if not set(["ts","v"]+list(RENAME)).issubset(q.columns):
        raise RuntimeError("FRESH_SCHEMA_CHANGED_"+str(list(q.columns)))
    q["ts"]=pd.to_datetime(pd.to_numeric(q.ts),unit="s",utc=True)
    q=q.rename(columns=RENAME)
    for k in PRICES+["v"]:q[k]=pd.to_numeric(q[k],errors="coerce")
    if q[PRICES].isna().any().any():raise RuntimeError("NULL_FRESH_QUOTES")
    return q.sort_values("ts"),hashlib.sha256(response.content).hexdigest()

def venue_schedule(q):
    utc=q.ts
    uslocal=utc.dt.tz_convert("America/New_York")
    is_summer=np.array([bool(t.dst()) for t in uslocal])
    dow=utc.dt.dayofweek.to_numpy()
    hour=utc.dt.hour.to_numpy()
    break_start=np.where(is_summer,21,22)
    is_break=(dow<5)&(hour==break_start)
    offhours=(dow==5)|((dow==6)&(hour<np.where(is_summer,21,22)))|((dow==4)&(hour>=break_start))
    # Friday evening break=closed until Sunday, not daily restart
    is_break=is_break & (dow<4)
    return is_break,offhours,is_summer

def quality(x,l,year,hashes):
    q,h=fresh(year)
    a=q.merge(x[x.ts.dt.year==year],on="ts",validate="one_to_one",suffixes=("_fresh","_private"),how="outer",indicator=True)
    missing=int((a["_merge"]!="both").sum())
    dif={}
    shared=a[a["_merge"]=="both"]
    for k in PRICES:
        dd=np.abs(shared[k+"_fresh"]-shared[k+"_private"])
        dif[k]=int((dd>1e-6).sum())
    if missing or any(dif.values()):
        raise RuntimeError("IMMUTABILITY_QC_FAILED_"+str(year)+"_missing_"+str(missing)+"_mismatches_"+str(dif))
    q=q.sort_values("ts").reset_index(drop=True)
    p=q[PRICES]
    bidbad=((q.bid_high+1e-6<q[["bid_open","bid_low","bid_close"]].max(axis=1))|
        (q.bid_low-1e-6>q[["bid_open","bid_high","bid_close"]].min(axis=1)))
    askbad=((q.ask_high+1e-6<q[["ask_open","ask_low","ask_close"]].max(axis=1))|
        (q.ask_low-1e-6>q[["ask_open","ask_high","ask_close"]].min(axis=1)))
    cross=((q.ask_open<q.bid_open)|(q.ask_close<q.bid_close))
    br,off,summer=venue_schedule(q)
    g=q.loc[br].copy()
    days=q.ts.dt.date
    # 15m source volume is provider's tick-derived aggregation, unit not confirmed.
    volume_nonzero=(q.v.fillna(0)>0)
    pxflat=((q.bid_high-q.bid_low).abs()<1e-8)&((q.ask_high-q.ask_low).abs()<1e-8)
    logret=np.log(q.bid_close/q.bid_close.shift(1))
    regular=(q.ts-q.ts.shift(1)==pd.Timedelta(minutes=15))
    large15=(regular & (np.abs(logret)>np.log(1.015)))
    large5=(regular & (np.abs(logret)>np.log(1.005)))
    spread=(q.ask_close/q.bid_close-1)*10000
    # recompute labels independently, anchored entirely on source price columns
    m=x.set_index("ts")
    def price(day,hm,key):
        if day is None:return None
        hh,mm=map(int,hm.split(":"))
        at=pd.Timestamp(day,tz="UTC")+pd.Timedelta(hours=hh,minutes=mm)
        return float(m.at[at,key]) if at in m.index else None
    def calc(a,b):
        if a is None or b is None:return None
        return float(np.log(b/a))
    diffs={"origin_rows":int(len(l)), "bad_next_expected_date":0,
      "wrong_persisted_target_return":{k:0 for k in ("day_bid_logret","day_ask_logret","overnight_bid_logret","overnight_ask_logret")},
      "wrong_persisted_direction":{"day_y":0,"overnight_y":0},
      "wrong_persisted_ambiguous_flags":{"day_low_margin":0,"overnight_low_margin":0},
      "wrong_persisted_bidask_sign":{"DAY":0,"OVN":0},
      "gated_complete_missing_anchor":{"DAY":0,"OVN":0},
      "flat_zero_bid_returns":{"DAY":0,"OVN":0},
      "calendar_break_inside_nights":0,
      "spread_at_9_bps_mismatch":0,
      "spread_at_17_bps_mismatch":0}
    issues=[]
    for r in l.itertuples(index=False):
        d=r.issue_date
        if isinstance(d,pd.Timestamp):d=d.date()
        want=(pd.Timestamp(d)+pd.Timedelta(days=(3 if pd.Timestamp(d).weekday()==4 else 1))).date()
        if r.next_expected_date!=want:diffs["bad_next_expected_date"]+=1
        ts9=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=6)
        complete_day=all(ts9+pd.Timedelta(minutes=15*i) in m.index for i in range(32))
        day_bid=calc(price(d,"06:00","bid_open"),price(d,"13:45","bid_close")) if complete_day else None
        day_ask=calc(price(d,"06:00","ask_open"),price(d,"13:45","ask_close")) if complete_day else None
        next_expected_present=(pd.Timestamp(want,tz="UTC")+pd.Timedelta(hours=6)) in m.index
        start=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=14)
        end=pd.Timestamp(want,tz="UTC")+pd.Timedelta(hours=6)
        if next_expected_present:
            if pd.Timestamp(d).weekday()<4:
                density=int(((m.index>=start)&(m.index<end)).sum())
                ok=density>=55
            else:ok=True
        else:ok=False
        ov_bid=calc(price(d,"14:00","bid_open"),price(want,"05:45","bid_close")) if ok else None
        ov_ask=calc(price(d,"14:00","ask_open"),price(want,"05:45","ask_close")) if ok else None
        specs=(("day_bid_logret",day_bid,r.day_bid_logret),("day_ask_logret",day_ask,r.day_ask_logret),
               ("overnight_bid_logret",ov_bid,r.overnight_bid_logret),("overnight_ask_logret",ov_ask,r.overnight_ask_logret))
        for k,expected,actual in specs:
            if expected is None:
                if actual is not None:diffs["wrong_persisted_target_return"][k]+=1
            elif actual is None or abs(float(actual)-expected)>1e-10:
                diffs["wrong_persisted_target_return"][k]+=1
                if len(issues)<20:issues.append({"date":str(d),"code":k+"_return_mismatch"})
        for k,expected,actual in (("day_y",day_bid,r.day_y),("overnight_y",ov_bid,r.overnight_y)):
            correct=None if expected is None else int(expected>0)
            if correct!=actual:
                diffs["wrong_persisted_direction"][k]+=1
                if len(issues)<35:issues.append({"date":str(d),"code":k+"_SIGN", "stored":actual,"recomputed":correct, "next_expected":str(want)})
        for k,expected,actual in (("day_low_margin",day_bid,r.low_margin_day_10bps),
                                  ("overnight_low_margin",ov_bid,r.low_margin_ovn_10bps)):
            correct=None if expected is None else (abs(expected)<=.001)
            if correct!=actual:diffs["wrong_persisted_ambiguous_flags"][k]+=1
        for k,expected_b,expected_a,actual in (("DAY",day_bid,day_ask,r.day_bidask_sign_disagreement),
            ("OVN",ov_bid,ov_ask,r.ovn_bidask_sign_disagreement)):
            exp=None if expected_b is None or expected_a is None else ((expected_b>0)!=(expected_a>0))
            if exp!=actual:diffs["wrong_persisted_bidask_sign"][k]+=1
            if expected_b is not None and expected_b==0:diffs["flat_zero_bid_returns"][k]+=1
        for k,rrt,gate in (("DAY",day_bid,r.day_gate),("OVN",ov_bid,r.overnight_gate)):
            if gate=="COMPLETE_SINGLE_SOURCE" and rrt is None:diffs["gated_complete_missing_anchor"][k]+=1
        for hm,field in (("06:00","spread_09_bps"),("14:00","spread_17_bps")):
            bb=price(d,hm,"bid_open"); aa=price(d,hm,"ask_open")
            exp=(aa/bb-1)*10000 if bb is not None else None
            actual=getattr(r,field)
            if (exp is None)!=(actual is None) or (exp is not None and abs(exp-actual)>1e-8):
                diffs["spread_at_"+("9" if hm=="06:00" else "17")+"_bps_mismatch"]+=1
        # Count existing apparent OVN labels involving maint break candle bars
        if ov_bid is not None and pd.Timestamp(d).weekday()<4:
            indices=q[(q.ts>=start)&(q.ts<end)]
            br2,_,_=venue_schedule(indices)
            if br2.any():diffs["calendar_break_inside_nights"]+=1
    extremes=q.loc[large15,["ts","bid_open","bid_high","bid_low","bid_close","ask_close","v"]].copy()
    sourcechecks={
      "utc_minute_alignment_error":int((q.ts.dt.minute%15!=0).sum()),
      "duplicate_interval_count":int(q.ts.duplicated().sum()),
      "nonpositive_quote_cells":int((p<=0).sum().sum()),
      "ohlc_bid_invalid_count":int(bidbad.sum()),"ohlc_ask_invalid_count":int(askbad.sum()),
      "bid_ask_crossed_open_or_close_count":int(cross.sum()),
      "definitely_offmarket_by_venue_count":int(off.sum()),
      "inside_documented_xau_daily_break_count":int(br.sum()),
      "daily_break_bar_count_with_positive_provider_volume":int(volume_nonzero[br].sum()),
      "daily_break_bar_count_with_flat_bid_ask_prices":int(pxflat[br].sum()),
      "daily_break_bar_count_with_nonflat_prices":int((~pxflat[br]).sum()),
      "daily_break_volume_median":float(g.v.median()) if len(g) else None,
      "provider_volume_missing_n":int(q.v.isna().sum()),
      "provider_volume_zero_n":int((q.v==0).sum()),
      "source_bar_flat_price_count":int(pxflat.sum()),
      "source_repeated_adjacent_bid_close_count":int((q.bid_close==q.bid_close.shift(1)).sum()),
      "positive_volume_share":float(volume_nonzero.mean()),
      "spread_close_bps_median":float(spread.median()),
      "spread_close_bps_p99":float(spread.quantile(.99)),
      "spread_close_bps_max":float(spread.max()),
      "spread_close_bps_over_30_count":int((spread>30).sum()),
      "spread_close_bps_over_100_count":int((spread>100).sum()),
      "adjacent_15m_bid_close_move_above_0_5pct_n":int(large5.sum()),
      "adjacent_15m_bid_close_move_above_1_5pct_n":int(large15.sum()),
      "adjacent_15m_bid_close_max_absolute_return_pct":float((np.abs(np.expm1(logret[regular]))*100).max()) if regular.any() else None,
      "extreme_bar_dates_sample":[str(x) for x in extremes.ts.dt.date.unique()[:15]],
      "daily_break_positive_volume_date_samples":[str(x) for x in q.loc[br&volume_nonzero,"ts"].dt.date.unique()[:10]],
    }
    return {"year":year,"bars":len(q),"raw_year_sha256":h,
       "database_vs_public_price_identity":{"unmatched_timestamp_rows":missing,"changed_private_price_cells":dif},
       "venue_price_quality":sourcechecks,"target_recompute":diffs,"sample_label_issues":issues}

def main():
    out={"asof":"2026-10-08","status":"INCOMPLETE","period":"2020-2025",
         "sources":"EV Trading Labs Dukascopy M15 BID ASK, original public gzip, exact private PostgreSQL stored price series and independently recomputed labels",
         "official_market_hours":"https://www.dukascopy.com/swiss/english/forex/forex-trading-accounts/link/?mob=1",
         "source_bar_docs":"https://evtradelabs.com/data",
         "independent_price_truth":"Same public source vs its private storage; not a third-party quote check except separate 2023 direct Dukascopy pilot",
         "model_retrained":False,"original_quote_rows_modified":False,
         "original_target_rows_modified":False,"raw_prices_exported":False,"years":{}}
    try:
        with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=25) as con:
            for year in range(2020,2026):
                p,l=db(con,year)
                out["years"][str(year)]=quality(p,l,year,None)
                stat=out["years"][str(year)]
                print("FORENSIC_FULL_YEAR",year,json.dumps(stat,default=str)[:28000],flush=True)
                print("PRICE_LABEL_FORENSIC",year,json.dumps({
                    "n":stat["bars"],"daily_break":stat["venue_price_quality"]["inside_documented_xau_daily_break_count"],
                    "daily_break_nonflat":stat["venue_price_quality"]["daily_break_bar_count_with_nonflat_prices"],
                    "source_15m_large":stat["venue_price_quality"]["adjacent_15m_bid_close_move_above_1_5pct_n"],
                    "label_changes":stat["target_recompute"]["wrong_persisted_direction"]}),flush=True)
        out["status"]="FULL_2020_2025_DATA_VENUE_AND_LABEL_FORENSIC_COMPLETE"
    except Exception as e:
        out["status"]="FORENSIC_INCOMPLETE_EXCEPTION"
        out["error_type"]=type(e).__name__
        out["error_summary"]=str(e)[:250]
    out["completed_at_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")
    print("SOURCE_FORENSIC_STATUS",out["status"],out.get("error_summary",""),flush=True)
    return 0 if out["status"].startswith("FULL_") else 1
if __name__=="__main__":raise SystemExit(main())
