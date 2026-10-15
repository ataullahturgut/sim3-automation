"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {eligibility,createJanuaryLearningRecord}=require("./monthly_learning_v2");
test("Jan29 severe shock's forward 96h label is not mature at month close",()=>{
 const x=eligibility("2026-01-29T15:15:00.000Z");
 assert.equal(x.labelMaturesUTC,"2026-02-02T15:15:00.000Z");
 assert.equal(x.maturedAtCutoff,false);
 assert.equal(x.status,"PENDING_FORWARD_LABEL");
});
test("Jan5 trade's label matures before Jan end",()=>{
 const x=eligibility("2026-01-05T06:30:00.000Z");
 assert.equal(x.labelMaturesUTC,"2026-01-09T06:30:00.000Z");
 assert.equal(x.maturedAtCutoff,true);
});
test("month-end learning record is reproducible and preserves cash asset",()=>{
 const a=createJanuaryLearningRecord(),b=createJanuaryLearningRecord();
 assert.deepEqual(a,b);
 assert.equal(a.feedbackReadiness.matured,1);
 assert.equal(a.feedbackReadiness.pending,1);
 assert.equal(a.nextMonth.month,"2026-02");
 assert.equal(a.nextMonth.portfolioAsset,"CASH");
 assert.ok(Math.abs(a.nextMonth.cashUSD-119.753917)<0.00001);
 assert.equal(a.nextMonth.autoRetrain,false);
 assert.equal(a.nextMonth.riskCalibrationReady,false);
 assert.equal(a.firstprintVerifiedEvents,0);
 assert.equal(a.sha256.length,64);
});
