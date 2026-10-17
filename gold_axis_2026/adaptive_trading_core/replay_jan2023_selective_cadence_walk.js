"use strict";
/**
 * Jan 2023 chronological selective-cadence research walk.
 * Uses the EXISTING SINGLE S1/S2/S3 CORE, with a real operational M1 cadence
 * gate (not a second forecasting model). Pretrain Q4 2022, then January M15.
 *
 * Price quotes and receivedAt are RECONSTRUCTED: +15s processing/quote delay
 * is a replay convention, NOT observed historical delivery latency.
 * Archived 2023 economic ledger IS NOT first-print PIT. Never inject those
 * 2026-reconstructed macro surprises into S1 as certified 2023 observations.
 * Never synthesize ORG causality from any price-only large move.
 */
const fs=require("node:fs");
const core=require("./adaptive_market_core_s1_s2");
const gate=require("./live_cadence_gate_v1");
const {releasesFromLedger}=require("./replay_conditional_pretrained_2023_2025");
const SOURCE_EVENT="MACRO_ARCHIVE_POST_RELEASE_PAIR_UNVERIFIED";
const JAN=Date.parse("2023-01-01T00:00:00Z"),FEB=Date.parse("2023-02-01T00:00:00Z");
const iso=v=>new Date(v).toISOString(),round=v=>Number.isFinite(v)?Math.round(v*10000)/10000:null;
const researchCandidates={
 "2023-01-04":"G01-mixed · JOLTS ve Fed tutanakları",
 "2023-01-05":"ORG02? · ADP",
 "2023-01-06":"ORG01 / ORG02? · NFP + AHE + UNEMP",
 "2023-01-12":"ORG01? · CPI",
 "2023-01-18":"ORG01? · ÜFE + perakende satış",
 "2023-01-26":"ORG02? · GSYH",
 "2023-01-27":"G01-mixed · PCE",
 "2023-01-31":"G01-mixed · ECI/Fed beklentisi"
};
function dailySnapshot(o,state,at){
 const h=(o.ruleDiscovery.forecastAtDecision?.byHorizon??[]).find(x=>x.horizonMinutes===240);
 const v=o.positionResearch,slow=state.lastSlow;
 return {at,
  s1:{ready:!!h?.ready,pUpPct:h?.ready?round(100*h.upFraction):null,
    expectedLogPct:h?.ready?round(h.expectedLogPct):null,
    n:h?.ready?round(h.effectiveN):null},
  s2:{phase:o.lifecycle.phase,direction:o.lifecycle.direction,
    trendZ:round(o.lifecycle.trendZ),
    slowPhase:slow&&Date.parse(slow.observedAt)<=Date.parse(at)?slow.phase:null},
  s3:{researchAction:v.proposedResearchAction,reason:v.researchDecisionReason,
      actualAction:v.action,tradeAllowed:v.tradeAllowed}};
}
function run(bars,sessions,ledger){
 if(!Array.isArray(bars)||bars.length<7500||!Array.isArray(sessions)||!ledger)
  throw Error("REAL_PRICE_PRETRAIN_AND_MACRO_REQUIRED");
 const source=bars[0].source_id;
 const waves=releasesFromLedger(ledger).filter(e=>e.ts>=JAN&&e.ts<FEB);
 if(waves.length!==2)throw Error("JANUARY_RECONSTRUCTED_MACRO_WAVE_CONTRACT:"+waves.length);
 // Keep the registered archive EVENT source for evidence audit, never attach
 // uncertified economicFeatures to bar inputs in the strict operational replay.
 const s=core.create({sourceId:source,sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",
  learningMode:"DISCOVERY_FULL_ARCHIVE",shadowResearch:false,
  positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",
  economicSources:{[SOURCE_EVENT]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}}});
 const dmap=new Map(),seenEvent=new Set(),eventRecords=[];
 const sampleGaps=[];let si=0,ei=0,train=0,janBars=0,gateCalls=0,
  modelCalls=0,coreTradeActions=0,gateTradeAllowed=0,pretrain=null,
  processedBarId=null,processedEventId=null,slowCalls=0,lastPrice=null,prevTime=-Infinity;
 function day(d){
  if(!dmap.has(d))dmap.set(d,{date:d,barCount:0,m1Accepted:0,
    eventCandidateCount:0,certifiedEconomicFeatures:0,
    priceChangeWatchCount:0,fastTransitions:0,modelActionChanges:0,
    lastPrice:null,firstPrice:null,eventNotes:[],snapshot:null});
  return dmap.get(d);
 }
 for(const r of bars){
  const started=Date.parse(r.bar_start_utc),ended=started+900000;
  if(started<=prevTime||r.source_id!==source)throw Error("UNSORTED_OR_SOURCE_CHANGED");
  const previousBarStart=prevTime;
  prevTime=started;
  const price=(Number(r.bid_close)+Number(r.ask_close))/2;
  if(!(price>0)||Number(r.ask_close)<Number(r.bid_close))throw Error("BAD_RECONSTRUCTED_QUOTE");
  while(si<sessions.length&&Date.parse(sessions[si].session+"T22:00:00Z")<ended){
   const ss=sessions[si++];
   if(ss.source_id!==source)throw Error("SLOW_SOURCE_CHANGE");
   core.observeSlowSession(s,ss);slowCalls++;
  }
  if(ended>=JAN&&pretrain===null){
   pretrain=core.summary(s);
   if(pretrain.ruleDiscovery.learnedRules<1)throw Error("STARTS_WITHOUT_PRIOR_MODEL_MEMORY");
  }
  const outBar={barStartedAt:iso(started),asof:iso(ended),
    priceAvailableAt:iso(ended),barMinutes:15,price,priceSource:source};
  if(started<JAN){
   core.observe(s,outBar);train++;lastPrice=price;continue;
  }
  if(started>=FEB)break;
  const date=iso(started+7200000).slice(0,10);
  if(date<"2023-01-01"||date>"2023-01-31")throw Error("SESSION_ROLL_BAD");
  const record=day(date),syntheticReception=ended+15000;
  // Every actual historical M15 is inspected exactly once. No made-up minute
  // ticks or fake observed quote/received_at are claimed.
  while(ei<waves.length&&waves[ei].ts+3600000<=syntheticReception){
   const e=waves[ei++],assumed=e.ts+3600000;
   const g=gate.evaluate({now:iso(assumed),marketOpen:true,
    registeredMarketSource:source,quote:null,
    latestEvent:{sourceId:SOURCE_EVENT,releaseId:e.id,revisionId:"RETROSPECTIVE_2026_ARCHIVE",
     eventTime:e.id,firstAvailableAt:iso(assumed),receivedAt:iso(assumed),
     firstPrintVerified:false,consensusVintageVerified:false},
    lastProcessedEventId:processedEventId});
   const task=g.tasks.find(x=>x.kind==="QUARANTINE_UNVERIFIED_ECONOMIC_EVENT_AS_RESEARCH");
   if(!task||g.triggered.event||g.actionGates.tradeAllowed)throw Error("FALSE_CERTIFIED_EVENT");
   processedEventId=task.id;seenEvent.add(e.id);
   const key=iso(e.ts+7200000).slice(0,10);
   const ed=day(key);
   ed.eventCandidateCount++;
   const note={kind:"RETROSPECTIVE_MACRO_WAVE_NOT_PIT",
    scheduledReleaseUTC:e.id,assumedResearchAvailableUTC:iso(assumed),
    note:"Haber/sürpriz ilk baskı ve konsensüs vintage doğrulanmadığı için S1'e sertifikalı ekonomik özellik verilmedi.",
    evidenceStatus:"RECONSTRUCTED_POST_RELEASE_UNVERIFIED"};
   ed.eventNotes.push(note);eventRecords.push(note);
  }
  const z=gate.evaluate({now:iso(syntheticReception),marketOpen:true,
    registeredMarketSource:source,quote:{sourceId:source,
     eventTime:iso(ended),availableAt:iso(syntheticReception),
     bid:Number(r.bid_close),ask:Number(r.ask_close)},
    completedBar:{sourceId:source,barStartedAt:iso(started),
     availableAt:iso(syntheticReception),barMinutes:15,completed:true},
    lastProcessedBarId:processedBarId});
  gateCalls++;
  if(!z.triggered.m15||z.actionGates.tradeAllowed||
    z.tasks.filter(x=>x.kind==="RUN_EXISTING_S1_S2_S3_RESEARCH_ON_COMPLETED_M15").length!==1)
   throw Error("SELECTIVE_M15_GATE_FAILED");
  processedBarId=source+"|"+iso(started);
  const obs=core.observe(s,outBar);
  modelCalls++;janBars++;record.barCount++;record.m1Accepted++;
  if(obs.tradeAllowed!==false||obs.action!==null)coreTradeActions++;
  if(z.actionGates.tradeAllowed)gateTradeAllowed++;
  if(record.firstPrice===null)record.firstPrice=price;
  record.lastPrice=price;
  // Mechanical no-future, no-economic-causality statistical watch. A fixed
  // 0.5%-per-M15 threshold is a descriptive attention flag, never a learned
  // macro rule, a BUY signal, or a parameter optimized on this January.
  if(lastPrice!==null&&started-previousBarStart===900000&&
     Math.abs(100*(price/lastPrice-1))>=0.5)
    record.priceChangeWatchCount++;
  if(["START","END","REENTRY"].includes(obs.lifecycle.phase))
    record.fastTransitions++; // observation count, not unique transitions
  record.snapshot=dailySnapshot(obs,s,iso(ended));
  lastPrice=price;
 }
 if(!pretrain||train!==5865||janBars!==1920||modelCalls!==janBars||
    gateCalls!==janBars||seenEvent.size!==2||coreTradeActions||gateTradeAllowed)
  throw Error("JANUARY_SELECTIVE_REPLAY_INCOMPLETE");
 const days=Array.from({length:31},(_,i)=>{
  const date="2023-01-"+String(i+1).padStart(2,"0");
  const d=dmap.get(date);
  if(!d)return {date,hasSession:false,barCount:0,m1Accepted:0,
    ruleCandidate:researchCandidates[date]||null,
    ruleEvidence:"RETROSPECTIVE_RESEARCH_HYPOTHESIS_NOT_MODEL_SIGNAL",
    priceChangeWatchCount:0,eventCandidateCount:0,
    economicFeaturesPITAccepted:0,snapshot:null,observedSessionReturnPct:null,eventNotes:[]};
  return {date,hasSession:!!d.barCount,barCount:d.barCount,m1Accepted:d.m1Accepted,
   ruleCandidate:researchCandidates[date]||null,
   ruleEvidence:"RETROSPECTIVE_RESEARCH_HYPOTHESIS_NOT_MODEL_SIGNAL",
   priceChangeWatchCount:d.priceChangeWatchCount,eventCandidateCount:d.eventCandidateCount,
   economicFeaturesPITAccepted:0,
   snapshot:d.snapshot,
   observedSessionReturnPct:d.firstPrice&&d.lastPrice?
    round(100*(d.lastPrice/d.firstPrice-1)):null,
   eventNotes:d.eventNotes};
 });
 return {version:"GOLD_JAN2023_SELECTIVE_M1_S1_S2_S3_WALK_V1_20261017",
  mode:"CHRONOLOGICAL_ARCHIVE_REPLAY_NOT_REAL_TIME",
  sourceId:source,marketPriceType:"RECONSTRUCTED_BID_ASK_MID_NOT_BANK",
  quoteReceiptTime:"ASSUMED_BAR_CLOSE_PLUS_15_SECONDS_NOT_OBSERVED",
  macroAccessTime:"ASSUMED_RELEASE_PLUS_60_MINUTES_NOT_FIRSTPRINT_VERIFIED",
  eventDetectionType:"ARCHIVE_REPLAY_NO_LIVE_NEWS_FEED",
  noFuturePriceAtDecision:true,firstPrintMacroVerified:false,
  goldBankExecution:false,tradeAllowed:false,
  coreSourceVersion:pretrain.version,modelCore:"adaptive_market_core_s1_s2.js",
  prior:{bars:train,rules:pretrain.ruleDiscovery.learnedRules,
    maturedLabels:pretrain.ruleDiscovery.matureLabels},
  observed:{janM15:janBars,gateCalls,modelCalls,
    slowSessionCallbacks:slowCalls,
    retrospectiveMacroWaves:seenEvent.size,
    retrospectiveMacroQuarantined:eventRecords.length,
    macroPITFeaturesAccepted:0,
    priceWatch15mEvents:days.reduce((z,x)=>z+x.priceChangeWatchCount,0),
    acceptedTradeActions:coreTradeActions,actualBankTrades:0,
    daySessions:days.filter(x=>x.hasSession).length,
    hoursWithoutBarModelInvocation:"NO_TICKS_EMULATED"},
  end:core.summary(s).ruleDiscovery,
  days};
}
if(require.main===module){
 const [a,b,c]=process.argv.slice(2);
 if(!a||!b||!c)throw Error("ARGS: PRIVATE_M15_JSON PRIVATE_SESSIONS_JSON MACRO_CSV");
 console.log(JSON.stringify(run(JSON.parse(fs.readFileSync(a,"utf8")),
  JSON.parse(fs.readFileSync(b,"utf8")),fs.readFileSync(c,"utf8")),null,2));
}
module.exports={run};
