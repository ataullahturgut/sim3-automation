"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const K=require("./v15_kavis_cekirdek");
const base=Date.parse("2020-01-01T00:00:00Z");
const at=(day,h=6)=>new Date(base+day*K.DAY+h*K.HOUR).toISOString();
function sig(m,d,pos="CASH",market={r4:1,r1:2,r3:3}){
 return K.signal(m,{asof:at(d),featureAvailableAt:at(d),position:pos,market});
}
const q=(s,d,p=100,h=9,bank=true)=>K.receiveQuote(s,{at:at(d,h),price:p,isBankCheckpoint:bank});
test("AUDIT: no future state is updated by a bad timezone or market quote",()=>{
 const s=K.make();const prior=K.checkpoint(s);
 A.throws(()=>K.signal(s,{asof:"2020-01-01T06:00:00",featureAvailableAt:at(0),
  market:{r4:1,r1:2,r3:3},position:"CASH"}),/TIMEZONE/);
 A.deepEqual(K.checkpoint(s),prior);
 sig(s,0);const frozen=K.checkpoint(s);
 A.throws(()=>q(s,0,100,10,true),/INVALID_BANK_CHECKPOINT_TIME/);
 A.deepEqual(K.checkpoint(s),frozen);
});
test("AUDIT: multi-horizon comparisons use action premium PER DAY, not raw horizon totals",()=>{
 const s=K.make({minMaturedLabels:3,confidenceZ:0});
 s.heads.ENTRY[28].n=6;s.heads.ENTRY[28].linear.w[0]=6;
 s.heads.ENTRY[56].n=6;s.heads.ENTRY[56].linear.w[0]=9;
 // Originally raw max chose 56 (9>6), despite 28 having faster edge.
 const z=sig(s,0);
 A.equal(z.decision.selectedHorizon,28);
 A.ok(Math.abs(z.decision.score-(6/3)/28)<1); // softmax 3 experts
 A.equal(z.decision.scoreUnit,"LOG_WEALTH_PERCENT_POINTS_PER_DAY");
 A.equal(z.decision.action,"BUY");
});
test("AUDIT: the SAME gold risk penalty discourages entry but supports protective exit",()=>{
 const mk=(position)=>{
   const s=K.make({maxHypotheticalDownsidePct:2,minMaturedLabels:3,confidenceZ:0});
   s.risk.lambda=2;s.risk.model.w[0]=9;
   s.heads.ENTRY[28].n=10;s.heads.ENTRY[28].linear.w[0]=1;
   s.heads.EXIT[7].n=10;s.heads.EXIT[7].linear.w[0]=-1;
   const res=sig(s,0,position);
   return {s,res};
 };
 const cash=mk("CASH").res.decision,gold=mk("GOLD").res.decision;
 A.ok(cash.riskAdjustmentPerDay>0&&gold.riskAdjustmentPerDay>0);
 A.equal(cash.action,"WAIT");
 A.equal(gold.action,"SELL");
 A.ok(gold.score>0);
});
test("AUDIT: position cannot be invented between two candidate bank fills",()=>{
 const s=K.make();sig(s,0,"CASH");q(s,0);
 const before=K.checkpoint(s);
 A.throws(()=>sig(s,1,"GOLD"),/POSITION_MISMATCH/);
 A.deepEqual(K.checkpoint(s),before);
 A.equal(sig(s,1,"CASH").decision.position,"CASH");
});
test("AUDIT: risk label requires sufficiently dense sampled quotes",()=>{
 const s=K.make({maxHypotheticalDownsidePct:2});sig(s,0);q(s,0,100);
 // 7-day and 28-day terminal labels may eventually exist,
 // but a multi-day missing stretch invalidates extremum-based risk targets.
 const z=q(s,28,50,12);
 const ep=z.matured.find(e=>e.h===28);
 A.ok(ep);A.equal(ep.sampledRiskCoverageComplete,false);
 A.equal(ep.worstHoldingLoss,null);
 A.equal(s.risk.modelObservations,0);
 A.equal(s.risk.observations,0);
 A.ok(s.heads.ENTRY[28].n>0); // terminal return still observable
});
test("AUDIT: continuous quote coverage matures true downside-risk estimation",()=>{
 const s=K.make({maxHypotheticalDownsidePct:2});sig(s,0);q(s,0,100);
 for(let i=1;i<=29;i++)q(s,i,i<28?90:95);
 A.equal(s.risk.modelObservations,1);
 A.ok(s.risk.model.w.some(z=>z!==0));
 A.ok(s.risk.lambda>0);
});
test("AUDIT: corrupt model checkpoint fails closed, not silently replaced with zeros",()=>{
 const m=K.make();
 for(const bad of [
  {heads:{ENTRY: {}}},
  {centers:[[0]]},
  {pending:[1,2]},
  {virtualPortfolio:{position:"UNKNOWN"}},
  {heads:{ENTRY:{1:{n:0,linear:{w:[1]}}}}},
 ]){
   const x=K.checkpoint(m),broken={...x,...bad};
   A.throws(()=>K.restore(broken),/CORRUPT|INCOMPATIBLE/);
 }
 const x=K.checkpoint(m);
 x.heads.ENTRY[7].linear.w[2]=null;
 A.throws(()=>K.restore(x),/CORRUPT|NONFINITE/);
});
test("AUDIT: no externally callable instant-label settlement or direct policy mutation",()=>{
 A.equal(typeof K.settle,"undefined");
 A.equal(typeof K.updateHead,"undefined");
 A.equal(typeof K.modelInput,"undefined");
 A.equal(typeof K.liveOrder,"undefined");
});
test("AUDIT: valid customized bank checkpoints must be explicit",()=>{
 A.throws(()=>K.make({checkpointHoursUTC:[6,6]}),/INVALID_BANK/);
 A.throws(()=>K.make({maxQuoteGapHours:0}),/INVALID_QUOTE/);
 const s=K.make({checkpointHoursUTC:[6,8,12]});
 sig(s,0);A.equal(q(s,0,100,8).fills.length,1);
});
test("AUDIT: stable EMA expert loss permits recovery and bounded reliability",()=>{
 const s=K.make();
 let position="CASH";
 for(let i=0;i<115;i++){
   sig(s,i,position,{r4:i<50?2:-2,r1:i<50?4:-4,r3:i<50?5:-5});
   const x=q(s,i,100*Math.exp(.01*Math.min(i,50)-.01*Math.max(0,i-50)));
   position=x.fills[0].intendedPosition;
 }
 const h=s.heads.ENTRY[1];
 A.ok(h.n>80);
 A.ok(h.logExpertWeight.every(Number.isFinite));
 A.ok(h.logExpertWeight.every(v=>Math.abs(v)<=13));
 A.ok(h.expertLoss.every(v=>v>=0&&Number.isFinite(v)));
});
