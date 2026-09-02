from __future__ import annotations

import json
import os
import time
import requests

URL = "https://api.twelvedata.com/time_series"
SYMS = ["XAU/USD", "XAG/USD", "XPT/USD", "XPD/USD"]


def key():
    v=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not v: raise RuntimeError("TWELVE_DATA_API_KEY_NOT_SET")
    return v


def call(params):
    r=requests.get(URL,params=params,headers={"Authorization":f"apikey {key()}","User-Agent":"Gold-Control-Patch-V3-Access-Probe/1.0"},timeout=(20,120))
    try: p=r.json()
    except Exception: p={}
    return r.status_code,p


def summarize(symbol,status,p):
    if isinstance(p,dict) and p.get("status")=="error":
        return {"symbol":symbol,"http":status,"ok":False,"provider_code":p.get("code"),"provider_status":p.get("status"),"message_class":str(p.get("message","")).split(".")[0][:120]}
    vals=p.get("values") if isinstance(p,dict) else None
    meta=p.get("meta") if isinstance(p,dict) else None
    return {"symbol":symbol,"http":status,"ok":bool(vals),"n_returned":0 if not vals else len(vals),"interval":None if not isinstance(meta,dict) else meta.get("interval"),"type":None if not isinstance(meta,dict) else meta.get("type")}


def main():
    out=[]
    # Tiny recent probes first: establishes entitlement/symbol semantics without logging values.
    for s in SYMS:
        status,p=call({"symbol":s,"interval":"1day","start_date":"2026-08-20","end_date":"2026-08-31","outputsize":20,"order":"ASC","format":"JSON"})
        out.append({"phase":"recent","result":summarize(s,status,p)})
        time.sleep(10)
    # Depth probes request only one oldest row by ascending bounded history; no values are logged.
    for s in SYMS:
        status,p=call({"symbol":s,"interval":"1day","start_date":"2010-01-01","end_date":"2011-03-01","outputsize":500,"order":"ASC","format":"JSON"})
        z=summarize(s,status,p)
        vals=p.get("values") if isinstance(p,dict) else None
        if vals:
            z["first_datetime"] = str(vals[0].get("datetime"))
            z["last_datetime"] = str(vals[-1].get("datetime"))
        out.append({"phase":"early_depth","result":z})
        time.sleep(10)
    print(json.dumps(out,sort_keys=True))
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")

if __name__=="__main__": main()
