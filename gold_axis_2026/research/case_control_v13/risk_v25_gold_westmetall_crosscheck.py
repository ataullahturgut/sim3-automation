#!/usr/bin/env python3
"""Independent London gold reference 2024–2026 vs V23 Neon price snapshot.

Never overwrite historical records. Do not upload full third-party price series.
If public reference download fails, mark UNAVAILABLE (fail closed for certification).
"""
import re,json,hashlib
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

OUT=Path(__file__).parent/"outputs"
YEARS=(2024,2025,2026)
BASE_URL="https://www.westmetall.com/en/markdaten.php?action=table&field=USD_ozt_London&year={year}"

def parse_reference(html,year):
    soup=BeautifulSoup(html,"html.parser")
    pattern=re.compile(r"^(\d{1,2})\.\s+([A-Za-z]+)\s+(\d{4})$")
    p={}
    for tr in soup.find_all("tr"):
        cells=[x.get_text(" ",strip=True) for x in tr.find_all("td")]
        if len(cells)<2:
            continue
        m=pattern.fullmatch(cells[0])
        if not m or int(m.group(3))!=year:
            continue
        try:
            dt=datetime.strptime(cells[0],"%d. %B %Y").date().isoformat()
            val=float(cells[1].replace(",","").replace(" ",""))
        except (ValueError,IndexError):
            continue
        if val<=0:
            continue
        if dt in p and abs(p[dt]-val)>.000001:
            raise ValueError("DUPLICATED_DIFFERENT_WESTMETALL_DATE "+dt)
        p[dt]=val
    return p

def main():
    local=pd.read_csv(OUT/"v23_price_calendar_RESEARCH_NOT_PIT.csv")
    assert local.date.is_unique and local.date.min()=="2024-01-02"
    results=[];case=[];checks=[]
    for year in YEARS:
        url=BASE_URL.format(year=year)
        status={"year":year,"url":url,"source":"Westmetall Gold London Fixing", "reference_license":"SEE_PROVIDER_TERMS", "not_identical_to_snapshot_price_definition":True}
        try:
            res=requests.get(url,headers={"User-Agent":"GoldDataHealthV25Research/1.0"},timeout=18)
            status["http_status"]=res.status_code
            res.raise_for_status()
            reference=parse_reference(res.text,year)
            status["html_sha256"]=hashlib.sha256(res.content).hexdigest()
            status["reference_rows"]=len(reference)
            if len(reference)<140:
                raise ValueError("TOO_FEW_REFERENCE_DATES")
            a=local[(local.date.str[:4]==str(year))&(local.date.isin(reference))].copy()
            a["westmetall_london_fix"]=a.date.map(reference)
            a["percent_difference"]=100*(a.price/a.westmetall_london_fix-1)
            diff=a.percent_difference.abs()
            result=dict(year=year,matched_days=len(a),
                        research_days=int(local.date.str[:4].eq(str(year)).sum()),
                        median_abs_pct=round(float(diff.median()),4),
                        p95_abs_pct=round(float(diff.quantile(.95)),4),
                        days_abs_gt_2pct=int((diff>2).sum()),
                        days_abs_gt_5pct=int((diff>5).sum()),
                        days_abs_gt_20pct=int((diff>20).sum()),
                        source_http_status=res.status_code,
                        external_data_certified_same_fixing=False,
                        status="COMPARISON_COMPLETE_DEFINITION_UNVERIFIED")
            if year==2026:
                suspect=a[a.date=="2026-02-27"]
                if len(suspect)!=1 or abs(float(suspect.iloc[0].westmetall_london_fix)-5174.10)>.01:
                    raise ValueError("EXTERNAL_BAD_GOLD_REFERENCE_INCOMPLETE")
            for _,v in a[diff>5].iterrows():
                case.append(dict(date=v.date,year=year,db_price=v.price,
                                 external_gold_fixing=v.westmetall_london_fix,
                                 abs_difference_pct=round(abs(v.percent_difference),4),
                                 still_requires_instrument_time_alignment=True))
            results.append(result)
            status["status"]="OK_RESEARCH_ONLY"
        except Exception as e:
            status["status"]="FAILED_NO_COVERAGE"
            status["error_type"]=type(e).__name__
            status["error_message"]=str(e)[:240]
            results.append(dict(year=year,status="UNAVAILABLE",
                         matched_days=0,research_days=int(local.date.str[:4].eq(str(year)).sum()),
                         source_http_status=status.get("http_status"),
                         external_data_certified_same_fixing=False))
        checks.append(status)
    pd.DataFrame(results).to_csv(OUT/"v25_westmetall_gold_2024_2026_coverage.csv",index=False)
    pd.DataFrame(case,columns=["date","year","db_price","external_gold_fixing",
                               "abs_difference_pct","still_requires_instrument_time_alignment"]).to_csv(
        OUT/"v25_westmetall_gold_large_differences.csv",index=False)
    manifest={
      "research_only":True,"Neon_mutated":False,
      "never_equate_unverified_reference_fixing_with_local_snapshot":True,
      "gold_2024_2026_external_comparison_years_ok":sum(q["status"]=="OK_RESEARCH_ONLY" for q in checks),
      "checks":checks,
      "full_gold_source_definition_certified":False,
      "monthly_H1_promotion_allowed":False}
    (OUT/"v25_westmetall_research_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("V25_WESTMETALL_RESULTS",pd.DataFrame(results).to_string(index=False))
    print("V25_WESTMETALL_MANIFEST",json.dumps(manifest,ensure_ascii=False))

if __name__=="__main__":main()
