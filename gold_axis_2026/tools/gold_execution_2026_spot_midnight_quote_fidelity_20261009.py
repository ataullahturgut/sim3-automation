"""Blind-to-target forensic of new 2026 every-minute midnight XAU M15 bars.
Assess if nominally complete BID OHLC candles at known US GC maintenance
timing have zero returns and repeated prices unlike historical unavailable bars.
This DOES NOT certify Dukascopy spot hours from CME futures rules.
"""
from pathlib import Path
import sys,json
import pandas as pd,numpy as np
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as src
NAME="GOLD_EXECUTION_2026_SPOT_M15_MIDNIGHT_SOURCE_FIDELITY_20261009"
def main():
    q,t,sources=src.source_sets();rows=[];nightst=[]
    for name,px,ts in sources:
        quote=pd.concat([q,px]).sort_index()
        events=pd.concat([t,ts],ignore_index=True)
        for r in events.itertuples(index=False):
            d=pd.Timestamp(r.date)
            if d.year<2023 or d.dayofweek>=4 or r.overnight_gate!="COMPLETE_SINGLE_SOURCE":continue
            start=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
            bars=quote.reindex(pd.date_range(start,periods=64,freq="15min"))
            close=bars.close.to_numpy(float);op=bars.open.to_numpy(float)
            labels=[x.tz_convert("Europe/Istanbul").strftime("%H:%M") for x in bars.index]
            frame=pd.DataFrame({"local_time":labels,"open":op,"close":close})
            frame["bp"]=10000*np.abs(np.log(frame.close/frame.open))
            frame["zero"]=frame.open.eq(frame.close)
            frame["stale_prev_close"]=frame.open.eq(frame.close.shift(1))&frame.zero
            frame["source"]=name;frame["year"]=d.year
            frame["date"]=d.strftime("%Y-%m-%d")
            subset=frame[frame.local_time.isin(
                ("00:00","00:15","00:30","00:45","01:00","01:15","01:30","01:45"))]
            slots=list(subset.local_time)
            summer=["00:00","00:15","00:30","00:45"]
            winter=["01:00","01:15","01:30","01:45"]
            v0=subset.set_index("local_time").reindex(summer)
            v1=subset.set_index("local_time").reindex(winter)
            nightst.append({"source":name,"year":int(d.year),
                "four_midnight_exact_prices":bool(v0.open.notna().all() and v0.close.notna().all()),
                "four_1am_exact_prices":bool(v1.open.notna().all() and v1.close.notna().all()),
                "four_midnight_all_zero":bool(v0.zero.all() and v0.open.notna().all()),
                "four_1am_all_zero":bool(v1.zero.all() and v1.open.notna().all()),
                "four_midnight_constant_close":bool(v0.close.notna().all() and v0.close.nunique()==1),
                "four_1am_constant_close":bool(v1.close.notna().all() and v1.close.nunique()==1)})
            rows.append(frame[frame.local_time.isin(summer+winter+[
                "19:00","19:15","19:30","19:45"])])
    f=pd.concat(rows,ignore_index=True)
    grouped=f.groupby(["source","year","local_time"]).agg(n_nonmissing=("bp","count"),
       zero_return_n=("zero","sum"),median_abs_bp=("bp","median"),
       p95_abs_bp=("bp",lambda x:float(x.quantile(.95))),
       stale_same_prev_n=("stale_prev_close","sum")).reset_index()
    grouped["zero_return_fraction"]=grouped.zero_return_n/grouped.n_nonmissing.replace(0,np.nan)
    grouped.to_csv(str(AX/NAME)+"_BAR_LEVEL_AGGREGATE.csv",index=False)
    k=pd.DataFrame(nightst).groupby(["source","year"]).agg(
      nights=("four_midnight_all_zero","size"),
      valid_00h=("four_midnight_exact_prices","sum"),
      valid_01h=("four_1am_exact_prices","sum"),
      all_zero_00h=("four_midnight_all_zero","sum"),
      all_zero_01h=("four_1am_all_zero","sum"),
      four_same_close_00h=("four_midnight_constant_close","sum"),
      four_same_close_01h=("four_1am_constant_close","sum")).reset_index()
    k.to_csv(str(AX/NAME)+"_NIGHT_AGGREGATE.csv",index=False)
    qc={"status":"2026_NATIVE_SPOT_MIDNIGHT_BID_BAR_SYNTHETIC_SOURCE_HYPOTHESIS_AUDIT_EXECUTED",
        "measure":"bar open=close and successive repeated prices, compare vendor/year around local 00 and 01",
        "not_market_close_proof":"CME GC futures are distinct venue from Dukascopy XAU spot; price staleness requires vendor quote provenance",
        "no_labels_and_no_2026_models_fitted":True}
    Path(str(AX/NAME)+"_SUMMARY.json").write_text(json.dumps(qc,indent=2)+"\n")
    print("MIDNIGHT_SPOT_NATIVE_ZERO_BAR_FORENSIC",k.to_string(index=False),flush=True)
    print("SLOT_SUMMARY",grouped.to_string(index=False),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        fr=traceback.extract_tb(e.__traceback__)[-1]
        qc={"status":"MIDNIGHT_QUOTE_BAR_SOURCE_FORENSIC_BLOCKED",
            "error":type(e).__name__,"reason":str(e)[:140],"line":fr.lineno}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(qc,indent=2)+"\n")
        print("MIDNIGHT_SOURCE_QC_BLOCK",json.dumps(qc),flush=True)
