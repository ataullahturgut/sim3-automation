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
const VERSION="KAVIS_S3_POSITION_VALUE_CRITIC_20261016";
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
 if(!["LEGACY_M15","MULTI_SESSION_RESEARCH"].includes(positionResearchMode))
  throw Error("S3_POSITION_POLICY_MODE_INVALID");
 return {version:VERSION,mode:learningMode,registry:clone(sourceRegistry),
  config:{feePerLeg:FEE_PER_LEG,gamma:0.998,minUpdates,positionResearchMode},
  sessionMemory:memory.create(),lastS1Evidence:null,
  q:{},last:null,audit:{bars:0,updates:0,gaps:0,sourceBreaks:0,
   proposed:0,abstained:0,shadowTrades:0,
   decisionsByReason:{},s1ResearchForecastReceived:0,
   economicRulesCertifiedAtDecision:0,multiSessionResearchEvaluations:0},
  paper:{enabled:!!shadowEnabled,valid:true,invalidReason:null,
   cash:100,goldOunces:0,holding:"CASH",firstPrice:null,lastPrice:null,
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
 s.audit.bars++;
 if(s.paper.firstPrice===null){
  s.paper.firstPrice=o.price;
  s.paper.buyHoldOunces=100*(1-FEE_PER_LEG)/o.price;
 }
 const h=s.paper.holding;
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
 const trHour=(new Date(t).getUTCHours()+3)%24+
  new Date(t).getUTCMinutes()/60; // Europe/Istanbul since 2016: UTC+03
 const trWeekday=new Date(t+3*3600000).getUTCDay();
 const bankWindow=trWeekday>=1&&trWeekday<=5&&trHour>=9&&trHour<=17;
 const longFive=longValue.byHorizon.find(x=>x.sessions===5);
 if(s.config.positionResearchMode==="MULTI_SESSION_RESEARCH"){
   if(!bankWindow){proposed="ABSTAIN";reason="BANK_WINDOW_CLOSED_RESEARCH";}
   else if(!ready){/* Keep strict fast/evidence gate, no fallback. */}
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
 if(proposed==="ABSTAIN")s.audit.abstained++;
 else s.audit.proposed++;
 s.audit.decisionsByReason[reason]=(s.audit.decisionsByReason[reason]||0)+1;
 // Shadow simulation is optional and NEVER changes the real portfolio.
 if(s.paper.enabled&&ready&&bankWindow&&proposed!=="KEEP")
  paperTrade(s,proposed,o.price);
 s.paper.lastPrice=o.price;
 if(s.paper.valid){
  const net=paperNet(s,o.price);
  s.paper.equityPeak=Math.max(s.paper.equityPeak,net);
  s.paper.maxDrawdownPct=Math.max(s.paper.maxDrawdownPct,
   100*(1-net/s.paper.equityPeak));
 }
 s.last={t,price:o.price,context:c,sourceId:o.sourceId};
 return {at:o.asof,context:c,holding:h,proposedResearchAction:proposed,
  qKeep:enough?keep.value:null,qSwitch:enough?sw.value:null,
  updateCount:s.audit.updates,readyForResearchComparison:ready,
  researchDecisionReason:reason,
  s1ResearchEvidence:s.lastS1Evidence?{provenance:s.lastS1Evidence.provenance,
    byHorizon:s.lastS1Evidence.byHorizon}:null,
  multiSessionResearch:{state:sessionState,fiveSession:longFive,
     policyMode:s.config.positionResearchMode,bankWindow},
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
   lastS1Evidence:s.lastS1Evidence?clone(s.lastS1Evidence):null,
   scienceGate:"NOT_PROVEN",liveTradeAuthorized:false,
  limitations:["RECONSTRUCTED_MID_NOT_BANK_EXECUTION_QUOTES",
    "15MIN_TRANSITIONS_CORRELATED_NOT_INDEPENDENT_EVIDENCE",
    "S1_S2_ALPHA_NOT_PROVEN","NO_BLIND_OOS_BACKTEST"]};
}
function checkpoint(s){return clone(s);}
function restore(data){
 const s=clone(data);
 if(s.version!==VERSION||!s.q||!s.paper||!s.registry||!s.audit||!s.sessionMemory)
  throw Error("S3_BAD_CHECKPOINT");
 s.sessionMemory=memory.restore(s.sessionMemory);
 return s;
}
function observeCompletedSession(s,session){
 if(s.version!==VERSION)throw Error("S3_BAD_CHECKPOINT_VERSION");
 if(!s.registry[session.sourceId])throw Error("S3_UNREGISTERED_SESSION_SOURCE");
 return memory.completed(s.sessionMemory,session);
}
module.exports={VERSION,FEE_PER_LEG,create,observe,observeCompletedSession,
 summary,checkpoint,restore,
 wealthMultiplier,context};
