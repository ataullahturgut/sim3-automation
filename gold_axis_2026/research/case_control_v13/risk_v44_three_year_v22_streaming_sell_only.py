#!/usr/bin/env python3
"""V44: three-year REAL V22 research diary + strictly sequential exit signals.

IMPORTANT:
  * 2024-2025 V22 = v22_daily_decisions.csv effective_review recorded original
    research output; not synthetic V41/V42 proxy.
  * 2026 V22 = v33_2026...DAILY model_v22_review (later replay/version).
    Versions are separately identified. Never assert 3yr same firstprint.
  * Watch starts on FIRST MARKET BAR AFTER completed V22 decision day.
  * One sell-only EXIT signal per risk-watch episode; NEVER BUY/RE-ENTRY.
  * Conditions use only current/completed bars and past 96-bar support.
  * Next 15m price is only a research fill proxy, NOT trade execution.
  * Evaluation uses the next FIVE DISTINCT later trading dates, NOT 5 rows.
  * No future price is consulted during trigger; source PIT uncertified.
"""
from __future__ import annotations
import os,csv,json,hashlib,argparse,math
from datetime import date,timedelta
from pathlib import Path
from collections import defaultdict
from statistics import mean,median
from zoneinfo import ZoneInfo
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import get_bars,enhance,V33

ROOT=Path(__file__).parent
HIST=ROOT/"outputs"/"v22_daily_decisions.csv"
CONFIG={
 "V22_IMMEDIATE":{"draw":0,"r4":0,"low":False,"type":"immediate"},
 "V43_STRUCTURAL_1":{"draw":.01,"r4":-.01,"low":True,"type":"structure"},
 "TRAIL2_4H_NEG1":{"draw":.02,"r4":-.01,"low":False,"type":"trailing"},
 "TRAIL3_4H_NEG1":{"draw":.03,"r4":-.01,"low":False,"type":"trailing"},
 "STRUCTURAL_1_4H_NEG1P5":{"draw":.01,"r4":-.015,"low":True,"type":"structure"},
}
COVERAGE={2024:23000,2025:23000,2026:16000}
MAX_WARN_AGE_CALENDAR_DAYS=12
PRICE_FREQUENCY_MIN=15
TARGET_FUTURE_MARKET_DAYS=5

def read_diaries():
    diaries={2024:{},2025:{},2026:{}}
    provenance={2024:"V22_original_V19_V18_2024_replay_effective_review_NOT_PIT",
                2025:"V22_original_V19_V18_2025_replay_effective_review_NOT_PIT",
                2026:"V33_later_full2026_replay_model_v22_review_NOT_PIT"}
    with HIST.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            year=int(r["year"])
            if year in (2024,2025):
                d=date.fromisoformat(r["origin"])
                if d in diaries[year]:raise ValueError("V22_DUPLICATE_ORIGIN")
                diaries[year][d]=r["effective_review"]=="True"
    with V33.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            if r["scenario"]!="AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":continue
            d=date.fromisoformat(r["date"])
            if d.year!=2026:continue
            if d in diaries[2026]:raise ValueError("V33_DUPLICATE_ORIGIN")
            diaries[2026][d]=r["model_v22_review"]=="True"
    return diaries,provenance

def condition(name,bar,peak):
    c=CONFIG[name]
    if c["type"]=="immediate":return True
    if bar["r4"] is None or not bar["usable4h"]:return False
    # All inputs at t or before t; prev96 low excludes current bar.
    draw=(bar["p"]/peak-1)
    if draw>-c["draw"] or bar["r4"]>c["r4"]:return False
    if c["low"] and not (bar["p"]<bar["prior24low"]):return False
    return True

