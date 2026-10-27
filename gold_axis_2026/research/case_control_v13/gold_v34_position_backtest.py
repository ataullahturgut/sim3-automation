#!/usr/bin/env python3
"""V34 frozen-ANN gold AL/TUT/CIK decision system.

Learn meta-policy on 2024–2025 ONLY, 2026 separate stress; 0.8% buy
and 0.8% sell costs, flat/gold binary no leverage/shorting. Trades execute
at Monday StakTrakr 12:00 UTC reference, NOT actual bank bid-ask/trade.
Weekly ANN forecast is previous Friday end-of-week prior to Monday.
Monthly ANN forecast is previous-month origin (no later monthly knowledge).
Risk veto is as of previous Friday V22 daily, never trade using Monday's
end-of-day V22 score.
"""
from __future__ import annotations
import csv,json,math
from pathlib import Path
import numpy as np
import pandas as pd
import gold_v34_ann_replay as ann

O=Path(__file__).parent/"outputs"
BUY=SELL=.008
START_CAPITAL=100.
POLICIES=("HOLD","WEEKLY_ANN","MONTHLY_ANN","ANN_CONSENSUS","ANN_EITHER","RISK_ONLY")
THRESHOLDS=(0.,.005,.01)
RISK_GATES=("NONE","V22_ATTENTION")
HOLDS=(1,3)

def need(x,msg):
    if not bool(x):raise AssertionError("V34_PORTFOLIO_GUARD_"+msg)
def flag(x):return str(x).lower() in ("true","1")
def candidates():
    out=[dict(name="HOLD",policy="HOLD",threshold=0.,veto="NONE",min_weeks=1)]
    for policy in POLICIES[1:]:
      for cutoff in THRESHOLDS:
       for veto in RISK_GATES:
        for hold in HOLDS:
         out.append(dict(name=f"{policy}|{cutoff:.4f}|{veto}|{hold}",
                    policy=policy,threshold=cutoff,veto=veto,min_weeks=hold))
    return out

