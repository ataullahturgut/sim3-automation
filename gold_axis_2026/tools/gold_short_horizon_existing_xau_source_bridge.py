from __future__ import annotations
import os, json, math, hashlib
from pathlib import Path
import numpy as np, pandas as pd, psycopg

OUT=Path(os.environ.get("OUT_DIR","global_xau_source_bridge_out")); OUT.mkdir(parents=True,exist_ok=True)
HIST="XAU_STAKTRAKR_RESEARCH_DAILY_R1"
CANDS=["XAU_EOD_TWELVE_NY17","XAU_DAILY_XAUS"]

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def load(cur,sid):
    cur.execute("""
      select observation_ts,value,source,source_symbol,quality_status,retrieved_at
      from observations where series_id=%s order by observation_ts,retrieved_at
    """,(sid,))
    r=cur.fetchall()
    x=pd.DataFrame(r,columns=["observation_ts","value","source","source_symbol","quality_status","retrieved_at"])
    if x.empty: return x
    x["observation_ts"]=pd.to_datetime(x.observation_ts,utc=True)
    x["retrieved_at"]=pd.to_datetime(x.retrieved_at,utc=True)
    x=x.sort_values(["observation_ts","retrieved_at"]).drop_duplicates("observation_ts",keep="last")
    x["value"]=pd.to_numeric(x.value,errors="coerce")
    return x

def dates(x,sid):
    if sid=="XAU_EOD_TWELVE_NY17":
        return x.observation_ts.dt.tz_convert("America/New_York").dt.date
    return x.observation_ts.dt.date

def metrics(h,c,sid):
    hh=h.copy(); cc=c.copy()
    hh["date"]=dates(hh,HIST); cc["date"]=dates(cc,sid)
    hh=hh.groupby("date",as_index=False).last()
    cc=cc.groupby("date",as_index=False).last()
    b=hh[["date","value"]].rename(columns={"value":"hist"}).merge(
        cc[["date","value"]].rename(columns={"value":"cand"}),on="date",how="inner"
    ).sort_values("date").reset_index(drop=True)
    if len(b)<2: return b,{}
    b["rh"]=np.log(b["hist"].astype(float)).diff(); b["rc"]=np.log(b["cand"].astype(float)).diff()
    q=b.dropna()
    d=q.rh-q.rc
    ratio=b["hist"].astype(float)/b["cand"].astype(float)
    m={
      "series_id":sid,
      "common_level_dates":int(len(b)),
      "common_return_pairs":int(len(q)),
      "first_common":str(b.date.min()),
      "last_common":str(b.date.max()),
      "pearson":float(q.rh.corr(q.rc)),
      "spearman":float(q.rh.corr(q.rc,method="spearman")),
      "sign_agreement":float(((q.rh>0)==(q.rc>0)).mean()),
      "mean_abs_return_diff":float(d.abs().mean()),
      "return_diff_sd":float(d.std(ddof=0)),
      "median_level_ratio":float(ratio.median()),
      "level_ratio_cv":float(ratio.std(ddof=0)/ratio.mean()),
    }
    m["reference_gate_pass"]=bool(m["common_return_pairs"]>=60 and m["pearson"]>=0.90 and m["sign_agreement"]>=0.80 and m["return_diff_sd"]<=0.0075)
    return b,m

def main():
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],autocommit=False) as conn:
      with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        hist=load(cur,HIST)
        cand={sid:load(cur,sid) for sid in CANDS}
      conn.rollback()

    metas=[]
    for sid,x in [(HIST,hist),*[(s,cand[s]) for s in CANDS]]:
      metas.append({
        "series_id":sid,"n":len(x),
        "first":None if x.empty else x.observation_ts.min().isoformat(),
        "last":None if x.empty else x.observation_ts.max().isoformat(),
        "sources":[] if x.empty else sorted(set(x.source.dropna().astype(str))),
        "quality":[] if x.empty else sorted(set(x.quality_status.dropna().astype(str)))
      })
    pd.DataFrame(metas).to_csv(OUT/"existing_xau_series_inventory.csv",index=False)

    rows=[]
    for sid in CANDS:
      b,m=metrics(hist,cand[sid],sid)
      b.to_csv(OUT/f"bridge_{sid.lower()}.csv",index=False)
      if m: rows.append(m)
    df=pd.DataFrame(rows)
    if len(df):
      elig=df[df.common_return_pairs>=60].copy()
      if len(elig):
        bestp=float(elig.pearson.max())
        near=elig[elig.pearson>=bestp-0.01].copy()
        best=near.sort_values(["sign_agreement","pearson"],ascending=False).iloc[0].to_dict()
      else: best=None
    else: best=None
    df.to_csv(OUT/"source_bridge_metrics.csv",index=False)
    summary={"inventory":metas,"metrics":rows,"preferred":best}
    (OUT/"source_bridge_summary.json").write_text(json.dumps(summary,indent=2,default=str),encoding="utf-8")
    lines=["# Existing Global XAU Source Bridge Screen","",
           "| Series | N | Pearson | Spearman | Sign | Diff SD | Gate |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for r in rows:
      lines.append(f"| {r['series_id']} | {r['common_return_pairs']} | {r['pearson']:.4f} | {r['spearman']:.4f} | {100*r['sign_agreement']:.1f}% | {100*r['return_diff_sd']:.3f}% | {r['reference_gate_pass']} |")
    lines+=["",f"Preferred: {best['series_id'] if best else 'NONE'}"]
    (OUT/"SOURCE_BRIDGE_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    print("SOURCE_BRIDGE_SUMMARY="+json.dumps(summary,separators=(",",":"),default=str))
    print((OUT/"SOURCE_BRIDGE_RESULT.md").read_text())

if __name__=="__main__": main()
