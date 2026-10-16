"use strict";
const test=require("node:test"),A=require("node:assert/strict"),M=require("./v17_kavis_olay_doubleq");
const base=Date.parse("2020-01-01T00:00:00Z");
const at=(n,h=6,shift=0)=>new Date(base+(n+shift)*M.DAY+h*M.HR).toISOString();
function obs(n,pos="CASH",r=1,shift=0,events){
 return {asof:at(n,6,shift),featureAvailableAt:at(n,6,shift),
   position:pos,market:{r4:r,r1:2*r,r3:3*r,rv:Math.abs(r),dd:Math.min(r,0)},
   ...(events?{events}:{})};
}
function fill(s,n,p=100,shift=0){return M.quote(s,{at:at(n,9,shift),price:p,isBankCheckpoint:true});}
test("V17 learns two distinct critics without changing V16 production model",()=>{
 const m=M.create({minimumMaturedIntervals:2});
 A.equal(M.FEATURES.length,20);
 M.signal(m,obs(0));fill(m,0);
 M.signal(m,obs(1));const a=fill(m,1,103).update;
 A.equal(a.trainedEstimator,"A");
 A.equal(m.q.CASH_SWITCH.n,1);A.equal(m.qb.CASH_SWITCH.n,0);
 M.signal(m,obs(2));const b=fill(m,2,107).update;
 A.equal(b.trainedEstimator,"B");
 A.equal(m.qb.CASH_SWITCH.n,1);A.equal(m.q.CASH_SWITCH.n,1);
});
test("Double Q target uses opposite network for evaluation not own maximum",()=>{
 const m=M.create({minimumMaturedIntervals:5,gammaPerDay:.9});
 M.signal(m,obs(0));fill(m,0,100);
 m.q.GOLD_KEEP.w[0]=10;m.q.GOLD_SWITCH.w[0]=1;
 m.qb.GOLD_KEEP.w[0]=3;m.qb.GOLD_SWITCH.w[0]=100;
 M.signal(m,obs(1));const x=fill(m,1,100).update;
 A.equal(x.trainedEstimator,"A");
 const sw=x.trainedHeads.find(x=>x.head==="CASH_SWITCH");
 const expected=100*Math.log(.992)+.9*3;
 A.ok(Math.abs(sw.target-expected)<.000001,JSON.stringify(sw));
});
test("No era/calendar features: shifting every observation 1000 days changes no decision",()=>{
 const a=M.create({minimumMaturedIntervals:3}),b=M.create({minimumMaturedIntervals:3});
 let p1="CASH",p2="CASH";
 for(let d=0;d<140;d++){
   const r=d<70?1.5:-1.5,px=100*Math.exp(.011*Math.min(d,70)-.012*Math.max(0,d-70));
   const x=M.signal(a,obs(d,p1,r,0)),y=M.signal(b,obs(d,p2,r,1000));
   A.equal(x.action,y.action);
   A.ok(Math.abs(x.actionGap-y.actionGap)<1e-8);
   const f1=fill(a,d,px,0).fill,f2=fill(b,d,px,1000).fill;
   p1=f1.positionAfter;p2=f2.positionAfter;
 }
 A.deepEqual(a.q,b.q);A.deepEqual(a.qb,b.qb);
 A.equal(p1,p2);
});
test("Future and non-vintage event blocked before learning any state",()=>{
 const s=M.create(),before=M.save(s);
 const good={verifiedFirstPublication:true,firstAvailableAt:at(0),
   evidenceId:"FED-2020-01-01",family:"G01",polarity:-.6};
 A.throws(()=>M.signal(s,obs(0,"CASH",1,0,[{...good,verifiedFirstPublication:false}])),/UNVERIFIED/);
 A.throws(()=>M.signal(s,obs(0,"CASH",1,0,[{...good,firstAvailableAt:at(1)}])),/FUTURE_EVENT/);
 A.throws(()=>M.signal(s,obs(0,"CASH",1,0,[{...good,family:"UNMAPPED"}])),/UNVERIFIED/);
 A.deepEqual(s,before);
 const x=M.signal(s,obs(0,"CASH",1,0,[good]));
 A.equal(x.action,"WAIT");A.equal(s.audit.eventObservations,1);
});
test("no input has lookahead return or mutable post-decision influence",()=>{
 const a=M.create(),b=M.create();
 const x=M.signal(a,obs(0)),y=M.signal(b,obs(0));
 A.deepEqual(x,y);
 fill(a,0,100);fill(b,0,100);
 M.signal(a,obs(1));M.signal(b,obs(1));
 A.deepEqual(a,b);
 fill(a,1,150);fill(b,1,75);
 A.notDeepEqual(a.q.CASH_SWITCH.w,b.q.CASH_SWITCH.w);
 A.deepEqual(x,y);
});
test("event-relative surprise changes with as-of market shock, not the future label",()=>{
 const a=M.create();
 let pos="CASH";
 for(let d=0;d<16;d++){
  const s=M.signal(a,obs(d,pos,1));
  pos=fill(a,d,100+d).fill.positionAfter;
 }
 const x=M.signal(a,obs(16,pos,-10));
 A.ok(x.regimeSurprise>0,JSON.stringify(x));
 A.ok(a.regime.lastSurprise>0);
});
test("flat fee-restricted market eventually abstains",()=>{
 const s=M.create({minimumMaturedIntervals:6}),actions=[];
 let pos="CASH";
 for(let d=0;d<120;d++){
  const z=M.signal(s,obs(d,pos,0));
  const f=fill(s,d,100).fill;pos=f.positionAfter;
  if(d>60&&z.action!=="WAIT")actions.push({d,action:z.action});
 }
 A.deepEqual(actions,[]);
});
test("save/restore retains both critics and regime state",()=>{
 const s=M.create();M.signal(s,obs(0));fill(s,0);
 const x=M.restore(M.save(s));A.deepEqual(x,s);
 const corrupt=M.save(s);corrupt.qb.GOLD_KEEP.w[0]=null;
 A.throws(()=>M.restore(corrupt),/BAD_Q_CHECKPOINT/);
 const bad=M.save(s);bad.regime.m2=null;
 A.throws(()=>M.restore(bad),/CHECKPOINT/);
});
test("arbitrary irregular observation gaps use elapsed duration; huge gap trains nothing",()=>{
 const s=M.create({maxIntervalHours:40,gammaPerDay:.85});
 M.signal(s,obs(0));fill(s,0,100);
 M.signal(s,obs(1));let u=fill(s,1,103).update;
 A.ok(Math.abs(u.discount-.85)<1e-9);
 M.signal(s,obs(5));u=fill(s,5,110).update;
 A.equal(u.accepted,false);
 A.equal(s.skipped,1);
});
test("single bank-leg fee still unchanged in both estimators' counterfactuals",()=>{
 const s=M.create({feePerSide:.008});
 M.signal(s,obs(0));fill(s,0,100);
 M.signal(s,obs(1));const u=fill(s,1,102).update;
 const x=Object.fromEntries(u.trainedHeads.map(z=>[z.head,z.reward]));
 A.ok(Math.abs(x.CASH_KEEP)<1e-9);
 A.ok(Math.abs(x.GOLD_KEEP-100*Math.log(1.02))<1e-8);
 A.ok(Math.abs(x.GOLD_SWITCH-100*Math.log(.992))<1e-8);
});

