import os,io,json,hashlib,zipfile,math,warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
STAGE5_ART=11177455544
READINESS_ART=11166972412
OUT=Path(os.environ.get("OUT_DIR","stage6c_mapping_out"))
OUT.mkdir(parents=True,exist_ok=True)

GLDM_COST=0.000125
MGC_COST=0.000100

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage6c"},timeout=120)
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

def dl_yf(ticker):
    x=yf.download(ticker,start="2021-12-01",end="2025-01-10",interval="1d",
                  auto_adjust=False,actions=False,progress=False,threads=False)
    if x is None or len(x)==0:
        raise RuntimeError(f"No yfinance data for {ticker}")
    if isinstance(x.columns,pd.MultiIndex):
        # yfinance often returns (Price,Ticker)
        x.columns=[c[0] for c in x.columns]
    x=x.reset_index()
    datecol="Date" if "Date" in x.columns else x.columns[0]
    x=x.rename(columns={datecol:"date","Adj Close":"adj_close","Close":"close","Open":"open","High":"high","Low":"low","Volume":"volume"})
    x["date"]=pd.to_datetime(x["date"]).dt.tz_localize(None).dt.normalize()
    for c in ["open","close","adj_close"]:
        x[c]=pd.to_numeric(x[c],errors="coerce")
    return x[["date","open","close","adj_close","volume"]].dropna(subset=["close"]).sort_values("date").reset_index(drop=True)

def dl_stooq_gldm():
    url="https://stooq.com/q/d/l/?s=gldm.us&d1=20211201&d2=20250110&i=d"
    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=60)
    r.raise_for_status()
    txt=r.text
    if "Date" not in txt or len(txt)<100:
        raise RuntimeError("Stooq GLDM response invalid")
    x=pd.read_csv(io.StringIO(txt))
    x.columns=[c.lower() for c in x.columns]
    x["date"]=pd.to_datetime(x["date"]).dt.normalize()
    return x.sort_values("date").reset_index(drop=True)

def prev_close(px,dt):
    z=px[px.date<=dt]
    if len(z)==0: return None,None
    rr=z.iloc[-1]
    return rr.date,float(rr.adj_close if pd.notna(rr.adj_close) else rr.close)

def first_open_on_after(px,dt,strict=False):
    z=px[px.date>dt] if strict else px[px.date>=dt]
    z=z[z.open.notna()]
    if len(z)==0: return None,None
    rr=z.iloc[0]
    return rr.date,float(rr.open)

def mapping_table(fc,panel,px,label):
    rows=[]
    for _,r in fc.iterrows():
        i=int(r.row_index)
        if i+3>=len(panel): continue
        origin=pd.Timestamp(panel.loc[i,"date"]).normalize()
        end=pd.Timestamp(panel.loc[i+3,"date"]).normalize()
        sdt=pd.Timestamp(r.signal_date).normalize()
        sd,sp=prev_close(px,origin)
        ed,ep=prev_close(px,end)
        if sd is None or ed is None or sp<=0 or ep<=0: continue
        inst=math.log(ep/sp)
        rows.append({
            "instrument":label,"row_index":i,"origin_date":origin,"signal_date":sdt,"h3_end_date":end,
            "bist_r3":float(r.y_return),"instrument_r3":inst,
            "start_px_date":sd,"end_px_date":ed,"start_px":sp,"end_px":ep,
            "diff":inst-float(r.y_return)
        })
    return pd.DataFrame(rows)

def mapping_metrics(m):
    y=m.bist_r3.to_numpy(float); x=m.instrument_r3.to_numpy(float)
    pear=float(np.corrcoef(y,x)[0,1])
    spear=float(spearmanr(y,x,nan_policy="omit").statistic)
    X=np.column_stack([np.ones(len(y)),y])
    coef=np.linalg.lstsq(X,x,rcond=None)[0]
    te=x-y
    return {
        "n":int(len(m)),"pearson":pear,"spearman":spear,
        "ols_intercept":float(coef[0]),"ols_beta":float(coef[1]),
        "tracking_error_sd":float(np.std(te,ddof=0)),
        "mae_tracking":float(np.mean(np.abs(te))),
        "sign_agreement":float(np.mean((x>0)==(y>0))),
        "severe_divergence_freq":float(np.mean(np.abs(te)>0.01)),
        "mean_return_difference":float(np.mean(te))
    }

