from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

DEV_START="2022-04"
DEV_END="2024-12"
T0_BASE=("A","D")
T0_OPTIONAL=("B","G","H","I1","I2")
T1_CONFIRM_POOL=("A","B","C","D","G","H","I1","I2")

def load(p):
    return json.loads(Path(p).read_text())

def stats(rows,mask):
    ev=[r for r,m in zip(rows,mask) if m]
    hi=[r for r in ev if r["severity"]=="HIGH"]
    med=[r for r in ev if r["severity"]=="MEDIUM"]
    norm=[r for r in ev if r["severity"]=="NORMAL"]
    high_all=[r for r in rows if r["severity"]=="HIGH"]
    return {
        "events":len(ev),
        "high_hits":len(hi),
        "medium_hits":len(med),
        "false_calls":len(norm),
        "high_recall":0.0 if not high_all else len(hi)/len(high_all),
        "false_call_rate":None if not ev else len(norm)/len(ev),
        "useful_call_rate":None if not ev else (len(hi)+len(med))/len(ev),
        "event_targets":[r["target"] for r in ev],
        "high_hit_targets":[r["target"] for r in hi],
        "medium_hit_targets":[r["target"] for r in med],
        "false_call_targets":[r["target"] for r in norm],
        "false_call_detail":[{"target":r["target"],"ape_pct":r["ape_pct"],"active_signals":r["active_signals"]} for r in norm],
        "missed_high_targets":[r["target"] for r in high_all if r not in hi],
    }

def mask_or(rows,signals):
    return [any(bool(r[s]) for s in signals) for r in rows]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    src=load(a.matrix_v2)
    if src.get("schema")!="GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_2026-09-30":
        raise RuntimeError(("BAD_SCHEMA",src.get("schema")))

    dev=[r for r in src["rows"] if DEV_START<=r["target"]<=DEV_END]
    if len(dev)!=33:
        raise RuntimeError(("DEV_ROW_COUNT",len(dev)))

    # T0 RED search.
    candidates=[]
    for k in range(len(T0_OPTIONAL)+1):
        for opt in itertools.combinations(T0_OPTIONAL,k):
            sigs=T0_BASE+opt
            m=mask_or(dev,sigs)
            st=stats(dev,m)
            if st["high_recall"] < 0.75:
                continue
            candidates.append({
                "signals":list(sigs),
                "optional":list(opt),
                "stats":st,
            })
    if not candidates:
        raise RuntimeError("NO_T0_CANDIDATE")

    def t0_key(c):
        st=c["stats"]
        return (
            st["false_calls"],
            -st["high_recall"],
            1.0 if st["false_call_rate"] is None else st["false_call_rate"],
            -st["medium_hits"],
            len(c["optional"]),
            tuple(c["optional"]),
        )
    candidates.sort(key=t0_key)
    t0_sel=candidates[0]

    # Raw T1 high-hit count in DEV.
    raw_t1_mask=[bool(r["T1_WGC"]) for r in dev]
    raw_t1_stats=stats(dev,raw_t1_mask)
    raw_t1_high=raw_t1_stats["high_hits"]

    # T1 confirmation gate search.
    t1_candidates=[]
    for k in range(1,len(T1_CONFIRM_POOL)+1):
        for sub in itertools.combinations(T1_CONFIRM_POOL,k):
            m=[
                bool(r["T1_WGC"]) and any(bool(r[s]) for s in sub)
                for r in dev
            ]
            st=stats(dev,m)
            if st["high_hits"] != raw_t1_high:
                continue
            t1_candidates.append({"signals":list(sub),"stats":st})
    if not t1_candidates:
        raise RuntimeError("NO_T1_CANDIDATE")

    def t1_key(c):
        st=c["stats"]
        return (
            st["false_calls"],
            -st["medium_hits"],
            len(c["signals"]),
            tuple(c["signals"]),
        )
    t1_candidates.sort(key=t1_key)
    t1_sel=t1_candidates[0]

    t0_mask=mask_or(dev,t0_sel["signals"])
    t1_mask=[
        bool(r["T1_WGC"]) and any(bool(r[s]) for s in t1_sel["signals"])
        for r in dev
    ]
    final_mask=[a or b for a,b in zip(t0_mask,t1_mask)]
    final_stats=stats(dev,final_mask)

    # AMBER/shadow are fixed governance channels, not tuned.
    amber_mask=mask_or(dev,("B","C","H"))
    shadow_mask=mask_or(dev,("E","G"))

    raw_t0_standard=[bool(r["T0_STANDARD"]) for r in dev]
    raw_any=[bool(r["ANY_VISIBLE"]) for r in dev]

    config={
        "T0_RED_signals":t0_sel["signals"],
        "T1_confirm_signals":t1_sel["signals"],
        "T1_rule":"T1_WGC AND OR(T1_confirm_signals)",
        "FINAL_RED_rule":"T0_RED OR T1_RED_CONFIRM",
        "AMBER_T0_signals":["B","C","H"],
        "SHADOW_T0_signals":["E","G"],
    }

    out={
        "schema":"GOLD_MONTHLY_ALARM_FINE_TUNING_V1_2026-09-30",
        "status":"FROZEN_DEV_ONLY",
        "selection_scope":{"start":DEV_START,"end":DEV_END,"rows":len(dev),"test_2025_2026_opened":False},
        "config":config,
        "selected":{
            "T0_RED":t0_sel,
            "T1_RED_CONFIRM":t1_sel,
            "FINAL_RED":final_stats,
            "AMBER_T0":stats(dev,amber_mask),
            "SHADOW_T0":stats(dev,shadow_mask),
        },
        "comparators":{
            "RAW_T1_WGC":raw_t1_stats,
            "RAW_T0_STANDARD":stats(dev,raw_t0_standard),
            "RAW_ANY_VISIBLE":stats(dev,raw_any),
        },
        "search_summary":{
            "t0_candidate_count":len(candidates),
            "t1_candidate_count":len(t1_candidates),
            "t0_top10":candidates[:10],
            "t1_top10":t1_candidates[:10],
        },
        "governance":{
            "underlying_signal_definitions_changed":False,
            "2025_2026_used_for_selection":False,
            "E_excluded_from_tuning_due_zero_DEV_activation":True,
            "C_excluded_from_HIGH_search_due_medium_role":True,
            "A_D_protected_in_T0_RED":True,
            "forecast_modified":False,
            "routing_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "config":config,
        "T0_RED":t0_sel["stats"],
        "T1_RED_CONFIRM":t1_sel["stats"],
        "FINAL_RED":final_stats,
        "RAW_T0_STANDARD":out["comparators"]["RAW_T0_STANDARD"],
        "RAW_ANY_VISIBLE":out["comparators"]["RAW_ANY_VISIBLE"],
    },sort_keys=True))

if __name__=="__main__":
    main()
