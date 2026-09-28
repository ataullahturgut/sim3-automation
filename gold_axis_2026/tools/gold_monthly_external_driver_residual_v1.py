from __future__ import annotations
import argparse, calendar, hashlib, io, json, math, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

FRED = {
 "BROAD_USD":"DTWEXBGS","EURUSD":"DEXUSEU","USDJPY":"DEXJPUS","GBPUSD":"DEXUSUK",
 "USDCHF":"DEXSZUS","USDCNY":"DEXCHUS","REAL10":"DFII10","NOM10":"DGS10","NOM2":"DGS2",
 "BE10":"T10YIE","VIX":"VIXCLS","SP500":"SP500","WTI":"DCOILWTICO"
}
# Conservative availability lags in calendar days. H.10 daily observations are
# released in weekly batches; 7d prevents month-end hindsight. H.15/EIA use 2d.
LAG_DAYS = {
 "BROAD_USD":7,"EURUSD":7,"USDJPY":7,"GBPUSD":7,"USDCHF":7,"USDCNY":7,
 "REAL10":2,"NOM10":2,"NOM2":2,"BE10":2,"VIX":0,"SP500":0,"WTI":2
}
DEV_START, DEV_END = "2022-04","2024-12"
TR_START, TR_END = "2025-01","2025-12"
MIN_HISTORY = 12
RIDGE_ALPHA = 10.0
CAP_MULT = 1.5
SCHEMA = "GOLD_MONTHLY_EXTERNAL_DRIVER_RESIDUAL_V1_2026-09-28"

def mshift(m,d):
    y,mo=map(int,m.split("-")); z=y*12+mo-1+d
    return f"{z//12:04d}-{z%12+1:02d}"

def mend(m):
    y,mo=map(int,m.split("-"))
    return pd.Timestamp(y,mo,calendar.monthrange(y,mo)[1])

def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def fred_csv(series_id):
    # Bound retrieval to the research window; downloading decades of daily history
    # is unnecessary and caused avoidable provider timeouts.
    url=(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
         f"&cosd=2020-01-01&coed=2025-12-31")
    raw=None
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-research/1.0"})
            with urllib.request.urlopen(req,timeout=45) as r:
                raw=r.read()
            break
        except Exception as e:
            last=e
            import time
            time.sleep(2*(attempt+1))
    if raw is None:
        raise RuntimeError(f"FRED_DOWNLOAD_FAILED {series_id}: {type(last).__name__}: {last}")
    df=pd.read_csv(io.BytesIO(raw))
    df.columns=["date","value"]
    df["date"]=pd.to_datetime(df["date"])
    df["value"]=pd.to_numeric(df["value"],errors="coerce")
    return df.dropna().sort_values("date").reset_index(drop=True), hashlib.sha256(raw).hexdigest()

def last_known(df, origin_month, lag_days):
    cutoff=mend(origin_month)-pd.Timedelta(days=lag_days)
    s=df[df.date<=cutoff]
    if s.empty: return np.nan
    return float(s.iloc[-1].value)

def safe_logret(a,b):
    if not np.isfinite(a) or not np.isfinite(b) or a<=0 or b<=0: return np.nan
    return float(math.log(a/b))

