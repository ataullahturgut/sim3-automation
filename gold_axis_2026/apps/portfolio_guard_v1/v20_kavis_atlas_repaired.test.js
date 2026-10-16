"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const M=require("./v20_kavis_atlas_repaired"),V18=require("./v18_kavis_dayaniqlilik");
const base=Date.parse("2020-01-01T00:00:00Z"),day=86400000,hour=3600000;
const at=(d,h=6)=>new Date(base+d*day+h*hour).toISOString();
function obs(s,d,r=-3){return {asof:at(d),featureAvailableAt:at(d),
 position:s.portfolio.position,market:{r4:r,r1:2*r,r3:3*r,rv:Math.abs(r),
 dd:Math.min(0,r)}};}
const quote=(s,d,price,extra={})=>M.quote(s,{at:at(d,9),price,isBankCheckpoint:true,...extra});
function force(s,position,keep=true){
 s.core.learned=100;
 for(const obj of [s.core.q,s.core.qb]){
  obj[position+"_KEEP"].w[0]=keep?20:-20;
  obj[position+"_SWITCH"].w[0]=keep?-20:20;
 }
}
function gold(s){
 s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;
 s.portfolio.units=1;s.portfolio.nav=100;s.portfolio.peak=100;
}
test("unconfigured drawdown limit never becomes zero and creates zero false breach flags",()=>{
 const s=M.create();gold(s);force(s,"GOLD");
 M.signal(s,obs(s,0,-3));quote(s,0,100);
 M.signal(s,obs(s,1,-3));const x=quote(s,1,95);
 assert.ok(x.portfolio.currentDrawdownPct>0);
 assert.equal(x.gapDrawdownBreached,false);
 assert.equal(s.audit.postCrashGapWarnings,0);
});
test("explicit drawdown limit reports an actual loss without a blind forced SELL",()=>{
 const s=M.create({maxDrawdownPct:15});gold(s);force(s,"GOLD");
 M.signal(s,obs(s,0,-3));quote(s,0,100);
 const decision=M.signal(s,obs(s,1,-3));
 assert.equal(decision.action,"WAIT");
 const filled=quote(s,1,81);
 assert.equal(filled.gapDrawdownBreached,true);
 assert.ok(s.audit.postCrashGapWarnings>=1);
 assert.equal(filled.fill.suggestedAction,"WAIT");
});
test("expiry kills lastFill, so later risk labels never bridge multiple days",()=>{
 const s=M.create({core:{maxIntervalHours:4}});
 M.signal(s,obs(s,0,1));quote(s,0,100);
 M.signal(s,obs(s,1,1));
 const exp=quote(s,2,100);
 assert.equal(exp.fill,null);assert.equal(exp.base.expired,true);
 assert.equal(s.risk.lastFill,null);
 assert.deepEqual(s.risk.twoStepQueue,[]);
 assert.equal(s.risk.learnedReturns,0);
});
test("core-accepted false on long gap also prevents stale CVaR and shadow labels",()=>{
 const s=M.create({core:{maxIntervalHours:40}});
 M.signal(s,obs(s,0,1));quote(s,0,100);
 M.signal(s,obs(s,2,1));const out=quote(s,2,110);
 assert.equal(out.baseFeedback.accepted,false);
 assert.equal(s.risk.learnedReturns,0);
 assert.equal(s.audit.unobservedGapLabels,1);
 assert.equal(s.audit.advisorMatured,0);
});
test("bad shadow lastFill is rejected including negative, NaN or corrupt candidate",()=>{
 const s=M.create();M.signal(s,obs(s,0,1));quote(s,0,100);
 for(const field of [
  z=>z.risk.lastFill.price=-1,
  z=>z.risk.lastFill.price=null,
  z=>z.risk.lastFill.fee=-.01,
  z=>z.risk.lastFill.shadow.adviceAction="FLY",
  z=>z.risk.lastFill.shadow.bucket="FUTURE"
 ]){
  const z=M.save(s);field(z);
  assert.throws(()=>M.restore(z),/CORRUPT_PORTFOLIO_OR_RISK/);
 }
});
test("EWMA effective observations never grow indefinitely and startup bias corrected",()=>{
 const s=M.create();
 const z=s.risk.advisor.STRESS_GOLD;
 z.n=1000;z.n2=1000;
 z.mean=.5;z.mean2=.5;z.var=1;z.var2=1;
 gold(s);force(s,"GOLD");
 const d=M.signal(s,obs(s,0,-4));
 assert.ok(d.advisorEvidence.effectiveObservations<33);
 assert.ok(d.advisorEvidence.effectiveObservations>30);
 assert.ok(d.advisorEvidence.lowerConfidence<.5);
 assert.ok(d.advisorEvidence.lowerTwoStep<.5);
});
test("stress GOLD adviser gains authority from valid 1- and 2-step losing-gold evidence",()=>{
 const s=M.create({riskAdvisorMinLabels:12});gold(s);
 let activated=false,rejected=0,earnedLabels=0;
 for(let d=0;d<85;d++){
  force(s,"GOLD");
  const x=M.signal(s,obs(s,d,-4));
  if(d<12){assert.equal(x.advisorApplied,false);rejected++;}
  const price=100*Math.exp(-.02*d),r=quote(s,d,price);
  assert.ok(r.fill);
  if(x.advisorApplied){
    assert.equal(x.action,"SELL");
    assert.equal(x.advisorEvidence.verified,true);
    activated=true;earnedLabels=s.risk.advisor.STRESS_GOLD.n2;break;
  }
 }
 assert.equal(activated,true,"the adviser must really activate in a relevant synthetic world");
 assert.ok(earnedLabels>=12);
 assert.ok(s.audit.advisorActivated>0);
});
test("adverse specialist does not activate when future reality contradicts it",()=>{
 const s=M.create({riskAdvisorMinLabels:12});gold(s);
 for(let d=0;d<45;d++){
  force(s,"GOLD");
  const x=M.signal(s,obs(s,d,-4));
  assert.equal(x.advisorApplied,false);
  const r=quote(s,d,100*Math.exp(.016*d));assert.ok(r.fill);
 }
 const ev=s.risk.advisor.STRESS_GOLD;
 assert.ok(ev.n>=12&&ev.n2>=12);
 assert.ok(ev.mean<0&&ev.mean2<0);
});
test("2-step evidence never matures at the first or second fill",()=>{
 const s=M.create();gold(s);force(s,"GOLD");
 M.signal(s,obs(s,0,-3));quote(s,0,100);
 M.signal(s,obs(s,1,-3));quote(s,1,98);
 assert.equal(s.risk.advisor.STRESS_GOLD.n2,0);
 M.signal(s,obs(s,2,-3));quote(s,2,96);
 assert.equal(s.risk.advisor.STRESS_GOLD.n2,1);
});
test("explicit prospective entry budget can block BUY before exposure; not an ex-post SELL",()=>{
 const s=M.create({maxDrawdownPct:12,enforceEntryRiskBudget:true});
 s.core.learned=100;force(s,"CASH",false);
 s.portfolio.peak=100;s.portfolio.nav=94;s.portfolio.cash=94;
 s.portfolio.drawdownPct=6;s.portfolio.maxDrawdownPct=6;
 s.risk.all=Array(24).fill(10);s.risk.buckets.RALLY=Array(15).fill(10);
 const x=M.signal(s,obs(s,0,2));
 assert.equal(x.projectedEntryViolation,true);
 assert.equal(x.action,"WAIT");
 assert.equal(x.reason,"EX_ANTE_ENTRY_BUDGET");
 assert.equal(s.audit.prospectiveEntryBlocks,1);
});
test("no-risk switch always preserves V18 action and learned Q weights",()=>{
 const s=M.create({useRiskPolicy:false}),v=V18.create();let position="CASH";
 for(let d=0;d<65;d++){
   const r=d<30?2:-2;
   const x=obs(s,d,r);
   const a=M.signal(s,x),b=V18.signal(v,x);
   assert.equal(a.action,b.action);
   const price=100*Math.exp(.008*Math.min(d,30)-.01*Math.max(0,d-30));
   const filled=quote(s,d,price).fill;
   const control=V18.quote(v,{at:at(d,9),price,isBankCheckpoint:true}).fill;
   position=filled.positionAfter;
   assert.equal(position,control.positionAfter);
 }
 assert.deepEqual(s.core.q,v.q);assert.deepEqual(s.core.qb,v.qb);
});
test("repaired checkpoint replay is reproducible even with pending two-step shadow",()=>{
 const a=M.create();gold(a);force(a,"GOLD");
 for(let d=0;d<3;d++){
  M.signal(a,obs(a,d,-4));quote(a,d,100*Math.exp(-.02*d));
 }
 const b=M.restore(M.save(a));
 assert.deepEqual(a,b);
 const xa=M.signal(a,obs(a,3,-4)),xb=M.signal(b,obs(b,3,-4));
 assert.deepEqual(xa,xb);
 assert.deepEqual(quote(a,3,94),quote(b,3,94));
});
test("no live bank order or false risk-loss guarantee is exported",()=>{
 const s=M.create();
 assert.equal(typeof M.placeOrder,"undefined");
 assert.equal(s.core.config.liveTrade,false);
});
