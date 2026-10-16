"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / S1. Evidence admission and paired ablation.
 * This module extends the EXISTING mathematical CORE. No trading decisions.
 * Archived publication and its embargo do NOT certify contemporary first access.
 * Need timestamped firstprint + actual AND pre-release consensus provenance.
 */
const core=require("./adaptive_rule_discovery_s1");
const TYPES=new Set(["NFP","AHE","UNEMP","CPI"]);
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const stamp=x=>{
  if(typeof x!=="string"||!/(Z|[+-]\d\d:\d\d)$/i.test(x)||!Number.isFinite(Date.parse(x)))
    throw Error("UTC_OFFSET_TIMESTAMP_REQUIRED");
  return Date.parse(x);
};
const iso=x=>new Date(x).toISOString();
const maxTime=(...xs)=>Math.max(...xs.map(stamp));
function reason(release,asof,scale){
  const t=stamp(asof),scheduled=stamp(release.scheduledUtc);
  if(t<scheduled)return "RELEASE_IN_FUTURE";
  if(t-scheduled>=4*3600000)return "EVENT_EXPOSURE_EXPIRED";
  if(!TYPES.has(release.type)||!finite(release.actual)||!finite(release.consensus))
    return "MISSING_MACRO_COMPONENT";
  if(!finite(scale)||scale<=0||Math.abs((release.actual-release.consensus)/scale)>5)
    return "NORMALIZATION_NOT_PRIOR_VERIFIED";
  const p=release.pit;
  if(!p||p.status!=="CONTEMPORANEOUS_CAPTURE"||p.origin!=="INDEPENDENT_TIMESTAMPED_LOG")
    return "MISSING_CONTEMPORANEOUS_FIRST_ACCESS";
  if(!p.actual||!p.consensus||!p.firstprint)return "INCOMPLETE_PROVENANCE_CHAIN";
  for(const entry of [p.actual,p.consensus,p.firstprint]){
    if(!entry.recordId||!entry.contentHash||!entry.sourceUrl||!entry.observedAt||!entry.loggedAt)
      return "INCOMPLETE_PROVENANCE_CHAIN";
  }
  if(stamp(p.consensus.observedAt)>=scheduled||stamp(p.consensus.loggedAt)>=scheduled)
    return "CONSENSUS_NOT_PRIOR_TO_RELEASE";
  if(stamp(p.actual.observedAt)<scheduled||stamp(p.firstprint.observedAt)<scheduled)
    return "ACTUAL_OR_FIRSTPRINT_PRE_RELEASE";
  for(const entry of [p.actual,p.consensus,p.firstprint]){
    if(stamp(entry.loggedAt)<stamp(entry.observedAt))return "REVERSED_PROVENANCE_CLOCK";
    if(stamp(entry.loggedAt)>t)return "PROVENANCE_RECORDED_AFTER_DECISION";
  }
  if(stamp(p.firstprint.observedAt)>stamp(p.actual.observedAt))
    return "FIRSTPRINT_LATER_THAN_ACTUAL";
  if(stamp(p.actual.observedAt)>t||stamp(p.firstprint.observedAt)>t)
    return "EVENT_NOT_ACCESSIBLE_AT_DECISION";
  if(p.actual.contentHash===p.consensus.contentHash)return "INDEPENDENT_VINTAGE_HASHES_REQUIRED";
  return null;
}
/** Signed surprises are numerical hypotheses, not manual UP/DOWN rules.
 * Missing events stay missing. Dates and case IDs never become features.
 */
function atDecision(asof,releases,scales,eventSource){
  const now=stamp(asof);
  const features={},quarantined=[],admitted=[];
  const seen=new Set();
  for(const r of releases){
    const rt=stamp(r.scheduledUtc);
    if(rt>now||now-rt>=4*3600000)continue;
    const k=r.scheduledUtc+"/"+r.type;
    if(seen.has(k))throw Error("DUPLICATE_MACRO_COMPONENT");
    seen.add(k);
    const why=reason(r,asof,scales[r.type]);
    if(why){quarantined.push({type:r.type,reason:why});continue;}
    const name=r.type.toLowerCase()+"_surprise_z",p=r.pit;
    if(name in features)throw Error("DUPLICATE_ADMITTED_FEATURE_WAVE");
    const access=maxTime(p.actual.loggedAt,p.firstprint.loggedAt,p.consensus.loggedAt);
    features[name]={value:(r.actual-r.consensus)/scales[r.type],
      observedAt:iso(Math.max(rt,stamp(p.actual.observedAt))),
      availableAt:iso(access),firstPublishedAt:p.firstprint.observedAt,
      firstprintVerified:true,source:eventSource,kind:"EVENT"};
    admitted.push({type:r.type,sourceIds:[p.actual.recordId,p.consensus.recordId,p.firstprint.recordId],
      asof,normalizedSurprise:features[name].value});
  }
  return {features,quarantined,admitted,decisionOnly:true};
}
/** Identical S1 CORE states/configuration except admissible economic fields.
 * Compare subsequent matured 4h outcomes; never inspect outcomes in matching.
 * Historical data are retrospective: comparison is not causal or blind OOS.
 */
