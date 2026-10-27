#!/usr/bin/env python3
"""V29 risk re-run of unchanged BASE14,CFTC21, V18/V21/V22 rules.

Read only, research-only alternate London AM/PM price substitution for the
CONFIRMED bad 2026-02-27 StakTrakr four-metal record.
Neither alternative is certified as same-session StakTrakr benchmark.
Keep original fail-closed quarantine baseline untouched and intact.
Do not persist patched model/source or relax production's BAD_DAY quarantine:
only change module variable inside a try/finally in a dedicated research run.
Never apply 2026 events to choose 200-tree IF hyperparameters/alert thresholds.

V22's existing rule and V18 BI are replayed using original fitted 14/21
scores, originally pre-2023 casebook, origin-time CFTC and GVZ, and existing
one-day hysteresis. Score parity on unaffected dates is mandatory.
"""
from __future__ import annotations
import copy,hashlib,json,math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest
import gold_risk_cftc_v8_fixed as original
import research as v13
import risk_v15_business_intelligence as v15
import risk_v19_2024_original_replay as v19
import risk_v23_calendar_safe_audit as v23

ROOT=Path(__file__).parent
O=ROOT/"outputs"
BAD="2026-02-27"
SOURCES={
    "AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":{"AU":5174.10,"AG":89.975,"PT":2365.0,"PD":1818.0},
    "PM_MIXED_CLOSE_REFERENCE_NOT_SAME_SERIES":{"AU":5222.30,"AG":89.975,"PT":2366.0,"PD":1793.0},
}
FAMILIES={"BASE14":list(range(14)),"CFTC21":list(range(21))}
PRICE_HEADERS=("AU","AG","PT","PD")
OLD={"AU":3516.02,"AG":62.15,"PT":1585.39,"PD":1201.26}
PEAKS=["2024-10-30","2025-04-22","2025-05-08","2025-10-17",
       "2026-01-29","2026-03-12","2026-06-04","2026-06-17","2026-08-25"]

def must(test,name):
    if not bool(test):raise AssertionError("V29_RISK_REPLAY_GATE_"+name)

def historic_evidence():
    ref,official,panel=v15.sources()
    src,cot,sourcehash=original.load(v13.I/"source.zip",v13.corrected_cftc())
    ref2=original.make_rows(src,cot)
    must(len(ref)==len(ref2),"ORIGINAL_ROW_COUNT")
    must([x["origin"] for x in ref]==[x["origin"] for x in ref2],"ORIGINAL_DATE_PARITY")
    stat,daily=original.compute(ref)
    past=pd.read_csv(O/"v15_daily_intelligence.csv")
    assert len(past)==786
    old=pd.DataFrame(daily)
    for fam in ("BASE_14","BASE_14_PLUS_CFTC_7"):
        name="BASE14" if fam=="BASE_14" else "CFTC21"
        z=old[old.family.eq(fam)].merge(past[past.model.eq(name)],
                                         on="origin",validate="one_to_one")
        must(len(z)==393,"FROZEN_MODEL_ROWS_"+name)
        must((z.alert_level_x==z.alert_level_y).all(),"FROZEN_ALERT_CHANGED_"+name)
        must(np.allclose(z.risk_score_x,z.risk_score_y,atol=1e-12,rtol=1e-12),
             "FROZEN_SCORE_NOT_REPRODUCED_"+name)
    price=next(r for r in src["prices"] if r["date"]==BAD)
    for i,k in enumerate(PRICE_HEADERS):
        must(abs(float(price["metals"][i])-OLD[k])<.001,
             "BAD_DAY_NOT_PRESENT_"+k)
    must(str(original.BAD_DAY)==BAD,"FROZEN_QUARANTINE_VALUE")
    return src,cot,ref,panel,sourcehash

def alternative_rows(src,cot,replacements):
    p=copy.deepcopy(src)
    changed=[x for x in p["prices"] if x["date"]==BAD]
    must(len(changed)==1,"EXACT_ONE_QUOTE_TO_REPLACE")
    changed[0]["metals"]=[float(replacements[k]) for k in PRICE_HEADERS]
    previous=original.BAD_DAY
    try:
        # RESEARCH-ONLY process-local bypass of known-bad-day abstention.
        # Never alter original file or deploy this temporary override.
        original.BAD_DAY="1900-01-01"
        alt=original.make_rows(p,cot)
    finally:
        original.BAD_DAY=previous
    must(original.BAD_DAY==BAD,"QUARANTINE_NOT_RESTORED")
    must(len(alt)>850,"NO_ADDITIONAL_SCOREABLE_DATES")
    result,scored=original.compute(alt)
    return p,alt,pd.DataFrame(scored),result

