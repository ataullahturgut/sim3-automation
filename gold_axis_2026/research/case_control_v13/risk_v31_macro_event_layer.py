#!/usr/bin/env python3
"""V31 macro event overlay: independent, fail-closed, no changes to BASE14/CFTC21/V22.
Historical event records and 5min prices: reconstructed, NOT verified first-print PIT.
A live alert is blocked without independently timestamped inputs and calendar captures.
"""
from __future__ import annotations
import csv, json, math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

OUT=Path(__file__).resolve().parent/"outputs"
CSV=OUT/"v31_macro_event_research_2023_2026_108_events.csv"
FAMILIES=("NFP","CPI","FOMC")
TRAIN_YEARS=("2023","2024")
QUANTILE=0.10
DELAY_MINUTES=35
ISTANBUL=ZoneInfo("Europe/Istanbul")
BATCH="2026-09-08T02:18:22.168Z"

def check(test,reason):
    if not test:raise RuntimeError("V31_FAIL_CLOSED_"+reason)

def utc(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def num(x):
    return None if x=="" else float(x)

def interp_percentile(v,p):
    v=sorted(v)
    check(len(v)>=7 and 0<p<1,"NO_TRAINING_QUANTILES")
    x=(len(v)-1)*p
    low=math.floor(x)
    return v[low]*(1-x+low)+v[min(low+1,len(v)-1)]*(x-low)

def events():
    with CSV.open(newline="") as f:d=list(csv.DictReader(f))
    check(len(d)==108 and len({r["event_id"] for r in d})==108,"108_UNIQUE_EVENT_ROWS")
    check(Counter(r["family"] for r in d)=={"NFP":44,"CPI":43,"FOMC":21},"SOURCE_COUNTS")
    check(all(r["source_macro_consensus_before_release_proven"]=="false" and
              r["official_calendar_snapshot_before_release_proven"]=="false" and
              r["source_data_price_first_print_PIT_proven"]=="false" for r in d),"RECONSTRUCTION_EVIDENCE_FLAGS")
    check(all(r["gold_5m_cache_retrieved_utc"]==BATCH and r["gold_bar_cache_provider"]=="Twelve Data"
              for r in d),"INTRADAY_SOURCE_LINEAGE")
    check(all(utc(r["release_utc"]).tzinfo is not None for r in d),"UTC_RELEASE_TIMES")
    return d

def calibrated_2023_2024(d):
    t={}
    for family in FAMILIES:
        x=[num(r["gold_return_30m_pct"]) for r in d if r["family"]==family and
           r["event_year"] in TRAIN_YEARS and r["gold_return_30m_pct"]]
        t[family]={"q10_30m_pct":interp_percentile(x,QUANTILE),
                   "train_n":len(x),"train_years":"2023-2024","no_2025_2026_selection":True}
        check(t[family]["q10_30m_pct"]<0,"NONNEGATIVE_DOWNSIDE_THRESHOLD")
    return t

def bank_window(t):
    z=t.astimezone(ISTANBUL)
    return "BANK_WINDOW" if 8<=z.hour<17 else "OUTSIDE_BANK_WINDOW"

def assess(row,asof,cutoff,proof=None,*,historical=True):
    """Clock-safe event state machine. A reported past release is NOT a prepublished calendar.
    After release market response is not known until 30min + conservative 5min bar-close lag.
    Proof for live evaluation must be caller-supplied genuine captured-at data, not a
    retrospectively assigned timestamp.
    """
    proof=proof or {}
    release=utc(row["release_utc"])
    asof=asof.astimezone(timezone.utc)
    first_complete=release+timedelta(minutes=DELAY_MINUTES)
    c=utc(proof["calendar_captured_at"]) if proof.get("calendar_captured_at") else None
    a=utc(proof["actual_captured_at"]) if proof.get("actual_captured_at") else None
    s=utc(proof["consensus_captured_at"]) if proof.get("consensus_captured_at") else None
    b=utc(proof["bars_captured_at"]) if proof.get("bars_captured_at") else None
    calendar_ok=bool(c and c<release and c<=asof and proof.get("official_schedule_captured") is True
         and proof.get("calendar_url","").startswith(("https://www.bls.gov/","https://www.federalreserve.gov/")))
    macro_ok=bool(a and release<=a<=asof and (row["family"]=="FOMC" or
         (s and s<release)) and proof.get("original_firstprint_verified") is True)
    bars_ok=bool(b and b>=first_complete and b<=asof and proof.get("bars_firstprint_verified") is True)
    if asof<release:
        state="EVENT_PENDING" if calendar_ok else "PENDING_UNVERIFIED_CALENDAR"
        ret=None;surprise="NOT_AVAILABLE_PRE_RELEASE"
    elif asof<first_complete:
        state="AWAIT_REACTION_30M_BAR"
        ret=None;surprise="RELEASE_CONTEXT_AFTER_PUBLICATION_ONLY"
    else:
        ret=num(row["gold_return_30m_pct"])
        surprise=(row["nfp_actual_minus_consensus_sign"] if row["family"]=="NFP" else
                 row["cpi_actual_minus_consensus_sign"] if row["family"]=="CPI" else
                 "FOMC_CONTEXT_NOT_DIRECTION")
        if ret is None or not math.isfinite(ret) or row["reaction_bars_complete"]!="true":
            state="ABSTAIN_MISSING_5MIN_BARS"
        elif ret<=cutoff:
            state="EVENT_REPRICING_RESEARCH_REVIEW"
        else:
            state="NO_RARE_ADVERSE_REACTION"
    live_eligible=bool(not historical and calendar_ok and macro_ok and bars_ok and
         state=="EVENT_REPRICING_RESEARCH_REVIEW" and bank_window(first_complete)=="BANK_WINDOW")
    return {"event_id":row["event_id"],"family":row["family"],"release_utc":row["release_utc"],
      "asof_utc":asof.isoformat(),"earliest_30m_complete_TR":first_complete.astimezone(ISTANBUL).isoformat(),
      "bank_window":bank_window(first_complete),"state":state,"gold_return_30m_pct":ret,
      "published_event_surprise_sign":surprise,"frozen_q10_2023_2024_pct":cutoff,
      "pre_release_calendar_PIT":calendar_ok,"release_actual_and_consensus_PIT":macro_ok,
      "gold_bar_firstprint_PIT":bars_ok,"live_eligible":live_eligible,
      "DXY_2Y_OIL_intraday_confirmation":"NOT_FOUND",
      "legacy_BASE14_CFTC21_V22_modified":False,"action":"INFORMATIONAL_NOT_AL_SAT"}

def export(rows,name):
    with (OUT/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def run():
    data=events()
    thresholds=calibrated_2023_2024(data)
    logs=[]
    for r in data:
        release=utc(r["release_utc"]);limit=thresholds[r["family"]]["q10_30m_pct"]
        pre=assess(r,release-timedelta(hours=12),limit)
        at=assess(r,release,limit)
        post=assess(r,release+timedelta(minutes=DELAY_MINUTES),limit)
        check(pre["gold_return_30m_pct"] is None and
              pre["published_event_surprise_sign"]=="NOT_AVAILABLE_PRE_RELEASE","PRE_RELEASE_LOOKAHEAD")
        check(at["gold_return_30m_pct"] is None and not post["live_eligible"],
              "AT_RELEASE_OR_HISTORIC_LIVE_LEAK")
        logs.append({**post,"year":r["event_year"],
                     "pre_release_state":pre["state"],"instant_release_state":at["state"]})
    june=[x for x in logs if x["event_id"].startswith(("NFP_2026-06-05",
             "CPI_2026-06-10","FOMC_2026-06-17"))]
    check(len(june)==3,"JUNE3_EVENTS")
    nfp=next(x for x in june if x["family"]=="NFP")
    check(abs(nfp["gold_return_30m_pct"]+1.207191906)<.00001,"JUNE_PRICE_REACTION_PARITY")
    overview=[]
    for year in ("2023","2024","2025","2026"):
        for fam in FAMILIES:
            group=[x for x in logs if x["year"]==year and x["family"]==fam]
            if not group:continue
            cnt=Counter(x["state"] for x in group)
            overview.append({"year":year,"family":fam,"events":len(group),
                "extreme_adverse_research":cnt["EVENT_REPRICING_RESEARCH_REVIEW"],
                "normal_market_reaction":cnt["NO_RARE_ADVERSE_REACTION"],
                "missing_bars":cnt["ABSTAIN_MISSING_5MIN_BARS"],
                "historical_firstprint_PIT_certified":False})
    export(logs,"v31_historical_macro_overlay_all_108_events.csv")
    export(june,"v31_june2026_macro_event_replay.csv")
    export(overview,"v31_by_year_macro_event_comparison.csv")
    result={"engine":"V31_MACRO_EVENT_CONTEXT_V1",
       "thresholds":thresholds,"events":len(logs),"train":"2023-2024",
       "validation":"2025 (ex post)","stress":"2026 (known events, not blind)",
       "original_model_unchanged":True,"old_parameters_unchanged":True,
       "neon_writes":False,"live_promotion_allowed":False,
       "original_PIT_consensus_and_calendar_verified":False,
       "intraday_prices_retrieved_after_historical_events":True,
       "all_historical_live_eligible":False,
       "required_live_sources":["official pre-release calendar snapshot",
          "pre-release consensus timestamp","actual original firstprint timestamp",
          "real-time 5min bar as-of and bar close convention","optional DXY/UST2Y/oil for macro cause"],
       "june":june}
    (OUT/"v31_macro_event_layer_manifest.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("V31_THRESHOLDS",json.dumps(thresholds))
    print("V31_JUNE",json.dumps(june,ensure_ascii=False))
    print("V31_YEAR_RESULTS",json.dumps(overview))
    print("V31_SUCCESS",len(logs))
    return result

if __name__=="__main__":run()