def prepare():
    shards=[pd.read_csv(O/f"v34_weekly_ANN_ORIGINAL_shard{i}.csv") for i in range(4)]
    w=pd.concat(shards,ignore_index=True).sort_values("target_week")
    need(len(w)==w.target_week.nunique() and len(w)>140,"WEEKLY_SHARD_REJOIN")
    need(w.target_week.min()>="2024-01-01" and w.target_week.max()=="2026-10-19",
         "WEEKLY_TARGET_DATE_RANGE")
    need((w.training_last_week<w.target_week).all(),"WEEKLY_FIT_CONTAINS_TARGET")
    need((w.origin_week<w.target_week).all(),"WEEKLY_LATE_ORIGIN")
    monthly=pd.read_csv(O/"v34_monthly_MPA_ANN_ORIGINAL_2024_2026_33_month_predictions.csv")
    need(len(monthly)==33 and monthly.month.is_unique,"MONTHLY_33")
    need((monthly.forecast_pre_target_month==True).all(),"MONTHLY_TARGET_VISIBLE")
    need(monthly.model.eq("MPA_ANN_ORIGINAL").all(),"MONTHLY_NEW_PARAMETERS_DISALLOWED")
    monthly["monthly_pred_pct"]=monthly.forecast/monthly.origin-1.
    w["month"]=w.target_week.str[:7]
    w=w.merge(monthly[["month","monthly_pred_pct"]],on="month",how="left",validate="many_to_one")
    w["weekly_pred_pct"]=w.forecast_mean_xau/w.origin_mean_xau-1.
    w["weekly_close_pred_pct"]=w.forecast_close_xau/w.origin_close_xau-1.
    w["execution_reference_price"]=w.apply(lambda r: 
        float(json.loads(r.weekly_reconstructed_inputs)["opens"][0])
        if "weekly_reconstructed_inputs" in w else float("nan"),axis=1)
    # Weekly ANN original row does not carry first-day open: use weekly
    # source snapshot, which is source-period reference, NOT a bank fill.
    source=json.loads((O/"v34_weekly_ann_input_2010_2026_reconstructed_sensitivity.json").read_text())
    dic={s["week_monday"]:s for s in source["week_summaries"]}
    w["execution_reference_price"]=[float(dic[t]["opens"][0]) for t in w.target_week]
    w["week_end_reference_price"]=[float(dic[t]["closes"][0]) for t in w.target_week]
    w["execution_reference_date"]=[dic[t]["first_observation"] for t in w.target_week]
    w["week_last_observed_date"]=[dic[t]["last_observation"] for t in w.target_week]
    w["previous_friday_asof_date"]=[dic[origin]["last_observation"] for origin in w.origin_week]
    need((w.previous_friday_asof_date<w.target_week).all(),"RISK_SIGNAL_IN_SAME_TARGET_WEEK")
    before=pd.read_csv(O/"v22_daily_decisions.csv")
    before=before[before.origin.str[:4].isin(("2024","2025"))]
    latest=pd.read_csv(O/"v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv")
    latest=latest[latest.scenario.eq("PM_MIXED_CLOSE_REFERENCE_NOT_SAME_SERIES")]
    older=before[["origin","BASE14_original_alert_level","effective_review"]].rename(columns={"origin":"date"})
    newer=latest[["date","BASE14_original_alert_level","model_v22_review"]].rename(columns={"model_v22_review":"effective_review"})
    risk=pd.concat([older,newer],ignore_index=True)
    risk=risk[risk.date.le("2026-10-23")].drop_duplicates("date").sort_values("date")
    need(risk.date.is_unique and len(risk)>620,"PREVIOUS_MODEL_RISK_SOURCE")
    risk["effective_review"]=risk.effective_review.map(flag)
    w=w.merge(risk.rename(columns={"date":"previous_friday_asof_date",
         "BASE14_original_alert_level":"prior_BASE14_level",
         "effective_review":"prior_V22_review"}),on="previous_friday_asof_date",
         how="left",validate="many_to_one")
    # Friday calendars sometimes close for holidays: use last daily score
    # STRICTLY BEFORE the target week, not next-day ffill.
    unmatched=w.prior_BASE14_level.isna()
    for idx in w.index[unmatched]:
        r=risk[risk.date.le(w.at[idx,"previous_friday_asof_date"])]
        if len(r):
            w.at[idx,"prior_BASE14_level"]=r.iloc[-1].BASE14_original_alert_level
            w.at[idx,"prior_V22_review"]=bool(r.iloc[-1].effective_review)
    missing_risk=w[w.prior_BASE14_level.isna()|w.prior_V22_review.isna()]
    # First model week Jan 2024 uses a 2023-12 risk origin outside this
    # frozen 2024+ V22 archive.  Do not invent it or fill from 2024.
    need(len(missing_risk)<=2 and missing_risk.target_week.str.startswith("2024").all(),
         "MISSING_ASOF_RISK_IN_2025_OR_2026")
    if len(missing_risk):
        print("V34_EXCLUDE_UNOBSERVED_PRIOR_RISK_WEEK",missing_risk.target_week.tolist(),flush=True)
        w=w[~w.index.isin(missing_risk.index)].copy()
    need(w.prior_BASE14_level.notna().all(),"MISSING_ASOF_RISK_FRIDAY")
    need(w.prior_V22_review.notna().all(),"MISSING_PRIOR_V22")
    w["prior_V22_review"]=w.prior_V22_review.map(flag)
    w["date"]=w.target_week
    w["exec_date_UTC_noon_reference"]=w.execution_reference_date+"T12:00:00Z"
    w["exec_time_TR"]="15:00_STAKTRAKR_REFERENCE_NOT_BANK_QUOTE"
    w["source_price_first_print_PIT_certified"]=False
    w["monthly_gap_is_ABSTAIN"]=w.monthly_pred_pct.isna()
    need(w[w.date.str[:4].isin(("2024","2025"))].monthly_pred_pct.notna().all(),
         "MISSING_LEARNING_ANN_INPUTS")
    need(w[w.date.str.startswith("2026")].shape[0]>=40,"2026_TOO_FEW_WEEKS")
    return w

def signal(row,c):
    mode=c["policy"]
    if mode=="HOLD":return 1,"BENCHMARK_HOLD"
    if mode in ("MONTHLY_ANN","ANN_CONSENSUS","ANN_EITHER") and pd.isna(row.monthly_pred_pct):
        return None,"MISSING_MONTHLY_ANN_NO_NEW_TRADE"
    a=row.weekly_pred_pct>c["threshold"]
    m=not pd.isna(row.monthly_pred_pct) and row.monthly_pred_pct>0.
    if mode=="WEEKLY_ANN":target=a
    elif mode=="MONTHLY_ANN":target=m
    elif mode=="ANN_CONSENSUS":target=a and m
    elif mode=="ANN_EITHER":target=a or m
    elif mode=="RISK_ONLY":target=True
    else:raise RuntimeError("UNKNOWN_POLICY")
    if c["veto"]=="V22_ATTENTION" and bool(row.prior_V22_review):
        target=False
    return int(target),"MODEL_RULE"

