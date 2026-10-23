"""Warning-only adapter to layer risk origins onto an ACTIVE forecast.

No changes to predictions, no fake probability of ANN error. Forecast is
marked only with warnings already generated at or before the requested as-of
date. Existing earlier alerts may overlap later forecast horizons. High
anomaly != confirmed fall direction.
"""
from __future__ import annotations
import argparse,json
from datetime import date
from pathlib import Path

def annotate(overlays,forecast):
    issue=forecast["issue_date"]
    start=forecast["target_start"]
    end=forecast["target_end"]
    asof=forecast["as_of_date"]
    if not issue<=asof or not start<=end:
        raise ValueError("invalid forecast as-of / date interval")
    if asof>=end:
        raise ValueError("as_of >= target end: historical forecast completed")
    family=forecast.get("risk_family","METAL_GVZ_USD_RATES")
    risks=[
        r for r in overlays["rows"]
        if r["family"]==family
        and r["origin"]<=asof
        and r["level"] in ("RED","YELLOW")
        # a 5d risk outlook intersects the requested forecast horizon
        and r["forecast_target_start"]<=end
        and r["horizon5_last"]>=start
    ]
    ranked={"RED":2,"YELLOW":1,"NORMAL":0}
    risks.sort(key=lambda r:(r["origin"],ranked[r["level"]]))
    most=max((r["level"] for r in risks),key=lambda v:ranked[v],default="NORMAL")
    eligible_after_issue=[r for r in risks if r["origin"]>=issue]
    eligible_before_issue=[r for r in risks if r["origin"]<issue]
    # An alert that existed already at forecast issue is separate from
    # *later* monitoring updates, which cannot retroactively change the
    # original issuance metadata.
    return {
      "forecast_id":forecast.get("forecast_id"),
      "model":forecast["model"],
      "issue_date":issue,"target_start":start,"target_end":end,
      "as_of_date":asof,
      "risk_family":family,"risk_level":most,
      "forecast_value_unchanged":forecast.get("forecast_value"),
      "warning_text":(
         "Olağan dışı piyasa koşulları tespit edildi. Bu tahminin belirsizliği"
         " artmış olabilir; bu bir düşüş veya ANN hata olasılığı değildir."
         if most!="NORMAL" else
         "Bu katman son kontrol tarihinde yüksek anomali uyarısı üretmedi;"
         " tahminin kesin doğruluğu anlamına gelmez."),
      "warnings_existing_before_original_issue":[{"origin":r["origin"],"level":r["level"]}
            for r in eligible_before_issue],
      "warnings_new_since_original_issue":[{"origin":r["origin"],"level":r["level"]}
            for r in eligible_after_issue],
      "base_forecast_modified":False,
      "risk_signal_is_not_calibrated_error_probability":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--risk-json",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    layer=json.loads(Path(a.risk_json).read_text())
    require=lambda ok,msg: None if ok else (_ for _ in ()).throw(RuntimeError(msg))
    require(layer["ann_error_probability_validated"] is False,"untrusted probability assertion")
    examples=[
      {"forecast_id":"JAN26_MONTHLY_ISSUED_END2025_PRE_2026_ALERT","model":"MONTHLY_ANN_RESEARCH",
       "issue_date":"2025-12-31","target_start":"2026-01-01","target_end":"2026-01-31",
       "as_of_date":"2025-12-31","forecast_value":None},
      {"forecast_id":"JAN26_MONTHLY_UPDATED_ASOF_JAN28","model":"MONTHLY_ANN_RESEARCH",
       "issue_date":"2025-12-31","target_start":"2026-01-01","target_end":"2026-01-31",
       "as_of_date":"2026-01-28","forecast_value":None},
      {"forecast_id":"FRI_JAN30_ISSUED_JAN29","model":"DAILY_ANN_RESEARCH",
       "issue_date":"2026-01-29","target_start":"2026-01-30","target_end":"2026-01-30",
       "as_of_date":"2026-01-29","forecast_value":5478.903740930488},
      {"forecast_id":"FEB26_MONTHLY_ISSUED_JAN30","model":"MONTHLY_ANN_RESEARCH",
       "issue_date":"2026-01-30","target_start":"2026-02-01","target_end":"2026-02-28",
       "as_of_date":"2026-01-30","forecast_value":4892.34},
      {"forecast_id":"FEB2_WEEK_ISSUED_JAN30","model":"WEEKLY_ANN_RESEARCH",
       "issue_date":"2026-01-30","target_start":"2026-02-02","target_end":"2026-02-06",
       "as_of_date":"2026-01-30","forecast_value":5037.21},
      {"forecast_id":"FEB26_MONTHLY_POSTHOC_MAR1","model":"MONTHLY_ANN_RESEARCH",
       "issue_date":"2026-01-30","target_start":"2026-02-01","target_end":"2026-02-28",
       "as_of_date":"2026-02-28","forecast_value":4892.34},
    ]
    out=[]
    for f in examples:
      try: v=annotate(layer,f)
      except ValueError as exc:
        if f["forecast_id"]=="FEB26_MONTHLY_POSTHOC_MAR1":
          continue
        raise
      out.append(v)
    pre=next(x for x in out if x["forecast_id"]=="JAN26_MONTHLY_ISSUED_END2025_PRE_2026_ALERT")
    post=next(x for x in out if x["forecast_id"]=="JAN26_MONTHLY_UPDATED_ASOF_JAN28")
    jan=next(x for x in out if x["forecast_id"]=="FRI_JAN30_ISSUED_JAN29")
    feb=next(x for x in out if x["forecast_id"]=="FEB26_MONTHLY_ISSUED_JAN30")
    assert not pre["warnings_new_since_original_issue"]
    assert post["risk_level"]=="RED" and post["warnings_new_since_original_issue"]
    assert jan["risk_level"]=="RED" and jan["forecast_value_unchanged"]==5478.903740930488
    assert feb["risk_level"]=="RED" and feb["forecast_value_unchanged"]==4892.34
    assert not any(x["base_forecast_modified"] for x in out)
    Path(a.out).write_text(json.dumps({"status":"FORECAST_RISK_OVERLAY_EXAMPLES_TEST_PASS",
      "not_deployed_to_app":True,"scenarios":out},indent=2,sort_keys=True)+"\n")
    print("FORECAST_WARNING_OVERLAY_NO_PAST_TIME_LEAK_PASS",len(out))
    for x in out:
        print("FORECAST_OVERLAY_EXAMPLE",x["forecast_id"],x["risk_level"],
            "inherited",len(x["warnings_existing_before_original_issue"]),
            "new",len(x["warnings_new_since_original_issue"]))
if __name__=="__main__":
    main()
