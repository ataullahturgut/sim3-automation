"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {loadFrozen,runAll,analog}=require("./engine");
const v2=require("./event_audit_v2");

test("all 92 matured aliases are not silently treated as 92 independent cases",()=>{
 const k=v2.buildV2Knowledge();
 assert.equal(k.metrics.archiveRows,96);
 assert.equal(k.metrics.eligibleAliases,92);
 assert.ok(k.metrics.uniqueCheckpoints<92);
 assert.equal(k.metrics.duplicateAliases,92-k.metrics.uniqueCheckpoints);
 assert.ok(k.metrics.approximateOverlapping96hEpisodes<=k.metrics.uniqueCheckpoints);
 assert.equal(k.metrics.clearlyCausalEvents,0);
 assert.equal(k.metrics.rejects.unverifiedFirstprint,96);
 assert.equal(k.metrics.rejects.unprovenCausality,96);
});

test("same original checkpoint appears only once in V2 learning bank",()=>{
 const k=v2.buildV2Knowledge();
 const keys=k.cases.map(c=>c.orig+"|"+c.utc);
 assert.equal(keys.length,new Set(keys).size);
 assert.equal(k.cases.every(c=>c.ms+96*3600000<=Date.parse("2025-12-31T21:00:00Z")),true);
});
test("V2 score never pretends to be a calibrated probability",()=>{
 const k=v2.buildV2Knowledge(),p=loadFrozen().rows[0];
 const r=v2.scoreDedup(p,k.cases);
 assert.ok(r.rawEventFraction>=0&&r.rawEventFraction<=1);
 assert.equal(r.probabilityCalibrated,false);
 assert.equal(r.economicMechanismConfirmed,false);
 assert.equal(r.firstprintConfirmed,false);
 assert.ok(r.episodeCount<=9);
 assert.ok(r.weightEffectiveN<=9+1e-9);
 assert.equal(r.nearest.length,3);
});

test("transaction costs are an explicit bidirectional hurdle, not an estimated future movement",()=>{
 assert.ok(v2.ROUND_TRIP_COST_PCT>1.6);
 assert.ok(v2.ROUND_TRIP_COST_PCT<1.7);
 const audit=v2.runAudit();
 assert.equal(audit.metrics.bankCostFullyKnown,false);
 assert.equal(audit.januaryV2ImplementedCashUSD,null);
 assert.equal(audit.metrics.additionalVerifiedProfitableSignals,0);
 assert.equal(audit.metrics.actionChangesAuthorized,0);
 for(const d of audit.critical){
  assert.equal(d.trading.estimatedRemainingDownsidePct,null);
  assert.equal(d.trading.canProveTransactionWorthCost,false);
 }
});

test("V2 monthly diagnostic is deterministic and does not rewrite January V1 trades",()=>{
 const r=v2.runAudit(),again=v2.runAudit(),ref=runAll().scenarios.event15m;
 assert.deepEqual(r,again);
 assert.equal(r.critical.length,2);
 assert.equal(r.critical[0].utc,ref.actions[0].utc);
 assert.equal(r.critical[1].utc,ref.actions[1].utc);
 assert.equal(r.januaryReferenceCashUSD,ref.finalUSD);
 assert.equal(r.observedExtraValueFromEventLayerUSD,0);
 for(const d of r.critical){
  assert.equal(d.questions.length,8);
  assert.ok(d.questions.some(q=>q.id==="Q03"&&q.verified===false));
  assert.equal(d.analog.probabilityCalibrated,false);
 }
});


test("calendar controls are independently chosen by clock before future outcomes",()=>{
 const controls=v2.buildCalendarControls();
 assert.equal(controls.length,163);
 assert.equal(new Set(controls.map(r=>r.utc)).size,163);
 assert.equal(controls.filter(r=>r.low96<=-3).length,14);
 assert.ok(controls.every(r=>r.ms+96*3600000<=Date.parse("2025-12-31T21:00:00Z")));
 assert.ok(controls.every(r=>r.observedBars>=40));
 assert.ok(controls.every(r=>new Date(r.utc).getUTCHours()===15));
});
test("calendar controls provide comparative base, not causal probability",()=>{
 const controls=v2.buildCalendarControls();
 const x=loadFrozen().rows[0];
 const score=v2.controlBaseline(x,controls);
 assert.equal(score.neighbors,21);
 assert.ok(score.rawBaseRate>0 && score.rawBaseRate<0.15);
 assert.equal(score.hasReliableConditionalProbability,false);
 assert.ok(score.effectiveN>0 && score.effectiveN<=21+1e-9);
 const test=v2.temporalControlReview(controls);
 assert.equal(test.trainN,100);
 assert.equal(test.testN,63);
 assert.equal(test.trainDown3,6);
 assert.equal(test.testDown3,8);
 assert.ok(Number.isFinite(test.brierUnconditionalBaseline));
 assert.ok(Number.isFinite(test.brierLocalControlNeighbors));
 assert.equal(test.clinicalOrFinancialForecastValidated,false);
});
test("critical January checks show separated event and calendar samples",()=>{
 const audit=v2.runAudit();
 assert.equal(audit.timeSampledControls.count,163);
 assert.equal(audit.timeSampledControls.down3,14);
 assert.equal(audit.critical.length,2);
 for(const d of audit.critical){
  assert.ok(d.control.rawBaseRate>0);
  assert.equal(d.control.hasReliableConditionalProbability,false);
  assert.equal(d.control.positiveCasesAreNotVerifiedEventFree,true);
 }
});