def simulate(w,c,scope):
    df=w[w.date.str[:4].isin(scope)].sort_values("date")
    # No future 2026 endpoint may decide 2024-2025 meta rule.
    if "2026" not in scope:
        df=df[df.week_last_observed_date.le("2025-12-31")]
    need(df.date.is_unique and len(df)>=38,"PORTFOLIO_SAMPLE_EMPTY")
    if "2026" not in scope:
        need(df.week_last_observed_date.max()<"2026-01-01",
             "TRAIN_EVALUATION_LOOKED_AT_2026_PRICES")
    need(df.exec_date_UTC_noon_reference.notna().all(),"MISSING_REFERENCE_EXEC_TIME")
    cash=START_CAPITAL;units=0.;position=0; held_weeks=0;actions=[];equity=[]
    initial=float(df.execution_reference_price.iloc[0])
    trades=0;buy_n=0;sell_n=0
    for i,row in enumerate(df.itertuples()):
        price=float(row.execution_reference_price)
        need(price>0 and math.isfinite(price),"NONPOSITIVE_TRADE_REFERENCE")
        tgt,why=signal(row._asdict(),c) if False else signal(row,c)
        if tgt is None:target=position;why="ABSTAIN_MISSING_MONTHLY"
        else:target=int(tgt)
        action="TUT" if position else "BEKLE"
        if target==0 and position==1:
            if held_weeks>=c["min_weeks"] or i==len(df)-1:
                cash=units*price*(1-SELL);units=0.;position=0
                trades+=1;sell_n+=1;held_weeks=0;action="CIK"
            else:
                action="TUT_MIN_HOLD"
        elif target==1 and position==0:
            units=cash*(1-BUY)/price;cash=0.;position=1
            trades+=1;buy_n+=1;held_weeks=0;action="AL"
        if position:held_weeks+=1
        wealth=cash+units*price*(1-SELL) # exit fee for comparable net realizable equity
        equity.append(wealth)
        actions.append(dict(execution_date=row.execution_reference_date,
           week_monday=row.date,decision=action,desired_position=target,
           actual_position=position,execution_reference_usd_oz=price,
           weekly_ann_forecast_pct=100*row.weekly_pred_pct,
           monthly_ann_forecast_pct=(100*row.monthly_pred_pct
               if pd.notna(row.monthly_pred_pct) else None),
           prior_BASE14=row.prior_BASE14_level,
           prior_V22=bool(row.prior_V22_review),
           signal_reason=why,bank_price_observed=False,
           research_not_real_order=True,
           net_liquidation_value_usd=wealth,
           price_firstprint_PIT_verified=False))
    # Final liquidation is marked at latest observed final-Friday 12:00Z source
    # after the last trade opportunity (Monday 15:00 TR), with sell fee.
    final_reference_price=float(df.week_end_reference_price.iloc[-1])
    final=cash+units*final_reference_price*(1-SELL)
    equity.append(final)
    drawdown=0.;high=START_CAPITAL
    for eq in equity:
        high=max(high,eq);drawdown=max(drawdown,(high-eq)/high)
    return dict(policy=c["name"],terminal_equity=final,net_return_pct=100*(final/START_CAPITAL-1),
         max_drawdown_pct=100*drawdown,buy_count=buy_n,sell_count=sell_n,
         trade_actions=trades,evaluated_weeks=len(df),
         start_price=initial,last_marked_price=final_reference_price,
         fees_buy_pct=0.8,fees_sell_pct=0.8,
         missing_2026_monthly_ANN_weeks=int(df.monthly_gap_is_ABSTAIN.sum())),actions

def buy_hold(w,scope):
    c=dict(name="BENCHMARK_BUY_HOLD",policy="HOLD",threshold=0.,veto="NONE",min_weeks=1)
    a,trades=simulate(w,c,scope)
    a["policy"]="BENCHMARK_BUY_HOLD"
    return a,trades

def optimise(w):
    train=w[w.date.str[:4].isin(("2024","2025"))]
    need(len(train[train.week_last_observed_date.ge("2026-01-01")])<=1,
         "MORE_THAN_ONE_WEEKS_CROSSES_TRAIN_YEAR")
    benchmark,_=buy_hold(w,("2024","2025"))
    scores=[]
    for c in candidates():
        perf,_=simulate(w,c,("2024","2025"))
        # Complexity and drawdown penalty frozen BEFORE testing 2026.
        objective=(perf["net_return_pct"]-.25*perf["max_drawdown_pct"]
                    -.05*perf["trade_actions"])
        scores.append({**perf,**c,"objective_2024_2025":objective})
    fit=pd.DataFrame(scores).sort_values(["objective_2024_2025","trade_actions","policy"],
             ascending=[False,True,True])
    chosen=fit.iloc[0]
    cfg={k:chosen[k] for k in ("name","policy","threshold","veto","min_weeks")}
    need(cfg["policy"] in POLICIES,"UNKNOWN_TRAIN_WINNER")
    return cfg,fit,benchmark

