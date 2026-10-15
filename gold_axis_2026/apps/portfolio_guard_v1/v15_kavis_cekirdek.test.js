"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const C=require("./v15_kavis_cekirdek");
const DAY=C.DAY,HOUR=C.HOUR;
const base=Date.parse("2020-01-01T00:00:00Z");
const at=(day,h=6)=>new Date(base+day*DAY+h*HOUR).toISOString();
const signal=(s,d,position="CASH",more={})=>
 C.signal(s,{asof:at(d),featureAvailableAt:at(d),
   market:{r4:1,r1:2,r3:4,rv:1,dd:0,nq6:null},position,...more});
const quote=(s,d,price=100,h=9,isBankCheckpoint=true)=>
 C.receiveQuote(s,{at:at(d,h),price,isBankCheckpoint});
const near=(x,y,eps=1e-8)=>assert.ok(Math.abs(x-y)<eps,x+" != "+y);

test("only research model; trained experts initialize independent of price futures",()=>{
 const m=C.make();assert.equal(m.version,C.VERSION);
 assert.equal(m.config.liveTrade,false);assert.equal(m.learning.matured,0);
 assert.equal(m.heads.ENTRY[56].n,0);assert.equal(m.heads.EXIT[1].n,0);
 assert.equal(C.FEATURE_NAMES.length,14);
});
test("cold start WAIT on both positions; future prices are not in signal API",()=>{
 const m=C.make();
 const a=signal(m,0);assert.equal(a.decision.action,"WAIT");
 assert.deepEqual(a.decision.reasons,["INSUFFICIENT_MATURED_EPISODES"]);
 assert.equal(a.liveTradingAuthorized,false);assert.equal(a.orderSent,false);
 quote(m,0,100);
 assert.equal(m.queue.length,5);
 const b=signal(m,1,"CASH");assert.equal(b.decision.action,"WAIT");
});
test("two legs of 0.8% are inside the completed action-value target exactly once",()=>{
 const m=C.make();signal(m,0);quote(m,0,100);
 const r=quote(m,1,102,12),label=r.matured.find(x=>x.h===1);
 assert.ok(label);
 near(label.entry,100*Math.log(102/100)+200*Math.log(.992));
 near(label.exit,-100*Math.log(102/100)+200*Math.log(.992));
 near(label.entry+label.exit,400*Math.log(.992));
 assert.ok(label.knownAt>label.entryAt);
 assert.equal(m.heads.ENTRY[1].n,1);assert.equal(m.heads.EXIT[1].n,1);
});
test("no learning before expiry; no same signal-and-fill checkpoint",()=>{
 const m=C.make();signal(m,0);
 let r=C.receiveQuote(m,{at:at(0,6),price:100,isBankCheckpoint:true});
 assert.equal(r.fills.length,0);
 r=C.receiveQuote(m,{at:at(0,9),price:100,isBankCheckpoint:true});
 assert.equal(r.fills.length,1);
 r=C.receiveQuote(m,{at:at(1,8),price:102,isBankCheckpoint:false});
 assert.equal(r.matured.length,0);
 assert.equal(m.learning.matured,0);
 r=C.receiveQuote(m,{at:at(1,9),price:102,isBankCheckpoint:true});
 assert.equal(r.matured.filter(x=>x.h===1).length,1);
 assert.equal(m.learning.matured,1);
});
test("unverified, not-yet-published and future legacy data are blocked",()=>{
 const cases=[
  {events:[{verifiedFirstPublication:false,firstAvailableAt:at(0),score:1}],match:/UNVERIFIED/},
  {events:[{verifiedFirstPublication:true,firstAvailableAt:at(1),score:1}],match:/FUTURE_EVENT/},
  {legacy:{net14:1,net56:10,availableAt:at(1)},match:/FUTURE_LEGACY/},
  {featureAvailableAt:at(1),match:/FUTURE_FEATURE/}
 ];
 for(const c of cases){const s=C.make();const o={asof:at(0),
   featureAvailableAt:at(0),market:{r4:1,r1:2,r3:3},position:"CASH",...c};
   assert.throws(()=>C.signal(s,o),c.match);
   assert.equal(s.market.lastSignalAt,null);
   assert.equal(s.queue.length,0);
 }
 const m=C.make();
 assert.doesNotThrow(()=>C.signal(m,{asof:at(0),featureAvailableAt:at(0),
  position:"CASH",market:{r4:1,r1:2,r3:3},events:[
   {verifiedFirstPublication:true,firstAvailableAt:at(0),score:.5}]}));
});
test("invalid inputs, repeated signals, overlapping unfilled decisions reject",()=>{
 const m=C.make();
 assert.throws(()=>C.signal(m,{asof:at(0),featureAvailableAt:at(0),
   market:{r4:1,r1:2,r3:3},position:"BAD"}),/INVALID_POSITION/);
 signal(m,0);
 assert.throws(()=>signal(m,1),/PENDING_SIGNAL/);
 assert.throws(()=>quote(m,0,-1),/BAD_BANK_PROXY_PRICE/);
 quote(m,0,100);
 assert.throws(()=>signal(m,0),/NONMONOTONE_SIGNAL/);
 assert.throws(()=>quote(m,0,101),/NONMONOTONE_QUOTE/);
 assert.throws(()=>C.make({feePerSide:-.01}),/INVALID_FEE/);
 assert.throws(()=>C.make({confidenceZ:NaN}),/INVALID_CONFIDENCE/);
});
test("late quotes do not silently invent an exact horizon label",()=>{
 const m=C.make();signal(m,0);quote(m,0,100);
 const x=quote(m,7,105,18,false);
 assert.equal(x.matured.filter(z=>z.h===1||z.h===3).length,0);assert.ok(m.learning.missing>0);
 assert.ok(x.stillOpen<5);
});
test("non-checkpoint bars may mature outcomes but never emulate a bank fill",()=>{
 const m=C.make();signal(m,0);
 const x=quote(m,0,100,9,false);
 assert.equal(x.fills.length,0);assert.equal(x.readySignals,1);
 const y=quote(m,0,100,12,true);
 assert.equal(y.fills.length,1);assert.equal(y.readySignals,0);
});
test("adaptive fuzzy, MLP, linear, loss weights and local memory train from matured episode only",()=>{
 const m=C.make(),pre=JSON.stringify(m.heads.ENTRY[1]);
 signal(m,0);quote(m,0,100);
 assert.equal(JSON.stringify(m.heads.ENTRY[1]),pre);
 const mid=JSON.stringify(m.memory.trendW);
 quote(m,1,106,12);
 const h=m.heads.ENTRY[1];
 assert.equal(h.n,1);assert.notEqual(JSON.stringify(h),pre);
 assert.ok(h.linear.w.some(v=>v!==0));
 assert.ok(h.fuzzy.w.some(row=>row.some(v=>v!==0)));
 assert.ok(h.mlp.w2.some(v=>v!==0)||h.mlp.b2!==0);
 assert.ok(m.learning.gateUpdates>0);
 // An initially identical trio of untrained experts needs a second
 // completed label before their relative loss weights can separate.
 signal(m,2);quote(m,2,103);quote(m,3,108,12);
 assert.ok(h.logExpertWeight.some(v=>v!==0));
 assert.ok(m.learning.centerUpdates>0,"supervised centers require diverse learned fuzzy consequents");
 assert.notEqual(JSON.stringify(m.memory.trendW),mid);
});
test("export/import reproduces later learning without hidden environmental state",()=>{
 const s=C.make();signal(s,0);quote(s,0,100);
 const cloned=C.restore(C.checkpoint(s));
 const a=quote(s,1,104,12),b=quote(cloned,1,104,12);
 assert.deepEqual(a,b);
 assert.deepEqual(C.checkpoint(s),C.checkpoint(cloned));
 assert.throws(()=>C.restore({version:"V13"}),/INCOMPATIBLE/);
});
test("fixed source observations produce identical prefix decisions regardless of later prices",()=>{
 const a=C.make(),b=C.make();
 const before1=signal(a,0),before2=signal(b,0);
 assert.deepEqual(before1,before2);
 quote(a,0,100);quote(b,0,100);
 signal(a,1);signal(b,1);
 const fixedA=C.checkpoint(a),fixedB=C.checkpoint(b);
 assert.deepEqual(fixedA,fixedB);
 quote(a,1,150);quote(b,1,70);
 assert.notDeepEqual(a.heads.ENTRY[1].linear.w,b.heads.ENTRY[1].linear.w);
 assert.deepEqual(fixedA,fixedB);
});
test("learned risk shadow price is active only with investor-specified budget",()=>{
 const m=C.make({maxHypotheticalDownsidePct:2});
 signal(m,0);quote(m,0,100);
 for(let d=1;d<=29;d++)quote(m,d,d<28?50:100);
 assert.ok(m.risk.observations>0);
 assert.ok(m.risk.lambda>0);
 const unconstrained=C.make();
 assert.equal(unconstrained.risk.lambda,0);
});
test("strong synthetic uptrend then downturn trains to BUY and SELL without a fixed price rule",()=>{
 const s=C.make({minMaturedLabels:3,confidenceZ:0});
 let position="CASH";const transitions=[];
 for(let d=0;d<390;d++){
   const direction=d<180?1:-1;
   const sent=C.signal(s,{asof:at(d),featureAvailableAt:at(d),position,
     market:{r4:direction*2.2,r1:direction*4.2,r3:direction*8.4,
       rv:1.2,dd:direction>0?0:-3}});
   const price=100*Math.exp(.015*Math.min(d,180)-.02*Math.max(0,d-180));
   const filled=quote(s,d,price).fills;
   assert.equal(filled.length,1);
   if(filled[0].intendedAction!=="WAIT")transitions.push({day:d,act:sent.decision.action});
   position=filled[0].intendedPosition;
 }
 assert.ok(transitions.some(x=>x.act==="BUY"),JSON.stringify(transitions));
 assert.ok(transitions.some(x=>x.act==="SELL"),JSON.stringify(transitions));
 assert.equal(position,"CASH");assert.ok(s.heads.ENTRY[56].n>5);
 assert.ok(s.heads.EXIT[1].n>200);
});
test("engine is not a historic replay, profit oracle, or live order interface",()=>{
 const model=C.make(),s=signal(model,0);
 assert.equal(s.orderSent,false);
 assert.equal(s.decision.provenProfitable,false);
 assert.equal(typeof C.replay,"undefined");
 assert.equal(typeof C.liveOrder,"undefined");
});
