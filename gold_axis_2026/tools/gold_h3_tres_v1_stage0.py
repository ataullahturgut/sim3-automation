from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

PRICES=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"

OUT_LEDGER=AX/"GOLD_H3_TRES_V1_STAGE0_EVENT_LEDGER_2026-10-04.csv"
OUT_YEAR=AX/"GOLD_H3_TRES_V1_STAGE0_EVENT_YEARLY_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_TRES_V1_STAGE0_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_TRES_V1_STAGE0_RESULT_2026-10-04.md"

TOL=1e-10
SCALES=[0.75,1.00,1.25]

def first_passage(gs,barrier):
    for i,g in enumerate(gs,1):
        if g>=barrier:
            return "CONTINUATION",i
        if g<=-barrier:
            return "REVERSAL",i
    return "CENSORED",None

def main():
    px=pd.read_csv(PRICES)
    px["date"]=pd.to_datetime(px.date)
    px=px.sort_values("date").reset_index(drop=True)
    if (px.gold<=0).any():
        raise RuntimeError("Non-positive Gold price found")
    px["gold_log"]=np.log(px.gold.astype(float))
    px["gold_r1"]=px.gold_log.diff()
    px["sigma20"]=px.gold_r1.rolling(20,min_periods=20).std(ddof=0)

    panel=pd.read_csv(PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        panel[c]=pd.to_datetime(panel[c])
    panel=panel.sort_values("feature_cutoff_date").reset_index(drop=True)

    pos={d:i for i,d in enumerate(px.date)}
    rows=[]
    failures=[]

    for r in panel.itertuples():
        d0=pd.Timestamp(r.feature_cutoff_date)
        if d0 not in pos:
            failures.append({"origin":str(d0.date()),"reason":"MISSING_ORIGIN_PRICE"})
            continue
        i=pos[d0]
        if i+3>=len(px):
            failures.append({"origin":str(d0.date()),"reason":"INSUFFICIENT_FUTURE_PATH"})
            continue

        p0=float(px.iloc[i].gold)
        fut=px.iloc[i+1:i+4]
        dates=list(fut.date)
        vals=list(fut.gold.astype(float))

        if dates[2] != pd.Timestamp(r.target_end_date_h3):
            failures.append({
                "origin":str(d0.date()),"reason":"TARGET_END_DATE_MISMATCH",
                "resolved_h3":str(dates[2].date()),
                "panel_h3":str(pd.Timestamp(r.target_end_date_h3).date())
            })
            continue

        rr=float(np.log(vals[2]/p0))
        diff=abs(rr-float(r.target_r3))
        if diff>TOL:
            failures.append({
                "origin":str(d0.date()),"reason":"TARGET_R3_MISMATCH",
                "recomputed":rr,"panel":float(r.target_r3),"abs_diff":diff
            })
            continue

        sigma=float(px.iloc[i].sigma20)
        if not np.isfinite(sigma) or sigma<=0:
            failures.append({"origin":str(d0.date()),"reason":"INVALID_SIGMA20","sigma20":sigma})
            continue

        m=1.0 if float(r.h_ret_12)>=0 else -1.0
        gs=[float(m*np.log(v/p0)) for v in vals]

        out={
            "feature_cutoff_date":d0,
            "forecast_issue_date":pd.Timestamp(r.forecast_issue_date),
            "target_end_date_h3":pd.Timestamp(r.target_end_date_h3),
            "year":int(r.year),
            "y_up":int(r.y_up),
            "target_r3":float(r.target_r3),
            "h_ret_12":float(r.h_ret_12),
            "momentum_up":int(float(r.h_ret_12)>=0),
            "terminal_reversal":int(int(r.y_up) != int(float(r.h_ret_12)>=0)),
            "origin_gold":p0,
            "h1_date":dates[0],"h2_date":dates[1],"h3_date":dates[2],
            "h1_gold":vals[0],"h2_gold":vals[1],"h3_gold":vals[2],
            "g1":gs[0],"g2":gs[1],"g3":gs[2],
            "sigma20":sigma,
            "target_identity_abs_diff":diff,
            "sigma_last_date":d0
        }
        for s in SCALES:
            b=s*sigma
            et,ed=first_passage(gs,b)
            key=str(s).replace(".","p")
            out[f"barrier_{key}"]=b
            out[f"event_type_{key}"]=et
            out[f"event_day_{key}"]=ed
        rows.append(out)

    ledger=pd.DataFrame(rows)
    ledger.to_csv(OUT_LEDGER,index=False)

    fail_count=len(failures)
    max_diff=float(ledger.target_identity_abs_diff.max()) if len(ledger) else None
    gate_pass=(fail_count==0 and len(ledger)==len(panel) and max_diff is not None and max_diff<=TOL)

    primary="1p0"
    yearly=[]
    for y,g in ledger.groupby("year"):
        vc=g[f"event_type_{primary}"].value_counts()
        yearly.append({
            "year":int(y),"n":len(g),
            "continuation":int(vc.get("CONTINUATION",0)),
            "reversal":int(vc.get("REVERSAL",0)),
            "censored":int(vc.get("CENSORED",0)),
            "terminal_reversal_n":int(g.terminal_reversal.sum())
        })
    pd.DataFrame(yearly).to_csv(OUT_YEAR,index=False)

    conditional={}
    for s in SCALES:
        key=str(s).replace(".","p")
        items=[]
        for et,g in ledger.groupby(f"event_type_{key}"):
            items.append({
                "event_type":et,
                "n":len(g),
                "terminal_reversal_rate":float(g.terminal_reversal.mean()),
                "mean_abs_terminal_h3":float(g.target_r3.abs().mean())
            })
        conditional[str(s)]=items

    examples=[]
    q=ledger[
        ((ledger[f"event_type_{primary}"]=="REVERSAL")&(ledger.terminal_reversal==0))
        | ((ledger[f"event_type_{primary}"]=="CONTINUATION")&(ledger.terminal_reversal==1))
    ].copy()
    for r in q.head(20).itertuples():
        examples.append({
            "origin":str(pd.Timestamp(r.feature_cutoff_date).date()),
            "event_type":getattr(r,f"event_type_{primary}"),
            "event_day":getattr(r,f"event_day_{primary}"),
            "terminal_reversal":int(r.terminal_reversal),
            "target_r3":float(r.target_r3),
            "g1":float(r.g1),"g2":float(r.g2),"g3":float(r.g3),
            "sigma20":float(r.sigma20)
        })

    summary={
        "schema":"TRES_H3_V1_STAGE0",
        "status":"PASS" if gate_pass else "STOP_MODELING_AND_REPAIR_TIMELINE",
        "panel_rows":len(panel),
        "audited_rows":len(ledger),
        "failure_count":fail_count,
        "failures":failures[:50],
        "max_target_identity_abs_diff":max_diff,
        "primary_barrier_scale":1.0,
        "conditional_terminal_reversal":conditional,
        "yearly":yearly,
        "disagreement_examples":examples
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# TRES-H3 V1 — STAGE 0 EVENT-TIME AUDIT RESULT","",
        f"**Status:** **{summary['status']}**  ",
        f"- panel rows: **{len(panel)}**",
        f"- audited rows: **{len(ledger)}**",
        f"- failures: **{fail_count}**",
        f"- max |recomputed target_r3 - panel target_r3|: **{max_diff:.3e}**" if max_diff is not None else "- target identity unavailable",
        "",
        "## Primary 1.00×sigma20 event counts","",
        "| Year | N | Continuation | Reversal | Censored | Terminal reversal |",
        "|---:|---:|---:|---:|---:|---:|"
    ]
    for x in yearly:
        lines.append(f"| {x['year']} | {x['n']} | {x['continuation']} | {x['reversal']} | {x['censored']} | {x['terminal_reversal_n']} |")

    lines += ["","## Terminal H3 reversal rate conditional on first-passage state",""]
    for s in SCALES:
        lines.append(f"### Barrier {s:.2f}× sigma20")
        for x in conditional[str(s)]:
            lines.append(f"- {x['event_type']}: n={x['n']}, terminal reversal **{100*x['terminal_reversal_rate']:.2f}%**, mean |H3| **{100*x['mean_abs_terminal_h3']:.2f}%**")
        lines.append("")

    lines += ["## Integrity interpretation",""]
    if gate_pass:
        lines += [
            "- origin / H1 / H2 / H3 date mapping is internally consistent with the frozen H3 target.",
            "- primary and robustness first-passage labels were constructed without future information entering the origin barrier.",
            "- Stage 1 competing-risk modeling is authorized."
        ]
    else:
        lines += [
            "- one or more frozen timeline identities failed.",
            "- Stage 1 modeling is prohibited until the timeline is repaired."
        ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