def run():
    w=prepare()
    w.to_csv(O/"v34_weekly_monthly_risk_joint_input_ASOF.csv",index=False)
    chosen,leader,train_hold=optimise(w)
    leader.to_csv(O/"v34_2024_2025_META_STRATEGY_SELECTION_NO_2026.csv",index=False)
    cfg=dict(chosen)
    strategy,acts=simulate(w,cfg,("2026",))
    hold,holdacts=buy_hold(w,("2026",))
    cash=dict(policy="BENCHMARK_ALL_CASH",terminal_equity=100.,net_return_pct=0.,
        max_drawdown_pct=0.,buy_count=0,sell_count=0,trade_actions=0,
        evaluated_weeks=int(len(w[w.date.str.startswith("2026")])))
    only_weekly=dict(name="WEEKLY_ANN_NO_VETO",policy="WEEKLY_ANN",threshold=0.,veto="NONE",min_weeks=1)
    weekly_perf,_=simulate(w,only_weekly,("2026",))
    combined_default=dict(name="CONSENSUS_PLUS_V22",policy="ANN_CONSENSUS",
                       threshold=0.,veto="V22_ATTENTION",min_weeks=1)
    combined_perf,_=simulate(w,combined_default,("2026",))
    row=pd.DataFrame([strategy,hold,cash,weekly_perf,combined_perf])
    row["trained_META_only_2024_2025"]=True
    row["2026_policy_selected_after_viewing_2026"]=False
    row["firstprint_price_and_trading_PIT_certified"]=False
    row.to_csv(O/"v34_2026_ANN_RISK_POSITION_NET_PNL_COMPARISON.csv",index=False)
    pd.DataFrame(acts).to_csv(O/"v34_2026_SELECTED_AL_TUT_CIK_EXECUTIONS.csv",index=False)
    portfolio=dict(version="GOLD_V34_ANN_RISK_POSITION",
       meta_train_2024_2025_chosen=cfg,
       frozen_selection_score=float(leader.iloc[0].objective_2024_2025),
       train_hold_reference=train_hold,
       year_2026_strategy_net_return_pct=float(strategy["net_return_pct"]),
       year_2026_buyhold_net_return_pct=float(hold["net_return_pct"]),
       excess_vs_buyhold_pct_points=float(strategy["net_return_pct"]-hold["net_return_pct"]),
       no_2026_meta_parameter_tuning=True,
       monthly_ANN="MPA_ANN_ORIGINAL_UNTUNED_V27_V28",
       weekly_ANN="ORIGINAL_WEEKLY_H1_MLP8_TANH_ALPHA1_V1",
       alarm_V22="FROZEN_PRIOR_FRIDAY_ONLY",
       year_2026_02_27_approx_price_fixing_certified=False,
       weekly_firstprint_price_PIT_certified=False,
       macro_firstprint_signal_PIT_certified=False,
       trade_execution_is_bank_bid_ask_certified=False,
       buy_fee_pct=0.8,sell_fee_pct=0.8,
       NOT_LIVE_TRADING=True,NEON_UNCHANGED=True,
       Oct2026_monthly_ANN_GPR_available=False,
       missing_2026_10_monthly_cannot_generate_fallback_sell=True)
    (O/"v34_frozen_meta_position_result_manifest.json").write_text(
        json.dumps(portfolio,ensure_ascii=False,indent=2)+"\n")
    print("V34_SELECTED_POLICY_TRAIN_2024_2025",json.dumps(cfg))
    print("V34_TOP_10_2024_2025_FIT\n"+leader.head(10).to_string(index=False))
    print("V34_2026_NET_PROFITS\n"+row.to_string(index=False))
    print("V34_2026_ACTIONS\n"+pd.DataFrame(acts)[["execution_date","decision",
        "execution_reference_usd_oz","weekly_ann_forecast_pct",
        "monthly_ann_forecast_pct","prior_V22","net_liquidation_value_usd"]].to_string(index=False))
    print("V34_ORIGINAL_ANN_ALARMS_POSITION_COMPLETE")
    return portfolio
if __name__=="__main__":run()
