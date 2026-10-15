"use strict";
/**
 * GOLD GUARD — scientific V2 research audit (NOT a live trade model).
 *
 * Improvements relative to V1:
 * - one original checkpoint = one training example (duplicate case IDs collapse)
 * - 96h outcome maturation guard against label lookahead
 * - explicitly differentiate an uncalibrated case fraction from actual P(down)
 * - unknown shocks, invalid causal labels, duplicate/overlapping episodes, and
 *   unavailable banking spread cannot silently become high-confidence actions
 * - every trade has explicit price, market, event, phase, future-label, and cost questions
 * - V1 execution remains frozen; V2 is an independent shadow diagnostic layer
 */
const fs=require("node:fs");
const path=require("node:path");
const {DATA,decodePinnedSource,loadFrozen,runAll,analog}=require("./engine");
const ROOT=path.resolve(__dirname,"../../..");
const ORIGIN=Date.parse("2025-12-31T21:00:00Z");
const MATURE_MS=96*3600*1000;
const FEE=0.008;
const ROUND_TRIP_COST_PCT=(1/((1-FEE)*(1-FEE))-1)*100;
const F=[
 ["r4","asof_ret4h_pct",1.2,1],
 ["rv","asof_rv4h_pct",0.65,1],
 ["ds","asof_downside_var_share4h",0.45,0.5],
 ["eff","asof_path_efficiency4h",0.55,0.5],
 ["loc","asof_close_location4h",0.55,0.4],
 ["dd4","asof_from_high_dd4h_pct",1.5,1],
 ["nq1","asof_nq_return_h1_pct",0.65,0.5],
 ["zn1","asof_zn_futures_price_return_h1_pct",0.15,0.25]
];
function n(v){if(v===""||v===undefined||v===null)return null;const a=Number(v);return Number.isFinite(a)?a:null;}
function grade(row){
 const x=row.evidence_grade||"";
 return x.startsWith("D2_")?2:x.startsWith("D1_")?1:0;
}
function frozenInput(spec){
 const bytes=fs.readFileSync(path.join(ROOT,spec.path));
 return decodePinnedSource(spec,bytes).rows;
}
function buildV2Knowledge(){
 const source=frozenInput(DATA.archive);
 const labels=Object.fromEntries(frozenInput(DATA.outcomes).map(r=>[r.case_id,r]));
 let rejects={unqualified:0,unmatured:0,noMeasuredOutcome:0,unverifiedFirstprint:0,unprovenCausality:0};
 const candidates=[];
 for(const r of source){
  if(r.onset_firstprint_verified!=="YES")rejects.unverifiedFirstprint++;
  if(r.mechanism_caused_proven!=="YES")rejects.unprovenCausality++;
  if(r.asof_price_quality!=="COMPLETE"){rejects.unqualified++;continue;}
  const at=Date.parse(r.checkpoint_utc);
  if(!Number.isFinite(at)||at+MATURE_MS>ORIGIN){rejects.unmatured++;continue;}
  const outcome=labels[r.case_id],low=n(outcome?.low96);
  if(low===null||n(outcome?.ct)<40){rejects.noMeasuredOutcome++;continue;}
  candidates.push({
   id:r.case_id,orig:r.unique_checkpoint_id||r.checkpoint_utc,
   utc:r.checkpoint_utc,ms:at,group:r.org_plot_candidate,
   grade:r.evidence_grade,rank:grade(r),
   verifiedFirstprint:r.onset_firstprint_verified==="YES",
   causalConfirmed:r.mechanism_caused_proven==="YES",
   low96:low,high96:n(outcome.high96),
   x:Object.fromEntries(F.map(([k,key])=>[k,n(r[key])]))
  });
 }
 // Two catalog rows with the same checkpoint are aliases, not new samples.
 const byOrigin=new Map();
 for(const c of candidates){
  const key=c.orig+"|"+c.utc;
  const existing=byOrigin.get(key);
  if(!existing || c.rank>existing.rank || (c.rank===existing.rank&&c.id<existing.id)){
   byOrigin.set(key,c);
  }
 }
 const unique=[...byOrigin.values()].sort((a,b)=>a.ms-b.ms||a.id.localeCompare(b.id));
 // Adjacent anchors may come from a single 96h stress episode. Distinguish
 // unique checkpoints from independent economic experiences; do not claim an
 // ESS-based probability until controls / proper episodic calibration exist.
 let episode=0,clusterEnd=-Infinity;
 for(const c of unique){
  if(c.ms>clusterEnd){episode++;clusterEnd=c.ms+MATURE_MS;}
  else clusterEnd=Math.max(clusterEnd,c.ms+MATURE_MS);
  c.episode=episode;
 }
 return {
  cases:unique,
  metrics:{
   archiveRows:source.length,eligibleAliases:candidates.length,
   uniqueCheckpoints:unique.length,duplicateAliases:candidates.length-unique.length,
   approximateOverlapping96hEpisodes:episode,
   clearlyCausalEvents:unique.filter(x=>x.causalConfirmed&&x.verifiedFirstprint).length,
   unmappedOrg:unique.filter(x=>!/^ORG\d{2}$/.test(x.group)).length,
   labelsWithFutureLowBelow3Pct:unique.filter(x=>x.low96<=-3).length,
   selectionBias:"HISTORICAL_EVENT_ANCHORS_ONLY_NO_NON_EVENT_CONTROLS",
   chronology:"ALL_FORWARD_OUTCOMES_MATURE_BEFORE_JAN2026_FIRST_DECISION",
   rejects
  }
 };
}
function scoreDedup(row,cases){
 const ranked=cases.map(c=>{
  let sum=0,wsum=0;
  for(const [key,unused,scale,w] of F){
   const a=row[key],b=c.x[key];
   if(a===null||a===undefined||b===null)continue;
   sum+=w*((a-b)/scale)**2;wsum+=w;
  }
  return {c,distance:wsum>0?Math.sqrt(sum/wsum):Infinity};
 }).filter(x=>Number.isFinite(x.distance)).sort((a,b)=>a.distance-b.distance||a.c.id.localeCompare(b.c.id)).slice(0,9);
 if(ranked.length<5)throw new Error("NOT_ENOUGH_COMPARABLE_HISTORY");
 let weightTotal=0,down=0,squares=0;
 for(const item of ranked){
  const w=1/(item.distance+0.35)**2;weightTotal+=w;squares+=w*w;
  if(item.c.low96<=-3)down+=w;
 }
 return {
  rawEventFraction:down/weightTotal,  // NOT P(down >=3%)!
  analogDistance:ranked[0].distance,
  weightEffectiveN:weightTotal**2/squares,
  neighborCount:ranked.length,
  episodeCount:new Set(ranked.map(x=>x.c.episode)).size,
  nearest:ranked.slice(0,3).map(x=>({id:x.c.id,orgCandidate:x.c.group,distance:x.distance,low96:x.c.low96})),
  probabilityCalibrated:false,
  firstprintConfirmed:false,
  economicMechanismConfirmed:false
 };
}
function diagnostic(row,position,knowledge,eventV1){
 const a=scoreDedup(row,knowledge.cases);
 const original=analog(row,loadFrozen_cached.events); // regression-only: old score, raw aliases
 const cosell=row.r4<=-1&&row.nq6!==null&&row.nq6<=-1;
 const unfamiliar=a.analogDistance>=1 && row.rv!==null && row.rv>=0.8;
 const exitPrice=row.r4<=-2;
 const postEcon="UNRESOLVED_FIRSTPRINT_OR_MECHANISM_NOT_VERIFIED";
 const phase=(unfamiliar&&cosell)?"P2_UNKNOWN_STRESS":
   cosell?"P2_CROSS_ASSET_SELLING_OBSERVED":
   row.r92>=1&&row.r276>=0?"P3_PRICE_TREND_CANDIDATE":"P0_UNRESOLVED";
 const questions=[
  {id:"Q01",question:"Karar anındaki veri tamamlanmış ve sıralı mı?",answer:"YES",evidence:["QUALIFIED_M15_PANEL","PRIOR_COMPLETED_CME_H1"],verified:true},
  {id:"Q02",question:"Altının yönü ve önceki hareketin aşaması?",answer:phase,evidence:["r4","r92","r276","rv","dd276"],verified:true},
  {id:"Q03",question:"Ekonomik neden ve ilk haber saati kanıtlı mı?",answer:postEcon,evidence:["CATALOG_FIRSTPRINT_NO","CATALOG_CAUSALITY_NO"],verified:false},
  {id:"Q04",question:"Geçmiş vaka benzerliği bağımsız ve güvenilir mi?",answer:unfamiliar?"OUT_OF_DISTRIBUTION":a.episodeCount<5?"LOW_EFFECTIVE_EPISODE_COUNT":"UNCALIBRATED_EVENT_SELECTED",evidence:["NEAREST_9_DEDUP","NO_NON_EVENT_NEGATIVES"],verified:false},
  {id:"Q05",question:"Altın ve Nasdaq'ta ortak sert satış var mı?",answer:cosell?"CROSS_MARKET_SELLING":"NOT_CONFIRMED",evidence:["r4","nq6"],verified:row.nq6!==null},
  {id:"Q06",question:"Satış ve geri girişin gerçek banka maliyeti karşılanabilir mi?",answer:"UNKNOWN_BANK_SPREAD_AND_UNCALIBRATED_FUTURE_MOVE",evidence:["0.8%_EACH_DIRECTION","BANK_BID_ASK_MISSING"],verified:false},
  {id:"Q07",question:"Mevcut portföy durumuyla risk kararı nedir?",answer:position==="GOLD"?(exitPrice||cosell&&unfamiliar?"RESEARCH_PROTECT_CANDIDATE":"HOLD_GOLD"):"HOLD_CASH_OR_REENTRY_CHECK",evidence:["POSITION","COST_GATE"],verified:false},
  {id:"Q08",question:"Bu ayın sonuçları aynı ay kararına eğitim olarak girdi mi?",answer:"NO_CROSS_MONTH_LABEL_EMBARGO",evidence:["HISTORICAL_LABEL_MATURED_AT_ORIGIN"],verified:true}
 ];
 return {
  utc:row.tt,asset:position,phase,
  observed:{goldR4Pct:row.r4,nasdaqR6Pct:row.nq6,rv4:row.rv,cosell,unfamiliar},
  sampleQuality:{libraryRows:knowledge.metrics.archiveRows,uniqueHistoricalCases:knowledge.metrics.uniqueCheckpoints,
    episodesInNine:a.episodeCount,distance:a.analogDistance,weightedEffectiveSampleCount:a.weightEffectiveN},
  analog:{legacySelectedEventFraction:original.riskScore,correctedSelectedEventFraction:a.rawEventFraction,
    selectedCases:a.nearest,probabilityCalibrated:false},
  trading:{currentAction:eventV1?.action||"OBSERVE_ONLY",protectCandidate:position==="GOLD"&&(exitPrice||cosell&&unfamiliar),
    roundTripCommissionBreakEvenPct:ROUND_TRIP_COST_PCT,bankSpreadKnown:false,
    estimatedRemainingDownsidePct:null,canProveTransactionWorthCost:false,
    vetoEconomicCausalityClaim:true},
  questions,modelStatus:"RESEARCH_SHADOW_NO_AUTOMATED_NEW_ORDERS"
 };
}
let loadFrozen_cached;
function runAudit(){
 loadFrozen_cached=loadFrozen();
 const v1=runAll().scenarios.event15m;
 const knowledge=buildV2Knowledge();
 const actions=new Map(v1.actions.map(a=>[a.utc,a]));
 const positions=new Map(v1.ledger.map(x=>[x.utc,x.position]));
 const items=loadFrozen_cached.rows.map(row=>{
  const at=actions.get(row.tt),p=positions.get(row.tt);
  return diagnostic(row,p,knowledge,at);
 });
 const critical=v1.actions.map(a=>{
  const d=items.find(x=>x.utc===a.utc);
  return {...d,action:a.action,decisionPrice:a.price,legacyReason:a.reason};
 });
 const stat=(key)=>items.filter(x=>x.observed[key]).length;
 const counts={
  validM15:items.length,unknownShockObservations:stat("unfamiliar"),
  jointlyFallingBars:stat("cosell"),
  simultaneouslyUnfamiliarAndCosell:items.filter(x=>x.observed.unfamiliar&&x.observed.cosell).length,
  eventFirstprintVerified:0,causalAttributionVerified:0,bankCostFullyKnown:false,
  additionalVerifiedProfitableSignals:0,actionChangesAuthorized:0
 };
 return {
  schema:"GOLD_GUARD_EVENT_AUDIT_V2",stage:"DIAGNOSTIC_SHADOW_ONLY",
  januaryReferenceCashUSD:v1.finalUSD,
  januaryV2ImplementedCashUSD:null,
  observedExtraValueFromEventLayerUSD:0,
  objective:"Portfolio protection against marginal >3% shocks, not daily trading.",
  archive:knowledge.metrics,
  metrics:counts,
  critical,
  riskLabels:"Selected event case fraction is not a calibrated probability of a drop.",
  requiredBeforeTrading:["TIMESTAMPED_NEWS_FIRSTPRINT","VINTAGE_MACRO_EXPECTATION",
    "NEGATIVE_NON_EVENT_CONTROLS","EPISODE_PURGED_BACKTEST",
    "BID_ASK_TRUE_BANK_QUOTES","VALIDATED_POST_ENTRY_EXPECTED_AVOIDABLE_LOSS"],
  inputHistoryFrozenBefore:"2026-01-01T00:00:00+03:00"
 };
}
module.exports={ROUND_TRIP_COST_PCT,buildV2Knowledge,scoreDedup,runAudit};
