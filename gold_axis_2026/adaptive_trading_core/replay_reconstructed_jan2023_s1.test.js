"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const mod=require("./replay_reconstructed_jan2023_s1");
const tm=t=>new Date(t).toISOString();
const t0=Date.parse("2023-01-03T08:00:00.000Z");
function row(t,x=1900,nq=.5,zn=.1,cl=-.3){
 const end=tm(t),h=tm(t-60*60000);
 return {end_utc:end,bar_start_utc:tm(t-15*60000),
   close_price:x,source_id:mod.XAU,gold_1h_pct:.2,
   nq_1h_pct:nq,zn_1h_pct:zn,cl_1h_pct:cl,
   nq_end:h,zn_end:h,cl_end:h};
}
test("Only valid January 2023 XAU as-of price proxy accepted",()=>{
 const x=row(t0);x.source_id="FALSE_SOURCE";
 assert.throws(()=>mod.run([x]),/SOURCE_ID/);
 x.source_id=mod.XAU;
 assert.equal(mod.run([x]).audit.bankTrades,0);
});
test("Delayed H1 future market values fail closed",()=>{
 const x=row(t0);x.nq_end=tm(t0+60000);
 assert.throws(()=>mod.run([x]),/STALE_OR_FUTURE_H1/);
});
test("Source rows and 4h anchors are chronological",()=>{
 const x=row(t0);assert.throws(()=>mod.run([x,x]),/BAR_ORDER/);
});
test("Sparse absent H1 series is omitted, never inserted as neutral 0",()=>{
 const x=row(t0);x.nq_1h_pct=null;x.nq_end=null;
 const a=mod.run([x]).audit;
 assert.equal(a.featureCoverage.nq_1h,0);
 assert.equal(a.featureCoverage.gold_1h,1);
 assert.equal(a.rules,1);
});
test("Reconstructed source quality is not declared genuinely point-in-time",()=>{
 const r=mod.run([row(t0),row(t0+4*3600000,1906)]);
 assert.equal(r.audit.truePointInTimeVintage,false);
 assert.equal(r.audit.firstPrintEconomicNewsValidated,false);
 assert.equal(r.audit.cmeContinuousRollPointInTimeValidated,false);
 assert.equal(r.audit.matureLabels,1);
 assert.equal(r.audit.bankTrades,0);
 assert.equal(r.checkpoint.audit.tradeActions,0);
});
