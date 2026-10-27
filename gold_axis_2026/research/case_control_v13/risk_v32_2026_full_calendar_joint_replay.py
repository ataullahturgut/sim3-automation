#!/usr/bin/env python3
"""V32: 2026 Jan-Sep FULL price-calendar, original V29 BASE14/CFTC21/V22
PLUS independent V31 event-time macro stress, with NO 2026 retuning.

Separate three questions which must NOT be conflated:
(1) Prior-to-price-peak legacy daily WARN (10 prior trading days);
(2) additional post-release macro WATCH (known only 35 min AFTER data);
(3) post-day future-five-session research labels, different from trades.

Historical PIT status is blocked for all scenarios. No source DB writes.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd

import risk_v29_fourmetal_price_replay as v29
import risk_v31_macro_event_layer as macro
from risk_v31_macro_event_layer import utc

O=Path(__file__).parent/"outputs"
START="2026-01-01"
END="2026-09-30"
CHECKPOINT="2026-09-21"
MODEL_FIELDS=("BASE14_original_alert_level","CFTC21_original_alert_level","effective_review")
FAMILIES={
    "JAN":"2026-01-29","MAR":"2026-03-12",
    "JUNE_FIRST":"2026-06-04","JUNE_SECOND":"2026-06-17",
    "AUG":"2026-08-25"
}
DROP_THRESHOLDS=(4,5)
COOLDOWN=5

def must(cond,msg):
    if not bool(cond):raise RuntimeError("V32_FAIL_CLOSED_"+msg)

def asbool(x):
    return str(x).strip().lower() in ("true","1")

def five_day_low(calendar,idx,h=5):
    future=calendar.iloc[idx+1:idx+h+1]
    if len(future)!=h:
        return None
    p=float(calendar.iloc[idx].price)
    return 100.*(float(future.price.min())/p-1.)

def event_state_rows():
    source=macro.events()
    frozen=macro.calibrated_2023_2024(source)
    rows=[]
    for r in source:
        if r["event_year"]!="2026" or r["release_utc"][:10]>END:continue
        release=utc(r["release_utc"])
        result=macro.assess(r,release+timedelta(minutes=macro.DELAY_MINUTES),
                            frozen[r["family"]]["q10_30m_pct"])
        must(result["asof_utc"]>=release.isoformat(),"EVENT_BEFORE_PUBLICATION")
        must(not result["live_eligible"],"INADVERTENT_LIVE_PROMOTION")
        must(result["action"]=="INFORMATIONAL_NOT_AL_SAT","AUTOMATED_SELL")
        detected=result["state"]=="EVENT_REPRICING_RESEARCH_REVIEW"
        rows.append(dict(date=release.date().isoformat(),event_id=r["event_id"],
            family=r["family"],release_utc=r["release_utc"],
            earliest_state_known_TR=result["earliest_30m_complete_TR"],
            state=result["state"],
            outside_bank=result["bank_window"]=="OUTSIDE_BANK_WINDOW",
            bank_hours_research_extreme=bool(detected and result["bank_window"]=="BANK_WINDOW"),
            any_hours_extreme=detected,
            reaction_pct=result["gold_return_30m_pct"],
            q10_2023_24=frozen[r["family"]]["q10_30m_pct"],
            macro_consensus_PIT_verified=False,real_time_5m_delivery_certified=False,
            pre_release_signal=False,source_date_not_firstprint=True,
            fixed_2023_24_quantile=True,not_AL_SAT=True))
    must(len(rows)==23,"NOT_23_2026_EVENTS")
    return pd.DataFrame(rows),frozen

def active_phases_research(merged,window=COOLDOWN):
    """Episode counts by 5 price-session cooldown, not 1 alarm = 1 crash."""
    days=merged.loc[merged.combined_attention_research].sort_values("calendar_index").copy()
    clusters=[]
    for r in days.itertuples():
        if not clusters or int(r.calendar_index)-clusters[-1]["last_idx"]>window:
            clusters.append(dict(first_date=r.date,last_date=r.date,
                first_idx=int(r.calendar_index),last_idx=int(r.calendar_index),
                days=1,any_macro_first=bool(r.macro_event_new_attention)))
        else:
            k=clusters[-1];k["last_date"]=r.date;k["last_idx"]=int(r.calendar_index)
            k["days"]+=1;k["any_macro_first"]|=bool(r.macro_event_new_attention)
    return clusters

def align(daily,event,calendar,scenario):
    cal=calendar[(calendar.date>=START)&(calendar.date<=END)].copy()
    must(len(cal)>175 and len(cal)<205 and cal.date.is_unique,"BAD_2026_CALENDAR")
    must(cal.date.is_monotonic_increasing,"UNSORTED_PRICE_CALENDAR")
    must("2026-02-27" in set(cal.date),"NO_HYPOTHETICAL_FEB27")
    most=pd.DataFrame(daily)
    must(len(most)==187 and most.origin.is_unique,"NOT_187_2026_FROZEN_MODEL_ROWS")
    must((most.origin.str[:7]<="2026-09").all(),"MODEL_DATE_OUTSIDE_SCOPE")
    must(all(x in set(cal.date) for x in most.origin),"MODEL_DATE_NOT_IN_PRICE_CALENDAR")
    must(all(x in set(cal.date) for x in event.date if x not in ("2026-04-03",)),
         "EVENT_UNEXPECTED_NONPRICE_DATE")
    if any(d not in set(cal.date) for d in event.date):
        print("V32_UNMAPPED_NONTRADING_EVENT", sorted(set(event.date)-set(cal.date)))

    # All 2026 price days are shown, including days with NO SCORED V29 models
    # and event days, avoiding a false 187 = whole year claim.
    cal["calendar_index"]=np.arange(len(cal))
    show=cal.merge(most[["origin",*MODEL_FIELDS,"effective_level",
         "BASE14_original_score","CFTC21_original_score"]].rename(columns={"origin":"date"}),
         on="date",how="left",validate="one_to_one")
    counts=event.groupby("date").agg(
        macro_events=("event_id","count"),
        macro_research_extreme=("any_hours_extreme","sum"),
        macro_research_in_bank=("bank_hours_research_extreme","sum"),
        macro_no_bars=("state",lambda x:int((x=="ABSTAIN_MISSING_5MIN_BARS").sum())),
        macro_event_detail=("event_id",lambda x:"|".join(x))).reset_index()
    show=show.merge(counts,on="date",how="left",validate="one_to_one")
    for x in ("macro_events","macro_research_extreme","macro_research_in_bank","macro_no_bars"):
        show[x]=show[x].fillna(0).astype(int)
    show["macro_event_detail"]=show.macro_event_detail.fillna("")
    show["scenario"]=scenario
    show["legacy_scored"]=show.BASE14_original_alert_level.notna()
    show["legacy_BASE14_red"]=show.BASE14_original_alert_level.eq("RED")
    show["legacy_CFTC21_red"]=show.CFTC21_original_alert_level.eq("RED")
    show["legacy_V22_attention"]=show.effective_review.apply(asbool)
    show.loc[~show.legacy_scored,"legacy_V22_attention"]=False
    show["macro_event_new_attention"]=show.macro_research_in_bank.gt(0)&~show.legacy_V22_attention
    show["combined_attention_research"]=show.legacy_V22_attention|show.macro_research_in_bank.gt(0)
    # Date-only alignment does NOT mean V22 full-day indicators were available
    # at macro alert minute; never claim same-day executable combined signal.
    show["legacy_daily_score_intraday_available"]="UNVERIFIED_DAILY_CLOSE_TIMESTAMP"
    show["v31_historical_live_signal_eligible"]=False
    show["PIT_price_certified"]=False
    show["corrected_Feb_price_source"]="REFERENCE_SENSITIVITY_NOT_CERTIFIED"
    show["any_sell_trade_executed"]=False
    risk5=[];risk4=[]
    for x in cal.itertuples():
        s=five_day_low(cal,x.calendar_index,5)
        risk5.append(s is not None and s<=-5)
        risk4.append(s is not None and s<=-4)
    show["next5_max_decline_pct"]=[
        five_day_low(cal,int(i),5) for i in show.calendar_index]
    show["next5_drop_ge4"]=risk4
    show["next5_drop_ge5"]=risk5
    show["next5_matured"]=show.next5_max_decline_pct.notna()
    return show

def summary(rows,events):
    m=[]
    evaluable=rows[rows.legacy_scored&rows.next5_matured]
    for label,col in [("BASE14_RED","legacy_BASE14_red"),
                      ("CFTC21_RED","legacy_CFTC21_red"),
                      ("V22_ATTENTION","legacy_V22_attention"),
                      ("V31_ADDITIONAL_BANK_REPRICING","macro_event_new_attention"),
                      ("V22_PLUS_V31_BANK","combined_attention_research")]:
        active=evaluable[evaluable[col]]
        m.append(dict(scenario=str(rows.scenario.iloc[0]),strategy=label,
            price_days=len(rows),legacy_scored_days=int(rows.legacy_scored.sum()),
            common_score_and_5day_label_days=len(evaluable),
            alert_days_on_common_scored_dates=len(active),
            next5_drop_ge5_alert_days=int(active.next5_drop_ge5.sum()),
            next5_NO_drop_ge5_alert_days=int((~active.next5_drop_ge5).sum()),
            next5_drop_ge4_alert_days=int(active.next5_drop_ge4.sum()),
            next5_NO_drop_ge4_alert_days=int((~active.next5_drop_ge4).sum()),
            all_alert_dates_with_matured_labels=int(rows[rows[col]&rows.next5_matured].shape[0]),
            time_accuracy_verified=False,retrospective_not_blind=True))
    return m

def peak_analysis(rows,events,scenario):
    p=[]
    for group,peak in FAMILIES.items():
        idx=rows.index[rows.date.eq(peak)]
        must(len(idx)==1,"MISSING_DECLINE_PEAK_"+group)
        i=int(idx[0])
        prior=rows.iloc[max(i-10,0):i]
        must(len(prior)==10,"PEAK_TOO_EARLY_"+group)
        legacy=prior[prior.legacy_V22_attention]
        new=prior[prior.macro_research_in_bank.gt(0)]
        combined=prior[prior.combined_attention_research]
        # Strict '< peak date' for event layer (not same-day post-peak).
        p.append(dict(scenario=scenario,economic_phase=group,
          peak_date=peak,pre_peak_price_sessions=10,
          V22_first_attention=str(legacy.date.iloc[0]) if len(legacy) else "NONE",
          V31_first_30m_bank_event=str(new.date.iloc[0]) if len(new) else "NONE",
          COMBINED_first_attention=str(combined.date.iloc[0]) if len(combined) else "NONE",
          V22_strict_prepeak_hit=bool(len(legacy)),
          V31_strict_prepeak_event=bool(len(new)),
          combined_strict_prepeak_hit=bool(len(combined)),
          V31_new_strict_prepeak_win=bool(len(combined)>0 and len(legacy)==0),
          V31_is_firstprint_PIT_approved=False,
          note="JUNE_SECOND_LEG_NOT_INDEPENDENT" if group=="JUNE_SECOND" else
               "MARCH_PRICE_REFERENCE_UNVERIFIED" if group=="MAR" else
               "TIMING_DAILY_CLOSE_NOT_CERTIFIED"))
    return p

def verify_old_unchanged(rows,old_source):
    same=rows[rows.date.isin(set(old_source.origin))]
    z=same.merge(old_source[["origin","BASE14_original_alert_level",
       "effective_review","BASE14_original_score"]],
       left_on="date",right_on="origin",suffixes=("_replayed","_frozen"),
       validate="one_to_one")
    must(len(z)==161,"OLD_2026_DAY_PARITY")
    must((z.BASE14_original_alert_level_replayed==z.BASE14_original_alert_level_frozen).all(),
         "OLD_BASE14_REASSIGNED")
    must(all(z.effective_review_replayed.astype(str)==z.effective_review_frozen.astype(str)),
         "OLD_V22_REASSIGNED")
    must(np.allclose(z.BASE14_original_score_replayed,z.BASE14_original_score_frozen,rtol=0,atol=1e-12),
         "OLD_V22_RISK_SCORE_CHANGED")

def replay():
    # Original V29 makes the same two AM/PM scenarios; live Neon untouched.
    src,cot,oldrows,panel,sha=v29.historic_evidence()
    original=pd.read_csv(O/"v22_daily_decisions.csv")
    events,thresholds=event_state_rows()
    existing=pd.read_csv(O/"v31_macro_event_research_2023_2026_108_events.csv")
    must(len(existing)==108,"CHANGED_MACRO_SOURCE")
    overview=[];days=[];peaks=[];phases=[]
    snapshots={}
    for scenario,values in v29.SOURCES.items():
        replacement,inp,scores,_=v29.alternative_rows(src,cot,values)
        must(v29.compare_frozen_scores(pd.DataFrame(v29.original.compute(oldrows)[1]),
             scores,scenario)==1572,"LEGACY_FOUR_MODEL_PARITY")
        dataframe=v29.source_panel(replacement,inp)
        legacy=v29.reconstruct_2026_triage(inp,scores,dataframe)
        must(len(legacy)==187,"REPLAY_2026_COVERAGE")
        prices=v29.complete_calendar(scenario,values)
        daily=align(legacy,events,prices,scenario)
        verify_old_unchanged(daily,original[original.year.eq(2026)])
        overview+=summary(daily,events)
        peaks+=peak_analysis(daily,events,scenario)
        episodes=active_phases_research(daily)
        phases.extend([dict(scenario=scenario,**x) for x in episodes])
        days.append(daily)
        snapshots[scenario]={
            "price_days_2026_jan_sep":int(len(daily)),
            "original_scored_days":int(daily.legacy_scored.sum()),
            "original_unscored_dates":daily.loc[~daily.legacy_scored,"date"].tolist(),
            "v31_2026_total_event_observations":int(len(events)),
            "v31_bank_hours_extreme_event_count":int(events.bank_hours_research_extreme.sum()),
            "v31_any_hours_extreme_event_count":int(events.any_hours_extreme.sum()),
            "v31_missing_5min_data_count":int(events.state.eq("ABSTAIN_MISSING_5MIN_BARS").sum()),
            "v31_extra_event_attention_days":int(daily.macro_event_new_attention.sum()),
            "v31_event_excluded_no_price_day":sorted(set(events.date)-set(daily.date)),
            "v22_old_parity_days":161,
            "future_5day_labels_available":int(daily.next5_matured.sum())}
    D=pd.concat(days,ignore_index=True)
    A=pd.DataFrame(overview)
    P=pd.DataFrame(peaks)
    E=pd.DataFrame(phases)
    events=events.copy()
    cal_dates=set(D.date)
    events["has_2026_price_day"]=events.date.isin(cal_dates)
    # Do not invent a same-date daily comparison for Good Friday or
    # other economic releases where source calendar has no gold fixing.
    D.to_csv(O/"v32_2026_all_days_base14_cftc21_v22_plus_v31_scenario.csv",index=False)
    A.to_csv(O/"v32_2026_common_denominator_alert_day_comparison.csv",index=False)
    P.to_csv(O/"v32_2026_5_peak_prepeak_early_warning_comparison.csv",index=False)
    events.to_csv(O/"v32_2026_23_event_time_observations.csv",index=False)
    E.to_csv(O/"v32_2026_combined_five_session_alarm_clusters.csv",index=False)
    manifest=dict(version="V32_2026_COMBINED_AUDIT",params_legacy_unchanged=True,
       v31_train_years="2023-2024",v31_2025_and_2026_unused_for_threshold_selection=True,
       original_baseline_parity_confirmed_161_days_each_scenario=True,
       prior_original_scores_equal_1572_each_scenario=True,
       no_neon_changes=True,no_live_alarms_sent=True,
       same_session_2026_Feb27_fourmetal_price_certified=False,
       historical_bars_firstprint_captured_asof_event=False,
       macros_prior_consensus_capture_proven=False,
       risk_event_occurrences_are_not_distinct_trading_executable_alarms=True,
       old_daily_model_score_availability_at_16_05_TR_unverified=True,
       prepeak_early_window_days=10,
       short_horizon_target="min next 5 price sessions vs origin fixing <= -4%, -5%",
       threshold_was_reoptimized_on_2026=False,
       v31_new_layer_uses_observed_30min_drop_not_pre_event_prediction=True,
       not_a_claim_of_out_of_sample_success=True,
       snapshot_by_scenario=snapshots,
       v31_event_thresholds_2023_2024=thresholds,
       five_peak_event_groups=FAMILIES,
       joint_report_status="RETROSPECTIVE_SENSITIVITY_NOT_PIT",
       macro_2026_timestamped_emissions_are_retrospective_simulation_only=True)
    (O/"v32_combined_2026_replay_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("V32_FINAL_SNAPSHOTS",json.dumps(snapshots))
    print("V32_FINAL_ALERT_COMPARE\n"+A.to_string(index=False))
    print("V32_FINAL_PREPEAK_EVENTS\n"+P.to_string(index=False))
    print("V32_2026_EVENT_TIMING\n"+events[
        ["date","event_id","state","earliest_state_known_TR",
        "bank_hours_research_extreme","has_2026_price_day"]].to_string(index=False))
    print("V32_FINAL_RUN_SUCCESS",len(D),len(events),len(P))
    return manifest

if __name__=="__main__":replay()
