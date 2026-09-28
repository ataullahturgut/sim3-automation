from __future__ import annotations
import argparse, calendar, csv, hashlib, io, json, math, time, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import gold_monthly_external_driver_residual_v1 as core

# Official H.10-only path; no FRED or Neon read in model execution.\nRATE_PACKAGE="60f32914ab61dfab590e0e470153e3ae"
INDEX_PACKAGE="122e3bcb627e8e53f1bf72a1a09cfb81"
BASE="https://www.federalreserve.gov/datadownload/Output.aspx"
START="01/01/2020"; END="12/31/2025"; LAG_DAYS=7

def fetch_package(package):
    from urllib.parse import urlencode
    q=urlencode({"filetype":"csv","from":START,"label":"include","layout":"seriescolumn",
                 "rel":"H10","series":package,"to":END,"type":"package"})
    url=BASE+"?"+q
    last=None
    for i in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-research/1.0"})
            with urllib.request.urlopen(req,timeout=60) as r: raw=r.read()
            return raw,hashlib.sha256(raw).hexdigest()
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise RuntimeError(f"FED_H10_DOWNLOAD_FAILED {package} {type(last).__name__}: {last}")

def parse_ddp(raw):
    rows=list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    hdr=None
    for i,r in enumerate(rows):
        if r and r[0].strip().lower().replace(":","") in ("time period","date"):
            hdr=i; break
    if hdr is None:
        raise RuntimeError("FED_H10_TIME_PERIOD_HEADER_NOT_FOUND "+repr(rows[:8]))
    cols=[x.strip() for x in rows[hdr]]
    data=[]
    for r in rows[hdr+1:]:
        if not r or not r[0].strip(): continue
        try: dt=pd.to_datetime(r[0].strip())
        except Exception: continue
        z={"date":dt}
        for j,c in enumerate(cols[1:],1):
            if j>=len(r): continue
            try: z[c]=float(r[j])
            except Exception: z[c]=np.nan
        data.append(z)
    if not data: raise RuntimeError("FED_H10_NO_DATA")
    return pd.DataFrame(data).sort_values("date").reset_index(drop=True)

def find_col(df, token):
    for c in df.columns:
        if token in c: return c
    raise RuntimeError(f"FED_H10_SERIES_MISSING {token} cols={list(df.columns)}")

def month_end(m):
    y,mo=map(int,m.split("-"))
    return pd.Timestamp(y,mo,calendar.monthrange(y,mo)[1])

def last_before(df,col,m):
    cutoff=month_end(m)-pd.Timedelta(days=LAG_DAYS)
    s=df.loc[(df.date<=cutoff)&np.isfinite(pd.to_numeric(df[col],errors="coerce")),col]
    return float(s.iloc[-1]) if len(s) else np.nan

def mshift(m,d):
    y,mo=map(int,m.split("-")); z=y*12+mo-1+d
    return f"{z//12:04d}-{z%12+1:02d}"

