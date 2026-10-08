from __future__ import annotations
import csv, io, json, hashlib, requests
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd

AX=Path(__file__).resolve().parents[1]
URL="https://www.federalreserve.gov/datadownload/Output.aspx?filetype=csv&from=&label=include&lastobs=&layout=seriescolumn&rel=H15&series=0b98a66d3ff5e1ea0fbf88adc59b387f&to=&type=package"
COL="RIFLGFCY10_XII_N.B"
OUT=AX/"GOLD_EXECUTION_DFII10_FREE_CANDIDATE_2020_20261007.csv"
REPORT=AX/"GOLD_EXECUTION_DFII10_FED_H15_BACKFILL_2026-10-08.json"

def main():
    result={"source":"FEDERAL_RESERVE_H15_REAL_10Y_DAILY","series":COL,"request_url":URL,
            "asof":"2026-10-08","origin_use":"D_MINUS_1","paid_download":False}
    try:
        r=requests.get(URL,timeout=(15,75),headers={"User-Agent":"Gold-Backfill-Research/1.0"})
        r.raise_for_status()
        lines=list(csv.reader(io.StringIO(r.content.decode("utf-8-sig"))))
        header=next(i for i,row in enumerate(lines) if row and row[0].strip()=="Time Period")
        head=[x.strip() for x in lines[header]]
        if COL not in head:raise ValueError("H15_REAL10_COLUMN_ABSENT")
        i=head.index(COL)
        vals=[]
        for row in lines[header+1:]:
            if len(row)<=i:continue
            try:vals.append((pd.Timestamp(row[0]),float(row[i])))
            except (ValueError,TypeError):pass
        q=pd.DataFrame(vals,columns=["date","value"]).drop_duplicates("date")
        q=q[(q.date>="2020-01-01") & (q.date<="2026-10-08")].sort_values("date")
        years={str(int(y)):int(len(g)) for y,g in q.groupby(q.date.dt.year)}
        if set(years)!=set(map(str,range(2020,2027))):raise ValueError("MISSING_YEAR")
        if min(years.values())<180:raise ValueError("YEAR_UNDER_180_DAYS")
        if q.date.duplicated().any():raise ValueError("DUPLICATE_DATE")
        q.to_csv(OUT,index=False,date_format="%Y-%m-%d",float_format="%.10g")
        result.update(status="OFFICIAL_FREE_COMPLETE",rows=len(q),annual=years,
                      first=str(q.date.min().date()),last=str(q.date.max().date()),
                      raw_sha256=hashlib.sha256(r.content).hexdigest(),
                      csv_sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),
                      filename=OUT.name)
    except Exception as e:
        result.update(status="SOURCE_FAILED",error_type=type(e).__name__)
    result["retrieved_at_utc"]=datetime.now(timezone.utc).isoformat()
    REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
