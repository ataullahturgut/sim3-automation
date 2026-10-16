"use strict";
const test=require("node:test"),A=require("node:assert/strict"),M=require("./v18_kavis_dayaniqlilik");
const base=Date.parse("2020-01-01T00:00:00Z"),D=M.DAY,H=M.HR;
const at=(d,h=6)=>new Date(base+d*D+h*H).toISOString();
const market=(m={})=>({r4:1,r1:2,r3:3,rv:1,dd:0,...m});
const sig=(s,d,p="CASH",m={},extra={})=>M.signal(s,{
 asof:at(d),featureAvailableAt:at(d),position:p,market:market(m),...extra});
const q=(s,d,price=100,extra={})=>M.quote(s,{
 at:at(d,9),price,isBankCheckpoint:true,...extra});
const near=(a,b)=>A.ok(Math.abs(a-b)<1e-8,String(a)+" vs "+String(b));
function init(o){const s=M.create(o);sig(s,0);q(s,0);return s;}
const corroboration=(d,p)=>({sources:[
 {provider:"BANK_RAW_PRIMARY",referencePrice:p,asof:at(d,9)},
 {provider:"INDEPENDENT_METAL_TAPE",referencePrice:p*1.001,asof:at(d,9)}
]});
const evt=(id="BANK-A")=>({verifiedFirstPublication:true,
 evidenceId:id,firstAvailableAt:at(0),family:"G05",polarity:-.8});
