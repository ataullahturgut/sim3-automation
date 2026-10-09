"""Bounded, metadata-only Twelve Data FX hourly historical source-readiness probe.
Does not send quotes to LLM; does not expose key, market prices, or SQL rows.
Exactly 4 low-volume GET requests, no retries/paid upgrade or raw-file writes.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"GOLD_R4_TWELVE_INDEPENDENT_FX_H1_SOURCE_PROBE_20261009.json"
PROBES=(("EUR/USD","2023-06-05T12:00:00","2023-06-07T18:00:00"),
        ("USD/JPY","2023-06-05T12:00:00","2023-06-07T18:00:00"),
        ("EUR/USD","2025-06-02T12:00:00","2025-06-04T18:00:00"),
        ("USD/JPY","2025-06-02T12:00:00","2025-06-04T18:00:00"))
def main():
    key=os.getenv("TWELVE_DATA_API_KEY","").strip()
    receipt={"date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "purpose":"independent FX historical H1 time-zone, entitlement and no-future source gate",
      "status":"NOT_RUN","max_requests":4,"calls_attempted":0,
      "quotes_saved":False,"secret_saved_or_logged":False,"no_paid_plan_activation":True,
      "no_model_fit_or_accuracy_claim":True,"probes":[]}
    if not key:
        receipt["status"]="MISSING_TWELVE_DATA_API_SECRET"
        OUT.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
        print("FX_PROBE_SECRET_NOT_AVAILABLE",flush=True);return 1
    for symbol,start,end in PROBES:
        row={"pair":symbol,"interval":"1h","timezone":"UTC","start":start,"end":end}
        params={"symbol":symbol,"interval":"1h","timezone":"UTC",
             "start_date":start,"end_date":end,"format":"JSON","outputsize":80}
        req=urllib.request.Request(
         "https://api.twelvedata.com/time_series?"+urllib.parse.urlencode(params),
         headers={"Authorization":"apikey "+key,
                  "Accept":"application/json","User-Agent":"GoldControl-FXSourceAudit/1.0"})
        receipt["calls_attempted"]+=1
        try:
            with urllib.request.urlopen(req,timeout=30) as resp:
                obj=json.loads(resp.read(100000).decode("utf-8"))
                status=resp.status
            meta=obj.get("meta") or {}
            values=obj.get("values") or []
            # Only counts, dates and symbol/type; NEVER raw prices.
            dtstr=sorted([str(z.get("datetime","")) for z in values if isinstance(z,dict)])
            row.update(http_status=status,provider_code=obj.get("code"),
              result="PASS_SOURCE" if status==200 and obj.get("status")!="error" and len(dtstr)>=12 else "BLOCKED",
              provider_symbol=meta.get("symbol"),provider_type=meta.get("type"),
              provider_tz=meta.get("exchange_timezone") or meta.get("timezone"),
              n_returned=len(dtstr),earliest_timestamp=dtstr[0] if dtstr else None,
              latest_timestamp=dtstr[-1] if dtstr else None,
              n_valid_close_values=sum(1 for z in values if z.get("close") not in (None,"","0")),
              first_seen_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
              source_identity_verified=meta.get("symbol")==symbol)
        except urllib.error.HTTPError as exc:
            row.update(result="BLOCKED",http_status=exc.code,
                       error="PROVIDER_HTTP_"+str(exc.code))
        except (urllib.error.URLError,TimeoutError) as exc:
            row.update(result="BLOCKED",error="PROVIDER_TRANSPORT_"+type(exc).__name__)
        except Exception as exc:
            row.update(result="BLOCKED",error="PROVIDER_FORMAT_"+type(exc).__name__)
        receipt["probes"].append(row)
    receipt["status"]="ALL_FOUR_SOURCE_PASS" if all(r.get("result")=="PASS_SOURCE" and
        r.get("source_identity_verified") for r in receipt["probes"]) else "PARTIAL_OR_BLOCKED_NO_INGEST"
    OUT.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("FX_READINESS_DONE",receipt["status"],"calls",receipt["calls_attempted"],
          "result_matrix",[(x["pair"],x["start"][:4],x["result"],x.get("n_returned")) for x in receipt["probes"]],flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
