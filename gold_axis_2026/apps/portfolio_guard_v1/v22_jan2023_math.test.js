"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const V=require("./v22_jan2023_math");
const MS=900000,start=Date.parse("2023-01-03T00:00:00Z");
const make=(n,drift=.0004)=>Array.from({length:n},(_,i)=>({
 t:start+i*MS,tt:new Date(start+i*MS).toISOString(),
 close:1800*Math.exp(drift*i),open:1800*Math.exp(drift*i-.0001)}));
test("January-only price source and strict past feature vector",()=>{
 const a=make(130),x=V.vector(a,64);
 assert.equal(x.length,8);
 const mutated=structuredClone(a);mutated[65].close*=10;
 assert.deepEqual(V.vector(mutated,64),x);
 assert.equal(V.vector(a,63),null);
 a[20].t+=60000;
 assert.equal(V.vector(a,64),null);
});
test("Prediction labels mature ONLY after their forward horizon",()=>{
 const a=make(130),s=V.create(),x=V.vector(a,64);
 for(let j=0;j<s.heads.length;j++)s.pending[j].push({
 start:64,due:64+s.heads[j].h,originPrice:a[64].close,
 x,pred:0});
 V.mature(s,a,64);
 assert.equal(s.totalTargets,0);
 V.mature(s,a,65);
 assert.equal(s.heads[0].n,1);
 assert.equal(s.heads[1].n,0);
 V.mature(s,a,68);
 assert.equal(s.heads[1].n,1);
 V.mature(s,a,80);
 assert.equal(s.heads[2].n,1);
 V.mature(s,a,128);
 assert.equal(s.heads[3].n,1);
 assert.ok(s.totalNonzeroUpdates>=4);
 assert.ok(s.heads.some(h=>h.w.some(w=>w!==0)));
});
test("Hedge changes weights only from matured labeled prediction errors",()=>{
 const s=V.create(),x=[1,0,0,0,0,0,0,0];
 for(const h of s.heads){h.n=10;h.loss=h.h===1?.2:2;}
 const sc=V.score(s,x);
 assert.equal(sc.ready,true);
 assert.equal(sc.predicts.length,4);
 const a=make(130);
 V.mature(s,a,64);
 assert.ok(s.metaWeights[0]>s.metaWeights[1]);
});
test("Bank windows only weekday 09–17 TR",()=>{
 assert.equal(V.bankWindow(Date.parse("2023-01-03T06:00:00Z")),true);
 assert.equal(V.bankWindow(Date.parse("2023-01-03T13:45:00Z")),true);
 assert.equal(V.bankWindow(Date.parse("2023-01-03T14:00:00Z")),false);
 assert.equal(V.bankWindow(Date.parse("2023-01-07T08:00:00Z")),false);
});
test("BUY and SELL incur one 0.8% leg each, WAIT no leg",()=>{
 const s=V.create();
 V.execute(s,"BUY",100,100,{t:start,edge:2,risk:.1});
 assert.equal(s.trades.length,1);assert.ok(Math.abs(s.units-.992)<1e-12);
 assert.equal(s.fees,.8);
 V.execute(s,"SELL",100,117,{t:start+17*MS,edge:-2,risk:.1});
 assert.ok(Math.abs(s.cash-98.4064)<1e-9);
 assert.ok(Math.abs(s.fees-(.8+.7936))<1e-9);
});
test("Only 2023 January accepted; original mathematical updates measurable",()=>{
 const arr=make(180,.0001),r=V.forward(arr);
 assert.equal(r.metadata.monthCount,1);
 assert.equal(r.metadata.usingOtherMarketFeatures,false);
 assert.ok(r.totalTargetsMatured>0);
 assert.ok(r.nonzeroMathematicalUpdates>0);
 assert.equal(r.benchCashUSD,100);
 assert.equal(r.feePerSide,.008);
 assert.equal(r.heads.length,4);
 const bad=make(180);bad.at(-1).tt="2023-02-02T00:00:00.000Z";
 bad.at(-1).t=Date.parse(bad.at(-1).tt);
 assert.throws(()=>V.forward(bad),/OUTSIDE_JAN_2023/);
});
test("Initial source-only parsing never references NASDAQ news ETF",()=>{
 const src="tt,close,p,r4,nq1\n2023-01-03T00:00:00.000Z,1800,1801,999,999";
 const r=V.parseCsv(src);
 assert.deepEqual(Object.keys(r[0]).sort(),["t","tt","close","open"].sort());
});
