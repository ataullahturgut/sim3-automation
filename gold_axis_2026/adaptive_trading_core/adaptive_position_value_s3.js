"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / S3 position-value critic, same S1+S2 CORE.
 * Off-policy tabular bootstrapped action values Q(state,position,KEEP/SWITCH),
 * updated only from the subsequent *completed* M15 close. Counterfactuals are
 * accounting identities, not hindsight-optimal trades. Realized future returns
 * never enter an earlier decision. S3 is DEVELOPMENT / RESEARCH ONLY:
 * not firstprint PIT, not OOS-accepted, not an AL-SAT authorization.
 *
 * Every bank buy/sell incurs 0.8% of bank-side wealth, MID proxy research.
 * No intraday bank quotation verification and no margin/leverage.
 */
const memory=require("./adaptive_position_memory_s3");
const longCycle=require("./adaptive_long_cycle_s3");
const opportunity=require("./adaptive_opportunity_learning_s3");
const conditional=require("./adaptive_conditional_position_s3");
const VERSION="KAVIS_S3_POSITION_VALUE_CRITIC_R2_20261016";
const FEE_PER_LEG=0.008, STEP=15*60*1000;
const HOLDINGS=["CASH","GOLD"],ACTIONS=["KEEP","SWITCH"];
const clone=x=>JSON.parse(JSON.stringify(x));
const finite=x=>typeof x==="number"&&Number.isFinite(x);
function ms(s){if(typeof s!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/i.test(s)||
 !Number.isFinite(Date.parse(s)))throw Error("S3_OFFSET_TIME_REQUIRED");return Date.parse(s);}
