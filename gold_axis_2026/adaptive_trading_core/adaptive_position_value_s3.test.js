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
 assert.equal(s.audit.censoredLabels,8); // first two sessions: 3+4 pending after one horizon matures
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
