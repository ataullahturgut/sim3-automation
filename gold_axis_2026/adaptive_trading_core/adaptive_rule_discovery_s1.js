"use strict";
/**
 * KAVIS S1: online, date-agnostic economic-state rule discovery. RESEARCH ONLY.
 * No BUY/SELL authority. No manually programmed market-direction rules.
 * Every feature must be numerically normalized using a prior/as-of-only transform.
 *
 * A rule is a mutable prototype of co-observed market conditions, not a cause.
 * Rule outcome statistics change ONLY when a previously anchored horizon matures.
 * At most one training anchor every 240 elapsed minutes avoids treating 15m
 * overlaps as independent labels. Meaningful economic names come from input
 * metadata; the engine knows no "USD down -> GOLD up" rule.
 */
const VERSION="KAVIS_S1_RULE_DISCOVERY_20261016";
const DEFAULT_HORIZONS=[240,1440,4320,10080,20160];
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const copy=x=>JSON.parse(JSON.stringify(x));
const stamp=x=>{
  if(typeof x!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/i.test(x))throw Error("ASOF_TIMEZONE_REQUIRED");
  const t=Date.parse(x);
  if(!Number.isFinite(t))throw Error("ASOF_TIME_INVALID");
  return t;
};
const iso=t=>new Date(t).toISOString();
function validateNames(names){
  if(!Array.isArray(names)||names.length<2||names.length>64||
    new Set(names).size!==names.length)throw Error("FEATURE_SCHEMA_INVALID");
  for(const n of names){
    if(typeof n!=="string"||!/^[a-z][a-z0-9_]{1,47}$/.test(n)||
       /^(date|year|month|day|weekday|timestamp|event_id|episode_id|case_id)$/.test(n)||
       /(?:^|_)(?:future|oracle|target|realized|next_price|lookahead)(?:_|$)/.test(n))
       throw Error("CALENDAR_ID_OR_TARGET_FEATURE_FORBIDDEN");
  }
}
function makeStats(){return {n:0,mean:0,m2:0,up:0,down:0,downsideMean:0};}
function create(options){
  const o=options||{};
  validateNames(o.featureNames);
  const horizons=o.horizons||DEFAULT_HORIZONS;
  if(!Array.isArray(horizons)||!horizons.length||new Set(horizons).size!==horizons.length||
     horizons.some(h=>!Number.isInteger(h)||h<60||h>43200))
    throw Error("HORIZON_SCHEMA_INVALID");
  const anchorMinutes=o.anchorMinutes??240;
  if(!Number.isInteger(anchorMinutes)||anchorMinutes<60)throw Error("ANCHOR_INVALID");
  // Source IDs must be reviewed by the caller. A source *name* alone is not
  // external proof of first publication or vintage; keep this distinction in audit.
  const sourceRegistry=o.sourceRegistry;
  if(!sourceRegistry||typeof sourceRegistry!=="object"||Array.isArray(sourceRegistry)||
     !Object.keys(sourceRegistry).length)throw Error("SOURCE_REGISTRY_REQUIRED");
  for(const [id,entry] of Object.entries(sourceRegistry)){
    if(!id||!entry||!["SYNTHETIC_ONLY","RECONSTRUCTED_MARKET_ASOF","VERIFIED_PIT"].includes(entry.evidenceStatus)||
       !["MARKET","EVENT","BOTH"].includes(entry.kind))throw Error("SOURCE_REGISTRY_INVALID");
  }
  const maxLateMinutes=o.maxLateMinutes??15;
  if(!Number.isInteger(maxLateMinutes)||maxLateMinutes<0||maxLateMinutes>15)
    throw Error("STRICT_M15_MATURITY_TOLERANCE_REQUIRED");
  return {version:VERSION, featureNames:o.featureNames.slice(),horizons:horizons.slice(),
    config:{anchorMinutes,maxRules:Math.min(32,Math.max(2,o.maxRules??16)),
      noveltyDistance:Math.max(.3,o.noveltyDistance??1.25),
      mergeDistance:.18,minReady:8,maxLateMinutes},
    sourceRegistry:copy(sourceRegistry),
    clock:null,lastAnchor:null,nextRuleId:1,rules:[],redirects:{},pending:[],
    audit:{observations:0,anchors:0,ruleCreated:0,ruleMerged:0,labelsMatured:0,
      labelsSkipped:0,rejectedMissing:0,tradeActions:0,newsVerified:0,
      rulesSaturated:0,sourceRejected:0}};
}
function featureVector(s,features,asof){
  if(!features||typeof features!=="object"||Array.isArray(features))
    throw Error("FEATURES_OBJECT_REQUIRED");
  const out={};
  for(const n of s.featureNames){
    if(!(n in features)||features[n]===null)continue; // missing means missing, never zero
    const f=features[n];
    if(!f||typeof f!=="object"||!finite(f.value)||
       Math.abs(f.value)>5||!f.availableAt||!f.observedAt||!f.source||
       !["MARKET","EVENT"].includes(f.kind))
      throw Error("FEATURE_UNPROVEN_OR_UNNORMALIZED_"+n);
    const entry=s.sourceRegistry[f.source];
    if(!entry||!(entry.kind===f.kind||entry.kind==="BOTH"))
      throw Error("UNREGISTERED_FEATURE_SOURCE_"+n);
    const av=stamp(f.availableAt),obs=stamp(f.observedAt);
    if(obs>av||av>asof)throw Error("FUTURE_OR_REVERSED_FEATURE_"+n);
    if(f.kind==="EVENT"){
      if(entry.evidenceStatus!=="VERIFIED_PIT")
        throw Error("EVENT_SOURCE_NOT_PIT_VERIFIED_"+n);
      if(f.firstPublishedAt===undefined||f.firstprintVerified!==true)
        throw Error("UNVERIFIED_EVENT_FIRSTPRINT_"+n);
      const first=stamp(f.firstPublishedAt);
      if(first>obs||first>av)throw Error("FUTURE_EVENT_FIRSTPRINT_"+n);
    }
    out[n]=f.value;
  }
  for(const k of Object.keys(features)){
    if(!s.featureNames.includes(k))throw Error("FEATURE_SCHEMA_DRIFT_"+k);
  }
  return out;
}
function squaredDistance(a,b){
  let sum=0,common=0,only=0;
  for(const k of Object.keys(a)){
    if(k in b){sum+=(a[k]-b[k])**2;common++;}else only++;
  }
  for(const k of Object.keys(b))if(!(k in a))only++;
  if(common<2)return Infinity; // don't identify different sparse patterns as same
  return Math.sqrt(sum/common)+.20*only/(common+only);
}
function scored(s,x){
  return s.rules.map(r=>({r,d:squaredDistance(x,r.center)}))
    .filter(z=>Number.isFinite(z.d)).sort((a,b)=>a.d-b.d);
}
function newRule(s,x,at){
  const r={id:"R"+String(s.nextRuleId++).padStart(4,"0"),
    bornAt:iso(at),observations:1,center:copy(x),
    featureN:Object.fromEntries(Object.keys(x).map(k=>[k,1])),
    outcomes:Object.fromEntries(s.horizons.map(h=>[h,makeStats()])),
    lastSeenAt:iso(at)};
  s.rules.push(r);s.audit.ruleCreated++;return r;
}
function updateCenter(r,x,at){
  r.observations++;r.lastSeenAt=iso(at);
  for(const [k,v] of Object.entries(x)){
    const n=(r.featureN[k]||0)+1;
    r.center[k]=(r.center[k]===undefined)?v:r.center[k]+(v-r.center[k])/n;
    r.featureN[k]=n;
  }
}
function activeId(s,id){
  let i=0;
  while(s.redirects[id]&&i++<100)id=s.redirects[id];
  if(i>=100)throw Error("RULE_REDIRECT_LOOP");
  return id;
}
function integrate(st,ret,down){
  st.n++;const delta=ret-st.mean;
  st.mean+=delta/st.n;st.m2+=delta*(ret-st.mean);
  st.up+=ret>0?1:0;st.down+=ret<=0?1:0;
  st.downsideMean+=(down-st.downsideMean)/st.n;
}
function mergeStats(a,b){
  if(!b.n)return;
  if(!a.n){Object.assign(a,copy(b));return;}
  const n=a.n+b.n,delta=b.mean-a.mean;
  a.m2+=b.m2+delta*delta*a.n*b.n/n;
  a.mean=(a.mean*a.n+b.mean*b.n)/n;
  a.downsideMean=(a.downsideMean*a.n+b.downsideMean*b.n)/n;
  a.up+=b.up;a.down+=b.down;a.n=n;
}
function maybeMerge(s){
  // Structural-only merge: both prototypes supported, empirically similar.
  // Do not merge solely on a shared G01/G02 label or date.
  for(let i=0;i<s.rules.length;i++)for(let j=i+1;j<s.rules.length;j++){
    const a=s.rules[i],b=s.rules[j];
    if(a.observations<8||b.observations<8)continue;
    if(squaredDistance(a.center,b.center)>s.config.mergeDistance)continue;
    const h=s.horizons[0],sa=a.outcomes[h],sb=b.outcomes[h];
    if(sa.n<8||sb.n<8||Math.abs(sa.mean-sb.mean)>.15)continue;
    for(const [k,v] of Object.entries(b.center)){
      const na=a.featureN[k]||0,nb=b.featureN[k];
      a.center[k]=na?(na*a.center[k]+nb*v)/(na+nb):v;
      a.featureN[k]=na+nb;
    }
    a.observations+=b.observations;
    for(const horizon of s.horizons)mergeStats(a.outcomes[horizon],b.outcomes[horizon]);
    s.redirects[b.id]=a.id;s.rules.splice(j,1);s.audit.ruleMerged++;
    return; // one merge per observation, stable rule IDs through redirect
  }
}
function safelyKnownSource(id,registry){return !!(registry&&registry[id]&&
  ["MARKET","BOTH"].includes(registry[id].kind));}