test("V18 invalid fee and guard configuration cannot start",()=>{
 for(const x of [
  {maxQuoteJumpLogPct:0},{maxQuoteJumpLogPct:1e3},
  {maxFeatureAgeHours:0},{maxFeatureAgeHours:500},
  {maxAbsFeaturePct:1e6}
 ])A.throws(()=>M.create(x),/BAD_DATA_GUARDS/);
});
test("stale market is rejected before any learning or state mutation",()=>{
 const s=M.create(),old=M.save(s);
 A.throws(()=>sig(s,5,"CASH",{},{
   featureAvailableAt:at(0)}),/STALE_MARKET_FEATURE/);
 A.deepEqual(s,old);
});
test("valid old market within explicit age window is accepted",()=>{
 const s=M.create();
 const a=sig(s,2,"CASH",{}, {featureAvailableAt:at(0)});
 A.equal(a.action,"WAIT");
});
test("mis-scaled prices and massive derived return are blocked before state mutation",()=>{
 const s=M.create(),old=M.save(s);
 A.throws(()=>sig(s,0,"CASH",{r4:100000}),/FEATURE_MAGNITUDE/);
 A.deepEqual(s,old);
});
test("same evidence id cannot be duplicated to artificially magnify G05",()=>{
 const s=M.create(),old=M.save(s);
 A.throws(()=>sig(s,0,"CASH",{}, {events:[evt(),evt()]}),/DUPLICATED_EVENT/);
 A.deepEqual(s,old);
});
test("different event evidence IDs and families enter separate causal channels",()=>{
 const s=M.create();
 sig(s,0,"CASH",{}, {events:[evt("FIN-0001"),
  {...evt("RATE-0002"),family:"G01",polarity:.3}]});
 A.equal(s.pending.x[12],.3);
 A.equal(s.pending.x[16],-.8);
});
test("unconfirmed extreme quote quarantines both fill and learning",()=>{
 const s=init(),before=M.save(s);
 sig(s,1);
 const a=q(s,1,200);
 A.equal(a.quarantined,true);A.equal(a.fill,null);
 A.equal(s.learned,0);A.deepEqual(s.q,before.q);A.deepEqual(s.qb,before.qb);
 A.equal(s.pending.id,"V16-2");
 A.equal(s.audit.quarantineQuotes,1);
 A.equal(s.lastExecution.price,100);
});
test("quarantine can recover on later valid checkpoint without inventing an order",()=>{
 const s=init();sig(s,1);
 const rejected=q(s,1,200);
 A.equal(rejected.quarantined,true);
 const fixed=M.quote(s,{at:at(1,12),price:102,isBankCheckpoint:true});
 A.equal(fixed.fill.positionAfter,"CASH");A.equal(s.learned,1);
});
test("independently confirmed extreme quote can be learned as real severe crash",()=>{
 const s=init();sig(s,1);
 const z=q(s,1,20,{confirmedExtremeQuote:true,corroboration:corroboration(1,20)});
 A.equal(z.quarantined,undefined);A.equal(s.learned,1);
 A.equal(s.audit.confirmedExtremeQuotes,1);
 A.ok(z.update.knownReturnPct< -100);
 for(const k of ["CASH_KEEP","GOLD_SWITCH","GOLD_KEEP","CASH_SWITCH"])
  A.ok(s.q[k].w.every(Number.isFinite));
});
test("safety quarantine does not forge a CASH sale from a GOLD position",()=>{
 const s=init();
 // Force a synthetic hold disposition by directly setting coherent
 // model state; no financial order is actually executed.
 s.virtualPosition="GOLD";
 sig(s,1,"GOLD");
 const bad=q(s,1,.001);
 A.equal(bad.quarantined,true);
 A.equal(s.virtualPosition,"GOLD");
 A.equal(s.pending.position,"GOLD");
});
test("dynamic bank fee at old execution checkpoint enters matured reward exactly once",()=>{
 const s=M.create();
 sig(s,0);q(s,0,100,{bankFeePerSide:.023});
 sig(s,1);const z=q(s,1,105,{bankFeePerSide:.011}).update;
 const pay=Object.fromEntries(z.trainedHeads.map(x=>[x.head,x.reward]));
 near(pay.CASH_SWITCH,100*Math.log(.977)+100*Math.log(1.05));
 near(pay.GOLD_SWITCH,100*Math.log(.977));
 A.equal(s.lastExecution.feePerSide,.011);
});
test("invalid current bank fee never mutates state",()=>{
 const s=init();sig(s,1);
 const old=M.save(s);
 for(const v of [-.01,.101,Infinity,NaN]){
   A.throws(()=>q(s,1,100,{bankFeePerSide:v}),/INVALID_EXECUTION_FEE/);
   A.deepEqual(s,old);
 }
});
test("bad extreme-quote confirmation value is rejected not coalesced",()=>{
 const s=init();sig(s,1);
 const before=M.save(s);
 A.throws(()=>q(s,1,200,{confirmedExtremeQuote:"yes"}),/BAD_EXTREME_CONFIRMATION/);
 A.deepEqual(s,before);
});
test("corrupted checkpoint execution fee or trained model is rejected",()=>{
 const s=init();
 for(const val of [null,-1,.5,NaN]){
  const bad=M.save(s);bad.lastExecution.feePerSide=val;
  A.throws(()=>M.restore(bad),/CHECKPOINT/);
 }
});
test("confirmed extreme high-to-low-to-high movement cannot create NaNs",()=>{
 const s=init();
 let pos="CASH";
 for(let d=1;d<=40;d++){
  sig(s,d,pos, {r4:d%2?-20:20,r1:d%2?-40:40,r3:d%2?-60:60});
  const extreme=d%2?1e-75:1e75;
  const x=q(s,d,extreme,{confirmedExtremeQuote:true,corroboration:corroboration(d,extreme)});
  pos=x.fill.positionAfter;
  A.doesNotThrow(()=>M.restore(M.save(s)));
 }
 A.ok(s.audit.confirmedExtremeQuotes>=35);
});
test("stray non-bank quote cannot create an execution or learn tomorrow",()=>{
 const s=init();sig(s,1);
 const a=M.quote(s,{at:at(1,8),price:1000,isBankCheckpoint:false});
 A.equal(a.fill,null);A.equal(a.update,null);A.equal(s.learned,0);
 const b=q(s,1,101);
 A.equal(b.update.accepted,true);
});
test("old V17 financial cost semantics still valid for one 0.8% bank leg",()=>{
 const s=init();sig(s,1);
 const z=q(s,1,102).update;
 const rew=Object.fromEntries(z.trainedHeads.map(t=>[t.head,t.reward]));
 near(rew.CASH_KEEP,0);
 near(rew.GOLD_KEEP,100*Math.log(1.02));
 near(rew.CASH_SWITCH,100*Math.log(.992)+100*Math.log(1.02));
 near(rew.GOLD_SWITCH,100*Math.log(.992));
});
test("full snapshot restores pending quarantined quote without losing fill intent",()=>{
 const s=init();sig(s,1);q(s,1,200);
 const twin=M.restore(M.save(s));
 const e=M.quote(s,{at:at(1,12),price:101,isBankCheckpoint:true});
 const f=M.quote(twin,{at:at(1,12),price:101,isBankCheckpoint:true});
 A.deepEqual(e,f);A.deepEqual(M.save(s),M.save(twin));
});
test("research engine never emits authorized real orders",()=>{
 const s=init();sig(s,1);
 const z=q(s,1,102);
 A.equal(z.ordersSent,0);
 A.equal(z.fill.simulatedExecutionOnly,true);
 A.equal(s.config.liveTrade,false);
});

