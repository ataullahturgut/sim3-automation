"""Exact per-day/per-value StakTrakr source parity for all 4 metals, 2010-Jul2026."""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,math,urllib.request
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path

REPO="lbruton/StakTrakr"
COMMIT="ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
BLOBS={
2010:"1d38346744943a76ccd7e5b24c80ccd769e9e370",
2011:"17d56267ace16c94af9a48ccd308350ef087d565",
2012:"8431c175c76cd437e15b8ed9b85ef087d565",
2013:"d68f91aa7806a072d4a8d8f1c4bff4a1f19743c3",
2014:"92e3fde254057c1833b60c3965bb9785fa9b5a17",
2015:"75b36edcf4380b884391f126525dcb54183a0a0c",
2016:"347b67f47174f69f48e9218f5f3f6e75e151e2a6",
2017:"9a075784b7f66ef2c200c3175da86a3dced85468",
2018:"07310dce8e2f83070f0c4008e7a098bf9379f90d",
2019:"af1c4569119ea0ef4e23962866c893d317f4f15d",
2020:"3cd88a1386510ff26111de21f1ea1cd06ee5b3bc",
2021:"c4f47fd5b777d5eeed09c122caf77a09d8767d",
2022:"b0b59a86b736de85364ee7dbfeef843fff711e4b",
2023:"511b2410d8a1e0bec39efc730d0ffd4c2fd1c93a",
2024:"7dc6579d7e75b3ddb73e4480fd1653ff1ee2ff1c",
2025:"3b0d5f0901852e1e47b3d9156462336bb0ad6955",
2026:"64e025fb943b31b7bc8b89c6cf521db4210f560b",
}
METALS={"Gold":"XAU","Silver":"XAG","Platinum":"XPT","Palladium":"XPD"}

def gitblob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def loadyear(year):
    url=f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/data/spot-history-{year}.json"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"GoldResearchAudit/1.0"}),timeout=80) as s:raw=s.read()
    got=gitblob(raw)
    if got!=BLOBS[year]:raise RuntimeError(f"ORIGINAL_GIT_BLOB_FAIL year={year} got={got}")
    return year,json.loads(raw),got

def verify(ref):
    if ref.get("schema")!="GOLD_FOUR_METAL_2010_2026_NEON_DAILY_SOURCE_DIGEST_V1":raise RuntimeError("NEON_MANIFEST_INVALID")
    rows={(r["yr"],r["symbol"]):r for r in ref["groups"]}
    if len(rows)!=68:raise RuntimeError("NEON_MANIFEST_GROUP_COUNT")
    data=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks=[pool.submit(loadyear,year) for year in BLOBS]
        for f in concurrent.futures.as_completed(tasks):data.append(f.result())
    reports=[]
    for yr,allprice,blob in sorted(data):
        buckets=defaultdict(list)
        labels=defaultdict(Counter)
        keys=set()
        for p in allprice:
            if p["metal"] not in METALS:continue
            day=p["timestamp"][:10]
            if date.fromisoformat(day).year!=yr:raise RuntimeError("WRONG_YEAR_SOURCE")
            if yr==2026 and day>"2026-07-31":continue
            value=float(p["spot"])
            if not math.isfinite(value) or value<=0:raise RuntimeError("INVALID_SPOT")
            key=(p["metal"],day)
            if key in keys:raise RuntimeError("DUPLICATE_DAY_METAL")
            keys.add(key)
            buckets[p["metal"]].append((day,value))
            labels[p["metal"]][str(p.get("provider") or "UNKNOWN")+"/"+str(p.get("source") or "UNKNOWN")]+=1
        for metal,symbol in METALS.items():
            points=sorted(buckets[metal])
            expected=rows[(yr,symbol)]
            payload="\n".join(f"{day}|{price:.4f}" for day,price in points)
            digest=hashlib.md5(payload.encode()).hexdigest()
            if len(points)!=expected["n"] or digest!=expected["md5_day_value_4dp"]:
                raise RuntimeError(f"PRICE_SOURCE_VALUE_MISMATCH {yr} {metal} count={len(points)} expected={expected['n']} md5={digest} expected={expected['md5_day_value_4dp']}")
            reports.append({"year":yr,"metal":metal,"n":len(points),
                            "source_blob":blob,"daily_value_md5_4dp":digest,
                            "provider_source_labels":dict(labels[metal]),"status":"PASS"})
    return {"schema":"GOLD_FOUR_METAL_2010_2026_ORIGINAL_EXACT_SOURCE_PARITY_V1",
            "status":"EXACT_RESEARCH_SOURCE_VALUE_PARITY_NOT_OFFICIAL_LBMA_BENCHMARK_CERTIFICATION",
            "github_repository":REPO,"commit":COMMIT,
            "groups":reports,"groups_passed":len(reports),
            "daily_observations_checked":sum(r["n"] for r in reports),
            "firstprint_available_for_original_origin":False,
            "unit":"reported USD per troy ounce source-native four precious metals; original fixing/license not certified"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    out=verify(json.loads(Path(a.manifest).read_text()))
    Path(a.output).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("ORIGINAL_FOUR_METAL_68_GROUP_EXACT_VALUES=PASS",out["daily_observations_checked"],flush=True)

if __name__=="__main__":main()
