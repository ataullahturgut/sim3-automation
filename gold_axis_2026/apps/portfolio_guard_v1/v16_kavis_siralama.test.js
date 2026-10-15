"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),C=require("./v16_kavis_siralama");
const base=Date.parse("2020-01-01T00:00:00Z"),at=(d,h=6)=>new Date(base+d*C.DAY+h*C.HR).toISOString();
const obs=(d,position="CASH",up=1,expert)=>({asof:at(d),featureAvailableAt:at(d),position,
 market:{r4:2*up,r1:4*up,r3:7*up,rv:1.2,dd:up<0?-3:0,nq6:null},
 ...(expert?{v15Expert:expert}:{})});
const fill=(s,d,p=100,h=9)=>C.quote(s,{at:at(d,h),price:p,isBankCheckpoint:true});
const near=(x,y,eps=1e-9)=>assert.ok(Math.abs(x-y)<eps,x+" vs "+y);
test("state cold-start abstains; no historical runner or live order API",()=>{
 const s=C.create(),a=C.signal(s,obs(0));
 assert.equal(a.action,"WAIT");assert.equal(a.noLiveOrders,true);
 assert.equal(typeof C.replay,"undefined");
 assert.equal(typeof C.liveOrder,"undefined");
 assert.equal(C.FEATURES.length,12);
 assert.equal(fill(s,0).fill.simulatedExecutionOnly,true);
});
test("bank signals at 09TR fill only at later valid bank checkpoint",()=>{
 const s=C.create();C.signal(s,obs(0));
 assert.throws(()=>fill(s,0,100,6),/SAME_BAR/);
 assert.throws(()=>fill(s,0,100,10),/INVALID_BANK_CHECKPOINT/);
 assert.equal(s.lastQuoteAt,null);
 const intrabar=C.quote(s,{at:at(0,8),price:99,isBankCheckpoint:false});
 assert.equal(intrabar.fill,null);
 const x=fill(s,0,100,9);
 assert.equal(x.fill.signalAt,at(0,6));assert.equal(x.fill.at,at(0,9));
 assert.equal(x.ordersSent,0);
});
test("one side of fee only when switching, not every day of holding",()=>{
 const s=C.create({feePerSide:.008,minimumMaturedIntervals:2});
 C.signal(s,obs(0));fill(s,0,100);
 C.signal(s,obs(1));const x=fill(s,1,102).update;
 assert.equal(x.accepted,true);assert.equal(x.trainedHeads.length,4);
 const reward=Object.fromEntries(x.trainedHeads.map(z=>[z.head,z.reward]));
 near(reward.CASH_KEEP,0);
 near(reward.CASH_SWITCH,100*Math.log(.992)+100*Math.log(1.02));
 near(reward.GOLD_KEEP,100*Math.log(1.02));
 near(reward.GOLD_SWITCH,100*Math.log(.992));
 near(reward.CASH_SWITCH-reward.GOLD_KEEP,100*Math.log(.992));
 assert.equal(s.audit.switchFeeObserved,2);
});
test("NO future-price label available at next-day signal before quote completion",()=>{
 const a=C.create(),b=C.create();
 C.signal(a,obs(0));C.signal(b,obs(0));fill(a,0,100);fill(b,0,100);
 const sa=C.signal(a,obs(1)),sb=C.signal(b,obs(1));
 assert.deepEqual(sa,sb);
 assert.deepEqual(C.save(a),C.save(b));
 fill(a,1,200);fill(b,1,50);
 assert.notDeepEqual(a.q.CASH_SWITCH.w,b.q.CASH_SWITCH.w);
});
test("no waiting-hour price observation can train Bellman head without next fill",()=>{
 const s=C.create();C.signal(s,obs(0));fill(s,0,100);
 C.signal(s,obs(1));
 const a=C.quote(s,{at:at(1,8),price:999,isBankCheckpoint:false});
 assert.equal(a.update,null);assert.equal(s.learned,0);
 fill(s,1,101);
 assert.equal(s.learned,1);
});
test("counterfactuals give four state-action updates after ONE actual interval",()=>{
 const s=C.create();C.signal(s,obs(0));fill(s,0,100);
 C.signal(s,obs(1));fill(s,1,98);
 for(const k of ["CASH_KEEP","CASH_SWITCH","GOLD_KEEP","GOLD_SWITCH"])
  assert.equal(s.q[k].n,1);
 assert.equal(s.learned,1);
 assert.equal(s.audit.trainingPairs,4);
});
test("incomplete >80-hour interval is skipped rather than treated as one day",()=>{
 const s=C.create();C.signal(s,obs(0));fill(s,0,100);
 C.signal(s,obs(4));const x=fill(s,4,120).update;
 assert.equal(x.accepted,false);assert.equal(x.reason,"GAP_TOO_LONG");
 assert.equal(s.learned,0);assert.equal(s.skipped,1);
});
test("old pending order candidate expires after delay, makes no imagined execution",()=>{
 const s=C.create({maxIntervalHours:10});C.signal(s,obs(0));
 const x=fill(s,1,103);
 assert.equal(x.expired,true);assert.equal(x.fill,null);
 assert.equal(s.pending,null);assert.equal(s.learned,0);
});
test("exposure risk budget applies only to learned downside, not automatic bank order",()=>{
 const s=C.create({goldDownsideBudgetPct:1,minimumMaturedIntervals:2});
 let position="CASH";
 for(let d=0;d<16;d++){
  const r=C.signal(s,obs(d,position,d<8?1:-1));
  const x=fill(s,d,100*Math.exp(.03*Math.min(d,8)-.04*Math.max(0,d-8)));
  position=x.fill.positionAfter;
 }
 assert.ok(s.risk.matured>0);
 assert.ok(Number.isFinite(s.risk.dual));
 assert.ok(s.risk.head.w.some(x=>x!==0));
});
test("deterministic synthetic up/dn/up path learns BUY SELL BUY, beyond finite horizon",()=>{
 const s=C.create({minimumMaturedIntervals:10,learningRate:.23,uncertaintyScale:.02});
 let pos="CASH",moves=[];
 for(let d=0;d<500;d++){
  const direction=d<240?1:d<410?-1:1;
  const a=C.signal(s,obs(d,pos,direction));
  const p=100*Math.exp(.014*Math.min(d,240)-
   .019*Math.max(0,Math.min(d-240,170))+.012*Math.max(0,d-410));
  const z=fill(s,d,p).fill;
  if(z.suggestedAction!=="WAIT")moves.push({d,action:z.suggestedAction,score:a.actionGap});
  pos=z.positionAfter;
 }
 assert.ok(moves.length>=3,JSON.stringify(moves));
 assert.deepEqual(moves.slice(0,3).map(x=>x.action),["BUY","SELL","BUY"]);
 assert.equal(pos,"GOLD");
 assert.equal(s.learned,499);
});
test("flat prices with 0.8% fee cause WAIT after training, no churn",()=>{
 const s=C.create({minimumMaturedIntervals:5});
 let pos="CASH",activity=[];
 for(let i=0;i<190;i++){
  const x=C.signal(s,obs(i,pos,0));
  const fill0=fill(s,i,100).fill;
  pos=fill0.positionAfter;
  if(i>80&&x.action!=="WAIT")activity.push({i,action:x.action});
 }
 assert.equal(activity.length,0,JSON.stringify(activity));
});
test("valid V15 expert signal must preexist current signal; position mismatches blocked",()=>{
 const s=C.create();
 assert.throws(()=>C.signal(s,obs(0,"CASH",1,{availableAt:at(1),actionEdge:1,position:"CASH"})),
  /UNVERIFIED_V15_EXPERT/);
 assert.throws(()=>C.signal(s,obs(0,"CASH",1,{availableAt:at(0),actionEdge:1,position:"GOLD"})),
  /POSITION_MISMATCH/);
 assert.equal(s.pending,null);
 const a=C.signal(s,obs(0,"CASH",1,{availableAt:at(0),actionEdge:2,position:"CASH"}));
 assert.equal(a.v15ExpertUsed,true);
});
test("checkpoint restores weights and locked intent without hidden state",()=>{
 const s=C.create(),a=C.signal(s,obs(0));
 const copy=C.restore(C.save(s));assert.deepEqual(copy,s);
 assert.deepEqual(fill(s,0,99),fill(copy,0,99));
 assert.deepEqual(C.save(s),C.save(copy));
 assert.throws(()=>C.restore({...C.save(s),version:"V13"}),/INVALID_CHECKPOINT/);
 const corrupt=C.save(s);corrupt.q.CASH_KEEP.w[0]=null;
 assert.throws(()=>C.restore(corrupt),/BAD_Q_CHECKPOINT/);
});
test("signals reject future feature timestamp and fabricated position",()=>{
 const s=C.create();
 assert.throws(()=>C.signal(s,{...obs(0),featureAvailableAt:at(1)}),/FUTURE_MARKET/);
 C.signal(s,obs(0));fill(s,0);
 assert.throws(()=>C.signal(s,obs(1,"GOLD")) ,/VIRTUAL_POSITION/);
 assert.throws(()=>C.signal(s,obs(0)),/NONMONOTONE_SIGNAL/);
});
test("future perturbation at signal t+1 cannot revise earlier t decision",()=>{
 const s=C.create(),a=C.signal(s,obs(0)),snapshot=C.save(s);
 fill(s,0,100);
 C.signal(s,obs(1));
 fill(s,1,200);
 assert.equal(a.action,"WAIT");assert.equal(snapshot.learned,0);
 assert.equal(snapshot.pending.id,"V16-1");
});
test("no observed short position or leverage allowed; every position in {CASH,GOLD}",()=>{
 const s=C.create();
 assert.throws(()=>C.signal(s,obs(0,"SHORT")),/BAD_POSITION/);
 assert.throws(()=>C.create({feePerSide:-1}),/BAD_FEE/);
 assert.throws(()=>C.create({gammaPerDay:1.5}),/BAD_GAMMA/);
 assert.throws(()=>C.create({bankCheckpointHoursUTC:[6,6]}),/BAD_CHECKPOINTS/);
});
