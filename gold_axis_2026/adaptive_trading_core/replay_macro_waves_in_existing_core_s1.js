"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / S1 — single existing CORE, real delayed labels.
 * DISCOVERY_FULL_ARCHIVE ONLY. Query result prices are transient input and are
 * NEVER persisted in a GitHub artifact. No action/BUY/SELL or future-feature.
 *
 * Input: read-only S1 independent_event_research_query_s1.buildSql(ledgerCSV)
 * and the matching retrospective macro ledger CSV. Return summary/checkpoints
 * ONLY to private caller; summary() explicitly strips all proprietary prices.
 */
const core=require("./adaptive_rule_discovery_s1");
const {csv}=require("./economic_evidence_s1");
const asof=x=>{
 if(typeof x!=="string"||!/(Z|[+-]\d\d:\d\d)$/i.test(x)||!Number.isFinite(Date.parse(x)))
   throw Error("UTC_OFFSET_REQUIRED");
 return Date.parse(x);
};
const iso=x=>new Date(x).toISOString();
const num=x=>typeof x==="number"&&Number.isFinite(x);
const safeNumber=x=>x===null||x===undefined?null:Number(x);
const scale={NFP:100,AHE:1,UNEMP:1,CPI:1};
const MKT="HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1";
const EVENT="MACRO_ARCHIVE_POST_RELEASE_PAIR_UNVERIFIED";
const CME="DATABENTO_GLBX_MDP3_OHLCV_1H_CALENDAR_CONTINUOUS_C_SOURCE_V1";
const features=["gold_1h","gold_prev_1h","nq_1h","zn_1h","cl_1h","si_1h",
  "nfp_surprise_z","ahe_surprise_z","unemp_surprise_z","cpi_surprise_z"];
