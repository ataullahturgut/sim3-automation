"use strict";
/**
 * 2023 JAN/FEB read-only full historical replay. Native core S1/S2/S3 + slow.
 * NO 2022 PRETRAIN. NO 2024/25 LEARNING. NO trades. No firstprint assumptions.
 * stdin: {"bars":[{bar_start_utc,bid_close,ask_close},...],
 *         "news":[{id,publisher,...},...],
 *         "registry":{sources:[...]}, "mechanismLibrary":{mechanisms:[...]},
 *         "researchProxyTags":{eventId:["Kxx",...]}}
 * Run from gold_axis_2026/adaptive_trading_core directory with node.
 */
const model=require("./adaptive_market_core_s1_s2");
const mechanism=require("./economic_mechanism_integrator_v1");
const MS15=15*60000,DAY=86400000;
const SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1";
function rnd(x,n=4){return x===null||!Number.isFinite(x)?null:+x.toFixed(n);}
function logret(p,base){return rnd(100*Math.log(p/base),5);}
function isReal(x){return typeof x==="number"&&Number.isFinite(x);}
function execute({bars,news,registry,mechanismLibrary,researchProxyTags={}}){
 if(!Array.isArray(bars)||!Array.isArray(news)||!registry?.sources||!mechanismLibrary?.mechanisms)throw Error("REPLAY_INPUT_CONTRACT");
 const state=model.create({sourceId:SOURCE,sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",
  learningMode:"DISCOVERY_FULL_ARCHIVE",shadowResearch:false,
  positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH"});
 const timeline=new Map(),sessions=[],stamps=[],closePrices=[];
 let lastBar=-Infinity,sessionRejected=0;
 for(let i=0;i<bars.length;i++){
  const b=bars[i],start=Date.parse(b.bar_start_utc),t=start+MS15;
  if(!Number.isFinite(start)||t<=lastBar||!isReal(+b.bid_close)||!isReal(+b.ask_close))throw Error("BAD_BAR_OR_ORDER");
  const mid=(+b.bid_close+ +b.ask_close)/2;
  if(mid<=0||+b.bid_close>+b.ask_close)throw Error("BAD_SPREAD");
  const asof=new Date(t).toISOString();
  const z=model.observe(state,{asof,barStartedAt:b.bar_start_utc,price:mid,priceAvailableAt:asof,barMinutes:15,priceSource:SOURCE});
  const s1=(z.ruleDiscovery.forecastAtDecision?.byHorizon??[]).find(x=>x.horizonMinutes===240)??null;
  const a={price:mid,asof,
    s1:s1?{ready:s1.ready,pUp:rnd(s1.upFraction,5),expected4hPct:rnd(s1.expectedLogPct,5),
     effectiveN:rnd(s1.effectiveN,2),uncertaintyPct:rnd(s1.uncertaintyPct,4)}:null,
    s2:{phase:z.lifecycle.phase,direction:z.lifecycle.direction,trendZ:rnd(z.lifecycle.trendZ,4)},
    s3:{research:z.positionResearch.proposedResearchAction,reason:z.positionResearch.researchDecisionReason},
    liveAction:z.action};
  timeline.set(t,a);closePrices.push({t,price:mid});
  stamps.push(t);lastBar=t;
  if(asof.endsWith("T22:00:00.000Z")){
   const label=asof.slice(0,10),dow=new Date(label+"T00:00:00Z").getUTCDay();
   if(dow>=1&&dow<=5){
    const slice=bars.slice(Math.max(0,i-110),i+1).filter(x=>{
     const t0=Date.parse(x.bar_start_utc)+MS15;
     return t0>t-DAY&&t0<=t;
    });
    let maxgap=0;for(let k=1;k<slice.length;k++)maxgap=Math.max(maxgap,
     (Date.parse(slice[k].bar_start_utc)-Date.parse(slice[k-1].bar_start_utc))/60000);
    const session={session:label,source_id:SOURCE,close_price:mid,n:slice.length,
     max_gap_minutes:maxgap,first_bar:slice[0].bar_start_utc,last_bar:slice[slice.length-1].bar_start_utc,
     valid_quotes:slice.length,terminal_bar_valid:true,
     sessionEvidence:"BIDASK_M15_RECONSTRUCTED_NOT_M1",availableAt:asof};
    const slow=model.observeSlowSession(state,session);
    if(slow.phase==="REJECTED_SESSION")sessionRejected++;
    sessions.push({session:label,utcClose:asof,price:rnd(mid),
     n:slice.length,s2Slow:slow.phase,
     s1:a.s1,s2:a.s2,s3:a.s3,liveAction:null,tradeAllowed:false});
   }
  }
 }
 function continuous(a,b){
  if(!timeline.has(a)||!timeline.has(b)||b<a||(b-a)%MS15!==0)return false;
  for(let x=a+MS15;x<=b;x+=MS15)if(!timeline.has(x))return false;
  return true;
 }
 function checked(a,b){
  if(!continuous(a,b))return null;
  return logret(timeline.get(b).price,timeline.get(a).price);
 }
 const newsTimeline=news.map(n=>{
  const t=Date.parse(n.eventTime),checkpoints=[];
  for(const h of [15,60,240]){
   const at=t+h*60000,cell=timeline.get(at),basis=timeline.get(t);
   const asof=new Date(at).toISOString();
   const mr=mechanism.integrate({news,registry,mechanismLibrary,
     asof,completedBars:bars,marketEvidence:[]});
   const ev=mr.events.find(x=>x.id===n.id);
   const future4h=checked(at,at+240*60000),before4h=checked(t-240*60000,t);
   const observed=checked(t,at);
   const beyond60=checked(at,at+60*60000);
   checkpoints.push({horizonMinutesSinceRelease:h,at:asof,
    priceBarExists:!!cell,pricePathComplete:observed!==null,
    eventLogReturnPct:observed,preEvent4hLogReturnPct:before4h,
    globalS2:cell?.s2??null,baselineS1_4hForecast:cell?.s1??null,
    S3_Research:cell?.s3??null,
    future60Pct_LABEL_ONLY:beyond60,
    future240Pct_LABEL_ONLY:future4h,
    K_verifiedStrict:ev?.conditions??[],
    conditionPatternsStrict:ev?.matchedPatterns?.map(p=>p.id)??[],
    candidateOrgsStrict:ev?.mechanisms?.map(m=>m.org)??[],
    mechanismEvidenceStatus:ev?.mechanisms?.map(m=>m.status)??[],
    researchProxyTagsNotCertified:researchProxyTags[n.id]??[],
    firstprintCertified:ev?.firstprintAttested===true,
    causalProof:"NOT_ESTABLISHED",realTradeAllowed:false});
  }
  return {id:n.id,source:n.publisher,eventKind:n.eventKind,jurisdiction:n.jurisdiction,
   releaseUtc:n.eventTime,macroProxyNotPITCertified:researchProxyTags[n.id]??[],
   checkpoints};
 });
 const a=model.summary(state),first=closePrices[0]?.price,last=closePrices.at(-1)?.price;
 const no2022Pretraining=true;
 const outcomes={
  firstObservedAt:closePrices.length?new Date(closePrices[0].t).toISOString():null,
  lastObservedAt:closePrices.length?new Date(closePrices.at(-1).t).toISOString():null,
  bars:closePrices.length,sessions:sessions.length,sessionRejected,firstPrice:rnd(first),lastPrice:rnd(last),
  S1:a.ruleDiscovery,
  S2:{phases:a.lifecycle?.phaseCounts??null},
  S3:{audit:{economicRulesCertifiedAtDecision:a.positionResearch.audit.economicRulesCertifiedAtDecision,
    shadowTrades:a.positionResearch.audit.shadowTrades,
    decisionsByReason:a.positionResearch.audit.decisionsByReason},
    activeResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",
    cashPortfolioFinalUsd:100,passiveGoldLiquidatableFinalUsd:rnd(100*(last/first)*(.992**2),5)},
  comparison:{prior2022PretrainingUsed:false,S1_2023_FreshStart:true,
    economic2023FirstprintAccepted:false,liveEconomicFeaturesInjected:false}
 };
 const scored=newsTimeline.flatMap(n=>n.checkpoints.map(q=>({...q,id:n.id}))).filter(x=>x.horizonMinutesSinceRelease===60);
 const stats={
  eventCount:newsTimeline.length,
  withMacroVerified:scored.filter(x=>x.K_verifiedStrict.length>0).length,
  atOneHour:{
   n:scored.length,up:scored.filter(x=>x.eventLogReturnPct>0).length,
   down:scored.filter(x=>x.eventLogReturnPct<0).length,
   absOver1Pct:scored.filter(x=>x.eventLogReturnPct!==null&&Math.abs(x.eventLogReturnPct)>=1).length,
   baselineS2_nonzero:scored.filter(x=>x.globalS2?.direction!==0&&x.globalS2).length,
   baselineS2_neutral:scored.filter(x=>x.globalS2?.direction===0).length
  },
  strictFirstprintCount:0,
  noAlphaOrOrders:true
 };
 return {version:"GOLD_UNIFIED_JANFEB2023_FULL_HISTORIC_METRIC_REPLAY_V1",
  originalModules:true,originSafeness:"ONLY_2023_PAST_PRICES_NO_2022_PRETRAIN_NO_2024_2025_TRAIN",
  limitations:["Macros K strict requires independent historical consensus firstprint; research proxy labels NOT injected into model.",
   "No automatic worldwide news completeness claim; eight curated economic headlines only.",
   "Future +60/+240 columns are EVALUATION LABELS, never decision features.",
   "Native 2023 cold-start core S1/S2/S3 has no actual economic feature wiring.",
   "Event overlapping windows are not independent samples or causal attribution."],
  stats,outcomes,sessions,newsTimeline,tradeAllowed:false};
}
module.exports={execute,SOURCE};
if(require.main===module){
 const fs=require("node:fs");
 process.stdout.write(JSON.stringify(execute(JSON.parse(fs.readFileSync(0,"utf8"))),null,2)+"\n");
}
