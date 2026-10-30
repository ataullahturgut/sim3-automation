#!/usr/bin/env python3
"""Check official CFTC disaggregated futures-only public API (no credentials).
Only report availability and schema; never assert publication vintage retroactively.
"""
import hashlib,json
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ENDPOINT="https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
CODE={"088691":"GC","084691":"SI"}

def fetch():
    p={"$where":"cftc_contract_market_code in('088691','084691') AND report_date_as_yyyy_mm_dd >= '2026-09-01T00:00:00'",
       "$order":"report_date_as_yyyy_mm_dd DESC","$limit":"80"}
    url=ENDPOINT+"?"+urlencode(p)
    req=Request(url,headers={"User-Agent":"Gold-Control-Original-CFTC-COT-Probe/1.0","Accept":"application/json"})
    with urlopen(req,timeout=40) as h:
        data=h.read(1_000_000)
        if not data or len(data)>=1_000_000:raise ValueError("CFTC_OVERSIZE_OR_EMPTY")
    records=json.loads(data)
    if not isinstance(records,list):raise ValueError("CFTC_BAD_FORMAT")
    fields=sorted({k for x in records for k in x})
    required=("report_date_as_yyyy_mm_dd","cftc_contract_market_code","open_interest_all",
              "m_money_positions_long_all","m_money_positions_short_all")
    if any(k not in fields for k in required):raise ValueError("CFTC_ORIGINAL_FIELDS_MISSING")
    filtered={}
    for rec in records:
        code=rec["cftc_contract_market_code"]
        if code not in CODE:raise ValueError("WRONG_MARKET")
        d=rec["report_date_as_yyyy_mm_dd"][:10]
        key=(d,code)
        if key in filtered:raise ValueError("CFTC_DUPLICATE_MARKET_REPORT")
        filtered[key]=rec
    overview={}
    for code,name in CODE.items():
        dates=sorted(d for d,c in filtered if c==code)
        if not dates:raise ValueError("MISSING_MARKET_"+name)
        latest=filtered[(dates[-1],code)]
        oi=float(latest["open_interest_all"])
        l=float(latest["m_money_positions_long_all"])
        s=float(latest["m_money_positions_short_all"])
        overview[name]={"reportDate":dates[-1],"openInterest":oi,"managedMoneyLong":l,
                        "managedMoneyShort":s,"managedMoneyNetOverOi":(l-s)/oi,
                        "weeks":len(dates)}
    print(json.dumps({"status":"OFFICIAL_CFTC_API_ACCESS_OK","endpoint":ENDPOINT,
      "schemaFields":fields,"sha256":hashlib.sha256(data).hexdigest(),
      "latest":overview,"publicationTimeProven":False,
      "dataUsedInProduction":False},indent=2,ensure_ascii=False))

if __name__=="__main__":fetch()
