import os,io,json,hashlib,zipfile,glob
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
STAGE1_ART=11167138282
STAGE2_ART=11167744845
OUT=Path("stage4_all"); OUT.mkdir(exist_ok=True)

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def rcsv(z,suffix):
    n=[x for x in z.namelist() if x.endswith(suffix)]
    if len(n)!=1: raise RuntimeError((suffix,n))
    return pd.read_csv(io.BytesIO(z.read(n[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

# Load TFT summaries
files=glob.glob("task*/stage4_tft_*_summary.json")
summ={json.loads(Path(p).read_text())["task"]:json.loads(Path(p).read_text()) for p in files}
if set(summ)!={"class","quant"}:
    raise RuntimeError(f"Missing summaries {summ.keys()}")
cls=summ["class"]; quant=summ["quant"]

# Authoritative classical references
z1=get_zip(STAGE1_ART)
dec1=rcsv(z1,"stage1_decisions.csv")
m1=rcsv(z1,"stage1_metrics_all.csv")
qs1=rcsv(z1,"stage1_quantile_summary_all.csv")

z2=get_zip(STAGE2_ART)
m2=rcsv(z2,"stage2_aggregate_metrics.csv")
yr2=rcsv(z2,"stage2_year_metrics.csv")
qs2=rcsv(z2,"stage2_quantile_summary.csv")
qy2=rcsv(z2,"stage2_quantile_year_summary.csv")

rows=[]
for h in [1,3,5]:
    # direction references
    if h==3:
        cr=m2[(m2.feature_block=="CORE3")&(m2["head"]=="direction")].iloc[0]
        classical=float(cr.brier); classical_co=float(cr.logloss)
        years_ref={yr:float(yr2[(yr2.feature_block=="CORE3")&(yr2["head"]=="direction")&(yr2.year==yr)].iloc[0].brier) for yr in [2022,2023,2024]}
        baseline=None; baseline_co=None
    else:
        dd=dec1[(dec1.horizon==h)&(dec1["head"]=="direction")].iloc[0]
        classical=float(dd.primary); classical_co=float(dd.support_metric)
        baseline=float(dd.baseline); baseline_co=float(dd.support_baseline)
        # year classical from exact selected Stage1 candidate
        cand=m1[(m1.horizon==h)&(m1["head"]=="direction")&(m1.feature_block==dd.feature_block)&(m1.model==dd.model)]
        # Stage1 aggregate artifact does not retain yearly rows; no yearly promotion for supporting H1/H5.
        years_ref=None

    t=cls["horizons"][str(h)]["aggregate"]
    rel=(classical-t["brier"])/classical
    co_ok=t["logloss"]<=classical_co
    if h==3:
        year_ok=True; yrels={}
        for yr in [2022,2023,2024]:
            v=cls["horizons"][str(h)]["years"][str(yr)]["brier"]
            rr=(years_ref[yr]-v)/years_ref[yr]; yrels[str(yr)]=rr
            if rr < -0.03: year_ok=False
        gate=rel>=0.005 and co_ok and year_ok
        extra="H3_CLASSICAL_GATE"
    else:
        base_rel=(baseline-t["brier"])/baseline
        baseline_gate=base_rel>=0.01 and t["logloss"]<=baseline_co
        gate=rel>=0.005 and co_ok and baseline_gate
        year_ok=None; yrels={}
        extra=f"BASELINE_REL={base_rel}"
    rows.append({"horizon":h,"head":"direction","tft_primary":t["brier"],"classical_primary":classical,"rel_vs_classical":rel,"co_ok":co_ok,"year_ok":year_ok,"gate":gate,"detail":extra,"year_rel":json.dumps(yrels)})

    # return references, using TFT q50
    if h==3:
        cr=m2[(m2.feature_block=="GOLD_ONLY")&(m2["head"]=="return")].iloc[0]
        classical=float(cr.mae); classical_co=float(cr.rmse)
        years_ref={yr:float(yr2[(yr2.feature_block=="GOLD_ONLY")&(yr2["head"]=="return")&(yr2.year==yr)].iloc[0].mae) for yr in [2022,2023,2024]}
    else:
        dd=dec1[(dec1.horizon==h)&(dec1["head"]=="return")].iloc[0]
        classical=float(dd.primary); classical_co=float(dd.support_metric)
        years_ref=None
    t=quant["horizons"][str(h)]["aggregate"]
    rel=(classical-t["mae_q50"])/classical
    co_ok=t["rmse_q50"]<=classical_co
    if h==3:
        year_ok=True; yrels={}
        for yr in [2022,2023,2024]:
            v=quant["horizons"][str(h)]["years"][str(yr)]["mae_q50"]
            rr=(years_ref[yr]-v)/years_ref[yr]; yrels[str(yr)]=rr
            if rr < -0.03: year_ok=False
        gate=rel>=0.005 and co_ok and year_ok
    else:
        year_ok=None; yrels={}; gate=rel>=0.005 and co_ok
    rows.append({"horizon":h,"head":"return","tft_primary":t["mae_q50"],"classical_primary":classical,"rel_vs_classical":rel,"co_ok":co_ok,"year_ok":year_ok,"gate":gate,"detail":"","year_rel":json.dumps(yrels)})

    # quantile
    if h==3:
        classical=float(qs2[qs2.feature_block=="GOLD_ONLY"].iloc[0].mean_pinball)
        years_ref={yr:float(qy2[(qy2.feature_block=="GOLD_ONLY")&(qy2.year==yr)].iloc[0].mean_pinball) for yr in [2022,2023,2024]}
    else:
        dd=dec1[(dec1.horizon==h)&(dec1["head"]=="quantile")].iloc[0]
        classical=float(dd.primary); years_ref=None
    rel=(classical-t["mean_pinball"])/classical
    if h==3:
        year_ok=True; yrels={}
        for yr in [2022,2023,2024]:
            v=quant["horizons"][str(h)]["years"][str(yr)]["mean_pinball"]
            rr=(years_ref[yr]-v)/years_ref[yr]; yrels[str(yr)]=rr
            if rr < -0.03: year_ok=False
        gate=rel>=0.005 and year_ok and t["crossing_rate"]==0.0
    else:
        year_ok=None; yrels={}; gate=rel>=0.005 and t["crossing_rate"]==0.0
    rows.append({"horizon":h,"head":"quantile","tft_primary":t["mean_pinball"],"classical_primary":classical,"rel_vs_classical":rel,"co_ok":None,"year_ok":year_ok,"gate":gate,"detail":"","year_rel":json.dumps(yrels)})

d=pd.DataFrame(rows)
d.to_csv(OUT/"stage4_tft_comparison.csv",index=False)

h3=d[d.horizon==3]
promoted=h3[h3.gate==True]
status="TFT_PROMOTION" if len(promoted) else "NO_TFT_PROMOTION"

lines=[
"# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 4 TFT Multi-Horizon Challenger Result","",
f"**Status:** **{status}**","",
"## Head decisions","",
"| Horizon | Head | TFT primary | Classical primary | Relative vs classical | Gate |",
"|---|---|---:|---:|---:|---|",
]
for _,r in d.iterrows():
    lines.append(f"| H{int(r.horizon)} | {r['head']} | {r.tft_primary:.6f} | {r.classical_primary:.6f} | {100*r.rel_vs_classical:.2f}% | {r.gate} |")

lines += ["","## H3 binding decision",""]
for _,r in h3.iterrows():
    decision="PROMOTE TFT" if r.gate else "RETAIN CLASSICAL"
    lines.append(f"- {r['head']}: **{decision}** ({100*r.rel_vs_classical:.2f}% vs classical).")

lines += ["","## Training scale","",
          f"- TFT-CLASS parameters: {cls['training']['parameter_count']}",
          f"- TFT-QUANT parameters: {quant['training']['parameter_count']}",
          f"- TFT-CLASS mean epochs: {cls['training']['mean_epochs']:.1f}",
          f"- TFT-QUANT mean epochs: {quant['training']['mean_epochs']:.1f}",
          "",
          "## Binding interpretation"]
if status=="NO_TFT_PROMOTION":
    lines.append("TFT adds no promotable H3 head. Close the deep-learning challenger program and retain classical boosting for H3. Proceed to forecast-head reconciliation / tactical allocation design.")
else:
    lines.append("Promote only the H3 TFT heads that pass their frozen gates. Non-winning heads remain classical. Proceed to forecast-head reconciliation with the mixed frozen architecture.")

(OUT/"STAGE4_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
(Path(OUT/"stage4_all_summaries.json")).write_text(json.dumps(summ,indent=2),encoding="utf-8")
files=list(OUT.iterdir())
summary={"status":status,"h3_promoted_heads":promoted["head"].tolist(),"comparisons":d.to_dict(orient="records"),"hashes":{p.name:sha(p) for p in files}}
(Path(OUT/"stage4_summary.json")).write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("STAGE4_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
print((OUT/"STAGE4_RESULT.md").read_text(),flush=True)
