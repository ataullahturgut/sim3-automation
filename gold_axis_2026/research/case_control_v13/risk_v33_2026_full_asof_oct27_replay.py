#!/usr/bin/env python3
"""V33 complete available 2026 chronological risk results through 27 Oct 2026.

Read-only: original BASE14 (14), CFTC21 (21), V22 (seven rules), V31 events.
Identical old 200-tree model parameters. Critical fix: score origin even when
NEXT FIVE prices have NOT YET HAPPENED; outcome is UNMATURED, never FALSE.
Original family model code is loaded verbatim via inspect in an isolated
namespace with ONLY eval range, label availability and as-of macro data gates
extended. It is not edited or deployed. Explicit old 187/187 score parity.
Latest price from SAME upstream lbruton/StakTrakr repo October 23 frozen SHA;
October 26/27 prices, 2026 October NFP/CPI historical prior-vintage missing.
"""
from __future__ import annotations
import copy
import inspect
import json
from pathlib import Path
import pandas as pd
import numpy as np
import risk_v29_fourmetal_price_replay as v29
import risk_v31_macro_event_layer as v31

O=Path(__file__).parent/"outputs"
END="2026-10-27"
LAST_SOURCE_PRICE="2026-10-23"
OLD_END="2026-09-21"
SOURCE_SHA="9933d45e4fc185e7cefe8ec56740b3974ec8d4a2"
SCENARIOS=v29.SOURCES

def gate(test,msg):
    if not bool(test):raise AssertionError("V33_FULL_2026_GATE_"+msg)

def patched(fn, replacements,namespace):
    code=inspect.getsource(fn)
    for a,b in replacements:
        gate(code.count(a)==1,"ORIGINAL_PATCH_EXPECTS_ONE_EXACT_OCCURRENCE_"+a[:20])
        code=code.replace(a,b)
    env=dict(namespace)
    exec(compile(code,"<runtime-research-only-scoring-no-original-file-write>","exec"),env)
    return env[fn.__name__]

def source_and_inputs():
    raw,cot,oldrows,panel,h=v29.historic_evidence()
    original=copy.deepcopy(raw)
    extra=pd.concat([pd.read_csv(O/"v33_oct01_16_frozen_2026_four_metals_weekday_20261023_snapshot.csv"),
                     pd.read_csv(O/"v33_staktrakr_4metals_2026_10_19_to_10_23_FIXED_COMMIT.csv")],
                     ignore_index=True)
    gate(len(extra)==68,"OCT_17_DATES_X_FOUR_METALS")
    gate(set(extra.metal)=={"AU","AG","PT","PD"},"FOUR_METAL_COMPLETE")
    gate(extra.groupby("date").metal.nunique().eq(4).all(),"PRICE_MISSING_ONE_METAL")
    gate(extra.date.nunique()==17 and extra.date.max()==LAST_SOURCE_PRICE,
         "PRICE_OCTOBER_HORIZON_OR_COUNT")
    gate(pd.to_datetime(extra.date).dt.dayofweek.le(4).all(),"WEEKEND_VALUES_NOT_TRADING_SESSIONS")
    old_dates={x["date"] for x in original["prices"]}
    gate(max(old_dates)=="2026-09-30","OLD_SOURCE_PRICE_HORIZON_CHANGED")
    gate(not set(extra.date)&old_dates,"OLD_RESEARCH_SOURCE_OVERLAP_NOT_ZERO")
    pv=extra.pivot(index="date",columns="metal",values="price_usd_oz")
    for dt,r in pv.iterrows():
        original["prices"].append({"date":dt,"metals":[float(r[m]) for m in ("AU","AG","PT","PD")]})
    original["prices"].sort(key=lambda x:x["date"])
    gate(len({x["date"] for x in original["prices"]})==len(original["prices"]),
         "PRICE_DUPLICATION")
    gate(original["prices"][-1]["date"]==LAST_SOURCE_PRICE,"PRICE_END_WRONG")
    q=pd.read_csv(O/"v33_oct2026_gvz_h15_h10_release_aware_neon_select.csv")
    expected={"GVZ_CBOE":"gvz","DGS10_FRB_H15":"DGS10_FRB_H15",
              "DTWEXBGS_FRB_H10":"DTWEXBGS_FRB_H10"}
    available={}
    for x in q.itertuples():
        gate(x.series_id in expected,"UNKNOWN_MACRO_SERIES")
        key=x.date
        target=original["gvz"] if x.series_id=="GVZ_CBOE" else original["macro"][x.series_id]
        if key in target:
            gate(abs(float(target[key])-float(x.value))<1e-7,
                 "MACRO_OVERLAP_PRICE_REVISION_"+x.series_id+"_"+key)
        else:
            target[key]=float(x.value)
        available[(x.series_id,key)]=str(x.available_as_of)[:10]
    gate(max(original["macro"]["DGS10_FRB_H15"])>="2026-10-19","H15_NO_EXTENSION")
    gate(max(original["macro"]["DTWEXBGS_FRB_H10"])>="2026-10-16","H10_NO_EXTENSION")
    gate(max(original["gvz"])>="2026-10-20","GVZ_NO_EXTENSION")
    gate(cot["GC"][-1]["available"]=="2026-10-27","CFTC_ASOF_CHANGED")
    return raw,original,cot,available

