from __future__ import annotations

import json, os, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

from gold_h3_data_integrity_gate_v1 import evaluate_row, decision_dict

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_integrity_gate_test_out"))
OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]
REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"


def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"h3-integrity-gate-test/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def load_stak():
    rows=[]
    for y in [2025,2026]:
        raw=json.loads(get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{REF}/data/spot-history-{y}.json"))
        for r in raw:
            metal=r.get("metal")
            if metal not in {"Gold","Silver","Platinum","Palladium"}: continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts) or ts.weekday()>=5: continue
            try:v=float(r.get("spot"))
            except:continue
            rows.append({"date":ts.normalize(),"metal":metal.lower(),"value":v,"source":r.get("source")})
    p=pd.DataFrame(rows).pivot_table(index="date",columns="metal",values="value",aggfunc="last").reset_index()
    return p.dropna(subset=["gold","silver","platinum","palladium"]).sort_values("date").reset_index(drop=True)


def load_independent():
    with psycopg.connect(DSN,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
              SELECT observation_ts,value
              FROM observations
              WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
              ORDER BY observation_ts
            """)
            x=cur.fetchall()
        conn.rollback()
    d=pd.DataFrame(x,columns=["ts","xau"])
    d["date"]=pd.to_datetime(d.ts,utc=True).dt.tz_localize(None).dt.normalize()
    return dict(zip(d.date,d.xau.astype(float)))


def main():
    p=load_stak()
    ix=load_independent()
    accepted=[]
    ledger=[]
    for r in p.itertuples(index=False):
        cur={"date":r.date,"gold":r.gold,"silver":r.silver,"platinum":r.platinum,"palladium":r.palladium}
        if not accepted:
            accepted.append(cur)
            ledger.append({**cur,"integrity_status":"PASS_BOOTSTRAP","integrity_admit":True})
            continue
        ind=ix.get(pd.Timestamp(r.date))
        d=evaluate_row(cur,accepted[-1],independent_xau=ind)
        rec={**cur,**decision_dict(d)}
        ledger.append(rec)
        if d.admit:
            accepted.append(cur)

    g=pd.DataFrame(ledger)
    g.to_csv(OUT/"integrity_gate_replay.csv",index=False)
    q=g[g.integrity_admit==False].copy()
    q.to_csv(OUT/"integrity_gate_quarantines.csv",index=False)

    key=g[g.date.astype(str).isin(["2026-01-30","2026-02-02","2026-02-27","2026-03-02"])].copy()
    expected={
      "2026-01-30":True,
      "2026-02-02":True,
      "2026-02-27":False,
      "2026-03-02":True,
    }
    checks={}
    for d,want in expected.items():
        z=key[key.date.astype(str)==d]
        checks[d]=bool(len(z)==1 and bool(z.iloc[0].integrity_admit)==want)

    if not all(checks.values()):
        raise RuntimeError(f"GATE_REPLAY_EXPECTATION_FAIL {checks}")

    summary={
      "schema":"GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY",
      "rows":int(len(g)),
      "admitted":int(g.integrity_admit.astype(bool).sum()),
      "quarantined":int((~g.integrity_admit.astype(bool)).sum()),
      "quarantine_dates":q.date.astype(str).tolist(),
      "key_checks":checks,
    }
    (OUT/"integrity_gate_replay_summary.json").write_text(json.dumps(summary,indent=2)+"\n")

    lines=["# GOLD H3 DATA INTEGRITY GATE V1 — HISTORICAL REPLAY","",
      f"- evaluated rows: **{len(g)}**",
      f"- admitted: **{int(g.integrity_admit.astype(bool).sum())}**",
      f"- quarantined: **{int((~g.integrity_admit.astype(bool)).sum())}**","",
      "## Key stress dates","",
      "| Date | Admit | Status | Gold | Independent XAU | Gold logret | Severe assets |",
      "|---|---|---|---:|---:|---:|---:|"]
    for r in key.itertuples():
        lines.append(f"| {pd.Timestamp(r.date).date()} | {bool(r.integrity_admit)} | {r.integrity_status} | {r.gold:.2f} | {r.independent_xau if pd.notna(r.independent_xau) else float('nan'):.2f} | {100*r.gold_logret:+.2f}% | {int(r.severe_asset_n)} |")
    lines += ["","## Quarantines",""]
    if q.empty:
        lines.append("- none")
    else:
        for r in q.itertuples():
            lines.append(f"- **{pd.Timestamp(r.date).date()}**: {r.integrity_status} — {r.integrity_reason}")
    (OUT/"INTEGRITY_GATE_REPLAY_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"INTEGRITY_GATE_REPLAY_RESULT.md").read_text())

if __name__=="__main__": main()
