"use strict";
const t=require("node:test"),assert=require("node:assert/strict");
const review=require("./v4_forward_review"),v4=require("./recovery_v4");
t("post-Feb data is Git-pinned, strictly chronological and 7 months covered",()=>{
 const r=review.loadHoldout();
 assert.equal(r.rows.length,1123);
 assert.equal(r.gitBlob,review.PIN.blob);
 assert.equal(Object.keys(r.byUTCMonth).length,7);
 assert.ok(Object.values(r.byUTCMonth).every(n=>n>=120));
 assert.ok(r.rows.every((x,i)=>i===0||x.time>r.rows[i-1].time));
 assert.ok(r.rows.every(x=>x.time>=Date.parse("2026-03-01T00:00:00Z")&&x.time<Date.parse("2026-10-01T00:00:00Z")));
});
t("preregistered V4 uses one portfolio across Feb-Sep with no future threshold refit",()=>{
 const a=review.runForwardReview();
 assert.equal(a.unchangedPolicy,v4.VERSION);
 assert.equal(a.thresholdCalibrationCutoffUTC,"2026-01-01T00:00:00.000Z");
 assert.equal(a.initialPosition,"CASH");
 assert.equal(a.startingCashUSD,119.75391720039644);
 assert.equal(a.monthEndCarryVerified,true);
 assert.equal(a.monthly.length,8);
 assert.deepEqual(a.monthly.map(x=>x.month),
  ["2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"]);
 assert.ok(a.monthly.every(x=>x.bars>=110));
 assert.equal(a.monthly[0].position,"GOLD");
 assert.ok(Math.abs(a.monthly[0].terminalNetUSD-122.8679)<.0001);
 assert.equal(a.hasProspectiveBlindValidation,false);
 assert.equal(a.economicMechanismVerified,false);
 assert.equal(a.bankBidAskIncluded,false);
 assert.equal(a.futureLabelAsDecisionFeature,false);
 assert.equal(a.monthEndTurkeyUTC,"2026-09-30T21:00:00.000Z");
});
t("buy-hold baseline is from first actual 09:00 bank hour, not 06:45",()=>{
 const f=review.loadFebruary3h();
 const o=review.buyingAtFirstBankTime(f,119.75391720039644);
 assert.equal(o.entryUTC,"2026-02-02T06:00:00.000Z");
 assert.equal(o.entryTR,"2026-02-02 09:00");
 assert.ok(Math.abs(o.price-4547.265)<1e-8);
});
t("V4 post-Feb review is identical on replay and contains only daytime buy/sell",()=>{
 const a=review.runForwardReview(),b=review.runForwardReview();
 assert.deepEqual(a,b);
 for(const order of a.actions){
  assert.ok([9,12,15].includes(Number(order.tr.slice(11,13))));
  assert.ok(order.utc<"2026-09-30T21:00:00.000Z");
 }
 assert.ok(a.actual.finalUSD>0);
 assert.equal(a.monthlyBenchmarks.length,8);
 assert.ok(a.monthlyBenchmarks.every(x=>Number.isFinite(x.V4MinusBuyHoldUSD)));
});
