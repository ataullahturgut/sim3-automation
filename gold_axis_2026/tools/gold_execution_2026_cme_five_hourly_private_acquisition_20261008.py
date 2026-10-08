"""Source-only pre-paid Databento five continuous CME futures H1, hard $2 cost cap.

Source timeframe 2023-01-01 inclusive to 2026-10-08 exclusive; direct native
DataBento GLBX.MDP3 ohlcv-1h, calendar continuous c.0 roots GC/SI/NQ/ZN/CL.
No 2026 outcomes or spot labels used for source/roll selection. Data in private
Neon only, not raw public Git files. Never perform a request above hard estimate.
"""
from pathlib import Path
import os,json,time,hashlib
import numpy as np,pandas as pd
import psycopg
AX=Path(__file__).resolve().parents[1]
OUTPUT=AX/"GOLD_EXECUTION_2026_CME_FIVE_H1_SOURCE_QC_20261008.json"
SYMBOLS=["GC.c.0","SI.c.0","NQ.c.0","ZN.c.0","CL.c.0"]
ROOTS=["GC","SI","NQ","ZN","CL"]
START="2023-01-01";END="2026-10-08"
MAX_USD=2.00
TABLE="gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c_v1"
SOURCE="DATABENTO_GLBX_MDP3_OHLCV_1H_CALENDAR_CONTINUOUS_C_SOURCE_V1"
def main():
    tic=time.time()
    report={"asof":"2026-10-08","status":"BLOCKED_NOT_ACQUIRED",
      "purpose":"Source-only 5 independent CME H1 2023 to Oct7 2026, no model scores",
      "dataset":"GLBX.MDP3","schema":"ohlcv-1h","symbols":SYMBOLS,
      "source_start":START,"source_end_exclusive":END,
      "cost_budget_USD":MAX_USD,
      "billing_only_if_quoted_under_budget":True,
      "raw_licensed_market_data_public":False,
      "spot_execution_model_fit":False,
      "private_table":TABLE,
      "before_decision_feature_clock":"H1 bar starts ts_event; bar must finish plus 15 min before issue"}
    try:
      key=os.environ.get("DATABENTO_API_KEY","")
      if not key:raise RuntimeError("DATABENTO_EXISTING_API_SECRET_NOT_FOUND")
      if not os.environ.get("NEON_DATABASE_URL"):
          raise RuntimeError("PRIVATE_NEON_SOURCE_ARCHIVE_URL_NOT_FOUND")
      import databento as db
      client=db.Historical(key)
      req={"dataset":"GLBX.MDP3","schema":"ohlcv-1h",
           "symbols":SYMBOLS,"stype_in":"continuous",
           "start":START,"end":END}
      cost=float(client.metadata.get_cost(**req))
      report["new_pre_request_cost_estimate_USD"]=round(cost,6)
      if not(0<=cost<=MAX_USD):
          raise RuntimeError("HARD_SPENDING_CAP_EXCEEDED_NO_DATA_REQUEST")
      store=client.timeseries.get_range(**req)
      z=store.to_df().reset_index()
      if "index" in z.columns and "ts_event" not in z.columns:
          z=z.rename(columns={"index":"ts_event"})
      mandatory=["ts_event","symbol","instrument_id","open","high","low","close","volume"]
      missing=set(mandatory)-set(z.columns)
      if missing:raise RuntimeError("VENDOR_OHLCV_SCHEMA_UNEXPECTED:"+str(sorted(missing)))
      z=z[mandatory].copy()
      z.ts_event=pd.to_datetime(z.ts_event,utc=True,errors="raise")
      for col in ["open","high","low","close","volume"]:
          z[col]=pd.to_numeric(z[col],errors="raise")
      z.instrument_id=pd.to_numeric(z.instrument_id,errors="raise").astype(int)
      if set(z.symbol)!=set(SYMBOLS):
          raise RuntimeError("MISSING_TARGET_CME_ROOTS:"+str(sorted(set(SYMBOLS)-set(z.symbol))))
      if z.duplicated(["symbol","ts_event"]).any():
          raise RuntimeError("SOURCE_TIMESTAMPS_DUPLICATE")
      if ((z.open<=0)|(z.high<=0)|(z.low<=0)|(z.close<=0)|(z.volume<0)).any():
          raise RuntimeError("CME_INVALID_NONPOSITIVE_PRICE_OR_VOLUME")
      if ((z.high+1e-10<z[["open","close","low"]].max(axis=1))|
              (z.low-1e-10>z[["open","close","high"]].min(axis=1))).any():
          raise RuntimeError("CME_OHLC_GEOMETRY_INVALID")
      start=pd.Timestamp(START,tz="UTC");end=pd.Timestamp(END,tz="UTC")
      if not (z.ts_event.ge(start)&z.ts_event.lt(end)).all():
          raise RuntimeError("CME_HISTORY_OUTSIDE_PURCHASED_WINDOW")
      z["year"]=z.ts_event.dt.year
      if any(len(z[(z.symbol==symbol)&(z.year==y)])<1000
             for symbol in SYMBOLS for y in (2023,2024,2025,2026)):
          raise RuntimeError("CME_4YEAR_SOURCE_COVERAGE_INCOMPLETE")
      z=z.sort_values(["symbol","ts_event"])
      with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=30) as conn:
          with conn.cursor() as c:
              c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE}(
              source_id TEXT NOT NULL, symbol TEXT NOT NULL,
              ts_event TIMESTAMPTZ NOT NULL, instrument_id BIGINT NOT NULL,
              open DOUBLE PRECISION NOT NULL,high DOUBLE PRECISION NOT NULL,
              low DOUBLE PRECISION NOT NULL,close DOUBLE PRECISION NOT NULL,
              volume DOUBLE PRECISION NOT NULL,PRIMARY KEY(source_id,symbol,ts_event))""")
              c.execute("""CREATE TEMP TABLE stage(
                source_id TEXT,symbol TEXT,ts_event TIMESTAMPTZ,instrument_id BIGINT,
                open DOUBLE PRECISION,high DOUBLE PRECISION,low DOUBLE PRECISION,
                close DOUBLE PRECISION,volume DOUBLE PRECISION) ON COMMIT DROP""")
              with c.copy("COPY stage (source_id,symbol,ts_event,instrument_id,open,high,low,close,volume) FROM STDIN") as writer:
                  for row in z.itertuples(index=False):
                      writer.write_row((SOURCE,row.symbol,row.ts_event.to_pydatetime(),
                         int(row.instrument_id),float(row.open),float(row.high),float(row.low),
                         float(row.close),float(row.volume)))
              c.execute(f"""INSERT INTO {TABLE}
                 SELECT * FROM stage ON CONFLICT(source_id,symbol,ts_event) DO NOTHING""")
              inserted=int(c.rowcount)
          conn.commit()
      report["status"]="DATABENTO_NATIVE_H1_SOURCE_ACQUIRED_PRIVATE_QC_PASS"
      report["rows_received"]=len(z)
      report["new_private_rows_inserted"]=inserted
      report["symbol_year_coverage"]=[
        {"symbol":str(sym),"year":int(y),"rows":len(g),
         "first_UTC":g.ts_event.min().isoformat(),"last_UTC":g.ts_event.max().isoformat(),
         "instrument_roll_ids":int(g.instrument_id.nunique())}
         for (sym,y),g in z.groupby(["symbol","year"])]
      report["model_2026_accuracy_measured"]=False
      report["license_raw_quotes_not_committed"]=True
    except Exception as err:
      import traceback
      fr=traceback.extract_tb(err.__traceback__)[-1]
      report["status"]="DATABENTO_SOURCE_COST_OR_SCHEMA_GATE_BLOCKED"
      report["block_type"]=type(err).__name__
      report["block_reason"]=str(err)[:130]
      report["failed_step"]=fr.name
      report["failure_line"]=fr.lineno
      report["no_model_results_claimed"]=True
    report["duration_seconds"]=int(time.time()-tic)
    OUTPUT.write_text(json.dumps(report,indent=2,default=str)+"\n")
    print("FIVE_INDEPENDENT_ASSET_CME_SOURCE_QC",json.dumps(report,default=str),flush=True)
if __name__=="__main__":main()
