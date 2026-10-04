from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"

OUT_CSV=AX/"GOLD_H3_CATALYST_EVENT_DIAGNOSTIC_V1_2026-10-04.csv"
OUT_MD=AX/"GOLD_H3_CATALYST_EVENT_DIAGNOSTIC_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_CATALYST_EVENT_DIAGNOSTIC_V1_SUMMARY_2026-10-04.json"

# Official scheduled release dates (Eastern time), frozen for a mechanism diagnostic.
# Scope intentionally limited to high-impact scheduled macro events with stable publication conventions.
EVENTS = {}
def add(kind, dates):
    for d in dates:
        EVENTS.setdefault(pd.Timestamp(d).date(), []).append(kind)

add("CPI", [
"2025-01-15","2025-02-12","2025-03-12","2025-04-10","2025-05-13","2025-06-11","2025-07-15","2025-08-12","2025-09-11",
"2026-01-13","2026-02-13","2026-03-11","2026-04-10","2026-05-12","2026-06-10","2026-07-14","2026-08-12","2026-09-11",
])
add("NFP", [
"2025-01-10","2025-02-07","2025-03-07","2025-04-04","2025-05-02","2025-06-06","2025-07-03","2025-08-01","2025-09-05",
"2026-01-09","2026-02-11","2026-03-06","2026-04-03","2026-05-08","2026-06-05","2026-07-02","2026-08-07","2026-09-04",
])
add("FOMC", [
"2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17",
"2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16",
])

def b(x):
    return x.astype(str).str.lower().isin(["true","1","yes"])

def load():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"])
    p=pd.read_csv(PANEL,usecols=["feature_cutoff_date","momentum_up"],parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    z["v5_correct"]=(z.v5_pred==z.y_up.astype(int))
    z["true_reversal"]=(z.y_up.astype(int)!=z.momentum_up.astype(int))
    z["v5_follows_momentum"]=(z.v5_pred==z.momentum_up.astype(int))
    z["v5_missed_reversal"]=z.true_reversal & z.v5_follows_momentum

    # Historical SAGE OCS exists only on its mature common universe; elsewhere SAGE=V5.
    try:
        s=pd.read_csv(SAGE,usecols=["feature_cutoff_date","ocs_candidate"],parse_dates=["feature_cutoff_date"])
        s["ocs_candidate"]=b(s.ocs_candidate)
        z=z.merge(s,on="feature_cutoff_date",how="left",validate="one_to_one")
    except Exception:
        z["ocs_candidate"]=False
    z["ocs_candidate"]=z.ocs_candidate.fillna(False).astype(bool)
    z["sage_pred"]=np.where(z.ocs_candidate,1-z.v5_pred,z.v5_pred).astype(int)
    z["sage_correct"]=(z.sage_pred==z.y_up.astype(int))
    z["sage_missed_reversal"]=z.true_reversal & (z.sage_pred==z.momentum_up.astype(int))

    z=z[(z.feature_cutoff_date>=pd.Timestamp("2025-01-01"))&(z.feature_cutoff_date<=pd.Timestamp("2026-09-24"))].copy()
    z["event_types"]=z.feature_cutoff_date.dt.date.map(lambda d:"+".join(EVENTS.get(d,[])))
    z["event_day"]=z.event_types.ne("")
    z["year"]=z.feature_cutoff_date.dt.year
    z["half"]=z.feature_cutoff_date.dt.year.astype(str)+"_"+np.where(z.feature_cutoff_date.dt.month<=6,"H1","H2")
    return z

def pct(x):
    return 100*float(x) if pd.notna(x) else np.nan

def summarize(g):
    n=len(g)
    return {
        "n":n,
        "reversal_n":int(g.true_reversal.sum()),
        "reversal_rate":float(g.true_reversal.mean()) if n else np.nan,
        "v5_error_n":int((~g.v5_correct).sum()),
        "v5_error_rate":float((~g.v5_correct).mean()) if n else np.nan,
        "v5_missed_reversal_n":int(g.v5_missed_reversal.sum()),
        "sage_error_n":int((~g.sage_correct).sum()),
        "sage_error_rate":float((~g.sage_correct).mean()) if n else np.nan,
        "sage_missed_reversal_n":int(g.sage_missed_reversal.sum()),
        "mean_abs_r3":float(g.target_r3.abs().mean()) if n else np.nan,
    }

def main():
    z=load()
    rows=[]
    for y in [2025,2026]:
        yy=z[z.year==y]
        for lab,mask in [("EVENT",yy.event_day),("NON_EVENT",~yy.event_day)]:
            rows.append({"year":y,"bucket":lab,**summarize(yy[mask])})
    for kind in ["CPI","NFP","FOMC"]:
        g=z[z.event_types.str.contains(kind,regex=False)]
        rows.append({"year":0,"bucket":kind,**summarize(g)})
    rows.append({"year":0,"bucket":"ALL_EVENT",**summarize(z[z.event_day])})
    rows.append({"year":0,"bucket":"ALL_NON_EVENT",**summarize(z[~z.event_day])})
    sm=pd.DataFrame(rows)
    sm.to_csv(OUT_CSV,index=False)

    ev=z[z.event_day].copy()
    # diagnostic concentration among the actual remaining misses
    all_sage_miss=int(z.sage_missed_reversal.sum())
    event_sage_miss=int(ev.sage_missed_reversal.sum())
    all_v5_miss=int(z.v5_missed_reversal.sum())
    event_v5_miss=int(ev.v5_missed_reversal.sum())

    out={
        "scope":"2025-01-01..2026-09-24",
        "rows":len(z),
        "event_rows":int(z.event_day.sum()),
        "summary":sm.to_dict("records"),
        "v5_missed_reversal_total":all_v5_miss,
        "v5_missed_reversal_on_event_days":event_v5_miss,
        "sage_missed_reversal_total":all_sage_miss,
        "sage_missed_reversal_on_event_days":event_sage_miss,
    }
    OUT_JSON.write_text(json.dumps(out,indent=2,default=str)+"\n")

    lines=[
      "# CATALYST-H3 V1 — EVENT-DAY DIAGNOSTIC",
      "",
      "**Status:** retrospective mechanism diagnostic; not a promotion test.",
      "",
      "Events: scheduled CPI, Employment Situation/NFP, and FOMC policy-decision dates.",
      "Event flag is based on the H3 feature_cutoff_date, so the scheduled release has occurred before the canonical end-of-day H3 decision state.",
      "",
      "## Event vs non-event",
      "",
      "| Year/Bucket | N | Reversal rate | V5 error | V5 missed rev | SAGE error | SAGE missed rev | Mean |H3| |",
      "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in rows:
        y="ALL" if r["year"]==0 else str(r["year"])
        lines.append(f"| {y} {r['bucket']} | {r['n']} | {pct(r['reversal_rate']):.2f}% | {pct(r['v5_error_rate']):.2f}% | {r['v5_missed_reversal_n']} | {pct(r['sage_error_rate']):.2f}% | {r['sage_missed_reversal_n']} | {pct(r['mean_abs_r3']):.2f}% |")
    lines += [
      "",
      "## Concentration",
      "",
      f"- V5 missed reversals on event days: **{event_v5_miss}/{all_v5_miss}**",
      f"- SAGE missed reversals on event days: **{event_sage_miss}/{all_sage_miss}**",
      "",
      "This diagnostic answers only whether scheduled macro-event days enrich reversal/error states. It does not use the surprise sign or intraday post-release response yet."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
