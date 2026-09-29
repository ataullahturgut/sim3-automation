from __future__ import annotations

import argparse
import io
import json
import math
import urllib.request
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

import gold_monthly_f4_b1_transform_parity_v1 as b1
import vw_midas_msvr_successor_v1 as base

SERIES = {
    "BROADUSD": {
        "fred_id": "DTWEXBGS",
        "source_bucket": "h10_daily",
        "source_key": "BROAD_USD_INDEX",
        "release": "H.10",
        "lag_days": 7,
    },
    "NOM10": {
        "fred_id": "DGS10",
        "source_bucket": "h15_daily",
        "source_key": "DGS10",
        "release": "H.15",
        "lag_days": 2,
    },
    "REAL10": {
        "fred_id": "DFII10",
        "source_bucket": "h15_daily",
        "source_key": "DFII10",
        "release": "H.15",
        "lag_days": 2,
    },
}
DEV_START, DEV_END = "2022-04", "2024-12"


def fetch_fred_csv(series_id: str, start: str, end: str):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={end}"
    last_err = None
    raw = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gold-monthly-audit/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read()
            break
        except Exception as e:
            last_err = repr(e)
            import time
            time.sleep(5 * (attempt + 1))
    if raw is None:
        raise RuntimeError(f"OFFICIAL_DOWNLOAD_FAILED series={series_id} err={last_err}")
    df = pd.read_csv(io.BytesIO(raw))
    date_col = df.columns[0]
    val_col = df.columns[1]
    df[date_col] = pd.to_datetime(df[date_col])
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce")
    df = df.dropna(subset=[val_col])
    return url, {d.date().isoformat(): float(v) for d, v in zip(df[date_col], df[val_col])}


def ext_series(ext: dict, spec: dict):
    s = b1.nested_daily(ext, spec["source_bucket"], spec["source_key"])
    return {d.strftime("%Y-%m-%d"): float(v) for d, v in s.items()}


def compare_series(name: str, ext_s: dict, off_s: dict):
    ext_dates = sorted(ext_s)
    mn, mx = ext_dates[0], ext_dates[-1]
    off_window = {d:v for d,v in off_s.items() if mn <= d <= mx}
    common = sorted(set(ext_s) & set(off_window))
    ext_only = sorted(set(ext_s) - set(off_window))
    off_only = sorted(set(off_window) - set(ext_s))
    diffs = [(d, ext_s[d], off_window[d], abs(ext_s[d]-off_window[d])) for d in common]
    max_row = max(diffs, key=lambda x:x[3]) if diffs else None
    mismatches = [x for x in diffs if x[3] > 1e-10]
    return {
        "series": name,
        "ext_min_date": mn,
        "ext_max_date": mx,
        "ext_n": len(ext_s),
        "official_window_n": len(off_window),
        "common_n": len(common),
        "ext_only_n": len(ext_only),
        "official_only_n": len(off_only),
        "ext_only_dates_first20": ext_only[:20],
        "official_only_dates_first20": off_only[:20],
        "max_abs_value_diff": None if max_row is None else max_row[3],
        "max_abs_value_diff_row": None if max_row is None else {
            "date":max_row[0], "external_v2":max_row[1], "official":max_row[2], "abs_diff":max_row[3]
        },
        "value_mismatch_gt_1e-10_n": len(mismatches),
        "value_mismatches_first20": [
            {"date":d,"external_v2":a,"official":b,"abs_diff":dd}
            for d,a,b,dd in mismatches[:20]
        ],
    }


def iso_to_ts_dict(s):
    return {pd.Timestamp(d):v for d,v in s.items()}


def eligible(series_iso, month, lag):
    s = iso_to_ts_dict(series_iso)
    vals,last,n = b1.eligible_month_values(s, month, lag)
    return vals, last, n


def fx_metrics(series_iso, p):
    pp = b1.mshift(p,-1)
    vp,lp,np_ = eligible(series_iso,p,7)
    vq,lq,nq = eligible(series_iso,pp,7)
    mr = float(math.log(float(np.mean(vp))/float(np.mean(vq))))
    r = np.diff(np.log(vp))
    rms = float(np.sqrt(np.mean(r*r)))
    return {
        "mr1":mr,
        "rms_vol":rms,
        "p_n":int(np_),"pp_n":int(nq),
        "p_last":lp,"pp_last":lq,
        "p_mean":float(np.mean(vp)),"pp_mean":float(np.mean(vq)),
        "daily_returns_n":int(len(r)),
    }


def rate_metrics(nom_iso, real_iso, p):
    pp=b1.mshift(p,-1)
    npv,nlast,nn=eligible(nom_iso,p,2)
    nqv,nqlast,nnq=eligible(nom_iso,pp,2)
    rpv,rlast,rn=eligible(real_iso,p,2)
    rqv,rqlast,rnq=eligible(real_iso,pp,2)
    nom_p=float(np.mean(npv)); nom_pp=float(np.mean(nqv))
    real_p=float(np.mean(rpv)); real_pp=float(np.mean(rqv))
    return {
        "nom10_diff":nom_p-nom_pp,
        "real10_diff":real_p-real_pp,
        "breakeven_diff":(nom_p-real_p)-(nom_pp-real_pp),
        "nom_p_mean":nom_p,"nom_pp_mean":nom_pp,
        "real_p_mean":real_p,"real_pp_mean":real_pp,
        "nom_p_last":nlast,"real_p_last":rlast,
        "nom_p_n":int(nn),"real_p_n":int(rn),
    }


