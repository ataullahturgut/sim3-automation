"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const {loadRows}=require("./adaptive_v7_app");
const {monthlyChoices,replayMonthlyDecision,PER_SIDE_FEE}=require("./monthly_regime_benchmark_v7");
const close=(a,b)=>assert.ok(Math.abs(a-b)<.000025,String(a)+" vs "+String(b));

test("2026 9 months: correct first/last checkpoint and costed hindsight selection",()=>{
 const m=monthlyChoices(loadRows());
 assert.equal(m.length,9);
 assert.equal(m[0].month,"2026-01");
 assert.equal(m[0].hindsightWinner,"GOLD");
 assert.equal(m[0].entryUTC,"2026-01-02T06:00:00.000Z");
 assert.equal(m.at(-1).month,"2026-09");
 assert.equal(m.at(-1).exitUTC,"2026-09-30T12:00:00.000Z");
 close(m[0].goldNetPct,15.366463103705286);
 assert.equal(PER_SIDE_FEE,.008);
});
test("monthly oracle NOT tradeable; previous month's choice IS as-of but unprofitable",()=>{
 const v=replayMonthlyDecision(loadRows());
 assert.equal(v.hindsightChoiceIsNotModelPrediction,true);
 assert.equal(v.independentBlindTest,false);
 assert.equal(v.acceptedForLiveTrading,false);
 assert.equal(v.months.length,8);
 assert.deepEqual(v.months.map(m=>m.hindsightWinner),[
  "GOLD","CASH","CASH","CASH","CASH","GOLD","GOLD","CASH"
 ]);
 assert.deepEqual(v.months.map(m=>m.laggedSelected),[
  "GOLD","GOLD","CASH","CASH","CASH","CASH","GOLD","GOLD"
 ]);
 close(v.endUSD.hindsightMonthlyOracle,145.42792374046712);
 close(v.endUSD.previousMonthWinner,112.43645437315674);
 close(v.endUSD.v7,123.52954535978293);
 close(v.endUSD.cash,119.753917);
 assert.equal(v.lagCorrectMonths,5);
 assert.equal(v.lagTotalMonths,8);
 assert.ok(v.endUSD.previousMonthWinner<v.endUSD.cash);
 for(const m of v.months){
   assert.ok(Date.parse(m.predecessorKnownUTC)<Date.parse(m.entryUTC));
 }
});
test("late-year changes cannot alter earlier monthly hindsight or past month chooser",()=>{
 const rows=loadRows(),m=replayMonthlyDecision(rows,{skipV7:true});
 const synth=rows.map(r=>r.tt>="2026-09-01"?{...r,p:r.p*1.25,c:r.c*1.25}:r);
 const x=replayMonthlyDecision(synth,{skipV7:true});
 assert.deepEqual(x.months.slice(0,7),m.months.slice(0,7));
 assert.equal(x.months[7].laggedSelected,m.months[7].laggedSelected);
});
test("read-only monthly dashboard API and HTML parse",()=>{
 const {requestHandler}=require("./server");
 let status,body;
 requestHandler({method:"GET",url:"/api/algorithm/v7/monthly-regimes"},
   {writeHead(n){status=n},end(s){body=JSON.parse(s)}});
 assert.equal(status,200);
 assert.equal(body.status,"RETROSPECTIVE_BENCHMARK_HINDSIGHT_NOT_ASOF");
 assert.equal(body.months.length,8);
 const html=fs.readFileSync(path.join(__dirname,"public","index.html"),"utf8");
 assert.match(html,/id="runMonthlyBenchmarkV7"/);
 const js=fs.readFileSync(path.join(__dirname,"public","app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(js));
 assert.match(js,/\/api\/algorithm\/v7\/monthly-regimes/);
});