def research_origins(source,cot,release_lookup):
    # The algorithm's 21 features (and training eligibility) remain exactly
    # verbatim. Replace only freeze date and future LABEL requirements,
    # and enforce actual Neon retrieval available_as_of on extra H10/H15.
    repl=[
      ("for i in range(260,len(days)-5):","for i in range(260,len(days)):"),
      ("if not '2023-01-01'<=d<='2026-09-21':continue",
       "if not '2023-01-01'<=d<='2026-10-27':continue"),
      ("valid_u=[k for k in udays if h10_is_available(k,d)]",
       "valid_u=[k for k in udays if h10_is_available(k,d) and extra_asof.get(('DTWEXBGS_FRB_H10',k),'1900-01-01')<=d]"),
      ("valid_r=[k for k in rdays if (date.fromisoformat(k)+timedelta(days=1)).isoformat()<=d]",
       "valid_r=[k for k in rdays if (date.fromisoformat(k)+timedelta(days=1)).isoformat()<=d and extra_asof.get(('DGS10_FRB_H15',k),'1900-01-01')<=d]"),
      ("next_day=px[i+1,0]/px[i,0]-1",
       "next_day=px[i+1,0]/px[i,0]-1 if i+1<len(days) else float('nan')"),
      ("m5=float(np.min(px[i+1:i+6,0]/px[i,0]-1))",
       "m5=float(np.min(px[i+1:i+6,0]/px[i,0]-1)) if i+5<len(days) else float('nan')"),
      ("'first_target':days[i+1],",
       "'first_target':days[i+1] if i+1<len(days) else 'UNMATURED',"),
      ("'target_mature':days[i+5],",
       "'target_mature':days[i+5] if i+5<len(days) else '9999-12-31',"),
      ("'y_next5_abs5':bool(np.max(abs(px[i+1:i+6,0]/px[i,0]-1))>=.05)",
       "'y_next5_abs5':(bool(np.max(abs(px[i+1:i+6,0]/px[i,0]-1))>=.05) if i+5<len(days) else None)")
    ]
    fn=patched(v29.original.make_rows,repl,{**vars(v29.original),"extra_asof":release_lookup,
                                              "BAD_DAY":"1900-01-01"})
    rows=fn(source,cot)
    gate(len(rows)>850,"RAW_ORIGINAL_FEATURE_COUNT")
    score=[r for r in rows if r["origin"]>="2026-01-01"]
    gate(len(score)>=200,"FAILED_TO_SCORE_OCT")
    gate(max(r["origin"] for r in score)==LAST_SOURCE_PRICE,"NOT_SCORED_LAST_SOURCE_PRICE")
    return rows

def historical_forest_scores(rows):
    src=v29.original.compute
    scorer=patched(src,[("('2026','2025-12-31','2026-01-01','2026-09-21')",
                        "('2026','2025-12-31','2026-01-01','2026-10-27')")],
                   vars(v29.original))
    return scorer(rows)[1]

def research_V22_triage(rows,model_daily,frame):
    fn=patched(v29.reconstruct_2026_triage,
      [('testing=[q for q in altrows if "2026-01-01"<=q["origin"]<="2026-09-21"]',
        'testing=[q for q in altrows if "2026-01-01"<=q["origin"]<="2026-10-27"]')],
      vars(v29))
    return fn(rows,model_daily,frame)