def build_external():
    series={}; source_hash={}
    for name,sid in FRED.items():
        df,h=fred_csv(sid); series[name]=df; source_hash[name]=h
    origins=[f"{y:04d}-{m:02d}" for y in range(2010,2026) for m in range(1,13)]
    rows={}
    for o in origins:
        p=mshift(o,-1)
        v={n:last_known(series[n],o,LAG_DAYS[n]) for n in FRED}
        pv={n:last_known(series[n],p,LAG_DAYS[n]) for n in FRED}
        broad=safe_logret(v["BROAD_USD"],pv["BROAD_USD"])
        eur=-safe_logret(v["EURUSD"],pv["EURUSD"])
        jpy=safe_logret(v["USDJPY"],pv["USDJPY"])
        gbp=-safe_logret(v["GBPUSD"],pv["GBPUSD"])
        chf=safe_logret(v["USDCHF"],pv["USDCHF"])
        cny=safe_logret(v["USDCNY"],pv["USDCNY"])
        aligned=np.array([eur,jpy,gbp,chf,cny],float)
        finite=aligned[np.isfinite(aligned)]
        breadth=float(np.mean(np.sign(finite))) if len(finite)>=4 else np.nan
        disp=float(np.std(finite)) if len(finite)>=4 else np.nan
        safehaven=float(np.mean([-jpy,-chf])-broad) if all(np.isfinite(x) for x in [jpy,chf,broad]) else np.nan
        curve=(v["NOM10"]-v["NOM2"]) if np.isfinite(v["NOM10"]) and np.isfinite(v["NOM2"]) else np.nan
        pcurve=(pv["NOM10"]-pv["NOM2"]) if np.isfinite(pv["NOM10"]) and np.isfinite(pv["NOM2"]) else np.nan
        rows[o]={
          "broad_usd_ret":broad,"eur_usdstrength_ret":eur,"jpy_usdstrength_ret":jpy,
          "gbp_usdstrength_ret":gbp,"chf_usdstrength_ret":chf,"cny_usdstrength_ret":cny,
          "usd_breadth":breadth,"fx_dispersion":disp,"safehaven_rotation":safehaven,
          "real10_change": float(v["REAL10"]-pv["REAL10"]) if np.isfinite(v["REAL10"]) and np.isfinite(pv["REAL10"]) else np.nan,
          "nom10_change": float(v["NOM10"]-pv["NOM10"]) if np.isfinite(v["NOM10"]) and np.isfinite(pv["NOM10"]) else np.nan,
          "curve_change": float(curve-pcurve) if np.isfinite(curve) and np.isfinite(pcurve) else np.nan,
          "breakeven10_change": float(v["BE10"]-pv["BE10"]) if np.isfinite(v["BE10"]) and np.isfinite(pv["BE10"]) else np.nan,
          "vix_ret": safe_logret(v["VIX"],pv["VIX"]),
          "sp500_ret": safe_logret(v["SP500"],pv["SP500"]),
          "wti_ret": safe_logret(v["WTI"],pv["WTI"]),
        }
    blocks={
      "DXY_ONLY":["broad_usd_ret"],
      "FX_MAJORS":["eur_usdstrength_ret","jpy_usdstrength_ret","gbp_usdstrength_ret","chf_usdstrength_ret","cny_usdstrength_ret"],
      "FX_GLOBAL":["broad_usd_ret","usd_breadth","fx_dispersion","safehaven_rotation"],
      "RATES":["real10_change","nom10_change","curve_change"],
      "RISK":["vix_ret","sp500_ret"],
      "INFLATION":["breakeven10_change"],
      "COMMODITY":["wti_ret"],
      "COMBINED_COMPACT":["broad_usd_ret","usd_breadth","safehaven_rotation","real10_change","curve_change","vix_ret","sp500_ret","breakeven10_change","wti_ret"],
      "FX_DROP_BROAD":["usd_breadth","fx_dispersion","safehaven_rotation"],
      "FX_DROP_BREADTH":["broad_usd_ret","fx_dispersion","safehaven_rotation"],
      "FX_DROP_DISPERSION":["broad_usd_ret","usd_breadth","safehaven_rotation"],
      "FX_DROP_SAFEHAVEN":["broad_usd_ret","usd_breadth","fx_dispersion"],
    }
    return rows,blocks,source_hash

def load_model(path, model_name):
    d=json.loads(Path(path).read_text())
    dev=d["dev"]["rows"]; tr=d["transport_2025"]["rows"]
    def norm(rows):
        out=[]
        for r in rows:
            out.append({
              "target":r["target"],"origin":r["origin"],"forecast":float(r["forecast"]),
              "actual":float(r["actual"]),"rw":float(r["rw"])
            })
        return out
    return {"name":model_name,"dev":norm(dev),"tr":norm(tr),"artifact_model_id":d.get("model_id")}

def metrics(rows,key="forecast"):
    a=np.array([r["actual"] for r in rows],float)
    f=np.array([r[key] for r in rows],float)
    rw=np.array([r["rw"] for r in rows],float)
    ae=np.abs(f-a)
    direction=(np.sign(f-rw)==np.sign(a-rw))
    return {"n":len(rows),"sum_ae":float(ae.sum()),"mae":float(ae.mean()),
            "rmse":float(np.sqrt(np.mean((f-a)**2))),
            "mape_pct":float(np.mean(ae/a)*100),
            "direction_correct":int(direction.sum()),"direction_n":len(rows),
            "worst_ae":float(ae.max())}

def valid_feature(rows, ext, cols):
    for r in rows:
        x=ext.get(r["origin"],{})
        if not all(c in x and np.isfinite(x[c]) for c in cols):
            return False
    return True

