"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const P=require("./chronological_ai_portfolio_v1");
const S="TEST_SYNTHETIC_RESEARCH_SOURCE";
function m(asof,action,events=[]){
 return {asof,action,createdAt:"2026-10-17T19:00:00Z",
  provenance:"GPT_ARCHIVE_RETROSPECTIVE",responseId:action+"@"+asof,
  reason:"This is an explicit SYNTHETIC MOCK note, not real GPT investment research.",
  counterEvidence:["SYNTHETIC_NEGATIVE_CONTROL"],mechanisms:["G01_A_SYNTHETIC"],
  refEventIds:events,expectedNetAdvantagePct:3.5};
}
const start="2023-01-03T10:00:00Z";
function create(records=[]){
 return P.newState({sourceId:S,firstAt:start,endAt:"2023-01-04T00:00:00Z",
  aiRecords:records});
}
function sample(n,price,phase="CONTINUE",direction=1){
 let t=Date.parse(start)+n*900000;
 return {barStart:new Date(t).toISOString(),asof:new Date(t+900000).toISOString(),
 bid:price,ask:price+0.5,
 snapshot:{s1:{ready:true,pUpPct:57,expectedLogPct:0.1},
  s2:{phase,direction,trendZ:1.4},
  s3:{researchAction:"KEEP",tradeAllowed:false}},
 modelAction:null};
}
test("no supplied GPT: do not synthesize a recommendation or a portfolio alpha claim",()=>{
 let a=create();
 P.onBar(a,sample(0,100));
 P.onBar(a,sample(1,101));
 let out=P.finish(a,{finalAt:"2023-01-03T10:30:00Z",endQuote:{bid:101}});
 assert.equal(out.aiUsed,0);
 assert.equal(out.aiResultsGrounded,false);
 assert.match(out.aiStatus,/NOT_SUPPLIED/);
 for(const arm of ["CORE","AI","HYBRID"]){
  assert.equal(out.arms[arm].finalLiquidatableUSD,100);
  assert.equal(out.arms[arm].transactions.length,0);
 }
 assert.equal(out.bankTradeAuthorized,false);
 assert.equal(out.blindOOS,false);
});
test("GPT mock BUY/SELL logged as retrospective only; executed on next completed bar, not same bar",()=>{
 const buyAt="2023-01-03T10:15:00Z",sellAt="2023-01-03T10:45:00Z";
 let a=create([m(buyAt,"BUY"),m(sellAt,"SELL",["event2"])]);
 P.onBar(a,sample(0,100));
 assert.equal(a.portfolios.AI.holding,"CASH");
 assert.ok(a.portfolios.AI.pending);
 P.onBar(a,sample(1,102));
 assert.equal(a.portfolios.AI.holding,"GOLD");
 assert.equal(a.portfolios.AI.transactions[0].executionAt,"2023-01-03T10:30:00.000Z");
 P.newEvent(a,{id:"event2",kind:"EMP",source:"SYNTHETIC_SOURCE",
  eventTime:"2023-01-03T10:30:00Z",availableAt:"2023-01-03T10:40:00Z",
  firstPrintVerified:false,consensusVintageVerified:false});
 P.onBar(a,sample(2,103,"END",-1));
 assert.equal(a.portfolios.AI.holding,"GOLD");
 assert.equal(a.portfolios.AI.pending.action,"SELL");
 P.onBar(a,sample(3,104,"CONTINUE",-1));
 const out=P.finish(a,{finalAt:"2023-01-03T11:00:00Z",endQuote:{bid:104}});
 assert.equal(out.aiUsed,2);
 assert.equal(out.arms.AI.transactions.length,2);
 assert.equal(out.arms.HYBRID.transactions.length,2);
 assert.equal(out.arms.CORE.transactions.length,0);
 assert.ok(out.arms.AI.finalLiquidatableUSD>100);
 assert.equal(out.quarantinedEconomicEvents,1);
 assert.equal(out.bankTradeAuthorized,false);
 assert.equal(out.gptRuntimeConnected,false);
});
test("future economic event cannot be cited by earlier memo",()=>{
 const memo=m("2023-01-03T10:15:00Z","BUY",["tomorrow_event"]);
 const a=create([memo]);
 P.newEvent(a,{id:"tomorrow_event",kind:"CPI",source:"SYNTHETIC",
  eventTime:"2023-01-04T12:00:00Z",availableAt:"2023-01-04T13:00:00Z",
  firstPrintVerified:false,consensusVintageVerified:false});
 assert.throws(()=>P.onBar(a,sample(0,100)),/FUTURE_OR_UNAVAILABLE_EVENT/);
});
test("retroactive GPT output must never be labeled genuinely prospective",()=>{
 assert.throws(()=>create([{
  ...m("2023-01-03T10:15:00Z","BUY"),provenance:"GPT_PROSPECTIVE"
 }]),/FUTURE_GENERATED_OUTPUT/);
});
test("duplicate bars, future slow outcome, forged model trading are rejected",()=>{
 const a=create();P.onBar(a,sample(0,100));
 assert.throws(()=>P.onBar(a,sample(0,100)),/CHRONOLOGY/);
 assert.throws(()=>P.completeSession(a,{day:"2023-01-03",
  sessionReturnPct:1,availableAt:"2023-01-04T00:00:00Z"}),/FUTURE_OR_INVALID/);
 assert.throws(()=>P.onBar(a,{...sample(1,102),modelAction:"BUY"}),/MODEL_TRADE_NOT_AUTHORIZED/);
});
test("GPT must supply immutable genuine rationale, opposing evidence, and positive net cost advantage",()=>{
 assert.throws(()=>create([{...m("2023-01-03T10:15:00Z","BUY"),
  counterEvidence:[]}]),/INVALID_OR_DUPLICATE/);
 const a=create([{...m("2023-01-03T10:15:00Z","BUY"),
  expectedNetAdvantagePct:1.0}]);
 P.onBar(a,sample(0,100));P.onBar(a,sample(1,100));
 assert.equal(a.portfolios.AI.holding,"CASH");
 assert.equal(a.portfolios.AI.transactions.length,0);
});
