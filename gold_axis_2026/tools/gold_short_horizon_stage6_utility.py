import os,io,json,hashlib,zipfile,math
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
STAGE5_ART=11177455544
READINESS_ART=11166972412
OUT=Path(os.environ.get("OUT_DIR","stage6_utility_out"))
OUT.mkdir(parents=True,exist_ok=True)

PRIMARY_COST=0.0020
COSTS=[0.0,0.0020,0.0050]
RULES=["U1_RET_ONLY","U2_MEDIAN_CONSENSUS","U3_PROB_TILT","U4_FULL_RISK"]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage6"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    n=[x for x in z.namelist() if x.endswith(suffix)]
    if len(n)!=1: raise RuntimeError((suffix,n))
    return pd.read_csv(io.BytesIO(z.read(n[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def perf(logr, dates, positions=None):
    r=np.asarray(logr,float)
    dates=pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    wealth=np.exp(np.cumsum(r))
    terminal=float(wealth[-1]) if len(wealth) else 1.0
    total=terminal-1.0
    span=max((dates.iloc[-1]-dates.iloc[0]).days/365.25,1/365.25) if len(dates)>1 else 1/365.25
    cagr=terminal**(1/span)-1.0
    peak=np.maximum.accumulate(wealth)
    dd=wealth/peak-1.0
    maxdd=float(dd.min()) if len(dd) else 0.0
    mu=float(np.mean(r))*252.0
    sd=float(np.std(r,ddof=0))*math.sqrt(252.0)
    sharpe=mu/sd if sd>1e-12 else None
    downside=np.minimum(r,0.0)
    ddev=float(np.sqrt(np.mean(downside**2))*math.sqrt(252.0))
    sortino=mu/ddev if ddev>1e-12 else None
    return {
        "terminal_wealth":terminal,"total_return":total,"cagr":float(cagr),
        "max_drawdown":maxdd,"sharpe":sharpe,"sortino":sortino,
        "mean_daily_log_return":float(np.mean(r)),
        "daily_log_vol":float(np.std(r,ddof=0)),
        "exposure":float(np.mean(positions)) if positions is not None else None
    }

def utility(row,rule):
    hvol=float(row["sigma20"])*math.sqrt(3.0)
    ret=float(row["ret_hat"]); q50=float(row["q50"]); q10=float(row["q10"]); p=float(row["p_up"])
    d=max(0.0,-q10)
    if rule=="U1_RET_ONLY":
        return ret
    if rule=="U2_MEDIAN_CONSENSUS":
        return 0.5*ret+0.5*q50
    if rule=="U3_PROB_TILT":
        return 0.5*ret+0.5*q50+0.5*(p-0.5)*hvol
    if rule=="U4_FULL_RISK":
        return 0.5*ret+0.5*q50+0.5*(p-0.5)*hvol-0.5*d
    raise KeyError(rule)

def simulate(rule, cost, fc, panel, first_idx, last_idx):
    # Interval return ending at row j is panel.gold_r1[j], representing j-1 -> j.
    pos=np.zeros(last_idx-first_idx,dtype=float)  # intervals ending first_idx+1..last_idx
    costs=np.zeros_like(pos)
    trades=[]
    forecast_map=fc.set_index("row_index")
    i=first_idx
    while i<=last_idx-3:
        if i not in forecast_map.index:
            i+=1; continue
        row=forecast_map.loc[i]
        u=utility(row,rule)
        if u>cost:
            # long over intervals i->i+1, i+1->i+2, i+2->i+3
            for j in range(i+1,i+4):
                pos[j-(first_idx+1)]=1.0
            costs[(i+1)-(first_idx+1)] += cost
            gross_log=float(panel.loc[i+3,"gold_r1"]+panel.loc[i+2,"gold_r1"]+panel.loc[i+1,"gold_r1"])
            # verify against frozen H3 realized return
            frozen=float(row["y_return"])
            if abs(gross_log-frozen)>1e-9:
                raise RuntimeError(f"H3 mismatch row {i}: {gross_log} vs {frozen}")
            net_log=gross_log-cost
            trades.append({
                "rule":rule,"cost":cost,"entry_row":int(i),"exit_row":int(i+3),
                "entry_date":str(panel.loc[i,"date"].date()),"exit_date":str(panel.loc[i+3,"date"].date()),
                "utility":float(u),"gross_log_return":gross_log,"net_log_return":net_log,
                "net_simple_return":float(np.expm1(net_log)),
                "win":bool(net_log>0),"vol_bucket":row["vol_bucket"],
                "p_up":float(row["p_up"]),"ret_hat":float(row["ret_hat"]),
                "q10":float(row["q10"]),"q50":float(row["q50"]),"q90":float(row["q90"])
            })
            i+=3
        else:
            i+=1
    interval_rows=np.arange(first_idx+1,last_idx+1)
    gold=np.array([float(panel.loc[j,"gold_r1"]) for j in interval_rows])
    strat=pos*gold-costs
    dates=[panel.loc[j,"date"] for j in interval_rows]
    eq=pd.DataFrame({
        "date":pd.to_datetime(dates),"row_index":interval_rows,
        "position":pos,"gold_log_return":gold,"cost_log":costs,
        "strategy_log_return":strat
    })
    eq["wealth"]=np.exp(eq["strategy_log_return"].cumsum())
    return eq,pd.DataFrame(trades)

def yearly_metrics(eq):
    rows=[]
    for yr,z in eq.groupby(eq["date"].dt.year):
        p=perf(z["strategy_log_return"],z["date"],z["position"])
        rows.append({"year":int(yr),**p})
    return pd.DataFrame(rows)

def trade_stats(tr):
    if len(tr)==0:
        return {"trades":0,"win_rate":None,"avg_trade_return":None,"median_trade_return":None,"worst_trade":None}
    return {
        "trades":int(len(tr)),
        "win_rate":float(tr["win"].mean()),
        "avg_trade_return":float(tr["net_simple_return"].mean()),
        "median_trade_return":float(tr["net_simple_return"].median()),
        "worst_trade":float(tr["net_simple_return"].min())
    }

def benchmark_curves(panel,first_idx,last_idx,cost):
    interval_rows=np.arange(first_idx+1,last_idx+1)
    dates=pd.to_datetime([panel.loc[j,"date"] for j in interval_rows])
    gold=np.array([float(panel.loc[j,"gold_r1"]) for j in interval_rows])

    cash=pd.DataFrame({"date":dates,"position":0.0,"strategy_log_return":np.zeros(len(gold))})
    # Buy and hold: one round-trip allowance charged once at start.
    bh=gold.copy(); bh[0]-=cost
    buy=pd.DataFrame({"date":dates,"position":1.0,"strategy_log_return":bh})

    # Always-long H3 roll: continuous exposure, cost every three intervals.
    roll=gold.copy()
    for k in range(0,len(roll),3):
        roll[k]-=cost
    h3=pd.DataFrame({"date":dates,"position":1.0,"strategy_log_return":roll})
    return {"CASH":cash,"BUY_AND_HOLD":buy,"ALWAYS_LONG_H3_ROLL":h3}

def main():
    z5=get_zip(STAGE5_ART)
    fc=read_csv(z5,"stage5_reconciled_forecasts.csv")
    fc["origin_date"]=pd.to_datetime(fc["origin_date"])
    fc["signal_date"]=pd.to_datetime(fc["signal_date"])

    zr=get_zip(READINESS_ART)
    panel=read_csv(zr,"short_horizon_readiness_panel.csv")
    panel["date"]=pd.to_datetime(panel["date"])
    panel["signal_date"]=pd.to_datetime(panel["signal_date"])
    panel=panel.reset_index(drop=True)

    first_idx=int(fc["row_index"].min())
    last_idx=int(fc["row_index"].max())
    # Keep economic simulation strictly inside DEV observation boundary.
    fc=fc[(fc["row_index"]>=first_idx)&(fc["row_index"]<=last_idx)].copy()

    bench=benchmark_curves(panel,first_idx,last_idx,PRIMARY_COST)
    bench_rows=[]
    for name,eq in bench.items():
        pp=perf(eq["strategy_log_return"],eq["date"],eq["position"])
        bench_rows.append({"benchmark":name,**pp})
    bdf=pd.DataFrame(bench_rows)
    bdf.to_csv(OUT/"stage6_benchmarks.csv",index=False)
    bh=bdf[bdf.benchmark=="BUY_AND_HOLD"].iloc[0]

    allmetrics=[]; allyears=[]; alltrades=[]; allcurves=[]; sensitivity=[]
    primary_rule_data={}

    for cost in COSTS:
        for rule in RULES:
            eq,tr=simulate(rule,cost,fc,panel,first_idx,last_idx)
            pp=perf(eq["strategy_log_return"],eq["date"],eq["position"])
            ts=trade_stats(tr)
            yr=yearly_metrics(eq)
            positive_years=int((yr["total_return"]>0).sum())
            row={"rule":rule,"cost":cost,**pp,**ts,"positive_years":positive_years}
            sensitivity.append(row)
            if abs(cost-PRIMARY_COST)<1e-12:
                allmetrics.append(row)
                yr["rule"]=rule; yr["cost"]=cost
                allyears.append(yr)
                tr["rule"]=rule; tr["cost"]=cost
                alltrades.append(tr)
                eq["rule"]=rule; eq["cost"]=cost
                allcurves.append(eq)
                primary_rule_data[rule]=(eq,tr,yr,row)

    m=pd.DataFrame(allmetrics)
    y=pd.concat(allyears,ignore_index=True)
    trades=pd.concat(alltrades,ignore_index=True) if alltrades else pd.DataFrame()
    curves=pd.concat(allcurves,ignore_index=True)
    sens=pd.DataFrame(sensitivity)

    # Primary tactical gate.
    m["tactical_pass"]=(
        (m["trades"]>=20) &
        (m["cagr"]>0) &
        (m["max_drawdown"]>=float(bh["max_drawdown"])) &
        (m["sortino"]>float(bh["sortino"])) &
        (m["positive_years"]>=2)
    )
    m["strong_pass"]=(
        m["tactical_pass"] &
        (m["cagr"]>=float(bh["cagr"])) &
        (m["max_drawdown"]>=float(bh["max_drawdown"]))
    )

    passing=m[m.tactical_pass].copy()
    if len(passing):
        best_cagr=float(passing.cagr.max())
        near=passing[passing.cagr>=best_cagr-0.005].copy()
        rank={r:i for i,r in enumerate(RULES)}
        near["simp"]=near["rule"].map(rank)
        if len(near)>1:
            sel=near.sort_values(["sortino","simp"],ascending=[False,True]).iloc[0]
        else:
            sel=near.iloc[0]
        champion=str(sel["rule"]); status="TACTICAL_PASS"
    else:
        champion=None; status="NO_TACTICAL_PASS"

    # Volatility trade summary
    vrows=[]
    if len(trades):
        for (rule,vb),z in trades.groupby(["rule","vol_bucket"]):
            vrows.append({
                "rule":rule,"vol_bucket":vb,"trades":len(z),
                "win_rate":float(z.win.mean()),
                "avg_trade_return":float(z.net_simple_return.mean()),
                "median_trade_return":float(z.net_simple_return.median()),
                "worst_trade":float(z.net_simple_return.min())
            })
    vdf=pd.DataFrame(vrows)

    m.to_csv(OUT/"stage6_candidate_metrics_20bp.csv",index=False)
    y.to_csv(OUT/"stage6_year_metrics_20bp.csv",index=False)
    trades.to_csv(OUT/"stage6_trade_ledger_20bp.csv",index=False)
    curves.to_csv(OUT/"stage6_equity_curves_20bp.csv",index=False)
    sens.to_csv(OUT/"stage6_cost_sensitivity.csv",index=False)
    vdf.to_csv(OUT/"stage6_volatility_trade_summary.csv",index=False)

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6 Tactical Allocation / Utility Result","",
        f"**Status:** **{status}**","",
        f"**Champion:** **{champion if champion else 'NONE'}**","",
        "## Benchmarks at 20 bp","",
        "| Benchmark | CAGR | Max DD | Sortino | Terminal wealth |",
        "|---|---:|---:|---:|---:|"
    ]
    for _,r in bdf.iterrows():
        lines.append(f"| {r['benchmark']} | {100*r['cagr']:.2f}% | {100*r['max_drawdown']:.2f}% | {r['sortino'] if pd.notna(r['sortino']) else float('nan'):.3f} | {r['terminal_wealth']:.3f} |")
    lines += ["","## Candidate rules at 20 bp","",
              "| Rule | Trades | Exposure | CAGR | Max DD | Sortino | Win rate | Positive years | PASS | Strong |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for _,r in m.iterrows():
        lines.append(
            f"| {r['rule']} | {int(r['trades'])} | {100*r['exposure']:.1f}% | {100*r['cagr']:.2f}% | "
            f"{100*r['max_drawdown']:.2f}% | {r['sortino']:.3f} | {100*r['win_rate']:.1f}% | "
            f"{int(r['positive_years'])}/3 | {bool(r['tactical_pass'])} | {bool(r['strong_pass'])} |"
        )

    lines += ["","## Binding interpretation"]
    if champion:
        lines.append(f"Freeze **{champion}** at the 20 bp primary research-cost assumption. Only this exact rule may be transported to 2025, with no retuning.")
    else:
        lines.append("No preregistered utility rule satisfies the tactical gate. Do not open 2025 to rescue the rule; retain the forecast engine without a frozen allocation strategy.")

    (OUT/"STAGE6_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary={
        "status":status,"champion":champion,
        "benchmarks":bdf.to_dict(orient="records"),
        "candidates":m.to_dict(orient="records"),
        "hashes":{p.name:sha(p) for p in files}
    }
    (OUT/"stage6_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("STAGE6_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE6_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