test("unverified boolean extreme confirmation alone NEVER bypasses quarantine",()=>{
 const s=init();sig(s,1);
 const z=q(s,1,220,{confirmedExtremeQuote:true});
 A.equal(z.quarantined,true);A.equal(s.learned,0);
 A.equal(s.audit.confirmedExtremeQuotes,0);
});
test("fabricated duplicated extreme price source and future-dated proof rejected",()=>{
 for(const wrong of [
  {sources:[{provider:"REPEAT",asof:at(1,9),referencePrice:210},
            {provider:"REPEAT",asof:at(1,9),referencePrice:210}]},
  {sources:[{provider:"ONE",asof:at(1,9),referencePrice:210},
            {provider:"TWO",asof:at(2,9),referencePrice:210}]},
  {sources:[{provider:"ONE",asof:at(1,9),referencePrice:210},
            {provider:"TWO",asof:at(1,9),referencePrice:100}]}
 ]){
  const s=init();sig(s,1);
  const a=q(s,1,210,{confirmedExtremeQuote:true,corroboration:wrong});
  A.equal(a.quarantined,true);A.equal(s.learned,0);
 }
});
test("posted time-safe higher bank fee reduces switching advantage without duplicate fee",()=>{
 const mk=(f)=>{
  const s=M.create({minimumMaturedIntervals:2});
  s.learned=40;
  s.q.CASH_SWITCH.w[0]=2;s.qb.CASH_SWITCH.w[0]=2;
  const x=sig(s,0,"CASH",{}, {bankFeeQuote:{feePerSide:f,availableAt:at(0)}});
  return x;
 };
 const normal=mk(.008),wide=mk(.04),narrow=mk(.001);
 A.ok(wide.actionGap<normal.actionGap);
 A.ok(narrow.actionGap>normal.actionGap);
 const correction=100*(Math.log(1-.04)-Math.log(1-.008));
 near(wide.bankFeeAdjustment,correction);
 near(normal.bankFeeAdjustment,0);
});
test("future or stale bank fee cannot contaminate decision",()=>{
 const cases=[
  {feePerSide:.03,availableAt:at(1)},
  {feePerSide:.03,availableAt:at(-1)},
  {feePerSide:-1,availableAt:at(0)}
 ];
 for(const z of cases){
  const s=M.create(),prior=M.save(s);
  A.throws(()=>sig(s,0,"CASH",{}, {bankFeeQuote:z}),/BANK_FEE_QUOTE/);
  A.deepEqual(s,prior);
 }
});
test("real bank fee is estimated from checkpoint history, checkpoint stable",()=>{
 const s=M.create();
 sig(s,0);q(s,0,100,{bankFeePerSide:.008});
 sig(s,1);q(s,1,102,{bankFeePerSide:.03});
 A.equal(s.feeKnowledge.n,2);
 A.ok(s.feeKnowledge.mean>.008);
 A.equal(s.feeKnowledge.lastKnown,.03);
 A.doesNotThrow(()=>M.restore(M.save(s)));
});
