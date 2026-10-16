"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01: one mathematical MODEL composition.
 * Existing S1 rule CORE + S2 price-lifecycle component; one timestamp, one
 * source registry and one checkpoint. S3 is a research-only shadow critic,
 * not a deployed AL/SAT policy or bank trade interface.
 * S1 research macro is NOT silently imported; S2 is price-only at this stage.
 */
const s1=require("./adaptive_rule_discovery_s1");
const s2=require("./adaptive_phase_lifecycle_s2");
const slow=require("./adaptive_slow_lifecycle_s2");
const s3=require("./adaptive_position_value_s3");
const VERSION="GOLD_ADAPTIVE_S1_S2_SLOW_S3_RESEARCH_BRIDGE_20261016";
const SCHEMA=["phase_trend_z","phase_retracement_norm","phase_direction","phase_age_norm",
 "slow_trend_z","slow_direction","slow_age_norm","slow_end_5session"];
const cp=x=>JSON.parse(JSON.stringify(x));
const iso=x=>new Date(x).toISOString();
const clip=x=>Math.max(-5,Math.min(5,x));
function create({sourceId,sourceIds=null,sourceEvidence="RECONSTRUCTED_MARKET_ASOF",
 learningMode="DISCOVERY_FULL_ARCHIVE",shadowResearch=false}={}){
 if(typeof sourceId!=="string"||!sourceId)
  throw Error("MODEL_SOURCE_ID_REQUIRED");
 if(!["RECONSTRUCTED_MARKET_ASOF","VERIFIED_PIT","SYNTHETIC_ONLY"].includes(sourceEvidence))
  throw Error("MODEL_SOURCE_EVIDENCE_INVALID");
 const known=sourceIds??[sourceId];
 if(!Array.isArray(known)||!known.length||known.some(x=>typeof x!=="string"||!x)||
   !known.includes(sourceId)||new Set(known).size!==known.length)
  throw Error("MODEL_SOURCE_ALLOWLIST_INVALID");
 const sourceRegistry=Object.fromEntries(known.map(id=>[id,
   {kind:"MARKET",evidenceStatus:sourceEvidence}]));
 return {version:VERSION,sourceId,allowedSources:known.slice(),
  mode:learningMode,
  s1:s1.create({learningMode,featureNames:SCHEMA,sourceRegistry,
   horizons:[240],anchorMinutes:240,maxRules:16}),
  s2:s2.create({learningMode,sourceRegistry}),
  slow:slow.create({sourceRegistry}),
  s3:s3.create({sourceRegistry,learningMode,shadowEnabled:shadowResearch}),lastSlow:null,
  audit:{observed:0,contextReady:0,phaseTransitions:0,slowAccepted:0,slowRejected:0}};
}
function features(p,t,id){
 if(p.trendZ===null||p.phase==="WARMUP"||p.phase==="GAP")return {};
 const market=value=>({value:clip(value),kind:"MARKET",source:id,
  observedAt:iso(t),availableAt:iso(t)});
 return {phase_trend_z:market(p.trendZ),
  phase_retracement_norm:market(p.retracementNorm??0),
  phase_direction:market(p.direction),
  phase_age_norm:market(p.episodeAgeMinutes/240)};
}
/** Commit a daily feature ONLY after UTC 22:00 session has closed.
 * Calling late never rewrites any already-issued S1 forecast.
 */
