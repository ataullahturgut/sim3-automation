"use strict";
const test=require("node:test"),A=require("node:assert/strict"),M=require("./v16_kavis_siralama");
const b=Date.parse("2020-01-01T00:00:00Z");
const t=(d,h)=>new Date(b+d*M.DAY+h*M.HR).toISOString();
const o=(d,edge=0)=>({asof:t(d,6),featureAvailableAt:t(d,6),
 position:"CASH",market:{r4:2,r1:4,r3:7,rv:1,dd:0},
 v15Expert:{availableAt:t(d,6),position:"CASH",actionEdge:edge}});
const quote=(s,d,p=100)=>M.quote(s,{at:t(d,9),price:p,isBankCheckpoint:true});
const close=(x,y)=>A.ok(Math.abs(x-y)<.000001,x+" vs "+y);
test("position-dependent V15 advice never leaks into hypothetical GOLD head updates",()=>{
 const a=M.create({minimumMaturedIntervals:100}),c=M.create({minimumMaturedIntervals:100});
 for(let d=0;d<12;d++){
   M.signal(a,o(d,12));M.signal(c,o(d,-12));
   quote(a,d,100*Math.exp(.008*d));
   quote(c,d,100*Math.exp(.008*d));
 }
 A.notDeepEqual(a.q.CASH_SWITCH.w,c.q.CASH_SWITCH.w);
 A.deepEqual(a.q.GOLD_SWITCH.w,c.q.GOLD_SWITCH.w);
 A.deepEqual(a.q.GOLD_KEEP.w,c.q.GOLD_KEEP.w);
});
test("risk-of-GOLD learner ignores hypothetical CASH-only V15 advice",()=>{
 const a=M.create({minimumMaturedIntervals:100,goldDownsideBudgetPct:1});
 const c=M.create({minimumMaturedIntervals:100,goldDownsideBudgetPct:1});
 for(let d=0;d<12;d++){
  M.signal(a,o(d,-12));M.signal(c,o(d,12));
  quote(a,d,100*Math.exp(-.02*d));
  quote(c,d,100*Math.exp(-.02*d));
 }
 A.deepEqual(a.risk.head.w,c.risk.head.w);
 close(a.risk.dual,c.risk.dual);
});
test("Bellman bootstrap uses discounted next-state value and one SWITCH fee",()=>{
 const s=M.create({gammaPerDay:.9,minimumMaturedIntervals:100});
 M.signal(s,o(0));quote(s,0,100);
 s.q.GOLD_KEEP.w[0]=10;s.q.GOLD_SWITCH.w[0]=0;
 M.signal(s,o(1));
 const r=quote(s,1,100).update;
 const sw=r.trainedHeads.find(z=>z.head==="CASH_SWITCH");
 close(sw.reward,100*Math.log(.992));
 close(sw.target,100*Math.log(.992)+9);
 const hold=r.trainedHeads.find(z=>z.head==="CASH_KEEP");
 close(hold.reward,0);close(hold.target,0);
});
test("corrupted future expert arrays and model memory are not reloadable",()=>{
 const s=M.create();M.signal(s,o(0));
 for(const corrupt of [
  x=>x.memory.trend=null,
  x=>x.pending.x[2]=null,
  x=>x.q.GOLD_KEEP.w[0]=null,
  x=>x.risk.head.w[0]=null,
  x=>x.pending.position="SHORT",
 ]){
  const x=M.save(s);corrupt(x);
  A.throws(()=>M.restore(x),/V16_.*CHECKPOINT/);
 }
});
