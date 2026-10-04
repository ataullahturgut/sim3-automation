from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
VAST_HOURLY=AX/"GOLD_H3_VAST_V1_HOURLY_PANEL_2026-10-04.csv"

OUT_CSV=AX/"GOLD_H3_REACTION_DECAY_CONFIRM_V1_2026-10-04.csv"
OUT_JSON=AX/"GOLD_H3_REACTION_DECAY_CONFIRM_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_REACTION_DECAY_CONFIRM_V1_RESULT_2026-10-04.md"

EVENTS=[
("2025-07-01","JOLTS","10:00",  6.0),
("2025-07-02","ADP","08:15",    0.0),
("2025-07-03","NFP","08:30",   10.0),
("2025-07-15","CPI","08:30",    5.0),
("2025-07-29","JOLTS","10:00", -5.0),
("2025-07-30","ADP","08:15",    8.0),
("2025-07-30","FOMC","14:00",   8.0),
("2025-07-31","PCE","08:30",    0.0),
("2025-08-01","NFP","08:30",  -25.0),
("2025-08-12","CPI","08:30",   -4.0),
("2025-08-29","PCE","08:30",   -3.0),
("2025-09-03","JOLTS","10:00", -5.0),
("2025-09-04","ADP","08:15",   -2.0),
("2025-09-05","NFP","08:30",   -8.0),
("2025-09-11","CPI","08:30",   -2.0),
("2025-09-17","FOMC","14:00",   1.0),
("2025-09-26","PCE","08:30",   -1.0),
("2025-09-30","JOLTS","10:00", -3.0),
]

def load_gc():
    d=pd.read_csv(VAST_HOURLY,usecols=["ts","GC_close"])
    d["ts"]=pd.to_datetime(d.ts,utc=True)
    d=d.rename(columns={"GC_close":"gc"}).dropna().drop_duplicates("ts").sort_values("ts")
    return d

def load_h3():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"])
    p=pd.read_csv(PANEL,usecols=["feature_cutoff_date","momentum_up","h_ret_12"],parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True)

def last_px(gc,t):
    q=gc[gc.ts<=t].tail(1)
    if q.empty: return np.nan,pd.NaT
    return float(q.gc.iloc[0]),q.ts.iloc[0]

def event_path(gc,date,time):
    rel=pd.Timestamp(f"{date} {time}",tz="America/New_York").tz_convert("UTC")
    pre,pre_ts=last_px(gc,rel-pd.Timedelta(hours=1))
    first,first_ts=last_px(gc,rel+pd.Timedelta(hours=2))
    close_t=(pd.Timestamp(date).tz_localize("America/New_York")+pd.Timedelta(hours=16)).tz_convert("UTC")
    close,close_ts=last_px(gc,close_t)
    if not all(np.isfinite([pre,first,close])): return None
    r1=float(np.log(first/pre))
    rt=float(np.log(close/pre))
    r2=float(np.log(close/first))
    decay=bool((r1>0 and r2<0 and rt>0) or (r1<0 and r2>0 and rt<0))
    return dict(pre_ts=pre_ts,first_ts=first_ts,close_ts=close_ts,
                first_ret=r1,total_ret=rt,post_first_ret=r2,reaction_decay=decay)

def main():
    gc=load_gc(); h=load_h3()
    rows=[]
    for date,event,time,dgs2_bp in EVENTS:
        cur=h[h.feature_cutoff_date==pd.Timestamp(date)].tail(1)
        if cur.empty: continue
        c=cur.iloc[0]
        path=event_path(gc,date,time)
        if path is None: continue
        mom=int(c.momentum_up); y=int(c.y_up); pred=int(c.v5_pred)
        reversal=bool(y!=mom)
        missed=bool(pred==mom and y!=mom)
        candidate=bool(path["reaction_decay"] and pred==mom)
        rescue=bool(candidate and pred!=y)
        broken=bool(candidate and pred==y)
        rows.append({
            "date":date,"event":event,"time":time,"dgs2_change_bp":dgs2_bp,
            "momentum_up":mom,"y_up":y,"v5_pred":pred,
            "h3_return":float(c.target_r3),
            "h3_reversal":reversal,"v5_missed_reversal":missed,
            **path,
            "candidate_flip":candidate,"rescue":rescue,"broken":broken,
        })
    q=pd.DataFrame(rows)
    q.to_csv(OUT_CSV,index=False)

    d=q[q.reaction_decay]
    nd=q[~q.reaction_decay]
    stats={
        "n_events":int(len(q)),
        "n_decay":int(len(d)),
        "decay_reversals":int(d.h3_reversal.sum()),
        "decay_reversal_rate":float(d.h3_reversal.mean()) if len(d) else np.nan,
        "n_nondecay":int(len(nd)),
        "nondecay_reversals":int(nd.h3_reversal.sum()),
        "nondecay_reversal_rate":float(nd.h3_reversal.mean()) if len(nd) else np.nan,
        "decay_v5_missed":int(d.v5_missed_reversal.sum()),
        "candidate_actions":int(q.candidate_flip.sum()),
        "rescues":int(q.rescue.sum()),
        "broken":int(q.broken.sum()),
    }
    stats["net"]=stats["rescues"]-stats["broken"]
    stats["precision"]=stats["rescues"]/max(stats["candidate_actions"],1)

    OUT_JSON.write_text(json.dumps({"stats":stats,"events":q.to_dict("records")},indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 — REACTION DECAY CONFIRMATION V1","",
      "**Window:** 2025-07-01 .. 2025-09-30",
      "**Rule:** frozen from June discovery; no threshold tuning.","",
      "## Events","",
      "| Date | Event | 2Y Δbp | First ~2h | Post-first | To 16ET | Decay | H3 reversal | V5 missed | Candidate rescue/broken |",
      "|---|---|---:|---:|---:|---:|---|---|---|---|"
    ]
    for r in q.itertuples():
        tag="RESCUE" if r.rescue else ("BROKEN" if r.broken else "—")
        lines.append(f"| {r.date} | {r.event} | {r.dgs2_change_bp:+.0f} | {100*r.first_ret:+.2f}% | {100*r.post_first_ret:+.2f}% | {100*r.total_ret:+.2f}% | {r.reaction_decay} | {r.h3_reversal} | {r.v5_missed_reversal} | {tag} |")
    lines += ["","## Confirmation summary","",
      f"- events: **{stats['n_events']}**",
      f"- reaction decay: **{stats['n_decay']}**; H3 reversal **{stats['decay_reversals']}/{max(stats['n_decay'],1)} = {100*stats['decay_reversal_rate']:.1f}%**",
      f"- no decay: **{stats['n_nondecay']}**; H3 reversal **{stats['nondecay_reversals']}/{max(stats['n_nondecay'],1)} = {100*stats['nondecay_reversal_rate']:.1f}%**",
      f"- decay events that were V5 missed reversals: **{stats['decay_v5_missed']}**",
      f"- incremental V5-follows-momentum actions: **{stats['candidate_actions']}**",
      f"- rescue / broken / net: **{stats['rescues']} / {stats['broken']} / {stats['net']:+d}**",
      f"- action precision: **{100*stats['precision']:.1f}%**",
      "",
      "Historical diagnostic only. Hourly Gold uses the frozen VAST Yahoo GC=F panel; 2Y daily changes are copied from official U.S. Treasury daily par-yield tables."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
