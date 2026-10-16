"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const core=require("./adaptive_rule_discovery_s1");
const {researchReconstructedAtDecision,pairedReplay}=require("./economic_pit_learning_s1");
const official="https://www.bls.gov/news.release/archives/empsit_01062023.htm";
const prior="https://www.reuters.com/markets/us/strong-us-jobs-wages-growth-expected-december-2023-01-06/";
const src="RECONSTRUCTED_BLS_RESEARCH";
const release={type:"NFP",scheduledUtc:"2023-01-06T13:30:00Z",
  actual:223,officialInitialActual:223,consensus:200,
  actualEdition:"OFFICIAL_FIRST_EDITION",actualSourceUrl:official,
  consensusEdition:"DATED_PRE_RELEASE_PUBLICATION",consensusSourceUrl:prior,
  consensusPublishedAt:"2023-01-06T05:00:00Z"};
const scale={NFP:100,AHE:1,UNEMP:1,CPI:1};
const m=(at,x)=>({value:x,kind:"MARKET",source:"MKT",observedAt:at,availableAt:at});
const options={featureNames:["gold_1h","nq_1h","nfp_surprise_z"],horizons:[240],anchorMinutes:240,
  sourceRegistry:{MKT:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
   [src]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}}};
const obs=(at,event)=>({asof:at,price:1900,priceAvailableAt:at,
   barStartedAt:new Date(Date.parse(at)-15*60000).toISOString(),barMinutes:15,
   priceSource:"MKT",features:{gold_1h:m(at,.1),nq_1h:m(at,-.1),...event}});
test("Actual first edition and dated pre-release expectation enter only RESEARCH mode",()=>{
 const e=researchReconstructedAtDecision("2023-01-06T16:00:00Z",[release],scale,src);
 assert.equal(e.admitted.length,1);
 assert.equal(e.features.nfp_surprise_z.value,.23);
 assert.equal(e.features.nfp_surprise_z.firstprintVerified,false);
 assert.equal(e.strictWalkForwardAdmissible,false);
 const strict=core.create(options);
 assert.throws(()=>core.observe(strict,obs("2023-01-06T16:00:00Z",e.features)),/EVENT_SOURCE_NOT_PIT_VERIFIED/);
 const research=core.create({...options,learningMode:"DISCOVERY_FULL_ARCHIVE"});
 assert.equal(core.observe(research,obs("2023-01-06T16:00:00Z",e.features)).action,null);
 assert.ok(Object.hasOwn(core.rules(research)[0].center,"nfp_surprise_z"));
 assert.equal(core.checkpoint(research).learningMode,"DISCOVERY_FULL_ARCHIVE");
});
test("Assumed one hour latency forbids early use and cannot silently shorten",()=>{
 const at="2023-01-06T14:00:00Z";
 const e=researchReconstructedAtDecision(at,[release],scale,src);
 assert.equal(e.admitted.length,0);
 assert.equal(e.quarantined[0].reason,"CONSERVATIVE_ACCESS_DELAY_NOT_ELAPSED");
 assert.throws(()=>researchReconstructedAtDecision(at,[release],scale,src,{assumedAccessDelayMinutes:0}),/UNSAFE/);
 const late=researchReconstructedAtDecision("2023-01-06T16:00:00Z",[release],scale,src,
 {assumedAccessDelayMinutes:180});
 assert.equal(late.admitted.length,0);
});
test("Official initial snapshot and dated consensus must be independently present",()=>{
 const e=researchReconstructedAtDecision("2023-01-06T16:00:00Z",
   [{...release,officialInitialActual:260}],scale,src);
 assert.equal(e.admitted.length,0);
 assert.match(e.quarantined[0].reason,/OFFICIAL_INITIAL/);
 const q=researchReconstructedAtDecision("2023-01-06T16:00:00Z",
   [{...release,consensusPublishedAt:"2023-01-06T14:00:00Z"}],scale,src);
 assert.equal(q.admitted.length,0);
 assert.match(q.quarantined[0].reason,/PRE_RELEASE/);
});
test("Archive research status never allows strict eligible feature",()=>{
 const e=researchReconstructedAtDecision("2023-01-06T16:00:00Z",[release],scale,src);
 const r=core.create({...options,learningMode:"DISCOVERY_FULL_ARCHIVE"});
 const forged={...e.features.nfp_surprise_z,firstprintVerified:true};
 assert.throws(()=>core.observe(r,obs("2023-01-06T16:00:00Z",{nfp_surprise_z:forged})),/UNPROVEN_RECONSTRUCTED_EVENT/);
 assert.throws(()=>core.create({...options,learningMode:"MY_NEW_LIVE_MODE"}),/UNKNOWN_LEARNING_MODE/);
});
test("Paired real mode refuses accidental promotion of retrospective source to verified trading",()=>{
 const at="2023-01-06T16:00:00Z";
 assert.throws(()=>pairedReplay({marketRows:[obs(at,{})],releases:[release],scales:scale,
   featureNames:options.featureNames,sourceRegistry:options.sourceRegistry,eventSource:src,
   learningMode:"STRICT_WALK_FORWARD"}),/EVENT_SOURCE_REGISTRY_NOT_VERIFIED/);
});


test("Observed economic wave never trains on later no-event anchors",()=>{
 const at="2023-01-06T16:00:00Z",before=Date.parse(at);
 const e=researchReconstructedAtDecision(at,[release],scale,src);
 const s=core.create({...options,learningMode:"DISCOVERY_FULL_ARCHIVE"});
 core.observe(s,obs(at,e.features));
 core.observe(s,obs(new Date(before+240*60000).toISOString(),{}));
 core.observe(s,obs(new Date(before+480*60000).toISOString(),{}));
 const withEvent=core.rules(s).filter(x=>Object.hasOwn(x.center,"nfp_surprise_z"));
 const withoutEvent=core.rules(s).filter(x=>!Object.hasOwn(x.center,"nfp_surprise_z"));
 assert.equal(withEvent.length,1);
 assert.equal(withoutEvent.length,1);
 assert.equal(withEvent[0].anchorObservations,1);
 assert.equal(withEvent[0].outcomes["240"].n,1);
 assert.equal(withoutEvent[0].anchorObservations,2);
 assert.equal(s.audit.ruleMerged,0);
});
test("No trained event alpha: paired replay backs off to market-only and records the abstention",()=>{
 const start=Date.parse("2023-01-03T16:00:00Z"),rows=[];
 for(let i=0;i<20;i++){
  const at=new Date(start+i*240*60000).toISOString();
  rows.push({...obs(at,{}),price:1900+i*2+(i%3)*.1});
 }
 const r=pairedReplay({marketRows:rows,releases:[release],scales:scale,
    featureNames:options.featureNames,sourceRegistry:options.sourceRegistry,
    eventSource:src,learningMode:"DISCOVERY_FULL_ARCHIVE",
    assumedAccessDelayMinutes:60,noveltyDistance:1.25});
 assert.equal(r.admissibleDecisionAnchors,1);
 assert.equal(r.eventForecastNotReady,1);
 assert.ok(r.marketFallbackCount>=1);
 assert.equal(r.eventCompared,1);
 assert.equal(r.eventWithBrier,r.eventWithoutBrier);
 assert.equal(r.learnedWith.some(x=>Object.hasOwn(x.center,"nfp_surprise_z")),true);
 assert.equal(r.policy,"NO_TRADING");
});
