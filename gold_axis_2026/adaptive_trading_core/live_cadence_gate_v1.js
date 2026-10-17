"use strict";
/** MODEL/M1 operational scheduler gate (pure function, NEVER a trading engine).
 * No network IO, cron, data provider, backend, live trading, or alpha logic.
 * An EVENT may trigger prompt evidence review, but only a completed M15 bar
 * can call the existing actual S1/S2/S3 CORE.
 */
const VERSION="GOLD_M1_HYBRID_CADENCE_GATE_SPEC_V1_20261017";
const M15=900000;
const MAX_LATE_BAR_MS=120000; // first field-test target, not a provider guarantee
const MAX_STALE_QUOTE_MS=120000; // first field-test target, not a certified live SLA
function stamp(x){
 if(typeof x!=="string"||!Number.isFinite(Date.parse(x))||
    !(/Z$|[+-]\d\d:\d\d$/.test(x)))throw Error("M1_TIME_MUST_INCLUDE_UTC_OFFSET");
 return Date.parse(x);
}
function asIso(x){return new Date(x).toISOString();}
function checkSource(source,expected){
 if(typeof source!=="string"||!source||source!==expected)
  throw Error("M1_UNREGISTERED_OR_CHANGED_SOURCE");
}
function evaluate(input){
 if(!input||typeof input!=="object")throw Error("M1_INPUT_REQUIRED");
 const now=stamp(input.now);
 const expected=input.registeredMarketSource;
 if(typeof expected!=="string"||!expected)throw Error("M1_REGISTERED_SOURCE_REQUIRED");
 const isOpen=input.marketOpen===true;
 if(typeof input.marketOpen!=="boolean")throw Error("M1_MARKET_STATUS_REQUIRED");
 const tasks=[],gates=[],reasons=[];
 let quoteFresh=false;
 if(input.quote){
  const q=input.quote;
  checkSource(q.sourceId,expected);
  const observed=stamp(q.eventTime),available=stamp(q.availableAt);
  if(available>now||observed>available)throw Error("M1_FUTURE_OR_IMPOSSIBLE_QUOTE");
  if(!Number.isFinite(q.bid)||!Number.isFinite(q.ask)||q.bid<=0||q.ask<q.bid)
   throw Error("M1_QUOTE_BID_ASK_INVALID");
  quoteFresh=now-available<=MAX_STALE_QUOTE_MS;
 }
 if(isOpen&&!quoteFresh)reasons.push("QUOTE_MISSING_OR_STALE");
 let barAccepted=false;
 if(input.completedBar){
  const b=input.completedBar;
  checkSource(b.sourceId,expected);
  const started=stamp(b.barStartedAt),available=stamp(b.availableAt);
  const ending=started+M15;
  if(b.barMinutes!==15||b.completed!==true||ending>now||ending>available)
   throw Error("M1_ONLY_COMPLETED_15MIN_BAR");
  const id=expected+"|"+asIso(started);
  const age=now-available;
  if(input.lastProcessedBarId===id)reasons.push("DUPLICATE_M15");
  else if(age>MAX_LATE_BAR_MS){
   tasks.push({kind:"QUARANTINE_LATE_BAR_FOR_CHRONOLOGICAL_BACKFILL",id});
   reasons.push("LATE_BAR_NO_RETROACTIVE_LIVE_DECISION");
  }else{
   tasks.push({kind:"RUN_EXISTING_S1_S2_S3_RESEARCH_ON_COMPLETED_M15",id,
     barAsOf:asIso(ending),availableAt:asIso(available)});
   barAccepted=true;
  }
 }
 let eventAccepted=false;
 if(input.latestEvent){
  const e=input.latestEvent;
  if(typeof e.sourceId!=="string"||!e.sourceId||!e.releaseId||!e.revisionId)
   throw Error("M1_EVENT_PROVENANCE_REQUIRED");
  const eventTime=stamp(e.eventTime),firstAvailable=stamp(e.firstAvailableAt),
    received=stamp(e.receivedAt);
  if(eventTime>firstAvailable||firstAvailable>received||received>now)
   throw Error("M1_FUTURE_EVENT_OR_INVALID_FIRST_AVAILABILITY");
  const id=[e.sourceId,e.releaseId,e.revisionId].join("|");
  if(id===input.lastProcessedEventId)reasons.push("DUPLICATE_EVENT_REVISION");
  else{
   tasks.push({kind:"APPEND_ONLY_EVENT_EVIDENCE",id,
    eventTime:asIso(eventTime),firstAvailableAt:asIso(firstAvailable),
    receivedAt:asIso(received)});
   if(e.firstPrintVerified===true&&e.consensusVintageVerified===true){
    tasks.push({kind:"CHECK_VERIFIED_ECONOMIC_CONTEXT_NOW_NO_PARTIAL_BAR_TRADE",id});
    eventAccepted=true;
   }else{
    tasks.push({kind:"QUARANTINE_UNVERIFIED_ECONOMIC_EVENT_AS_RESEARCH",id});
    reasons.push("MACRO_FIRSTPRINT_OR_CONSENSUS_UNVERIFIED");
   }
  }
 }
 let slowAccepted=false;
 if(input.closedSession){
  const ss=input.closedSession;
  checkSource(ss.sourceId,expected);
  if(typeof ss.sessionId!=="string"||!ss.sessionId)
   throw Error("M1_SLOW_SESSION_ID_REQUIRED");
  const closed=stamp(ss.closedAt),available=stamp(ss.availableAt);
  if(closed>available||available>now)throw Error("M1_SLOW_SESSION_NOT_YET_AVAILABLE");
  const id=ss.sourceId+"|"+ss.sessionId;
  if(id===input.lastProcessedSlowSessionId)reasons.push("DUPLICATE_SLOW_SESSION");
  else if(ss.qualified===true){
   tasks.push({kind:"UPDATE_S2_SLOW_FROM_QUALIFIED_COMPLETED_SESSION",id,
    asOf:asIso(available)});
   slowAccepted=true;
  }else{
   tasks.push({kind:"RECORD_REJECTED_SLOW_SESSION_AND_CENSOR_PENDING",id});
   reasons.push("UNQUALIFIED_SLOW_SESSION");
  }
 }
 const actionGates={marketOpen:isOpen,quoteFresh,
   bankBidAskVerified:false,modelScienceAccepted:false,
   tradeAllowed:false};
 if(!isOpen)reasons.push("MARKET_CLOSED_NO_NEW_EXECUTION");
 gates.push("CORE_ONLY_AFTER_COMPLETED_M15",
   "EVENT_NEVER_BECOMES_UNVALIDATED_S1_PIT_FEATURE",
   "S1_240MIN_ANCHOR_INTERNAL_TO_EXISTING_CORE",
   "SLOW_ONLY_AFTER_VERIFIED_COMPLETE_SESSION",
   "S3_RESEARCH_ONLY_NO_BROKER_TRADE",
   "NO_REWRITE_OF_MATURED_OR_PENDING_LABELS");
 return {version:VERSION,asOf:asIso(now),tasks,gates,actionGates,
  triggered:{m15:barAccepted,event: eventAccepted,slow:slowAccepted},
  reasons:[...new Set(reasons)],
  status:!isOpen?"MARKET_CLOSED":!quoteFresh?"PRICE_STALE":"OBSERVING",
  providerConnected:false,liveTradingConnected:false};
}
module.exports={VERSION,evaluate,MAX_LATE_BAR_MS,MAX_STALE_QUOTE_MS};
