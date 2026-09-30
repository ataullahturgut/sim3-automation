from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from scipy.stats import fisher_exact

SIGNALS = ["A","B","C","D","E","G","H","I1","I2","T1_WGC"]

ERAS = {
    "PRE_R2_ERA": (None, "2024-03"),
    "R2_EARLY": ("2024-04", "2024-12"),
    "R2_LATE": ("2025-01", "2026-04"),
    "R2_BREAK": ("2026-05", "2026-07"),
}

PRIMARY_ERAS = ["PRE_R2_ERA", "R2_EARLY", "R2_LATE"]
PAIRWISE = [
    ("PRE_R2_ERA","R2_EARLY"),
    ("PRE_R2_ERA","R2_LATE"),
    ("R2_EARLY","R2_LATE"),
]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def in_range(month: str, start: str | None, end: str | None):
    if start is not None and month < start:
        return False
    if end is not None and month > end:
        return False
    return True


def era_of(origin: str):
    for name,(a,b) in ERAS.items():
        if in_range(origin,a,b):
            return name
    return None


def safe_rate(n,d):
    return None if d == 0 else float(n/d)


def severity_summary(rows):
    c=Counter(r["severity"] for r in rows)
    n=len(rows)
    h=int(c.get("HIGH",0)); m=int(c.get("MEDIUM",0)); normal=int(c.get("NORMAL",0))
    return {
        "n":n,
        "high":h,
        "medium":m,
        "elevated":h+m,
        "normal":normal,
        "high_rate":safe_rate(h,n),
        "medium_rate":safe_rate(m,n),
        "elevated_rate":safe_rate(h+m,n),
        "normal_rate":safe_rate(normal,n),
    }


def union_metrics(rows, field):
    ev=[r for r in rows if bool(r[field])]
    h=sum(r["severity"]=="HIGH" for r in ev)
    m=sum(r["severity"]=="MEDIUM" for r in ev)
    f=sum(r["severity"]=="NORMAL" for r in ev)
    all_h=sum(r["severity"]=="HIGH" for r in rows)
    all_e=sum(r["severity"] in ("HIGH","MEDIUM") for r in rows)
    return {
        "events":len(ev),
        "high_hits":int(h),
        "medium_hits":int(m),
        "false_calls":int(f),
        "high_recall":safe_rate(h,all_h),
        "elevated_recall":safe_rate(h+m,all_e),
        "false_call_rate":safe_rate(f,len(ev)),
        "useful_call_rate":safe_rate(h+m,len(ev)),
    }


def signal_metrics(rows, signal):
    ev=[r for r in rows if bool(r[signal])]
    useful=sum(r[f"{signal}_outcome"] in ("HIGH_HIT","MEDIUM_HIT") for r in ev)
    false=sum(r[f"{signal}_outcome"]=="FALSE_CALL" for r in ev)
    return {
        "events":len(ev),
        "useful":int(useful),
        "false":int(false),
        "useful_call_rate":safe_rate(useful,len(ev)),
        "false_call_rate":safe_rate(false,len(ev)),
        "evidence_label":"NO_EVENTS" if not ev else ("SMALL_N" if len(ev)<3 else "REPORTABLE"),
    }


def v2_status_metrics(rows):
    out={}
    for z in ["STABLE","TRANSITION"]:
        rr=[r for r in rows if r["v2_transition_status"]==z]
        out[z]=severity_summary(rr)
    s=out["STABLE"]; t=out["TRANSITION"]
    out["transition_minus_stable"]={
        "high_rate_diff":None if s["high_rate"] is None or t["high_rate"] is None else float(t["high_rate"]-s["high_rate"]),
        "elevated_rate_diff":None if s["elevated_rate"] is None or t["elevated_rate"] is None else float(t["elevated_rate"]-s["elevated_rate"]),
    }
    return out


def v2_no_alarm(rows, alarm_field):
    rr=[r for r in rows if r["v2_transition_flag"] and not bool(r[alarm_field])]
    q=severity_summary(rr)
    q["origins"]=[r["origin"] for r in rr]
    q["targets"]=[r["target"] for r in rr]
    return q


def era_report(rows):
    return {
        "severity":severity_summary(rows),
        "ANY_VISIBLE":union_metrics(rows,"ANY_VISIBLE"),
        "T0_STANDARD":union_metrics(rows,"T0_STANDARD"),
        "v2_status":v2_status_metrics(rows),
        "v2_transition_no_ANY_VISIBLE":v2_no_alarm(rows,"ANY_VISIBLE"),
        "v2_transition_no_T0_STANDARD":v2_no_alarm(rows,"T0_STANDARD"),
        "signals":{s:signal_metrics(rows,s) for s in SIGNALS},
        "origins":[r["origin"] for r in rows],
    }


def fisher_high(a_rows,b_rows):
    ah=sum(r["severity"]=="HIGH" for r in a_rows)
    an=len(a_rows)-ah
    bh=sum(r["severity"]=="HIGH" for r in b_rows)
    bn=len(b_rows)-bh
    if len(a_rows)==0 or len(b_rows)==0:
        return None
    odds,p=fisher_exact([[ah,an],[bh,bn]],alternative="two-sided")
    return {
        "table":[[int(ah),int(an)],[int(bh),int(bn)]],
        "odds_ratio":None if odds != odds else float(odds),
        "p_value":float(p),
    }


