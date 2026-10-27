#!/usr/bin/env python3
"""V34 original ANN accuracy and active-only policy research appendix.

Uses only committed immutable V34 ANN forecasts and prior-Friday risks.
Active-only policy is EXPLORATORY after global 2026 was previously inspected;
2024–25 alone selects within active constraint, 2026 no threshold reoptimization.
No claim of truly blind 2026. Source is proxy 12:00 UTC price, not bank bid/ask.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import gold_v34_position_backtest as port
O=Path(__file__).parent/"outputs"

def check(c,s):
 if not bool(c):raise AssertionError("V34_FINANCIAL_AUDIT_"+s)
def accuracy():
 w=pd.concat([pd.read_csv(O/f"v34_weekly_ANN_ORIGINAL_shard{i}.csv") for i in range(4)],
             ignore_index=True).sort_values("target_week")
 check(w.target_week.is_unique and len(w)>=140,"WEEKLY_ORIGINS")
 m=pd.read_csv(O/"v34_monthly_MPA_ANN_ORIGINAL_2024_2026_33_month_predictions.csv")
 rows=[]
 for year in ("2024","2025","2026"):
    z=w[w.target_week.str[:4].eq(year)]
    a=m[m.month.str[:4].eq(year)]
    for endpoint in ("weekly_mean","weekly_last_quote"):
        meta={"weekly_mean":("mean_ape_pct","baseline_mean_ape_pct","mean_direction_correct"),
              "weekly_last_quote":("close_ape_pct","baseline_close_ape_pct","close_direction_correct")}
        ape,naive,direction=meta[endpoint]
        for scope,q in [("ALL",z),("EXCLUDE_UNCERTIFIED_FEB_MAR_2026_WEEKS",
                   z[~z.target_week.isin(("2026-02-23","2026-03-02"))])]:
            if year!="2026" and scope!="ALL":continue
            rows.append(dict(year=year,endpoint=endpoint,scope=scope,n=len(q),
                ANN_MAPE_pct=float(q[ape].mean()),
                naive_MAPE_pct=float(q[naive].mean()),
                ANN_direction_correct=int(q[direction].sum()),
                ANN_direction_accuracy_pct=100*float(q[direction].mean()),
                ANN_better_than_naive_MAPE=bool(q[ape].mean()<q[naive].mean()),
                original_ann_parameters_unchanged=True,
                historical_price_firstprint_certified=False))
    if len(a):
        for scope,q in [("ALL",a),("EXCLUDE_UNVERIFIED_FEB2026",
                   a[a.month.ne("2026-02")])]:
            if year!="2026" and scope!="ALL":continue
            err=(q.forecast-q.actual).abs()
            naive=(q.origin-q.actual).abs()
            rows.append(dict(year=year,endpoint="MPA_MONTHLY_AVERAGE",scope=scope,n=len(q),
               ANN_MAPE_pct=float((err/q.actual).mean()*100),
               naive_MAPE_pct=float((naive/q.actual).mean()*100),
               ANN_direction_correct=int(((q.forecast>q.origin)==(q.actual>q.origin)).sum()),
               ANN_direction_accuracy_pct=100*float(((q.forecast>q.origin)==(q.actual>q.origin)).mean()),
               ANN_better_than_naive_MAPE=bool(err.mean()<naive.mean()),
               original_ann_parameters_unchanged=True,
               historical_price_firstprint_certified=False))
 result=pd.DataFrame(rows)
 result.to_csv(O/"v34_ANN_monthly_weekly_accuracy_2024_2025_2026.csv",index=False)
 print("V34_ORIGINAL_ANN_ACCURACY\n"+result.to_string(index=False))
 return result

def active():
 w=pd.read_csv(O/"v34_weekly_monthly_risk_joint_input_ASOF.csv")
 check(len(w)>140 and (w.previous_friday_asof_date<w.target_week).all(),
       "INPUT_ASOF_PRIOR_FRIDAY_PARITY")
 ledger=pd.read_csv(O/"v34_2024_2025_META_STRATEGY_SELECTION_NO_2026.csv")
 check("objective_2024_2025" in ledger,"MISSING_LOCKED_TRAIN_FIT")
 active=ledger[(ledger.buy_count.ge(2))&(ledger.sell_count.ge(2))].copy()
 check(len(active)>4,"NO_ACTIVE_POLICY_CANDIDATES")
 rank=active.sort_values(["objective_2024_2025","trade_actions","name"],
                         ascending=[False,True,True])
 chosen=rank.iloc[0]
 policy={k:(chosen[k].item() if isinstance(chosen[k],np.generic) else chosen[k])
        for k in ("name","policy","threshold","veto","min_weeks")}
 perf,operations=port.simulate(w,policy,("2026",))
 selected_only=[x for x in operations if x["decision"] in ("AL","CIK")]
 check(len(selected_only)>1,"SELECTED_ACTIVE_POLICY_NO_TRADES")
 df=pd.DataFrame(operations)
 df["rule_name"]=policy["name"]
 df["rule_chosen_from_2024_2025_not_2026"]=True
 df["2026_new_active_constraint_hypothesis_is_exploratory"]=True
 df.to_csv(O/"v34_2026_BEST_2024_2025_ACTIVE_POLICY_WEEKLY_DECISIONS.csv",index=False)
 pd.DataFrame(selected_only).to_csv(O/"v34_2026_BEST_2024_2025_ACTIVE_POLICY_TRADES.csv",index=False)
 reference=pd.read_csv(O/"v34_2026_ANN_RISK_POSITION_NET_PNL_COMPARISON.csv")
 hold=reference[reference.policy.eq("BENCHMARK_BUY_HOLD")].iloc[0]
 cash=reference[reference.policy.eq("BENCHMARK_ALL_CASH")].iloc[0]
 result=dict(active_policy_chosen_within_2024_2025_frozen_grid=policy,
   active_policy_2024_2025_train_net_pct=float(chosen.net_return_pct),
   active_policy_2026_net_pct=float(perf["net_return_pct"]),
   buyhold_2026_net_pct=float(hold.net_return_pct),
   cash_2026_net_pct=float(cash.net_return_pct),
   active_policy_2026_terminal_100usd=float(perf["terminal_equity"]),
   active_policy_2026_max_drawdown_pct=float(perf["max_drawdown_pct"]),
   active_policy_2026_buy_count=int(perf["buy_count"]),
   active_policy_2026_sell_count=int(perf["sell_count"]),
   active_policy_2026_trades=selected_only,
   year_2026_result_not_blind_because_active_constraint_added_after_prior_2026_research=True,
   no_inference_params_changed=True,
   no_neon_mutations=True,
   not_investment_advice_or_real_bank_order=True,
   same_price_firstprint_PIT_verified=False,
   bank_spread_not_observed_beyond_frozen_0p8_side_cost=True)
 # Numeric-only CSV for comparisons.
 pd.DataFrame([{"policy":policy["name"],"return_2024_2025_train_pct":float(chosen.net_return_pct),
     "return_2026_test_pct":float(perf["net_return_pct"]),
     "buyhold_2026_return_pct":float(hold.net_return_pct),
     "terminal_100usd":float(perf["terminal_equity"]),
     "buy_count":perf["buy_count"],"sell_count":perf["sell_count"],
     "maxdd_2026_pct":float(perf["max_drawdown_pct"]),
     "exploratory_2026":True}]).to_csv(O/"v34_active_policy_research_comparison.csv",index=False)
 (O/"v34_active_policy_research_manifest.json").write_text(json.dumps(result,
               indent=2,ensure_ascii=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+"\n")
 print("V34_ACTIVE_EXPLORATORY_2026",json.dumps({k:v for k,v in result.items() if k!="active_policy_2026_trades"}))
 print("V34_ACTIVE_EXPLORATORY_TRADES\n"+pd.DataFrame(selected_only).to_string(index=False))
 return result
def run():
 accuracy();active();print("V34_ANN_ACCURACY_AND_ACTIVE_POLICY_RESEARCH_OK")
if __name__=="__main__":run()
