"use strict";
/** GOLD-ADAPTIVE-MODEL-APP-01 / February 2023 actual CORE S1+S2(+S3) daily audit.
 * Train on all available continuous Oct-Dec 2022 + Jan 2023 M15, NEVER future February returns.
 * Economic ledger from 2026 is research-only and not certified Feb-2023 PIT.
 * Daily precommitted checkpoint: final observed NY17-rolling 22:00 UTC session
 * (NOT a mandated bank trading window). The rule ontology match is an
 * unverified hypothesis, separate from the actual S1/S2 calculation.
 */
const fs=require("node:fs"),core=require("./adaptive_market_core_s1_s2");
const {releasesFromLedger}=require("./replay_conditional_pretrained_2023_2025");
const EVENT="MACRO_ARCHIVE_POST_RELEASE_PAIR_UNVERIFIED";
const iso=x=>new Date(x).toISOString();
const beginning=Date.parse("2023-02-01T00:00:00Z");
const endFeb=Date.parse("2023-03-01T00:00:00Z");
const cases={
 "2023-02-01":{hypothesis:"ORG01? / ORG02? RIVAL",trigger:"FOMC 25bp + Powell press conference",source:"FOMC_TIMESTAMP_ONLY_NO_CERTIFIED_SURPRISE"},
 "2023-02-02":{hypothesis:"ORG10? / ORG02? RIVAL",trigger:"Fed sonrası ters fiyatlama; somut ayrı tetik belirsiz",source:"PRICE_PATTERN_NOT_CAUSAL_PROOF"},
 "2023-02-03":{hypothesis:"ORG02?",trigger:"NFP + AHE + UNEMP",source:"RETROSPECTIVE_LEDGER_POST_RELEASE_ONLY"},
 "2023-02-07":{hypothesis:"ORG02? RIVAL",trigger:"Fed Başkanı Powell açıklamaları",source:"EVENT_DOCUMENTED_NO_PIT_SURPRISE"},
 "2023-02-09":{hypothesis:"ORG02? RIVAL",trigger:"Faiz beklentisi / USD baskısı adayı",source:"UNVERIFIED_CROSS_ASSET_TRANSFER"},
 "2023-02-14":{hypothesis:"ORG01 / ORG02 RIVAL",trigger:"TÜFE beklentiye paralel",source:"RETROSPECTIVE_LEDGER_POST_RELEASE_ONLY"},
 "2023-02-15":{hypothesis:"ORG02?",trigger:"ABD perakende satışlar",source:"EVENT_DOCUMENTED_NO_PIT_SURPRISE"},
 "2023-02-16":{hypothesis:"ORG02?",trigger:"ABD ÜFE",source:"EVENT_DOCUMENTED_NO_PIT_SURPRISE"},
 "2023-02-22":{hypothesis:"ORG02?",trigger:"Fed toplantı tutanakları",source:"EVENT_DOCUMENTED_NO_PIT_SURPRISE"},
 "2023-02-24":{hypothesis:"ORG02?",trigger:"ABD PCE",source:"EVENT_DOCUMENTED_NO_PIT_SURPRISE"}
};
function round(x){return typeof x==="number"&&Number.isFinite(x)?Math.round(x*10000)/10000:null;}
function run(bars,sessions,ledgerCSV){
 if(!Array.isArray(bars)||bars.length<4000)throw Error("OCT_DEC_PRICE_PRETRAIN_REQUIRED");
 if(!Array.isArray(sessions)||!ledgerCSV)throw Error("SESSION_AND_MACRO_REQUIRED");
 const sourceId=bars[0].source_id,ev=releasesFromLedger(ledgerCSV).filter(x=>x.ts<endFeb);
 const s=core.create({sourceId,sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",
  learningMode:"DISCOVERY_FULL_ARCHIVE",shadowResearch:false,
  positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",
  economicSources:{[EVENT]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}}});
 const daily=new Map();
 const pretrain={},seenEvents=new Set();
 let si=0,prevTime=null,trained=false,macAnchors=0,februaryBars=0,trainBars=0,lastSession=null;
 function info(o,at,price){
  const h=(o.ruleDiscovery.forecastAtDecision?.byHorizon||[]).find(x=>x.horizonMinutes===240);
  const z=o.lifecycle.hazard4h;
  const trend=o.lifecycle.trendZ;
  const v=o.positionResearch;
  const slow=s.lastSlow&&Date.parse(s.lastSlow.observedAt)<=Date.parse(at)?s.lastSlow:null;
  return {at,price:round(price),
   s1:{fourHourReady:!!h?.ready,expectedLogPct:h?.ready?round(h.expectedLogPct):null,
    upProbability:h?.ready?round(h.upFraction):null,
    uncertaintyPct:h?.ready?round(h.uncertaintyPct):null,
    effectiveN:h?.ready?round(h.effectiveN):0,
    matchedRuleIds:h?.ruleIds?.slice(0,8)||[]},
   s2:{phase:o.lifecycle.phase,direction:o.lifecycle.direction,
    trendZ:round(trend),episodeAgeMinutes:o.lifecycle.episodeAgeMinutes,
    hazard4hReady:!!z?.ready,pEnd4h:z?.ready?round(z.p):null,
    pContinue4h:z?.ready?round(z.continuationP):null,
    riskN:z?.riskN??0,
    slowPhase:slow?.phase??"UNREADY",slowDirection:slow?.direction??null,
    slowTrendZ:round(slow?.trendZ),slowEnd5SessionReady:slow?.pEnd5!==null&&slow?.pEnd5!==undefined,
    slowEnd5SessionProbability:round(slow?.pEnd5)},
   s3:{researchAction:v.proposedResearchAction,reason:v.researchDecisionReason,
    action:v.action,tradeAllowed:v.tradeAllowed,holding:v.holding,
    conditionalSource:v.conditionalResearch?.best?.source??null,
    expectedNetAdvantagePct:round(v.conditionalResearch?.best?.selected?.meanNetPct),
    independentN:v.conditionalResearch?.best?.selected?.effectiveN??null}};
 }
 for(const r of bars){
  const t=Date.parse(r.bar_start_utc),at=t+900000,price=(Number(r.bid_close)+Number(r.ask_close))/2;
  if(prevTime!==null&&t<=prevTime)throw Error("UNSORTED_REAL_QUOTES");
  prevTime=t;
  if(r.source_id!==sourceId||!Number.isFinite(price)||price<=0)throw Error("PRICE_SOURCE_FAILURE");
  while(si<sessions.length&&Date.parse(sessions[si].session+"T22:00:00Z")<at){
   const session=sessions[si++];
   if(session.source_id!==sourceId)throw Error("SESSION_SOURCE_MISMATCH");
   // Only completed slow-session data can influence later observations.
   core.observeSlowSession(s,session);
  }
  if(at>=beginning&&!trained){
   Object.assign(pretrain,{s1:core.summary(s).ruleDiscovery,
     s2:core.summary(s).lifecycle,s2Slow:core.summary(s).slowLifecycle,
     firstFebAsOf:iso(at)});
   trained=true;
  }
  if(t<beginning){trainBars++;} else if(t<endFeb){februaryBars++;}
  // Need event firstprint evidence and +60min delay; do not repeat on event-free bars.
  const active=ev.find(e=>at>=e.ts+3600000&&at<e.ts+4*3600000);
  const bar={barStartedAt:iso(t),asof:iso(at),priceAvailableAt:iso(at),
   barMinutes:15,price,priceSource:sourceId};
  if(active){bar.economicFeatures=active.features;macAnchors++;}
  const obs=core.observe(s,bar);
  // Date index is shifted by 2h, matching daily 22:00-UTC research roll, not a bank-hours rule.
  const d=iso(t+2*3600000).slice(0,10);
  if(d<"2023-02-01"||d>"2023-02-28")continue;
  const old=daily.get(d)??{date:d,n:0,firstPrice:null,lastPrice:null,eventSnapshot:null,summary:null};
  if(old.firstPrice===null)old.firstPrice=price;
  old.lastPrice=price;
  old.n++;
  if(active&&!seenEvents.has(active.id)){
   old.eventSnapshot={eventUTC:active.id,firstModelObservation:info(obs,iso(at),price),
     macroProvenance:"POST_RELEASE_LEDGER_2026_RECONSTRUCTED_PLUS_60_MIN_RESEARCH"};
   seenEvents.add(active.id);
  }
  old.summary=info(obs,iso(at),price);
  daily.set(d,old);
 }
 if(!trained||februaryBars<1300)throw Error("FEBRUARY_NOT_FULLY_READ");
 const result=Array.from({length:28},(_,i)=>{
  const date="2023-02-"+String(i+1).padStart(2,"0");
  const r=daily.get(date);
  if(!r)return {date,sessionStatus:"NO_OBSERVED_SESSION",ruleHypothesis:cases[date]??null};
  return {date,sessionStatus:r.n<86?"PARTIAL_OR_UNVERIFIED":"QUOTE_SESSION_OBSERVED",
   bars:r.n,ruleHypothesis:cases[date]??null,
   actualSessionFirstToLastPct:round(100*(r.lastPrice/r.firstPrice-1)),
   sameDayEconomicSnapshot:r.eventSnapshot,
   dayEndMetrics:r.summary};
 });
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",purpose:"FEB_2023_ECONOMIC_S1_S2_S3_DAILY_RESEARCH",
  sourceId,trainPeriod:"2022-10-01..2023-01-31",evaluation:"2023-02",
  trainBars,februaryBars,pretrain,
  assumptions:["no future labels at decisions","S1 four-hour horizon only","S2 fast and slow separated",
    "macro event retrospective, not certified initial print PIT",
    "rule hypotheses by economic news are NOT actual trained-ORG predictions",
    "not a bank transaction replay, no constrained bank hours"],
  observedMacroWaves:seenEvents.size,macroFeatureObservations:macAnchors,
  scienceGate:"NOT_PROVEN",tradeAllowed:false,
  rows:result,finalSummary:core.summary(s)};
}
if(require.main===module){
 const [a,b,c]=process.argv.slice(2);
 if(!a||!b||!c)throw Error("ARGS: M15_JSON SESSION_JSON MACRO_CSV");
 console.log(JSON.stringify(run(JSON.parse(fs.readFileSync(a,"utf8")),
  JSON.parse(fs.readFileSync(b,"utf8")),fs.readFileSync(c,"utf8")),null,2));
}
module.exports={run};