def fisher_union_useful(a_rows,b_rows,field):
    def counts(rows):
        ev=[r for r in rows if bool(r[field])]
        u=sum(r["severity"] in ("HIGH","MEDIUM") for r in ev)
        f=sum(r["severity"]=="NORMAL" for r in ev)
        return int(u),int(f),len(ev)
    au,af,an=counts(a_rows); bu,bf,bn=counts(b_rows)
    if an==0 or bn==0:
        return None
    odds,p=fisher_exact([[au,af],[bu,bf]],alternative="two-sided")
    return {
        "table":[[au,af],[bu,bf]],
        "odds_ratio":None if odds != odds else float(odds),
        "p_value":float(p),
    }


def pairwise_tests(groups):
    out={}
    for a,b in PAIRWISE:
        out[f"{a}_VS_{b}"]={
            "high_vs_nonhigh":fisher_high(groups[a],groups[b]),
            "ANY_VISIBLE_useful_vs_false":fisher_union_useful(groups[a],groups[b],"ANY_VISIBLE"),
            "T0_STANDARD_useful_vs_false":fisher_union_useful(groups[a],groups[b],"T0_STANDARD"),
        }
    return out


def compact_pattern(era_reports):
    out={}
    for e in PRIMARY_ERAS:
        r=era_reports[e]
        out[e]={
            "high_rate":r["severity"]["high_rate"],
            "elevated_rate":r["severity"]["elevated_rate"],
            "any_useful_rate":r["ANY_VISIBLE"]["useful_call_rate"],
            "any_false_rate":r["ANY_VISIBLE"]["false_call_rate"],
            "t0_useful_rate":r["T0_STANDARD"]["useful_call_rate"],
            "t0_false_rate":r["T0_STANDARD"]["false_call_rate"],
            "v2_transition_high_rate":r["v2_status"]["TRANSITION"]["high_rate"],
            "v2_transition_elevated_rate":r["v2_status"]["TRANSITION"]["elevated_rate"],
            "v2_transition_minus_stable_high_diff":r["v2_status"]["transition_minus_stable"]["high_rate_diff"],
            "v2_transition_minus_stable_elevated_diff":r["v2_status"]["transition_minus_stable"]["elevated_rate_diff"],
            "v2_no_any_high":r["v2_transition_no_ANY_VISIBLE"]["high"],
            "v2_no_any_n":r["v2_transition_no_ANY_VISIBLE"]["n"],
        }
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audit-json",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    src=load_json(args.audit_json)
    if src.get("status")!="COMPLETE":
        raise RuntimeError("INVALID_SOURCE")
    if src.get("primary_schedule")!="EXPANDING_REFIT":
        raise RuntimeError("INVALID_SCHEDULE")
    if src.get("join_contract",{}).get("target_month_v2_state_used") is not False:
        raise RuntimeError("BAD_JOIN")

    rows=sorted(src["rows"],key=lambda r:r["origin"])
    if len(rows)!=58:
        raise RuntimeError(("ROW_COUNT",len(rows)))

    for r in rows:
        r["market_era"]=era_of(r["origin"])

    groups={e:[r for r in rows if r["market_era"]==e] for e in ERAS}
    if any(len(groups[e])==0 for e in PRIMARY_ERAS):
        raise RuntimeError({e:len(groups[e]) for e in groups})

    reports={e:era_report(groups[e]) for e in ERAS}

    # Same-regime control uses best semantic state R2, independent of confidence label.
    r2_groups={e:[r for r in groups[e] if r["v2_semantic_state"]=="R2"] for e in ERAS}
    r2_reports={e:era_report(r2_groups[e]) for e in ERAS}

    result={
        "schema":"GOLD_MONTHLY_MARKET_ERA_CONCEPT_DRIFT_AUDIT_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "era_definition":{
            "basis":"frozen market-regime chronology, origin month",
            "PRE_R2_ERA":"origin <= 2024-03",
            "R2_EARLY":"2024-04..2024-12",
            "R2_LATE":"2025-01..2026-04",
            "R2_BREAK":"2026-05..2026-07",
            "boundary_searched_posthoc":False,
        },
        "all_rows_by_era":reports,
        "live_R2_only_by_era":r2_reports,
        "pairwise_diagnostics_all_rows":pairwise_tests(groups),
        "pairwise_diagnostics_live_R2_only":pairwise_tests(r2_groups),
        "primary_pattern_all_rows":compact_pattern(reports),
        "primary_pattern_live_R2_only":compact_pattern(r2_reports),
        "governance":{
            "era_boundary_moved":False,
            "change_date_search_performed":False,
            "v2_retuned":False,
            "alarm_definitions_changed":False,
            "severity_thresholds_changed":False,
            "weights_fit":False,
            "alarm_suppression_tested":False,
            "forecast_modified":False,
            "routing_tested":False,
        },
    }

    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "counts":{e:len(groups[e]) for e in groups},
        "r2_counts":{e:len(r2_groups[e]) for e in r2_groups},
        "primary_pattern_all_rows":result["primary_pattern_all_rows"],
        "primary_pattern_live_R2_only":result["primary_pattern_live_R2_only"],
        "pairwise_all":result["pairwise_diagnostics_all_rows"],
        "pairwise_r2":result["pairwise_diagnostics_live_R2_only"],
        "signals":{
            e:{s:reports[e]["signals"][s] for s in ["E","H","B","T1_WGC"]}
            for e in ERAS
        },
        "signals_r2":{
            e:{s:r2_reports[e]["signals"][s] for s in ["E","H","B","T1_WGC"]}
            for e in ERAS
        },
        "break":reports["R2_BREAK"],
    },sort_keys=True))


if __name__=="__main__":
    main()
