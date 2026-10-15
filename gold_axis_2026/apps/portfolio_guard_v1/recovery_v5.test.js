"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const model=require("./recovery_v5"),old=require("./recovery_v4");
const v3=require("./recovery_v3");
test("EMA uses prior values and new completed bar without forward labels",()=>{
 const s=model.updateEma(null,100,40);
 assert.equal(s,100);
 const next=model.updateEma(s,120,40);
 assert.ok(next>100&&next<120);
 assert.equal(model.updateEma(next,120,40)>next,true);
});
test("V5 training and warmup contain only past data",()=>{
 const source=v3.loadHistorical();
 const d=Date.parse("2024-01-01T00:00:00Z");
 const history=model.warmup(source,d);
 assert.ok(history.length<=model.P.slowEMAObservations);
 assert.ok(history.every(x=>x.time<d));
 const trained=old.trainBefore(source,d);
 assert.ok(trained.trainingEndUTC<"2024");
});
test("V5 annual and carryforward review is deterministic, with no overnight trades",()=>{
 const a=model.fullResearch(),b=model.fullResearch();
 assert.deepEqual(a,b);
 assert.equal(a.promotionAuthorized,false);
 assert.equal(a.fromFebThroughSeptember.openingUSD,119.75391720039644);
 assert.equal(a.years.length,3);
 assert.equal(a.monthResults.length,8);
 assert.deepEqual(a.monthResults.map(x=>x.month),
 ["2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"]);
 assert.ok(a.monthResults.every(x=>x.finalUSD>0));
 assert.ok(a.years.every(x=>x.trainingEndUTC<new Date(x.year+"-01-01").toISOString()));
 for(const t of a.fromFebThroughSeptember.trades){
  assert.ok([9,12,15].includes(Number(t.tr.slice(11,13))));
  assert.ok(t.utc<"2026-09-30T21:00:00.000Z");
 }
 assert.equal(a.training.causalMechanism,"UNRESOLVED");
});
test("V5 refuses unsorted prices, invalid initial capital and future warmup",()=>{
 const h=v3.loadHistorical(),train=old.trainBefore(h,Date.parse("2023-01-01T00:00:00Z"));
 const r=h[0];
 assert.throws(()=>model.run([],train),/EMPTY_SERIES/);
 assert.throws(()=>model.run([r,r],train),/INVALID_ASOF_INPUT/);
 assert.throws(()=>model.run([r],train,{initialUSD:0}),/INVALID_INITIAL_USD/);
 assert.throws(()=>model.run([r],train,{priorHistory:[r]}),/WARMUP_FUTURE_DATA/);
});