def compare_immutable(oldrow,newrow,scenario):
    old=pd.DataFrame(oldrow)
    prior=pd.DataFrame(newrow)
    joined=old.merge(prior,on="origin",suffixes=("_old","_new"),
                      validate="one_to_one")
    must(len(joined)==len(old),"MISSING_ORIGINAL_DATES_"+scenario)
    for q in joined.itertuples():
        must(float(q.gold_price_usd_oz_old)==float(q.gold_price_usd_oz_new),
             "INPUT_PRICE_CHANGED_OUTSIDE_WINDOW_"+q.origin)
        must(np.allclose(q.features_old,q.features_new,atol=1e-13,rtol=0),
             "INPUT_FEATURE_CHANGED_OUTSIDE_WINDOW_"+q.origin)
    return prior[~prior.origin.isin(old.origin)].copy()

def compare_frozen_scores(archive,alt,scenario):
    z=archive.merge(alt,on=["origin","family"],suffixes=("_old","_new"),
                    validate="one_to_one")
    must(len(z)==len(archive),"ORIGINAL_SCORE_DATES_MISSING_"+scenario)
    must((z.alert_level_old==z.alert_level_new).all(),"ALARM_CHANGED_UNAFFECTED_"+scenario)
    must(np.allclose(z.risk_score_old,z.risk_score_new,rtol=0,atol=1e-12),
         "RISK_SCORE_CHANGED_UNAFFECTED_"+scenario)
    must(np.allclose(z.train_threshold_red_old,z.train_threshold_red_new,
                      rtol=0,atol=1e-12),"TRAINING_THRESHOLD_CHANGED_"+scenario)
    return int(len(z))

def source_panel(p,rows):
    """2026 scenario 21 original origin features as values already stored
    in old.make_rows; historical 2010-2022 time indices from original panel.
    build_panel masks suspect 27-Feb in its extras but restores 21
    genuine scenario-inferred input columns for recovered origins.
    """
    weekly=v13.cot_archives()
    frame,_=v13.build_panel(p,rows,weekly)
    return frame

def historical_analogues(frame):
    hist=pd.read_csv(O/"v15_historical_cases_and_controls.csv")
    n=v19.FEATURES
    his=frame.loc[:"2022-12-31",n].dropna()
    med=his.median().to_numpy(float)
    iqr=np.maximum((his.quantile(.75)-his.quantile(.25)).to_numpy(float),1e-8)
    d={}
    for kind in ("PRE_DECLINE_PEAK","MATCHED_NO_DROP"):
        vectors=[]
        for _,r in hist[hist.type.eq(kind)].iterrows():
            idx=pd.Timestamp(r.date)
            if idx not in frame.index:continue
            v=frame.loc[idx,n].to_numpy(float)
            if np.isfinite(v).all():vectors.append(v)
        must(len(vectors)>15,"HIST_CASE_REFERENCE_"+kind)
        d[kind]=np.vstack(vectors)
    return med,iqr,d

