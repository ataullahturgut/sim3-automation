"use strict";
/** Chronological GPT handoff + SHADOW-only portfolio auditor, never bank execution.
 *
 * 1. Do not turn post-2023 research archives into certified 2023 economic facts.
 * 2. Real GPT outputs must be supplied as immutable per-timestamp observations.
 *    No implicit GPT calls, fake GPT reasons, auto-approved economic predictions.
 * 3. Decisions execute at NEXT COMPLETED M15 bar BID/ASK proxy + .8% per leg.
 * 4. Time zone is UTC for timestamp math; "research day" rolls 22:00Z.
 * 5. Historical replay GPT output generated in 2026 is explicitly retrospective,
 *    even when its visible input slice is chronological.
 */
const crypto=require("node:crypto");
const VERSION="GOLD_AI_EVENT_MECHANISM_SHADOW_V1_20261017",FEE=0.008;
const iso=n=>new Date(n).toISOString();
const round=n=>Number.isFinite(n)?Math.round(n*1e5)/1e5:null;
const stamp=x=>{
 const n=Date.parse(x);
 if(typeof x!=="string"||!Number.isFinite(n)||!/(Z|[+-]\d\d:\d\d)$/.test(x))
  throw Error("GPT_PROTOCOL_OFFSET_AWARE_TIMESTAMP_REQUIRED");
 return n;
};
// Research day labels derive from the 15m bar START, not bar END:
// the final bar ending at 22:00Z still belongs to the departing session.
const dayAt=x=>iso(stamp(x)-900000+2*3600e3).slice(0,10);
const sha=o=>crypto.createHash("sha256").update(JSON.stringify(o)).digest("hex");
function portfolio(){
 return {cash:100,ounces:0,holding:"CASH",pending:null,transactions:[],
  lastValue:100,maxValue:100,maxDrawdownPct:0};
}
function newState({sourceId,firstAt,endAt,aiRecords=[]}){
 if(!sourceId||stamp(firstAt)>=stamp(endAt)||!Array.isArray(aiRecords))
  throw Error("GPT_PROTOCOL_INPUT");
 const byAt=new Map();
 for(const x of aiRecords){
  const t=stamp(x.asof),created=stamp(x.createdAt);
  if(t<stamp(firstAt)||t>=stamp(endAt)||byAt.has(t)||
    !["BUY","SELL","HOLD"].includes(x.action)||
    !["GPT_ARCHIVE_RETROSPECTIVE","GPT_PROSPECTIVE"].includes(x.provenance)||
    !x.responseId||typeof x.reason!=="string"||x.reason.length<30||
    !Array.isArray(x.mechanisms)||!Array.isArray(x.counterEvidence)||
    x.counterEvidence.length===0||x.mechanisms.length===0||
    !Number.isFinite(x.expectedNetAdvantagePct))
   throw Error("GPT_PROTOCOL_INVALID_OR_DUPLICATE_RECORD");
  if(x.provenance==="GPT_PROSPECTIVE"&&created>t)
   throw Error("GPT_PROTOCOL_FUTURE_GENERATED_OUTPUT_CANNOT_BE_PROSPECTIVE");
  byAt.set(t,x);
 }
 return {version:VERSION,sourceId,firstAt,endAt,lastBarTime:-Infinity,
  lastBarStart:-Infinity,byAt,seenAI:new Set(),
  memory:{active:new Map(),expired:0,quarantined:0},priorSessions:[],
  eventLog:[],attention:[],decisionLog:[],executionLog:[],
  portfolios:{CORE:portfolio(),AI:portfolio(),HYBRID:portfolio()},
  benchmark:{cash:100,ounces:0,bought:false},
  pendingEvent:false,prevPhase:null,prevDirection:null,lastPromptTime:-Infinity,
  lastDaily:null,latestSnapshot:null,checksum:"GENESIS",
  observations:0,sourceQuotes:0,aiSupplied:aiRecords.length,aiConsumed:0,
  modelApprovedTrades:0,aiPolicyTrades:0,hybridPolicyTrades:0};
}
function newEvent(s,e){
 if(!e||!e.id||!e.kind||!e.eventTime||!e.availableAt)throw Error("EVENT_PROVENANCE_REQUIRED");
 const t=stamp(e.eventTime),avail=stamp(e.availableAt);
 if(t>avail)throw Error("EVENT_AVAILABLE_BEFORE_ORIGIN");
 if(s.eventLog.some(z=>z.id===e.id))throw Error("DUPLICATE_EVENT_ID");
 const allowed=e.firstPrintVerified===true&&e.consensusVintageVerified===true;
 const item={id:e.id,kind:e.kind,eventTime:iso(t),availableAt:iso(avail),
   source:e.source||"ARCHIVE",researchOnly:!allowed,
   certification:allowed?"SOURCE_TIME_VERIFIED_ONLY_NOT_CAUSAL":"RECONSTRUCTED_RESEARCH_QUARANTINE",
   mechanismCandidates:e.mechanismCandidates||[],
   isVerifiedEconomicFeature:allowed};
 s.eventLog.push(item);
 if(!allowed)s.memory.quarantined++;
 // Note: it may not be visible to the historical decision yet.
 return item;
}
function updatePriceMark(p,bid){
 const value=p.cash+p.ounces*bid*(1-FEE);
 p.lastValue=value;p.maxValue=Math.max(p.maxValue,value);
 p.maxDrawdownPct=Math.max(p.maxDrawdownPct,100*(1-value/p.maxValue));
}
function queue(p,action,ctx){
 if(p.pending)throw Error("ONE_PENDING_ORDER_ONLY");
 p.pending={action,at:ctx.asof,rationale:ctx.reason,source:ctx.source};
}
function executePending(s,p,bid,ask,at,arm){
 const q=p.pending;
 if(!q)return;
 if(stamp(at)<=stamp(q.at))throw Error("EXECUTION_NOT_AFTER_DECISION");
 if(q.action==="BUY"&&p.holding==="CASH"){
  const amount=p.cash;
  p.ounces=amount*(1-FEE)/ask;p.cash=0;p.holding="GOLD";
 }else if(q.action==="SELL"&&p.holding==="GOLD"){
  p.cash=p.ounces*bid*(1-FEE);p.ounces=0;p.holding="CASH";
 }else throw Error("INVALID_SHADOW_POSITION_CHANGE");
 const tx={arm,action:q.action,decisionAt:q.at,executionAt:at,
  quoteType:q.action==="BUY"?"RECONSTRUCTED_VENDOR_ASK":"RECONSTRUCTED_VENDOR_BID",
  price:round(q.action==="BUY"?ask:bid),feePerLeg:FEE,
  executionModel:"FIRST_NEXT_COMPLETED_M15_CLOSE_PROXY_NOT_LIVE_BANK",
  rationale:q.rationale,source:q.source};
 p.transactions.push(tx);s.executionLog.push(tx);
 p.pending=null;
}
function onBar(s,{barStart,asof,bid,ask,snapshot,modelAction=null}){
 const start=stamp(barStart),t=stamp(asof),lastObservedBarStart=s.lastBarStart;
 if(s.version!==VERSION||t!==start+900000||t<=s.lastBarTime||
    start<=s.lastBarStart||!(bid>0)||!(ask>=bid))
  throw Error("BAR_CHRONOLOGY_OR_QUOTE");
 // For 2023 archive research, only completed-bar close proxies are available.
 // Existing CORE uses MID. Execution is first later completed bar proxy.
 if(t<stamp(s.firstAt)||t>=stamp(s.endAt))throw Error("BAR_OUTSIDE_EVALUATION");
 if(!snapshot||!snapshot.s1||!snapshot.s2||!snapshot.s3)
  throw Error("ACTUAL_CORE_SNAPSHOT_REQUIRED");
 s.lastBarTime=t;s.lastBarStart=start;s.observations++;s.sourceQuotes++;
 // Previous bar's orders execute BEFORE consuming current bar output.
 for(const [arm,p] of Object.entries(s.portfolios)){
  if(p.pending)executePending(s,p,bid,ask,iso(t),arm);
  updatePriceMark(p,bid);
 }
 if(!s.benchmark.bought){
  s.benchmark.ounces=s.benchmark.cash*(1-FEE)/ask;
  s.benchmark.cash=0;s.benchmark.bought=true;
  s.benchmark.buyAt=iso(t);s.benchmark.buyPrice=ask;
 }
 // Avoid treating soon-to-be-released news as already known.
 const available=s.eventLog.filter(e=>stamp(e.availableAt)<=t);
 const newly=available.filter(e=>!s.memory.active.has(e.id));
 for(const e of newly){
  s.memory.active.set(e.id,{...e,discoveredAt:iso(t),status:"ACTIVE_RESEARCH",
    evidenceLevel:e.researchOnly?"UNVERIFIED_ARCHIVE":"TIME_VERIFIED_NO_CAUSAL_PROOF"});
 }
 const clockDay=dayAt(iso(t));
 const firstDaily=clockDay!==s.lastDaily;
 if(firstDaily)s.lastDaily=clockDay;
 const phase=snapshot.s2.phase,direction=snapshot.s2.direction;
 const phaseChanged=s.prevPhase!==null&&
  (phase!==s.prevPhase||direction!==s.prevDirection)&&
  ["START","REENTRY","END"].includes(phase);
 s.prevPhase=phase;s.prevDirection=direction;
 const prev=s.latestSnapshot;
 const shock=prev&&start-lastObservedBarStart===900000&&
  Math.abs(100*((bid+ask)/(prev.bid+prev.ask)-1))>=0.5;
 s.latestSnapshot={barStart:iso(start),bid,ask};
 const wantsAttention=newly.length||firstDaily||shock||
  (phaseChanged&&t-s.lastPromptTime>=4*3600000);
 if(wantsAttention){
  const kinds=[...new Set([...(newly.length?["EVENT"]:[]),
   ...(firstDaily?["DAY_OPEN"]:[]),...(shock?["PRICE_WATCH"]:[]),
   ...(phaseChanged?["PHASE_CHANGE"]:[])])];
  const prompt={at:iso(t),day:clockDay,kinds,
   position:{AI:s.portfolios.AI.holding,HYBRID:s.portfolios.HYBRID.holding},
   events:available.map(z=>({id:z.id,kind:z.kind,availableAt:z.availableAt,
     evidenceStatus:z.certification,mechanismCandidates:z.mechanismCandidates})),
   s1:snapshot.s1,s2:snapshot.s2,
   s3:{researchAction:snapshot.s3.researchAction,tradeAllowed:false},
   priorCompletedSessions:s.priorSessions.slice(-5),
   marketQuote:{bid:round(bid),ask:round(ask),
    source:s.sourceId,time:iso(t),reconstructed:true},
   requiredResponse:["action","reason","mechanisms","counterEvidence",
    "expectedNetAdvantagePct","responseId","createdAt","provenance"],
   futureBarsVisible:false,bankExecutionAvailable:false};
  s.attention.push(prompt);s.lastPromptTime=t;
 }
 // MODEL arm: trade is impossible until the existing CORE itself explicitly
 // certifies a model trade; never map KEEP into a new shadow BUY.
 if(modelAction!==null)throw Error("MODEL_TRADE_NOT_AUTHORIZED_IN_RESEARCH_CORE");
 const submitted=s.byAt.get(t);
 if(submitted){
  if(!wantsAttention)throw Error("AI_SUBMISSION_WHEN_NO_TRIGGER");
  const asof=iso(t);s.seenAI.add(t);s.aiConsumed++;
  const activeIds=new Set(available.map(x=>x.id));
  if(submitted.mechanisms.some(id=>!id)||submitted.refEventIds?.some(id=>!activeIds.has(id)))
   throw Error("GPT_REFERENCED_FUTURE_OR_UNAVAILABLE_EVENT");
  const aiCanTrade=submitted.action!=="HOLD"&&
   submitted.expectedNetAdvantagePct>=(100*(1/(1-FEE)**2-1));
  let aiDecision="HOLD",hybridDecision="HOLD",reason="NO_NET_ADVANTAGE";
  if(aiCanTrade){
   const p=s.portfolios.AI;
   if(submitted.action==="BUY"&&p.holding==="CASH"||
      submitted.action==="SELL"&&p.holding==="GOLD"){
    aiDecision=submitted.action;
    queue(p,aiDecision,{asof,source:"SUPPLIED_GPT_RESEARCH",reason:submitted.reason});
    s.aiPolicyTrades++;
   }
   // Hybrid requires noncontradictory price phase and sufficient S1 evidence.
   const fast=snapshot.s2;
   const agrees=submitted.action==="BUY"&&fast.direction===1&&
     snapshot.s1.ready===true&&snapshot.s1.pUpPct>=50||
     submitted.action==="SELL"&&fast.direction===-1;
   const pH=s.portfolios.HYBRID;
   if(agrees&&(submitted.action==="BUY"&&pH.holding==="CASH"||
       submitted.action==="SELL"&&pH.holding==="GOLD")){
    hybridDecision=submitted.action;
    queue(pH,hybridDecision,{asof,
     source:"AI_PLUS_S1_S2_RESEARCH_HEURISTIC",reason:submitted.reason});
    s.hybridPolicyTrades++;
   }else reason="HYBRID_PRICE_CONFIRMATION_NOT_MET";
  }
  const audit={asof,aiAction:submitted.action,aiResearchOrder:aiDecision,
   hybridResearchOrder:hybridDecision,reason:submitted.reason,
   counterEvidence:submitted.counterEvidence,mechanisms:submitted.mechanisms,
   modelAction:null,coreTradeAllowed:false,source:submitted.provenance,
   responseId:submitted.responseId,createdAt:submitted.createdAt,
   expectedNetAdvantagePct:submitted.expectedNetAdvantagePct,
   paperOnly:true,scientificGate:"NOT_PROVEN",gatingReason:reason,
   evidenceHash:sha(s.attention.at(-1))};
  s.decisionLog.push(audit);
  s.checksum=sha([s.checksum,audit]);
 }
 return {at:iso(t),day:clockDay,attention:wantsAttention,
  kinds:wantsAttention?s.attention.at(-1).kinds:[],newEvents:newly.length,
  ai:s.portfolios.AI.holding,hybrid:s.portfolios.HYBRID.holding};
}
function completeSession(s,{day,sessionReturnPct,availableAt}){
 if(!/^\d{4}-\d\d-\d\d$/.test(day)||!Number.isFinite(sessionReturnPct)||
    stamp(availableAt)>s.lastBarTime)throw Error("FUTURE_OR_INVALID_DAILY_OUTCOME");
 if(s.priorSessions.length&&day<=s.priorSessions.at(-1).day)
  throw Error("DUPLICATE_OR_OUT_OF_ORDER_DAILY_SESSION");
 s.priorSessions.push({day,sessionReturnPct:round(sessionReturnPct),availableAt});
}
function finish(s,{endQuote,finalAt}){
 if(stamp(finalAt)<s.lastBarTime||!endQuote||!(endQuote.bid>0))
  throw Error("FINAL_PRICE_REQUIRED");
 for(const p of Object.values(s.portfolios))updatePriceMark(p,endQuote.bid);
 const baseline=s.benchmark.bought?
  s.benchmark.ounces*endQuote.bid*(1-FEE):100;
 const arms=Object.fromEntries(Object.entries(s.portfolios).map(([arm,p])=>
  [arm,{finalLiquidatableUSD:round(p.lastValue),
    pnlPct:round(p.lastValue-100),
    maxDrawdownPct:round(p.maxDrawdownPct),holding:p.holding,
    transactions:p.transactions.slice(),
    pendingNotFilled:p.pending!==null}]));
 return {version:VERSION,evalStart:s.firstAt,evalEnd:s.endAt,asof:finalAt,
  source:s.sourceId,feePerLeg:FEE,priceBasis:"VENDOR_BID_ASK_RECONSTRUCTED_PLUS_FEE",
  blindOOS:false,originalPITEventVerified:false,modelScienceAccepted:false,
  bankTradeAuthorized:false,gptRuntimeConnected:false,
  aiResultsGrounded:s.aiConsumed>0,
  aiStatus:s.aiConsumed?"GPT_ARCHIVE_RETROSPECTIVE_UNVALIDATED":
   "GPT_NOT_SUPPLIED_NO_AI_PORTFOLIO_PERFORMANCE_CLAIM",
  inputAICount:s.aiSupplied,aiUsed:s.aiConsumed,
  attentionCount:s.attention.length,activeEventCount:s.memory.active.size,
  quarantinedEconomicEvents:s.memory.quarantined,
  modelApprovedTrades:s.modelApprovedTrades,
  observations:s.observations,reference:{
    cashUSD:100,buyHoldLiquidatableUSD:round(baseline)},
  arms:arms,decisions:s.decisionLog,
  attention:s.attention,events:s.eventLog,
  auditHash:s.checksum};
}
module.exports={VERSION,newState,newEvent,onBar,completeSession,finish,dayAt};
