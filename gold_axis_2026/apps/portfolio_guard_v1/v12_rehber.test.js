"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const E=require("./v12_episodic_memory"),R=require("./v12_rehber_agent");
const {loadFullRows}=require("./v8_regret_engine"),{dataset}=require("./v11_ann_research");
const almost=(a,b,tol=.00005)=>assert.ok(Math.abs(a-b)<tol,String(a)+" vs "+String(b));
let DS;
const source=()=>DS??(DS=dataset(loadFullRows().rows));
let A;const audit=()=>A??(A=R.audit());

test("REHBER is non-ANN original memory+regret decision engine",()=>{
 assert.equal(typeof E.forecast,"function");
 assert.deepEqual(Object.keys(E.LENSES),["TREND","STRESS","STRUCTURE"]);
 assert.equal(R.VARIANTS.REHBER_CORE.adapt,true);
 assert.equal(audit().design.ANNArchitecture,false);
 assert.equal(audit().design.learnableLayers.length,3);
 assert.equal(audit().data.labeledOrigins,947);
});
test("future matured outcomes cannot enter memory or update regret",()=>{
 const memory=E.create(),now=Date.parse("2024-01-01T06:00:00Z");
 const ep={at:"2023-12-25T06:00:00Z",ts:Date.parse("2023-12-25T06:00:00Z"),
  exit14Ts:now+7*E.DAY,features:Array(14).fill(0),y:[2,4]};
 assert.throws(()=>E.appendMatured(memory,ep,now),/FUTURE/);
 assert.throws(()=>E.feedback(memory,ep,{ready:true},ep.y,now),/NOT_MATURE/);
 assert.equal(memory.memory.length,0);
});
test("daily labels are not counted as independent episode-neighbors",()=>{
 const x=source().samples.filter(q=>q.ts<Date.parse("2024-01-02T06:00:00Z"));
 const memory=E.create(),now=Date.parse("2024-01-02T06:00:00Z");
 for(const q of x)if(q.exit14Ts<now)E.appendMatured(memory,q,now);
 const prediction=E.forecast(memory,x.at(-1).features,now);
 assert.ok(prediction.ready);
 for(const lens of Object.keys(E.LENSES)){
  const l=prediction.experts[lens];
  assert.ok(l.nEffective<=l.episodes+1e-8);
  assert.ok(l.episodes<=32);
  assert.ok(l.episodes< x.length/2);
  const blocks=l.analogs.map(a=>E.blockOf(Date.parse(a.date)));
  assert.equal(new Set(blocks).size,blocks.length);
 }
});
test("2024 and 2025 negative controls remain CASH and miss passive gold",()=>{
 const d=source(),periods=[
  {start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
  {start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100}
 ];
 for(const x of periods){
  const r=R.memoryTimeline(d,{...x,variant:"REHBER_CORE"});
  almost(r.final,100);
  assert.equal(r.trades.length,0);
  assert.ok(r.learning.updates>10);
 }
});
test("2026 online memory beats frozen memory on examined data, but specialist weight/margin ablations do not",()=>{
 const a=audit(),get=n=>a.results.find(x=>x.year==="2026_FEB_SEP"&&x.variant===n);
 const main=get("REHBER_CORE"),frozen=get("REHBER_FROZEN_MEMORY");
 const frozenMargin=get("REHBER_FIXED_MARGIN"),noReliability=get("REHBER_NO_RELIABILITY");
 almost(main.final,135.66380806850964);
 almost(frozen.final,130.59159419266462);
 assert.ok(main.final>frozen.final);
 almost(main.final,frozenMargin.final);
 almost(main.final,noReliability.final);
 assert.equal(main.tradeCount,6);
 assert.equal(frozen.tradeCount,11);
 assert.ok(main.learning.updates>frozen.learning.updates);
 assert.equal(a.scientificGate.promote,false);
 assert.equal(a.scientificGate.independentBlindPeriod,false);
});
test("every REHBER filled trade has earlier timestamp than next-bank-checkpoint fill",()=>{
 const x=R.memoryTimeline(source(),{start:"2026-02-02T06:00:00Z",
  end:"2026-09-30T12:00:00Z",initial:119.753917,
  variant:"REHBER_CORE",includeDecisions:true});
 for(const t of x.trades){
  assert.ok(Date.parse(t.at)>Date.parse(t.signalAt));
  assert.ok([6,9,12].includes(new Date(t.at).getUTCHours()));
 }
 assert.equal(x.assumptions.bankFeeEachDirection,.008);
 assert.equal(x.assumptions.actualBankBidAsk,false);
 assert.ok(x.decisions.length>100);
});
test("changes in entirely future rows do not affect earlier actions or NAV",()=>{
 const rows=loadFullRows().rows,cut="2026-05-29T12:00:00Z";
 const args={start:"2026-02-02T06:00:00Z",end:cut,
  initial:119.753917,variant:"REHBER_CORE"};
 const a=R.memoryTimeline(dataset(rows),args);
 const shifted=rows.map(q=>q.tt>cut?
  {...q,p:q.p*1.75,c:q.c*1.75,r4:60,r1:50,r3:55}:q);
 const b=R.memoryTimeline(dataset(shifted),args);
 assert.deepEqual(a.trades,b.trades);almost(a.final,b.final);
});
test("V12 remains read-only and all earlier version pages stay usable",()=>{
 const {requestHandler}=require("./server");
 let status=0,body="";
 requestHandler({url:"/api/algorithm/v12/rehber",method:"GET"},
  {writeHead(c){status=c},end(x){body=x}});
 assert.equal(status,200);
 const response=JSON.parse(body);
 assert.equal(response.version,"V12_REHBER_ORIGINAL_CAUSAL_MEMORY_RESEARCH");
 assert.equal(response.scientificGate.promote,false);
 assert.equal(response.scientificGate.liveTradingAuthorized,false);
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 assert.match(html,/id="runV12Rehber"/);
 const app=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(app));
});
