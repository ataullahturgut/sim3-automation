"""Verify unchanged original GPR Git vintages and official World Bank workbook.

The existence and bytes of an original workbook are verified. XLS/XLSX
parsing or selecting a monthly value is a later, independent scientific gate;
do NOT interpret source-file existence as validated model values.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

GPR={
 "2026-09":{"commit":"21449bec606bc5a5b1bf58d08ce526dc35d66c94",
  "blob":"253056ac5d54881c1f3e5767087ef682e258c7a5",
  "path":"gpr_archive_files/data_gpr_export_202609.xls",
  "archive_commit_time":"2026-09-01T14:27:55Z",
  "contains_observations_through":"2026-08"},
 "2026-10":{"commit":"8b903073ea4ce9caf9b2f238e792685ca17270f4",
  "blob":"a46ff84a7e9fe83f5d1b73186d161aeba57b4da0",
  "path":"gpr_archive_files/data_gpr_export_202610.xls",
  "archive_commit_time":"2026-10-01T14:19:21Z",
  "contains_observations_through":"2026-09"}
}
GPR_REPO="iacoviel/iacoviel.github.io"
WB_OFFICIAL_URL="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def verify(sep:str,oct:str,wb:str):
    out={}
    for key,p in (("2026-09",sep),("2026-10",oct)):
        data=Path(p).read_bytes()
        h=git_blob(data)
        exp=GPR[key]["blob"]
        if h!=exp:raise RuntimeError(f"GPR_GIT_BLOB_SHA_MISMATCH {key} got={h}")
        if len(data)<100000 or data[:8]!=bytes.fromhex("d0cf11e0a1b11ae1"):
            raise RuntimeError(f"GPR_LEGACY_XLS_HEADER_FAIL {key}")
        out[key]={
            **GPR[key],"source_repo":GPR_REPO,
            "git_blob_sha_verified":h,"size_bytes":len(data),
            "source_file_integrity":"VERIFIED_UNCHANGED",
            "gpr_monthly_values_parsed":False,"live_first_capture_verified":False}
    wbdat=Path(wb).read_bytes()
    if len(wbdat)<100000 or wbdat[:2]!=b"PK":
        raise RuntimeError("WORLD_BANK_XLSX_SOURCE_HEADER_FAIL")
    return {
        "schema":"GOLD_MONTHLY_ORIGINAL_GPR_WB_WORKBOOK_SOURCE_GATE_V1",
        "status":"ORIGINAL_SOURCE_FILES_FETCHED_AND_BYTES_VERIFIED_NOT_PARSED",
        "gpr_official":{"repo":GPR_REPO,"vintages":out},
        "worldbank_official":{"url":WB_OFFICIAL_URL,
           "sha256":hashlib.sha256(wbdat).hexdigest(),
           "size_bytes":len(wbdat),
           "xlsx_container_verified":True,
           "worldbank_gold_monthly_values_parsed":False},
        "model_eligible":False,
        "can_replace_canonical_model_inputs":False,
        "neon_writes":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gpr-sep",required=True);p.add_argument("--gpr-oct",required=True)
    p.add_argument("--wb",required=True);p.add_argument("--report",required=True)
    x=p.parse_args()
    result=verify(x.gpr_sep,x.gpr_oct,x.wb)
    Path(x.report).write_text(json.dumps(result,indent=2,sort_keys=True)+chr(10))
    print("OFFICIAL_GPR_WB_SOURCE_BYTES_GATE=PASS")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
