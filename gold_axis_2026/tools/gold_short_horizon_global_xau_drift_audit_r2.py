from __future__ import annotations
import io,json,os,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
TRANSPORT_ARTIFACT=int(os.environ["TRANSPORT_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_r2_drift_out"));OUT.mkdir(parents=True,exist_ok=True)
CORE3=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
"silver_r1","silver_r5","silver_r21","silver_age_days",
"platinum_r1","platinum_r5","platinum_r21","platinum_age_days"]

def zip_for(aid):
 tok=os.environ["GITHUB_TOKEN"];u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
 r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-r2-drift"},timeout=120);r.raise_for_status()
 return zipfile.ZipFile(io.BytesIO(r.content))
def csv(z,suffix):
 n=[x for x in z.namelist() if x.endswith(suffix)]
 if len(n)!=1:raise RuntimeError((suffix,n))
 return pd.read_csv(io.BytesIO(z.read(n[0])))
def psi(ref,x,bins=10):
 a=pd.to_numeric(ref,errors="coerce").dropna().to_numpy(float);b=pd.to_numeric(x,errors="coerce").dropna().to_numpy(float)
 if len(a)<20 or len(b)<20:return np.nan
 edges=np.unique(np.quantile(a,np.linspace(0,1,bins+1)))
 if len(edges)<3:return 0.0
 edges[0]=-np.inf;edges[-1]=np.inf
 pa=np.histogram(a,bins=edges)[0]/len(a);pb=np.histogram(b,bins=edges)[0]/len(b)
 pa=np.clip(pa,1e-6,None);pb=np.clip(pb,1e-6,None)
 return float(np.sum((pb-pa)*np.log(pb/pa)))

def main():
 p=csv(zip_for(READINESS_ARTIFACT),"global_xau_r2_readiness_panel.csv")
 for c in ["forecast_issue_date","target_end_date_h3"]:p[c]=pd.to_datetime(p[c])
 l=csv(zip_for(TRANSPORT_ARTIFACT),"global_xau_r2_h3_transport_predictions.csv")
 l["forecast_issue_date"]=pd.to_datetime(l.forecast_issue_date)
 ref=p[(p.forecast_issue_date.dt.year.between(2022,2024)) & p.target_r3.notna()].copy()
 periods={
  "DEV_2022_2024":ref,
  "TRANSPORT_2025":p[(p.forecast_issue_date.dt.year==2025)&p.target_r3.notna()],
  "OPENED_2026":p[(p.forecast_issue_date.dt.year==2026)&p.target_r3.notna()],
  "2026_H1":p[(p.forecast_issue_date.between("2026-01-01","2026-06-30"))&p.target_r3.notna()],
  "2026_JUL_SEP":p[(p.forecast_issue_date.between("2026-07-01","2026-09-30"))&p.target_r3.notna()],
 }
 rows=[]
 for name,z in periods.items():
  for f in CORE3:
   a=pd.to_numeric(ref[f],errors="coerce");b=pd.to_numeric(z[f],errors="coerce")
   s=float(a.std(ddof=0))
   rows.append({"period":name,"feature":f,"n":int(b.notna().sum()),
    "mean":float(b.mean()),"ref_mean":float(a.mean()),
    "standardized_mean_shift":0.0 if s==0 else float((b.mean()-a.mean())/s),
    "std_ratio":np.nan if s==0 else float(b.std(ddof=0)/s),
    "psi":psi(a,b)})
 d=pd.DataFrame(rows);d.to_csv(OUT/"feature_drift.csv",index=False)
 pr=[]
 for period,g in l.groupby("year"):
  pr.append({"period":str(period),"n":len(g),"mean_p_up":float(g.p_up.mean()),"pred_sd":float(g.p_up.std(ddof=0)),
    "actual_up_rate":float((g.actual_direction=="UP").mean()),"accuracy":float(g.correct.mean())})
 for period,g in l[l.year==2026].groupby("month"):
  pr.append({"period":period,"n":len(g),"mean_p_up":float(g.p_up.mean()),"pred_sd":float(g.p_up.std(ddof=0)),
    "actual_up_rate":float((g.actual_direction=="UP").mean()),"accuracy":float(g.correct.mean())})
 pdf=pd.DataFrame(pr);pdf.to_csv(OUT/"probability_drift.csv",index=False)
 top={}
 for name,g in d[d.period!="DEV_2022_2024"].groupby("period"):
  q=g.assign(abs_shift=g.standardized_mean_shift.abs()).sort_values(["psi","abs_shift"],ascending=False).head(7)
  top[name]=q[["feature","standardized_mean_shift","std_ratio","psi"]].to_dict(orient="records")
 summary={"status":"DIAGNOSTIC_ONLY","readiness_artifact":READINESS_ARTIFACT,"transport_artifact":TRANSPORT_ARTIFACT,
  "top_shifts":top,"probability_drift":pdf.to_dict(orient="records"),
  "interpretation_rule":"No 2025/2026 drift pattern may be converted into a tuned gate under this audit."}
 (OUT/"drift_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")
 lines=["# GLOBAL XAU R2 — Regime / Distribution Shift Diagnostic","",
  "**Status:** DIAGNOSTIC ONLY — NO RETUNING","",
  "## Probability / outcome state","",
  "| Period | N | Mean P(UP) | P SD | Actual UP | Accuracy |","|---|---:|---:|---:|---:|---:|"]
 for r in pdf.itertuples():
  if r.period in ["2025","2026","2026-07","2026-08","2026-09"]:
   lines.append(f"| {r.period} | {r.n} | {r.mean_p_up:.3f} | {r.pred_sd:.3f} | {100*r.actual_up_rate:.1f}% | {100*r.accuracy:.1f}% |")
 lines += ["","## Largest feature-distribution shifts"]
 for name in ["TRANSPORT_2025","OPENED_2026","2026_JUL_SEP"]:
  lines.append(f"### {name}")
  for r in top.get(name,[])[:5]:
   lines.append(f"- {r['feature']}: mean shift {r['standardized_mean_shift']:+.2f} SD, std ratio {r['std_ratio']:.2f}, PSI {r['psi']:.3f}.")
 lines += ["","These diagnostics describe failure anatomy only. They do not authorize a post-hoc regime gate or threshold change."]
 (OUT/"DRIFT_RESULT.md").write_text("\n".join(lines)+"\n")
 print((OUT/"DRIFT_RESULT.md").read_text())
if __name__=="__main__":main()