function registry(){return {
 [MKT]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
 [CME]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
 [EVENT]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}
};}
function ledgerIndex(text){
 const ix=new Map();
 for(const r of csv(text)){
  if(!Object.hasOwn(scale,r.event_type)||r.pit_use!=="POST_RELEASE_ONLY"||
    r.pair_complete!=="True"||!r.actual_lineage_id||!r.consensus_lineage_id||
    !Number.isFinite(Number(r.surprise)))continue;
  const key=iso(asof(new Date(r.event_ts_utc).toISOString()))+"/"+r.event_type;
  if(ix.has(key))throw Error("DUPLICATE_LEDGER_COMPONENT");
  ix.set(key,{surprise:Number(r.surprise),actual:r.actual_lineage_id,
    consensus:r.consensus_lineage_id,quality:r.pit_use});
 }
 return ix;
}
function marketFeatures(row,t,{crossAssets=false}={}){
 const a=row.pre1h,b=row.pre2h;
 if(!num(a)||!num(b))throw Error("MARKET_STATE_MISSING");
 const m=x=>({value:Math.max(-5,Math.min(5,x/1.5)),source:MKT,
  observedAt:iso(t),availableAt:iso(t),kind:"MARKET"});
 const out={gold_1h:m(a),gold_prev_1h:m(b)};
 if(crossAssets){
  // Precommitted engineering scales (not fitted to observed gold outcomes).
  const crossScale={nq_1h:1.5,zn_1h:.35,cl_1h:2.5,si_1h:2};
  for(const [name,scale] of Object.entries(crossScale)){
    const raw=row[name],observed=row[name.replace("_1h","_known_end_utc")];
    if(raw===null||raw===undefined){
      if(observed!==null&&observed!==undefined)throw Error("INCOMPLETE_CROSS_ASSET_PAIR_"+name);
      continue;
    }
    if(!num(raw)||!observed)throw Error("INVALID_CROSS_ASSET_"+name);
    const end=asof(observed);
    if(end>t||t-end>75*60000)throw Error("STALE_OR_FUTURE_CROSS_ASSET_"+name);
    out[name]={value:Math.max(-5,Math.min(5,raw/scale)),
      observedAt:iso(end),availableAt:iso(end),source:CME,kind:"MARKET"};
  }
 }
 return out;
}
function eventFeatures(row,t,ix){
 if(!["EMP","CPI"].includes(row.release_family))throw Error("BAD_RELEASE_FAMILY");
 const release=asof(row.release_utc);
 if(t<release+60*60000||t>release+75*60000)
   throw Error("EVENT_ARRIVED_BEFORE_RESEARCH_ASSUMED_AVAILABILITY");
 const present=row.release_family==="EMP"?["NFP","AHE","UNEMP"]:["CPI"];
 const out={};
 for(const type of present){
  const d=ix.get(iso(release)+"/"+type);
  const actual=row[type.toLowerCase()];
  if(!d||!num(actual)||Math.abs(d.surprise-actual)>1e-7)
   throw Error("LEDGER_FEATURE_VALUE_OR_PROVENANCE_MISMATCH_"+type);
  const z=Math.max(-5,Math.min(5,actual/scale[type]));
  out[type.toLowerCase()+"_surprise_z"]={
    value:z,source:EVENT,kind:"EVENT",
    observedAt:iso(release),availableAt:iso(release+60*60000),
    firstprintVerified:false,researchOnly:true,assumedAccessDelayMinutes:60,
    researchReleaseConfidence:"RETROSPECTIVE_LEDGER_POST_EVENT_PAIR_UNVERIFIED",
    researchReleaseGrade:"POST_RELEASE_ONLY_NOT_PIT",
    actualLineageId:d.actual,consensusLineageId:d.consensus};
 }
 return out;
}
function validatePriceRow(r){
 for(const k of ["pre1h","pre2h","next4h","anchor_price","due_price"])
  if(!num(r[k])||(k.includes("price")&&r[k]<=0))
    throw Error("REAL_PRICE_OR_FEATURE_MISSING_"+k);
 if(Math.abs(100*Math.log(r.due_price/r.anchor_price)-r.next4h)>1e-7)
  throw Error("DUE_PRICE_RETURN_CONFLICT");
}
function observations(rows,ledgerCSV,{crossAssets=false}={}){
 if(!Array.isArray(rows)||rows.length<2)throw Error("DERIVED_ROWS_REQUIRED");
 const index=ledgerIndex(ledgerCSV);
 const waves=new Map(),anchors=new Map(),byTime=new Map();
 const counts={inputRows:rows.length,allReleaseWaves:0,
    incompleteReleaseWaves:0,completeReleaseWaves:0,
    controlAssignments:0,uniqueControls:0};
 const ctrlUsed=new Set();
 const create=(r,isEvent)=>{
  const t=asof(r.anchor_utc);
  validatePriceRow(r);
  const entry={at:t,kind:isEvent?"EVENT":"CONTROL",release:isEvent?r.release_utc:null,
    price:r.anchor_price,features:marketFeatures(r,t,{crossAssets}),
    outcome:r.next4h,duePrice:r.due_price};
  if(isEvent)Object.assign(entry.features,eventFeatures(r,t,index));
  return entry;
 };
 for(const input of rows){
  const r={...input};
  for(const k of ["nfp","ahe","unemp","cpi","pre1h","pre2h","next4h","anchor_price","due_price","nq_1h","zn_1h","cl_1h","si_1h"])
    if(r[k]!==undefined)r[k]=safeNumber(r[k]);
  if(r.kind==="EVENT"){
    if(waves.has(r.release_utc))throw Error("ONE_WAVE_ONLY_NO_DUPLICATES");
    waves.set(r.release_utc,true);
    if(r.anchor_utc===null){counts.incompleteReleaseWaves++;continue;}
    const a=create(r,true);
    if(anchors.has(a.at))throw Error("DUPLICATE_EVENT_ANCHOR");
    anchors.set(a.at,a);
    counts.completeReleaseWaves++;
  }else if(r.kind==="CONTROL"){
    counts.controlAssignments++;
    const a=create(r,false);
    if(ctrlUsed.has(a.at)){
      const old=anchors.get(a.at);
      if(!old||old.kind!=="CONTROL"||Math.abs(old.price-a.price)>1e-7||
         Math.abs(old.outcome-a.outcome)>1e-7)
        throw Error("REPEATED_CONTROL_INCONSISTENT");
      continue;
    }
    if(anchors.has(a.at))throw Error("CONTROL_SAME_TIME_AS_EVENT");
    ctrlUsed.add(a.at);anchors.set(a.at,a);
  }else throw Error("INVALID_CASE_KIND");
 }
 counts.allReleaseWaves=waves.size;
 counts.uniqueControls=ctrlUsed.size;
 function insert(t,price,anchor=null){
  const known=byTime.get(t);
  if(known){
    if(Math.abs(known.price-price)>Math.max(1e-6,price*1e-9))
      throw Error("TIME_PRICE_CONFLICT");
    if(anchor){
      if(known.anchor)throw Error("DUPLICATE_LEARNING_ANCHOR");
      known.anchor=anchor;
    }
  }else byTime.set(t,{at:t,price,anchor});
 }
 for(const a of anchors.values()){
   insert(a.at,a.price,a);
   insert(a.at+240*60000,a.duePrice);
 }
 const events=[...byTime.values()].sort((a,b)=>a.at-b.at);
 return {events,counts};
}
function make(){
 return core.create({learningMode:"DISCOVERY_FULL_ARCHIVE",featureNames:features,
    horizons:[240],anchorMinutes:240,noveltyDistance:1.25,maxRules:32,
    maxLateMinutes:15,sourceRegistry:registry()});
}
const pPrior=x=>(x.up+1)/(x.n+2);
function run(rows,ledgerCSV,{marketContext="XAU_ONLY"}={}){
 if(!["XAU_ONLY","XAU_PLUS_RECONSTRUCTED_CME"].includes(marketContext))
  throw Error("UNKNOWN_MARKET_CONTEXT");
 const {events,counts}=observations(rows,ledgerCSV,
   {crossAssets:marketContext==="XAU_PLUS_RECONSTRUCTED_CME"});
 const withEconomy=make(),marketOnly=make(),waiting=[];
 const s={settled:0,eventCases:0,controlCases:0,
   scoredBoth:0,eventScoredBoth:0,controlScoredBoth:0,
   brierE:0,brierM:0,brierPrior:0,
   correctE:0,correctM:0,correctPrior:0,
   eventBrierE:0,eventBrierM:0,eventCorrectE:0,eventCorrectM:0,
   eventCorrectPrior:0,
   readyEventForecasts:0,marketReadyEventForecasts:0,
   noEconomicForecast:0,anchoredEvents:0,anchoredControls:0,
   missedAnchorEvents:0,rejectedNoReady:0};
 const prior={n:0,up:0},eventImprovements=[];
 // Deterministic release-level bootstrap: exploratory uncertainty only.
 const confidence=values=>{
   if(values.length<10)return {n:values.length,ci95:null,mean:null};
   const average=a=>a.reduce((v,x)=>v+x,0)/a.length;
   let state=16102026;const rng=()=>{state=(1664525*state+1013904223)>>>0;
      return state/4294967296;};
   const sample=[];for(let i=0;i<1000;i++){
     let total=0;for(let j=0;j<values.length;j++)total+=values[Math.floor(rng()*values.length)];
     sample.push(total/values.length);
   }
   sample.sort((a,b)=>a-b);
   return {n:values.length,mean:average(values),ci95:[sample[24],sample[974]],
     method:"INDEPENDENT_RELEASE_CLUSTER_BOOTSTRAP_1000_EXPLORATORY"};
 };
 let last=-Infinity;
 for(const step of events){
  const t=step.at;
  if(t<=last)throw Error("NONMONOTONIC_STREAM");
  last=t;
  for(let i=waiting.length-1;i>=0;i--){
    const w=waiting[i];
    if(w.due>t)continue;
    waiting.splice(i,1);
    if(t!==w.due)throw Error("MISSING_EXACT_MATURITY_M15");
    const y=Number(step.price>w.price);
    prior.n++;prior.up+=y;
    s.settled++;
    if(w.kind==="EVENT")s.eventCases++;else s.controlCases++;
    if(w.pe!==null&&w.pm!==null){
      s.scoredBoth++;
      if(w.kind==="EVENT")s.eventScoredBoth++;
      else s.controlScoredBoth++;
      s.brierE+=(w.pe-y)**2;s.brierM+=(w.pm-y)**2;
      s.brierPrior+=(w.pr-y)**2;
      s.correctE+=Number((w.pe>=.5)===Boolean(y));
      s.correctM+=Number((w.pm>=.5)===Boolean(y));
      s.correctPrior+=Number((w.pr>=.5)===Boolean(y));
      if(w.kind==="EVENT"){
        s.eventBrierE+=(w.pe-y)**2;s.eventBrierM+=(w.pm-y)**2;
        s.eventCorrectE+=Number((w.pe>=.5)===Boolean(y));
        s.eventCorrectM+=Number((w.pm>=.5)===Boolean(y));
        s.eventCorrectPrior+=Number((w.pr>=.5)===Boolean(y));
        eventImprovements.push((w.pm-y)**2-(w.pe-y)**2);
      }
    }else s.rejectedNoReady++;
  }
  const base=step.anchor?step.anchor.features:{};
  const stripped=Object.fromEntries(Object.entries(base).filter(([k])=>!k.endsWith("_surprise_z")));
  const asofTime=iso(t);
  const build=fs=>({asof:asofTime,price:step.price,
    priceAvailableAt:asofTime,priceSource:MKT,
    barStartedAt:iso(t-15*60000),barMinutes:15,features:fs});
  const a=core.observe(withEconomy,build(base));
  const b=core.observe(marketOnly,build(stripped));
  if(a.anchored!==b.anchored)throw Error("DIFFERENT_EXPOSURE_ANCHORS");
  if(!step.anchor)continue;
  if(!a.anchored){
    if(step.anchor.kind==="EVENT")s.missedAnchorEvents++;
    continue;
  }
  const e=a.forecastAtDecision.byHorizon[0],m=b.forecastAtDecision.byHorizon[0];
  if(step.anchor.kind==="EVENT"){
    s.anchoredEvents++;
    if(e?.ready)s.readyEventForecasts++;
    else s.noEconomicForecast++;
    if(m?.ready)s.marketReadyEventForecasts++;
  }else s.anchoredControls++;
  // Prediction is immutable BEFORE the 4h target matures.
  waiting.push({due:t+240*60000,price:step.price,kind:step.anchor.kind,
    pe:e?.ready?e.upFraction:null,pm:m?.ready?m.upFraction:null,
    pr:pPrior(prior)});
 }
 if(waiting.length)throw Error("INCOMPLETE_EVENT_STREAM_PENDING_LABELS");
 const bothRules=core.rules(withEconomy),marketRules=core.rules(marketOnly);
 const economicRules=bothRules.filter(x=>Object.keys(x.center).some(k=>k.endsWith("_surprise_z")));
 return {model:"EXISTING_ADAPTIVE_RULE_DISCOVERY_S1",
  mode:"DISCOVERY_FULL_ARCHIVE",marketContext,
  strictWalkForward:false,tradePolicy:"NOT_IMPLEMENTED",
  dataQuality:"RETROSPECTIVE_LEDGER_UNVERIFIED_POST_RELEASE_ONLY",
  ...counts,stepEvents:events.length,...s,
  brierEconomic:s.scoredBoth?s.brierE/s.scoredBoth:null,
  brierMarket:s.scoredBoth?s.brierM/s.scoredBoth:null,
  brierPrior:s.scoredBoth?s.brierPrior/s.scoredBoth:null,
  eventBrierEconomic:s.eventScoredBoth?s.eventBrierE/s.eventScoredBoth:null,
  eventBrierMarket:s.eventScoredBoth?s.eventBrierM/s.eventScoredBoth:null,
  eventBrierImprovementCI95:confidence(eventImprovements),
  ruleCountEconomic:bothRules.length,ruleCountMarket:marketRules.length,
  economicRuleCount:economicRules.length,
  economicRuleMatureSupport:economicRules.map(x=>({
    dimensions:Object.keys(x.center).filter(k=>k.endsWith("_surprise_z")),
    uniqueWaveAnchors:x.anchorObservations,independentMatured4h:x.outcomes[240].n,
    observedUp:x.outcomes[240].up,observedDown:x.outcomes[240].down,
    expected4hLogPct:x.outcomes[240].meanLogPct,
    uncertainty4hPct:x.outcomes[240].standardDeviationPct
  })),
  scientificGate:"NOT_PROVEN_ARCHIVE_RESEARCH_ONLY",modelGate:"FAIL",
  evaluationCaveats:["RECONSTRUCTED_NOT_VERIFIED_PIT",
    "CONTROL_TIMESTAMPS_CHOSEN_EX_POST_RESEARCH_ONLY",
    "MATCHED_NEGATIVE_CONTROLS_CAN_BE_REUSED",
    "RETROSPECTIVE_ARCHIVE_ALREADY_RESEARCHED_NOT_BLIND_OOS",
    "NO_SIGNIFICANT_ECONOMIC_ALPHA_PROVEN"],
  // Never return serialized proprietary market price observations/checkpoints.
  coreCheckpointSerialization:"PRIVATE_ONLY_RESEARCH_MODE_NOT_FOR_STRICT_OR_PUBLIC_REPO"};
}
if(require.main===module){
 // Only private runtime inputs. stdout contains summaries and SHA256, not bars.
 const fs=require("node:fs"),crypto=require("node:crypto");
 if(process.argv.length<4||process.argv.length>5)throw Error(
   "Usage: node replay_macro_waves_in_existing_core_s1.js PRIVATE_ROWS.json PRIVATE_MACRO_LEDGER.csv [--cross-assets]");
 if(process.argv[4]&&process.argv[4]!=="--cross-assets")throw Error("UNKNOWN_MARKET_CONTEXT");
 const raw=fs.readFileSync(process.argv[2],"utf8");
 const ledger=fs.readFileSync(process.argv[3],"utf8");
 const sha=crypto.createHash("sha256").update(raw).update("\n").update(ledger)
   .digest("hex");
 const out=run(JSON.parse(raw),ledger,
   {marketContext:process.argv[4]?"XAU_PLUS_RECONSTRUCTED_CME":"XAU_ONLY"});
 console.log(JSON.stringify({runId:"S1_ARCHIVE_CORE_"+sha.slice(0,16),inputSha256:sha,
   ...out},null,2));
}
module.exports={run,observations,make,eventFeatures,registry};
