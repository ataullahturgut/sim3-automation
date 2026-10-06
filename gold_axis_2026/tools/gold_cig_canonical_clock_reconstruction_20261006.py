from __future__ import annotations
import io, json, os, time, calendar, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"CIG_CANONICAL_CLOCK_OUT"; OUT.mkdir(exist_ok=True)
PIN="fcbf50080afdf164dae460e8e855faf3f72bb1b0"
NY="America/New_York"

def git_text(path):
    p=subprocess.run(["git","show",f"{PIN}:{path}"],capture_output=True,text=True,check=True)
    return p.stdout

def read_csv_pin(path):
    return pd.read_csv(io.StringIO(git_text(path)))

def chunks(start,end):
    out=[]; cur=pd.Timestamp(start); end=pd.Timestamp(end)
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end)
        out.append((f"{cur.date()} 00:00:00",f"{b.date()} 23:59:59"))
        cur=b+pd.Timedelta(days=1)
    return out

def fetch(interval,a,b):
    p={"symbol":"XAU/USD","interval":interval,"timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":os.environ["TWELVE_DATA_API_KEY"],"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str({"interval":interval,"a":a,"b":b,"status":r.status_code,"response":j}))
    rows=[]
    for z in vals:
        try:
            rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
        except: pass
    return pd.DataFrame(rows),{"interval":interval,"start":a,"end":b,"rows":len(rows)}

def fetch_all(interval):
    parts=[]; meta=[]
    for a,b in chunks("2025-12-15","2026-08-02"):
        q,m=fetch(interval,a,b); parts.append(q);meta.append(m);time.sleep(8)
    x=pd.concat(parts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    x["date"]=x.dt.dt.strftime("%Y-%m-%d")
    x["hm"]=x.dt.dt.strftime("%H:%M")
    return x,meta

def pred_map(df,pcol):
    df=df.copy()
    df["forecast_issue_date"]=pd.to_datetime(df.forecast_issue_date).dt.strftime("%Y-%m-%d")
    return {r.forecast_issue_date:int(float(getattr(r,pcol))>=.5) for r in df.itertuples(index=False)}

def met(rows,key):
    z=[r for r in rows if r.get(key) is not None]
    if not z:return {}
    return {"n":len(z),"correct":sum(int(r[key]==r["actual16"]) for r in z),
            "accuracy":sum(int(r[key]==r["actual16"]) for r in z)/len(z)}

def exec_met(rows,key="post0815_to_1600"):
    z=[r for r in rows if r.get(key) is not None]
    if not z:return {}
    acc=sum(int(r["consensus_pred"]==(1 if r[key]>0 else 0)) for r in z)
    ups=[r for r in z if r["consensus_pred"]==1]
    dns=[r for r in z if r["consensus_pred"]==0]
    def part(a):
        if not a:return {}
        return {"n":len(a),"direction_hit":sum(int(r["consensus_pred"]==(1 if r[key]>0 else 0)) for r in a)/len(a),
                "compound_long":float(np.prod([1+r[key] for r in a])-1),
                "mean":float(np.mean([r[key] for r in a]))}
    return {"n":len(z),"direction_accuracy":acc/len(z),"UP":part(ups),"DOWN":part(dns)}

def main():
    v5=read_csv_pin("gold_axis_2026/GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv")
    rift=read_csv_pin("gold_axis_2026/GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv")
    vega=read_csv_pin("gold_axis_2026/GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv")
    ev=read_csv_pin("gold_axis_2026/GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv")
    for d in [v5,rift,vega]:
        d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
        d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    V={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_helios_v5_dce)>=.5) for r in v5.itertuples(index=False)}
    R={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_rift)>=.5) for r in rift.itertuples(index=False)}
    G={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_vega)>=.5) for r in vega.itertuples(index=False)}
    cutoff_to_issue={r.feature_cutoff_date.strftime("%Y-%m-%d"):r.forecast_issue_date.strftime("%Y-%m-%d") for r in v5.itertuples(index=False)}
    S=dict(V)
    mapped_events=[]
    for e in ev.itertuples(index=False):
        c=pd.Timestamp(e.feature_cutoff_date).strftime("%Y-%m-%d")
        issue=cutoff_to_issue.get(c)
        if issue:
            S[issue]=int(e.combined_pred)
            mapped_events.append({"feature_cutoff_date":c,"forecast_issue_date":issue,"source":e.source,
                                  "v5_pred":int(e.v5_pred),"combined_pred":int(e.combined_pred)})

    h1,m1=fetch_all("1h")
    m15,mm=fetch_all("15min")

    # Canonical candidate = exact 16:00 NY anchor-close series, matching prior hourly D1 authority.
    anchors=h1[h1.hm=="16:00"].copy().sort_values("dt").reset_index(drop=True)
    anchors["prev_close"]=anchors.close.shift(1)
    anchors["prev_date"]=anchors.date.shift(1)
    anchors["actual16"]=(anchors.close>anchors.prev_close).astype(int)
    anchors=anchors[(anchors.date>="2026-01-02")&(anchors.date<="2026-07-31")].copy()

    m15open={(r.date,r.hm):float(r.open) for r in m15.itertuples(index=False)}
    rows=[]
    for a in anchors.itertuples(index=False):
        d=a.date
        if not all(d in M for M in [V,R,G,S]): continue
        vv,rr,gg,ss=V[d],R[d],G[d],S[d]
        consensus=(vv==rr==gg==ss)
        p0815=m15open.get((d,"08:15")); p1600=m15open.get((d,"16:00")); p1700=m15open.get((d,"17:00")); p2000=m15open.get((d,"20:00"))
        rows.append({
          "issue_date":d,"prev_anchor_date":a.prev_date,"anchor16_close":float(a.close),"prev_anchor16_close":float(a.prev_close),
          "actual16":int(a.actual16),"sage":ss,"v5":vv,"rift":rr,"vega":gg,
          "consensus":bool(consensus),"consensus_pred":vv if consensus else None,
          "post0815_to_1600":(p1600/p0815-1) if p0815 and p1600 else None,
          "post0815_to_2000":(p2000/p0815-1) if p0815 and p2000 else None,
          "late1700_to_2000":(p2000/p1700-1) if p1700 and p2000 else None,
        })
    z=pd.DataFrame(rows)
    z.to_csv(OUT/"canonical_rows.csv",index=False)

    allrows=rows
    cons=[r for r in rows if r["consensus"]]
    disag=[r for r in rows if not r["consensus"]]
    canonical={
      "universe_n":len(rows),
      "sage":met(rows,"sage"),"v5":met(rows,"v5"),"rift":met(rows,"rift"),"vega":met(rows,"vega"),
      "consensus_n":len(cons),
      "consensus_correct":sum(int(r["consensus_pred"]==r["actual16"]) for r in cons),
      "consensus_accuracy":sum(int(r["consensus_pred"]==r["actual16"]) for r in cons)/len(cons) if cons else None,
      "disagreement_n":len(disag),
      "disagreement_v5_correct":sum(int(r["v5"]==r["actual16"]) for r in disag),
      "mapped_sage_ruleflow_events":mapped_events
    }
    expected={"universe_n":145,"sage_correct":103,"v5_correct":102,"rift_correct":102,"vega_correct":102,
              "consensus_n":125,"consensus_correct":93,"disagreement_n":20,"disagreement_correct":10}
    checks={
      "universe_n":canonical["universe_n"]==expected["universe_n"],
      "sage_correct":canonical["sage"].get("correct")==expected["sage_correct"],
      "v5_correct":canonical["v5"].get("correct")==expected["v5_correct"],
      "rift_correct":canonical["rift"].get("correct")==expected["rift_correct"],
      "vega_correct":canonical["vega"].get("correct")==expected["vega_correct"],
      "consensus_n":canonical["consensus_n"]==expected["consensus_n"],
      "consensus_correct":canonical["consensus_correct"]==expected["consensus_correct"],
      "disagreement_n":canonical["disagreement_n"]==expected["disagreement_n"],
      "disagreement_correct":canonical["disagreement_v5_correct"]==expected["disagreement_correct"],
    }
    gate=all(checks.values())

    result={
      "status":"CANONICAL_CIG_CLOCK_RECONSTRUCTION_PASS" if gate else "CANONICAL_CIG_CLOCK_RECONSTRUCTION_MISMATCH",
      "pinned_source_commit":PIN,
      "candidate_label_clock":"XAU/USD exact 16:00 America/New_York hourly anchor close, previous available 16:00 anchor -> current 16:00 anchor",
      "canonical_expected":expected,
      "canonical_reconstructed":canonical,
      "checks":checks,
      "exact_match":gate,
      "post_issue_same_rows":{
        "08:15_to_16:00_NY":exec_met(cons,"post0815_to_1600"),
        "08:15_to_20:00_NY":exec_met(cons,"post0815_to_2000"),
        "17:00_to_20:00_NY":exec_met(cons,"late1700_to_2000"),
      } if gate else {},
      "clock_translation":{
        "16:00_NY":"23:00 Istanbul during US DST; 00:00 next day during US standard time",
        "08:00_NY":"15:00 Istanbul during US DST; 16:00 during US standard time",
        "08:15_NY":"15:15 Istanbul during US DST; 16:15 during US standard time"
      },
      "guardrails":[
        "Canonical reconstruction must match all published 145/125/93 and expert counts before post-issue results are promoted.",
        "08:15 is the first strictly post-08:00 15-minute bar used here; 08:00 bar open is not used as post-signal execution.",
        "15-minute execution outcomes are gross XAU/USD spot diagnostics, not instrument-specific net P&L."
      ],
      "api_meta":{"h1":m1,"m15":mm}
    }
    (OUT/"summary.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__":
    main()
