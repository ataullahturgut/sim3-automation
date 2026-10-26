#!/usr/bin/env python3
"""Issuer/public evidence spot-checks, research only, no source mutation.

AM/PM benchmarks are secondary reproductions of LBMA fixes, NOT official
licensed first-print feed, and are NOT automatically interchangeable with
the StakTrakr Git snapshot time/quote definition.
CFTC schedule is the issuer's real publication calendar but DOES NOT verify
the numeric CFTC, H10, H15, or GVZ first publication vintages.
"""
from pathlib import Path
import pandas as pd, json
O=Path(__file__).parent/"outputs"

LBMA_AM_PM_EVIDENCE={
    "2026-01-29":(5501.70,5405.00),
    "2026-02-25":(5171.75,5191.55),
    "2026-02-26":(5174.75,5167.35),
    "2026-02-27":(5174.10,5222.30),
    "2026-10-16":(4181.90,4189.20),
}
LBMA_SOURCES=[
 "https://www.doma.srl/fixing-2026/",
 "https://gold.1prime.ru/amp/20260303/kotirovki-1168924.html",
 "https://www.goldpriceoz.com/historical-london-gold-fixing/",
]
CFTC_SOURCES=[
 "https://www.cftc.gov/PressRoom/PressReleases/9138-25",
 "https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm",
]
def main():
    p=pd.read_csv(O/"v23_price_calendar_RESEARCH_NOT_PIT.csv").set_index("date")
    rows=[]
    for date,(am,pm) in LBMA_AM_PM_EVIDENCE.items():
        q=p.loc[date]
        actual=float(q.price)
        is_bad=bool(q.quarantined)
        row=dict(date=date,stored_price=actual,
            secondary_LBMA_AM=am,secondary_LBMA_PM=pm,
            delta_vs_LBMA_AM=actual-am,delta_vs_LBMA_PM=actual-pm,
            aligns_exact_AM=abs(actual-am)<.005,
            aligns_exact_PM=abs(actual-pm)<.005,
            quarantined=is_bad,
            source_definition_mismatch_possible=True,
            safe_to_overwrite_original_source=False,
            original_source_firstprint_PIT_certified=False,
            label="CONFIRMED_GROSS_OUTLIER" if date=="2026-02-27"
                else "RESEARCH_FEED_DEFINITION_DIFFERS_OR_UNPROVEN",
            evidence_urls="|".join(LBMA_SOURCES))
        rows.append(row)
    audit=pd.DataFrame(rows)
    assert len(audit)==5 and audit.quarantined.sum()==1
    assert audit.set_index("date").loc["2026-01-29","aligns_exact_AM"]
    assert abs(audit.set_index("date").loc["2026-02-27","stored_price"]-3516.02)<1e-8
    assert abs(audit.set_index("date").loc["2026-02-27","secondary_LBMA_AM"]-5174.10)<.001
    assert abs(audit.set_index("date").loc["2026-02-27","secondary_LBMA_PM"]-5222.30)<.001
    assert not audit.set_index("date").loc["2026-02-26","aligns_exact_AM"]
    audit.to_csv(O/"v24_external_price_source_comparison.csv",index=False)
    cftc=pd.DataFrame([
        dict(CFTC_report_as_of="2025-09-30",official_released="2025-11-19",
             conservative_usable="2025-11-20",release_clock_NY="15:30",
             validation="2025_SHUTDOWN_OFFICIAL_DATE_CROSSCHECK",
             reference=CFTC_SOURCES[0]),
        dict(CFTC_report_as_of="2026-01-20",official_released="2026-01-23",
             conservative_usable="2026-01-24",release_clock_NY="15:30",
             validation="2026_ISSUER_SCHEDULE_DATE_ONLY",
             reference=CFTC_SOURCES[1]),
        dict(CFTC_report_as_of="2026-02-24",official_released="2026-02-27",
             conservative_usable="2026-02-28",release_clock_NY="15:30",
             validation="2026_ISSUER_SCHEDULE_DATE_ONLY",
             reference=CFTC_SOURCES[1]),
        dict(CFTC_report_as_of="2026-06-16",official_released="2026-06-22",
             conservative_usable="2026-06-23",release_clock_NY="15:30",
             validation="2026_HOLIDAY_DELAY_ISSUER_SCHEDULE_DATE_ONLY",
             reference=CFTC_SOURCES[1]),
    ])
    cftc.to_csv(O/"v24_cftc_official_schedule_spotchecks.csv",index=False)
    status=dict(
      external_gross_bad_gold_record_found=True,
      correct_LBMA_AM_2026_02_27=5174.10,correct_LBMA_PM_2026_02_27=5222.30,
      original_source_was_not_changed=True,pricing_time_definition_not_harmonized=True,
      cftc_2025_shutdown_release_reconciled_to_issuer=True,
      cftc_2026_release_calendar_spotchecked=True,
      all_CFTC_numeric_vintages_verified=False,
      all_Fed_H10_numeric_vintages_verified=False,
      all_Fed_H15_numeric_vintages_verified=False,
      all_GVZ_same_day_legal_at_decision_time_verified=False,
      all_gold_price_firstprints_verified=False,
      model_production_safe=False)
    (O/"v24_source_release_validation_status.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n")
    print("V24_PRICE_DEFINITION_RECONCILIATION")
    print(audit[["date","stored_price","secondary_LBMA_AM","secondary_LBMA_PM",
      "aligns_exact_AM","aligns_exact_PM","quarantined"]].to_string(index=False))
    print("V24_CFTC_ISSUER_SCHEDULE_SPOTCHECKS")
    print(cftc.to_string(index=False))
    print("V24_SOURCE_VINTAGE_LIMITS",json.dumps(status,ensure_ascii=False))
if __name__=="__main__":
    main()
