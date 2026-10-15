"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {loadFullRows,replay,marketRegime}=require("./v8_regret_engine");
const {assess,VERSION}=require("./v8_regret_audit");
const near=(a,b,tol=.000025)=>assert.ok(Math.abs(a-b)<tol,String(a)+" vs "+String(b));
const data=loadFullRows(),rows=data.rows;

test("V8 source integrity and 2023-2026 chronological union",()=>{
 assert.equal(rows.length,6724);
 assert.equal(data.data.historicBefore2025,3213);
 assert.equal(data.data.after2025,3511);
 assert.ok(data.data.overlapVerified>1800);
 assert.equal(rows[0].tt,"2023-01-03T06:00:00.000Z");
 assert.equal(rows.at(-1).tt,"2026-09-30T21:00:00.000Z");
 for(let i=1;i<rows.length;i++)assert.ok(rows[i].ts>rows[i-1].ts);
});
test("V8 fixed chronology and commission-inclusive 2024-2025 results",()=>{
 const a=assess();
 assert.equal(a.version,VERSION);
 assert.equal(a.status,"REJECT_PROMOTION_SHADOW_ONLY");
 near(a.yearScores[0].v8FinalUSD,117.97611257516375);
 near(a.yearScores[1].v8FinalUSD,145.67462846056316);
 assert.ok(a.yearScores[0].v8FinalUSD<a.yearScores[0].passiveGoldUSD);
 assert.ok(a.yearScores[1].v8FinalUSD<a.yearScores[1].passiveGoldUSD);
});
test("2026 candidate is not better than V7 or cash; auto promotion rejected",()=>{
 const a=assess();
 near(a.controls.v8OnlineUSD,117.33227601916045);
 near(a.controls.v8RegretLearningOffUSD,117.33227601916045);
 near(a.controls.v8AllLearningFrozenUSD,103.64265250593279);
 near(a.controls.referenceV7USD,123.52954535978293);
 assert.ok(a.controls.v8OnlineUSD<a.controls.referenceV7USD);
 assert.ok(a.controls.v8OnlineUSD<119.753917);
 assert.equal(a.controls.regretFeedbackChangedTradeDecision,false);
 assert.equal(a.scientificGate.authorized,false);
 assert.equal(a.contract.automaticPromotionAuthorized,false);
 assert.equal(a.contract.liveTradeAuthorized,false);
});
test("delayed labels are never applied before 96h or 336h maturity",()=>{
 const x=replay(rows,{start:"2026-02-02T06:00:00Z",stop:"2026-03-31T12:00:00Z",initial:119.753917,includeErrors:true});
 for(const e of x.errors){
  const actualHours=(Date.parse(e.asof_matured)-Date.parse(e.origin))/3600000;
  assert.ok(actualHours+1e-8>=(e.expectedHorizon==="short"?96:336));
 }
});
test("future perturbation cannot affect decisions through June",()=>{
 const stop="2026-06-30T12:00:00Z",input={start:"2026-02-02T06:00:00Z",stop,initial:119.753917,includeDecisions:true};
 const a=replay(rows,input);
 const modified=rows.map(r=>r.tt>stop?{...r,p:r.p*1.45,c:r.c*1.45,r4:99,r1:99,r3:99}:r);
 const b=replay(modified,input);
 assert.deepEqual(a.decisions,b.decisions);
 near(a.final,b.final);
});
test("conflicting bearish stress blocks BUY at the same checkpoint",()=>{
 const a=assess();
 for(const trade of a.trades.filter(x=>x.action==="BUY")){
  assert.notEqual(trade.reason,"SLOW_DOWNSIDE_BREAK");
  assert.notEqual(trade.reason,"XAU_NQ_STRESS");
 }
 assert.deepEqual(a.trades.map(t=>t.action),["BUY","SELL","BUY","SELL"]);
});
test("overlapping opportunity records never interpreted as realizable cash gain",()=>{
 const a=assess();
 assert.ok(a.errorsByMonth.length>=7);
 const count=a.errorsByMonth.reduce((s,m)=>s+m.completedLabels,0);
 assert.ok(count>150);
 assert.equal(a.contract.macroFirstprintVerified,0);
 assert.equal(a.contract.bankBidAskIncluded,false);
 assert.equal(a.scientificGate.testNotBlind,true);
});
test("V8 read-only app endpoint does not alter legacy modes",()=>{
 const {requestHandler}=require("./server");
 function call(url,method="GET"){
  let code=0,data="";
  requestHandler({method,url},{writeHead(c){code=c},end(x){data=x}});
  return {code,body:JSON.parse(data)};
 }
 const a=call("/api/algorithm/v8/regret");
 assert.equal(a.code,200);
 assert.equal(a.body.version,VERSION);
 assert.equal(a.body.scientificGate.authorized,false);
 assert.equal(call("/api/algorithm/v8/regret","POST").code,405);
 assert.equal(call("/api/health").code,200);
});