function create({sourceRegistry,learningMode="DISCOVERY_FULL_ARCHIVE",
 shadowEnabled=false,minUpdates=32,positionResearchMode="LEGACY_M15"}={}){
 if(!sourceRegistry||!Object.keys(sourceRegistry).length||
  Object.values(sourceRegistry).some(v=>v?.kind!=="MARKET"||
   !["RECONSTRUCTED_MARKET_ASOF","SYNTHETIC_ONLY","VERIFIED_PIT"].includes(v.evidenceStatus)))
  throw Error("S3_SOURCE_EVIDENCE_INVALID");
 if(!["DISCOVERY_FULL_ARCHIVE","STRICT_WALK_FORWARD"].includes(learningMode))
  throw Error("S3_BAD_LEARNING_MODE");
 if(!Number.isInteger(minUpdates)||minUpdates<16)throw Error("S3_MIN_SUPPORT");
 if(!["LEGACY_M15","MULTI_SESSION_RESEARCH","INTEGRATED_LONG_RESEARCH",
  "OPPORTUNITY_MATURED_RESEARCH","CONDITIONAL_ECONOMIC_RESEARCH"].includes(positionResearchMode))
  throw Error("S3_POSITION_POLICY_MODE_INVALID");
 return {version:VERSION,mode:learningMode,registry:clone(sourceRegistry),
  config:{feePerLeg:FEE_PER_LEG,gamma:0.998,minUpdates,positionResearchMode},
  sessionMemory:memory.create(),longCycle:longCycle.create(),
   opportunity:opportunity.create(),conditional:conditional.create(),lastS1Evidence:null,
  lastDownsideResearch:null,
  q:{},last:null,audit:{bars:0,updates:0,gaps:0,sourceBreaks:0,
   proposed:0,abstained:0,shadowTrades:0,
   decisionsByReason:{},s1ResearchForecastReceived:0,
   queuedOrders:0,executedNextBar:0,canceledOrders:0,longModeEvaluations:0,
   economicRulesCertifiedAtDecision:0,multiSessionResearchEvaluations:0,
   downsideResearchFrames:0,downsideEarlyAlerts:0},
  paper:{enabled:!!shadowEnabled,valid:true,invalidReason:null,
   cash:100,goldOunces:0,holding:"CASH",pendingOrder:null,
   firstPrice:null,lastPrice:null,
   buyHoldOunces:0,equityPeak:100,maxDrawdownPct:0,
   buyCount:0,sellCount:0,fees:0}};
}
function bucket(phase,dir){
 const p=String(phase??"UNKNOWN");
 const cls=["START","CONTINUE","REENTRY"].includes(p)?"TREND":
  p==="PULLBACK"?"PULLBACK":p==="END"?"END":
  p==="NEUTRAL"?"NEUTRAL":"UNREADY";
 return cls+":"+(dir===1?"UP":dir===-1?"DOWN":"NONE");
}
function context({fast,slow}={}){
 if(!fast||typeof fast!=="object")throw Error("S3_PHASE_INPUT_REQUIRED");
 // No date/event ID, no future label and no manual direction=BUY rule.
 const f=bucket(fast.phase,fast.direction);
 // Slow WARMUP is missing evidence, NOT a bearish/neutral regime and NOT
 // grounds to block an otherwise qualified fast-only research decision.
 const slowReady=slow&&!["WARMUP","REJECTED_SESSION","GAP"].includes(slow.phase);
 const l=slowReady?bucket(slow.phase,slow.direction):"NO_SLOW";
 return l+"|"+f;
}
function record(s,k){return s.q[k]??(s.q[k]={value:0,visits:0,meanTdSquare:0});}
function key(c,h,a){return c+"#"+h+"#"+a;}
function value(s,c,h,a){return s.q[key(c,h,a)]?.value??0;}
function wealthMultiplier(holding,action,gross){
 if(!HOLDINGS.includes(holding)||!ACTIONS.includes(action)||!finite(gross)||gross<=0)
  throw Error("S3_BAD_COUNTERFACTUAL");
 if(holding==="CASH")return action==="KEEP"?1:(1-FEE_PER_LEG)*gross;
 return action==="KEEP"?gross:1-FEE_PER_LEG;
}
function nextHolding(h,a){return a==="KEEP"?h:(h==="CASH"?"GOLD":"CASH");}
function update(s,previous,next,gross){
 // Use all four accounting outcomes on the now-matured bar, NEVER at issue.
 const bootstrap={};
 for(const h of HOLDINGS)bootstrap[h]=Math.max(value(s,next,h,"KEEP"),value(s,next,h,"SWITCH"));
 for(const h of HOLDINGS)for(const a of ACTIONS){
  const k=key(previous,h,a),r=record(s,k),nh=nextHolding(h,a);
  const target=Math.log(wealthMultiplier(h,a,gross))+s.config.gamma*bootstrap[nh];
  const error=target-r.value,step=1/Math.sqrt(r.visits+1);
  r.value+=Math.min(.2,step)*error;
  r.visits++;
  r.meanTdSquare+=((error*error)-r.meanTdSquare)/r.visits;
 }
 s.audit.updates++;
}
function paperNet(s,price){
 return s.paper.cash+s.paper.goldOunces*price*(1-FEE_PER_LEG);
}
function paperBaseline(s,price){
 return s.paper.buyHoldOunces*price*(1-FEE_PER_LEG);
}
function paperTrade(s,action,price){
 if(!s.paper.enabled||!s.paper.valid)return;
 if(action==="BUY"&&s.paper.holding==="CASH"){
  s.paper.fees+=s.paper.cash*FEE_PER_LEG;
  s.paper.goldOunces=s.paper.cash*(1-FEE_PER_LEG)/price;
  s.paper.cash=0;s.paper.holding="GOLD";s.paper.buyCount++;s.audit.shadowTrades++;
 }else if(action==="SELL"&&s.paper.holding==="GOLD"){
  const gross=s.paper.goldOunces*price;
  s.paper.fees+=gross*FEE_PER_LEG;
  s.paper.cash=gross*(1-FEE_PER_LEG);s.paper.goldOunces=0;
  s.paper.holding="CASH";s.paper.sellCount++;s.audit.shadowTrades++;
 }
}
function observe(s,o){
 if(s.version!==VERSION)throw Error("S3_BAD_CHECKPOINT_VERSION");
 if(!o||!finite(o.price)||o.price<=0||o.barMinutes!==15||
  !s.registry[o.sourceId]||!o.fast||
  ["futureReturn","futurePrice","oracle","target","label","optimalAction"].some(k=>k in o))
  throw Error("S3_INVALID_OR_FUTURE_INPUT");
 const t=ms(o.asof),available=ms(o.priceAvailableAt);
 if(available>t)throw Error("S3_PRICE_NOT_YET_AVAILABLE");
 if(s.last&&t<=s.last.t)throw Error("S3_NONMONOTONIC");
 if(s.mode==="STRICT_WALK_FORWARD"&&s.registry[o.sourceId].evidenceStatus!=="VERIFIED_PIT"&&
  s.registry[o.sourceId].evidenceStatus!=="SYNTHETIC_ONLY")
  throw Error("S3_RECONSTRUCTED_PRICE_NOT_STRICT_PIT");
 let c=context({fast:o.fast,slow:o.slow});
 if(o.downsideEvidence!==undefined){
  const d=o.downsideEvidence;
  if(!d||d.asof!==o.asof||
    !["NO_ALERT","WARMUP","EARLY_WEAKNESS","CONFIRMED_FALL"].includes(d.phase)||
    !Array.isArray(d.linkedNewsIds)||!Number.isInteger(d.firstprintNewsCount)||
    d.firstprintNewsCount<0||d.causalAttribution!=="UNPROVEN"||
    (d.firstPriceWeaknessAt!==null&&ms(d.firstPriceWeaknessAt)>t))
    throw Error("S3_BAD_DOWNSIDE_RESEARCH_PROVENANCE");
  s.lastDownsideResearch=clone(d);
  s.audit.downsideResearchFrames=(s.audit.downsideResearchFrames||0)+1;
  if(["EARLY_WEAKNESS","CONFIRMED_FALL"].includes(d.phase))
   s.audit.downsideEarlyAlerts=(s.audit.downsideEarlyAlerts||0)+1;
  // No change to Q state or BUY/SELL. Review is not a trading command.
 }
 // A genuine S1 forecast (not manually recoded direction). Retain evidence,
 // do not promote research-only predictions to certified macro alpha.
 if(o.s1Evidence!==undefined){
  const e=o.s1Evidence;
  if(!e||e.asof!==o.asof||!Array.isArray(e.byHorizon)||
     !["MARKET_ONLY_UNVALIDATED","RESEARCH_MACRO_UNVERIFIED",
       "VERIFIED_PIT_BUT_ALPHA_NOT_PROVEN"].includes(e.provenance)||
     e.byHorizon.some(x=>!Number.isInteger(x.horizonMinutes)||
       (x.ready&&(!finite(x.expectedLogPct)||!Number.isInteger(x.effectiveN)&&
                 !(finite(x.effectiveN)&&x.effectiveN>=0)))))
    throw Error("S3_INVALID_S1_EVIDENCE");
  s.lastS1Evidence=clone(e);
  s.audit.s1ResearchForecastReceived++;
  // Firstprint evidence certification is not economic-ALPHA certification.
  if(e.provenance!=="MARKET_ONLY_UNVALIDATED"){
   s.audit.researchEconomicContexts=(s.audit.researchEconomicContexts||0)+1;
   const pred=e.byHorizon.find(x=>x.horizonMinutes===240&&x.ready&&
      finite(x.expectedLogPct)&&finite(x.effectiveN)&&x.effectiveN>=8);
   // This is a learnt STATE descriptor (never an explicit BUY rule).
   // An unsupported economic rule gets its own UNKNOWN slot.
   c+="|S1_ECON:"+(pred?(pred.expectedLogPct>0?"UP":"DOWN"):"UNREADY");
  }
 }
 let contiguous=false;
 if(s.last){
  contiguous=t-s.last.t===STEP&&s.last.sourceId===o.sourceId;
  if(!contiguous)s.audit.gaps++;
  if(s.last.sourceId!==o.sourceId){
   s.audit.sourceBreaks++;
   s.paper.valid=false;s.paper.invalidReason="UNCOMPARABLE_SOURCE_CHANGE";
  }
  if(contiguous)update(s,s.last.context,c,o.price/s.last.price);
 }
 // Research execution must use a price OBSERVED AFTER the signal.
 // No assumed bank business hours; cancel stale orders across gaps / feeds.
 if(["INTEGRATED_LONG_RESEARCH","OPPORTUNITY_MATURED_RESEARCH","CONDITIONAL_ECONOMIC_RESEARCH"].includes(s.config.positionResearchMode)&&
    s.paper.pendingOrder){
   const order=s.paper.pendingOrder;s.paper.pendingOrder=null;
   if(contiguous&&s.paper.valid&&s.paper.enabled&&order.sourceId===o.sourceId
      &&order.issuedAt<t){
     paperTrade(s,order.side,o.price);s.audit.executedNextBar++;
   }else s.audit.canceledOrders++;
 }
 s.audit.bars++;
 if(s.paper.firstPrice===null){
  s.paper.firstPrice=o.price;
  s.paper.buyHoldOunces=100*(1-FEE_PER_LEG)/o.price;
 }
 const opportunityResearch=opportunity.observeCandidate(s.opportunity,{
    at:o.asof,price:o.price,sourceId:o.sourceId,fast:o.fast,slow:o.slow,
    s1Evidence:o.s1Evidence});
 const h=s.paper.holding;
 const conditionalResearch=conditional.observe(s.conditional,{at:o.asof,price:o.price,
   sourceId:o.sourceId,fast:o.fast,s1Evidence:o.s1Evidence,holding:h});
 const keep=s.q[key(c,h,"KEEP")],sw=s.q[key(c,h,"SWITCH")];
 // Correlated M15 updates are NOT independent episodes or a science PASS.
 const enough=!!(keep&&sw&&keep.visits>=s.config.minUpdates&&
  sw.visits>=s.config.minUpdates);
 const ready=contiguous&&enough&&s.paper.valid&&
  !c.includes("UNREADY");
 let proposed="ABSTAIN",reason;
 if(!contiguous)reason="INCOMPLETE_BAR_OR_GAP";
 else if(c.includes("UNREADY"))reason="FAST_PHASE_NOT_READY";
 else if(!s.paper.valid)reason="SOURCE_PRICE_NOT_COMPARABLE";
 else if(!enough)reason="ACTION_VALUE_SUPPORT_INSUFFICIENT";
 else{
  proposed=sw.value>keep.value?
   (h==="CASH"?"BUY":"SELL"):"KEEP";
  reason=proposed==="KEEP"?"LEARNED_KEEP_GREATER_OR_EQUAL":"LEARNED_SWITCH_GREATER";
 }
 // Long-horizon shadow ablation is possible ONLY from prior, matured
 // sessions with net buy+sell fee and fixed 5-session support, not hindsight.
 // It is never a live signal. Baseline 15m Q remains separately testable.
 const sessionState=s.sessionMemory.last?.state??"NO_SLOW:NONE";
 const longValue=memory.forecast(s.sessionMemory,sessionState);
 // Never impose an invented BANK_HOUR trading gate. All accepted,
 // time-stamped market observations may be evaluated in research.
 // Actual executable bank quote/venue availability remains unverified.
 const longFive=longValue.byHorizon.find(x=>x.sessions===5);
 if(s.config.positionResearchMode==="MULTI_SESSION_RESEARCH"){
   if(!ready){/* Keep strict fast/evidence gate, no fallback. */}
   else{
     s.audit.multiSessionResearchEvaluations++;
     if(!longFive.ready){proposed="ABSTAIN";reason="MATURED_SESSION_SUPPORT_INSUFFICIENT";}
     else if(h==="CASH"){
       proposed=longFive.conservativeLowerPct>0?"BUY":"KEEP";
       reason=proposed==="BUY"?"MATURED_5_SESSION_NET_ADVANTAGE_RESEARCH":
         "MATURED_5_SESSION_NOT_CONVINCING";
     }else{
       proposed=longFive.netGoldVsCashLogPct<0&&
        longFive.netGoldVsCashLogPct+1.96*longFive.stderrPct<0?"SELL":"KEEP";
       reason=proposed==="SELL"?"MATURED_5_SESSION_NET_DISADVANTAGE_RESEARCH":
        "MATURED_5_SESSION_HOLD_OR_UNCERTAIN";
     }
   }
 }
 let longResearch=null;
 if(s.config.positionResearchMode==="INTEGRATED_LONG_RESEARCH"){
   s.audit.longModeEvaluations++;
   longResearch=longCycle.action(s.longCycle,s.paper.holding);
   if(!contiguous||!s.paper.valid||c.includes("UNREADY")){
     proposed="ABSTAIN";
     reason=!contiguous?"LONG_BAR_GAP":!s.paper.valid?
      "LONG_UNCOMPARABLE_SOURCE":"LONG_FAST_PHASE_NOT_READY";
   }else if(!s.longCycle.last||t-s.longCycle.last.t>5*86400000){
     proposed="ABSTAIN";reason="LONG_MEMORY_STALE";
   }else{
     proposed=longResearch.action;
     reason=longResearch.reason;
   }
 }
 // Optional same-CORE fee-net opportunity evidence ablation.
 // This DOES NOT certify net liquidation value or use future labels.
 if(s.config.positionResearchMode==="OPPORTUNITY_MATURED_RESEARCH"){
  const f=opportunityResearch.forecast;
  if(!contiguous||!s.paper.valid||c.includes("UNREADY")){
   proposed="ABSTAIN";reason="OPPORTUNITY_SOURCE_OR_PHASE_NOT_READY";
  }else if(!opportunityResearch.candidate){
   proposed="KEEP";reason="OPPORTUNITY_NO_NEW_EPISODE";
  }else if(h==="CASH"&&o.fast.direction===1){
   proposed=f.learnedResearchPreference==="GOLD_ENTRY_CANDIDATE"?"BUY":"KEEP";
   reason=proposed==="BUY"?"OPPORTUNITY_MATURED_NET_UPSIDE":
     "OPPORTUNITY_NO_SUPPORTED_NET_ENTRY";
  }else if(h==="GOLD"&&o.fast.direction===-1){
   const downside=f.byHorizon.filter(x=>
    [5,10].includes(x.horizonSessions)&&x.supportReady&&
    x.selected.meanNetLogPct+x.selected.stderrPct<0);
   proposed=downside.length?"SELL":"KEEP";
   reason=proposed==="SELL"?"OPPORTUNITY_MATURED_DOWNSIDE_PROXY":
    "OPPORTUNITY_NO_CONFIRMED_EXIT";
  }else {proposed="KEEP";reason="OPPORTUNITY_MAINTAIN_POSITION";}
 }
 if(s.config.positionResearchMode==="CONDITIONAL_ECONOMIC_RESEARCH"){
  // An S1 4h alpha forecast may be UNREADY while a separately matured
  // conditional 5/10/20-session S3 cohort is available. Do not veto it.
  const fastUnready=!["START","CONTINUE","PULLBACK","END","REENTRY","NEUTRAL"].includes(o.fast.phase);
  if(!contiguous||!s.paper.valid||fastUnready){
   proposed="ABSTAIN";reason=!contiguous?"CONDITIONAL_BAR_GAP":
     !s.paper.valid?"CONDITIONAL_SOURCE_INVALID":"CONDITIONAL_PHASE_UNREADY";
  }else{
   proposed=conditionalResearch.actionCandidate;
   reason=conditionalResearch.reason;
  }
 }
 if(proposed==="ABSTAIN")s.audit.abstained++;
 else s.audit.proposed++;
 s.audit.decisionsByReason[reason]=(s.audit.decisionsByReason[reason]||0)+1;
 // Shadow simulation is optional and NEVER changes the real portfolio.
 if(["INTEGRATED_LONG_RESEARCH","OPPORTUNITY_MATURED_RESEARCH","CONDITIONAL_ECONOMIC_RESEARCH"].includes(s.config.positionResearchMode)){
   if(s.paper.enabled&&proposed!=="ABSTAIN"&&proposed!=="KEEP"&&
       s.paper.pendingOrder===null&&s.paper.valid){
     s.paper.pendingOrder={side:proposed,issuedAt:t,sourceId:o.sourceId};
     s.audit.queuedOrders++;
   }
 }else if(s.paper.enabled&&ready&&proposed!=="KEEP")
   paperTrade(s,proposed,o.price);
 s.paper.lastPrice=o.price;
 if(s.paper.valid){
  const net=paperNet(s,o.price);
  s.paper.equityPeak=Math.max(s.paper.equityPeak,net);
  s.paper.maxDrawdownPct=Math.max(s.paper.maxDrawdownPct,
   100*(1-net/s.paper.equityPeak));
 }
 s.last={t,price:o.price,context:c,sourceId:o.sourceId};
 s.lastProposedResearchAction=proposed;
 return {at:o.asof,context:c,holding:h,proposedResearchAction:proposed,
  qKeep:enough?keep.value:null,qSwitch:enough?sw.value:null,
  updateCount:s.audit.updates,readyForResearchComparison:ready,
  researchDecisionReason:reason,
  s1ResearchEvidence:s.lastS1Evidence?{provenance:s.lastS1Evidence.provenance,
    byHorizon:s.lastS1Evidence.byHorizon}:null,
  multiSessionResearch:{state:sessionState,fiveSession:longFive,
     policyMode:s.config.positionResearchMode,
     quoteAccepted:true,executionVenueCertified:false},
  longCycleResearch:longResearch,opportunityResearch,conditionalResearch,
  downsideResearch:s.lastDownsideResearch?{
    phase:s.lastDownsideResearch.phase,
    firstPriceWeaknessAt:s.lastDownsideResearch.firstPriceWeaknessAt,
    linkedNewsIds:s.lastDownsideResearch.linkedNewsIds,
    positionReview:s.lastDownsideResearch.phase==="CONFIRMED_FALL"?
      "REVIEW_EXISTING_GOLD_EXPOSURE_NO_ORDER":"NO_DOWNSIDE_REVIEW",
    tradeAllowed:false}:null,
  nextObservedBarResearchOrder:s.paper.pendingOrder?
   clone(s.paper.pendingOrder):null,
  action:null,tradeAllowed:false,scienceGate:"NOT_PROVEN"};
}
function summary(s){
 const price=s.paper.lastPrice;
 return {version:VERSION,mode:s.mode,
  feePerLeg:s.config.feePerLeg,roundTripFraction:1-(1-FEE_PER_LEG)**2,
  criticStates:Object.keys(s.q).length,
  audit:clone(s.audit),portfolio:{
    status:"SHADOW_ONLY_NEVER_LIVE",
    shadowEnabled:s.paper.enabled,valid:s.paper.valid,
    invalidReason:s.paper.invalidReason,
    shadowTrades:s.audit.shadowTrades,
    cashHolding:s.paper.holding,
    liquidatableNetUsd:s.paper.enabled&&s.paper.valid&&price!==null?
     paperNet(s,price):null,
    passiveGoldNetUsd:s.paper.valid&&price!==null?paperBaseline(s,price):null,
    passiveCashNetUsd:100,
    maxDrawdownPct:s.paper.enabled&&s.paper.valid?s.paper.maxDrawdownPct:null,
    feeUsdShadow:s.paper.enabled?s.paper.fees:null
  },positionMemory:memory.summary(s.sessionMemory),
   opportunityMemory:opportunity.summary(s.opportunity),
   conditionalPositionMemory:conditional.summary(s.conditional),
   longCycleMemory:longCycle.summary(s.longCycle),
   lastS1Evidence:s.lastS1Evidence?clone(s.lastS1Evidence):null,
   scienceGate:"NOT_PROVEN",liveTradeAuthorized:false,
  limitations:["RECONSTRUCTED_MID_NOT_BANK_EXECUTION_QUOTES",
    "15MIN_TRANSITIONS_CORRELATED_NOT_INDEPENDENT_EVIDENCE",
    "S1_S2_ALPHA_NOT_PROVEN","NO_BLIND_OOS_BACKTEST"]};
}
function checkpoint(s){return clone(s);}
function restore(data){
 const s=clone(data);
 if(s.version!==VERSION||!s.q||!s.paper||!s.registry||!s.audit||
    !s.sessionMemory||!s.longCycle)
  throw Error("S3_BAD_CHECKPOINT");
 s.sessionMemory=memory.restore(s.sessionMemory);
 s.longCycle=longCycle.restore(s.longCycle);
 // Legacy checkpoints have no opportunity state; never invent previous learning.
 s.opportunity=s.opportunity?opportunity.restore(s.opportunity):opportunity.create();
 s.conditional=s.conditional?conditional.restore(s.conditional):conditional.create();
 return s;
}
function observeCompletedSession(s,session){
 if(s.version!==VERSION)throw Error("S3_BAD_CHECKPOINT_VERSION");
 if(!s.registry[session.sourceId])throw Error("S3_UNREGISTERED_SESSION_SOURCE");
 const updated=memory.completed(s.sessionMemory,session);
 const opportunityUpdate=opportunity.closeSession(s.opportunity,{
  session:session.session,sourceId:session.sourceId,price:session.price,
  availableAt:session.availableAt});
 const conditionalUpdate=conditional.completedSession(s.conditional,{
   session:session.session,sourceId:session.sourceId,price:session.price,
   availableAt:session.availableAt});
 const outcome=longCycle.observe(s.longCycle,{...session,
    shadowHolding:s.paper.holding,
    shadowProposal:s.lastProposedResearchAction??"KEEP"});
 return {...updated,longCycle:outcome,opportunity:opportunityUpdate,
   conditional:conditionalUpdate};
}
module.exports={VERSION,FEE_PER_LEG,create,observe,observeCompletedSession,
 summary,checkpoint,restore,
 wealthMultiplier,context};
