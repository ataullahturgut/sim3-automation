"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const C=require("./v13_sentez_core"),R=require("./v13_sentez_run");
const near=(a,b,eps=.00004)=>assert.ok(Math.abs(a-b)<eps,String(a)+" vs "+String(b));
let cached;
const built=()=>cached??(cached=R.build());
test("hybrid consists of nonlinear trained ANN, normalized fuzzy Sugeno and recurrent gated state",()=>{
 assert.equal(C.RULES.length,6);
 assert.equal(C.ANN.INPUTS,14);
 const z=Array(14).fill(0),g=C.gatedState({trend:.5,stress:0,recovery:0},z);
 assert.ok(g.trend>.05&&g.trend<.5);
 const f=C.member(null,z,g);
 near(f.w.reduce((a,b)=>a+b,0),1,1e-9);
 const x=C.create();assert.equal(x.theta14.length,6);
 const initial=C.fuzzyPredict(f.w,x.theta14,f.x);
 C.updateConsequents(x.theta14,f,3,initial,.35);
 assert.notEqual(C.fuzzyPredict(f.w,x.theta14,f.x),initial);
});
test("14/56-day bank return targets have delayed expiry and 0.8% each-side costs",()=>{
 const b=built();
 assert.equal(b.src.rows.length,6724);
 assert.equal(b.primary.samples.length,947);
 assert.equal(b.extended.samples.filter(x=>x.y56!==null).length,918);
 const q=b.extended.samples[0];
 const bank=b.extended.bank;
 const entry=bank.find(x=>x.tt===q.entry);
 const exit=bank.find(x=>x.tt===q.exit56);
 assert.ok(exit.ts-entry.ts>=56*C.DAY);
 near(q.y56,100*((1-C.FEE)**2*exit.p/entry.p-1),1e-8);
 const dummy={exitTs:Date.parse("2025-04-01T06:00:00Z"),target:4,
  forecast:{a14:0,f14:0,net14:0}};
 assert.throws(()=>C.applyOutcome(C.create(),dummy,{now:dummy.exitTs},14),/NOT_YET_KNOWN/);
});
test("continuous capital simulation exceeds previous REHBER but not passive gold",()=>{
 const r=R.one(built(),{start:"2023-01-03T06:00:00Z",
  end:"2026-09-30T12:00:00Z",initial:100});
 near(r.final,201.59257865757388);
 near(r.passiveGoldUSD,224.27200359905993);
 assert.equal(r.tradeCount,1);
 assert.equal(r.trades[0].at,"2023-11-29T09:00:00.000Z");
 assert.equal(r.trades[0].side,"BUY");
 assert.ok(r.final<r.passiveGoldUSD);
 assert.equal(r.scientificGate.promote,false);
 assert.equal(r.assumptions.bankBidAsk,false);
});
test("2024, 2025 and 2026 same-policy net gains are not overclaimed",()=>{
 const b=built(),periods=[
  ["2024-01-02T06:00:00Z","2024-12-31T12:00:00Z",100,113.86791705945313],
  ["2025-01-07T06:00:00Z","2025-12-31T12:00:00Z",100,160.53546596024486],
  ["2026-02-02T06:00:00Z","2026-09-30T12:00:00Z",119.753917,97.29548948027461]
 ];
 for(const [start,end,initial,expected] of periods){
  const q=R.one(b,{start,end,initial,variant:"SENTEZ_HYBRID"});
  near(q.final,expected);
  assert.ok(q.final<q.passiveGoldUSD);
  assert.ok(q.labelsApplied14>30&&q.labelsApplied56>10);
  for(const tr of q.trades)assert.ok(Date.parse(tr.at)>Date.parse(tr.asOf));
 }
});
test("no future bar perturbation can alter earlier signal or costed PnL",()=>{
 const source=built().src.rows,stop="2026-05-29T12:00:00Z";
 const orig=R.build();
 const config={start:"2026-02-02T06:00:00Z",end:stop,
  initial:119.753917,variant:"SENTEZ_HYBRID",includeDiagnostics:true};
 const first=R.one(orig,config);
 const altered=source.map(r=>r.tt>stop?
  {...r,p:r.p*1.77,c:r.c*1.77,r1:99,r3:99,r4:99}:r);
 const primary=C.dataset(altered),extended=C.addExtendedLabels(primary);
 const second=R.one({src:{rows:altered},primary,extended},config);
 near(first.final,second.final);
 assert.deepEqual(first.trades,second.trades);
 assert.deepEqual(first.diagnostic,second.diagnostic);
});
test("SENTEZ research gate, ablations, and read-only API remain non-investment",()=>{
 const result=R.audit();
 assert.equal(result.version,"V13_SENTEZ_RESEARCH_AUDIT_20261016");
 assert.equal(result.experiments.length,20);
 assert.equal(result.scientificGate.promote,false);
 assert.equal(result.scientificGate.liveTrading,false);
 assert.equal(result.scientificGate.blind2026,false);
 assert.equal(result.scientificGate.bankBidAskVerified,false);
 assert.equal(result.scientificGate.macroFirstprintsVerified,0);
 assert.equal(result.scientificGate.passedBothEarlyYearsAgainstPassive,false);
 const {requestHandler}=require("./server");
 let status,body;
 requestHandler({method:"GET",url:"/api/algorithm/v13/sentez"},{
  writeHead(c){status=c},end(s){body=s}});
 assert.equal(status,200);
 assert.equal(JSON.parse(body).scientificGate.promote,false);
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 assert.match(html,/id="runV13Sentez"/);
 const app=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(app));
});