def mapping_pass(mm):
    return (
        mm["n"]>=650 and mm["pearson"]>=0.90 and mm["spearman"]>=0.88 and
        0.85<=mm["ols_beta"]<=1.15 and mm["sign_agreement"]>=0.85 and
        mm["tracking_error_sd"]<=0.006 and mm["severe_divergence_freq"]<=0.10
    )

def u3(row):
    hvol=float(row.sigma20)*math.sqrt(3.0)
    return 0.5*float(row.ret_hat)+0.5*float(row.q50)+0.5*(float(row.p_up)-0.5)*hvol

def transfer(fc,panel,px,label,cost,strict_entry):
    fmap=fc.set_index("row_index")
    i=int(fc.row_index.min()); last=int(fc.row_index.max())
    trades=[]
    while i<=last-3:
        if i not in fmap.index:
            i+=1; continue
        r=fmap.loc[i]
        util=u3(r)
        if util>cost:
            end=pd.Timestamp(panel.loc[i+3,"date"]).normalize()
            signal=pd.Timestamp(r.signal_date).normalize()
            ed,ep=first_open_on_after(px,signal,strict=strict_entry)
            if ed is None:
                i+=3; continue
            xd,xp=first_open_on_after(px,end,strict=False)
            if xd is None or xd<=ed:
                # force strictly after entry if horizon/session collapse
                xd,xp=first_open_on_after(px,ed,strict=True)
            if xd is None or xp is None or ep<=0 or xp<=0:
                i+=3; continue
            gross=math.log(xp/ep)
            net=gross-cost
            trades.append({
                "instrument":label,"entry_row":i,"entry_date":ed,"exit_date":xd,
                "utility":util,"gross_log_return":gross,"net_log_return":net,
                "net_simple_return":math.expm1(net),"win":net>0,
                "signal_date":signal,"bist_end_date":end
            })
            i+=3
        else:
            i+=1
    tr=pd.DataFrame(trades)
    return tr

def perf_from_trades(tr, start_date, end_date):
    if len(tr)==0:
        return {"trades":0,"total_return":0.0,"cagr":0.0,"max_drawdown":0.0,"sortino":None,"win_rate":None,"positive_years":0,"avg_trade_return":None}
    tr=tr.sort_values("entry_date").copy()
    daily=pd.DataFrame({"date":pd.date_range(start_date,end_date,freq="D")})
    daily["r"]=0.0
    for _,r in tr.iterrows():
        # book net trade return at exit date; cash otherwise. This preserves compounded terminal wealth and drawdown at trade resolution.
        idx=daily.index[daily.date==pd.Timestamp(r.exit_date)]
        if len(idx): daily.loc[idx[0],"r"]+=float(r.net_log_return)
    wealth=np.exp(daily.r.cumsum().to_numpy())
    total=float(wealth[-1]-1)
    span=max((pd.Timestamp(end_date)-pd.Timestamp(start_date)).days/365.25,1/365.25)
    cagr=float(wealth[-1]**(1/span)-1)
    peak=np.maximum.accumulate(wealth); mdd=float(np.min(wealth/peak-1))
    rr=daily.r.to_numpy(float)
    mu=float(np.mean(rr))*365.25
    dn=np.minimum(rr,0)
    ddev=float(np.sqrt(np.mean(dn**2))*math.sqrt(365.25))
    sortino=mu/ddev if ddev>1e-12 else None
    yr=[]
    for y,z in daily.groupby(daily.date.dt.year):
        yr.append(math.expm1(float(z.r.sum())))
    return {
        "trades":int(len(tr)),"total_return":total,"cagr":cagr,"max_drawdown":mdd,
        "sortino":sortino,"win_rate":float(tr.win.mean()),"positive_years":int(sum(v>0 for v in yr)),
        "avg_trade_return":float(tr.net_simple_return.mean())
    }

def transfer_pass(mp,pp):
    return (
        mp and pp["trades"]>=20 and pp["cagr"]>0 and pp["positive_years"]>=2 and
        pp["sortino"] is not None and pp["sortino"]>0.75 and pp["max_drawdown"]>-0.25
    )

