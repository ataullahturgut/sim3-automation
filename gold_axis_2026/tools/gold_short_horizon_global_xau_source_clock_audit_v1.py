from __future__ import annotations
import csv,json,os
from pathlib import Path
import pandas as pd
import psycopg

OUT=Path(os.environ.get("OUT_DIR","global_xau_source_clock_audit_out"));OUT.mkdir(parents=True,exist_ok=True)

FAMILIES=[
 ("XAU",["XAU"],"target/market","explicit target identity; do not stitch clocks"),
 ("PRECIOUS",["XAG","XPT","XPD","SILVER","PLATINUM","PALLADIUM"],"cross-metal","as-of feature cutoff / previous available observation"),
 ("RATES",["DGS10","DFII10","H15","RIFLGFCY10"],"rates","release-aware; conservative H.15 lag"),
 ("FX_USD",["DTWEX","BROAD_USD","H10","JRXWTFB","EURUSD","GBPUSD","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"],"fx/usd","release-aware H.10/as-of; no same-origin future publication"),
 ("VOL",["VIX","GVZ"],"volatility","strictly previous available date at daily forecast origin"),
 ("EQUITY",["NASDAQ","NDX","SP500","DJIA"],"equity","strictly previous available date at daily forecast origin"),
 ("OIL",["WTI","BRENT","DCOIL"],"oil","registered challenger only; PIT/clock mapping required before model promotion"),
 ("GPR",["GPR"],"geopolitical","release-aware / vintage-safe only"),
]

def family_for(s):
 u=s.upper()
 for fam,keys,role,rule in FAMILIES:
  if any(k in u for k in keys):return fam,role,rule
 return None,None,None

def main():
 dsn=os.environ["NEON_DATABASE_URL"];rows=[]
 with psycopg.connect(dsn,autocommit=False) as conn:
  with conn.cursor() as cur:
   cur.execute("SET TRANSACTION READ ONLY")
   cur.execute("""
     SELECT series_id, semantic_id, source_name, source_symbol, source_tier,
            frequency, unit, model_role, status, metadata
     FROM source_registry
     ORDER BY series_id
   """)
   registry=cur.fetchall()
   for r in registry:
    sid=str(r[0]);sem=str(r[1] or "");src=str(r[2] or "");sym=str(r[3] or "")
    fam,role,rule=family_for(" ".join([sid,sem,src,sym]))
    if fam is None:continue
    try:
     cur.execute("""SELECT MIN(observation_ts)::date,MAX(observation_ts)::date,COUNT(*),
       COUNT(*) FILTER (WHERE observation_ts::date BETWEEN DATE '2026-08-01' AND DATE '2026-09-30')
       FROM observations WHERE series_id=%s""",(sid,))
     d0,d1,n,nlate=cur.fetchone()
    except Exception:
     d0=d1=None;n=nlate=0
    rows.append({
      "family":fam,"role":role,"series_id":sid,"semantic_id":sem,
      "source_name":src,"source_symbol":sym,"source_tier":str(r[4] or ""),
      "frequency":str(r[5] or ""),"unit":str(r[6] or ""),"model_role":str(r[7] or ""),
      "status":str(r[8] or ""),"first_observation":str(d0) if d0 else "",
      "last_observation":str(d1) if d1 else "","rows":int(n or 0),
      "aug_sep_2026_rows":int(nlate or 0),"daily_join_rule":rule,
      "metadata":json.dumps(r[9] or {},sort_keys=True,default=str),
    })
  conn.rollback()
 df=pd.DataFrame(rows)
 df.to_csv(OUT/"source_clock_audit.csv",index=False)
 summary=[]
 for fam,g in df.groupby("family"):
  summary.append({"family":fam,"registered_series":int(len(g)),
    "latest_observation":max([x for x in g.last_observation if x],default=""),
    "aug_sep_rows_total":int(g.aug_sep_2026_rows.sum()),
    "join_rule":g.daily_join_rule.iloc[0]})
 sdf=pd.DataFrame(summary).sort_values("family")
 sdf.to_csv(OUT/"source_clock_family_summary.csv",index=False)
 lines=["# GLOBAL XAU DAILY — Source / Clock Audit","",
   "This audit inventories the established project registry. It does not authorize a new provider or add a feature to the frozen H3 CORE3 engine.","",
   "| Family | Registered series | Latest observation | Aug-Sep rows | Binding daily rule |",
   "|---|---:|---|---:|---|"]
 for r in sdf.itertuples():
  lines.append(f"| {r.family} | {r.registered_series} | {r.latest_observation} | {r.aug_sep_rows_total} | {r.join_rule} |")
 lines += ["","Key governance:",
  "- Source identity and availability clock are separate contracts.",
  "- DEXCHUS must not be relabeled as broad USD; use the corrected Broad-USD authority where registered.",
  "- WTI/Brent remain challengers until their short-horizon PIT clock is explicitly frozen.",
  "- Current R2 baseline uses CORE3 only; external families are not silently added."]
 (OUT/"SOURCE_CLOCK_AUDIT_RESULT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print((OUT/"SOURCE_CLOCK_AUDIT_RESULT.md").read_text())
if __name__=="__main__":main()
