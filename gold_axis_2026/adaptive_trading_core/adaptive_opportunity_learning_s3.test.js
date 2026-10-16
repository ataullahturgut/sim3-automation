"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const m=require("./adaptive_opportunity_learning_s3"),s3=require("./adaptive_position_value_s3");
const at=(d)=>d+"T22:00:00Z",sid="SYNTHETIC";
const session=(day,price,sourceId=sid)=>({
 session:day,price,sourceId,availableAt:at(day)});
const signal=(date,price=1900,dir=1)=>({
 at:date,price,sourceId:sid,fast:{phase:"START",direction:dir}});
test("no hindsight label before 5/10/20 completed sessions",()=>{
 const s=m.create();
 const e=m.observeCandidate(s,signal("2023-01-06T17:00:00Z"));
 assert.equal(e.candidate,true);
 assert.equal(m.summary(s).audit.matured,0);
 m.closeSession(s,session("2023-01-06",1903));
 assert.equal(m.summary(s).audit.matured,0);
 for(const [d,p] of [["2023-01-09",1904],["2023-01-10",1905],
   ["2023-01-11",1906],["2023-01-12",1907]])m.closeSession(s,session(d,p));
 assert.equal(m.summary(s).audit.matured,0);
 m.closeSession(s,session("2023-01-13",1945));
 assert.equal(m.summary(s).audit.matured,1);
 assert.equal(m.summary(s).pending,2);
 assert.equal(m.summary(s).learned["FAST:TREND:UP#5"].lastMaturedAt,"2023-01-13");
});
test("research-only: no ready entry from one matured outcome",()=>{
 const s=m.create();
 m.observeCandidate(s,signal("2023-01-06T17:00:00Z"));
 for(const [d,p] of [["2023-01-06",1900],["2023-01-09",1901],["2023-01-10",1902],
  ["2023-01-11",1903],["2023-01-12",1904],["2023-01-13",2100]])m.closeSession(s,session(d,p));
 const f=m.forecast(s,{fast:{phase:"START",direction:1}});
 assert.equal(f.learnedResearchPreference,"NO_SUPPORTED_ENTRY_ADVANTAGE");
 assert.equal(f.byHorizon[0].selected,null);
 assert.equal(f.byHorizon[0].global.n,1);
});
test("broken daily source cancels unknown outcomes",()=>{
 const s=m.create();
 m.observeCandidate(s,signal("2023-01-06T17:00:00Z"));
 m.closeSession(s,session("2023-01-06",1900));
 m.closeSession(s,session("2023-01-10",1940));
 assert.equal(m.summary(s).audit.censored,0); // a one-day holiday is tolerated
 m.closeSession(s,session("2023-01-16",1990));
 assert.equal(m.summary(s).audit.censored,3); // long missing interval censors
 assert.equal(m.summary(s).audit.matured,0);
});
test("checkpoint, restored knowledge and separated simulator clock",()=>{
 const s=m.create();
 m.observeCandidate(s,signal("2023-01-06T17:00:00Z"));
 const restored=m.restore(JSON.parse(JSON.stringify(s)));
 assert.deepEqual(m.summary(restored),m.summary(s));
 const copy=m.fromKnowledge(m.knowledge(s));
 assert.equal(copy.clock,null);
 assert.equal(copy.pending.length,0);
 assert.equal(copy.audit.bars,0);
 assert.equal(copy.version,m.VERSION);
});
test("S3 emits discovery candidate without authorizing or placing an order",()=>{
 const state=s3.create({sourceRegistry:{[sid]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"}},
  shadowEnabled:true,positionResearchMode:"INTEGRATED_LONG_RESEARCH"});
 const time="2023-01-06T17:00:00Z",ob=s3.observe(state,{
  asof:time,priceAvailableAt:time,barMinutes:15,price:1863.485,
  sourceId:sid,fast:{phase:"START",direction:1},slow:null});
 assert.equal(ob.opportunityResearch.candidate,true);
 assert.equal(ob.tradeAllowed,false);
 assert.equal(ob.action,null);
 assert.equal(state.paper.buyCount,0);
 const cp=s3.restore(s3.checkpoint(state));
 assert.equal(cp.opportunity.pending.length,3);
});