def main():
    z5=get_zip(STAGE5_ART); fc=read_csv(z5,"stage5_reconciled_forecasts.csv")
    zr=get_zip(READINESS_ART); panel=read_csv(zr,"short_horizon_readiness_panel.csv")
    panel["date"]=pd.to_datetime(panel["date"]).dt.normalize()
    fc["signal_date"]=pd.to_datetime(fc["signal_date"]).dt.normalize()
    # hard DEV-only boundary
    fc=fc[(fc.signal_date>=pd.Timestamp("2022-01-03"))&(fc.signal_date<=pd.Timestamp("2024-12-31"))].copy()

    gldm=dl_yf("GLDM")
    mgc=dl_yf("MGC=F")
    stooq_ok=True; stooq_error=None
    try:
        stq=dl_stooq_gldm()
    except Exception as e:
        stooq_ok=False; stooq_error=str(e); stq=pd.DataFrame()

    gldm.to_csv(OUT/"stage6c_gldm_yahoo_daily.csv",index=False)
    mgc.to_csv(OUT/"stage6c_mgc_yahoo_daily.csv",index=False)
    if stooq_ok: stq.to_csv(OUT/"stage6c_gldm_stooq_daily.csv",index=False)

    coverage=[
        {"instrument":"GLDM_YAHOO","n":len(gldm),"start":str(gldm.date.min().date()),"end":str(gldm.date.max().date())},
        {"instrument":"MGC_YAHOO","n":len(mgc),"start":str(mgc.date.min().date()),"end":str(mgc.date.max().date())},
        {"instrument":"GLDM_STOOQ","n":len(stq) if stooq_ok else 0,"start":str(stq.date.min().date()) if stooq_ok and len(stq) else None,
         "end":str(stq.date.max().date()) if stooq_ok and len(stq) else None,"error":stooq_error}
    ]
    pd.DataFrame(coverage).to_csv(OUT/"stage6c_external_coverage.csv",index=False)

    # independent GLDM price sanity
    sanity={}
    if stooq_ok and len(stq):
        yy=gldm[["date","close"]].merge(stq[["date","close"]],on="date",suffixes=("_yf","_stq"))
        sanity={
            "n":len(yy),
            "level_corr":float(np.corrcoef(yy.close_yf,yy.close_stq)[0,1]),
            "median_abs_level_pct_diff":float(np.median(np.abs(yy.close_yf/yy.close_stq-1))),
            "daily_return_corr":float(np.corrcoef(np.diff(np.log(yy.close_yf)),np.diff(np.log(yy.close_stq)))[0,1]) if len(yy)>2 else None
        }
        pd.DataFrame([sanity]).to_csv(OUT/"stage6c_gldm_source_sanity.csv",index=False)

    gm=mapping_table(fc,panel,gldm,"GLDM")
    mm=mapping_table(fc,panel,mgc,"MGC")
    gm.to_csv(OUT/"stage6c_gldm_mapping.csv",index=False)
    mm.to_csv(OUT/"stage6c_mgc_mapping.csv",index=False)
    gmet=mapping_metrics(gm); mmet=mapping_metrics(mm)
    gpass=mapping_pass(gmet); mpass=mapping_pass(mmet)

    gtr=transfer(fc,panel,gldm,"GLDM",GLDM_COST,strict_entry=False)
    mtr=transfer(fc,panel,mgc,"MGC_DELAYED",MGC_COST,strict_entry=True)
    gtr.to_csv(OUT/"stage6c_gldm_u3_transfer.csv",index=False)
    mtr.to_csv(OUT/"stage6c_mgc_delayed_u3_transfer.csv",index=False)
    start=fc.signal_date.min(); end=fc.signal_date.max()
    gperf=perf_from_trades(gtr,start,end)
    mperf=perf_from_trades(mtr,start,end)
    gtpass=transfer_pass(gpass,gperf)
    mtpass=transfer_pass(mpass,mperf)

    # year returns as realized net log sums by trade exit year
    yrows=[]
    for label,tr in [("GLDM",gtr),("MGC_DELAYED",mtr)]:
        if len(tr):
            tr2=tr.copy(); tr2["year"]=pd.to_datetime(tr2.exit_date).dt.year
            for yr,z in tr2.groupby("year"):
                yrows.append({"instrument":label,"year":int(yr),"trades":len(z),"return":float(math.expm1(z.net_log_return.sum())),"win_rate":float(z.win.mean())})
    pd.DataFrame(yrows).to_csv(OUT/"stage6c_transfer_years.csv",index=False)

    decisions=[
        {
            "instrument":"GLDM","mapping_pass":gpass,"transfer_pass":gtpass,
            "production_freeze_eligible":bool(gpass and gtpass and sanity.get("daily_return_corr",0)>=0.995),
            "status":"PASS_CANDIDATE" if (gpass and gtpass and sanity.get("daily_return_corr",0)>=0.995) else "FAIL_OR_CONDITIONAL",
            **{f"map_{k}":v for k,v in gmet.items()},
            **{f"transfer_{k}":v for k,v in gperf.items()}
        },
        {
            "instrument":"MGC","mapping_pass":mpass,"transfer_pass":mtpass,
            "production_freeze_eligible":False,
            "status":"RESEARCH_PASS_INTRADAY_AUTHORITY_REQUIRED" if (mpass and mtpass) else "RESEARCH_FAIL",
            **{f"map_{k}":v for k,v in mmet.items()},
            **{f"transfer_{k}":v for k,v in mperf.items()}
        }
    ]
    dec=pd.DataFrame(decisions)
    dec.to_csv(OUT/"stage6c_instrument_decisions.csv",index=False)

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6C Cross-Instrument Mapping Result","",
        "## Mapping diagnostics","",
        "| Instrument | N | Pearson | Spearman | Beta | Sign agreement | TE SD | Severe divergence | PASS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for name,met,ps in [("GLDM",gmet,gpass),("MGC",mmet,mpass)]:
        lines.append(f"| {name} | {met['n']} | {met['pearson']:.4f} | {met['spearman']:.4f} | {met['ols_beta']:.4f} | {100*met['sign_agreement']:.1f}% | {100*met['tracking_error_sd']:.3f}% | {100*met['severe_divergence_freq']:.1f}% | {ps} |")
    lines += ["","## Frozen U3 transfer","",
              "| Instrument | Cost | Trades | CAGR | Max DD | Sortino | Positive years | Transfer PASS |",
              "|---|---:|---:|---:|---:|---:|---:|---|",
              f"| GLDM | {GLDM_COST*10000:.2f} bp | {gperf['trades']} | {100*gperf['cagr']:.2f}% | {100*gperf['max_drawdown']:.2f}% | {gperf['sortino'] if gperf['sortino'] is not None else float('nan'):.3f} | {gperf['positive_years']}/3 | {gtpass} |",
              f"| MGC delayed daily stress | {MGC_COST*10000:.2f} bp | {mperf['trades']} | {100*mperf['cagr']:.2f}% | {100*mperf['max_drawdown']:.2f}% | {mperf['sortino'] if mperf['sortino'] is not None else float('nan'):.3f} | {mperf['positive_years']}/3 | {mtpass} |",
              "","## GLDM source sanity",json.dumps(sanity,indent=2),
              "","## Binding decision"]
    if decisions[0]["production_freeze_eligible"]:
        lines.append("GLDM clears the frozen research mapping and transfer gates and passes the independent source sanity check. It is eligible for a conditional execution freeze subject to account-specific FX/commission verification.")
    else:
        lines.append("GLDM does not satisfy all frozen requirements for production freeze.")
    if mpass and mtpass:
        lines.append("MGC clears research mapping/transfer stress, but production use remains blocked because daily secondary continuous data cannot establish origin-safe same-session futures execution. Official timestamped CME data are required.")
    else:
        lines.append("MGC does not clear the research mapping/transfer gate under the frozen daily-data stress.")

    (OUT/"STAGE6C_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary={
        "gldm_mapping":gmet,"mgc_mapping":mmet,
        "gldm_mapping_pass":gpass,"mgc_mapping_pass":mpass,
        "gldm_transfer":gperf,"mgc_transfer":mperf,
        "gldm_transfer_pass":gtpass,"mgc_transfer_pass":mtpass,
        "gldm_source_sanity":sanity,
        "decisions":decisions,
        "hashes":{p.name:sha(p) for p in files}
    }
    (OUT/"stage6c_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("STAGE6C_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE6C_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
