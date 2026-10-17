#!/usr/bin/env python3
"""Read-only, ephemeral export. Never upload M15 prices or personal data to git."""
import json,os,sys
from datetime import datetime,timedelta,timezone
import psycopg
from psycopg.rows import dict_row
UTC=timezone.utc
SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1"
def fmt(t): return t.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00","Z")
def main(directory):
    os.makedirs(directory,exist_ok=True)
    url=os.environ.get("NEON_DATABASE_URL")
    if not url: raise RuntimeError("NEON_DATABASE_URL_SECRET_MISSING")
    bars_path=os.path.join(directory,"PRIVATE_EV_XAU_M15.json")
    sessions_path=os.path.join(directory,"PRIVATE_EV_SLOW.json")
    n=0;days={}
    with psycopg.connect(url,autocommit=False,row_factory=dict_row) as conn:
      with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
      with conn.cursor(name="conditional_evduka_read_only",row_factory=dict_row) as cur:
        cur.itersize=3000
        cur.execute("""SELECT source_id,bar_start_utc,bid_close,ask_close
                  FROM gold_research_evduka_xau15m_bidask_candidate
                  WHERE source_id=%s
                    AND bar_start_utc>='2020-01-01T00:00:00Z'
                    AND bar_start_utc<'2026-01-01T00:00:00Z'
                  ORDER BY bar_start_utc""",(SOURCE,))
        with open(bars_path,"w",encoding="utf8") as f:
          f.write("[")
          for r in cur:
            t=r["bar_start_utc"]
            bid=float(r["bid_close"]);ask=float(r["ask_close"])
            if bid<=0 or ask<bid:raise ValueError("BAD_OR_INVERTED_QUOTE")
            v={"source_id":r["source_id"],"bar_start_utc":fmt(t),
               "bid_close":bid,"ask_close":ask}
            f.write(("," if n else "")+json.dumps(v,separators=(",",":")));n+=1
            # 22:00 UTC fixed daily roll, label is t+2h's UTC date.
            d=(t+timedelta(hours=2)).date()
            if d.weekday()>=5:continue
            a=days.setdefault(d,{"first":t,"last":t,"n":0,"max_gap":0,
                                 "last_price":0.0,"prev":None})
            if a["prev"] is not None:
              lag=(t-a["prev"]).total_seconds()/60
              a["max_gap"]=max(a["max_gap"],lag)
            a["prev"]=t;a["last"]=t;a["n"]+=1
            a["last_price"]=(bid+ask)/2
          f.write("]")
      conn.rollback()
    slow=[]
    for d,a in sorted(days.items()):
      # Pass ALL sessions to the S2 quality gate; never reconstruct missing bars.
      end=datetime(d.year,d.month,d.day,22,0,tzinfo=UTC)
      terminal=a["last"]+timedelta(minutes=15)
      slow.append({"session":str(d),"source_id":SOURCE,
       "first_bar":fmt(a["first"]),"last_bar":fmt(a["last"]),
       "n":a["n"],"valid_quotes":a["n"],
       "terminal_bar_valid":terminal<=end,
       "max_gap_minutes":a["max_gap"],
       "close_price":a["last_price"],"availableAt":fmt(end),
       "sessionEvidence":"BIDASK_M15_RECONSTRUCTED_NOT_M1"})
    with open(sessions_path,"w",encoding="utf8") as f:
      json.dump(slow,f,separators=(",",":"))
    print(json.dumps({"source_id":SOURCE,"bars":n,"sessions":len(slow),
      "years":sorted(set(str(d)[:4] for d in days)),
      "privacy":"EPHEMERAL_ONLY_NO_PUBLIC_RAW_DATA"},sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python export... DIR")
    main(sys.argv[1])
