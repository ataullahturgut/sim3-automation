from __future__ import annotations
import argparse, json, os, urllib.request
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import psycopg

SERIES={
 "gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
 "silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
 "platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
 "palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
METAL={"gold":"Gold","silver":"Silver","platinum":"Platinum","palladium":"Palladium"}

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"global-xau-lineage-audit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def public_year(ref,year):
    rows=json.loads(get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{ref}/data/spot-history-{year}.json"))
    out=defaultdict(dict); meta=defaultdict(dict)
    for r in rows:
        m=str(r.get("metal") or "")
        if m not in METAL.values():continue
        ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
        if pd.isna(ts):continue
        d=ts.date().isoformat()
        try:v=float(r.get("spot"))
        except:continue
        if not np.isfinite(v) or v<=0:continue
        out[m][d]=v
        meta[m][d]={"source":r.get("source"),"provider":r.get("provider"),"timestamp":str(r.get("timestamp"))}
    return out,meta

def normalize_obj(x):
    if x is None:return None
    if isinstance(x,(dict,list,str,int,float,bool)):return x
    return str(x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stak-ref",required=True)
    ap.add_argument("--output",default="source_lineage_audit.json")
    a=ap.parse_args()
    dsn=os.environ["NEON_DATABASE_URL"]
    pub,pmeta=public_year(a.stak_ref,2026)

    result={"stak_ref":a.stak_ref,"series":{},"source_registry":None}
    with psycopg.connect(dsn,autocommit=False) as conn:
      with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        # source_registry introspection, if present
        cur.execute("""
          SELECT column_name FROM information_schema.columns
          WHERE table_schema='public' AND table_name='source_registry'
          ORDER BY ordinal_position
        """)
        cols=[r[0] for r in cur.fetchall()]
        if cols:
          safe=[c for c in cols if c not in {"api_key","secret","token","password","credentials"}]
          qcols=",".join('"'+c.replace('"','""')+'"' for c in safe)
          try:
            cur.execute(f"SELECT {qcols} FROM source_registry")
            regrows=cur.fetchall()
            hits=[]
            for row in regrows:
              rec={c:normalize_obj(v) for c,v in zip(safe,row)}
              blob=json.dumps(rec,default=str).upper()
              if "STAK" in blob or any(s.upper() in blob for s in SERIES.values()):
                hits.append(rec)
            result["source_registry"]={"columns":safe,"matching_rows":hits[:50]}
          except Exception as e:
            result["source_registry"]={"columns":safe,"error":type(e).__name__}

        for key,sid in SERIES.items():
          # schema-safe columns already known from old readers.
          cur.execute("""
            SELECT observation_ts::date, value, source, source_symbol, quality_status,
                   metadata, retrieved_at
            FROM observations
            WHERE series_id=%s
            ORDER BY observation_ts, retrieved_at
          """,(sid,))
          rows=cur.fetchall()
          if not rows:raise RuntimeError(f"NO_ROWS {sid}")
          df=pd.DataFrame(rows,columns=["date","value","source","source_symbol","quality_status","metadata","retrieved_at"])
          df["date"]=pd.to_datetime(df.date)
          df["value"]=pd.to_numeric(df.value,errors="coerce")
          df=df.dropna(subset=["value"]).sort_values(["date","retrieved_at"]).drop_duplicates("date",keep="last")
          # provenance summaries
          src=df.groupby(["source","source_symbol"],dropna=False).size().reset_index(name="n").sort_values("n",ascending=False)
          qstat=df.groupby(["quality_status"],dropna=False).size().reset_index(name="n")
          metadata_samples=[]
          for _,r in df.iloc[np.unique(np.linspace(0,len(df)-1,min(12,len(df))).astype(int))].iterrows():
            metadata_samples.append({
              "date":str(r.date.date()),"value":float(r.value),
              "source":normalize_obj(r.source),"source_symbol":normalize_obj(r.source_symbol),
              "quality_status":normalize_obj(r.quality_status),
              "metadata":normalize_obj(r.metadata),"retrieved_at":str(r.retrieved_at),
            })
          # exact same-date comparison on 2026
          p=pub[METAL[key]]
          comp=[]
          for r in df[df.date.dt.year==2026].itertuples():
            d=r.date.date().isoformat()
            if d in p:
              pv=float(p[d]); dv=float(r.value)
              comp.append({
                "date":d,"db":dv,"public":pv,
                "abs_diff":abs(dv-pv),
                "rel_diff":abs(dv-pv)/max(abs(dv),1e-12),
                "public_source":pmeta[METAL[key]][d].get("source"),
                "public_provider":pmeta[METAL[key]][d].get("provider"),
                "public_timestamp":pmeta[METAL[key]][d].get("timestamp"),
              })
          compdf=pd.DataFrame(comp)
          if len(compdf):
            compdf=compdf.sort_values("rel_diff",ascending=False)
            comp_summary={
              "n":int(len(compdf)),
              "mean_rel_diff":float(compdf.rel_diff.mean()),
              "median_rel_diff":float(compdf.rel_diff.median()),
              "max_rel_diff":float(compdf.rel_diff.max()),
              "exact_1e8_share":float((compdf.rel_diff<=1e-8).mean()),
              "within_10bp_share":float((compdf.rel_diff<=0.001).mean()),
              "within_50bp_share":float((compdf.rel_diff<=0.005).mean()),
              "top_mismatches":compdf.head(20).to_dict(orient="records"),
            }
          else:comp_summary={"n":0}
          result["series"][key]={
            "series_id":sid,"n":int(len(df)),
            "first":str(df.date.min().date()),"last":str(df.date.max().date()),
            "first_retrieved":str(df.retrieved_at.min()),"last_retrieved":str(df.retrieved_at.max()),
            "source_symbol_counts":src.to_dict(orient="records"),
            "quality_counts":qstat.to_dict(orient="records"),
            "metadata_samples":metadata_samples,
            "public_2026_same_date_comparison":comp_summary,
          }
      conn.rollback()

    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print("SOURCE_LINEAGE_AUDIT="+json.dumps({
      "stak_ref":a.stak_ref,
      "series":{k:{
        "first":v["first"],"last":v["last"],
        "sources":v["source_symbol_counts"],
        "comparison":{kk:vv for kk,vv in v["public_2026_same_date_comparison"].items() if kk!="top_mismatches"}
      } for k,v in result["series"].items()}
    },sort_keys=True,default=str))

if __name__=="__main__":main()
