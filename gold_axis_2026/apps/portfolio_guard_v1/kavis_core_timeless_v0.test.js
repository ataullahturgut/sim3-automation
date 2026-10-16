"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const C=require("./kavis_core_timeless_v0");
const at=(x)=>new Date(x).toISOString();
const t0=Date.parse("2023-01-03T09:00:00Z");
function ob(t,price=1840,ev=[]){
 return {asof:at(t),price,priceAvailableAt:at(t),
 market:{goldR4hPct:{value:.6,availableAt:at(t-15*60000)},
  silverR4hPct:{value:-.3,availableAt:at(t-15*60000)}},
 events:ev};
}
test("month and year never become features; only relative event age matters",()=>{
 const t=t0,delta=800*86400000;
 const e=(u)=>[{mechanismFamily:"G01_RATES_USD",signedSurprise:-1.5,
  sourceConfidence:.9,firstAvailableAt:at(u-3*3600000),eventId:"C001_SECRET"}];
 const a=C.encode(ob(t,1840,e(t))).x,
   b=C.encode(ob(t+delta,1840,e(t+delta))).x;
 assert.deepEqual(a,b);
 assert.equal(a.length,C.NFEATURES);
});
test("future news publication, future price availability, or bad vintage rejected",()=>{
 const a=ob(t0);
 a.events=[{mechanismFamily:"G02_TRADE_TARIFF",signedSurprise:1,
 sourceConfidence:.9,firstAvailableAt:at(t0+60000)}];
 assert.throws(()=>C.encode(a),/CORE_FUTURE_INFORMATION/);
 a.events=[];a.priceAvailableAt=at(t0+900000);
 assert.throws(()=>C.encode(a),/CORE_FUTURE_INFORMATION/);
 a.priceAvailableAt=at(t0);
 a.market.goldR4hPct.availableAt=at(t0+120000);
 assert.throws(()=>C.encode(a),/CORE_FUTURE_INFORMATION/);
});
test("missing asset is explicitly encoded, not fabricated",()=>{
 const x=C.encode(ob(t0));
 assert.ok(x.missing.includes("palladiumR4hPct"));
 assert.equal(x.quality.available,2);
 assert.equal(x.quality.missing,C.SIGNALS.length-2);
});
test("delayed outcome labels and online parameter weights update ONLY after maturation",()=>{
 const s=C.create(),before=C.checkpoint(s);
 const z=C.observe(s,ob(t0,1840));
 assert.equal(z.action,"WAIT");
 assert.equal(s.totalMatured,0);
 assert.equal(s.heads[0].n,0);
 assert.equal(s.heads[0].pending.length,1);
 C.observe(s,ob(t0+60*60000,1841));
 assert.equal(s.totalMatured,0);
 const y=C.observe(s,ob(t0+240*60000,1860));
 assert.ok(s.totalMatured>=1);
 assert.ok(s.totalNonzeroUpdates>0);
 assert.ok(s.heads[0].wReturn.some(w=>w!==0));
 assert.equal(s.heads[1].n,0);
 assert.equal(y.learningLabels,s.totalMatured);
 assert.equal(before.totalMatured,0);
});
test("economic events influence learned scores only through mutable coefficients, no categorical action rule",()=>{
 const s=C.create();const first=C.observe(s,ob(t0,1840));
 assert.equal(first.action,"WAIT");
 const ev=[{mechanismFamily:"G03_GEOPOLITICS",signedSurprise:3,
   sourceConfidence:1,firstAvailableAt:at(t0+3600000)}];
 const second=C.observe(s,ob(t0+3600000,1840,ev));
 assert.equal(second.action,"WAIT"); // untrained event coefficients never force trades
 assert.equal(s.portfolio.trades,0);
});
test("sparse switching compares net model value to two leg fee and uncertainty",()=>{
 const s=C.create();
 for(const h of s.heads){h.n=10;h.mse=.04;h.wReturn[0]=.6;}
 const no=C.observe(s,ob(t0,1840));
 assert.equal(no.action,"WAIT");
 for(const h of s.heads)h.wReturn[0]=4;
 const yes=C.observe(s,ob(t0+60000,1840));
 assert.equal(yes.action,"BUY");
 assert.ok(yes.lowerSwitchAdvantagePct>0);
 const fill=C.fill(s,yes,{at:at(t0+2*60000),
  quoteFirstAvailableAt:at(t0+2*60000),price:1840});
 assert.equal(fill.positionAfter,"GOLD");
 assert.ok(Math.abs(s.portfolio.ounces-100*.992/1840)<1e-12);
 assert.equal(s.portfolio.trades,1);
 assert.equal(s.portfolio.feesPaidUSD,.8);
 for(const h of s.heads)h.wReturn[0]=-4;
 const out=C.observe(s,ob(t0+3*60000,1840));
 assert.equal(out.action,"SELL");
 const sold=C.fill(s,out,{at:at(t0+4*60000),
   quoteFirstAvailableAt:at(t0+4*60000),price:1840});
 assert.equal(sold.positionAfter,"CASH");
 assert.ok(Math.abs(s.portfolio.cash-98.4064)<1e-10);
 assert.equal(s.portfolio.trades,2);
 assert.ok(s.portfolio.feesPaidUSD>1.59&&s.portfolio.feesPaidUSD<1.60);
});
test("no reordering, no ahead quote, frozen cost and persistence",()=>{
 const s=C.create();
 C.observe(s,ob(t0));
 assert.throws(()=>C.observe(s,ob(t0)),/NONMONOTONIC/);
 assert.throws(()=>C.fill(s,{action:"BUY",sourceTime:at(t0),
  modelVersion:s.version},
   {at:at(t0),quoteFirstAvailableAt:at(t0+60000),price:1900}),/FUTURE_BANK_QUOTE/);
 assert.throws(()=>C.create({feePerSide:.025}),/FROZEN/);
 assert.deepEqual(C.restore(C.checkpoint(s)),s);
});
