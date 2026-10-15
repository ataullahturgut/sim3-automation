"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const C=require("./v13_sentez_core"),R=require("./v14_karar_run");
let cached;
const built=()=>cached??(cached=require("./v13_sentez_run").build());
test("V14 simulates chronological bank-cost actions and matured learning",()=>{
 const r=R.one(built(),{start:"2023-01-03T06:00:00Z",
   end:"2025-12-31T12:00:00Z",initial:100});
 assert.ok(Number.isFinite(r.final)&&r.final>0);
 assert.ok(r.learned7>20&&r.learned28>10);
 assert.equal(r.scientificGate.promote,false);
 assert.equal(r.scientificGate.liveTrade,false);
 for(const tr of r.trades){
   assert.ok(Date.parse(tr.at)>Date.parse(tr.signalAt));
   assert.ok(["BUY","SELL"].includes(tr.side));
 }
});
test("future price perturbation cannot change earlier V14 trades or NAV",()=>{
 const src=built().src.rows,stop="2026-05-29T12:00:00Z";
 const one=R.one(built(),{start:"2026-02-02T06:00:00Z",end:stop,
   initial:119.753917,includeDiagnostics:true});
 const shifted=src.map(r=>r.tt>stop?{...r,p:r.p*1.43,c:r.c*1.43,
   r1:90,r3:90,r4:90}:r);
 const primary=C.dataset(shifted),extended=C.addExtendedLabels(primary);
 const two=R.one({src:{rows:shifted},primary,extended},{
   start:"2026-02-02T06:00:00Z",end:stop,
   initial:119.753917,includeDiagnostics:true});
 assert.ok(Math.abs(one.final-two.final)<.00001);
 assert.deepEqual(one.trades,two.trades);
 assert.deepEqual(one.diagnostics,two.diagnostics);
});