function observeSlowSession(s,session){
 if(s.version!==VERSION)throw Error("MODEL_BRIDGE_CHECKPOINT_VERSION");
 if(!(s.allowedSources??[s.sourceId]).includes(session.source_id))
  throw Error("MODEL_UNDECLARED_SLOW_SOURCE");
 const out=slow.observe(s.slow,session);
 if(out.phase==="REJECTED_SESSION"){
  s.lastSlow=null;s.audit.slowRejected++;
 }else{
  s.lastSlow={observedAt:new Date(Date.parse(session.session+"T22:00:00Z")).toISOString(),
   source:session.source_id,phase:out.phase,age:out.episodeAgeSessions,
   trendZ:out.trendZ,direction:out.direction,
   pEnd5:out.hazards?.[5]?.ready?out.hazards[5].pEnd:null};
  s.audit.slowAccepted++;
 }
 return {session:session.session,phase:out.phase,
  action:null,tradeAllowed:false};
}
function observe(s,bar){
 if(s.version!==VERSION)throw Error("MODEL_BRIDGE_CHECKPOINT_VERSION");
 if(!(s.allowedSources??[s.sourceId]).includes(bar.priceSource))
  throw Error("MODEL_UNDECLARED_SOURCE");
 // Price is validated by S2 and by S1; source and complete-bar time match.
 const p=s2.observe(s.s2,bar);
 const t=Date.parse(bar.asof),fs=features(p,t,bar.priceSource);
 const hist=s.lastSlow,market=value=>({value:clip(value),
  kind:"MARKET",source:bar.priceSource,
  observedAt:hist.observedAt,availableAt:hist.observedAt});
 // Session UTC 22:00 completion must be observed before this M15 decision.
 // Never use another source's trend across feed transition.
 if(hist&&hist.source===bar.priceSource&&Date.parse(hist.observedAt)<=t&&
  t-Date.parse(hist.observedAt)<=4*86400000&&
  hist.trendZ!==null&&hist.phase!=="WARMUP"&&
  hist.phase!=="REJECTED_SESSION"){
  Object.assign(fs,{slow_trend_z:market(hist.trendZ),
   slow_direction:market(hist.direction),
   slow_age_norm:market(hist.age/10)});
  if(hist.pEnd5!==null)fs.slow_end_5session=market(hist.pEnd5);
 }
 const q=s1.observe(s.s1,{...bar,features:fs});
 const v=s3.observe(s.s3,{asof:bar.asof,price:bar.price,
  priceAvailableAt:bar.priceAvailableAt,barMinutes:bar.barMinutes,
  sourceId:bar.priceSource,
  fast:{phase:p.phase,direction:p.direction},
  slow:hist&&hist.source===bar.priceSource&&
   Date.parse(hist.observedAt)<=t&&t-Date.parse(hist.observedAt)<=4*86400000&&
   !["WARMUP","REJECTED_SESSION","GAP"].includes(hist.phase)?
    {phase:hist.phase,direction:hist.direction}:null});
 s.audit.observed++;
 if(Object.keys(fs).length>=2)s.audit.contextReady++;
 if(p.phase==="START"||p.phase==="END")s.audit.phaseTransitions++;
 return {asof:bar.asof,lifecycle:p,ruleDiscovery:q,
  positionResearch:v,action:null,tradeAllowed:false};
}
function summary(s){
 return {version:VERSION,mode:s.mode,
  lifecycle:s2.summary(s.s2),slowLifecycle:slow.summary(s.slow),
  positionResearch:s3.summary(s.s3),ruleDiscovery:{
   observations:s.s1.audit.observations,anchors:s.s1.audit.anchors,
   matureLabels:s.s1.audit.labelsMatured,learnedRules:s1.rules(s.s1).length},
  audit:cp(s.audit),tradeAllowed:false,bankTrades:0};
}
function checkpoint(s){return cp(s);}
function restore(data){
 const s=cp(data);
 if(s.version!==VERSION)throw Error("MODEL_BRIDGE_CHECKPOINT_VERSION");
 if(!s.allowedSources)s.allowedSources=[s.sourceId];
 s.s1=s1.restore(s.s1);s.s2=s2.restore(s.s2);
 if(!s.slow)throw Error("MODEL_MISSING_SLOW_LAYER_CHECKPOINT");
 s.slow=slow.restore(s.slow);
 if(!s.s3)throw Error("MODEL_MISSING_S3_RESEARCH_CHECKPOINT");
 s.s3=s3.restore(s.s3);
 return s;
}
module.exports={VERSION,create,observe,observeSlowSession,summary,checkpoint,restore,SCHEMA};