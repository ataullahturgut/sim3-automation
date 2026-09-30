from __future__ import annotations
import argparse,csv,json
from pathlib import Path

TEST_WINDOWS={
    "2025":{"start":"2025-01","end":"2025-12"},
    "2026_JAN_AUG":{"start":"2026-01","end":"2026-08"},
    "COMBINED":{"start":"2025-01","end":"2026-08"},
}

def load(p): return json.loads(Path(p).read_text())

def outcome(active,severity):
    if not active: return "OFF"
    if severity=="HIGH": return "HIGH_HIT"
    if severity=="MEDIUM": return "MEDIUM_HIT"
    return "FALSE_CALL"

def summarize(rows,flag):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in ev if r["severity"]=="HIGH"]
    med=[r for r in ev if r["severity"]=="MEDIUM"]
    norm=[r for r in ev if r["severity"]=="NORMAL"]
    allhi=[r for r in rows if r["severity"]=="HIGH"]
    allelev=[r for r in rows if r["severity"] in ("HIGH","MEDIUM")]
    return {
        "rows":len(rows),
        "events":len(ev),
        "high_n":len(allhi),
        "high_hits":len(hi),
        "medium_hits":len(med),
        "false_calls":len(norm),
        "high_recall":None if not allhi else len(hi)/len(allhi),
        "elevated_recall":None if not allelev else (len(hi)+len(med))/len(allelev),
        "false_call_rate":None if not ev else len(norm)/len(ev),
        "useful_call_rate":None if not ev else (len(hi)+len(med))/len(ev),
        "high_hit_targets":[r["target"] for r in hi],
        "medium_hit_targets":[r["target"] for r in med],
        "false_call_targets":[r["target"] for r in norm],
        "false_call_detail":[{"target":r["target"],"ape_pct":r["ape_pct"],"active_signals":r["active_signals"]} for r in norm],
        "missed_high_targets":[r["target"] for r in allhi if not r[flag]],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix-v2",required=True)
    ap.add_argument("--fine-tune",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-csv",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    mat=load(a.matrix_v2)
    tune=load(a.fine_tune)
    if mat.get("schema")!="GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_2026-09-30":
        raise RuntimeError(("BAD_MATRIX_SCHEMA",mat.get("schema")))
    if tune.get("schema")!="GOLD_MONTHLY_ALARM_FINE_TUNING_V1_2026-09-30":
        raise RuntimeError(("BAD_TUNE_SCHEMA",tune.get("schema")))
    if tune.get("status")!="FROZEN_DEV_ONLY":
        raise RuntimeError(("TUNE_NOT_FROZEN",tune.get("status")))

    cfg=tune["config"]
    t0s=list(cfg["T0_RED_signals"])
    t1s=list(cfg["T1_confirm_signals"])
    amber=list(cfg["AMBER_T0_signals"])
    shadow=list(cfg["SHADOW_T0_signals"])

    rows=[]
    for r0 in mat["rows"]:
        if not ("2025-01"<=r0["target"]<="2026-08"): continue
        r=dict(r0)
        r["T0_RED"]=any(bool(r[s]) for s in t0s)
        r["T1_RED_CONFIRM"]=bool(r["T1_WGC"]) and any(bool(r[s]) for s in t1s)
        r["T1_RED_INCREMENTAL"]=bool(r["T1_RED_CONFIRM"] and not r["T0_RED"])
        r["FINAL_RED"]=bool(r["T0_RED"] or r["T1_RED_CONFIRM"])
        r["AMBER_T0"]=any(bool(r[s]) for s in amber)
        r["SHADOW_T0"]=any(bool(r[s]) for s in shadow)
        r["FINAL_RED_outcome"]=outcome(r["FINAL_RED"],r["severity"])
        r["T0_RED_outcome"]=outcome(r["T0_RED"],r["severity"])
        r["T1_RED_CONFIRM_outcome"]=outcome(r["T1_RED_CONFIRM"],r["severity"])
        rows.append(r)

    if len(rows)!=20:
        raise RuntimeError(("TEST_ROW_COUNT",len(rows)))

    summaries={}
    for name,w in TEST_WINDOWS.items():
        rr=[r for r in rows if w["start"]<=r["target"]<=w["end"]]
        summaries[name]={
            "T0_RED":summarize(rr,"T0_RED"),
            "T1_RED_CONFIRM":summarize(rr,"T1_RED_CONFIRM"),
            "FINAL_RED":summarize(rr,"FINAL_RED"),
            "AMBER_T0":summarize(rr,"AMBER_T0"),
            "SHADOW_T0":summarize(rr,"SHADOW_T0"),
            "RAW_T0_STANDARD":summarize(rr,"T0_STANDARD"),
            "RAW_ANY_VISIBLE":summarize(rr,"ANY_VISIBLE"),
            "T1_incremental_red_targets":[r["target"] for r in rr if r["T1_RED_INCREMENTAL"]],
            "T1_incremental_high_hits":[r["target"] for r in rr if r["T1_RED_INCREMENTAL"] and r["severity"]=="HIGH"],
            "T1_incremental_false_calls":[r["target"] for r in rr if r["T1_RED_INCREMENTAL"] and r["severity"]=="NORMAL"],
        }

    out={
        "schema":"GOLD_MONTHLY_ALARM_FINE_TUNING_V1_TRANSPORT_2025_2026_2026-09-30",
        "status":"COMPLETE_UNTOUCHED_TRANSPORT",
        "frozen_config":cfg,
        "fine_tune_artifact_status":tune["status"],
        "rows":rows,
        "summaries":summaries,
        "governance":{
            "2025_2026_used_for_tuning":False,
            "config_modified_after_opening_test":False,
            "underlying_signal_definitions_changed":False,
            "forecast_modified":False,
            "routing_tested":False,
        }
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")

    fields=["target","origin","ape_pct","severity","active_signals","T0_RED","T0_RED_outcome",
            "T1_WGC","T1_RED_CONFIRM","T1_RED_INCREMENTAL","T1_RED_CONFIRM_outcome",
            "FINAL_RED","FINAL_RED_outcome","AMBER_T0","SHADOW_T0"]
    with open(a.output_csv,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            z={k:r[k] for k in fields}
            if isinstance(z["active_signals"],list):
                z["active_signals"]=",".join(z["active_signals"])
            w.writerow(z)

    md=[]
    md.append("# GOLD MONTHLY — Alarm Fine-Tuning V1 Transport 2025/2026\n")
    md.append("**Status:** untouched transport after DEV-only freeze.\n")
    md.append("## Frozen config\n")
    md.append(f"- T0_RED: {' OR '.join(t0s)}")
    md.append(f"- T1_RED_CONFIRM: T1_WGC AND ({' OR '.join(t1s)})")
    md.append(f"- AMBER_T0: {' OR '.join(amber)}")
    md.append(f"- SHADOW_T0: {' OR '.join(shadow)}")
    md.append("\n## Month-by-month\n")
    md.append("| Target | APE | Severity | T0 RED | T1 confirm | T1 incremental | Final RED | Outcome | Amber | Shadow | Active raw signals |")
    md.append("|---|---:|---|---:|---:|---:|---:|---|---:|---:|---|")
    for r in rows:
        md.append("| "+" | ".join([
            r["target"],f'{r["ape_pct"]:.3f}%',r["severity"],
            "Y" if r["T0_RED"] else "",
            "Y" if r["T1_RED_CONFIRM"] else "",
            "Y" if r["T1_RED_INCREMENTAL"] else "",
            "Y" if r["FINAL_RED"] else "",
            r["FINAL_RED_outcome"],
            "Y" if r["AMBER_T0"] else "",
            "Y" if r["SHADOW_T0"] else "",
            ", ".join(r["active_signals"]) if r["active_signals"] else "—"
        ])+" |")

    md.append("\n## Summary\n")
    md.append("| Window | Final events | HIGH hits | HIGH recall | MEDIUM hits | False calls | False-call rate | T1 incremental HIGH | T1 incremental false |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name in ["2025","2026_JAN_AUG","COMBINED"]:
        s=summaries[name]["FINAL_RED"]
        ti_h=len(summaries[name]["T1_incremental_high_hits"])
        ti_f=len(summaries[name]["T1_incremental_false_calls"])
        hr="—" if s["high_recall"] is None else f'{100*s["high_recall"]:.1f}%'
        fr="—" if s["false_call_rate"] is None else f'{100*s["false_call_rate"]:.1f}%'
        md.append(f'| {name} | {s["events"]} | {s["high_hits"]} | {hr} | {s["medium_hits"]} | {s["false_calls"]} | {fr} | {ti_h} | {ti_f} |')

    Path(a.output_md).write_text("\n".join(md)+"\n",encoding="utf-8")

    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "config":cfg,
        "2025":summaries["2025"],
        "2026":summaries["2026_JAN_AUG"],
        "combined":summaries["COMBINED"],
        "rows":[{"target":r["target"],"ape_pct":r["ape_pct"],"severity":r["severity"],
                 "T0_RED":r["T0_RED"],"T1_RED_CONFIRM":r["T1_RED_CONFIRM"],
                 "FINAL_RED":r["FINAL_RED"],"outcome":r["FINAL_RED_outcome"],
                 "amber":r["AMBER_T0"],"shadow":r["SHADOW_T0"],"active":r["active_signals"]} for r in rows]
    },sort_keys=True))

if __name__=="__main__":
    main()
