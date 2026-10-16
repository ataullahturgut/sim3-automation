"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const critic=require("./adaptive_position_value_s3");
const bridge=require("./adaptive_market_core_s1_s2");
const src="TEST_XAU",alt="TEST_OTHER";
const reg={[src]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"},
 [alt]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"}};
const start=Date.parse("2023-01-03T10:00:00Z"),STEP=900000;
function tick(i,price=1800,sourceId=src){const asof=new Date(start+i*STEP).toISOString();
 return {asof,price,sourceId,priceAvailableAt:asof,barMinutes:15,
  fast:{phase:"CONTINUE",direction:1},slow:{phase:"CONTINUE",direction:1}};}
function m15(i,p,sourceId=src){
 const t=start+i*STEP;
 return {asof:new Date(t).toISOString(),
  barStartedAt:new Date(t-STEP).toISOString(),priceAvailableAt:new Date(t).toISOString(),
  price:p,priceSource:sourceId,barMinutes:15};
}
test("Untrained critic does not issue financial action or fabricate profits",()=>{
 const s=critic.create({sourceRegistry:reg,shadowEnabled:true});
 const out=critic.observe(s,tick(0));
 assert.equal(out.proposedResearchAction,"ABSTAIN");
 assert.equal(out.action,null);assert.equal(out.tradeAllowed,false);
 assert.equal(s.audit.updates,0);
 assert.equal(critic.summary(s).portfolio.liquidatableNetUsd,100);
 assert.equal(critic.summary(s).scienceGate,"NOT_PROVEN");
});
test("Both directions pay exact bank 0.8%, 1.5936% compounded roundtrip",()=>{
 assert.equal(critic.wealthMultiplier("CASH","KEEP",1.05),1);
 assert.equal(critic.wealthMultiplier("CASH","SWITCH",1.05),.992*1.05);
 assert.equal(critic.wealthMultiplier("GOLD","KEEP",1.05),1.05);
 assert.equal(critic.wealthMultiplier("GOLD","SWITCH",1.05),.992);
 assert.ok(Math.abs(critic.summary(critic.create({sourceRegistry:reg})).roundTripFraction-.015936)<1e-10);
});
test("Mature exactly one completed next bar, not at time of prediction",()=>{
 const s=critic.create({sourceRegistry:reg});
 critic.observe(s,tick(0,2000));
 assert.equal(s.audit.updates,0);
 critic.observe(s,tick(1,2020));
 assert.equal(s.audit.updates,1);
 assert.equal(s.q["TREND:UP|TREND:UP#GOLD#KEEP"].visits,1);
 assert.ok(s.q["TREND:UP|TREND:UP#GOLD#KEEP"].value>0);
 assert.ok(s.q["TREND:UP|TREND:UP#CASH#SWITCH"].value<0.01);
});
test("Gap and source switch never synthesize a maturity, and invalidate cross-feed shadow PnL",()=>{
 const s=critic.create({sourceRegistry:reg,shadowEnabled:true});
 critic.observe(s,tick(0));critic.observe(s,tick(1,1810));
 critic.observe(s,tick(4,1820));assert.equal(s.audit.updates,1);
 assert.equal(s.audit.gaps,1);
 critic.observe(s,tick(5,5000,alt));
 assert.equal(s.audit.sourceBreaks,1);
 assert.equal(critic.summary(s).portfolio.valid,false);
 assert.equal(critic.summary(s).portfolio.liquidatableNetUsd,null);
});
test("Reject future quote, future label and nonmonotonic clock",()=>{
 const s=critic.create({sourceRegistry:reg});
 assert.throws(()=>critic.observe(s,{...tick(0),priceAvailableAt:new Date(start+STEP).toISOString()}),/NOT_YET_AVAILABLE/);
 assert.throws(()=>critic.observe(s,{...tick(0),futurePrice:3000}),/FUTURE_INPUT/);
 critic.observe(s,tick(0));
 assert.throws(()=>critic.observe(s,tick(0)),/NONMONOTONIC/);
});
test("STRICT rejects retrospective data; research cannot become live trade authority",()=>{
 const registry={X:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}};
 const s=critic.create({sourceRegistry:registry,learningMode:"STRICT_WALK_FORWARD"});
 assert.throws(()=>critic.observe(s,{...tick(0),sourceId:"X"}),/NOT_STRICT_PIT/);
 const r=critic.create({sourceRegistry:reg,shadowEnabled:true,minUpdates:16});
 for(let i=0;i<45;i++)critic.observe(r,tick(i,1800*Math.pow(1.0004,i)));
 assert.equal(critic.summary(r).liveTradeAuthorized,false);
 assert.equal(critic.summary(r).scienceGate,"NOT_PROVEN");
});
test("Checkpoint continues deterministically without resetting learning or shadow",()=>{
 const a=critic.create({sourceRegistry:reg,shadowEnabled:true,minUpdates:16});
 for(let i=0;i<22;i++)critic.observe(a,tick(i,1800*Math.pow(1.002,i)));
 const b=critic.restore(critic.checkpoint(a));
 for(let i=22;i<50;i++){
  const x=tick(i,1800*Math.pow(1.002,i));
  assert.deepEqual(critic.observe(a,x),critic.observe(b,x));
 }
 assert.deepEqual(critic.summary(a),critic.summary(b));
});
test("S3 runs inside existing S1+S2 single-core bridge with no live trade",()=>{
 const s=bridge.create({sourceId:src,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD",shadowResearch:true});
 for(let i=0;i<35;i++){
  const out=bridge.observe(s,m15(i,1800*Math.pow(1.0002,i)));
  assert.equal(out.action,null);
  assert.equal(out.tradeAllowed,false);
  assert.ok(out.positionResearch);
  assert.equal(out.positionResearch.action,null);
 }
 assert.equal(bridge.summary(s).bankTrades,0);
 assert.equal(bridge.summary(s).positionResearch.scienceGate,"NOT_PROVEN");
 const old=bridge.checkpoint(s),restored=bridge.restore(old);
 assert.deepEqual(bridge.summary(s),bridge.summary(restored));
});

test("An untrained S2 slow WARMUP does not veto fast-only research; FAST WARMUP still vetoes",()=>{
 const warm=critic.context({fast:{phase:"CONTINUE",direction:1},
  slow:{phase:"WARMUP",direction:0}});
 assert.equal(warm,"NO_SLOW|TREND:UP");
 assert.equal(critic.context({fast:{phase:"WARMUP",direction:0},
  slow:{phase:"CONTINUE",direction:1}}),"TREND:UP|UNREADY:NONE");
 const s=critic.create({sourceRegistry:reg,minUpdates:16});
 for(let i=0;i<40;i++)critic.observe(s,{...tick(i,1800),slow:{phase:"WARMUP",direction:0}});
 assert.equal(critic.summary(s).audit.decisionsByReason.FAST_PHASE_NOT_READY||0,0);
 assert.ok(critic.summary(s).audit.proposed>0);
 assert.equal(critic.summary(s).liveTradeAuthorized,false);
});
test("Decision abstention reasons are recorded without lowering support or adding trade authority",()=>{
 const s=critic.create({sourceRegistry:reg});
 const a=critic.observe(s,{...tick(0),slow:{phase:"WARMUP",direction:0}});
 assert.equal(a.researchDecisionReason,"INCOMPLETE_BAR_OR_GAP");
 const b=critic.observe(s,{...tick(1),fast:{phase:"WARMUP",direction:0}});
 assert.equal(b.researchDecisionReason,"FAST_PHASE_NOT_READY");
 assert.equal(b.action,null);assert.equal(b.tradeAllowed,false);
 assert.equal(s.audit.decisionsByReason.FAST_PHASE_NOT_READY,1);
});

test("M4 matured daily-session memory learns fee-net alternatives only when horizon finishes",()=>{
 const m=require("./adaptive_position_memory_s3");
 const s=m.create(),ds=["2023-01-02","2023-01-03","2023-01-04",
  "2023-01-05","2023-01-06","2023-01-09"];
 for(let i=0;i<ds.length;i++){
  m.completed(s,{session:ds[i],sourceId:src,
   phase:"CONTINUE",direction:1,price:1800*Math.pow(1.01,i),
   availableAt:ds[i]+"T22:00:00Z"});
  if(i<5)assert.equal(s.cohorts["TREND:UP#5"],undefined);
 }
 assert.equal(s.cohorts["TREND:UP#5"].n,1);
 const net=100*(Math.log(Math.pow(1.01,5))+2*Math.log(.992));
 assert.ok(Math.abs(s.cohorts["TREND:UP#5"].mean-net)<1e-10);
 assert.equal(m.forecast(s,"TREND:UP").byHorizon.find(z=>z.sessions===5).ready,false);
 const cp=m.restore(JSON.parse(JSON.stringify(s)));
 assert.deepEqual(cp,s);
});
test("Missing completed weekday censors outstanding multi-session labels",()=>{
 const m=require("./adaptive_position_memory_s3"),s=m.create();
 for(const day of ["2023-01-02","2023-01-03","2023-01-05"])
  m.completed(s,{session:day,sourceId:src,phase:"CONTINUE",direction:1,
   price:1800,availableAt:day+"T22:00:00Z"});
 assert.equal(s.audit.brokenSessions,1);
 assert.equal(s.audit.maturedLabels,1);
 assert.equal(s.audit.censoredLabels,7); // first 1-session label matured; seven remaining must be censored
 assert.equal(s.cohorts["TREND:UP#3"],undefined);
});
test("S3 receives actual completed S1 research forecast but never calls it economic PIT",()=>{
 const s=bridge.create({sourceId:src,sourceEvidence:"SYNTHETIC_ONLY",
    learningMode:"STRICT_WALK_FORWARD",shadowResearch:true});
 for(let i=0;i<38;i++)bridge.observe(s,m15(i,1800*Math.pow(1.001,i)));
 assert.equal(s.s3.audit.s1ResearchForecastReceived,38);
 assert.equal(s.s3.audit.economicRulesCertifiedAtDecision,0);
 assert.equal(bridge.summary(s).positionResearch.lastS1Evidence.provenance,
  "MARKET_ONLY_UNVALIDATED");
 assert.equal(bridge.summary(s).positionResearch.liveTradeAuthorized,false);
});
test("Multi-session policy cannot buy from immature or reconstructed lookahead labels",()=>{
 const s=critic.create({sourceRegistry:reg,shadowEnabled:true,
    positionResearchMode:"MULTI_SESSION_RESEARCH",minUpdates:16});
 for(let i=0;i<50;i++){
  const out=critic.observe(s,tick(i,1800*Math.pow(1.01,i)));
  assert.notEqual(out.proposedResearchAction,"BUY");
 }
 assert.equal(critic.summary(s).audit.shadowTrades,0);
 assert.equal(critic.summary(s).liveTradeAuthorized,false);
});

test("No invented bank-hour gate: researched BUY may occur at any completed quote time",()=>{
 const s=critic.create({sourceRegistry:reg,positionResearchMode:"MULTI_SESSION_RESEARCH",
  shadowEnabled:true,minUpdates:16});
 const m=require("./adaptive_position_memory_s3");
 // Thirteen observed eligible sessions generate at least eight independent-
 // in-time (but overlapping) five-session matured research labels.
 const days=["2023-01-02","2023-01-03","2023-01-04","2023-01-05",
  "2023-01-06","2023-01-09","2023-01-10","2023-01-11","2023-01-12",
  "2023-01-13","2023-01-16","2023-01-17","2023-01-18"];
 for(let i=0;i<days.length;i++)m.completed(s.sessionMemory,{
  session:days[i],sourceId:src,phase:"CONTINUE",direction:1,
  price:1800*Math.pow(1.02,i),availableAt:days[i]+"T22:00:00Z"});
 assert.equal(m.forecast(s.sessionMemory,"TREND:UP").byHorizon[2].ready,true);
 const c="NO_SLOW|TREND:UP";
 for(const a of ["KEEP","SWITCH"])s.q[c+"#CASH#"+a]={value:0,visits:40,meanTdSquare:0};
 // 20:00 UTC = 23:00 Türkiye, previously blocked by an unrequested gate.
 const p={...tick(0,2000),asof:"2023-01-19T20:00:00.000Z",
  priceAvailableAt:"2023-01-19T20:00:00.000Z",slow:{phase:"WARMUP",direction:0}};
 const first=critic.observe(s,p);
 assert.equal(first.proposedResearchAction,"ABSTAIN"); // no preceding completed bar
 const second=critic.observe(s,{...p,asof:"2023-01-19T20:15:00.000Z",
  priceAvailableAt:"2023-01-19T20:15:00.000Z",price:2000.1});
 assert.equal(second.multiSessionResearch.quoteAccepted,true);
 assert.equal(second.multiSessionResearch.executionVenueCertified,false);
 assert.equal(second.proposedResearchAction,"BUY");
 assert.equal(s.audit.shadowTrades,1);
 assert.equal(critic.summary(s).liveTradeAuthorized,false);
});

test("Economic M2 evidence enters same CORE and S3 only with registered firstprint inputs",()=>{
 const s=bridge.create({sourceId:src,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD",economicSources:{
    OFFICIAL_EVENT_TEST:{kind:"EVENT",evidenceStatus:"VERIFIED_PIT"}}});
 // The fast phase needs actual completed market observations before
 // S1 can form a fully observed event-conditioned economic prototype.
 for(let i=0;i<32;i++)bridge.observe(s,m15(i,1800+i));
 const at=start+32*STEP,asof=new Date(at).toISOString();
 const event=(availableAt,source="OFFICIAL_EVENT_TEST")=>({
   value:.55,kind:"EVENT",source,observedAt:asof,availableAt,
   firstPublishedAt:asof,firstprintVerified:true});
 const accepted=bridge.observe(s,{...m15(32,1832),economicFeatures:{
  cpi_surprise_z:event(asof)}});
 assert.equal(accepted.positionResearch.s1ResearchEvidence.provenance,
   "VERIFIED_PIT_BUT_ALPHA_NOT_PROVEN");
 assert.equal(s.s3.audit.researchEconomicContexts,1);
 assert.equal(s.s3.audit.economicRulesCertifiedAtDecision,0);
 assert.ok(s.s1.rules.some(rule=>"cpi_surprise_z" in rule.center));
 assert.equal(accepted.tradeAllowed,false);
 const t1=new Date(at+STEP).toISOString();
 assert.throws(()=>bridge.observe(s,{...m15(33,1833),economicFeatures:{
  cpi_surprise_z:event(new Date(at+2*STEP).toISOString())}}),
  /FUTURE_OR_REVERSED_FEATURE/);
 assert.throws(()=>bridge.observe(s,{...m15(34,1834),economicFeatures:{
  cpi_surprise_z:event(t1,"UNREGISTERED_EVENT")}}),
  /UNREGISTERED_FEATURE_SOURCE/);
});
test("Retrospective economic source is rejected in strict mode without claiming it was PIT",()=>{
 const s=bridge.create({sourceId:src,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD",economicSources:{
   OLD_LEDGER:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}}});
 const time=new Date(start).toISOString();
 assert.throws(()=>bridge.observe(s,{...m15(0,1800),economicFeatures:{
  nfp_surprise_z:{value:1,kind:"EVENT",source:"OLD_LEDGER",
    observedAt:time,availableAt:time,firstPublishedAt:time,
    firstprintVerified:false}}}),/EVENT_SOURCE_NOT_PIT_VERIFIED/);
 assert.equal(s.s3.audit.s1ResearchForecastReceived,0);
});

