import os,io,json,math,hashlib,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg, requests

REPO="ataullahturgut/sim3-automation"
EXT_ARTIFACT=11028494060
OUT=Path(os.environ.get("OUT_DIR","global_xau_readiness_out"))
OUT.mkdir(parents=True,exist_ok=True)

SERIES={
    "gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-readiness"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_json(z):
    names=[n for n in z.namelist() if n.endswith(".json")]
    if len(names)!=1: raise RuntimeError(names)
    return json.loads(z.read(names[0]))

def series_from_dict(dct,field=None,name=None):
    rows=[]
    if field is None:
        for ds,v in dct.items():
            if v is None: continue
            rows.append((pd.to_datetime(ds),float(v)))
    else:
        for ds,v in dct.items():
            val=v.get(field)
            if val is None: continue
            rows.append((pd.to_datetime(ds),float(val)))
    return pd.DataFrame(rows,columns=["obs_date",name]).sort_values("obs_date")

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def load_metals():
    dsn=os.environ["NEON_DATABASE_URL"]
    raw={}
    lineage={}
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for name,sid in SERIES.items():
                cur.execute("""
                    SELECT observation_ts::date AS d, value, source, source_symbol, quality_status
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts, retrieved_at
                """,(sid,))
                rows=cur.fetchall()
                if not rows: raise RuntimeError(f"NO_ROWS {sid}")
                q=pd.DataFrame(rows,columns=["date","value","source","source_symbol","quality_status"])
                q["date"]=pd.to_datetime(q["date"])
                q["value"]=pd.to_numeric(q["value"],errors="coerce")
                q=q.dropna(subset=["value"])
                q=q[q.value>0]
                q=q.sort_values("date").drop_duplicates("date",keep="last")
                # Historical spot bundle is market-daily; exclude Sat/Sun.
                q=q[q.date.dt.weekday<5].reset_index(drop=True)
                raw[name]=q[["date","value"]].rename(columns={"value":name})
                lineage[name]={
                    "series_id":sid,"n":int(len(q)),"first":str(q.date.min().date()),"last":str(q.date.max().date()),
                    "sources":sorted(set(str(x) for x in q.merge(pd.DataFrame(rows,columns=["date0","v0","source","source_symbol","quality_status"]),left_index=True,right_index=True,how="left").source.dropna())) if False else []
                }
        conn.rollback()
    return raw,lineage

def main():
    metals,lineage=load_metals()
    gold=metals["gold"].copy().sort_values("date").reset_index(drop=True)
    df=gold.copy()
    df["signal_date"]=df["date"].shift(-1)
    lg=np.log(df.gold)
    for h in [1,3,5]:
        df[f"target_r{h}"]=np.log(df.gold.shift(-h)/df.gold)
    for h in [1,3,5,10,21]:
        df[f"gold_r{h}"]=lg.diff(h)
    df["sigma20"]=lg.diff().rolling(20).std(ddof=0)

    for name in ["silver","platinum","palladium"]:
        q=metals[name].copy().sort_values("date")
        lp=np.log(q[name])
        for h in [1,5,21]:
            q[f"{name}_r{h}"]=lp.diff(h)
        q=q.rename(columns={"date":f"{name}_obs_date",name:f"{name}_price"})
        df=pd.merge_asof(
            df.sort_values("date"),q.sort_values(f"{name}_obs_date"),
            left_on="date",right_on=f"{name}_obs_date",direction="backward"
        )
        df[f"{name}_age_days"]=(df.date-df[f"{name}_obs_date"]).dt.days

    df=df[df.signal_date.notna()].copy().reset_index(drop=True)

    ext=read_json(get_zip(EXT_ARTIFACT))
    df["cut_h15"]=df.signal_date-pd.Timedelta(days=2)
    df["cut_h10"]=df.signal_date-pd.Timedelta(days=7)
    df["cut_us"]=df.signal_date-pd.Timedelta(days=1)
    df["rid"]=np.arange(len(df))
    specs=[
        ("DGS10",series_from_dict(ext["h15_daily"],"DGS10","DGS10"),"cut_h15"),
        ("DFII10",series_from_dict(ext["h15_daily"],"DFII10","DFII10"),"cut_h15"),
        ("BREAKEVEN10_PROXY",series_from_dict(ext["h15_daily"],"BREAKEVEN10_PROXY","BREAKEVEN10_PROXY"),"cut_h15"),
        ("BROAD_USD_INDEX",series_from_dict(ext["h10_daily"],"BROAD_USD_INDEX","BROAD_USD_INDEX"),"cut_h10"),
        ("EURUSD_QUOTE",series_from_dict(ext["h10_daily"],"EURUSD_QUOTE","EURUSD_QUOTE"),"cut_h10"),
        ("GBPUSD_QUOTE",series_from_dict(ext["h10_daily"],"GBPUSD_QUOTE","GBPUSD_QUOTE"),"cut_h10"),
        ("JPY_PER_USD",series_from_dict(ext["h10_daily"],"JPY_PER_USD","JPY_PER_USD"),"cut_h10"),
        ("CHF_PER_USD",series_from_dict(ext["h10_daily"],"CHF_PER_USD","CHF_PER_USD"),"cut_h10"),
        ("CNY_PER_USD",series_from_dict(ext["h10_daily"],"CNY_PER_USD","CNY_PER_USD"),"cut_h10"),
        ("VIX",series_from_dict(ext["vix_daily"],None,"VIX"),"cut_us"),
        ("NDX",series_from_dict(ext["nasdaq100_daily"],None,"NDX"),"cut_us"),
    ]
    for name,s,cut in specs:
        rr=s.rename(columns={"obs_date":f"{name}_obs_date"})
        df=df.sort_values(cut)
        df=pd.merge_asof(df,rr,left_on=cut,right_on=f"{name}_obs_date",direction="backward")
        df[f"{name}_age_days"]=(df.signal_date-df[f"{name}_obs_date"]).dt.days

    df=df.sort_values("rid").reset_index(drop=True)
    df["role"]=np.select(
        [df.signal_date.dt.year<=2021,df.signal_date.dt.year.between(2022,2024),df.signal_date.dt.year==2025],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025"],default="OTHER"
    )

    gold_feats=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
    core3=gold_feats+[
        "silver_r1","silver_r5","silver_r21","silver_age_days",
        "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
    ]
    core4=core3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]
    rates=["DGS10","DFII10","BREAKEVEN10_PROXY"]
    fx=["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]
    safe=core3+rates+fx+["VIX","NDX"]
    blocks=[
        ("GOLD_ONLY",gold_feats),("CORE3",core3),("CORE4",core4),("CORE3_SAFE_EXTERNAL",safe)
    ]

    cov=[]
    for h in [1,3,5]:
        for b,feats in blocks:
            mask=df[f"target_r{h}"].notna() & df[feats].notna().all(axis=1)
            cov.append({
                "horizon":h,"block":b,"all_n":int(mask.sum()),
                "train_history_n":int((mask&(df.role=="TRAIN_HISTORY")).sum()),
                "dev_n":int((mask&(df.role=="DEV")).sum()),
                "transport_2025_n":int((mask&(df.role=="TRANSPORT_2025")).sum()),
                "first_signal":str(df.loc[mask,"signal_date"].min().date()) if mask.any() else None,
                "last_signal":str(df.loc[mask,"signal_date"].max().date()) if mask.any() else None,
            })
    cov=pd.DataFrame(cov); cov.to_csv(OUT/"global_xau_coverage.csv",index=False)

    targets=[]
    for h in [1,3,5]:
        mask=(df.role=="DEV") & df[f"target_r{h}"].notna() & df[safe].notna().all(axis=1)
        x=df.loc[mask,f"target_r{h}"]
        targets.append({
            "horizon":h,"n":len(x),"up_share":float((x>0).mean()),
            "mean_return":float(x.mean()),"median_return":float(x.median()),"std_return":float(x.std(ddof=0))
        })
    targets=pd.DataFrame(targets); targets.to_csv(OUT/"global_xau_dev_targets.csv",index=False)

    age=[]
    q=df[df[safe].notna().all(axis=1)].copy()
    for name in rates+fx+["VIX","NDX"]:
        a=q[f"{name}_age_days"]
        age.append({"series":name,"p50":float(a.median()),"p95":float(a.quantile(.95)),"max":int(a.max())})
    pd.DataFrame(age).to_csv(OUT/"global_xau_external_staleness.csv",index=False)

    save_cols=["date","signal_date","role"]+[f"target_r{h}" for h in [1,3,5]]+sorted(set(core4+safe+[
        f"{x}_age_days" for x in rates+fx+["VIX","NDX"]
    ]))
    panel=df[save_cols].copy()
    panel.to_csv(OUT/"global_xau_readiness_panel.csv",index=False)

    c3=cov[cov.block=="CORE3_SAFE_EXTERNAL"].set_index("horizon")
    gates={
        "dev_ge_700":all(int(c3.loc[h,"dev_n"])>=700 for h in [1,3,5]),
        "train_ge_2000":int(c3.loc[5,"train_history_n"])>=2000,
        "transport_ge_200":all(int(c3.loc[h,"transport_2025_n"])>=200 for h in [1,3,5]),
    }
    status="PASS" if all(gates.values()) else "REVIEW"
    summary={
        "status":status,
        "target":"GLOBAL_XAU_STAKTRAKR_METALPRICEAPI_DAILY_SPOT_AVERAGE",
        "lineage":lineage,
        "coverage":cov.to_dict(orient="records"),
        "dev_targets":targets.to_dict(orient="records"),
        "gates":gates
    }
    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU — Data Readiness Result","",
        f"**Status:** **{status}**","",
        "Target: global XAU/USD daily spot-average research series (StakTrakr / MetalPriceAPI), not BIST Metal Price.","",
        "## Preferred panel coverage","",
        "| H | Train | DEV | 2025 frozen |",
        "|---|---:|---:|---:|"
    ]
    for h in [1,3,5]:
        r=c3.loc[h]
        lines.append(f"| H{h} | {int(r.train_history_n)} | {int(r.dev_n)} | {int(r.transport_2025_n)} |")
    lines += ["","## DEV target characteristics"]
    for _,r in targets.iterrows():
        lines.append(f"- H{int(r.horizon)}: n={int(r.n)}, UP={100*r.up_share:.1f}%, median={100*r.median_return:.3f}%, SD={100*r.std_return:.3f}%.")
    lines += ["","## Gate",json.dumps(gates,indent=2)]
    (OUT/"GLOBAL_XAU_READINESS_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary["hashes"]={p.name:sha(p) for p in files}
    (OUT/"global_xau_readiness_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("GLOBAL_XAU_READINESS="+json.dumps(summary,separators=(",",":")))
    print((OUT/"GLOBAL_XAU_READINESS_RESULT.md").read_text())

if __name__=="__main__":
    main()
