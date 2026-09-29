from __future__ import annotations
import argparse,hashlib,json,urllib.request
from pathlib import Path
import numpy as np
import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base

STAK_REF="b7f5ced4ce802b55972e52bf45840ac28f1ca733"
METALS=base.METALS

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-prehistory/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def sha(b):return hashlib.sha256(b).hexdigest()

def parse(raw):
    rows=json.loads(raw); out={}
    for r in rows:
        m=r.get("metal")
        if m not in METALS: continue
        d=str(r.get("timestamp"))[:10]
        v=float(r["spot"])
        out.setdefault(d,{})[m]=v
    common={d:z for d,z in out.items() if set(z)==set(METALS)}
    return common

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    b,meta=snap.load_snapshot(a.snapshot)
    raw09=get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_REF}/data/spot-history-2009.json")
    raw10=get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_REF}/data/spot-history-2010.json")
    d09=parse(raw09); d10=parse(raw10)
    # Exact parity against frozen 2010 common rows for every available date/metal.
    frozen={}
    for m in METALS:
        for mk,v in b.daily_month_values[m].items():
            pass
    # reconstruct frozen date-level rows from snapshot payload directly
    doc=json.loads(Path(a.snapshot).read_text())
    fr={r["date"]:{m:float(r[m]) for m in METALS} for r in doc["payload"]["daily_common_rows"] if r["date"].startswith("2010-")}
    overlap=sorted(set(fr)&set(d10))
    if len(overlap)<250: raise RuntimeError(f"PREHISTORY_2010_OVERLAP_TOO_SMALL {len(overlap)}")
    diffs=[]
    for d in overlap:
        for m in METALS: diffs.append(abs(fr[d][m]-float(d10[d][m])))
    maxdiff=float(max(diffs)) if diffs else float("inf")
    if maxdiff>1e-12: raise RuntimeError(f"PREHISTORY_SOURCE_PARITY_FAIL maxdiff={maxdiff}")
    if min(d09)>"2009-01-05" or max(d09)<"2009-12-30":
        raise RuntimeError(f"PREHISTORY_2009_COVERAGE_FAIL {min(d09)} {max(d09)}")
    out={
      "schema":"GOLD_MONTHLY_METAL_PREHISTORY_V1_2026-09-29",
      "authority":{
        "source_repo":"lbruton/StakTrakr",
        "source_commit":STAK_REF,
        "role":"PREHISTORY_ONLY_FOR_REPRESENTATION_FEATURES",
        "neon_reads":0,
        "frozen_snapshot_payload_sha256":meta["payload_sha256"],
      },
      "source_hashes":{"spot_history_2009_sha256":sha(raw09),"spot_history_2010_sha256":sha(raw10)},
      "parity":{"overlap_2010_days":len(overlap),"max_abs_diff":maxdiff,"pass":True},
      "daily_2009":[{"date":d,**{m:float(d09[d][m]) for m in METALS}} for d in sorted(d09)],
    }
    raw=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    out["payload_sha256"]=sha(raw)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("METAL_PREHISTORY_GATE=PASS")
    print(json.dumps({"n_2009":len(d09),"first":min(d09),"last":max(d09),"parity":out["parity"],"payload_sha256":out["payload_sha256"]},sort_keys=True))
if __name__=="__main__":main()
