"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const M=require("./v20_kavis_atlas"),Core=require("./v18_kavis_dayaniqlilik");
const base=Date.parse("2020-01-01T00:00:00Z");
const at=(d,h=6)=>new Date(base+d*86400000+h*3600000).toISOString();
const obs=(s,d,r=1)=>({asof:at(d),featureAvailableAt:at(d),position:s.portfolio.position,
 market:{r4:r,r1:r*2,r3:r*3,rv:Math.abs(r),dd:Math.min(0,r)}});
const fill=(s,d,p=100)=>M.quote(s,{at:at(d,9),price:p,isBankCheckpoint:true});
test("V20 no explicit DD budget means no hard, permanent liquidation directive",()=>{
 const s=M.create();A.equal(s.config.maxDrawdownPct,null);
 A.equal(s.portfolio.position,"CASH");
 A.equal(s.risk.advisor.STRESS.n,0);
});
test("V20 empirical advisor is not permitted to overrule proven Double Q without labels",()=>{
 const s=M.create();s.core.learned=60;
 s.core.virtualPosition="GOLD";s.portfolio.position="GOLD";
 s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.nav=88;s.portfolio.peak=100;s.portfolio.drawdownPct=12;
 s.portfolio.maxDrawdownPct=12;
 s.risk.all=Array(30).fill(11);
 s.risk.buckets.STRESS=Array(16).fill(11);
 const x=M.signal(s,obs(s,0,-3));
 A.equal(x.advisorEvidence.verified,false);
 A.equal(x.advisorApplied,false);
 A.equal(s.core.pending.choice,"KEEP");
});
test("Explicit user max drawdown is still emergency priority",()=>{
 const s=M.create({maxDrawdownPct:11});s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.nav=87;s.portfolio.peak=100;s.portfolio.drawdownPct=13;
 s.portfolio.maxDrawdownPct=13;
 const x=M.signal(s,obs(s,0,-2));
 A.equal(x.action,"SELL");
 A.equal(x.reason,"DRAW_DOWN_GUARD");
});
test("Advisor evidence updates only after two completed checkpoints",()=>{
 const s=M.create();s.core.learned=30;
 s.risk.all=Array(30).fill(10);
 s.risk.buckets.STRESS=Array(20).fill(10);
 for(const h of [s.core.q.CASH_SWITCH,s.core.qb.CASH_SWITCH])h.w[0]=15;
 M.signal(s,obs(s,0,-2));A.equal(s.risk.advisor.STRESS.n,0);
 fill(s,0,100);A.equal(s.risk.advisor.STRESS.n,0);
 const before=M.signal(s,obs(s,1,-2));
 A.equal(s.risk.advisor.STRESS.n,0);
 A.equal(before.advisorApplied,false);
 fill(s,1,90);
 A.equal(s.risk.advisor.STRESS.n,1);
 A.ok(Number.isFinite(s.risk.advisor.STRESS.lastDelta));
});
test("Profitable risk specialist can activate only after enough mature positive labels",()=>{
 const s=M.create({riskAdvisorMinLabels:8});
 s.core.learned=50;s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.nav=92;s.portfolio.peak=100;s.portfolio.drawdownPct=8;
 s.portfolio.maxDrawdownPct=8;
 s.risk.all=Array(30).fill(12);
 s.risk.buckets.STRESS=Array(15).fill(12);
 const z=s.risk.advisor.STRESS;z.n=9;z.mean=10;z.var=1;
 const x=M.signal(s,obs(s,0,-3));
 A.equal(x.advisorEvidence.verified,true);
 A.equal(x.advisorApplied,true);
 A.equal(x.action,"SELL");
});
test("Unprofitable adviser with many labels is rejected deterministically",()=>{
 const s=M.create({riskAdvisorMinLabels:8});
 s.core.learned=50;s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.nav=92;s.portfolio.peak=100;s.portfolio.drawdownPct=8;
 s.portfolio.maxDrawdownPct=8;
 s.risk.all=Array(30).fill(12);s.risk.buckets.STRESS=Array(15).fill(12);
 s.risk.advisor.STRESS.n=100;s.risk.advisor.STRESS.mean=-8;
 const x=M.signal(s,obs(s,0,-3));
 A.equal(x.advisorEvidence.verified,false);
 A.equal(x.advisorApplied,false);
});
test("Risk consultant cannot learn same-point future quote before it exists",()=>{
 const a=M.create(),b=M.create();a.core.learned=30;b.core.learned=30;
 for(const s of [a,b]){
  s.risk.all=Array(30).fill(12);
  s.risk.buckets.STRESS=Array(20).fill(12);
  for(const h of [s.core.q.CASH_SWITCH,s.core.qb.CASH_SWITCH])h.w[0]=15;
  M.signal(s,obs(s,0,-3));fill(s,0,100);
 }
 const x=M.signal(a,obs(a,1,-3)),y=M.signal(b,obs(b,1,-3));
 A.deepEqual(x,y);
 fill(a,1,80);fill(b,1,105);
 A.notDeepEqual(a.risk.advisor.STRESS,b.risk.advisor.STRESS);
});
test("Wrong bank price is quarantined before any adviser outcome update",()=>{
 const s=M.create();s.core.learned=30;s.risk.all=Array(30).fill(12);
 s.risk.buckets.STRESS=Array(20).fill(12);
 M.signal(s,obs(s,0,-3));fill(s,0,100);
 M.signal(s,obs(s,1,-3));
 const q=M.quote(s,{at:at(1,9),price:500,isBankCheckpoint:true});
 A.equal(q.fill,null);A.equal(s.risk.advisor.STRESS.n,0);
});
test("V20 state and shadow evidence restart bitwise-identically",()=>{
 const a=M.create();M.signal(a,obs(a,0));fill(a,0,100);
 const b=M.restore(M.save(a));A.deepEqual(a,b);
 const x=M.signal(a,obs(a,1)),y=M.signal(b,obs(b,1));
 A.deepEqual(x,y);
 A.deepEqual(fill(a,1,101),fill(b,1,101));
});
test("No-shield V20 preserves V18 actions, fee accounting and learned values",()=>{
 const a=M.create({useRiskPolicy:false}),b=Core.create();
 let position="CASH";
 for(let d=0;d<85;d++){
  const r=d<40?1:-1;
  const ob={asof:at(d),featureAvailableAt:at(d),position,market:
    {r4:r,r1:r*2,r3:r*3,rv:1,dd:r<0?-2:0}};
  const x=M.signal(a,ob),y=Core.signal(b,ob);
  A.equal(x.action,y.action);
  const price=100*Math.exp(.009*Math.min(40,d)-.012*Math.max(0,d-40));
  position=fill(a,d,price).fill.positionAfter;
  const k=Core.quote(b,{at:at(d,9),price,isBankCheckpoint:true}).fill;
  A.equal(position,k.positionAfter);
 }
 A.deepEqual(a.core.q,b.q);A.deepEqual(a.core.qb,b.qb);
});
test("V20 does not offer any live trading API or financing/leverage",()=>{
 const s=M.create();
 A.equal(typeof M.placeOrder,"undefined");
 A.equal(s.core.config.liveTrade,false);
 A.throws(()=>M.create({advisorDecay:1}),/INVALID_RISK_GOALS/);
});
