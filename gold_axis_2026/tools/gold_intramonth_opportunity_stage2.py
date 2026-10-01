import os, io, json, math, time, hashlib, zipfile, requests
from pathlib import Path
import numpy as np
import pandas as pd

REPO = "ataullahturgut/sim3-automation"
BIST_URL = "https://www.borsaistanbul.com/metal-fiyatlari.php"
METALS = {"AU":"gold","AG":"silver","PT":"platinum","PD":"palladium"}
START_YEAR, END_YEAR = 2011, 2025
CHHHO_ARTIFACT_ID = 10989389723
CHHHO_RUN_ID = 36251783712
OUT = Path(os.environ.get("OUT_DIR","stage2_out"))
OUT.mkdir(parents=True, exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 Gold-Intramonth-Research/1.0"}

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def fetch_bist(metal, year, retries=4):
    params={
        "op":"fetchMetalFiyatlari",
        "startDate":f"{year}/01/01",
        "endDate":f"{year}/12/31",
        "priceType":metal,
    }
    last=None
    for i in range(retries):
        try:
            r=requests.get(BIST_URL,params=params,headers=UA,timeout=45)
            r.raise_for_status()
            x=r.json()
            if x.get("status")!="success":
                raise RuntimeError(f"status={x.get('status')} body={str(x)[:500]}")
            return x.get("data",[])
        except Exception as e:
            last=e; time.sleep(0.8*(i+1))
    raise RuntimeError(f"BIST fetch failed {metal} {year}: {last}")

def load_bist():
    rows=[]
    request_log=[]
    for code,name in METALS.items():
        for y in range(START_YEAR,END_YEAR+1):
            data=fetch_bist(code,y)
            request_log.append({"metal":code,"year":y,"records":len(data)})
            for r in data:
                if r.get("priceRef")=="MTL" and r.get("priceCurrency")=="USD" and r.get("priceWeight")=="OZ":
                    rows.append({
                        "date":r["priceDate"],"metal":name,"metal_code":code,
                        "price":float(r["priceValue"]),"source_id":r.get("id")
                    })
            time.sleep(0.08)
    df=pd.DataFrame(rows)
    if df.empty: raise RuntimeError("No governed BIST rows returned")
    df["date"]=pd.to_datetime(df["date"])
    df=df.sort_values(["metal","date","source_id"]).drop_duplicates(["metal","date"],keep="last")
    df.to_csv(OUT/"bist_metal_usd_oz_long.csv",index=False)
    pd.DataFrame(request_log).to_csv(OUT/"bist_request_audit.csv",index=False)
    wide=df.pivot(index="date",columns="metal",values="price").sort_index()
    wide.to_csv(OUT/"bist_four_metal_usd_oz_wide.csv")
    return df,wide,request_log

def download_monthly_context():
    token=os.environ.get("GITHUB_TOKEN")
    if not token: raise RuntimeError("GITHUB_TOKEN missing")
    url=f"https://api.github.com/repos/{REPO}/actions/artifacts/{CHHHO_ARTIFACT_ID}/zip"
    r=requests.get(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","User-Agent":"gold-intramonth-stage2"},timeout=60)
    r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    js=[n for n in z.namelist() if n.endswith(".json")]
    if not js: raise RuntimeError("ChHHO artifact contains no JSON")
    x=json.loads(z.read(js[0]))
    out=[]
    for block in ["dev","transport_2025","stress_2026"]:
        for row in x.get(block,{}).get("rows",[]):
            out.append({
                "block":block,
                "origin_month":row["origin"],
                "target_month":row["target"],
                "pred_log_return_gold":float(row["pred_log_return_gold"]),
                "monthly_direction":"UP" if float(row["pred_log_return_gold"])>0 else ("DOWN" if float(row["pred_log_return_gold"])<0 else "FLAT"),
                "monthly_forecast":float(row["forecast"]),
                "monthly_actual":float(row["actual"]),
                "monthly_rw":float(row["rw"]),
            })
    c=pd.DataFrame(out)
    c.to_csv(OUT/"monthly_chhho_context.csv",index=False)
    return c,x

def metal_feature_frame(s,name):
    z=pd.DataFrame({"date":s.index,"price":s.values}).dropna().sort_values("date")
    z[f"{name}_logp"]=np.log(z["price"])
    for h in [1,3,5,10,21]:
        z[f"{name}_r{h}"]=z[f"{name}_logp"].diff(h)
    return z

def build_dataset(wide,ctx):
    gold=wide["gold"].dropna().sort_index()
    g=pd.DataFrame({"origin_date":gold.index,"gold":gold.values})
    g["gold_logp"]=np.log(g["gold"])
    for h in [1,3,5,10,21]:
        g[f"gold_r{h}"]=g["gold_logp"].diff(h)
    g["gold_r1_raw"]=g["gold_logp"].diff()
    g["sigma20"]=g["gold_r1_raw"].rolling(20,min_periods=20).std(ddof=0)
    g["scale5"]=g["sigma20"]*math.sqrt(5)
    g["rv20"]=np.sqrt((g["gold_r1_raw"]**2).rolling(20,min_periods=20).sum())
    g["absret20"]=g["gold_r1_raw"].abs().rolling(20,min_periods=20).mean()
    high21=g["gold"].rolling(21,min_periods=21).max()
    low21=g["gold"].rolling(21,min_periods=21).min()
    g["dd_high21"]=np.log(g["gold"]/high21)
    g["dist_low21"]=np.log(g["gold"]/low21)
    g["reversal_1_vs_5"]=g["gold_r1"]-(g["gold_r5"]/5.0)

    # Future-path labels on Gold calendar
    dates=list(g["origin_date"])
    prices=g["gold"].to_numpy(float)
    n=len(g)
    for h in [1,3,5,10]:
        mfe=np.full(n,np.nan); mae=np.full(n,np.nan)
        for i in range(n-h):
            rr=np.log(prices[i+1:i+h+1]/prices[i])
            mfe[i]=np.max(rr); mae[i]=np.min(rr)
        g[f"mfe{h}"]=mfe; g[f"mae{h}"]=mae
        g[f"mfe{h}_pct"]=100*np.expm1(g[f"mfe{h}"])
        g[f"mae{h}_pct"]=100*np.expm1(g[f"mae{h}"])

    g["signal_date"]=g["origin_date"].shift(-1)
    g["signal_month"]=g["signal_date"].dt.to_period("M").astype(str)

    # Same-month truncated 5-observation excursion
    sm_mfe=np.full(n,np.nan); sm_mae=np.full(n,np.nan); sm_n=np.zeros(n,dtype=int)
    for i in range(n-1):
        sig=dates[i+1]
        vals=[]
        for j in range(i+1,min(n,i+6)):
            if dates[j].year==sig.year and dates[j].month==sig.month:
                vals.append(math.log(prices[j]/prices[i]))
            else:
                break
        if vals:
            sm_mfe[i]=max(vals); sm_mae[i]=min(vals); sm_n[i]=len(vals)
    g["mfe5_same_month"]=sm_mfe
    g["mae5_same_month"]=sm_mae
    g["mfe5_same_month_pct"]=100*np.expm1(g["mfe5_same_month"])
    g["mae5_same_month_pct"]=100*np.expm1(g["mae5_same_month"])
    g["same_month_future_n"]=sm_n

    for k in [0.50,0.75,1.00]:
        tag=f"k{int(k*100):03d}"
        g[f"opp5_{tag}"]=(g["mfe5"]>=k*g["scale5"]).where(g["mfe5"].notna() & g["scale5"].notna())
        g[f"opp5_same_month_{tag}"]=(g["mfe5_same_month"]>=k*g["scale5"]).where(g["mfe5_same_month"].notna() & g["scale5"].notna())

    # Causal companion features on each companion's own calendar, then as-of onto Gold origin
    for name in ["silver","platinum","palladium"]:
        z=metal_feature_frame(wide[name].dropna().sort_index(),name)
        keep=["date","price",f"{name}_r1",f"{name}_r5",f"{name}_r21"]
        z=z[keep].rename(columns={"date":f"{name}_obs_date","price":f"{name}_price"})
        g=pd.merge_asof(
            g.sort_values("origin_date"),
            z.sort_values(f"{name}_obs_date"),
            left_on="origin_date",right_on=f"{name}_obs_date",direction="backward"
        )
        g[f"{name}_age_days"]=(g["origin_date"]-g[f"{name}_obs_date"]).dt.days

    comp1=g[["silver_r1","platinum_r1","palladium_r1"]]
    comp5=g[["silver_r5","platinum_r5","palladium_r5"]]
    g["cross_r1_breadth_pos"]=(comp1>0).sum(axis=1)
    g["cross_r5_breadth_pos"]=(comp5>0).sum(axis=1)
    g["cross_r1_dispersion"]=comp1.std(axis=1,ddof=0)
    g["cross_r5_dispersion"]=comp5.std(axis=1,ddof=0)
    g["gold_comp_r1_divergence"]=g["gold_r1"]-comp1.mean(axis=1)
    g["gold_comp_r5_divergence"]=g["gold_r5"]-comp5.mean(axis=1)

    # Monthly ChHHO context
    cm=ctx[ctx["block"].isin(["dev","transport_2025"])].copy()
    g=g.merge(cm,left_on="signal_month",right_on="target_month",how="left")

    # Chronology role by signal date, independent of context coverage
    sd=g["signal_date"]
    g["period_role"]=np.select(
        [
            sd.dt.year<=2021,
            sd.dt.year.between(2022,2024),
            sd.dt.year==2025,
            sd.dt.year>=2026,
        ],
        ["BACKGROUND","DEV","TRANSPORT_2025","OPENED_2026"],
        default="UNKNOWN"
    )

    # Prior-only event probability baselines + continuous medians
    for tag in ["k050","k075","k100"]:
        y=g[f"opp5_{tag}"].astype(float)
        prior=y.shift(1)
        g[f"p_expand_{tag}"]=prior.expanding(min_periods=252).mean()
        g[f"p_roll252_{tag}"]=prior.rolling(252,min_periods=252).mean()
    for col in ["mfe5","mae5"]:
        prior=g[col].shift(1)
        g[f"{col}_expand_median"]=prior.expanding(min_periods=252).median()
        g[f"{col}_roll252_median"]=prior.rolling(252,min_periods=252).median()

    return g

def logloss(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    y=np.asarray(y,float)
    return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))

def summarize(long,wide,g,ctx,request_log):
    cov={}
    for m in METALS.values():
        s=wide[m].dropna()
        cov[m]={
            "n":int(len(s)),
            "first":str(s.index.min().date()) if len(s) else None,
            "last":str(s.index.max().date()) if len(s) else None,
            "duplicate_dates_after_filter":0,
        }
    common=wide.dropna(subset=list(METALS.values()))
    cov["all4_common"]={"n":int(len(common)),"first":str(common.index.min().date()) if len(common) else None,"last":str(common.index.max().date()) if len(common) else None}

    eligible=g[g["mfe5"].notna() & g["scale5"].notna()].copy()
    dev=eligible[(eligible["period_role"]=="DEV")]
    devctx=dev[dev["block"]=="dev"].copy()
    down=devctx[devctx["monthly_direction"]=="DOWN"].copy()
    up=devctx[devctx["monthly_direction"]=="UP"].copy()
    tr=eligible[(eligible["period_role"]=="TRANSPORT_2025") & (eligible["block"]=="transport_2025")]

    prev={}
    for tag in ["k050","k075","k100"]:
        prev[tag]={
            "all_dev":float(dev[f"opp5_{tag}"].mean()),
            "dev_with_monthly_context":float(devctx[f"opp5_{tag}"].mean()),
            "monthly_down_dev":float(down[f"opp5_{tag}"].mean()) if len(down) else None,
            "monthly_up_dev":float(up[f"opp5_{tag}"].mean()) if len(up) else None,
            "monthly_down_same_month_dev":float(down[f"opp5_same_month_{tag}"].mean()) if len(down) else None,
            "transport_2025":float(tr[f"opp5_{tag}"].mean()) if len(tr) else None,
        }

    baseline={}
    for tag in ["k050","k075","k100"]:
        y=dev[f"opp5_{tag}"].astype(float)
        baseline[tag]={}
        for base in [f"p_expand_{tag}",f"p_roll252_{tag}"]:
            z=dev[[f"opp5_{tag}",base]].dropna()
            baseline[tag][base]={
                "n":int(len(z)),
                "brier":float(np.mean((z[base]-z[f"opp5_{tag}"])**2)) if len(z) else None,
                "logloss":logloss(z[f"opp5_{tag}"],z[base]) if len(z) else None,
            }

    cont={}
    for target in ["mfe5","mae5"]:
        cont[target]={}
        for base in [f"{target}_expand_median",f"{target}_roll252_median"]:
            z=dev[[target,base]].dropna()
            cont[target][base]={
                "n":int(len(z)),
                "mae_log":float(np.mean(np.abs(z[target]-z[base]))) if len(z) else None,
                "rmse_log":float(np.sqrt(np.mean((z[target]-z[base])**2))) if len(z) else None,
            }

    # Month-level business diagnostic on frozen DEV context
    month_rows=[]
    for month,mm in devctx.groupby("signal_month"):
        d=mm["monthly_direction"].iloc[0]
        row={
            "target_month":month,
            "monthly_direction":d,
            "daily_origins":int(len(mm)),
            "max_mfe5_same_month_pct":float(mm["mfe5_same_month_pct"].max()),
            "median_mfe5_same_month_pct":float(mm["mfe5_same_month_pct"].median()),
        }
        for pct in [1,2,3]:
            row[f"has_same_month_mfe_ge_{pct}pct"]=bool((mm["mfe5_same_month_pct"]>=pct).any())
        for tag in ["k050","k075","k100"]:
            row[f"has_same_month_{tag}"]=bool(mm[f"opp5_same_month_{tag}"].fillna(False).any())
            row[f"share_same_month_{tag}"]=float(mm[f"opp5_same_month_{tag}"].mean())
        month_rows.append(row)
    month_df=pd.DataFrame(month_rows).sort_values("target_month")
    month_df.to_csv(OUT/"dev_monthly_context_opportunity_summary.csv",index=False)
    downm=month_df[month_df["monthly_direction"]=="DOWN"]
    upm=month_df[month_df["monthly_direction"]=="UP"]

    fixed={}
    for pct in [1,2,3]:
        col=f"has_same_month_mfe_ge_{pct}pct"
        fixed[str(pct)]={
            "down_months_with_opportunity":int(downm[col].sum()),
            "down_months_total":int(len(downm)),
            "down_month_share":float(downm[col].mean()) if len(downm) else None,
            "up_months_with_opportunity":int(upm[col].sum()),
            "up_months_total":int(len(upm)),
            "up_month_share":float(upm[col].mean()) if len(upm) else None,
        }

    out={
        "status":"PASS" if len(dev)>100 and len(down)>20 else "REVIEW",
        "authority":{
            "bist_endpoint":BIST_URL,
            "row_filter":"MTL/USD/OZ",
            "chhho_run":CHHHO_RUN_ID,
            "chhho_artifact":CHHHO_ARTIFACT_ID,
            "chronology":{"background":"2011-2021","dev":"2022-2024","transport":"2025","2026":"opened"},
        },
        "coverage":cov,
        "rows":{
            "eligible_all":int(len(eligible)),
            "dev":int(len(dev)),
            "dev_with_monthly_context":int(len(devctx)),
            "dev_monthly_down":int(len(down)),
            "dev_monthly_up":int(len(up)),
            "transport_2025":int(len(tr)),
        },
        "months":{
            "dev_context_months":int(len(month_df)),
            "dev_down_months":int(len(downm)),
            "dev_up_months":int(len(upm)),
        },
        "mfe5_dev":{
            "mean_pct":float(dev["mfe5_pct"].mean()),
            "median_pct":float(dev["mfe5_pct"].median()),
            "p75_pct":float(dev["mfe5_pct"].quantile(.75)),
            "p90_pct":float(dev["mfe5_pct"].quantile(.90)),
        },
        "mae5_dev":{
            "mean_pct":float(dev["mae5_pct"].mean()),
            "median_pct":float(dev["mae5_pct"].median()),
            "p10_pct":float(dev["mae5_pct"].quantile(.10)),
        },
        "candidate_prevalence":prev,
        "fixed_same_month_diagnostics":fixed,
        "baseline_metrics":baseline,
        "continuous_baselines":cont,
        "down_month_max_mfe_same_month_pct":{
            "median":float(downm["max_mfe5_same_month_pct"].median()) if len(downm) else None,
            "min":float(downm["max_mfe5_same_month_pct"].min()) if len(downm) else None,
            "max":float(downm["max_mfe5_same_month_pct"].max()) if len(downm) else None,
        },
    }
    return out,month_df

def main():
    long,wide,req=load_bist()
    ctx,_=download_monthly_context()
    g=build_dataset(wide,ctx)
    g.to_csv(OUT/"intramonth_opportunity_stage2_dataset.csv",index=False)
    summary,month_df=summarize(long,wide,g,ctx,req)

    files=[
        OUT/"bist_metal_usd_oz_long.csv",
        OUT/"bist_four_metal_usd_oz_wide.csv",
        OUT/"intramonth_opportunity_stage2_dataset.csv",
        OUT/"monthly_chhho_context.csv",
        OUT/"dev_monthly_context_opportunity_summary.csv",
    ]
    summary["hashes"]={p.name:sha256_file(p) for p in files}
    with open(OUT/"stage2_summary.json","w") as f: json.dump(summary,f,indent=2)

    # Human-readable compact result
    fx=summary["fixed_same_month_diagnostics"]
    lines=[
        "# GOLD INTRAMONTH OPPORTUNITY — Stage 2A Core Label Audit Result",
        "",
        f"**Status:** {summary['status']}",
        "",
        "## Coverage",
    ]
    for k,v in summary["coverage"].items():
        lines.append(f"- {k}: n={v['n']}, {v.get('first')}..{v.get('last')}")
    lines += [
        "",
        "## DEV population",
        f"- DEV eligible daily origins: {summary['rows']['dev']}",
        f"- DEV origins with frozen monthly ChHHO context: {summary['rows']['dev_with_monthly_context']}",
        f"- monthly-DOWN daily origins: {summary['rows']['dev_monthly_down']}",
        f"- monthly-UP daily origins: {summary['rows']['dev_monthly_up']}",
        f"- DEV ChHHO context months: {summary['months']['dev_context_months']} (DOWN {summary['months']['dev_down_months']}, UP {summary['months']['dev_up_months']})",
        "",
        "## Main path statistics",
        f"- DEV median MFE5: {summary['mfe5_dev']['median_pct']:.3f}%",
        f"- DEV p75 MFE5: {summary['mfe5_dev']['p75_pct']:.3f}%",
        f"- DEV p90 MFE5: {summary['mfe5_dev']['p90_pct']:.3f}%",
        f"- DEV median MAE5: {summary['mae5_dev']['median_pct']:.3f}%",
        "",
        "## Candidate label prevalence",
    ]
    for tag,v in summary["candidate_prevalence"].items():
        lines.append(
            f"- {tag}: DEV {100*v['all_dev']:.1f}%; monthly-DOWN {100*v['monthly_down_dev']:.1f}%; "
            f"monthly-DOWN same-month {100*v['monthly_down_same_month_dev']:.1f}%"
        )
    lines += ["","## Monthly-DOWN same-month opportunity existence"]
    for pct,v in fx.items():
        lines.append(
            f"- >= {pct}% within-month 5-observation excursion: "
            f"{v['down_months_with_opportunity']}/{v['down_months_total']} DOWN months "
            f"({100*v['down_month_share']:.1f}%)"
        )
    lines += [
        "",
        "## Governance",
        "- 2022-2024 only for DEV selection",
        "- 2025 transport only",
        "- 2026 not used",
        "- monthly context from frozen ChHHO artifact 10989389723",
        "- no complex model selected in Stage 2A",
    ]
    (OUT/"STAGE2_RESULT.md").write_text("\n".join(lines),encoding="utf-8")

    print("STAGE2_SUMMARY_JSON="+json.dumps(summary,separators=(",",":")))
    print((OUT/"STAGE2_RESULT.md").read_text())

if __name__=="__main__":
    main()
