"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {diag}=require("./v12_earliest_origin_audit");
const nearly=(a,b)=>assert.ok(Math.abs(a-b)<.0001,String(a)+" vs "+String(b));
test("unbroken 2023 to Sep 2026 portfolio does not inherit 2026 start reset success",()=>{
 const a=diag();
 assert.equal(a.continuous.start,"2023-01-03T06:00:00Z");
 assert.equal(a.continuous.earliestMemoryReady,"2023-03-17T06:00:00.000Z");
 nearly(a.continuous.initialUSD,100);
 nearly(a.continuous.finalUSD,100.07688106607975);
 nearly(a.resetFeb2026.finalUSD,135.66380806850964);
 assert.equal(a.continuous.totalTrades,6);
 assert.equal(a.continuous.firstFilledTrade.at,"2026-01-30T09:00:00.000Z");
 assert.equal(a.continuous.trades[1].at,"2026-02-02T09:00:00.000Z");
 assert.equal(a.continuous.distinctFourteenDayBlocks,98);
 assert.ok(a.passiveGold.finalUSD>220);
 assert.equal(a.rootCause.onlyTechnicalMarketFeatures,true);
 assert.equal(a.scientificGate.promote,false);
});
test("2024 and 2025 were opportunity veto failures, not unavailable source labels",()=>{
 const a=diag();
 for(const year of [2024,2025]){
  const y=a.continuous.yearly.find(x=>x.year===year);
  assert.ok(y.memoryReadyDays>250);
  assert.equal(y.filledTrades,0);
  nearly(y.yearEndUSD,100);
 }
 assert.equal(a.continuous.yearly.find(x=>x.year===2024).buyNetGainGateDays,0);
 assert.equal(a.continuous.yearly.find(x=>x.year===2025).buyProbabilityGateDays,0);
 assert.equal(a.auditLimitations.prospectiveBlindPeriod,false);
 assert.equal(a.auditLimitations.trueBankBidAsk,false);
});
