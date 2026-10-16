"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const M=require("./v20_atlas_r3_gate"),Core=require("./v18_kavis_dayaniqlilik");
const BASE=Date.parse("2020-01-01T00:00:00Z"),DAY=86400000;
const at=(i,h=6)=>new Date(BASE+i*DAY+h*3600000).toISOString();
const market=r=>({r4:r,r1:2*r,r3:3*r,rv:Math.abs(r)/2,dd:Math.min(0,r)});
function ob(s,d,r=2){return {asof:at(d),featureAvailableAt:at(d),
 position:s.inner.portfolio.position,market:market(r)};}
function bank(s,d,p){return M.quote(s,{at:at(d,9),price:p,isBankCheckpoint:true});}
test("First PREREG has alert only; independent gate needs calibrated threshold",()=>{
 const s=M.create({maxDrawdownPct:15});A.equal(s.policy.riskMode,"alert");
 A.equal(s.policy.shadowGate,"off");A.equal(s.policy.riskPenaltyLambda,0);
 A.equal(s.policy.dualAscentEta,0);
 A.throws(()=>M.create({riskMode:"constrained",maxDrawdownPct:15}),/R4_ONLY/);
 A.throws(()=>M.create({shadowGate:"gated"}),/NOT_CALIBRATED/);
 A.ok(M.create({shadowGate:"gated",gateThreshold:4}).policy.gateThreshold===4);
});
test("Blocks are 16 accepted checkpoints, at least eight complete blocks",()=>{
 const a=Array(127).fill(1),b=Array(128).fill(1),c=Array(143).fill(1);
 A.equal(M.blockEvidence(a).ready,false);
 A.equal(M.blockEvidence(b).ready,true);
 A.equal(M.blockEvidence(c).nBlocks,8);
 A.equal(M.reconstruct(b,1).gateOpen,false);
 A.equal(M.reconstruct(Array(144).fill(1),1).gateOpen,true);
});
test("Open only after two consecutive significant complete blocks",()=>{
 let d=Array(143).fill(0.5);
 let e=M.reconstruct(d,2);A.equal(e.gateOpen,false);
 d.push(0.5);
 e=M.reconstruct(d,2);A.equal(e.gateOpen,true);
});
test("Closing on two consecutive negative complete block sums independent of old signal",()=>{
 const d=Array(160).fill(1);
 A.equal(M.reconstruct(d,2).gateOpen,true);
 d.push(...Array(16).fill(-.2));
 A.equal(M.reconstruct(d,2).gateOpen,true);
 d.push(...Array(16).fill(-.2));
 A.equal(M.reconstruct(d,2).gateOpen,false);
});
test("Forge lastEvidence and confirmedStreak cannot open checkpoint",()=>{
 const a=M.create({shadowGate:"gated",gateThreshold:3});
 a.shadow.gateOpen=true;a.shadow.confirmedStreak=99;
 a.shadow.lastEvidence={ready:true,t:9000};
 const s=M.restore(M.save(a));
 A.equal(s.shadow.gateOpen,false);A.equal(s.shadow.confirmedStreak,0);
 A.equal(s.shadow.lastEvidence,null);
});
test("Forged returns and malformed pending action or audit counters rejected",()=>{
 const a=M.create();
 M.signal(a,ob(a,0));bank(a,0,100);
 for(const mutate of [
  s=>{s.shadow.relativeReturns[0]=1e6},
  s=>{s.shadow.pending={asof:"2020-01-01T00:00:00Z",actualAction:"FLY"}},
  s=>{s.audit.warnings=-9},
  s=>{s.shadow.base.cash=-1},
 ]){
  const x=M.save(a);mutate(x);A.throws(()=>M.restore(x));
 }
});
test("Default gate off = V18 and DD percent budgets do not alter AL/SAT decisions",()=>{
 for(const limit of [null,5,15,50]){
  const a=M.create({maxDrawdownPct:limit}),b=Core.create();
  for(let d=0;d<45;d++){
   const r=d<25?2:-2;
   const x=M.signal(a,ob(a,d,r)),y=Core.signal(b,
    {asof:at(d),featureAvailableAt:at(d),position:a.inner.portfolio.position,market:market(r)});
   A.equal(x.action,y.action);
   const price=100*Math.exp(.016*Math.min(d,25)-.012*Math.max(0,d-25));
   const l=bank(a,d,price),m=Core.quote(b,{at:at(d,9),price,isBankCheckpoint:true});
   A.equal(l.fill.positionAfter,m.fill.positionAfter);
  }
  A.deepEqual(a.inner.core.q,b.q);
 }
});
test("Target is shadow risk intended AFTER current action, not stale position",()=>{
 const a=M.create({shadowGate:"gated",gateThreshold:0.1});
 // Deliberately pinned true gate can only arise from legitimate returns.
 // A controlled 170-bar trend trains the independent RALLY shadow.
 for(let d=0;d<174;d++){
   const z=M.signal(a,ob(a,d,2));
   const x=bank(a,d,100*Math.exp(.02*d));
   if(z.gateActive)A.equal(x.portfolio.position,x.shadow.risk.position);
 }
 A.ok(a.audit.gateOpens>=1);
});
test("Expiring bank quote cannot create fabricated shadow returns",()=>{
 const a=M.create({core:{maxIntervalHours:4}});
 M.signal(a,ob(a,0));bank(a,0,100);
 const before=a.shadow.relativeReturns.length;
 M.signal(a,ob(a,1));
 const invalid=M.quote(a,{at:at(2,9),price:101,isBankCheckpoint:true});
 A.equal(invalid.fill,null);
 A.equal(a.shadow.relativeReturns.length,before);
 A.equal(a.shadow.pending,null);
});
test("No trading API and record includes only accepted prior bank price",()=>{
 const a=M.create();A.equal(typeof M.liveOrder,"undefined");
 const x=M.signal(a,ob(a,0));
 A.equal(x.ordersSent,0);A.equal(a.shadow.relativeReturns.length,0);
 bank(a,0,100);
 A.equal(a.shadow.relativeReturns.length,1);
});
test("Two contiguous blocks are independent of single-bar threshold scan",()=>{
 const v=Array(127).fill(1);
 A.equal(M.blockEvidence(v).ready,false);
 v.push(1);
 const e=M.blockEvidence(v);
 A.equal(e.blockSums.length,8);
 A.equal(e.blockSums[0],16);
 A.equal(M.reconstruct(v,0).gates.length,1);
});