def verify_legacy_parity(new,old,scenario):
    z=new.merge(old,on="origin",validate="one_to_one",suffixes=("_latest","_old"))
    gate(len(z)==187,"OLD_187_DATE_MODEL_PARITY_"+scenario)
    gate((z.BASE14_original_alert_level_latest==z.BASE14_original_alert_level_old).all(),
         "BASE14_ALARM_CHANGED_"+scenario)
    gate((z.CFTC21_original_alert_level_latest==z.CFTC21_original_alert_level_old).all(),
         "CFTC21_ALARM_CHANGED_"+scenario)
    gate((z.effective_review_latest.astype(str)==z.effective_review_old.astype(str)).all(),
         "V22_ALARM_CHANGED_"+scenario)
    gate(np.allclose(z.BASE14_original_score_latest,z.BASE14_original_score_old,
               rtol=0,atol=1e-12),"BASE14_SCORE_CHANGED_"+scenario)
    gate(np.allclose(z.CFTC21_original_score_latest,z.CFTC21_original_score_old,
               rtol=0,atol=1e-12),"CFTC21_SCORE_CHANGED_"+scenario)
    return len(z)

def gold_calendar(src):
    z=pd.DataFrame([{"date":x["date"],"price":x["metals"][0]} for x in src["prices"]])
    z=z[z.date.between("2026-01-01",LAST_SOURCE_PRICE)].copy()
    gate(z.date.is_unique,"GOLD_PRICE_DATE_DUP")
    gate(z.date.is_monotonic_increasing,"GOLD_PRICE_UNSORTED")
    return z

def last5_label_at_price_day(cal,index):
    next5=cal.iloc[index+1:index+6]
    if len(next5)<5:return None,None,None,None
    m=100*(float(next5.price.min())/float(cal.iloc[index].price)-1.)
    return m,m<=-4.,m<=-5.,str(next5.date.iloc[-1])

def daily_calendar(records,source,events,scenario):
    # Market weekdays Jan1-Oct27; unavailable October26/27 explicit rows.
    expected=pd.bdate_range("2026-01-01",END)
    market=gold_calendar(source)
    z=pd.DataFrame({"date":expected.strftime("%Y-%m-%d")})
    z=z.merge(market,on="date",how="left",validate="one_to_one")
    model=records.copy().rename(columns={"origin":"date"})
    z=z.merge(model[["date","BASE14_original_alert_level",
        "CFTC21_original_alert_level","BASE14_original_score",
        "CFTC21_original_score","effective_review","effective_level",
        "original_reason"]],on="date",how="left",validate="one_to_one")
    z["has_same_source_gold"]=z.price.notna()
    z["has_legacy_model_score"]=z.BASE14_original_score.notna()
    z["date_not_yet_available"]=z.date.gt(LAST_SOURCE_PRICE)
    z["model_v22_review"]=z.effective_review.fillna(False).astype(bool)
    z["model_BASE14_RED"]=z.BASE14_original_alert_level.eq("RED")
    z["model_CFTC21_RED"]=z.CFTC21_original_alert_level.eq("RED")
    labels={r.date:last5_label_at_price_day(market,i)
          for i,r in enumerate(market.itertuples())}
    z["five_day_min_pct_research"]=[labels.get(d,(None,None,None,None))[0] for d in z.date]
    z["next5_drop4_AUDIT_ONLY"]=[labels.get(d,(None,None,None,None))[1] for d in z.date]
    z["next5_drop5_AUDIT_ONLY"]=[labels.get(d,(None,None,None,None))[2] for d in z.date]
    z["next5_label_last_observed_date"]=[labels.get(d,(None,None,None,None))[3] for d in z.date]
    z["five_day_label_status"]=np.where(z.next5_label_last_observed_date.notna(),
             "MATURED_RESEARCH","UNMATURED_OR_PRICE_NOT_FOUND")
    z["model_data_status"]=np.where(~z.has_same_source_gold,"PRICE_NOT_FOUND",
           np.where(~z.has_legacy_model_score,"FEATURES_OR_CFTC_NOT_FOUND","RESEARCH_SCORED"))
    event=events.copy();event["date"]=event.release_utc.str[:10]
    num=event.groupby("date").agg(macro_events=("event_id","count"),
       macro_reaction_bank=("bank_hours_research_extreme","sum"),
       macro_reaction_all=("any_hours_extreme","sum"),
       macro_events_missing=("state",lambda x:int(x.eq("ABSTAIN_MISSING_5MIN_BARS").sum())),
       macro_event_ids=("event_id",lambda x:"|".join(x))).reset_index()
    z=z.merge(num,on="date",how="left",validate="one_to_one")
    for k in ("macro_events","macro_reaction_bank","macro_reaction_all","macro_events_missing"):
        z[k]=z[k].fillna(0).astype(int)
    z["macro_event_ids"]=z.macro_event_ids.fillna("")
    z["V31_event_coverage"]="EVENT_SOURCE_ENDS_2026_09_11" # 2026 October is unavailable, not zero verified!
    z.loc[z.date.le("2026-09-11"),"V31_event_coverage"]="KNOWN_23_EVENTS_RESEARCH_ONLY"
    z["combined_research_review"]=z.model_v22_review|z.macro_reaction_bank.gt(0)
    z["additional_V31_review"]=z.macro_reaction_bank.gt(0)&~z.model_v22_review
    z["scenario"]=scenario
    z["same_session_fourmetal_price_PIT_certified"]=False
    z["signal_time_intraday_certified"]=False
    z["Oct26_Oct27_unobserved_not_assumed_to_be_normal"]=True
    z["original_params_changed"]=False
    return z