test("Regime EWMA forgets old average after many as-of observations",()=>{
 const m=M.create({regimeMemory:.90});
 let pos="CASH",scoreEarly=0,scoreLate=0;
 for(let i=0;i<180;i++){
  const direction=i<80?1.5:-1.5;
  const z=M.signal(m,obs(i,pos,direction));
  if(i===80)scoreEarly=z.regimeSurprise;
  if(i===150)scoreLate=z.regimeSurprise;
  pos=fill(m,i,100*Math.exp(.01*Math.min(i,80)-.01*Math.max(0,i-80))).fill.positionAfter;
 }
 A.ok(scoreEarly>scoreLate,scoreEarly+" should exceed "+scoreLate);
});
test("Forgetting-rate config is explicit and not learnable calendar ID",()=>{
 const m=M.create();
 A.ok(m.config.gradientMemory>0&&m.config.gradientMemory<1);
 A.ok(m.config.regimeMemory>0&&m.config.regimeMemory<1);
 A.throws(()=>M.create({gradientMemory:1}),/BAD_FORGETTING/);
 A.throws(()=>M.create({regimeMemory:0}),/BAD_FORGETTING/);
});

test("Independent event families G01/G05 occupy independent learned channels",()=>{
 const a=M.create(),b=M.create();
 const template={verifiedFirstPublication:true,firstAvailableAt:at(0),
  evidenceId:"SYNTHETIC-PUBLICATION-1",polarity:-.8};
 M.signal(a,obs(0,"CASH",0,0,[{...template,family:"G01"}]));
 M.signal(b,obs(0,"CASH",0,0,[{...template,family:"G05"}]));
 const x=a.pending.x,y=b.pending.x;
 A.ok(x[12]!==y[12]);
 A.ok(x[16]!==y[16]);
 A.equal(x[12],-.8);A.equal(y[16],-.8);
 A.equal(x.at(-1),y.at(-1));
});
test("As-of event-group learning cannot infer tomorrow's event",()=>{
 const a=M.create(),b=M.create();
 const future={verifiedFirstPublication:true,firstAvailableAt:at(1),
  evidenceId:"SYNTHETIC-FUTURE-RELEASE",family:"G02",polarity:.9};
 A.throws(()=>M.signal(a,obs(0,"CASH",1,0,[future])),/FUTURE_EVENT/);
 M.signal(a,obs(0));M.signal(b,obs(0));
 A.deepEqual(a.pending.x,b.pending.x);
});