test("Integrated long learner only matures 14 and 56 calendar-day labels after their deadlines",()=>{
 const long=require("./adaptive_long_cycle_s3"),s=long.create();
 const dates=[];for(let i=0;i<95;i++){
  const d=new Date(Date.parse("2023-01-02T00:00:00Z")+i*86400000);
  if(d.getUTCDay()>=1&&d.getUTCDay()<=5)dates.push(d.toISOString().slice(0,10));
 }
 let matureBefore=false,first56Date=null;
 for(const [i,day] of dates.entries()){
  long.observe(s,{session:day,sourceId:src,price:1800*Math.pow(1.002,i),
   direction:1,phase:"CONTINUE",availableAt:day+"T22:00:00Z"});
  if(Date.parse(day+"T00:00:00Z")<Date.parse("2023-02-27T00:00:00Z")
    &&s.audit.mature56>0)matureBefore=true;
  if(s.audit.mature56>0&&!first56Date)first56Date=day;
 }
 assert.equal(matureBefore,false);
 assert.ok(first56Date>="2023-02-27");
 assert.ok(s.audit.mature14>=3);
 assert.ok(s.audit.mature56>=1);
 assert.ok(s.audit.missedUp>0);
 const cp=long.restore(JSON.parse(JSON.stringify(s)));
 assert.deepEqual(cp,s);
 const f=long.predict(cp,cp.last.state);
 assert.equal(f.provenance,"MATURED_PRIOR_SESSIONS_NOT_CAUSAL_MACRO");
});
test("Long forecasts are invariant to prices after the evaluation timestamp",()=>{
 const long=require("./adaptive_long_cycle_s3");
 const run=(outlier)=>{const s=long.create();const arr=[];
  for(let i=0;i<130;i++){
   const d=new Date(Date.parse("2023-01-02T00:00:00Z")+i*86400000);
   if(d.getUTCDay()===0||d.getUTCDay()===6)continue;
   const day=d.toISOString().slice(0,10);
   const px=i<90?1800*Math.exp(i*.001):(outlier?8000:1800)*Math.exp(i*.001);
   long.observe(s,{session:day,sourceId:src,price:px,
    direction:1,availableAt:day+"T22:00:00Z"});
   if(i===88)return {prediction:long.action(s,"CASH"),cp:JSON.stringify(s)};
  }
 };
 const left=run(false),right=run(true);
 assert.deepEqual(left,right);
});
test("Integrated long action is queued and fills next completed observation even after 17:00",()=>{
 const long=require("./adaptive_long_cycle_s3");
 const s=critic.create({sourceRegistry:reg,
  positionResearchMode:"INTEGRATED_LONG_RESEARCH",shadowEnabled:true,minUpdates:16});
 // Provide an as-of pretrained synthetic long-memory snapshot using only
 // completed sessions before the first test bar, not an arbitrary BUY rule.
 const dates=[];for(let i=0;i<214;i++){
  const d=new Date(Date.parse("2022-06-20T00:00:00Z")+i*86400000);
  if(d.getUTCDay()>0&&d.getUTCDay()<6)dates.push(d.toISOString().slice(0,10));
 }
 for(const [i,day] of dates.entries())long.observe(s.longCycle,{
  session:day,sourceId:src,price:1800*Math.exp(i*.004),
  direction:1,availableAt:day+"T22:00:00Z"});
 const base=Date.parse("2023-01-19T20:00:00Z");
 const p=(n)=>({...tick(0,2200),asof:new Date(base+900000*n).toISOString(),
   priceAvailableAt:new Date(base+900000*n).toISOString(),price:2200+2*n});
 const first=critic.observe(s,p(0));
 assert.equal(first.proposedResearchAction,"ABSTAIN");
 const second=critic.observe(s,p(1));
 assert.equal(second.action,null);
 assert.equal(second.tradeAllowed,false);
 assert.equal(second.proposedResearchAction,"BUY");
 assert.equal(s.paper.holding,"CASH");
 const third=critic.observe(s,p(2));
 assert.equal(s.paper.holding,"GOLD");
 assert.equal(s.audit.executedNextBar,1);
 assert.equal(third.at,"2023-01-19T20:30:00.000Z");
 assert.equal(critic.summary(s).liveTradeAuthorized,false);
});
