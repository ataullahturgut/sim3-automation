"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const M=require("./v20_atlas_r2_shadow"),V18=require("./v18_kavis_dayaniqlilik");
const t0=Date.parse("2020-01-01T00:00:00Z"),D=864e5,H=36e5;
const at=(i,h=6)=>new Date(t0+i*D+h*H).toISOString();
function obs(s,i,r=1){return {asof:at(i),featureAvailableAt:at(i),
 position:s.inner.portfolio.position,
 market:{r4:r,r1:2*r,r3:3*r,rv:1,dd:Math.min(0,r)}};}
function q(s,i,p,fee=.008){return M.quote(s,{at:at(i,9),price:p,
 bankFeePerSide:fee,isBankCheckpoint:true});}
function hardForce(core,p){
 core.learned=100;
 for(const [k,h] of Object.entries(core.q)){
  if(!h||!Array.isArray(h.w))continue;
  h.w.fill(0);h.w[0]=k.startsWith(p+"_")?
    (k.endsWith("_KEEP")?40:-40):0;
 }
 for(const [k,h] of Object.entries(core.qb)){
  if(!h||!Array.isArray(h.w))continue;
  h.w.fill(0);h.w[0]=k.startsWith(p+"_")?
    (k.endsWith("_KEEP")?40:-40):0;
 }
}
test("R2 default is alert-only and no mandatory sell/auto bank API",()=>{
 const s=M.create({maxDrawdownPct:15});
 A.equal(s.policy.riskMode,"alert");
 A.equal(typeof M.placeOrder,"undefined");
 A.equal(s.inner.core.config.liveTrade,false);
 A.throws(()=>M.create({riskMode:"soft_penalty"}),/EXPLICIT_BUDGET/);
});
test("Full fee-net shadow risk specialist buys once and HOLDS, never daily repays fee",()=>{
 const s=M.create();
 hardForce(s.inner.core,"CASH");hardForce(s.baseCore,"CASH");
 M.signal(s,obs(s,0,2));const x=q(s,0,100);
 A.equal(x.shadow.risk.position,"GOLD");
 A.equal(x.shadow.risk.trades,1);
 A.ok(Math.abs(x.shadow.risk.nav-100*.992*.992)<1e-8);
 A.equal(x.shadow.base.position,"CASH");
 M.signal(s,obs(s,1,2));const y=q(s,1,102);
 A.equal(y.shadow.risk.trades,1);
 A.ok(Math.abs(y.shadow.risk.nav-100*.992*.992*1.02)<1e-7);
});
test("Default alert mode stays exactly aligned with V18, even with explicit 15pct limit",()=>{
 const s=M.create({maxDrawdownPct:15}),v=V18.create();let pos="CASH";
 for(let i=0;i<70;i++){
  const r=i<35?2:-2,o=obs(s,i,r);
  const a=M.signal(s,o),b=V18.signal(v,o);
  A.equal(a.action,b.action);
  const price=100*Math.exp(.014*Math.min(i,35)-.018*Math.max(0,i-35));
  const f=q(s,i,price),g=V18.quote(v,{at:at(i,9),price,isBankCheckpoint:true});
  pos=f.portfolio.position;
  A.equal(pos,g.fill.positionAfter);
 }
 A.deepEqual(s.inner.core.q,v.q);
});
test("Calibrated score uses completed returns and does not allow short fake histories",()=>{
 const s=M.create();
 A.equal(M.evidence([20,20]).ready,false);
 const a=M.evidence(Array(31).fill(1));
 A.equal(a.ready,true);A.ok(a.lower>0);
 A.ok(a.ess<=31);
 const b=M.evidence(Array(32).fill(-2));
 A.ok(b.lower<0);
});
test("No historical peak absorbing-state lock in soft risk mode",()=>{
 const s=M.create({maxDrawdownPct:15,riskMode:"soft_penalty"});
 s.inner.portfolio.peak=100;s.inner.portfolio.nav=70;
 s.inner.portfolio.cash=70;s.inner.portfolio.drawdownPct=30;
 s.inner.portfolio.maxDrawdownPct=30;
 for(const k of ["CASH_SWITCH"]){
  for(const c of [s.inner.core.q,s.inner.core.qb]){
    c[k].w[0]=100;
  }
 }
 s.inner.core.learned=40;
 const x=M.signal(s,obs(s,0,2));
 A.equal(x.action,"BUY","High positive marginal Q must allow re-entry");
});
test("Corrupt R2 shadow checkpoint rejected",()=>{
 const s=M.create();
 for(const bad of [
  x=>x.shadow.risk.cash=-1,
  x=>x.shadow.base.nav=null,
  x=>x.shadow.risk.returns=[Infinity],
  x=>x.shadow.relativeReturns=[NaN],
  x=>x.policy.riskMode="force_anyway"
 ]){
  const b=M.save(s);bad(b);A.throws(()=>M.restore(b));
 }
});
test("Full-path parallel specialist really can earn authority in a persistent uptrend",()=>{
 const s=M.create({riskMode:"soft_penalty",maxDrawdownPct:15});
 let activated=false;
 for(let i=0;i<65;i++){
  hardForce(s.inner.core,"CASH");hardForce(s.baseCore,"CASH");
  const x=M.signal(s,obs(s,i,2));
  if(i<24)A.equal(x.shadowConfirmed,false);
  const z=q(s,i,100*Math.exp(.015*i));
  if(x.shadowConfirmed&&x.specialistAction==="BUY"){
   A.equal(x.action,"BUY");activated=true;break;
  }
 }
 A.equal(activated,true,"Specialist should beat deliberately CASH-frozen baseline");
 A.ok(s.audit.specialistOverrides>0);
});
test("Parallel specialist consistently loses in falling-price hostile mock universe",()=>{
 const s=M.create({riskMode:"soft_penalty",maxDrawdownPct:15});
 for(let i=0;i<55;i++){
   // CASH always base, RALLY implies rule BUY but actual prices go DOWN.
   hardForce(s.inner.core,"CASH");hardForce(s.baseCore,"CASH");
   const x=M.signal(s,obs(s,i,2));
   A.equal(x.action,"WAIT");
   q(s,i,100*Math.exp(-.015*i));
 }
 A.equal(s.audit.specialistOverrides,0);
 A.ok(s.shadow.lastEvidence.lower<0);
});
test("After invalid extra-long quote both shadow portfolios do not learn a fictional return",()=>{
 const s=M.create({core:{maxIntervalHours:4}});
 M.signal(s,obs(s,0,2));q(s,0,100);
 M.signal(s,obs(s,1,2));const bad=q(s,2,105);
 A.equal(bad.fill,null);
 A.equal(s.shadow.relativeReturns.length,1);
 A.equal(s.shadow.pending,null);
});
test("Save/restore replays all shadow checkpoint and Q decisions deterministically",()=>{
 const a=M.create();
 M.signal(a,obs(a,0,2));q(a,0,100);
 const b=M.restore(M.save(a));
 A.deepEqual(a,b);
 A.deepEqual(M.signal(a,obs(a,1,2)),M.signal(b,obs(b,1,2)));
 A.deepEqual(q(a,1,104),q(b,1,104));
});
