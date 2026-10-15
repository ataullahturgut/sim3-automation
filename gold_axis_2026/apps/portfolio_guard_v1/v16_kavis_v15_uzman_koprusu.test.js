"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const B=require("./v16_kavis_v15_uzman_koprusu");
const ms=24*3600000,hr=3600000,base=Date.parse("2020-01-01T00:00:00Z");
const at=(d,h=6)=>new Date(base+d*ms+h*hr).toISOString();
const obs=(d,pos,dir=1)=>({asof:at(d),featureAvailableAt:at(d),
 position:pos,market:{r4:1.8*dir,r1:4*dir,r3:6*dir,rv:1.3,dd:dir>0?0:-3}});
const quote=(h,d,p=100)=>B.quote(h,{at:at(d,9),price:p,isBankCheckpoint:true});
test("inference-only V15 advice cannot change the actual V15 market learning clock",()=>{
 const h=B.create(),pre=B.save(h);
 const x=B.infer(h,obs(0,"CASH"));
 A.equal(x,null);
 A.deepEqual(B.save(h),pre);
 A.equal(h.v15.market.lastSignalAt,null);
});
test("V15 shadow and V16 sole policy may disagree without portfolio-state conflation",()=>{
 const h=B.create({v16:{minimumMaturedIntervals:8,learningRate:.23,uncertaintyScale:.02}});
 let p="CASH",used=0,disagree=0;
 for(let d=0;d<310;d++){
   const direction=d<160?1:-1;
   const s=B.signal(h,obs(d,p,direction));
   const px=100*Math.exp(.015*Math.min(d,160)-.017*Math.max(0,d-160));
   const r=quote(h,d,px);
   A.equal(r.ordersSent,0);
   A.equal(s.validPortfolioDecision,"V16_ONLY");
   A.equal(s.decision.noLiveOrders,true);
   A.ok(r.decisionFill);
   p=r.decisionFill.positionAfter;
   if(s.expertUsed)used++;
   if(s.shadow.position!==s.decision.position)disagree++;
 }
 A.ok(h.v15.learning.matured>100);
 A.ok(h.v16.learned>200);
 A.ok(used>0,"V15 matured expert should eventually become available");
 A.equal(used,h.bridge.expertUsed);
 A.ok(h.bridge.signals===310);
 A.ok(h.bridge.shadowMismatch===disagree);
});
test("V15 news release or V16 bad input cannot half-mutate bridge states",()=>{
 const h=B.create(),before=B.save(h);
 A.throws(()=>B.signal(h,{...obs(0,"CASH"),events:[{
   verifiedFirstPublication:false,firstAvailableAt:at(0),score:1
 }]}),/UNVERIFIED_EVENT/);
 const after=B.save(h);
 A.deepEqual(after.v15,before.v15);A.deepEqual(after.v16,before.v16);
 A.equal(h.bridge.rollbackCount,1);
});
test("invalid bank fill time restores both V15 and V16 states atomically",()=>{
 const h=B.create();B.signal(h,obs(0,"CASH"));
 const before=B.save(h);
 A.throws(()=>B.quote(h,{at:at(0,10),price:100,isBankCheckpoint:true}),
   /INVALID_BANK_CHECKPOINT/);
 const after=B.save(h);
 A.deepEqual(after.v15,before.v15);A.deepEqual(after.v16,before.v16);
 A.equal(h.bridge.rollbackCount,1);
 const q=quote(h,0,100);
 A.equal(q.decisionFill.positionAfter,"CASH");
});
test("bridge checkpoint deterministically reproduces outcomes after resuming",()=>{
 const h=B.create();B.signal(h,obs(0,"CASH"));quote(h,0,100);
 const clone=B.restore(B.save(h));
 B.signal(h,obs(1,"CASH"));B.signal(clone,obs(1,"CASH"));
 const a=quote(h,1,105),b=quote(clone,1,105);
 A.deepEqual(a,b);
 A.deepEqual(B.save(h),B.save(clone));
 A.throws(()=>B.restore({version:"WRONG"}),/BAD_BRIDGE/);
});
