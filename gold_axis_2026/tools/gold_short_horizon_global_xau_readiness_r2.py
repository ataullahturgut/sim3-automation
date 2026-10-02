from __future__ import annotations
import os,io,json,hashlib,zipfile,urllib.request
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
EXT_ARTIFACT=11028494060
OUT=Path(os.environ.get("OUT_DIR","global_xau_readiness_r2_out"))
OUT.mkdir(parents=True,exist_ok=True)
METALS={"gold":"Gold","silver":"Silver","platinum":"Platinum","palladium":"Palladium"}

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"global-xau-readiness-r2/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-readiness-r2"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_json(z):
    names=[n for n in z.namelist() if n.endswith(".json")]
    if len(names)!=1:raise RuntimeError(names)
    return json.loads(z.read(names[0]))

def series_from_dict(dct,field=None,name=None):
    rows=[]
    for ds,v in dct.items():
        val=v if field is None else v.get(field)
        if val is None:continue
        rows.append((pd.to_datetime(ds),float(val)))
    return pd.DataFrame(rows,columns=["obs_date",name]).sort_values("obs_date")

def load_public_metals(stak_ref,cutoff):
    by=defaultdict(dict); prov=defaultdict(dict); hashes={}
    for year in range(2010,pd.Timestamp(cutoff).year+1):
        raw=get_bytes(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{stak_ref}/data/spot-history-{year}.json")
        hashes[str(year)]=hashlib.sha256(raw).hexdigest()
        rows=json.loads(raw)
        for r in rows:
            metal=str(r.get("metal") or "")
            if metal not in METALS.values():continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts) or ts>pd.Timestamp(cutoff)+pd.Timedelta(days=1):continue
            d=ts.normalize()
            if d.weekday()>=5:continue
            try:v=float(r.get("spot"))
            except:continue
            if not np.isfinite(v) or v<=0:continue
            by[metal][d]=v
            prov[metal][d]=(str(r.get("source") or ""),str(r.get("provider") or ""))
    common=sorted(set.intersection(*(set(by[m]) for m in METALS.values())))
    if not common:raise RuntimeError("NO_COMMON_PUBLIC_METAL_DATES")
    df=pd.DataFrame({"date":common})
    for key,m in METALS.items():df[key]=[by[m][d] for d in common]
    provider_counts={}
    for key,m in METALS.items():
        q=defaultdict(int)
        for d in common:q["|".join(prov[m][d])]+=1
        provider_counts[key]=dict(sorted(q.items(),key=lambda x:-x[1]))
    return df,{"stak_ref":stak_ref,"annual_payload_sha256":hashes,"provider_counts":provider_counts,
               "first":str(df.date.min().date()),"last":str(df.date.max().date()),"n":int(len(df))}