def lret(a,b):
    return float(math.log(a/b)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan

def build():
    rr,hr=fetch_package(RATE_PACKAGE); ri,hi=fetch_package(INDEX_PACKAGE)
    rates=parse_ddp(rr); idx=parse_ddp(ri)
    C={
      "EUR":find_col(rates,"RXI$US_N.B.EU"),
      "GBP":find_col(rates,"RXI$US_N.B.UK"),
      "JPY":find_col(rates,"RXI_N.B.JA"),
      "CHF":find_col(rates,"RXI_N.B.SZ"),
      "CNY":find_col(rates,"RXI_N.B.CH"),
      "BROAD":find_col(idx,"JRXWTFB_N.B"),
    }
    ext={}
    for y in range(2021,2026):
      for mo in range(1,13):
        m=f"{y:04d}-{mo:02d}"; p=mshift(m,-1)
        cur={k:last_before(idx if k=="BROAD" else rates,c,m) for k,c in C.items()}
        prv={k:last_before(idx if k=="BROAD" else rates,c,p) for k,c in C.items()}
        broad=lret(cur["BROAD"],prv["BROAD"])
        eur=-lret(cur["EUR"],prv["EUR"]); gbp=-lret(cur["GBP"],prv["GBP"])
        jpy=lret(cur["JPY"],prv["JPY"]); chf=lret(cur["CHF"],prv["CHF"]); cny=lret(cur["CNY"],prv["CNY"])
        a=np.array([eur,jpy,gbp,chf,cny],float); f=a[np.isfinite(a)]
        ext[m]={
          "broad_usd_ret":broad,"eur_usdstrength_ret":eur,"jpy_usdstrength_ret":jpy,
          "gbp_usdstrength_ret":gbp,"chf_usdstrength_ret":chf,"cny_usdstrength_ret":cny,
          "usd_breadth":float(np.mean(np.sign(f))) if len(f)>=4 else np.nan,
          "fx_dispersion":float(np.std(f)) if len(f)>=4 else np.nan,
          "safehaven_rotation":float(np.mean([-jpy,-chf])-broad) if all(np.isfinite(x) for x in [jpy,chf,broad]) else np.nan,
        }
    blocks={
      "H10_BROAD_USD":["broad_usd_ret"],
      "H10_FX_MAJORS":["eur_usdstrength_ret","jpy_usdstrength_ret","gbp_usdstrength_ret","chf_usdstrength_ret","cny_usdstrength_ret"],
      "H10_FX_GLOBAL":["broad_usd_ret","usd_breadth","fx_dispersion","safehaven_rotation"],
      "H10_DROP_BROAD":["usd_breadth","fx_dispersion","safehaven_rotation"],
      "H10_DROP_BREADTH":["broad_usd_ret","fx_dispersion","safehaven_rotation"],
      "H10_DROP_DISP":["broad_usd_ret","usd_breadth","safehaven_rotation"],
      "H10_DROP_SAFEHAVEN":["broad_usd_ret","usd_breadth","fx_dispersion"],
    }
    return ext,blocks,{"rates_sha256":hr,"indexes_sha256":hi,"series_columns":C}

def run(chhho,deabc,outdir):
    ext,blocks,src=build()
    models=[core.load_model(chhho,"ChHHO-ANFIS"),core.load_model(deabc,"DE-ABC-RBFNN")]
    out={"schema":"GOLD_MONTHLY_FX_H10_RESIDUAL_V1_2026-09-28",
         "authority":{"source":"Federal Reserve Board H.10 DDP","availability_lag_days":LAG_DAYS,
                      "evidence_class":"OFFICIAL_CURRENT_HISTORICAL_SERIES_WITH_CONSERVATIVE_RELEASE_LAG_NOT_REALTIME_VINTAGE",
                      "selection":"DEV_ONLY","2025":"FROZEN_REPORTING_ONLY","base_models_frozen":True,
                      "random_split":False,"neon_reads":0},
         "source":src,"blocks":blocks,"models":{}}
    primary=("H10_BROAD_USD","H10_FX_MAJORS","H10_FX_GLOBAL")
    for m in models:
        mr={"base_dev":core.metrics(m["dev"]),"base_2025":core.metrics(m["tr"]),"dev_blocks":{}}
        cand=[]
        for b,cols in blocks.items():
            corr=core.prequential(m["dev"],ext,cols); gate=core.stability_gate(m["dev"],corr)
            mr["dev_blocks"][b]={"columns":cols,"diagnostics":core.diagnostic(m["dev"],ext,cols),
                                  "full_metrics":core.metrics(corr,"corrected_forecast"),"gate":gate,"rows":corr}
            if b in primary and gate.get("pass"): cand.append((gate["eligible_corrected"]["sum_ae"],b))
        cand.sort(); sel=cand[0][1] if cand else "BASE"; mr["selected_on_dev"]=sel
        if sel=="BASE": mr["transport_2025"]={"selected":"BASE","metrics":core.metrics(m["tr"]),"rows":m["tr"],"fit":None}
        else:
            tr,fit=core.freeze_fit_apply(m["dev"],m["tr"],ext,blocks[sel])
            mr["transport_2025"]={"selected":sel,"metrics":core.metrics(tr,"corrected_forecast"),"rows":tr,"fit":fit}
        out["models"][m["name"]]=mr
    out["result_sha256"]=core.sha({k:v for k,v in out.items() if k!="result_sha256"})
    d=Path(outdir);d.mkdir(parents=True,exist_ok=True)
    (d/"gold_monthly_fx_h10_result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    lines=["# GOLD MONTHLY FX H10 EXTERNAL RESULT",""]
    for n,m in out["models"].items():
        lines += [f"## {n}",f"- Base DEV ΣAE: {m['base_dev']['sum_ae']:.4f}",f"- DEV selected: **{m['selected_on_dev']}**",
                  f"- Base 2025 ΣAE: {m['base_2025']['sum_ae']:.4f}",f"- Frozen 2025 ΣAE: {m['transport_2025']['metrics']['sum_ae']:.4f}","",
                  "| Block | Eligible DEV ΔΣAE | 2024 ΔΣAE | Gate |","|---|---:|---:|---|"]
        for b in blocks:
            g=m["dev_blocks"][b]["gate"]
            if "eligible_sum_ae_improvement" in g:
                lines.append(f"| {b} | {g['eligible_sum_ae_improvement']:.4f} | {g['y2024_sum_ae_improvement']:.4f} | {'PASS' if g['pass'] else 'FAIL'} |")
        lines.append("")
    lines += ["## Governance","- Federal Reserve H.10 official historical FX data.","- 7-day conservative origin availability cutoff.",
              "- Base models unchanged; only residual correction layer tested.","- DEV selection only; 2025 frozen transport only.","- Neon reads: 0."]
    (d/"GOLD_MONTHLY_FX_H10_RESULT_2026-09-28.md").write_text("\n".join(lines)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({n:{"selected":m["selected_on_dev"],"base_dev":m["base_dev"]["sum_ae"],"base_2025":m["base_2025"]["sum_ae"],"transport_2025":m["transport_2025"]["metrics"]["sum_ae"]} for n,m in out["models"].items()},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--chhho",required=True);p.add_argument("--deabc",required=True);p.add_argument("--outdir",default="fx_h10_out")
    a=p.parse_args();run(a.chhho,a.deabc,a.outdir)