def prequential(rows, ext, cols):
    out=[]
    for i,r in enumerate(rows):
        z=dict(r); z["corrected_forecast"]=r["forecast"]; z["correction"]=0.0; z["eligible"]=False
        prior=rows[:i]
        if len(prior)>=MIN_HISTORY:
            train=[q for q in prior if all(np.isfinite(ext.get(q["origin"],{}).get(c,np.nan)) for c in cols)]
            if len(train)>=MIN_HISTORY and all(np.isfinite(ext.get(r["origin"],{}).get(c,np.nan)) for c in cols):
                X=np.array([[ext[q["origin"]][c] for c in cols] for q in train],float)
                y=np.array([q["actual"]-q["forecast"] for q in train],float)
                sc=StandardScaler().fit(X)
                md=Ridge(alpha=RIDGE_ALPHA,fit_intercept=True).fit(sc.transform(X),y)
                pred=float(md.predict(sc.transform(np.array([[ext[r["origin"]][c] for c in cols]],float)))[0])
                cap=CAP_MULT*float(np.median(np.abs(y)))
                pred=float(np.clip(pred,-cap,cap))
                z["correction"]=pred; z["corrected_forecast"]=float(r["forecast"]+pred); z["eligible"]=True
        out.append(z)
    return out

def freeze_fit_apply(dev,tr,ext,cols):
    train=[q for q in dev if all(np.isfinite(ext.get(q["origin"],{}).get(c,np.nan)) for c in cols)]
    X=np.array([[ext[q["origin"]][c] for c in cols] for q in train],float)
    y=np.array([q["actual"]-q["forecast"] for q in train],float)
    sc=StandardScaler().fit(X); md=Ridge(alpha=RIDGE_ALPHA).fit(sc.transform(X),y)
    cap=CAP_MULT*float(np.median(np.abs(y)))
    out=[]
    for r in tr:
        z=dict(r)
        if all(np.isfinite(ext.get(r["origin"],{}).get(c,np.nan)) for c in cols):
            x=np.array([[ext[r["origin"]][c] for c in cols]],float)
            p=float(np.clip(md.predict(sc.transform(x))[0],-cap,cap))
        else: p=0.0
        z["correction"]=p; z["corrected_forecast"]=float(r["forecast"]+p); out.append(z)
    coef={c:float(v) for c,v in zip(cols,md.coef_)}
    return out,{"n":len(train),"cap":cap,"intercept":float(md.intercept_),"coef_standardized":coef}

def stability_gate(base_rows,corr_rows):
    eligible=[r for r in corr_rows if r["eligible"]]
    if not eligible: return {"pass":False,"reason":"NO_ELIGIBLE_ROWS"}
    base_e=[r for r in base_rows if r["target"] in {z["target"] for z in eligible}]
    mb=metrics(base_e); mc=metrics(eligible,"corrected_forecast")
    diffs=np.array([abs(b["forecast"]-b["actual"])-abs(c["corrected_forecast"]-c["actual"]) for b,c in zip(base_e,eligible)])
    if len(diffs)>1:
        j=int(np.argmax(diffs)); robust=float(diffs.sum()-diffs[j])
    else: robust=-1e9
    y24_base=[r for r in base_e if r["target"].startswith("2024")]
    y24_corr=[r for r in eligible if r["target"].startswith("2024")]
    y24_imp=(metrics(y24_base)["sum_ae"]-metrics(y24_corr,"corrected_forecast")["sum_ae"]) if y24_base else 0.0
    passed=(mc["sum_ae"]<mb["sum_ae"] and robust>0 and y24_imp>0)
    return {"pass":bool(passed),"eligible_base":mb,"eligible_corrected":mc,
            "eligible_sum_ae_improvement":float(mb["sum_ae"]-mc["sum_ae"]),
            "improvement_excluding_single_best_month":robust,"y2024_sum_ae_improvement":float(y24_imp)}

def diagnostic(rows,ext,cols):
    vals=[]
    for r in rows:
        x=ext.get(r["origin"],{})
        if all(np.isfinite(x.get(c,np.nan)) for c in cols):
            vals.append((r,x))
    if len(vals)<8:return {}
    residual=np.array([r["actual"]-r["forecast"] for r,_ in vals],float)
    ae=np.abs(residual)
    out={}
    for c in cols:
        x=np.array([d[c] for _,d in vals],float)
        out[c]={"corr_signed_error":float(np.corrcoef(x,residual)[0,1]),
                "corr_abs_error":float(np.corrcoef(x,ae)[0,1])}
    return out