def fingerprint(episode,bar,method):
    payload={
      "type":"V44_RESEARCH_SIGNAL","method":method,
      "watchStart":episode["firstRiskDate"],"startUTC":episode["startUTC"],
      "barUTC":bar["ts"].isoformat(),"price":bar["p"],
      "peak":episode["peak"],"prior96Low":bar["prior24low"],
      "fourHourReturn":bar["r4"],"source":"HISTDATA_M15_NONPIT"
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class Stream:
    def __init__(self,rule,year,diary):
        self.rule=rule
        self.year=year
        self.diary=diary
        self.state="IDLE"
        self.last_warn=None
        self.episodes=[]
        self.episode=None
        self.pending=None
        self.prev_day=None
        self.transitions=[]
    def transition(self,kind,ts,**detail):
        self.transitions.append({"type":kind,"time":str(ts),**detail})
    def start(self,bar,riskdate):
        assert self.state=="IDLE"
        self.episode={"firstRiskDate":str(riskdate),
                      "lastRiskDate":str(riskdate),
                      "startUTC":str(bar["ts"]),"peak":float(bar["p"]),
                      "riskUpdates":1,"signal":None,
                      "endUTC":None,"lastWatchBarUTC":str(bar["ts"])}
        self.episodes.append(self.episode)
        self.state="WATCH"
        self.transition("WATCH_START",bar["ts"],risk_date=str(riskdate))
    def push(self,bar):
        if bar["ts"].year!=self.year:raise ValueError("WRONG_YEAR")
        day=bar["date"]
        # First emit price/fill for previous signal. Current bar may follow
        # a large overnight/market closure, so gaps are explicitly recorded.
        if self.pending is not None:
            event=self.pending
            mins=int((bar["ts"]-event["signalTimestamp"]).total_seconds()/60)
            if mins<PRICE_FREQUENCY_MIN:raise ValueError("NONMONOTONIC_BAR")
            event["fillUTC"]=str(bar["ts"])
            event["fillPx"]=float(bar["p"])
            event["fillGapMinutes"]=mins
            event["fillCandidateValid"]=mins==PRICE_FREQUENCY_MIN
            del event["signalTimestamp"]
            self.pending=None
            self.transition("EXIT_FILL_PROXY",bar["ts"],
                            valid_next_15m=mins==15)
        if self.prev_day is not None and self.prev_day!=day:
            if self.diary.get(self.prev_day,False):
                self.last_warn=self.prev_day
                if self.state=="IDLE":
                    self.start(bar,self.prev_day)
                else:
                    self.episode["riskUpdates"]+=1
                    self.episode["lastRiskDate"]=str(self.prev_day)
                    self.transition("V22_RISK_REFRESH",bar["ts"],risk_date=str(self.prev_day))
        self.prev_day=day
        if self.state in ("WATCH","EXIT_RECORDED"):
            assert self.last_warn is not None
            if (day-self.last_warn).days>MAX_WARN_AGE_CALENDAR_DAYS:
                self.episode["endUTC"]=str(bar["ts"])
                self.episode["termination"]="RISK_EXPIRED"
                self.transition("RISK_EXPIRED",bar["ts"])
                self.episode=None
                self.state="IDLE"
        if self.state not in ("WATCH","EXIT_RECORDED"):return
        self.episode["peak"]=max(float(bar["p"]),self.episode["peak"])
        self.episode["lastWatchBarUTC"]=str(bar["ts"])
        if self.state=="EXIT_RECORDED":return
        if condition(self.rule,bar,self.episode["peak"]):
            sig={
                "signalUTC":str(bar["ts"]),
                "signalPx":float(bar["p"]),
                "sourceBarUTC":str(bar["ts"]),
                "warningDate":self.episode["firstRiskDate"],
                "peakSoFar":self.episode["peak"],
                "drawdownPct":100*(bar["p"]/self.episode["peak"]-1),
                "fourHourPct":None if bar["r4"] is None else 100*bar["r4"],
                "prev96BarLow":float(bar["prior24low"]),
                "sha256":fingerprint(self.episode,bar,self.rule),
                "signalTimestamp":bar["ts"],"fillUTC":None,"fillPx":None,
                "fillCandidateValid":False,"fillGapMinutes":None
            }
            self.episode["signal"]=sig
            self.pending=sig
            self.state="EXIT_RECORDED"
            self.transition("EXIT_SIGNAL",bar["ts"],sha256=sig["sha256"])
    def end(self,last_bar):
        if self.episode is not None:
            self.episode["endUTC"]=str(last_bar["ts"])
            self.episode["termination"]="YEAR_END_CENSORED"
        if self.pending:
            self.pending["fillCandidateValid"]=False
            self.pending.pop("signalTimestamp",None)

NY=ZoneInfo("America/New_York")

def market_session(ts):
    """New York 17:00 daily cut; Sunday session belongs Monday.
    Distinct MARKET sessions, not UTC dates. Future price labels only.
    """
    local=ts.astimezone(NY)
    # FX trading week roll 17:00 ET; Sunday 17:00 => Monday session.
    day=local.date()+(timedelta(days=1) if local.hour>=17 else timedelta(days=0))
    return day

def future_prices(bars,start_idx):
    # Price rows of exactly 5 distinct subsequent NY17 FX market sessions;
    # exclude the whole session containing fill. No hindsight in signals.
    start_session=market_session(bars[start_idx]["ts"])
    seen=[]
    prices=[]
    completed_five=False
    last_future_bar=None
    for row in bars[start_idx+1:]:
        session=market_session(row["ts"])
        if session<=start_session:continue
        if not seen or seen[-1]!=session:
            if len(seen)>=TARGET_FUTURE_MARKET_DAYS:
                completed_five=True
                break
            seen.append(session)
        prices.append(row["p"])
        last_future_bar=row["ts"]
    if len(seen)==TARGET_FUTURE_MARKET_DAYS and last_future_bar is not None:
        local=last_future_bar.astimezone(NY)
        if local.hour==16 and local.minute>=30:
            completed_five=True
    return prices,len(seen)==TARGET_FUTURE_MARKET_DAYS and completed_five

def score(stream,bars):
    idx={str(b["ts"]):i for i,b in enumerate(bars)}
    episodes=[]
    for e in stream.episodes:
        sig=e["signal"]
        out={
            "firstRiskDate":e["firstRiskDate"],
            "lastRiskDate":e["lastRiskDate"],
            "riskUpdates":e["riskUpdates"],
            "watchStartUTC":e["startUTC"],
            "watchEndUTC":e["endUTC"],
            "termination":e.get("termination"),
            "signal":None,
            "outcome5":None,
            "mature5":False,
        }
        lo=idx[e["startUTC"]]
        hi=min(idx[e["endUTC"]],len(bars)-1) if e["endUTC"] in idx else len(bars)-1
        observed=bars[lo:hi+1]
        if observed:
            high=max(x["p"] for x in observed)
            first=observed[0]["p"]
            out["maxRiseSinceWatchPct"]=round(100*(high/first-1),3)
            out["lowSinceWatchPct"]=round(100*(min(x["p"] for x in observed)/first-1),3)
        if sig is not None:
            out["signal"]={k:v for k,v in sig.items() if k!="signalTimestamp"}
            if sig["fillUTC"] is not None and sig["fillCandidateValid"]:
                at=idx[sig["fillUTC"]]
                prices,mature=future_prices(bars,at)
                out["mature5"]=mature
                if mature:
                    draw=100*(min(prices)/sig["fillPx"]-1)
                    out["outcome5"]=round(draw,3)
                    out["confirmed4Pct"]=draw<=-4
                    out["confirmedCost1p6Pct"]=draw<=-1.6
                    out["future5MaxRisePct"]=round(100*(max(prices)/sig["fillPx"]-1),3)
            if observed:
                later=[b["p"] for b in observed if str(b["ts"])>=sig["fillUTC"]] if sig["fillUTC"] is not None else []
                out["foregoneRiseWithinEpisodePct"]=round(100*(max(later)/sig["fillPx"]-1),3) if later else None
                out["peakGivebackPct"]=round(100*(high-sig["fillPx"])/high,3) if sig["fillPx"] is not None else None
        episodes.append(out)
    signaled=[x for x in episodes if x["signal"] is not None]
    fill=[x for x in signaled if x["signal"]["fillCandidateValid"]]
    mature=[x for x in fill if x["mature5"]]
    hits=[x for x in mature if x["confirmed4Pct"]]
    foregone=[x["foregoneRiseWithinEpisodePct"] for x in fill if x.get("foregoneRiseWithinEpisodePct") is not None]
    return {
      "metrics":{
        "riskEpisodes":len(episodes),"signalEpisodes":len(signaled),
        "fillValid":len(fill),"matureNext5":len(mature),
        "matureHitNext5FourPct":len(hits),"matureNoHitNext5FourPct":len(mature)-len(hits),
        "maturePrecisionPct":round(100*len(hits)/len(mature),2) if mature else None,
        "noSignalRiskEpisodes":len(episodes)-len(signaled),
        "meanExtraRiseAfterExitPct":round(mean(foregone),3) if foregone else None,
        "medianExtraRiseAfterExitPct":round(median(foregone),3) if foregone else None,
        "min15mFillInvalid":len(signaled)-len(fill),
        "outcomesPending":len(fill)-len(mature),
      },
      "episodes":episodes,
      "transitions":stream.transitions
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="gold-v44-three-year-causal-stream-exits.json")
    args=parser.parse_args()
    diaries,provenance=read_diaries()
    raw=get_bars()
    results={}
    for year in (2024,2025,2026):
        subset=[r for r in raw if r[0].year==year]
        if len(subset)<COVERAGE[year]:raise RuntimeError("INCOMPLETE_15M_YEAR_"+str(year))
        bars=enhance(subset)
        cohort={}
        for rule in CONFIG:
            engine=Stream(rule,year,diaries[year])
            for bar in bars:engine.push(bar)
            engine.end(bars[-1])
            cohort[rule]=score(engine,bars)
        results[str(year)]={
            "v22Origin":provenance[year],
            "sourceBars":len(bars),
            "riskDays":sum(diaries[year].values()),
            "V22DecisionDays":len(diaries[year]),
            "firstSourceUTC":str(bars[0]["ts"]),
            "lastSourceUTC":str(bars[-1]["ts"]),
            "strategies":cohort
        }
    report={
      "schema":"GOLD_V44_THREE_YEAR_V22_CAUSAL_SELL_ONLY_STREAMING_VALIDATION",
      "status":"HISTORICAL_RESEARCH_NOT_PIT_NOT_BLIND",
      "noBuyOrReentry":True,"noTradingPnL":True,
      "noNeonWrites":True,"liveSignalEnabled":False,
      "2026V22VersionSameAs2024_2025":False,
      "2024_2025HaveRealOriginalV22ResearchDecisionFiles":True,
      "signalModel":"WATCH started after completed V22 day; confirm structural break while watch active",
      "episodeLogic":"one signal per watch, risk refreshed on consecutive historical V22; expires 12 calendar days after last risk",
      "executionProxy":"next 15-minute sample close ONLY when gap exactly 15m",
      "comparisonRules":CONFIG,
      "years":results,
      "provenanceLimitations":[
        "2024-25 original V22 research decisions ≠ 2026 V33 later replay",
        "V22 retrospective inputs not verified as-of-first-publication",
        "2026 already observed many times; sensitivity is not blind holdout",
        "Original 15m source HistData noncanonical, not verified bank bid/ask",
        "Risk episode ends after 12 calendar days, differs V43 offline 8 price sessions",
        "No model threshold optimized on 2024-25 or 2026 here; all frozen",
        "No detection possible for actual dips when V22 had no warning",
        "Risk expiry/realert and weekend gaps need future prospective validation"
      ]
    }
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
    summary={year:{rule:x["metrics"] for rule,x in group["strategies"].items()}
             for year,group in results.items()}
    print("THREE_YEAR_SUMMARY",json.dumps(summary,ensure_ascii=False,default=str),flush=True)
    print("ALL_EPISODES",json.dumps({
        year:{rule:[{
            "risk":x["firstRiskDate"],
            "sig":x["signal"]["signalUTC"] if x["signal"] else None,
            "px":x["signal"]["fillPx"] if x["signal"] else None,
            "decline5":x["outcome5"],
            "peakSinceWatch":x.get("maxRiseSinceWatchPct")
        } for x in g["episodes"]] for rule,g in group["strategies"].items()}
        for year,group in results.items()},
        ensure_ascii=False,default=str),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## V44 2024–26 V22 real retrospective WATCH → SELL signals\n\n")
            f.write("| Year | V22 source | Rule | Watch episodes | Exit signals | Mature | Hits | False |\n")
            f.write("|---|---|---|---:|---:|---:|---:|---:|\n")
            for y,g in results.items():
                for k,v in g["strategies"].items():
                    m=v["metrics"]
                    f.write(f"| {y} | {g['v22Origin']} | {k} | {m['riskEpisodes']} | "
                            f"{m['signalEpisodes']} | {m['matureNext5']} | "
                            f"{m['matureHitNext5FourPct']} | {m['matureNoHitNext5FourPct']} |\n")
            f.write("\nNo buy/reentry, no live signals, no PIT or blind proof.\n")
if __name__=="__main__":main()
