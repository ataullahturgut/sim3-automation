from pathlib import Path
import os,json,time,requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_2023_TWELVE_FUTURES_BRIDGE_PROBE_2026-10-05.json"
OUTM=AX/"GOLD_H3_2023_TWELVE_FUTURES_BRIDGE_PROBE_2026-10-05.md"

KEY=os.environ.get("TWELVE_DATA_API_KEY","").strip()
if not KEY:
    raise RuntimeError("TWELVE_DATA_API_KEY missing")
S=requests.Session();S.headers.update({"User-Agent":"gold-h3-research/1.0"})

queries=[
 ("GC","gold futures"),("GOLD","gold futures"),("SI","silver futures"),("SILVER","silver futures"),
 ("NQ","nasdaq futures"),("NASDAQ","nasdaq futures"),("ZN","10y treasury futures"),
 ("10Y","10y treasury futures"),("CL","crude futures"),("CRUDE","crude futures")
]

def get(path,params):
    p=dict(params);p["apikey"]=KEY
    r=S.get("https://api.twelvedata.com/"+path,params=p,timeout=45)
    try:j=r.json()
    except Exception:j={"raw":r.text[:1000]}
    return r.status_code,j

res={"searches":[],"candidate_tests":[]}
seen={}
for q,label in queries:
    status,j=get("symbol_search",{"symbol":q,"outputsize":50})
    rows=j.get("data",[]) if isinstance(j,dict) else []
    compact=[]
    for x in rows:
        y={k:x.get(k) for k in ["symbol","instrument_name","exchange","mic_code","exchange_timezone","instrument_type","type","country","currency"] if k in x}
        compact.append(y)
        text=(" ".join(str(v) for v in y.values())).lower()
        if any(w in text for w in ["future","cme","comex","nymex","cbot"]) and y.get("symbol"):
            seen[(y.get("symbol"),y.get("exchange"))]=y
    res["searches"].append({"query":q,"label":label,"http":status,"rows":len(rows),"top":compact[:25]})
    time.sleep(.15)

# Historical-depth test for every distinct futures-like search candidate, capped for credit safety.
for (_,ex),x in list(seen.items())[:20]:
    sym=x["symbol"]
    params={"symbol":sym,"interval":"1h","start_date":"2025-07-01","end_date":"2025-07-07","timezone":"UTC","outputsize":5000}
    if ex: params["exchange"]=ex
    st,j=get("time_series",params)
    meta=j.get("meta",{}) if isinstance(j,dict) else {}
    vals=j.get("values",[]) if isinstance(j,dict) else []
    test={"symbol":sym,"exchange":ex,"http":st,"status":j.get("status") if isinstance(j,dict) else None,
          "message":j.get("message") if isinstance(j,dict) else None,"meta":meta,"n_2025":len(vals)}
    if vals:
        p2={"symbol":sym,"interval":"1h","start_date":"2023-06-01","end_date":"2023-06-07","timezone":"UTC","outputsize":5000}
        if ex:p2["exchange"]=ex
        st2,j2=get("time_series",p2)
        vals2=j2.get("values",[]) if isinstance(j2,dict) else []
        test.update({"http_2023":st2,"status_2023":j2.get("status") if isinstance(j2,dict) else None,
                     "message_2023":j2.get("message") if isinstance(j2,dict) else None,
                     "n_2023":len(vals2),
                     "first_2023":vals2[-1].get("datetime") if vals2 else None,
                     "last_2023":vals2[0].get("datetime") if vals2 else None})
    res["candidate_tests"].append(test)
    time.sleep(.2)

OUTJ.write_text(json.dumps(res,indent=2,default=str)+"\n")
lines=["# GOLD H3 — Twelve Data Futures Bridge Probe","",
       "Purpose: determine whether the already-connected Twelve Data source can provide 1h historical futures needed to bridge the missing 2023 IFBC/LLRS state.","",
       "## Futures-like candidates","",
       "| Symbol | Exchange | 2025 1h rows | 2023 1h rows | Message |",
       "|---|---|---:|---:|---|"]
if res["candidate_tests"]:
    for x in res["candidate_tests"]:
        msg=str(x.get("message_2023") or x.get("message") or "").replace("|","/")
        lines.append(f"| {x.get('symbol')} | {x.get('exchange')} | {x.get('n_2025',0)} | {x.get('n_2023',0)} | {msg} |")
else:
    lines.append("| _none discovered_ | | | | |")
lines+=["","## Search inventory",""]
for s in res["searches"]:
    lines.append(f"- {s['query']}: HTTP {s['http']}, rows {s['rows']}")
OUTM.write_text("\n".join(lines)+"\n")
print(OUTM.read_text())