def stats_by_month(d):
    m=[]
    for (scenario,month),g in d.groupby(["scenario",d.date.str[:7]]):
        valid=g[g.has_legacy_model_score & g.five_day_label_status.eq("MATURED_RESEARCH")]
        for label,col in (("BASE14","model_BASE14_RED"),
                          ("CFTC21","model_CFTC21_RED"),
                          ("V22","model_v22_review"),
                          ("V22_PLUS_V31","combined_research_review")):
            x=valid[valid[col]]
            m.append(dict(scenario=scenario,month=month,model=label,
                expected_weekday_rows=len(g),has_price_days=int(g.has_same_source_gold.sum()),
                score_days=int(g.has_legacy_model_score.sum()),
                scored_and_matured_label_days=len(valid),alert_days=int(g[col].sum()),
                evaluated_alert_days=len(x),
                next5_drop5_true_alarm_days=int(x.next5_drop5_AUDIT_ONLY.fillna(False).sum()),
                next5_drop5_no_alarm_outcome_days=int(x.next5_drop5_AUDIT_ONLY.eq(False).sum()),
                newly_added_V31_days=int(g.additional_V31_review.sum()),
                missing_price_days=int((~g.has_same_source_gold).sum()),
                five_day_immature_score_days=int((g.has_legacy_model_score&
                     g.five_day_label_status.ne("MATURED_RESEARCH")).sum()),
                price_full_firstprint_certified=False,
                numerical_2026_history_is_blind=False))
    result=pd.DataFrame(m)
    gate((result.next5_drop5_true_alarm_days+result.next5_drop5_no_alarm_outcome_days==result.evaluated_alert_days).all(),"NEGATIVE_OR_WRONG_FALSE_ALERT_COUNTS")
    return result

