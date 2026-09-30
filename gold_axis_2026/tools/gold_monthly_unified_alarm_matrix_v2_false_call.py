from __future__ import annotations
import argparse,csv,json
from pathlib import Path

INDIVIDUAL=["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
UNIONS=["T0_STANDARD","T0_ALL_VISIBLE","T0_PLUS_T1_STANDARD","ANY_VISIBLE"]
ALL=INDIVIDUAL+UNIONS

def load(p): return json.loads(Path(p).read_text())

def outcome(row,flag):
    if not row[flag]: return "OFF"
    if row["severity"]=="HIGH": return "HIGH_HIT"
    if row["severity"]=="MEDIUM": return "MEDIUM_HIT"
    return "FALSE_CALL"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix-v1",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-csv",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    src=load(a.matrix_v1)
    if src.get("schema")!="GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V1_2026-09-30":
        raise RuntimeError(("BAD_MATRIX_SCHEMA",src.get("schema")))
    rows=[dict(r) for r in src["rows"]]
    if len(rows)!=58: raise RuntimeError(("ROW_COUNT",len(rows)))

    stats={}
    for flag in ALL:
        for r in rows:
            r[f"{flag}_outcome"]=outcome(r,flag)
        ev=[r for r in rows if r[flag]]
        hi=[r for r in ev if r["severity"]=="HIGH"]
        med=[r for r in ev if r["severity"]=="MEDIUM"]
        norm=[r for r in ev if r["severity"]=="NORMAL"]
        high_all=[r for r in rows if r["severity"]=="HIGH"]
        elev_all=[r for r in rows if r["severity"] in ("MEDIUM","HIGH")]
        stats[flag]={
            "events":len(ev),
            "high_hits":len(hi),
            "medium_hits":len(med),
            "false_calls":len(norm),
            "high_precision":None if not ev else len(hi)/len(ev),
            "useful_call_rate":None if not ev else (len(hi)+len(med))/len(ev),
            "false_call_rate":None if not ev else len(norm)/len(ev),
            "high_recall":None if not high_all else len(hi)/len(high_all),
            "elevated_recall":None if not elev_all else (len(hi)+len(med))/len(elev_all),
            "high_hit_targets":[r["target"] for r in hi],
            "medium_hit_targets":[r["target"] for r in med],
            "false_call_targets":[r["target"] for r in norm],
            "false_call_detail":[
                {
                    "target":r["target"],
                    "ape_pct":r["ape_pct"],
                    "active_signals":r["active_signals"],
                } for r in norm
            ],
        }

    normal_rows=[r for r in rows if r["severity"]=="NORMAL"]
    multi_false=[]
    for r in normal_rows:
        active=[s for s in INDIVIDUAL if r[s]]
        if len(active)>=2:
            multi_false.append({
                "target":r["target"],
                "ape_pct":r["ape_pct"],
                "active_signals":active,
                "n_active":len(active),
            })

    yearly={}
    for r in rows:
        y=r["target"][:4]
        yearly.setdefault(y,{})
        for flag in ALL:
            yearly[y].setdefault(flag,{"events":0,"high_hits":0,"medium_hits":0,"false_calls":0})
            if r[flag]:
                z=yearly[y][flag]; z["events"]+=1
                if r["severity"]=="HIGH": z["high_hits"]+=1
                elif r["severity"]=="MEDIUM": z["medium_hits"]+=1
                else: z["false_calls"]+=1

    out={
        "schema":"GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_2026-09-30",
        "status":"COMPLETE",
        "rows":rows,
        "signal_stats":stats,
        "multi_signal_false_calls":multi_false,
        "yearly":yearly,
        "governance":{
            "thresholds_retuned":False,
            "new_boolean_rule_created":False,
            "forecast_modified":False,
            "routing_tested":False,
            "medium_counted_as_false_call":False,
        }
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")

    # CSV: keep original fields plus outcome columns.
    base=list(src["rows"][0].keys())
    fields=base+[f"{s}_outcome" for s in ALL]
    with open(a.output_csv,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            z={k:r.get(k) for k in fields}
            if isinstance(z.get("active_signals"),list):
                z["active_signals"]=",".join(z["active_signals"])
            w.writerow(z)

    md=[]
    md.append("# GOLD MONTHLY — Unified Alarm Matrix V2 False-Call Accounting\n")
    md.append("**Severity:** NORMAL <2.5%, MEDIUM 2.5–<3.0%, HIGH >=3.0%.  ")
    md.append("MEDIUM alarms are useful warnings, not false calls.\n")
    md.append("## Signal quality\n")
    md.append("| Signal | Events | HIGH hit | MEDIUM hit | False call | Useful rate | False-call rate | HIGH recall |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in ALL:
        q=stats[s]
        useful="—" if q["useful_call_rate"] is None else f'{100*q["useful_call_rate"]:.1f}%'
        fcr="—" if q["false_call_rate"] is None else f'{100*q["false_call_rate"]:.1f}%'
        hr="—" if q["high_recall"] is None else f'{100*q["high_recall"]:.1f}%'
        md.append(f'| {s} | {q["events"]} | {q["high_hits"]} | {q["medium_hits"]} | {q["false_calls"]} | {useful} | {fcr} | {hr} |')
    md.append("\n## Exact false calls by signal\n")
    for s in ALL:
        q=stats[s]
        md.append(f"### {s}")
        if not q["false_call_detail"]:
            md.append("- None")
        else:
            for d in q["false_call_detail"]:
                act=", ".join(d["active_signals"]) if d["active_signals"] else "—"
                md.append(f'- {d["target"]}: APE {d["ape_pct"]:.3f}% — active: {act}')
    md.append("\n## Normal months with multiple simultaneous signals\n")
    if not multi_false:
        md.append("- None")
    else:
        for d in multi_false:
            md.append(f'- {d["target"]}: APE {d["ape_pct"]:.3f}% — {", ".join(d["active_signals"])}')
    Path(a.output_md).write_text("\n".join(md)+"\n",encoding="utf-8")

    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "stats":stats,
        "multi_signal_false_calls":multi_false
    },sort_keys=True))

if __name__=="__main__":
    main()
