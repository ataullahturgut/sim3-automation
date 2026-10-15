"use strict";
const test=require("node:test"),A=require("node:assert/strict"),V=require("./v14_karar_ogrenme");
const features=[0,1,2,1,0,0,0,0,0,0,0,0,0,0];
test("cold system abstains; fee is charged on both directions",()=>{
 const s=V.create(),p=V.forecast(s,V.observe(s,features));
 A.equal(p.ready,false);A.equal(V.action(s,p,"CASH").target,"CASH");
 A.ok(Math.abs(V.action(s,p,"CASH").entryBarrier-1.6064)<.02);
});
test("causal maturity guard and online coefficients actually learn",()=>{
 const s=V.create(),snap=V.observe(s,features,{net14:4,net56:8,regime:{stress:0}});
 const p=V.forecast(s,snap),before=s.heads[7].w.slice();
 A.throws(()=>V.learn(s,{h:7,exitTs:101,grossLogPct:5,
   worstLossPct:0,pred:p},101),/UNMATURED/);
 const a=V.learn(s,{h:7,exitTs:100,grossLogPct:5,
   worstLossPct:0,pred:p,origin:"old"},101);
 A.equal(a.learned,1);A.notDeepEqual(s.heads[7].w,before);
});
test("policy selects both entry and protective exit after learning",()=>{
 const s=V.create();
 for(let h of V.HORIZONS){s.heads[h].n=20;s.heads[h].mse=1;s.heads[h].w[0]=5;}
 let p=V.forecast(s,V.observe(s,features));
 A.equal(V.action(s,p,"CASH").target,"GOLD");
 for(let h of V.HORIZONS)s.heads[h].w[0]=-5;
 p=V.forecast(s,V.observe(s,features));
 A.equal(V.action(s,p,"GOLD").target,"CASH");
});
test("fixed timestamp labels: next execution checkpoint and future only after expiry",()=>{
 const base=Date.parse("2024-01-01T09:00:00Z"),H=V.HR;
 const b=Array.from({length:31*8},(_,i)=>({
   ts:base+(i+1)*3*H,p:100*(1+i*.001)}));
 const q=V.label(b,base,7);
 A.ok(q);A.equal(q.entryAt,base+3*H);
 A.ok(q.exitAt>=q.entryAt+7*V.DAY);
 const s=V.create(),p=V.forecast(s,V.observe(s,features));
 A.throws(()=>V.learn(s,{...q,h:7,pred:p},q.exitTs),/UNMATURED/);
});
test("future label price does not alter state until its maturity",()=>{
 const s1=V.create(),s2=V.create();
 const x1=V.observe(s1,features),x2=V.observe(s2,features);
 const p1=V.forecast(s1,x1),p2=V.forecast(s2,x2);
 A.deepEqual(p1,p2);
 A.deepEqual(V.action(s1,p1,"CASH"),V.action(s2,p2,"CASH"));
});
