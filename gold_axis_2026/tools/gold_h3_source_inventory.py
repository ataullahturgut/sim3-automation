from __future__ import annotations
import json, os
import pandas as pd
import psycopg

dsn=os.environ["NEON_DATABASE_URL"]
with psycopg.connect(dsn, autocommit=False) as conn:
    with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute("""
            SELECT series_id, COUNT(*) AS n, MIN(observation_ts), MAX(observation_ts)
            FROM observations
            GROUP BY series_id
            HAVING COUNT(*) >= 500
            ORDER BY COUNT(*) DESC, series_id
        """)
        rows=cur.fetchall()
    conn.rollback()

out=[]
for sid,n,first,last in rows:
    out.append({"series_id":str(sid),"n":int(n),"first":str(first),"last":str(last)})
print("HOURLY_SOURCE_INVENTORY="+json.dumps(out))
