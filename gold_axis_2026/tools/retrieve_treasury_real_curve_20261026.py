"""Official US Treasury daily *real* yield curve 2023-2026, only downloadable source validation."""
import csv,datetime as dt,hashlib,io,json,os,re,requests
from pathlib import Path
ROOT=Path("/tmp/gold_treasury_real_20261026");ROOT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Research US Treasury official public XML/CSV source)"})
state={}
for year in range(2023,2027):
    base=f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all"
    query=f"?type=daily_treasury_real_yield_curve&field_tdr_date_value={year}&page&_format=csv"
    url=base+query
    try:
      resp=S.get(url,timeout=(18,45))
      resp.raise_for_status()
      data=resp.content
      if len(data)<4000 or b"<html" in data[:200].lower():raise ValueError("not CSV response")
      (ROOT/f"treasury_real_{year}_original.csv").write_bytes(data)
      parsed=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
      if not parsed:raise ValueError("empty Treasury CSV")
      fields=list(parsed[0])
      datekey=next((x for x in fields if x.lower()=="date"),None)
      realkey=next((x for x in fields if x.lower().strip() in ("10 yr","10-year","10-year real yield")) ,None)
      if not datekey or not realkey:raise ValueError("headers do not contain Date and 10 YR: "+repr(fields))
      values=[]
      for r in parsed:
        dateval=r.get(datekey,"")
        val=r.get(realkey,"").strip()
        if not val or val=="N/A":continue
        day=dt.datetime.strptime(dateval,"%m/%d/%Y").date()
        if day.year!=year:raise ValueError("unexpected date year "+str(day))
        values.append((day.isoformat(),float(val)))
      if len(values)<(175 if year==2026 else 215):raise ValueError(f"insufficient 10yr {year}: {len(values)}")
      state[year]={"status":"OFFICIAL_SOURCE_VALIDATED_RESEARCH_ONLY",
            "url":url,"sha256":hashlib.sha256(data).hexdigest(),"rows":len(parsed),
            "valid_10y_real":len(values),"first":values[0],"last":values[-1],
            "pit_certified":False,"distinction":"US Treasury Par 10y Real CMT not identical to FRED DFII10 vintage"}
    except Exception as e:state[year]={"status":"BLOCKED","url":url,"error":str(e)[:350]}
    print("TREASURY",year,json.dumps(state[year]),flush=True)
(ROOT/"treasury_real_audit.json").write_text(json.dumps(state,indent=2))