def reconstruct_2026_triage(altrows,model_daily,frame):
    """Same 200-tree feature math, V15 group what-ifs, V16 case
    distances, V18 strongest paths, V21 watch, V22 P1..P7."""
    allnames=original.FEATURES
    training=[q for q in altrows if q["target_mature"]<="2025-12-31"]
    testing=[q for q in altrows if "2026-01-01"<=q["origin"]<="2026-09-21"]
    must(len(testing)>161,"RESTORED_SCORABLE_DAYS")
    xt=np.array([r["features"] for r in training],float)
    xv=np.array([r["features"] for r in testing],float)
    medhist,scalehist,examples=historical_analogues(frame)
    candidates={}
    for fam,ix in FAMILIES.items():
        X=xt[:,ix];Y=xv[:,ix]
        scaler=RobustScaler().fit(X)
        forest=IsolationForest(n_estimators=200,max_samples=min(256,len(training)),
                      contamination="auto",random_state=1701,n_jobs=1)
        forest.fit(scaler.transform(X))
        fitted=-forest.score_samples(scaler.transform(X))
        risk=-forest.score_samples(scaler.transform(Y))
        yellow,red=np.quantile(fitted,[.9,.95])
        score_from_original=model_daily[(model_daily.period.eq("2026")) &
            (model_daily.family.eq("BASE_14" if fam=="BASE14" else
                                    "BASE_14_PLUS_CFTC_7"))]
        score_from_original=score_from_original.set_index("origin")
        must(len(score_from_original)==len(testing),"EXACT_FULL_DAILY_SCORE_"+fam)
        must(np.allclose(risk,score_from_original.loc[[r["origin"] for r in testing],"risk_score"],
                         atol=1e-12,rtol=0),"V15_RISK_REPLAY_PARITY_"+fam)
        groups={}
        for group,source_ix in v15.GROUPS.items():
            local=[ix.index(k) for k in source_ix if k in ix]
            if not local:continue
            med=np.median(X,axis=0)
            shift=Y.copy();shift[:,local]=med[local]
            groups[group]=risk-(-forest.score_samples(scaler.transform(shift)))
        selected=sorted(groups,key=lambda a:0) # nonempty, rank separately for each day
        case=examples["PRE_DECLINE_PEAK"][:,ix]
        ctrl=examples["MATCHED_NO_DROP"][:,ix]
        div=scalehist[ix]
        for j,row in enumerate(testing):
            cur=xv[j,ix]
            dc=np.linalg.norm((case-cur)/div,axis=1).min()/math.sqrt(len(ix))
            dn=np.linalg.norm((ctrl-cur)/div,axis=1).min()/math.sqrt(len(ix))
            top=sorted(groups,key=lambda g:groups[g][j],reverse=True)[0]
            candidates.setdefault(row["origin"],{})[fam]=dict(
                risk_score=float(risk[j]),alert_level="RED" if risk[j]>=red else
                "YELLOW" if risk[j]>=yellow else "NORMAL",
                whatif_top=top,closer_crash=bool(dc<dn),
                threshold_red=float(red),
                score_risk_group_GVZ=(top=="GVZ"))
    series=[]
    prev=None
    decisions=[]
    for k,day in enumerate(testing):
        date=day["origin"]
        a=candidates[date]["BASE14"];b=candidates[date]["CFTC21"]
        strong_a=bool(a["alert_level"]=="RED" and
                     (a["whatif_top"]=="GVZ" or a["closer_crash"]))
        adj=bool(prev and 0<(pd.Timestamp(date)-pd.Timestamp(prev["origin"])).days<=4)
        today=100*(float(day["gold_price_usd_oz"])/float(testing[k-1]["gold_price_usd_oz"])-1) if adj else float("nan")
        increase=bool(adj and a["risk_score"]>prev["BASE14_original_score"])
        # V18 path A/B and C. YELLOW may carry only from previous V16 CONFIRMED.
        path_a=bool(a["alert_level"]=="RED" and a["whatif_top"]=="GVZ")
        path_b=bool(a["alert_level"]=="RED" and a["closer_crash"])
        path_c=bool(a["alert_level"]=="RED" and b["alert_level"]=="RED"
                    and today<0 and increase)
        carry=bool(adj and a["alert_level"]=="YELLOW"
                   and prev["V16_confirmed"] and today<0)
        strong=path_a or path_b or path_c or carry
        reason="|".join(v for cond,v in [
            (path_a,"GVZ_ANOMALY"),(path_b,"HISTORIC_CASEBOOK"),
            (path_c,"CFTC_CONFIRMED_RISK_ACCELERATION"),
            (carry,"ONE_SESSION_YELLOW_CONTINUATION")] if cond)
        # V21 frozen independent WATCH band (never replaces base RED).
        x=day["features"]
        watch=(a["alert_level"]=="NORMAL" and x[2]>=.74 and .04<=x[1]<=.06
               and x[7]>=0 and x[16]<0)
        red=a["alert_level"]=="RED"; yellow=a["alert_level"]=="YELLOW"
        p5=float(x[0])*100
        prior5=(float(testing[k-5]["features"][0])*100
                if k>=5 and testing[k-5]["origin"][:4]==date[:4]
                else float("nan"))
        accel=p5-prior5
        P1=bool(red and strong and np.isfinite(accel) and accel>1)
        P2=bool(red and strong and "CFTC_CONFIRMED_RISK_ACCELERATION" in reason)
        P3=bool(red and strong and np.isfinite(today) and today<=-1.5 and "GVZ" in reason)
        P4=bool(red and strong and x[6]>=35 and x[2]>=.55)
        core=P1 or P2 or P3 or P4
        P5=bool(red and strong and x[0]>0 and adj and
                prev["original_RED_core"] and prev["five_day_gold_pct"]>0)
        P6=bool(yellow and strong)
        P7=bool(watch)
        if core or P5:status="ACTIVE_REVIEW"
        elif P6:status="CONTINUATION_REVIEW"
        elif P7:status="FRAGILITY_WATCH"
        elif red:status="ORIGINAL_RED_REVIEW_ONLY"
        else:status="NO_ACTIONABLE_REVIEW"
        names=[v for flag,v in ((P1,"MOMENTUM_ACCELERATES"),(P2,"CFTC_CONFIRM"),
                (P3,"GVZ_SHOCK"),(P4,"EXTREME_GVZ"),(P5,"ONE_DAY_RED_MEMORY"),
                (P6,"V18_ONE_DAY_YELLOW"),(P7,"V21_NORMAL_FRAGILITY")) if flag]
        out=dict(origin=date,price=float(day["gold_price_usd_oz"]),
            BASE14_original_alert_level=a["alert_level"],BASE14_original_score=a["risk_score"],
            CFTC21_original_alert_level=b["alert_level"],CFTC21_original_score=b["risk_score"],
            previous_BI_strong=strong,original_reason=reason if reason else (
                "OTHER_ORIGINAL_RED" if red else "NO_STRONG_PATH"),
            five_day_gold_pct=p5,twenty_day_gold_pct=float(x[1])*100,
            five_day_acceleration_pp=accel,one_day_gold_pct=today,
            gvz=float(x[6]),rsi14=float(x[2]),V16_confirmed=path_a or path_b,
            original_RED_core=core,
            effective_review=bool(core or P5 or P6 or P7),
            effective_level=status,effective_reasons="|".join(names),
            active_RED_phase=bool(core or P5),yellow_carry=P6,watch=P7,
            live_enabled=False,signal_price_same_fixing_certified=False,
            no_future_labels_used=True,signal_hypothesis_nonblind=True)
        decisions.append(out)
        prev=out
    return pd.DataFrame(decisions)

