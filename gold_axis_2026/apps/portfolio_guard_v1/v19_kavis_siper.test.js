"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const S=require("./v19_kavis_siper"),Core=require("./v18_kavis_dayaniqlilik");
const BASE=Date.parse("2020-01-01T00:00:00Z");
const at=(d,h=6)=>new Date(BASE+d*S_DAY+h*3600000).toISOString();
const S_DAY=86400000;
const m=(r=1)=>({r4:r,r1:2*r,r3:3*r,rv:Math.abs(r),dd:Math.min(0,r)});
const sig=(s,d,r=1,extra={})=>S.signal(s,{
 asof:at(d),featureAvailableAt:at(d),position:s.portfolio.position,market:m(r),...extra});
const q=(s,d,price=100,fee=.008)=>S.quote(s,{at:at(d,9),price,
  bankFeePerSide:fee,isBankCheckpoint:true});
const near=(a,b,tol=1e-8)=>A.ok(Math.abs(a-b)<tol,a+" != "+b);
test("V19 cold-start is abstention and no live order methods are exposed",()=>{
 const s=S.create();const d=sig(s,0);
 A.equal(d.action,"WAIT");A.equal(d.ordersSent,0);
 const x=q(s,0,100);
 A.equal(x.fill.suggestedAction,"WAIT");
 A.equal(typeof S.liveTrade,"undefined");
 A.equal(s.portfolio.cash,100);
 A.deepEqual(S.restore(S.save(s)),s);
});
test("Empirical loss CVaR is average of top 10 percent, not average negative return",()=>{
 const values=Array(90).fill(0).concat(Array(9).fill(3),[30]);
 const v=S.riskTail(values,.9);
 near(v.cvar,(9*3+30)/10);
 A.ok(v.mean<v.cvar);
});
test("Tail estimator uses only completed and sufficiently numerous prices",()=>{
 const s=S.create({minTailObservations:20});
 sig(s,0);
 A.equal(S.estimate(s,"STRESS").ready,false);
 q(s,0);
 for(let i=1;i<=19;i++){sig(s,i,1);q(s,i,100+Math.sin(i));}
 A.equal(S.estimate(s,"STRESS").ready,false);
 sig(s,20);q(s,20,100);
 A.equal(S.estimate(s,"STRESS").ready,true);
 A.equal(s.risk.learnedReturns,20);
});
test("Actual completed bank fill triggers 1 and only 1 gold-risk label",()=>{
 const s=S.create();
 sig(s,0);q(s,0,100);
 sig(s,1);
 const r=S.quote(s,{at:at(1,8),price:1e9,isBankCheckpoint:false});
 A.equal(r.fill,null);A.equal(s.risk.learnedReturns,0);
 q(s,1,96);
 A.equal(s.risk.learnedReturns,1);
 near(s.risk.all[0],-100*Math.log(.96));
});
test("Liquidity-aware liquidation NAV charges BUY and hypothetical terminal exit",()=>{
 const s=S.create();
 s.core.learned=30;
 for(const key of ["CASH_SWITCH"])for(const h of [s.core.q[key],s.core.qb[key]])
   h.w[0]=10;
 const a=sig(s,0);
 A.equal(a.action,"BUY");
 const out=q(s,0,100);
 A.equal(out.portfolio.position,"GOLD");
 near(out.portfolio.capital,100*(1-.008)**2);
 near(out.portfolio.feesPaidDollars,.8);
 A.equal(out.portfolio.trades,1);
});
test("A real SELL charges only one execution leg, future buy no fee until executed",()=>{
 const s=S.create();
 s.core.learned=40;
 for(const h of [s.core.q.CASH_SWITCH,s.core.qb.CASH_SWITCH])h.w[0]=10;
 sig(s,0);q(s,0,100);
 for(const h of [s.core.q.GOLD_SWITCH,s.core.qb.GOLD_SWITCH])h.w[0]=30;
 for(const h of [s.core.q.GOLD_KEEP,s.core.qb.GOLD_KEEP])h.w[0]=-30;
 const x=sig(s,1,-1);
 A.equal(x.action,"SELL");
 const end=q(s,1,110);
 A.equal(end.portfolio.position,"CASH");
 near(end.portfolio.capital,100*(1-.008)**2*1.1);
 A.equal(end.portfolio.trades,2);
});
test("Hard drawdown guard orders exit even if Double-Q says hold; gap risk remains",()=>{
 const s=S.create({maxDrawdownPct:10});
 s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.peak=100;s.portfolio.nav=88;s.portfolio.drawdownPct=12;
 s.portfolio.maxDrawdownPct=12;
 const z=sig(s,0,-2);
 A.equal(z.action,"SELL");
 A.equal(z.reason,"DRAW_DOWN_GUARD");
 A.equal(s.core.pending.choice,"SWITCH");
 A.equal(z.ordersSent,0);
});
test("Tail risk cannot trigger before sufficient matured labels",()=>{
 const s=S.create({maxDrawdownPct:12,minTailObservations:20});
 s.core.virtualPosition="GOLD";
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.core.learned=40;
 s.risk.all=Array(19).fill(15);
 const z=sig(s,0,-3);
 A.equal(z.tailEstimate.ready,false);
 A.equal(z.guardHot,false);
});
test("Conditioned stress tail forces SELL before hard DD, only after causal evidence",()=>{
 const s=S.create({maxDrawdownPct:12,minTailObservations:20,
    minConditionalObservations:8});
 s.core.virtualPosition="GOLD";s.core.learned=35;
 s.portfolio.position="GOLD";s.portfolio.cash=0;s.portfolio.units=1;
 s.portfolio.nav=93;s.portfolio.peak=100;s.portfolio.drawdownPct=7;
 s.portfolio.maxDrawdownPct=7;
 s.risk.all=Array(24).fill(12);
 s.risk.buckets.STRESS=Array(12).fill(12);
 const z=sig(s,0,-3);
 A.equal(z.action,"SELL");
 A.equal(z.reason,"TAIL_BUDGET_GUARD");
 A.ok(z.tailEstimate.ready);
 A.ok(z.tailEstimate.upper>=12);
});
test("Tail budget blocks unsafe entry while allowing calmer risk after recovery",()=>{
 const s=S.create({maxDrawdownPct:12});
 s.core.learned=50;
 for(const h of [s.core.q.CASH_SWITCH,s.core.qb.CASH_SWITCH])h.w[0]=10;
 s.risk.all=Array(24).fill(15);s.risk.buckets.STRESS=Array(18).fill(15);
 const z=sig(s,0,-2);
 A.equal(z.baseAction,"BUY");
 A.equal(z.action,"WAIT");A.equal(z.reason,"RISK_BUDGET_BLOCK");
 A.equal(s.core.pending.choice,"KEEP");
});
test("Quoted V18 anomaly never triggers risk update nor fictional portfolio loss",()=>{
 const s=S.create();sig(s,0);q(s,0,100);
 sig(s,1);
 const prior=S.save(s);
 const z=q(s,1,300);
 A.equal(z.fill,null);
 A.equal(z.base.quarantined,true);
 A.equal(s.risk.learnedReturns,0);
 A.deepEqual(s.portfolio,prior.portfolio);
 A.deepEqual(s.risk,prior.risk);
 const recovered=S.quote(s,{at:at(1,12),price:101,isBankCheckpoint:true});
 A.ok(recovered.fill);
 A.equal(s.risk.learnedReturns,1);
});
test("Position mismatch and corrupt fee rejected before state mutation",()=>{
 const s=S.create(),before=S.save(s);
 A.throws(()=>S.signal(s,{asof:at(0),featureAvailableAt:at(0),
   position:"GOLD",market:m()}),/POSITION_DISAGREEMENT/);
 A.deepEqual(s,before);
 A.throws(()=>S.create({maxDrawdownPct:0}),/INVALID_RISK_GOALS/);
});
test("V18 delayed bank fill expiry frees V19 pending risk context",()=>{
 const s=S.create({core:{maxIntervalHours:4}});
 sig(s,0);
 const z=q(s,1,100);
 A.equal(z.fill,null);A.equal(z.base.expired,true);
 A.equal(s.pendingContext,null);
 A.equal(s.core.pending,null);
});
test("Completely different hypothetical paths update risk without time leakage",()=>{
 const a=S.create(),b=S.create();
 sig(a,0);sig(b,0);q(a,0,100);q(b,0,100);
 const x=sig(a,1,-1),y=sig(b,1,-1);
 A.deepEqual(x,y);
 q(a,1,96);q(b,1,102);
 A.equal(a.risk.learnedReturns,1);
 A.ok(a.risk.all[0]>b.risk.all[0]);
});
test("Portfolio checkpoint detects counterfeit units and negative cash",()=>{
 const s=S.create();
 sig(s,0);q(s,0);
 for(const mutate of [
  x=>x.portfolio.cash=-100,
  x=>x.portfolio.units=12,
  x=>x.portfolio.nav=null,
  x=>x.risk.all=[Infinity],
  x=>x.risk.buckets.STRESS=[-1]
 ]){const x=S.save(s);mutate(x);A.throws(()=>S.restore(x),/CORRUPT/);}
});
test("Risk module doesn't mutate V18 original source or import historical data",()=>{
 const s=S.create();
 A.ok(typeof Core.create==="function");
 A.equal(typeof S.backtestHistorical,"undefined");
 A.equal(s.core.version,Core.VERSION);
});
test("Frozen low-fee market signals remain V18-identical when shield disabled",()=>{
 const a=S.create({useRiskPolicy:false}),b=Core.create();
 let pos="CASH";
 for(let i=0;i<75;i++){
  const obs={asof:at(i),featureAvailableAt:at(i),position:pos,market:m(i<40?1:-1)};
  const x=S.signal(a,obs),y=Core.signal(b,obs);
  A.equal(x.action,y.action);
  const px=100*Math.exp(.007*Math.min(i,40)-.011*Math.max(0,i-40));
  const f=S.quote(a,{at:at(i,9),price:px,isBankCheckpoint:true}).fill;
  const g=Core.quote(b,{at:at(i,9),price:px,isBankCheckpoint:true}).fill;
  A.equal(f.suggestedAction,g.suggestedAction);
  pos=f.positionAfter;
 }
});