function pairedReplay({marketRows,releases,scales,featureNames,sourceRegistry,
  eventSource,anchorMinutes=240,horizons=[240],maxRules=16,noveltyDistance=1.25}){
  if(!Array.isArray(marketRows)||!marketRows.length)throw Error("MARKET_ROWS_REQUIRED");
  if(!sourceRegistry?.[eventSource]||sourceRegistry[eventSource].kind!=="EVENT"||
     sourceRegistry[eventSource].evidenceStatus!=="VERIFIED_PIT")
    throw Error("EVENT_SOURCE_REGISTRY_NOT_VERIFIED");
  const baseNames=featureNames.filter(x=>!x.endsWith("_surprise_z"));
  if(baseNames.length<2)throw Error("BASE_FEATURES_REQUIRED");
  const names=[...new Set([...baseNames,...[...TYPES].map(x=>x.toLowerCase()+"_surprise_z")])];
  const options={featureNames:names,horizons,sourceRegistry,anchorMinutes,maxRules,noveltyDistance};
  const withEvents=core.create(options),withoutEvents=core.create(options);
  const pending=[],stats={compared:0,withBrier:0,withoutBrier:0,
    admissibleDecisionAnchors:0,quarantined:0,admitted:0,correctWith:0,correctWithout:0};
  let previous=-Infinity;
  for(const ob of marketRows){
    const t=stamp(ob.asof);
    if(t<=previous)throw Error("ROWS_NOT_CHRONOLOGICAL");
    previous=t;
    for(let i=pending.length-1;i>=0;i--){
      const p=pending[i];
      if(t<p.due)continue;
      pending.splice(i,1);
      if(t-p.due>15*60000||!finite(ob.price)||ob.price<=0)continue;
      if(p.withP===null||p.withoutP===null)continue;
      const y=ob.price>p.price?1:0;
      stats.compared++;
      stats.withBrier+=(p.withP-y)**2;stats.withoutBrier+=(p.withoutP-y)**2;
      stats.correctWith+=((p.withP>=.5?1:0)===y)?1:0;
      stats.correctWithout+=((p.withoutP>=.5?1:0)===y)?1:0;
    }
    const evidence=atDecision(ob.asof,releases,scales,eventSource);
    stats.admitted+=evidence.admitted.length;
    stats.quarantined+=evidence.quarantined.length;
    const marketFeatures=ob.features||{};
    if(Object.keys(marketFeatures).some(k=>!baseNames.includes(k)))
      throw Error("UNDECLARED_MARKET_FEATURE");
    const full={...ob,features:{...marketFeatures,...evidence.features}};
    const market={...ob,features:{...marketFeatures}};
    const a=core.observe(withEvents,full),b=core.observe(withoutEvents,market);
    if(a.anchored!==b.anchored)throw Error("ABLATED_ANCHOR_MISMATCH");
    if(a.anchored){
      if(evidence.admitted.length)stats.admissibleDecisionAnchors++;
      const get=r=>r.forecastAtDecision.byHorizon.find(z=>z.horizonMinutes===horizons[0]);
      const x=get(a),y=get(b);
      pending.push({due:t+horizons[0]*60000,price:ob.price,
        withP:x?.ready?x.upFraction:null,withoutP:y?.ready?y.upFraction:null});
    }
  }
  return {experiment:"S1_PIT_ADMITTED_ECONOMIC_FEATURE_ABLATION",policy:"NO_TRADING",
    status:stats.admitted?"RESEARCH_COMPARISON_NOT_CAUSAL":"NO_CERTIFIED_EVENT_EVIDENCE",
    ...stats,withBrier:stats.compared?stats.withBrier/stats.compared:null,
    withoutBrier:stats.compared?stats.withoutBrier/stats.compared:null,
    learnedWith:core.rules(withEvents),learnedWithout:core.rules(withoutEvents),
    checkpointWith:core.checkpoint(withEvents),checkpointWithout:core.checkpoint(withoutEvents)};
}
module.exports={atDecision,pairedReplay,reason};
