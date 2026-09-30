from __future__ import annotations
import argparse,csv,json
from pathlib import Path

SIGNALS=["A","B","C","D","E","G","H","I1","I2","T1_WGC"]

STATUS={
 "A":"SELECTIVE_T0_ALARM_CANDIDATE",
 "B":"WARNING_ONLY",
 "C":"MEDIUM_ERROR_LOW_EVENT_WARNING",
 "D":"RARE_HIGH_HIT",
 "E":"DISCOVERY_PERIOD_UNVALIDATED",
 "G":"HIGH_MOVEMENT_REGIME_WARNING",
 "H":"CFTC_POSITIONING_WARNING",
 "I1":"ETF_TRANSITION_WARNING_CANDIDATE",
 "I2":"HISTORICALLY_SUPPORTED_REGIME_WARNING",
 "T1_WGC":"EARLY_MONTH_REPORT_WARNING",
}

def load(p): return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True)
    ap.add_argument("--etf-dynamic",required=True)
    ap.add_argument("--wgc-t1",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-csv",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    sev=load(a.severity)
    etf=load(a.etf_dynamic)
    wgc=load(a.wgc_t1)

    if sev.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30":
        raise RuntimeError(("BAD_SEVERITY_SCHEMA",sev.get("schema")))
    if etf.get("schema")!="GOLD_MONTHLY_CHHHO_ETF_DYNAMIC_REGIME_V2_2026-09-30":
        raise RuntimeError(("BAD_ETF_SCHEMA",etf.get("schema")))
    if wgc.get("schema")!="GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V4_2026-09-30":
        raise RuntimeError(("BAD_WGC_SCHEMA",wgc.get("schema")))

    sm={r["target"]:r for r in sev["rows"]}
    em={r["target"]:r for r in etf["rows"]}
    wm={r["page_month"]:r for r in wgc["rows"] if r.get("severity") is not None}

    targets=sorted(sm)
    if len(targets)!=58: raise RuntimeError(("SEVERITY_ROW_COUNT",len(targets)))

    rows=[]
    for t in targets:
        s=sm[t]
        e=em.get(t)
        w=wm.get(t)
        if e is None: raise RuntimeError(("ETF_ROW_MISSING",t))
        if w is None: raise RuntimeError(("WGC_ROW_MISSING",t))

        row={
          "target":t,
          "origin":s["origin"],
          "forecast":float(s["forecast"]),
          "actual":float(s["actual"]),
          "ae":float(s["ae"]),
          "ape_pct":float(s["ape_pct"]),
          "severity":s["ape_severity"],
          "A":bool(s["A"]),
          "B":bool(s["B"]),
          "C":bool(s["C"]),
          "D":bool(s["D"]),
          "E":bool(s["E"]),
          "G":bool(s["G"]),
          "H":bool(s["H"]),
          "I1":bool(e["ETF_FLOW_DETERIORATION_Q10"]),
          "I2":bool(e["ETF_BREADTH2_STREAK_Q90"]),
          "T1_WGC":bool(w["R2_WGC"]),
          "T1_publication_date":w["publication_date"],
          "T1_publish_day":int(w["publish_day"]),
          "T1_timely":bool(w["TIMELY_T1"]),
        }
        row["T0_STANDARD"]=bool(row["A"] or row["B"] or row["C"] or row["D"] or row["H"])
        row["T0_ALL_VISIBLE"]=bool(row["A"] or row["B"] or row["C"] or row["D"] or row["E"] or row["G"] or row["H"] or row["I1"] or row["I2"])
        row["T0_PLUS_T1_STANDARD"]=bool(row["T0_STANDARD"] or row["T1_WGC"])
        row["ANY_VISIBLE"]=bool(row["T0_ALL_VISIBLE"] or row["T1_WGC"])
        row["active_signals"]=[x for x in SIGNALS if row[x]]
        rows.append(row)

    def signal_stats(sig):
        ev=[r for r in rows if r[sig]]
        hi=[r for r in ev if r["severity"]=="HIGH"]
        med=[r for r in ev if r["severity"]=="MEDIUM"]
        norm=[r for r in ev if r["severity"]=="NORMAL"]
        allhi=[r for r in rows if r["severity"]=="HIGH"]
        return {
          "status":STATUS[sig],
          "events":len(ev),
          "high_hits":len(hi),
          "medium_hits":len(med),
          "normal_false_alarms":len(norm),
          "high_precision":None if not ev else len(hi)/len(ev),
          "high_recall":len(hi)/len(allhi),
          "event_targets":[r["target"] for r in ev],
          "high_hit_targets":[r["target"] for r in hi],
        }

    stats={s:signal_stats(s) for s in SIGNALS}

    overlaps={}
    for i,x in enumerate(SIGNALS):
        for y in SIGNALS[i+1:]:
            both=[r["target"] for r in rows if r[x] and r[y]]
            if both:
                overlaps[f"{x}&{y}"]={"count":len(both),"targets":both}

    per_year={}
    for r in rows:
        y=r["target"][:4]
        if y not in per_year:
            per_year[y]={s:0 for s in SIGNALS}
            per_year[y].update({"HIGH":0,"MEDIUM":0,"NORMAL":0})
        for s in SIGNALS:
            per_year[y][s]+=int(r[s])
        per_year[y][r["severity"]]+=1

    summaries={
      "high_rows":[r for r in rows if r["severity"]=="HIGH"],
      "medium_rows":[r for r in rows if r["severity"]=="MEDIUM"],
      "high_no_t0_standard":[r["target"] for r in rows if r["severity"]=="HIGH" and not r["T0_STANDARD"]],
      "high_no_t0_all_visible":[r["target"] for r in rows if r["severity"]=="HIGH" and not r["T0_ALL_VISIBLE"]],
      "high_no_any_visible":[r["target"] for r in rows if r["severity"]=="HIGH" and not r["ANY_VISIBLE"]],
      "signal_stats":stats,
      "pairwise_overlaps":overlaps,
      "per_year":per_year,
    }

    out={
      "schema":"GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V1_2026-09-30",
      "status":"COMPLETE",
      "signal_status":STATUS,
      "rows":rows,
      "summaries":summaries,
      "governance":{
        "thresholds_retuned":False,
        "new_alarm_rule_created":False,
        "forecast_modified":False,
        "routing_tested":False,
        "source_artifacts":[11090497943,11090919621,11093192454],
      }
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")

    fields=["target","origin","forecast","actual","ae","ape_pct","severity"]+SIGNALS+[
      "T0_STANDARD","T0_ALL_VISIBLE","T0_PLUS_T1_STANDARD","ANY_VISIBLE",
      "T1_publication_date","T1_publish_day","T1_timely","active_signals"
    ]
    with open(a.output_csv,"w",newline="",encoding="utf-8-sig") as f:
        wri=csv.DictWriter(f,fieldnames=fields)
        wri.writeheader()
        for r in rows:
            z={k:r[k] for k in fields}
            z["active_signals"]=",".join(r["active_signals"])
            wri.writerow(z)

    md=[]
    md.append("# GOLD MONTHLY — Unified Alarm Matrix V1\n")
    md.append("**Date:** 2026-09-30  ")
    md.append("**Status:** COMPLETE / CONSOLIDATED  ")
    md.append("**Rows:** 58  \n")
    md.append("Primary severity: APE — NORMAL <2.5%, MEDIUM 2.5–<3.0%, HIGH >=3.0%.\n")
    md.append("## Signal status\n")
    for s in SIGNALS:
        md.append(f"- **{s}** — {STATUS[s]}")
    md.append("\n## Complete 58-row matrix\n")
    hdr=["Target","APE","Severity","A","B","C","D","E","G","H","I1","I2","T1","Active"]
    md.append("| "+" | ".join(hdr)+" |")
    md.append("|"+"|".join(["---"]*len(hdr))+"|")
    for r in rows:
        vals=[
          r["target"],f'{r["ape_pct"]:.3f}%',r["severity"],
          *[("✓" if r[s] else "") for s in ["A","B","C","D","E","G","H","I1","I2","T1_WGC"]],
          ", ".join(r["active_signals"]) if r["active_signals"] else "—"
        ]
        md.append("| "+" | ".join(vals)+" |")

    md.append("\n## HIGH blind spots\n")
    md.append("- No T0 standard A/B/C/D/H: "+(", ".join(summaries["high_no_t0_standard"]) or "none"))
    md.append("- No T0 visible A/B/C/D/E/G/H/I1/I2: "+(", ".join(summaries["high_no_t0_all_visible"]) or "none"))
    md.append("- No visible T0 or T1 signal: "+(", ".join(summaries["high_no_any_visible"]) or "none"))

    md.append("\n## Signal statistics vs HIGH APE\n")
    md.append("| Signal | Events | HIGH hits | MEDIUM hits | Normal false alarms | HIGH precision | HIGH recall |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    for s in SIGNALS:
        q=stats[s]
        hp="—" if q["high_precision"] is None else f'{100*q["high_precision"]:.1f}%'
        hr=f'{100*q["high_recall"]:.1f}%'
        md.append(f'| {s} | {q["events"]} | {q["high_hits"]} | {q["medium_hits"]} | {q["normal_false_alarms"]} | {hp} | {hr} |')

    Path(a.output_md).write_text("\n".join(md)+"\n",encoding="utf-8")

    print("OUTPUT_GATE=PASS")
    print(json.dumps({
      "high_no_t0_standard":summaries["high_no_t0_standard"],
      "high_no_t0_all_visible":summaries["high_no_t0_all_visible"],
      "high_no_any_visible":summaries["high_no_any_visible"],
      "signal_stats":stats,
      "high_rows":[{"target":r["target"],"ape_pct":r["ape_pct"],"active":r["active_signals"]} for r in rows if r["severity"]=="HIGH"],
    },sort_keys=True))

if __name__=="__main__":
    main()
