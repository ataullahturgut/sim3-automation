"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01: one mathematical MODEL composition.
 * Existing S1 rule CORE + S2 price-lifecycle component; one timestamp, one
 * source registry and one checkpoint. No AL/SAT or policy/portfolio code.
 * S1 research macro is NOT silently imported; S2 is price-only at this stage.
 */
const s1=require("./adaptive_rule_discovery_s1");
const s2=require("./adaptive_phase_lifecycle_s2");
const VERSION="GOLD_ADAPTIVE_S1_S2_RESEARCH_BRIDGE_20261016";
const SCHEMA=["phase_trend_z","phase_retracement_norm","phase_direction","phase_age_norm"];
const cp=x=>JSON.parse(JSON.stringify(x));
const iso=x=>new Date(x).toISOString();
const clip=x=>Math.max(-5,Math.min(5,x));
function create({sourceId,sourceEvidence="RECONSTRUCTED_MARKET_ASOF",
 learningMode="DISCOVERY_FULL_ARCHIVE"}={}){
 if(typeof sourceId!=="string"||!sourceId)
  throw Error("MODEL_SOURCE_ID_REQUIRED");
 if(!["RECONSTRUCTED_MARKET_ASOF","VERIFIED_PIT","SYNTHETIC_ONLY"].includes(sourceEvidence))
  throw Error("MODEL_SOURCE_EVIDENCE_INVALID");
 const sourceRegistry={[sourceId]:{kind:"MARKET",evidenceStatus:sourceEvidence}};
 return {version:VERSION,sourceId,
  mode:learningMode,
  s1:s1.create({learningMode,featureNames:SCHEMA,sourceRegistry,
   horizons:[240],anchorMinutes:240,maxRules:16}),
  s2:s2.create({learningMode,sourceRegistry}),
  audit:{observed:0,contextReady:0,phaseTransitions:0}};
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
function observe(s,bar){
 if(s.version!==VERSION)throw Error("MODEL_BRIDGE_CHECKPOINT_VERSION");
 if(bar.priceSource!==s.sourceId)throw Error("MODEL_SOURCE_ID_DRIFT");
 // Price is validated by S2 and by S1; source and complete-bar time match.
 const p=s2.observe(s.s2,bar);
 const t=Date.parse(bar.asof),fs=features(p,t,s.sourceId);
 const q=s1.observe(s.s1,{...bar,features:fs});
 s.audit.observed++;
 if(Object.keys(fs).length>=2)s.audit.contextReady++;
 if(p.phase==="START"||p.phase==="END")s.audit.phaseTransitions++;
 return {asof:bar.asof,lifecycle:p,ruleDiscovery:q,
  action:null,tradeAllowed:false};
}
function summary(s){
 return {version:VERSION,mode:s.mode,
  lifecycle:s2.summary(s.s2),ruleDiscovery:{
   observations:s.s1.audit.observations,anchors:s.s1.audit.anchors,
   matureLabels:s.s1.audit.labelsMatured,learnedRules:s1.rules(s.s1).length},
  audit:cp(s.audit),tradeAllowed:false,bankTrades:0};
}
function checkpoint(s){return cp(s);}
function restore(data){
 const s=cp(data);
 if(s.version!==VERSION)throw Error("MODEL_BRIDGE_CHECKPOINT_VERSION");
 s.s1=s1.restore(s.s1);s.s2=s2.restore(s.s2);
 return s;
}
module.exports={VERSION,create,observe,summary,checkpoint,restore,SCHEMA};