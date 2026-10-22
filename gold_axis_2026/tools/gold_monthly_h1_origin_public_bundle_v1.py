from __future__ import annotations
"""Origin-safe H=1 monthly data bundle, for actual future months only.

All external source commits are pinned at or before month-end 17:00 America/New_York.
If historical sources cannot prove complete origin-month observations the run FAILS,
and it produces no forecast. This does not retrofit PIT proof to 2010-2026 training.
"""
import argparse, calendar, hashlib, io, json, os, re, urllib.parse, urllib.request
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import gold_monthly_public_current_bundle_v1 as public

GIT_API="https://api.github.com/repos/"
START_PUBLIC="2025-01-01"

def month_origin(target):
    if not re.fullmatch(r"20[0-9]{2}-(0[1-9]|1[0-2])",target):
        raise RuntimeError("INVALID_YYYY_MM_TARGET")
    if target<"2026-11": raise RuntimeError("NO_RETROACTIVE_DYNAMIC_FORECAST")
    origin=base.month_shift(target,-1)
    y,m=map(int,origin.split("-"))
    last=date(y,m,calendar.monthrange(y,m)[1])
    cutoff=datetime(y,m,last.day,17,0,tzinfo=ZoneInfo("America/New_York"))
    return origin,last,cutoff

def github_api(path):
    req=urllib.request.Request(GIT_API+path,headers={
        "User-Agent":"gold-monthly-h1-asof-provenance/1.0",
        "Accept":"application/vnd.github+json",
        **({"Authorization":"Bearer "+os.environ["GH_TOKEN"]} if os.environ.get("GH_TOKEN") else {})
    })
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def pinned_before(owner_repo,cutoff,filepath=None):
    until=urllib.parse.quote(cutoff.astimezone(timezone.utc).isoformat(),safe="")
    args=f"commits?per_page=1&until={until}"
    if filepath:args+="&path="+urllib.parse.quote(filepath,safe="")
    matches=github_api(f"{owner_repo}/{args}")
    if not matches:raise RuntimeError(f"NO_SOURCE_COMMIT_BY_CUTOFF {owner_repo} {filepath}")
    chosen=matches[0]
    published=datetime.fromisoformat(chosen["commit"]["committer"]["date"].replace("Z","+00:00"))
    if published>cutoff.astimezone(timezone.utc):
        raise RuntimeError("SOURCE_COMMIT_AFTER_ORIGIN_CUTOFF")
    sha=chosen["sha"]
    if not re.fullmatch("[a-f0-9]{40}",sha):raise RuntimeError("INVALID_SOURCE_COMMIT")
    return {"sha":sha,"committedAtUtc":published.isoformat(),
            "url":f"https://github.com/{owner_repo}/commit/{sha}"}

def fetch_exact(repo,commit,filepath):
    url=f"https://raw.githubusercontent.com/{repo}/{commit}/{filepath}"
    raw=public.get_bytes(url)
    if len(raw)<200:raise RuntimeError("PINNED_SOURCE_FILE_TOO_SMALL")
    return raw,hashlib.sha256(raw).hexdigest(),url

def last_weekday_of_month(last):
    d=last
    while d.weekday()>=5:d-=timedelta(days=1)
    return d

