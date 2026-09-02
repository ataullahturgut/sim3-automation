from __future__ import annotations

import json
import requests

BASE="https://data.nasdaq.com/api/v3/datasets"
CODES={
 "Gold":"CHRIS/CME_GC1",
 "Silver":"CHRIS/CME_SI1",
 "Platinum":"CHRIS/CME_PL1",
 "Palladium":"CHRIS/CME_PA1",
}


def req(code,start,end,limit=5):
    url=f"{BASE}/{code}.json"
    try:
        r=requests.get(url,params={"start_date":start,"end_date":end,"limit":limit,"order":"asc"},headers={"User-Agent":"Gold-Control-Patch-V4-Source-Probe/1.0"},timeout=(20,120))
        try:p=r.json()
        except Exception:p={}
        if r.status_code!=200 or not isinstance(p,dict) or "dataset" not in p:
            err=p.get("quandl_error",{}) if isinstance(p,dict) else {}
            return {"http":r.status_code,"ok":False,"error_code":err.get("code"),"error_message_class":str(err.get("message","")).split(".")[0][:160]}
        ds=p["dataset"]
        data=ds.get("data") or []
        return {
          "http":r.status_code,"ok":bool(data),"dataset_code":ds.get("dataset_code"),"database_code":ds.get("database_code"),
          "name":ds.get("name"),"frequency":ds.get("frequency"),"type":ds.get("type"),
          "oldest_available_date":ds.get("oldest_available_date"),"newest_available_date":ds.get("newest_available_date"),
          "column_names":ds.get("column_names"),"n_returned":len(data),
          "first_date":None if not data else data[0][0],"last_date":None if not data else data[-1][0],
        }
    except Exception as exc:
        return {"ok":False,"error_code":type(exc).__name__}


def main():
    out={}
    for name,code in CODES.items():
        out[name]={
          "code":code,
          "recent":req(code,"2026-08-20","2026-08-31",20),
          "early":req(code,"2010-01-01","2011-03-01",500),
        }
    print(json.dumps(out,sort_keys=True))
    print("RAW_MARKET_VALUES_LOGGED=NO")
    print("API_KEY_USED=NO")
    print("DATABASE_WRITES=NONE")

if __name__=="__main__":main()
