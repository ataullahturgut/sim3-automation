"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const {replay}=require("./replay_pretrained_jan2023_s3");
const SOURCE="RESEARCH_PRETRAIN_SYNT";
function mkbar(iso,p){
 const price=+p.toFixed(5);
 return {bar_start_utc:iso,source_id:SOURCE,bid_close:price-.01,ask_close:price+.01};
}
test("2023 JAN no empty memory: 2022 learned S3 critic is checkpointed and retained",()=>{
 const start=Date.parse("2022-12-29T14:00:00Z");
 const pre=Array.from({length:140},(_,i)=>mkbar(
  new Date(start+900000*i).toISOString(),1800*Math.exp(.0001*i)));
 const jan=Array.from({length:120},(_,i)=>mkbar(
  new Date(Date.parse("2023-01-03T10:00:00Z")+900000*i).toISOString(),
  1820*Math.exp(.0002*i)));
 const out=replay([...pre,...jan],[],{modes:["LEGACY_M15","INTEGRATED_LONG_RESEARCH"]});
 assert.equal(out.trainedBars,140);
 assert.equal(out.examBars,120);
 assert.equal(out.initialCashUSD,100);
 assert.equal(out.bankTradingHourRestriction,false);
 assert.ok(out.models.LEGACY_M15.startLearnedState.qStates>0);
 assert.ok(out.models.LEGACY_M15.startLearnedState.s1Rules>=0);
 assert.equal(out.models.LEGACY_M15.startLearnedState.trainingCutoff,"2023-01-01T00:00:00.000Z");
 assert.equal(out.firstprintPIT,false);
 assert.equal(out.scientificGate,"NOT_PROVEN");
});
test("Future test prices cannot retroactively change pretrained state",()=>{
 const start=Date.parse("2022-12-29T14:00:00Z");
 const pre=Array.from({length:130},(_,i)=>mkbar(
  new Date(start+900000*i).toISOString(),1820+.1*i));
 const jan=Array.from({length:35},(_,i)=>mkbar(
  new Date(Date.parse("2023-01-03T10:00:00Z")+900000*i).toISOString(),1840+.1*i));
 const a=replay([...pre,...jan],[],{modes:["LEGACY_M15"]});
 const b=replay([...pre,...jan.map((x,i)=>i<10?x:
    {...x,bid_close:x.bid_close+400,ask_close:x.ask_close+400})],[],{modes:["LEGACY_M15"]});
 assert.deepEqual(a.models.LEGACY_M15.startLearnedState,
   b.models.LEGACY_M15.startLearnedState);
});
test("Cannot claim a pre-trained Jan test from empty, spliced or overlapping rows",()=>{
 const x=mkbar("2023-01-03T10:00:00Z",1800);
 assert.throws(()=>replay([x],[]),/REQUIRED_BOTH_WINDOWS/);
 const a=mkbar("2022-12-29T14:00:00Z",1800),
   b=mkbar("2023-01-03T10:00:00Z",1850);
 assert.throws(()=>replay([a,a,b],[]),/INVALID_OR_SPLICED/);
 assert.throws(()=>replay([{...a,source_id:"WRONG"},b],[]),/INVALID_OR_SPLICED/);
});
