"use strict";
/** GOLD downside mechanism: online market weakness vs FIRST news availability.
 * Fixed descriptive thresholds: NOT validated forecasts or BUY/SELL authority.
 * All inputs must be available at completed M15 bar time. Gaps reset the
 * window (never bridge weekends). An article explaining the fall after it
 * began cannot be a first trigger. An article before the fall is NOT
 * necessarily causal. No selected swing pivots, calendar ID or future labels.
 */
const newsRouter=require("./event_news_condition_router_v1");
const VERSION="GOLD_DOWNSIDE_NEWS_ONSET_V1_20261019";
const STEP=900000,MIN=60000,HOUR=3600000;
const num=x=>typeof x==="number"&&Number.isFinite(x);
function ms(v,name){if(typeof v!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/.test(v)||
 !Number.isFinite(Date.parse(v)))throw Error("DOWN_OFFSET_TIME_REQUIRED_"+name);
 return Date.parse(v);}
const iso=t=>new Date(t).toISOString();
const round=x=>num(x)?+x.toFixed(5):null;
function create({registry=null,sourceId=null}={}){
 if(registry!==null&&(!registry||!Array.isArray(registry.sources)))
  throw Error("DOWN_NEWS_REGISTRY_INVALID");
 return {version:VERSION,registry,sourceId,lastAt:null,lastPrice:null,
  window:[],onsetAt:null,onsetReference:null,
  previousEpisodeOnsetAt:null,previousEpisodeReference:null,
  lastPhase:"WARMUP",seen:{},
  latestNews:null,newsHistory:[],pendingBeforeFall:[],
  audit:{bars:0,gaps:0,newsReceived:0,newsFirstprintAttested:0,
   priceOnlyStarts:0,firstNewsBeforeOnsetCandidates:0,
   newsAfterOnset:0,coincidentUnresolved:0,posthocOrUnverified:0}};
}
function preflight(s,bar){
 if(s.version!==VERSION)throw Error("DOWN_BAD_VERSION");
 const t=ms(bar.asof,"asof"),start=ms(bar.barStartedAt,"barStartedAt"),
       available=ms(bar.priceAvailableAt,"priceAvailableAt");
 if(start+STEP!==t||available>t||!num(bar.price)||bar.price<=0||
   bar.barMinutes!==15)throw Error("DOWN_INVALID_INCOMPLETE_PRICE");
 if(s.sourceId&&bar.priceSource!==s.sourceId)throw Error("DOWN_SOURCE_CHANGED");
 if(s.lastAt!==null&&t<=s.lastAt)throw Error("DOWN_NONMONOTONIC");
 if(bar.downsideNews!==undefined){
  if(!Array.isArray(bar.downsideNews))throw Error("DOWN_NEWS_ARRAY_REQUIRED");
  if(bar.downsideNews.length&&!s.registry)throw Error("DOWN_REGISTRY_REQUIRED_FOR_NEWS");
  const ids=new Set();
  for(const n of bar.downsideNews){
   if(!n||typeof n.id!=="string"||!n.id||ids.has(n.id)||s.seen[n.id])
    throw Error("DOWN_DUPLICATE_OR_INVALID_NEWS");
   ids.add(n.id);
   const detected=ms(n.detectedAt,"newsDetected");
   if(detected>t)throw Error("DOWN_FUTURE_NEWS");
   newsRouter.route(n,{asof:bar.asof,registry:s.registry});
  }
 }
 return t;
}
function sample(x,t){
 const win=x.window;
 if(win.length<17)return {ready:false,pressure:0,drawdown:0,exhaustion:0,negativeShare:0,
  phase:"WARMUP",reference:null};
 const old=win[win.length-17],current=win[win.length-1];
 let variance=0,negative=0;
 for(let i=win.length-16;i<win.length;i++){
  const z=Math.log(win[i]/win[i-1]);
  variance+=z*z;if(z<0)negative++;
 }
 const fourVol=Math.max(.00015,Math.sqrt(variance));
 const fourRet=Math.log(current/old);
 const peak=Math.max(...win);
 const drawdown=100*Math.max(0,Math.log(peak/current));
 const prior=win.slice(0,-1);
 const oldPeak=Math.max(...prior);
 const ddPrior=100*Math.max(0,Math.log(oldPeak/win[win.length-2]));
 const pressure=Math.max(0,-fourRet/fourVol);
 const ex=prior.length>=32?Math.max(0,Math.log(oldPeak/prior[0]))/
    Math.max(.0001,fourVol):0;
 const phase=drawdown>=1.0&&pressure>=0.8?"CONFIRMED_FALL":
  drawdown>=.5?"EARLY_WEAKNESS":"NO_ALERT";
 return {ready:true,pressure:round(pressure),drawdown:round(drawdown),
  exhaustion:round(ex),negativeShare:round(negative/16),phase,
  reference:round(peak),previousDrawdown:ddPrior,volatility4h:round(fourVol)};
}
function observe(s,bar){
 const t=preflight(s,bar),contiguous=s.lastAt!==null&&t-s.lastAt===STEP;
 const currentNews=bar.downsideNews??[];
 if(s.lastAt!==null&&!contiguous){
  s.audit.gaps++;s.window=[];s.onsetAt=null;
  s.onsetReference=null;s.lastPhase="GAP";
  // Time itself advances through weekends, but no price bars are interpolated.
  // Retain prior verified releases as context within the 72h research window;
  // they never become a fabricated continuous price signal.
 }
 // Classify relative to PRICE INFORMATION KNOWN BEFORE this bar closed.
 const priorOnset=s.onsetAt??(s.previousEpisodeOnsetAt!==null&&
  t-s.previousEpisodeOnsetAt<=72*HOUR?s.previousEpisodeOnsetAt:null);
 const priorWasAcrossGap=s.onsetAt===null&&priorOnset!==null;
 const seenNow=[];
 for(const n of currentNews){
  const result=newsRouter.route(n,{asof:bar.asof,registry:s.registry});
  const detect=ms(n.detectedAt,"detectedAt");
  const firstprint=result.firstprintAttested===true;
  const lagged= s.lastAt!==null && detect<=s.lastAt;
  let role;
  const chronologyRole=priorOnset===null?"NOT_YET_WEAK":
   priorWasAcrossGap?"AFTER_PREVIOUS_PRICE_WEAKNESS_PRIOR_SESSION":
   detect<=priorOnset+STEP?"SAME_BAR_OR_EARLIER_UNRESOLVED":"AFTER_PRICE_WEAKNESS";
  if(lagged||!firstprint)role="UNVERIFIED_OR_LATE_CONTEXT";
  else if(priorOnset===null)role="BEFORE_FIRST_OBSERVED_WEAKNESS";
  else if(priorWasAcrossGap)role="AFTER_PREVIOUS_PRICE_WEAKNESS_ACCELERANT_CANDIDATE";
  else if(detect<=priorOnset+STEP)role="SAME_BAR_UNRESOLVED";
  else role="AFTER_PRICE_WEAKNESS_ACCELERANT_CANDIDATE";
  if(result.status==="SECONDARY_OR_LAGGED_CONTEXT_ONLY")role="POSTHOC_OR_SECONDARY_REPORT";
  const rec={id:n.id,source:result.source,detectedAt:n.detectedAt,
   observedAt:bar.asof,eventTime:n.eventTime,
   conditions:result.conditions,candidateOrgs:result.candidateOrgs.map(z=>z.org),
   firstprintAttested:firstprint,availableFirstAt:n.availableAt,
   role,chronologyRole,causalEvidence:"NOT_ESTABLISHED"};
  s.seen[n.id]=true;s.latestNews=rec;s.newsHistory.push(rec);
  if(s.newsHistory.length>80)s.newsHistory.shift();
  if(role==="BEFORE_FIRST_OBSERVED_WEAKNESS")
   s.pendingBeforeFall.push(rec);
  if(firstprint)s.audit.newsFirstprintAttested++;
  if(["AFTER_PRICE_WEAKNESS_ACCELERANT_CANDIDATE",
      "AFTER_PREVIOUS_PRICE_WEAKNESS_ACCELERANT_CANDIDATE"].includes(role))
    s.audit.newsAfterOnset++;
  if(role==="SAME_BAR_UNRESOLVED")s.audit.coincidentUnresolved++;
  if(role==="UNVERIFIED_OR_LATE_CONTEXT"||role==="POSTHOC_OR_SECONDARY_REPORT")
   s.audit.posthocOrUnverified++;
  s.audit.newsReceived++;seenNow.push(rec);
 }
 // G causal price clock; drawdown from at most 96 completed consecutive bars.
 s.window.push(bar.price);
 if(s.window.length>96)s.window.shift();
 const m=sample(s,t);
 // A severe price discontinuity at the first quote after a gap is observable,
 // but is NOT a measured continuous drawdown from unobserved weekend bars.
 const gapDrop=!contiguous&&s.audit.bars>0&&s.lastPrice!==null&&
  Math.log(bar.price/s.lastPrice)<=Math.log(.995);
 if(gapDrop){m.phase="GAP_OPEN_DOWN_DISLOCATION";m.drawdown=round(-100*Math.log(bar.price/s.lastPrice));
  m.reference=round(s.lastPrice);m.ready=false;}
 let newOnset=false,newsLinked=null;
 if((m.ready&&m.drawdown>=.5||gapDrop)&&s.onsetAt===null){
  s.onsetAt=t;s.onsetReference=m.reference;newOnset=true;
  if(!existingEarlier){s.previousEpisodeOnsetAt=t;s.previousEpisodeReference=m.reference;}
  // Only firstprint verified, not retroactively ingested earlier news.
  const existingEarlier=priorWasAcrossGap;
  const eligible=s.pendingBeforeFall.filter(n=>!existingEarlier&&
   t-ms(n.detectedAt,"detect")<=72*HOUR&&
   s.lastAt!==null&&ms(n.detectedAt,"detect")<=s.lastAt);
  // Multiple overlapping headlines: retain all, never attribute total move.
  newsLinked=eligible.map(n=>n.id);
  if(eligible.length)s.audit.firstNewsBeforeOnsetCandidates++;
  else s.audit.priceOnlyStarts++;
  if(currentNews.length)for(const rec of seenNow){
   if(rec.role==="BEFORE_FIRST_OBSERVED_WEAKNESS"){
    rec.role="SAME_BAR_UNRESOLVED";s.audit.coincidentUnresolved++;
   }
  }
  s.pendingBeforeFall=[];
 }
 if(s.previousEpisodeOnsetAt!==null&&
   (t-s.previousEpisodeOnsetAt>72*HOUR||
    (s.previousEpisodeReference!==null&&
      bar.price>=s.previousEpisodeReference*.998))){
   s.previousEpisodeOnsetAt=null;s.previousEpisodeReference=null;
 }
 if(m.ready&&m.drawdown<.20&&s.onsetAt!==null){
  s.onsetAt=null;s.onsetReference=null;s.pendingBeforeFall=[];
 }
 if(s.pendingBeforeFall.length)
  s.pendingBeforeFall=s.pendingBeforeFall.filter(n=>t-ms(n.detectedAt,"detect")<=72*HOUR);
 s.lastPrice=bar.price;s.lastAt=t;s.lastPhase=m.phase;s.audit.bars++;
 return {asof:bar.asof,phase:m.phase,ready:m.ready,
  observedPriceWeaknessSince:s.onsetAt===null?null:iso(s.onsetAt),
  newPriceWeakness:newOnset,
  linkedNewsBeforeObservedWeakness:newsLinked??[],
  marketEvidence:{down_pressure_z:Math.min(5,m.pressure),down_drawdown_norm:Math.min(5,m.drawdown),
   down_negative_share:Math.min(5,m.negativeShare),down_rally_exhaustion:Math.min(5,m.exhaustion)},
  drawdownPct:m.drawdown,marketReference:m.reference,
  latestNews:s.latestNews,newsNewlyObserved:seenNow,
  gapOpenDislocation:gapDrop,
  state:"OBSERVATIONAL_WARNING_NOT_PREDICTION",
  probabilityOfFurtherFall:null,remainingFallPct:null,
  causalAttribution:"UNPROVEN",action:null,tradeAllowed:false};
}
function checkpoint(s){return JSON.parse(JSON.stringify(s));}
function restore(s){if(!s||s.version!==VERSION||!s.audit||!Array.isArray(s.window))
  throw Error("DOWN_INVALID_CHECKPOINT");return checkpoint(s);}
module.exports={VERSION,create,preflight,observe,checkpoint,restore};
