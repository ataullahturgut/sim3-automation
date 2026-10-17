"use strict";
const t=require("node:test"),a=require("node:assert/strict");
const {evaluate}=require("./live_cadence_gate_v1");
const SRC="VERIFIED_SOURCE_TEST"; // synthetic source name, never real market data
const at="2026-10-16T15:15:25Z",marketOpen=true;
const quote={sourceId:SRC,eventTime:"2026-10-16T15:15:05Z",
 availableAt:"2026-10-16T15:15:07Z",bid:1900,ask:1900.3};
const bar={sourceId:SRC,barStartedAt:"2026-10-16T15:00:00Z",
 availableAt:"2026-10-16T15:15:09Z",barMinutes:15,completed:true};
const event={sourceId:"OFFICIAL_TEST_FEED",releaseId:"NFP_TEST",revisionId:"first",
 eventTime:"2026-10-16T15:07:00Z",firstAvailableAt:"2026-10-16T15:07:05Z",
 receivedAt:"2026-10-16T15:07:10Z",firstPrintVerified:true,consensusVintageVerified:true};
function base(extra={}){return {now:at,marketOpen,registeredMarketSource:SRC,quote,...extra}}
const kinds=r=>r.tasks.map(z=>z.kind);
t("valid completed M15 evaluates the existing CORE once but never authorizes execution",()=>{
 const x=evaluate(base({completedBar:bar}));
 a.ok(kinds(x).includes("RUN_EXISTING_S1_S2_S3_RESEARCH_ON_COMPLETED_M15"));
 a.equal(x.triggered.m15,true);a.equal(x.actionGates.tradeAllowed,false);
 a.equal(x.providerConnected,false);a.equal(x.liveTradingConnected,false);
 a.equal(x.tasks.find(z=>z.kind.startsWith("RUN_")).barAsOf,"2026-10-16T15:15:00.000Z");
});
t("economic release triggers immediate evidence check but not incomplete M15 or trade",()=>{
 const x=evaluate(base({now:"2026-10-16T15:07:12Z",
 quote:{...quote,eventTime:"2026-10-16T15:07:10Z",availableAt:"2026-10-16T15:07:11Z"},
 latestEvent:event}));
 a.equal(x.triggered.event,true);a.equal(x.triggered.m15,false);
 a.deepEqual(kinds(x),["APPEND_ONLY_EVENT_EVIDENCE",
  "CHECK_VERIFIED_ECONOMIC_CONTEXT_NOW_NO_PARTIAL_BAR_TRADE"]);
 a.equal(x.actionGates.tradeAllowed,false);
});
t("unverified first-print release is quarantined, not passed as economic alpha",()=>{
 const x=evaluate(base({latestEvent:{...event,firstPrintVerified:false}}));
 a.equal(x.triggered.event,false);
 a.ok(kinds(x).includes("QUARANTINE_UNVERIFIED_ECONOMIC_EVENT_AS_RESEARCH"));
 a.ok(x.reasons.includes("MACRO_FIRSTPRINT_OR_CONSENSUS_UNVERIFIED"));
});
t("model and macro duplicates never generate repeated inference",()=>{
 const x=evaluate(base({completedBar:bar,
  lastProcessedBarId:SRC+"|2026-10-16T15:00:00.000Z",
  latestEvent:event,
  lastProcessedEventId:"OFFICIAL_TEST_FEED|NFP_TEST|first"}));
 a.equal(x.tasks.length,0);
 a.ok(x.reasons.includes("DUPLICATE_M15"));
 a.ok(x.reasons.includes("DUPLICATE_EVENT_REVISION"));
});
t("stale prices fail closed but unverified research events can still be recorded",()=>{
 const x=evaluate(base({now:"2026-10-16T15:19:00Z",latestEvent:event,
  quote:{...quote,eventTime:"2026-10-16T15:14:01Z",
    availableAt:"2026-10-16T15:14:01Z"}}));
 a.equal(x.status,"PRICE_STALE");
 a.equal(x.actionGates.quoteFresh,false);
 a.equal(x.actionGates.tradeAllowed,false);
 a.ok(kinds(x).includes("APPEND_ONLY_EVENT_EVIDENCE"));
});
t("late bar is backfilled/quarantined, not transformed into a retroactive live decision",()=>{
 const x=evaluate(base({now:"2026-10-16T15:18:00Z",completedBar:bar}));
 a.equal(x.triggered.m15,false);
 a.ok(kinds(x).includes("QUARANTINE_LATE_BAR_FOR_CHRONOLOGICAL_BACKFILL"));
 a.ok(!kinds(x).includes("RUN_EXISTING_S1_S2_S3_RESEARCH_ON_COMPLETED_M15"));
});
t("rejects incomplete 15-minute bar and future event leakage",()=>{
 a.throws(()=>evaluate(base({completedBar:{...bar,barStartedAt:"2026-10-16T15:15:00Z"}})),/ONLY_COMPLETED/);
 a.throws(()=>evaluate(base({latestEvent:{...event,firstAvailableAt:"2026-10-16T18:00:00Z"}})),/FUTURE_EVENT/);
 a.throws(()=>evaluate(base({completedBar:{...bar,sourceId:"UNAPPROVED"}})),/SOURCE/);
});
t("qualified daily S2 SLOW updates once after close, not before",()=>{
 const ss={sourceId:SRC,sessionId:"2026-10-15",closedAt:"2026-10-15T22:00:00Z",
  availableAt:"2026-10-15T22:01:00Z",qualified:true};
 const x=evaluate(base({closedSession:ss}));
 a.equal(x.triggered.slow,true);
 a.ok(kinds(x).includes("UPDATE_S2_SLOW_FROM_QUALIFIED_COMPLETED_SESSION"));
 const y=evaluate(base({closedSession:ss,lastProcessedSlowSessionId:SRC+"|2026-10-15"}));
 a.equal(y.triggered.slow,false);
 const z=evaluate(base({closedSession:{...ss,qualified:false}}));
 a.ok(kinds(z).includes("RECORD_REJECTED_SLOW_SESSION_AND_CENSOR_PENDING"));
});
t("weekend/market closure is not a synthetic trade timer",()=>{
 const x=evaluate(base({marketOpen:false,quote:null,latestEvent:event}));
 a.equal(x.status,"MARKET_CLOSED");
 a.equal(x.actionGates.tradeAllowed,false);
 a.equal(x.triggered.event,true);a.equal(x.triggered.m15,false);
 a.ok(x.reasons.includes("MARKET_CLOSED_NO_NEW_EXECUTION"));
});
