#!/usr/bin/env python3
"""V31 separate release-audited JOLTS/ADP prior context; no RED override.

2026 June observations are AFTER their historical public evidence timestamp
and BEFORE June 5 NFP; consensus historical provider update time is unproven.
Do not predict NFP value or direction from these two releases.
"""
import csv
import json
from datetime import timedelta
from pathlib import Path
from risk_v31_macro_event_layer import utc, check, OUT

SRC=OUT/"v31_june_before_NFP_JOLTS_ADP_evidence.csv"
NFP="2026-06-05T12:30:00Z"
SCHEMA="V31_PRIOR_CONTEXT_ONLY_NOT_MODEL_SIGNAL"

def available_prior_context(as_of):
    with SRC.open(newline="") as f:records=list(csv.DictReader(f))
    check(len(records)==2 and {x["event_code"].split("_")[0] for x in records}=={"JOLTS","ADP"},
         "PRECURSOR_EVENT_COUNT")
    out=[]
    for x in records:
        recorded=utc(x["earliest_public_evidence_utc"])
        check(recorded < utc(NFP),"SOURCES_NOT_PRECEDING_NFP")
        if recorded > as_of:continue
        check(x["was_known_before_2026_06_05_NFP"]=="true","INVALID_PRE_NFP_CONTEXT")
        check(x["exact_consensus_pre_release_timestamp_proven"]=="false",
              "CONSENSUS_PIT_FALSE_CERTIFICATION")
        diff=float(x["actual"])-float(x["consensus"])
        check(diff>0 and x["sign"]=="POSITIVE","INPUT_SURPRISE_DISAGREEMENT")
        out.append({"event_code":x["event_code"],"earliest_public_evidence_utc":x["earliest_public_evidence_utc"],
                    "actual_minus_reported_consensus":diff,"units":x["units"],
                    "pre_NFP_context":"LABOR_RESILIENCE_INDICATOR_MIXED",
                    "macro_adverse_gold_direction_known":False,"historical_consensus_PIT_certified":False,
                    "source":x["primary_official_source"],"consensus_source":x["contemporaneous_consensus_source"],
                    "counter_indicator":x["other_important_counter_indicator"],"automatic_risk_override":False})
    return out

def main():
    check(len(available_prior_context(utc("2026-06-02T14:15:00Z")))==0,"TOO_EARLY_FOR_JOLTS_ARTICLE")
    check(len(available_prior_context(utc("2026-06-03T12:00:00Z")))==1,"ADP_LOOKAHEAD")
    before=available_prior_context(utc("2026-06-04T13:45:00Z"))
    check(len(before)==2,"JUNE4_PRIOR_CONTEXT_MISSING")
    proof={"schema":SCHEMA,"as_of_utc":"2026-06-04T13:45:00Z",
       "as_of_TR":"2026-06-04T16:45:00+03:00",
       "known_released_before_NFP":before,
       "event_warning_status":"EVENT_PENDING_RESEARCH_WITH_UNVERIFIED_HISTORIC_CALENDAR_SNAPSHOT",
       "is_NFP_direction_forecast":False,
       "is_actionable_sell":False,
       "model_BASE14_CFTC21_V22_changed":False,
       "requires_PIT_provider_consensus_before_live":True}
    (OUT/"v31_june2026_known_prior_release_context.json").write_text(
         json.dumps(proof,indent=2,ensure_ascii=False)+"\n")
    print("V31_PRIOR_CONTEXT",json.dumps(proof,ensure_ascii=False))
    return proof

if __name__=="__main__":
    main()