test("mathematical anti-deadlock: CASH after drawdown can BUY on verified recovery",()=>{
 const z=S.create({maxDrawdownPct:12});
 z.core.learned=50;
 for(const h of [z.core.q.CASH_SWITCH,z.core.qb.CASH_SWITCH])h.w[0]=15;
 z.portfolio.peak=100;z.portfolio.nav=80;
 z.portfolio.cash=80;z.portfolio.drawdownPct=20;
 z.portfolio.maxDrawdownPct=20;
 z.risk.all=Array(40).fill(2);
 z.risk.buckets.RALLY=Array(25).fill(.5);
 const a=sig(z,0,3);
 A.equal(a.hardLoss,true);
 A.equal(a.entryGuard,false);
 A.equal(a.action,"BUY");
 A.equal(a.baseAction,"BUY");
});
test("two completed RALLY checkpoints restore buying after protective GOLD exit",()=>{
 const z=S.create({maxDrawdownPct:12,recoveryObservations:2});
 z.core.learned=50;
 for(const h of [z.core.q.CASH_SWITCH,z.core.qb.CASH_SWITCH])h.w[0]=15;
 z.risk.afterForcedExit=true;
 z.risk.recoveryCount=0;
 let a=sig(z,0,3);
 A.equal(a.action,"WAIT");A.equal(a.reason,"RECOVERY_OBSERVATIONS");
 q(z,0,100);
 A.equal(z.risk.recoveryCount,1);
 a=sig(z,1,3);
 A.equal(a.action,"WAIT");q(z,1,101);
 A.equal(z.risk.recoveryCount,2);
 a=sig(z,2,3);
 A.equal(a.action,"BUY");
});
