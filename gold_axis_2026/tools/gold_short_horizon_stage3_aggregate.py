import os,glob,json,hashlib,io,zipfile,requests
from pathlib import Path
import numpy as np
import pandas as pd

OUT=Path("stage3_all"); OUT.mkdir(exist_ok=True)
STAGE2_ART=11167744845
REPO="ataullahturgut/sim3-automation"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def get_stage2():
    token=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{STAGE2_ART}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

# Load all challenger summaries
summ=[]
for p in glob.glob("seq*/stage3_*_summary.json"):
    summ.append(json.loads(Path(p).read_text()))
if len(summ)!=6: raise RuntimeError(f"expected 6 summaries got {len(summ)}")

# Classical authoritative metrics
z=get_stage2()
def rcsv(suffix):
    n=[n for n in z.namelist() if n.endswith(suffix)]
    if len(n)!=1: raise RuntimeError((suffix,n))
    return pd.read_csv(io.BytesIO(z.read(n[0])))
agg2=rcsv("stage2_aggregate_metrics.csv")
yr2=rcsv("stage2_year_metrics.csv")
qsum2=rcsv("stage2_quantile_summary.csv")
qy2=rcsv("stage2_quantile_year_summary.csv")

cdir=agg2[(agg2.feature_block=="CORE3")&(agg2["head"]=="direction")].iloc[0]
cret=agg2[(agg2.feature_block=="GOLD_ONLY")&(agg2["head"]=="return")].iloc[0]
cquant=qsum2[qsum2.feature_block=="GOLD_ONLY"].iloc[0]

rows=[]
for s in summ:
    cfg=f"{s['arch']}_L{s['lookback']}"
    # Direction gate
    rel=(float(cdir.brier)-s["direction"]["brier"])/float(cdir.brier)
    ll_ok=s["direction"]["logloss"]<=float(cdir.logloss)
    year_ok=True; yrels={}
    for yr in [2022,2023,2024]:
        cb=float(yr2[(yr2.feature_block=="CORE3")&(yr2["head"]=="direction")&(yr2.year==yr)].iloc[0].brier)
        v=s["years"][str(yr)]["direction"]["brier"]
        rr=(cb-v)/cb; yrels[str(yr)]=rr
        if rr < -0.03: year_ok=False
    gate=rel>=0.005 and ll_ok and year_ok
    rows.append({"config":cfg,"arch":s["arch"],"lookback":s["lookback"],"head":"direction","primary":s["direction"]["brier"],"classical":float(cdir.brier),"rel_improve":rel,"co_primary":s["direction"]["logloss"],"classical_co":float(cdir.logloss),"year_ok":year_ok,"gate":gate,"year_rel":json.dumps(yrels,sort_keys=True),"parameter_count":s["training"]["parameter_count"],"mean_epochs":s["training"]["mean_epochs"]})

    # Return
    rel=(float(cret.mae)-s["return"]["mae"])/float(cret.mae)
    rm_ok=s["return"]["rmse"]<=float(cret.rmse)
    year_ok=True; yrels={}
    for yr in [2022,2023,2024]:
        cb=float(yr2[(yr2.feature_block=="GOLD_ONLY")&(yr2["head"]=="return")&(yr2.year==yr)].iloc[0].mae)
        v=s["years"][str(yr)]["return"]["mae"]
        rr=(cb-v)/cb; yrels[str(yr)]=rr
        if rr < -0.03: year_ok=False
    gate=rel>=0.005 and rm_ok and year_ok
    rows.append({"config":cfg,"arch":s["arch"],"lookback":s["lookback"],"head":"return","primary":s["return"]["mae"],"classical":float(cret.mae),"rel_improve":rel,"co_primary":s["return"]["rmse"],"classical_co":float(cret.rmse),"year_ok":year_ok,"gate":gate,"year_rel":json.dumps(yrels,sort_keys=True),"parameter_count":s["training"]["parameter_count"],"mean_epochs":s["training"]["mean_epochs"]})

    # Quantile
    rel=(float(cquant.mean_pinball)-s["quantile"]["mean_pinball"])/float(cquant.mean_pinball)
    year_ok=True; yrels={}
    for yr in [2022,2023,2024]:
        cb=float(qy2[(qy2.feature_block=="GOLD_ONLY")&(qy2.year==yr)].iloc[0].mean_pinball)
        v=s["years"][str(yr)]["quantile"]["mean_pinball"]
        rr=(cb-v)/cb; yrels[str(yr)]=rr
        if rr < -0.03: year_ok=False
    gate=rel>=0.005 and year_ok
    rows.append({"config":cfg,"arch":s["arch"],"lookback":s["lookback"],"head":"quantile","primary":s["quantile"]["mean_pinball"],"classical":float(cquant.mean_pinball),"rel_improve":rel,"co_primary":None,"classical_co":None,"year_ok":year_ok,"gate":gate,"year_rel":json.dumps(yrels,sort_keys=True),"parameter_count":s["training"]["parameter_count"],"mean_epochs":s["training"]["mean_epochs"],"crossing_rate":s["quantile"]["crossing_rate_pre_repair"]})

