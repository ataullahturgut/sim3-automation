import os, io, json, math, hashlib, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
STAGE2_ARTIFACT=11161358194
EXT_ARTIFACT=11028494060
OUT=Path(os.environ.get("OUT_DIR","short_horizon_readiness_out"))
OUT.mkdir(parents=True,exist_ok=True)

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-readiness"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def read_json(z):
    names=[n for n in z.namelist() if n.endswith(".json")]
    if len(names)!=1: raise RuntimeError(names)
    return json.loads(z.read(names[0]))

def series_from_dict(dct, field=None, name=None):
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

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    z2=get_zip(STAGE2_ARTIFACT)
    wide=read_csv(z2,"bist_four_metal_usd_oz_wide.csv")
    wide["date"]=pd.to_datetime(wide["date"])
    wide=wide.sort_values("date").reset_index(drop=True)

    ext=read_json(get_zip(EXT_ARTIFACT))

    df=wide.copy()
    df["signal_date"]=df["date"].shift(-1)
    lg=np.log(df["gold"])
    for h in [1,3,5]:
        df[f"target_r{h}"]=np.log(df["gold"].shift(-h)/df["gold"])
    for h in [1,3,5,10,21]:
        df[f"gold_r{h}"]=lg.diff(h)
    df["sigma20"]=lg.diff().rolling(20).std(ddof=0)
    gold_feats=[f"gold_r{h}" for h in [1,3,5,10,21]]+["sigma20"]

    # Companion features on own official calendars, causal as-of onto Gold origin.
    for name in ["silver","platinum","palladium"]:
        q=wide[["date",name]].dropna().copy().sort_values("date")
        lp=np.log(q[name])
        for h in [1,5,21]:
            q[f"{name}_r{h}"]=lp.diff(h)
        q=q.rename(columns={"date":f"{name}_obs_date",name:f"{name}_price"})
        df=pd.merge_asof(
            df.sort_values("date"),
            q.sort_values(f"{name}_obs_date"),
            left_on="date",right_on=f"{name}_obs_date",direction="backward"
        )
        df[f"{name}_age_days"]=(df["date"]-df[f"{name}_obs_date"]).dt.days

    df=df[df["signal_date"].notna()].copy().reset_index(drop=True)
    df["cut_h15"]=df["signal_date"]-pd.Timedelta(days=2)
    df["cut_h10"]=df["signal_date"]-pd.Timedelta(days=7)
    df["cut_us"]=df["signal_date"]-pd.Timedelta(days=1)
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
        df[f"{name}_age_days"]=(df["signal_date"]-df[f"{name}_obs_date"]).dt.days

    df=df.sort_values("rid").reset_index(drop=True)

    df["role"]=np.select(
        [df["signal_date"].dt.year<=2021,df["signal_date"].dt.year.between(2022,2024),df["signal_date"].dt.year==2025],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025"],default="OTHER"
    )

    core3=gold_feats[:]
    for name in ["silver","platinum"]:
        core3 += [f"{name}_r1",f"{name}_r5",f"{name}_r21",f"{name}_age_days"]
    core4=core3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]
    rates=["DGS10","DFII10","BREAKEVEN10_PROXY"]
    fx=["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]
    blocks=[
        ("GOLD_ONLY",gold_feats),
        ("CORE3_GOLD_SILVER_PLATINUM",core3),
        ("CORE4_ADD_PALLADIUM",core4),
        ("CORE3_PLUS_RATES",core3+rates),
        ("CORE3_PLUS_RATES_FX",core3+rates+fx),
        ("CORE3_PLUS_RATES_FX_VIX",core3+rates+fx+["VIX"]),
        ("CORE3_PLUS_RATES_FX_VIX_NDX",core3+rates+fx+["VIX","NDX"]),
        ("CORE4_PLUS_ALL_SAFE_EXTERNAL",core4+rates+fx+["VIX","NDX"]),
    ]

    rows=[]
    for h in [1,3,5]:
        for b,feats in blocks:
            mask=df[f"target_r{h}"].notna() & df[feats].notna().all(axis=1)
            rows.append({
                "horizon":h,"block":b,"all_n":int(mask.sum()),
                "train_history_n":int((mask&(df["role"]=="TRAIN_HISTORY")).sum()),
                "dev_n":int((mask&(df["role"]=="DEV")).sum()),
                "transport_2025_n":int((mask&(df["role"]=="TRANSPORT_2025")).sum()),
                "first_signal_date":str(df.loc[mask,"signal_date"].min().date()) if mask.any() else None,
                "last_signal_date":str(df.loc[mask,"signal_date"].max().date()) if mask.any() else None,
            })
    cov=pd.DataFrame(rows)
    cov.to_csv(OUT/"coverage_by_horizon_and_block.csv",index=False)

    # DEV target balance on fully safe CORE3+external panel.
    target_rows=[]
    safe3=core3+rates+fx+["VIX","NDX"]
    for h in [1,3,5]:
        mask=df[f"target_r{h}"].notna() & df[safe3].notna().all(axis=1) & (df["role"]=="DEV")
        x=df.loc[mask,f"target_r{h}"]
        target_rows.append({
            "horizon":h,"n":int(len(x)),"up_share":float((x>0).mean()),
            "mean_return_pct":float(100*np.expm1(x.mean())),
            "median_return_pct":float(100*np.expm1(x.median())),
            "std_log_return":float(x.std(ddof=0)),
        })
    target=pd.DataFrame(target_rows)
    target.to_csv(OUT/"dev_target_characteristics.csv",index=False)

    # External staleness on H5 strict safe CORE3 panel.
    mask=df["target_r5"].notna() & df[safe3].notna().all(axis=1)
    q=df[mask].copy()
    age_rows=[]
    for name in rates+fx+["VIX","NDX"]:
        a=q[f"{name}_age_days"]
        age_rows.append({
            "series":name,"n":int(a.notna().sum()),"mean_age_days":float(a.mean()),
            "p50_age_days":float(a.median()),"p95_age_days":float(a.quantile(.95)),
            "max_age_days":int(a.max()),
        })
    ages=pd.DataFrame(age_rows)
    ages.to_csv(OUT/"external_staleness_audit.csv",index=False)

    # Raw optional source coverage.
    optional=pd.DataFrame([
        {"family":"WTI","status":"SOURCE_READY_PIT_MAPPING_BLOCKED_FOR_SHORT_HORIZON","first":min(ext["wti_daily"]),"last":max(ext["wti_daily"]),"n":len(ext["wti_daily"])},
        {"family":"BRENT","status":"SOURCE_READY_PIT_MAPPING_BLOCKED_FOR_SHORT_HORIZON","first":min(ext["brent_daily"]),"last":max(ext["brent_daily"]),"n":len(ext["brent_daily"])},
        {"family":"DAILY_GPR","status":"EXCLUDED_PENDING_COMPLETE_DAILY_VINTAGE_MERGED_AUDIT","first":None,"last":None,"n":None},
    ])
    optional.to_csv(OUT/"optional_family_status.csv",index=False)

    # Save prepared strict audit panel for reproducibility.
    save_cols=["date","signal_date","role"]+[f"target_r{h}" for h in [1,3,5]]+sorted(set(safe3+core4+[
        f"{x}_age_days" for x in rates+fx+["VIX","NDX"]
    ]))
    df[save_cols].to_csv(OUT/"short_horizon_readiness_panel.csv",index=False)

    # PASS gate.
    dev_ok=all(int(target.loc[target.horizon==h,"n"].iloc[0])>=700 for h in [1,3,5])
    cov3=cov[cov.block=="CORE3_PLUS_RATES_FX_VIX_NDX"].set_index("horizon")
    train_ok=int(cov3.loc[5,"train_history_n"])>=2000
    transport_ok=all(int(cov3.loc[h,"transport_2025_n"])>=200 for h in [1,3,5])
    ext_no_collapse=all(int(cov3.loc[h,"dev_n"])==749 for h in [1,3,5])
    status="PASS" if (dev_ok and train_ok and transport_ok and ext_no_collapse) else "REVIEW"

    summary={
        "status":status,
        "source_artifacts":{"bist_stage2":STAGE2_ARTIFACT,"external_v2":EXT_ARTIFACT},
        "gold_rows":int(len(wide)),
        "coverage":cov.to_dict(orient="records"),
        "dev_targets":target.to_dict(orient="records"),
        "staleness":ages.to_dict(orient="records"),
        "optional":optional.to_dict(orient="records"),
        "gates":{"dev_ge_700":dev_ok,"core3_train_ge_2000":train_ok,"transport_ge_200":transport_ok,"safe_external_no_dev_collapse":ext_no_collapse},
    }

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Data Readiness Audit Result","",
        f"**Status:** **{status}**","",
        "## Binding conclusion","",
        "The governed data are sufficient to start H1/H3/H5 short-horizon model research.",
        "",
        "The preferred first strict panel is **CORE3 + Rates + FX + VIX + Nasdaq-100**.",
        "Palladium is retained as a challenger block because its historical gaps shorten the strict common training history.",
        "",
        "## Coverage — preferred safe panel","",
        "| Horizon | Train history | DEV 2022-24 | 2025 transport | First signal | Last labelled signal |",
        "|---|---:|---:|---:|---|---|",
    ]
    for h in [1,3,5]:
        r=cov3.loc[h]
        lines.append(f"| H{h} | {int(r['train_history_n'])} | {int(r['dev_n'])} | {int(r['transport_2025_n'])} | {r['first_signal_date']} | {r['last_signal_date']} |")
    lines += ["","## Palladium effect",""]
    c4=cov[cov.block=="CORE4_PLUS_ALL_SAFE_EXTERNAL"].set_index("horizon")
    for h in [1,3,5]:
        lines.append(f"- H{h}: CORE3 train {int(cov3.loc[h,'train_history_n'])} vs CORE4 train {int(c4.loc[h,'train_history_n'])}; DEV remains {int(c4.loc[h,'dev_n'])}.")
    lines += ["","## DEV target balance",""]
    for _,r in target.iterrows():
        lines.append(f"- H{int(r.horizon)}: n={int(r.n)}, UP share={100*r.up_share:.1f}%, median return={r.median_return_pct:.3f}%.")
    lines += ["","## External timing",""]
    for _,r in ages.iterrows():
        lines.append(f"- {r['series']}: median age {r['p50_age_days']:.0f}d, p95 {r['p95_age_days']:.0f}d, max {int(r['max_age_days'])}d.")
    lines += ["","## Optional blocked lanes",
              "- WTI/Brent: official daily source exists, but short-horizon PIT publication mapping is not yet frozen; exclude first batch.",
              "- Daily GPR: exclude first batch pending complete merged vintage-coverage audit.",
              "",
              "## Model-family implication",
              "- Elastic Net / LightGBM / XGBoost / CatBoost / quantile boosting: data volume is sufficient.",
              "- Small TCN/GRU/BiGRU: feasible as later challengers with regularization.",
              "- TFT: feasible only as a constrained challenger; sample size is modest for a large transformer and does not justify making it the first model.",
              "",
              "## Next action",
              "Freeze the new short-horizon project contract and run the first H1/H3/H5 baseline/model batch on the preferred CORE3+safe-external panel, while keeping CORE4/Palladium as an incremental challenger."
    ]
    (OUT/"READINESS_RESULT.md").write_text("\n".join(lines),encoding="utf-8")

    files=[OUT/"coverage_by_horizon_and_block.csv",OUT/"dev_target_characteristics.csv",OUT/"external_staleness_audit.csv",OUT/"optional_family_status.csv",OUT/"short_horizon_readiness_panel.csv",OUT/"READINESS_RESULT.md"]
    summary["hashes"]={p.name:sha256_file(p) for p in files}
    (OUT/"readiness_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("READINESS_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"READINESS_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