def complete_calendar(scenario,replacements):
    q=pd.read_csv(O/"v23_price_calendar_RESEARCH_NOT_PIT.csv")
    assert len(q)==713
    isbad=q.date.eq(BAD)
    must(isbad.sum()==1,"CALENDAR_MISSING_BAD")
    q.loc[isbad,"price"]=replacements["AU"]
    q.loc[isbad,"quarantined"]=False
    q["research_replacement_not_pit"]=isbad
    return q

def all_price_status(prices,dates):
    mapping={}
    for date in dates:
        match=prices.index[prices.date.eq(date)]
        if len(match)!=1:continue
        i=int(match[0]);end=prices.iloc[i+1:i+11]
        if len(end)<10:status="UNKNOWN_NOT_MATURE";pct=float("nan")
        else:
            origin=float(prices.iloc[i].price)
            pct=100*(float(end.price.min())/origin-1)
            status="TRUE_DROP_5PCT" if pct<=-5 else "FALSE_DROP_5PCT"
        mapping[date]=(status,pct)
    return mapping

def frozen_2024_2025_plus_scenario(baseline_v22,scenario_2026):
    """Pre-2026 original decisions MUST not disappear from nine-event audit."""
    early=baseline_v22.loc[baseline_v22.year.le(2025),[
        "origin","BASE14_original_alert_level","effective_review"]].copy()
    cf24=pd.read_csv(O/"v19_2024_original_models.csv")
    cf24=cf24.loc[cf24.model.eq("CFTC21"),["origin","alert_level"]]
    cf25=pd.read_csv(O/"v15_daily_intelligence.csv")
    cf25=cf25.loc[cf25.model.eq("CFTC21")&
        cf25.origin.str.startswith("2025"),["origin","alert_level"]]
    cftc=pd.concat([cf24,cf25],ignore_index=True)
    must(len(cftc)==486 and cftc.origin.is_unique,"FROZEN_2024_2025_CFTC21_ROWS")
    early=early.merge(cftc.rename(columns={"alert_level":"CFTC21_original_alert_level"}),
        on="origin",validate="one_to_one",how="left")
    must(len(early)==486 and early.CFTC21_original_alert_level.notna().all(),
         "FROZEN_2024_2025_COMPLETE")
    keep=["origin","BASE14_original_alert_level",
          "CFTC21_original_alert_level","effective_review"]
    result=pd.concat([early[keep],scenario_2026[keep]],ignore_index=True)
    must(result.origin.is_unique and len(result)==486+len(scenario_2026),
         "HISTORICAL_FULL_COMPARISON")
    # Frozen 2024/25 V22 prepeak must match original V24 ledger.
    return result

