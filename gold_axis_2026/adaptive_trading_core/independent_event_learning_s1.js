"use strict";
/**
 * S1 / GOLD-ADAPTIVE-MODEL-APP-01:
 * Independent-release research rule learning and negative controls.
 *
 * Economically signed surprise, AFTER the release + assumed 60m availability,
 * can condition a learned outcome. No manual USD->gold directional mapping.
 *
 * DATA CONTRACT: derived archival/reconstructed macro actual-consensus and
 * XAU M15 returns; NOT CERTIFIED HISTORICAL FIRSTPRINT OR REAL OOS.
 * DISCOVERY_FULL_ARCHIVE ONLY. Never grant BUY/SELL or import a checkpoint
 * into STRICT_WALK_FORWARD. Historical archive future bars may be used ONLY
 * to score already-issued research forecasts / ex-post negative controls.
 */
const VERSION="S1_INDEPENDENT_ARCHIVE_MECHANISM_AUDIT_20261016";
const MIN_EPISODES=8,NEIGHBORS=8,BANDWIDTH=1.5;
const num=x=>typeof x==="number"&&Number.isFinite(x);
const clock=x=>{
  if(typeof x!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/.test(x)||
     !Number.isFinite(Date.parse(x)))throw Error("TIMESTAMP_OFFSET_REQUIRED");
  return Date.parse(x);
};
const iso=t=>new Date(t).toISOString();
const smooth=x=>(1+x.filter(y=>y>0).length)/(2+x.length);
const square=x=>x*x;
const clamp=x=>Math.max(-5,Math.min(5,x));
const mean=x=>x.length?x.reduce((s,z)=>s+z,0)/x.length:null;
const up=y=>y>0?1:0;
function validate(row){
  if(!row||!["EMP","CPI"].includes(row.release_family))throw Error("FAMILY_UNSUPPORTED");
  const t=clock(row.release_utc);
  if(t<Date.parse("2023-01-01Z")||t>=Date.parse("2026-01-01Z"))
    throw Error("OUTSIDE_ARCHIVE_2023_2025");
  if(row.anchor_utc===null||row.anchor_utc===undefined)return false;
  const a=clock(row.anchor_utc);
  if(a<t+60*60000||a>t+75*60000)throw Error("ANCHOR_PRE_AVAILABILITY");
  if(!num(row.pre1h)||!num(row.next4h))throw Error("MARKET_OUTCOME_INCOMPLETE");
  if(row.release_family==="EMP"&&![row.nfp,row.ahe,row.unemp].every(num))
    throw Error("MISSING_EMP_SURPRISES");
  if(row.release_family==="CPI"&&!num(row.cpi))throw Error("MISSING_CPI_SURPRISE");
  return true;
}
function vector(row,withEconomy){
  const v=[clamp(row.pre1h/1.5)];
  if(withEconomy){
    if(row.release_family==="EMP")
      v.push(clamp(row.nfp/100),clamp(row.ahe/1),clamp(row.unemp/1));
    else v.push(clamp(row.cpi/1));
  }
  return v;
}
function euclidean(a,b){
  if(a.length!==b.length)throw Error("FEATURE_SCHEMA_DRIFT");
  return Math.sqrt(a.reduce((s,x,i)=>s+square(x-b[i]),0)/a.length);
}
function probability(history,row,withEconomy){
  if(history.length<MIN_EPISODES)return null;
  const v=vector(row,withEconomy);
  const ranked=history.map(h=>({h,d:euclidean(v,vector(h,withEconomy))}))
    .sort((a,b)=>a.d-b.d).slice(0,NEIGHBORS);
  const p0=smooth(history.map(h=>h.next4h));
  const ws=ranked.map(r=>Math.exp(-.5*square(r.d/BANDWIDTH)));
  const total=ws.reduce((s,z)=>s+z,0);
  const p=(2*p0+ranked.reduce((s,r,i)=>s+ws[i]*up(r.h.next4h),0))/(2+total);
  const ret=ranked.reduce((s,r,i)=>s+ws[i]*r.h.next4h,0)/total;
  return {p,expectedLogPct:ret,historicalN:history.length,neighborN:ranked.length};
}
function confidenceDeltas(diffs){
  // IID release-cluster bootstrap. Not causal identification or exact p-value.
  if(diffs.length<10)return {mean:mean(diffs),ci95:null,method:"NOT_ENOUGH_INDEPENDENT_EPISODES"};
  let state=1701;
  const rand=()=>{state=(1664525*state+1013904223)>>>0;return state/4294967296;};
  const draw=[];
  for(let b=0;b<1000;b++){
    let total=0;
    for(let i=0;i<diffs.length;i++)total+=diffs[Math.floor(rand()*diffs.length)];
    draw.push(total/diffs.length);
  }
  draw.sort((a,b)=>a-b);
  return {mean:mean(diffs),ci95:[draw[24],draw[974]],
    method:"RELEASE_LEVEL_BOOTSTRAP_1000_EXPLORATORY_NOT_CAUSAL"};
}
/** One event = one training label; NFP/AHE/UNEMP are ONE EMP wave. */
function run(raw,{mode="DISCOVERY_FULL_ARCHIVE",proof="RETROSPECTIVE_UNVERIFIED_LEDGER"}={}){
  if(mode!=="DISCOVERY_FULL_ARCHIVE"||proof!=="RETROSPECTIVE_UNVERIFIED_LEDGER")
    throw Error("ARCHIVE_RESEARCH_CANNOT_PASS_STRICT_GATE");
  if(!Array.isArray(raw)||!raw.length)throw Error("ARCHIVE_ROWS_REQUIRED");
  const seen=new Set(),evidence=[],missing=[],controlByRelease=new Map();
  for(const row of raw){
    const t=clock(row.release_utc);
    if(row.kind==="CONTROL"){
      if(row.anchor_utc===null||!num(row.pre1h)||!num(row.next4h))
        throw Error("BAD_NEGATIVE_CONTROL");
      if(!controlByRelease.has(row.release_utc))controlByRelease.set(row.release_utc,[]);
      controlByRelease.get(row.release_utc).push(row);continue;
    }
    if(row.kind!=="EVENT")throw Error("DATASET_ROW_KIND_INVALID");
    if(seen.has(row.release_utc))throw Error("DUPLICATED_RELEASE_CLUSTER");
    seen.add(row.release_utc);
    if(!validate(row)){missing.push(row.release_utc);continue;}
    evidence.push(row);
  }
  evidence.sort((a,b)=>clock(a.anchor_utc)-clock(b.anchor_utc));
  const past=[],scored=[],eventsAnalysis=[];
  let last=-Infinity;
  for(const e of evidence){
    const at=clock(e.anchor_utc);
    if(at<=last)throw Error("NONMONOTONIC_RELEASE_ANCHOR");
    last=at;
    const familyHistory=past.filter(h=>h.release_family===e.release_family&&
      clock(h.anchor_utc)+240*60000<=at);
    const market=probability(familyHistory,e,false);
    const economic=probability(familyHistory,e,true);
    const y=up(e.next4h);
    const controls=controlByRelease.get(e.release_utc)||[];
    if(controls.length!==4)throw Error("MISSING_FOUR_MATCHED_CONTROLS");
    for(const c of controls){
      if(clock(c.anchor_utc)===at)throw Error("SELF_NEGATIVE_CONTROL");
      if(new Date(c.anchor_utc).getUTCHours()!==new Date(e.anchor_utc).getUTCHours()||
        new Date(c.anchor_utc).getUTCMinutes()!==new Date(e.anchor_utc).getUTCMinutes())
        throw Error("CLOCK_UNMATCHED_CONTROL");
    }
    const controlRet=mean(controls.map(c=>c.next4h));
    eventsAnalysis.push({family:e.release_family,
      y,ret:e.next4h,controlRet,contrast:e.next4h-controlRet,
      controlUp:controls.filter(c=>up(c.next4h)).length,
      hadOppositeControls:controls.some(c=>up(c.next4h)!==y)});
    if(market&&economic){
      const brierMarket=square(market.p-y),brierEco=square(economic.p-y);
      scored.push({year:new Date(at).getUTCFullYear(),family:e.release_family,
        forecastAt:iso(at),history:familyHistory.length,realized:y,
        marketProbability:market.p,economicProbability:economic.p,
        brierMarket,brierEco,brierPrior:square(smooth(familyHistory.map(h=>h.next4h))-y),
        correctMarket:Number((market.p>=.5)===Boolean(y)),
        correctEco:Number((economic.p>=.5)===Boolean(y)),
        improvement:brierMarket-brierEco});
    }
    // A real event is permitted to contribute ONE label only after it matures.
    // Each later release is days away; still enforce the due timestamp in history.
    past.push(e);
  }
  const getScore=a=>({count:a.length,
    correctMarket:a.reduce((s,z)=>s+z.correctMarket,0),
    correctEconomic:a.reduce((s,z)=>s+z.correctEco,0),
    brierMarket:mean(a.map(z=>z.brierMarket)),
    brierEconomic:mean(a.map(z=>z.brierEco)),
    brierPrior:mean(a.map(z=>z.brierPrior)),
    meanBrierImprovement:mean(a.map(z=>z.improvement))});
  const grouped=family=>eventsAnalysis.filter(x=>x.family===family);
  const descript=family=>{
    const a=grouped(family);
    return {events:a.length,up:a.filter(x=>x.y).length,
      down:a.filter(x=>!x.y).length,
      mean4hLogPct:mean(a.map(x=>x.ret)),
      matchedControlMeanLogPct:mean(a.map(x=>x.controlRet)),
      meanEventMinusControlPct:mean(a.map(x=>x.contrast)),
      negativeContradictions:a.filter(x=>x.hadOppositeControls).length,
      positiveEventEvenWhenControlUp:a.filter(x=>x.y&&x.controlUp>0).length};
  };
  return {version:VERSION,mode,proof,certifiedFirstprint:false,
    outputAuthority:"DESCRIPTIVE_LEARNED_HYPOTHESIS_ONLY_NO_TRADE",
    candidateReleaseWaves:seen.size,completeWaves:evidence.length,
    rejectedIncompleteWaves:missing.length,
    descriptors:{employment:descript("EMP"),inflation:descript("CPI")},
    predictive:{all:getScore(scored),
      byYear:Object.fromEntries([2023,2024,2025].map(y=>[y,getScore(scored.filter(z=>z.year===y))])),
      byFamily:Object.fromEntries(["EMP","CPI"].map(f=>[f,getScore(scored.filter(z=>z.family===f))])),
      bootstrapImprovement:confidenceDeltas(scored.map(x=>x.improvement)),
      policy:"SAME_FAMILY_FIXED_8NN_SURPRISE_AND_PRE1H_VS_PRE1H_ONLY;NO_HYPERPARAM_TUNING"},
    technicalSupport:{labelUnit:"ONE_RELEASE_WAVE",
      independence:"DISTINCT_PUBLICATION_TIME_NOT_COMPONENT",
      marketOutcomePhase:"60_MIN_AFTER_RELEASE_TO_PLUS_4_HOURS",
      matchedControls:"FOUR_SAME_UTC_CLOCK_NEAREST_PRE1H_NO_RELEASE_PLUSMINUS_24H",
      controlsUsedForPrediction:false,
      futureYearLeakageToEarlierTraining:false,
      missingReconstruction:"DO_NOT_IMPUTE",
      strictWalkForwardReady:false,modelGate:"FAIL",
      noPositionDecision:true}};
}
module.exports={VERSION,run,validate,vector,probability,confidenceDeltas};
