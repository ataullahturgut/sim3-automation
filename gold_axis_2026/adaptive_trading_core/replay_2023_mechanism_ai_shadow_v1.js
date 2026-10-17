"use strict";
/** Real chronological 2022Q4 pretrained CORE, Jan-Feb23 ACTUAL bid/ask archive.
 * AI GPT submissions are optional but NEVER fabricated.
 * 2023 firstprint macro news unavailable => retrospective quarantine only.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const core=require("./adaptive_market_core_s1_s2");
const cadence=require("./live_cadence_gate_v1");
const protocol=require("./chronological_ai_portfolio_v1");
const {releasesFromLedger}=require("./replay_conditional_pretrained_2023_2025");
const JAN=Date.parse("2023-01-01T00:00:00Z"),MARCH=Date.parse("2023-03-01T00:00:00Z");
const REPLAY_END="2023-03-01T00:15:00Z",REGISTRY="MACRO_ARCHIVE_POST_RELEASE_PAIR_UNVERIFIED";
const iso=n=>new Date(n).toISOString();
const round=n=>Number.isFinite(n)?Math.round(n*10000)/10000:null;
const evalStart="2023-01-01T00:00:00Z";
const eventsOnDays={
 "2023-01-04":"JOLTS/Fed minutes — RETROSPECTIVE_NAME_ONLY",
 "2023-01-05":"ADP — RETROSPECTIVE_NAME_ONLY",
 "2023-01-06":"NFP/AHE/UNEMP — RECONSTRUCTED_MACRO",
 "2023-01-12":"CPI — RECONSTRUCTED_MACRO",
 "2023-01-18":"PPI/retail — RETROSPECTIVE_NAME_ONLY",
 "2023-01-26":"GDP — RETROSPECTIVE_NAME_ONLY",
 "2023-01-27":"PCE — RETROSPECTIVE_NAME_ONLY",
 "2023-01-31":"ECI/Fed — RETROSPECTIVE_NAME_ONLY",
 "2023-02-01":"Fed — RETROSPECTIVE_NAME_ONLY",
 "2023-02-02":"ECB/BoE/Fed repricing — RETROSPECTIVE_NAME_ONLY",
 "2023-02-03":"NFP/AHE/UNEMP — RECONSTRUCTED_MACRO",
 "2023-02-14":"CPI — RECONSTRUCTED_MACRO"
};
function snap(o){
 const h=(o.ruleDiscovery.forecastAtDecision?.byHorizon||[]).find(x=>x.horizonMinutes===240);
 return {s1:{ready:!!h?.ready,
     pUpPct:h?.ready?round(100*h.upFraction):null,
     expectedLogPct:h?.ready?round(h.expectedLogPct):null,
     effectiveN:h?.ready?round(h.effectiveN):null},
  s2:{phase:o.lifecycle.phase,direction:o.lifecycle.direction,
   trendZ:round(o.lifecycle.trendZ)},
  s3:{researchAction:o.positionResearch.proposedResearchAction,
      reason:o.positionResearch.researchDecisionReason,
      actualAction:o.action,tradeAllowed:o.tradeAllowed}};
}
function run(bars,sessions,ledgerText,aiRecords=[]){
 if(!Array.isArray(bars)||bars.length<9500||
    !Array.isArray(sessions)||!ledgerText||!Array.isArray(aiRecords))
  throw Error("REAL_2022_Q4_TO_FEB_2023_M15_REQUIRED");
 const source=bars[0].source_id,types=releasesFromLedger(ledgerText)
  .filter(x=>x.ts>=JAN&&x.ts<MARCH);
 if(types.length!==4)throw Error("EXPECTED_4_MACRO_RELEASE_WAVES:"+types.length);
 const model=core.create({sourceId:source,
   sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",learningMode:"DISCOVERY_FULL_ARCHIVE",
   shadowResearch:false,positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",
   economicSources:{[REGISTRY]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}}});
 const s=protocol.newState({sourceId:source,firstAt:evalStart,endAt:REPLAY_END,aiRecords});
 let si=0,ei=0,last=-Infinity,trained=false,train=0,evalBars=0,gateCalls=0,
  prior=null,lastEval=null,previousDay=null,prevDayFirst=null,prevDayLast=null,
  eventIDs=[],processBarId=null,processedEventId=null;
 const days=new Map();
 function ensure(d){
  if(!days.has(d))days.set(d,{date:d,barCount:0,attention:0,
   attentionReasons:{},macroWaveNew:0,
   sessionReturnPct:null,lastCore:null,coreTradeAuthority:false,
   firstBid:null,lastBid:null,aiActions:0,hybridActions:0});
  return days.get(d);
 }
 function finishDay(nextAt){
  if(!previousDay||prevDayFirst===null||prevDayLast===null)return;
  // Outcomes become available after prior session has finished.
  const v=round(100*(prevDayLast/prevDayFirst-1)),d=ensure(previousDay);
  d.sessionReturnPct=v;
  protocol.completeSession(s,{day:previousDay,
   sessionReturnPct:v,availableAt:iso(s.lastBarTime)});
  prevDayFirst=null;prevDayLast=null;
 }
 for(const r of bars){
  const t=Date.parse(r.bar_start_utc),at=t+900000,price=(Number(r.bid_close)+Number(r.ask_close))/2;
  if(!Number.isFinite(t)||t<=last||r.source_id!==source||
    !(Number(r.bid_close)>0)||Number(r.ask_close)<Number(r.bid_close))
   throw Error("UNSORTED_OR_BAD_REAL_BIDASK");
  last=t;
  while(si<sessions.length&&Date.parse(sessions[si].session+"T22:00:00Z")<at){
   const ss=sessions[si++];
   if(ss.source_id!==source)throw Error("SLOW_SOURCE_CHANGED");
   core.observeSlowSession(model,ss);
  }
  if(t>=MARCH)break;
  const out={barStartedAt:iso(t),asof:iso(at),priceAvailableAt:iso(at),
   barMinutes:15,price,priceSource:source};
  if(t<JAN){
   core.observe(model,out);train++;continue;
  }
  if(!trained){
   prior=core.summary(model).ruleDiscovery;
   if(prior.learnedRules<1||train!==5865)
    throw Error("MISSING_REAL_PRE2023_MODEL_MEMORY");
   trained=true;
  }
  const today=protocol.dayAt(iso(at));
  if(previousDay!==null&&today!==previousDay)finishDay(iso(at));
  previousDay=today;
  if(prevDayFirst===null)prevDayFirst=price;
  prevDayLast=price;
  const received=at+15000;
  // Economic source is genuinely archived but the firstprint/vintage is NOT:
  // do not treat assumed +60m delay as a verified economic release.
  while(ei<types.length&&types[ei].ts+3600000<=received){
   const e=types[ei++],assumed=e.ts+3600000;
   const gateEvent=cadence.evaluate({now:iso(assumed),marketOpen:true,
    registeredMarketSource:source,
    latestEvent:{sourceId:REGISTRY,releaseId:e.id,revisionId:"2026_ARCHIVE",
     eventTime:e.id,firstAvailableAt:iso(assumed),receivedAt:iso(assumed),
     firstPrintVerified:false,consensusVintageVerified:false},
    lastProcessedEventId:processedEventId});
   const task=gateEvent.tasks.find(x=>x.kind==="QUARANTINE_UNVERIFIED_ECONOMIC_EVENT_AS_RESEARCH");
   if(!task||gateEvent.triggered.event)throw Error("RETRO_MACRO_FIRSTPRINT_PROMOTED");
   processedEventId=task.id;
   const info=protocol.newEvent(s,{id:e.id,kind:e.features.cpi_surprise_z?"CPI":"EMP",
    eventTime:e.id,availableAt:iso(assumed),source:REGISTRY,
    firstPrintVerified:false,consensusVintageVerified:false,
    mechanismCandidates:e.features.cpi_surprise_z?["G01","ORG01","ORG02"]:["G01","ORG01","ORG02"]});
   eventIDs.push(info.id);
   ensure(protocol.dayAt(e.id)).macroWaveNew++;
  }
  const gateNow=cadence.evaluate({now:iso(received),marketOpen:true,
   registeredMarketSource:source,
   quote:{sourceId:source,eventTime:iso(at),availableAt:iso(received),
    bid:Number(r.bid_close),ask:Number(r.ask_close)},
   completedBar:{sourceId:source,barStartedAt:iso(t),availableAt:iso(received),
     barMinutes:15,completed:true},lastProcessedBarId:processBarId});
  if(!gateNow.triggered.m15||gateNow.actionGates.tradeAllowed)
   throw Error("M15_CORE_GATE_FAILURE");
  processBarId=source+"|"+iso(t);
  gateCalls++;
  const o=core.observe(model,out);
  if(o.action!==null||o.tradeAllowed!==false)
   throw Error("CORE_TRADE_AUTHORIZATION_MUST_REMAIN_FALSE");
  const summary=snap(o);
  const take=protocol.onBar(s,{barStart:iso(t),asof:iso(at),
   bid:Number(r.bid_close),ask:Number(r.ask_close),snapshot:summary,modelAction:o.action});
  evalBars++;lastEval={price,asof:iso(at),bid:Number(r.bid_close),ask:Number(r.ask_close)};
  const d=ensure(today);d.barCount++;d.lastCore=summary;d.lastBid=Number(r.bid_close);
  if(d.firstBid===null)d.firstBid=Number(r.bid_close);
  if(take.attention){
   d.attention++;
   take.kinds.forEach(x=>{d.attentionReasons[x]=(d.attentionReasons[x]||0)+1});
  }
 }
 if(!trained||evalBars!==3750||gateCalls!==3750||eventIDs.length!==4||!lastEval)
  throw Error("INCOMPLETE_JAN_FEB_2023_REPLAY");
 if(previousDay)finishDay(lastEval.asof);
 const v=protocol.finish(s,{endQuote:lastEval,finalAt:lastEval.asof});
 if(v.aiUsed!==aiRecords.length)throw Error("UNCONSUMED_AI_RESPONSES_REJECTED");
 const records=Array.from({length:59},(_,i)=>{
  const at=new Date(Date.UTC(2023,0,1+i)).toISOString().slice(0,10);
  const d=days.get(at)||{date:at,barCount:0,attention:0,attentionReasons:{},
   macroWaveNew:0,sessionReturnPct:null,lastCore:null};
  return {date:at,hasSession:d.barCount>0,
   bars:d.barCount,attention:d.attention,attentionReasons:d.attentionReasons,
   knownEconomicResearchCandidate:eventsOnDays[at]||null,
   observedArchiveMacroWaves:d.macroWaveNew,core:d.lastCore,
   observedSessionReturnPct:d.sessionReturnPct,
   decisions:v.decisions.filter(x=>protocol.dayAt(x.asof)===at),
   shadowExecutions:s.executionLog.filter(x=>protocol.dayAt(x.executionAt)===at)};
 });
 return {version:"GOLD_2023_JAN_FEB_ACTUAL_CORE_WITH_GPT_HANDOFF_V1_20261017",
  project:"GOLD-ADAPTIVE-MODEL-APP-01",mode:"CHRONOLOGICAL_RECONSTRUCTED_ARCHIVE_RESEARCH",
  sourceId:source,pretrain:{start:"2022-10-01",end:"2022-12-31",
    bars:train,ruleCount:prior.learnedRules,maturedLabels:prior.matureLabels},
  range:"2023-01-01..2023-02-28",
  janFebBars:evalBars,coreCalls:evalBars,gateCalls,
  researchReleases:eventIDs,
  eventProof:"RECONSTRUCTED_ARCHIVE_FIRSTPRINT_UNVERIFIED",
  aiProviderConnected:false,aiSubmitted:aiRecords.length,
  aiNote:aiRecords.length?"EXPLICIT_EXTERNALLY_SUPPLIED_RETROSPECTIVE_AI_MEMOS":
   "NO_AI_PROVIDER_OR_GPT_DECISIONS; DO_NOT_INTERPRET_AI_PORTFOLIO_AS_PERFORMANCE",
  portfolioAudit:{...v,attention:v.attention.map(x=>({
    at:x.at,day:x.day,kinds:x.kinds,events:x.events.map(e=>({id:e.id,kind:e.kind,
     evidenceStatus:e.evidenceStatus})),snapshotHash:crypto.createHash("sha256")
       .update(JSON.stringify(x)).digest("hex")}))},
  dates:records,
  mainScientificGate:"FAIL_NOT_BLIND_OOS",
  tradeAllowed:false,actualBankTrades:0};
}
if(require.main===module){
 const [a,b,c,d]=process.argv.slice(2);
 if(!a||!b||!c)throw Error("ARGS PRIVATE_M15_JSON PRIVATE_SLOW_JSON MACRO_CSV [OPTIONAL_REAL_GPT_DECISIONS_JSON]");
 const records=d?JSON.parse(fs.readFileSync(d,"utf8")):[];
 const result=run(JSON.parse(fs.readFileSync(a,"utf8")),
  JSON.parse(fs.readFileSync(b,"utf8")),fs.readFileSync(c,"utf8"),records);
 console.log(JSON.stringify(result,null,2));
}
module.exports={run};
