import os,io,json,hashlib,zipfile,math
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
STAGE5_ART=11177455544
READINESS_ART=11166972412
OUT=Path(os.environ.get("OUT_DIR","stage6b_feasibility_out"))
OUT.mkdir(parents=True,exist_ok=True)

RULES=["U1_RET_ONLY","U2_MEDIAN_CONSENSUS","U3_PROB_TILT","U4_FULL_RISK"]
GRID=np.round(np.arange(0.0,0.0050000001,0.000025),8)  # 0.25 bp
REPORT_COSTS=[0.0,0.0005,0.0010,0.0015,0.0020,0.0030,0.0040,0.0050]
BH_COST=0.0020

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage6b"},timeout=120)
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

def utility(row,rule):
    hvol=float(row["sigma20"])*math.sqrt(3.0)
    ret=float(row["ret_hat"]); q50=float(row["q50"]); q10=float(row["q10"]); p=float(row["p_up"])
    downside=max(0.0,-q10)
    if rule=="U1_RET_ONLY": return ret
    if rule=="U2_MEDIAN_CONSENSUS": return 0.5*ret+0.5*q50
    if rule=="U3_PROB_TILT": return 0.5*ret+0.5*q50+0.5*(p-0.5)*hvol
    if rule=="U4_FULL_RISK": return 0.5*ret+0.5*q50+0.5*(p-0.5)*hvol-0.5*downside
    raise KeyError(rule)

def perf(r,dates,pos):
    r=np.asarray(r,float)
    dates=pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    wealth=np.exp(np.cumsum(r))
    terminal=float(wealth[-1])
    total=terminal-1.0
    span=max((dates.iloc[-1]-dates.iloc[0]).days/365.25,1/365.25)
    cagr=terminal**(1/span)-1.0
    peak=np.maximum.accumulate(wealth)
    mdd=float((wealth/peak-1.0).min())
    mu=float(np.mean(r))*252.0
    sd=float(np.std(r,ddof=0))*math.sqrt(252.0)
    sharpe=mu/sd if sd>1e-12 else np.nan
    dn=np.minimum(r,0.0)
    ddev=float(np.sqrt(np.mean(dn**2))*math.sqrt(252.0))
    sortino=mu/ddev if ddev>1e-12 else np.nan
    return dict(terminal_wealth=terminal,total_return=total,cagr=float(cagr),max_drawdown=mdd,
                sharpe=sharpe,sortino=sortino,exposure=float(np.mean(pos)))

def yearly_positive_count(r,dates):
    d=pd.DataFrame({"date":pd.to_datetime(dates),"r":r})
    vals=[]
    for yr,z in d.groupby(d.date.dt.year):
        vals.append(float(np.expm1(z.r.sum())))
    return int(sum(v>0 for v in vals)),vals

def simulate(rule,cost,fc,panel,first_idx,last_idx):
    fmap=fc.set_index("row_index")
    pos=np.zeros(last_idx-first_idx,float)
    cost_arr=np.zeros_like(pos)
    trades=[]
    i=first_idx
    while i<=last_idx-3:
        if i not in fmap.index:
            i+=1; continue
        row=fmap.loc[i]
        u=utility(row,rule)
        if u>cost:
            for j in range(i+1,i+4):
                pos[j-(first_idx+1)]=1.0
            cost_arr[(i+1)-(first_idx+1)] += cost
            gross=sum(float(panel.loc[j,"gold_r1"]) for j in (i+1,i+2,i+3))
            frozen=float(row["y_return"])
            if abs(gross-frozen)>1e-9:
                raise RuntimeError(f"H3 mismatch {i}")
            trades.append({
                "entry_row":i,"exit_row":i+3,"utility":u,
                "gross_log_return":gross,"net_log_return":gross-cost,
                "gross_simple_return":float(np.expm1(gross)),
                "net_simple_return":float(np.expm1(gross-cost))
            })
            i+=3
        else:
            i+=1

    interval_rows=np.arange(first_idx+1,last_idx+1)
    gold=np.array([float(panel.loc[j,"gold_r1"]) for j in interval_rows])
    strat=pos*gold-cost_arr
    dates=pd.to_datetime([panel.loc[j,"date"] for j in interval_rows])
    p=perf(strat,dates,pos)
    py,yearvals=yearly_positive_count(strat,dates)
    if trades:
        gross_log=float(sum(t["gross_log_return"] for t in trades))
        cost_drag=float(cost*len(trades))
        avg_gross=float(np.mean([t["gross_simple_return"] for t in trades]))
    else:
        gross_log=0.0; cost_drag=0.0; avg_gross=np.nan
    return {
        **p,
        "trades":len(trades),
        "positive_years":py,
        "gross_log_return":gross_log,
        "cost_drag_log":cost_drag,
        "net_log_return":float(strat.sum()),
        "avg_gross_trade_return":avg_gross,
        "cost_share_of_avg_gross_trade":float(cost/avg_gross) if trades and avg_gross>0 else np.nan
    }

def benchmark(panel,first_idx,last_idx,cost):
    rows=np.arange(first_idx+1,last_idx+1)
    gold=np.array([float(panel.loc[j,"gold_r1"]) for j in rows])
    gold[0]-=cost
    dates=pd.to_datetime([panel.loc[j,"date"] for j in rows])
    return perf(gold,dates,np.ones(len(gold)))

def max_cost(z,mask):
    q=z[mask]
    return float(q["cost"].max()) if len(q) else None

