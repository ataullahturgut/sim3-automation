#!/usr/bin/env python3
"""V26: 2010–2026 four-metal independent daily data comparator (research-only).

External GoldPrice.com history claims attribution-friendly CSV. It is a
DIFFERENT price definition, often daily close versus LBMA London fixing.
Never automatically replace the StakTrakr benchmark with a different close.
Never infer point-in-time first-print availability from today's archived CSV.
Downloads are ephemeral CI inputs; only aggregates and exceptions are saved.
"""
from __future__ import annotations
import io,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
import requests

HERE=Path(__file__).parent
OUT=HERE/"outputs"
FILES=("v26_internal_fourmetal_2010_2018_NOT_PIT.csv",
       "v26_internal_fourmetal_2019_2026_NOT_PIT.csv")
METALS=("AU","AG","PT","PD")
URLS={m:"https://goldprice.com/"+slug+"-price-history.csv" for m,slug in
      {"AU":"gold","AG":"silver","PT":"platinum","PD":"palladium"}.items()}
EXCLUDED="2026-02-27"

def checked_price_frame(raw,metal):
    # Files published as date,close USD per troy ounce.
    t=pd.read_csv(io.BytesIO(raw))
    t.columns=[str(x).lstrip("\ufeff").strip().lower() for x in t.columns]
    if "date" not in t.columns:
        raise ValueError("EXTERNAL_NO_DATE_"+metal+"_"+repr(t.columns.tolist()))
    value=next((v for v in ("close","value","price","usd_per_oz") if v in t.columns),None)
    if not value:
        raise ValueError("EXTERNAL_NO_PRICE_"+metal+"_"+repr(t.columns.tolist()))
    d=pd.to_datetime(t.date,errors="coerce",utc=True)
    p=pd.to_numeric(t[value].astype(str).str.replace(",","",regex=False),errors="coerce")
    z=pd.DataFrame({"date":d.dt.strftime("%Y-%m-%d"),"external":p}).dropna()
    if z.date.duplicated().any() or (z.external<=0).any():
        raise ValueError("EXTERNAL_DUPLICATE_OR_NONPOSITIVE_"+metal)
    if len(z)<4000 or z.date.min()>"2010-01-01" or z.date.max()<"2026-09-01":
        raise ValueError("EXTERNAL_INADEQUATE_COVERAGE_"+metal+"_"+str(len(z)))
    return z.set_index("date")["external"]

def internal_snapshot():
    d=pd.concat([pd.read_csv(OUT/n) for n in FILES],ignore_index=True)
    assert len(d)==4234 and d.date.is_unique and d.date.is_monotonic_increasing
    assert d.date.iloc[0]=="2010-01-04" and d.date.iloc[-1]=="2026-09-30"
    assert (d[list(METALS)]>0).all().all()
    feb=d.set_index("date").loc[EXCLUDED]
    assert feb.AU==3516.02 and feb.AG==62.15 and feb.PT==1585.39 and feb.PD==1201.26
    return d