def peak_research_result(decisions,calendar):
    ids={v:i for i,v in enumerate(calendar.date)}
    peaks=pd.read_csv(O/"v24_nine_event_compact_audit.csv")
    a=[]
    for r in peaks.itertuples():
        peak=str(r.price_peak);i=ids[peak]
        before=calendar.iloc[max(0,i-10):i].date.tolist()
        segment=decisions[decisions.origin.isin(before)].copy()
        c=int(len(segment))
        base=segment[segment.BASE14_original_alert_level.eq("RED")].sort_values("origin")
        cf=segment[segment.CFTC21_original_alert_level.eq("RED")].sort_values("origin")
        v22=segment[segment.effective_review.astype(bool)].sort_values("origin")
        record=dict(event_id=str(r.event_id),price_peak=peak,year=int(r.year),
          days_with_model_score=c,expected_prior10_price_sessions=len(before),
          BASE14_first_RED_prior10=(base.origin.iloc[0] if len(base) else ""),
          CFTC21_first_RED_prior10=(cf.origin.iloc[0] if len(cf) else ""),
          V22_first_review_prior10=(v22.origin.iloc[0] if len(v22) else ""),
          V22_prepeak_visible=len(v22)>0,
          V22_coverage_complete=c==len(before),
          V22_verdict=("NO_SCORABLE_DAYS" if c==0 else
             "PARTIAL_WINDOW" if c<len(before) else
             "PREPEAK_REVIEW" if len(v22) else "NO_PREPEAK_REVIEW"),
          historical_event_known_during_study=True,
          independent_source_same_price_definition_verified=False,
          numerical_PIT_certified=False)
        a.append(record)
    return pd.DataFrame(a)