function validatePrice(s,ob,t){
  if(!finite(ob.price)||ob.price<=0||!ob.priceAvailableAt||
     !ob.barStartedAt||!Number.isInteger(ob.barMinutes)||ob.barMinutes<=0)
     throw Error("PRICE_VINTAGE_OR_BAR_MISSING");
  const start=stamp(ob.barStartedAt),avail=stamp(ob.priceAvailableAt);
  const end=start+ob.barMinutes*60000;
  if(end>t||avail<end||avail>t)throw Error("PRICE_BAR_NOT_YET_COMPLETE");
  if(ob.barMinutes!==15)throw Error("S1_REQUIRES_FULL_M15_BAR");
  if(!ob.priceSource||!safelyKnownSource(ob.priceSource,s.sourceRegistry))
    throw Error("UNREGISTERED_PRICE_SOURCE");

}
function mature(s,t,price){
  const remain=[];
  for(const p of s.pending){
    p.low=Math.min(p.low,price);
    if(t<p.due){remain.push(p);continue;}
    if(t-p.due>s.config.maxLateMinutes*60000){
      s.audit.labelsSkipped++;continue;
    }
    const r=s.rules.find(q=>q.id===activeId(s,p.ruleId));
    if(!r)throw Error("PENDING_RULE_MISSING");
    const ret=100*Math.log(price/p.price);
    const down=Math.max(0,100*Math.log(p.price/p.low));
    integrate(r.outcomes[p.horizon],ret,down);
    s.audit.labelsMatured++;
  }
  s.pending=remain;
}
function predictVector(s,x){
  const neighbours=scored(s,x);
  return s.horizons.map(h=>{
    const qualified=neighbours.filter(({r})=>r.outcomes[h].n>=s.config.minReady);
    if(!qualified.length)return {horizonMinutes:h,ready:false,expectedLogPct:null,
      uncertaintyPct:null,upFraction:null,downsidePct:null,effectiveN:0,ruleIds:[]};
    const weights=qualified.map(z=>Math.exp(-.5*(z.d/Math.max(.2,s.config.noveltyDistance))**2));
    const total=weights.reduce((a,b)=>a+b,0);
    let mean=0,var0=0,pup=0,downside=0,n=0;
    qualified.forEach(({r},i)=>{
      const w=weights[i]/total,q=r.outcomes[h];
      mean+=w*q.mean;pup+=w*q.up/q.n;downside+=w*q.downsideMean;
      n+=w*q.n;
    });
    qualified.forEach(({r},i)=>{
      const w=weights[i]/total,q=r.outcomes[h];
      var0+=w*(Math.max(0,q.m2/Math.max(1,q.n-1))+(q.mean-mean)**2);
    });
    return {horizonMinutes:h,ready:true,expectedLogPct:mean,
      uncertaintyPct:Math.sqrt(var0),upFraction:pup,
      downsidePct:downside,effectiveN:n,
      ruleIds:qualified.map(z=>z.r.id)};
  });
}
function forecast(s,ob){
  const t=stamp(ob.asof);
  if(s.clock!==null&&t<s.clock)throw Error("HISTORICAL_FORECAST_REQUIRES_ASOF_CHECKPOINT");
  const x=featureVector(s,ob.features,t);
  if(Object.keys(x).length<2)return {ready:false,reason:"INSUFFICIENT_ASOF_FEATURES",byHorizon:[]};
  return {ready:true,reason:"RESEARCH_ONLY_NOT_A_TRADE_SIGNAL",
    matchedRules:scored(s,x).map(z=>({ruleId:z.r.id,distance:z.d,support:z.r.observations})),
    byHorizon:predictVector(s,x)};
}
function observe(s,ob){
  if(s.version!==VERSION)throw Error("BAD_CORE_VERSION");
  if(!ob||typeof ob!=="object"||["futureReturn","target","oracle"].some(k=>k in ob))
    throw Error("FORBIDDEN_FUTURE_TARGET");
  const t=stamp(ob.asof);
  if(s.clock!==null&&t<=s.clock)throw Error("NONMONOTONIC_CORE_CLOCK");
  validatePrice(s,ob,t);
  const x=featureVector(s,ob.features,t); // validate entire observation BEFORE mutation
  mature(s,t,ob.price);
  s.clock=t;s.audit.observations++;
  const decisionForecast=Object.keys(x).length<2?
     {ready:false,reason:"INSUFFICIENT_ASOF_FEATURES",byHorizon:[]}:
     {ready:true,reason:"RESEARCH_ONLY_NOT_A_TRADE_SIGNAL",
      byHorizon:predictVector(s,x)};
  let anchored=false,ruleId=null;
  if(Object.keys(x).length>=2&&(s.lastAnchor===null||
      t-s.lastAnchor>=s.config.anchorMinutes*60000)){
    let near=scored(s,x);
    let r;
    if(!near.length||near[0].d>s.config.noveltyDistance){
      if(s.rules.length<s.config.maxRules)r=newRule(s,x,t);
      else {r=null;s.audit.rulesSaturated++;} // Don't force novel patterns into false prototypes
    }else r=near[0].r;
    if(r){
      if(r.bornAt!==iso(t))updateCenter(r,x,t);
      ruleId=r.id;anchored=true;s.lastAnchor=t;s.audit.anchors++;
      for(const horizon of s.horizons)s.pending.push({
        ruleId,horizon,at:iso(t),due:t+horizon*60000,
        price:ob.price,low:ob.price});
      maybeMerge(s);
    }
  }else if(Object.keys(x).length<2)s.audit.rejectedMissing++;
  return {version:VERSION,asof:ob.asof,anchored,ruleId,action:null,
    policyStatus:"NOT_IMPLEMENTED_NO_BUY_SELL",observedDimensions:Object.keys(x),
    learnedRules:s.rules.length,matured:s.audit.labelsMatured,
    forecastAtDecision:decisionForecast};
}
function rules(s){
  return s.rules.map(r=>({id:r.id,center:copy(r.center),
    anchorObservations:r.observations,firstObservedAt:r.bornAt,
    outcomes:Object.fromEntries(s.horizons.map(h=>{
      const x=r.outcomes[h];return [h,{n:x.n,up:x.up,down:x.down,
        meanLogPct:x.n?x.mean:null,standardDeviationPct:x.n>1?
          Math.sqrt(Math.max(0,x.m2/(x.n-1))):null,
        observedDownsidePct:x.n?x.downsideMean:null}];
    }))}));
}
function checkpoint(s){return copy(s);}
function restore(v){
  const s=copy(v);
  if(!s.sourceRegistry||!Object.keys(s.sourceRegistry).length)throw Error("CHECKPOINT_MISSING_SOURCE_REGISTRY");
  if(s.version!==VERSION||!Array.isArray(s.rules)||!Array.isArray(s.pending)||
    !Array.isArray(s.horizons))throw Error("BAD_CHECKPOINT");
  validateNames(s.featureNames);return s;
}
module.exports={VERSION,create,observe,forecast,rules,checkpoint,restore};