m=pd.DataFrame(rows)
m.to_csv(OUT/"stage3_sequence_comparison.csv",index=False)

simp_arch={"GRU":0,"TCN":1,"BIGRU":2}
dec=[]
for head in ["direction","return","quantile"]:
    q=m[m["head"]==head].copy()
    passing=q[q.gate==True].copy()
    if len(passing):
        best_imp=passing.rel_improve.max()
        near=passing[passing.rel_improve>=best_imp-0.0025].copy()
        near["simp"]=near.arch.map(simp_arch)*10+(near.lookback==60).astype(int)
        sel=near.sort_values(["simp","rel_improve"],ascending=[True,False]).iloc[0]
        status="PROMOTE"; selected=sel["config"]
    else:
        sel=q.sort_values("rel_improve",ascending=False).iloc[0]
        status="RETAIN_CLASSICAL"; selected="CLASSICAL"
    dec.append({"head":head,"status":status,"selected":selected,"best_sequence":sel["config"],"best_sequence_rel_improve":float(sel["rel_improve"]),"best_sequence_gate":bool(sel["gate"])})

d=pd.DataFrame(dec); d.to_csv(OUT/"stage3_decisions.csv",index=False)

# Save all summaries flattened raw JSON
(Path(OUT/"stage3_all_summaries.json")).write_text(json.dumps(summ,indent=2),encoding="utf-8")

lines=[
"# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 3 Sequence Challenger Result","",
"## Head decisions","",
"| Head | Decision | Selected | Best sequence | Relative improvement vs classical | Gate |",
"|---|---|---|---|---:|---|",
]
for _,r in d.iterrows():
    lines.append(f"| {r['head']} | {r['status']} | {r['selected']} | {r['best_sequence']} | {100*r['best_sequence_rel_improve']:.2f}% | {r['best_sequence_gate']} |")
lines += ["","## All challenger comparisons","",
"| Config | Head | Primary | Classical | Relative improvement | Year gate | Promotion gate | Params | Mean epochs |",
"|---|---|---:|---:|---:|---|---|---:|---:|"]
for _,r in m.sort_values(["head","rel_improve"],ascending=[True,False]).iterrows():
    lines.append(f"| {r['config']} | {r['head']} | {r['primary']:.6f} | {r['classical']:.6f} | {100*r['rel_improve']:.2f}% | {r['year_ok']} | {r['gate']} | {int(r['parameter_count'])} | {r['mean_epochs']:.1f} |")

overall="PROMOTION" if (d.status=="PROMOTE").any() else "NO_SEQUENCE_PROMOTION"
lines += ["","## Binding interpretation",f"Stage 3 status: **{overall}**."]
(Path(OUT/"STAGE3_RESULT.md")).write_text("\n".join(lines),encoding="utf-8")

files=list(OUT.iterdir())
summary={"status":overall,"decisions":d.to_dict(orient="records"),"hashes":{p.name:sha(p) for p in files}}
(Path(OUT/"stage3_summary.json")).write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("STAGE3_SUMMARY="+json.dumps(summary,separators=(",",":")))
print((OUT/"STAGE3_RESULT.md").read_text())
