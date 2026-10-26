#!/usr/bin/env python3
"""V24 independent-event timeline evaluation from verified V23 price calendar.

Pure post-hoc evaluation. No model refit, Neon writes, or 2026 threshold selection.
Nine event proxies: 2024-Nov predeclared V20, 2025/2026 original V13 event ledger.
Lead signal STRICTLY before price peak, not on peak or on onset.
Missing model-score rows (March 2026) are NOT scored as misses.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

O=Path(__file__).parent/"outputs"
def _gate(ok,name):
    if not bool(ok): raise AssertionError("V24_EVENT_GATE_"+name)

def load():
    px=pd.read_csv(O/"v23_price_calendar_RESEARCH_NOT_PIT.csv").sort_values("date").reset_index(drop=True)
    d=pd.read_csv(O/"v23_calendar_safe_daily.csv").sort_values("origin").reset_index(drop=True)
    ledger=pd.read_csv(O/"event_alarm_timeline.csv")
    ledger=ledger.loc[ledger.model.eq("BASE14")].copy()
    legacy=pd.read_csv(O/"v20_physical_peak_definitions.csv")
    e24=legacy.loc[legacy.event.eq("2024_11")].iloc[0]
    new=pd.DataFrame([dict(period=2024,model="BASE14",event_id="2024_11",
        peak=e24.price_peak,onset_proxy=e24.V13_onset_proxy,trough="2024-11-14",
        source="V20_2024_PREDECLARED")])
    ledger=ledger[["period","model","event_id","peak","onset_proxy","trough"]].copy()
    ledger["source"]="V13_PREDECLARED_EVENT_LEDGER"
    ledger=pd.concat([new,ledger],ignore_index=True).sort_values("peak").reset_index(drop=True)
    _gate(len(ledger)==9 and ledger.event_id.is_unique,"NINE_PREDECLARED_EVENTS")
    _gate(len(px)==713 and len(d)==647,"FROZEN_INPUT_COUNTS")
    _gate(px.date.is_unique and d.origin.is_unique,"DATE_UNIQUE")
    _gate(px.loc[px.quarantined,"date"].tolist()==["2026-02-27"],"QUARANTINE_FROZEN")
    return px,d,ledger

def first_where(prices, peak, threshold, until):
    post=prices.iloc[peak+1:until+1]
    hit=post.loc[100*(post.price.astype(float)/float(prices.iloc[peak].price)-1)<=-threshold]
    return str(hit.date.iloc[0]) if len(hit) else ""

def time_window(d, dates):
    return d.loc[d.origin.isin(dates)].sort_values("origin")

def first_relevant(w,field):
    selected=w.loc[w[field].astype(bool)]
    return selected.iloc[0] if len(selected) else None

def event_timeline(px,d,ledger):
    idx={date:i for i,date in enumerate(px.date)}
    records=[]
    for _,e in ledger.iterrows():
        name=str(e.event_id)
        peak=str(e.peak); onset=str(e.onset_proxy); trough=str(e.trough)
        _gate(peak in idx and onset in idx and trough in idx,"EVENT_DATE_MISSING_"+name)
        i,j,k=[idx[v] for v in [peak,onset,trough]]
        _gate(i<j<=k,"EVENT_ORDER_"+name)
        _gate(not px.iloc[i:k+1].quarantined.any(),"EVENT_PRICE_QUARANTINED_"+name)
        pre10=px.iloc[max(0,i-10):i].date.tolist()
        pre5=px.iloc[max(0,i-5):i].date.tolist()
        including=px.iloc[max(0,i-4):i+1].date.tolist()
        scorepre10=time_window(d,pre10)
        scorepre5=time_window(d,pre5)
        scoreincl=time_window(d,including)
        _gate(len(scorepre10)<=10 and len(scorepre5)<=5,"VALID_PREWINDOW")
        first10=first_relevant(scorepre10,"effective_review")
        first5=first_relevant(scorepre5,"effective_review")
        first_incl=first_relevant(scoreincl,"effective_review")
        orig10=scorepre10.loc[scorepre10.BASE14_original_alert_level.eq("RED")]
        orig5=scorepre5.loc[scorepre5.BASE14_original_alert_level.eq("RED")]
        watch10=scorepre10.loc[scorepre10.watch.astype(bool)]
        active10=scorepre10.loc[scorepre10.active_RED_phase.astype(bool)]
        price_peak=float(px.iloc[i].price)
        trough_price=float(px.iloc[k].price)
        signal=first10
        valid10= len(scorepre10)==len(pre10)
        valid5= len(scorepre5)==len(pre5)
        # Scores are at EOD. Only signals strictly earlier than the peak can
        # count as having lead. On-peak attention is a different field.
        if signal is not None:
            lead=i-idx[str(signal.origin)]
            advance=100*(price_peak/float(signal.price)-1)
        else:
            lead=np.nan
            advance=np.nan
        timeline=px.iloc[i:k+1].copy()
        depth=100*(trough_price/price_peak-1)
        lower=timeline.loc[~timeline.quarantined]
        lowest=lower.loc[lower.price.astype(float).idxmin()]
        records.append(dict(event_id=name,year=int(str(e.period)),price_source=str(e.source),
            price_peak=peak,peak_price=price_peak,original_v13_onset_proxy=onset,
            first_1pct_drawdown_close=first_where(px,i,1,k),
            first_2pct_drawdown_close=first_where(px,i,2,k),
            first_3pct_drawdown_close=first_where(px,i,3,k),
            price_trough=trough,trough_price=trough_price,
            peak_to_proxy_sessions=j-i,peak_to_trough_sessions=k-i,
            peak_to_trough_pct=depth,
            lowest_close_within_event_date=str(lowest.date),
            lowest_close_within_event_pct=100*(float(lowest.price)/price_peak-1),
            prior10_price_sessions=len(pre10),prior10_scoreable_sessions=len(scorepre10),
            prior5_price_sessions=len(pre5),prior5_scoreable_sessions=len(scorepre5),
            all_last10_prepeak_scores_present=valid10,
            all_last5_prepeak_scores_present=valid5,
            BASE14_first_red_prior10=str(orig10.origin.iloc[0]) if len(orig10) else "",
            BASE14_first_red_prior5=str(orig5.origin.iloc[0]) if len(orig5) else "",
            V22_first_any_prior10=str(first10.origin) if first10 is not None else "",
            V22_first_any_prior5=str(first5.origin) if first5 is not None else "",
            V22_first_any_before_or_on_peak=str(first_incl.origin) if first_incl is not None else "",
            V22_first_any_prior10_status=str(first10.effective_level) if first10 is not None else "",
            V22_first_ACTIVE_RED_prior10=str(active10.origin.iloc[0]) if len(active10) else "",
            V22_first_WATCH_prior10=str(watch10.origin.iloc[0]) if len(watch10) else "",
            V22_signal_to_peak_sessions=lead,
            gold_advance_signal_to_peak_pct=advance,
            has_verified_prepeak_review=first10 is not None,
            has_verified_prepeak_active_red=len(active10)>0,
            only_on_peak_or_unalerted=first10 is None and first_incl is not None,
            score_data_gap_prevents_verdict=not valid10,
            verdict=("NOT_EVALUABLE_NO_MODEL_SCORES" if len(scorepre10)==0
                     else "PARTIAL_COVERAGE" if not valid10
                     else "EARLY_PREPEAK_REVIEW" if first10 is not None
                     else "NO_PREPEAK_REVIEW"),
            event_dates_preselected_from_historical_price=True,
            decisions_built_with_future_data=False,
            true_intraday_onset_verified=False,
            numerical_macro_firstprint_PIT_verified=False))
    out=pd.DataFrame(records)
    _gate((out.price_peak<out.original_v13_onset_proxy).all(),"PEAK_PRIOR_TO_PROXY")
    _gate(out.loc[out.event_id=="2026_002","verdict"].iloc[0]=="NOT_EVALUABLE_NO_MODEL_SCORES","MARCH_UNSCORABLE")
    _gate(out.loc[out.event_id=="2024_11","V22_first_any_prior10"].isna().all()
          or out.loc[out.event_id=="2024_11","V22_first_any_prior10"].iloc[0]!="2024-10-30",
          "OCTOBER_ONPEAK_NOT_PREPEAK")
    _gate(out.loc[out.event_id=="2026_003","price_peak"].iloc[0]=="2026-06-04",
          "JUNE_LOCAL_PEAK_NOT_APRIL_GLOBAL")
    out.to_csv(O/"v24_nine_event_peak_onset_trough.csv",index=False)
    return out

def research_summary(result):
    rows=[]
    for year,g in result.groupby("year"):
        rows.append(dict(year=int(year),events=len(g),
          strict_early_signal=int(g.verdict.eq("EARLY_PREPEAK_REVIEW").sum()),
          partial_windows=int(g.verdict.eq("PARTIAL_COVERAGE").sum()),
          completely_unscorable=int(g.verdict.eq("NOT_EVALUABLE_NO_MODEL_SCORES").sum()),
          complete_no_early=int(g.verdict.eq("NO_PREPEAK_REVIEW").sum()),
          true_peak_to_trough_range_pct_min=float(g.peak_to_trough_pct.min())))
    m=pd.DataFrame(rows)
    m.to_csv(O/"v24_event_year_quality.csv",index=False)
    return m

def family_timeline(e):
    """Economic families are predeclared, not optimized to flatter alarms.

    April and May 2025 share a macro decline family; the two June 2026
    legs likewise share one. Credit ONLY the first component's STRICTLY
    prepeak signal. June 05 signal for June 17 is not a successful forecast
    of the FIRST June selloff. Unknown March is never called a miss.
    """
    names={
      "2024_11":"2024_NOV",
      "2025_001":"2025_APR_MAY","2025_002":"2025_APR_MAY",
      "2025_003":"2025_OCT",
      "2026_001":"2026_JAN",
      "2026_002":"2026_MAR",
      "2026_003":"2026_JUNE","2026_004":"2026_JUNE",
      "2026_005":"2026_AUG"
    }
    tmp=e.copy()
    tmp["economic_family"]=tmp.event_id.map(names)
    _gate(tmp.economic_family.notna().all(),"ALL_EVENTS_ASSIGNED_TO_FAMILY")
    rows=[]
    for family,g in tmp.groupby("economic_family",sort=True):
        g=g.sort_values("price_peak")
        first=g.iloc[0]
        records=dict(economic_family=family,year=int(first.year),
            component_events="|".join(g.event_id.astype(str)),
            first_component_peak=str(first.price_peak),
            first_component_onset=str(first.original_v13_onset_proxy),
            component_count=len(g),
            first_component_prior10_scoreable=int(first.prior10_scoreable_sessions),
            first_component_first_v22_attention=str(first.V22_first_any_prior10)
                      if pd.notna(first.V22_first_any_prior10) else "",
            first_component_verdict=str(first.verdict),
            family_verdict=(
              "UNKNOWN_NO_MODEL_COVERAGE"
              if first.verdict in ("NOT_EVALUABLE_NO_MODEL_SCORES","PARTIAL_COVERAGE")
              else "EARLY" if first.verdict=="EARLY_PREPEAK_REVIEW"
              else "MISSED_STRICT_PREPEAK"),
            economic_family_merging_is_research_judgement=True,
            blind_validation_2026=False)
        rows.append(records)
    result=pd.DataFrame(rows)
    _gate(len(result)==7,"SEVEN_ECONOMIC_FAMILIES")
    _gate(result.family_verdict.eq("EARLY").sum()==4,"FOUR_EARLY_FAMILIES")
    _gate(result.family_verdict.eq("MISSED_STRICT_PREPEAK").sum()==2,"TWO_MISSED_FAMILIES")
    _gate(result.family_verdict.eq("UNKNOWN_NO_MODEL_COVERAGE").sum()==1,"ONE_UNKNOWN_FAMILY")
    result.to_csv(O/"v24_seven_economic_families.csv",index=False)
    return result

def main():
    px,d,ledger=load()
    e=event_timeline(px,d,ledger)
    summary=research_summary(e)
    families=family_timeline(e)
    caveats=dict(
       model_retrained=False,production_changed=False,neon_modified=False,
       prices_firstprint_PIT_certified=False,macro_CFTC_numeric_firstprint_certified=False,
       V22_hypotheses_previously_saw_2024_to_2026_events=True,
       no_intraday_claim=True,complete_price_calendar_rows=len(px),
       total_decision_rows=len(d),event_count=len(e),
       is_observational_historical_hindsight=True,
       price_definition_mixed_vs_LBMA_AM_PM_not_validated=True,
       known_bad_2026_02_27_retained_and_quarantined=True,
       march2026_unscorable_never_count_as_model_miss=True,
       misleading_2026_april_peak_association_to_june_onset_replaced_by_june_local_event=True,
       thresholds_for_first_drawdown_peak_1pct_2pct_3pct_are_audit_only=True)
    (O/"v24_event_audit_manifest.json").write_text(json.dumps(caveats,ensure_ascii=False,indent=2)+"\n")
    print("V24_EVENT_TIMELINE")
    print(e[["event_id","price_peak","V22_first_any_prior10","V22_first_any_prior5",
      "V22_first_any_before_or_on_peak","original_v13_onset_proxy",
      "first_1pct_drawdown_close","price_trough","peak_to_trough_pct",
      "V22_signal_to_peak_sessions","gold_advance_signal_to_peak_pct",
      "prior10_scoreable_sessions","verdict"]].to_string(index=False))
    print("V24_EVENT_YEAR_SUMMARY")
    print(summary.to_string(index=False))
    print("V24_INDEPENDENT_FAMILY_SUMMARY")
    print(families.to_string(index=False))
    print("V24_RESEARCH_CAVEATS",json.dumps(caveats,ensure_ascii=False))
if __name__=="__main__":main()