def run():
    source,cot,oldrows,panel,sourcehash=historic_evidence()
    old_scores=pd.DataFrame(original.compute(oldrows)[1])
    baseline_v22=pd.read_csv(O/"v22_daily_decisions.csv")
    base_dates=set(baseline_v22.origin)
    all_recovered=[]
    all_alarms=[]
    event_rows=[]
    audited=[]
    comparisons=[]
    for scenario,alternative in SOURCES.items():
        alt_src,altrows,new_scores,_=alternative_rows(source,cot,alternative)
        recovered=compare_immutable(oldrows,altrows,scenario)
        restored=recovered[recovered.origin.str[:4].eq("2026")]
        score_match=compare_frozen_scores(old_scores,new_scores,scenario)
        # Recompute original V15/V16/V18/V21/V22 features & risk under the
        # hypothetical input, not just relabeling old risk decisions.
        frame=source_panel(alt_src,altrows)
        new_decisions=reconstruct_2026_triage(altrows,new_scores,frame)
        check=new_decisions[new_decisions.origin.isin(base_dates)].merge(
            baseline_v22[baseline_v22.year.eq(2026)],
            on="origin",suffixes=("_new","_old"),validate="one_to_one")
        must(len(check)==161,"SCOREABLE_2026_PARITY_COUNT")
        for col in ["BASE14_original_alert_level","effective_review","active_RED_phase","watch"]:
            must((check[col+"_new"].astype(str)==check[col+"_old"].astype(str)).all(),
                 "V22_UNAFFECTED_DATE_PARITY_"+scenario+"_"+col)
        must(np.allclose(check.BASE14_original_score_new,
                         check.BASE14_original_score_old,atol=1e-12,rtol=0),
             "V22_BASE14_FROZEN_SCORE_PARITY")
        calendar=complete_calendar(scenario,alternative)
        labels=all_price_status(calendar,new_decisions.origin)
        new_decisions["scenario"]=scenario
        new_decisions["next10_outcome_research_only"]=[labels[d][0] for d in new_decisions.origin]
        new_decisions["next10_min_pct_research_only"]=[labels[d][1] for d in new_decisions.origin]
        new_decisions["was_previously_unscored"]=~new_decisions.origin.isin(base_dates)
        new_decisions["research_uncertified_single_day_price"]=True
        all_alarms.extend(new_decisions.to_dict("records"))
        for f in ("BASE14_original_alert_level","CFTC21_original_alert_level"):
            q=new_decisions[f].eq("RED")
            audited.append(dict(scenario=scenario,model=f.replace("_original_alert_level",""),
                year_2026_total_scored=len(new_decisions),newly_recovered_scoreable_days=int(new_decisions.was_previously_unscored.sum()),
                total_RED=int(q.sum()),
                recovered_RED=int((q&new_decisions.was_previously_unscored).sum()),
                overlap_original_frozen_RED=int((q&~new_decisions.was_previously_unscored).sum()),
                label_true10=int((q&new_decisions.next10_outcome_research_only.eq("TRUE_DROP_5PCT")).sum()),
                label_false10=int((q&new_decisions.next10_outcome_research_only.eq("FALSE_DROP_5PCT")).sum()),
                label_unknown=int((q&new_decisions.next10_outcome_research_only.str.startswith("UNKNOWN")).sum())))
        v=new_decisions.effective_review
        audited.append(dict(scenario=scenario,model="V22_RESEARCH_REVIEW",
                year_2026_total_scored=len(new_decisions),
                newly_recovered_scoreable_days=int(new_decisions.was_previously_unscored.sum()),
                total_RED=int(v.sum()),recovered_RED=int((v&new_decisions.was_previously_unscored).sum()),
                overlap_original_frozen_RED=int((v&~new_decisions.was_previously_unscored).sum()),
                label_true10=int((v&new_decisions.next10_outcome_research_only.eq("TRUE_DROP_5PCT")).sum()),
                label_false10=int((v&new_decisions.next10_outcome_research_only.eq("FALSE_DROP_5PCT")).sum()),
                label_unknown=int((v&new_decisions.next10_outcome_research_only.str.startswith("UNKNOWN")).sum())))
        historical=frozen_2024_2025_plus_scenario(baseline_v22,new_decisions)
        e=peak_research_result(historical,calendar)
        e["scenario"]=scenario
        event_rows.extend(e.to_dict("records"))
        for _,r in restored.iterrows():
            all_recovered.append(dict(origin=r.origin,scenario=scenario,
                fourmetal_alternative_values=str(alternative),
                CFTC_source_cot_pinned=True,
                original_hardcoded_quarantine_not_deployed=True))
        comparisons.append(dict(scenario=scenario,additional_days=len(restored),
            old_model_scores_unchanged=score_match,
            V22_frozen_2026_score_rows_exactly_reproduced=len(check),
            restored_march_prepeak_days=int(new_decisions.origin.between("2026-02-26","2026-03-11").sum()),
            research_price_definition_proven=False))
    alarm=pd.DataFrame(all_alarms)
    event=pd.DataFrame(event_rows)
    score=pd.DataFrame(audited)
    origin=pd.DataFrame(all_recovered)
    alarm.to_csv(O/"v29_replayed_BASE14_CFTC21_V22_all_2026_daily.csv",index=False)
    event.to_csv(O/"v29_nine_historical_declines_event_sensitivity.csv",index=False)
    score.to_csv(O/"v29_scenario_model_alarm_2026_metrics.csv",index=False)
    origin.to_csv(O/"v29_recovered_daily_origin_flags.csv",index=False)
    status=dict(status="RESEARCH_ALT_PRICE_REPLAY_NO_LIVE_PROMOTION",
        scenario_prices=SOURCES,source_gold_bad_original=OLD,
        full_model_params_unchanged=True,
        trained_model_core="RobustScaler+IsolationForest(200) 2023-2025 train",
        old_model_scores_2025_2026_reproduced_on_overlap=True,
        V22_BI_RSI_GVZ_CFTC_triggers_rebuilt=True,
        same_session_LBMA_fixing_approved=False,source_price_PIT_certified=False,
        full_CFTC_MACRO_PIT_certified=False,original_quarantine_unchanged=True,
        no_orig_Neon_mutation=True,no_production_writes=True,
        scenarios_comparisons=comparisons)
    (O/"v29_replay_manifest.json").write_text(json.dumps(status,indent=2,ensure_ascii=False)+"\n")
    print("V29_COMPARE_PARITY",json.dumps(comparisons,ensure_ascii=False))
    print("V29_SCENARIO_MODEL_METRICS\n",score.to_string(index=False))
    print("V29_MARCH_2026_DECISIONS\n",alarm[(alarm.origin.between("2026-02-23","2026-03-13"))][
        ["scenario","origin","price","BASE14_original_alert_level",
         "CFTC21_original_alert_level","effective_level","original_reason",
         "was_previously_unscored"]].to_string(index=False))
    print("V29_NINE_EVENTS\n",event.to_string(index=False))
    print("V29_REPLAY_OK",len(alarm))
if __name__=="__main__":
    run()
