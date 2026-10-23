"""Independently verify ALL 54 official GPR vintages (3 index series) against Neon.

The source file for each vintage comes from its ACTUAL historic Git commit,
rather than today's final GPR source. Full month-by-month value digest on
1985..vintage-1, no interpolation, no re-scaling, and exact original Git
availability lower bound. Also parse Aug/Sep 2026 missing vintages as a
separate, research-only dated source for later append-only DB staging.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,io,json,math,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd

REPO="iacoviel/iacoviel.github.io"
METRIC_IDS={"GPR":"GPR_OFFICIAL_GIT_PIT",
            "GPRT":"GPRT_OFFICIAL_GIT_PIT",
            "GPRA":"GPRA_OFFICIAL_GIT_PIT"}
NEW={
 "2026-09":{"commit":"21449bec606bc5a5b1bf58d08ce526dc35d66c94","sha":"253056ac5d54881c1f3e5767087ef682e258c7a5","released":"2026-09-01T14:27:55Z"},
 "2026-10":{"commit":"8b903073ea4ce9caf9b2f238e792685ca17270f4","sha":"a46ff84a7e9fe83f5d1b73186d161aeba57b4da0","released":"2026-10-01T14:19:21Z"}
}

def get_gpr(vintage,commit,path,expected_blob=None):
    url=f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}"
    err=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"GPR-vintage-IntegrityAudit/1.0"}),timeout=110) as stream:
                raw=stream.read()
            break
        except Exception as e:
            err=e
            time.sleep(1+attempt)
    else:
        raise RuntimeError(f"OFFICIAL_VINTAGE_DOWNLOAD_FAILED {vintage} {err}")
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    if expected_blob and sha!=expected_blob:
        raise RuntimeError(f"OFFICIAL_GPR_BLOB_UNEXPECTED {vintage} got={sha}")
    frame=pd.read_excel(io.BytesIO(raw),engine="xlrd",sheet_name="Sheet1")
    if not set(["month","GPR","GPRT","GPRA"]).issubset(frame.columns):
        raise RuntimeError(f"INVALID_OFFICIAL_INDEX_COLUMNS {vintage}")
    parsed={}
    for _,r in frame.iterrows():
        d=r["month"]
        if pd.isna(d):continue
        month=pd.to_datetime(d,errors="coerce")
        if pd.isna(month):continue
        k=month.strftime("%Y-%m")
        if k<"1985-01" or k>=vintage:continue
        vals={}
        for col in METRIC_IDS:
            v=r[col]
            if pd.isna(v):raise RuntimeError(f"OFFICIAL_INDEX_SERIES_HOLE {vintage} {k} {col}")
            v=float(v)
            if not math.isfinite(v) or v<0:raise RuntimeError(f"GPR_VALUE_BAD {vintage} {k} {col}")
            vals[col]=v
        if k in parsed:raise RuntimeError(f"GPR_DUPLICATE_MONTH {vintage} {k}")
        parsed[k]=vals
    return {"vintage":vintage,"commit":commit,"path":path,
            "sha":sha,"month_values":parsed,"byte_count":len(raw)}

def digest(values,metric):
    items=sorted(values)
    s="\n".join(f"{k}|{values[k][metric]:.6f}" for k in items)
    return hashlib.md5(s.encode()).hexdigest()

def run(manifest):
    if manifest.get("vintage_count")!=54 or len(manifest["rows"])!=162:
        raise RuntimeError("BAD_NEON_BASELINE_54x3")
    refs={}
    for row in manifest["rows"]:
        key=(row["vintage"],row["series_id"])
        if key in refs:raise RuntimeError("DUPLICATE_NEON_REFERENCE")
        refs[key]=row
    vintages={row["vintage"]:(row["source_commit"],row["source_path"])
              for row in manifest["rows"]}
    if len(vintages)!=54:raise RuntimeError("INCONSISTENT_VINTAGE_INPUT")
    specs=[(v,c,p,None) for v,(c,p) in sorted(vintages.items())]
    specs.extend((v,d["commit"],f"gpr_archive_files/data_gpr_export_{v.replace('-','')}.xls",d["sha"]) for v,d in NEW.items())
    loaded=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futs=[pool.submit(get_gpr,*x) for x in specs]
        for fut in concurrent.futures.as_completed(futs):loaded.append(fut.result())
    result=[]
    additions=[]
    for item in sorted(loaded,key=lambda z:z["vintage"]):
        v=item["vintage"]
        values=item["month_values"]
        months=sorted(values)
        if not months or months[0]!="1985-01":
            raise RuntimeError(f"GPR_START_HISTORY_MISSING {v}")
        # Contiguous monthly sequence through the previous month.
        first_y,first_m=1985,1
        for key in months:
            wanted=f"{first_y:04d}-{first_m:02d}"
            if key!=wanted:raise RuntimeError(f"GPR_HISTORY_MONTH_GAP {v} got={key} wanted={wanted}")
            first_y,first_m=(first_y+1,1) if first_m==12 else (first_y,first_m+1)
        if months[-1]!=monthshift(v,-1):
            raise RuntimeError(f"GPR_RELEASE_MISSING_PREV_MONTH {v} last={months[-1]}")
        for metric,sid in METRIC_IDS.items():
            md5=digest(values,metric)
            source_ref=refs.get((v,sid))
            if source_ref:
                if len(months)!=source_ref["n"] or md5!=source_ref["md5_6dp"]:
                    raise RuntimeError(f"NEON_GPR_VALUE_SCALE_VINTAGE_MISMATCH {v} {metric} n={len(months)} expect_n={source_ref['n']} hash={md5} ref_hash={source_ref['md5_6dp']}")
                if source_ref["last_month"]!=months[-1]+"-01" or source_ref["first_month"]!="1985-01-01":
                    raise RuntimeError(f"NEON_GPR_MONTH_RANGE_INCONSISTENT {v} {metric}")
                state="EXACT_NEON_INDEX_PARITY"
            else:
                if v not in NEW:raise RuntimeError(f"GPR_UNEXPECTED_VINTAGE {v}")
                state="NEW_ORIGINAL_SOURCE_VINTAGE_AWAITING_DB_COMPLETE_IMPORT"
            result.append({"vintage":v,"metric":metric,"months":len(months),
                           "last_observed":months[-1],"source_git_sha":item["sha"],
                           "md5_6dp":md5,"status":state})
        if v in NEW:
            if months[-1] not in ("2026-08","2026-09"):
                raise RuntimeError("UNEXPECTED_NEW_GPR_CUTOFF")
            for ym in months:
                if ym<"2010-01":continue
                for metric,value in values[ym].items():
                    additions.append({"vintage":v,"metric":metric,"observed_month":ym,
                                      "index_value":value,"source_commit":item["commit"],
                                      "source_blob":item["sha"],"released_utc":NEW[v]["released"],
                                      "source":"iacoviel/iacoviel.github.io",
                                      "provenance":"OFFICIAL_GIT_COMMIT_RESEARCH_RECONSTRUCTION",
                                      "firstprint_as_captured_by_our_system":False})
        print(f"GPR_ORIGINAL_VINTAGE_CHECK {v} {sum(x['vintage']==v for x in result)}/3",flush=True)
    if len(result)!=168 or sum(x["status"]=="EXACT_NEON_INDEX_PARITY" for x in result)!=162:
        raise RuntimeError(f"GPR_ALL_VINTAGES_NOT_EXACT {len(result)}")
    if len(additions)!=(200+201)*3:raise RuntimeError(f"GPR_NEW_COMPLETE_ADD_COUNT {len(additions)}")
    return {"schema":"GPR_OFFICIAL_2010_2026_EXACT_56_VINTAGE_VALUE_AUDIT_V1",
            "status":"OFFICIAL_GIT_SOURCE_CHECKED_162_NEON_PARITIES_NEW_VINTAGES_RESEARCH_ONLY",
            "verified_prior_vintages":54,"verified_existing_series_digests":162,
            "original_monthly_values_parsed_for_new_vintages":len(additions),
            "new_vintages":["2026-09","2026-10"],
            "unit":"GPR/GPRT/GPRA index, baseline normalization 1985-2019 equals 100, NOT percentage and NOT probability",
            "firstprint_captured_for_2010_origins":False,
            "results":result},additions

def monthshift(month,delta):
    y,m=map(int,month.split("-"))
    x=y*12+m-1+delta
    return f"{x//12:04d}-{x%12+1:02d}"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--report",required=True)
    p.add_argument("--new-vintage-rows",required=True)
    a=p.parse_args()
    report,rows=run(json.loads(Path(a.manifest).read_text()))
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    Path(a.new_vintage_rows).write_text(json.dumps({
        "schema":"OFFICIAL_GPR_2026_SEP_OCT_ALL_2010_FORWARD_VINTAGE_ROWS_V1",
        "source":"iacoviel/iacoviel.github.io","metric_unit":"INDEX",
        "rows":rows,"firstprint_certified":False,"model_promotion":False,
    },indent=2,sort_keys=True)+"\n")
    print("GPR_54_EXISTING_OFFICIAL_VINTAGES_EXACT_PARITY=PASS",len(report["results"]),len(rows),flush=True)

if __name__=="__main__":main()