def main():
    stak_ref=os.environ["STAK_REF"]
    cutoff=os.environ.get("CUTOFF","2026-09-30")
    metal,source_meta=load_public_metals(stak_ref,cutoff)
    df=metal[["date","gold"]].copy().sort_values("date").reset_index(drop=True)
    df["feature_cutoff_date"]=df["date"]
    df["forecast_issue_date"]=df["date"].shift(-1)
    df["target_start_date"]=df["date"]
    lg=np.log(df.gold)
    for h in [1,3,5]:
        df[f"target_end_date_h{h}"]=df["date"].shift(-h)
        df[f"target_r{h}"]=np.log(df.gold.shift(-h)/df.gold)
    for h in [1,3,5,10,21]:df[f"gold_r{h}"]=lg.diff(h)
    df["sigma20"]=lg.diff().rolling(20).std(ddof=0)

    for name in ["silver","platinum","palladium"]:
        q=metal[["date",name]].copy()
        lp=np.log(q[name])
        for h in [1,5,21]:q[f"{name}_r{h}"]=lp.diff(h)
        q=q.rename(columns={"date":f"{name}_obs_date",name:f"{name}_price"})
        df=pd.merge_asof(df.sort_values("date"),q.sort_values(f"{name}_obs_date"),
                         left_on="date",right_on=f"{name}_obs_date",direction="backward")
        df[f"{name}_age_days"]=(df.date-df[f"{name}_obs_date"]).dt.days

    df=df[df.forecast_issue_date.notna()].copy().reset_index(drop=True)
    ext=read_json(get_zip(EXT_ARTIFACT))
    df["cut_h15"]=df.forecast_issue_date-pd.Timedelta(days=2)
    df["cut_h10"]=df.forecast_issue_date-pd.Timedelta(days=7)
    df["cut_us"]=df.forecast_issue_date-pd.Timedelta(days=1)
    df["rid"]=np.arange(len(df))
    specs=[
        ("DGS10",series_from_dict(ext["h15_daily"],"DGS10","DGS10"),"cut_h15"),
        ("DFII10",series_from_dict(ext["h15_daily"],"DFII10","DFII10"),"cut_h15"),
        ("BREAKEVEN10_PROXY",series_from_dict(ext["h15_daily"],"BREAKEVEN10_PROXY","BREAKEVEN10_PROXY"),"cut_h15"),
        ("BROAD_USD_INDEX",series_from_dict(ext["h10_daily"],"BROAD_USD_INDEX","BROAD_USD_INDEX"),"cut_h10"),
        ("EURUSD_QUOTE",series_from_dict(ext["h10_daily"],"EURUSD_QUOTE","EURUSD_QUOTE"),"cut_h10"),
        ("GBPUSD_QUOTE",series_from_dict(ext["h10_daily"],"GBPUSDUSD_QUOTE" if False else "GBPUSD_QUOTE","GBPUSD_QUOTE"),"cut_h10"),
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
        df[f"{name}_age_days"]=(df.forecast_issue_date-df[f"{name}_obs_date"]).dt.days
    df=df.sort_values("rid").reset_index(drop=True)

    df["role"]=np.select(
        [df.forecast_issue_date.dt.year<=2021,df.forecast_issue_date.dt.year.between(2022,2024),
         df.forecast_issue_date.dt.year==2025,df.forecast_issue_date.dt.year==2026],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025","OPENED_2026"],default="OTHER")

    gold=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
    core3=gold+["silver_r1","silver_r5","silver_r21","silver_age_days",
                "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"]
    core4=core3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]
    rates=["DGS10","DFII10","BREAKEVEN10_PROXY"]
    fx=["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]
    safe=core3+rates+fx+["VIX","NDX"]
    blocks=[("GOLD_ONLY",gold),("CORE3",core3),("CORE4",core4),("CORE3_SAFE_EXTERNAL",safe)]

    cov=[]
    for h in [1,3,5]:
      for b,feats in blocks:
        mask=df[f"target_r{h}"].notna() & df[feats].notna().all(axis=1)
        cov.append({"horizon":h,"block":b,"all_n":int(mask.sum()),
          "train_history_n":int((mask&(df.role=="TRAIN_HISTORY")).sum()),
          "dev_n":int((mask&(df.role=="DEV")).sum()),
          "transport_2025_n":int((mask&(df.role=="TRANSPORT_2025")).sum()),
          "opened_2026_n":int((mask&(df.role=="OPENED_2026")).sum()),
          "first_issue":str(df.loc[mask,"forecast_issue_date"].min().date()) if mask.any() else None,
          "last_issue":str(df.loc[mask,"forecast_issue_date"].max().date()) if mask.any() else None})
    cov=pd.DataFrame(cov);cov.to_csv(OUT/"global_xau_r2_coverage.csv",index=False)

    save_cols=["date","feature_cutoff_date","forecast_issue_date","target_start_date","role"]+[
        f"target_end_date_h{h}" for h in [1,3,5]]+[f"target_r{h}" for h in [1,3,5]]+sorted(set(core4+safe+[
        f"{x}_age_days" for x in rates+fx+["VIX","NDX"]]))
    panel=df[save_cols].copy()
    panel.to_csv(OUT/"global_xau_r2_readiness_panel.csv",index=False)

    c3=cov[cov.block=="CORE3"].set_index("horizon")
    gates={
      "dev_ge_700":all(int(c3.loc[h,"dev_n"])>=700 for h in [1,3,5]),
      "train_ge_2000":int(c3.loc[5,"train_history_n"])>=2000,
      "transport_2025_ge_200":all(int(c3.loc[h,"transport_2025_n"])>=200 for h in [1,3,5]),
      "aug_sep_2026_present":str(panel.forecast_issue_date.max())[:7]>="2026-09",
    }
    summary={"status":"PASS" if all(gates.values()) else "REVIEW",
      "identity":"GLOBAL_XAU_PUBLIC_STAKTRAKR_R2",
      "source_meta":source_meta,"cutoff":cutoff,"external_artifact":EXT_ARTIFACT,
      "timeline_semantics":{
        "feature_cutoff_date":"last Gold observation used by feature transforms",
        "forecast_issue_date":"next retained weekday Gold observation date; old signal_date replacement",
        "target_end_date_hN":"exact retained weekday Gold date ending forward HN return"},
      "coverage":cov.to_dict(orient="records"),"gates":gates}
    summary["hashes"]={p.name:sha(p) for p in OUT.iterdir()}
    (OUT/"global_xau_r2_readiness_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    lines=["# GOLD SHORT-HORIZON GLOBAL XAU — R2 Data Readiness","",
      f"**Status:** **{summary['status']}**","",
      f"Identity: **{summary['identity']}**",
      f"Pinned StakTrakr commit: {stak_ref}",
      f"Public common weekday coverage: {source_meta['first']} .. {source_meta['last']} (n={source_meta['n']})","",
      "R2 is a full-history reconstruction at one pinned public StakTrakr commit. It is not a silent append to the prior Neon snapshot.","",
      "## CORE3 coverage","",
      "| H | Train | DEV | 2025 | Opened 2026 | Last issue |","|---|---:|---:|---:|---:|---|"]
    for h in [1,3,5]:
      r=c3.loc[h];lines.append(f"| H{h} | {int(r.train_history_n)} | {int(r.dev_n)} | {int(r.transport_2025_n)} | {int(r.opened_2026_n)} | {r.last_issue} |")
    lines += ["","## Gate",json.dumps(gates,indent=2)]
    (OUT/"R2_READINESS_RESULT.md").write_text("\n".join(lines)+"\n")
    print("GLOBAL_XAU_R2_READINESS="+json.dumps(summary,separators=(",",":")))
    print((OUT/"R2_READINESS_RESULT.md").read_text())

if __name__=="__main__":main()