def run(chhho_path,deabc_path,outdir):
    ext,blocks,source_hash=build_external()
    models=[load_model(chhho_path,"ChHHO-ANFIS"),load_model(deabc_path,"DE-ABC-RBFNN")]
    result={"schema":SCHEMA,"authority":{
      "selection":"DEV_2022-04..2024-12_ONLY","2025":"FROZEN_REPORTING_ONLY",
      "neon_reads":0,"random_split":False,"target_month_external_data":False,
      "fred_conservative_lag_days":LAG_DAYS,"ridge_alpha_fixed":RIDGE_ALPHA,
      "min_prior_residuals":MIN_HISTORY,"correction_cap_trailing_median_ae_multiple":CAP_MULT},
      "fred_series":FRED,"fred_source_sha256":source_hash,
      "external_evidence_class":"HISTORICAL_MARKET_RECONSTRUCTION_WITH_CONSERVATIVE_AVAILABILITY_LAGS_NOT_ORIGINAL_RETRIEVAL_PIT",
      "strict_pit_crosscheck_available_in_neon":["DEXCHUS_ALFRED_PIT_ME","DGS10_ALFRED_PIT_ME","DFF_ALFRED_PIT_ME"],
      "blocks":blocks,
      "models":{}}
    for m in models:
        mr={"artifact_model_id":m["artifact_model_id"],"base_dev":metrics(m["dev"]),"base_2025":metrics(m["tr"]),
            "diagnostics":{},"dev_blocks":{}}
        candidates=[]
        for b,cols in blocks.items():
            mr["diagnostics"][b]=diagnostic(m["dev"],ext,cols)
            corr=prequential(m["dev"],ext,cols)
            gate=stability_gate(m["dev"],corr)
            mr["dev_blocks"][b]={"columns":cols,"full_metrics":metrics(corr,"corrected_forecast"),"gate":gate,"rows":corr}
            if b in ("DXY_ONLY","FX_MAJORS","FX_GLOBAL","RATES","RISK","INFLATION","COMMODITY","COMBINED_COMPACT") and gate.get("pass"):
                candidates.append((gate["eligible_corrected"]["sum_ae"],b))
        candidates.sort()
        selected=candidates[0][1] if candidates else "BASE"
        mr["selected_on_dev"]=selected
        if selected=="BASE":
            mr["transport_2025"]={"selected":"BASE","metrics":metrics(m["tr"]),"rows":m["tr"],"fit":None}
        else:
            tr,fit=freeze_fit_apply(m["dev"],m["tr"],ext,blocks[selected])
            mr["transport_2025"]={"selected":selected,"metrics":metrics(tr,"corrected_forecast"),"rows":tr,"fit":fit}
        result["models"][m["name"]]=mr
    result["external_snapshot_sha256"]=sha({"series":FRED,"lags":LAG_DAYS,"rows":ext})
    result["result_sha256"]=sha({k:v for k,v in result.items() if k!="result_sha256"})
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    (out/"gold_monthly_external_driver_result.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    # concise report
    lines=["# GOLD MONTHLY EXTERNAL DRIVER — RESULT","",f"External snapshot SHA: `{result['external_snapshot_sha256']}`",""]
    for name,mr in result["models"].items():
        lines += [f"## {name}",f"- Base DEV ΣAE: {mr['base_dev']['sum_ae']:.4f}",
                  f"- DEV-selected external block: **{mr['selected_on_dev']}**",
                  f"- Base 2025 ΣAE: {mr['base_2025']['sum_ae']:.4f}",
                  f"- Frozen external 2025 ΣAE: {mr['transport_2025']['metrics']['sum_ae']:.4f}","",
                  "| Block | Eligible DEV ΔΣAE | 2024 ΔΣAE | Gate |","|---|---:|---:|---|"]
        for b in ("DXY_ONLY","FX_MAJORS","FX_GLOBAL","RATES","RISK","INFLATION","COMMODITY","COMBINED_COMPACT"):
            g=mr["dev_blocks"][b]["gate"]
            if "eligible_sum_ae_improvement" in g:
                lines.append(f"| {b} | {g['eligible_sum_ae_improvement']:.4f} | {g['y2024_sum_ae_improvement']:.4f} | {'PASS' if g['pass'] else 'FAIL'} |")
        lines.append("")
    lines += ["## Governance","- Feature/block list frozen before outcome computation.",
              "- External features use conservative publication lags.",
              "- Prequential DEV correction uses only prior residuals.",
              "- 2025 fit uses DEV only; no 2025 residual updating or rescue.",
              "- Neon reads: 0."]
    (out/"GOLD_MONTHLY_EXTERNAL_DRIVER_RESULT_2026-09-28.md").write_text("\n".join(lines)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({n:{"selected":m["selected_on_dev"],"base_dev":m["base_dev"]["sum_ae"],"base_2025":m["base_2025"]["sum_ae"],"transport_2025":m["transport_2025"]["metrics"]["sum_ae"]} for n,m in result["models"].items()},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True); ap.add_argument("--deabc",required=True); ap.add_argument("--outdir",default="external_driver_out")
    a=ap.parse_args(); run(a.chhho,a.deabc,a.outdir)
