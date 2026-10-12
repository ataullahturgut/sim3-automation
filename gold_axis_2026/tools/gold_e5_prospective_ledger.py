"""E5 prospective append-only journal (manual/event-ingest stage, not a model scheduler).

Captures UTC time with system clock at append; do not backdate. Repository history
and a SHA256 hash chain provide tamper evidence, not an unbreakable guarantee.
No network, database, bank scraping, account information or secrets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"prospective"/"GOLD_E5_PROSPECTIVE_EVENTS.ndjson"
SCHEMA="GOLD_E5_V1"
ZERO="0"*64
TR=ZoneInfo("Europe/Istanbul")

def dt(s):
    if not isinstance(s,str):
        raise ValueError("Timestamp must be ISO-8601 with offset")
    z=datetime.fromisoformat(s.replace("Z","+00:00"))
    if z.tzinfo is None:
        raise ValueError("Naive timestamp prohibited")
    return z.astimezone(timezone.utc)

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha(o):
    return hashlib.sha256(canon(o).encode("utf-8")).hexdigest()

def assert_keys(payload,allow,must):
    if not isinstance(payload,dict) or not set(must)<=set(payload) or not set(payload)<=set(allow):
        raise ValueError("Invalid payload fields; extra fields (including secrets) prohibited")

def validate_payload(kind,payload,captured):
    if kind=="FORECAST":
        req={"session","window_start","window_end","feature_cutoff","model_git_sha","model_name",
             "prediction","probability_up","data_snapshot_sha256"}
        assert_keys(payload,req,req)
        if payload["session"] not in ("DAY","OVN"):
            raise ValueError("Unknown session")
        if payload["prediction"] not in ("UP","DOWN","ABSTAIN"):
            raise ValueError("Unknown prediction")
        prob=payload["probability_up"]
        if prob is not None and (not isinstance(prob,(int,float)) or isinstance(prob,bool) or not 0<=prob<=1):
            raise ValueError("Invalid probability")
        if not re.fullmatch(r"[0-9a-fA-F]{40}",str(payload["model_git_sha"])):
            raise ValueError("Model SHA must be full 40-hex git commit")
        if not re.fullmatch(r"[0-9a-fA-F]{64}",str(payload["data_snapshot_sha256"])):
            raise ValueError("Input snapshot SHA256 required")
        if not isinstance(payload["model_name"],str) or not payload["model_name"].strip():
            raise ValueError("Missing model name")
        start=dt(payload["window_start"])
        end=dt(payload["window_end"])
        cutoff=dt(payload["feature_cutoff"])
        if not cutoff<=captured<start<end:
            raise ValueError("Non-prospective forecast, incomplete feature, or invalid order")
        local=start.astimezone(TR)
        if payload["session"]=="DAY":
            if (local.hour,local.minute)!=(9,0):
                raise ValueError("DAY entry must be 09:00 Turkey time")
            close=end.astimezone(TR)
            if close.date()!=local.date() or (close.hour,close.minute)!=(16,45):
                raise ValueError("DAY exit must be 16:45 Turkey time")
        else:
            if (local.hour,local.minute)!=(16,45):
                raise ValueError("OVN entry must be 16:45 Turkey time")
            if local.weekday()>3:
                raise ValueError("No Friday/weekend OVN")
            close=end.astimezone(TR)
            if close.date()!=local.date()+timedelta(days=1) or (close.hour,close.minute)!=(9,0):
                raise ValueError("OVN must close next calendar day 09:00 TR")
    elif kind=="BANK_QUOTE":
        req={"provider","product","currency","unit","bid","ask"}
        assert_keys(payload,req,req)
        if not all(isinstance(payload[k],str) and payload[k].strip() for k in
                   ("provider","product","currency","unit")):
            raise ValueError("Source and quotation units are required")
        bid,ask=payload["bid"],payload["ask"]
        if any(not isinstance(x,(int,float)) or isinstance(x,bool) for x in (bid,ask)):
            raise ValueError("Quotes must be numeric")
        if not 0<bid<=ask:
            raise ValueError("Quotes must satisfy 0 < bid <= ask")
    else:
        raise ValueError("Unknown event kind")

def validate(path=LEDGER):
    prev=ZERO
    last=None
    count=0
    if not path.exists():
        raise ValueError("Ledger missing; initialize an empty file before first event")
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        try:
            event=json.loads(line)
            if set(event)!={"schema","captured_at_utc","kind","payload","previous_sha256","record_sha256"}:
                raise ValueError("Unexpected keys")
            if event["schema"]!=SCHEMA or event["previous_sha256"]!=prev:
                raise ValueError("Schema/chain break")
            record_hash=event["record_sha256"]
            if not isinstance(record_hash,str) or record_hash!=sha({k:v for k,v in event.items() if k!="record_sha256"}):
                raise ValueError("Record digest mismatch")
            captured=dt(event["captured_at_utc"])
            if last is not None and captured<last:
                raise ValueError("Non-monotone event timestamps")
            validate_payload(event["kind"],event["payload"],captured)
            prev,last,count=record_hash,captured,count+1
        except Exception as e:
            raise ValueError(f"Invalid journal line {number}: {e}") from e
    return {"records":count,"head_sha256":prev}

def append(kind,payload,path=LEDGER):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.touch(exist_ok=True)
    state=validate(path)
    now=datetime.now(timezone.utc)
    validate_payload(kind,payload,now)
    event={"schema":SCHEMA,"captured_at_utc":now.isoformat(),
           "kind":kind,"payload":payload,"previous_sha256":state["head_sha256"]}
    event["record_sha256"]=sha(event)
    with path.open("a",encoding="utf-8") as handle:
        handle.write(canon(event)+"\n")
        handle.flush()
        os.fsync(handle.fileno())
    print(canon(validate(path)))

def selftest():
    t=datetime(2026,10,13,5,45,tzinfo=timezone.utc)
    base={"session":"DAY","window_start":"2026-10-13T09:00:00+03:00",
          "window_end":"2026-10-13T16:45:00+03:00",
          "feature_cutoff":"2026-10-13T08:30:00+03:00",
          "model_git_sha":"a"*40,"model_name":"test-only",
          "prediction":"ABSTAIN","probability_up":None,
          "data_snapshot_sha256":"b"*64}
    validate_payload("FORECAST",base,t)
    try:
        validate_payload("FORECAST",{**base,"window_start":"2026-10-13T08:00:00+03:00"},t)
    except ValueError:
        pass
    else:
        raise AssertionError("Backdated forecast accepted")
    validate_payload("BANK_QUOTE",{"provider":"test-only","product":"gram-gold",
        "currency":"TRY","unit":"TRY/gram","bid":1.0,"ask":2.0},t)
    print("E5 self-test PASS (synthetic inputs, no recorded forecasts)")

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--validate",action="store_true")
    g.add_argument("--self-test",action="store_true")
    g.add_argument("--append-forecast",metavar="PAYLOAD_JSON")
    g.add_argument("--append-quote",metavar="PAYLOAD_JSON")
    a=p.parse_args()
    if a.self_test:selftest()
    elif a.validate:print(canon(validate()))
    else:
        fn=a.append_forecast or a.append_quote
        payload=json.loads(Path(fn).read_text(encoding="utf-8"))
        append("FORECAST" if a.append_forecast else "BANK_QUOTE",payload)
if __name__=="__main__":main()