def run():
    internal=internal_snapshot()
    summary,exceptions,source,allpairs=[],[],[],[]
    for metal,url in URLS.items():
        metadata={"metal":metal,"url":url,"date_field":"date",
                  "reference_type":"GoldPrice.com daily close (may differ from London fixing)",
                  "same_fixing_definition_proven":False,"historical_first_print_PIT_proven":False}
        try:
            r=requests.get(url,timeout=35,headers={"User-Agent":"GoldHealthResearchV26/1.0"})
            metadata["http_status"]=r.status_code
            r.raise_for_status()
            metadata["download_sha256"]=hashlib.sha256(r.content).hexdigest()
            ext=checked_price_frame(r.content,metal)
            metadata["download_rows"]=len(ext)
            s=internal[["date",metal]].rename(columns={metal:"internal"}).copy()
            s["external"]=s.date.map(ext)
            s["abs_diff_pct"]=100*(s.internal/s.external-1).abs()
            s["diff_pct"]=100*(s.internal/s.external-1)
            s["matched"]=s.external.notna()
            metadata["matched"]=int(s.matched.sum())
            if s.matched.sum()<2500:
                raise ValueError("TOO_FEW_MATCHES_"+metal)
            for year,t in s.groupby(s.date.str[:4]):
                v=t.loc[t.matched,"abs_diff_pct"]
                summary.append(dict(year=int(year),metal=metal,
                    internal_days=int(len(t)),external_matched=int(len(v)),
                    unmatched=int(len(t)-len(v)),median_abs_pct=float(v.median()) if len(v) else np.nan,
                    p95_abs_pct=float(v.quantile(.95)) if len(v) else np.nan,
                    max_abs_pct=float(v.max()) if len(v) else np.nan,
                    differences_gt_2pct=int((v>2).sum()),differences_gt_5pct=int((v>5).sum()),
                    external_close_not_automatically_same_as_LBMA_fixing=True,
                    status="RESEARCH_COMPARISON_NOT_PIT"))
            suspicious=s.loc[s.abs_diff_pct>5].sort_values("abs_diff_pct",ascending=False)
            for _,t in suspicious.iterrows():
                exceptions.append(dict(date=t.date,metal=metal,internal_usd=t.internal,
                    external_close_usd=t.external,
                    difference_pct=t.diff_pct,abs_difference_pct=t.abs_diff_pct,
                    data_health_class=("QUARANTINED_CONFIRMED_WRONG_SOURCE"
                                       if t.date==EXCLUDED else "REVIEW_DIFFERENT_SOURCE_DEFINITION"),
                    no_automatic_replacement=True))
            f=s.loc[s.date==EXCLUDED].iloc[0]
            metadata["feb27_external_close"]=None if pd.isna(f.external) else float(f.external)
            metadata["feb27_internal_price"]=float(f.internal)
            metadata["status"]="RESEARCH_COMPARE_COMPLETE"
        except Exception as ex:
            metadata["status"]="UNAVAILABLE_NO_CERTIFICATION"
            metadata["failure"]=type(ex).__name__+":"+str(ex)[:320]
        source.append(metadata)
    # Only aggregated results and exception differences, no rehosting original external CSV.
    columns=["date","metal","internal_usd","external_close_usd","difference_pct",
             "abs_difference_pct","data_health_class","no_automatic_replacement"]
    pd.DataFrame(summary).to_csv(OUT/"v26_fourmetal_independent_daily_year_comparison.csv",index=False)
    pd.DataFrame(exceptions,columns=columns).to_csv(
        OUT/"v26_fourmetal_independent_large_discrepancies.csv",index=False)
    status={"source_files":list(FILES),"historical_internal_fourmetal_dates":len(internal),
      "source_hist_pre2026":"StakTrakr ed2e549f82ba0d1cd3ca32842b82d3888d301e01",
      "source_2026":"StakTrakr 02964d0324dde362099976c867f5077a369acaa5",
      "external_website":"GoldPrice.com (attribution required)",
      "external_last_download_hashes":[{"metal":v["metal"],"hash":v.get("download_sha256")}
                                       for v in source],
      "sources":source,
      "all_four_independently_compared":all(z["status"]=="RESEARCH_COMPARE_COMPLETE" for z in source),
      "benchmark_definition_identical_verified":False,
      "historical_first_print_prices_verified":False,
      "raw_Neon_modified":False,"research_only":True,
      "safe_to_auto_replace_from_different_price_definition":False,
      "safe_for_live_forecasting":False}
    (OUT/"v26_fourmetal_comparison_manifest.json").write_text(
        json.dumps(status,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print("V26_INDEPENDENT_YEAR_COMPARISON")
    print(pd.DataFrame(summary).to_string(index=False))
    print("V26_INDEPENDENT_EXCEPTIONS_TOP15")
    print(pd.DataFrame(exceptions).sort_values("abs_difference_pct",ascending=False).head(15).to_string(index=False)
          if exceptions else "NONE")
    print("V26_FOURMETAL_SOURCE_STATUS",json.dumps(status,ensure_ascii=False))
    if not status["all_four_independently_compared"]:
        # fail closed; permanent evidentiary outputs can still be reviewed
        raise RuntimeError("V26_EXTERNAL_FOURMETAL_COVERAGE_NOT_COMPLETE")
    return status

if __name__=="__main__":
    run()