def transform_parity(ext_s, off_s):
    fx_rows=[]
    rate_rows=[]
    max_fx_mr=0.0; max_fx_rms=0.0
    max_real=0.0; max_nom=0.0; max_be=0.0
    for target in base.month_range(DEV_START,DEV_END):
        p=b1.mshift(target,-1)
        ex=fx_metrics(ext_s["BROADUSD"],p)
        of=fx_metrics(off_s["BROADUSD"],p)
        dmr=abs(ex["mr1"]-of["mr1"]); drms=abs(ex["rms_vol"]-of["rms_vol"])
        max_fx_mr=max(max_fx_mr,dmr); max_fx_rms=max(max_fx_rms,drms)
        fx_rows.append({"target":target,"origin_month":p,"ext":ex,"official":of,
                        "mr1_abs_diff":dmr,"rms_abs_diff":drms})

        er=rate_metrics(ext_s["NOM10"],ext_s["REAL10"],p)
        orr=rate_metrics(off_s["NOM10"],off_s["REAL10"],p)
        dn=abs(er["nom10_diff"]-orr["nom10_diff"])
        dr=abs(er["real10_diff"]-orr["real10_diff"])
        db=abs(er["breakeven_diff"]-orr["breakeven_diff"])
        max_nom=max(max_nom,dn); max_real=max(max_real,dr); max_be=max(max_be,db)
        rate_rows.append({"target":target,"origin_month":p,"ext":er,"official":orr,
                          "nom10_diff_abs_diff":dn,"real10_diff_abs_diff":dr,
                          "breakeven_diff_abs_diff":db})
    return {
        "fx_max_mr1_abs_diff":max_fx_mr,
        "fx_max_rms_vol_abs_diff":max_fx_rms,
        "nom10_diff_max_abs_diff":max_nom,
        "real10_diff_max_abs_diff":max_real,
        "breakeven_diff_max_abs_diff":max_be,
        "fx_rows":fx_rows,
        "rate_rows":rate_rows,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    ext=json.loads(Path(a.external_v2).read_text())
    ext_s={}
    off_s={}
    urls={}
    series_cmp={}
    for name,spec in SERIES.items():
        ext_s[name]=ext_series(ext,spec)
        ext_dates=sorted(ext_s[name])
        url,off=fetch_fred_csv(spec["fred_id"], ext_dates[0], ext_dates[-1])
        off_s[name]=off; urls[name]=url
        series_cmp[name]=compare_series(name,ext_s[name],off_s[name])

    parity=transform_parity(ext_s,off_s)

    strict_series_pass=all(
        x["value_mismatch_gt_1e-10_n"]==0 and x["ext_only_n"]==0 and x["official_only_n"]==0
        for x in series_cmp.values()
    )
    transform_pass=all([
        parity["fx_max_mr1_abs_diff"] <= 1e-12,
        parity["fx_max_rms_vol_abs_diff"] <= 1e-12,
        parity["nom10_diff_max_abs_diff"] <= 1e-12,
        parity["real10_diff_max_abs_diff"] <= 1e-12,
        parity["breakeven_diff_max_abs_diff"] <= 1e-12,
    ])

    out={
        "schema":"GOLD_MONTHLY_F4_FX_RATES_RAW_DATA_AUTHORITY_AUDIT_V1_2026-09-29",
        "created_at_utc":datetime.utcnow().isoformat()+"Z",
        "official_distribution":"Federal Reserve data via FRED CSV; series source is Board of Governors",
        "official_urls":urls,
        "series_specs":SERIES,
        "external_v2_payload_sha256":ext.get("payload_sha256"),
        "series_comparison":series_cmp,
        "dev_transform_recalculation":parity,
        "gates":{
            "all_external_v2_dates_exist_in_official":all(x["ext_only_n"]==0 for x in series_cmp.values()),
            "no_official_dates_missing_inside_external_v2_window":all(x["official_only_n"]==0 for x in series_cmp.values()),
            "all_daily_values_exact_within_1e10":all(x["value_mismatch_gt_1e-10_n"]==0 for x in series_cmp.values()),
            "all_dev_transforms_exact_within_1e12":transform_pass,
            "strict_series_pass":strict_series_pass,
            "pass":strict_series_pass and transform_pass,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_RAW_DATA_AUDIT_GATE="+("PASS" if out["gates"]["pass"] else "FAIL"))
    print(json.dumps({
        "gates":out["gates"],
        "series_comparison":{k:{
            "ext_min_date":v["ext_min_date"],"ext_max_date":v["ext_max_date"],
            "ext_n":v["ext_n"],"official_window_n":v["official_window_n"],
            "common_n":v["common_n"],"ext_only_n":v["ext_only_n"],
            "official_only_n":v["official_only_n"],
            "max_abs_value_diff":v["max_abs_value_diff"],
            "value_mismatch_gt_1e-10_n":v["value_mismatch_gt_1e-10_n"],
        } for k,v in series_cmp.items()},
        "transform_max_diffs":{k:v for k,v in parity.items() if k.endswith("abs_diff")},
    },sort_keys=True))


if __name__=="__main__":
    main()