def run():
    raw,src,cot,extra_asof=source_and_inputs()
    baseline=pd.read_csv(O/"v22_daily_decisions.csv")
    events,_=__import__("risk_v32_2026_full_calendar_joint_replay").event_state_rows()
    all_days=[]
    checks=[]
    # Fail-closed: no live use and two explicit price hypotheses for 27-Feb.
    for scenario,prices in SCENARIOS.items():
        x=copy.deepcopy(src)
        affected=[v for v in x["prices"] if v["date"]=="2026-02-27"]
        gate(len(affected)==1,"FEB27_INVALID_SOURCE_DAY_MISSING")
        affected[0]["metals"]=[prices[k] for k in ("AU","AG","PT","PD")]
        rows=research_origins(x,cot,extra_asof)
        scores=pd.DataFrame(historical_forest_scores(rows))
        frame=v29.source_panel(x,rows)
        v22=research_V22_triage(rows,scores,frame)
        oldsrc,oldrows,oldscores,_=v29.alternative_rows(raw,cot,prices)
        oldframe=v29.source_panel(oldsrc,oldrows)
        original_v22=v29.reconstruct_2026_triage(oldrows,oldscores,oldframe)
        parity=verify_legacy_parity(v22,original_v22,scenario)
        from_base=v22[v22.origin.isin(baseline.loc[baseline.year.eq(2026),"origin"])]
        gate(len(from_base)==161,"PRIOR_FROZEN_161_V22_MISSING")
        cal=daily_calendar(v22,x,events,scenario)
        gate(int(cal.has_legacy_model_score.sum())>187,"EXTENDED_2026_SCORES_NOT_ADDED")
        gate(len(cal)>=210,"MISSING_ALL_YEAR_WEEKDAY_SLOTS")
        checks.append(dict(scenario=scenario,unchanged_prior_origins=parity,
              full_weekdays=len(cal),price_days=int(cal.has_same_source_gold.sum()),
              scored_days=int(cal.has_legacy_model_score.sum()),
              last_price_date=cal.loc[cal.has_same_source_gold,"date"].max(),
              last_model_score=cal.loc[cal.has_legacy_model_score,"date"].max(),
              max_matured_target=cal.loc[cal.five_day_label_status.eq("MATURED_RESEARCH"),"date"].max(),
              score_unmatured_count=int((cal.has_legacy_model_score&
                  cal.five_day_label_status.ne("MATURED_RESEARCH")).sum()),
              last5_model_rows=cal.loc[cal.has_legacy_model_score].tail(5)[
                  ["date","model_BASE14_RED","model_CFTC21_RED","model_v22_review"]].to_dict("records")))
        all_days.append(cal)
    d=pd.concat(all_days,ignore_index=True)
    m=stats_by_month(d)
    overall=m.groupby(["scenario","model"],as_index=False).agg(
       score_days=("score_days","sum"),alert_days=("alert_days","sum"),
       evaluated_alert_days=("evaluated_alert_days","sum"),
       next5_drop5_true_alarm_days=("next5_drop5_true_alarm_days","sum"),
       next5_drop5_no_alarm_outcome_days=("next5_drop5_no_alarm_outcome_days","sum"),
       V31_extra_days=("newly_added_V31_days","sum"),
       price_days_with_records=("has_price_days","sum"))
    d.to_csv(O/"v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv",index=False)
    m.to_csv(O/"v33_2026_jan_oct27_MONTHLY_all_models_and_outcomes.csv",index=False)
    overall.to_csv(O/"v33_2026_jan_oct27_SUMMARY_all_models.csv",index=False)
    gate(m.month.nunique()==10,"NOT_TEN_2026_MONTHS")
    manifest={"study":"V33_FULL_AS_AVAILABLE_2026_10_27",
       "data_end":LAST_SOURCE_PRICE,"requested_end":END,
       "original_model_params_unchanged":True,"original_frozen_187_output_parity":True,
       "source_price_2026_10_26_27_NOT_FOUND":True,
       "Oct_2026_NFP_CPI_MACRO_RELEASE_PRECONSENSUS_NOT_FOUND":True,
       "Oct_2026_V31_event_results_unavailable_not_assumed_no_signal":True,
       "2026_02_27_price_scenario_same_definiton_not_certified":True,
       "no_production_writes":True,"no_neon_modification":True,
       "new_model_scoring_does_not_require_five_future_trading_sessions":True,
       "missing_five_day_labels_abstain_not_false_alarm":True,
       "candidate_score_timing_PIT_certified":False,
       "snapshot_git_new_2026":SOURCE_SHA,
       "asof_macro_inserted_available_asof_enforced":True,
       "CFTC_10_20_report_not_available_until_2026_10_27":True,
       "checks":checks}
    (O/"v33_full_2026_asof_audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("V33_FULL_COVERAGE",json.dumps(checks))
    print("V33_MONTHLY_2026\n"+m.to_string(index=False))
    print("V33_ALL_2026_SUMMARY\n"+overall.to_string(index=False))
    print("V33_FINAL_2026_DATES\n"+d[d.date.ge("2026-10-13")][[
        "scenario","date","price","model_data_status","BASE14_original_alert_level",
        "CFTC21_original_alert_level","effective_level","five_day_label_status",
        "five_day_min_pct_research","V31_event_coverage"]].to_string(index=False))
    print("V33_2026_REPORT_PASS",len(d),len(m))
    return manifest
if __name__=="__main__":
    run()
