#!/usr/bin/env python3
"""Reproduce one illustrative month from a PRIVATELY exported NY17 daily M15 BID/ASK aggregation.

Not a trading system. Requires a user's own authorized vendor observations.
Inputs are not bundled in GitHub. This is a reference implementation of the
January 2023 research v0 method; numerical gold prices remain private.

Usage:
    python gold_adaptive_monthly_v0_replay_20261014.py private_ny17_daily.json --month 2023-01

Input JSON array rows: session, n, first_utc, first_bid, first_ask,
closing_utc, close_bid, close_ask (dates can be ISO or YYYY-MM-DD).
A full session has >=70 bars and an actually observed NY17 closing bar.
"""
import argparse
import json
import math

FEE = 0.008
PARAMETERS = {"lagged_sessions": 5, "vol_ref_sessions": 20, "vol_gate": 2.0, "fee_per_leg": FEE}

def numeric(row, key):
    v = row.get(key)
    return None if v is None or v == "" else float(v)

def eligible(row):
    return int(row["n"]) >= 70 and numeric(row, "close_bid") is not None and numeric(row, "close_ask") is not None

def dateonly(s):
    return str(s)[:10]

def replay(rows, month):
    rows = sorted([dict(r, day=dateonly(r["session"])) for r in rows], key=lambda r:r["day"])
    complete = [r for r in rows if eligible(r)]
    full_by_day = {r["day"]: i for i, r in enumerate(complete)}
    closes = [(float(r["close_bid"])+float(r["close_ask"]))/2 for r in complete]
    lrs = [None]+[math.log(closes[i]/closes[i-1]) for i in range(1,len(closes))]
    targets = [r for r in rows if r["day"].startswith(month)]
    if not targets or any(r["day"] not in full_by_day and eligible(r) for r in targets):
        raise ValueError("Month missing or malformed")
    end_day = targets[-1]["day"]
    def feature(idx):
        prior = idx-1
        if prior<20:
            return None
        a5=sum(abs(x) for x in lrs[prior-4:prior+1])/5
        a20=sum(abs(x) for x in lrs[prior-19:prior+1])/20
        return {"ret5":closes[prior]/closes[prior-5]-1, "ratio": a5/a20}
    def policy_result(policy):
        cash,units,last_bid,fees=100.0,0.0,None,0.0
        orders, sessions=[],[]
        for row in targets:
            full=eligible(row)
            f=feature(full_by_day[row["day"]]) if full else None
            if full and f is None:
                raise ValueError("20 completed past sessions missing for "+row["day"])
            if not full:
                desired="NO_NEW_ORDER"
            elif policy=="CASH": desired="CASH"
            elif policy=="GOLD": desired="GOLD"
            elif policy=="TREND5": desired="GOLD" if f["ret5"]>0 else "CASH"
            else: desired="GOLD" if f["ret5"]>0 and f["ratio"]<=2 else "CASH"
            action="HOLD"
            if full and desired=="GOLD" and units==0:
                fee=cash*FEE
                units=(cash-fee)/float(row["first_ask"])
                cash=0.0
                fees+=fee
                action="BUY"
                orders.append({"session":row["day"],"utc":row["first_utc"],"action":action,"fee":fee})
            elif full and desired=="CASH" and units>0:
                gross=units*float(row["first_bid"])
                fee=gross*FEE
                cash=gross-fee
                units=0.0
                fees+=fee
                action="SELL"
                orders.append({"session":row["day"],"utc":row["first_utc"],"action":action,"fee":fee})
            if full: last_bid=float(row["close_bid"])
            if row["day"]==end_day and units>0:
                gross=units*last_bid
                fee=gross*FEE
                cash=gross-fee
                units=0.0
                fees+=fee
                orders.append({"session":row["day"],"utc":row["closing_utc"],"action":"END_SELL","fee":fee})
            nav=cash+(units*(last_bid or 0))
            sessions.append({"session":row["day"],"valid":full,"target":desired,"action":action,
                             "prior5_pct":100*f["ret5"] if f else None,"adaptive_vol_ratio":f["ratio"] if f else None,
                             "nav_usd":nav})
        return {"policy":policy,"final_usd":cash,"fees_usd":fees,"orders":orders,"sessions":sessions}
    result=[policy_result(p) for p in ("CASH","GOLD","TREND5","RISK_TREND5")]
    return {"month":month, "parameters":PARAMETERS, "studies":result,
            "warning":"Historical vendor bid/ask and known 2023-2026 events. Not bank execution, not an unseen test."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("input_json", help="PRIVATE vendor derived daily rows, not committed")
    parser.add_argument("--month", default="2023-01")
    args=parser.parse_args()
    with open(args.input_json,encoding="utf-8") as f: data=json.load(f)
    print(json.dumps(replay(data,args.month),indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