def build(target,dev_snapshot):
    origin,origin_last,cutoff=month_origin(target)
    if datetime.now(timezone.utc)<=cutoff.astimezone(timezone.utc):
        raise RuntimeError("ORIGIN_MONTH_NOT_CLOSED")
    _,devmeta=snap.load_snapshot(dev_snapshot)
    stak_commit=pinned_before(public.STAK_REPO,cutoff)
    stak_api_commit=pinned_before(public.STAK_API_REPO,cutoff)
    gpr_path="gpr_archive_files/data_gpr_export_"+origin.replace("-","")+".xls"
    gpr_commit=pinned_before("iacoviel/iacoviel.github.io",cutoff,gpr_path)
    gpr_raw,gpr_sha,gpr_url=fetch_exact("iacoviel/iacoviel.github.io",gpr_commit["sha"],gpr_path)
    frame=public.workbook_series(gpr_raw,"GPR")
    gh={pd.Timestamp(r.date).strftime("%Y-%m"):float(r.value) for r in frame.itertuples()}
    lag=base.month_shift(origin,-1)
    if lag not in gh or len([m for m in gh if m<=lag])<24:
        raise RuntimeError("GPR_VINTAGE_MISSING_REQUIRED_P_MINUS_1")
    z=base.gpr_norm(gh,lag)
    daily,stak=public.fetch_stak_extension(stak_commit["sha"],stak_api_commit["sha"],
                                         START_PUBLIC,origin_last.isoformat())
    dates=[r["date"] for r in daily]
    if not dates or min(dates)>"2025-01-05":
        raise RuntimeError("FOUR_METAL_HISTORY_START_MISSING")
    maxd=max(dates)
    if maxd<last_weekday_of_month(origin_last).isoformat():
        raise RuntimeError(f"FOUR_METAL_MONTH_END_NOT_COMPLETE {maxd} {origin_last}")
    dates_origin=[d for d in dates if d.startswith(origin)]
    if len(dates_origin)<18:raise RuntimeError("ORIGIN_FOUR_METAL_DAILY_TOO_SHORT")
    pp=base.month_shift(origin,-1)
    wb,wbmeta=public.load_worldbank()
    # WorldBank values at origin may have been published AFTER cutoff. For that reason
    # all origin-price conversions use the completed, provenance-pinned Stak average.
    # Old training-core Gold uses the pre-origin months only (not its target).
    wb_safe={m:v for m,v in wb.items() if m<=pp and m>="2025-01"}
    bundle={
     "schema":"GOLD_MONTHLY_H1_ORIGIN_PUBLIC_BUNDLE_V1",
     "target":target,"origin":origin,
     "origin_cutoff_utc":cutoff.astimezone(timezone.utc).isoformat(),
     "daily_extension_rows":daily,
     "daily_extension_first":min(dates),"daily_extension_last":maxd,
     "world_bank":{"gold_monthly":wb_safe,**wbmeta},
     "gpr_vintages":{origin:gh},
     "gpr_meta":{origin:{
       "source_repository":"iacoviel/iacoviel.github.io",
       "origin":origin,"source_commit_sha":gpr_commit["sha"],
       "source_committed_at_utc":gpr_commit["committedAtUtc"],
       "source_xls_sha256":gpr_sha,"official_source_file":gpr_path,"official_source_url":gpr_url,
       "lag_month":lag,"lag_value":gh[lag],"gpr_z":z,
       "origin_cutoff_utc":cutoff.astimezone(timezone.utc).isoformat()
     }},
     "staktrakr":{"repo_ref":stak_commit["sha"],"api_repo_ref":stak_api_commit["sha"],**stak},
     "source_commits":{"stak":stak_commit,"stak_api":stak_api_commit,"gpr":gpr_commit},
     "authority":{"neon_reads":0,"dev_snapshot_payload_sha256":devmeta["payload_sha256"],
        "source_cutoff_proven":True,"origin_metal_month_complete":True,
        "external_daily_historical_origin_pit_proven":False,
        "world_bank_origin_publication_proven":False,
        "origin_reference_price_role":"STAKTRAKR_COMPLETED_ORIGIN_PROVISIONAL"},
    }
    raw=json.dumps(bundle,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    bundle["payload_sha256"]=hashlib.sha256(raw).hexdigest()
    return bundle

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",required=True)
    p.add_argument("--dev-snapshot",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    d=build(a.target,a.dev_snapshot)
    Path(a.output).write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("GOLD_MONTHLY_H1_ORIGIN_BUNDLE_GATE=PASS",json.dumps({
     "target":d["target"],"origin":d["origin"],"daily_last":d["daily_extension_last"],
     "gpr_origin":list(d["gpr_vintages"]),"source_commit":d["source_commits"],
     "sha256":d["payload_sha256"]},sort_keys=True))

if __name__=="__main__":main()