def intervals(costs,step=0.000025):
    vals=sorted(float(x) for x in costs)
    if not vals: return []
    out=[]; a=vals[0]; b=vals[0]
    for x in vals[1:]:
        if abs(x-b-step)<1e-10:
            b=x
        else:
            out.append((a,b)); a=b=x
    out.append((a,b))
    return out

def main():
    z5=get_zip(STAGE5_ART)
    fc=read_csv(z5,"stage5_reconciled_forecasts.csv")
    zr=get_zip(READINESS_ART)
    panel=read_csv(zr,"short_horizon_readiness_panel.csv")
    panel["date"]=pd.to_datetime(panel["date"])
    panel=panel.reset_index(drop=True)

    first_idx=int(fc.row_index.min()); last_idx=int(fc.row_index.max())
    bh=benchmark(panel,first_idx,last_idx,BH_COST)

    rows=[]
    for rule in RULES:
        for cost in GRID:
            m=simulate(rule,float(cost),fc,panel,first_idx,last_idx)
            tactical=(
                m["trades"]>=20 and m["cagr"]>0 and
                m["max_drawdown"]>=bh["max_drawdown"] and
                pd.notna(m["sortino"]) and m["sortino"]>bh["sortino"] and
                m["positive_years"]>=2
            )
            strong=(m["cagr"]>=bh["cagr"] and m["max_drawdown"]>=bh["max_drawdown"])
            rows.append({"rule":rule,"cost":float(cost),"cost_bp":float(cost*10000),**m,
                         "tactical_pass":bool(tactical),"strong_parity":bool(strong)})
    g=pd.DataFrame(rows)
    g.to_csv(OUT/"stage6b_cost_grid.csv",index=False)

    br=[]
    passbands=[]
    for rule,z in g.groupby("rule",sort=False):
        profit=max_cost(z,z.cagr>0)
        sortino=max_cost(z,z.sortino>=bh["sortino"])
        strong=max_cost(z,z.strong_parity)
        tact=max_cost(z,z.tactical_pass)
        ints=intervals(z.loc[z.tactical_pass,"cost"].tolist())
        passbands.append({"rule":rule,"tactical_pass_intervals":json.dumps([[a*10000,b*10000] for a,b in ints])})
        br.append({
            "rule":rule,
            "profit_breakeven_cost_bp":None if profit is None else profit*10000,
            "sortino_parity_cost_bp":None if sortino is None else sortino*10000,
            "strong_parity_cost_bp":None if strong is None else strong*10000,
            "tactical_gate_cost_bp":None if tact is None else tact*10000,
            "tactical_pass_grid_points":int(z.tactical_pass.sum())
        })
    bdf=pd.DataFrame(br).merge(pd.DataFrame(passbands),on="rule")
    bdf.to_csv(OUT/"stage6b_break_even_table.csv",index=False)

    rpt=g[np.isclose(g["cost"].to_numpy()[:,None],np.array(REPORT_COSTS)[None,:],atol=1e-12).any(axis=1)].copy()
    rpt.to_csv(OUT/"stage6b_turnover_decomposition.csv",index=False)

    summary={
        "buy_and_hold_20bp":bh,
        "break_even":bdf.to_dict(orient="records"),
        "non_monotonic_tactical_pass":bool(any(
            len(json.loads(x))>1 or (len(json.loads(x))==1 and json.loads(x)[0][0]>0)
            for x in bdf["tactical_pass_intervals"]
        ))
    }

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6B Cost / Turnover Audit","",
        "## Frozen benchmark",
        f"- BUY_AND_HOLD CAGR: {100*bh['cagr']:.2f}%",
        f"- BUY_AND_HOLD max DD: {100*bh['max_drawdown']:.2f}%",
        f"- BUY_AND_HOLD Sortino: {bh['sortino']:.3f}","",
        "## Break-even / parity grid","",
        "| Rule | Profit BE | Sortino parity | Strong parity | Highest tactical-pass cost | Tactical-pass grid points |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for _,r in bdf.iterrows():
        def fmt(v):
            return "—" if pd.isna(v) else f"{v:.2f} bp"
        lines.append(f"| {r['rule']} | {fmt(r['profit_breakeven_cost_bp'])} | {fmt(r['sortino_parity_cost_bp'])} | {fmt(r['strong_parity_cost_bp'])} | {fmt(r['tactical_gate_cost_bp'])} | {int(r['tactical_pass_grid_points'])} |")
    lines += ["","## Tactical-pass cost bands"]
    for _,r in bdf.iterrows():
        lines.append(f"- {r['rule']}: {r['tactical_pass_intervals']}")
    if summary["non_monotonic_tactical_pass"]:
        lines += ["","## Critical interpretation",
                  "The tactical gate is non-monotonic in execution cost because the frozen Stage-6 entry hurdle equals the assumed cost. Higher cost can mechanically suppress marginal trades and therefore sometimes improve risk-adjusted metrics. Accordingly, the reported highest tactical-pass cost is **not** a simple statement that every lower cost would pass.",
                  "",
                  "Instrument feasibility must compare the actual all-in cost to the exact frozen cost/hurdle contract, or a new ex-ante fixed-hurdle implementation must be separately preregistered."]

    (OUT/"STAGE6B_COST_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary["hashes"]={p.name:sha(p) for p in files}
    (OUT/"stage6b_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("STAGE6B_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE6B_COST_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
