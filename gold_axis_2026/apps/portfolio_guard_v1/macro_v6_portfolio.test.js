"use strict";
const t=require("node:test"),assert=require("node:assert/strict");
const model=require("./macro_v6_portfolio"),base=require("./recovery_v5");
t("frozen CME cross-market data is exact asof and signed source preserved",()=>{
 const {data,byYear}=model.loadMacro();
 assert.equal(data.size,7682);
 assert.equal(byYear["2024"].all,2059);
 assert.ok(byYear["2024"].bothSixHour>1500);
 assert.ok(byYear["2024"].silver<100);
 assert.equal(data.get("2023-01-03T00:00:00.000Z").nq6,null);
 const test=data.get("2023-01-03T00:00:00.000Z");
 assert.equal(model.regime(test).state,"NO_CONSENSUS_OR_STALE");
 assert.equal(model.economicEvidence().cases,96);
 assert.equal(model.economicEvidence().allowedAsCausalTradingInputs,false);
});
t("macro states are threshold-defined, not invented economic causality",()=>{
 assert.equal(model.regime({nq6:-1,zn6:-.1,si6:-1}).state,"EQUITY_BOND_SELL_OFF");
 assert.equal(model.regime({nq6:-1,zn6:.1,si6:null}).state,"SAFE_HAVEN_ROTATION");
 assert.equal(model.regime({nq6:.7,zn6:-.1,si6:null}).state,"YIELD_HEADWIND");
 assert.equal(model.regime({nq6:.7,zn6:.02,si6:null}).state,"CROSS_RISK_ON");
 assert.equal(model.regime({nq6:null,zn6:.02,si6:null}).state,"NO_CONSENSUS_OR_STALE");
 assert.equal(model.regime({nq6:-1,zn6:-.1,si6:-1}).economicMechanism,"UNRESOLVED");
});
t("V6 runs 2024/2025/Feb-Sep without lookahead or overnight bank trades, compares fixed V5",()=>{
 const result=model.fullResearch();
 assert.equal(result.status,"CROSS_ASSET_RETROSPECTIVE_NOT_BLIND");
 assert.equal(result.years.length,3);
 assert.equal(result.fromFebThroughSeptember.openingUSD,119.75391720039644);
 assert.equal(result.monthResults.length,8);
 assert.ok(result.fromFebThroughSeptember.finalUSD>0);
 assert.equal(result.promotionAuthorized,false);
 assert.equal(result.scientificGate.authorized,false);
 assert.equal(result.scientificGate.testedFullYears.length,2);
 assert.equal(result.eventEvidence.verifiedFirstprints,0);
 assert.equal(result.eventEvidence.provenMechanisms,0);
 assert.ok(Math.abs(result.comparison.V5-base.fullResearch().fromFebThroughSeptember.finalUSD)<1e-9);
 for(const x of result.fromFebThroughSeptember.trades){
  assert.ok([9,12,15].includes(Number(x.tr.slice(11,13))));
  assert.equal(x.macro.economicMechanism,"UNRESOLVED");
  assert.ok(x.utc<"2026-09-30T21:00:00.000Z");
 }
});
t("V6 source input and the frozen V5 are not mutated",()=>{
 const e=require("./engine"),b=e.runAll().scenarios.event15m;
 assert.equal(b.terminalAsset,"CASH");
 assert.ok(Math.abs(b.finalUSD-119.75391720039644)<1e-8);
 assert.equal(base.VERSION,"V5_SLOW_TREND_PROTECTION_SHADOW_20261015");
});
