"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 — economic mechanism research integrator.
 * OLAY-02 news provenance → ETKI-05 K/CR/CTX labels → OGREN-03 ORG mechanism
 * → G(global)/E(event-relative) measurement → non-trading shadow hand-off.
 *
 * No model fitting, real-time news retrieval, H3/H4 causal certification,
 * operational S1/S2/S3 modification, or transaction decisions.
 */
const router=require("./event_news_condition_router_v1");
const STEP=15*60000, MAX_EVENT_HOURS=24*7;
const ISOTIME=/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/;
function stamp(x,field){
 if(typeof x!=="string"||!ISOTIME.test(x)||!Number.isFinite(Date.parse(x)))
  throw Error("EVENT_MECHANISM_OFFSET_TIME_REQUIRED_"+field);
 return Date.parse(x);
}
function finite(x){return typeof x==="number"&&Number.isFinite(x);}
function round(x,n=5){return x===null||!Number.isFinite(x)?null:+x.toFixed(n);}
function barsAt(completedBars,asof){
 if(!Array.isArray(completedBars))throw Error("PRICE_BARS_ARRAY_REQUIRED");
 const byClose=[];
 for(const x of completedBars){
  const t=stamp(x.bar_start_utc,"bar_start_utc")+STEP;
  // A future source row is never a usable price.
  if(t>asof)continue;
  if(!finite(x.bid_close)||!finite(x.ask_close)||x.bid_close<=0||
    x.ask_close<=0||x.ask_close<x.bid_close)throw Error("MALFORMED_BID_ASK");
  byClose.push({t,price:(x.bid_close+x.ask_close)/2});
 }
 byClose.sort((a,b)=>a.t-b.t);
 for(let i=1;i<byClose.length;i++)
  if(byClose[i].t===byClose[i-1].t)throw Error("PRICE_BAR_DUPLICATED");
 return byClose;
}
function latestBefore(bars,t){let b=null;for(const x of bars){if(x.t>t)break;b=x;}return b;}
function lastWindow(bars,lastMs,count){
 const out=[];for(let i=count-1;i>=0;i--){
  const v=latestBefore(bars,lastMs-i*STEP);
  if(!v||v.t!==lastMs-i*STEP)return null;
  out.push(v);
 }
 return out;
}
function globalPrice(bars){
 const recent=bars.length?bars[bars.length-1]:null;
 if(!recent)return {ready:false,trend4hPct:null,volatility4hPct:null,price:null,asof:null};
 const w=lastWindow(bars,recent.t,17);
 if(!w)return {ready:false,trend4hPct:null,volatility4hPct:null,price:round(recent.price),asof:new Date(recent.t).toISOString()};
 let sq=0;for(let i=1;i<w.length;i++)sq+=Math.log(w[i].price/w[i-1].price)**2;
 return {ready:true,trend4hPct:round(100*Math.log(recent.price/w[0].price)),
  volatility4hPct:round(100*Math.sqrt(sq)),price:round(recent.price),
  asof:new Date(recent.t).toISOString()};
}
const MEDIATORS={
 ORG01:{supports:["USD_DOWN","REAL_YIELD_DOWN"],opposes:["USD_UP","REAL_YIELD_UP"]},
 ORG02:{supports:["USD_UP","REAL_YIELD_UP"],opposes:["USD_DOWN","REAL_YIELD_DOWN"]},
 ORG03:{supports:["FUNDING_STRESS_UP","HAVEN_DEMAND_UP"],opposes:["FORCED_LIQUIDATION_UP"]},
 ORG04:{supports:["SAFE_HAVEN_DEMAND_UP","RISK_AVERSION_UP"],opposes:["RISK_AVERSION_DOWN","REAL_YIELD_UP"]},
 ORG05:{supports:["RISK_AVERSION_DOWN","HEDGE_POSITION_UNWINDING"],opposes:["RISK_AVERSION_UP"]},
 ORG06:{supports:["TRADE_UNCERTAINTY_UP","SAFE_HAVEN_DEMAND_UP"],opposes:["USD_UP","FORCED_LIQUIDATION_UP"]},
 ORG07:{supports:["TRADE_UNCERTAINTY_DOWN","RISK_AVERSION_DOWN"],opposes:["TRADE_UNCERTAINTY_UP"]},
 ORG08:{supports:["FUNDING_STRESS_UP","FORCED_LIQUIDATION_UP"],opposes:["FUNDING_STRESS_DOWN"]},
 ORG09:{supports:["PHYSICAL_PREMIUM_UP","VERIFIED_GOLD_FLOWS_UP"],opposes:["VERIFIED_GOLD_FLOWS_DOWN"]},
 ORG10:{supports:["GOLD_OI_DOWN","HEDGE_POSITION_UNWINDING"],opposes:["VERIFIED_GOLD_FLOWS_UP"]},
 ORG11:{supports:["RESERVE_DEMAND_UP","REAL_YIELD_UP"],opposes:["RESERVE_DEMAND_DOWN"]},
 ORG12:{supports:["MARGIN_REQUIREMENTS_UP","FORCED_LIQUIDATION_UP"],opposes:["VERIFIED_GOLD_FLOWS_UP"]}
};
function evidenceAt(items,asof,earliest){
 if(!Array.isArray(items))throw Error("MEDIATOR_EVIDENCE_ARRAY_REQUIRED");
 const out=[];
 for(const a of items){
  if(!a||typeof a!=="object"||!a.id||!a.code)throw Error("MEDIATOR_ID_CODE_REQUIRED");
  const observed=stamp(a.observedAt,"observedAt"),available=stamp(a.availableAt,"availableAt");
  // Future or late-arriving original evidence never becomes an old market response.
  if(observed>asof||available>asof)continue;
  if(a.originalEvidenceVerified!==true||a.independentFromGoldPrice!==true||
   typeof a.sourceEvidenceId!=="string"||a.sourceEvidenceId.length<9)continue;
  if(available<observed||observed<earliest)continue;
  if(typeof a.sourceId!=="string"||!a.sourceId)continue;
  out.push({id:a.id,code:a.code,observedAt:a.observedAt,availableAt:a.availableAt,sourceId:a.sourceId});
 }
 return out;
}
function marketEpisode(news,allBars,asof){
 const eventT=stamp(news.eventTime,"eventTime"),detect=stamp(news.detectedAt,"detectedAt");
 const before=latestBefore(allBars,eventT);
 const detectionBase=latestBefore(allBars,detect);
 const last=allBars.length?allBars[allBars.length-1]:null;
 const preValid=before!==null&&eventT-before.t<=STEP;
 const detectValid=detectionBase!==null&&detect-detectionBase.t<=STEP;
 // A fixed observation-horizon cap is NOT an economic mechanism lifetime.
 // Stop interpreting large multi-week price drift as the price response of one news.
 const inObservationWindow=last!==null&&last.t-eventT<=MAX_EVENT_HOURS*3600000;
 const priceOk=last!==null&&preValid&&last.t>eventT&&inObservationWindow;
 const eventSlice=priceOk?allBars.filter(x=>x.t>=before.t&&x.t<=last.t):[];
 let gaps=0;
 for(let i=1;i<eventSlice.length;i++)if(eventSlice[i].t-eventSlice[i-1].t!==STEP)gaps++;
 const futurePrice=last&&last.t>=detect?last:null;
 const priceSinceNews=priceOk?round(100*Math.log(last.price/before.price)):null;
 const sinceDetection=detectValid&&futurePrice?round(100*Math.log(futurePrice.price/detectionBase.price)):null;
 // Pre-window volatility uses ONLY prices completed before information first arrived.
 const preWindow=before?lastWindow(allBars,before.t,17):null;
 let preVol=null;if(preWindow){
  let sum=0;for(let i=1;i<preWindow.length;i++)sum+=Math.log(preWindow[i].price/preWindow[i-1].price)**2;
  preVol=100*Math.sqrt(sum);
 }
 const b15=allBars.find(x=>x.t===eventT+STEP);
 const ret15=preValid&&b15&&b15.t<=asof?round(100*Math.log(b15.price/before.price)):null;
 return {
  announcementAt:news.eventTime,firstDetectedAt:news.detectedAt,
  outcomePriceLastBar:priceOk?new Date(last.t).toISOString():null,
  eventElapsedMinutes:priceOk?round((last.t-eventT)/60000,0):null,
  freshPriceBaseline:preValid,priceGapCount:gaps,
  priceSinceAnnouncementPct:priceSinceNews,first15mResponsePct:ret15,
  priceSinceDetectionPct:sinceDetection,preEventVolatility4hPct:round(preVol),
  directionOfObservedResponse:priceSinceNews===null?"UNKNOWN":priceSinceNews>0?"OBSERVED_UP":priceSinceNews<0?"OBSERVED_DOWN":"OBSERVED_FLAT",
  priceResponseInterpretable:priceOk&&gaps===0,
  observationWindowExpired:last!==null&&last.t-eventT>MAX_EVENT_HOURS*3600000,
  warning:"OBSERVED_PRICE_PATH_NOT_CAUSAL_EFFECT_OR_FUTURE_RETURN"
 };
}
function mechanismCandidates(news,market,med,library){
 const refs=Array.isArray(library?.mechanisms)?library.mechanisms:[];
 const byName=new Map(refs.map(x=>[x.org,x]));
 return news.candidateOrgs.map(c=>{
  if(!byName.has(c.org))throw Error("ORG_DEFINITION_MISSING_"+c.org);
  const def=byName.get(c.org),spec=MEDIATORS[c.org];
  const yes=med.filter(x=>spec.supports.includes(x.code));
  const no=med.filter(x=>spec.opposes.includes(x.code));
  const supportSources=new Set(yes.map(x=>x.sourceId));
  const conflict=no.length>0;
  const mediatorSupported=yes.length>=2&&supportSources.size>=2&&!conflict;
  const sourceAttested=news.firstprintAttested===true;
  const status=mediatorSupported&&sourceAttested?"H2_MEDIATOR_EVIDENCE_PRESENT_NOT_CAUSAL":
   sourceAttested?"H1_SOURCE_ATTESTED_MECHANISM_UNCONFIRMED":"H0_UNVERIFIED_OR_UNATTRIBUTED";
  // No price-only evidence upgrades mediator status; no H3/H4 from this adapter.
  const phase=mediatorSupported?"P2_TRANSMISSION_CANDIDATE":
   "P1_TRIGGER_CANDIDATE";
  return {
   org:c.org,name:def.name,role:c.role,conditions:c.triggerTags,
   status,phase,counterEvidence:conflict,
   supportingIndependentSignals:yes.map(x=>x.id),
   competingIndependentSignals:no.map(x=>x.id),
   neededForP2:spec.supports.filter(code=>!yes.some(x=>x.code===code)),
   initialHypothesis:def.expected,
   causalConfirmation:"NOT_ESTABLISHED",largeMoveProb:null,
   remainingMovePrediction:null,durationPrediction:null,
   marketResponse:market.directionOfObservedResponse,
   readyForLiveTrading:false
  };
 });
}
function integrate({news,registry,mechanismLibrary,asof,completedBars=[],marketEvidence=[]}){
 const t=stamp(asof,"asof");
 const routed=router.routeMany(news,{registry,asof});
 const bars=barsAt(completedBars,t);
 const global=globalPrice(bars);
 const events=routed.events.map(e=>{
  if(e.status==="PENDING_FIRST_ACCESS")
   return {...e,market:null,mechanisms:[],decisionEligible:false,action:null};
  const market=marketEpisode(e,bars,t),available=stamp(e.detectedAt,"detectedAt");
  const evidence=evidenceAt(marketEvidence,t,available);
  const mechanisms=mechanismCandidates(e,market,evidence,mechanismLibrary);
  return {...e,market,mechanisms,decisionEligible:false,action:null,
   outcomeInterpretation:"OBSERVATIONAL_NOT_CAUSALLY_ATTRIBUTED"};
 });
 const episodes=routed.overlappingEpisodes.map(group=>{
  const children=events.filter(x=>group.ids.includes(x.id));
  const orgs=[...new Set(children.flatMap(x=>x.mechanisms.map(m=>m.org)))];
  return {...group,candidateOrgs:orgs,
   tradeSignals:0,priceReturnsMayNotBeSummed:true,
   combinedCausalAttribution:"NOT_IDENTIFIED"};
 });
 return {
  version:"GLOBAL_GOLD_NEWS_MECHANISM_INTEGRATOR_V1_20261018",
  asof,globalMarket:global,events,overlappingEpisodes:episodes,
  priorEconomicContexts:routed.priorEconomicContexts,
  audit:{...routed.audit,candidateOrgs:[...new Set(events.flatMap(e=>e.mechanisms.map(m=>m.org)))].length,
   independentMechanismConfirmations:0,trainedDirectionalRules:0,
   coreS1S2S3Executions:0,bankOrders:0},
  S1Shadow:{status:"NOT_TRAINED",reason:"event conditioned forward labels uncalibrated"},
  S2Shadow:{status:"GLOBAL_BASELINE_PLUS_EVENT_MEASUREMENT_ONLY",global},
  S3Shadow:{status:"NO_ACTION",netExpectedBenefit:null},
  scientificStatus:"RESEARCH_SHADOW_ONLY",tradeAllowed:false
 };
}
module.exports={integrate,globalPrice,marketEpisode,MEDIATORS};
